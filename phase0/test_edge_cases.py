"""Test edge-case index codes to determine fetch strategy per code pattern."""
import sys, io, time, traceback
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import akshare as ak

test_cases = [
    ("399986", "中证银行",    "399xxx CSI-managed"),
    ("930050", "中证A50",     "93xxxx newer CSI"),
    ("932000", "中证2000",    "93xxxx newer CSI"),
    ("931643", "科创创业50",   "93xxxx cross-board"),
    ("H30022", "800银行",     "H-prefix CSI"),
    ("000925", "基本面50",    "strategy/smart-beta"),
    ("000918", "300成长",     "style index"),
    ("399975", "证券公司",    "sector 399xxx"),
    ("000985", "中证全指",    "all-share (5000+ members)"),
    ("000001", "上证指数",    "SSE Composite (exchange-native)"),
    ("399001", "深证成指",    "SZSE Component (exchange-native)"),
]

for symbol, name, desc in test_cases:
    print(f"\n{'='*60}")
    print(f"{symbol}  {name}  ({desc})")
    print(f"{'='*60}")

    # Try csindex first
    t0 = time.time()
    try:
        df = ak.index_stock_cons_csindex(symbol=symbol)
        ms = int((time.time() - t0) * 1000)
        print(f"  [csindex] OK  {len(df)} members  {ms}ms")
        if len(df) > 0:
            row = df.iloc[0]
            print(f"  sample: code={row.get('成分券代码','?')} name={row.get('成分券名称','?')}")
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        print(f"  [csindex] FAIL  {ms}ms  {type(e).__name__}: {e}")

    time.sleep(1)

    # Try sina fallback
    t0 = time.time()
    try:
        df = ak.index_stock_cons(symbol=symbol)
        ms = int((time.time() - t0) * 1000)
        print(f"  [sina]   OK  {len(df)} members  {ms}ms")
        if len(df) > 0:
            print(f"  columns: {list(df.columns)}")
            row = df.iloc[0]
            print(f"  sample: {dict(row)}")
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        print(f"  [sina]   FAIL  {ms}ms  {type(e).__name__}: {e}")

    time.sleep(2)

print("\n\nDONE")
