const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW } = T;
const p = new P(); p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "Framework Interop — LangChain, LangGraph, CrewAI, n8n";
const FT = ["AIVidhya4Sarvam · Building with Sarvam", "09 · Framework Interop"];
let s;

/* 1 */ T.titleSlide(p, { eyebrow: "Segment 09 · The interop segment",
  title: "Your existing framework.\nSarvam underneath.",
  subtitle: "LangChain, LangGraph, CrewAI, n8n — one base-URL swap and a stock MCP server",
  meta: "Nothing new to learn · everything you already ship keeps shipping · four frameworks in one lab" });

/* 2 */ s = T.slideL(p, "Why this segment exists at all", "The premise");
T.rows(p, s, [
  { icon: "1", title: "Half the room already ships on LangChain, LangGraph, CrewAI or n8n",
    body: "Telling that team to rewrite onto a new SDK is a non-starter. The interesting question is whether their existing pipeline can point at Sarvam without changing shape." },
  { icon: "2", title: "The answer is yes, and the change fits in one line",
    body: "Sarvam followed the OpenAI wire protocol precisely, and shipped an MCP server that speaks the stock protocol. Every framework built on either of those two contracts inherits Sarvam for free.",
    color: C.TEAL },
  { icon: "3", title: "This is the segment that unblocks adoption in existing shops",
    body: "It is also the segment that reframes 'should we use Indus?' as a build-vs-buy question rather than a religion. If your orchestrator is already good, you keep it — you just point it at a different endpoint." },
], { y: 1.6, rh: 1.35, bSize: 11 });
T.takeaway(p, s, "You are not migrating to Sarvam. You are giving your existing stack a new endpoint. That is the whole segment in one sentence.");
T.foot(s, ...FT);

/* 3 */ s = T.slideD(p, "Two contracts, four frameworks, zero rewrites", "The single insight");
T.compare(p, s,
  { icon: "1", title: "The chat contract — OpenAI wire protocol", color: C.SAF, items: [
    "Endpoint: POST /v1/chat/completions",
    "Auth: Authorization: Bearer <key>",
    "Request shape: messages[], tools[], stream, temperature…",
    "Response shape: choices[].message.content, tool_calls",
    "SSE for streaming — identical event framing",
    "Any framework that wraps OpenAI works by pointing base_url at api.sarvam.ai",
  ]},
  { icon: "2", title: "The tools contract — Model Context Protocol", color: C.TEAL, items: [
    "sarvam-mcp: uvx sarvam-mcp, stdio transport, standard MCP",
    "30 tools: 23 runtime (sarvam_tools_*) + 7 builder (sarvam_code_*)",
    "Runtime: STT, TTS, translate, transliterate, LID, LLM, vision, pronunciation, dub, localize",
    "Every MCP-aware framework picks it up: LangChain adapters, CrewAI tools, n8n MCP node",
    "One SARVAM_API_KEY env var, one config block",
    "No custom SDK bindings anywhere in your code",
  ]},
  { y: 1.7, h: 4.0, size: 11, dark: true });
T.takeaway(p, s, "One protocol for chat, one protocol for tools. Everything downstream of those two protocols inherits Sarvam without knowing the vendor name.", { dark: true, y: 6.0 });

