"""Phase 4 - daily orchestrator.

Chain: fetch (+diff, snapshot guard)  ->  build site aggregates  ->  commit ALL
(current/ + changes.jsonl + meta.json + assets/)  ->  push (non-fatal)  ->  Telegram alert.

Invoked by run_daily.bat via Windows Task Scheduler (~13:00 IST / 15:30 CST).
Extra args pass through to the fetcher, e.g.   python run_daily.py --only "CSI 300"
"""
import os, sys, json

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(ROOT, "fetcher"))
sys.path.insert(0, os.path.join(ROOT, "web"))

import config as C
import fetch, notify, build_site


def run():
    print("=" * 72)
    print("DAILY RUN", fetch.now_ist())
    print("=" * 72)

    extra = sys.argv[1:]
    sys.argv = ["fetch.py", "--no-commit"] + extra
    fetch.main()

    print("\n" + "-" * 40 + "\nbuild site aggregates")
    build_site.main()

    meta = json.load(open(C.META_FILE, encoding="utf-8"))
    s = meta.get("summary", {})

    print("\n" + "-" * 40 + "\ncommit + push")
    fetch.git_commit(f"daily {fetch.today_ist()}: {s.get('indices_changed', 0)} change(s), "
                     f"{s.get('ok', 0)}/{s.get('total', 0)} ok")

    print("\n" + "-" * 40 + "\nalerts")
    notify.check_and_alert(meta)

    print("\nDAILY RUN COMPLETE", fetch.now_ist())


if __name__ == "__main__":
    run()
