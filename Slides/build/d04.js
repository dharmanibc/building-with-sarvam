const P = require("pptxgenjs");
const T = require("./theme");
const { C, M, CW } = T;
const p = new P(); p.layout = "LAYOUT_WIDE";
p.author = "Dr. Bhaveshkumar C. Dharmani"; p.company = "AIVidhya4Sarvam";
p.title = "Sarvam-105B and Document AI";
const FT = ["AIVidhya4Sarvam · Building with Sarvam", "04 · LLM & Documents"];
let s;

/* 1 */ T.titleSlide(p, { eyebrow: "Segment 04", title: "Sarvam-105B\nand Document AI",
  subtitle: "Reasoning, tool calling, and turning Indic paper into structured data",
  meta: "Chat Completions · reasoning_effort · tool use · Vision 1.5 · digitise & extract" });

/* 2 */ s = T.sectionSlide(p, { num: "A", title: "Sarvam-105B", subtitle: "The ninety seconds that reframes the whole platform" });

/* 3 */ s = T.slideD(p, "Your existing code already works", "The base-URL swap");
T.code(p, s, { y: 1.6, h: 2.2, label: "OPENAI SDK — POINTED AT SARVAM. NOTHING ELSE CHANGES.",
  code: `from openai import OpenAI\n\nclient = OpenAI(\n    api_key="YOUR_SARVAM_KEY",\n    base_url="https://api.sarvam.ai/v1",   # <- the only change\n)\n\nr = client.chat.completions.create(\n    model="sarvam-105b",\n    messages=[{"role": "user", "content": "GST का आर्थिक प्रभाव समझाइए"}],\n)` });
T.rows(p, s, [
  { icon: "✓", title: "LangChain, Vercel AI SDK, LlamaIndex, most agent frameworks", body: "All work through the OpenAI-compatible endpoint. Your existing scaffolding is not wasted." },
  { icon: "!", title: "But the native SDK breaks convention in one place", body: "With the sarvamai client it is client.chat.completions(...) — NOT .create(...). This trips up every AI coding assistant that has not read the Agent Skills.", color: C.RED },
], { y: 4.05, rh: 1.05, dark: true });
T.takeaway(p, s, "Ninety seconds, and the platform stops being 'another API to learn' and becomes 'a base URL'. Do this demo live, early, while attention is high.", { dark: true, y: 6.2 });

/* 4 */ s = T.slideL(p, "The architecture, briefly", "Sarvam-105B");
T.stats(p, s, [
  { value: "128", label: "sparse experts in the\nMixture-of-Experts transformer" },
  { value: "MLA", label: "Multi-head Latent Attention —\ncompressed KV for long context", color: C.TEAL },
  { value: "12T", label: "pre-training tokens: code, math,\nmultilingual, web" },
  { value: "128K", label: "context window\n(Sarvam-30B: 64K)", color: C.TEAL },
], { y: 1.75, h: 2.0, vSize: 32 });
T.bullets(p, s, [
  "Trained from scratch on IndiaAI Mission compute — not a fine-tune of someone else's base model. That distinction is what makes the sovereignty claim real rather than cosmetic.",
  "Released under Apache 2.0 alongside Sarvam-30B. You can download the weights and self-host. This is your insurance policy against pricing or terms changing.",
  "Powers Indus, Sarvam's own AI assistant — which is a useful signal about what the model is actually good at: long-horizon reasoning and agentic workflows.",
], { y: 4.1, size: 12.5 });
T.foot(s, ...FT);

/* 5 */ s = T.slideL(p, "The failure everyone hits in the first hour", "reasoning_effort");
T.code(p, s, { x: M, y: 1.65, w: 5.85, h: 2.5, label: "WHAT PEOPLE WRITE",
  code: `r = client.chat.completions(\n    model="sarvam-105b",\n    messages=[...],\n    max_tokens=200,\n)\n\nprint(r.choices[0].message.content)\n# None`, size: 10 });
T.code(p, s, { x: M + 6.24, y: 1.65, w: 5.85, h: 2.5, label: "WHY",
  code: `# reasoning is ON by default\n#   reasoning_effort="low"\n#\n# reasoning tokens count\n# AGAINST max_tokens.\n#\n# 200 tokens of budget,\n# all consumed thinking,\n# nothing left to say.`, size: 10 });
T.compare(p, s,
  { icon: "1", title: "Fix A — give it room", color: C.TEAL, items: ["max_tokens=2000", "Keeps the reasoning, which is usually what you want", "Plan ceilings: Starter 4096 / Pro 16384 / Business 128000"] },
  { icon: "2", title: "Fix B — turn reasoning off", color: C.SAF, items: ["reasoning_effort=None", "Faster and cheaper for simple extraction or classification", "Default temperature shifts 0.5 → 0.2 when reasoning is disabled"] },
  { y: 4.35, h: 1.85, size: 11 });
