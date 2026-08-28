const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW } = T;
const p = new P(); p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "Capabilities, Limits and What's Next";
const FT = ["AIVidhya4Sarvam · Building with Sarvam", "08 · Limits & Next"];
let s;

/* 1 */ T.titleSlide(p, { eyebrow: "Segment 08 · The honest map", title: "What you can build.\nWhat you cannot. Yet.",
  subtitle: "Twenty minutes of honesty buys more trust than twenty minutes of enthusiasm",
  meta: "Capabilities · limitations · the gotchas list · what happens next" });

/* 2 */ s = T.slideL(p, "Genuinely strong today", "Capabilities");
T.cards(p, s, [
  { icon: "✓", title: "Indic speech, both directions", body: "23 languages in, 11 out. Code-mixed input handled natively. Nothing else comes close on Indian language coverage." },
  { icon: "✓", title: "8 kHz telephony audio", body: "Real Indian call traffic. Most Western models degrade badly here; this stack was built for it." },
  { icon: "✓", title: "Indic document extraction", body: "Typed, scanned and handwritten, across 23 languages and scripts, at ₹0.50 a page.", color: C.TEAL },
  { icon: "✓", title: "Cost", body: "The Indic-native flagship is also the cheapest chat model on the platform. Document processing is 3x cheaper than a year ago.", color: C.TEAL },
  { icon: "✓", title: "Sovereign deployment", body: "Managed, VPC, on-premise, air-gapped. SOC 2 Type II, ISO 27001, DPDP. Chanakya for defence-grade isolation." },
  { icon: "✓", title: "Open weights", body: "30B and 105B under Apache 2.0. You are not locked in — you can take the weights and run." },
], { cols: 3, y: 1.68, h: 1.88 });
T.takeaway(p, s, "For any product where Indian language, Indian data residency, or Indian cost structure is a hard requirement, this is now the default answer rather than the patriotic one.");
T.foot(s, ...FT);

/* 3 */ s = T.slideD(p, "Where it is genuinely weaker", "Limitations");
T.rows(p, s, [
  { icon: "1", title: "Frontier general reasoning still trails the best closed models", body: "Sarvam-105B is excellent and competitive in its class. For the hardest general reasoning tasks in English, the global frontier is still ahead. Pretending otherwise costs you credibility." },
  { icon: "2", title: "Ecosystem depth is younger", body: "Fewer Stack Overflow answers, fewer blog posts, fewer people who have hit your exact bug. You will be reading source and docs more often.", color: C.RED },
  { icon: "3", title: "Documentation lags announcements", body: "V4 and Vision 2.0 shipped ten days ago and are not in the public API docs. You saw this yourself in segment two.", color: C.RED },
  { icon: "4", title: "TTS covers 11 languages, ASR covers 23", body: "You can transcribe Santali. You cannot speak it back yet. Design around the narrowest model in your chain." },
  { icon: "5", title: "Hard operational limits", body: "Document AI: 10 pages a job, 10 requests a minute on every plan. STT REST: 30 seconds. These shape your architecture, not just your code." },
], { y: 1.62, rh: 0.88, dark: true, bSize: 10.5 });
T.takeaway(p, s, "Say all of this out loud when you teach it. A room that hears you name real weaknesses believes you about the strengths.", { dark: true, y: 6.25, h: 0.78, size: 11.5 });

/* 4 */ s = T.slideL(p, "The gotchas list", "The most-saved slide of the session");
T.table(p, s, { y: 1.6, headers: ["Gotcha", "Symptom", "Fix"], colW: [4.3, 4.0, 3.793],
  rows: [
    ["client.chat.completions.create(...)", "AttributeError", "client.chat.completions(...) — no .create"],
    ["reasoning eats max_tokens", "content is None", "Raise max_tokens or reasoning_effort=None"],
    ["output_script on sarvam-translate", "200 OK, wrong script", "Use Mayura, or post-process"],
    ["language_code on Document AI", "Silently ignored", "Use language="],
    ["output_format=\"markdown\"", "400 Bad Request", "Use \"md\""],
    ["schema as a dict", "'dict' has no attribute 'read'", "json.dumps(schema)"],
    ["file=open(...) on doc_ai", "Type error", "file=[(name, handle, mime)] — an array"],
    ["sample_rate= on REST transcribe()", "TypeError: unexpected keyword", "Drop it — the WAV header carries it"],
    ["sample_rate MISSING when streaming", "Garbage transcript, no error", "connect(sample_rate=...) — raw PCM has no header"],
    ["Only checking status == completed", "Pages silently lost", "Handle partially_completed"],
    ["Results before terminal state", "409", "Poll get_status first"],
    ["Bulbul v3 by default", "2x the TTS bill", "v2 is often adequate for IVR"],
    ["Assuming model defaults are stable", "Behaviour changes silently", "Pass model= explicitly, always"],
    ["async with on the sync SarvamAI", "asynchronous context manager", "Use with — or AsyncSarvamAI"],
    ["MCP tool calls miss your ₹ meter", "Bill reads ₹0.00, silently", "Wrap the tool and meter your inputs"],
  ], rowH: 0.26, size: 9 });
