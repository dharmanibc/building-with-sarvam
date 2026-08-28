const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW } = T;
const p = new P(); p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "MCP and Context Engineering";
const FT = ["AIVidhya4Sarvam · Building with Sarvam", "10 · MCP & Context"];
let s;

/* 1 */ T.titleSlide(p, { eyebrow: "Segment 10 · Tooling and context",
  title: "Tools the agent finds.\nContext the assistant needs.",
  subtitle: "The Sarvam MCP server at runtime — and four ways to stop your coding assistant inventing APIs",
  meta: "MCP voice agents · Markdown · llms.txt · Context7 · Agent Skills · everything measured" });

/* 2 */ s = T.slideL(p, "Two different problems, often confused", "The premise");
T.compare(p, s,
  { icon: "1", title: "Runtime context — what the AGENT can reach", color: C.SAF, items: [
    "Your deployed agent needs to transcribe, translate, speak",
    "MCP describes those capabilities in a standard protocol",
    "The model chooses which tool to call, and when",
    "Failure mode: it picks the wrong tool, on a live call",
    "You pay in milliseconds and in schema tokens, every turn",
    "Lab 11 measures all three costs",
  ]},
  { icon: "2", title: "Build-time context — what YOU can reach", color: C.TEAL, items: [
    "Your coding assistant writes Sarvam code that does not run",
    "Markdown, llms.txt, Context7 and Agent Skills each fix part of it",
    "The model never calls anything — it just writes better code",
    "Failure mode: confident, plausible, non-existent methods",
    "You pay once, in setup, and the benefit compounds",
    "Lab 12 measures which layer actually helps",
  ]},
  { y: 1.7, h: 4.0, size: 11 });
T.takeaway(p, s, "Both are context engineering. One feeds a running agent, the other feeds the person building it. Confusing them is why teams adopt MCP and wonder why their code still does not compile.");
T.foot(s, ...FT);

/* 3 */ s = T.sectionSlide(p, { num: "A", title: "MCP at runtime",
  subtitle: "Fourteen tools, zero wrappers — and the three prices nobody quotes" });

/* 4 */ s = T.slideD(p, "The whole integration is a config block", "Sarvam MCP");
T.code(p, s, { y: 1.55, h: 2.0, label: "ANY MCP CLIENT — CLAUDE CODE, CURSOR, WINDSURF, ZED, n8n",
  code: `{
  "mcpServers": {
    "sarvam": {
      "command": "uvx", "args": ["sarvam-mcp"],
      "env": { "SARVAM_API_KEY": "<YOUR_KEY>" }
    }
  }
}` });
T.table(p, s, { y: 3.75, headers: ["Namespace", "Tools", "What it is for", "Costs ₹"], colW: [2.7, 1.2, 5.1, 3.093],
  rows: [
    ["sarvam_tools_*", "23", "STT · TTS · translate · transliterate · LID · LLM · vision · pronunciation · dub · localize · recall", "Yes — real calls"],
    ["sarvam_code_*",  "7",  "api_reference · languages · speakers · pricing · snippet · recommend_model · validate_request", "Effectively free"],
  ], rowH: 0.42, size: 10.5 });
T.takeaway(p, s, "Give a production voice agent the runtime tools ONLY. Hand it the builder tools and you have invited it to read documentation in the middle of a phone call.", { dark: true, y: 5.5 });

/* 5 */ s = T.slideL(p, "The agent that writes no plumbing", "Lab 11 · the good part");
T.code(p, s, { y: 1.55, h: 2.55, label: "PYTHON · the entire voice agent",
  code: `tools = await MultiServerMCPClient(SERVER).get_tools()   # 30 tools
agent = create_agent(llm, tools=tools)      # langchain.agents, not langgraph.prebuilt

await agent.ainvoke({"messages": [{"role": "user", "content":
    "Transcribe ./data/call.wav in Hindi, then summarise it in English"}]})

#  → agent picks sarvam_stt_transcribe, calls it, reads the transcript,
#    reasons over it, and answers. You wrote no wrapper. None.` });
T.rows(p, s, [
  { icon: "✓", title: "Compare with Lab 08", body: "There, listen() / think() / speak() was about sixty lines you owned and maintained. Here it is three lines and a config block.", color: C.TEAL },
  { icon: "?", title: "So why would anyone still hand-wire it?", body: "Because those sixty lines bought you something. The next three slides measure exactly what." },
], { y: 4.35, rh: 1.0, bSize: 10.5 });
T.foot(s, ...FT);

