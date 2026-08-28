const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW, W } = T;
const p = new P(); p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "The Sarvam Stack After Epoch";
const FT = ["AIVidhya4Sarvam · Building with Sarvam", "02 · The Stack"];
let s;

/* 1 */ T.titleSlide(p, { eyebrow: "Segment 02", title: "The Sarvam Stack,\nafter Epoch 2026",
  subtitle: "Five layers, twelve new products, and the gap between announced and callable",
  meta: "Epoch 2026 · Bengaluru · 30 July 2026 — ten days before this session" });

/* 2 */ s = T.slideD(p, "One company, five layers", "The map");
T.rows(p, s, [
  { icon: "1", title: "MODELS — what you call", body: "Saaras (speech in) · Bulbul (speech out) · Sarvam-105B / 30B (reasoning) · Mayura & Sarvam-Translate (translation) · Sarvam Vision (documents)" },
  { icon: "2", title: "APIs — the developer surface", body: "REST · Batch · WebSocket streaming · OpenAI-compatible chat · Document AI jobs · Dubbing · Pronunciation dictionaries" },
  { icon: "3", title: "PRODUCTS — what you compete with, partner with, or resell", body: "Indus · Samvaad · Arya · Akshar · Studio · Kivi · Kaze · Sarvam Code · Edge", color: C.TEAL },
  { icon: "4", title: "TOOLING — the productivity multiplier", body: "Python & JS SDKs · MCP server · Agent Skills · llms.txt · Context7 · API Playground · Cookbook", color: C.TEAL },
  { icon: "5", title: "DEPLOYMENT — where it runs", body: "Sarvam Cloud · Private VPC · On-premise · Air-gapped · AWS Marketplace + SageMaker · Chanakya · Anvaya" },
], { y: 1.7, rh: 1.02, dark: true });
s.addNotes("Walk the poster. They don't need to retain it — they need to have seen the shape. Five layers, and today we mostly live in layers 1, 2 and 3.");

/* 3 */ s = T.sectionSlide(p, { num: "A", title: "Layer 1 — The models", subtitle: "Six model families, each doing one job well" });

/* 4 */ s = T.slideL(p, "The model line-up", "Layer 1");
T.table(p, s, { y: 1.6, headers: ["Model", "Job", "Languages", "Model ID", "Status"],
  colW: [2.3, 3.3, 2.3, 2.5, 1.693],
  rows: [
    ["Saaras v3", "Speech to text, 5 modes", "23 (22 Indic + En)", "saaras:v3", "Live"],
    ["Bulbul v3", "Text to speech, 30+ voices", "11", "bulbul:v3", "Live"],
    ["Sarvam-105B", "Flagship reasoning LLM", "11", "sarvam-105b", "Live"],
    ["Sarvam-30B", "Smaller reasoning LLM", "11", "sarvam-30b", "Deprecated → use 105B"],
    ["Mayura v1", "Translation", "11", "mayura:v1", "Live"],
    ["Sarvam-Translate v1", "Extended translation", "23", "sarvam-translate:v1", "Live"],
    ["Sarvam Vision 1.5", "Document OCR + extraction", "23", "via doc_ai", "Live"],
    ["Saarika v2.5", "Legacy ASR", "11", "saarika:v2.5", "Legacy"],
    ["Sarvam-M / 30B-16k", "Superseded", "—", "—", "Deprecated"],
  ], rowH: 0.33, size: 10 });
T.takeaway(p, s, "Also on the chat endpoint, third-party: Gemma-4 31B and GLM 5.2. Note the pricing later — the Indic-native flagship is also the cheapest of the three.");
T.foot(s, ...FT);

