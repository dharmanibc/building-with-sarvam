
FREE_CREDIT = 1000.00

RATES = {'stt_per_hour': 30.0, 'stt_diarized_per_hour': 45.0, 'translate_per_10k': 20.0, 'transliterate_per_10k': 20.0, 'lid_per_10k': 3.5, 'tts_v2_per_10k': 15.0, 'tts_v3_per_10k': 30.0, 'llm_in_per_1m': 29.28, 'llm_cached_in_per_1m': 10.98, 'llm_out_per_1m': 73.2, 'doc_per_page': 0.5, 'samvaad_per_min': 3.5}

class CostMeter:
    def __init__(self): self.items = []
    def add(self, label, rupees, detail=""):
        self.items.append({"label": label, "inr": rupees, "detail": detail}); return rupees
    def stt(self, seconds, diarized=False):
        r = RATES["stt_diarized_per_hour" if diarized else "stt_per_hour"]/3600*seconds
        return self.add("STT", r, f"{seconds:.1f}s")
    def tts(self, chars, v3=True):
        r = RATES["tts_v3_per_10k" if v3 else "tts_v2_per_10k"]/10_000*chars
        return self.add("TTS", r, f"{chars} chars")
    def text(self, chars, kind="translate"):
        return self.add(kind, RATES[f"{kind}_per_10k"]/10_000*chars, f"{chars} chars")
    def llm(self, i, o, c=0):
        r = ((i-c)*RATES["llm_in_per_1m"] + c*RATES["llm_cached_in_per_1m"]
             + o*RATES["llm_out_per_1m"])/1_000_000
        return self.add("LLM", r, f"{i} in / {o} out")
    def doc(self, pages): return self.add("DocAI", RATES["doc_per_page"]*pages, f"{pages} pages")
    def report(self):
        for i in self.items: print(f"{i['label']:<12} ₹{i['inr']:>9.4f}  {i['detail']}")
        t = sum(i["inr"] for i in self.items)
        print(f"{'TOTAL':<12} ₹{t:>9.4f}")
        print(f"{'':<12}  (₹{FREE_CREDIT:.0f} free credit → ₹{FREE_CREDIT-t:.2f} left)")
        print(f"{'':<12}  Estimated from published rates; actual billing usually lower")
        return t