/* 4 */ s = T.slideL(p, "The base-URL swap, four ways", "One page, everything you need");
T.table(p, s, { y: 1.55, headers: ["Framework", "The change", "Model string"], colW: [2.4, 6.593, 3.1],
  rows: [
    ["LangChain (Python)",
     "ChatOpenAI(base_url=\"https://api.sarvam.ai/v1\", api_key=…, model=…)",
     "\"sarvam-105b\""],
    ["LangGraph",
     "Uses your LangChain ChatOpenAI — same swap; StateGraph and create_agent unchanged",
     "same as LangChain"],
    ["CrewAI",
     "LLM(model=\"openai/sarvam-105b\", base_url=…, api_key=…)  — base_url is what actually matters; without it BOTH forms hit real OpenAI",
     "\"openai/sarvam-105b\""],
    ["n8n (no-code)",
     "OpenAI credential → Base URL: https://api.sarvam.ai/v1  · then TYPE the model name in the node (dropdown is OpenAI-only)",
     "\"sarvam-105b\" — typed manually"],
    ["Vercel AI SDK",
     "createOpenAI({ baseURL: \"https://api.sarvam.ai/v1\", apiKey: … })",
     "\"sarvam-105b\""],
    ["Any HTTP tool (curl, n8n HTTP node, Zapier Webhook)",
     "POST to https://api.sarvam.ai/v1/chat/completions with the OpenAI JSON body — no SDK at all",
     "same"],
  ], rowH: 0.42, size: 10 });
T.takeaway(p, s, "This is the slide you screenshot. Six frameworks, one swap each, one page. Everything else in this deck is a proof for one of these rows.");
T.foot(s, ...FT);

/* 5 */ s = T.sectionSlide(p, { num: "A", title: "The four walkthroughs",
  subtitle: "LangChain · LangGraph · CrewAI · n8n — minimal, runnable, in that order" });

/* 6 */ s = T.slideL(p, "LangChain — ChatOpenAI is already a Sarvam client", "Walkthrough 1 of 4");
T.code(p, s, { y: 1.55, h: 3.05, label: "PYTHON · pip install langchain langchain-openai",
  code: `from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(
    model      = "sarvam-105b",                       # sarvam-m/30b deprecated
    base_url   = "https://api.sarvam.ai/v1",          # <- the one line
    api_key    = os.environ["SARVAM_API_KEY"],
    temperature= 0.2,
    max_tokens = 800,
)

reply = llm.invoke([
    SystemMessage("You are a concise NBFC agent. One sentence."),
    HumanMessage("मेरी अगली EMI कब देय है?"),
])
print(reply.content)` });
T.rows(p, s, [
  { icon: "1", title: "Tools work through the standard LangChain binding",
    body: "llm.bind_tools([...]).invoke(...) — the same @tool decorator, the same schema, the same tool_calls response. Nothing framework-side changes." },
  { icon: "★", title: "reasoning_effort is now a first-class OpenAI parameter",
    body: "It is a typed kwarg in openai>=2.41 and a declared field on ChatOpenAI. Pass it DIRECTLY — ChatOpenAI(..., reasoning_effort=None). Routing it through model_kwargs still works but raises a UserWarning telling you to stop.",
    color: C.SAF },
], { y: 4.75, rh: 0.9, bSize: 10.5 });
T.foot(s, ...FT);

/* 7 */ s = T.slideD(p, "LangChain + Sarvam MCP — 30 tools with zero glue", "Walkthrough 1 of 4, continued");
T.code(p, s, { y: 1.6, h: 3.15, label: "PYTHON · pip install langchain-mcp-adapters",
  code: `from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent   # langgraph.prebuilt version deprecated

client = MultiServerMCPClient({
    "sarvam": {
        "command":   "uvx",
        "args":      ["sarvam-mcp"],
        "transport": "stdio",
        "env":       {"SARVAM_API_KEY": os.environ["SARVAM_API_KEY"]},
    }
})
tools = await client.get_tools()          # 30 tools, ready to bind

agent = create_agent(llm, tools=tools)
result = await agent.ainvoke({"messages":
    [{"role": "user", "content": "Transcribe ./data/hi_call.wav in Hindi"}]})` });
T.rows(p, s, [
  { icon: "✓", title: "sarvam_stt_transcribe, sarvam_tts_speak, sarvam_translate, sarvam_llm_complete — all appear as ordinary LangChain tools",
    body: "The agent picks the right one from the prompt. You did not write a single wrapper. That is the value.", color: C.TEAL },
], { y: 4.9, rh: 1.05, dark: true, bSize: 11 });
T.takeaway(p, s, "The MCP adapter is the reason your existing agent can suddenly transcribe Hindi audio, translate to Tamil and speak it back — with no new code in your project.", { dark: true, y: 6.15 });

