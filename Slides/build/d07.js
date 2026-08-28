const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW } = T;
const p = new P(); p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "Unit Economics and the Business";
const FT = ["AIVidhya4Sarvam · Building with Sarvam", "07 · The Money"];
let s;

/* 1 */ T.titleSlide(p, { eyebrow: "Segment 07 · The money", title: "What it costs.\nWhat you charge.",
  subtitle: "Twenty-five minutes that separate a demo from a business",
  meta: "Derived live. Bring your own volumes — we will run them on screen." });

/* 2 */ s = T.slideL(p, "The scenario we are costing", "Set-up");
T.cards(p, s, [
  { icon: "1", title: "A 3-minute outbound call", body: "Collections reminder for an NBFC. Realistic length for a payment-reminder conversation." },
  { icon: "2", title: "In Hindi, 8 turns", body: "Agent speaks, customer responds, eight times. Typical for a structured reminder call." },
  { icon: "3", title: "Customer speaks ~1.2 min", body: "The rest is the agent talking and silence. Only what the customer says goes through STT.", color: C.TEAL },
  { icon: "4", title: "Agent speaks ~1.8 min", body: "Roughly 1,600 characters of synthesised speech. This number matters more than you expect.", color: C.TEAL },
], { cols: 4, y: 1.72, h: 2.0, bSize: 10.5 });
T.txt(s, "We are going to build this up one line at a time. Do not skip ahead — the interesting part is not the total, it is which line is biggest.", {
  x: M, y: 4.05, w: CW, h: 0.6, fontSize: 14, color: C.MUTEDL, lineSpacing: 21 });
T.takeaway(p, s, "Open a shared spreadsheet on screen. When someone asks about their own volume and language, run it live. That moment is when the room decides you are worth listening to.");
T.foot(s, ...FT);
s.addNotes("No slides for the derivation itself — do it on a live spreadsheet. This deck is your safety net and your post-session handout.");

/* 3 */ s = T.slideD(p, "Line by line", "The build-up");
T.table(p, s, { y: 1.7, headers: ["Line item", "Rate", "Quantity", "Cost"], colW: [4.6, 3.0, 2.4, 2.093],
  rows: [
    ["Speech to text — customer speaking", "₹30/hour = ₹0.00833/sec", "72 sec", "₹0.60"],
    ["Text to speech — agent speaking (Bulbul v3)", "₹30 / 10K chars", "1,620 chars", "₹4.86"],
    ["LLM input — cumulative context, 8 turns", "₹29.28 / 1M tokens", "~20,000 tok", "₹0.59"],
    ["LLM output — the agent's replies", "₹73.20 / 1M tokens", "~1,500 tok", "₹0.11"],
    ["Telephony — outbound, indicative", "~₹0.60 / minute", "3 min", "₹1.80"],
    ["TOTAL PER CALL", "", "", "₹7.96"],
  ], rowH: 0.44, size: 11 });
T.takeaway(p, s, "Now look again at line two. Text to speech is ₹4.86 of ₹7.96 — sixty-one percent of the bill.", { dark: true, y: 5.5, icon: "!" });

