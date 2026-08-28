const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW } = T;
const p = new P(); p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "Indus and the Agentic Platform";
const FT = ["AIVidhya4Sarvam · Building with Sarvam", "05 · Indus & Agents"];
let s;

/* 1 */ T.titleSlide(p, { eyebrow: "Segment 05 · Hands-on", title: "Indus and the\nagentic platform",
  subtitle: "From APIs you assemble to agents you deploy",
  meta: "indus.sarvam.ai · six tools · work, voice, content, doc, coding agents + inference" });

/* 2 */ s = T.slideL(p, "What actually makes something 'agentic'", "Definitions");
T.compare(p, s,
  { icon: "1", title: "A chatbot", color: C.MUTEDL, items: [
    "Answers a question",
    "Stateless, or state you manage yourself",
    "One turn in, one turn out",
    "Cannot act on the world",
    "Failure = a bad answer",
    "You evaluate it on response quality",
  ]},
  { icon: "2", title: "An agent", color: C.SAF, items: [
    "Completes a task",
    "Holds state across many steps, sometimes days",
    "Decides which tools to call, and in what order",
    "Takes actions — writes to a CRM, raises a ticket, moves money",
    "Failure = a wrong action, which may be irreversible",
    "You evaluate it on task success, tool accuracy and recovery",
  ]},
  { y: 1.7, h: 3.5, size: 11.5 });
T.takeaway(p, s, "The moment an LLM can take an action, the engineering problem stops being prompt quality and becomes reliability, observability and blast radius.");
T.foot(s, ...FT);

/* 3 */ s = T.slideD(p, "Indus — one platform, six tools", "Hands-on");
T.cards(p, s, [
  { icon: "W", title: "Work agents", body: "Multi-step business workflows. The general-purpose surface — compliance review, onboarding, internal ops." },
  { icon: "V", title: "Voice agents", body: "Conversational systems over telephony and web. The Samvaad capability, exposed as a building block." },
  { icon: "C", title: "Content agents", body: "Generation, transformation and localisation of content at scale across Indian languages.", color: C.TEAL },
  { icon: "D", title: "Doc agents", body: "Document ingestion, digitisation, extraction and downstream routing. Vision 1.5 with a workflow around it.", color: C.TEAL },
  { icon: "K", title: "Coding agents", body: "Sarvam Code — writing and understanding code. Beta." },
  { icon: "I", title: "Inference stack", body: "Sarvam Inference — India-hosted serving for 105B and frontier open models, underneath all of it.", color: C.TEAL },
], { cols: 3, y: 1.68, h: 1.9, dark: true });
T.takeaway(p, s, "Create your account at indus.sarvam.ai now if you have not. We are going to run a real task through it together in the next ten minutes.", { dark: true, y: 5.8 });
s.addNotes("Have a screen recording ready as fallback. Never debug someone else's SaaS live in front of 100 people.");

/* 4 */ s = T.slideL(p, "What we are doing, together, right now", "The exercise");
T.flow(p, s, [
  { t: "Pick a document", d: "your own, or the sample" },
  { t: "Point an agent at it", d: "doc agent, no code" },
  { t: "Watch it reason", d: "step by step, visible" },
  { t: "Inspect the trace", d: "what did it see, why" },
  { t: "Ask: what would this cost?", d: "if you built it yourself" },
], { y: 2.1, h: 1.7 });
T.rows(p, s, [
  { icon: "★", title: "Narrate the layers underneath as it runs", body: "That is Vision doing extraction. That is 105B doing the reasoning. That is a tool call. Everything on this screen, you could assemble yourself from the APIs we ran in the last segment." },
  { icon: "?", title: "Which raises the actual question of the day", body: "You could build this. Sometimes you should. Sometimes you absolutely should not. We settle that with arithmetic in the next segment." },
], { y: 4.15, rh: 1.05 });
T.foot(s, ...FT);

/* 5 */ s = T.sectionSlide(p, { num: "B", title: "The anatomy of a production agent", subtitle: "The checklist an enterprise buyer will hold you to" });

/* 6 */ s = T.slideL(p, "Seven things that separate a demo from a product", "Agent architecture");
T.rows(p, s, [
  { icon: "1", title: "Tools", body: "Scoped, typed, individually permissioned. The agent should reach only what that task needs — not your whole database." },
  { icon: "2", title: "State", body: "Where is the conversation, the task, the partial result? Held explicitly, not implicitly in a growing context window." },
  { icon: "3", title: "Memory", body: "What persists across sessions? Structured feedback loops mean agents learn from corrections rather than repeating them.", color: C.TEAL },
  { icon: "4", title: "Checkpointing", body: "A failure at step 40 must not lose the first 39. This is the single biggest reliability difference at scale.", color: C.TEAL },
  { icon: "5", title: "Recovery", body: "Resume from the last good step, not from zero. Instant, automatic, and tested before you need it." },
  { icon: "6", title: "Observability", body: "Every reasoning step, tool call and decision logged and inspectable. Replay any step with different inputs." },
  { icon: "7", title: "Audit trail", body: "Who did what, when, and on what evidence. Not a nice-to-have in BFSI or government — a procurement requirement.", color: C.TEAL },
], { y: 1.58, rh: 0.6, tSize: 12.5, bSize: 9.5, badge: 0.44, iSize: 12 });
T.takeaway(p, s, "Arya is built around exactly this list. You are not learning their product — you are learning the questions a CISO will ask you in month three.", { y: 6.0, h: 0.78 });
T.foot(s, ...FT);

