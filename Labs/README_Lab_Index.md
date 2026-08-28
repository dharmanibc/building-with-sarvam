# Code Labs — Building with Sarvam

**13 Jupyter notebooks · 440 cells · 234 code cells.**
**85% of every code cell has been executed against the live Sarvam API** — the saved
outputs in these notebooks are real API responses, real latencies and real rupee
figures, not illustrative placeholders.

Built to be run gradually, cell by cell, in front of a room or alone.

| # | Notebook | Est. cost | Covers |
|---|---|---|---|
| 00 | `00_Setup_and_the_Cost_Meter.ipynb` | ₹0.02 | SDK, key, **the ₹ meter**, the `content is None` trap |
| 01 | `01_The_Sampler_Every_API_in_One_Script.ipynb` | ₹4.20 | Every live API in one script — **the live-session lab** |
| 02 | `02_Saaras_Speech_to_Text_Deep_Dive.ipynb` | ₹8 | 5 modes · REST/Batch/WebSocket · **8 kHz measured, not assumed** · 3-file batch · realtime VAD · diarization |
| 03 | `03_Bulbul_Text_to_Speech_Deep_Dive.ipynb` | ₹6 | Voices · pitch/pace/loudness · **TTFB measured** · telephony formats · pronunciation dictionaries |
| 04 | `04_Language_Layer_Translate_Transliterate_LID.ipynb` | ₹3 | Mayura vs Sarvam-Translate · registers · **the silent `output_script` failure** · auto-router |
| 05 | `05_Sarvam105B_Reasoning_Tools_Streaming.ipynb` | ₹5 | Base-URL swap · `reasoning_effort` · every parameter · **caching measured** · tool calling |
| 06 | `06_Document_AI_Digitise_and_Extract.ipynb` | ₹10 | Digitise vs extract · schemas · **`partially_completed`** · chunking · rate-limit queue |
| 07 | `07_Agentic_Tools_State_Evals_Guardrails.ipynb` | ₹8 | State · **checkpoint + resume** · tracing · PII redaction · **the eval harness** |
| 08 | `08_Voice_Agent_Latency_Barge_in_Telephony.ipynb` | ₹12 | Latency budget · full agent loop · **barge-in** · telephony · Pipecat/LiveKit |
| 09 | `09_Framework_Interop_LangChain_LangGraph_CrewAI_n8n.ipynb` | ₹6 | LangChain · LangGraph · CrewAI · n8n · **same task, four frameworks, one endpoint** · nine interop gotchas found live |
| 10 | `10_MCP_Voice_Agents_With_Sarvam_MCP_Server.ipynb` | ₹9 | 30 MCP tools, zero wrappers · **tool-choice accuracy measured** · the benchmark that refused to cooperate · schema-token cost |
| 11 | `11_Context_Engineering_Markdown_llms_txt_Context7_Skills.ipynb` | ₹4 | Markdown · llms.txt · Context7 · **authoring an Agent Skill** · every layer scored against a 14-rule rubric |
| 12 | `12_Product_Economics_Build_vs_Buy_Benchmarks.ipynb` | ₹3 | Cost models · **build vs buy** · self-hosting crossover · benchmark your own audio |

**Total: ~₹78 of the ₹1000 free credit** — under 8% of what a new account starts with.

> **Lab 11 is the cheap one (₹4) and mostly offline** — it fetches docs and writes
> files rather than calling APIs. That makes it the easiest one to put in front of a
> large group: high value, near-zero credit burn, and everyone leaves with tooling
> that makes every other lab easier.

---

## Read this before you judge any lab

**[`SESSION_FINDINGS_2026-08.md`](SESSION_FINDINGS_2026-08.md) is the most useful file
in this folder.** It is the engineering log from the debugging session that produced
the current state of these notebooks — every correction listed there was found by
running code and reading installed library source, not by consulting documentation
and hoping.

Several things in these labs contradict what you will read elsewhere, including
earlier versions of this very repository. Those contradictions are deliberate and
each one is explained in that file. The three worth knowing before you start:

