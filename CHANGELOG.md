# Changelog

Notable changes to this teaching kit. Dates are release dates, newest first.

---

## [1.0.0] — 2026-08-28

Initial public release.

### What is in it

- **13 Jupyter labs** — 440 cells, 234 code cells, ~₹78 of the
  ₹1000 free Sarvam credit. 85% of code cells carry real executed outputs.
- **10 slide decks** — 179 slides with speaker notes, generated from
  `Slides/build/*.js` against a shared design system.
- **2 Agent Skills** in [`skills/`](skills/) — drop-in context for Claude Code, Cursor,
  Windsurf or any agent implementing the Agent Skills spec.
- **[`Labs/SESSION_FINDINGS_2026-08.md`](Labs/SESSION_FINDINGS_2026-08.md)** — the
  engineering log behind the material.

### What this material targets

The Sarvam platform moves quickly, and a lot of Sarvam code on the internet — and a lot
of code that LLMs generate — targets an older surface. These are the versions and API
shapes every lab and deck here assumes. **Check them against
[the changelog](https://docs.sarvam.ai/api/getting-started/changelog) before you teach
from this, and treat any disagreement as a signal that something has moved.**

**Models**

| Use | Current | Do not use |
|---|---|---|
| Chat | `sarvam-105b` | `sarvam-m`, `sarvam-30b` — phased out |
| STT | `saaras:v3` (default), `saaras:v4` | — |
| STT realtime | `saaras:v3-realtime` | — |
| TTS | `bulbul:v3` | `bulbul:v2` — deprecated 2026-08-27 |

**TTS speaker names are model-version-specific and do not overlap.** The v2 voices
(`anushka`, `abhilash`, `manisha`, `vidya`, `arya`, `karun`, `hitesh`) raise
`BadRequestError` on v3. The labs use v3 voices throughout (`pooja`, `shubh`, `priya`,
`neha`, `ishita`, `rahul`, `dev`).

**Library versions**

| Package | Minimum | Why |
|---|---|---|
| `sarvamai` | 0.1.30 | `speech_to_text_realtime_streaming` and its `RealtimeAudioInput` / `RealtimeEnd` types do not exist in 0.1.28 |
| `openai` | 2.41.0 | `reasoning_effort` became a typed kwarg here |
| `langchain` | 1.0 | provides `langchain.agents.create_agent` |
| `langgraph` | 1.0 | `langgraph.prebuilt.create_react_agent` is deprecated |
| `langchain-mcp-adapters` | 0.3.2 | `tool_interceptors` extension point |
| `crewai` | 1.14 | provider auto-inference behaviour described below |

**API surface facts that commonly surprise people**

These are documented in full, with how each was established, in
[`SESSION_FINDINGS_2026-08.md`](Labs/SESSION_FINDINGS_2026-08.md).

- `SarvamAI(api_subscription_key=...)`, not `api_key=`. It also defaults to
  `os.getenv("SARVAM_API_KEY")`, so an empty constructor can silently "work" — validate
  the key explicitly instead of relying on that.
- `client.chat.completions(...)` — there is **no** `.create()`.
- Responses are Pydantic-style objects: `r.choices[0].message.content`, not dict
  subscripting.
- **`sample_rate` is not a REST parameter.** `speech_to_text.transcribe(..., sample_rate=8000)`
  raises `TypeError` — a `.wav` header already carries the rate. It is required only on
  the *streaming* paths, where raw PCM has no header.
- `input_audio_codec` should not be passed for any recognised container. It exists for
  raw PCM only.
- **Chat models default to `reasoning_effort="low"` (reasoning on).** With a small
  `max_tokens`, reasoning can consume the whole budget and `content` returns `None` —
  the most common silent failure across the whole platform.
- Omitting `reasoning_effort` and sending it as `null` are **different signals**:
  omitted gets Sarvam's default; explicit null disables reasoning.
- **`crewai.LLM` cannot disable reasoning.** Its `call()` strips `None`-valued params
  before serialising, so the field never reaches the API. The only lever is a generous
  `max_tokens`.
- TTS uses `language_code=`, not `target_language_code=`.
- Document AI: `language=` (not `language_code=`, which is silently ignored),
  `output_format="md"` (not `"markdown"`, which 400s), `schema=json.dumps(...)` as a
  **string**, and `file=[(name, handle, mime)]` as an **array**. The extract schema does
  not support a `required` key at all.
- `partially_completed` is a **terminal** state. A 20-file batch can report `Completed`
  overall while individual files failed — reconcile counts, always.
- Pronunciation dictionaries are created by uploading a JSON file, and `dict_id` is
  honoured only on `bulbul:v3`.

**Framework interop facts**

- MCP tool results arrive as a **list of content blocks**; Sarvam requires
  `tool.content` to be a plain string and returns 400 otherwise. Fix with
  `tool_interceptors=[…]` on `MultiServerMCPClient`, covering the **error path as well
  as success**.
- `sarvam_tools_tts_speak` returns `AudioContent`, not text. An interceptor that only
  extracts `"text"` leaves the model an uninformative stub, and it may retry the call at
  real cost.
- `crewai_tools.MCPServerAdapter` picks its transport from the Python **type**: a dict
  routes to SSE, `mcp.StdioServerParameters` routes to stdio. A dict with
  `command`/`args` fails with `sse_client() got an unexpected keyword argument 'command'`.
- The dependency behind crewai's "mcp package missing" message is usually **`mcpadapt`**,
  not `mcp`.
- On crewai 1.14.6, a bare model name works — provider auto-inference handles it.
  **`base_url` is what actually matters**; without it, both the prefixed and unprefixed
  forms reach real OpenAI with a Sarvam key.
- The Sarvam MCP server exposes **30 tools**: 23 runtime (`sarvam_tools_*`) and 7
  builder (`sarvam_code_*`).

### Known limitations

- Cost figures are a **conservative upper bound** computed from published rates dated
  August 2026. Prompt caching, free-tier credit and invoice rounding all push the real
  bill lower. Verify at
  [docs.sarvam.ai](https://docs.sarvam.ai/api/getting-started/pricing) before quoting
  anything to a customer.
- The SageMaker instance pricing in Lab 12 is indicative. Substitute your own region's
  rate before showing a self-hosting crossover to anyone.
- Whether Samvaad's ₹3.50/min bundles telephony is undocumented. Lab 12 models it both
  ways and says so.
- Lab 10's MCP-versus-SDK latency comparison is n=3 and its spread exceeds its effect.
  It is retained deliberately, as a lesson in reading your own benchmarks sceptically —
  not as a performance claim.