/* 7 */ s = T.slideD(p, "The design law worth writing on your wall", "LLMs reason, code executes");
T.compare(p, s,
  { icon: "✕", title: "The expensive way", color: C.RED, items: [
    "Ask the model to compute the EMI",
    "Ask the model to sort 200 records",
    "Ask the model to validate a PAN format",
    "Ask the model to add up an invoice",
    "Non-deterministic, expensive, occasionally wrong",
    "Costs scale with every token of data you paste in",
  ]},
  { icon: "✓", title: "The right way", color: C.TEAL, items: [
    "Model decides WHICH calculation is needed",
    "Code performs it, deterministically",
    "Model interprets the result and decides what next",
    "Deterministic, auditable, free at the point of execution",
    "Arya reports 114% better on complex tasks — with smaller, cheaper models",
    "Push everything deterministic out of the model",
  ]},
  { y: 1.75, h: 3.6, size: 11.5, dark: true });
T.takeaway(p, s, "This is not a Sarvam-specific trick. It is the general law of agent design, and it is where most of the cost and most of the errors go away at once.", { dark: true, y: 5.6 });

/* 8 */ s = T.slideL(p, "MCP — connect your tools without exposing them", "Integration");
T.code(p, s, { y: 1.62, h: 1.85, label: "ONE-TIME CONFIG — CLAUDE DESKTOP, CLAUDE CODE, CURSOR, WINDSURF, ZED",
  code: `{\n  "mcpServers": {\n    "sarvam": {\n      "command": "uvx", "args": ["sarvam-mcp"],\n      "env": { "SARVAM_API_KEY": "<YOUR_KEY>" }\n    }\n  }\n}` });
T.table(p, s, { y: 3.65, headers: ["Tool", "What it does", "Default model"], colW: [3.9, 5.0, 3.193],
  rows: [
    ["sarvam_stt_transcribe", "Audio file → transcript, five modes", "saaras:v3"],
    ["sarvam_tts_speak / _stream", "Text → audio file or stream", "bulbul:v3"],
    ["sarvam_translate", "Cross-language translation", "mayura:v1"],
    ["sarvam_transliterate", "Script conversion", "—"],
    ["sarvam_identify_language", "Language + script detection", "—"],
    ["sarvam_llm_complete", "Chat completions", "sarvam-105b"],
    ["sarvam_vision_extract / _job_status", "Document intelligence", "Sarvam Vision"],
    ["sarvam_pronunciation_*", "Create, list, get, delete dictionaries", "—"],
  ], rowH: 0.3, size: 10 });
T.takeaway(p, s, "Two namespaces: sarvam_tools_* to actually call the APIs, sarvam_code_* for docs, endpoint shapes and starter projects while you build.");
T.foot(s, ...FT);

/* 9 */ s = T.sectionSlide(p, { num: "C", title: "Evals", subtitle: "The module every workshop skips and every deployment needs" });

/* 10 */ s = T.slideL(p, "The buyer's second question", "Why evals decide deals");
T.rows(p, s, [
  { icon: "1", title: "\"Does it work?\"", body: "You demo it. It works. Everyone is pleased. This part is easy and it is not what closes the deal." },
  { icon: "2", title: "\"How do you know it still works next month?\"", body: "This is the question that separates a pilot from a contract — and a documented eval harness is the only real answer to it.", color: C.SAF },
], { y: 1.7, rh: 1.05 });
T.cards(p, s, [
  { icon: "★", title: "Build the golden set from real data", body: "30 cases from actual transcripts, not invented ones. Ten is enough to start. Real data surfaces failures your imagination will not." },
  { icon: "✓", title: "Score what matters", body: "Task success · tool-call accuracy · language correctness · hallucination rate · latency p50 and p95 · cost per task." },
  { icon: "⟳", title: "Run it on every prompt change", body: "A prompt edit is a code change. It needs the same regression discipline. seed= makes results repeatable." },
  { icon: "§", title: "Guardrails belong here too", body: "PII redaction before logging · refusal boundaries · human-in-the-loop escalation thresholds · full recording for compliance.", color: C.TEAL },
], { cols: 4, y: 4.0, h: 2.0, bSize: 10.5 });
T.foot(s, ...FT);