/* 6 */ s = T.slideD(p, "Price one — the ₹ meter goes blind", "The gotcha");
T.compare(p, s,
  { icon: "✕", title: "What you expect", color: C.RED, items: [
    "Agent transcribes ten minutes of audio",
    "Agent speaks ten replies through Bulbul",
    "Your CostMeter reports what it cost",
    "You reconcile against the dashboard",
    "Everyone is happy",
  ]},
  { icon: "!", title: "What actually happens", color: C.SAF, items: [
    "The SDK call happens INSIDE the MCP server",
    "Tool results carry no usage back through the adapter",
    "response.usage never reaches your notebook",
    "Your meter prints ₹0.00 — confidently",
    "The dashboard disagrees at the end of the month",
  ]},
  { y: 1.7, h: 3.3, size: 11, dark: true });
T.takeaway(p, s, "The general law: put a protocol boundary between your code and a billed API, and your observability stops at that boundary. Whatever you cannot see you cannot cost — so meter at the boundary you DO control.", { dark: true, y: 5.25 });

/* 7 */ s = T.slideL(p, "Price two — and the measurement that refused to cooperate", "Latency");
T.code(p, s, { y: 1.5, h: 1.35, label: "WHAT LAB 10 ACTUALLY PRINTED — three runs each",
  code: `direct SDK :    1611 ms   ['435', '805', '3593']   <- one 3.6 s outlier
via MCP    :     821 ms   ['934', '787', '743']    <- tight, consistent
MCP overhead: -790 ms per call     # i.e. MCP came out FASTER` });
T.rows(p, s, [
  { icon: "1", title: "The expected answer was 'MCP is slower'. The data said otherwise",
    body: "Not because MCP is fast, but because n=3 over a live network is dominated by variance. One 3.6-second outlier moved the direct-SDK mean by more than the protocol hop could." },
  { icon: "★", title: "This is the most useful thing in the lab, and it is not about MCP",
    body: "A benchmark whose spread is larger than its effect has not measured the effect. Report the raw samples, not just the mean — the list of three numbers is what makes the problem visible.",
    color: C.SAF },
  { icon: "→", title: "So decide on architecture, not on this number",
    body: "A stdio round-trip is real but small. What actually rules MCP out of the hot path is variance and an extra failure mode on a call a human is waiting on — not a mean you can measure in three tries.",
    color: C.TEAL },
], { y: 3.05, rh: 1.05, bSize: 10.5 });
T.takeaway(p, s, "Run it live and let the room watch the outlier wreck the mean. Teaching somebody to distrust their own three-sample benchmark is worth more than any number this slide could print.");
T.foot(s, ...FT);

/* 8 */ s = T.slideL(p, "Price three — you pay for tools you never call", "Schema tokens · measured");
T.stats(p, s, [
  { value: "8,518", label: "tokens of tool schema\ninjected on EVERY turn" },
  { value: "₹4.99", label: "per 20-turn call\nschemas alone", color: C.RED },
  { value: "₹4.99L", label: "per 100k calls\nbefore a word is spoken", color: C.RED },
  { value: "₹4.63L", label: "saved by trimming\n30 tools → 5", color: C.TEAL },
], { y: 1.55, h: 1.78 });
T.rows(p, s, [
  { icon: "₹", title: "Thirty tools is 8,518 tokens before your caller says a word",
    body: "Injected on every turn, twenty times over a twenty-turn call. The single largest schema is sarvam_tools_stt_transcribe at 661 tokens." },
  { icon: "→", title: "A voice agent needs five tools, not thirty",
    body: "STT, TTS, translate, transliterate, identify_language. Filter by EXACT tool name — a substring match like \"speak\" also catches sarvam_code_speakers.",
    color: C.SAF },
  { icon: "★", title: "And the filter usually raises accuracy too",
    body: "Fewer options is a smaller decision for the model. Cheaper and more reliable at the same time — the rare trade that is not a trade.",
    color: C.TEAL },
], { y: 3.6, rh: 0.98, bSize: 10.5 });
T.takeaway(p, s, "₹4.6 lakh per 100k calls, recovered by deleting twenty-five tools the agent was never going to call. Nothing costs more than an option that only exists to be ignored.", { y: 6.65, h: 0.72, size: 11.5 });

/* 9 */ s = T.slideL(p, "So where does MCP belong in a voice product?", "The honest split");
T.compare(p, s,
  { icon: "H", title: "Hot path → direct SDK", color: C.SAF, items: [
    "The STT → LLM → TTS loop the caller is waiting on",
    "Every millisecond is audible to a human being",
    "Three calls you already know and will not change",
    "You want to see and tune every single hop",
    "High volume, where schema tokens compound",
    "This is Lab 08, and it stays that way",
  ]},
  { icon: "A", title: "Around it → MCP", color: C.TEAL, items: [
    "Post-call summarisation and translation of transcripts",
    "Document lookups and pronunciation-dictionary updates",
    "Analytics, enrichment, anything asynchronous",
    "Capability you want as configuration, not code",
    "Tool sets shared across several agents or products",
    "This is Lab 11, and it is genuinely better here",
  ]},
  { y: 1.7, h: 3.95, size: 11 });
