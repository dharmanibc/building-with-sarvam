const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW, W } = T;

const p = new P();
p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "Opening — India's AI Sovereignty";

let s;

/* 1 */ s = T.titleSlide(p, {
  eyebrow: "Segment 01 · 15 August 2026",
  title: "Building with Sarvam\nfor India's AI Sovereignty",
  subtitle: "Why an Indian AI stack is a market, not a sentiment",
  meta: "Community-run session. Not affiliated with or endorsed by Sarvam AI.",
});
s.addNotes("Two minutes on the theme, said plainly, then move. The framing earns its place by being true, not by being repeated. Open with: '79 years ago today India became politically independent. Today most of the AI this country runs on is trained, hosted and governed somewhere else. That's not a grievance - it's a fact, and it's changing.'");

/* 2 */ s = T.sectionSlide(p, { num: "01", title: "The gap nobody is building for",
  subtitle: "Three numbers that explain why this stack exists" });

/* 3 */ s = T.slideL(p, "India speaks 22 languages. Its software speaks one.", "The problem");
T.stats(p, s, [
  { value: "~800M", label: "Indians who do not transact\ncomfortably in English" },
  { value: "22", label: "Constitutionally scheduled\nlanguages", color: C.TEAL },
  { value: "~10%", label: "of Indians speak English\nwith any fluency" },
  { value: "1", label: "language most Indian\nsoftware actually supports", color: C.RED },
], { y: 1.9, h: 2.1, vSize: 40 });
T.txt(s, "Every product decision made in English is a decision to serve the top decile. That has been the default for thirty years — not from malice, but because the infrastructure to do otherwise did not exist at a price anyone could afford.", {
  x: M, y: 4.35, w: CW, h: 1.1, fontSize: 14, color: C.MUTEDL, lineSpacing: 22,
});
T.takeaway(p, s, "The gap is no longer capability. The models exist. The gap is that most Indian developers don't know what they cost or what they make possible.");
T.foot(s, "AIVidhya4Sarvam · Building with Sarvam", "01 · Opening");
s.addNotes("Don't rush these numbers. Ask the room: how many of you have built something your own parents could use in their first language? Usually near-zero hands. That silence is the whole session.");

/* 4 */ s = T.analogy(p, {
  kicker: "A short story",
  symbol: "₹",
  symSize: 96,
  title: "The ATM that only spoke English",
  story: "For twenty years, an Indian bank's ATM greeted every customer in English. In a district where 8% of people read English.\n\nThe bank's fix was not technology. It was hiring a person to stand next to the machine and translate.\n\nThat person cost ₹18,000 a month. Per ATM.\n\nThey were not solving a language problem. They were paying, in salaries, the price of software that did not exist yet.",
  punch: "Today that software costs ₹30 an hour of audio. The interpreter cost ₹18,000 a month. That difference is not a technical story — it is a business one, and it is the reason you are in this room.",
});
s.addNotes("This lands better if you tell it conversationally rather than reading it. The point: vernacular access was always a solved problem — solved expensively, with human labour. AI makes it cheap. Cheap changes what is buildable.");

/* 5 */ s = T.slideL(p, "Sovereignty is a commercial fact, not a slogan", "Why it matters to you");
T.cards(p, s, [
  { icon: "§", title: "DPDP Act", body: "India's data protection law creates real constraints on where personal data can be processed and stored. Compliance is not optional for regulated buyers." },
  { icon: "₹", title: "RBI localisation", body: "Payment system data must be stored in India. Banks and NBFCs cannot casually route customer audio through an offshore API." },
  { icon: "■", title: "Government procurement", body: "Public-sector tenders increasingly require India-domiciled processing. GeM listings and empanelment favour local stacks." },
  { icon: "✕", title: "Sector rules", body: "Healthcare, insurance and defence workloads carry residency requirements that rule out most global providers outright.", color: C.TEAL },
  { icon: "⚡", title: "Latency", body: "An endpoint in Mumbai beats one in Virginia by 200ms+. For a real-time voice agent, that is the difference between natural and broken.", color: C.TEAL },
  { icon: "✓", title: "Currency", body: "Priced and billed in rupees, with GST invoices. Sounds boring. It removes a procurement objection that kills deals.", color: C.TEAL },
], { cols: 3, y: 1.68, h: 1.88 });
T.takeaway(p, s, "A CISO's constraint list is a developer's opportunity list. Everything a bank cannot legally do with an offshore API is a market someone has to serve.");
T.foot(s, "AIVidhya4Sarvam · Building with Sarvam", "01 · Opening");
s.addNotes("This is the slide that reframes the whole day for the sceptics. Sovereignty sounds like flag-waving until you show it as procurement policy. Then it's a moat.");