T.foot(s, ...FT);
s.addNotes("Trigger this deliberately on stage. Let the room sit with the None for a beat, then fix it two ways. Walking people into a bug and out of it is the best teaching moment of the session.");

/* 6 */ s = T.slideL(p, "Every parameter that matters", "Chat Completions reference");
T.table(p, s, { y: 1.6, headers: ["Parameter", "Range / default", "When you touch it"], colW: [2.9, 3.2, 5.993],
  rows: [
    ["model", "sarvam-105b", "The only current chat model. sarvam-m and sarvam-30b are deprecated — pass model= explicitly, always"],
    ["reasoning_effort", "low (default) / None", "None for classification and extraction. Low for anything multi-step"],
    ["temperature", "0–2. 0.5 reasoning on, 0.2 off", "0–0.3 for extraction, 0.7+ for generation"],
    ["max_tokens", "Starter 4096 / Pro 16K / Business 128K", "Must leave room past reasoning tokens"],
    ["top_p", "0–1", "Leave at 1 unless you know why"],
    ["stream", "true / false", "true for any user-facing interface"],
    ["seed", "integer", "Repeatable results. Essential for eval harnesses"],
    ["stop", "up to 4 sequences", "Structured output boundaries"],
    ["frequency_penalty", "-2 to 2", "Reduce repetition in long generation"],
    ["presence_penalty", "-2 to 2", "Encourage topic movement"],
    ["n", "1–128", "Multiple completions per request"],
  ], rowH: 0.3, size: 10 });
T.foot(s, ...FT);

/* 7 */ s = T.slideD(p, "Prompt caching is an architecture decision", "Cost");
T.stats(p, s, [
  { value: "₹29.28", label: "input, per 1M tokens" },
  { value: "₹10.98", label: "CACHED input, per 1M tokens", color: C.TEAL },
  { value: "62%", label: "saving on the stable\npart of your prompt", color: C.TEAL },
  { value: "₹73.20", label: "output, per 1M tokens" },
], { y: 1.8, h: 1.9, vSize: 30, dark: true });
T.code(p, s, { y: 4.0, h: 2.0, label: "STRUCTURE YOUR PROMPTS SO THE STABLE PART IS CACHEABLE",
  code: `messages = [\n  {"role": "system", "content": LONG_STABLE_INSTRUCTIONS + POLICY + EXAMPLES},  # cached\n  {"role": "user",   "content": this_turn_only},                                # not cached\n]\n# Put everything that does not change per request FIRST and keep it byte-identical.` });
T.takeaway(p, s, "On a voice agent with an 8-turn conversation this saves roughly ₹0.36 a call. At 100,000 calls a month that is ₹36,000. From prompt ordering.", { dark: true, y: 6.2, icon: "₹" });

/* 8 */ s = T.slideL(p, "Tool calling — the foundation of everything agentic", "Sarvam-105B");
T.code(p, s, { y: 1.62, h: 3.3, label: "PYTHON — a three-tool agent",
  code: `tools = [{\n  "type": "function",\n  "function": {\n    "name": "get_emi_schedule",\n    "description": "Fetch the EMI schedule for a loan account",\n    "parameters": {\n      "type": "object",\n      "properties": {"account_id": {"type": "string", "description": "Loan account number"}},\n      "required": ["account_id"],\n    },\n  },\n}]\n\nr = client.chat.completions(\n    model="sarvam-105b", messages=msgs, tools=tools, max_tokens=2000,\n)`, size: 10 });
T.rows(p, s, [
  { icon: "★", title: "Why the benchmarks matter here", body: "49.5 on BrowseComp and 68.3 on Tau2 — the highest among compared models. Those are the agentic scores, and they are the reason this model is worth building workflows on rather than just chatting with." },
], { y: 5.15, rh: 1.0 });
T.foot(s, ...FT);

/* 9 */ s = T.sectionSlide(p, { num: "B", title: "Document AI", subtitle: "Sarvam Vision 1.5 — the cheapest useful thing on the platform" });

