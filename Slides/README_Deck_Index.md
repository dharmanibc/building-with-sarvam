# Deck Index — Building with Sarvam

**179 slides across 10 decks.** Every deck has speaker notes on the key slides.

| # | File | Slides | Purpose |
|---|---|---|---|
| 01 | `01_Opening_India_AI_Sovereignty.pptx` | 13 | Independence Day framing, the language gap, sovereignty as a commercial fact, agenda, setup check |
| 02 | `02_The_Sarvam_Stack_After_Epoch.pptx` | 24 | Five-layer map, every model, all 12 Epoch launches, **announced vs callable**, products, tooling, deployment |
| 03 | `03_Speech_and_Language_APIs.pptx` | 20 | Saaras five modes, three delivery paths, **where `sample_rate` actually belongs**, Bulbul, pronunciation dicts, translate/transliterate/LID |
| 04 | `04_Sarvam105B_and_Document_AI.pptx` | 18 | Base-URL swap, `reasoning_effort`, every chat parameter, prompt caching, tool calling, Vision digitise/extract |
| 05 | `05_Indus_and_Agentic_Platform.pptx` | 15 | Indus six tools, agent anatomy, "LLMs reason code executes", MCP, evals, build-vs-platform |
| 06 | `06_Kivi_SarvamCode_and_Tooling.pptx` | 13 | Kivi, Kaze, Sarvam Code, Agent Skills, MCP server, llms.txt |
| 07 | `07_Unit_Economics_and_Business.pptx` | 18 | The ₹7.90 derivation with chart, sensitivities, vs human agent, **build vs buy at ₹3.50/min**, pricing models, opportunity map |
| 08 | `08_Capabilities_Limits_and_Next.pptx` | 14 | Honest capability map, **the gotchas list**, "why not OpenAI", FAQ, 30-day plan, the offer |
| 09 | `09_Framework_Interop_LangChain_LangGraph_CrewAI_n8n.pptx` | 16 | The base-URL swap, four ways. 30 MCP tools. **Nine interop gotchas, every one found live.** Pairs with Lab 09 |
| 10 | `10_MCP_and_Context_Engineering.pptx` | 18 | Runtime vs build-time context. MCP's three prices. Markdown · llms.txt · Context7 · Agent Skills, each measured. Pairs with Labs 10 and 11 |

---

## Slides that contradict common advice

Several slides here state things you will find contradicted elsewhere on the internet,
including in code that LLMs generate confidently. Each was established by running code
and reading installed library source — the method is documented in
[`../Labs/SESSION_FINDINGS_2026-08.md`](../Labs/SESSION_FINDINGS_2026-08.md).

Expect these to be challenged from the floor. Each is worth defending.

| Deck | Widely repeated | What these decks assert |
|---|---|---|
| 03 | "Pass `sample_rate=8000` for telephony audio" | Not a REST parameter — it raises `TypeError`. The WAV header carries it. Required only on the streaming paths, where raw PCM has no header |
| 03 | `target_language_code=` on TTS, speaker `anushka` | TTS uses `language_code=`. `bulbul:v2` was deprecated 2026-08-27 and its voices raise `BadRequestError` on v3 — use a v3 voice such as `pooja` |
| 02, 04 | `sarvam-m` / `sarvam-30b` as current models | Both phased out. `sarvam-105b` is the current chat model |
| 09 | "`reasoning_effort` is a Sarvam-only extra" | It is a typed kwarg in `openai>=2.41` and a declared field on `ChatOpenAI`. Pass it directly — `model_kwargs` raises a `UserWarning` |
| 09 | "CrewAI needs the `openai/` prefix or litellm throws" | On crewai 1.14.6 provider auto-inference makes the bare name work. **`base_url` is what matters** — without it both forms reach real OpenAI |
| 09 | CrewAI MCP configured with a plain dict | `MCPServerAdapter` picks its transport from the Python **type**. A dict routes to SSE and fails; pass `mcp.StdioServerParameters(...)` |
| 09, 10 | `langgraph.prebuilt.create_react_agent` | Deprecated in LangGraph v1.0 → `from langchain.agents import create_agent` |
| 09, 10 | Assorted tool counts for the Sarvam MCP server | **30 tools — 23 runtime (`sarvam_tools_*`) + 7 builder (`sarvam_code_*`)** |
| 10 | "MCP adds latency to the hot path" | Our own n=3 benchmark showed MCP **790 ms faster** — one 3.6 s outlier wrecked the direct-SDK mean. The slide teaches benchmark scepticism rather than a performance claim |

