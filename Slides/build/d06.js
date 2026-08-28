const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW } = T;
const p = new P(); p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "Kivi, Sarvam Code and Developer Tooling";
const FT = ["AIVidhya4Sarvam · Building with Sarvam", "06 · Kivi & Tooling"];
let s;

/* 1 */ T.titleSlide(p, { eyebrow: "Segment 06 · Demo", title: "Kivi, Sarvam Code\nand the tooling layer",
  subtitle: "Products built on the stack — and how to make your AI assistant good at it",
  meta: "Kivi · Kaze · Sarvam Code · MCP server · Agent Skills · llms.txt · Context7" });

/* 2 */ s = T.slideL(p, "Kivi — the stack, productised", "Demo");
T.cards(p, s, [
  { icon: "♪", title: "What it is", body: "A desktop voice tool. Type, code and control your computer by speech. Built on Saaras V4, natively multilingual across Indian languages." },
  { icon: "⇄", title: "The comparison people make", body: "Similar in shape to Whisper Flow and other dictation tools — but pitched around multilingual use and full computer control, not just transcription." },
  { icon: "★", title: "Why a developer should care", body: "This is what Saaras V4 makes possible as a product rather than an API. The category is wide open in every vertical.", color: C.TEAL },
  { icon: "▶", title: "What we are doing now", body: "I demo it live — dictating in Hindi, controlling the machine, writing code by voice. You download it tonight and try it.", color: C.TEAL },
], { cols: 4, y: 1.7, h: 2.2, bSize: 10.5 });
T.rows(p, s, [
  { icon: "!", title: "Why you are watching rather than installing", body: "Getting a hundred people to install desktop software across three operating systems mid-session costs twenty minutes and derails the room. Watch now, install tonight, tell me tomorrow what you built with it." },
], { y: 4.2, rh: 1.0 });
T.takeaway(p, s, "The interesting question is not 'is Kivi good'. It is: what is the Kivi of your industry, and has anyone built it yet?");
T.foot(s, ...FT);

/* 3 */ s = T.slideD(p, "Kaze — where this is heading", "Ambient");
T.stats(p, s, [
  { value: "Kaze", label: "AI smart glasses that understand\nwhat you see", color: C.TEAL },
  { value: "Edge", label: "on-device inference for offline\nand low-connectivity" },
  { value: "8kHz", label: "telephony — the other end\nof the same spectrum", color: C.TEAL },
], { y: 1.9, h: 2.0, vSize: 32, dark: true });
T.bullets(p, s, [
  "The interesting thing about Kaze and Edge together is what they imply: Sarvam is not assuming a good internet connection or a modern phone.",
  "For rural India that is not a nice-to-have. A field officer in a district with patchy 4G, a farmer on a feature phone, a health worker in a village — these are the actual users of population-scale AI.",
  "Sarvam Edge is the one to watch if your product has to work where connectivity does not. Very few global providers are building for that constraint at all.",
], { y: 4.15, dark: true, size: 12.5 });

/* 4 */ s = T.sectionSlide(p, { num: "B", title: "Make your assistant good at this stack", subtitle: "Four tools, ten minutes of setup, permanent payoff" });

/* 5 */ s = T.slideL(p, "Why your AI assistant gets Sarvam wrong", "The problem");
T.rows(p, s, [
  { icon: "1", title: "Training data goes stale", body: "This stack shipped a new flagship LLM, two speech generations, a vision upgrade and a rebuilt Document AI in six months. Any model's priors are out of date." },
  { icon: "2", title: "Method names break OpenAI convention", body: "client.chat.completions(...) — not .create(...). Every assistant writes .create() by default, because that is what every other OpenAI-shaped client does.", color: C.RED },
  { icon: "3", title: "Parameters fail silently", body: "output_script ignored on sarvam-translate. language_code ignored on Document AI. HTTP 200, wrong output, no warning.", color: C.RED },
  { icon: "4", title: "Response fields behave unexpectedly", body: "content can be None when reasoning consumes the token budget. An assistant that has not seen this writes code that crashes on a null." },
], { y: 1.7, rh: 0.98, bSize: 10.5 });
T.takeaway(p, s, "None of these are hard once you know them. All of them cost you an afternoon the first time. That is precisely the gap Agent Skills fill.");
T.foot(s, ...FT);