/* 6 */ s = T.slideD(p, "The budget already exists", "Proof of market");
T.txt(s, "Organisations running Sarvam's stack in production today", { x: M, y: 1.6, w: CW, h: 0.35, fontSize: 13, color: C.MUTED });
const logos = ["Aadhaar", "Axis Bank", "CRED", "Decentro", "IDFC", "IndiaMART", "Infosys", "LIC", "Mahindra Finance", "NABARD", "SBI Life", "Skill India", "Tata Capital", "Urban Company", "CRED Resolve"];
logos.forEach((L, i) => {
  const cols = 5, gap = 0.24, cw = (CW - gap * (cols - 1)) / cols;
  const r = Math.floor(i / cols), c = i % cols;
  const x = M + c * (cw + gap), y = 2.1 + r * 0.85;
  s.addShape(p.ShapeType.roundRect, { x, y, w: cw, h: 0.68, rectRadius: 0.06, fill: { color: C.INK2 }, line: { color: C.INK3, width: 1 } });
  T.txt(s, L, { x: x + 0.1, y: y + 0.2, w: cw - 0.2, h: 0.3, fontSize: 12, bold: true, color: C.WHITE, align: "center" });
});
T.takeaway(p, s, "These are not pilots. This is BFSI, government and enterprise paying for Indic AI at population scale — which means the question is no longer whether there is a market.", { dark: true, y: 5.35 });
s.addNotes("Read three or four of these out loud. LIC. NABARD. Aadhaar. The room understands instantly that this is not a hobby stack.");

/* 7 */ s = T.slideL(p, "Sarvam at population scale, today", "The numbers");
T.stats(p, s, [
  { value: "2M+", label: "voice conversations\nper day" },
  { value: "35M", label: "pages digitised", color: C.TEAL },
  { value: "~1 crore", label: "API calls a day\non their own models" },
  { value: "<100ms", label: "median latency,\n99.9% uptime SLA", color: C.TEAL },
], { y: 1.85, h: 2.0, vSize: 34 });
T.rows(p, s, [
  { icon: "◆", title: "Built and operated entirely in India", body: "Sovereign compute, India-domiciled inference, no offshore dependency in the serving path." },
  { icon: "✓", title: "Open weights on the flagship models", body: "Sarvam-30B and Sarvam-105B released under Apache 2.0 — you are not locked to the API.", color: C.TEAL },
  { icon: "★", title: "SOC 2 Type II · ISO 27001 · DPDP compliant", body: "The compliance posture you inherit when you build on it — and can put in your own security questionnaire." },
], { y: 4.1, rh: 0.83 });
T.foot(s, "AIVidhya4Sarvam · Building with Sarvam", "01 · Opening");
s.addNotes("The open-weights point matters more than people realise. It's the answer to 'what if they raise prices' — you can self-host. Architect for portability from day one.");

/* 8 */ s = T.sectionSlide(p, { num: "02", title: "What we are doing for the next three hours",
  subtitle: "You will have your editor open the whole time" });

/* 9 */ s = T.slideL(p, "The session, end to end", "Agenda");
T.table(p, s, {
  y: 1.65,
  headers: ["Time", "Segment", "What you do"],
  colW: [1.5, 4.4, 6.193],
  rows: [
    ["4:00", "Independence Day & the sovereignty thesis", "Listen, argue, ask"],
    ["4:15", "The complete Sarvam stack after Epoch", "Map the territory"],
    ["4:35", "LAB — the sampler script", "Run code against every live API"],
    ["5:05", "Break", "Stretch"],
    ["5:15", "Indus — the six-tool agentic platform", "Hands-on, real task"],
    ["5:45", "Kivi + Sarvam Code", "Watch, then try at home"],
    ["6:05", "The money segment — unit economics", "Derive costs live with me"],
    ["6:30", "What you can and cannot build today", "The honest map"],
    ["6:50", "What's next, and Q&A", "Ask anything"],
  ],
  rowH: 0.36,
});
T.takeaway(p, s, "One rule for the whole session: every segment ends with a number in rupees. If we cannot cost it, we have not understood it.");
T.foot(s, "AIVidhya4Sarvam · Building with Sarvam", "01 · Opening");

