"""Labs 00-04: setup, sampler, Saaras, Bulbul, language layer."""
from nbkit import build, md, code, header, SETUP, COSTMETER, COSTMETER_IMPORT

# ══════════════════════════════════════════════════════ LAB 00 — SETUP
build("00_Setup_and_the_Cost_Meter.ipynb", "Setup and the Cost Meter", [
    header("LAB 00 · FOUNDATION", "Setup and the ₹ Cost Meter",
           "Everything else depends on this notebook. Run it once, keep the meter.",
           "15 min", "₹0.02", "Python 3.11+, a Sarvam API key"),
    md("""
## What you build here

1. A working SDK connection
2. **A cost meter** — the `₹` tally every other lab imports
3. Your first deliberate failure (`content is None`) and its two fixes

> **Teaching note.** Do not skip the cost meter. The habit of printing rupees after
> every call is the single thing that separates this course from an API tour.
"""),
    md("### 1 · Install"),
    code("""
# Run once. Restart the kernel afterwards if the import fails.
%pip install -q sarvamai python-dotenv requests websockets
"""),
    md("""
### 2 · Your key

Get one free at **indus.sarvam.ai** (or dashboard.sarvam.ai) — new accounts
include ₹1000 of credit,
which is more than enough for every lab in this series.

Create a file called `.env` next to this notebook:

```
SARVAM_API_KEY=sk_xxxxxxxxxxxxxxxx
```
"""),
    SETUP,
    md("### 3 · Smoke test — is the key alive?"),
    code("""
r = client.chat.completions(
    model="sarvam-105b",
    messages=[{"role": "user", "content": "एक वाक्य में बताइए: भारत में UPI क्यों सफल हुआ?"}],
    max_tokens=1500,          # note: generous. See section 5 for why.
)
print(r.choices[0].message.content)
"""),
    md("""
### 4 · The cost meter

Every billing unit on the platform, wrapped in one class. Import it into every
later notebook, or just re-run this cell.
"""),
    COSTMETER,
    code("""
# Try it — the smoke test above, costed
u = r.usage
cost.llm(u.prompt_tokens, u.completion_tokens)
cost.report()
"""),
    md("""
### 5 · Your first deliberate failure

`reasoning_effort` defaults to `"low"` on Sarvam-105B, **and reasoning tokens count
against `max_tokens`.** With a small budget the model spends it all thinking and
returns `content = None`.

This is the #1 support question on this platform. Cause it on purpose now so you
recognise it instantly later.
"""),
    code("""
# ⚠️ THIS IS SUPPOSED TO FAIL
bad = client.chat.completions(
    model="sarvam-105b",
    messages=[{"role": "user", "content": "Explain GST in three sentences."}],
    max_tokens=60,            # too small — reasoning eats it
)
print("content :", bad.choices[0].message.content)
print("tokens  :", bad.usage.completion_tokens, "completion tokens billed anyway")
"""),
    code("""
# FIX A — give it room to think AND answer
ok_a = client.chat.completions(
    model="sarvam-105b",
    messages=[{"role": "user", "content": "Explain GST in three sentences."}],
    max_tokens=2000,
)
print("FIX A:", ok_a.choices[0].message.content[:200], "...\\n")

# FIX B — turn reasoning off entirely (faster, cheaper, fine for extraction)
ok_b = client.chat.completions(
    model="sarvam-105b",
    messages=[{"role": "user", "content": "Explain GST in three sentences."}],
    max_tokens=300,
    reasoning_effort=None,
)
print("FIX B:", ok_b.choices[0].message.content[:200])
"""),
    md("""
| | Fix A — raise `max_tokens` | Fix B — `reasoning_effort=None` |
|---|---|---|
| Keeps reasoning | ✅ | ❌ |
| Cheaper | ❌ | ✅ |
| Faster | ❌ | ✅ |
| Use for | multi-step logic, agents | classification, extraction, routing |

**Plan ceilings on `max_tokens`:** Starter 4096 · Pro 16384 · Business 128000.
"""),
    md("### 6 · Save the meter for reuse"),
    code("""
Path("cost_meter.py").write_text('''
"""Shared cost meter. Written by Lab 00; imported by Labs 01-12.

Rates dated August 2026 - verify at docs.sarvam.ai/api/getting-started/pricing.
Figures are a conservative UPPER BOUND: prompt caching, free-tier credit and
invoice rounding all push the real bill lower.
"""
FREE_CREDIT = 1000.00

RATES = ''' + repr(RATES) + '''

class CostMeter:
    def __init__(self): self.items = []
    def add(self, label, rupees, detail=""):
        self.items.append({"label": label, "inr": rupees, "detail": detail}); return rupees
    def stt(self, seconds, diarized=False):
        r = RATES["stt_diarized_per_hour" if diarized else "stt_per_hour"]/3600*seconds
        return self.add("STT", r, f"{seconds:.1f}s")
    def tts(self, chars, v3=True):
        r = RATES["tts_v3_per_10k" if v3 else "tts_v2_per_10k"]/10_000*chars
        return self.add("TTS", r, f"{chars} chars")
    def text(self, chars, kind="translate"):
        return self.add(kind, RATES[f"{kind}_per_10k"]/10_000*chars, f"{chars} chars")
    def llm(self, i, o, c=0):
        r = ((i-c)*RATES["llm_in_per_1m"] + c*RATES["llm_cached_in_per_1m"]
             + o*RATES["llm_out_per_1m"])/1_000_000
        return self.add("LLM", r, f"{i} in / {o} out")
    def doc(self, pages): return self.add("DocAI", RATES["doc_per_page"]*pages, f"{pages} pages")
    def report(self):
        for i in self.items: print(f"{i['label']:<12} ₹{i['inr']:>9.4f}  {i['detail']}")
        t = sum(i["inr"] for i in self.items)
        print(f"{'TOTAL':<12} ₹{t:>9.4f}")
        print(f"{'':<12}  (₹{FREE_CREDIT:.0f} free credit → ₹{FREE_CREDIT-t:.2f} left)")
        print(f"{'':<12}  Estimated from published rates; actual billing usually lower")
        return t
''')
print("wrote cost_meter.py")
print("Every other lab imports it:  from cost_meter import CostMeter")
"""),
    md("""
---
## ✅ Checkpoint

- [ ] `client` connects and returns Hindi text
- [ ] You have caused `content is None` and fixed it two ways
- [ ] `cost.report()` prints a rupee total
- [ ] `cost_meter.py` exists on disk

## 🧪 Try this

1. Set `max_tokens=200` with `reasoning_effort=None`. Does it work now? Why?
2. Run the same prompt at `temperature=0` twice with `seed=42`. Identical?
3. Raise `max_tokens` and re-run the `content is None` cell. At what budget does reasoning stop eating the whole reply?
"""),
])