/* 6 */ s = T.slideD(p, "The install — thirty seconds", "Agent Skills");
T.code(p, s, { y: 1.6, h: 1.95, ls: 14, size: 10, label: "BASH",
  code: `npx skills add sarvamai/skills                      # everything\nnpx skills add sarvamai/skills --skill chat         # just one\nnpx skills add sarvamai/skills --list               # browse first\n\nexport SARVAM_API_KEY="your-key"   &&   pip install sarvamai` });
T.table(p, s, { y: 3.68, rowH: 0.3, size: 9.5, headers: ["Skill", "What it corrects"], colW: [2.8, 9.293],
  rows: [
    ["chat", "Sarvam-105B/30B: quick starts, streaming, reasoning mode, the OpenAI-compatible path, the content=None gotcha"],
    ["speech-to-text", "Saaras v3: quick starts, Batch API for long audio + diarization, WebSocket streaming across 23 languages"],
    ["text-to-speech", "Bulbul v3: HTTP streaming, WebSocket, pronunciation dictionaries, unsupported-parameter warnings"],
    ["translate", "Sarvam-Translate v1 and Mayura v1: feature differences and silent parameter failures"],
    ["voice-agents", "Real-time agents with LiveKit and Pipecat (Python), plus a JS/TS reference for custom pipelines"],
    ["vibe-coding", "Vendor-neutral habits: small steps, verification, skills over long prompts. Pair with a domain skill"],
  ]});
T.takeaway(p, s, "Works with anything supporting the Agent Skills spec — Claude Code, Cursor, Windsurf. Install once, and every future session reads them automatically.", { dark: true, y: 6.1, h: 0.78 });

/* 7 */ s = T.slideL(p, "The proof — do this live", "Skills demo");
T.compare(p, s,
  { icon: "✕", title: "Without skills installed", color: C.RED, items: [
    "Ask: \"write a Saaras transcription script\"",
    "",
    "client.chat.completions.create(...)",
    "→ AttributeError",
    "",
    "Invents parameters that do not exist",
    "Uses saarika:v2.5 — the legacy model",
    "Misses mode= entirely",
    "Writes a plausible script that does not run",
  ]},
  { icon: "✓", title: "With skills installed", color: C.TEAL, items: [
    "Same prompt, same assistant",
    "",
    "client.chat.completions(...)",
    "→ works",
    "",
    "Correct current model IDs",
    "Knows the five modes exist",
    "Handles content=None",
    "Links out to llms.txt for parameter tables",
  ]},
  { y: 1.68, h: 4.02, size: 10.5 });
T.takeaway(p, s, "Ninety seconds, and it lands harder than any explanation. Ask someone in the room to run it too, so it is not just my machine.");
T.foot(s, ...FT);

/* 8 */ s = T.slideL(p, "Three ways to get Sarvam knowledge into an assistant", "Choosing");
T.table(p, s, { y: 1.7, headers: ["", "Agent Skills", "MCP server", "llms.txt"], colW: [2.4, 3.3, 3.3, 3.093],
  rows: [
    ["When it loads", "Once, installed into your project or editor", "Live, queried on demand while you code", "Fetched manually when you need it"],
    ["Best for", "Baking in SDK corrections an assistant keeps getting wrong", "Interactive sessions needing current API details, or calling Sarvam directly", "Bulk ingestion, RAG indexes, one-shot context"],
    ["Setup", "npx skills add sarvamai/skills", "One-time MCP client config", "None — just a URL"],
    ["Gives you", "Corrections", "Live tool access + docs", "The whole corpus"],
  ], rowH: 0.78, size: 10.5 });
T.takeaway(p, s, "Use all three. A skill stops the wrong method name. The MCP server and llms.txt supply the parameter tables a skill deliberately leaves out.");
T.foot(s, ...FT);

/* 9 */ s = T.slideD(p, "llms.txt — the trick nobody uses", "Docs as data");
T.code(p, s, { y: 1.62, h: 2.5, label: "APPEND .md TO ANY DOCS PAGE. OR TAKE THE WHOLE CORPUS.",
  code: `# Markdown version of any page\nhttps://docs.sarvam.ai/api/getting-started/models.md\n\n# Page-level index\nhttps://docs.sarvam.ai/api/getting-started/llms.txt\n\n# Full index of the documentation\nhttps://docs.sarvam.ai/llms.txt\n\n# THE ENTIRE DOCUMENTATION IN ONE FILE\nhttps://docs.sarvam.ai/llms-full.txt` });
