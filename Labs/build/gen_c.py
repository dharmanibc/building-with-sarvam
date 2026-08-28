"""Labs 08-09: voice agent, product economics."""
from nbkit import build, md, code, header, SETUP, COSTMETER_IMPORT

# ══════════════════════════════════════════════════════ LAB 08 — VOICE AGENT
build("08_Voice_Agent_Latency_Barge_in_Telephony.ipynb", "Voice Agent", [
    header("LAB 08 · REAL-TIME VOICE", "Building a voice agent — and the 800 ms budget",
           "STT → LLM → TTS loop · latency waterfall · barge-in · telephony · Pipecat/LiveKit",
           "90 min", "≈ ₹12", "Labs 02, 03, 05, 07"),
    SETUP, COSTMETER_IMPORT,
    md("""
## The only number that matters

A human conversation tolerates roughly **800 ms** of silence before it feels broken.
Your budget:

```
VAD endpointing   ~200 ms   ─┐
STT finalisation  ~150 ms    │
LLM first token   ~300 ms    ├─  must total < 800 ms
TTS first byte    ~150 ms    │
network             ~50 ms  ─┘
```

**One non-streaming hop blows the entire budget.** That is why Lab 03's REST number
disqualified it for live agents.

> **Teaching note.** Run this lab in **text mode first** (section 2). It exercises the
> exact same pipeline with zero telephony setup and near-zero credit burn. Only move to
> a real phone number once the logic works.
"""),
    md("""
---
## 1 · Measure your own budget before you build

Never trust the docs' latency numbers. Measure on your connection.
"""),
    code("""
import time
from sarvamai.play import save

TURNS = ["नमस्ते, मेरा EMI कब देय है?", "और late fee कितनी है?"]

def measure_llm_first_token(msg, history=None):
    msgs = (history or [{"role": "system", "content": "You are a concise loan agent. One short sentence."}]) + \\
           [{"role": "user", "content": msg}]
    t0 = time.perf_counter(); first = None; out = []
    for ch in client.chat.completions(model="sarvam-105b", messages=msgs,
                                      max_tokens=200, reasoning_effort=None, stream=True):
        if ch.choices and getattr(ch.choices[0].delta, "content", None):
            if first is None: first = time.perf_counter() - t0
            out.append(ch.choices[0].delta.content)
    return first, time.perf_counter() - t0, "".join(out)

first, total, text = measure_llm_first_token(TURNS[0])
print(f"LLM first token : {first*1000:>6.0f} ms")
print(f"LLM complete    : {total*1000:>6.0f} ms")
print(f"reply           : {text}")
"""),
    code("""
def measure_tts_first_byte(text):
    t0 = time.perf_counter(); first = None; n = 0
    for chunk in client.text_to_speech_streaming.convert(
            text=text, target_language_code="hi-IN", model="bulbul:v2", speaker="anushka"):
        if first is None: first = time.perf_counter() - t0
        n += len(chunk) if isinstance(chunk, (bytes, bytearray)) else 0
    cost.tts(len(text), v3=False)
    return first, time.perf_counter() - t0, n

tf, tt, nb = measure_tts_first_byte(text)
print(f"TTS first byte  : {tf*1000:>6.0f} ms")
print(f"TTS complete    : {tt*1000:>6.0f} ms   ({nb} bytes)")

print(f"\\n── YOUR BUDGET ──")
print(f"LLM first token   {first*1000:>6.0f} ms")
print(f"TTS first byte    {tf*1000:>6.0f} ms")
print(f"subtotal          {(first+tf)*1000:>6.0f} ms   (+ VAD ~200ms + STT ~150ms + net ~50ms)")
print(f"estimated turn    {(first+tf)*1000+400:>6.0f} ms   {'✅ under 800' if (first+tf)*1000+400 < 800 else '⚠️  OVER BUDGET'}")
"""),
    md("""
---
## 2 · The agent loop — text mode

Same pipeline, no telephony. Get the logic right here first.
"""),
    code("""
# ── Tools (reuse from Lab 07) ─────────────────────────────────────────────
ACCOUNTS = {"LN1001": {"name": "Rajesh Kumar", "emi": 12500, "due": "15 अगस्त",
                       "outstanding": 340000, "late_fee_pct": 2}}

def get_account(account_id): return ACCOUNTS.get(account_id, {"error": "not found"})
def get_late_fee(account_id):
    a = ACCOUNTS.get(account_id)
    return {"error": "nf"} if not a else {"pct_per_month": a["late_fee_pct"],
                                          "on_amount": a["emi"]}

REGISTRY = {"get_account": get_account, "get_late_fee": get_late_fee}
TOOLS = [
 {"type":"function","function":{"name":"get_account","description":"Loan account details by ID",
  "parameters":{"type":"object","properties":{"account_id":{"type":"string","description":"e.g. LN1001"}},"required":["account_id"]}}},
 {"type":"function","function":{"name":"get_late_fee","description":"Late payment charge for an account",
  "parameters":{"type":"object","properties":{"account_id":{"type":"string","description":"e.g. LN1001"}},"required":["account_id"]}}},
]

SYSTEM = ("You are a phone agent for an Indian NBFC. Speak like a person on a call: "
          "ONE short sentence, no lists, no markdown. Use tools for any account fact. "
          "Never invent numbers. Always reply in the caller's language. "
          "The caller's account is LN1001.")
"""),
    code("""
class VoiceAgent:
    \"\"\"The STT -> LLM(+tools) -> TTS loop, with per-turn latency and cost.\"\"\"

    def __init__(self, language="hi-IN", meter=None):
        self.lang = language
        self.msgs = [{"role": "system", "content": SYSTEM}]
        self.meter = meter
        self.turns = []

    # -- 1. speech in ------------------------------------------------------
    def listen(self, wav_path):
        t0 = time.perf_counter()
        with open(wav_path, "rb") as f:
            r = client.speech_to_text.transcribe(
                file=f, model="saaras:v3", language_code=self.lang, mode="transcribe")
        import wave
        with wave.open(str(wav_path), "rb") as w:
            secs = w.getnframes() / w.getframerate()
        if self.meter: self.meter.stt(secs)
        return r.transcript, time.perf_counter() - t0

    # -- 2. think ----------------------------------------------------------
    def think(self, user_text):
        self.msgs.append({"role": "user", "content": user_text})
        t0 = time.perf_counter(); first = None
        for _ in range(3):
            r = client.chat.completions(model="sarvam-105b", messages=self.msgs,
                                        tools=TOOLS, max_tokens=800, reasoning_effort=None)
            if self.meter: self.meter.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
            m = r.choices[0].message
            calls = getattr(m, "tool_calls", None)
            if not calls:
                self.msgs.append({"role": "assistant", "content": m.content})
                return m.content, time.perf_counter() - t0
            self.msgs.append({"role":"assistant","content":m.content,"tool_calls":
                [{"id":c.id,"type":"function","function":{"name":c.function.name,
                  "arguments":c.function.arguments}} for c in calls]})
            for c in calls:
                out = REGISTRY[c.function.name](**json.loads(c.function.arguments))
                print(f"     🔧 {c.function.name} → {out}")
                self.msgs.append({"role":"tool","tool_call_id":c.id,
                                  "content":json.dumps(out, ensure_ascii=False)})
        return "क्षमा करें, कृपया दोबारा कहिए।", time.perf_counter() - t0

    # -- 3. speak ----------------------------------------------------------
    def speak(self, text, out_path):
        t0 = time.perf_counter()
        a = client.text_to_speech.convert(text=text, target_language_code=self.lang,
                                          model="bulbul:v2", speaker="anushka")
        save(a, str(out_path))
        if self.meter: self.meter.tts(len(text), v3=False)
        return time.perf_counter() - t0

    # -- one full turn -----------------------------------------------------
    def turn(self, wav_in, wav_out):
        heard, t_stt = self.listen(wav_in)
        print(f"  👤 {heard}")
        reply, t_llm = self.think(heard)
        print(f"  🤖 {reply}")
        t_tts = self.speak(reply, wav_out)
        rec = {"stt_ms": t_stt*1000, "llm_ms": t_llm*1000, "tts_ms": t_tts*1000,
               "total_ms": (t_stt+t_llm+t_tts)*1000}
        self.turns.append(rec)
        print(f"  ⏱  stt {rec['stt_ms']:.0f} + llm {rec['llm_ms']:.0f} "
              f"+ tts {rec['tts_ms']:.0f} = {rec['total_ms']:.0f} ms")
        return reply
"""),
    code("""
# Synthesise caller audio so the loop is end-to-end without a phone
CALLER_LINES = ["नमस्ते, मेरा EMI कब देय है?", "और late fee कितनी लगेगी?"]
for i, line in enumerate(CALLER_LINES):
    a = client.text_to_speech.convert(text=line, target_language_code="hi-IN",
                                      model="bulbul:v2", speaker="karun")
    save(a, str(DATA / f"caller_{i}.wav")); cost.tts(len(line), v3=False)
print("caller audio ready")
"""),
    code("""
agent = VoiceAgent(language="hi-IN", meter=cost)
for i in range(len(CALLER_LINES)):
    print(f"\\n── TURN {i+1} ──")
    agent.turn(DATA / f"caller_{i}.wav", OUT / f"agent_{i}.wav")

from IPython.display import Audio, display
display(Audio(str(OUT / "agent_0.wav")))
"""),
    code("""
# The latency waterfall across the conversation
print(f"{'turn':<6}{'STT':>9}{'LLM':>9}{'TTS':>9}{'TOTAL':>10}")
print("─" * 43)
for i, t in enumerate(agent.turns):
    print(f"{i+1:<6}{t['stt_ms']:>9.0f}{t['llm_ms']:>9.0f}{t['tts_ms']:>9.0f}{t['total_ms']:>10.0f}")
avg = sum(t['total_ms'] for t in agent.turns)/len(agent.turns)
print("─" * 43)
print(f"{'mean':<6}{'':<27}{avg:>10.0f} ms")
print(f"\\n⚠️  This is BATCH mode — nothing streams. A real agent streams every hop\\n"
      f"    and hides most of this behind the audio already playing.")
"""),
    md("""
---
## 3 · Barge-in — the thing that separates a demo from a product

The caller interrupts. You must detect speech, **kill the in-flight TTS stream**,
discard the partial LLM response, and re-enter listening — without losing state.
"""),
    code("""
import asyncio

class BargeInController:
    \"\"\"Cancellable speak(). This is the core of interruptible voice.\"\"\"

    def __init__(self):
        self._task = None
        self.interrupted = False

    async def speak(self, text, on_chunk=None):
        self.interrupted = False
        self._task = asyncio.create_task(self._stream(text, on_chunk))
        try:
            await self._task
        except asyncio.CancelledError:
            self.interrupted = True
            print("     ⏹  TTS cancelled mid-utterance")

    async def _stream(self, text, on_chunk):
        # Simulated chunked TTS — replace with the real WebSocket stream
        for i, piece in enumerate(text.split()):
            await asyncio.sleep(0.12)          # ~120 ms per word of audio
            if on_chunk: on_chunk(piece)
        print()

    def interrupt(self):
        if self._task and not self._task.done():
            self._task.cancel()

async def demo_barge_in():
    ctl = BargeInController()
    speaking = asyncio.create_task(
        ctl.speak("आपकी अगली किस्त पंद्रह अगस्त को देय है और राशि बारह हज़ार पाँच सौ रुपये है",
                  on_chunk=lambda w: print(w, end=" ", flush=True)))
    await asyncio.sleep(0.7)                   # caller starts talking after 700 ms
    print("\\n     🎤 CALLER INTERRUPTS")
    ctl.interrupt()
    await speaking
    print("     ↩️  re-entering listening state, conversation history intact")

await demo_barge_in()
"""),
    md("""
**The four things barge-in must do, in order**

1. **Detect** speech during playback (VAD on the inbound stream)
2. **Cancel** the outbound TTS task immediately — not after the current sentence
3. **Discard** the partial LLM response so it does not get spoken later
4. **Preserve** conversation state — the caller interrupted, they did not reset

Getting 1–3 right but not 4 produces an agent that forgets what it was talking about.
"""),
    md("""
---
## 4 · Telephony — formats and providers
"""),
    code("""
# Phone bridges want 8 kHz mu-law. Generate it correctly.
tel = client.text_to_speech.convert(
    text="आपकी किस्त पंद्रह अगस्त को देय है।",
    target_language_code="hi-IN", model="bulbul:v2", speaker="anushka",
    speech_sample_rate=8000,
    output_audio_codec="mulaw",
)
save(tel, str(OUT / "telephony_out.raw"))
cost.tts(30, v3=False)
print("8 kHz mu-law written — feed this straight to the phone bridge")
"""),
    md("""
| Provider | Best for | Watch out for |
|---|---|---|
| **Exotel** | **India — usually the right answer.** Cheaper, native DLT/TRAI compliance | India-only |
| Twilio | Global reach, excellent docs | Expensive in India, DLT paperwork |
| Vapi | Managed layer, fastest to demo | Less control, another vendor |
| **Sarvam number rental** | **~30 seconds with PAN + Aadhaar** (announced at Epoch) | Verify availability |

> The instant number rental removes the single biggest friction in shipping an Indian
> voice product. Verify it works before you promise it to a workshop room.
"""),
    md("""
---
## 5 · Production frameworks — the sketch

Do not hand-roll the orchestration in production. Use Pipecat (Python-native, easier
to reason about) or LiveKit (WebRTC-native, production-hardened).
"""),
    code("""
PIPECAT_SKELETON = '''
# pip install "pipecat-ai[sarvam,silero]"
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.task import PipelineTask, PipelineParams
from pipecat.services.sarvam import SarvamSTTService, SarvamTTSService, SarvamLLMService
from pipecat.processors.aggregators.openai_llm_context import OpenAILLMContext
from pipecat.audio.vad.silero import SileroVADAnalyzer

stt = SarvamSTTService(api_key=KEY, model="saaras:v3", language="hi-IN", sample_rate=8000)
llm = SarvamLLMService(api_key=KEY, model="sarvam-105b")
tts = SarvamTTSService(api_key=KEY, model="bulbul:v2", speaker="anushka",
                       sample_rate=8000, codec="mulaw")

llm.register_function("get_account", get_account)
llm.register_function("get_late_fee", get_late_fee)

context = OpenAILLMContext(messages=[{"role": "system", "content": SYSTEM}], tools=TOOLS)

pipeline = Pipeline([
    transport.input(),          # phone / WebRTC in
    stt,                        # streaming speech -> text
    context_aggregator.user(),
    llm,                        # streaming reasoning + tools
    tts,                        # streaming text -> speech
    transport.output(),         # phone / WebRTC out
    context_aggregator.assistant(),
])

task = PipelineTask(pipeline, PipelineParams(
    allow_interruptions=True,          # <- barge-in, handled for you
    enable_metrics=True,               # <- per-hop latency
    vad_analyzer=SileroVADAnalyzer(),  # <- endpointing
))
'''
print(PIPECAT_SKELETON)
"""),
    md("""
**Pipecat vs LiveKit**

| | Pipecat | LiveKit |
|---|---|---|
| Model | Python pipeline, explicit stages | WebRTC-native agent framework |
| Best for | Learning, custom flows, telephony | Web/app, scale, production hardening |
| Barge-in | `allow_interruptions=True` | Built into the agent loop |
| Sarvam support | First-party plugin + production guide | First-party plugin + production guide |

Start with Pipecat because you can *see* the pipeline. Move to LiveKit when you need
WebRTC at scale.
"""),
    md("""
---
## 6 · The unit economics of this exact agent
"""),
    code("""
def cost_a_call(minutes=3.0, caller_share=0.40, chars_per_min=900,
                turns=8, ctx_tokens=20_000, out_tokens=1_500,
                tts_v3=False, telephony_per_min=0.60, cached_share=0.0):
    stt_sec   = minutes * 60 * caller_share
    tts_chars = minutes * (1 - caller_share) * chars_per_min
    stt  = 30/3600 * stt_sec
    tts  = (30 if tts_v3 else 15)/10_000 * tts_chars
    llm_in  = ctx_tokens * ((1-cached_share)*29.28 + cached_share*10.98) / 1_000_000
    llm_out = out_tokens * 73.20 / 1_000_000
    tel  = telephony_per_min * minutes
    total = stt + tts + llm_in + llm_out + tel
    return {"STT": stt, "TTS": tts, "LLM in": llm_in, "LLM out": llm_out,
            "Telephony": tel, "TOTAL": total}

base = cost_a_call(tts_v3=True)
for k, v in base.items():
    bar = "█" * int(v / base["TOTAL"] * 40)
    print(f"{k:<10} ₹{v:>6.2f}  {bar}")
print(f"\\n60% of the bill is TTS. The LLM is {(base['LLM in']+base['LLM out'])/base['TOTAL']:.0%}.")
"""),
    code("""
SCENARIOS = [
    ("naive (Bulbul v3)",              dict(tts_v3=True)),
    ("Bulbul v2",                      dict(tts_v3=False)),
    ("v2 + prompt caching",            dict(tts_v3=False, cached_share=0.8)),
    ("v2 + caching + 20% shorter script", dict(tts_v3=False, cached_share=0.8, chars_per_min=720)),
]
for name, kw in SCENARIOS:
    t = cost_a_call(**kw)["TOTAL"]
    print(f"{name:<38} ₹{t:>5.2f}/call   ₹{t*100_000:>10,.0f} per 100k calls")

human = 40
print(f"\\nHuman agent (fully loaded)             ₹{human:>5.2f}/call   "
      f"₹{human*100_000:>10,.0f} per 100k calls")
"""),
    code("cost.report()"),
    md("""
---
## ✅ Checkpoint

- [ ] You measured **your own** LLM-first-token and TTS-first-byte latency
- [ ] The text-mode agent completed a 2-turn conversation with a tool call
- [ ] Barge-in cancels TTS mid-utterance and preserves history
- [ ] You produced 8 kHz mu-law output for a phone bridge
- [ ] You can state your cost per call and the three levers that move it

## 🧪 Try this

1. Make every hop **stream** and re-measure. How much of the batch latency disappears?
2. Add a third tool that is slow (2s). Where does the agent need a filler phrase?
3. Rent a number (Exotel or Sarvam) and phone your own agent. This is the moment it becomes real.
4. Run your agent against Lab 07's eval harness. What is the tool-call accuracy over 10 calls?
5. Add a "please hold" utterance when a tool takes >800 ms. Does the call feel better?
"""),
])

