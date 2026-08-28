---
name: sarvam-cost-metering
description: Adds rupee cost tracking to Sarvam AI API calls. Use whenever writing or reviewing Python that calls the sarvamai SDK - speech_to_text, text_to_speech, chat.completions, text.translate, doc_ai - or that reaches Sarvam through an MCP tool, so that every billed call is accompanied by a CostMeter entry and the script prints a total in rupees before it exits.
license: Apache-2.0
compatibility: Python 3.10+, sarvamai>=0.1.30
metadata:
  author: AIVidhya4Sarvam
  version: "1.0"
  source: https://github.com/dharmanibc/building-with-sarvam
---

# Sarvam cost metering

Every Sarvam API call costs money. Code that calls Sarvam without tracking spend is
incomplete — a script that runs for an hour and cannot say what it cost is not
finished.

When you write or review such code, attach a meter entry to every billed call and print
a total at the end.

## The rule

| API | Billed by | Meter call |
|---|---|---|
| `speech_to_text.transcribe` | audio seconds | `cost.stt(seconds)` |
| …with diarization | audio seconds | `cost.stt(seconds, diarized=True)` |
| `text_to_speech.convert` | characters | `cost.tts(len(text))` |
| `text.translate` / `transliterate` | characters | `cost.text(len(s), kind="translate")` |
| `text.identify_language` | characters | `cost.text(len(s), kind="lid")` |
| `chat.completions` | tokens | `cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)` |
| `doc_ai` digitise / extract | pages | `cost.doc(n_pages)` |

End every script with `cost.report()`.

## Correct usage

```python
from cost_meter import CostMeter
cost = CostMeter()

r = client.chat.completions(
    model="sarvam-105b",
    messages=msgs,
    max_tokens=800,
    reasoning_effort=None,
)
cost.llm(r.usage.prompt_tokens, r.usage.completion_tokens)

with open("call.wav", "rb") as f:
    t = client.speech_to_text.transcribe(
        file=f, model="saaras:v3", language_code="hi-IN", mode="transcribe")
cost.stt(duration_seconds("call.wav"))

cost.report()
```

## A minimal meter, if the project has none

```python
FREE_CREDIT = 1000.00           # new Sarvam accounts
RATES = {                       # Rs, August 2026 — verify before quoting
    "stt_per_hour": 30.00, "stt_diarized_per_hour": 45.00,
    "tts_per_10k": 30.00,
    "translate_per_10k": 20.00, "transliterate_per_10k": 20.00, "lid_per_10k": 3.50,
    "llm_in_per_1m": 29.28, "llm_cached_in_per_1m": 10.98, "llm_out_per_1m": 73.20,
    "doc_per_page": 0.50,
}

class CostMeter:
    """Running Rs tally. Conservative upper bound - see 'Honesty' below."""
    def __init__(self): self.items = []

    def add(self, label, rupees, detail=""):
        self.items.append({"label": label, "inr": rupees, "detail": detail})
        return rupees

    def stt(self, seconds, diarized=False):
        key = "stt_diarized_per_hour" if diarized else "stt_per_hour"
        return self.add("STT" + (" +diar" if diarized else ""),
                        RATES[key] / 3600 * seconds, f"{seconds:.1f}s")

    def tts(self, chars):
        return self.add("TTS", RATES["tts_per_10k"] / 10_000 * chars, f"{chars} chars")

    def text(self, chars, kind="translate"):
        return self.add(kind, RATES[f"{kind}_per_10k"] / 10_000 * chars, f"{chars} chars")

    def llm(self, in_tok, out_tok, cached_tok=0):
        r = ((in_tok - cached_tok) * RATES["llm_in_per_1m"]
             + cached_tok * RATES["llm_cached_in_per_1m"]
             + out_tok * RATES["llm_out_per_1m"]) / 1_000_000
        return self.add("LLM", r, f"{in_tok} in / {out_tok} out / {cached_tok} cached")

    def doc(self, pages):
        return self.add("DocAI", RATES["doc_per_page"] * pages, f"{pages} pages")

    def report(self):
        if not self.items:
            print("nothing billed yet"); return 0.0
        w = max(len(i["label"]) for i in self.items) + 2
        for i in self.items:
            print(f"{i['label']:<{w}} Rs{i['inr']:>9.4f}   {i['detail']}")
        total = sum(i["inr"] for i in self.items)
        print(f"{'TOTAL':<{w}} Rs{total:>9.4f}")
        print(f"{'':<{w}}  (Rs{FREE_CREDIT:.0f} free credit -> Rs{FREE_CREDIT-total:.2f} left)")
        print(f"{'':<{w}}  Estimated from published rates; actual billing usually lower")
        return total
```