/* 10 */ s = T.slideL(p, "What you will walk out with", "Outcomes");
T.cards(p, s, [
  { icon: "▶", title: "Working code", body: "A script that touches every live Sarvam API and prints what each call cost you, in ₹. Yours to keep and extend." },
  { icon: "♪", title: "Your own language, spoken", body: "Audio you generated yourself — Hindi, Tamil, Bengali, Marathi, Odia, whichever is yours." },
  { icon: "◆", title: "A map of the stack", body: "What exists, what shipped at Epoch, what is announced but not yet callable, and which model to reach for when." },
  { icon: "₹", title: "Unit economics", body: "What an AI voice call costs, why 60% of it is not the AI, and when to build versus buy." },
  { icon: "!", title: "The gotchas list", body: "The silent failures that cost people days — wrong parameters that return HTTP 200 and the wrong answer." },
  { icon: "★", title: "A view of the opportunity", body: "Where the platform companies are not competing, and what that leaves open for a small team." },
], { cols: 3, y: 1.68, h: 1.88 });
T.takeaway(p, s, "Three hours is a map, not a hike. You will not master this today — you will know exactly where to walk next.");
T.foot(s, "AIVidhya4Sarvam · Building with Sarvam", "01 · Opening");

/* 11 */ s = T.slideD(p, "Before we write a line of code", "Setup check");
T.rows(p, s, [
  { icon: "1", title: "Sarvam API key — indus.sarvam.ai", body: "New accounts get ₹1000 free credit. Today's entire session costs about ₹5 of it. If you don't have a key, get one now — it takes three minutes.", color: C.SAF },
  { icon: "2", title: "pip install sarvamai", body: "Python 3.11 or newer. There is a JavaScript/TypeScript SDK too — npm install sarvamai — if that's your world.", color: C.SAF },
  { icon: "3", title: "An Indus account — indus.sarvam.ai", body: "We go hands-on with it at 5:15. Create it now so you're not doing signup while I'm talking.", color: C.TEAL },
  { icon: "4", title: "Optional — Kivi, the desktop voice tool", body: "For the 5:45 demo. You can also just watch and install it tonight.", color: C.TEAL },
], { y: 1.75, rh: 1.05, dark: true });
T.takeaway(p, s, "Type OK in chat when your key works. If something is broken, say so now — not at 4:35 when everyone else is running code.", { dark: true, y: 6.0, icon: "!" });
s.addNotes("Poll the room. Anyone red goes to a breakout with a table captain for ten minutes while you start the next segment. Do not hold 38 people for 2.");

/* 12 */ s = T.slideL(p, "Who is in the room?", "Quick poll");
T.compare(p, s,
  { icon: "▶", title: "By background", color: C.SAF, items: [
    "Working developers — building something now",
    "Students — CS, IT, AI/ML",
    "Founders and technical PMs",
    "Researchers and academics",
    "Curious, not currently coding",
  ]},
  { icon: "★", title: "By intent", color: C.TEAL, items: [
    "I want to build a product on this",
    "I want to use it at work",
    "I want to understand the Indian AI market",
    "I want to teach or write about it",
    "I want to know if there is a business here",
  ]},
  { y: 1.7, h: 3.6 });
T.takeaway(p, s, "Answer in chat. It changes how I pitch the next three hours — and the best answers become examples I use later today.");
T.foot(s, "AIVidhya4Sarvam · Building with Sarvam", "01 · Opening");

/* 13 */ s = T.quoteSlide(p, {
  quote: "The model is not the moat.\nThe workflow, the distribution and the cost structure are.",
  by: "— The one line to remember from today",
});
s.addNotes("Say this now, and say it again at 6:50. Bookending it is what makes it stick. Everything in between is evidence for this claim.");

p.writeFile({ fileName: "01_Opening_India_AI_Sovereignty.pptx" }).then(f => console.log("OK", f));
