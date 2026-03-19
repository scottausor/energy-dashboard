# config.py — Central configuration for all tickers and settings

# ── Coal Benchmarks ────────────────────────────────────────────────────────────
COAL_TICKERS = {
    "XO1 Comdty": {"name": "API4 – FOB Richards Bay 6,000 kCal",  "short": "API4 - FOB Richards Bay 6'000kCal",  "color": "#F4A261"},
    "XA1 Comdty": {"name": "API2 – CIF ARA 6,000 kCal",           "short": "API2 - CIF ARA 6'000kCal",          "color": "#E76F51"},
    "XW1 Comdty": {"name": "NEWC – FOB Newcastle 6,000 kCal",      "short": "FOB Newcastle 6'000kCal",           "color": "#E9C46A"},
}

# Spread: XA1 - XO1  (ARA minus Richards Bay = implied freight)
COAL_SPREAD = {
    "ticker_a":  "XA1 Comdty",
    "ticker_b":  "XO1 Comdty",
    "name":      "Richards Bay – ARA Implied Freight (XA1 – XO1)",
    "short":     "Richards Bay - ARA Implied Freight",
    "color":     "#52B788",
}

# Tickers that get futures-chain pulls for the Coal tab (CCRV forward curves)
COAL_FUTURES_TICKERS = ["XO1 Comdty", "XA1 Comdty", "XW1 Comdty"]

# ── Explicit CT contracts  (Monthly / Quarterly / Yearly) ──────────────────────
COAL_CT_CONTRACTS = {
    "API4 - FOB Richards Bay": {
        "color":     "#F4A261",
        "Monthly":   [f"XO{i} Comdty"  for i in range(1, 13)],
        "Quarterly": [f"XS{i} Comdty"  for i in range(1, 9)],
        "Yearly":    [f"BV{i} Comdty"  for i in range(1, 4)],
    },
    "API2 - CIF ARA": {
        "color":     "#E76F51",
        "Monthly":   [f"XA{i} Comdty"  for i in range(1, 13)],
        "Quarterly": [f"XE{i} Comdty"  for i in range(1, 9)],
        "Yearly":    [f"TM{i} Comdty"  for i in range(1, 4)],
    },
    "NEWC - FOB Newcastle": {
        "color":     "#E9C46A",
        "Monthly":   [f"XW{i} Comdty"  for i in range(1, 13)],
        "Quarterly": [f"FK{i} Comdty"  for i in range(1, 9)],
        "Yearly":    [f"YJ{i} Comdty"  for i in range(1, 4)],
    },
}

# ── Physical Coal (Argus / Platts assessments) ─────────────────────────────────
PHYSICAL_COAL_TICKERS = {
    # ── Richards Bay ────────────────────────────────────────────────────────
    "CO03C001 Index": {"name": "Argus – Daily RB1",         "short": "RB1 Daily",  "color": "#F4A261"},
    "CO03C008 Index": {"name": "Argus – Daily RB2",         "short": "RB2 Daily",  "color": "#E76F51"},
    "CO03C005 Index": {"name": "Argus – Weekly RB3",        "short": "RB3 Weekly", "color": "#E9C46A"},
    "CO01C015 Index": {"name": "Argus – Weekly RB4",        "short": "RB4 Weekly", "color": "#F3C677"},
    # ── ARA ─────────────────────────────────────────────────────────────────
    "CO22C015 Index": {"name": "Argus – Daily ARA 6,000 kCal",  "short": "ARA 6k Daily",  "color": "#2A9D8F"},
    "CO20C017 Index": {"name": "Argus – Weekly ARA 6,000 kCal", "short": "ARA 6k Weekly",  "color": "#48CAE4"},
    "CO24C069 Index": {"name": "Argus – Daily ARA 5,700 kCal",  "short": "ARA 5.7k Daily", "color": "#0096C7"},
    # ── Export Markets ───────────────────────────────────────────────────────
    "NACI00B4 Index": {"name": "Platts CFR West Coast India 5,500 kCal", "short": "India W Coast", "color": "#8338EC"},
    "NACI00AD Index": {"name": "Platts CFR East Coast India 5,500 kCal", "short": "India E Coast", "color": "#7209B7"},
    "NACI019C Index": {"name": "Platts CFR Pakistan 5,500 kCal",         "short": "Pakistan",      "color": "#B5179E"},
    "NACI0137 Index": {"name": "Platts CFR South China 5,500 kCal",      "short": "S China",       "color": "#F72585"},
}

# Sections group tickers into named sub-sections within the Physical Coal tab.
PHYSICAL_COAL_SECTIONS = {
    "Richards Bay": [
        "CO03C001 Index", "CO03C008 Index",
        "CO03C005 Index", "CO01C015 Index",
    ],
    "ARA": [
        "CO22C015 Index", "CO20C017 Index", "CO24C069 Index",
    ],
    "Export Markets": [
        "NACI00B4 Index", "NACI00AD Index",
        "NACI019C Index", "NACI0137 Index",
    ],
}