---

## How these are built to be used

**These decks hold more than any one session will show.** That is deliberate. Decks
02, 03, 04 and 07 carry far more reference detail than a talk needs — they exist so
that:

- when code is running and you need to fill the wait, you have somewhere to go
- when someone asks about a parameter you did not plan to cover, you have a slide
- the same decks serve a short talk and a long course without a rebuild
- participants who ask for the deck afterwards get something worth keeping

**Decks 09 and 10 go deeper than an introduction needs.** Treat them as appendix
material and pull them in when the audience is ready for them.

Pick your own subset. Nothing here assumes a particular running order or length.

## Slides you should not skip

| Deck · slide | Why |
|---|---|
| 02 · "Announced is not the same as callable" | Your single strongest credibility slide. Nobody else has assembled this |
| 03 · "The five modes" | The centrepiece of the speech segment |
| 03 · "Where `sample_rate` belongs — and where it does not" | A correction to an earlier version of this same deck. Say so out loud; a room that hears you fix your own slide trusts the rest of it more |
| 04 · "Your existing code already works" | Reframes the whole platform in one demo. Do it live |
| 07 · "Where the money actually goes" | The chart. 60% is TTS, 9% is the LLM |
| 07 · "Your build versus Samvaad" | Your most original material |
| 08 · "The gotchas list" | Tell them to screenshot it. They will |
| 09 · "The interop gotchas — every one found live" | Nine failures that each cost real hours. The most useful slide in the appendix |
| 10 · "Price one — the ₹ meter goes blind" | Nobody warns about this. Costs nothing to explain, saves a month of confused billing |
| 10 · "The measurement that refused to cooperate" | Teaching a room to distrust their own three-sample benchmark is worth more than any number |
| 10 · "The recipe card the cook actually keeps" | The analogy that makes Agent Skills land in one sentence |

## Design system

- **Palette:** deep midnight navy dominant, saffron accent, teal secondary — Indian without being a flag
- **Type:** Cambria headings, Calibri body (both ship with Office, both render true-to-width)
- **Motif:** rounded cards with circular glyph badges, carried across all ten decks
- **Logo:** `AIVidhya4Sarvam`, top-right, inherited from `build/theme.js` by every slide
- **No colour emoji** anywhere — they render as empty boxes on many systems. Only BMP symbols (★ ✓ ✕ ⚡ ₹ ♪ ⇄ §) are used

## Before you present

1. Open each deck once in **your own** PowerPoint/Keynote and page through it — fonts and rendering differ from the build environment.
2. Check the speaker notes (View → Notes). The presenter guidance is there, not on the slides.
3. Deck 07's chart is a native PowerPoint chart — you can edit the numbers live if someone challenges them.
4. `build/` contains the generator scripts. To change content, edit `build/dNN.js` and run `node dNN.js` — **do not hand-edit the .pptx.**
5. The logo and the `AIVidhya4Sarvam · Building with Sarvam` footer come from `build/theme.js` — every deck inherits both automatically. Change them once there, rebuild, done.

> **Logo geometry note.** `LOGO_BIG` and `LOGO_SMALL` in `theme.js` are both kept
> fully inside the 13.333 × 7.5 in slide with a 0.34" right margin. An earlier version
> placed the big logo at `x=11.330 w=2.468`, whose right edge landed at 13.798 — 0.465"
> past the slide — so PowerPoint clipped it on every title and section slide. Content
> slide titles are capped at `HEADW` so a long title can never run underneath the mark.

## Regenerating

```bash
cd build
npm install pptxgenjs               # first time only
node d01.js                         # rebuilds one deck
for f in d??.js; do node $f; done   # rebuilds all ten
```

> Note the glob is `d??.js`, not `d0*.js` — the latter silently skips deck 10.

## PDFs

`../pdf/` carries a rendered PDF of every deck. Those are what GitHub previews inline,
so they are the fastest way to read a deck without downloading anything. Regenerate
them with:

```bash
soffice --headless --convert-to pdf build/*.pptx --outdir pdf/
```