# ══════════════════════════════════════════════════════ LAB 01 — SAMPLER
build("01_The_Sampler_Every_API_in_One_Script.ipynb", "The Sampler", [
    header("LAB 01 · THE LIVE SESSION LAB", "Every API in one script",
           "Language ID → Translate → Transliterate → TTS → STT → cost report",
           "30 min", "≈ ₹4.20", "Lab 00"),
    md("""
## The point of this lab

One file that touches the **entire live surface** of the platform and prints what
each call cost. Step 4 produces an audio file you can play — hearing your own
language spoken by code you just ran is the moment this stops being abstract.

> **Teaching note.** Run this cell by cell in front of the room. The chat filling
> with people's generated audio files is your best social proof of the session.
"""),
    SETUP, COSTMETER_IMPORT,
    md("### 1 · Language ID — what language is this, and in what script?"),
    code("""
SAMPLES = [
    "मेरा EMI due date क्या है",        # Hindi, Devanagari, code-mixed
    "mera EMI due date kya hai",       # Hindi, romanised
    "What is my EMI due date?",        # English
    "எனது கடன் தவணை எப்போது?",          # Tamil
]

for s in SAMPLES:
    r = client.text.identify_language(input=s)
    cost.text(len(s), "lid")
    print(f"{r.language_code:>8}  {getattr(r, 'script_code', '—'):>8}   {s}")
"""),
    md("""
**Why this matters:** at ₹3.50 per 10,000 characters, LID is cheap enough to run on
*every* inbound message as a router. Most people never think to use it.
"""),
    md("### 2 · Translate — English ⇄ Hindi"),
    code("""
EN = "Your loan instalment of Rs 12,500 is due on the 15th of this month."

hi = client.text.translate(
    input=EN,
    source_language_code="en-IN",
    target_language_code="hi-IN",
    model="mayura:v1",
    mode="formal",                 # colloquial | modern | classical | formal
)
cost.text(len(EN), "translate")
print("HI :", hi.translated_text)

back = client.text.translate(
    input=hi.translated_text,
    source_language_code="hi-IN",
    target_language_code="en-IN",
    model="mayura:v1",
)
cost.text(len(hi.translated_text), "translate")
print("EN :", back.translated_text)
"""),
    md("### 3 · Transliterate — same sound, different script"),
    code("""
tr = client.text.transliterate(
    input=hi.translated_text,
    source_language_code="hi-IN",
    target_language_code="hi-IN",
    spoken_form=True,
)
cost.text(len(hi.translated_text), "transliterate")
print("Devanagari :", hi.translated_text)
print("Roman      :", tr.transliterated_text)
"""),
    md("""
### 4 · Text to speech — **the moment**

Change `MY_LANGUAGE` to your own. Run it. Play the file.
"""),
    code("""
from sarvamai.play import save

MY_LANGUAGE = "hi-IN"      # ← change me: ta-IN bn-IN te-IN mr-IN gu-IN kn-IN ml-IN pa-IN od-IN
MY_TEXT     = hi.translated_text
SPEAKER     = "anushka"

audio = client.text_to_speech.convert(
    text=MY_TEXT,
    target_language_code=MY_LANGUAGE,
    model="bulbul:v2",         # v2 = ₹15/10k. v3 = ₹30/10k. See Lab 03.
    speaker=SPEAKER,
)
save(audio, str(OUT / "my_language.wav"))
cost.tts(len(MY_TEXT), v3=False)
print("saved →", OUT / "my_language.wav")
"""),
    code("""
# Play it right here in the notebook
from IPython.display import Audio, display
display(Audio(str(OUT / "my_language.wav")))
"""),
    md("### 5 · Speech to text — transcribe it back, all five modes"),
    code("""
MODES = ["transcribe", "translate", "verbatim", "translit", "codemix"]
results = {}

for m in MODES:
    with open(OUT / "my_language.wav", "rb") as f:
        r = client.speech_to_text.transcribe(
            file=f, model="saaras:v3", language_code=MY_LANGUAGE, mode=m,
        )
    results[m] = r.transcript
    cost.stt(4.0)          # ~4s clip; replace with real duration in Lab 02
    print(f"{m:>11} │ {r.transcript}")
"""),
    md("### 6 · The cost report"),
    code("cost.report()"),
    md("""
---
## ✅ Checkpoint

- [ ] You generated audio in **your own** language and played it
- [ ] All five STT modes returned different text
- [ ] `cost.report()` shows roughly ₹4 or less

## 🧪 Try this

1. Feed a **code-mixed** sentence through all five modes. Which mode preserves it best?
2. Set `mode="formal"` vs `mode="colloquial"` on the translate call. Read both aloud.
3. Total up what a 10,000-message-a-day support inbox would cost using LID + translate only.
"""),
])

