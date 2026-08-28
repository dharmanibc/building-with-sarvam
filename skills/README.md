# Agent Skills for Sarvam

Two drop-in context files for AI coding assistants. They encode what the Sarvam SDK
actually looks like and where it differs from what a model will guess — which is the
difference between generated code that runs and generated code that raises
`AttributeError`.

| Skill | What it does |
|---|---|
| [`sarvam-sdk-gotchas-skill.md`](sarvam-sdk-gotchas-skill.md) | Correct signatures and known traps across the whole SDK — client construction, chat, STT, TTS, Document AI, and framework interop |
| [`sarvam-cost-metering-skill.md`](sarvam-cost-metering-skill.md) | Makes generated code track spend in rupees by default, including the MCP case where usage is invisible |

They are complementary: the first stops the code being wrong, the second stops it being
untracked. Install both.

## Install

Both files are valid `SKILL.md` content — YAML frontmatter plus a Markdown body — under
the [Agent Skills specification](https://agentskills.io/specification). To install, put
each in a directory whose **name matches its `name:` field**:

```bash
mkdir -p ~/.claude/skills/sarvam-sdk-gotchas
cp sarvam-sdk-gotchas-skill.md ~/.claude/skills/sarvam-sdk-gotchas/SKILL.md

mkdir -p ~/.claude/skills/sarvam-cost-metering
cp sarvam-cost-metering-skill.md ~/.claude/skills/sarvam-cost-metering/SKILL.md
```

The directory name must match `name:` exactly, or the skill will not load.

Paths differ by tool — Claude Code uses `~/.claude/skills/` for user-level skills and
`.claude/skills/` for project-level ones; Cursor and Windsurf have their own locations.
Check your tool's documentation for where it looks.

Sarvam also publishes its own skills, which cover API surface rather than traps and are
worth having alongside these:

```bash
npx skills add sarvamai/skills          # chat, speech-to-text, text-to-speech, translate, voice-agents
```

## Use them without installing anything

If you just want better output from one prompt, paste the file contents in front of your
question. That is the whole mechanism — a skill is context, delivered automatically
instead of manually.

## Why these exist

Ask any assistant for a Sarvam snippet with no context and it will typically write
`client.chat.completions.create(...)` — a method that does not exist in this SDK. It is
not being careless; it has read a hundred thousand OpenAI examples and very few Sarvam
ones, so it produces the shape it knows.

A bigger model does not fix this. It is a knowledge gap, not a reasoning gap, and
context is the fix.

[Lab 11](../Labs/11_Context_Engineering_Markdown_llms_txt_Context7_Skills.ipynb) builds
this argument properly: it scores four different ways of supplying context — Markdown
docs, `llms.txt`, Context7 and Agent Skills — against a 14-rule rubric, and shows which
ones actually move the number.

## Keeping them current

The Sarvam platform moves quickly and these files will drift. Both carry a
`metadata.version`; the facts behind them are documented, with how each was established,
in [`../Labs/SESSION_FINDINGS_2026-08.md`](../Labs/SESSION_FINDINGS_2026-08.md).

**If you hit a trap that is not in here, that is worth a pull request.** Adding one line
to a skill improves generated code for everyone who installs it — which is a
considerably better return than fixing it in your own project and moving on.

## Licence

Apache 2.0, same as the rest of this repository. Fork them, adapt them for your own
stack, ship them in your own tooling.
