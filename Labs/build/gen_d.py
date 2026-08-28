"""Lab 10: framework interop — LangChain, LangGraph, CrewAI, n8n."""
from nbkit import build, md, code, header, SETUP, COSTMETER

# ═════════════════════════════════════════════ LAB 10 — FRAMEWORK INTEROP
build("10_Framework_Interop_LangChain_LangGraph_CrewAI_n8n.ipynb",
      "Framework Interop", [
    header("LAB 10 · INTEROP", "Your existing framework, Sarvam underneath",
           "LangChain · LangGraph · CrewAI · n8n — same task, four orchestrators, one endpoint",
           "75 min", "≈ ₹6", "Labs 00, 05, 07"),
    SETUP, COSTMETER,

    md("""
## The whole lab in one sentence

Sarvam speaks the OpenAI wire protocol on `/v1/chat/completions` and ships a
standard MCP server on `uvx sarvam-mcp`. **Every framework built on either of
those two contracts inherits Sarvam with a one-line configuration change.**

This notebook proves that for the four orchestrators most Indian teams already
ship on. Each section is 15 minutes, self-contained, and prints rupees. If you
already know one of the four, you can skip to the ones you do not.

> **Prereqs.** Lab 00's cost meter is loaded above. You need `SARVAM_API_KEY` and
> Python 3.10+. Framework installs are called out inline — pip in this cell as
> you go, or run this once up front:
>
> ```bash
> pip install langchain langchain-openai langgraph langchain-mcp-adapters \\
>             crewai crewai-tools httpx
> ```
>
> **The MCP walkthroughs** shell out to `uvx sarvam-mcp` (installed on first run
> from PyPI). On a fresh machine, `pip install uv` first — the `uvx` command
> lives in the `uv` package. If MCP is blocked in your environment (offline
> workshop, corporate proxy), each MCP cell has a plain-SDK fallback marked
> `# no-MCP fallback` — the lab still runs end-to-end.
"""),

    # ────────────────────────────────────────────────────── 0 · sanity check
    md("""
---
## 0 · Prove the endpoint works from the raw OpenAI SDK

Before adding any framework, do the one-line swap on the vanilla `openai`
library. If this cell works, everything downstream is guaranteed to work —
because everything downstream is *this cell* with a wrapper on top.
"""),
    code("""
# pip install openai
from openai import OpenAI

raw = OpenAI(base_url="https://api.sarvam.ai/v1", api_key=API_KEY)

r = raw.chat.completions.create(
    model    = "sarvam-m",
    messages = [{"role": "user", "content": "One sentence: what is a सूत्र?"}],
    max_tokens = 120,
)
print(r.choices[0].message.content)
cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
"""),
    md("""
That is the entire trick. `base_url + api_key + model` and the OpenAI SDK is now
a Sarvam SDK. Every framework in the next four sections is doing exactly this
underneath — you are only changing what wraps it.
"""),

    # ══════════════════════════════════════════════════════════ 1 · LANGCHAIN
    md("""
---
## 1 · LangChain — `ChatOpenAI` is already a Sarvam client

**Time: 15 min. Cost: ~₹1.**

`langchain-openai` is a thin wrapper around the OpenAI SDK. The same swap works
verbatim — every LangChain construct (prompts, chains, agents, structured
output, streaming, tool binding) inherits Sarvam without modification.

```bash
pip install langchain langchain-openai
```
"""),
    code("""
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(
    model      = "sarvam-m",
    base_url   = "https://api.sarvam.ai/v1",
    api_key    = API_KEY,
    temperature= 0.2,
    max_tokens = 400,
    # Sarvam-specific arg — LangChain passes it through model_kwargs
    model_kwargs = {"reasoning_effort": None},
)

reply = llm.invoke([
    SystemMessage("You are a concise NBFC agent. One sentence, in the caller's language."),
    HumanMessage("मेरी अगली EMI कब देय है?"),
])
print(reply.content)
# LangChain surfaces usage under .usage_metadata on newer versions
u = reply.usage_metadata or {}
cost.llm(u.get("input_tokens", 0), u.get("output_tokens", 0))
"""),
    md("""
### 1.1  Tool binding — the standard `@tool` decorator, unchanged
"""),
    code("""
from langchain_core.tools import tool

ACCOUNTS = {"LN1001": {"name": "Rajesh Kumar", "emi": 12500, "due": "15 अगस्त"}}

@tool
def get_account(account_id: str) -> dict:
    \"\"\"Look up an NBFC loan account by its ID (e.g. LN1001).\"\"\"
    return ACCOUNTS.get(account_id, {"error": "not found"})

llm_with_tools = llm.bind_tools([get_account])

msg = llm_with_tools.invoke("The caller's account is LN1001. When is the next EMI?")
print("tool_calls:", msg.tool_calls)
u = msg.usage_metadata or {}
cost.llm(u.get("input_tokens", 0), u.get("output_tokens", 0))
"""),
    md("""
The `tool_calls` list follows OpenAI's standard shape. Every LangChain agent
class (`create_openai_tools_agent`, `create_tool_calling_agent`,
`create_react_agent` from LangGraph) speaks that shape natively — you can hand
this LLM to any of them and it will drive tools correctly.
"""),

    md("""
### 1.2  Sarvam MCP through the LangChain MCP adapter

Same LLM, plus the 14 tools from `sarvam-mcp` — STT, TTS, translate, LID,
vision, pronunciation — appearing as ordinary LangChain tools.

```bash
pip install langchain-mcp-adapters
# and:  pip install uv   (provides the `uvx` command sarvam-mcp launches with)
```
"""),
    code("""
try:
    from langchain_mcp_adapters.client import MultiServerMCPClient
    _HAVE_LC_MCP = True
except ImportError:
    _HAVE_LC_MCP = False
    print("langchain-mcp-adapters not installed — skipping MCP demo")

if _HAVE_LC_MCP:
    mcp = MultiServerMCPClient({
        "sarvam": {
            "command":   "uvx",
            "args":      ["sarvam-mcp"],
            "transport": "stdio",
            "env":       {"SARVAM_API_KEY": API_KEY},
        }
    })
    try:
        tools = await mcp.get_tools()
        print(f"loaded {len(tools)} Sarvam tools via MCP")
        for t in tools[:6]:
            print(f"  · {t.name:<28} {t.description[:60]}")
        print("  ...")
    except Exception as e:
        print(f"MCP server did not start ({e.__class__.__name__}: {e}).")
        print("Common fixes: install uv (`pip install uv`), or set transport='stdio' explicitly.")
"""),
    code("""
# Bind the MCP tools to any React-style agent and let it choose
if _HAVE_LC_MCP and 'tools' in dir() and tools:
    from langgraph.prebuilt import create_react_agent
    agent = create_react_agent(llm, tools=tools)
    try:
        out = await agent.ainvoke({"messages": [
            {"role": "user",
             "content": "Translate 'Independence Day is on 15 August' to Hindi using the sarvam_translate tool. Return only the Hindi text."}
        ]})
        print(out["messages"][-1].content)
        # Rough cost — MCP tools do NOT report token usage back through LangChain,
        # so we credit ~800 tokens per hop as a conservative estimate.
        cost.llm(800, 200, 0)
        cost.text(50, kind="translate")
    except Exception as e:
        print(f"agent invoke failed: {e}")
else:
    # no-MCP fallback — call translate through the SDK directly
    r = client.text.translate(input="Independence Day is on 15 August",
                              source_language_code="en-IN",
                              target_language_code="hi-IN",
                              model="mayura:v1")
    print(r.translated_text); cost.text(50, kind="translate")
"""),
    md("""
**What just happened.** The agent read your prompt, looked at the 14 MCP tool
schemas, picked `sarvam_translate`, called it with the right arguments, and
returned the Hindi string — with zero glue code from you. That is the *value* of
MCP: Sarvam's non-chat surface (STT/TTS/vision/pronunciation) becomes part of
your agent's tool palette without a single wrapper written on your side.
"""),

    # ═════════════════════════════════════════════════════════ 2 · LANGGRAPH
    md("""
---
## 2 · LangGraph — same LLM, the graph you already know

**Time: 15 min. Cost: ~₹1.**

LangGraph is orchestration, not a model layer — it reuses your LangChain
`ChatOpenAI` as-is. Any StateGraph, checkpointer, interrupt, or human-in-the-loop
pattern from Lab 07 works verbatim; the only edit is the endpoint.

```bash
pip install langgraph
```
"""),
    code("""
from typing import TypedDict
from langgraph.graph import StateGraph, END

class RouterState(TypedDict):
    query:    str
    language: str
    answer:   str

def detect(state: RouterState) -> dict:
    \"\"\"Node 1 — classify the caller's language from the query itself.\"\"\"
    r = llm.invoke([
        ("system", "Return only the BCP-47 code, e.g. hi-IN, ta-IN, en-IN. No prose."),
        ("user",   state["query"]),
    ])
    u = r.usage_metadata or {}; cost.llm(u.get("input_tokens", 0), u.get("output_tokens", 0))
    return {"language": r.content.strip()}

def answer(state: RouterState) -> dict:
    \"\"\"Node 2 — reply in the detected language, one sentence.\"\"\"
    r = llm.invoke([
        ("system", f"Reply in {state['language']}. One sentence. No markdown."),
        ("user",   state["query"]),
    ])
    u = r.usage_metadata or {}; cost.llm(u.get("input_tokens", 0), u.get("output_tokens", 0))
    return {"answer": r.content}

g = StateGraph(RouterState)
g.add_node("detect", detect); g.add_node("answer", answer)
g.set_entry_point("detect"); g.add_edge("detect", "answer"); g.add_edge("answer", END)
app = g.compile()

for q in ["मेरा खाता कब खुला था?",
          "என் கடன் தவணை எப்போது?",
          "What is the current interest rate?"]:
    out = app.invoke({"query": q})
    print(f"[{out['language']:<6}] {out['answer']}")
"""),
    md("""
### 2.1  A React agent over the Sarvam MCP tools — one line
"""),
    code("""
# If MCP is available, wire the same tools into a full React loop.
if _HAVE_LC_MCP and 'tools' in dir() and tools:
    from langgraph.prebuilt import create_react_agent
    react = create_react_agent(llm, tools=tools)
    try:
        out = await react.ainvoke({"messages": [
            {"role": "user",
             "content": ("Identify the language of this text and then translate it to English: "
                         "'நமஸ்தே, என்னுடைய கடன் விவரங்கள் என்ன?'. Use the appropriate MCP tools.")}
        ]})
        print(out["messages"][-1].content)
        cost.llm(1200, 300, 0); cost.text(60, kind="translate"); cost.text(60, kind="lid")
    except Exception as e:
        print(f"react agent failed: {e}")
else:
    print("(MCP unavailable — skipped; the plain-LangGraph example above is what the segment tests.)")
"""),
    md("""
**Notice what did not change.** You did not touch `StateGraph`, `add_node`,
`add_edge`, `interrupt`, `MemorySaver`, `create_react_agent`, or any LangGraph
primitive. Your LangGraph investment carries over — the endpoint is the only
thing that moved.
"""),

    # ══════════════════════════════════════════════════════════════ 3 · CREWAI
    md("""
---
## 3 · CrewAI — one `openai/` prefix routes the crew to Sarvam

**Time: 15 min. Cost: ~₹2.**

CrewAI uses `litellm` under the hood. To route to a non-standard
OpenAI-compatible endpoint, **prefix the model name with `openai/`** — this
tells litellm to use the OpenAI HTTP shape, while `base_url` decides where the
request actually goes.

```bash
pip install crewai crewai-tools
```
"""),

    md("""
### 3.1  First, the deliberate failure — because everyone hits it once

Every CrewAI + Sarvam bug report starts here. Trigger the error, read it, then
fix it.
"""),
    code("""
try:
    from crewai import LLM
    # WRONG — no provider prefix. litellm cannot infer that this is OpenAI-shape.
    bad = LLM(
        model    = "sarvam-105b",                    # ← missing the openai/ prefix
        base_url = "https://api.sarvam.ai/v1",
        api_key  = API_KEY,
    )
    bad.call([{"role": "user", "content": "hi"}])
except Exception as e:
    print(f"{e.__class__.__name__}: {e}")
    print("\\n↑ THIS is the gotcha. Fix in the next cell.")
"""),
    code("""
from crewai import LLM

# Correct — `openai/` tells litellm the wire format; base_url decides the host.
sarvam_llm = LLM(
    model    = "openai/sarvam-105b",
    base_url = "https://api.sarvam.ai/v1",
    api_key  = API_KEY,
    temperature = 0.2,
    max_tokens  = 800,
)
print(sarvam_llm.call([{"role": "user", "content": "In one sentence, what is Sarvam-105B?"}]))
cost.llm(200, 120)   # rough — CrewAI does not surface litellm usage cleanly
"""),

    md("""
### 3.2  A minimal 2-agent crew, entirely on Sarvam
"""),
    code("""
from crewai import Agent, Task, Crew, Process

researcher = Agent(
    role      = "Indic Content Researcher",
    goal      = "Find one specific fact about Indian language technology and cite it",
    backstory = "You are a technology journalist covering the Indian AI stack.",
    llm       = sarvam_llm,
    verbose   = False,
    allow_delegation = False,
)

writer = Agent(
    role      = "Bilingual Writer",
    goal      = "Turn a fact into a one-line tweet in both English and Hindi",
    backstory = "You write for Indian developer audiences; you code-mix naturally.",
    llm       = sarvam_llm,
    verbose   = False,
    allow_delegation = False,
)

t1 = Task(description="State one specific fact about Sarvam AI's 105B model — cite one number.",
          expected_output="A single sentence containing one specific number.",
          agent=researcher)

t2 = Task(description="Rewrite that fact as a one-line tweet in English AND its Hindi translation.",
          expected_output="Two lines: English tweet on line 1, Hindi tweet on line 2.",
          agent=writer, context=[t1])

crew = Crew(agents=[researcher, writer], tasks=[t1, t2], process=Process.sequential, verbose=False)
print(crew.kickoff())
cost.llm(1500, 400)   # two-agent handoff, rough
"""),

    md("""
### 3.3  Sarvam MCP as CrewAI tools — `MCPServerAdapter`
"""),
    code("""
try:
    from crewai_tools import MCPServerAdapter
    server_params = {
        "command": "uvx",
        "args":    ["sarvam-mcp"],
        "env":     {"SARVAM_API_KEY": API_KEY},
    }
    with MCPServerAdapter(server_params) as mcp_tools:
        print(f"CrewAI sees {len(mcp_tools)} Sarvam MCP tools")
        speech = Agent(
            role      = "Speech Analyst",
            goal      = "Transliterate a name from Devanagari to Roman using the MCP tool",
            backstory = "You handle inbound Indic text and normalise it for downstream systems.",
            llm       = sarvam_llm,
            tools     = mcp_tools,
            verbose   = False,
        )
        task = Task(description="Transliterate 'भावेशकुमार धर्माणी' from Devanagari to Roman script "
                                "using the sarvam_transliterate tool.",
                    expected_output="Just the Roman-script name.",
                    agent=speech)
        result = Crew(agents=[speech], tasks=[task], verbose=False).kickoff()
        print("\\nresult:", result)
        cost.llm(900, 150); cost.text(40, kind="transliterate")
except ImportError:
    print("crewai-tools not installed — skipping MCP-in-CrewAI demo")
except Exception as e:
    print(f"MCP adapter failed: {e}")
    print("Fallback: call client.text.transliterate(...) from the Sarvam SDK directly.")
"""),

    # ══════════════════════════════════════════════════════════════════ 4 · N8N
    md("""
---
## 4 · n8n — the no-code path (screenshot walkthrough + importable workflow)

**Time: 15 min. Cost: ~₹1 (from the equivalent HTTP calls below).**

n8n does not run inside a Jupyter notebook, so this section does three things
instead:

1. **Documents the exact node configuration** — what to click, in order.
2. **Exports a workflow JSON** you can import into your own n8n instance (Import
   from File → Paste the JSON block below).
3. **Runs the equivalent HTTP calls** here in the notebook — so you can prove
   the endpoint works before you ever open n8n, and so the ₹ meter stays honest.
"""),

    md("""
### 4.1  The credential — one-time setup in n8n

Credentials → **Add Credential** → **OpenAI API**:

| Field | Value |
|---|---|
| **API Key** | your `SARVAM_API_KEY` |
| **Organization ID** | *(leave blank)* |
| **Base URL** | `https://api.sarvam.ai/v1` |

Save it as **"Sarvam (OpenAI-compatible)"**. Every OpenAI node in every future
workflow can now pick this credential and it will point at Sarvam.

### 4.2  The Chat Model node — one field to know about

Add an **OpenAI** node → operation **Message a Model**. Pick the Sarvam
credential you just made. Then:

> **The model dropdown lists OpenAI's catalogue.** It does not know about
> Sarvam models. **Click the field, type `sarvam-m` (or `sarvam-105b`),
> hit Enter.** n8n accepts custom values and passes the string straight
> through to the API. This is the single thing that surprises everyone.

### 4.3  The MCP Client node — for the other 13 APIs

If your n8n has the **MCP Client** community node installed (Settings →
Community Nodes → search `n8n-nodes-mcp`), add it and configure:

| Field | Value |
|---|---|
| **Connection Type** | Command Line (stdio) |
| **Command** | `uvx` |
| **Arguments** | `sarvam-mcp` |
| **Environment** | `SARVAM_API_KEY=sk_...` |

All 14 Sarvam MCP tools now appear in the workflow palette. Chain them like
any other node.

### 4.4  The escape hatch — the plain HTTP Request node

If a node does not exist, or misbehaves, or you want zero dependencies: use
n8n's built-in **HTTP Request** node.

| Field | Value |
|---|---|
| **Method** | POST |
| **URL** | `https://api.sarvam.ai/v1/chat/completions` |
| **Auth** | Header Auth · `Authorization: Bearer {{$env.SARVAM_API_KEY}}` |
| **Body** | JSON, with `model`, `messages`, `max_tokens` |

Below is exactly that call, run from Python so you can see it works before you
touch n8n.
"""),
    code("""
# What the n8n HTTP Request node would send — reproduced here so you can prove it works
import httpx

resp = httpx.post(
    "https://api.sarvam.ai/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type":  "application/json",
    },
    json={
        "model": "sarvam-m",
        "messages": [
            {"role": "system", "content": "You are an NBFC support bot. One line."},
            {"role": "user",   "content": "Kya EMI aaj de sakte hain?"},
        ],
        "max_tokens": 120,
    },
    timeout=30,
)
resp.raise_for_status()
data = resp.json()
print(data["choices"][0]["message"]["content"])
cost.llm(data["usage"]["prompt_tokens"], data["usage"]["completion_tokens"])
"""),

    md("""
### 4.5  Copy-paste starter workflow (JSON)

This is a minimal n8n workflow: **When clicked → OpenAI (Sarvam) → Set output**.
Import it (File → Import from File → paste), then attach your Sarvam credential
to the OpenAI node.
"""),
    code(r"""
N8N_WORKFLOW = r'''
{
  "name": "Sarvam · OpenAI-compatible starter",
  "nodes": [
    {
      "parameters": {},
      "id": "trigger-1",
      "name": "When clicked",
      "type": "n8n-nodes-base.manualTrigger",
      "typeVersion": 1,
      "position": [240, 300]
    },
    {
      "parameters": {
        "resource": "chat",
        "operation": "message",
        "model": "sarvam-m",
        "messages": {
          "messageValues": [
            { "role": "system", "content": "You are an NBFC support bot. One line." },
            { "role": "user",   "content": "Kya EMI aaj de sakte hain?" }
          ]
        },
        "options": { "maxTokens": 120 }
      },
      "id": "openai-1",
      "name": "OpenAI (Sarvam)",
      "type": "n8n-nodes-base.openAi",
      "typeVersion": 1,
      "position": [520, 300],
      "credentials": {
        "openAiApi": { "id": "REPLACE_ME", "name": "Sarvam (OpenAI-compatible)" }
      }
    }
  ],
  "connections": {
    "When clicked": { "main": [[{ "node": "OpenAI (Sarvam)", "type": "main", "index": 0 }]] }
  }
}
'''
# Save it so participants can grab it from disk without copy-paste line breaks
open(OUT / "sarvam_n8n_starter.json", "w").write(N8N_WORKFLOW)
print("wrote", OUT / "sarvam_n8n_starter.json")
"""),

    # ═════════════════════════════════════════════════════ 5 · THE GOTCHAS
    md("""
---
## 5 · The four gotchas — trigger them on purpose

Every one of these has bitten every team that has tried this. The lab makes you
cause each failure, then fix it, in under two minutes each.
"""),

    md("### 5.1  LangChain — `reasoning_effort` silently ignored → `content is None`"),
    code("""
# Sarvam's chat API accepts a `reasoning_effort` argument that is NOT part of the
# OpenAI standard. If LangChain drops it, the model may reason its full max_tokens
# budget and return no visible content.
from openai import OpenAI as _O
_raw = _O(base_url="https://api.sarvam.ai/v1", api_key=API_KEY)

# WRONG — no reasoning cap, small budget → content likely None
try:
    r = _raw.chat.completions.create(
        model="sarvam-m",
        messages=[{"role": "user", "content": "Solve: what is 17 * 23?"}],
        max_tokens=50,           # too small once reasoning is on
    )
    print("content:", repr(r.choices[0].message.content))
    cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
except Exception as e:
    print("error:", e)
"""),
    code("""
# FIX — either raise max_tokens, or explicitly disable reasoning via extra_body
r = _raw.chat.completions.create(
    model      = "sarvam-m",
    messages   = [{"role": "user", "content": "Solve: what is 17 * 23?"}],
    max_tokens = 400,
    extra_body = {"reasoning_effort": None},   # <- the fix
)
print("content:", r.choices[0].message.content)
cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
"""),

    md("### 5.2  CrewAI — bare model name → `LLM Provider NOT provided`"),
    md("""
Already triggered above in **3.1**. The fix is the `openai/` prefix. If you
skipped that section, jump back — this one is worth causing yourself once.
"""),

    md("### 5.3  MCP adapter — server never starts (missing `uvx` or missing env)"),
    code("""
# The two most common MCP startup failures:
#   a) `uvx` is not on PATH → install it:   pip install uv
#   b) SARVAM_API_KEY is not passed via env → server starts, then every tool call fails
#
# Sanity check: try running the server directly for two seconds.
import subprocess, shutil, os
if shutil.which("uvx") is None:
    print("✕ uvx not found on PATH. Fix:  pip install uv")
else:
    try:
        p = subprocess.Popen(
            ["uvx", "sarvam-mcp"],
            env={**os.environ, "SARVAM_API_KEY": API_KEY},
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )
        # It is a stdio server — it will sit and wait for JSON-RPC on stdin.
        # If it *exits* immediately, something is wrong. Give it 2 seconds.
        try:
            p.wait(timeout=2.0)
            err = p.stderr.read()
            print(f"✕ server exited early ({p.returncode})\\n{err[:400]}")
        except subprocess.TimeoutExpired:
            print("✓ uvx sarvam-mcp is running (as expected — stdio server waits for input)")
            p.terminate()
    except FileNotFoundError:
        print("✕ uvx not found. Install with:  pip install uv")
"""),

    md("### 5.4  n8n — cannot save the OpenAI node because the model dropdown has no Sarvam"),
    md("""
There is no code to run for this — it is a UI trap. **Click into the model
field and type `sarvam-m` or `sarvam-105b` manually, then press Enter.** n8n
accepts custom values; it just does not offer them. This is 30 seconds when you
know, and an hour when you do not.
"""),

    # ═══════════════════════════════════════════════ 6 · COST COMPARISON
    md("""
---
## 6 · The same job, four ways — what does each framework cost?

We ran roughly the same LLM work through four surfaces. Here is what the
CostMeter says.
"""),
    code("""
# Attribute-by-label rollup — sums whatever is in the meter
by_label = {}
for it in cost.items:
    by_label[it["label"]] = by_label.get(it["label"], 0.0) + it["inr"]

print(f"{'component':<20}{'₹ total':>10}")
print("─" * 30)
for k, v in sorted(by_label.items(), key=lambda x: -x[1]):
    bar = "█" * int(v / max(by_label.values()) * 20) if by_label.values() else ""
    print(f"{k:<20}₹{v:>8.4f}   {bar}")
print("─" * 30)
print(f"{'TOTAL':<20}₹{sum(by_label.values()):>8.4f}")
print("\\nInterop overhead vs raw SDK is effectively zero — the extra rupees you see")
print("above are extra CALLS the frameworks made (React loops, tool re-planning),")
print("not extra cost per call. Choose your framework by ergonomics, not per-call ₹.")
"""),
    code("cost.report()"),

    md("""
---
## ✅ Checkpoint

- [ ] The raw OpenAI SDK talks to Sarvam with just a `base_url` swap
- [ ] LangChain `ChatOpenAI` and `bind_tools` work unchanged
- [ ] Sarvam MCP tools appear inside a LangChain / LangGraph agent
- [ ] LangGraph `StateGraph` runs with a Sarvam LLM node
- [ ] CrewAI `LLM(model="openai/sarvam-105b", ...)` drives a multi-agent crew
- [ ] `MCPServerAdapter` surfaces Sarvam's 14 tools to a CrewAI agent
- [ ] You can describe, without looking, the four n8n fields that change
- [ ] You caused, saw, and fixed all four gotchas

## 🧪 Try this

1. **Route by language.** Add a LangGraph edge that picks `sarvam-m` for Indic
   queries and `sarvam-105b` for long English reasoning. Measure the ₹ delta.
2. **Multi-vendor routing.** Point one `ChatOpenAI` at Sarvam and another at
   OpenAI. Same graph. Route by task, not by vendor. This is the pattern most
   real Indian shops end up in.
3. **CrewAI on Indic voice.** Replace the writer agent with a "voice publisher"
   that uses the `sarvam_tts_speak` MCP tool. What was text output is now an
   audio file. Measure TTFB.
4. **The n8n webhook.** Import the JSON above, add a webhook trigger, and make
   the whole thing a callable HTTP endpoint. Fifteen minutes to a working
   micro-service with no code.
5. **Portability check.** Change `base_url` and `model` to Groq (or any other
   OpenAI-compatible provider) in each of the four sections above. Same test,
   different endpoint. This is what "no vendor lock-in" actually looks like in
   code — it is worth seeing at least once.

---

## The one thing to take away

You did not learn four frameworks today. You learned that **the OpenAI wire
protocol and MCP are, together, the interface every serious orchestrator now
speaks** — and that Sarvam ships both of them faithfully.

So the honest advice to any team already on LangChain, LangGraph, CrewAI or
n8n is: **do not migrate. Point the base URL at Sarvam and keep shipping.** The
migration was already done, by two standards bodies, a couple of years ago.
"""),
])

print("\\nlab 10 done")