## Capture cached tokens where the API reports them

Sarvam follows the OpenAI wire protocol, so cached input tokens appear under
`usage.prompt_tokens_details.cached_tokens` when present. Reading them makes the
estimate materially more accurate, since cached input bills at roughly a third of the
normal rate:

```python
def llm_from_usage(meter, usage):
    cached = getattr(getattr(usage, "prompt_tokens_details", None),
                     "cached_tokens", 0) or 0
    return meter.llm(usage.prompt_tokens, usage.completion_tokens, cached_tok=cached)
```

## MCP tool calls do not meter themselves

When Sarvam is reached through an MCP server rather than the SDK directly, **the tool
result carries no usage information back**. The billed call happened inside the server;
nothing tells the calling process. A meter fed only from `response.usage` will report
₹0.00 while real money is spent.

Meter from the **input you sent** instead — audio seconds for STT, characters for
TTS and translate:

```python
def metered(tool, meter):
    """Wrap an MCP tool so every invocation lands on the cost meter."""
    original = tool.coroutine or tool.func

    async def _wrapped(**kwargs):
        result = await original(**kwargs) if tool.coroutine else original(**kwargs)
        name = tool.name
        try:
            if "stt" in name or "transcribe" in name:
                p = kwargs.get("file_path") or kwargs.get("file")
                if p and Path(str(p)).exists():
                    meter.stt(duration_seconds(p))
            elif "tts" in name or "speak" in name:
                meter.tts(len(str(kwargs.get("text", ""))))
            elif "translate" in name or "transliterate" in name:
                meter.text(len(str(kwargs.get("input", kwargs.get("text", "")))),
                           kind="translate")
        except Exception:
            pass                      # never let metering break the agent
        return result

    tool.coroutine = _wrapped
    return tool
```

**This wrapper is not idempotent.** Applying it twice stacks two layers and doubles
every recorded cost. Guard it, or restart the process rather than re-running the code
that applies it.

**The general principle:** put a protocol boundary between your code and a billed API,
and your observability stops at that boundary. Meter at the boundary you control.

## Honesty about the number

Report it as an **estimate**, never as an invoice:

```
TOTAL      Rs  6.4231
           Estimated from published rates; actual billing usually lower
```

The estimate is a **conservative upper bound**. Real billing typically comes in slightly
lower, because these are not modelled:

- server-side prompt caching that the response did not report
- the ₹1000 free-tier credit
- invoice-level rounding

Erring high is deliberate. Someone who budgets ₹10 and is billed ₹8 is fine; the
reverse is not.

Rates above are dated **August 2026**. Verify at
`docs.sarvam.ai/api/getting-started/pricing` before putting any figure in front of a
customer, and check live spend at `indus.sarvam.ai`.

## Non-negotiables when generating Sarvam code

- Always pass `model=` explicitly — defaults drift between releases.
- `client.chat.completions(...)` has **no** `.create()`.
- With `reasoning_effort` left on and a small `max_tokens`, reasoning eats the budget
  and `content` returns `None`. Pass `reasoning_effort=None` or raise `max_tokens`.
- Never print or log an API key alongside a cost report.

For the full set of SDK signatures and traps, pair this with the
`sarvam-sdk-gotchas` skill.
