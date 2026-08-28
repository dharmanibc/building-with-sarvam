"""Labs 05-07: Sarvam-105B, Document AI, Agentic."""
from nbkit import build, md, code, header, SETUP, COSTMETER_IMPORT

# ══════════════════════════════════════════════════════ LAB 05 — SARVAM-105B
build("05_Sarvam105B_Reasoning_Tools_Streaming.ipynb", "Sarvam-105B Deep Dive", [
    header("LAB 05 · THE MODEL", "Sarvam-105B — reasoning, tools, streaming, caching",
           "Base-URL swap · every parameter · prompt caching measured · tool calling · structured output",
           "70 min", "≈ ₹5", "Lab 00"),
    SETUP, COSTMETER_IMPORT,
    md("""
## 1 · The ninety seconds that reframes the platform

Chat completions are **OpenAI-compatible**. Your existing code, LangChain chains and
Vercel AI SDK apps work with a base-URL change.
"""),
    code("""
# Path A — the OpenAI SDK, pointed at Sarvam
from openai import OpenAI

oa = OpenAI(api_key=API_KEY, base_url="https://api.sarvam.ai/v1")

r = oa.chat.completions.create(          # note: .create() — OpenAI convention
    model="sarvam-105b",
    messages=[{"role": "user", "content": "GST का आर्थिक प्रभाव एक पैराग्राफ में।"}],
    max_tokens=1200,
)
cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
print(r.choices[0].message.content[:400])
"""),
    code("""
# Path B — the native Sarvam SDK
# ⚠️ NOTE THE DIFFERENCE: client.chat.completions(...)  — there is NO .create()
r2 = client.chat.completions(
    model="sarvam-105b",
    messages=[{"role": "user", "content": "GST का आर्थिक प्रभाव एक पैराग्राफ में।"}],
    max_tokens=1200,
)
cost.llm(r2.usage.prompt_tokens, r2.usage.completion_tokens)
print(r2.choices[0].message.content[:400])
"""),
    md("""
> **The single most common AI-assistant error on this platform.** Every coding assistant
> writes `client.chat.completions.create(...)` because that is what every other
> OpenAI-shaped SDK does. The native client breaks that convention.
> `npx skills add sarvamai/skills` fixes it permanently.
"""),
    md("""
---
## 2 · `reasoning_effort` — the parameter that surprises everyone
"""),
    code("""
import time
PROMPT = "A loan of ₹5,00,000 at 9.5% reducing balance over 60 months. Monthly EMI?"

for effort, budget in [(None, 400), ("low", 400), ("low", 3000)]:
    t0 = time.perf_counter()
    kw = dict(model="sarvam-105b", max_tokens=budget,
              messages=[{"role": "user", "content": PROMPT}])
    if effort is None:
        kw["reasoning_effort"] = None
    r = client.chat.completions(**kw)
    dt = time.perf_counter() - t0
    cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
    content = r.choices[0].message.content
    print(f"effort={str(effort):<5} budget={budget:<5} {dt:>5.1f}s  "
          f"out={r.usage.completion_tokens:<5} "
          f"content={'None ⚠️' if content is None else content[:60]+'...'}")
"""),
    md("""
| Setting | Keeps reasoning | Cost | Speed | Use for |
|---|---|---|---|---|
| `reasoning_effort=None` | ❌ | lowest | fastest | classification, extraction, routing |
| `"low"` + generous `max_tokens` | ✅ | higher | slower | multi-step logic, agents, maths |

**Watch the billing.** Even when `content` is `None`, the reasoning tokens are billed.
A silent failure that costs money is worse than one that crashes.
"""),
    md("""
---
## 3 · Every parameter, swept
"""),
    code("""
BASE = dict(model="sarvam-105b", max_tokens=600, reasoning_effort=None,
            messages=[{"role": "user", "content": "Name three risks of an unsecured personal loan."}])

SWEEP = [
    ("temperature=0.0",   dict(temperature=0.0)),
    ("temperature=1.5",   dict(temperature=1.5)),
    ("top_p=0.3",         dict(top_p=0.3)),
    ("freq_penalty=1.5",  dict(frequency_penalty=1.5)),
    ("pres_penalty=1.5",  dict(presence_penalty=1.5)),
    ("stop=['3.']",       dict(stop=["3."])),
]

for label, kw in SWEEP:
    r = client.chat.completions(**{**BASE, **kw})
    cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
    print(f"\\n── {label}\\n{(r.choices[0].message.content or '')[:220]}")
"""),
    code("""
# seed = reproducibility. Essential for eval harnesses (Lab 07).
outs = []
for _ in range(2):
    r = client.chat.completions(**{**BASE, "temperature": 0.9, "seed": 42})
    cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
    outs.append(r.choices[0].message.content)
print("identical with seed=42 :", outs[0] == outs[1])
"""),
    md("""
| Parameter | Range | Default | When you touch it |
|---|---|---|---|
| `temperature` | 0–2 | 0.5 (reasoning on) / 0.2 (off) | 0–0.3 extraction · 0.7+ generation |
| `top_p` | 0–1 | 1 | Leave alone unless you know why |
| `max_tokens` | — | — | Starter 4096 / Pro 16384 / Business 128000 |
| `frequency_penalty` | −2…2 | 0 | Long generation that repeats itself |
| `presence_penalty` | −2…2 | 0 | Force topic movement |
| `seed` | int | — | **Always set it in evals** |
| `stop` | ≤4 strings | — | Structured output boundaries |
| `n` | 1–128 | 1 | Sampling multiple candidates |
| `stream` | bool | False | Any user-facing interface |
"""),
    md("""
---
## 4 · Streaming
"""),
    code("""
t0 = time.perf_counter(); first = None; buf = []
for chunk in client.chat.completions(
        model="sarvam-105b", max_tokens=1500, stream=True,
        messages=[{"role": "user", "content": "भारत की डिजिटल क्रांति पर एक संक्षिप्त विश्लेषण।"}]):
    if chunk.choices:
        d = chunk.choices[0].delta
        if getattr(d, "content", None):
            if first is None:
                first = time.perf_counter() - t0
                print(f"[first token @ {first*1000:.0f} ms]\\n")
            buf.append(d.content); print(d.content, end="", flush=True)
print(f"\\n\\ntotal {time.perf_counter()-t0:.1f}s · {len(''.join(buf))} chars")
"""),
    md("""
---
## 5 · Prompt caching — a 62% saving that is an architecture decision

Cached input is **₹10.98/1M** against **₹29.28/1M**. The trick is to put everything
stable *first* and keep it byte-identical between calls.
"""),
    code("""
STABLE_SYSTEM = ("You are a loan servicing assistant for an Indian NBFC. "
                 "Answer only from the policy below. Be concise.\\n\\n"
                 + "POLICY:\\n" + ("Late payment attracts 2% per month. "
                 "Prepayment allowed after 6 EMIs with 2% charge. " * 40))

def ask(user_msg):
    r = client.chat.completions(
        model="sarvam-105b", max_tokens=500, reasoning_effort=None,
        messages=[{"role": "system", "content": STABLE_SYSTEM},   # ← identical every time
                  {"role": "user",   "content": user_msg}])
    u = r.usage
    cached = getattr(u, "prompt_tokens_details", None)
    cached = getattr(cached, "cached_tokens", 0) if cached else 0
    cost.llm(u.prompt_tokens, u.completion_tokens, cached)
    return r.choices[0].message.content, u.prompt_tokens, cached

for i, q in enumerate(["What is the late payment charge?",
                       "Can I prepay after 3 EMIs?",
                       "What happens if I miss two EMIs?"]):
    ans, ptok, cached = ask(q)
    print(f"call {i+1}: prompt={ptok:>5} cached={cached:>5}  → {ans[:70]}")
"""),
    code("""
# What caching is worth at scale
SYS_TOKENS, TURNS, CALLS = 2000, 8, 100_000
uncached = SYS_TOKENS * TURNS * CALLS * 29.28 / 1_000_000
cached   = SYS_TOKENS * TURNS * CALLS * 10.98 / 1_000_000
print(f"uncached ₹{uncached:>12,.0f} / month")
print(f"cached   ₹{cached:>12,.0f} / month")
print(f"saving   ₹{uncached-cached:>12,.0f}  ({(1-cached/uncached):.0%})")
"""),
    md("""
---
## 6 · Tool calling — the foundation of everything agentic
"""),
    code("""
# ── Mock backend ──────────────────────────────────────────────────────────
ACCOUNTS = {"LN1001": {"name": "Rajesh Kumar", "emi": 12500, "due": "2026-08-15",
                       "outstanding": 340000, "overdue_days": 0}}

def get_account(account_id: str):
    return ACCOUNTS.get(account_id, {"error": "not found"})

def get_emi_schedule(account_id: str):
    a = ACCOUNTS.get(account_id)
    return {"error": "not found"} if not a else {
        "next_due": a["due"], "amount": a["emi"], "remaining_months": 28}

def raise_ticket(account_id: str, issue: str):
    return {"ticket_id": "TKT-88214", "status": "open", "issue": issue}

REGISTRY = {"get_account": get_account,
            "get_emi_schedule": get_emi_schedule,
            "raise_ticket": raise_ticket}

TOOLS = [
    {"type": "function", "function": {
        "name": "get_account", "description": "Fetch loan account details by account ID",
        "parameters": {"type": "object", "properties": {
            "account_id": {"type": "string", "description": "Loan account number, e.g. LN1001"}},
            "required": ["account_id"]}}},
    {"type": "function", "function": {
        "name": "get_emi_schedule", "description": "Fetch the upcoming EMI schedule",
        "parameters": {"type": "object", "properties": {
            "account_id": {"type": "string", "description": "Loan account number"}},
            "required": ["account_id"]}}},
    {"type": "function", "function": {
        "name": "raise_ticket", "description": "Raise a support ticket for an unresolved issue",
        "parameters": {"type": "object", "properties": {
            "account_id": {"type": "string", "description": "Loan account number"},
            "issue": {"type": "string", "description": "Short description of the problem"}},
            "required": ["account_id", "issue"]}}},
]
print("3 tools registered")
"""),
    code("""
def run_agent(user_msg, max_turns=5, verbose=True):
    msgs = [{"role": "system", "content":
             "You are a loan servicing agent. Use tools for any account fact. "
             "Never invent numbers. Reply in the user's language."},
            {"role": "user", "content": user_msg}]

    for turn in range(max_turns):
        r = client.chat.completions(model="sarvam-105b", messages=msgs,
                                    tools=TOOLS, max_tokens=2000)
        cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
        m = r.choices[0].message
        calls = getattr(m, "tool_calls", None)

        if not calls:
            return m.content

        msgs.append({"role": "assistant", "content": m.content, "tool_calls":
                     [{"id": c.id, "type": "function",
                       "function": {"name": c.function.name,
                                    "arguments": c.function.arguments}} for c in calls]})
        for c in calls:
            args = json.loads(c.function.arguments)
            out = REGISTRY[c.function.name](**args)
            if verbose:
                print(f"  🔧 {c.function.name}({args}) → {out}")
            msgs.append({"role": "tool", "tool_call_id": c.id,
                         "content": json.dumps(out, ensure_ascii=False)})
    return "max turns reached"


print(run_agent("मेरे अकाउंट LN1001 की अगली EMI कब है और कितनी है?"))
"""),
    code("""
# Multi-tool: this one should call two tools then answer
print(run_agent("Account LN1001 — my auto-debit failed last month. "
                "What's my outstanding, and please raise a ticket."))
"""),
    md("""
---
## 7 · Structured output — JSON you can trust
"""),
    code("""
SCHEMA_HINT = '''Return ONLY valid JSON matching:
{"intent": "<balance|emi|complaint|other>",
 "account_id": "<string or null>",
 "sentiment": "<positive|neutral|negative>",
 "urgency": <1-5>,
 "summary": "<one line in English>"}'''

def classify(msg):
    r = client.chat.completions(
        model="sarvam-105b", max_tokens=400, temperature=0, reasoning_effort=None,
        messages=[{"role": "system", "content": SCHEMA_HINT},
                  {"role": "user", "content": msg}])
    cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
    raw = (r.choices[0].message.content or "").strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {"_parse_error": raw[:200]}

for m in ["मेरा EMI तीन बार fail हो गया, बहुत परेशान हूँ! Account LN1001",
          "What is my current balance?"]:
    print(json.dumps(classify(m), ensure_ascii=False, indent=2))
"""),
    md("""
> **Production tip.** `temperature=0` + `reasoning_effort=None` + an explicit schema in
> the system prompt gives you parseable JSON far more reliably than asking nicely.
> Always wrap `json.loads` in a try — and log the raw string when it fails.
"""),
    md("### 8 · Model comparison — is the flagship worth it for your task?"),
    code("""
TASK = "Summarise in one sentence: RBI raised the repo rate by 25bps citing food inflation."
for model in ["sarvam-105b", "sarvam-30b"]:
    t0 = time.perf_counter()
    r = client.chat.completions(model=model, max_tokens=400, reasoning_effort=None,
                                messages=[{"role": "user", "content": TASK}])
    cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
    print(f"{model:<14} {time.perf_counter()-t0:>5.1f}s  {r.choices[0].message.content}")
"""),
    code("cost.report()"),
    md("""
---
## ✅ Checkpoint

- [ ] Both SDK paths work; you know why `.create()` differs between them
- [ ] You reproduced `content is None` and can explain the token accounting
- [ ] You measured caching and can state the monthly saving at your volume
- [ ] A multi-tool agent called two tools and answered in Hindi

## 🧪 Try this

1. Add a 4th tool that **fails** (raises). Make the agent recover gracefully.
2. Make the agent hallucinate: remove the "never invent numbers" system line and ask
   about an account that doesn't exist. This is why tool discipline matters.
3. Sweep `temperature` 0→2 on the classifier. At what point does JSON parsing break?
4. Measure tokens-per-second for 105B vs 30B. Where is 30B good enough?
"""),
])