# Physical OTC swaps — displayed as a side-by-side table + forward curve
# Each entry: list of (row_label, bloomberg_ticker) tuples
PHYSICAL_COAL_SWAPS = {
    "RB1 Swaps": {
        "color": "#F4A261",
        "contracts": [
            ("Current Month", "CO03C001 Index"),
            ("Month 1",       "CO01C001 Index"),
            ("Quarter 1",     "CO01C002 Index"),
            ("Quarter 2",     "CO01C003 Index"),
            ("Quarter 3",     "CO01C004 Index"),
            ("Quarter 4",     "CO01C005 Index"),
            ("Quarter 5",     "CO01C013 Index"),
            ("Year 1",        "CO01C006 Index"),
            ("Year 2",        "CO01C007 Index"),
            ("Year 3",        "CO01C008 Index"),
        ],
    },
    "ARA CIF Swaps": {
        "color": "#2A9D8F",
        "contracts": [
            ("Current Month", "CO22C015 Index"),
            ("Month 1",       "CO22C001 Index"),
            ("Quarter 1",     "CO22C002 Index"),
            ("Quarter 2",     "CO22C003 Index"),
            ("Quarter 3",     "CO22C004 Index"),
            ("Quarter 4",     "CO22C005 Index"),
            ("Quarter 5",     "CO22C017 Index"),
            ("Year 1",        "CO22C006 Index"),
            ("Year 2",        "CO22C007 Index"),
            ("Year 3",        "CO22C008 Index"),
        ],
    },
}

# ── Energy Benchmarks ──────────────────────────────────────────────────────────
ENERGY_TICKERS = {
    "CO1 Comdty":          {"name": "Brent Crude",          "short": "Brent",   "color": "#2A9D8F"},
    "CL1 Comdty":          {"name": "WTI Crude",            "short": "WTI",     "color": "#457B9D"},
    "TTFG1MON BCFV Index": {"name": "TTF Natural Gas",      "short": "TTF",     "color": "#1D3557"},
    "NG1 Comdty":          {"name": "Henry Hub Natural Gas", "short": "HH Gas",  "color": "#48CAE4"},
    "AJKMM1 Comdty":       {"name": "JKM Asia LNG (DES Japan-Korea)", "short": "JKM", "color": "#023E8A"},
}

ENERGY_FUTURES_TICKERS = list(ENERGY_TICKERS.keys())

# TTF explicit forward-curve contracts (FSTUM1–24 Index) for CCRV overlay
TTF_CURVE_TICKERS = [f"FSTUM{i} Index" for i in range(1, 25)]

# ── Explicit CT contracts for Energy (18 monthly contracts each) ───────────────
ENERGY_CT_CONTRACTS = {
    "Brent Crude": {
        "color":   "#2A9D8F",
        "Monthly": [f"CO{i} Comdty"    for i in range(1, 19)],
    },
    "WTI Crude": {
        "color":   "#457B9D",
        "Monthly": [f"CL{i} Comdty"    for i in range(1, 19)],
    },
    "JKM Asia LNG": {
        "color":   "#023E8A",
        "Monthly": [f"AJKMM{i} Comdty" for i in range(1, 19)],
    },
    "Henry Hub Gas": {
        "color":   "#48CAE4",
        "Monthly": [f"NG{i} COMB Comdty"  for i in range(1, 19)],
    },
    "TTF Natural Gas": {
        "color":   "#1D3557",
        "Monthly": [f"TTFG{i}MON BCFV Index" for i in range(1, 10)]
                 + [f"TTFG{i}M BCFV Index"   for i in range(10, 19)],
    },
}

# ── Macro Indicators ───────────────────────────────────────────────────────────
MACRO_TICKERS = {
    "USDZAR Curncy": {"name": "USD / ZAR",       "short": "USDZAR",  "color": "#8338EC"},
    "XAU Curncy":    {"name": "Gold (XAU/USD)",   "short": "Gold",    "color": "#FFB703"},
    "XBTUSD Curncy": {"name": "Bitcoin (BTC/USD)","short": "BTC",     "color": "#FB8500"},
}

# US Treasury on-the-run actives (GC curve)
TREASURY_TICKERS = {
    "GT1 Govt":  "1Y",
    "GT2 Govt":  "2Y",
    "GT3 Govt":  "3Y",
    "GT5 Govt":  "5Y",
    "GT7 Govt":  "7Y",
    "GT10 Govt": "10Y",
    "GT20 Govt": "20Y",
    "GT30 Govt": "30Y",
}

# ── Bloomberg field lists ──────────────────────────────────────────────────────
FUTURES_CHAIN_FIELDS = [
    "PX_LAST",
    "CHG_NET_1D",
    "CHG_PCT_1D",
    "PX_VOLUME",
    "OPEN_INT",
    "FUT_LAST_TRADE_DT",
]

HISTORY_FIELD = "PX_LAST"

# ── Data settings ──────────────────────────────────────────────────────────────
DATA_DIR          = "data"
HIST_LOOKBACK_YRS = 5          # years of history to pull
MAX_CONTRACTS     = 24         # max futures contracts in chain
