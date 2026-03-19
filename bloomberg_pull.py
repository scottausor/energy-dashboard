"""
bloomberg_pull.py
─────────────────
Daily data-pull script.  Connects to Bloomberg Terminal (blpapi/xbbg),
fetches all prices, futures chains, and yield-curve data, and saves them
to CSV files under the data/ directory.

Schedule this to run each business day via Windows Task Scheduler, e.g.:
    python bloomberg_pull.py

Requirements: Bloomberg Terminal must be open on the same machine.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime, timedelta

import pandas as pd

from config import (
    DATA_DIR, HIST_LOOKBACK_YRS, MAX_CONTRACTS,
    COAL_TICKERS, ENERGY_TICKERS, MACRO_TICKERS,
    COAL_FUTURES_TICKERS, ENERGY_FUTURES_TICKERS,
    COAL_CT_CONTRACTS, ENERGY_CT_CONTRACTS,
    TTF_CURVE_TICKERS,
    TREASURY_TICKERS, FUTURES_CHAIN_FIELDS, HISTORY_FIELD,
    PHYSICAL_COAL_TICKERS, PHYSICAL_COAL_SWAPS,
)

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ── Bloomberg import (graceful fallback) ───────────────────────────────────────
try:
    from xbbg import blp
    BBG_OK = True
    log.info("Bloomberg (xbbg) loaded successfully.")
except Exception as exc:
    BBG_OK = False
    log.warning(f"Could not load xbbg: {exc}")
    log.warning("Running in DEMO mode — synthetic data will be generated.")


# ═══════════════════════════════════════════════════════════════════════════════
# Bloomberg helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _start_date() -> str:
    return (datetime.today() - timedelta(days=365 * HIST_LOOKBACK_YRS)).strftime("%Y-%m-%d")


def bbg_history(tickers: list[str]) -> pd.DataFrame:
    """Pull daily PX_LAST history for a list of tickers."""
    log.info(f"  bdh → {tickers}")
    try:
        raw = blp.bdh(
            tickers=tickers,
            flds=[HISTORY_FIELD],
            start_date=_start_date(),
            end_date=datetime.today().strftime("%Y-%m-%d"),
        )
        # Flatten multi-level columns: keep only the ticker level
        raw.columns = [col[0] if isinstance(col, tuple) else col for col in raw.columns]
        # Bloomberg sometimes appends out-of-order holiday fill rows at the end
        # (e.g. Christmas, New Year's, US market holidays) for certain tickers.
        # Sort, deduplicate, and strip anything beyond today to clean this up.
        raw.index = pd.to_datetime(raw.index)
        raw = raw.sort_index()
        raw = raw[~raw.index.duplicated(keep="last")]
        raw = raw[raw.index <= pd.Timestamp(datetime.today().date())]
        raw = raw.replace(0, pd.NA)   # drop Bloomberg zero-fills (e.g. holidays)
        return raw
    except Exception as exc:
        log.error(f"  bbg_history failed: {exc}")
        return pd.DataFrame()


def bbg_futures_chain(root_ticker: str) -> pd.DataFrame:
    """
    Pull the active futures chain for root_ticker (CT equivalent).
    Returns a DataFrame with columns matching FUTURES_CHAIN_FIELDS.
    """
    log.info(f"  bds FUT_CHAIN → {root_ticker}")
    try:
        chain = blp.bds(root_ticker, "FUT_CHAIN")
        if chain.empty:
            log.warning(f"  Empty chain for {root_ticker}")
            return pd.DataFrame()

        # xbbg may return the chain under different column names depending on
        # version / backend setting.  Use the first column unconditionally.
        log.info(f"  chain columns returned: {list(chain.columns)}")
        contracts = chain.iloc[:, 0].dropna().tolist()[:MAX_CONTRACTS]

        prices = blp.bdp(tickers=contracts, flds=FUTURES_CHAIN_FIELDS)
        prices.index.name = "contract"
        prices = prices.reset_index()
        prices.columns = [c.lower() for c in prices.columns]
        return prices
    except Exception as exc:
        log.error(f"  bbg_futures_chain failed for {root_ticker}: {exc}")
        return pd.DataFrame()


def bbg_treasury_curve() -> pd.DataFrame:
    """Pull yield and maturity for US Treasury on-the-run actives (GC)."""
    log.info("  bdp → US Treasury actives")
    tickers = list(TREASURY_TICKERS.keys())
    try:
        df = blp.bdp(tickers=tickers, flds=["YLD_YTM_MID", "MATURITY", "PX_LAST"])
        df.index.name = "ticker"
        df = df.reset_index()
        df.columns = [c.lower() for c in df.columns]
        df["tenor"] = df["ticker"].map(TREASURY_TICKERS)
        return df
    except Exception as exc:
        log.error(f"  bbg_treasury_curve failed: {exc}")
        return pd.DataFrame()


# ═══════════════════════════════════════════════════════════════════════════════
# Demo-mode synthetic data  (used when Bloomberg is not available)
# ═══════════════════════════════════════════════════════════════════════════════

import numpy as np

DEMO_SEED_PRICES = {
    # Coal
    "XO1 Comdty": 115.0, "XA1 Comdty": 130.0, "XW1 Comdty": 118.0,
    # Energy
    "CO1 Comdty": 82.0, "CL1 Comdty": 78.0,
    "TTFG1MON BCFV Index": 35.0, "NG1 Comdty": 2.5, "AJKMM1 Comdty": 12.5,
    # Physical Coal (Argus / Platts)
    "CO03C001 Index": 108.0, "CO03C008 Index": 95.0, "NACI0004 Index": 102.0,
    # Macro
    "USDZAR Curncy": 18.50, "XAU Curncy": 2050.0, "XBTUSD Curncy": 62000.0,
    # Treasuries (yields)
    "GT1 Govt": 5.20, "GT2 Govt": 4.90, "GT3 Govt": 4.75,
    "GT5 Govt": 4.55, "GT7 Govt": 4.45, "GT10 Govt": 4.35,
    "GT20 Govt": 4.50, "GT30 Govt": 4.55,
}


def _synthetic_series(ticker: str, n_days: int = 365 * HIST_LOOKBACK_YRS) -> pd.Series:
    rng = np.random.default_rng(abs(hash(ticker)) % (2**31))
    seed = DEMO_SEED_PRICES.get(ticker, 100.0)
    vol = seed * 0.012
    returns = rng.normal(0, vol, n_days)
    prices = seed + np.cumsum(returns)
    prices = np.maximum(prices, seed * 0.2)
    dates = pd.date_range(end=datetime.today(), periods=n_days, freq="B")
    return pd.Series(prices, index=dates, name=ticker)


def demo_history(tickers: list[str]) -> pd.DataFrame:
    return pd.concat([_synthetic_series(t) for t in tickers], axis=1)


def demo_futures_chain(root_ticker: str) -> pd.DataFrame:
    base_price = DEMO_SEED_PRICES.get(root_ticker, 100.0)
    rng = np.random.default_rng(abs(hash(root_ticker)) % (2**31))
    months = pd.date_range(start=datetime.today(), periods=12, freq="MS")
    rows = []
    last = base_price
    for month in months:
        last += rng.normal(0, base_price * 0.008)
        last = max(last, base_price * 0.3)
        rows.append({
            "contract":           f"{root_ticker[:2]} {month.strftime('%b%y')}",
            "px_last":            round(last, 2),
            "chg_net_1d":         round(rng.normal(0, base_price * 0.005), 2),
            "chg_pct_1d":         round(rng.normal(0, 0.5), 2),
            "px_volume":          int(rng.integers(500, 8000)),
            "open_int":           int(rng.integers(2000, 40000)),
            "fut_last_trade_dt":  month.strftime("%Y-%m-%d"),
        })
    return pd.DataFrame(rows)


def bbg_explicit_contracts(ct_config: dict) -> pd.DataFrame:
    """
    Pull a flat table of explicitly-named futures contracts for the CT table.
    ct_config = COAL_CT_CONTRACTS from config.py
    Returns columns: commodity, type, contract, px_last, chg_net_1d,
                     chg_pct_1d, px_volume, open_int, fut_last_trade_dt
    """
    log.info("  bdp → explicit CT contracts")
    all_tickers, meta = [], []
    for commodity, cfg in ct_config.items():
        for contract_type, tickers in cfg.items():
            if contract_type == "color":
                continue
            for tkr in tickers:
                all_tickers.append(tkr)
                meta.append({"commodity": commodity, "type": contract_type, "contract": tkr})

    try:
        prices = blp.bdp(tickers=all_tickers, flds=FUTURES_CHAIN_FIELDS)
        prices.index.name = "contract"
        prices = prices.reset_index()
        prices.columns = [c.lower() for c in prices.columns]

        meta_df = pd.DataFrame(meta)
        result = meta_df.merge(prices, on="contract", how="left")
        return result
    except Exception as exc:
        log.error(f"  bbg_explicit_contracts failed: {exc}")
        return pd.DataFrame()


def demo_explicit_contracts(ct_config: dict) -> pd.DataFrame:
    """Demo synthetic version of bbg_explicit_contracts."""
    SEED_PRICES = {"API4 - FOB Richards Bay": 115.0,
                   "API2 - CIF ARA": 130.0,
                   "NEWC - FOB Newcastle": 118.0}
    rows = []
    for commodity, cfg in ct_config.items():
        base = SEED_PRICES.get(commodity, 110.0)
        rng = np.random.default_rng(abs(hash(commodity)) % (2**31))
        months = pd.date_range(start=datetime.today(), periods=23, freq="MS")
        price = base
        idx = 0
        for contract_type, tickers in cfg.items():
            if contract_type == "color":
                continue
            for tkr in tickers:
                price += rng.normal(0, base * 0.006)
                price = max(price, base * 0.4)
                rows.append({
                    "commodity":        commodity,
                    "type":             contract_type,
                    "contract":         tkr,
                    "px_last":          round(price, 2),
                    "chg_net_1d":       round(rng.normal(0, base * 0.004), 2),
                    "chg_pct_1d":       round(rng.normal(0, 0.35), 2),
                    "px_volume":        int(rng.integers(200, 6000)),
                    "open_int":         int(rng.integers(1000, 30000)),
                    "fut_last_trade_dt": months[min(idx, len(months)-1)].strftime("%Y-%m-%d"),
                })
                idx += 1
    return pd.DataFrame(rows)


def demo_treasury_curve() -> pd.DataFrame:
    rows = []
    for ticker, tenor in TREASURY_TICKERS.items():
        rows.append({
            "ticker":      ticker,
            "tenor":       tenor,
            "yld_ytm_mid": round(DEMO_SEED_PRICES.get(ticker, 4.5), 3),
            "px_last":     round(100 - DEMO_SEED_PRICES.get(ticker, 4.5), 3),
        })
    return pd.DataFrame(rows)


def bbg_physical_swaps(swap_config: dict) -> pd.DataFrame:
    """
    Pull current snapshot prices for physical OTC swap contracts.
    Returns columns: series, label, ticker, px_last, chg_net_1d, chg_pct_1d
    """
    log.info("  bdp → physical coal swaps")
    rows_meta, all_tickers = [], []
    for series_name, cfg in swap_config.items():
        for label, ticker in cfg["contracts"]:
            rows_meta.append({"series": series_name, "label": label, "ticker": ticker})
            all_tickers.append(ticker)
    try:
        prices = blp.bdp(tickers=all_tickers, flds=["PX_LAST", "CHG_NET_1D", "CHG_PCT_1D"])
        prices.index.name = "ticker"
        prices = prices.reset_index()
        prices.columns = [c.lower() for c in prices.columns]
        meta_df = pd.DataFrame(rows_meta)
        return meta_df.merge(prices, on="ticker", how="left")
    except Exception as exc:
        log.error(f"  bbg_physical_swaps failed: {exc}")
        return pd.DataFrame()


def demo_physical_swaps(swap_config: dict) -> pd.DataFrame:
    """Demo synthetic version of bbg_physical_swaps."""
    SEED = {"RB1 Swaps": 108.0, "ARA CIF Swaps": 118.0}
    rows = []
    for series_name, cfg in swap_config.items():
        base = SEED.get(series_name, 110.0)
        rng = np.random.default_rng(abs(hash(series_name)) % (2**31))
        price = base
        for label, ticker in cfg["contracts"]:
            price += rng.normal(0.3, 1.0)
            price = max(price, base * 0.5)
            rows.append({
                "series":      series_name,
                "label":       label,
                "ticker":      ticker,
                "px_last":     round(price, 2),
                "chg_net_1d":  round(rng.normal(0, base * 0.004), 2),
                "chg_pct_1d":  round(rng.normal(0, 0.35), 2),
            })
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════════════════════════
# Save helpers
# ═══════════════════════════════════════════════════════════════════════════════

def _safe_name(ticker: str) -> str:
    return ticker.replace(" ", "_").replace("/", "_")


def save_history(df: pd.DataFrame, filename: str):
    path = os.path.join(DATA_DIR, "prices", filename)
    df.to_csv(path)
    log.info(f"  saved → {path}  shape={df.shape}")


def save_chain(df: pd.DataFrame, ticker: str):
    path = os.path.join(DATA_DIR, "futures", f"{_safe_name(ticker)}_chain.csv")
    df.to_csv(path, index=False)
    log.info(f"  saved → {path}  rows={len(df)}")


def save_macro(df: pd.DataFrame, filename: str):
    path = os.path.join(DATA_DIR, "macro", filename)
    df.to_csv(path, index=False if "date" not in df.index.names else True)
    log.info(f"  saved → {path}  shape={df.shape}")


def stamp_update():
    path = os.path.join(DATA_DIR, "last_updated.txt")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(path, "w") as f:
        f.write(ts)
    log.info(f"  timestamp → {ts}")


# ═══════════════════════════════════════════════════════════════════════════════
# Git push  (keeps GitHub / Streamlit Cloud in sync)
# ═══════════════════════════════════════════════════════════════════════════════

# Set PUSH_TO_GIT = False to disable auto-push (e.g. during testing)
PUSH_TO_GIT = True

def git_push():
    if not PUSH_TO_GIT:
        log.info("Git push disabled — skipping.")
        return

    repo_dir = os.path.dirname(os.path.abspath(__file__))
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    cmds = [
        ["git", "add", "data/"],
        ["git", "commit", "-m", f"data: auto-update {ts}"],
        ["git", "push"],
    ]
    for cmd in cmds:
        result = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
        if result.returncode != 0:
            # "nothing to commit" is not a real error — skip silently
            if "nothing to commit" in result.stdout + result.stderr:
                log.info("  git: nothing new to commit.")
                return
            log.error(f"  git error ({' '.join(cmd)}): {result.stderr.strip()}")
            return
        log.info(f"  git: {' '.join(cmd[1:])} ✓")


# ═══════════════════════════════════════════════════════════════════════════════
# Main pull routine
# ═══════════════════════════════════════════════════════════════════════════════

def run():
    log.info("════════════════════════════════════════")
    log.info("  Energy & Coal Dashboard — Data Pull   ")
    log.info(f"  Mode: {'LIVE (Bloomberg)' if BBG_OK else 'DEMO (synthetic)'}   ")
    log.info("════════════════════════════════════════")

    fetch      = bbg_history            if BBG_OK else demo_history
    chain      = bbg_futures_chain      if BBG_OK else demo_futures_chain
    tsy        = bbg_treasury_curve     if BBG_OK else demo_treasury_curve
    ct_pull    = bbg_explicit_contracts if BBG_OK else demo_explicit_contracts
    swaps_pull = bbg_physical_swaps     if BBG_OK else demo_physical_swaps

    # 1 ── Coal prices ──────────────────────────────────────────────────────────
    log.info("[1/7] Coal historical prices")
    coal_df = fetch(list(COAL_TICKERS.keys()))
    if not coal_df.empty:
        save_history(coal_df, "coal_prices.csv")

    # 1b ── Physical Coal (Argus / Platts assessments) ──────────────────────────
    log.info("[1b/7] Physical Coal prices (Argus / Platts)")
    physical_coal_df = fetch(list(PHYSICAL_COAL_TICKERS.keys()))
    if not physical_coal_df.empty:
        save_history(physical_coal_df, "physical_coal_prices.csv")

    # 1c ── Physical Coal OTC swaps ─────────────────────────────────────────────
    log.info("[1c/7] Physical Coal OTC swaps (RB1 / ARA CIF)")
    swaps_df = swaps_pull(PHYSICAL_COAL_SWAPS)
    if not swaps_df.empty:
        path = os.path.join(DATA_DIR, "prices", "physical_coal_swaps.csv")
        swaps_df.to_csv(path, index=False)
        log.info(f"  saved → {path}  rows={len(swaps_df)}")

    # 2 ── Coal CT explicit contracts ───────────────────────────────────────────
    log.info("[2/7] Coal CT contracts (Monthly / Quarterly / Yearly)")
    ct_df = ct_pull(COAL_CT_CONTRACTS)
    if not ct_df.empty:
        path = os.path.join(DATA_DIR, "futures", "coal_ct_contracts.csv")
        ct_df.to_csv(path, index=False)
        log.info(f"  saved → {path}  rows={len(ct_df)}")

    # 2b ── Coal forward-curve chains (CCRV) ────────────────────────────────────
    log.info("[2b/7] Coal futures chains (CCRV)")
    for ticker in COAL_FUTURES_TICKERS:
        df = chain(ticker)
        if not df.empty:
            save_chain(df, ticker)

    # 3 ── Energy prices ────────────────────────────────────────────────────────
    log.info("[3/7] Energy historical prices")
    energy_df = fetch(list(ENERGY_TICKERS.keys()))
    if not energy_df.empty:
        save_history(energy_df, "energy_prices.csv")

    # 4 ── Energy futures chains (CCRV) ────────────────────────────────────────
    log.info("[4/7] Energy futures chains (CCRV)")
    for ticker in ENERGY_FUTURES_TICKERS:
        df = chain(ticker)
        if not df.empty:
            save_chain(df, ticker)

    # 4b ── Energy CT explicit contracts ────────────────────────────────────────
    log.info("[4b/7] Energy CT contracts (18 monthly each)")
    energy_ct_df = ct_pull(ENERGY_CT_CONTRACTS)
    if not energy_ct_df.empty:
        path = os.path.join(DATA_DIR, "futures", "energy_ct_contracts.csv")
        energy_ct_df.to_csv(path, index=False)
        log.info(f"  saved → {path}  rows={len(energy_ct_df)}")

    # 4c ── TTF explicit forward curve (FSTUM1–24 Index) ───────────────────────
    log.info("[4c/7] TTF forward curve (FSTUM1–24 Index)")
    try:
        if BBG_OK:
            ttf_raw = blp.bdp(tickers=TTF_CURVE_TICKERS,
                              flds=["PX_LAST", "FUT_LAST_TRADE_DT"])
            ttf_raw.index.name = "contract"
            ttf_raw = ttf_raw.reset_index()
            ttf_raw.columns = [c.lower() for c in ttf_raw.columns]
        else:
            # Demo: build a synthetic upward-sloping TTF curve
            rng = np.random.default_rng(42)
            months = pd.date_range(start=datetime.today(), periods=24, freq="MS")
            price = 35.0
            rows = []
            for tkr, month in zip(TTF_CURVE_TICKERS, months):
                price += rng.normal(0.4, 0.8)
                rows.append({"contract": tkr,
                             "px_last": round(price, 2),
                             "fut_last_trade_dt": month.strftime("%Y-%m-%d")})
            ttf_raw = pd.DataFrame(rows)

        path = os.path.join(DATA_DIR, "futures", "ttf_fwd_curve.csv")
        ttf_raw.to_csv(path, index=False)
        log.info(f"  saved → {path}  rows={len(ttf_raw)}")
    except Exception as exc:
        log.error(f"  TTF curve pull failed: {exc}")

    # 5 ── Macro: FX, Gold, BTC, Treasuries ────────────────────────────────────
    log.info("[5/7] Macro indicators + Treasury curve")
    macro_df = fetch(list(MACRO_TICKERS.keys()))
    if not macro_df.empty:
        path = os.path.join(DATA_DIR, "macro", "macro_prices.csv")
        macro_df.to_csv(path)
        log.info(f"  saved → {path}")

    treasury_df = tsy()
    if not treasury_df.empty:
        save_macro(treasury_df, "treasury_curve.csv")

    stamp_update()
    git_push()
    log.info("Done ✓")


if __name__ == "__main__":
    run()