# ══════════════════════════════════════════════════════ LAB 06 — DOCUMENT AI
build("06_Document_AI_Digitise_and_Extract.ipynb", "Document AI", [
    header("LAB 06 · DOCUMENTS", "Sarvam Vision — digitise, extract, and survive the limits",
           "Job lifecycle · schema design · partially_completed · chunking · rate-limit queue",
           "55 min", "≈ ₹10", "Lab 00"),
    SETUP, COSTMETER_IMPORT,
    md("""
## The two endpoints

| | Digitise | Extract |
|---|---|---|
| Job | Whole document → HTML/Markdown + per-page JSON | Your schema → structured JSON/CSV/XLSX |
| For | Archival, search, RAG ingestion | KYC, invoices, forms |
| Rule | Don't digitise 40 pages to pull 3 fields | Write a schema instead |

**Hard limits that shape your architecture, not just your code:**
`10 pages per job` · `200 MB` · **`10 requests/minute on EVERY plan`** · ₹0.50/page
"""),
    md("### 0 · Get a document"),
    code("""
# Make a simple test PDF if you have none. Replace with a real Indic document when you can.
%pip install -q reportlab pypdf
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas

pdf_path = DATA / "policy.pdf"
c = rl_canvas.Canvas(str(pdf_path), pagesize=A4)
for page in range(1, 4):
    c.drawString(60, 780, "SAMPLE INSURANCE POLICY")
    c.drawString(400, 780, f"Policy No: ABC-{1230+page}")
    c.drawString(60, 750, "Insured Name: Rajesh Kumar Sharma")
    c.drawString(60, 730, "Sum Insured: INR 500000")
    c.drawString(60, 710, "Premium: INR 12500 per annum")
    c.drawString(60, 690, f"Page {page} of 3")
    c.showPage()
c.save()
print("wrote", pdf_path)
"""),
    md("""
---
## 1 · Digitise — the whole document
"""),
    code("""
with open(pdf_path, "rb") as f:
    job = client.doc_ai.digitise(
        file=[("policy.pdf", f, "application/pdf")],   # ⚠️ an ARRAY of tuples
        language="en-IN",                              # ⚠️ 'language', NOT 'language_code'
        output_format="md",                            # ⚠️ 'md', NOT 'markdown'
    )
print("job:", job.job_id)
"""),
    code("""
# ── Poll properly: backoff, and handle EVERY terminal state ───────────────
TERMINAL = {"completed", "partially_completed", "failed", "rejected"}

def wait(job, timeout=300):
    delay, waited = 2, 0
    while waited < timeout:
        st = client.doc_ai.get_status(job_id=job.job_id)
        state = str(getattr(st, "job_state", getattr(st, "status", ""))).lower()
        print(f"  {state:<22} +{waited}s")
        if state in TERMINAL:
            return state, st
        time.sleep(delay); waited += delay; delay = min(delay * 1.5, 20)
    raise TimeoutError("job did not finish")

state, status = wait(job)
print("\\nterminal state:", state)
"""),
    code("""
# ⚠️ partially_completed IS TERMINAL. Most code only checks 'completed' and loses pages.
if state == "completed":
    print("all pages OK")
elif state == "partially_completed":
    done = getattr(getattr(status, "usage", None), "pages_processed", "?")
    print(f"⚠️  ONLY {done} pages processed — the rest FAILED SILENTLY.")
    print("   Reconcile against your expected page count and re-queue the gaps.")
elif state in ("failed", "rejected"):
    print("job failed:", getattr(status, "error", ""))
"""),
    code("""
res = client.doc_ai.get_results(job_id=job.job_id)
cost.doc(3)
url = client.doc_ai.get_download_url(job_id=job.job_id)
print("download:", getattr(url, "url", url))
print(str(res)[:600])
"""),
    md("""
---
## 2 · Extract — only the fields you define

**The `description` IS the prompt.** Be specific about location and format —
`"Policy number, top-right, format ABC-1234"` beats `"policy number"` by a wide margin.
"""),
    code("""
schema = {
    "type": "object",
    "properties": {
        "policy_number": {"type": "string",
            "description": "Insurance policy number, top-right of page 1, format ABC-1234"},
        "insured_name": {"type": "string",
            "description": "Full name of the insured person"},
        "sum_insured": {"type": "number",
            "description": "Total sum insured, in INR, digits only"},
        "premium": {"type": "number",
            "description": "Annual premium amount in INR"},
        "policy_type": {"type": "string", "enum": ["life", "health", "motor", "other"],
            "description": "Category of the policy"},
    },
    "required": ["policy_number", "insured_name"],
}

with open(pdf_path, "rb") as f:
    ejob = client.doc_ai.extract(
        file=[("policy.pdf", f, "application/pdf")],
        schema=json.dumps(schema),     # ⚠️ JSON STRING, not a dict
        language="en-IN",
        output_format="json",
    )
state, _ = wait(ejob)
if state in ("completed", "partially_completed"):
    out = client.doc_ai.get_results(job_id=ejob.job_id)
    cost.doc(3)
    print(json.dumps(out if isinstance(out, dict) else str(out), indent=2)[:800])
"""),
    md("""
**Schema rules**

- Root must be `type: "object"` with non-empty `properties`
- Every field needs a `type` **and** a non-empty `description`
- Types: `string number integer boolean object array` · optional `enum`
- **Max nesting depth 4**
- Provide **exactly one** of `schema` or `config_id` — both or neither returns 400
"""),
    md("""
---
## 3 · ⚠️ Every naming gotcha, demonstrated

Run these deliberately. Recognising the error signature in one second is the skill.
"""),
    code("""
def try_it(label, fn):
    try:
        fn(); print(f"✅ {label}")
    except Exception as e:
        print(f"❌ {label}\\n     {type(e).__name__}: {str(e)[:150]}")

with open(pdf_path, "rb") as f: blob = f.read()
mk = lambda: [("policy.pdf", io.BytesIO(blob), "application/pdf")]

try_it("schema as dict (should fail)",
       lambda: client.doc_ai.extract(file=mk(), schema=schema, language="en-IN"))

try_it("output_format='markdown' (should fail)",
       lambda: client.doc_ai.digitise(file=mk(), language="en-IN", output_format="markdown"))

try_it("file as bare handle, not array (should fail)",
       lambda: client.doc_ai.digitise(file=io.BytesIO(blob), language="en-IN", output_format="md"))

try_it("language_code instead of language (silently ignored — no error!)",
       lambda: client.doc_ai.digitise(file=mk(), language_code="en-IN", output_format="md"))
"""),
    md("""
| You write | What happens | Correct |
|---|---|---|
| `language_code=` | **Silently ignored** | `language=` |
| `output_format="markdown"` | 400 | `"md"` |
| `schema={...}` dict | `AttributeError: 'dict' object has no attribute 'read'` | `json.dumps(schema)` |
| `file=open(...)` | Type error | `file=[(name, handle, mime)]` |
| JS `getStatus({job_id})` | undefined fields | `getStatus(job_id)` — positional |
| 11-page PDF | 400 `invalid_request_error` | Chunk to 10 |
"""),
    md("""
---
## 4 · Chunking past the 10-page limit
"""),
    code("""
from pypdf import PdfReader, PdfWriter

def chunk_pdf(src, max_pages=10):
    reader = PdfReader(str(src)); parts = []
    for start in range(0, len(reader.pages), max_pages):
        w = PdfWriter()
        for p in reader.pages[start:start + max_pages]:
            w.add_page(p)
        out = OUT / f"{Path(src).stem}_p{start+1}-{start+max_pages}.pdf"
        with open(out, "wb") as fh: w.write(fh)
        parts.append(out)
    return parts

parts = chunk_pdf(pdf_path)
print(f"{len(PdfReader(str(pdf_path)).pages)} pages → {len(parts)} chunk(s)")
for p in parts: print("  ", p.name)
"""),
    md("""
---
## 5 · The rate-limit queue — 10 req/min on EVERY plan

This is not a tier limit you can pay to remove. Your architecture needs a queue.
"""),
    code("""
import threading, queue as _q

class RateLimiter:
    \"\"\"Token bucket. Document AI allows 10 requests per minute, on every plan.\"\"\"
    def __init__(self, per_minute=10):
        self.interval = 60.0 / per_minute
        self._lock = threading.Lock(); self._last = 0.0
    def acquire(self):
        with self._lock:
            wait = self._last + self.interval - time.monotonic()
            if wait > 0: time.sleep(wait)
            self._last = time.monotonic()

limiter = RateLimiter(10)

def submit_with_backoff(path, max_retries=5):
    for attempt in range(max_retries):
        limiter.acquire()
        try:
            with open(path, "rb") as f:
                return client.doc_ai.digitise(
                    file=[(Path(path).name, f, "application/pdf")],
                    language="en-IN", output_format="md")
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                backoff = (2 ** attempt) + (attempt * 0.1)
                print(f"  429 → backing off {backoff:.1f}s"); time.sleep(backoff)
            else:
                raise
    raise RuntimeError("exhausted retries")

print("queue armed — submit_with_backoff() paces at 10/min and retries 429s")
"""),
    md("""
---
## 6 · A pipeline that survives a bad file

The difference between a script and a pipeline: one corrupted file in ten thousand
must not kill the run.
"""),
    code("""
def process_batch(paths):
    results, failures = [], []
    for p in paths:
        try:
            job = submit_with_backoff(p)
            state, status = wait(job)
            if state == "completed":
                results.append({"file": Path(p).name, "state": state,
                                "data": client.doc_ai.get_results(job_id=job.job_id)})
            elif state == "partially_completed":
                results.append({"file": Path(p).name, "state": state,
                                "data": client.doc_ai.get_results(job_id=job.job_id)})
                failures.append({"file": Path(p).name, "reason": "partial — pages lost"})
            else:
                failures.append({"file": Path(p).name, "reason": state})
        except Exception as e:
            failures.append({"file": Path(p).name, "reason": f"{type(e).__name__}: {e}"})
    return results, failures

# Include a deliberately broken file
bad = OUT / "corrupt.pdf"; bad.write_bytes(b"%PDF-1.4 this is not a pdf")
ok, bad_list = process_batch(parts + [bad])
cost.doc(3)
print(f"succeeded : {len(ok)}")
print(f"failed    : {len(bad_list)}")
for f in bad_list: print("   ", f)
"""),
    md("""
---
## 7 · The economics
"""),
    code("""
for pages in [1_000, 10_000, 100_000, 1_000_000]:
    you  = pages * 0.50
    bpo_lo, bpo_hi = pages * 3, pages * 8
    print(f"{pages:>9,} pages   your cost ₹{you:>11,.0f}   "
          f"BPO charges ₹{bpo_lo:>11,.0f}–₹{bpo_hi:>11,.0f}")

print(f"\\nThroughput ceiling: 10 jobs/min × 10 pages = 100 pages/min = "
      f"{100*60*24:,} pages/day per key.")
print("→ For a million-page backfile, that is ~7 days. Plan for parallel keys.")
"""),
    code("cost.report()"),
    md("""
---
## ✅ Checkpoint

- [ ] A digitise job reached a terminal state and you handled `partially_completed`
- [ ] An extract job returned your schema's fields
- [ ] You triggered all four naming gotchas and recognise each error
- [ ] Your batch survived a corrupted file
- [ ] You can state the throughput ceiling per API key

## 🧪 Try this

1. Run a **handwritten** Indic document. Where does extraction degrade?
2. Write two schemas for the same doc — one vague, one very specific. Compare accuracy.
3. Add a confidence threshold and route low-confidence extractions to a human queue.
4. Cost a 500,000-page archival project end to end, including the human review queue.
"""),
])