# ══════════════════════════════════════════════════════ LAB 02 — SAARAS
build("02_Saaras_Speech_to_Text_Deep_Dive.ipynb", "Saaras Deep Dive", [
    header("LAB 02 · SPEECH IN", "Saaras — every mode, every path, every trap",
           "5 modes · REST / Batch / WebSocket · the 8 kHz question · diarization · pronunciation",
           "60 min", "≈ ₹8", "Lab 00"),
    md("""
## What you will have proved by the end

1. The five modes are **five different products**, not five formatting options
2. Saaras reads the sample rate **out of the WAV header** — 8 kHz telephony audio
   works on the REST path with no extra parameter. You will measure this yourself.
3. `sample_rate` belongs to the **streaming** APIs, not the REST one — and you will
   see exactly where the boundary sits
4. Batch, REST and WebSocket suit completely different shapes of audio
5. Diarization costs 50% more and you usually do not need it
"""),
    SETUP, COSTMETER_IMPORT,
    md("""
### 0 · Get some audio

You need three files. Use your own if you have them — the lab is far better with
real audio from your own domain.

| File | What it should be |
|---|---|
| `data/clean_16k.wav` | Clean 16 kHz speech, ~10s, any Indian language |
| `data/codemix.wav`   | Code-mixed speech: *"mera EMI due date kya hai"* |
| `data/call_8k.wav`   | Telephony audio, 8 kHz — or downsample the clean one below |
"""),
    code("""
# Generate the sample files from TTS if you have no recordings.
# Idempotent — a file that already exists is left alone and costs nothing,
# so you can safely re-run this cell.
from sarvamai.play import save

def ensure_audio(fname, text, speaker="anushka", lang="hi-IN"):
    \"\"\"Create data/<fname> via TTS only if it is missing. Returns the Path.\"\"\"
    p = DATA / fname
    if p.exists() and p.stat().st_size > 44:      # 44 = minimum WAV header
        print(f"  {fname:<18} exists, skipping")
        return p
    a = client.text_to_speech.convert(text=text, target_language_code=lang,
                                      model="bulbul:v2", speaker=speaker)
    save(a, str(p))
    cost.tts(len(text), v3=False)
    print(f"  {fname:<18} generated")
    return p

SPECS = [
    ("clean_16k.wav", "नमस्ते, मैं अपने लोन के बारे में जानकारी चाहता हूँ।",             "anushka"),
    ("codemix.wav",   "मेरा EMI due date क्या है और late payment charge कितना लगेगा?", "anushka"),
]
for fname, text, spk in SPECS:
    ensure_audio(fname, text, spk)
"""),
    code("""
# Downsample to 8 kHz to simulate telephony.
# `audioop` was removed in Python 3.13 — fall back to a plain-stdlib decimator.
import wave

def _resample_pcm16(frames, nch, src_rate, dst_rate):
    \"\"\"Minimal linear-interpolation resampler for 16-bit PCM. No dependencies.\"\"\"
    import array
    a = array.array("h"); a.frombytes(frames)
    if nch > 1:                                   # take channel 0 only
        a = array.array("h", a[0::nch]); nch = 1
    ratio = dst_rate / src_rate
    n_out = int(len(a) * ratio)
    out = array.array("h", [0]) * n_out
    for i in range(n_out):
        pos = i / ratio
        j = int(pos)
        if j + 1 < len(a):
            frac = pos - j
            out[i] = int(a[j] * (1 - frac) + a[j + 1] * frac)
        elif j < len(a):
            out[i] = a[j]
    return out.tobytes(), nch

def downsample(src, dst, target=8000):
    with wave.open(str(src), "rb") as w:
        params = w.getparams(); frames = w.readframes(w.getnframes())
    try:
        import audioop                            # Python <= 3.12
        conv, _ = audioop.ratecv(frames, params.sampwidth, params.nchannels,
                                 params.framerate, target, None)
        nch = params.nchannels
    except ModuleNotFoundError:                   # Python 3.13+
        conv, nch = _resample_pcm16(frames, params.nchannels,
                                    params.framerate, target)
    with wave.open(str(dst), "wb") as o:
        o.setnchannels(nch); o.setsampwidth(params.sampwidth)
        o.setframerate(target); o.writeframes(conv)
    return dst

downsample(DATA / "clean_16k.wav", DATA / "call_8k.wav")
print("wrote call_8k.wav @ 8000 Hz")
"""),
    code("""
# Helper: how long is a wav, in seconds? (we bill per second)
def duration(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()

for f in ["clean_16k.wav", "codemix.wav", "call_8k.wav"]:
    print(f"{f:<16} {duration(DATA/f):.2f}s")
"""),
    md("""
---
## 1 · The five modes

Same audio. Five different jobs. This is the heart of Saaras and most people
discover it three weeks into a project.
"""),
    code("""
def transcribe(path, mode="transcribe", **kw):
    with open(path, "rb") as f:
        r = client.speech_to_text.transcribe(
            file=f, model="saaras:v3", mode=mode, **kw
        )
    cost.stt(duration(path), diarized=kw.get("diarization", False))
    return r

MODES = ["transcribe", "translate", "verbatim", "translit", "codemix"]
table = {}
for m in MODES:
    table[m] = transcribe(DATA / "codemix.wav", mode=m, language_code="hi-IN").transcript

for m, t in table.items():
    print(f"{m:>11} │ {t}")
"""),
    md("""
| mode | Returns | Reach for it when |
|---|---|---|
| `transcribe` | Native script, lightly normalised | **Default.** Chat logs, search, storage |
| `translate` | English | Analytics, dashboards, English-only downstream |
| `verbatim` | Every filler, stutter, repetition | Compliance, QA scoring, legal record |
| `translit` | Roman script | Your DB or UI can't render Devanagari |
| `codemix` | The actual mix as spoken | Training data, authentic UX |

**Question for the room:** which mode for a recorded compliance call? Most people say
`transcribe`. The answer is `verbatim` — a regulator wants the disfluencies.
"""),
    md("""
---
## 2 · The 8 kHz question — measure it, do not take anyone's word for it

Real Indian call traffic is 8 kHz. Every Western speech stack degrades on it, and
the internet is full of advice telling you to declare a `sample_rate` so the model
knows what it is looking at.

**On the Saaras REST path, that parameter does not exist.** Try it and you get:

```
TypeError: SpeechToTextClient.transcribe() got an unexpected keyword argument 'sample_rate'
```

That is not an oversight. A `.wav` file is a *container* — its 44-byte RIFF header
already declares the sample rate, channel count and bit depth. Saaras reads the
header. There is nothing for you to declare.

So the honest experiment is not *"what breaks without the flag"* — it is
**"how much accuracy does telephony bandwidth actually cost on this model?"**
Let us measure it.
"""),
    code("""
# The parameter genuinely does not exist on the REST path. Prove it, then move on.
try:
    with open(DATA / "call_8k.wav", "rb") as f:
        client.speech_to_text.transcribe(
            file=f, model="saaras:v3", language_code="hi-IN", sample_rate=8000)
except TypeError as e:
    print("TypeError (expected):", e)
    print("\\n↑ The WAV header already carries the rate. Nothing to declare.")
"""),
    code("""
# The real question: does 8 kHz cost us accuracy? Transcribe both and compare.
ref_16k = transcribe(DATA / "clean_16k.wav", language_code="hi-IN")
hyp_8k  = transcribe(DATA / "call_8k.wav",   language_code="hi-IN")

print("16 kHz (reference) :", ref_16k.transcript)
print(" 8 kHz (telephony) :", hyp_8k.transcript)
"""),
    code("""
# Quantify with a word error rate. This `wer()` is reused in Lab 09 on YOUR audio.
def wer(ref, hyp):
    r, h = ref.split(), hyp.split()
    d = [[0]*(len(h)+1) for _ in range(len(r)+1)]
    for i in range(len(r)+1): d[i][0] = i
    for j in range(len(h)+1): d[0][j] = j
    for i in range(1, len(r)+1):
        for j in range(1, len(h)+1):
            d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1] + (r[i-1] != h[j-1]))
    return d[-1][-1] / max(len(r), 1)

score = wer(ref_16k.transcript, hyp_8k.transcript)
print(f"WER  8 kHz vs 16 kHz : {score:.2%}")
print()
if score == 0:
    print("Identical. On this clip, halving the bandwidth cost nothing at all.")
elif score < 0.10:
    print("Under 10% — telephony bandwidth is essentially free on this clip.")
else:
    print("Above 10% — worth re-testing on real call recordings before you quote a number.")
print("\\nThis is a synthetic downsample of clean TTS audio. Real telephony also brings")
print("codec loss, packet jitter and background noise. Measure on YOUR recordings")
print("before you put an accuracy number in front of a customer.")
"""),
    md("""
### So where *does* `sample_rate` matter?

On the **streaming** paths — and only there. When you stream, you are not sending a
container with a header; you are sending a bare sequence of samples. Nothing in that
byte stream says how fast to play it back, so you must declare it:

| Path | Sample rate | Why |
|---|---|---|
| `speech_to_text.transcribe(...)` — REST | **Not a parameter** | The `.wav` header already declares it |
| `speech_to_text_streaming.connect(sample_rate=...)` | **Required** | Raw sample stream, no container |
| `...socket.transcribe(audio, sample_rate=16000)` | **Per chunk** | Defaults to 16000 — override for telephony |
| `speech_to_text_realtime_streaming.connect(sample_rate=...)` | **Required** | Same reason |

> **The rule worth remembering.** Container in, rate declared for you. Raw samples in,
> you declare the rate. Get this wrong on a streaming socket and you *will* get the
> silent-garbage failure the internet warned you about — it is just in section 5,
> not here.
"""),
    md("""
---
## 3 · Language handling — declare, or auto-detect?
"""),
    code("""
# Explicit language code
a = transcribe(DATA / "codemix.wav", language_code="hi-IN")

# Auto-detect — omit language_code entirely
b = transcribe(DATA / "codemix.wav")

print("explicit  :", a.transcript)
print("auto      :", b.transcript)
print("detected  :", getattr(b, "language_code", "—"))
"""),
    md("""
**Rule of thumb.** Auto-detect for unknown inbound audio. Declare explicitly when you
already know (an IVR where the caller picked Hindi) — it is more accurate and lets
you skip a detection round-trip.

**23 languages:** `hi-IN bn-IN ta-IN te-IN mr-IN gu-IN kn-IN ml-IN od-IN pa-IN as-IN
ur-IN ne-IN kok-IN ks-IN sd-IN sa-IN sat-IN mni-IN brx-IN mai-IN doi-IN en-IN`
"""),
    md("""
---
## 4 · Delivery path 2 — Batch, for many files at once

Up to 20 files × 60 minutes per job. Async: create → upload → start → wait → fetch.
This is also the only path with **speaker diarization**.

The point of batch is *plurality* — one job, many files, one bill, one poll. So we
will submit **three** files together and read back a per-file result table.
"""),
    code("""
# ── Self-healing audio setup ─────────────────────────────────────────────
# Regenerates any missing file, so this section works even if you jumped
# straight here without running section 0. Idempotent: existing files are
# left alone and cost nothing.
from sarvamai.play import save          # re-imported so this cell stands alone

WANTED = [
    # filename,           text,                                                     speaker
    ("clean_16k.wav", "नमस्ते, मैं अपने लोन के बारे में जानकारी चाहता हूँ।",              "anushka"),
    ("codemix.wav",   "मेरा EMI due date क्या है और late payment charge कितना लगेगा?",  "anushka"),
    ("query_16k.wav", "कृपया मेरा खाता नंबर वेरिफाई कीजिए और बैलेंस बताइए।",              "karun"),
]

def ensure_audio(fname, text, speaker="anushka", lang="hi-IN"):
    \"\"\"Create data/<fname> via TTS only if it is missing. Returns the Path.\"\"\"
    p = DATA / fname
    if p.exists() and p.stat().st_size > 44:      # 44 = minimum WAV header
        return p
    a = client.text_to_speech.convert(text=text, target_language_code=lang,
                                      model="bulbul:v2", speaker=speaker)
    save(a, str(p))
    cost.tts(len(text), v3=False)
    print(f"  generated {fname}")
    return p

BATCH_FILES = []
for fname, text, spk in WANTED:
    try:
        ensure_audio(fname, text, spk)
        BATCH_FILES.append(fname)
    except Exception as e:
        print(f"  SKIP {fname} — {type(e).__name__}: {e}")

print(f"\\n{'file':<18}{'seconds':>9}")
print("─" * 27)
for f in BATCH_FILES:
    print(f"{f:<18}{duration(DATA/f):>9.2f}")
print("─" * 27)
print(f"{'TOTAL':<18}{sum(duration(DATA/f) for f in BATCH_FILES):>9.2f}"
      f"   across {len(BATCH_FILES)} files")

assert len(BATCH_FILES) >= 2, "Need at least 2 files to demonstrate batch mode."
"""),
    code("""
# ── Create → upload ALL three → start ────────────────────────────────────
job = client.speech_to_text_job.create_job(
    model="saaras:v3",
    language_code="hi-IN",
    with_diarization=True,
    num_speakers=2,
)

# upload_files takes a LIST — this is the whole point of batch mode
job.upload_files(file_paths=[str(DATA / f) for f in BATCH_FILES])
job.start()
print("job started :", job.job_id)
print("files queued:", len(BATCH_FILES))
"""),
    md("""
### Polling: use the SDK's own waiter, not a hand-rolled loop

Older cookbook snippets hand-roll a `while True` with `get_status()` and a backoff.
It works, but the SDK ships `wait_until_complete()` which does exactly that — with a
proper timeout and a `TimeoutError` you can actually catch:

```python
job.wait_until_complete(poll_interval=5, timeout=600)   # ← use this
```

Companion helpers you get for free: `job.is_complete()`, `job.is_successful()`,
`job.is_failed()`, `job.get_file_results()`, `job.get_output_mappings()`.
Prefer these over parsing `job_state` strings yourself — the string casing has
changed between API versions, and these methods normalise it for you.
"""),
    code("""
# ── Wait, then read PER-FILE results ─────────────────────────────────────
try:
    final = job.wait_until_complete(poll_interval=5, timeout=600)
    print("job_state:", final.job_state)
except TimeoutError as e:
    print("timed out:", e)

results = job.get_file_results()          # {"successful": [...], "failed": [...]}

print(f"\\n{'file':<20}{'status':<12}{'output':<28}")
print("─" * 60)
for r in results["successful"]:
    print(f"{r['file_name']:<20}{r['status']:<12}{str(r['output_file']):<28}")
for r in results["failed"]:
    print(f"{r['file_name']:<20}{r['status']:<12}{r['error_message']}")

print(f"\\n{len(results['successful'])} succeeded · {len(results['failed'])} failed")
"""),
    md("""
> **Why `get_file_results()` matters more than it looks.** In a 20-file job, two files
> can fail — a corrupt upload, an unsupported codec — while the job as a whole still
> reports `Completed`. If you only check the job state, you silently lose those two
> files. This is the batch-mode cousin of the `partially_completed` trap you will meet
> again in Lab 06 with Document AI. **Always reconcile counts: files in == files out.**
"""),
    code("""
# ── Download every successful output, then read the diarized turns ───────
if results["successful"]:
    job.download_outputs(output_dir=str(OUT / "batch"))

    # Bill for what actually PROCESSED, not what we intended to upload.
    # A file that failed server-side should not appear on your cost report.
    billed = 0.0
    for r in results["successful"]:
        p = DATA / r["file_name"]
        if p.exists():
            billed += duration(p)
    cost.stt(billed, diarized=True)

    print(f"downloaded {len(results['successful'])} file(s) to {OUT / 'batch'}")
    print(f"billed for  {billed:.2f}s of audio (diarized)")

    # get_output_mappings() tells you which output belongs to which input
    for m in job.get_output_mappings():
        print(f"  {m['input_file']}  →  {m['output_file']}")
else:
    print("No files succeeded — nothing to download, nothing billed.")
    for r in results["failed"]:
        print(f"  {r['file_name']}: {r['error_message']}")
"""),
    code("""
# Read each diarized output — who said what, when, per file
import glob
for p in sorted(glob.glob(str(OUT / "batch" / "*.json"))):
    data = json.load(open(p))
    print(f"\\n── {Path(p).name} ──")
    entries = data.get("diarized_transcript", {}).get("entries", [])
    if not entries:
        print("   (no diarized entries — check the raw JSON keys:", list(data)[:6], ")")
    for seg in entries[:8]:
        print(f"   [{seg.get('start_time_seconds', 0):>6.2f}s] "
              f"spk{seg.get('speaker_id', '?')}: {seg.get('transcript', '')}")
"""),
    md("""
> **Cost discipline.** Diarization is ₹45/hr vs ₹30/hr — a 50% premium. Only pay it
> when you genuinely need *who* said something. For a single-speaker voice note it is
> pure waste, and at a million minutes a month that waste is real money.
"""),
    md("""
---
## 5 · Delivery path 3 — WebSocket streaming

The one your voice agent needs. Partial results come back while the person is still
talking.

**Three things bite everyone here, and all three are worth causing on purpose:**

1. **`SarvamAI` is synchronous.** `connect()` is a *sync* context manager. Write
   `async with` / `await` against it and you get
   `TypeError: 'generator' object does not support the asynchronous context manager
   protocol`. For `async`, use `AsyncSarvamAI` instead — a different class.
2. **Audio must be base64 text, not raw bytes.** The socket carries JSON, and raw
   PCM bytes are not JSON-serialisable.
3. **This is where `sample_rate` finally matters** — you are sending bare samples
   with no header, exactly as section 2 promised.
"""),
    code("""
# ── The failure, on purpose. Read the error, then look at the fix below. ─
import asyncio
try:
    async def broken():
        async with client.speech_to_text_streaming.connect(      # ← sync client!
                model="saaras:v3", language_code="hi-IN") as ws:
            await ws.transcribe(audio=b"\\x00\\x00")               # ← raw bytes!
    await broken()
except TypeError as e:
    print("TypeError (expected):", e)
    print("\\n↑ `SarvamAI` is sync. Either use `with`, or switch to `AsyncSarvamAI`.")
except Exception as e:
    print(f"{type(e).__name__}: {e}")
"""),
    code("""
# ── The SYNC way — simplest, and correct for a notebook ──────────────────
import base64, wave

def stream_transcribe(path, language="hi-IN", model="saaras:v3"):
    \"\"\"Chunked WebSocket transcription using the synchronous client.\"\"\"
    with wave.open(str(path), "rb") as w:
        rate     = w.getframerate()          # read it from the header ONCE
        n_frames = w.getnframes()
        chunk    = int(rate * 0.2)           # 200 ms per chunk
        pcm      = [w.readframes(chunk) for _ in range(0, n_frames, chunk)]

    finals = []
    with client.speech_to_text_streaming.connect(
        model         = model,
        language_code = language,
        sample_rate   = str(rate),           # ← REQUIRED here. Note: a STRING.
        input_audio_codec = "pcm_s16le",
    ) as ws:
        for frames in pcm:
            if not frames:
                continue
            ws.transcribe(
                audio       = base64.b64encode(frames).decode(),   # ← base64 TEXT
                encoding    = "audio/wav",
                sample_rate = rate,
            )
        ws.flush()                            # force-close the open segment

        for msg in ws:                        # plain sync iteration
            t = getattr(getattr(msg, "data", None), "transcript", None)
            if t:
                finals.append(t)
                print("  partial →", t)
            if getattr(msg, "type", "") in ("end_of_stream", "close"):
                break
    return " ".join(finals)

try:
    text = stream_transcribe(DATA / "clean_16k.wav")
    cost.stt(duration(DATA / "clean_16k.wav"))
    print("\\nFINAL:", text)
except Exception as e:
    print(f"{type(e).__name__}: {e}")
    print("Streaming APIs move fast between SDK versions — check docs.sarvam.ai/api-reference.")
"""),
    md("""
### 5.1 · The realtime endpoint — `saaras:v3-realtime`

There are **two** streaming surfaces and they are not the same product:

| | `speech_to_text_streaming` | `speech_to_text_realtime_streaming` |
|---|---|---|
| Model | `saaras:v3` / `saaras:v4` | `saaras:v3-realtime` |
| Built for | Streaming a file or a long feed | **Live conversation** |
| Events | `data` messages | `transcript.partial`, `transcript.final`, `vad.speech_start/end` |
| Endpointing | `flush()` | Server-side VAD, or `manual` |
| Encoding | `pcm_s16le`, `wav` | `linear16`, `mulaw`, `alaw` ← **telephony codecs** |
| Use it for | Batch-ish streaming, captioning | The voice agent in Lab 08 |

The realtime endpoint is the one that speaks `mulaw` — i.e. the one that plugs
straight into an Indian phone bridge. It is also the model behind the realtime
captioning example in Sarvam's own cookbook.
"""),
    code("""
# ── Realtime streaming — VAD-driven, partial + final transcripts ─────────
from sarvamai.types.realtime_audio_input import RealtimeAudioInput
from sarvamai.types.realtime_end import RealtimeEnd

def realtime_transcribe(path, language="hi-IN"):
    with wave.open(str(path), "rb") as w:
        rate     = w.getframerate()
        n_frames = w.getnframes()
        chunk    = int(rate * 0.1)                       # 100 ms — realtime cadence
        pcm      = [w.readframes(chunk) for _ in range(0, n_frames, chunk)]

    partials, finals = [], []
    with client.speech_to_text_realtime_streaming.connect(
        model         = "saaras:v3-realtime",
        language_code = language,
        encoding      = "linear16",       # "mulaw" for an 8 kHz phone bridge
        sample_rate   = str(rate),
        endpointing   = "vad",            # let the server decide turn boundaries
        stream_type   = "balanced",       # "fast" | "balanced" | "simulated"
    ) as ws:
        for frames in pcm:
            if not frames:
                continue
            ws.send_realtime_audio_input(
                RealtimeAudioInput(audio=base64.b64encode(frames).decode()))
        ws.send_realtime_end(RealtimeEnd())              # signal end of input

        for msg in ws:
            ev = getattr(msg, "event", "")
            if ev == "transcript.partial":
                partials.append(msg.text)
                print(f"  … {msg.text}")
            elif ev == "transcript.final":
                finals.append(msg.text)
                print(f"  ✓ [{msg.start_s:.2f}s–{msg.end_s:.2f}s] {msg.text}")
            elif ev in ("vad.speech_start", "vad.speech_end"):
                print(f"  · {ev}")
            elif ev in ("session.end", "error"):
                if ev == "error":
                    print("  server error:", getattr(msg, "message", msg))
                break
    return partials, finals

try:
    partials, finals = realtime_transcribe(DATA / "clean_16k.wav")
    cost.stt(duration(DATA / "clean_16k.wav"))
    print(f"\\n{len(partials)} partials → {len(finals)} final utterance(s)")
    print("FINAL:", " ".join(finals))
except Exception as e:
    print(f"{type(e).__name__}: {e}")
    print("If this endpoint is not enabled on your plan, skip to section 6 —")
    print("Lab 08 rebuilds the same loop inside a full voice agent.")
"""),
    md("""
**Partials vs finals — the distinction your UI depends on.** Partials are the model's
running best guess; they get *revised* as more audio arrives. Finals are committed and
never change. Render partials in grey and finals in black, and your captioning UI
suddenly feels like every professional one you have used.

**VAD is what decides where a turn ends.** `endpointing="vad"` lets the server call it
from silence duration; `endpointing="manual"` puts you in charge. Tuning
`silence_duration_ms` is the difference between an agent that interrupts people and one
that feels patient — you will tune exactly this in Lab 08.
"""),
    md("""
---
## 6 · Pronunciation dictionaries

Brand names, scheme names, SKUs and place names get mangled by default. A dictionary
fixes them for both recognition and synthesis.
"""),
    code("""
# Create a dictionary for your domain's problem words
try:
    d = client.pronunciation_dictionary.create(
        name="aividhya-bfsi",
        entries=[
            {"word": "IRDAI",      "pronunciation": "आई आर डी ए आई"},
            {"word": "PM-KISAN",   "pronunciation": "पी एम किसान"},
            {"word": "AIVidhya",   "pronunciation": "ए आई विद्या"},
        ],
    )
    print("dictionary:", d.id)
except Exception as e:
    print("Dictionary API shape varies by SDK version — check docs.sarvam.ai. Error:", e)
"""),
    md("""
---
## 7 · The bill
"""),
    code("cost.report()"),
    md("""
---
## ✅ Checkpoint

- [ ] Five modes produced five genuinely different transcripts
- [ ] You measured the real WER cost of 8 kHz telephony audio — and can state the number
- [ ] You can explain **why** REST needs no `sample_rate` but streaming does
- [ ] A **three-file** batch job completed via `wait_until_complete()`, and you read the
      per-file table from `get_file_results()`
- [ ] Streaming produced partial results before the audio finished
- [ ] You saw partials get *revised* into finals on the realtime endpoint

## 🧪 Try this

1. Record 30 seconds of yourself, in your own dialect. Run all five modes. Where does it fail?
2. **Re-run the 8 kHz comparison on a real call recording**, not a synthetic downsample.
   Codec loss and background noise are what actually move WER — does your number hold?
3. Push the batch job to 10 files. Does throughput scale linearly, or does the
   10-requests-per-minute ceiling bite first?
4. Deliberately corrupt one file in the batch (truncate it) and confirm
   `get_file_results()["failed"]` catches it while the job still reports `Completed`.
5. Switch the realtime call to `encoding="mulaw"` with 8 kHz audio — the exact
   configuration a phone bridge sends. Does the transcript hold up?
6. Build a 10-file eval set from real audio and compute mean WER. **This is the artefact
   that wins enterprise pilots** — a documented accuracy number on *their* data.
"""),
])

