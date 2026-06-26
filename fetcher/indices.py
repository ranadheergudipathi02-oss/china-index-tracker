# Allow-list of tracked China A-share indices.
#
# Structure: each entry has:
#   code     — CSI/exchange index code (6-digit or Hxxxxx)
#   name     — short Chinese name
#   name_en  — English name (for the frontend)
#   board    — grouping for the frontend directory (SSE / SZSE / Cross / STAR / ChiNext)
#   category — Broad market / Sector / Thematic / Strategy
#   method   — "csindex" (primary) or "sina" (fallback for exchange-native indices)
#
# Excluded: bond, commodity, currency-hedged, HK/overseas, non-equity indices.
# Source: index_csindex_all() catalogue + index_stock_info(), verified Phase 0.

INDICES = [
    # ── BROAD MARKET (规模) ──────────────────────────────────────────
    {"code": "000300", "name": "沪深300",     "name_en": "CSI 300",          "board": "Cross",   "category": "Broad market", "method": "csindex"},
    {"code": "000905", "name": "中证500",     "name_en": "CSI 500",          "board": "Cross",   "category": "Broad market", "method": "csindex"},
    {"code": "000852", "name": "中证1000",    "name_en": "CSI 1000",         "board": "Cross",   "category": "Broad market", "method": "csindex"},
    {"code": "000906", "name": "中证800",     "name_en": "CSI 800",          "board": "Cross",   "category": "Broad market", "method": "csindex"},
    {"code": "000510", "name": "中证A500",    "name_en": "CSI A500",         "board": "Cross",   "category": "Broad market", "method": "csindex"},
    {"code": "000903", "name": "中证A100",    "name_en": "CSI A100",         "board": "Cross",   "category": "Broad market", "method": "csindex"},
    {"code": "930050", "name": "中证A50",     "name_en": "CSI A50",          "board": "Cross",   "category": "Broad market", "method": "csindex"},
    {"code": "000904", "name": "中证200",     "name_en": "CSI 200",          "board": "Cross",   "category": "Broad market", "method": "csindex"},
    {"code": "932000", "name": "中证2000",    "name_en": "CSI 2000",         "board": "Cross",   "category": "Broad market", "method": "csindex"},
    {"code": "000985", "name": "中证全指",    "name_en": "CSI All Share",    "board": "Cross",   "category": "Broad market", "method": "csindex"},

    # SSE exchange-native
    {"code": "000001", "name": "上证指数",    "name_en": "SSE Composite",    "board": "SSE",     "category": "Broad market", "method": "csindex"},
    {"code": "000016", "name": "上证50",      "name_en": "SSE 50",           "board": "SSE",     "category": "Broad market", "method": "csindex"},
    {"code": "000010", "name": "上证180",     "name_en": "SSE 180",          "board": "SSE",     "category": "Broad market", "method": "csindex"},
    {"code": "000009", "name": "上证380",     "name_en": "SSE 380",          "board": "SSE",     "category": "Broad market", "method": "csindex"},

    # SZSE exchange-native
    {"code": "399001", "name": "深证成指",    "name_en": "SZSE Component",   "board": "SZSE",    "category": "Broad market", "method": "sina"},
    {"code": "399006", "name": "创业板指",    "name_en": "ChiNext Index",    "board": "ChiNext", "category": "Broad market", "method": "sina"},

    # STAR Market (科创板)
    {"code": "000688", "name": "科创50",      "name_en": "STAR 50",          "board": "STAR",    "category": "Broad market", "method": "csindex"},
    {"code": "000698", "name": "科创100",     "name_en": "STAR 100",         "board": "STAR",    "category": "Broad market", "method": "csindex"},
    {"code": "931643", "name": "科创创业50",  "name_en": "STAR-ChiNext 50",  "board": "Cross",   "category": "Broad market", "method": "csindex"},

    # ── SECTOR (行业) ────────────────────────────────────────────────
    {"code": "399986", "name": "中证银行",    "name_en": "CSI Banks",        "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "000807", "name": "食品饮料",    "name_en": "F&B",              "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "000808", "name": "医药生物",    "name_en": "Pharma & Bio",     "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "000819", "name": "有色金属",    "name_en": "Non-ferrous Metal","board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "000928", "name": "800能源",     "name_en": "CSI 800 Energy",   "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "000932", "name": "800消费",     "name_en": "CSI 800 Staples",  "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "000933", "name": "800医卫",     "name_en": "CSI 800 Health",   "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "000935", "name": "800信息",     "name_en": "CSI 800 IT",       "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "399975", "name": "证券公司",    "name_en": "Securities",       "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "399998", "name": "中证煤炭",    "name_en": "CSI Coal",         "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "930697", "name": "家用电器",    "name_en": "Appliances",       "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "932087", "name": "集成电路",    "name_en": "IC / Semicon",     "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "932094", "name": "软件开发",    "name_en": "Software",         "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "931897", "name": "绿色电力",    "name_en": "Green Power",      "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "399965", "name": "800地产",     "name_en": "CSI 800 Real Est", "board": "Cross",   "category": "Sector", "method": "csindex"},
    {"code": "000841", "name": "800医药",     "name_en": "CSI 800 Pharma",   "board": "Cross",   "category": "Sector", "method": "csindex"},

    # ── THEMATIC (主题) ──────────────────────────────────────────────
    {"code": "399997", "name": "中证白酒",    "name_en": "CSI Baijiu",       "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "399987", "name": "中证酒",      "name_en": "CSI Liquor",       "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "399967", "name": "中证军工",    "name_en": "CSI Military",     "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "399976", "name": "CS新能车",    "name_en": "CSI NEV",          "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "399989", "name": "中证医疗",    "name_en": "CSI Medical",      "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "000827", "name": "中证环保",    "name_en": "CSI Environ",      "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "399808", "name": "中证新能",    "name_en": "CSI New Energy",   "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "399973", "name": "中证国防",    "name_en": "CSI Defense",      "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "399994", "name": "信息安全",    "name_en": "Info Security",    "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "399959", "name": "军工指数",    "name_en": "Military Index",   "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "399974", "name": "国企改革",    "name_en": "SOE Reform",       "board": "Cross",   "category": "Thematic", "method": "csindex"},
    {"code": "000846", "name": "ESG 100",     "name_en": "CSI ESG 100",     "board": "Cross",   "category": "Thematic", "method": "csindex"},

    # ── STRATEGY / SMART BETA ────────────────────────────────────────
    {"code": "000925", "name": "基本面50",    "name_en": "Fundamental 50",   "board": "Cross",   "category": "Strategy", "method": "csindex"},
    {"code": "000918", "name": "300成长",     "name_en": "CSI 300 Growth",   "board": "Cross",   "category": "Strategy", "method": "csindex"},
    {"code": "000919", "name": "300价值",     "name_en": "CSI 300 Value",    "board": "Cross",   "category": "Strategy", "method": "csindex"},
    {"code": "000015", "name": "红利指数",    "name_en": "SSE Dividend",     "board": "SSE",     "category": "Strategy", "method": "csindex"},
]