T.takeaway(p, s, "This is the same build-versus-platform line from Segment 05, drawn one level lower — and now you can draw it with numbers you measured rather than numbers a vendor gave you.");
T.foot(s, ...FT);

/* 10 */ s = T.sectionSlide(p, { num: "B", title: "Context engineering",
  subtitle: "Four ways to stop your coding assistant inventing APIs that do not exist" });

/* 11 */ s = T.slideD(p, "The failure every team hits in week one", "The problem");
T.code(p, s, { y: 1.55, h: 1.7, label: "WHAT AN ASSISTANT WITH NO CONTEXT WRITES",
  code: `resp = client.chat.completions.create(          # ← AttributeError. No .create
    messages=[{"role": "user", "content": text}]  # ← no model= : defaults drift
)
r = client.speech_to_text.transcribe(file=f, sample_rate=8000)   # ← TypeError` });
T.rows(p, s, [
  { icon: "1", title: "It is not being stupid — it is pattern-matching",
    body: "It has read a hundred thousand OpenAI examples and close to zero Sarvam ones. So it writes the shape it knows. Every line above is on your gotchas list already.", color: C.SAF },
  { icon: "2", title: "A bigger model does not fix this",
    body: "This is a knowledge gap, not a reasoning gap. The fix is not a better model — the fix is better context. Four layers of it, and they cost between nothing and one config block.", color: C.TEAL },
], { y: 3.45, rh: 1.05, dark: true, bSize: 10.5 });
T.takeaway(p, s, "Every wrong line above is already documented on the gotchas slide. The question is not whether you know the fix — it is whether your tooling knows it.", { dark: true, y: 5.75 });

/* 12 */ s = T.slideL(p, "The four layers, cheapest first", "The toolkit");
T.flow(p, s, [
  { t: "Markdown", d: "append .md to any docs URL — zero setup, always live" },
  { t: "llms.txt", d: "the vendor's own curated index, published for LLMs" },
  { t: "Context7", d: "MCP server serving indexed docs on demand" },
  { t: "Agent Skills", d: "portable folders of signatures + gotchas you own" },
], { y: 1.9, h: 1.85 });
T.table(p, s, { y: 4.1, headers: ["Layer", "Setup", "Freshness", "Best for"], colW: [2.5, 2.2, 2.4, 4.993],
  rows: [
    ["Markdown",     "Zero",            "Live",       "One page, one question, right now"],
    ["llms.txt",     "Zero",            "Live",       "\"What does this platform even offer?\""],
    ["Context7",     "One config block", "Index lag",  "Working across many libraries at once"],
    ["Agent Skills", "One install",     "You own it", "Your team repeats the same mistakes"],
  ], rowH: 0.34, size: 10.5 });
T.takeaway(p, s, "Docs DESCRIBE what the API offers. Skills PRESCRIBE what your team must do. You need both halves — and most teams only ever install the first.");
T.foot(s, ...FT);

/* 13 */ s = T.slideL(p, "Two facts worth correcting out loud", "Getting it right");
T.rows(p, s, [
  { icon: "1", title: "llms-full.txt is NOT part of the llms.txt standard",
    body: "The spec defines exactly one file: an H1 (the only required part), an optional blockquote summary, and optional H2 sections of links. `llms-full.txt` is a widely-adopted convention for \"everything, concatenated\" — Sarvam ships one — but do not expect every vendor to." },
  { icon: "2", title: "Sarvam is already indexed in Context7 — library ID /websites/sarvam_ai",
    body: "No API key needed, docs pre-indexed. But say the caveat too: Context7 re-crawls on its own schedule, so for an API shipping this fast the vendor's own llms.txt is fresher by definition.",
    color: C.TEAL },
  { icon: "★", title: "And one correction to my own gotchas slide",
    body: "The 8 kHz row used to say \"no sample_rate → garbage transcript\". Lab 02 disproved it: sample_rate is not a REST parameter at all. It belongs to the streaming APIs, where raw PCM has no header. A rubric that encodes a stale belief punishes correct code.",
    color: C.SAF },
], { y: 1.6, rh: 1.35, bSize: 10.5 });
T.foot(s, ...FT);