/* 5 */ s = T.slideL(p, "Saaras — speech in", "Model deep dive");
T.cards(p, s, [
  { icon: "◆", title: "23 languages", body: "All 22 constitutionally scheduled Indian languages plus English. The widest Indic ASR coverage available anywhere." },
  { icon: "5", title: "Five output modes", body: "transcribe · translate · verbatim · translit · codemix. One audio file, five different jobs. This is the differentiator." },
  { icon: "⚡", title: "Three delivery paths", body: "REST for clips under 30s · Batch for up to 20 files x 60 min with diarization · WebSocket for real-time with VAD.", color: C.TEAL },
  { icon: "▶", title: "Built for real audio", body: "Code-mixed speech, heavy accent variance, and 8kHz telephony — the three things that break Western ASR models.", color: C.TEAL },
], { cols: 4, y: 1.7, h: 2.15, bSize: 10.5 });
T.takeaway(p, s, "₹30/hour, or ₹45/hour with speaker diarization. Billed per second, rounded up per request.", { icon: "₹" });
T.foot(s, ...FT);

/* 6 */ s = T.slideL(p, "Bulbul — speech out", "Model deep dive");
T.cards(p, s, [
  { icon: "♪", title: "30+ voices, 11 languages", body: "Chosen by persona — Conversational/Friendly, News/Authoritative, Entertainment/Dynamic — not by personal preference." },
  { icon: "⚙", title: "Full control surface", body: "Pitch, pace, loudness, tone, sample rate. Plus pronunciation dictionaries for brand names, SKUs and scheme names." },
  { icon: "⚡", title: "Streaming is mandatory", body: "REST, HTTP stream, and WebSocket with an end signal. For a voice agent, first-audio latency is the entire experience.", color: C.TEAL },
  { icon: "■", title: "Telephony formats", body: "mp3, linear16, mulaw, alaw, opus, flac, aac, wav. mulaw and alaw are the ones your phone system needs.", color: C.TEAL },
], { cols: 4, y: 1.7, h: 2.15, bSize: 10.5 });
T.takeaway(p, s, "Bulbul v3 is ₹30/10K characters. Bulbul v2 is ₹15/10K. On a high-volume IVR, that single choice is your entire margin.", { icon: "₹" });
T.foot(s, ...FT);

/* 7 */ s = T.slideL(p, "Sarvam-105B — the flagship", "Model deep dive");
T.stats(p, s, [
  { value: "105B+", label: "parameters, Mixture-of-Experts\nwith 128 sparse experts" },
  { value: "12T", label: "pre-training tokens across code,\nmath, multilingual and web", color: C.TEAL },
  { value: "128K", label: "context window,\nMulti-head Latent Attention" },
  { value: "Apache 2.0", label: "open weights —\nyou are not locked in", color: C.TEAL },
], { y: 1.7, h: 1.9, vSize: 30 });
T.table(p, s, { y: 3.85, headers: ["Benchmark", "Score", "What it means"], colW: [3.0, 1.8, 7.293],
  rows: [
    ["Math500", "98.6", "Multi-step mathematical reasoning"],
    ["AIME 2025", "88.3 (96.7 with tools)", "Competition-level problem solving"],
    ["BrowseComp", "49.5", "Agentic web navigation — matters for tool use"],
    ["Tau2 (avg)", "68.3", "Tool use and environment interaction — highest among compared models"],
    ["Indic pairwise", "wins 90%", "Against open and closed frontier models of its class"],
  ], rowH: 0.3, size: 10 });
T.foot(s, ...FT);
s.addNotes("Dwell on BrowseComp and Tau2 — those are the agentic numbers, and they're what matter for everything we do on Day 2 of the full workshop.");

/* 8 */ s = T.slideL(p, "The language layer and Vision", "Model deep dive");
T.compare(p, s,
  { icon: "→", title: "Translation & script", color: C.SAF, items: [
    "Mayura v1 — 11 languages, tuned quality, context preservation",
    "Sarvam-Translate v1 — 23 languages, open weights, wider coverage",
    "Both ₹20 per 10K characters — choose on coverage first, register second",
    "Registers: colloquial, modern, classical, formal",
    "Transliterate — script conversion preserving pronunciation, ₹20/10K",
    "Language ID — returns language AND script, ₹3.50/10K. Cheap enough to run on every inbound message as a router",
  ]},
  { icon: "■", title: "Sarvam Vision 1.5 — documents", color: C.TEAL, items: [
    "3B-parameter vision-language model, 23 languages",
    "Digitise — full OCR, layout and reading order preserved, tables to HTML/Markdown",
    "Extract — you define a JSON schema, it returns those fields",
    "Handles typed, scanned and handwritten Indic documents",
    "₹0.50 per page — down from ₹1.50 in May 2026",
    "Hard limits: 10 pages per job, 200MB, 10 requests/minute on every plan",
  ]},
  { y: 1.7, h: 4.0, size: 11 });