# ══════════════════════════════════════════════════════ LAB 09 — PRODUCT
build("09_Product_Economics_Build_vs_Buy_Benchmarks.ipynb", "Product Economics", [
    header("LAB 09 · THE BUSINESS", "Unit economics, build vs buy, and benchmarking your own data",
           "Cost models · Samvaad comparison · self-hosting crossover · measure accuracy on YOUR audio",
           "50 min", "≈ ₹3", "Labs 02, 03, 05"),
    SETUP, COSTMETER_IMPORT,
    md("""
## Why this is a lab and not a slide

Anybody can quote a price list. The skill is turning it into a **decision** — build or
buy, managed or self-hosted, v2 or v3, what to charge. All of that is arithmetic you
can run, and this notebook is the calculator.
"""),
    md("""
---
## 1 · A complete unit-economics model
"""),
    code("""
RATES = {
    "stt_hr": 30.0, "stt_diar_hr": 45.0,
    "tts_v2_10k": 15.0, "tts_v3_10k": 30.0,
    "xlate_10k": 20.0, "lid_10k": 3.50,
    "llm_in_1m": 29.28, "llm_cached_1m": 10.98, "llm_out_1m": 73.20,
    "doc_page": 0.50, "samvaad_min": 3.50,
}

def voice_call(minutes=3.0, caller_share=.40, chars_per_min=900,
               ctx_tokens=20_000, out_tokens=1_500, cached_share=0.0,
               tts_v3=False, diarize=False, telephony_min=0.60):
    stt = (RATES["stt_diar_hr"] if diarize else RATES["stt_hr"])/3600 * minutes*60*caller_share
    tts = (RATES["tts_v3_10k"] if tts_v3 else RATES["tts_v2_10k"])/10_000 * \\
          minutes*(1-caller_share)*chars_per_min
    lin = ctx_tokens*((1-cached_share)*RATES["llm_in_1m"] + cached_share*RATES["llm_cached_1m"])/1e6
    lou = out_tokens*RATES["llm_out_1m"]/1e6
    tel = telephony_min*minutes
    return dict(STT=stt, TTS=tts, LLM=lin+lou, Telephony=tel,
                TOTAL=stt+tts+lin+lou+tel)

def doc_pipeline(pages, llm_validate=True, tokens_per_page=800):
    d = pages*RATES["doc_page"]
    l = pages*tokens_per_page*RATES["llm_in_1m"]/1e6 if llm_validate else 0
    return dict(DocAI=d, LLM=l, TOTAL=d+l)

import pprint; pprint.pp(voice_call(tts_v3=True))
"""),
    code("""
# Margin model — the four numbers a founder actually needs
def margin(cost_per_unit, price_per_unit, volume_per_month, fixed_monthly=0):
    rev = price_per_unit*volume_per_month
    cogs = cost_per_unit*volume_per_month
    gp = rev - cogs
    return {
        "revenue":      rev,
        "cogs":         cogs,
        "gross_profit": gp - fixed_monthly,
        "gross_margin": (gp - fixed_monthly)/rev if rev else 0,
        "breakeven_vol": fixed_monthly/(price_per_unit-cost_per_unit)
                         if price_per_unit > cost_per_unit else float("inf"),
    }

c = voice_call(tts_v3=False, cached_share=0.8)["TOTAL"]
m = margin(cost_per_unit=c, price_per_unit=15.0,
           volume_per_month=100_000, fixed_monthly=250_000)
print(f"cost/call     ₹{c:.2f}")
for k, v in m.items():
    print(f"{k:<14} {v:>14,.2f}" if isinstance(v, float) and k != "gross_margin"
          else f"{k:<14} {v:>14.1%}" if k == "gross_margin" else f"{k:<14} {v:>14,.0f}")
"""),
    md("""
---
## 2 · Build vs buy — Sarvam's own price is your benchmark

Samvaad went generally available at **₹3.50/minute**. Compare like for like.

> ⚠️ **Check before you quote this.** It is not documented whether ₹3.50/min bundles
> telephony. The comparison below shows both readings — verify with Sarvam before you
> put either number in a customer deck.
"""),
    code("""
mins = 3.0
naive     = voice_call(minutes=mins, tts_v3=True)["TOTAL"]
optimised = voice_call(minutes=mins, tts_v3=False, cached_share=0.8)["TOTAL"]
tel       = 0.60 * mins
samvaad   = RATES["samvaad_min"] * mins

print(f"{'':<34}{'per call':>10}{'per min':>10}")
print("─" * 54)
print(f"{'DIY naive (v3, no cache), all-in':<34}₹{naive:>9.2f}₹{naive/mins:>9.2f}")
print(f"{'DIY naive, excl. telephony':<34}₹{naive-tel:>9.2f}₹{(naive-tel)/mins:>9.2f}")
print(f"{'DIY optimised, all-in':<34}₹{optimised:>9.2f}₹{optimised/mins:>9.2f}")
print(f"{'DIY optimised, excl. telephony':<34}₹{optimised-tel:>9.2f}₹{(optimised-tel)/mins:>9.2f}")
print(f"{'Samvaad (managed)':<34}₹{samvaad:>9.2f}₹{RATES['samvaad_min']:>9.2f}")
print("─" * 54)
print(f"\\nManaged premium vs naive build     : {samvaad/(naive-tel)-1:>6.0%}")
print(f"Managed premium vs optimised build : {samvaad/(optimised-tel)-1:>6.0%}")
"""),
    md("""
**Two things follow.**

1. **Your cost model is sane** — a commercial managed product prices in the same
   order of magnitude, which is the sanity check you want before quoting anyone.
2. **The managed premium is large**, and it grows the more you optimise. That premium
   is exactly what a developer sells: you capture it by owning the plumbing.

The premium is not Sarvam overcharging. It is the real cost of orchestration, state,
retries, barge-in, observability, uptime and someone answering the phone at 3am. The
question is whether you want to own that work — and below a certain volume, you
emphatically do not.
"""),
    code("""
# At what volume does the engineering to build it actually pay for itself?
ENGINEER_MONTHLY = 250_000          # one senior engineer, fully loaded
saving_per_call  = samvaad - (optimised - tel)

for vol in [1_000, 10_000, 50_000, 100_000, 500_000]:
    saved = saving_per_call*vol
    verdict = "BUILD" if saved > ENGINEER_MONTHLY else "BUY"
    print(f"{vol:>8,} calls/mo  saving ₹{saved:>11,.0f}  "
          f"vs ₹{ENGINEER_MONTHLY:,} eng cost → {verdict}")

breakeven = ENGINEER_MONTHLY/saving_per_call
print(f"\\nBreakeven ≈ {breakeven:,.0f} calls/month.")
print("Below that, buying is not laziness — it is arithmetic.")
"""),
    md("""
---
## 3 · The self-hosting crossover

The number that wins bank deals: *at what volume does a dedicated GPU endpoint beat
per-call pricing — while also keeping the data inside their VPC?*
"""),
    code("""
# Indicative SageMaker GPU pricing — REPLACE with your region's real numbers
INSTANCE_PER_HOUR = 95.0            # ₹/hour, ml.g5.xlarge-class, on-demand
HOURS_PER_MONTH   = 730

def crossover(managed_rate_per_hour_audio, instance_hourly, hours=HOURS_PER_MONTH):
    monthly_instance = instance_hourly*hours
    audio_hours = monthly_instance/managed_rate_per_hour_audio
    return monthly_instance, audio_hours

inst_cost, audio_hrs = crossover(RATES["stt_hr"], INSTANCE_PER_HOUR)
print(f"Dedicated endpoint : ₹{inst_cost:>10,.0f} / month")
print(f"Managed equivalent : {audio_hrs:>10,.0f} audio-hours / month")
print(f"                   = {audio_hrs*60:>10,.0f} audio-minutes / month")
print(f"                   ≈ {audio_hrs*60/3:>10,.0f} three-minute calls / month")
print("\\nAbove that volume, self-hosting is cheaper AND the audio never leaves the VPC.")
print("Below it, you are paying for idle GPU.")
"""),
    md("""
> **How to use this in a sales conversation.** A CISO asks "can our data stay inside
> our perimeter?" You say yes, and then: *"and above roughly N calls a month it is also
> cheaper — here is the model, put your own volumes in."* That is a materially
> different conversation from a feature checkbox.
"""),
    md("""
---
## 4 · Benchmark accuracy on YOUR data

Never quote a vendor benchmark to a customer. Measure on their audio. This takes
twenty minutes and it is the artefact that closes pilots.
"""),
    code("""
# Drop your own (audio, ground-truth) pairs here. 10 is enough to signal.
BENCH = [
    # ("data/real_call_01.wav", "मेरा EMI due date क्या है"),
]

def wer(ref, hyp):
    r, h = ref.split(), hyp.split()
    d = [[0]*(len(h)+1) for _ in range(len(r)+1)]
    for i in range(len(r)+1): d[i][0] = i
    for j in range(len(h)+1): d[0][j] = j
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+(r[i-1] != h[j-1]))
    return d[-1][-1]/max(len(r), 1)

def benchmark(pairs, **stt_kw):
    import wave
    rows = []
    for path, truth in pairs:
        with open(path, "rb") as f:
            r = client.speech_to_text.transcribe(file=f, model="saaras:v3", **stt_kw)
        with wave.open(str(path), "rb") as w:
            secs = w.getnframes()/w.getframerate()
        cost.stt(secs)
        rows.append({"file": Path(path).name, "wer": wer(truth, r.transcript),
                     "truth": truth, "hyp": r.transcript})
    if rows:
        mean = sum(x["wer"] for x in rows)/len(rows)
        for x in rows: print(f"{x['wer']:>6.1%}  {x['file']:<24} {x['hyp'][:50]}")
        print(f"\\nMEAN WER: {mean:.1%}  over {len(rows)} files")
        return mean
    print("Add real audio to BENCH and re-run. This is the most valuable cell in the lab.")
    return None

benchmark(BENCH, language_code="hi-IN")
"""),
    md("""
---
## 5 · Pricing models — and their traps

| Model | Fits | The trap |
|---|---|---|
| Per-minute / per-call | Voice agents | Your cost is also per-minute — thin, volume-dependent margin |
| Per-page / per-document | Doc pipelines | Buyer benchmarks against BPO rates. Race to the bottom |
| **Per-seat SaaS** | Internal tools, dashboards | **Decouples revenue from API cost — best margin structure** |
| Outcome-based | Collections, lead-gen | Highest capture, highest risk. Needs provable attribution |
| Platform + implementation | Enterprise, on-prem | Where the real money is in Indian enterprise |
"""),
    code("""
def compare_pricing(monthly_calls=50_000, cost_per_call=None):
    c = cost_per_call or voice_call(tts_v3=False, cached_share=0.8)["TOTAL"]
    cogs = c*monthly_calls
    models = {
        "per-call @ ₹15":            15*monthly_calls,
        "per-minute @ ₹6":           6*3*monthly_calls,
        "per-seat @ ₹8k × 40 seats": 8_000*40,
        "outcome @ ₹120 × 4% conv":  120*monthly_calls*0.04,
        "platform ₹6L + ₹4/call":    600_000 + 4*monthly_calls,
    }
    print(f"COGS at {monthly_calls:,} calls: ₹{cogs:,.0f}  (₹{c:.2f}/call)\\n")
    print(f"{'model':<28}{'revenue':>13}{'gross':>13}{'margin':>9}")
    print("─"*63)
    for k, rev in models.items():
        print(f"{k:<28}₹{rev:>12,.0f}₹{rev-cogs:>12,.0f}{(rev-cogs)/rev:>9.0%}")

compare_pricing()
"""),
    md("""
> **The rule.** Never price cost-plus when the customer's alternative is a human.
> Price against the incumbent — ₹25–60 a call, ₹3–8 a page, ₹25–40k/month per agent —
> hold 50–70% gross margin, and let the customer keep the rest of the saving. That is
> what makes a pilot an easy yes.
"""),
    md("""
---
## 6 · Document pipeline economics
"""),
    code("""
for pages in [10_000, 100_000, 1_000_000]:
    p = doc_pipeline(pages)
    bpo_lo, bpo_hi = pages*3, pages*8
    print(f"{pages:>10,} pages   your cost ₹{p['TOTAL']:>12,.0f}   "
          f"BPO ₹{bpo_lo:>12,.0f}–₹{bpo_hi:>12,.0f}   "
          f"you could charge ₹{pages*1.5:>12,.0f} at 1/2 BPO")

print(f"\\nThroughput ceiling per API key: 10 jobs/min × 10 pages "
      f"= {100*60*24:,} pages/day.")
"""),
    md("""
---
## 7 · Your turn — build your own model
"""),
    code("""
# ─────────────────────────────────────────────────────────────────────────
# EDIT THIS CELL. This is the deliverable of the whole lab series.
# ─────────────────────────────────────────────────────────────────────────
MY = {
    "who":              "NBFCs with a ₹5–50 crore loan book",
    "job":              "outbound EMI reminder and collection calls",
    "language":         "Hindi + Marathi",
    "incumbent":        "in-house tele-callers at ₹40/call fully loaded",
    "my_cost_per_unit": voice_call(tts_v3=False, cached_share=0.8)["TOTAL"],
    "my_price":         15.00,
    "volume_month":     50_000,
    "fixed_month":      250_000,
}

m = margin(MY["my_cost_per_unit"], MY["my_price"], MY["volume_month"], MY["fixed_month"])
print(f"I help {MY['who']}")
print(f"  do {MY['job']} in {MY['language']},")
print(f"  replacing {MY['incumbent']}.\\n")
print(f"  my cost      ₹{MY['my_cost_per_unit']:.2f}/unit")
print(f"  my price     ₹{MY['my_price']:.2f}/unit")
print(f"  gross margin {m['gross_margin']:.0%}")
print(f"  breakeven    {m['breakeven_vol']:,.0f} units/month")
print(f"  monthly GP   ₹{m['gross_profit']:,.0f}")

undercut = 1 - MY["my_price"]/40
print(f"\\n  customer saves {undercut:.0%} vs the incumbent — "
      f"and I keep {m['gross_margin']:.0%}. Both sides win.")
"""),
    code("cost.report()"),
    md("""
---
## ✅ Checkpoint

- [ ] You can state your cost per transaction, derived not guessed
- [ ] You know the volume at which building beats buying Samvaad
- [ ] You know the volume at which self-hosting beats the managed API
- [ ] You filled in the `MY` cell with your own ICP and numbers

## 🧪 Try this

1. Run the model for **three** different verticals. Which has the best margin structure?
2. Add a human-review queue at ₹8/escalation and a 12% escalation rate. Does it still work?
3. Model a per-seat SaaS instead of per-call. How does the picture change at 500 seats?
4. Benchmark WER on 10 real recordings from your domain — then price with that number in hand.

---

## 🏁 You have finished the series

| Lab | What you built |
|---|---|
| 00 | Cost meter + the `content is None` trap |
| 01 | Every API in one script |
| 02 | Saaras — 5 modes, 3 paths, the 8 kHz cliff |
| 03 | Bulbul — voices, controls, streaming, TTFB |
| 04 | Language layer + auto-routing pipeline |
| 05 | Sarvam-105B — reasoning, tools, caching, streaming |
| 06 | Document AI — schemas, lifecycle, limits, queue |
| 07 | Agentic — state, checkpointing, evals, guardrails |
| 08 | Voice agent — latency budget, barge-in, telephony |
| 09 | The business model |

**Next:** pick one workflow in your own domain, ship it to a URL or a phone number, and
show it to one person who would pay for it. Everything above is preparation for that.
"""),
])

print("\\nlabs 08-09 done")