T.takeaway(p, s, "Screenshot this one. It is the single most useful artefact from today, and every item on it cost somebody a working day to discover.");
T.foot(s, ...FT);

/* 5 */ s = T.slideL(p, "\"Why not just use OpenAI or Gemini?\"", "The question you will be asked");
T.compare(p, s,
  { icon: "✓", title: "Where Sarvam genuinely wins", color: C.TEAL, items: [
    "Indic speech recognition — 23 languages, code-mixed, 8kHz telephony",
    "Indic TTS quality and voice range",
    "Document extraction across Indian scripts, including handwriting",
    "Data residency, DPDP, and India-domiciled processing",
    "Rupee pricing, GST invoices, local procurement",
    "On-premise and air-gapped deployment options",
    "Cost — meaningfully cheaper for these workloads",
  ]},
  { icon: "→", title: "Where the global stack is still ahead", color: C.SAF, items: [
    "Frontier general reasoning in English",
    "Multimodal breadth — video, advanced vision, real-time interruption",
    "Ecosystem maturity: tooling, integrations, community answers",
    "Very long context handling at the extreme end",
    "Model variety — you cannot A/B five frontier models here",
    "Documentation completeness and stability",
    "",
  ]},
  { y: 1.7, h: 3.9, size: 11 });
T.takeaway(p, s, "The right answer is not loyalty to one stack. It is knowing precisely which workload belongs where — and being able to defend that choice to a risk team.");
T.foot(s, ...FT);

/* 6 */ s = T.slideL(p, "The other questions you will get", "FAQ");
T.rows(p, s, [
  { icon: "1", title: "\"Will Sarvam compete with what I build?\"", body: "They sell platforms to large enterprises with forward-deployed teams. Vertical depth, SMB, workflow-adjacent and on-prem appliance remain genuinely open. Be straight that this could change — and architect for portability." },
  { icon: "2", title: "\"What is the real accuracy on my dialect?\"", body: "I do not know, and nor does anyone who has not tested it. Take twenty recordings from your own users and measure it in an afternoon. That answer beats any benchmark." },
  { icon: "3", title: "\"What if they raise prices?\"", body: "30B and 105B are Apache 2.0. The API is OpenAI-compatible. Both facts mean real portability. Architect for model-swappability from day one and this stops being a risk.", color: C.TEAL },
  { icon: "4", title: "\"How long to production?\"", body: "Weeks for a prototype. Months for a regulated deployment. In Indian enterprise the long pole is procurement and security review, not engineering.", color: C.TEAL },
], { y: 1.7, rh: 0.98, bSize: 10.5 });
T.takeaway(p, s, "\"I don't know, and here is how we would find out\" is a better answer than a confident guess. Experienced rooms can tell the difference instantly.");
T.foot(s, ...FT);

/* 7 */ s = T.analogy(p, { kicker: "On choosing a stack", symbol: "⇄", symSize: 88,
  title: "Nobody asks a carpenter why he owns two saws",
  story: "A carpenter has a hand saw and a circular saw. Nobody asks him to justify the choice, or accuses him of disloyalty to one.\n\nHe uses the circular saw for long straight cuts in cheap timber, and the hand saw when he is working close to a finished edge and cannot afford a mistake.\n\nThe question is never \"which saw is better\". It is \"what am I cutting\".",
  punch: "You will use Sarvam for Indic speech, Indian documents and anything a compliance officer has to sign off. You will use something else for frontier English reasoning. Knowing which is which is the skill — not picking a side." });

/* 8 */ s = T.sectionSlide(p, { num: "B", title: "What happens next", subtitle: "India's AI Sovereignty Month — 15 August to 15 September" });

/* 9 */ s = T.slideL(p, "Your next 30 days", "Take this home");
T.flow(p, s, [
  { t: "Week 1", d: "Ship something. Show one person in your ICP. Write down exactly what they said." },
  { t: "Week 2", d: "Build a 10-case eval set from real data. Measure accuracy on YOUR audio." },
  { t: "Week 3", d: "Price it. Send one paid-pilot proposal to one named prospect." },
  { t: "Week 4", d: "Apply to the Sarvam Startup Program. Post your build in Discord. Contribute a cookbook example." },
], { y: 2.0, h: 1.9 });
T.rows(p, s, [
  { icon: "★", title: "The one that compounds", body: "Contributing to the cookbook costs you an evening and permanently changes how the ecosystem sees you. It is the cheapest developer marketing available, and it puts your name in front of the team building this." },
], { y: 4.3, rh: 1.0 });
T.takeaway(p, s, "Set up the tooling tonight — Agent Skills, MCP server, Kivi. Ten minutes now saves an afternoon next week.");
T.foot(s, ...FT);