T.foot(s, ...FT);

/* 9 */ s = T.sectionSlide(p, { num: "B", title: "Epoch 2026", subtitle: "Twelve products in a single day — 30 July 2026" });

/* 10 */ s = T.slideD(p, "What shipped at Epoch", "Ten days ago");
T.cards(p, s, [
  { icon: "♪", title: "Saaras V4", body: "Speech recognition across all 22 scheduled languages. Plus V4 Multi-Speaker with diarisation for multi-party conversations." },
  { icon: "♪", title: "Bulbul V4", body: "More expressive, more human-sounding text to speech." },
  { icon: "■", title: "Vision 2.0", body: "Digitising complex documents — an upgrade on the 1.5 generation." },
  { icon: "★", title: "Indus", body: "One platform, six tools: work, voice, content, doc and coding agents, plus the inference stack.", color: C.TEAL },
  { icon: "▶", title: "Kivi", body: "Desktop voice tool for speech-driven control and coding. Built on Saaras V4, natively multilingual.", color: C.TEAL },
  { icon: "◆", title: "Kaze", body: "AI smart glasses that understand what you see and assist with everyday tasks.", color: C.TEAL },
  { icon: "⚙", title: "Sarvam Code (Beta)", body: "A coding assistant built on open models, to help developers write and understand code." },
  { icon: "⚡", title: "Sarvam Inference", body: "India-hosted inference platform serving Sarvam-105B alongside frontier open models." },
  { icon: "§", title: "Chanakya & Anvaya", body: "A complete AI system that runs entirely inside your own servers, and a custom 30B model — both for defence, intelligence and government." },
  { icon: "₹", title: "Samvaad — now GA", body: "Managed voice agents generally available at ₹3.50 per minute. Your build-versus-buy benchmark for the rest of today." },
  { icon: "☎", title: "Instant phone numbers", body: "Rent an Indian number in about 30 seconds with PAN and Aadhaar verification. Removes the biggest friction in shipping a voice product." },
  { icon: "∞", title: "A 1 trillion+ model", body: "Announced as in training from scratch, targeted live within six months. For coding, cybersecurity, scientific research and simulation.", color: C.TEAL },
], { cols: 4, y: 1.62, h: 1.6, gap: 0.24, dark: true, bSize: 9.5, tSize: 12.5 });
s.addNotes("This is your differentiator as a teacher — almost nobody has assembled the post-Epoch picture yet, and the docs certainly haven't.");

/* 11 */ s = T.slideL(p, "Announced is not the same as callable", "The critical distinction");
T.table(p, s, { y: 1.65, headers: ["Announced at Epoch (30 July)", "What the public API serves today", "What you should do"],
  colW: [3.8, 3.6, 4.693],
  rows: [
    ["Saaras V4 / V4 Multi-Speaker", "saaras:v3", "Build on v3. Watch the changelog."],
    ["Bulbul V4", "bulbul:v3", "Build on v3."],
    ["Vision 2.0", "Sarvam Vision 1.5", "Build on 1.5 via doc_ai."],
    ["Sarvam Inference", "Not in public docs", "Watch for access."],
    ["Kivi / Kaze", "Product downloads, not APIs", "Use as products."],
    ["Indus (6 tools)", "Platform at indus.sarvam.ai", "Use the platform directly."],
    ["Chanakya / Anvaya", "Enterprise / government sales", "Contact sales."],
    ["1T+ parameter model", "Announced, ~6 months out", "Nothing to do yet."],
  ], rowH: 0.35, size: 10.5 });
T.takeaway(p, s, "Say this out loud when you teach it: everything we run today is on what is actually callable. Being the person who separates announced from shipped buys more trust than any demo.");
T.foot(s, ...FT);
s.addNotes("This slide is worth more than any demo. Anyone can read a launch blog. Knowing what actually works today is what people pay for.");