# ══════════════════════════════════════════════════════ LAB 03 — BULBUL
build("03_Bulbul_Text_to_Speech_Deep_Dive.ipynb", "Bulbul Deep Dive", [
    header("LAB 03 · SPEECH OUT", "Bulbul — voices, controls, streaming, and 60% of your bill",
           "Personas · pitch/pace/loudness · REST vs stream vs WebSocket · TTFB · telephony formats",
           "50 min", "≈ ₹6", "Lab 00"),
    md("""
## Why this lab matters more than it looks

In a voice product, **text-to-speech is roughly 60% of your per-call cost** — far more
than the LLM everyone obsesses over. It is also the component that decides whether
your agent sounds like a person or a train announcement.
"""),
    SETUP, COSTMETER_IMPORT,
    md("### 1 · The voice catalogue"),
    code("""
SPEAKERS = ["anushka", "abhilash", "manisha", "vidya", "arya", "karun", "hitesh"]
LINE = "आपकी किस्त पंद्रह तारीख को देय है। कृपया समय पर भुगतान करें।"

from sarvamai.play import save
from IPython.display import Audio, display

for spk in SPEAKERS[:4]:                     # trim to conserve credit
    try:
        a = client.text_to_speech.convert(
            text=LINE, target_language_code="hi-IN", model="bulbul:v2", speaker=spk)
        p = OUT / f"voice_{spk}.wav"; save(a, str(p)); cost.tts(len(LINE), v3=False)
        print(spk); display(Audio(str(p)))
    except Exception as e:
        print(f"{spk}: unavailable ({e})")
"""),
    md("""
**Pick by persona, not preference.**

| Persona | Use for | Wrong for |
|---|---|---|
| Conversational / Friendly | Support, assistants, reminders | Regulatory notices |
| News / Authoritative | Announcements, compliance readouts | A chatty helper |
| Entertainment / Dynamic | Edtech, media, content | A bank |
| Consistent / Neutral | Long-form narration | Anything needing warmth |
"""),
    md("### 2 · The control surface"),
    code("""
VARIANTS = [
    ("baseline",   dict()),
    ("slow",       dict(pace=0.75)),
    ("fast",       dict(pace=1.3)),
    ("low_pitch",  dict(pitch=-0.3)),
    ("high_pitch", dict(pitch=0.3)),
    ("loud",       dict(loudness=1.4)),
]

for name, kw in VARIANTS:
    a = client.text_to_speech.convert(
        text=LINE, target_language_code="hi-IN",
        model="bulbul:v2", speaker="anushka", **kw)
    p = OUT / f"ctrl_{name}.wav"; save(a, str(p)); cost.tts(len(LINE), v3=False)
    print(f"{name:<11}", kw); display(Audio(str(p)))
"""),
    md("""
| Parameter | Range | Notes |
|---|---|---|
| `pitch` | roughly −1 … 1 | Small moves. ±0.2 is already noticeable |
| `pace` | roughly 0.5 … 2 | 0.9 often sounds more natural than 1.0 for Indic |
| `loudness` | roughly 0.3 … 3 | Normalise instead where you can |
| `speech_sample_rate` | 8000 / 16000 / 22050 / 24000 | **8000 for telephony** |
| `enable_preprocessing` | bool | Expands numbers, dates, currency. Usually leave on |
| `output_audio_codec` | mp3, wav, linear16, **mulaw**, alaw, opus, flac, aac | mulaw/alaw = phone |
"""),
    md("### 3 · Telephony output — the format that breaks people"),
    code("""
# Phone systems want 8 kHz mu-law. Get this wrong and you hear static or chipmunks.
tel = client.text_to_speech.convert(
    text=LINE,
    target_language_code="hi-IN",
    model="bulbul:v2",
    speaker="anushka",
    speech_sample_rate=8000,
    output_audio_codec="mulaw",     # <- what Twilio/Exotel expect
)
save(tel, str(OUT / "telephony.raw")); cost.tts(len(LINE), v3=False)
print("wrote telephony.raw — 8 kHz mu-law, ready for a phone bridge")
"""),
    md("""
---
## 4 · Three delivery paths, and the number that matters

For a conversation, **time to first audio byte** is the whole user experience.
Measure it yourself — your numbers beat the docs.
"""),
    code("""
import time

LONG = ("आपका ऋण आवेदन स्वीकृत हो गया है। कृपया अगले चरण के लिए दस्तावेज़ जमा करें। "
        "किसी भी सहायता के लिए हमारी ग्राहक सेवा से संपर्क करें।")

# --- Path 1: REST (batch) — nothing until the whole thing is generated
t0 = time.perf_counter()
a = client.text_to_speech.convert(text=LONG, target_language_code="hi-IN",
                                  model="bulbul:v2", speaker="anushka")
rest_total = time.perf_counter() - t0
cost.tts(len(LONG), v3=False)
print(f"REST      first audio = {rest_total*1000:>7.0f} ms   (== total)")
"""),
    code("""
# --- Path 2: HTTP streaming — audio starts arriving progressively
t0 = time.perf_counter(); first = None; nbytes = 0
stream = client.text_to_speech_streaming.convert(
    text=LONG, target_language_code="hi-IN", model="bulbul:v2", speaker="anushka")
for chunk in stream:
    if first is None:
        first = time.perf_counter() - t0
    nbytes += len(chunk) if isinstance(chunk, (bytes, bytearray)) else 0
http_total = time.perf_counter() - t0
cost.tts(len(LONG), v3=False)
print(f"HTTP str  first audio = {first*1000:>7.0f} ms   total = {http_total*1000:.0f} ms")
"""),
    code("""
# --- Path 3: WebSocket — lowest latency, needs an explicit end signal
async def ws_tts(text):
    t0 = time.perf_counter(); first = None; buf = bytearray()
    async with client.text_to_speech_streaming.connect(
        model="bulbul:v2", target_language_code="hi-IN", speaker="anushka") as ws:
        await ws.convert(text)
        await ws.flush()
        async for m in ws:
            if getattr(m, "type", "") == "audio":
                if first is None: first = time.perf_counter() - t0
                buf.extend(m.data.audio if hasattr(m.data, "audio") else b"")
    return first, time.perf_counter() - t0, len(buf)

first_ws, total_ws, n = await ws_tts(LONG)
cost.tts(len(LONG), v3=False)
print(f"WebSocket first audio = {first_ws*1000:>7.0f} ms   total = {total_ws*1000:.0f} ms")
"""),
    md("""
> **The latency budget.** A human conversation tolerates roughly **800 ms** of silence
> before it feels broken. Your budget: VAD endpointing + STT finalisation + LLM first
> token + **TTS first byte** + network. One non-streaming hop blows the whole thing —
> which is why the REST number above disqualifies it for live agents.
"""),
    md("""
---
## 5 · The version choice that decides your margin
"""),
    code("""
CHARS_PER_CALL = 1600          # ~1.8 min of agent speech
for volume in [1_000, 10_000, 100_000, 1_000_000]:
    v2 = volume * CHARS_PER_CALL / 10_000 * 15
    v3 = volume * CHARS_PER_CALL / 10_000 * 30
    print(f"{volume:>9,} calls/mo   v2 ₹{v2:>12,.0f}   v3 ₹{v3:>12,.0f}   Δ ₹{v3-v2:>12,.0f}")
"""),
    code("""
# Hear the difference yourself before you decide it doesn't matter
for model in ["bulbul:v2", "bulbul:v3"]:
    a = client.text_to_speech.convert(text=LINE, target_language_code="hi-IN",
                                      model=model, speaker="anushka")
    p = OUT / f"cmp_{model.replace(':','_')}.wav"; save(a, str(p))
    cost.tts(len(LINE), v3=(model == "bulbul:v3"))
    print(model); display(Audio(str(p)))
"""),
    md("""
**The decision is a product decision, not a technical one.** For an outbound reminder
IVR, v2 is almost certainly fine and halves your largest cost line. For a premium
concierge assistant, v3 earns its price. Decide deliberately — most teams never do.
"""),
    md("### 6 · Long text — sentence splitting and buffering"),
    code("""
ESSAY = (LONG + " ") * 6      # ~1,000 characters

a = client.text_to_speech.convert(
    text=ESSAY,
    target_language_code="hi-IN",
    model="bulbul:v2",
    speaker="anushka",
    enable_preprocessing=True,     # expands ₹, dates, numbers
)
save(a, str(OUT / "long.wav")); cost.tts(len(ESSAY), v3=False)
print(f"{len(ESSAY)} chars → {OUT/'long.wav'}")
display(Audio(str(OUT / "long.wav")))
"""),
    code("cost.report()"),
    md("""
---
## ✅ Checkpoint

- [ ] You listened to ≥4 voices and can name which persona fits your product
- [ ] You have **your own** TTFB numbers for REST / HTTP / WebSocket
- [ ] You produced 8 kHz mu-law output for a phone bridge
- [ ] You can state, in rupees, what v2-vs-v3 costs at your volume

## 🧪 Try this

1. Read your agent's actual script aloud, then shorten it 20%. Recompute the TTS cost.
   **Copywriting is cost control.**
2. Generate the same line in all 10 Indic languages and play them back to back.
3. Build a pronunciation dictionary for 5 terms in your domain and A/B it with a native speaker.
"""),
])