/* 11 */ s = T.slideD(p, "A minimal eval harness", "Ten cases is enough to start");
T.code(p, s, { y: 1.6, h: 4.3, label: "PYTHON — run this on every prompt change",
  code: `CASES = [\n    {"audio": "hi_emi_query.wav", "expect_tool": "get_emi_schedule",\n     "expect_lang": "hi-IN", "must_contain": ["EMI"]},\n    # ... 9 more from REAL transcripts\n]\n\ndef run_evals():\n    results = []\n    for c in CASES:\n        out = agent(c["audio"], seed=42)          # seed = repeatable\n        results.append({\n            "tool_ok":  out.tool_called == c["expect_tool"],\n            "lang_ok":  out.language   == c["expect_lang"],\n            "content_ok": all(k in out.text for k in c["must_contain"]),\n            "latency_ms": out.latency,\n            "cost_inr":   out.cost,\n        })\n    return summarise(results)   # print pass rate, p95 latency, mean ₹/task`, size: 10 });
T.takeaway(p, s, "Now break one prompt deliberately and watch the harness catch it. That thirty seconds is what convinces a room that evals are not bureaucracy.", { dark: true, y: 6.15 });

/* 12 */ s = T.analogy(p, { kicker: "Why checkpointing matters", symbol: "40", symSize: 76,
  title: "The wedding cook who lost the biryani at step 39",
  story: "Forty steps. Soak, marinate, fry, layer, seal, dum.\n\nAt step 39 the gas ran out.\n\nThe question is not whether the gas will run out. It will. The question is whether you start again from the rice, or relight the stove and continue.\n\nA cook who has to restart from step 1 every time something goes wrong cannot cater a wedding. He can only cook for four people.",
  punch: "Checkpointing is the difference between an agent that demos well for four steps and one that runs a fifty-step compliance review across an enterprise. Design for the gas running out." });

/* 13 */ s = T.slideL(p, "Where you would actually deploy an agent", "The workflows with budget");
T.cards(p, s, [
  { icon: "1", title: "Compliance & risk review", body: "Insurance. Review a policy document against IRDAI guidelines, flag deviations, cite the clause." },
  { icon: "2", title: "Customer onboarding", body: "Fintech. KYC document extraction, validation, eligibility check, routing or escalation." },
  { icon: "3", title: "Loan application processing", body: "BFSI. Multi-document triage, field validation, credit-policy check, decision or human escalation.", color: C.TEAL },
  { icon: "4", title: "Contract review & redlining", body: "Legal. Clause extraction, deviation from standard terms, suggested redlines with rationale.", color: C.TEAL },
  { icon: "5", title: "Scheme eligibility & enrolment", body: "Government. Citizen documents in 22 languages, eligibility rules, enrolment, status callback by voice." },
  { icon: "6", title: "Patient record processing", body: "Healthcare. Handwritten and typed records, structured extraction, residency-compliant deployment." },
  { icon: "7", title: "Candidate screening", body: "HR. Resume parsing at volume, structured scoring against a rubric, shortlist with reasoning.", color: C.TEAL },
  { icon: "8", title: "Supply chain monitoring", body: "Manufacturing. Document and message ingestion, exception detection, alerting with context.", color: C.TEAL },
], { cols: 4, y: 1.68, h: 1.85, bSize: 10 });
T.takeaway(p, s, "Each of these is a vertical product, not a platform feature. That gap — between what a platform sells and what a specific buyer needs — is where a small team makes money.");
T.foot(s, ...FT);

/* 14 */ s = T.slideL(p, "Build it yourself, or deploy on a platform?", "The honest framework");
T.compare(p, s,
  { icon: "B", title: "Build on the raw APIs when", color: C.SAF, items: [
    "The workflow logic is your actual differentiator",
    "You need margin at high volume",
    "You need a deployment shape the platform does not offer",
    "You are selling the software, not using it",
    "You have the engineering capacity to own reliability",
    "The vertical rules are too specific to configure",
  ]},
  { icon: "P", title: "Use Indus / Samvaad / Arya when", color: C.TEAL, items: [
    "Time to market matters more than unit cost",
    "You do not want to own state, retries and observability",
    "Volume does not justify the engineering",
    "You are the end user, not the vendor",
    "The buyer wants a supported platform, not your code",
    "You need enterprise compliance posture on day one",
  ]},
  { y: 1.7, h: 3.6, size: 11.5 });
T.takeaway(p, s, "Neither answer is always right. But you cannot choose without the numbers — which is exactly what the next segment gives you.");
T.foot(s, ...FT);

/* 15 */ T.quoteSlide(p, { quote: "Every agent decision, traceable.\nEvery step, recoverable.\nThat is not polish — it is the price of entry.",
  by: "— End of Segment 05. Next: Kivi, Sarvam Code, and the tooling." });

p.writeFile({ fileName: "05_Indus_and_Agentic_Platform.pptx" }).then(f => console.log("OK", f));