/* 10 */ s = T.slideL(p, "Two endpoints, one job model", "Document AI");
T.compare(p, s,
  { icon: "D", title: "Digitise — the whole document", color: C.SAF, items: [
    "Full-document OCR",
    "Preserves layout and reading order",
    "Tables parsed into HTML or Markdown",
    "Output: html or md, PLUS per-page JSON always",
    "Download is a ZIP: primary file + metadata/page_NNN.json + manifest.json",
    "For: archival, search, RAG ingestion, faithful conversion",
    "POST /doc-ai/v1/job/digitise",
  ]},
  { icon: "E", title: "Extract — just the fields you define", color: C.TEAL, items: [
    "Schema-based key-value extraction",
    "You supply a JSON schema (or a saved config_id)",
    "Output: JSON, CSV or XLSX",
    "For: KYC, invoices, forms, structured capture",
    "POST /doc-ai/v1/job/extract",
    "Provide exactly one of schema OR config_id — both or neither returns 400",
    "",
  ]},
  { y: 1.7, h: 3.9, size: 11 });
T.takeaway(p, s, "The rule: do not digitise a whole document to pull three fields. Write a schema and let Extract do it. Cheaper, faster, and far more reliable.");
T.foot(s, ...FT);

/* 11 */ s = T.slideD(p, "The job lifecycle", "Document AI");
T.flow(p, s, [
  { t: "digitise() / extract()", d: "creates AND submits in one call" },
  { t: "poll get_status()", d: "with backoff, until terminal" },
  { t: "get_results()", d: "structured data" },
  { t: "get_download_url()", d: "output file" },
], { y: 1.75, h: 1.6, dark: true });
T.table(p, s, { y: 3.6, headers: ["State", "Meaning", "What you must do"], colW: [2.8, 4.0, 5.293],
  rows: [
    ["pending", "Created, queued", "Keep polling"],
    ["running", "Being processed", "Watch usage.pages_processed"],
    ["completed", "All pages succeeded", "Fetch results"],
    ["partially_completed", "Some pages succeeded, some failed", "TERMINAL. Handle it — most people don't, and silently lose pages"],
    ["failed", "All pages failed or job-level error", "Log and retry"],
    ["rejected", "Rejected before processing", "Validation or entitlement problem"],
  ], rowH: 0.34, size: 10.5 });
T.takeaway(p, s, "partially_completed is a terminal state, not a transient one. If your code only checks for 'completed' you will lose pages and never know.", { dark: true, y: 6.1, icon: "!" });

/* 12 */ s = T.slideL(p, "Writing a schema that actually works", "Extract");
T.code(p, s, { x: M, y: 1.62, w: 6.6, h: 4.55, label: "PYTHON",
  code: `schema = {\n  "type": "object",\n  "properties": {\n    "policy_number": {\n      "type": "string",\n      "description": "Insurance policy number,\n        top-right, format ABC-1234"},\n    "insured_name": {\n      "type": "string",\n      "description": "Name of the insured person"},\n    "sum_insured": {\n      "type": "number",\n      "description": "Total sum insured, in INR"},\n  },\n}\n\njob = client.doc_ai.extract(\n    file=[("policy.pdf", f, "application/pdf")],\n    schema=json.dumps(schema),  # STRING not dict\n    language="en-IN",\n    output_format="json",\n)`, size: 9.5, ls: 13 });
T.rows(p, s, [
  { icon: "1", title: "The description IS the prompt", body: "\"Insurance policy number, top-right, format ABC-1234\" beats \"policy number\" by a wide margin. Be specific about location and format." },
  { icon: "2", title: "Schema rules", body: "Root must be type object with non-empty properties. Every field needs a type and a non-empty description. Types: string, number, integer, boolean, object, array. Optional enum. Max nesting depth 4." },
  { icon: "3", title: "Pass it as a JSON string", body: "It is sent as a multipart form field. json.dumps() in Python, JSON.stringify() in JS. A dict raises AttributeError: 'dict' object has no attribute 'read'.", color: C.RED },
], { x: 7.42, y: 1.7, rh: 1.2, w: 5.29, tSize: 12.5, bSize: 10 });
T.foot(s, ...FT);

/* 13 */ s = T.slideL(p, "The naming gotchas — all six", "Document AI");
T.table(p, s, { y: 1.65, headers: ["You write", "What happens", "Correct"], colW: [3.6, 4.4, 4.093],
  rows: [
    ["language_code=\"hi-IN\"", "Silently ignored. No error", "language=\"hi-IN\""],
    ["output_format=\"markdown\"", "400 Bad Request", "output_format=\"md\""],
    ["schema={...} (a dict)", "AttributeError: 'dict' has no attribute 'read'", "schema=json.dumps({...})"],
    ["file=open(...)", "Type error", "file=[(name, handle, mimetype)] — an array"],
    ["getStatus({job_id}) in JS", "undefined fields", "getStatus(job_id) — positional, wire names not camelCase"],
    ["11-page PDF", "400 invalid_request_error", "Chunk to 10 pages maximum"],
  ], rowH: 0.42, size: 10.5 });
