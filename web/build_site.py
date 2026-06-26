"""Generate the two aggregates the static frontend reads:
  assets/directory.json  — categorized index directory (+ count, file, last_changed)
  assets/stocks.json     — reverse index: stock -> indices it belongs to
Reads current/*.json + changes.jsonl + meta.json. Run after fetch.py.
"""
import os, sys, json, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fetcher"))
import config as C

ASSETS = os.path.join(C.PROJECT_ROOT, "assets")
os.makedirs(ASSETS, exist_ok=True)


def load_last_changed():
    last = {}
    if os.path.exists(C.CHANGES_FILE):
        for line in open(C.CHANGES_FILE, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            e = json.loads(line)
            d = e["date"]
            if e["index"] not in last or d > last[e["index"]]["date"]:
                last[e["index"]] = {"date": d, "type": e["type"]}
    return last


def main():
    meta = json.load(open(C.META_FILE, encoding="utf-8"))
    last_changed = load_last_changed()

    directory = []
    for iid, m in meta["indices"].items():
        if m["status"] not in ("ok", "guard_skipped"):
            continue
        parts = iid.split(":", 1)
        board = parts[0]
        name = parts[1] if len(parts) > 1 else iid
        lc = last_changed.get(iid, {})
        # read the current file to get English name + category
        fpath = os.path.join(C.CURRENT_DIR, m.get("file", ""))
        name_en = ""
        category = ""
        if os.path.exists(fpath):
            try:
                doc = json.load(open(fpath, encoding="utf-8"))
                name_en = doc.get("name_en", "")
                category = doc.get("category", "")
            except Exception:
                pass
        directory.append({"id": iid, "board": board, "name": name, "name_en": name_en,
                          "count": m.get("count"), "file": m.get("file"), "code": m.get("code"),
                          "category": category or "Thematic",
                          "last_changed": lc.get("date"), "last_change_type": lc.get("type")})
    directory.sort(key=lambda d: (d["board"], d["category"], d["name"]))

    # reverse index: symbol -> stock + indices it's in
    stocks = {}
    for path in glob.glob(os.path.join(C.CURRENT_DIR, "*.json")):
        doc = json.load(open(path, encoding="utf-8"))
        iid = doc["id"]
        for mem in doc["members"]:
            key = mem["symbol"]
            s = stocks.setdefault(key, {"symbol": mem["symbol"], "name": mem.get("name", ""),
                                        "name_en": mem.get("name_en", ""), "indices": []})
            if mem.get("name") and len(mem["name"]) > len(s["name"]):
                s["name"] = mem["name"]
            if mem.get("name_en") and len(mem.get("name_en", "")) > len(s.get("name_en", "")):
                s["name_en"] = mem["name_en"]
            s["indices"].append(iid)
    stock_list = sorted(({"symbol": s["symbol"], "name": s["name"], "name_en": s.get("name_en", ""),
                          "indices": sorted(set(s["indices"]))} for s in stocks.values()),
                        key=lambda s: s["symbol"])

    json.dump(directory, open(os.path.join(ASSETS, "directory.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))
    json.dump(stock_list, open(os.path.join(ASSETS, "stocks.json"), "w", encoding="utf-8"),
              ensure_ascii=False, separators=(",", ":"))

    cats = {}
    for d in directory:
        key = f'{d["board"]} · {d["category"]}'
        cats[key] = cats.get(key, 0) + 1
    print(f"directory.json: {len(directory)} indices")
    for k in sorted(cats):
        print(f"   {k}: {cats[k]}")
    print(f"stocks.json: {len(stock_list)} unique stocks")


if __name__ == "__main__":
    main()
