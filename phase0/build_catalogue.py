"""Save full CSI catalogue and analyze categories for allow-list building."""
import sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import akshare as ak
import pandas as pd

print("Fetching full CSI catalogue (index_csindex_all)...")
df = ak.index_csindex_all()
print(f"Total indices: {len(df)}")

records = df.to_dict(orient="records")
for r in records:
    for k, v in list(r.items()):
        if hasattr(v, "isoformat"):
            r[k] = v.isoformat()
        elif pd.isna(v):
            r[k] = None

out = "phase0/csindex_all_catalogue.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=1)
print(f"Saved to {out}\n")

# Analysis
col_asset = "资产类别"   # 资产类别
col_cat   = "指数类别"   # 指数类别
col_track = "跟踪产品"   # 跟踪产品
col_code  = "指数代码"   # 指数代码
col_name  = "指数简称"   # 指数简称
col_count = "样本数量"   # 样本数量
col_hot   = "指数热点"   # 指数热点

print("=" * 60)
print("CATEGORY ANALYSIS")
print("=" * 60)

print(f"\nAsset class:")
for a, n in df[col_asset].value_counts().items():
    print(f"  {a}: {n}")

stock = df[df[col_asset] == "股票"]  # 股票
print(f"\nStock indices: {len(stock)}")
print(f"\nStock index categories:")
for c, n in stock[col_cat].value_counts().items():
    print(f"  {c}: {n}")

tracked = stock[stock[col_track] == "是"]  # 是
print(f"\nStock indices with tracking products: {len(tracked)}")
print(f"\nTracked stock index categories:")
for c, n in tracked[col_cat].value_counts().items():
    print(f"  {c}: {n}")

# The headline indices we MUST have
print("\n" + "=" * 60)
print("HEADLINE INDICES (must-have)")
print("=" * 60)
headline_codes = [
    "000300", "000905", "000852", "000906", "000016", "000001",
    "399001", "399006", "000688", "000010", "000009",
    "000510", "000903", "930050",
]
for code in headline_codes:
    row = df[df[col_code] == code]
    if len(row) > 0:
        r = row.iloc[0]
        print(f"  {code}  {r[col_name]:12}  cat={r[col_cat]}  members={r[col_count]}  tracked={r[col_track]}")
    else:
        print(f"  {code}  NOT FOUND in catalogue")

# Print all 规模 (scale/size) indices
print("\n" + "=" * 60)
print("ALL SCALE (规模) INDICES")
print("=" * 60)
scale = stock[stock[col_cat] == "规模"]
for _, r in scale.iterrows():
    print(f"  {r[col_code]}  {r[col_name]:16}  members={r[col_count]}  tracked={r[col_track]}")

# Print all 行业 (sector) indices with tracking products
print("\n" + "=" * 60)
print("SECTOR (行业) INDICES WITH TRACKING PRODUCTS")
print("=" * 60)
sector_tracked = stock[(stock[col_cat] == "行业") & (stock[col_track] == "是")]
for _, r in sector_tracked.iterrows():
    print(f"  {r[col_code]}  {r[col_name]:16}  members={r[col_count]}")

# Print all 主题 (thematic) indices with tracking products
print("\n" + "=" * 60)
print("THEMATIC (主题) INDICES WITH TRACKING PRODUCTS (sample)")
print("=" * 60)
theme_tracked = stock[(stock[col_cat] == "主题") & (stock[col_track] == "是")]
for _, r in theme_tracked.head(40).iterrows():
    hot = r[col_hot] if pd.notna(r[col_hot]) else ""
    print(f"  {r[col_code]}  {r[col_name]:16}  members={r[col_count]}  hot={hot}")
print(f"  ... ({len(theme_tracked)} total)")

# Print Smart Beta tagged
print("\n" + "=" * 60)
print("SMART BETA / STRATEGY INDICES WITH TRACKING")
print("=" * 60)
smart = stock[(stock[col_hot] == "Smart Beta") & (stock[col_track] == "是")]
for _, r in smart.iterrows():
    print(f"  {r[col_code]}  {r[col_name]:16}  cat={r[col_cat]}  members={r[col_count]}")

# Style indices
print("\n" + "=" * 60)
print("STYLE (风格) INDICES WITH TRACKING")
print("=" * 60)
style_tracked = stock[(stock[col_cat] == "风格") & (stock[col_track] == "是")]
for _, r in style_tracked.iterrows():
    print(f"  {r[col_code]}  {r[col_name]:16}  members={r[col_count]}")
