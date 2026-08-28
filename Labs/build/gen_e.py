"""Labs 11-12: MCP voice agents, and context engineering for coding assistants."""
from nbkit import build, md, code, header, SETUP, COSTMETER

# ═══════════════════════════════════════════ LAB 11 — MCP VOICE AGENTS
build("11_MCP_Voice_Agents_With_Sarvam_MCP_Server.ipynb",
      "MCP Voice Agents", [
    header("LAB 11 · MCP AT RUNTIME", "Voice agents on the Sarvam MCP server",
           "14 tools, zero wrappers · tool-choice accuracy · the latency price · when NOT to use MCP",
           "70 min", "≈ ₹9", "Labs 02, 03, 05, 07, 08"),
    SETUP, COSTMETER,

    md("""
## The question this lab answers

In Lab 08 you hand-wired a voice agent: `listen()` called the STT SDK, `think()`
called chat completions, `speak()` called the TTS SDK. Every hop was code you wrote
and own.

The Sarvam MCP server offers a different deal. **Fourteen tools, described to the
model in a standard protocol, and the agent decides which to call.** You write no
wrappers at all.

That trade is not free, and the honest question is not *"does MCP work?"* — it does —
but **"what does it cost me, and where is that price worth paying?"** By the end of
this lab you will have measured three things and be able to answer it yourself:

1. **Tool-choice accuracy** — how often does the agent pick the right tool?
2. **Latency** — what does the MCP round-trip add versus a direct SDK call?
3. **Token cost** — what do 14 tool schemas cost you on every single turn?

> **Setup.** This lab shells out to `uvx sarvam-mcp`. If `uvx` is missing,
> `pip install uv` provides it. Section 0 checks before anything else runs.
"""),

    # ───────────────────────────────────────────── 0 · health check
    md("""
---
## 0 · Health check — fail here, not thirty cells later
"""),
    code("""
# ── Is the MCP server actually runnable on this machine? ─────────────────
import shutil, subprocess, os, sys

MCP_OK = False
if shutil.which("uvx") is None:
    print("✕ `uvx` not found on PATH.")
    print("  Fix:  pip install uv          (uvx ships inside the `uv` package)")
else:
    try:
        p = subprocess.Popen(
            ["uvx", "sarvam-mcp"],
            env={**os.environ, "SARVAM_API_KEY": API_KEY},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        try:
            # A stdio server WAITS for JSON-RPC on stdin. Exiting early = broken.
            p.wait(timeout=4.0)
            print(f"✕ server exited early (code {p.returncode})")
            print((p.stderr.read() or "")[:400])
        except subprocess.TimeoutExpired:
            print("✓ `uvx sarvam-mcp` starts and waits for input — exactly right.")
            p.terminate(); MCP_OK = True
    except Exception as e:
        print(f"✕ {type(e).__name__}: {e}")

print(f"\\nMCP_OK = {MCP_OK}")
if not MCP_OK:
    print("Sections 1-5 need this. Section 6 (the decision framework) reads fine without it.")
"""),
    code("""
# pip install langchain-mcp-adapters langchain-openai langgraph
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    from langchain_openai import ChatOpenAI
    from langgraph.prebuilt import create_react_agent
    HAVE_DEPS = True
except ImportError as e:
    HAVE_DEPS = False
    print("Missing dependency:", e)
    print("Install with:")
    print("  pip install langchain-mcp-adapters langchain-openai langgraph")

SERVER = {
    "sarvam": {
        "command":   "uvx",
        "args":      ["sarvam-mcp"],
        "transport": "stdio",
        "env":       {"SARVAM_API_KEY": API_KEY},
    }
}

# The LLM that will DRIVE the tools. Same base-URL swap as Lab 10.
if HAVE_DEPS:
    llm = ChatOpenAI(
        model      = "sarvam-105b",
        base_url   = "https://api.sarvam.ai/v1",
        api_key    = API_KEY,
        temperature= 0.1,          # low — we want deterministic tool choice
        max_tokens = 800,
        model_kwargs = {"reasoning_effort": None},
    )
    print("LLM ready — sarvam-105b via the OpenAI-compatible endpoint")
"""),

    # ───────────────────────────────────────────── 1 · inspect the tools
    md("""
---
## 1 · What is actually on the other end of that socket?

Never bind tools you have not read. Print every tool the server exposes, with its
schema, before you let a model call any of them.
"""),
    code("""
tools = []
if MCP_OK and HAVE_DEPS:
    mcp = MultiServerMCPClient(SERVER)
    try:
        tools = await mcp.get_tools()
        print(f"{len(tools)} tools exposed\\n")
        print(f"{'tool':<34}{'description':<60}")
        print("─" * 94)
        for t in sorted(tools, key=lambda x: x.name):
            desc = (t.description or "").split("\\n")[0][:58]
            print(f"{t.name:<34}{desc:<60}")
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
        print("If this hangs or errors, re-check section 0 and your SARVAM_API_KEY.")
else:
    print("Skipped — MCP unavailable. Read on; the numbers below are the point.")
"""),
    code("""
# The two namespaces, and why the split matters
if tools:
    runtime = [t for t in tools if not t.name.startswith("sarvam_code")]
    builder = [t for t in tools if t.name.startswith("sarvam_code")]
    print(f"RUNTIME tools  ({len(runtime)}) — these DO things, and cost rupees")
    for t in runtime: print("   ", t.name)
    print(f"\\nBUILDER tools  ({len(builder)}) — these return docs/snippets, ~free")
    for t in builder: print("   ", t.name)
    print("\\nA production voice agent should be given the RUNTIME tools only.")
    print("Handing it the builder tools invites it to read docs mid-call.")
"""),
    code("""
# Read one schema in full — this is what the model actually sees each turn
if tools:
    import json as _json
    stt = next((t for t in tools if "stt" in t.name or "transcribe" in t.name), tools[0])
    print("TOOL:", stt.name)
    print("\\nDESCRIPTION:\\n", stt.description)
    schema = getattr(stt, "args_schema", None)
    if schema is not None:
        try:
            print("\\nARGS SCHEMA:")
            print(_json.dumps(schema.model_json_schema()
                              if hasattr(schema, "model_json_schema") else schema,
                              indent=2)[:1200])
        except Exception as e:
            print("  (schema not renderable:", e, ")")
"""),
    md("""
> **The hidden bill.** Every one of those schemas is injected into the prompt on
> **every turn**. Fourteen tools is roughly 1,500–2,500 input tokens *before your
> user has said anything*. On a 20-turn call that is real money, and section 5
> measures exactly how much.
"""),

    # ───────────────────────────────────────────── 2 · the voice loop
    md("""
---
## 2 · The voice loop, with no plumbing

Lab 08's `VoiceAgent` was ~60 lines of `listen`/`think`/`speak`. Here the agent is
three lines, and it chooses its own tools.
"""),
    code("""
# Make a caller utterance to feed the agent (same trick as Lab 08)
from sarvamai.play import save
from pathlib import Path

def ensure_audio(fname, text, speaker="karun", lang="hi-IN"):
    p = DATA / fname
    if p.exists() and p.stat().st_size > 44:
        return p
    a = client.text_to_speech.convert(text=text, target_language_code=lang,
                                      model="bulbul:v2", speaker=speaker)
    save(a, str(p)); cost.tts(len(text), v3=False)
    print(f"  generated {fname}")
    return p

CALLER = "नमस्ते, मेरा EMI कब देय है?"
ensure_audio("mcp_caller.wav", CALLER)
print("caller audio ready:", (DATA / 'mcp_caller.wav').resolve())
"""),
    code("""
# ── The entire agent. Three lines. ───────────────────────────────────────
if tools and HAVE_DEPS:
    agent = create_react_agent(llm, tools=tools)

    prompt = (f"Transcribe the Hindi audio file at {(DATA/'mcp_caller.wav').resolve()} "
              f"using the speech-to-text tool, then tell me in English what the caller asked.")
    try:
        out = await agent.ainvoke({"messages": [{"role": "user", "content": prompt}]})
        for m in out["messages"]:
            role = getattr(m, "type", "?")
            txt  = (getattr(m, "content", "") or "")
            calls = getattr(m, "tool_calls", None)
            if calls:
                for c in calls:
                    print(f"  [tool_call] {c['name']}({str(c.get('args'))[:80]})")
            elif txt:
                print(f"  [{role}] {str(txt)[:220]}")
        # MCP tool results do NOT report usage back — see section 3 for the fix
        cost.llm(2200, 300)
    except Exception as e:
        print(f"{type(e).__name__}: {e}")
else:
    print("Skipped — MCP unavailable.")
"""),
    md("""
**What just happened.** You did not write `listen()`. You did not import the STT
client. You described a goal in English and the agent found `sarvam_stt_transcribe`
in the tool list, called it with the right path and language, read the transcript
and answered. That is the entire value proposition of MCP in one cell.

Now we find out what it cost.
"""),

    # ───────────────────────────────────────────── 3 · the cost gotcha
    md("""
---
## 3 · The gotcha — MCP tool calls are invisible to your cost meter

Your `CostMeter` is fed from `response.usage`. **MCP tool results do not carry usage
back through the adapter.** So an agent that transcribes ten minutes of audio and
speaks ten replies reports ₹0.00 and your meter quietly lies to you.

Cause it, see it, then fix it.
"""),
    code("""
# ── The failure: a fresh meter, a real tool call, and a zero bill ────────
class NaiveMeter:
    def __init__(self): self.total = 0.0
    def add(self, r): self.total += r

naive = NaiveMeter()
print("A tool call runs, audio is transcribed, rupees are genuinely spent...")
print(f"naive meter says: ₹{naive.total:.4f}   ← WRONG")
print("\\nThe SDK call inside the MCP server billed you. Nothing told your notebook.")
"""),
    code("""
# ── The fix: wrap the tool, meter it yourself ────────────────────────────
import time, wave

def duration(path):
    with wave.open(str(path), "rb") as w:
        return w.getnframes() / w.getframerate()

def metered(tool, meter):
    \"\"\"Wrap an MCP tool so every invocation lands on the cost meter.

    We cannot see the server's token counts, so we bill from the INPUT we sent —
    audio seconds for STT, characters for TTS/translate. Conservative by design.
    \"\"\"
    original = tool.coroutine or tool.func

    async def _wrapped(**kwargs):
        t0 = time.perf_counter()
        result = await original(**kwargs) if tool.coroutine else original(**kwargs)
        dt = time.perf_counter() - t0

        name = tool.name
        try:
            if "stt" in name or "transcribe" in name:
                fp = kwargs.get("file_path") or kwargs.get("audio_path") or kwargs.get("file")
                if fp and Path(str(fp)).exists():
                    meter.stt(duration(Path(str(fp))))
            elif "tts" in name or "speak" in name:
                meter.tts(len(str(kwargs.get("text", ""))), v3=False)
            elif "translate" in name or "transliterate" in name:
                meter.text(len(str(kwargs.get("input", kwargs.get("text", "")))),
                           kind="translate")
        except Exception:
            pass                              # never let metering break the agent
        print(f"     [metered] {name} · {dt*1000:.0f} ms")
        return result

    tool.coroutine = _wrapped
    return tool

if tools:
    tools = [metered(t, cost) for t in tools]
    print(f"wrapped {len(tools)} tools — every call now hits the ₹ meter")
"""),
    md("""
> **The general lesson, beyond Sarvam.** The moment you put a protocol boundary
> between your code and a billed API, your observability stops at that boundary.
> Whatever you cannot see, you cannot cost — and whatever you cannot cost will
> surprise you at scale. Meter at the boundary you *do* control.
"""),

    # ───────────────────────────────────────────── 4 · tool-choice accuracy
    md("""
---
## 4 · Does it pick the right tool? Measure, do not assume.

This is Lab 07's eval harness, pointed at tool selection. Ten utterances, each with
the tool that *should* fire.
"""),
    code("""
CASES = [
    {"say": "Transcribe the Hindi audio at ./data/mcp_caller.wav",
     "expect": "stt"},
    {"say": "Say 'आपका स्वागत है' out loud in Hindi and save it",
     "expect": "tts"},
    {"say": "Translate 'What is my loan balance?' into Tamil",
     "expect": "translate"},
    {"say": "Convert the name 'भावेश' into Roman script",
     "expect": "translit"},
    {"say": "What language is this text: 'என் கடன் தவணை எப்போது?'",
     "expect": "identify"},
    {"say": "Summarise in one line: an NBFC customer asking about EMI dates",
     "expect": "llm"},
]

def bucket(tool_name):
    \"\"\"Map a concrete tool name onto the coarse capability we expected.\"\"\"
    n = tool_name.lower()
    if "transcribe" in n or "stt" in n:      return "stt"
    if "tts" in n or "speak" in n:            return "tts"
    if "transliterate" in n:                  return "translit"
    if "translate" in n:                      return "translate"
    if "identify" in n or "language" in n:    return "identify"
    if "llm" in n or "complete" in n:         return "llm"
    return n
"""),
    code("""
# Run the eval. Each case is a fresh agent invocation with seed-equivalent settings.
results = []
if tools and HAVE_DEPS:
    ev_agent = create_react_agent(llm, tools=tools)
    for c in CASES:
        picked = None
        try:
            out = await ev_agent.ainvoke({"messages": [{"role": "user", "content": c["say"]}]})
            for m in out["messages"]:
                for call in (getattr(m, "tool_calls", None) or []):
                    picked = picked or bucket(call["name"])
            cost.llm(2200, 200)
        except Exception as e:
            picked = f"ERROR:{type(e).__name__}"
        ok = (picked == c["expect"])
        results.append({"say": c["say"][:44], "expected": c["expect"],
                        "picked": picked, "ok": ok})
        print(f"  {'✓' if ok else '✕'}  expected={c['expect']:<10} got={str(picked):<12}")

    hits = sum(r["ok"] for r in results)
    print(f"\\nTOOL-CHOICE ACCURACY: {hits}/{len(results)} = {hits/len(results):.0%}")
else:
    print("Skipped — MCP unavailable.")
"""),
    md("""
**How to read your number.** Anything under ~90% means an agent that occasionally
does the wrong thing to a real customer. The usual causes, in order of frequency:

1. **Too many tools.** Fourteen options with overlapping descriptions is a hard
   choice. Section 5 fixes this.
2. **Vague tool descriptions.** The model only sees the description string.
3. **Ambiguous user phrasing** — which is what real callers produce.

Notice that all three are *context* problems, not model problems. That is the bridge
into Lab 12.
"""),

    # ───────────────────────────────────────────── 5 · the price
    md("""
---
## 5 · The two prices: latency and tokens

MCP is a protocol hop. Protocol hops cost milliseconds. For a voice agent working to
an 800 ms budget (Lab 08), milliseconds are the whole game.
"""),
    code("""
# ── Latency: MCP round-trip vs the direct SDK call, same work ────────────
import statistics

def time_direct_stt(path, n=3):
    ts = []
    for _ in range(n):
        t0 = time.perf_counter()
        with open(path, "rb") as f:
            client.speech_to_text.transcribe(file=f, model="saaras:v3",
                                             language_code="hi-IN", mode="transcribe")
        ts.append((time.perf_counter() - t0) * 1000)
        cost.stt(duration(path))
    return ts

async def time_mcp_stt(path, n=3):
    ts = []
    stt_tool = next((t for t in tools if "transcribe" in t.name or "stt" in t.name), None)
    if stt_tool is None: return []
    for _ in range(n):
        t0 = time.perf_counter()
        try:
            fn = stt_tool.coroutine or stt_tool.func
            await fn(file_path=str(Path(path).resolve()), language_code="hi-IN")
        except Exception as e:
            print("   mcp call failed:", type(e).__name__, e); return ts
        ts.append((time.perf_counter() - t0) * 1000)
    return ts

wav = DATA / "mcp_caller.wav"
try:
    direct = time_direct_stt(wav)
    print(f"direct SDK : {statistics.mean(direct):>7.0f} ms   {[f'{t:.0f}' for t in direct]}")
except Exception as e:
    direct = []; print("direct failed:", e)

if tools:
    viamcp = await time_mcp_stt(wav)
    if viamcp:
        print(f"via MCP    : {statistics.mean(viamcp):>7.0f} ms   {[f'{t:.0f}' for t in viamcp]}")
        if direct:
            delta = statistics.mean(viamcp) - statistics.mean(direct)
            print(f"\\nMCP overhead: {delta:+.0f} ms per call")
            print(f"As a share of the 800 ms conversational budget: {abs(delta)/800:.0%}")
"""),
    code("""
# ── Tokens: what do 14 tool schemas cost on EVERY turn? ──────────────────
if tools:
    def approx_tokens(s):     # ~4 chars/token for English+JSON
        return len(s) // 4

    per_tool = []
    for t in tools:
        blob = f"{t.name}\\n{t.description or ''}"
        sch = getattr(t, "args_schema", None)
        if sch is not None:
            try:
                import json as _j
                blob += _j.dumps(sch.model_json_schema()
                                 if hasattr(sch, "model_json_schema") else sch)
            except Exception:
                pass
        per_tool.append((t.name, approx_tokens(blob)))

    per_tool.sort(key=lambda x: -x[1])
    total = sum(n for _, n in per_tool)
    print(f"{'tool':<34}{'~tokens':>9}")
    print("─" * 43)
    for name, n in per_tool[:8]:
        print(f"{name:<34}{n:>9,}")
    print("─" * 43)
    print(f"{'ALL TOOLS, EVERY TURN':<34}{total:>9,}")

    RATE_IN = 29.28 / 1_000_000
    print(f"\\nCost of the tool schemas alone:")
    for turns in (1, 10, 20):
        print(f"  {turns:>2} turn(s): ₹{total*turns*RATE_IN:>7.4f}")
    print(f"  100k calls @ 20 turns: ₹{total*20*RATE_IN*100_000:>12,.0f}")
"""),
    code("""
# ── The fix: give the agent only the tools the job needs ─────────────────
if tools:
    KEEP = ("transcribe", "stt", "tts", "speak", "translate")
    lean = [t for t in tools if any(k in t.name.lower() for k in KEEP)]

    lean_tokens = 0
    for t in lean:
        blob = f"{t.name}\\n{t.description or ''}"
        lean_tokens += len(blob) // 4

    print(f"full set : {len(tools):>2} tools")
    print(f"lean set : {len(lean):>2} tools  →  {[t.name for t in lean]}")
    saved = total - lean_tokens
    print(f"\\nschema tokens saved per turn : ~{saved:,}")
    print(f"over 100k calls @ 20 turns    : ₹{saved*20*RATE_IN*100_000:,.0f}")
    print("\\nFewer tools is not only cheaper — it usually raises tool-choice")
    print("accuracy too, because the model has a smaller decision to make.")
"""),
    md("""
> **Try this now:** re-run section 4's eval with `lean` instead of `tools`. Most
> rooms see accuracy go **up** while cost goes **down**. That result surprises
> people, and it is the most useful thing in this lab.
"""),

    # ───────────────────────────────────────────── 6 · the decision
    md("""
---
## 6 · So when should a voice agent use MCP?

You now have real numbers instead of opinions. Here is how to read them.
"""),
    code("cost.report()"),
    md("""
| | **Reach for MCP** | **Stay on the direct SDK** |
|---|---|---|
| Latency | Not on the critical path — post-call analysis, batch enrichment | **Live conversation.** Every ms comes out of the 800 ms budget |
| Tools | The set changes often; you want config-driven capability | Fixed, known, three calls you will never change |
| Team | Multiple agents/products share one tool surface | One service, one vendor, one hot path |
| Ops | You want capability without shipping code | You need to see and tune every hop |
| Cost | Volume is modest; developer time dominates | High volume — schema tokens on every turn add up |
| Portability | Swap the MCP server, keep the agent | Portability handled at the base-URL layer (Lab 10) |

**The pattern most production teams land on — and it is not a compromise:**

- **Hot path → direct SDK.** The STT → LLM → TTS loop in Lab 08. Every millisecond
  is visible to the caller, so you own every hop.
- **Everything around it → MCP.** Post-call summarisation, translation of the
  transcript, document lookups, pronunciation-dictionary updates, analytics. None of
  it is latency-critical, and all of it benefits from being configuration rather than
  code.

That is the same build-vs-platform line from Deck 05, drawn one level lower — and now
you can draw it with your own measured numbers instead of a vendor's slide.
"""),
    md("""
---
## ✅ Checkpoint

- [ ] `uvx sarvam-mcp` starts and the tool list printed
- [ ] You can name the two namespaces and say which belongs in a production agent
- [ ] An agent transcribed audio without you writing a single wrapper
- [ ] You caused the silent-cost failure and wrapped the tools to fix it
- [ ] You have a **tool-choice accuracy number** for your own run
- [ ] You have an **MCP latency overhead number** in milliseconds
- [ ] You can state the per-turn token cost of carrying 14 tool schemas

## 🧪 Try this

1. Re-run the section 4 eval with the `lean` tool set. Accuracy up or down? Cost?
2. Rewrite one tool's description to be sharper. Does the tool it competes with stop
   winning? This is prompt engineering applied to *tools*, not messages.
3. Add a second MCP server (a filesystem or HTTP one) alongside Sarvam. Does
   tool-choice accuracy degrade as the pool grows?
4. Put the MCP call **behind** the audio, not in front of it — start playing a filler
   phrase, then call the tool. How much of the overhead disappears perceptually?
5. Take the metering wrapper from section 3 and generalise it into a decorator you
   could publish. That is a genuinely useful open-source contribution.
"""),
])


