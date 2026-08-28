# Session findings — corrections needed across the Sarvam workshop notebooks/decks

Compiled from a long debugging session across Labs 02, 03, 04, 05–08, 10, 11, 12.
Hand this to a review pass before re-shipping the notebooks or the slide decks —
every item below was found live, not theorized, and most were confirmed by reading
the installed library's actual source rather than assumed from memory.

## 1 · Model names — deprecated or never real

- **`sarvam-m` and `sarvam-30b` are deprecated.** Use `sarvam-105b`. It appears as the
  default model in several older notebook cells and in the n8n JSON workflow —
  all instances were swept to `sarvam-105b`.
- **`saarika:v1` and `sarvam-1` are not real model names.** They showed up in an
  LLM-generated (hallucinated) code sample, not in any shipped notebook, but are
  worth flagging as a "looks plausible, isn't real" trap for Lab 11's gotchas list.
- Valid, current names: chat → `sarvam-105b` (`sarvam-m` and `sarvam-30b` are phased out);
  STT → `saaras:v3` (default), `saaras:v4`; TTS →  `bulbul:v3` (`bulbul:v2` depricated now - just yesterday, 26th August).

## 2 · Core SDK signature corrections

| Wrong (seen in the wild / older code) | Correct |
|---|---|
| `SarvamAI(api_key=...)` | `SarvamAI(api_subscription_key=...)` |
| `client.chat.completions.create(...)` | `client.chat.completions(...)` — no `.create` |
| `client.chat(...)` (bare) | `client.chat.completions(...)` |
| `client.speech_to_text(...)` (bare) | `client.speech_to_text.transcribe(file=..., ...)` |
| `response["transcript"]`, `r["choices"][0]["message"]["content"]` | Attribute access: `response.transcript`, `r.choices[0].message.content` — every SDK response is a Pydantic-style object, not a dict |
| `from sarvamai import Audio, Chat` | Does not exist. Only `SarvamAI` / `AsyncSarvamAI` are exported at the top level |
| `speech_to_text.transcribe(..., sample_rate=8000)` | `sample_rate` is **not a REST parameter** — the WAV header carries it. Raises `TypeError`. Only applies on the streaming path (raw samples, no header) |
| `speech_to_text.transcribe(..., input_audio_codec="amr_wb")` / `"amr_nb"` | Neither value exists in the SDK's enum (only bare `"amr"` does), and the parameter shouldn't be passed at all for a WAV/MP3/any recognized container — it's auto-detected. It exists only for raw PCM (`pcm_s16le`, `pcm_l16`, `pcm_raw`), which has no header to detect from |

- **`SarvamAI()` with empty parens does not crash** — confirmed in the installed SDK
  source, the constructor defaults `api_subscription_key` to
  `os.getenv("SARVAM_API_KEY")`, so it silently works if that env var happens to be
  set. Not a hard error, but a standalone script shouldn't depend on an unchecked env
  var — validate explicitly (`API_KEY = os.environ.get(...); assert API_KEY, "..."`)
  before constructing the client, the same way every notebook's header cell already
  does.