/* 4 */ s = T.slideL(p, "Where the money actually goes", "The reveal");
s.addChart(p.ChartType.bar, [{
  name: "Cost per call (₹)",
  labels: ["Text to speech", "Telephony", "LLM (in + out)", "Speech to text"],
  values: [4.86, 1.80, 0.70, 0.60],
}], {
  x: M, y: 1.68, w: 7.1, h: 3.95,
  barDir: "bar", showTitle: true, title: "₹7.96 per 3-minute call",
  titleFontSize: 13, titleColor: C.INK, titleFontFace: "Calibri",
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: '₹0.00',
  dataLabelColor: C.INK, dataLabelFontSize: 10,
  chartColors: [C.SAF], showLegend: false,
  catAxisLabelColor: C.MUTEDL, valAxisLabelColor: C.MUTEDL,
  catAxisLabelFontSize: 10, valAxisLabelFontSize: 9,
  valGridLine: { color: "E3E6EE", size: 1 }, catGridLine: { style: "none" },
  valAxisMaxVal: 6,
});
T.rows(p, s, [
  { icon: "1", title: "60% is the voice", body: "Not the AI. The synthesised speech is the single biggest line on the bill." },
  { icon: "2", title: "The LLM is 9%", body: "The component everyone optimises first is the one that barely moves the number.", color: C.TEAL },
  { icon: "3", title: "Telephony is 23%", body: "Bigger than your model cost. Choose your telco with the same care." },
], { x: 8.05, y: 1.9, rh: 1.25, w: 4.65, tSize: 13, bSize: 10.5 });
T.takeaway(p, s, "Every engineer in this room has spent a week choosing an LLM. Almost nobody has spent an hour choosing a TTS version. The arithmetic says that is backwards.");
T.foot(s, ...FT);

/* 5 */ s = T.slideL(p, "Three levers, in order of effect", "Sensitivities");
T.table(p, s, { y: 1.65, headers: ["Change", "Effect on the ₹7.96", "New total", "Verdict"],
  colW: [4.2, 3.6, 2.0, 2.293],
  rows: [
    ["Switch to Bulbul v2 (₹15 vs ₹30/10K)", "TTS ₹4.86 → ₹2.43", "₹5.53", "31% cut. One parameter"],
    ["Prompt-cache the system prompt", "Input cost drops ~62%", "₹7.67", "₹0.29 saved, free"],
    ["Both together", "", "₹5.24", "34% cut, no quality loss"],
    ["Add diarization you do not need", "+₹0.30 (₹45/hr vs ₹30/hr)", "₹8.26", "Pure waste at volume"],
    ["Shorten the agent's scripts by 20%", "TTS drops ₹0.97", "₹6.99", "Copywriting as cost control"],
  ], rowH: 0.42, size: 10.5 });
T.stats(p, s, [
  { value: "₹7.96", label: "naive implementation" },
  { value: "₹5.24", label: "after two free changes", color: C.TEAL },
  { value: "34%", label: "cut, with no change\nto agent quality", color: C.TEAL },
  { value: "₹2.72", label: "saved per call — at 100K calls\nthat is ₹2.72 lakh a month" },
], { y: 4.35, h: 1.85, vSize: 30 });
T.foot(s, ...FT);

/* 6 */ s = T.slideD(p, "The comparison that makes it a business", "vs. a human");
T.stats(p, s, [
  { value: "₹25–60", label: "a human agent per call,\nfully loaded", color: C.RED },
  { value: "₹5–8", label: "your cost per call", color: C.TEAL },
  { value: "₹15", label: "what you charge" },
  { value: "47%", label: "your gross margin", color: C.TEAL },
], { y: 1.8, h: 2.0, vSize: 34, dark: true });
T.txt(s, "At ₹15 you are 70% cheaper than what the customer pays today, and you keep 47% of what they pay you. The customer keeps the rest of the saving — which is exactly why the pilot is an easy yes.", {
  x: M, y: 4.1, w: CW, h: 0.85, fontSize: 14.5, color: C.MUTED, lineSpacing: 23 });
T.takeaway(p, s, "That gap is the entire business. Not the model. Not the accuracy. The arithmetic between what a human costs and what software costs.", { dark: true, y: 5.25, size: 14 });
s.addNotes("Say this line slowly and then stop talking for two seconds. It is the sentence people write down.");

/* 7 */ s = T.sectionSlide(p, { num: "B", title: "Build or buy?", subtitle: "Sarvam's own managed price is the benchmark — and it validates your model" });