/* 12 */ s = T.sectionSlide(p, { num: "C", title: "Layer 3 — The products", subtitle: "What you compete with, partner with, or resell" });

/* 13 */ s = T.slideL(p, "The product portfolio", "Layer 3");
T.table(p, s, { y: 1.6, headers: ["Product", "What it is", "Why a developer cares"], colW: [2.2, 4.4, 5.493],
  rows: [
    ["Indus", "Agentic platform — six tools in one", "The reference architecture for what you'd build"],
    ["Samvaad", "Conversational AI — voice, WhatsApp, web", "GA at ₹3.5/min. Your build-vs-buy benchmark"],
    ["Arya", "Enterprise agent platform", "Teaches the patterns your own agents need"],
    ["Akshar", "Document digitisation", "Vision, productised"],
    ["Studio", "Content transformation and dubbing", "Media and edtech vertical"],
    ["Kivi", "Desktop voice tool", "A product category wide open in your vertical"],
    ["Kaze", "AI smart glasses", "Ambient computing, early"],
    ["Sarvam Code", "Coding agents (Beta)", "Dev tooling surface"],
    ["Sarvam Edge", "On-device inference", "Offline and rural, low-connectivity"],
    ["Chanakya / Anvaya", "On-prem and defence stack", "How regulated buyers actually deploy"],
    ["Model Training", "Custom model training service", "The enterprise upsell path"],
  ], rowH: 0.31, size: 10 });
T.foot(s, ...FT);

/* 14 */ s = T.slideD(p, "Arya — the patterns worth stealing", "Enterprise agents");
T.cards(p, s, [
  { icon: "✓", title: "Checkpointed steps", body: "A failure at step 40 does not lose the first 39. Recovery is instant. 50-step workflows just work." },
  { icon: "◆", title: "Total observability", body: "Every reasoning step, tool call and decision is logged and inspectable. Replay any step with different inputs." },
  { icon: "§", title: "Scoped permissions", body: "Connect private tools, databases and APIs without exposing them. Each agent accesses only what it needs." },
  { icon: "⇄", title: "Model portability", body: "Bring your own model or use theirs. Swap vendors without rewriting workflows. A/B test across providers." },
  { icon: "⟳", title: "Self-improving", body: "Structured feedback loops and persistent memory — agents learn from corrections and carry it forward.", color: C.TEAL },
  { icon: "∞", title: "Long-run reliable", body: "Workflows spanning hours or days. State managed across long-horizon processes without silent failure.", color: C.TEAL },
], { cols: 3, y: 1.68, h: 1.85, dark: true });
T.takeaway(p, s, "You are not being sold Arya. You are learning the checklist an enterprise buyer will hold you to — and 'LLMs reason, code executes' is the design law underneath all of it.", { dark: true, y: 5.75 });

/* 15 */ s = T.sectionSlide(p, { num: "D", title: "Layer 4 — Developer tooling", subtitle: "The multiplier most people skip" });

/* 16 */ s = T.slideL(p, "Four ways to make your AI assistant good at this stack", "Tooling");
T.rows(p, s, [
  { icon: "1", title: "Official SDKs — pip install sarvamai / npm install sarvamai", body: "Typed clients with async, retries and streaming built in. Reduces integration from hours to minutes." },
  { icon: "2", title: "MCP server — uvx sarvam-mcp", body: "Exposes every public Sarvam API as a tool to Claude Desktop, Claude Code, Cursor, Windsurf, Zed. Two namespaces: sarvam_tools_* to call APIs, sarvam_code_* for docs and snippets.", color: C.TEAL },
  { icon: "3", title: "Agent Skills — npx skills add sarvamai/skills", body: "Six skills (chat, speech-to-text, text-to-speech, translate, voice-agents, vibe-coding) that teach your assistant the SDK quirks it otherwise gets wrong.", color: C.TEAL },
  { icon: "4", title: "llms.txt and Markdown docs", body: "Append .md to any docs URL. /llms.txt for the index, /llms-full.txt for the whole corpus — built for RAG ingestion and one-shot context." },
], { y: 1.7, rh: 0.98, bSize: 10.5 });
T.takeaway(p, s, "Without the skills installed, your assistant writes client.chat.completions.create(...). The real method is client.chat.completions(...). We will prove this live in three minutes.");
T.foot(s, ...FT);