# ══════════════════════════════════════════════════════ LAB 07 — AGENTIC
build("07_Agentic_Tools_State_Evals_Guardrails.ipynb", "Agentic AI", [
    header("LAB 07 · AGENTIC AI", "Tools, state, checkpointing, evals, guardrails",
           "Multi-step workflows · recovery · observability · the eval harness that wins pilots",
           "75 min", "≈ ₹8", "Labs 05, 06"),
    SETUP, COSTMETER_IMPORT,
    md("""
## Chatbot vs agent

| | Chatbot | Agent |
|---|---|---|
| Does | Answers a question | Completes a task |
| State | None, or yours | Explicit, across many steps |
| Acts | No | **Yes — writes to systems** |
| Failure | A bad answer | A wrong action, possibly irreversible |
| Evaluate on | Response quality | Task success, tool accuracy, recovery |

The moment an LLM can take an action, the engineering problem stops being prompt
quality and becomes **reliability, observability and blast radius**.
"""),
    md("""
---
## 1 · The design law: LLMs reason, code executes

Push everything deterministic *out* of the model. It is cheaper, auditable, and correct.
"""),
    code("""
# ❌ The expensive way — ask the model to compute
r = client.chat.completions(
    model="sarvam-105b", max_tokens=1500,
    messages=[{"role": "user", "content":
               "Loan ₹500000, 9.5% annual reducing, 60 months. Compute the exact EMI."}])
cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
print("LLM says:", (r.choices[0].message.content or "")[-200:])
"""),
    code("""
# ✅ The right way — model decides WHICH calculation, code performs it
def emi(principal: float, annual_rate: float, months: int) -> dict:
    r = annual_rate / 12 / 100
    m = principal * r * (1 + r) ** months / ((1 + r) ** months - 1)
    return {"emi": round(m, 2), "total_paid": round(m * months, 2),
            "total_interest": round(m * months - principal, 2)}

print("code says:", emi(500000, 9.5, 60))
"""),
    md("""
> Deterministic, free at the point of execution, unit-testable, and identical every
> time. Arya reports **114% better performance on complex tasks** using smaller, cheaper
> models by applying exactly this principle.
"""),
    md("""
---
## 2 · A stateful, checkpointed agent

A failure at step 40 must not lose the first 39.
"""),
    code("""
import sqlite3, uuid
from dataclasses import dataclass, field, asdict

DB = sqlite3.connect(":memory:")
DB.execute("CREATE TABLE ckpt (run_id TEXT, step INT, state TEXT, ts REAL)")

@dataclass
class RunState:
    run_id: str
    step: int = 0
    data: dict = field(default_factory=dict)
    trace: list = field(default_factory=list)

def save(st: RunState):
    DB.execute("INSERT INTO ckpt VALUES (?,?,?,?)",
               (st.run_id, st.step, json.dumps(asdict(st)), time.time())); DB.commit()

def restore(run_id: str):
    row = DB.execute("SELECT state FROM ckpt WHERE run_id=? ORDER BY step DESC LIMIT 1",
                     (run_id,)).fetchone()
    return RunState(**json.loads(row[0])) if row else None

print("checkpoint store ready")
"""),
    code("""
# ── A 5-step loan triage workflow ─────────────────────────────────────────
def step_extract(st):
    st.data["applicant"] = {"name": "Rajesh Kumar", "income": 65000,
                            "pan": "ABCDE1234F", "loan_amount": 500000}
    return "extracted applicant fields"

def step_validate(st):
    a = st.data["applicant"]
    errs = []
    if len(a["pan"]) != 10: errs.append("PAN malformed")
    if a["income"] <= 0:    errs.append("income missing")
    st.data["validation"] = {"ok": not errs, "errors": errs}
    return f"validation ok={not errs}"

def step_eligibility(st):
    a = st.data["applicant"]
    e = emi(a["loan_amount"], 9.5, 60)
    ratio = e["emi"] / a["income"]
    st.data["eligibility"] = {"emi": e["emi"], "foir": round(ratio, 3),
                              "eligible": ratio < 0.5}
    return f"FOIR={ratio:.2f} eligible={ratio < 0.5}"

def step_risk(st):
    if st.data.get("_inject_failure"):
        raise RuntimeError("credit bureau timeout")
    st.data["risk"] = {"bureau_score": 748, "band": "low"}
    return "bureau score 748"

def step_decide(st):
    ok = st.data["eligibility"]["eligible"] and st.data["risk"]["band"] == "low"
    st.data["decision"] = "APPROVE" if ok else "ESCALATE"
    return st.data["decision"]

STEPS = [step_extract, step_validate, step_eligibility, step_risk, step_decide]
"""),
    code("""
def run_workflow(run_id=None, resume=False, inject_failure=False):
    st = restore(run_id) if resume else RunState(run_id=run_id or str(uuid.uuid4())[:8])
    st.data["_inject_failure"] = inject_failure
    print(f"{'RESUMING' if resume else 'STARTING'} run {st.run_id} at step {st.step}")

    while st.step < len(STEPS):
        fn = STEPS[st.step]
        try:
            t0 = time.perf_counter()
            msg = fn(st)
            st.trace.append({"step": st.step, "fn": fn.__name__, "ok": True,
                             "ms": round((time.perf_counter()-t0)*1000, 1), "msg": msg})
            print(f"  ✅ {st.step} {fn.__name__:<18} {msg}")
            st.step += 1
            save(st)                       # ← checkpoint AFTER each success
        except Exception as e:
            st.trace.append({"step": st.step, "fn": fn.__name__, "ok": False, "err": str(e)})
            print(f"  ❌ {st.step} {fn.__name__:<18} {e}")
            save(st)
            return st, False
    return st, True

st, ok = run_workflow(run_id="demo1", inject_failure=True)
print("\\ncompleted:", ok, "| stopped at step", st.step)
"""),
    code("""
# Resume from the checkpoint — steps 0-2 are NOT re-run
st2, ok2 = run_workflow(run_id="demo1", resume=True, inject_failure=False)
print("\\ncompleted:", ok2, "| decision:", st2.data.get("decision"))
print("\\nFull trace:")
for t in st2.trace: print("  ", t)
"""),
    md("""
> **This is the single biggest reliability difference at scale.** A workflow that must
> restart from step 1 every time something transient fails cannot run a fifty-step
> compliance review. It can only demo.
"""),
    md("""
---
## 3 · Observability — you cannot debug what you cannot see
"""),
    code("""
class Tracer:
    def __init__(self): self.spans = []
    def span(self, name, **meta):
        return _Span(self, name, meta)
    def report(self):
        print(f"{'span':<26}{'ms':>9}{'tokens':>9}{'₹':>10}")
        print("─" * 54)
        for s in self.spans:
            print(f"{s['name']:<26}{s['ms']:>9.0f}{s.get('tokens',0):>9}{s.get('inr',0):>10.4f}")
        print("─" * 54)
        print(f"{'TOTAL':<26}{sum(s['ms'] for s in self.spans):>9.0f}"
              f"{sum(s.get('tokens',0) for s in self.spans):>9}"
              f"{sum(s.get('inr',0) for s in self.spans):>10.4f}")

class _Span:
    def __init__(self, tr, name, meta): self.tr, self.name, self.meta = tr, name, meta
    def __enter__(self): self.t0 = time.perf_counter(); return self
    def __exit__(self, *a):
        self.tr.spans.append({"name": self.name, "ms": (time.perf_counter()-self.t0)*1000,
                              **self.meta})
    def set(self, **kw): self.meta.update(kw)

tracer = Tracer()

with tracer.span("classify") as sp:
    r = client.chat.completions(model="sarvam-105b", max_tokens=300, reasoning_effort=None,
        messages=[{"role":"user","content":"Classify: 'my EMI bounced twice'"}])
    inr = cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
    sp.set(tokens=r.usage.total_tokens, inr=inr)

with tracer.span("emi_calc") as sp:
    emi(500000, 9.5, 60)

tracer.report()
"""),
    md("""
---
## 4 · Guardrails — PII redaction before you log anything
"""),
    code("""
import re

PII = [
    (re.compile(r"\\b[A-Z]{5}[0-9]{4}[A-Z]\\b"),                "[PAN]"),
    (re.compile(r"\\b\\d{4}\\s?\\d{4}\\s?\\d{4}\\b"),              "[AADHAAR]"),
    (re.compile(r"\\b(?:\\+91[- ]?)?[6-9]\\d{9}\\b"),            "[PHONE]"),
    (re.compile(r"\\b\\d{9,18}\\b"),                            "[ACCOUNT]"),
    (re.compile(r"[\\w.+-]+@[\\w-]+\\.[\\w.]+"),                  "[EMAIL]"),
]

def redact(text: str) -> str:
    for pat, tag in PII:
        text = pat.sub(tag, text)
    return text

SAMPLE = ("Rajesh, PAN ABCDE1234F, Aadhaar 1234 5678 9012, phone +91 9876543210, "
          "a/c 123456789012, email rajesh@example.com — EMI bounced.")
print("RAW     :", SAMPLE)
print("REDACTED:", redact(SAMPLE))
"""),
    code("""
# Escalation thresholds — when does a human take over?
ESCALATE_IF = {
    "sentiment_negative_turns": 2,
    "tool_failures": 2,
    "turns": 10,
    "explicit_request": ["human", "agent", "manager", "शिकायत", "इंसान"],
}

def should_escalate(state):
    if state["turns"] >= ESCALATE_IF["turns"]: return "turn limit"
    if state["tool_failures"] >= ESCALATE_IF["tool_failures"]: return "repeated tool failure"
    if state["neg_turns"] >= ESCALATE_IF["sentiment_negative_turns"]: return "customer frustrated"
    if any(k in state["last_msg"].lower() for k in ESCALATE_IF["explicit_request"]):
        return "explicitly requested"
    return None

for s in [{"turns": 3, "tool_failures": 0, "neg_turns": 0, "last_msg": "what is my balance"},
          {"turns": 4, "tool_failures": 0, "neg_turns": 0, "last_msg": "मुझे इंसान से बात करनी है"},
          {"turns": 11, "tool_failures": 0, "neg_turns": 0, "last_msg": "ok"}]:
    print(f"{str(should_escalate(s) or 'continue'):<24} ← {s['last_msg']}")
"""),
    md("""
---
## 5 · The eval harness — the module that wins pilots

An enterprise buyer's first question is *"does it work"*. Their second, and the one
that decides the contract, is **"how do you know it still works next month?"**
"""),
    code("""
# ── Golden set. Ten cases from REAL transcripts beats fifty invented ones. ──
GOLDEN = [
    {"id": "g1", "input": "मेरे अकाउंट LN1001 की अगली EMI कब है?",
     "expect_tool": "get_emi_schedule", "expect_lang": "hi", "must_contain": ["15"]},
    {"id": "g2", "input": "What is the outstanding on LN1001?",
     "expect_tool": "get_account", "expect_lang": "en", "must_contain": ["340000", "3,40,000"]},
    {"id": "g3", "input": "LN1001 auto-debit failed, raise a complaint",
     "expect_tool": "raise_ticket", "expect_lang": "en", "must_contain": ["TKT"]},
    {"id": "g4", "input": "What is the capital of France?",
     "expect_tool": None, "expect_lang": "en", "must_contain": []},
]

def detect_lang(text):
    return "hi" if any("\\u0900" <= ch <= "\\u097F" for ch in text) else "en"
"""),
    code("""
# Reuse the tool agent from Lab 05 (redefined compactly here)
ACCOUNTS = {"LN1001": {"name": "Rajesh Kumar", "emi": 12500, "due": "2026-08-15",
                       "outstanding": 340000}}
def get_account(account_id): return ACCOUNTS.get(account_id, {"error": "not found"})
def get_emi_schedule(account_id):
    a = ACCOUNTS.get(account_id)
    return {"error": "nf"} if not a else {"next_due": a["due"], "amount": a["emi"]}
def raise_ticket(account_id, issue): return {"ticket_id": "TKT-88214", "issue": issue}
REGISTRY = {"get_account": get_account, "get_emi_schedule": get_emi_schedule,
            "raise_ticket": raise_ticket}
TOOLS = [
  {"type":"function","function":{"name":"get_account","description":"Loan account details",
   "parameters":{"type":"object","properties":{"account_id":{"type":"string","description":"Account no"}},"required":["account_id"]}}},
  {"type":"function","function":{"name":"get_emi_schedule","description":"Upcoming EMI schedule",
   "parameters":{"type":"object","properties":{"account_id":{"type":"string","description":"Account no"}},"required":["account_id"]}}},
  {"type":"function","function":{"name":"raise_ticket","description":"Raise a support ticket",
   "parameters":{"type":"object","properties":{"account_id":{"type":"string","description":"Account no"},
    "issue":{"type":"string","description":"Problem"}},"required":["account_id","issue"]}}},
]

SYSTEM = ("You are a loan servicing agent. Use tools for any account fact. "
          "Never invent numbers. Reply in the user's language.")

def agent(user_msg, seed=42):
    msgs = [{"role":"system","content":SYSTEM},{"role":"user","content":user_msg}]
    used, inr, t0 = [], 0.0, time.perf_counter()
    for _ in range(4):
        r = client.chat.completions(model="sarvam-105b", messages=msgs, tools=TOOLS,
                                    max_tokens=1500, seed=seed)
        inr += cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)
        m = r.choices[0].message
        calls = getattr(m, "tool_calls", None)
        if not calls:
            return {"text": m.content or "", "tools": used,
                    "ms": (time.perf_counter()-t0)*1000, "inr": inr}
        msgs.append({"role":"assistant","content":m.content,"tool_calls":
            [{"id":c.id,"type":"function","function":{"name":c.function.name,
              "arguments":c.function.arguments}} for c in calls]})
        for c in calls:
            used.append(c.function.name)
            out = REGISTRY[c.function.name](**json.loads(c.function.arguments))
            msgs.append({"role":"tool","tool_call_id":c.id,
                         "content":json.dumps(out, ensure_ascii=False)})
    return {"text":"max turns","tools":used,"ms":(time.perf_counter()-t0)*1000,"inr":inr}
"""),
    code("""
def run_evals(cases=GOLDEN, verbose=True):
    rows = []
    for c in cases:
        out = agent(c["input"])
        tool_ok = (c["expect_tool"] in out["tools"]) if c["expect_tool"] else (not out["tools"])
        lang_ok = detect_lang(out["text"]) == c["expect_lang"]
        cont_ok = (not c["must_contain"]) or any(
            k.replace(",", "") in out["text"].replace(",", "") for k in c["must_contain"])
        rows.append({"id": c["id"], "tool": tool_ok, "lang": lang_ok,
                     "content": cont_ok, "ms": out["ms"], "inr": out["inr"],
                     "pass": tool_ok and lang_ok and cont_ok, "text": out["text"][:60]})
        if verbose:
            mark = "✅" if rows[-1]["pass"] else "❌"
            print(f"{mark} {c['id']}  tool={tool_ok!s:<5} lang={lang_ok!s:<5} "
                  f"content={cont_ok!s:<5} {out['ms']:>6.0f}ms ₹{out['inr']:.4f}")
    return rows

def summarise(rows):
    n = len(rows)
    lat = sorted(r["ms"] for r in rows)
    print("\\n" + "═" * 52)
    print(f"pass rate        {sum(r['pass'] for r in rows)}/{n}  "
          f"({sum(r['pass'] for r in rows)/n:.0%})")
    print(f"tool accuracy    {sum(r['tool'] for r in rows)/n:.0%}")
    print(f"language correct {sum(r['lang'] for r in rows)/n:.0%}")
    print(f"latency p50      {lat[len(lat)//2]:.0f} ms")
    print(f"latency p95      {lat[int(len(lat)*0.95)-1]:.0f} ms")
    print(f"mean cost/task   ₹{sum(r['inr'] for r in rows)/n:.4f}")
    print("═" * 52)

baseline = run_evals(); summarise(baseline)
"""),
    code("""
# ── Now break a prompt deliberately and watch the harness catch it ─────────
SYSTEM = "You are a helpful assistant."      # ← tool discipline removed

broken = run_evals(); summarise(broken)

print("\\nREGRESSION vs baseline:")
for b, k in zip(baseline, broken):
    if b["pass"] != k["pass"]:
        print(f"  {b['id']}: {b['pass']} → {k['pass']}   «{k['text']}»")
"""),
    md("""
> **That thirty seconds is the whole argument for evals.** Without the harness, that
> prompt change ships and is discovered by a customer. With it, you knew before you
> merged. This is the artefact you show a buyer when they ask about reliability.
"""),
    code("""
SYSTEM = ("You are a loan servicing agent. Use tools for any account fact. "
          "Never invent numbers. Reply in the user's language.")     # restore
cost.report()
"""),
    md("""
---
## ✅ Checkpoint

- [ ] You moved a calculation out of the model and into code
- [ ] A workflow failed at step 3, resumed from checkpoint, and did not re-run steps 0–2
- [ ] Tracer output shows per-span latency, tokens and ₹
- [ ] PII is redacted before anything is logged
- [ ] The eval harness caught a deliberate prompt regression

## 🧪 Try this

1. Grow the golden set to 10 cases **from your own domain**.
2. Add a `hallucination` check: ask about an account that does not exist. Does it invent?
3. Add retry-with-backoff around the tool calls and inject a flaky tool.
4. Persist checkpoints to a real database and resume across a kernel restart.
5. Add cost-per-task to your escalation rules — escalate when a conversation exceeds ₹X.
"""),
])

print("\\nlabs 05-07 done")
