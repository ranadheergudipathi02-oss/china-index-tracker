# Phase 0 Findings — China A-Share Index Tracker

## Reachability (from Indian residential IP)

| Source | Status | Latency | Notes |
|--------|--------|---------|-------|
| csindex.com.cn homepage | OK | ~2-3s | No geo-block |
| AkShare `index_stock_cons_csindex` | OK | 4-10s/index | Primary method, wraps csindex.com.cn Excel download |
| AkShare `index_stock_cons` (Sina) | OK | ~1.5s/index | Fallback, fewer columns |
| eastmoney API | Unreliable | 502s intermittent | Not needed — AkShare suffices |
| csindex.com.cn weight API (`/csindex-home/index/weight/`) | 404 | — | Endpoint removed/changed |

## AkShare Function Selection

- **Primary**: `index_stock_cons_csindex(symbol=code)` — returns date, index code/name (CN+EN),
  constituent code/name (CN+EN), exchange. Works for all CSI-managed indices.
- **Fallback**: `index_stock_cons(symbol=code)` — Sina-sourced, returns code + Chinese name only.
  Needed for SZSE exchange-native indices (399001 SZSE Component, 399006 ChiNext) where the
  csindex function fails.
- **Catalogue**: `index_csindex_all()` — 2341 indices with rich metadata (category, asset class,
  member count, tracking products). Used to build the allow-list.
- **No ISIN**: AkShare does not return ISIN. Identity key = 6-digit ticker code.

## Pinned Version

`akshare==1.18.64` — tested and working 2026-06-26.

## Catalogue Analysis

- 2341 total indices in CSI catalogue
- 1488 equity (股票) indices
- 366 with tracking products (ETFs/funds tracking them)
- Categories: 规模 (Scale/Broad) 46, 行业 (Sector) 429, 主题 (Thematic) 675, 策略 (Strategy) 297, 风格 (Style) 36

## Allow-List: 48 Indices

**Broad market (16)**: CSI 300/500/1000/800/200/2000, A50/A100/A500, All Share,
SSE 50/180/380, SZSE Component, ChiNext, STAR-ChiNext 50

**Sector (16)**: Banks, F&B, Pharma/Bio, Non-ferrous Metal, Energy, Staples, Health, IT,
Securities, Coal, Appliances, IC/Semicon, Software, Green Power, Real Estate, 800 Pharma

**Thematic (12)**: Baijiu, Liquor, Military (×2), NEV, Medical, Environment, New Energy,
Defense, Info Security, SOE Reform, ESG 100

**Strategy (4)**: Fundamental 50, 300 Growth, 300 Value, SSE Dividend

## Full Run Results

- 48/48 indices fetched successfully (zero failures)
- 13,195 total constituent entries (5,134 unique stocks)
- Total run time: 236 seconds (~4 minutes)
- No rate-limiting or geo-blocking encountered

## Key Design Decisions

1. AkShare is the SOLE data source (no raw HTTP fallback needed — AkShare itself falls back internally)
2. Auto-fallback from csindex → sina within the fetcher for any index that fails csindex
3. Sleep 2s between requests (AkShare calls are 4-10s themselves, so effective rate is ~6-12s/index)
4. Board grouping for frontend: Cross (CSI cross-market), SSE, SZSE, ChiNext, STAR
5. UTF-8 stdout wrapper required on Windows (Chinese characters)
