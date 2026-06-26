"""Final data-layer verification of the built site aggregates."""
import sys, json, os
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = json.load(open(os.path.join(ROOT, "assets/directory.json"), encoding="utf-8"))
s = json.load(open(os.path.join(ROOT, "assets/stocks.json"), encoding="utf-8"))

# directory.json shape: support either {indices:[...]} or [...]
idx = d["indices"] if isinstance(d, dict) and "indices" in d else d
codes = {i["code"]: i for i in idx}
print(f"directory.json: {len(idx)} indices")

# 1. new headline indices present
for c, label in [("000688", "STAR 50"), ("000698", "STAR 100"), ("000001", "SSE Composite")]:
    it = codes.get(c)
    print(f"  {c} {label}: {'PRESENT board=' + it.get('board','?') + ' count=' + str(it.get('count','?')) if it else 'MISSING!'}")

# 2. STAR board populated
star = [i for i in idx if i.get("board") == "STAR"]
print(f"  STAR board indices: {[i['code'] for i in star]}")

# 3. stock -> indices reverse lookup for a known STAR 50 constituent (688008 澜起科技)
smap = s["stocks"] if isinstance(s, dict) and "stocks" in s else s
def lookup(sym):
    if isinstance(smap, dict):
        return smap.get(sym)
    for row in smap:
        if row.get("symbol") == sym or row.get("code") == sym:
            return row
    return None
r = lookup("688008")
print(f"\nstocks.json: {len(smap)} stocks")
print(f"  688008 (澜起科技) -> {json.dumps(r, ensure_ascii=False)[:160] if r else 'NOT FOUND'}")
print("\nVERIFY OK")
