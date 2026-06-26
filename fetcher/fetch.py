"""Phase 1+2 fetcher + diff engine: loop allow-listed China A-share indices via AkShare,
throttle + retry, apply snapshot guard, diff against previous snapshot, append changes.jsonl,
write current/<slug>.json + meta.json, then best-effort (non-fatal) git commit.

Run:  python fetcher/fetch.py
"""
import os, sys, json, time, re, subprocess, threading
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config as C
import diff
from indices import INDICES
from datetime import datetime


def now_ist():
    return datetime.now(C.IST).isoformat(timespec="seconds")

def today_ist():
    return datetime.now(C.IST).date().isoformat()

def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def fetch_csindex(code):
    """Fetch via AkShare index_stock_cons_csindex (wraps csindex.com.cn)."""
    import akshare as ak
    df = ak.index_stock_cons_csindex(symbol=code)
    members = []
    for _, row in df.iterrows():
        sym = str(row.get("成分券代码", "")).strip()
        if not sym:
            continue
        exchange = str(row.get("交易所英文名称", ""))
        suffix = ".SH" if "Shanghai" in exchange else ".SZ"
        members.append({
            "symbol": sym,
            "name": str(row.get("成分券名称", "")).strip(),
            "name_en": str(row.get("成分券英文名称", "")).strip(),
        })
    return members


def fetch_sina(code):
    """Fallback: AkShare index_stock_cons (Sina-sourced). Fewer fields."""
    import akshare as ak
    df = ak.index_stock_cons(symbol=code)
    members = []
    for _, row in df.iterrows():
        sym = str(row.get("品种代码", row.get("code", ""))).strip()
        if not sym:
            continue
        members.append({
            "symbol": sym,
            "name": str(row.get("品种名称", row.get("name", ""))).strip(),
            "name_en": "",
        })
    return members


def call_with_timeout(fn, args, timeout):
    """Run fn(*args) in a daemon thread with a hard join timeout.
    AkShare/requests can hang on a half-open connection with no socket timeout; a plain
    call would block the whole run forever. Daemon thread (not ThreadPoolExecutor, whose
    atexit join would itself hang on the stuck thread) so a hung call can't block exit.
    """
    box = {}
    def worker():
        try:
            box["val"] = fn(*args)
        except Exception as e:  # noqa: BLE001 — surface any fetch error to the retry loop
            box["err"] = e
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    t.join(timeout)
    if t.is_alive():
        raise TimeoutError(f"hard timeout after {timeout}s")
    if "err" in box:
        raise box["err"]
    return box.get("val")


def with_retry(fn, *args):
    last = "failed"
    for i in range(C.RETRIES):
        try:
            m = call_with_timeout(fn, args, C.CALL_TIMEOUT)
            if m:
                return m
            last = "empty response"
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
        time.sleep(C.RETRY_BACKOFF * (i + 1))
    raise RuntimeError(last)


def read_old(path):
    try:
        return json.load(open(path, encoding="utf-8")).get("members")
    except Exception:
        return None