T.takeaway(p, s, "Document AI uses a different parameter vocabulary from STT, translate and LID. That inconsistency is exactly why the Agent Skills exist.");
T.foot(s, ...FT);

/* 14 */ s = T.slideD(p, "The limits that shape your architecture", "Document AI");
T.stats(p, s, [
  { value: "10", label: "pages per job\n(PDF or ZIP)", color: C.RED },
  { value: "200 MB", label: "maximum file size" },
  { value: "10/min", label: "requests per minute —\nON EVERY PLAN", color: C.RED },
  { value: "₹0.50", label: "per page\n(was ₹1.50 until May 2026)", color: C.TEAL },
], { y: 1.8, h: 1.95, vSize: 32, dark: true });
T.bullets(p, s, [
  "The 10 req/min cap is not a tier limit — Starter, Pro and Business all get it. Your architecture needs a queue, not a bigger plan.",
  "Thirty people in this room submitting simultaneously will hit it instantly. That is why we are running this lab in waves — and experiencing the constraint is the lesson.",
  "At ₹0.50 a page, digitising 100,000 pages of legacy Indic records costs ₹50,000. A BPO charges ₹3–8 a page. Sit with that gap for a moment.",
], { y: 4.15, dark: true, size: 12.5 });

/* 15 */ s = T.slideL(p, "Error handling you will actually need", "Document AI");
T.table(p, s, { y: 1.65, headers: ["Status", "Meaning", "What to do"], colW: [1.8, 5.0, 5.293],
  rows: [
    ["400", "Invalid request or schema, or over 10 pages", "Fix the payload. Chunk the document"],
    ["402 / 403", "Billing or entitlement", "Check credits. Not retryable"],
    ["404", "Job not found", "Check the job_id"],
    ["409", "Results requested before terminal state", "Poll get_status first"],
    ["413", "File too large", "Split it"],
    ["422", "Invalid format or corrupted file", "Validate before submitting"],
    ["429", "Rate or admission limit", "Exponential backoff with jitter"],
    ["503", "Billing unavailable", "Retry with backoff"],
  ], rowH: 0.34, size: 10.5 });
T.takeaway(p, s, "Build the retry logic before you need it. A pipeline that dies on one corrupted file in a batch of ten thousand is not a pipeline.");
T.foot(s, ...FT);

/* 16 */ s = T.analogy(p, { kicker: "Why Extract beats Digitise", symbol: "E", symSize: 88,
  title: "The man who read the whole newspaper for the cricket score",
  story: "Every morning he read all forty pages, front to back, to find one number.\n\nIt took an hour. It was thorough. It was correct.\n\nHis neighbour turned to page 14, read the score, and made tea.\n\nBoth men got the same number. One of them got an hour back.",
  punch: "Digitise reads the whole newspaper. Extract turns to page 14. If you know which three fields you need, define a schema — do not OCR forty pages and regex your way through the result." });

/* 17 */ s = T.slideL(p, "What this segment cost you", "₹ summary");
T.table(p, s, { y: 1.65, headers: ["Service", "Input", "Cached input", "Output"], colW: [4.0, 2.7, 2.7, 2.693],
  rows: [
    ["Sarvam-105B", "₹29.28 / 1M", "₹10.98 / 1M", "₹73.20 / 1M"],
    ["Sarvam-105B Chat", "₹29.28 / 1M", "₹10.98 / 1M", "₹73.20 / 1M"],
    ["Gemma-4 31B", "₹36.60 / 1M", "₹13.73 / 1M", "₹91.50 / 1M"],
    ["GLM 5.2", "₹128.10 / 1M", "₹23.79 / 1M", "₹402.60 / 1M"],
    ["Document Digitisation", "₹0.50 per page", "—", "max 10 pages/job"],
  ], rowH: 0.38, size: 11 });
T.rows(p, s, [
  { icon: "★", title: "Notice something", body: "The Indic-native flagship is also the cheapest of the three chat models on the platform. GLM 5.2 costs 4.4x more on input and 5.5x more on output. That is not an accident — it is a defensible cost advantage for anyone building India-first." },
], { y: 4.1, rh: 1.0 });
T.takeaway(p, s, "Your Lab 4 agent: about ₹0.70 for ten conversations. Lab 5 document pipeline: about ₹10 for twenty pages. Check your dashboard.", { icon: "₹" });
T.foot(s, ...FT);

/* 18 */ T.quoteSlide(p, { quote: "The reasoning model is 9% of your bill.\nThe part everyone optimises is the part that barely matters.",
  by: "— A preview of the money segment. Next: Indus." });

p.writeFile({ fileName: "04_Sarvam105B_and_Document_AI.pptx" }).then(f => console.log("OK", f));