# ══════════════════════════════════════════════════════ LAB 04 — LANGUAGE
build("04_Language_Layer_Translate_Transliterate_LID.ipynb", "Language Layer", [
    header("LAB 04 · THE LANGUAGE LAYER", "Translate, transliterate, detect — and one silent failure",
           "Mayura vs Sarvam-Translate · registers · script conversion · auto-routing pipeline",
           "40 min", "≈ ₹3", "Lab 00"),
    SETUP, COSTMETER_IMPORT,
    md("""
## 1 · Two translation models. Choose on coverage first, quality second.

| | Mayura v1 | Sarvam-Translate v1 |
|---|---|---|
| Languages | 11 | **23** |
| Weights | closed | **open (Apache 2.0)** |
| Price | ₹20 / 10K chars | ₹20 / 10K chars |
| `output_script` | works | **silently ignored** |
"""),
    code("""
SRC = "Your insurance policy will lapse on 30 September unless the premium is paid."

for model in ["mayura:v1", "sarvam-translate:v1"]:
    r = client.text.translate(
        input=SRC, source_language_code="en-IN",
        target_language_code="hi-IN", model=model)
    cost.text(len(SRC), "translate")
    print(f"{model:<22} {r.translated_text}")
"""),
    md("""
### The registers — same meaning, very different product
"""),
    code("""
for mode in ["colloquial", "modern", "classical", "formal"]:
    r = client.text.translate(
        input=SRC, source_language_code="en-IN", target_language_code="hi-IN",
        model="mayura:v1", mode=mode)
    cost.text(len(SRC), "translate")
    print(f"{mode:<11} │ {r.translated_text}")
"""),
    md("""
> A government notice rendered in `colloquial` reads like a WhatsApp forward. A support
> chatbot in `classical` sounds absurd. Same API call, completely different product.
"""),
    md("""
---
## 2 · ⚠️ The silent failure worth memorising

`output_script` is **ignored** on `sarvam-translate:v1`. The request returns
**HTTP 200** and the wrong script. No exception. No warning.
"""),
    code("""
# ⚠️ Expect roman text. You will not get it.
r = client.text.translate(
    input=SRC, source_language_code="en-IN", target_language_code="hi-IN",
    model="sarvam-translate:v1",
    output_script="roman",          # <- SILENTLY IGNORED on this model
)
cost.text(len(SRC), "translate")
print("asked for roman, received:", r.translated_text)
"""),
    code("""
# ✅ Mayura honours it
r2 = client.text.translate(
    input=SRC, source_language_code="en-IN", target_language_code="hi-IN",
    model="mayura:v1", output_script="roman")
cost.text(len(SRC), "translate")
print("mayura + roman            :", r2.translated_text)

# ✅ Or post-process with transliterate
r3 = client.text.transliterate(
    input=r.translated_text, source_language_code="hi-IN",
    target_language_code="hi-IN", spoken_form=True)
cost.text(len(r.translated_text), "transliterate")
print("sarvam-translate + translit:", r3.transliterated_text)
"""),
    md("""
**Why this class of bug is the dangerous one.** An exception costs you five minutes.
A 200 response with subtly wrong output ships to production and gets discovered by a
customer. This is exactly what Agent Skills exist to prevent —
`npx skills add sarvamai/skills`.
"""),
    md("""
---
## 3 · Transliterate — the quiet workhorse
"""),
    code("""
NAMES = ["राजेश कुमार शर्मा", "तिरुवनंतपुरम", "भुवनेश्वर", "₹1,20,000"]

for n in NAMES:
    r = client.text.transliterate(
        input=n, source_language_code="hi-IN",
        target_language_code="en-IN", spoken_form=True)
    cost.text(len(n), "transliterate")
    print(f"{n:<22} → {r.transliterated_text}")
"""),
    md("""
**Where it earns its keep:** cross-script search, KYC name matching, Roman-script UIs,
databases that cannot store Indic Unicode, and legacy system integration. Unglamorous,
constantly needed.

`spoken_form=True` also expands numerals and currency the way a person would say them —
which is exactly what you want before sending text to TTS.
"""),
    md("""
---
## 4 · Language ID as a router
"""),
    code("""
INBOX = [
    "मेरा payment fail हो गया",
    "எனது கட்டணம் தோல்வியடைந்தது",
    "my payment failed",
    "mera payment fail ho gaya",
    "আমার পেমেন্ট ব্যর্থ হয়েছে",
]

for msg in INBOX:
    r = client.text.identify_language(input=msg)
    cost.text(len(msg), "lid")
    print(f"{r.language_code:>8} / {getattr(r,'script_code','—'):<10} {msg}")
"""),
    md("""
---
## 5 · Put it together — the auto-routing pipeline

Detect → translate to English → run your (English) business logic → translate back.
This is the single most reusable pattern in Indic product work.
"""),
    code("""
def handle(message: str, meter=cost):
    # 1. What language is this?
    lid = client.text.identify_language(input=message); meter.text(len(message), "lid")
    lang = lid.language_code or "en-IN"

    # 2. Normalise to English so your logic stays monolingual
    if lang != "en-IN":
        t = client.text.translate(input=message, source_language_code=lang,
                                  target_language_code="en-IN", model="mayura:v1")
        meter.text(len(message), "translate")
        english = t.translated_text
    else:
        english = message

    # 3. Your business logic — one language, one set of prompts, one set of tests
    reply_en = business_logic(english)

    # 4. Answer in the language they wrote in
    if lang != "en-IN":
        t = client.text.translate(input=reply_en, source_language_code="en-IN",
                                  target_language_code=lang, model="mayura:v1",
                                  mode="formal")
        meter.text(len(reply_en), "translate")
        return lang, t.translated_text
    return lang, reply_en


def business_logic(text_en: str) -> str:
    r = client.chat.completions(
        model="sarvam-105b", max_tokens=800, reasoning_effort=None,
        messages=[
            {"role": "system", "content": "You are a concise bank support agent. Two sentences maximum."},
            {"role": "user", "content": text_en},
        ])
    cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
    return r.choices[0].message.content


for msg in INBOX[:3]:
    lang, reply = handle(msg)
    print(f"\\n[{lang}] {msg}\\n     → {reply}")
"""),
    code("""
cost.report()
print(f"\\nPer message handled: ₹{cost.report.__self__.items and sum(i['inr'] for i in cost.items)/max(len(INBOX[:3]),1):.4f}")
"""),
    md("""
> **The architectural question this raises.** You just paid for two translation calls to
> avoid writing prompts in 11 languages. The alternative is prompting Sarvam-105B
> directly in Hindi — no translation cost, but now your prompts, tests and evals
> multiply by the number of languages you support. There is no universally right
> answer; there is only the one you costed.
"""),
    md("""
---
## ✅ Checkpoint

- [ ] You compared Mayura and Sarvam-Translate on the same input
- [ ] You heard all four registers and can say which suits your product
- [ ] You triggered the `output_script` silent failure and fixed it two ways
- [ ] The auto-routing pipeline answers in the language it was asked in

## 🧪 Try this

1. Run the router on a **romanised** Hindi message. Does LID call it `hi-IN`?
2. Cost the two architectures for 100,000 messages/month: translate-to-English vs
   native-language prompting. Which wins, and at what volume does it flip?
3. Translate a legal paragraph in all four registers and show them to a native speaker.
   Which would you actually send to a customer?
"""),
])

print("\\nlabs 00-04 done")