/* 8 */ s = T.slideL(p, "Your build versus Samvaad", "The honest comparison");
T.compare(p, s,
  { icon: "B", title: "You assemble it — ₹1.14–2.05 / minute", color: C.SAF, items: [
    "Naive build (Bulbul v3, no caching): ₹2.05/min excl. telephony",
    "Optimised (v2 + prompt caching): ₹1.14/min excl. telephony",
    "You own: orchestration, state, retries, barge-in, observability",
    "You own: uptime, on-call, and every 3am failure",
    "Full control of vertical logic and workflow",
    "Engineering cost is real, recurring, and easy to under-count",
  ]},
  { icon: "S", title: "Samvaad — ₹3.50 / minute, GA", color: C.TEAL, items: [
    "Fully managed, generally available since Epoch",
    "CRM and banking integrations, conversation memory",
    "Voice, WhatsApp and web channels",
    "Enterprise compliance posture on day one",
    "~70% more than a naive build; ~3x an optimised one",
    "You own the workflow design, not the plumbing",
  ]},
  { y: 1.7, h: 3.5, size: 11.5 });
T.takeaway(p, s, "Verify what ₹3.50/min includes before quoting it — telephony may or may not be bundled. Either way the managed premium is large, and that premium is where a developer's business lives.");
T.foot(s, ...FT);
s.addNotes("This comparison is your most original material. Almost nobody teaching Sarvam is putting these two numbers side by side.");

/* 9 */ s = T.slideL(p, "So when do you actually build?", "Decision framework");
T.compare(p, s,
  { icon: "✓", title: "Build when", color: C.SAF, items: [
    "The workflow logic IS your product",
    "You are selling software, not using it",
    "Volume is high enough that 35% matters",
    "You need a deployment shape the platform does not offer",
    "The vertical rules are too specific to configure",
    "You have engineering capacity to own reliability",
  ]},
  { icon: "→", title: "Buy when", color: C.TEAL, items: [
    "Time to market beats unit cost",
    "You are the end user, not the vendor",
    "Volume does not justify the engineering",
    "The buyer wants a supported platform, not your code",
    "You need enterprise compliance from day one",
    "Your differentiation is elsewhere in the value chain",
  ]},
  { y: 1.7, h: 3.4, size: 11.5 });
T.rows(p, s, [
  { icon: "★", title: "The third option most people miss", body: "Build the vertical layer, buy the plumbing. Use Samvaad or Indus for the conversation, and put your value in the workflow, the integrations, the compliance rules and the dashboard the buyer actually wants." },
], { y: 5.25, rh: 1.0 });
T.foot(s, ...FT);

/* 10 */ s = T.slideL(p, "Documents — the other economics", "₹0.50 a page");
T.stats(p, s, [
  { value: "₹0.50", label: "your cost per page\n(was ₹1.50 until May 2026)", color: C.TEAL },
  { value: "₹3–8", label: "what a BPO charges\nper page today", color: C.RED },
  { value: "₹50,000", label: "your cost to process\n100,000 pages" },
  { value: "₹3–8 L", label: "what that customer\npays today" },
], { y: 1.78, h: 2.0, vSize: 30 });
T.bullets(p, s, [
  "A 3x price cut in May 2026 is not a pricing tweak — it is a signal. At ₹0.50 a page, categories of work that were economically impossible in India become viable overnight.",
  "Legacy Indic archives. Government form backfiles. Land records. Court documents. Insurance policy libraries. Hospital records. None of these were worth digitising at ₹8 a page.",
  "The constraint is not cost any more — it is the 10-page job limit and the 10 requests/minute cap. Your architecture is a queue, and that is a solvable engineering problem, not a business one.",
], { y: 4.1, size: 12.5 });
T.foot(s, ...FT);