| Widely repeated | What we actually measured |
|---|---|
| "Pass `sample_rate=8000` for telephony audio" | Not a REST parameter at all — raises `TypeError`. The WAV header already carries it. It belongs to the **streaming** paths, where raw PCM has no header. |
| "The `openai/` prefix is required for CrewAI" | Was true for older litellm-only crewai. On crewai 1.14.6 provider auto-inference makes the bare name work — **`base_url` is what actually matters.** Without it, *both* forms hit real OpenAI with a Sarvam key. |
| "MCP adds latency to the hot path" | Our own three-run benchmark showed MCP **faster** — because one 3.6-second outlier wrecked the direct-SDK mean. n=3 over a live network measures variance, not protocol overhead. The lab now teaches that lesson instead. |

---

## How to run

```bash
pip install -r ../requirements.txt
echo 'SARVAM_API_KEY=sk_your_key_here' > .env
jupyter lab
```

Start with **00**. It writes `cost_meter.py`; every other lab imports the meter from
there rather than redefining it, so a rate change is a one-file edit. A working copy
of `cost_meter.py` is committed alongside the notebooks, so any lab runs standalone —
Lab 00 is where you see how it is built and why each rate is what it is. Everything
else can be run in any order, though 02→03→04, 05→07→08 and 09→10→11 build on each
other.

