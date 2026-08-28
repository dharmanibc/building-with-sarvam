---
name: sarvam-sdk-gotchas
description: Correct signatures and known traps for the Sarvam AI Python SDK (sarvamai). Use whenever writing, reviewing, or debugging Python that calls Sarvam - speech_to_text, text_to_speech, chat.completions, text.translate, doc_ai - or that wires Sarvam into LangChain, LangGraph, CrewAI, n8n or an MCP client. Prevents the common failures - wrong constructor kwarg, a .create() method that does not exist, deprecated model names, sample_rate on the REST path, reasoning consuming the whole token budget, and Document AI parameter naming.
license: Apache-2.0
compatibility: Python 3.10+, sarvamai>=0.1.30, openai>=2.41
metadata:
  author: AIVidhya4Sarvam
  version: "1.0"
  source: https://github.com/dharmanibc/building-with-sarvam
---

# Sarvam SDK — correct signatures and known traps

Sarvam's API is OpenAI-compatible in shape but **not** identical in surface. The most
common failure mode is writing code that looks right because it matches OpenAI's
conventions, and fails at runtime because it does not match Sarvam's.

Everything below was established by running code and reading installed library source.
When this file disagrees with a memory of "how the SDK works", prefer this file — and
when it disagrees with the live SDK, prefer the SDK and fix this file.

## Client construction

```python
from sarvamai import SarvamAI          # only SarvamAI / AsyncSarvamAI are exported

API_KEY = os.environ.get("SARVAM_API_KEY")
assert API_KEY, "Set SARVAM_API_KEY"    # validate BEFORE constructing
client = SarvamAI(api_subscription_key=API_KEY)
```

- The kwarg is **`api_subscription_key`**, not `api_key`.
- `SarvamAI()` with empty parens does **not** raise — the constructor defaults to
  `os.getenv("SARVAM_API_KEY")`. It will silently work when that variable happens to be
  set and fail confusingly when it is not. Always validate explicitly.
- `from sarvamai import Audio, Chat` does not exist. There are no such top-level
  exports.
- Every response is a Pydantic-style object. Use attribute access
  (`r.choices[0].message.content`, `r.transcript`), never dict subscripting.

## Current model names

| Use | Correct | Deprecated / not real |
|---|---|---|
| Chat | `sarvam-105b` | `sarvam-m`, `sarvam-30b` |
| STT | `saaras:v3`, `saaras:v4` | `saarika:v1` (never existed) |
| STT realtime | `saaras:v3-realtime` | — |
| TTS | `bulbul:v3` | `bulbul:v2` (deprecated 2026-08-27) |

**Always pass `model=` explicitly.** Defaults drift between releases, and a script that
relies on one changes behaviour silently.

## Chat completions

```python
r = client.chat.completions(                 # NOT .completions.create(...)
    model="sarvam-105b",
    messages=[{"role": "user", "content": "..."}],
    max_tokens=800,
    reasoning_effort=None,                   # see below
)
text = r.choices[0].message.content
```

- **There is no `.create()`.** `client.chat.completions.create(...)` raises
  `AttributeError`. `client.chat(...)` bare is also wrong.
- **Reasoning is ON by default** (`reasoning_effort="low"`). With a small `max_tokens`,
  reasoning consumes the entire budget and `content` comes back **`None`**. This is the
  single most common silent failure on the platform. Either raise `max_tokens` or pass
  `reasoning_effort=None`.
- Omitting the field and sending explicit `null` are **different signals**: omitted →
  Sarvam's own default; explicit null → reasoning disabled. Any layer that strips
  `None` values before serialising cannot produce the second case.

## Speech to text

```python
with open("call.wav", "rb") as f:
    r = client.speech_to_text.transcribe(     # NOT client.speech_to_text(...)
        file=f, model="saaras:v3",
        language_code="hi-IN", mode="transcribe",
    )
print(r.transcript)
```

- **`sample_rate` is not a REST parameter.** Passing it raises
  `TypeError: transcribe() got an unexpected keyword argument 'sample_rate'`. A `.wav`
  header already declares the rate, so 8 kHz telephony audio works on the REST path
  with nothing extra. `sample_rate` is required only on the **streaming** paths, where
  raw PCM carries no header.
- **Do not pass `input_audio_codec` for a recognised container** (`.wav`, `.mp3`, …) —
  it is auto-detected. It exists for raw PCM only (`pcm_s16le`, `pcm_l16`, `pcm_raw`).
  Values like `"amr_wb"` / `"amr_nb"` are not in the enum; only bare `"amr"` is. This
  parameter is a frequent hallucination — if you find yourself adding it because the
  audio is "telephony", do not.
- `SarvamAI` is **synchronous**. `speech_to_text_streaming.connect(...)` is a *sync*
  context manager — `async with` on it raises a protocol `TypeError`. Use `with`, or
  switch to `AsyncSarvamAI`.
- Streaming audio is sent as **base64 text**, never raw bytes.
- Realtime `start_s` / `end_s` are `None` unless the connection was opened with
  `return_timestamps=True`. Formatting them with `:.2f` unconditionally will crash.

## Text to speech

```python
a = client.text_to_speech.convert(
    text="नमस्ते",
    language_code="hi-IN",        # NOT target_language_code
    model="bulbul:v3",
    speaker="pooja",              # v3 voice
)
```

- The kwarg is **`language_code=`** on TTS. (`target_language_code=` is correct on
  `text.translate` — the two APIs differ, which is exactly why this is easy to get
  wrong.)
- **Speaker names are model-version-specific and do not overlap.** v2 voices
  (`anushka`, `abhilash`, `manisha`, `vidya`, `arya`, `karun`, `hitesh`) raise
  `BadRequestError` on v3. Valid v3 speakers include `pooja`, `shubh`, `priya`, `neha`,
  `ishita`, `rahul`, `dev`, `aditya`, `ritu`, `kavya`, `amit`, `shreya`, `varun`.