/* 11 */ s = T.slideD(p, "The self-hosting crossover", "When to stop paying per call");
T.compare(p, s,
  { icon: "1", title: "Managed API", color: C.SAF, items: [
    "Pay per call — ₹30/hour of audio",
    "Zero infrastructure to run",
    "Scales instantly, no capacity planning",
    "Data transits Sarvam",
    "Best below the crossover volume",
  ]},
  { icon: "2", title: "Self-hosted — SageMaker", color: C.TEAL, items: [
    "Flat instance-hour cost, usage-independent",
    "Saaras v3, Bulbul v3, Sarvam Vision available",
    "Audio and documents never leave your VPC",
    "Network isolation for air-gapped deployments",
    "No licence key — AWS Marketplace handles entitlement",
  ]},
  { y: 1.7, h: 2.9, size: 11.5, dark: true });
T.rows(p, s, [
  { icon: "₹", title: "Work out your own crossover — this is the number that wins bank deals", body: "At ₹30/hour for STT, how many audio-hours a month justify a permanently-running GPU endpoint? Compute it for your volume. Then you can tell a CISO exactly when their data stops leaving the building AND gets cheaper." },
  { icon: "★", title: "Deploy via console, boto3 or Terraform", body: "Subscribe on AWS Marketplace, copy the model package ARN, create a real-time, async or batch endpoint. There is no licence proxy to run." },
], { y: 4.75, rh: 1.0, dark: true });

/* 12 */ s = T.slideL(p, "The complete price list", "Reference · August 2026");
T.table(p, s, { y: 1.6, headers: ["Service", "Price", "Unit", "Notes"], colW: [3.6, 3.0, 2.6, 2.893],
  rows: [
    ["Sarvam-105B", "₹29.28 / ₹10.98 / ₹73.20", "per 1M tokens", "in / cached in / out"],
    ["Gemma-4 31B", "₹36.60 / ₹13.73 / ₹91.50", "per 1M tokens", "third-party"],
    ["GLM 5.2", "₹128.10 / ₹23.79 / ₹402.60", "per 1M tokens", "4.4x the input cost"],
    ["Speech to Text", "₹30", "per hour", "billed per second"],
    ["STT + diarization", "₹45", "per hour", "only when needed"],
    ["STT + translate", "₹30", "per hour", "same as transcribe"],
    ["Sarvam Translate / Mayura", "₹20", "per 10K chars", ""],
    ["Transliterate", "₹20", "per 10K chars", ""],
    ["Language Identification", "₹3.50", "per 10K chars", "cheap enough for everything"],
    ["Bulbul v2 TTS", "₹15", "per 10K chars", "the margin choice"],
    ["Bulbul v3 TTS", "₹30", "per 10K chars", "beta pricing"],
    ["Document Digitisation", "₹0.50", "per page", "max 10 pages/job"],
    ["Samvaad (managed voice)", "₹3.50", "per minute", "GA since Epoch"],
  ], rowH: 0.28, size: 9.5 });
T.takeaway(p, s, "Rate limits: Starter 60 req/min · Pro 200 · Business 1,000 · Enterprise custom. Document AI is 10 req/min on every plan. New accounts get ₹1000 free.");
T.foot(s, ...FT);

/* 13 */ s = T.sectionSlide(p, { num: "C", title: "What you charge", subtitle: "Never price cost-plus when the alternative is a human" });

/* 14 */ s = T.slideL(p, "Five pricing models and their traps", "Packaging");
T.table(p, s, { y: 1.65, headers: ["Model", "Fits", "The trap"], colW: [3.0, 4.5, 4.593],
  rows: [
    ["Per-minute / per-call", "Voice agents", "Your cost is also per-minute — margin is thin and volume-dependent"],
    ["Per-page / per-document", "Document pipelines", "Easy for the buyer to benchmark against BPO rates. Race to the bottom"],
    ["Per-seat SaaS", "Internal tools, dashboards", "Decouples revenue from API cost — the best margin structure available to you"],
    ["Outcome-based", "Collections, lead-gen", "Highest price capture, highest risk. Needs attribution you can actually prove"],
    ["Platform + implementation", "Enterprise, on-prem", "Where the real money is in Indian enterprise. Services fund the product"],
  ], rowH: 0.55, size: 10.5 });