/* 8 */ s = T.slideL(p, "LangGraph — same LLM, graph you already know", "Walkthrough 2 of 4");
T.code(p, s, { y: 1.55, h: 3.55, label: "PYTHON · pip install langgraph  ·  reuse the ChatOpenAI llm from slide 6",
  code: `from typing import TypedDict
from langgraph.graph import StateGraph, END

class S(TypedDict):
    query: str; language: str; answer: str

def detect(state):    # node 1 — call Sarvam LLM to classify
    r = llm.invoke([("system", "Return only the ISO code, e.g. hi-IN."),
                    ("user",   state["query"])])
    return {"language": r.content.strip()}

def answer(state):    # node 2 — reply in the detected language
    r = llm.invoke([("system", f"Reply in {state['language']}. One sentence."),
                    ("user",   state["query"])])
    return {"answer": r.content}

g = StateGraph(S); g.add_node("detect", detect); g.add_node("answer", answer)
g.set_entry_point("detect"); g.add_edge("detect", "answer"); g.add_edge("answer", END)

app = g.compile()
print(app.invoke({"query": "मेरा खाता कब खुला था?"})["answer"])` });
T.rows(p, s, [
  { icon: "★", title: "The graph is the value — the model is a swap",
    body: "You did not touch StateGraph, add_node, add_edge, checkpointers, interrupt() or human-in-the-loop. You changed the endpoint. Your LangGraph investment is intact." },
], { y: 5.25, rh: 0.95, bSize: 11 });
T.foot(s, ...FT);

/* 9 */ s = T.slideL(p, "CrewAI — the transport is chosen by Python TYPE", "Walkthrough 3 of 4");
T.code(p, s, { y: 1.55, h: 3.55, label: "PYTHON · pip install crewai 'crewai-tools[mcp]' mcpadapt",
  code: `from crewai import Agent, Task, Crew, LLM
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters          # <- NOT a plain dict

llm = LLM(model    = "openai/sarvam-105b",     # prefix still the safe default
          base_url = "https://api.sarvam.ai/v1",
          api_key  = os.environ["SARVAM_API_KEY"],
          max_tokens = 4000)                   # reasoning cannot be disabled here

server = StdioServerParameters(                # a dict here routes to SSE and
    command="uvx", args=["sarvam-mcp"],        # dies: sse_client() got an
    env={"SARVAM_API_KEY": os.environ["SARVAM_API_KEY"]})   # unexpected 'command'

with MCPServerAdapter(server) as tools:
    speech = Agent(role="Speech Analyst", llm=llm, tools=tools, goal="…",
                   backstory="You handle inbound support calls end-to-end.")
    print(await Crew(agents=[speech], tasks=[task]).kickoff_async())` });
T.rows(p, s, [
  { icon: "!", title: "crewai.LLM cannot disable reasoning — at all",
    body: "call() strips every None-valued param before serialising, so reasoning_effort=None never reaches Sarvam and its default (reasoning on) applies. Your only lever is a generous max_tokens — and even that is not a guarantee.",
    color: C.RED },
], { y: 5.28, rh: 0.95, bSize: 10.5 });
T.foot(s, ...FT);