**Get a key** at [indus.sarvam.ai](https://indus.sarvam.ai/) — new accounts include
₹1000 of credit, so the whole series uses well under a tenth of it.

---

## Picking a subset

The labs are independent enough to be taken in any order and in any combination —
there is no prescribed running order and no assumed length. A few properties worth
knowing when you choose:

| If you want… | Reach for |
|---|---|
| One lab that touches every API | **01** — the whole platform in a single script |
| The cheapest lab to run for a large group | **11** — ₹4, mostly offline, no telephony |
| The labs that build on each other | 02→03→04 · 05→07→08 · 09→10→11 |
| The credit-hungry ones to plan around | 06, 08, 10 |
| The commercial argument | **12**, which leans on the meter threaded through all thirteen |

**00 first** if you want the meter explained. A ready-made `cost_meter.py` ships in
this folder, so no lab is blocked on it.

---

## The teaching design

**Every lab prints rupees.** The `CostMeter` from Lab 00 is threaded through all
thirteen. Costing every call is what separates this from an API tour, and it is what
makes Lab 12 land. Lab 10 goes further and shows what happens when the meter goes
**blind** — MCP tool calls bill you without telling your notebook.

> **On the meter's accuracy.** It is a *conservative upper bound*, computed from
> published rates. Actual billing is typically slightly lower, because server-side
> prompt caching, free-tier credit and invoice rounding are not modelled. The rates
> are dated August 2026 — verify at
> [docs.sarvam.ai](https://docs.sarvam.ai/api/getting-started/pricing) before quoting
> any figure to a customer.

**Every gotcha is a deliberate experiment, not a warning box.** Participants *cause*
each failure and then fix it:

| Lab | The failure they trigger on purpose |
|---|---|
| 00 | `content is None` — reasoning eats `max_tokens` |
| 02 | `sample_rate=` on the REST path → `TypeError` — then learn where it *does* belong |
| 02 | `async with` on the sync `SarvamAI` streaming client → protocol `TypeError` |
| 04 | `output_script` silently ignored on `sarvam-translate` — HTTP 200, wrong script |
| 05 | `.create()` vs `.completions()` across the two SDKs |
| 06 | All four Document AI naming gotchas, in one cell |
| 06 | `partially_completed` silently losing pages |
| 07 | A prompt regression caught by the eval harness |
| 09 | MCP tool results arrive as a **list** of content blocks → Sarvam 400s on `tool.content` |
| 09 | `crewai_tools.MCPServerAdapter` given a plain dict → routed to SSE → `TypeError` |
| 10 | MCP tool calls bill real rupees while the meter prints ₹0.00 — wrap and meter |
| 11 | A context-free assistant writes `.create()`, invents params, omits `model=` |

**Every lab ends with a checkpoint and "Try this."** The checkpoint is what you poll
the room on. The exercises are the homework, and several are genuinely open —
"benchmark WER on 10 recordings from your own domain" is the one that turns a
participant into a customer.

---

## Notes for the coach

**Lab 01 is the one you run live.** Everything else is either pre-work or reference.
Run it cell by cell, and when you reach the TTS cell, ask the room to change
`MY_LANGUAGE` to their own and drop the audio in chat. The flood of Tamil, Bengali,
Marathi and Odia clips is your best screenshot of the session.

**Lab 08 runs in text mode by default.** No telephony account needed — it synthesises
the caller's side. Only move to a real phone number once the logic works. Telephony
setup has derailed more workshops than any other single thing.

**Labs 06, 08 and 10 are the credit-hungry ones.** For a room of 30 on free tier,
stagger Lab 06 by table (Document AI is capped at **10 requests/minute on every
plan**) and cap Lab 08 to the text-mode sections.

**Restart the kernel between Lab 09's interop sections.** Several of that lab's traps
are stale-kernel-state traps by nature — `crewai`'s litellm import is cached at first
module load, and the tool-metering wrapper in Lab 10 is not idempotent (re-running the
cell stacks another layer and doubles every timing print).

---

## Known things to verify before you teach

These move faster than any documentation:

1. **The changelog.** [`docs.sarvam.ai/api/getting-started/changelog`](https://docs.sarvam.ai/api/getting-started/changelog)
   — check it the week you teach. As of these labs: `saaras:v4` is callable,
   `saaras:v3-realtime` powers the realtime endpoint, **`bulbul:v2` was deprecated on
   2026-08-27** and `sarvam-m` / `sarvam-30b` are phased out in favour of
   `sarvam-105b`.
2. **Speaker names are model-version-specific.** The `bulbul:v2` voices
   (`anushka`, `karun`, …) do **not** exist on v3 and raise `BadRequestError`. The
   labs use v3 voices throughout (`pooja`, `shubh`, `rahul`, …).
3. **SDK version drift.** `speech_to_text_realtime_streaming` and its
   `RealtimeAudioInput` / `RealtimeEnd` types arrived in `sarvamai==0.1.30` and do not
   exist in `0.1.28`. Check `pip show sarvamai` before assuming a surface exists.
4. **Samvaad's ₹3.50/min** — it is undocumented whether that bundles telephony. Lab 12
   shows the comparison both ways and flags the uncertainty. Do not quote it to a
   customer until you have confirmed.
5. **SageMaker instance pricing** in Lab 12 is indicative. Put your own region's real
   number in before showing a crossover to a customer.

---

## Sample data

The labs generate their own test audio and PDFs via TTS and reportlab, so they run
with no external files. **They are considerably better with real data** — a genuine
call recording, a scanned Indic form, a customer FAQ in your own language. Ask
participants to bring one artefact from their own work.

```
Labs/
├── 00..12 notebooks
├── build/                         generator scripts — edit these, not the .ipynb
├── SESSION_FINDINGS_2026-08.md    the engineering log; read it
├── data/                          created on first run (sample audio, test PDF)
└── out/                           created on first run (generated audio, extracted JSON)
```

## Regenerating

The notebooks are **generated**. Edit the scripts in `build/`, not the `.ipynb` files —
it keeps the thirteen consistent and means a fix to the shared header propagates
everywhere.

```bash
cd build
pip install nbformat
python3 gen_a.py    # labs 00-04
python3 gen_b.py    # labs 05-07
python3 gen_c.py    # labs 08, 12
python3 gen_d.py    # lab 09      (framework interop)
python3 gen_e.py    # labs 10-11  (MCP voice agents · context engineering)
```

> **Regenerating discards saved outputs.** The committed notebooks carry real executed
> results; a fresh generation produces empty cells. Regenerate when you are changing
> content, then re-run the notebook before committing if you want the outputs back.