- **`input_audio_codec` is a reproducible LLM hallucination, not a one-off.** Two
  independent generations against identical context both invented a codec value —
  `"amr_wb"` then, on rerun, `"amr_nb"` — for a plain `.wav` file, even though the
  fetched STT reference page explicitly says the parameter is unnecessary except for
  raw PCM. The task's own wording ("8 kHz telephony audio") appears to be priming a
  plausible-sounding parameter the model adds unprompted, which is a different
  failure mode from ignoring or misreading something the docs actually showed (see
  §9 for why a "trust the context" system prompt doesn't reliably fix this one).

## 3 · `reasoning_effort` — the parameter that changed meaning mid-session

- Sarvam's chat models default to `reasoning_effort="low"` (reasoning **on**). If
  `max_tokens` is small, reasoning can consume the whole budget and `content` comes
  back `None` — the single most common "silent failure" across every lab.
- **This is now a genuine first-class OpenAI parameter, not a Sarvam-only extra.**
  Confirmed directly in the installed `openai==2.41.0` SDK: `reasoning_effort` is a
  typed kwarg on `chat.completions.create()` (`Literal['none','minimal','low','medium','high','xhigh'] | None`).
  Any earlier note in a deck calling this "not part of the OpenAI standard" is stale. 
- **Passing it correctly differs by layer:**
  - Raw `openai` SDK: can now pass `reasoning_effort=None` directly as a kwarg
    (works because the SDK types it); `extra_body={"reasoning_effort": None}` still
    works too and is more version-agnostic.
  - `langchain_openai.ChatOpenAI`: `reasoning_effort` is now a **declared field** on
    the class. Passing it through `model_kwargs={"reasoning_effort": None}` still
    "works" but triggers a `UserWarning` telling you to pass it directly instead —
    `ChatOpenAI(..., reasoning_effort=None)`.
  - **`crewai.LLM` cannot disable reasoning at all.** Verified in `crewai/llm.py`:
    `call()` builds a params dict and does
    `{k: v for k, v in params.items() if v is not None}` — this strips
    `reasoning_effort` whenever it's `None`, whether you set it explicitly or left
    it at its (also-`None`) default. Sarvam never receives the field either way and
    falls back to its own default (reasoning on). **The only lever left is a
    generous `max_tokens`** — and even that isn't a guarantee, since the model runs
    at `temperature=0.2`, not `0`; raising `max_tokens` from 800→4000 was observed to
    make one run *worse* (3/3 failures vs. 1 failure-then-recover at 800), which is
    evidence this is dominated by run-to-run sampling variance, not a monotonic
    function of budget.
- **Absent vs. explicit-null are different signals to Sarvam's API**, not
  interchangeable: omitting the field entirely → Sarvam's own default (`"low"`);
  sending literal JSON `null` → reasoning disabled. Any framework that silently
  drops `None` values before serializing (crewai's `LLM.call()`) cannot produce the
  second case no matter what you pass it in Python.

## 4 · Document AI (Lab 06)

- `language=`, not `language_code=` — the latter is **silently ignored**, no error.
- `output_format="md"`, not `"markdown"` — the latter returns 400.
- `schema=json.dumps(schema_dict)` — a JSON **string**, not a dict (`AttributeError`
  otherwise: `'dict' object has no attribute 'read'`).
- `file=[(name, handle, mime)]` — an array of tuples, not a bare `open(...)` handle.
- **The extract schema does not support a `required` key at all** —
  `SCHEMA_INVALID: schema property contains unsupported key "required"`. Every field
  is effectively optional; steer must-have fields through a sharper `description`.
- Digitise's actual per-page result shape can be **layout blocks**
  (`page.blocks[*].text`, ordered by `reading_order`), not the documented
  `page.content` Markdown string, depending on what the document actually contains —
  code that assumes `page.content` will silently get 0 characters. Build extraction
  code that checks both shapes (or walks the raw `model_dump()` for any populated
  `content`/`markdown`/`text` key) rather than trusting the documented field name
  alone.
- Always poll `get_status()` / `wait_until_complete()` before `get_results()`.
  `partially_completed` is a **terminal** state and is the one most codebases miss —
  a 20-file batch job can report `Completed` overall while 2 files silently failed.

## 5 · Text-to-Speech (Lab 03)

- `language_code=`, not `target_language_code=`, on `text_to_speech.convert()`.
- `dict_id` (pronunciation dictionaries) is **only honored on `bulbul:v3`** — passing
  it on `bulbul:v2` is silently a no-op, not an error. If `bulbul:v3` isn't
  available on your plan, the dictionary feature currently has no effect at all;
  there's no v2 fallback for it.
- Pronunciation dictionaries are created by **uploading a JSON file**
  (`pronunciation_dictionary.create(file=...)`, a `{"pronunciations": {lang: {word: pronunciation}}}` structure), not by passing `name=`/`entries=` as a dict — that
  shape doesn't match the installed SDK.
- Speaker names are **model-version-specific** — `anushka`/`abhilash`/etc. are
  `bulbul:v2` voices; `bulbul:v3` uses a different, non-overlapping voice list
  (default `shubh`). Using a v2 speaker name with `model="bulbul:v3"` raises
  `BadRequestError`.
- **`bulbul:v2` is deprecated as of 2026-08-27.** `bulbul:v3` is now the only TTS
  model. Every notebook cell using `model="bulbul:v2"` and every v2-only speaker
  name (`anushka`, `abhilash`, `manisha`, `vidya`, `arya`, `karun`, `hitesh` — none
  of which exist on v3) was swept to `bulbul:v3` with a valid v3 voice
  (`anushka→pooja`, `abhilash→shubh`, `manisha→priya`, `vidya→neha`, `arya→ishita`,
  `karun→rahul`, `hitesh→dev`). Valid v3 speakers: `aditya, ritu, ashutosh, priya,
  neha, rahul, pooja, rohan, simran, kavya, amit, dev, ishita, shreya, ratan, varun,
  manan, sumit, roopa, kabir, aayan, shubh, advait, anand, tanya, tarun, sunny, mani,
  gokul, vijay, shruti, suhani, mohit, kavitha, rehan, soham, rupali, niharika`.
  This also retired Lab 03's and Lab 08's v2-vs-v3 cost-comparison sections and
  scenario tables, since there's no longer a real choice to compare.
- HTTP streaming lives on the plain client — `client.text_to_speech.convert_stream(...)`
  — not on `text_to_speech_streaming` (that's the WebSocket-only client, no
  `.convert()` method at all).
- The WebSocket client's `connect()` only accepts `model`/`send_completion_event` —
  `language_code`/`speaker`/etc. go through `ws.configure(target_language_code=..., speaker=...)` **after** connecting, and `connect()` is only an async generator on
  `AsyncSarvamAI` (the sync client's version is a sync generator — same
  "`async with` on a sync client" trap as STT streaming). Audio arrives base64-encoded, not raw bytes.

## 6 · Speech-to-Text (Lab 02)

- REST `transcribe()` genuinely has no `sample_rate` parameter (see §2). Streaming
  paths (`speech_to_text_streaming`, `speech_to_text_realtime_streaming`) require it,
  since raw sample streams carry no header.
- Realtime streaming response `start_s`/`end_s` fields are `None` unless the
  connection was opened with `return_timestamps=True` — code that formats them with
  `:.2f` unconditionally will crash on a normal call.
- `sarvamai` package version drift matters: `speech_to_text_realtime_streaming` and
  its `RealtimeAudioInput`/`RealtimeEnd` types were added in `0.1.30`; they don't
  exist in `0.1.28`. Confirm the installed version before assuming a streaming
  surface is available.

## 7 · Framework interop (Lab 09/10 — renumbered 2026-08-28; was Lab 10/11)

- **`langgraph.prebuilt.create_react_agent` is deprecated** (LangGraph v1.0) —
  moved to `from langchain.agents import create_agent`, same call shape
  (`create_agent(llm, tools=tools)`), same `.ainvoke({"messages": [...]})` interface.
- **`langchain-mcp-adapters` ≥0.3 always converts a successful MCP tool result into
  a LIST of content blocks** (`[{"type":"text","text":...}]`), and `langchain-openai`
  passes that list straight through as a `tool` message's `content`. Sarvam's chat
  endpoint requires `content` to be a plain string for a `tool`-role message (this is
  actually closer to OpenAI's real schema than the newer content-blocks convention)
  and 400s: `body.messages.N.tool.content : Input should be a valid string`. Fix via
  the library's own `tool_interceptors=[...]` extension point on
  `MultiServerMCPClient(...)`, flattening every result — success *and* error paths —
  back to a string `ToolMessage` (covering only the success path leaves failed tool
  calls still 400ing).
- **Not every MCP tool's real payload is text.** `sarvam_tools_tts_speak` returns
  `AudioContent`, not `TextContent` — an interceptor that only extracts `"text"`
  blocks silently drops it, leaving the model an uninformative
  `"(success, no text content)"` stub with no confirmation anything worked, which can
  prompt the model to call the same tool again, repeatedly, at real cost. Give every
  content type (audio/image/resource) an actual textual acknowledgment.
- `crewai_tools.MCPServerAdapter` dispatches transport **purely on Python type**: a
  `StdioServerParameters` object → stdio, a plain `dict` → SSE — regardless of what
  keys the dict has. A bare dict with `command`/`args`/`env` gets routed to
  `sse_client(**server_params)`, which doesn't accept `command`, producing
  `TypeError: sse_client() got an unexpected keyword argument 'command'`. Construct
  a real `mcp.StdioServerParameters(...)` instead. (This is a different convention
  from `langchain-mcp-adapters`, which does accept a plain dict for stdio.)
- **crewai's litellm import is cached at first module import.** `crewai/llm.py` does
  `try: import litellm; LITELLM_AVAILABLE = True except ImportError: ... = False` at
  module load time. `pip install litellm` mid-kernel-session does not retroactively
  fix this — the kernel must be restarted so `crewai.llm` re-imports.
- **`crewai_tools.MCPServerAdapter`'s "missing mcp package" prompt is misleading.**
  The actual missing dependency in that failure mode is usually `mcpadapt` (a
  separate PyPI package `crewai_tools` needs alongside `mcp` itself), not `mcp`.
  `pip install mcpadapt` (or `pip install 'crewai-tools[mcp]'`).
- **crewai's per-task retry restarts the whole task, not just the failing step.**
  `Agent.execute_task()` catches any non-litellm, non-passthrough exception,
  increments `_times_executed`, and if `_times_executed <= max_retry_limit` (default
  `2`, i.e. **3 total attempts**), calls `execute_task(...)` again from scratch —
  discarding any partial progress from the failed attempt. This is why
  `"Invalid response from LLM call - None or empty"` shows up as 1–3 repeated ERROR
  lines before either recovering or failing the whole crew.
- **crewai 1.14.6's provider auto-inference can accidentally "fix" an intentional
  demo failure.** A bare model name with no `/` defaults, via
  `_infer_provider_from_model()`, to `provider="openai"` and routes to crewai's
  *native* OpenAI-compatible client class (bypassing litellm entirely) — which does
  no model-name validation and just sends the request to whatever `base_url` you
  configured. So `LLM(model="sarvam-105b", base_url="https://api.sarvam.ai/v1", ...)`
  (no `openai/` prefix) now genuinely works on this crewai version, even though the
  "missing prefix breaks it" lesson was true for older litellm-only crewai. Without
  `base_url` set at all, though, **both** the prefixed and unprefixed forms fail the
  same way — they fall back to real OpenAI's endpoint with a Sarvam key.
- A stdio MCP health-check subprocess must give the child its own `stdin=subprocess.PIPE`. Without it, the child inherits the Jupyter kernel's own
  stdin — typically already closed/EOF in a notebook — and a standard MCP stdio
  server reads that EOF immediately and exits **cleanly** (`code 0`), which looks
  identical to "the server is broken" if the check only looks at whether the process
  exited early. The real MCP client always gives the child a genuine pipe; a
  hand-rolled health check must too.
- A tool-metering wrapper (`tool.coroutine = wrapped_fn`) is not automatically
  idempotent — re-running the cell that applies it stacks another layer around
  whatever `tool.coroutine` currently is, so a second run doubles every print/timing,
  a third triples it, etc. Restart the kernel (or guard the wrapper to detect it's
  already applied) rather than re-running that cell.
- Lean/filtered tool sets should be built from **exact tool names**, not loose
  substring matching, and should be filtered from the runtime-only tool list (never
  builder/doc tools). A `KEEP` tuple like `("tts","speak",...)` can accidentally
  match an unrelated builder tool (`"speak" in "sarvam_code_speakers"` is `True`)
  and can just as easily *omit* a capability the eval actually exercises
  (`transliterate`, `identify`) if the tuple wasn't kept in sync with the test cases.
- **A correctly-written `tool_interceptors` fix can sit right next to the bug that
  defeats it, and look identical to "the interceptor doesn't work."** The actual
  root cause, found only by rereading the cell line-by-line: the line that calls
  `await mcp.get_tools()` on the *intercepted* client had been commented out, so
  `tools` was never rebound — every downstream `create_agent(llm, tools=tools)` was
  still running against the earlier, unintercepted client's tool objects. The
  interceptor code itself traced cleanly through
  `langchain-mcp-adapters==0.3.2` → `langchain_core==1.4.0`'s tool-output formatting
  → `langgraph`'s `ToolNode._normalize_tool_response` (what `create_agent` actually
  uses) — a plain-string `ToolMessage` survives every hop intact. The bug was never
  in the mechanism; it was in which client object's tools were actually in scope.
  Two structural traps compounded this: (1) the fixed and unfixed cells shared the
  same global names (`mcp`, `tools`), so whichever cell last ran decided the outcome
  regardless of "the fix is right there in the file"; (2) a `.ipynb`'s saved cell
  *outputs* can be stale from a much earlier run (dated a day before the cell
  actually re-ran), which can look like fresh evidence the fix still fails when it's
  actually an old failure the file never re-executed since. Fix: give the fixed
  client/tools their own names (`mcp_fixed`/`tools_fixed`) so accidentally-stale or
  commented-out state can't silently satisfy a downstream `if tools:` check.

## 8 · Jupyter/asyncio mechanics (general, not Sarvam-specific)

- `crew.kickoff()` can conflict with Jupyter's already-running event loop.
  `kickoff_async()` works around it by running the same sync `kickoff()` in a
  background thread — but it's an `async def`, so it must be **awaited**
  (`await crew.kickoff_async()`), not just called; calling it alone just produces an
  un-awaited coroutine object and a `RuntimeWarning`.
- Editing a notebook's `.ipynb` file on disk does not affect variables already
  sitting in a running kernel's memory. Several "I already fixed this, why is it
  still broken" moments in this session traced back to re-running a downstream cell
  without first re-running the (now-fixed) upstream cell that rebuilds the relevant
  variable (`tools`, `llm`, `mcp`, etc.) in that same kernel session.
- `pip install X` in a different Python environment than the one the Jupyter kernel
  is actually running does not become visible to that kernel. When an install
  "doesn't seem to take effect" even after a restart, verify with
  `import sys; print(sys.executable)` inside the notebook, and if needed
  `!{sys.executable} -m pip install X` to guarantee it lands on the right interpreter.

## 9 · Lab-authoring lessons (about the labs' own design, not the SDK)

- **A hand-written gotchas rubric only catches what it was explicitly written to
  catch.** Lab 11's original 8-rule `GOTCHAS` list reported a context-free
  generation as "8/8 avoided — no gotchas" despite the code having ~6 distinct real
  defects (wrong constructor kwarg, two different bare-method-call mistakes, an
  invalid model name, dict-style response access, and — in one variant — importing
  nonexistent classes) — none of which matched any of the 8 existing regexes. A
  rubric with incomplete coverage doesn't just fail to catch new mistakes; it
  actively manufactures false confidence by reporting a perfect score. Extended to
  14 rules to close this gap; the general lesson (keep the rubric growing every time
  a new trap is found) applies to any such automated grader, not just this one.
- **Not every context layer can be expected to reach a "clean sweep."** A single
  fetched doc page can only fix mistakes the *specific page* happens to document —
  a chat-completions page cannot fix an STT mistake no matter how capable the model
  is. A retrieval layer capped at N pages is bounded by keyword-overlap scoring
  finding the right pages. An Agent Skill authored for one purpose (e.g. cost
  metering) shouldn't be expected to also serve as a comprehensive API reference
  unless it was deliberately scoped that way. The layer most likely to reach 100%
  against a known rubric is a skill *deliberately authored to cover that rubric* —
  which is the honest version of "Agent Skills prescribe; documentation describes,"
  not a knock against the other layers.
- **A weak result despite good context is not automatically evidence the model is
  "bad at coding."** Checked directly against the fetched pages in one case: the
  STT reference page's own Python example showed the exact correct client-
  construction pattern verbatim, and the model still wrote the wrong one — that's a
  context-*grounding* failure (the model reverting to a familiar prior over a low-
  salience snippet buried in a long, multi-language reference page), not evidence
  about general coding ability. The controlled way to actually test a "weak at
  coding" hypothesis is a general coding benchmark with no Sarvam-specific context
  involved at all; a single Sarvam-domain generation can't isolate that variable.
- **Telling the model to prioritize the given context over its training has a real,
  measurable effect on ONE class of mistake and none on another — worth separating,
  not averaging together.** Tested directly: adding an explicit
  "treat the documentation as ground truth; reproduce exact patterns it shows"
  instruction to the system prompt, with identical context and task otherwise,
  closed the client-construction mistake above (the model now copied the doc's
  verbatim `SarvamAI(api_subscription_key=...)` pattern instead of writing a bare
  `SarvamAI()`). It did **not** stop the `input_audio_codec` hallucination in the
  same generation — because that failure isn't the model overriding something the
  context showed, it's inventing something the context never showed, primed by the
  task's own wording. An instruction to trust provided context has leverage over
  "model ignored/overrode the shown pattern" failures; it has little to none over
  "model added an unshown parameter from its own priors" failures. Don't expect one
  prompt change to fix both, and don't judge it a failure if it only fixes one.
- **A single small-sample eval run cannot support a directional claim, and printing
  only pass/fail hides *why* two runs disagree.** A 5-case golden set run at
  non-zero temperature (`agent()` had a `seed` but no `temperature=0`) produced 4/5
  with a tool-discipline system prompt and 5/5 with a stripped-down one — the
  opposite of the lab's intended "we caught a regression" narrative. One flipped
  case out of five is a 20-point swing; it is not evidence "less guidance is
  better" any more than the original evidence was "the guidance regressed nothing."
  The fix that actually adds insight isn't a bigger score, it's printing what each
  tool call was actually *asked* (the arguments, not just the tool name) — that
  turns "these two runs disagree" into "one run checked the tool before answering
  and the other didn't," which is a diagnosable, specific difference instead of an
  unexplained score wobble. Separately: closing a genuine hallucination gap (an
  agent inventing a balance for a non-existent account) needed an explicit system
  prompt instruction ("if an account id doesn't match any record, say so plainly —
  never guess") — tool-selection accuracy driven by schema alone does not
  automatically extend to safe behavior on the *empty-result* case a tool can
  return.
</content>