/* 10 */ s = T.slideL(p, "n8n — no code, same trick, one credential", "Walkthrough 4 of 4");
T.rows(p, s, [
  { icon: "1", title: "Create an OpenAI credential — override the Base URL",
    body: "Credentials → OpenAI API → Base URL: https://api.sarvam.ai/v1 · API Key: your Sarvam key. That single credential now works with every OpenAI node in n8n." },
  { icon: "2", title: "In the OpenAI Chat Model node, TYPE the model name",
    body: "The model dropdown lists OpenAI's catalogue. Click the field, type sarvam-105b, hit enter. The node passes it straight through to Sarvam.",
    color: C.SAF },
  { icon: "3", title: "For the 13 non-chat APIs — install the MCP Client (Community) node",
    body: "Point it at command=\"uvx\" args=[\"sarvam-mcp\"] with SARVAM_API_KEY in env. All 30 tools appear in the workflow palette. Chain them like any other node.",
    color: C.TEAL },
  { icon: "★", title: "The escape hatch — the raw HTTP Request node",
    body: "If a node does not exist or acts up, POST directly to https://api.sarvam.ai/v1/chat/completions with the OpenAI JSON body. It is the last-resort integration you never actually need." },
], { y: 1.62, rh: 1.02, bSize: 10.5 });
T.takeaway(p, s, "n8n is the demo of the whole segment: not one line of code, and the workflow you already built now speaks Hindi. Show this to a non-engineer buyer.");
T.foot(s, ...FT);

/* 11 */ s = T.sectionSlide(p, { num: "B", title: "The gotchas, and when to interop at all",
  subtitle: "The four things that will bite you, and the decision framework" });

/* 12 */ s = T.slideL(p, "The interop gotchas — every one found live", "You will hit at least three of these");
T.table(p, s, { y: 1.5, headers: ["Where", "Symptom", "Fix"], colW: [3.1, 4.4, 4.593],
  rows: [
    ["MCP tool result is a LIST of blocks",
     "400: messages.N.tool.content — Input should be a valid string",
     "MultiServerMCPClient(..., tool_interceptors=[…]) → flatten to a string"],
    ["…and the interceptor covers only success",
     "Failed tool calls still 400",
     "Flatten the error path too"],
    ["tts_speak returns AudioContent, not text",
     "\"(success, no text content)\" → model retries, at real cost",
     "Acknowledge audio/image/resource types explicitly"],
    ["crewai MCPServerAdapter given a dict",
     "sse_client() got an unexpected keyword 'command'",
     "Pass mcp.StdioServerParameters(...) — type picks the transport"],
    ["crewai_tools says 'mcp package missing'",
     "Misleading — mcp IS installed",
     "pip install mcpadapt  (or 'crewai-tools[mcp]')"],
    ["crewai.LLM drops reasoning_effort=None",
     "content is None; 1–3 repeated ERROR lines",
     "Cannot be disabled — raise max_tokens; expect sampling variance"],
    ["langgraph.prebuilt.create_react_agent",
     "DeprecationWarning (LangGraph v1.0)",
     "from langchain.agents import create_agent"],
    ["crew.kickoff() inside Jupyter",
     "Conflicts with the running event loop",
     "await crew.kickoff_async() — it is async, so await it"],
    ["Stale kernel state after editing a cell",
     "\"I fixed it, why is it still broken\"",
     "Re-run the UPSTREAM cell; name fixed objects distinctly"],
  ], rowH: 0.3, size: 9.5 });
T.takeaway(p, s, "Each of these cost real hours to find. Screenshot this slide — it is the cheapest artefact in the deck and the one most likely to save somebody a working day.");
T.foot(s, ...FT);

/* 13 */ s = T.analogy(p, { kicker: "The interop principle", symbol: "⇄", symSize: 84,
  title: "You did not rewire the house to change the bulb",
  story: "Your house has a light socket. You changed the bulb from incandescent to LED. You did not rewire the house, replace the switch, or hire an electrician.\n\nWhy? Because everyone agreed on the shape of the socket a hundred years ago.\n\nThe OpenAI chat completions endpoint is that socket. MCP is that socket for tools. Sarvam ships a bulb that fits both.",
  punch: "This is why 'point your existing framework at Sarvam' is a slide and not a project. The socket is standard. You are only changing what is plugged into it." });

