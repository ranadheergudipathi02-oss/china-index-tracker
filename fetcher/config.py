# Fetcher configuration: paths, throttle/retry, correctness-guard thresholds.
import os
from datetime import timezone, timedelta

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENT_DIR  = os.path.join(PROJECT_ROOT, "current")
META_FILE    = os.path.join(PROJECT_ROOT, "meta.json")
CHANGES_FILE = os.path.join(PROJECT_ROOT, "changes.jsonl")

IST = timezone(timedelta(hours=5, minutes=30))

# AkShare is the primary data source (wraps csindex.com.cn).
# Pin version: akshare==1.18.64
AKSHARE_SLEEP = 2.0          # seconds between AkShare calls (csindex is slow, ~5-10s per call)
RETRIES = 3
RETRY_BACKOFF = 3.0           # seconds * attempt (generous for Chinese sources)
CALL_TIMEOUT = 45            # HARD cap per fetch call; AkShare/requests can hang with no socket
                             # timeout — without this, one stuck index stalls the whole run forever.
                             # Normal calls 1-3s; largest (SSE Composite ~2200 rows) ~7s. 45s = wide margin.

# correctness guard: never overwrite a healthy snapshot with a suspiciously short fetch
SHRINK_GUARD = 0.5
