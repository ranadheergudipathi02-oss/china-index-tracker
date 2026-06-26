# China A-Share Index Tracker

Static, always-on reference site cataloguing mainland-China (A-share) stock index
constituents with auto-tracked add/remove history. Sibling of the NSE/BSE India tracker —
same architecture, only the data-sourcing layer differs (AkShare → csindex.com.cn).

## Architecture

- **Fetcher** (`fetcher/fetch.py`): pulls allow-listed indices via AkShare, throttle + retry,
  snapshot guard, diffs vs previous snapshot, appends `changes.jsonl`.
- **Storage**: pure JSON flat files, append-only. No database.
  - `current/<code-name>.json` — overwritten each run; current constituents (no timestamp inside → clean git).
  - `changes.jsonl` — append-only; one line per detected diff; `type = "initial" | "change"`.
  - `meta.json` — last-run time + per-index status.
- **Site** (`index.html` + `assets/`): 100% static, reads the JSON. Serve over HTTP.
- **Orchestrator** (`run_daily.py`): fetch → build site aggregates → git commit/push → Telegram alert.

## Data source

- AkShare `index_stock_cons_csindex` (primary, wraps csindex.com.cn).
- Auto-fallback to `index_stock_cons` (Sina) for SZSE-native indices (399001, 399006).
- Pinned: `akshare==1.18.64`. See `PHASE0_FINDINGS.md`.
- Identity key = 6-digit ticker (AkShare returns no ISIN).

## Run

```
pip install -r requirements.txt
python fetcher/fetch.py          # fetch + diff + write (first run = baseline)
python web/build_site.py         # rebuild directory.json + stocks.json
python -m http.server 8090       # serve, then open http://localhost:8090
```

Or the full daily chain:  `python run_daily.py`

## Schedule (Windows Task Scheduler)

A-share market closes 15:00 CST (UTC+8) = 12:30 IST. Fetch runs 13:00 IST (15:30 CST).
Register once as Administrator:  `.\register_task.ps1`

## Telegram alerts (optional)

Create `fetcher/secrets.json` (git-ignored):
```json
{"telegram_token": "...", "telegram_chat_id": "..."}
```
Alerts fire on fetch failures / unhealthy runs — NOT on zero membership changes (the normal state).

## Coverage

51 indices: broad market (incl. CSI 300/500/1000/800, SSE 50/180/380/Composite, SZSE Component,
ChiNext, STAR 50/100), sector, thematic, strategy. Allow-list in `fetcher/indices.py`.
Excludes bond/commodity/currency-hedged/HK-overseas variants.

## Not yet done (deployment)

- `git init` + GitHub remote + GitHub Pages (publish).
- Run `register_task.ps1` to schedule.
- Populate `secrets.json` for Telegram.