/* 10 */ s = T.slideD(p, "India's AI Sovereignty Month", "What I am running next");
T.cards(p, s, [
  { icon: "1", title: "17–28 August — Campus tour", body: "Free hands-on sessions for students at colleges across the region. If you are at an institution that would want this, message me tonight. I am not charging students." },
  { icon: "2", title: "29–30 August — The full workshop", body: "Two days, 16 hours, ₹1,000. You build a voice agent that answers a real phone call, a document pipeline, an agentic workflow with evals, and your own costed business model.", color: C.TEAL },
  { icon: "3", title: "19 September — 8-week cohort", body: "From 'I can call the API' to 'I have shipped a product'. Weekly live sessions, code review, capstone. ₹2,500 students / ₹5,000 professionals. Early bird open now." },
], { cols: 3, y: 1.75, h: 2.35, dark: true, bSize: 11 });
T.takeaway(p, s, "The ₹1,000 from the August workshop is credited against your cohort fee. If today was useful, that is the path — and the links are in chat now.", { dark: true, y: 4.5 });
T.rows(p, s, [
  { icon: "?", title: "One ask before you go", body: "If you are at a college, or know a coding club that would want a session like this — message me. My room is my pipeline, and I would rather ask than assume." },
], { y: 5.6, rh: 1.0, dark: true });

/* 11 */ s = T.slideL(p, "Everything you need, in one place", "Resources");
T.table(p, s, { y: 1.62, headers: ["What", "Where"], colW: [4.5, 7.593],
  rows: [
    ["Documentation", "docs.sarvam.ai — append .md to any page for Markdown"],
    ["Full docs as one file", "docs.sarvam.ai/llms-full.txt"],
    ["Dashboard, keys, playground", "dashboard.sarvam.ai"],
    ["Changelog — check before every project", "docs.sarvam.ai/api/getting-started/changelog"],
    ["Cookbook", "github.com/sarvamai/sarvam-ai-cookbook"],
    ["Agent Skills", "github.com/sarvamai/skills — npx skills add sarvamai/skills"],
    ["MCP server", "uvx sarvam-mcp"],
    ["Indus", "indus.sarvam.ai"],
    ["Status page", "status.sarvam.ai"],
    ["Discord community", "discord.com/invite/5rAsykttcs"],
    ["Startup Program", "sarvam.ai/startup-program"],
    ["Sarvam Champions", "sarvam.ai/sarvam-champions"],
    ["Self-hosting on SageMaker", "docs.sarvam.ai/api/self-hosted/introduction"],
    ["Migration guides", "docs.sarvam.ai/api/migrations — from ElevenLabs, Cartesia, Deepgram, Gemini"],
  ], rowH: 0.28, size: 10 });
T.foot(s, ...FT);

/* 12 */ s = T.slideL(p, "Before you close the tab", "Certificate & feedback");
T.flow(p, s, [
  { t: "Run the lab", d: "if you have not finished it" },
  { t: "Fill the form", d: "link in chat, 2 minutes" },
  { t: "Paste your ₹ total", d: "what the cost report printed" },
  { t: "Tell me one thing to change", d: "for the 29–30 August workshop" },
  { t: "Certificate follows", d: "by email, Sunday" },
], { y: 2.05, h: 1.8 });
T.rows(p, s, [
  { icon: "★", title: "The one question I actually need answered honestly", body: "\"What is one thing I should change for the 29–30 August workshop?\" I am running this five more times on campuses this month. Flattering feedback helps nobody — tell me what did not land." },
], { y: 4.35, rh: 1.0 });
T.takeaway(p, s, "And if you generated audio you liked, drop it in chat. I want to count how many Indian languages this room covered tonight.", { icon: "♪" });
T.foot(s, ...FT);

/* 13 */ T.quoteSlide(p, { quote: "The model is not the moat.\nThe workflow, the distribution\nand the cost structure are.",
  by: "Thank you, and happy Independence Day.   —   aividhya.in · dharmanibc@gmail.com" });

/* 14 */ s = T.titleSlide(p, { eyebrow: "Next", title: "29–30 August\nThe full workshop",
  subtitle: "16 hours. You build a voice agent, a document pipeline, an agentic workflow, and a business model.",
  meta: "₹1,000 — credited against the September cohort · Links in chat · aividhya.in" });

p.writeFile({ fileName: "08_Capabilities_Limits_and_Next.pptx" }).then(f => console.log("OK", f));