T.rows(p, s, [
  { icon: "1", title: "Paste llms-full.txt into your assistant's context", body: "Instant, current, complete knowledge of the whole API surface. No RAG pipeline, no embedding step, no staleness." },
  { icon: "2", title: "Or index it for a real RAG setup", body: "It is structured markdown, designed for ingestion. This is what you build a documentation assistant on top of.", color: C.TEAL },
  { icon: "3", title: "Also: Context7 and the docs MCP server", body: "docs.sarvam.ai/_mcp/server connects your editor straight to the documentation. Different from the API MCP server — this one is for reading, that one is for doing.", color: C.TEAL },
], { y: 4.35, rh: 0.92, dark: true });

/* 10 */ s = T.slideL(p, "Sarvam Code and the rest of the toolkit", "Reference");
T.cards(p, s, [
  { icon: "⚙", title: "Sarvam Code (Beta)", body: "A coding assistant built on open models, for writing and understanding code. Announced at Epoch." },
  { icon: "▶", title: "API Playground", body: "dashboard.sarvam.ai/playground — test every endpoint in the browser with no setup. Where you send someone who is stuck." },
  { icon: "★", title: "The Cookbook", body: "github.com/sarvamai/sarvam-ai-cookbook — working notebooks for STT, TTS, translation, doc intelligence, voice agents.", color: C.TEAL },
  { icon: "◆", title: "Official SDKs", body: "pip install sarvamai · npm install sarvamai. Async, retries and streaming built in. Typed clients.", color: C.TEAL },
  { icon: "?", title: "AI docs assistant", body: "Built into the documentation search bar. Fastest route to an answer when you are mid-build." },
  { icon: "!", title: "Status and changelog", body: "status.sarvam.ai for incidents. The changelog is the one page to check before every project — this stack moves." },
], { cols: 3, y: 1.68, h: 1.85 });
T.takeaway(p, s, "Contributing a cookbook example is the cheapest developer marketing available to you — and it puts your name in front of the team.");
T.foot(s, ...FT);

/* 11 */ s = T.analogy(p, { kicker: "Why skills beat long prompts", symbol: "★", symSize: 88,
  title: "The new cook and the recipe card taped to the wall",
  story: "You can explain the kitchen's quirks to every new cook, every shift, out loud. The left burner runs hot. The oven is twenty degrees off. Salt goes in at the end, not the start.\n\nOr you can tape a card to the wall.\n\nThe card does not make anyone a better cook. It just stops the same four mistakes being made forever.",
  punch: "That is what an Agent Skill is. Not intelligence — institutional memory. Install it once and stop re-explaining that the method is client.chat.completions(), not .create()." });

/* 12 */ s = T.slideL(p, "Set this up tonight — ten minutes", "Homework");
T.flow(p, s, [
  { t: "Install skills", d: "npx skills add sarvamai/skills" },
  { t: "Wire the MCP server", d: "uvx sarvam-mcp + your key" },
  { t: "Verify", d: "\"translate good morning to Hindi\"" },
  { t: "Download Kivi", d: "and dictate something in your language" },
  { t: "Bookmark the changelog", d: "check it before every project" },
], { y: 2.1, h: 1.75 });
T.takeaway(p, s, "Do this before you write another line of Sarvam code. Ten minutes tonight saves you an afternoon next week — and I would rather you spent that afternoon building.", { y: 4.4 });
T.rows(p, s, [
  { icon: "→", title: "Next: the money segment", body: "Everything so far has been capability. Now we find out what it costs, what you can charge, and where the business actually is. This is the twenty-five minutes people repeat to colleagues on Monday." },
], { y: 5.5, rh: 1.0 });
T.foot(s, ...FT);

/* 13 */ T.quoteSlide(p, { quote: "Institutional memory beats intelligence.\nTape the card to the wall.",
  by: "— End of Segment 06. Next: unit economics." });

p.writeFile({ fileName: "06_Kivi_SarvamCode_and_Tooling.pptx" }).then(f => console.log("OK", f));