/* 17 */ s = T.slideL(p, "Which tool, when", "Tooling");
T.table(p, s, { y: 1.7, headers: ["", "Agent Skills", "MCP server", "llms.txt"], colW: [2.5, 3.2, 3.2, 3.193],
  rows: [
    ["When it loads", "Once, installed into your project or editor", "Live, queried on demand while coding", "Fetched manually when you need it"],
    ["Best for", "Baking in SDK corrections an assistant keeps getting wrong", "Interactive sessions needing current API details, or to call Sarvam directly", "Bulk ingestion, RAG indexes, one-shot context"],
    ["Setup", "npx skills add sarvamai/skills", "One-time MCP client config", "None — just a URL"],
  ], rowH: 0.9, size: 10.5 });
T.takeaway(p, s, "They are complementary. A skill stops the wrong method name; the MCP server and llms.txt supply the parameter tables a skill deliberately leaves out.");
T.foot(s, ...FT);

/* 18 */ s = T.sectionSlide(p, { num: "E", title: "Layer 5 — Where it runs", subtitle: "Managed, private, on-premise, air-gapped" });

/* 19 */ s = T.slideL(p, "Four deployment postures", "Layer 5");
T.cards(p, s, [
  { icon: "1", title: "Sarvam Cloud", body: "Fully managed, automatic scaling, fastest time to value. Pay per call. Data transits Sarvam. Where you start." },
  { icon: "2", title: "Private Cloud (VPC)", body: "Your security perimeter, their management. The middle option most mid-size enterprises land on." },
  { icon: "3", title: "On-premise / SageMaker", body: "Saaras v3, Bulbul v3 and Vision self-hosted via AWS Marketplace. Audio and documents never leave your VPC.", color: C.TEAL },
  { icon: "4", title: "Air-gapped", body: "Network isolation enabled, no outbound internet from the model container. Chanakya for defence and national security.", color: C.TEAL },
], { cols: 4, y: 1.7, h: 2.2, bSize: 10.5 });
T.rows(p, s, [
  { icon: "₹", title: "The crossover calculation", body: "Per-call pricing wins until volume justifies a permanently-running GPU. At ₹30/hour for STT, work out how many audio-hours a month justify a dedicated endpoint. That number is the most useful thing you can take to a bank." },
  { icon: "★", title: "No licence key, no proxy", body: "AWS Marketplace handles entitlement. Subscribe, deploy via console, boto3 or Terraform, and the endpoint is licensed for the instances you run." },
], { y: 4.2, rh: 0.95 });
T.foot(s, ...FT);

/* 20 */ s = T.slideL(p, "The integrations you will actually reach for", "Ecosystem");
T.cards(p, s, [
  { icon: "▶", title: "LiveKit", body: "WebRTC-native voice agents. Production-hardened. Best for web and app. First-party Sarvam plugin plus a production best-practices guide." },
  { icon: "▶", title: "Pipecat", body: "Python-native pipeline. Easier to reason about. Best for learning and custom flows. Also has a production guide." },
  { icon: "☎", title: "Twilio / Exotel / Vapi", body: "Telephony. Exotel is usually right for India — cheaper, better DLT/TRAI compliance. Or rent a number from Sarvam in 30 seconds.", color: C.TEAL },
  { icon: "⚙", title: "n8n", body: "Workflow automation. Call Sarvam APIs as drop-in nodes, no code required.", color: C.TEAL },
  { icon: "◆", title: "LangChain", body: "Agent scaffolding. Works via the OpenAI-compatible endpoint with a base-URL swap." },
  { icon: "◆", title: "Vercel AI SDK", body: "Streaming UI for JavaScript and TypeScript apps. Same base-URL swap story.", color: C.TEAL },
], { cols: 3, y: 1.68, h: 1.85 });
T.takeaway(p, s, "Because chat completions are OpenAI-compatible, most existing code works with a base-URL change. We will demo that swap in the next segment — it takes ninety seconds.");
T.foot(s, ...FT);