T.takeaway(p, s, "The rule: price against the incumbent cost — ₹25–60 a call, ₹3–8 a page, ₹25–40K a month per agent. Hold 50–70% gross margin. Let the customer keep the rest of the saving.");
T.foot(s, ...FT);

/* 15 */ s = T.analogy(p, { kicker: "Why cost-plus pricing loses", symbol: "₹", symSize: 96,
  title: "The tailor who charged for thread",
  story: "A tailor works out that a shirt costs him ₹40 in cloth, ₹5 in thread and two hours of labour. He adds 30% and charges ₹180.\n\nAcross the road, a shop sells the same shirt for ₹900.\n\nThe tailor is not cheaper because he is generous. He is cheaper because he priced from his costs instead of from the customer's alternative.\n\nHe will work twice as hard for a fifth of the money, forever.",
  punch: "Your customer's alternative is not your API bill. It is ₹40 a call to a human, or ₹6 a page to a BPO. Price from there, keep half, and let them keep the rest. Everyone is better off — including you." });

/* 16 */ s = T.slideL(p, "Where the opportunity actually is", "The map");
T.cards(p, s, [
  { icon: "1", title: "Vertical depth", body: "Sarvam sells a voice agent platform. You sell 'collections for NBFCs with a ₹5–50 crore book' — with the dialer, RBI recovery rules, compliance scripts and the dashboard a credit head actually wants." },
  { icon: "2", title: "SMB and mid-market", body: "Companies too small for a forward-deployed engineering team, who still need Hindi voice support. Nobody is serving them well." },
  { icon: "3", title: "Workflow-adjacent", body: "The CRM plugin. The WhatsApp layer. The Tally integration. The school-ERP module. Small surfaces, deeply embedded, hard to displace.", color: C.TEAL },
  { icon: "4", title: "Regulated on-premise", body: "Smaller banks and hospitals needing air-gapped deployment. Package the SageMaker self-hosted models as an appliance with your workflow on top.", color: C.TEAL },
  { icon: "5", title: "Archive and data services", body: "Indic document backfiles at ₹0.50 a page input cost. Land records, court files, insurance libraries, hospital archives." },
  { icon: "6", title: "Tooling and enablement", body: "Everything around the stack: evals, observability, migration, training. Small markets, but early and uncrowded." },
], { cols: 3, y: 1.68, h: 1.9 });
T.takeaway(p, s, "Sarvam sells platforms to large enterprises with forward-deployed teams. That is not a gap in their strategy — it is the shape of every platform market that has ever existed.");
T.foot(s, ...FT);

/* 17 */ s = T.slideD(p, "Do this before you leave", "Your own numbers");
T.rows(p, s, [
  { icon: "1", title: "Pick one workflow in your own domain", body: "A call, a document, a conversation. Something specific enough to count." },
  { icon: "2", title: "Cost one transaction, using today's rates", body: "STT seconds · TTS characters · LLM tokens · telephony minutes · pages. Use the cost.py helper from the lab." },
  { icon: "3", title: "Find out what the incumbent costs", body: "What does the customer pay for this today — in salaries, BPO fees, or lost time? This is the number that matters.", color: C.TEAL },
  { icon: "4", title: "Price at 50–70% margin, well under the incumbent", body: "If those two constraints cannot both hold, you have found out something important very cheaply.", color: C.TEAL },
], { y: 1.75, rh: 1.02, dark: true, bSize: 10.5 });
T.takeaway(p, s, "Type your one-line answer in chat: 'I help [buyer] do [job] in [language], replacing [incumbent cost].' The best answers become the examples I use next.", { dark: true, y: 6.15 });

/* 18 */ T.quoteSlide(p, { quote: "The gap between what a human costs\nand what software costs\nis the entire business.",
  by: "— End of Segment 07. Next: what you can and cannot build." });

p.writeFile({ fileName: "07_Unit_Economics_and_Business.pptx" }).then(f => console.log("OK", f));
