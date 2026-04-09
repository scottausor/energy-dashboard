# config.py — Central configuration for all tickers and settings

# ── Coal Benchmarks ────────────────────────────────────────────────────────────
COAL_TICKERS = {
    "XOA Comdty": {"name": "API4 – FOB Richards Bay 6,000 kCal",  "short": "API4 - FOB Richards Bay 6'000kCal",  "color": "#F4A261"},
    "XAA Comdty": {"name": "API2 – CIF ARA 6,000 kCal",           "short": "API2 - CIF ARA 6'000kCal",          "color": "#E76F51"},
    "XWA Comdty": {"name": "NEWC – FOB Newcastle 6,000 kCal",      "short": "FOB Newcastle 6'000kCal",           "color": "#E9C46A"},
}

# Spread: XAA - XOA  (ARA minus Richards Bay = implied freight)
COAL_SPREAD = {
    "ticker_a":  "XAA Comdty",
    "ticker_b":  "XOA Comdty",
    "name":      "Richards Bay – ARA Implied Freight (XAA – XOA)",
    "short":     "Richards Bay - ARA Implied Freight",
    "color":     "#52B788",
}

# Tickers that get futures-chain pulls for the Coal tab (CCRV forward curves)
COAL_FUTURES_TICKERS = ["XO1 Comdty", "XA1 Comdty", "XW1 Comdty"]

# Display config for coal forward curves (maps front-month → same style as active ticker)
COAL_CHAIN_CONFIG = {
    "XO1 Comdty": COAL_TICKERS["XOA Comdty"],
    "XA1 Comdty": COAL_TICKERS["XAA Comdty"],
    "XW1 Comdty": COAL_TICKERS["XWA Comdty"],
}

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
    # ── Richards Bay (original daily assessments) ────────────────────────────
    "CO03C001 Index": {"name": "Argus – Daily RB1",   "short": "RB1 Daily",  "color": "#F4A261"},
    "CO03C008 Index": {"name": "Argus – Daily RB2",   "short": "RB2 Daily",  "color": "#E76F51"},
    "NACI0004 Index": {"name": "Platts – Daily RB3",  "short": "RB3 Daily",  "color": "#E9C46A"},
    # ── Richards Bay Argus 1–4 ───────────────────────────────────────────────
    "CO03C005 Index": {"name": "Argus – Weekly RB3",  "short": "RB3 Weekly", "color": "#52B788"},
    "CO01C015 Index": {"name": "Argus – Weekly RB4",  "short": "RB4 Weekly", "color": "#F3C677"},
    # ── ARA ──────────────────────────────────────────────────────────────────
    "CO22C015 Index": {"name": "Argus – Daily ARA 6,000 kCal",  "short": "ARA 6k Daily",   "color": "#2A9D8F"},
    "CO20C017 Index": {"name": "Argus – Weekly ARA 6,000 kCal", "short": "ARA 6k Weekly",  "color": "#48CAE4"},
    "CO24C002 Index": {"name": "Argus – CIF ARA 6,000 kCal",    "short": "CIF ARA 6k",     "color": "#2A9D8F"},
    "CO24C069 Index": {"name": "Argus – CIF ARA 5,700 kCal",    "short": "CIF ARA 5.7k",   "color": "#0096C7"},
    # ── Export Markets ────────────────────────────────────────────────────────
    "NACI00B4 Index": {"name": "Platts CFR West Coast India 5,500 kCal", "short": "India W Coast", "color": "#8338EC"},
    "NACI00AD Index": {"name": "Platts CFR East Coast India 5,500 kCal", "short": "India E Coast", "color": "#7209B7"},
    "NACI019C Index": {"name": "Platts CFR Pakistan 5,500 kCal",         "short": "Pakistan",      "color": "#B5179E"},
    "NACI0137 Index": {"name": "Platts CFR South China 5,500 kCal",      "short": "S China",       "color": "#F72585"},
}

# Original top section — 3 daily assessments with cards + individual charts
PHYSICAL_COAL_SECTIONS = {
    "Richards Bay": ["CO03C001 Index", "CO03C008 Index", "NACI0004 Index"],
}

# Argus RB 1–4 — 2×2 cards + combined price history chart
PHYSICAL_COAL_RB_ARGUS = [
    "CO03C001 Index", "CO03C008 Index",
    "CO03C005 Index", "CO01C015 Index",
]

# ARA — cards only
PHYSICAL_COAL_ARA = [
    "CO22C015 Index", "CO20C017 Index", "CO24C069 Index",
]

# Argus CIF ARA — 2 cards + combined price history chart
PHYSICAL_COAL_ARA_ARGUS = [
    "CO24C002 Index", "CO24C069 Index",
]

# Export Markets — cards only
PHYSICAL_COAL_EXPORT = [
    "NACI00B4 Index", "NACI00AD Index",
    "NACI019C Index", "NACI0137 Index",
]

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
            ("Current Month", "CO24C002 Index"),
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
    "COA Comdty":    {"name": "Brent Crude",                       "short": "Brent",   "color": "#2A9D8F"},
    "CLA Comdty":    {"name": "WTI Crude",                         "short": "WTI",     "color": "#457B9D"},
    "TZTA Comdty":   {"name": "TTF Natural Gas",                   "short": "TTF",     "color": "#1D3557"},
    "NGA Comdty":    {"name": "Henry Hub Natural Gas",             "short": "HH Gas",  "color": "#48CAE4"},
    "AJKMM1 Comdty": {"name": "JKM Asia LNG (DES Japan-Korea)",   "short": "JKM",     "color": "#023E8A"},
}