/* 21 */ s = T.slideL(p, "Language coverage — check before you pick a model", "Reference");
T.compare(p, s,
  { icon: "23", title: "23 languages — Saaras v3, Sarvam-Translate, Vision", color: C.SAF, items: [
    "Hindi hi-IN · Bengali bn-IN · Tamil ta-IN · Telugu te-IN",
    "Marathi mr-IN · Gujarati gu-IN · Kannada kn-IN · Malayalam ml-IN",
    "Odia od-IN · Punjabi pa-IN · Assamese as-IN · Urdu ur-IN",
    "Nepali ne-IN · Konkani kok-IN · Kashmiri ks-IN · Sindhi sd-IN",
    "Sanskrit sa-IN · Santali sat-IN · Manipuri mni-IN · Bodo brx-IN",
    "Maithili mai-IN · Dogri doi-IN · English en-IN",
  ]},
  { icon: "11", title: "11 languages — Bulbul v3, Mayura, Sarvam-105B", color: C.TEAL, items: [
    "Hindi hi-IN · Bengali bn-IN · Tamil ta-IN · Telugu te-IN",
    "Gujarati gu-IN · Kannada kn-IN · Malayalam ml-IN",
    "Marathi mr-IN · Punjabi pa-IN · Odia od-IN · English en-IN",
    "",
    "This asymmetry matters: you can TRANSCRIBE Santali but you cannot SPEAK it back yet.",
    "Design your product around the narrowest model in your chain.",
  ]},
  { y: 1.7, h: 3.9, size: 11 });
T.takeaway(p, s, "The narrowest model in your pipeline defines your product's language coverage. Check it before you promise a customer 22 languages.");
T.foot(s, ...FT);

/* 22 */ s = T.analogy(p, { kicker: "How to read a launch", symbol: "?", symSize: 100,
  title: "The restaurant with a very long menu",
  story: "A new restaurant opens with a menu of forty dishes. You order the biryani. The waiter says: \"That one is coming soon.\"\n\nYou order the dosa. \"Also coming soon.\"\n\nEventually you learn that eight dishes are actually available today, and the rest are on the menu because the chef intends to make them.\n\nThe menu is not lying. It is a roadmap printed as a menu.",
  punch: "Epoch announced twelve products. The API serves a subset today. Both facts are true, and the developer who knows which is which does not waste a weekend building against a model that is not there yet." });

/* 23 */ s = T.slideD(p, "Where this is going", "The roadmap");
T.stats(p, s, [
  { value: "1T+", label: "parameter model announced,\nlive within ~6 months" },
  { value: "V4 / 2.0", label: "speech and vision generations\nrolling into the API", color: C.TEAL },
  { value: "6", label: "tools converging into\none Indus platform" },
  { value: "₹3.5", label: "per minute — managed voice\nagents, generally available", color: C.TEAL },
], { y: 1.85, h: 1.95, vSize: 32, dark: true });
T.bullets(p, s, [
  "The direction is unmistakable: from APIs you assemble, toward platforms you deploy. Samvaad and Indus are that shift made concrete.",
  "For a developer this is not a threat — it is a signal. Platform companies move up-market. The vertical, the SMB and the workflow-adjacent stay open.",
  "The open-weights release of 30B and 105B under Apache 2.0 is the safety valve. If pricing or terms ever change, you can self-host. Architect for that from day one.",
], { y: 4.15, dark: true, size: 12.5 });
s.addNotes("Close the segment here. Then straight into the lab — momentum matters and they have been listening for twenty minutes.");

/* 24 */ T.quoteSlide(p, { quote: "Anyone can read a launch blog.\nKnowing what actually works today is the job.",
  by: "— End of Segment 02. Next: we run code." });

p.writeFile({ fileName: "02_The_Sarvam_Stack_After_Epoch.pptx" }).then(f => console.log("OK", f));