def handle(idx, meta, date_str, baseline):
    code = idx["code"]
    name = idx["name"]
    iid = f'{idx["board"]}:{name}'
    path = os.path.join(C.CURRENT_DIR, f"{slugify(code + '-' + name)}.json")

    fetch_fn = fetch_csindex if idx["method"] == "csindex" else fetch_sina
    try:
        members = with_retry(fetch_fn, code)
    except Exception as e:
        # If csindex failed, try sina as fallback
        if idx["method"] == "csindex":
            try:
                members = with_retry(fetch_sina, code)
                print(f"  (fell back to sina for {code})")
            except Exception as e2:
                meta["indices"][iid] = {"status": "failed", "reason": str(e),
                                        "fallback_error": str(e2), "count": 0,
                                        "code": code, "fetched_at": now_ist()}
                return "failed"
        else:
            meta["indices"][iid] = {"status": "failed", "reason": str(e), "count": 0,
                                    "code": code, "fetched_at": now_ist()}
            return "failed"

    old = read_old(path)
    n = len(members)

    # snapshot guard
    if old is not None and n < len(old) * C.SHRINK_GUARD:
        meta["indices"][iid] = {"status": "guard_skipped", "count": n, "prev_count": len(old),
                                "reason": f"shrank {len(old)}->{n}", "code": code,
                                "fetched_at": now_ist()}
        return "guard"

    # diff / baseline
    if baseline or old is None:
        diff.append_change(diff.make_entry(date_str, iid, "initial", members, []))
        added_n, removed_n, changed = n, 0, True
    else:
        added, removed = diff.compute_diff(old, members)
        if added or removed:
            diff.append_change(diff.make_entry(date_str, iid, "change", added, removed))
        added_n, removed_n, changed = len(added), len(removed), bool(added or removed)

    # current/<slug>.json — no timestamp inside
    doc = {"id": iid, "code": code, "board": idx["board"], "name": name,
           "name_en": idx["name_en"], "category": idx["category"],
           "count": n, "members": members}
    json.dump(doc, open(path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    meta["indices"][iid] = {"status": "ok", "count": n,
                            "prev_count": (len(old) if old else None),
                            "changed": changed, "added": added_n, "removed": removed_n,
                            "file": os.path.basename(path), "code": code,
                            "fetched_at": now_ist()}
    return "ok"


def git_commit(msg):
    root = C.PROJECT_ROOT
    if not os.path.isdir(os.path.join(root, ".git")):
        print("git: no repo (skipping commit)")
        return
    subprocess.run(["git", "-C", root, "add", "current", "changes.jsonl", "meta.json", "assets"],
                   capture_output=True, text=True)
    r = subprocess.run(["git", "-C", root, "commit", "-m", msg], capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip().splitlines()
    print("git commit:", out[-1] if out else "(nothing to commit)")
    try:
        p = subprocess.run(["git", "-C", root, "push"], capture_output=True, text=True, timeout=60)
        msg2 = (p.stdout + p.stderr).strip().splitlines()
        print("git push:", "ok" if p.returncode == 0 else
              f"skipped/non-fatal ({msg2[-1] if msg2 else p.returncode})")
    except Exception as e:
        print("git push: skipped/non-fatal —", e)


def ensure_utf8_stdout():
    """Idempotent: reconfigure stdout/stderr to UTF-8 (Chinese names on Windows cp1252).
    Uses reconfigure() rather than re-wrapping so it's safe to call from the orchestrator
    after it has already set encoding — re-wrapping twice closes the buffer (I/O on closed file).
    """
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def main():
    ensure_utf8_stdout()
    os.makedirs(C.CURRENT_DIR, exist_ok=True)
    items = INDICES[:]
    if "--only" in sys.argv:
        sub = sys.argv[sys.argv.index("--only") + 1].lower()
        items = [it for it in items if sub in f'{it["code"]} {it["name"]} {it["name_en"]}'.lower()]
    if "--resume" in sys.argv:
        # Skip indices already written this baseline; lets an interrupted run finish
        # without re-fetching (slow Chinese sources). Safe: unseen index -> old is None
        # -> seeded "initial" regardless of the baseline flag (see handle()).
        before = len(items)
        items = [it for it in items
                 if not os.path.exists(os.path.join(C.CURRENT_DIR, f"{slugify(it['code'] + '-' + it['name'])}.json"))]
        print(f"[resume] {before - len(items)} already present, fetching remaining {len(items)}")
    date_str = today_ist()
    baseline = not os.path.exists(C.CHANGES_FILE)
    print(f"loaded {len(items)} indices  date={date_str}"
          f"{'  [BASELINE run: seeding initial]' if baseline else ''}\n")

    meta = {"last_run": now_ist(), "indices": {}}
    if os.path.exists(C.META_FILE):
        try:
            meta["indices"] = json.load(open(C.META_FILE, encoding="utf-8")).get("indices", {})
        except Exception:
            pass

    t0 = time.time()
    failed = []
    changes = []
    for i, it in enumerate(items):
        st = handle(it, meta, date_str, baseline)
        iid = f'{it["board"]}:{it["name"]}'
        m = meta["indices"][iid]
        tag = f"[{i+1}/{len(items)}]"
        if st == "ok" and m.get("changed"):
            changes.append((iid, m["added"], m["removed"]))
            print(f"  {tag} {it['code']:8} {it['name']:12} -> {st} ({m['count']} members, +{m['added']}/-{m['removed']})")
        elif st == "ok":
            print(f"  {tag} {it['code']:8} {it['name']:12} -> {st} ({m['count']} members)")
        else:
            print(f"  {tag} {it['code']:8} {it['name']:12} -> {st}")
            if st == "failed":
                failed.append(it)
        time.sleep(C.AKSHARE_SLEEP)

    if failed:
        print(f"\nretry pass: {len(failed)} failed, cooling down 10s...")
        time.sleep(10)
        for it in failed:
            st = handle(it, meta, date_str, baseline)
            iid = f'{it["board"]}:{it["name"]}'
            if st == "ok" and meta["indices"][iid].get("changed"):
                changes.append((iid, meta["indices"][iid]["added"], meta["indices"][iid]["removed"]))
            print(f"  retry {it['code']:8} {it['name']:12} -> {st}")
            time.sleep(3.0)

    statuses = [m["status"] for m in meta["indices"].values()]
    meta["duration_sec"] = round(time.time() - t0, 1)
    meta["summary"] = {"total": len(meta["indices"]), "ok": statuses.count("ok"),
                       "failed": statuses.count("failed"), "guard_skipped": statuses.count("guard_skipped"),
                       "indices_changed": len(changes),
                       "members_added": sum(c[1] for c in changes),
                       "members_removed": sum(c[2] for c in changes)}
    json.dump(meta, open(C.META_FILE, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

    print(f"\nDONE in {meta['duration_sec']}s  {meta['summary']}")
    if changes:
        print("changes this run:")
        for iid, a, r in changes:
            print(f"   {iid:44} +{a} -{r}")
    if "--no-commit" not in sys.argv:
        git_commit(f"fetch {date_str}: {len(changes)} index change(s), "
                   f"{meta['summary']['ok']}/{len(items)} ok")


if __name__ == "__main__":
    main()
