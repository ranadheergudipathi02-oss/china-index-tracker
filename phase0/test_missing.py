"""Verify the headline indices missing from the allow-list: STAR 50, SSE Composite, STAR 100."""
import sys, io, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import akshare as ak

cases = [
    ("000688", "STAR 50 / 科创50"),
    ("000698", "STAR 100 / 科创100"),
    ("000001", "SSE Composite / 上证指数"),
]
for code, label in cases:
    print(f"\n=== {code}  {label} ===")
    for method in ("csindex", "sina"):
        t0 = time.time()
        try:
            fn = ak.index_stock_cons_csindex if method == "csindex" else ak.index_stock_cons
            df = fn(symbol=code)
            ms = int((time.time()-t0)*1000)
            print(f"  [{method}] OK {len(df)} members {ms}ms  cols={list(df.columns)[:4]}")
            if len(df):
                r = df.iloc[0]
                k = "成分券代码" if method=="csindex" else "品种代码"
                kn = "成分券名称" if method=="csindex" else "品种名称"
                print(f"      sample: {r.get(k,'?')} {r.get(kn,'?')}")
            break
        except Exception as e:
            ms = int((time.time()-t0)*1000)
            print(f"  [{method}] FAIL {ms}ms {type(e).__name__}: {str(e)[:80]}")
        time.sleep(1.5)
    time.sleep(1.5)
print("\nDONE")
