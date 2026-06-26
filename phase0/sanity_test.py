"""Phase 0 — Sanity Test for China A-Share Index Tracker.

Tests from THIS IP (Indian residential):
  (a) Reachability: AkShare, csindex.com.cn, eastmoney
  (b) Constituent fetch: CSI 300, SSE 50, ChiNext — parse + print sample
  (c) Full CSI index catalogue — assess coverage for allow-list
  (d) Verdict: AkShare vs raw HTTP per source

Run:  python phase0/sanity_test.py
"""
import time, json, traceback, sys, os, io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# (a) Reachability probes
# ---------------------------------------------------------------------------
def probe_requests(label, url, headers=None, timeout=15):
    import requests
    t0 = time.time()
    try:
        r = requests.get(url, headers=headers or {}, timeout=timeout)
        ms = int((time.time() - t0) * 1000)
        ok = r.status_code == 200
        snippet = r.text[:200].replace("\n", " ").strip()
        return ok, r.status_code, ms, snippet
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        return False, 0, ms, f"{type(e).__name__}: {e}"

def test_reachability():
    print("=" * 72)
    print("(a) REACHABILITY from this IP")
    print("=" * 72)
    import requests

    targets = [
        ("csindex.com.cn homepage",
         "https://www.csindex.com.cn/",
         {"User-Agent": "Mozilla/5.0", "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}),
        ("eastmoney — quote API (simple ping)",
         "https://push2.eastmoney.com/api/qt/clist/get?pn=1&pz=5&fs=b:MK0010",
         {"User-Agent": "Mozilla/5.0", "Referer": "https://www.eastmoney.com/"}),
    ]
    results = {}
    for label, url, hdrs in targets:
        ok, status, ms, snippet = probe_requests(label, url, hdrs)
        tag = "OK" if ok else "FAIL"
        print(f"  [{tag}] {label}  status={status}  {ms}ms")
        if not ok:
            print(f"        {snippet[:120]}")
        results[label] = ok
        time.sleep(0.5)

    # Discover correct csindex API endpoint
    print("\n  Probing csindex.com.cn API endpoints...")
    api_candidates = [
        ("v1: /csindex-home/index/weight/000300",
         "https://www.csindex.com.cn/csindex-home/index/weight/000300"),
        ("v2: /csindex-home/perf/index-perf?indexCode=000300",
         "https://www.csindex.com.cn/csindex-home/perf/index-perf?indexCode=000300"),
        ("v3: POST /csindex-home/index-list/query-index-item",
         None),  # POST — handled separately
    ]
    hdrs = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.csindex.com.cn/",
            "Accept": "application/json, text/plain, */*", "Accept-Language": "zh-CN,zh;q=0.9"}

    for label, url in api_candidates:
        if url is None:
            # POST endpoint
            try:
                t0 = time.time()
                r = requests.post(
                    "https://www.csindex.com.cn/csindex-home/index-list/query-index-item",
                    headers={**hdrs, "Content-Type": "application/json"},
                    json={"indexFilter": "", "isPagination": True, "pageNum": 1, "pageSize": 5},
                    timeout=20)
                ms = int((time.time() - t0) * 1000)
                print(f"    [{r.status_code}] {label}  {ms}ms")
                if r.status_code == 200:
                    d = r.json()
                    print(f"          keys: {list(d.keys()) if isinstance(d, dict) else type(d)}")
                    if isinstance(d, dict) and "data" in d:
                        print(f"          data keys: {list(d['data'].keys()) if isinstance(d['data'], dict) else type(d['data'])}")
                results[label] = r.status_code == 200
            except Exception as e:
                print(f"    [FAIL] {label}: {e}")
                results[label] = False
        else:
            ok, status, ms, snippet = probe_requests(label, url, hdrs)
            print(f"    [{status}] {label}  {ms}ms")
            if status == 200:
                print(f"          {snippet[:150]}")
            results[label] = ok
        time.sleep(0.5)

    return results


# ---------------------------------------------------------------------------
# (b) Constituent fetch — AkShare
# ---------------------------------------------------------------------------
def test_akshare_constituents():
    print("\n" + "=" * 72)
    print("(b) CONSTITUENT FETCH via AkShare")
    print("=" * 72)
    import akshare as ak

    test_indices = [
        ("CSI 300",   "000300"),
        ("SSE 50",    "000016"),
        ("ChiNext",   "399006"),
        ("CSI 500",   "000905"),
    ]
    results = {}
    for name, symbol in test_indices:
        print(f"\n  --- {name} (symbol={symbol}) ---")

        # Try index_stock_cons_csindex first
        t0 = time.time()
        try:
            df = ak.index_stock_cons_csindex(symbol=symbol)
            ms = int((time.time() - t0) * 1000)
            n = len(df)
            cols = list(df.columns)
            print(f"  [index_stock_cons_csindex] OK  {n} constituents  {ms}ms")
            print(f"  columns: {cols}")
            for _, row in df.head(5).iterrows():
                print(f"    {dict(row)}")
            results[name] = {"ok": True, "count": n, "ms": ms, "columns": cols,
                             "method": "index_stock_cons_csindex"}
            time.sleep(1.5)
            continue
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            print(f"  [index_stock_cons_csindex] FAIL  {ms}ms  {type(e).__name__}: {e}")
            time.sleep(1)

        # Fallback: index_stock_cons (Sina-sourced)
        t0 = time.time()
        try:
            df = ak.index_stock_cons(symbol=symbol)
            ms = int((time.time() - t0) * 1000)
            n = len(df)
            cols = list(df.columns)
            print(f"  [index_stock_cons (sina)] OK  {n} constituents  {ms}ms")
            print(f"  columns: {cols}")
            for _, row in df.head(5).iterrows():
                print(f"    {dict(row)}")
            results[name] = {"ok": True, "count": n, "ms": ms, "columns": cols,
                             "method": "index_stock_cons"}
            time.sleep(1.5)
            continue
        except Exception as e:
            ms = int((time.time() - t0) * 1000)
            print(f"  [index_stock_cons (sina)] FAIL  {ms}ms  {type(e).__name__}: {e}")

        results[name] = {"ok": False, "error": str(e)}
        time.sleep(1.5)

    # Also test weight variant
    print(f"\n  --- CSI 300 WEIGHT variant ---")
    t0 = time.time()
    try:
        df = ak.index_stock_cons_weight_csindex(symbol="000300")
        ms = int((time.time() - t0) * 1000)
        n = len(df)
        cols = list(df.columns)
        print(f"  [index_stock_cons_weight_csindex] OK  {n} rows  {ms}ms")
        print(f"  columns: {cols}")
        for _, row in df.head(3).iterrows():
            print(f"    {dict(row)}")
        results["CSI 300 weight"] = {"ok": True, "count": n, "ms": ms, "columns": cols}
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        print(f"  [index_stock_cons_weight_csindex] FAIL  {ms}ms  {type(e).__name__}: {e}")
        results["CSI 300 weight"] = {"ok": False, "error": str(e)}

    return results


# ---------------------------------------------------------------------------
# (c) Full CSI index catalogue
# ---------------------------------------------------------------------------
def test_index_catalogue():
    print("\n" + "=" * 72)
    print("(c) FULL CSI INDEX CATALOGUE")
    print("=" * 72)
    import akshare as ak

    t0 = time.time()
    try:
        df = ak.index_stock_info()
        ms = int((time.time() - t0) * 1000)
        n = len(df)
        cols = list(df.columns)
        print(f"  [index_stock_info] OK  {n} indices  {ms}ms")
        print(f"  columns: {cols}")
        print(f"\n  Sample (first 30):")
        for _, row in df.head(30).iterrows():
            print(f"    {dict(row)}")

        # Save full catalogue to file for allow-list building
        out_path = os.path.join(os.path.dirname(__file__), "csi_catalogue.json")
        records = df.to_dict(orient="records")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=1)
        print(f"\n  Full catalogue saved to {out_path}")

        return {"ok": True, "count": n, "columns": cols, "ms": ms}
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        print(f"  FAIL  {ms}ms  {type(e).__name__}: {e}")
        traceback.print_exc()
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# (c2) Also try index_csindex_all for another catalogue view
# ---------------------------------------------------------------------------
def test_csindex_all():
    print("\n" + "=" * 72)
    print("(c2) CATALOGUE via index_csindex_all")
    print("=" * 72)
    import akshare as ak

    t0 = time.time()
    try:
        df = ak.index_csindex_all()
        ms = int((time.time() - t0) * 1000)
        n = len(df)
        cols = list(df.columns)
        print(f"  [index_csindex_all] OK  {n} indices  {ms}ms")
        print(f"  columns: {cols}")
        print(f"\n  Sample (first 15):")
        for _, row in df.head(15).iterrows():
            print(f"    {dict(row)}")

        out_path = os.path.join(os.path.dirname(__file__), "csindex_all_catalogue.json")
        records = df.to_dict(orient="records")
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=1)
        print(f"\n  Full catalogue saved to {out_path}")
        return {"ok": True, "count": n, "columns": cols, "ms": ms}
    except Exception as e:
        ms = int((time.time() - t0) * 1000)
        print(f"  FAIL  {ms}ms  {type(e).__name__}: {e}")
        return {"ok": False, "error": str(e)}


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main():
    print("PHASE 0 — China A-Share Index Tracker Sanity Test")
    print(f"AkShare version: ", end="")
    try:
        import akshare as ak
        print(ak.__version__)
    except Exception as e:
        print(f"import failed: {e}")
        return

    reach = test_reachability()
    ak_results = test_akshare_constituents()
    cat_results = test_index_catalogue()
    cat2_results = test_csindex_all()

    # ---------------------------------------------------------------------------
    # (d) Verdict
    # ---------------------------------------------------------------------------
    print("\n" + "=" * 72)
    print("(d) VERDICT")
    print("=" * 72)

    print("\n  Reachability:")
    for k, v in reach.items():
        print(f"    {'OK' if v else 'FAIL':6} {k}")

    print("\n  AkShare constituent fetch:")
    for k, v in ak_results.items():
        if v["ok"]:
            print(f"    OK    {k}: {v['count']} members via {v.get('method','?')} in {v['ms']}ms")
        else:
            print(f"    FAIL  {k}: {v.get('error', '?')}")

    if cat_results.get("ok"):
        print(f"\n  Index catalogue (index_stock_info): {cat_results['count']} indices")
    else:
        print(f"\n  Index catalogue (index_stock_info): FAILED")

    if cat2_results.get("ok"):
        print(f"  Index catalogue (index_csindex_all): {cat2_results['count']} indices")
    else:
        print(f"  Index catalogue (index_csindex_all): FAILED")

    print("\n" + "-" * 40)
    print("  NEXT: review csi_catalogue.json / csindex_all_catalogue.json to build allow-list")
    print("\nPHASE 0 COMPLETE\n")


if __name__ == "__main__":
    main()