- HTTP streaming is `client.text_to_speech.convert_stream(...)` on the plain client.
  `text_to_speech_streaming` is the **WebSocket-only** client and has no `.convert()`.
- On the WebSocket client, `connect()` accepts only `model` / `send_completion_event`;
  `language_code` and `speaker` go through `ws.configure(...)` **after** connecting.
- Pronunciation dictionaries are created by **uploading a JSON file**
  (`pronunciation_dictionary.create(file=...)` with
  `{"pronunciations": {lang: {word: pronunciation}}}`), not by passing `name=`/`entries=`.
  `dict_id` is honoured **only on `bulbul:v3`** — on v2 it is a silent no-op.

## Document AI

```python
job = client.doc_ai.extract(
    file=[("form.pdf", handle, "application/pdf")],   # an ARRAY of tuples
    schema=json.dumps(schema_dict),                   # a JSON STRING
    language="hi-IN",                                 # NOT language_code
    output_format="md",                               # NOT "markdown"
)
```

Four naming traps, each failing differently:

| Wrong | What happens |
|---|---|
| `language_code=` | **Silently ignored** — no error, wrong behaviour |
| `output_format="markdown"` | HTTP 400 |
| `schema={...}` as a dict | `AttributeError: 'dict' object has no attribute 'read'` |
| `file=open(...)` bare | Type error — it must be an array of tuples |

Also:

- **The extract schema does not support a `required` key** — `SCHEMA_INVALID: schema
  property contains unsupported key "required"`. Every field is effectively optional;
  steer must-have fields through a sharper `description`.
- Digitise per-page results may arrive as **layout blocks** (`page.blocks[*].text`,
  ordered by `reading_order`) rather than the documented `page.content` string. Code
  that assumes `page.content` silently gets zero characters. Check both shapes.
- Always poll `get_status()` / `wait_until_complete()` before `get_results()`.
- **`partially_completed` is a terminal state.** A 20-file job can report `Completed`
  overall while individual files failed. Reconcile counts: files in == files out.

## Framework interop

**LangChain / LangGraph**

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent    # NOT langgraph.prebuilt.create_react_agent

llm = ChatOpenAI(
    model="sarvam-105b",
    base_url="https://api.sarvam.ai/v1",
    api_key=os.environ["SARVAM_API_KEY"],
    reasoning_effort=None,                   # a declared field — pass it DIRECTLY
)
```

- `reasoning_effort` is now a first-class OpenAI parameter and a declared field on
  `ChatOpenAI`. Routing it through `model_kwargs` still works but raises a
  `UserWarning`.
- `langgraph.prebuilt.create_react_agent` is deprecated as of LangGraph v1.0.

**MCP via `langchain-mcp-adapters`**

- Tool results arrive as a **list of content blocks**; Sarvam requires a `tool` message's
  `content` to be a plain **string** and returns
  `body.messages.N.tool.content : Input should be a valid string` otherwise. Fix with
  `MultiServerMCPClient(..., tool_interceptors=[...])` that flattens results to a
  string — and **cover the error path too**, or failed tool calls keep 400ing.
- Not every payload is text: `sarvam_tools_tts_speak` returns `AudioContent`. An
  interceptor that extracts only `"text"` leaves the model an uninformative stub, and it
  may call the tool again, repeatedly, at real cost. Acknowledge every content type.
- After building an intercepted client, **re-fetch its tools** and bind those. Reusing
  the earlier client's tool objects is a silent no-op that looks exactly like "the
  interceptor does not work". Give the fixed objects distinct names.

**CrewAI**

```python
from mcp import StdioServerParameters        # a plain dict routes to SSE and dies

llm = LLM(model="openai/sarvam-105b",
          base_url="https://api.sarvam.ai/v1",
          api_key=os.environ["SARVAM_API_KEY"],
          max_tokens=4000)                   # reasoning cannot be disabled here
```

- `MCPServerAdapter` chooses its transport from the Python **type** of its argument, not
  its keys. A dict with `command`/`args` goes to `sse_client(**params)` and fails with
  `TypeError: sse_client() got an unexpected keyword argument 'command'`.
- The missing dependency behind "mcp package missing" is usually **`mcpadapt`**
  (`pip install mcpadapt` or `'crewai-tools[mcp]'`), not `mcp`.
- **`crewai.LLM` cannot disable reasoning.** `call()` strips `None`-valued params before
  serialising, so `reasoning_effort=None` never reaches Sarvam. Raise `max_tokens`
  instead, and expect run-to-run variance rather than a monotonic improvement.
- On crewai 1.14.6 a bare model name works (provider auto-inference). **`base_url` is
  what matters** — without it, both prefixed and unprefixed forms hit real OpenAI.
- crewai's litellm import is cached at first module load; installing litellm mid-session
  requires a kernel restart.
- A failed task restarts **from scratch** (`max_retry_limit` default 2, so 3 attempts),
  which is why one failure prints as 1–3 repeated ERROR lines.

**Jupyter**

- `await crew.kickoff_async()` — it is an `async def`; calling it without `await` yields
  a coroutine object and a `RuntimeWarning`.
- Editing a `.ipynb` on disk does not change variables already in a running kernel.
  Re-run the upstream cell that rebuilds `tools` / `llm` / `mcp`, not just the
  downstream one.
- `pip install X` in a different environment than the kernel is invisible to it. Check
  with `import sys; print(sys.executable)`, and install via
  `!{sys.executable} -m pip install X`.

## Cost

Every call above is billed. Pair this skill with `sarvam-cost-metering` so generated
code tracks spend by default.