/* 14 */ s = T.slideL(p, "Interop through a framework, or native on the SDK?", "The honest decision");
T.compare(p, s,
  { icon: "F", title: "Reach for interop when", color: C.TEAL, items: [
    "You already have a LangChain / LangGraph / CrewAI / n8n codebase in production",
    "The team's mental model is the framework, not the vendor SDK",
    "You want portability — swap Sarvam for another OpenAI-compatible model in one line",
    "You are prototyping fast and n8n gets you to a demo before lunch",
    "You need multi-vendor routing — Sarvam for Indic, OpenAI for frontier English, same graph",
    "The buyer wants to see a familiar framework in their stack",
  ]},
  { icon: "S", title: "Stay on the Sarvam SDK when", color: C.SAF, items: [
    "You are consuming Sarvam-specific features — reasoning_effort, pronunciation dicts, batch STT modes",
    "You need the exact behaviour Sarvam's own docs describe, without a framework's abstraction leaking",
    "You are teaching or writing a cookbook — the SDK is what the docs reference",
    "You are chasing every millisecond of latency — one less abstraction layer helps",
    "Your production is a single service with one vendor and no orchestrator",
    "You want first-class support paths — the SDK is what the Sarvam team debugs first",
  ]},
  { y: 1.7, h: 4.05, size: 11 });
T.takeaway(p, s, "Neither answer is a religion. Most real projects use both — the SDK for the hot path, a framework for the orchestration around it. Choose per surface, not per stack.");
T.foot(s, ...FT);

/* 15 */ s = T.slideD(p, "Take this home — your framework, your one-line change", "The matrix");
T.table(p, s, { y: 1.55, headers: ["If your team already ships…", "…do this", "Time to first call"], colW: [3.6, 6.2, 2.293],
  rows: [
    ["LangChain",         "ChatOpenAI(base_url=api.sarvam.ai/v1, api_key=…, model=…)",     "3 minutes"],
    ["LangGraph",         "Reuse LangChain ChatOpenAI in your nodes — no graph change",     "3 minutes"],
    ["CrewAI",            "LLM(model=\"openai/sarvam-105b\", base_url=…, api_key=…)",       "5 minutes"],
    ["n8n",               "OpenAI credential → Base URL swap + type the model name",        "5 minutes"],
    ["Vercel AI SDK",     "createOpenAI({ baseURL: api.sarvam.ai/v1, apiKey: … })",         "3 minutes"],
    ["LlamaIndex",        "OpenAI(api_base=api.sarvam.ai/v1, api_key=…, model=…)",          "3 minutes"],
    ["Nothing yet",       "Start on the Sarvam SDK — you get first-class support and docs", "10 minutes"],
    ["Non-Python stack",  "Any OpenAI SDK works · or POST /v1/chat/completions with curl",  "5 minutes"],
  ], rowH: 0.34, size: 10.5, hSize: 11.5 });
T.takeaway(p, s, "Twenty-eight minutes of total work across every mainstream orchestrator on the market. That is the size of the barrier to adopting Sarvam in an existing shop.", { dark: true, y: 5.65 });
T.rows(p, s, [
  { icon: "★", title: "The lab you are about to run does all four in one notebook",
    body: "LangChain, LangGraph, CrewAI and n8n — same task, four frameworks, ₹ cost printed for each. You leave the session with a running interop template." },
], { y: 6.55, rh: 0.9, dark: true, bSize: 11 });

/* 16 */ T.quoteSlide(p, { quote: "The endpoint is standard.\nThe orchestrator is your choice.\nBoth of those are freedoms, not compromises.",
  by: "— End of Segment 09. Lab 10 is the hands-on: four frameworks, one endpoint, one hour." });

p.writeFile({ fileName: "09_Framework_Interop_LangChain_LangGraph_CrewAI_n8n.pptx" }).then(f => console.log("OK", f));