# Front-month tickers used for futures chain pulls and CT table (unchanged)
ENERGY_FUTURES_TICKERS = ["CO1 Comdty", "CL1 Comdty", "TZT1 Comdty", "NG1 Comdty", "AJKMM1 Comdty"]

# Display config for energy forward curves (maps front-month → same style as active ticker)
ENERGY_CHAIN_CONFIG = {
    "CO1 Comdty":    ENERGY_TICKERS["COA Comdty"],
    "CL1 Comdty":    ENERGY_TICKERS["CLA Comdty"],
    "TZT1 Comdty":   ENERGY_TICKERS["TZTA Comdty"],
    "NG1 Comdty":    ENERGY_TICKERS["NGA Comdty"],
    "AJKMM1 Comdty": ENERGY_TICKERS["AJKMM1 Comdty"],
}

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
        "Monthly": [f"TZT{i} Comdty" for i in range(1, 19)],
    },
}

# ── Oil Products (BOIL equivalent) ────────────────────────────────────────────
OIL_PRODUCTS_TICKERS = {
    "Crude": {
        "EUCRBRDT Index": {"name": "Dated Brent",    "short": "Dated Brent",  "color": "#2A9D8F"},
        "GIOS0973 Index": {"name": "Forties NWE",    "short": "Forties",      "color": "#264653"},
        "GIOS0977 Index": {"name": "Ekofisk NWE",    "short": "Ekofisk",      "color": "#457B9D"},
        "USCRWTIM Index": {"name": "WTI Midland",    "short": "WTI Midl.",    "color": "#1D3557"},
        "USCRWTIC Index": {"name": "WTI Cushing",    "short": "WTI Cush.",    "color": "#0077B6"},
        "USCRSRIN Index": {"name": "US Sour (GCSI)", "short": "US Sour",      "color": "#0096C7"},
        "LACRMAUS Index": {"name": "Maya USGC",      "short": "Maya",         "color": "#00B4D8"},
        "GIOS0299 Index": {"name": "ESPO",           "short": "ESPO",         "color": "#48CAE4"},
        "GIOS0097 Index": {"name": "Dubai FOB",      "short": "Dubai",        "color": "#023E8A"},
        "GIOS0098 Index": {"name": "Oman FOB",       "short": "Oman",         "color": "#ADE8F4"},
    },
    "Fuel Oil": {
        "N6SH380S Index": {"name": "SG 380 CST",          "short": "SG 380",  "color": "#6D6875"},
        "N6SH180S Index": {"name": "SG 180 CST 3.5%",     "short": "SG 180",  "color": "#B5838D"},
        "GIOS0266 Index": {"name": "NWE 380 3.5% Barges", "short": "NWE 380", "color": "#E5989B"},
    },
    "Gasoil": {
        "HEATAAAB Index": {"name": "NWE Gasoil CIF", "short": "NWE GO",    "color": "#F4A261"},
        "DIEN10CF Index": {"name": "NWE ULSD CIF",   "short": "NWE ULSD",  "color": "#E76F51"},
        "GIOS0094 Index": {"name": "MED ULSD CIF",   "short": "MED ULSD",  "color": "#E9C46A"},
        "GDD01646 Index": {"name": "Magel ULSD",     "short": "Magel ULSD","color": "#F3C677"},
    },
    "Jet Fuel": {
        "JETKSPOT Index": {"name": "SG FOB",    "short": "SG Jet",  "color": "#8338EC"},
        "JET1NECC Index": {"name": "NWE CIF",   "short": "NWE Jet", "color": "#7209B7"},
        "JETFLAPL Index": {"name": "US LA",     "short": "US LA",   "color": "#480CA8"},
        "JETIGCPR Index": {"name": "US 54 Pas", "short": "US 54",   "color": "#B5179E"},
    },
    "Gasoline": {
        "MOGFM92S Index": {"name": "SG 92 RON",     "short": "SG 92",    "color": "#52B788"},
        "GIOS0004 Index": {"name": "NWE EBOB",      "short": "NWE EBOB", "color": "#40916C"},
        "RBOBG87P Index": {"name": "US RBOB Pas",   "short": "RBOB",     "color": "#2D6A4F"},
        "MOGLCB85 Index": {"name": "LA CARBOB",     "short": "CARBOB",   "color": "#74C69D"},
        "GGD01642 Index": {"name": "US Magell. V",  "short": "US Mag",   "color": "#95D5B2"},
        "GGC01651 Index": {"name": "US CBOB Chi",   "short": "CBOB Chi", "color": "#1B4332"},
        "GGC01005 Index": {"name": "US 87 Pas",     "short": "US 87",    "color": "#B7E4C7"},
    },
    "Naphtha": {
        "NAPHJPNC Index": {"name": "Japan CFR", "short": "Japan CFR", "color": "#FFB703"},
        "GIOS0092 Index": {"name": "NWE CIF",   "short": "NWE Naph",  "color": "#FB8500"},
    },
    "LPG": {
        "GIOS0878 Index": {"name": "ME Propane",  "short": "ME Prop",  "color": "#F72585"},
        "GIOS0880 Index": {"name": "ME Butane",   "short": "ME But",   "color": "#E63946"},
        "GIOS0686 Index": {"name": "NWE Propane", "short": "NWE Prop", "color": "#FF6B6B"},
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
