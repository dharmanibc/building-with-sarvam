# Contributing

This repository is a **tested, verified exploration of the Sarvam AI stack** — not a
tutorial for one application. Its value is breadth plus evidence: every feature is
reached, every claim is something somebody ran, and every cost is measured rather than
estimated.

Contributions that extend that are welcome. In rough order of usefulness:

1. **A capability nobody has covered yet.** Dubbing, voice cloning, an API surface that
   shipped last month. See the *Coverage* table in the [README](README.md) for what is
   currently untouched — those gaps are the most valuable thing you could close.
2. **A trap you hit that is not documented.** If the SDK surprised you and
   [`Labs/SESSION_FINDINGS_2026-08.md`](Labs/SESSION_FINDINGS_2026-08.md) does not
   mention it, that is a gap in the material. A one-line issue is a real contribution.
3. **A measurement on your own data.** WER on your recordings, latency from your
   region, cost at your volume. Numbers from a second machine are worth more than a
   second opinion.
4. **A correction.** The platform moves; some of this will go stale. Corrections that
   contradict what is here are welcome — bring the evidence and it goes in.

---

## The one rule that matters

**Edit the generators, not the artefacts.**

Both the notebooks and the decks are generated. A change to a `.ipynb` or a `.pptx`
will be silently destroyed the next time somebody runs a build.

| To change… | Edit | Then run |
|---|---|---|
| A lab's content | `Labs/build/gen_*.py` | `python3 gen_X.py` |
| Anything shared across labs (header, `CostMeter`, cell helpers) | `Labs/build/nbkit.py` | all five generators |
| A deck's content | `Slides/build/dNN.js` | `node dNN.js` |
| Colours, fonts, logo, footer, slide shells | `Slides/build/theme.js` | `for f in d??.js; do node $f; done` |

Which generator builds which lab:

```
gen_a.py → 00 01 02 03 04
gen_b.py → 05 06 07
gen_c.py → 08 12
gen_d.py → 09
gen_e.py → 10 11
```

---

## Reporting a correction

Open an issue with:

1. **What you ran** — the smallest snippet that reproduces it
2. **What happened** — the actual traceback or the actual wrong output
3. **What you expected**, and where you got that expectation from
4. **Versions** — `pip show sarvamai openai langchain-mcp-adapters crewai` and your
   Python version

The bar is *"I ran this and observed that"*, not *"the docs say"*. Everything in
`SESSION_FINDINGS` was found by running code and reading installed library source;
please hold new entries to that standard.

---

## Submitting a change

```bash
git checkout -b fix/short-description
# edit the generator
cd Labs/build && python3 gen_a.py     # or the relevant one
git add Labs/build/gen_a.py Labs/02_*.ipynb
git commit -m "fix(lab02): correct X — Y raises Z on sarvamai 0.1.30"
```

**Commit both the generator and the regenerated artefact.** Reviewers read the
generator diff; users get the built file.

### Before opening a PR

- [ ] The generator runs without error
- [ ] `nbformat.validate()` passes on any regenerated notebook
- [ ] No API key, `.env` file, or personal path appears anywhere in the diff
- [ ] If you corrected a fact, add a line to `SESSION_FINDINGS_2026-08.md` saying how
      you established it
- [ ] If you added a new failure mode, consider adding a rule to Lab 11's `GOTCHAS`
      rubric so it is caught automatically from now on

### On notebook outputs

The committed notebooks carry **real executed outputs** — that is deliberate and part
of what makes them useful to read on GitHub without running anything.

- Fixing a typo in prose? Regenerating wipes outputs. Prefer a targeted edit, or re-run
  the notebook before committing.
- Changing code? Re-run the affected cells so the saved output matches the code.
- Never commit an output containing your API key, an account identifier, or a real
  customer's data.

---

## Style

The material has a voice; please match it.

- **Measure, do not assert.** "We timed it: 821 ms" beats "MCP is fast."
- **Every failure is a deliberate experiment**, not a warning box. Make the reader
  *cause* the error, read it, then fix it.
- **Every API call is metered.** If you add a billed call, add the `cost.*()` line.
- **Say what is uncertain.** "Verify before quoting this to a customer" is a feature.
- **No colour emoji in decks** — they render as empty boxes in Office and
  LibreOffice. Only BMP symbols (★ ✓ ✕ ⚡ ₹ ♪ ⇄ §).
- Prose in the labs is British-English and plain. No exclamation marks, no hype.

---

## Things deliberately not accepted

- **A "simplified" lab that removes the cost meter.** The metering is the pedagogy.
- **Replacing measured numbers with rounder ones.** If a number is ugly, it is ugly
  because it is real.
- **Removing a correction because it contradicts the official docs.** If the SDK
  behaves differently from its documentation, that gap *is* the lesson — document
  both.

---

## Licence

By contributing you agree your work is licensed under [Apache 2.0](LICENSE).
