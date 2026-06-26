"""Hard-timeout reachability probe — is csindex/sina responding from THIS IP right now?"""
import sys, time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FTimeout
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import akshare as ak

def call(fn, code):
    return fn(symbol=code)

tests = [
    ("csindex", ak.index_stock_cons_csindex, "000016"),  # SSE 50, small
    ("sina",    ak.index_stock_cons,          "399006"),  # ChiNext
    ("csindex", ak.index_stock_cons_csindex, "000300"),  # CSI 300, medium
]
ex = ThreadPoolExecutor(max_workers=1)
for label, fn, code in tests:
    t0 = time.time()
    fut = ex.submit(call, fn, code)
    try:
        df = fut.result(timeout=25)
        print(f"[{label}] {code}: OK {len(df)} rows in {time.time()-t0:.1f}s")
    except FTimeout:
        print(f"[{label}] {code}: TIMEOUT after 25s (source hanging from this IP)")
    except Exception as e:
        print(f"[{label}] {code}: ERROR {type(e).__name__}: {str(e)[:70]}")
    time.sleep(1)
ex.shutdown(wait=False)
print("PROBE DONE")