# ═══════════════════════════════════════ LAB 12 — CONTEXT ENGINEERING
build("12_Context_Engineering_Markdown_llms_txt_Context7_Skills.ipynb",
      "Context Engineering", [
    header("LAB 12 · CONTEXT ENGINEERING",
           "Making your coding assistant write Sarvam code that runs",
           "Markdown docs · llms.txt · Context7 · Agent Skills — four layers, measured against the gotchas list",
           "65 min", "≈ ₹4", "Lab 00"),
    SETUP, COSTMETER,

    md("""
## The problem, in one sentence

Ask any coding assistant for a Sarvam snippet and it will confidently write
`client.chat.completions.create(...)` — a method that **does not exist** in this SDK.

It is not being stupid. It has read a hundred thousand OpenAI examples and roughly
none for Sarvam, so it pattern-matches to the thing it knows. The fix is not a better
model. **The fix is better context.**

This lab builds four layers of context, cheapest first, and then does something the
internet almost never does: **measures whether each one actually helped.**

| Layer | What it is | Setup cost | Freshness |
|---|---|---|---|
| 1 · **Markdown docs** | Append `.md` to any docs URL | Zero | Live |
| 2 · **llms.txt** | A curated index the vendor publishes for LLMs | Zero | Live |
| 3 · **Context7** | An MCP server that serves indexed docs on demand | One config block | Index lag |
| 4 · **Agent Skills** | Portable folders of SDK signatures + gotchas | One install | You own it |

> **This lab is cheap (≈ ₹4) and mostly offline.** Most cells fetch documents and
> read files. That makes it the best candidate in the series for a free campus
> session — high value, near-zero credit burn.
"""),

    # ───────────────────────────────────────────── 1 · the baseline
    md("""
---
## 1 · The baseline — what a context-free assistant produces

We will use Sarvam-105B itself as the stand-in for "a coding assistant with no
special context". Same failure modes, and it keeps the lab self-contained.
"""),
    code("""
TASK = (
    "Write a short Python snippet using the `sarvamai` SDK that:\\n"
    "1. transcribes ./data/call.wav (Hindi, 8 kHz telephony audio), and\\n"
    "2. sends the transcript to Sarvam's chat model for a one-line summary.\\n"
    "Return ONLY code, no prose."
)

def generate(task, context="", model="sarvam-105b", label=""):
    \"\"\"Ask the model for code, optionally with retrieved context prepended.\"\"\"
    sys_msg = "You are a senior Python engineer. Output only runnable code."
    user = (f"{context}\\n\\n---\\n\\n{task}" if context else task)
    r = client.chat.completions(
        model=model,
        messages=[{"role": "system", "content": sys_msg},
                  {"role": "user",   "content": user}],
        max_tokens=900, temperature=0.1, reasoning_effort=None,
    )
    cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
    out = r.choices[0].message.content or ""
    if label:
        print(f"── {label} ── ({r.usage.prompt_tokens} in / {r.usage.completion_tokens} out)")
    return out

baseline = generate(TASK, label="LAYER 0 · no context")
print(baseline[:1400])
"""),

    # ───────────────────────────────────────────── 2 · the rubric
    md("""
---
## 2 · The rubric — your own gotchas list, as code

Deck 08 slide 4 is the most-screenshotted artefact of the whole workshop. Here it
becomes an **automated grader**. Each gotcha is a regex for the *wrong* pattern; a
generation scores a point for every trap it avoids.

Deterministic, free, and transparent — no judge model, no API call, no opinion.
"""),
    code("""
import re

# Each rule: (id, human description, regex matching the WRONG pattern, the fix)
GOTCHAS = [
    ("no-create",   "client.chat.completions.create(...) — method does not exist",
     r"chat\\s*\\.\\s*completions\\s*\\.\\s*create\\s*\\(",
     "client.chat.completions(...) — no .create"),

    ("rest-sample-rate", "sample_rate= passed to the REST transcribe() call",
     r"speech_to_text\\s*\\.\\s*transcribe\\s*\\([^)]*sample_rate\\s*=",
     "Not a REST parameter — the WAV header carries it (Lab 02 §2)"),

    ("doc-language-code", "language_code= on a Document AI call",
     # [\\s\\S] so the rule still fires when the call spans several lines
     r"(doc_ai|document_intelligence)[\\s\\S]{0,160}?language_code\\s*=",
     "Use language= on Document AI"),

    ("md-not-markdown", 'output_format="markdown" instead of "md"',
     r"output_format\\s*=\\s*[\\\"']markdown[\\\"']",
     'Use "md"'),

    ("schema-dict",  "schema passed as a dict instead of a JSON string",
     r"schema\\s*=\\s*\\{",
     "json.dumps(schema)"),

    ("bare-file",    "file=open(...) on a Document AI call",
     r"(doc_ai|document_intelligence)[\\s\\S]{0,160}?file\\s*=\\s*open\\s*\\(",
     "file=[(name, handle, mime)] — an array"),

    ("terminal-state", "reading results without polling for a terminal state",
     r"get_results?\\s*\\((?![^)]*status)",
     "Poll get_status() / wait_until_complete() first"),

    ("implicit-model", "no explicit model= argument anywhere",
     r"\\A(?:(?!model\\s*=).)*\\Z",
     "Always pass model= explicitly — defaults drift"),
]

def score(codeblock, verbose=False):
    \"\"\"Return (points, max, [failed ids]). One point per gotcha AVOIDED.\"\"\"
    failed = []
    for gid, desc, pattern, fix in GOTCHAS:
        if re.search(pattern, codeblock, flags=re.S):
            failed.append(gid)
            if verbose:
                print(f"   ✕ {gid:<18} {desc}")
                print(f"     fix: {fix}")
    return len(GOTCHAS) - len(failed), len(GOTCHAS), failed

pts, mx, failed = score(baseline, verbose=True)
print(f"\\nBASELINE SCORE: {pts}/{mx} gotchas avoided")
"""),
    md("""
> **A note on rule accuracy — and why this lab corrects the deck.** The original
> Deck 08 table listed *"8 kHz audio, no `sample_rate` → garbage transcript"*. Lab 02
> disproved that: `sample_rate` is **not a REST parameter at all**, and passing it
> raises `TypeError`. The rule above encodes the *corrected* fact. If your rubric
> encodes a stale belief, it will punish correct code — which is exactly the failure
> mode this whole lab exists to prevent.
"""),

    # ───────────────────────────────────────────── 3 · markdown
    md("""
---
## 3 · Layer 1 — Markdown docs, for free

Every page on `docs.sarvam.ai` is available as clean Markdown: **append `.md` to the
URL**. No key, no SDK, no setup.

Why it matters: HTML spends most of its tokens on navigation, scripts and styling.
Markdown is nearly all content. Measure the difference.
"""),
    code("""
import httpx

PAGE = "https://docs.sarvam.ai/api-reference/chat/chat-completions"

def fetch(url, timeout=30):
    try:
        r = httpx.get(url, timeout=timeout, follow_redirects=True)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"  fetch failed {url}: {type(e).__name__}: {e}")
        return ""

html = fetch(PAGE)
mark = fetch(PAGE + ".md")

def approx_tokens(s): return len(s) // 4

print(f"{'form':<12}{'chars':>10}{'~tokens':>10}")
print("─" * 32)
print(f"{'HTML':<12}{len(html):>10,}{approx_tokens(html):>10,}")
print(f"{'Markdown':<12}{len(mark):>10,}{approx_tokens(mark):>10,}")
if html and mark:
    print(f"\\nMarkdown is {len(html)/max(len(mark),1):.1f}x smaller — "
          f"~{approx_tokens(html)-approx_tokens(mark):,} tokens saved per page")
"""),
    code("""
print(mark[:900] if mark else "(markdown fetch failed — check network access)")
"""),

    # ───────────────────────────────────────────── 4 · llms.txt
    md("""
---
## 4 · Layer 2 — `llms.txt`, the vendor's own curated index

[`llms.txt`](https://llmstxt.org/) is a small open standard. The format is strict and
deliberately tiny:

| Part | Required | Content |
|---|---|---|
| H1 | **Yes** — the only required part | Project name |
| Blockquote | No | One-paragraph summary |
| Body | No | Any markdown *except headings* |
| H2 sections | No | Lists of `[name](url): notes` links |

**One honest correction to what you will read elsewhere:** `llms-full.txt` is **not**
part of the spec. It is a widely-adopted convention for "everything, concatenated",
and Sarvam ships one — but do not expect every vendor to.
"""),
    code("""
LLMS      = "https://docs.sarvam.ai/llms.txt"
LLMS_FULL = "https://docs.sarvam.ai/llms-full.txt"

idx  = fetch(LLMS)
full = fetch(LLMS_FULL, timeout=60)

print(f"{'file':<16}{'chars':>12}{'~tokens':>10}")
print("─" * 38)
print(f"{'llms.txt':<16}{len(idx):>12,}{approx_tokens(idx):>10,}")
print(f"{'llms-full.txt':<16}{len(full):>12,}{approx_tokens(full):>10,}")
print()
print("llms.txt is the MAP. llms-full.txt is the TERRITORY.")
print("Feed the map when you need to choose; feed the territory when you need detail.")
"""),
    code("""
# Parse llms.txt per the spec: H1, optional blockquote, H2 link sections
def parse_llms_txt(text):
    title, summary, sections, current = None, [], {}, None
    for line in text.split("\\n"):
        s = line.strip()
        if s.startswith("# ") and title is None:
            title = s[2:].strip()
        elif s.startswith("> "):
            summary.append(s[2:].strip())
        elif s.startswith("## "):
            current = s[3:].strip(); sections[current] = []
        elif s.startswith("-") and current:
            m = re.match(r"-\\s*\\[([^\\]]+)\\]\\(([^)]+)\\)\\s*:?\\s*(.*)", s)
            if m:
                sections[current].append({"name": m.group(1), "url": m.group(2),
                                          "note": m.group(3)})
    return title, " ".join(summary), sections

if idx:
    title, summary, sections = parse_llms_txt(idx)
    print("TITLE  :", title)
    print("SUMMARY:", (summary or "(none)")[:200])
    print(f"\\n{len(sections)} section(s):")
    for name, links in sections.items():
        print(f"  {name:<34} {len(links):>3} links")
        for l in links[:2]:
            print(f"      {l['name'][:40]:<42} {l['url'][:52]}")
else:
    title, summary, sections = None, "", {}
    print("(llms.txt fetch failed)")
"""),
    code("""
# Use the index the way an agent would: pick the relevant pages, fetch only those
def retrieve(query_words, sections, limit=2):
    \"\"\"Naive relevance: score links by keyword overlap, fetch the winners as .md\"\"\"
    scored = []
    for name, links in sections.items():
        for l in links:
            blob = f"{name} {l['name']} {l['note']}".lower()
            hits = sum(w.lower() in blob for w in query_words)
            if hits: scored.append((hits, l))
    scored.sort(key=lambda x: -x[0])
    out = []
    for _, l in scored[:limit]:
        url = l["url"]
        if not url.startswith("http"):
            url = "https://docs.sarvam.ai" + url
        body = fetch(url if url.endswith(".md") else url + ".md")
        if body:
            out.append(f"# {l['name']}\\n{body[:6000]}")
            print(f"  retrieved {l['name']}  ({approx_tokens(body):,} tokens)")
    return "\\n\\n".join(out)

ctx_llms = retrieve(["speech", "text", "transcribe", "chat"], sections) if sections else ""
print(f"\\nretrieved context: ~{approx_tokens(ctx_llms):,} tokens")
"""),

    # ───────────────────────────────────────────── 5 · Context7
    md("""
---
## 5 · Layer 3 — Context7, docs on demand over MCP

[Context7](https://context7.com/) is a documentation index that coding assistants
query **through MCP**, so the docs arrive as tool results rather than as something you
paste. Sarvam maintains a page for it, and the docs are **already indexed** —
[`docs.sarvam.ai/api/developer-tools/context7`](https://docs.sarvam.ai/api/developer-tools/context7).

**The Sarvam library ID is `/websites/sarvam_ai`.**

### Setup — one config block, no API key

```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

Drop that into Claude Code, Cursor, Windsurf or any MCP client. A free key from
`context7.com/dashboard` raises rate limits but is not required.

### Using it

Two tools: **`resolve-library-id`** (name → Context7 ID) and **`query-docs`** (ID +
question → docs). In practice you skip the resolve step by naming the library:

> *"Use library `/websites/sarvam_ai`. Write a Python script that transcribes
> `audio.wav` with the latest Sarvam speech-to-text model."*

### When Context7 is the **wrong** tool

Be honest about this in the room:

- **Index lag.** Context7 re-crawls on its own schedule. For an API shipping as fast
  as Sarvam's, the vendor's own `llms.txt` is fresher by definition.
- **Another moving part.** One more MCP server, one more failure mode, one more thing
  to explain to a new team member.
- **You already have the docs.** If a page is two fetches away, layer 1 is simpler.

Context7 earns its place when you are working across **many** libraries and want one
uniform way to reach all their docs — not when you need the freshest possible truth
about one.
"""),
    code("""
# Verify the config is well-formed, and (optionally) that the server starts.
import json, shutil, subprocess

CONTEXT7_CONFIG = {
    "mcpServers": {
        "context7": {"command": "npx", "args": ["-y", "@upstash/context7-mcp"]}
    }
}
print(json.dumps(CONTEXT7_CONFIG, indent=2))
Path("context7_mcp_config.json").write_text(json.dumps(CONTEXT7_CONFIG, indent=2))
print("\\nwrote context7_mcp_config.json — paste into your MCP client\\n")

SARVAM_LIBRARY_ID = "/websites/sarvam_ai"
print("Sarvam library ID:", SARVAM_LIBRARY_ID)
print("Browse it at    : https://context7.com/websites/sarvam_ai")

if shutil.which("npx") is None:
    print("\\n(npx not found — install Node.js to run the Context7 server locally)")
else:
    print("\\n(npx present — the config above will work in your MCP client)")
"""),

    # ───────────────────────────────────────────── 6 · Agent Skills
    md("""
---
## 6 · Layer 4 — Agent Skills, the layer you own

The first three layers hand your assistant **documentation**. Documentation tells it
what the API *offers*. It does not tell it what people *get wrong*.

An [Agent Skill](https://agentskills.io/specification) is a folder your assistant
loads that carries exactly that: signatures, and the traps. Sarvam publishes five —
`chat`, `speech-to-text`, `text-to-speech`, `translate`, `voice-agents` — and they
point at `llms.txt` for anything deeper.

```bash
npx skills add sarvamai/skills            # all five
npx skills add sarvamai/skills --skill chat
npx skills add sarvamai/skills --list     # browse first
```

Works in Claude Code, Cursor, Windsurf, and anything implementing the spec.
"""),
    md("""
### The spec, exactly

A skill is a directory with a `SKILL.md` at minimum:

```
skill-name/
├── SKILL.md          # required: YAML frontmatter + markdown body
├── scripts/          # optional: runnable code
├── references/       # optional: detail loaded on demand
└── assets/           # optional: templates, data
```

| Frontmatter | Required | Constraint |
|---|---|---|
| `name` | **Yes** | ≤64 chars, `a-z0-9-` only, no leading/trailing/double hyphen, **must match the directory name** |
| `description` | **Yes** | ≤1024 chars. Say *what it does* **and** *when to use it* |
| `license` | No | Name or bundled file |
| `compatibility` | No | ≤500 chars — environment needs |
| `metadata` | No | Arbitrary string→string map |
| `allowed-tools` | No | Space-separated pre-approved tools (experimental) |

**Progressive disclosure is the design constraint that matters.** The agent loads:

1. `name` + `description` (~100 tokens) — for **every** installed skill, at startup
2. The `SKILL.md` body (**keep under 5,000 tokens / 500 lines**) — only when activated
3. `references/`, `scripts/`, `assets/` — only when actually needed

So the description is doing triage for a model that has not read your skill yet.
Write it for that job.
"""),
    code("""
# ── Author a real skill: teach an assistant to always meter Sarvam calls ──
SKILL_DIR = Path("skills/sarvam-cost-metering")
(SKILL_DIR / "references").mkdir(parents=True, exist_ok=True)

SKILL_MD = '''---
name: sarvam-cost-metering
description: Adds rupee cost tracking to Sarvam AI API calls. Use whenever writing or reviewing Python that calls the sarvamai SDK - speech_to_text, text_to_speech, chat.completions, translate, or doc_ai - so that every billed call is accompanied by a CostMeter entry and the script prints a total in rupees.
license: Apache-2.0
compatibility: Requires Python 3.10+ and the sarvamai SDK
metadata:
  author: AIVidhya4Sarvam
  version: "1.0"
---

# Sarvam cost metering

Every Sarvam API call costs money. Code that calls Sarvam without tracking spend is
incomplete. When you write or review such code, attach a meter entry to every billed
call and print a total at the end.

## The rule

For each billed call, add the matching meter line immediately after it:

| API | Billed by | Meter call |
|---|---|---|
| `speech_to_text.transcribe` | audio seconds | `cost.stt(seconds)` |
| `speech_to_text` + diarization | audio seconds | `cost.stt(seconds, diarized=True)` |
| `text_to_speech.convert` | characters | `cost.tts(len(text), v3=False)` |
| `text.translate` / `transliterate` | characters | `cost.text(len(s), kind="translate")` |
| `chat.completions` | tokens | `cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)` |
| `doc_ai` extract/digitise | pages | `cost.doc(n_pages)` |

End every script with `cost.report()`.

## Correct usage

```python
from cost_meter import CostMeter
cost = CostMeter()

r = client.chat.completions(model="sarvam-105b", messages=msgs,
                            max_tokens=400, reasoning_effort=None)
cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)

cost.report()
```

## Non-negotiables

- Always pass `model=` explicitly. Defaults drift between releases.
- `client.chat.completions(...)` has **no** `.create()`. Writing
  `client.chat.completions.create(...)` raises `AttributeError`.
- If `reasoning_effort` is left on with a small `max_tokens`, reasoning consumes the
  whole budget and `content` comes back `None`. Pass `reasoning_effort=None` or raise
  `max_tokens`.
- MCP tool calls do not report usage back. Meter them from your own inputs.

See [references/RATES.md](references/RATES.md) for current pricing.
'''

RATES_MD = '''# Sarvam rates (August 2026)

Verify at https://docs.sarvam.ai/api/getting-started/pricing before quoting.

| Item | Rate |
|---|---|
| STT | Rs 30 / hour |
| STT + diarization | Rs 45 / hour |
| TTS bulbul:v2 | Rs 15 / 10k chars |
| TTS bulbul:v3 | Rs 30 / 10k chars |
| Translate / transliterate | Rs 20 / 10k chars |
| LLM input | Rs 29.28 / 1M tokens |
| LLM cached input | Rs 10.98 / 1M tokens |
| LLM output | Rs 73.20 / 1M tokens |
| Document AI | Rs 0.50 / page |

Estimates are a conservative upper bound: prompt caching, free-tier credit and
invoice rounding all push the real bill slightly lower.
'''

(SKILL_DIR / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")
(SKILL_DIR / "references" / "RATES.md").write_text(RATES_MD, encoding="utf-8")

for p in sorted(SKILL_DIR.rglob("*")):
    print(f"  {p.relative_to(SKILL_DIR.parent)}  ({p.stat().st_size if p.is_file() else '-'} bytes)")
"""),
    code("""
# ── Validate against the spec, before any agent ever sees it ─────────────
def validate_skill(skill_dir):
    errs, warns = [], []
    p = Path(skill_dir); md_path = p / "SKILL.md"
    if not md_path.exists():
        return ["SKILL.md is missing"], []

    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return ["SKILL.md must begin with YAML frontmatter (---)"], []

    fm_raw = text.split("---", 2)[1]
    fm = {}
    for line in fm_raw.split("\\n"):
        if ":" in line and not line.startswith((" ", "\\t", "-")):
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()

    name = fm.get("name", "")
    if not name:                                errs.append("`name` is required")
    if len(name) > 64:                          errs.append("`name` exceeds 64 chars")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name or ""):
        errs.append(f"`name` must be lowercase a-z0-9 with single hyphens: {name!r}")
    if name != p.name:
        errs.append(f"`name` ({name!r}) must match directory ({p.name!r})")

    desc = fm.get("description", "")
    if not desc:                                errs.append("`description` is required")
    if len(desc) > 1024:                        errs.append("`description` exceeds 1024 chars")
    if desc and " use " not in desc.lower() and not desc.lower().startswith("use "):
        warns.append("`description` should say WHEN to use the skill, not just what it does")

    comp = fm.get("compatibility", "")
    if len(comp) > 500:                         errs.append("`compatibility` exceeds 500 chars")

    body = text.split("---", 2)[2]
    n_lines, n_tok = len(body.split("\\n")), len(body) // 4
    if n_lines > 500:   warns.append(f"body is {n_lines} lines — spec recommends under 500")
    if n_tok   > 5000:  warns.append(f"body is ~{n_tok} tokens — spec recommends under 5000")

    print(f"  name        : {name}")
    print(f"  description : {len(desc)} chars")
    print(f"  body        : {n_lines} lines, ~{n_tok} tokens")
    return errs, warns

errs, warns = validate_skill(SKILL_DIR)
print()
for e in errs:  print("  ERROR  ", e)
for w in warns: print("  WARN   ", w)
print("\\n" + ("✓ VALID — conforms to the Agent Skills spec" if not errs
               else f"✕ {len(errs)} error(s) to fix"))
print("\\nOfficial validator:  skills-ref validate ./skills/sarvam-cost-metering")
"""),

    # ───────────────────────────────────────────── 7 · the measurement
    md("""
---
## 7 · The measurement — does any of this actually help?

Same task. Same model. Four different context layers. Scored against your own
gotchas list.

This is the section that makes the lab worth running. Everything above is a claim;
this is the evidence.
"""),
    code("""
# Build the context payload for each layer
skill_text = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")

LAYERS = [
    ("0 · no context",        ""),
    ("1 · markdown page",     mark[:8000] if mark else ""),
    ("2 · llms.txt retrieval", ctx_llms[:8000] if ctx_llms else ""),
    ("3 · agent skill",       skill_text),
    ("4 · skill + markdown",  (skill_text + "\\n\\n" + (mark or ""))[:12000]),
]

runs = []
for label, ctx in LAYERS:
    if not ctx and label != "0 · no context":
        print(f"  skipping {label} — context unavailable")
        continue
    out = generate(TASK, ctx, label=label)
    pts, mx, failed = score(out)
    runs.append({"layer": label, "score": pts, "max": mx,
                 "failed": failed, "ctx_tokens": approx_tokens(ctx), "code": out})
    print(f"     → {pts}/{mx} gotchas avoided   (context ~{approx_tokens(ctx):,} tokens)")
"""),
    code("""
# ── The result table + a chart you can screenshot ────────────────────────
if runs:
    print(f"{'layer':<24}{'score':>8}{'ctx tokens':>13}   {'bar':<24}")
    print("─" * 72)
    for r in runs:
        bar = "█" * int(r["score"] / r["max"] * 22)
        print(f"{r['layer']:<24}{r['score']:>3}/{r['max']:<4}{r['ctx_tokens']:>13,}   {bar}")
    print("─" * 72)

    best = max(runs, key=lambda r: r["score"])
    base = runs[0]
    print(f"\\nbest layer : {best['layer']}  ({best['score']}/{best['max']})")
    print(f"improvement over no context: +{best['score'] - base['score']} gotchas avoided")

    still = set(best["failed"])
    if still:
        print(f"\\nStill failing even at the best layer: {sorted(still)}")
        print("Each of those is a candidate line for your NEXT skill revision.")
    else:
        print("\\nClean sweep at the best layer.")
"""),
    code("""
# Show the winning generation so the room can read what good looks like
if runs:
    print(f"── {best['layer']} ──\\n")
    print(best["code"][:1600])
"""),
    code("cost.report()"),

    # ───────────────────────────────────────────── 8 · decision
    md("""
---
## 8 · Which layer, when

| Situation | Reach for |
|---|---|
| One page, one question, right now | **Markdown** — append `.md`, paste, done |
| "What does this platform even offer?" | **llms.txt** — the map, then fetch the pages that matter |
| Working across many libraries at once | **Context7** — one uniform way to reach all their docs |
| Your team repeats the same mistakes | **Agent Skills** — encode the fix once, everyone inherits it |
| The API ships faster than any index | **llms.txt** — the vendor publishes it; nothing is fresher |
| You need something enforced, not suggested | **Agent Skills** — docs describe, skills prescribe |

**The two-layer default that works for most teams:** an **Agent Skill** carrying your
house rules and the gotchas, plus **`llms.txt`** for live detail. The skill is
prescriptive and yours; `llms.txt` is descriptive and current. Between them you have
covered both halves of the problem.

**The compounding move.** Every time a teammate hits a Sarvam trap, add one line to
the skill. Six months in, that file is the most valuable engineering artefact your
team owns — and unlike documentation, it is loaded automatically by every assistant
your team uses.
"""),
    md("""
---
## ✅ Checkpoint

- [ ] You saw a context-free assistant produce code with real, named defects
- [ ] Your gotchas list runs as an automated grader
- [ ] You measured the token difference between HTML and Markdown docs
- [ ] You parsed `llms.txt` and used it to retrieve only the pages you needed
- [ ] Context7's config is written to disk and you know the Sarvam library ID
- [ ] You **authored and validated** an Agent Skill against the real spec
- [ ] You have a bar chart showing which layer actually helped most

## 🧪 Try this

1. **Add a gotcha.** Next trap you hit, write the regex, add the row, re-run §7.
   Does your best layer still win?
2. **Shrink the skill.** Halve the `SKILL.md` body and re-measure. Where is the
   knee — how little can you say and keep the score?
3. **Rewrite the description only.** Leave the body untouched, sharpen the
   `description` field. Does activation improve? (This is triage-prompt engineering.)
4. **Swap the model.** Run §7 with `sarvam-m` instead of `sarvam-105b`. Does good
   context close the gap between a small model and a large one? Usually: yes, mostly.
5. **Ship it.** Polish the `sarvam-cost-metering` skill and open a PR against
   [`sarvamai/skills`](https://github.com/sarvamai/skills). It is a genuine gap in
   their set, and an evening's work.
"""),
])

print("\\nlabs 11-12 done")
