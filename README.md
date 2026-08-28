<!-- AIVidhya4Sarvam · Building with Sarvam -->

# Building with Sarvam

**An open teaching kit for the Sarvam AI stack — India's Indic-language AI platform.**

13 hands-on Jupyter labs and 10 slide decks that take a working Python developer from
*"I have an API key"* to *"I have shipped an Indic voice agent and I can defend its
unit economics."*

Every API call in every lab prints what it cost, in rupees. The whole series runs
inside the ₹1000 free credit.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Labs](https://img.shields.io/badge/labs-13-orange.svg)](Labs/README_Lab_Index.md)
[![Decks](https://img.shields.io/badge/decks-10-teal.svg)](Slides/README_Deck_Index.md)

---

## What makes this different

**85% of the code cells here have been executed against the live API**, and the saved
outputs are real — real transcripts, real latencies, real rupee totals. Where a
measurement disagreed with what we expected, **the lab teaches the measurement, not
the expectation.**

That produced a file we think is more valuable than any individual lab:
**[`Labs/SESSION_FINDINGS_2026-08.md`](Labs/SESSION_FINDINGS_2026-08.md)** — the
engineering log from a long live-debugging session. Every correction in it was found
by running code and reading installed library source, not by reading documentation and
hoping. A sample of what is in there:

- `sample_rate` is **not** a REST parameter on `speech_to_text.transcribe()` — it
  raises `TypeError`. The WAV header already carries it. It belongs to the streaming
  paths, where raw PCM has no header. *(A lot of advice online says otherwise.)*
- The `openai/` prefix for CrewAI is **no longer required** on crewai 1.14.6 —
  provider auto-inference handles it. `base_url` is what actually matters; without it,
  both the prefixed and unprefixed forms quietly hit real OpenAI with a Sarvam key.
- `crewai.LLM` **cannot disable reasoning at all** — `call()` strips every `None`
  param before serialising, so `reasoning_effort=None` never reaches the API.
- A hand-written gotchas rubric scored a generation **8/8 "no gotchas"** while the code
  carried six real defects none of the eight rules described. An incomplete rubric does
  not merely miss mistakes; it manufactures confidence.
- Our own MCP-vs-direct-SDK benchmark showed MCP **faster** — because one 3.6-second
  outlier wrecked the direct-SDK mean over three runs. The lab now teaches benchmark
  scepticism instead of the conclusion we set out to demonstrate.

---

## Quick start

```bash
git clone https://github.com/dharmanibc/building-with-sarvam.git
cd building-with-sarvam
pip install -r requirements.txt

# Free key + ₹1000 credit: https://indus.sarvam.ai/
echo 'SARVAM_API_KEY=sk_your_key_here' > Labs/.env

cd Labs && jupyter lab 00_Setup_and_the_Cost_Meter.ipynb
```

Start with **Lab 00** — it writes `cost_meter.py`, which every later notebook imports.
A working copy ships in `Labs/`, so any lab runs standalone; Lab 00 is where you see
how the meter is built and why every rate is what it is.

---

## What is in here

| | |
|---|---|
| **[`Labs/`](Labs/README_Lab_Index.md)** | 13 notebooks · 440 cells · 234 code cells · ~₹78 of the ₹1000 free credit |
| **[`Slides/`](Slides/README_Deck_Index.md)** | 10 decks · 179 slides · speaker notes throughout |
| **[`skills/`](skills/)** | 2 Agent Skills — drop-in context so your coding assistant writes Sarvam code that runs |
| **[`pdf/`](pdf/)** | Every deck as a PDF — GitHub previews these inline, no download needed |
| **[`Labs/SESSION_FINDINGS_2026-08.md`](Labs/SESSION_FINDINGS_2026-08.md)** | The engineering log. Start here if you only read one file |

### The arc

| Labs | What you build |
|---|---|
| **00–01** | Setup, the ₹ cost meter, and every API in one script |
| **02–04** | Speech in, speech out, and the language layer — 23 Indian languages |
| **05–06** | Sarvam-105B reasoning and tool calling; Document AI on Indic scripts |
| **07–08** | Agents with state, checkpointing and evals; a voice agent inside an 800 ms budget |
| **09–11** | Your existing framework over Sarvam; MCP at runtime; context engineering for coding assistants |
| **12** | The business model — build vs buy, self-hosting crossover, benchmark your own data |

### Two Agent Skills you can use without running anything

[`skills/`](skills/) carries two drop-in context files for Claude Code, Cursor,
Windsurf or any agent implementing the
[Agent Skills spec](https://agentskills.io/specification):

- **[`sarvam-sdk-gotchas`](skills/sarvam-sdk-gotchas-skill.md)** — correct signatures
  and known traps across the whole SDK, so generated code stops inventing methods
- **[`sarvam-cost-metering`](skills/sarvam-cost-metering-skill.md)** — makes generated
  code track spend in rupees by default, including the MCP case where usage is invisible

One stops the code being wrong; the other stops it being untracked. Install both, or
just paste them in front of a prompt — a skill is only context, delivered
automatically.

---

## Coverage

What this kit teaches hands-on, and what it does not. Stated plainly so you can tell at
a glance whether it covers what you came for.

| Capability | Status | Where |
|---|---|---|
| Chat / reasoning / tool calling (`sarvam-105b`) | **Covered in depth** | Labs 00, 05, 07 |
| Speech to text (Saaras) — 5 modes, REST · batch · streaming · realtime | **Covered in depth** | Lab 02 |
| Text to speech (Bulbul) — voices, controls, streaming, telephony formats | **Covered in depth** | Lab 03 |
| Translate · transliterate · language ID | **Covered in depth** | Lab 04 |
| Document AI — digitise, extract, schemas, job lifecycle | **Covered in depth** | Lab 06 |
| Agents — state, checkpointing, evals, guardrails | **Covered in depth** | Lab 07 |
| Voice agents — latency budget, barge-in, telephony | **Covered in depth** | Lab 08 |
| Framework interop — LangChain, LangGraph, CrewAI, n8n | **Covered in depth** | Lab 09 |
| MCP server — all 30 tools, tool-choice accuracy, schema cost | **Covered in depth** | Lab 10 |
| Context engineering — Markdown, llms.txt, Context7, Agent Skills | **Covered in depth** | Lab 11 |
| Unit economics — build vs buy, self-hosting crossover | **Covered in depth** | Lab 12 |
| Pronunciation dictionaries | Covered, briefly | Lab 03 |
| Prompt caching | Covered, briefly | Lab 05 |
| **Dubbing & localisation** (`client.dubbing`) | **Not yet — next up** | listed in Lab 10's tool inventory only |
| **Voice cloning** (`voice_cloning`, `voice_id`) | **Not yet** | arrives with dubbing |
| Indus, Samvaad, Arya as products | Discussed, not built on | Deck 05 |
| Self-hosting / VPC deployment | Modelled financially, not deployed | Lab 12 |

**On dubbing specifically.** It is a real gap and it is the next thing to land. Note
that it is a *composite* capability — STT plus translate plus TTS plus voice cloning,
packaged — and every one of those primitives is already covered here in depth. A planned
Lab 13 will cover the job lifecycle (`create` → `start` → poll → export), the language
matrix, voice cloning and its consent implications, export shapes (video / audio / SRT),
and the arithmetic of dubbing-as-a-service versus assembling the pipeline yourself.

Anything marked *not yet* is a genuine invitation — see
[CONTRIBUTING.md](CONTRIBUTING.md).

---

## Both artefacts are generated — edit the generators

Neither the notebooks nor the decks are hand-authored. Editing a `.ipynb` or `.pptx`
directly will be overwritten on the next build.

```bash
# Notebooks
cd Labs/build && python3 gen_a.py gen_b.py gen_c.py gen_d.py gen_e.py

# Decks
cd Slides/build && for f in d??.js; do node $f; done
```

The shared design system lives in `Slides/build/theme.js`; the shared notebook header,
`SETUP` cell and meter import live in `Labs/build/nbkit.py`. Change either once and
every artefact inherits it. Lab 00 writes `cost_meter.py`; Labs 01–12 import it, so a
rate change is a one-file edit rather than thirteen.

Both were drafted with AI assistance and then verified by execution against the live
API — which is how most of `SESSION_FINDINGS` came to exist, since running the code kept
disproving things the drafting had asserted confidently. Lab 11 turns that experience
into method.

---

## A note on the cost meter

It is a **conservative upper bound**, not an invoice. It computes from published rates
(dated August 2026) and does not model server-side prompt caching, free-tier credit or
invoice rounding — all of which push the real bill slightly *lower*. Verify current
pricing at [docs.sarvam.ai](https://docs.sarvam.ai/api/getting-started/pricing) before
quoting any figure to a customer.

Erring high is deliberate: a student who budgets ₹10 and is billed ₹8 is fine; the
reverse is not.

---

## Contributing

Corrections are the most welcome kind of contribution here — especially ones that
contradict something in these files. If you hit a trap that is not in
`SESSION_FINDINGS_2026-08.md`, that is a bug in the teaching material.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

[Apache 2.0](LICENSE) — use it commercially, teach from it, fork it for your own
workshop. Attribution appreciated, not required.

## Author

**Dr. Bhaveshkumar C. Dharmani** — PhD (ICT), DA-IICT Gandhinagar · Visiting Faculty
(formerly Professor), AIDTM Gandhinagar · Founder, AIVidhya4Sarvam

Contributor to [`sarvamai/sarvam-ai-cookbook`](https://github.com/sarvamai/sarvam-ai-cookbook)

[aividhya4sarvam.in](https://www.aividhya4sarvam.in/) · [aividhya.in](https://www.aividhya.in/) · bhavesh@aividhya.in

---

*Not affiliated with or endorsed by Sarvam AI. Built by a practitioner who teaches this
stack.*
