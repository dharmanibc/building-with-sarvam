"""nbkit — tiny helper to build teaching notebooks from a compact cell list."""
import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
import os

OUT = os.environ.get("LAB_OUT", "/sessions/determined-intelligent-einstein/mnt/Sarvam_Workshop/Labs")


def md(t):
    return ("md", t.strip("\n"))


def code(t):
    return ("code", t.strip("\n"))


def build(filename, title, cells):
    nb = new_notebook()
    nb.cells = []
    for kind, body in cells:
        nb.cells.append(new_markdown_cell(body) if kind == "md" else new_code_cell(body))
    nb.metadata = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.11"},
        "title": title,
        "authors": [{"name": "Dr. Bhaveshkumar C. Dharmani — AIVidhya"}],
    }
    nbf.validate(nb)
    path = os.path.join(OUT, filename)
    with open(path, "w", encoding="utf-8") as f:
        nbf.write(nb, f)
    n_code = sum(1 for c in nb.cells if c.cell_type == "code")
    print(f"{filename:<52} {len(nb.cells):>3} cells ({n_code} code)")
    return path


# ---------------------------------------------------------------- shared blocks

BANNER = """
<div style="background:#12172E;color:#fff;padding:20px 24px;border-radius:8px">
<div style="color:#FF8A3D;font-size:12px;letter-spacing:2px;font-weight:700">{eyebrow}</div>
<div style="font-size:26px;font-weight:700;margin-top:6px">{title}</div>
<div style="color:#FFB37A;font-size:14px;margin-top:8px">{sub}</div>
</div>

**Time:** {time} &nbsp;·&nbsp; **Est. cost:** {cost} &nbsp;·&nbsp; **Prereq:** {prereq}
"""

SETUP = code("""
# ── Standard lab header. Run this first in every notebook. ─────────────────
import os, sys, json, time, math, wave, io
from pathlib import Path

# pip install sarvamai python-dotenv
from sarvamai import SarvamAI

# Put SARVAM_API_KEY in a .env file next to this notebook, or set it here.
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

API_KEY = os.environ.get("SARVAM_API_KEY") or "PASTE_YOUR_KEY_HERE"
assert API_KEY != "PASTE_YOUR_KEY_HERE", "Set SARVAM_API_KEY first"

client = SarvamAI(api_subscription_key=API_KEY)
DATA = Path("./data"); DATA.mkdir(exist_ok=True)
OUT  = Path("./out");  OUT.mkdir(exist_ok=True)
print("SDK ready ·", sys.version.split()[0])
""")

COSTMETER = code('''
# ── The ₹ meter. Lab 00 defines it; every other lab imports it. ───────────
# Rates as of August 2026. Verify at docs.sarvam.ai/api/getting-started/pricing
FREE_CREDIT = 1000.00          # new Sarvam accounts — see indus.sarvam.ai
RATES = {
    "stt_per_hour":            30.00,
    "stt_diarized_per_hour":   45.00,
    "translate_per_10k":       20.00,
    "transliterate_per_10k":   20.00,
    "lid_per_10k":              3.50,
    "tts_v2_per_10k":          15.00,
    "tts_v3_per_10k":          30.00,
    "llm_in_per_1m":           29.28,
    "llm_cached_in_per_1m":    10.98,
    "llm_out_per_1m":          73.20,
    "doc_per_page":             0.50,
    "samvaad_per_min":          3.50,
}

class CostMeter:
    """Running ₹ tally. Call .add() after every API call."""
    def __init__(self): self.items = []

    def add(self, label, rupees, detail=""):
        self.items.append({"label": label, "inr": rupees, "detail": detail})
        return rupees

    # --- convenience wrappers, one per billing unit -----------------------
    def stt(self, seconds, diarized=False):
        r = RATES["stt_diarized_per_hour" if diarized else "stt_per_hour"] / 3600 * seconds
        return self.add("STT" + (" +diar" if diarized else ""), r, f"{seconds:.1f}s")

    def tts(self, chars, v3=True):
        r = RATES["tts_v3_per_10k" if v3 else "tts_v2_per_10k"] / 10_000 * chars
        return self.add(f"TTS {'v3' if v3 else 'v2'}", r, f"{chars} chars")

    def text(self, chars, kind="translate"):
        r = RATES[f"{kind}_per_10k"] / 10_000 * chars
        return self.add(kind, r, f"{chars} chars")

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
        print("─" * (w + 34))
        for i in self.items:
            print(f"{i['label']:<{w}} ₹{i['inr']:>9.4f}   {i['detail']}")
        total = sum(i["inr"] for i in self.items)
        print("─" * (w + 34))
        print(f"{'TOTAL':<{w}} ₹{total:>9.4f}")
        print(f"{'':<{w}}  (₹{FREE_CREDIT:.0f} free credit → ₹{FREE_CREDIT-total:.2f} left)")
        print(f"{'':<{w}}  Estimated from published rates; actual billing usually lower")
        return total

cost = CostMeter()
print("cost meter armed")
''')


# Labs 01-12 do NOT redefine the meter — they import the module Lab 00 writes.
# Keeping one definition on disk means a rate change is a one-file edit.
COSTMETER_IMPORT = code("""
# ── The ₹ meter, imported ─────────────────────────────────────────────────
# Lab 00 writes cost_meter.py next to these notebooks. If this import fails,
# run Lab 00 once — it is the only lab that defines the meter.
try:
    from cost_meter import CostMeter, RATES, FREE_CREDIT
except ImportError:
    raise ImportError(
        "cost_meter.py not found.\\n"
        "Run 00_Setup_and_the_Cost_Meter.ipynb once — its last section writes "
        "cost_meter.py into this folder, and every other lab imports it from there."
    )

cost = CostMeter()
print(f"cost meter armed · rates dated Aug 2026 · ₹{FREE_CREDIT:.0f} free credit")
""")


def header(eyebrow, title, sub, time_, est, prereq):
    return md(BANNER.format(eyebrow=eyebrow, title=title, sub=sub,
                            time=time_, cost=est, prereq=prereq))