/* 14 */ s = T.slideD(p, "An Agent Skill, in one slide", "The layer you own");
T.code(p, s, { y: 1.55, h: 2.65, label: "skills/sarvam-cost-metering/SKILL.md",
  code: `---
name: sarvam-cost-metering          # <=64 chars, a-z0-9-, MUST match the folder
description: Adds rupee cost tracking to Sarvam AI API calls. Use whenever
  writing or reviewing Python that calls the sarvamai SDK...   # <=1024 chars
license: Apache-2.0
---

# Sarvam cost metering
Every Sarvam API call costs money. Attach a meter entry to every billed call...` });
T.rows(p, s, [
  { icon: "1", title: "Progressive disclosure is the design constraint",
    body: "name + description (~100 tokens) load for EVERY installed skill at startup. The body loads only on activation — keep it under 500 lines / 5,000 tokens. Detail goes in references/, loaded only when needed.", color: C.TEAL },
  { icon: "2", title: "The description is doing triage, not marketing",
    body: "It is read by a model that has not opened your skill yet, deciding whether to. Say what it does AND when to use it. Write it for that job.", color: C.SAF },
], { y: 4.45, rh: 1.0, dark: true, bSize: 10.5 });

/* 15 */ s = T.slideL(p, "Does any of it actually work? Measure it.", "The section that earns the lab");
T.rows(p, s, [
  { icon: "★", title: "Your gotchas slide becomes an automated grader — now 14 rules, not 8",
    body: "One regex per gotcha, matching the WRONG pattern. The first 8-rule version scored a context-free generation 8/8 while the code carried six real defects none of the rules described. An incomplete rubric does not merely miss mistakes — it manufactures confidence. Grow it every time you find a trap.", color: C.SAF },
], { y: 1.6, rh: 1.25, bSize: 10.5 });
T.table(p, s, { y: 3.05, headers: ["Context layer", "Score", "Context tokens", "What it can and cannot fix"], colW: [3.0, 1.7, 2.3, 5.093],
  rows: [
    ["0 · no context",        "measure it", "0",       "the baseline you must beat"],
    ["1 · markdown page",     "measure it", "~2–4k",   "only mistakes THAT page documents — a chat page cannot fix an STT error"],
    ["2 · llms.txt retrieval","measure it", "~4–8k",   "bounded by whether keyword scoring found the right pages"],
    ["3 · agent skill",       "measure it", "~0.5k",   "smallest payload; covers exactly what you wrote into it"],
    ["4 · skill + markdown",  "measure it", "~6–12k",  "usually the winner — prescription plus description"],
  ], rowH: 0.34, size: 9.5 });
T.takeaway(p, s, "Do not expect a clean sweep from every layer, and do not read a low score as \"the model is bad at coding\" — a doc page can only fix what it documents. Only a skill written AGAINST the rubric should be expected to clear it.", { y: 5.6, h: 0.85, size: 11 });
T.foot(s, ...FT);

/* 16 */ s = T.analogy(p, { kicker: "Why skills beat documentation", symbol: "§", symSize: 88,
  title: "The recipe card the cook actually keeps",
  story: "Every professional kitchen owns the same shelf of cookbooks. Nobody reads them during service.\n\nWhat they read is the card taped inside the cupboard door — three lines in the head chef's handwriting. \"Our stock is salted. Do not season before reducing. The oven runs hot by 15 degrees.\"\n\nThat card is not better than the cookbooks. It is smaller, it is specific to this kitchen, and it is where the burnt dinners are recorded.",
  punch: "Documentation tells your assistant what the API offers. A skill tells it what YOUR team gets wrong. Add one line every time somebody hits a trap, and in six months that file is the most valuable engineering artefact you own." });

/* 17 */ s = T.slideL(p, "Take this home", "The two-layer default");
T.compare(p, s,
  { icon: "S", title: "An Agent Skill — prescriptive, yours", color: C.SAF, items: [
    "npx skills add sarvamai/skills",
    "Then write your own for your house rules",
    "SDK signatures and the traps, not the tour",
    "Under 500 lines; detail in references/",
    "Grows one line at a time, forever",
    "Loaded automatically by every assistant your team uses",
  ]},
  { icon: "L", title: "Plus llms.txt — descriptive, current", color: C.TEAL, items: [
    "docs.sarvam.ai/llms.txt — the map",
    "docs.sarvam.ai/llms-full.txt — the territory",
    "Append .md to any page for a clean version",
    "Nothing is fresher; the vendor publishes it",
    "Costs nothing and needs no setup at all",
    "Context7 on top if you work across many libraries",
  ]},
  { y: 1.7, h: 3.85, size: 11 });
T.takeaway(p, s, "One layer prescribes, the other describes. Together they cover both halves of the problem — and the whole setup is an afternoon, once.");
T.foot(s, ...FT);

/* 18 */ T.quoteSlide(p, { quote: "The model was never the bottleneck.\nWhat it could reach was.",
  by: "— End of Segment 10. Labs 11 and 12 are the hands-on: measure all of it yourself." });

p.writeFile({ fileName: "10_MCP_and_Context_Engineering.pptx" }).then(f => console.log("OK", f));
