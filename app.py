"""
app.py — Energy & Coal Streamlit Dashboard
──────────────────────────────────────────
Run with:  streamlit run app.py

Reads pre-cached CSV files produced by bloomberg_pull.py.
Three tabs:  🪨 Coal  |  🛢️ Energy  |  🌍 Macro
"""

import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def _hex_to_rgba(hex_color: str, alpha: float = 0.09) -> str:
    """Convert a 6-digit hex color string to an rgba() string for Plotly fills."""
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

from config import (
    COAL_TICKERS, COAL_SPREAD, COAL_FUTURES_TICKERS, COAL_CT_CONTRACTS,
    ENERGY_TICKERS, ENERGY_FUTURES_TICKERS, ENERGY_CT_CONTRACTS,
    MACRO_TICKERS, TREASURY_TICKERS,
    DATA_DIR,
)

# ══════════════════════════════════════════════════════════════════════════════
# Page setup
# ══════════════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="Energy & Coal Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  /* Tighten top padding */
  .block-container { padding-top: 0.75rem !important; }

  /* Metric cards */
  div[data-testid="stMetric"] {
      background: rgba(255,255,255,0.04);
      border-radius: 8px;
      padding: 10px 14px;
      border: 1px solid rgba(255,255,255,0.07);
  }
  div[data-testid="stMetricLabel"]  { font-size: 11px !important; opacity: 0.7; }
  div[data-testid="stMetricValue"]  { font-size: 20px !important; font-weight: 700; }
  div[data-testid="stMetricDelta"]  { font-size: 12px !important; }

  /* Tab styling */
  .stTabs [data-baseweb="tab-list"]  { gap: 6px; }
  .stTabs [data-baseweb="tab"]       { padding: 8px 22px; border-radius: 6px 6px 0 0; }

  /* Divider colour */
  hr { border-color: rgba(255,255,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# Data loaders (all cached)
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=3600)
def load_prices(filename: str) -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "prices", filename)
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    return df


@st.cache_data(ttl=3600)
def load_macro_prices() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "macro", "macro_prices.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    df = pd.read_csv(path, index_col=0, parse_dates=True)
    df.index = pd.to_datetime(df.index)
    return df


@st.cache_data(ttl=3600)
def load_chain(ticker: str) -> pd.DataFrame:
    safe = ticker.replace(" ", "_").replace("/", "_")
    path = os.path.join(DATA_DIR, "futures", f"{safe}_chain.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=3600)
def load_coal_ct() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "futures", "coal_ct_contracts.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=3600)
def load_energy_ct() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "futures", "energy_ct_contracts.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=3600)
def load_ttf_curve() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "futures", "ttf_fwd_curve.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


@st.cache_data(ttl=3600)
def load_treasury() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "macro", "treasury_curve.csv")
    if not os.path.exists(path):
        return pd.DataFrame()
    return pd.read_csv(path)


def get_last_updated() -> str:
    path = os.path.join(DATA_DIR, "last_updated.txt")
    return open(path).read().strip() if os.path.exists(path) else "—"


# ══════════════════════════════════════════════════════════════════════════════
# Chart factories
# ══════════════════════════════════════════════════════════════════════════════

_LAYOUT_BASE = dict(
    margin=dict(l=42, r=16, t=44, b=28),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)",
               tickfont=dict(size=10), showline=False, zeroline=False),
    yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.08)",
               tickfont=dict(size=10), showline=False, zeroline=False,
               rangemode="normal"),
    hovermode="x unified",
    showlegend=False,
)

_CHART_CFG = {"displayModeBar": False}


def _title_with_delta(name: str, series: pd.Series) -> str:
    """Return an HTML title string including last value and day change."""
    if len(series) < 2:
        return f"<b>{name}</b>"
    last, prev = series.iloc[-1], series.iloc[-2]
    chg = last - prev
    pct = chg / prev * 100 if prev else 0
    arrow = "▲" if chg >= 0 else "▼"
    colour = "#00CC96" if chg >= 0 else "#EF553B"
    return (
        f"<b>{name}</b>  "
        f"<span style='color:{colour};font-size:11px'>"
        f"{arrow} {abs(chg):.2f} ({abs(pct):.2f}%)</span>"
    )


def price_chart(
    df: pd.DataFrame,
    ticker: str,
    name: str,
    color: str,
    date_from: datetime,
    height: int = 290,
) -> go.Figure:
    fig = go.Figure()
    if df.empty or ticker not in df.columns:
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(color="gray"))
        fig.update_layout(**_LAYOUT_BASE, height=height)
        return fig

    s = df[ticker].dropna()
    s = s[s > 0]                                   # drop zero / bad-data points
    s = s.sort_index()                             # ensure chronological order
    s = s[~s.index.duplicated(keep="last")]        # remove roll-day duplicates
    s = s[s.index >= pd.Timestamp(date_from)]

    if s.empty:
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(color="gray"))
        fig.update_layout(**_LAYOUT_BASE, height=height)
        return fig

    fig.add_trace(go.Scatter(
        x=s.index, y=s.values, mode="lines", name=name,
        line=dict(color=color, width=2),
        connectgaps=False,
        hovertemplate=f"<b>{name}</b><br>%{{x|%d %b %Y}}  %{{y:,.2f}}<extra></extra>",
    ))

    # Explicitly set y range so axis starts near data, not at 0
    pad = (s.max() - s.min()) * 0.05 if s.max() != s.min() else s.max() * 0.05
    lo = _LAYOUT_BASE.copy()
    lo.update(height=height,
              title=dict(text=_title_with_delta(name, s), font=dict(size=13)),
              yaxis=dict(**_LAYOUT_BASE["yaxis"],
                         range=[s.min() - pad, s.max() + pad]))
    fig.update_layout(**lo)
    return fig


def spread_chart(
    df: pd.DataFrame,
    ticker_a: str,
    ticker_b: str,
    name: str,
    color: str,
    date_from: datetime,
    height: int = 290,
) -> go.Figure:
    fig = go.Figure()
    if df.empty or ticker_a not in df.columns or ticker_b not in df.columns:
        fig.add_annotation(text="No data available", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(color="gray"))
        fig.update_layout(**_LAYOUT_BASE, height=height)
        return fig

    spread = (df[ticker_a] - df[ticker_b]).dropna()
    spread = spread.sort_index()
    spread = spread[~spread.index.duplicated(keep="last")]
    spread = spread[spread.index >= pd.Timestamp(date_from)]

    fig.add_trace(go.Scatter(
        x=spread.index, y=spread.values,
        mode="lines", name=name,
        line=dict(color=color, width=2),
        hovertemplate=f"<b>{name}</b><br>%{{x|%d %b %Y}}  %{{y:+,.2f}}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="rgba(255,255,255,0.25)", line_width=1)

    pad = (spread.max() - spread.min()) * 0.05 if spread.max() != spread.min() else 1
    lo = _LAYOUT_BASE.copy()
    lo.update(height=height,
              title=dict(text=_title_with_delta(name, spread), font=dict(size=13)),
              yaxis=dict(**_LAYOUT_BASE["yaxis"],
                         range=[spread.min() - pad, spread.max() + pad]))
    fig.update_layout(**lo)
    return fig


def forward_curve_chart(chains: dict, height: int = 360) -> go.Figure:
    """
    CCRV equivalent: overlay forward curves for multiple tickers.
    chains = {ticker: (chain_df, cfg_dict)}
    """
    fig = go.Figure()
    tenor_order = ["1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "3Y"]

    for ticker, (chain_df, cfg) in chains.items():
        if chain_df.empty or "px_last" not in chain_df.columns:
            continue

        df = chain_df.dropna(subset=["px_last"]).copy()
        if "fut_last_trade_dt" in df.columns:
            df["expiry"] = pd.to_datetime(df["fut_last_trade_dt"], errors="coerce")
            df = df.dropna(subset=["expiry"]).sort_values("expiry")
            x = df["expiry"]
            x_title = "Contract Expiry"
        else:
            x = list(range(len(df)))
            x_title = "Contract Number"

        fig.add_trace(go.Scatter(
            x=x, y=df["px_last"].values,
            mode="lines+markers",
            name=cfg["short"],
            line=dict(color=cfg["color"], width=2.5),
            marker=dict(size=7, color=cfg["color"]),
            hovertemplate=(
                f"<b>{cfg['name']}</b><br>"
                "Expiry: %{x|%b %Y}<br>"
                "Price: %{y:,.2f}<extra></extra>"
            ),
        ))

    lo = _LAYOUT_BASE.copy()
    lo.update(
        height=height,
        showlegend=True,
        legend=dict(x=0.01, y=0.99, bgcolor="rgba(0,0,0,0.45)",
                    font=dict(size=11), borderwidth=0),
        title=dict(text="<b>Forward Curves (CCRV)</b>", font=dict(size=13)),
        xaxis=dict(**_LAYOUT_BASE["xaxis"], title="Contract Expiry"),
        yaxis=dict(**_LAYOUT_BASE["yaxis"], title="Price (USD / t  or  $/MMBtu)"),
    )
    fig.update_layout(**lo)
    return fig


def treasury_curve_chart(df: pd.DataFrame, height: int = 380) -> go.Figure:
    """US Treasury actives yield curve (GC equivalent)."""
    fig = go.Figure()

    TENOR_ORDER = ["1Y", "2Y", "3Y", "5Y", "7Y", "10Y", "20Y", "30Y"]

    if not df.empty and "tenor" in df.columns and "yld_ytm_mid" in df.columns:
        df = df.copy()
        df["_order"] = df["tenor"].map({t: i for i, t in enumerate(TENOR_ORDER)})
        df = df.sort_values("_order")

        fig.add_trace(go.Scatter(
            x=df["tenor"], y=df["yld_ytm_mid"],
            mode="lines+markers",
            line=dict(color="#00CC96", width=2.5),
            marker=dict(size=9, color="#00CC96"),
            hovertemplate="<b>%{x}</b>  Yield: %{y:.3f}%<extra></extra>",
        ))
    else:
        fig.add_annotation(text="No Treasury curve data", xref="paper", yref="paper",
                           x=0.5, y=0.5, showarrow=False, font=dict(color="gray"))

    lo = _LAYOUT_BASE.copy()
    lo.update(
        height=height,
        title=dict(text="<b>US Treasury Actives Yield Curve (GC)</b>", font=dict(size=13)),
        xaxis=dict(**_LAYOUT_BASE["xaxis"], title="Tenor"),
        yaxis=dict(**_LAYOUT_BASE["yaxis"], title="Yield (%)"),
    )
    fig.update_layout(**lo)
    return fig


# ══════════════════════════════════════════════════════════════════════════════
# Futures table helper  (CT equivalent)
# ══════════════════════════════════════════════════════════════════════════════

def build_ct_table(chains: dict) -> pd.DataFrame:
    """Combine multiple futures chains into a single styled CT-style table."""
    rows = []
    for ticker, (chain_df, cfg) in chains.items():
        if chain_df.empty:
            continue
        for _, row in chain_df.head(12).iterrows():
            rows.append({
                "Commodity":  cfg["short"],
                "Contract":   row.get("contract", ticker),
                "Last":       row.get("px_last"),
                "Chg":        row.get("chg_net_1d"),
                "Chg %":      row.get("chg_pct_1d"),
                "Volume":     row.get("px_volume"),
                "Open Int.":  row.get("open_int"),
                "Expiry":     row.get("fut_last_trade_dt", ""),
            })
    return pd.DataFrame(rows)


def render_ct_table(chains: dict):
    df = build_ct_table(chains)
    if df.empty:
        st.info("No futures chain data. Run `python bloomberg_pull.py` to fetch.")
        return

    def colour_chg(val):
        if pd.isna(val) or not isinstance(val, (int, float)):
            return ""
        return "color: #00CC96" if val > 0 else "color: #EF553B" if val < 0 else ""

    fmt = {
        "Last":      "{:.2f}",
        "Chg":       "{:+.2f}",
        "Chg %":     "{:+.2f}",
        "Volume":    "{:,.0f}",
        "Open Int.": "{:,.0f}",
    }

    styled = (
        df.style
        .format(fmt, na_rep="—")
        .applymap(colour_chg, subset=["Chg", "Chg %"])
    )
    st.dataframe(styled, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# KPI metric row
# ══════════════════════════════════════════════════════════════════════════════

def kpi_row(df: pd.DataFrame, tickers: dict, extra_spread: dict | None = None,
            ordered_items: list | None = None):
    """Display a row of st.metric cards for the latest prices.
    Pass ordered_items to fully control order (list of (ticker_or_key, cfg) tuples).
    """
    if ordered_items is not None:
        items = ordered_items
    else:
        items = list(tickers.items())
        if extra_spread:
            items.append(("__spread__", extra_spread))

    cols = st.columns(len(items))
    for col, (ticker, cfg) in zip(cols, items):
        with col:
            if ticker == "__spread__":
                # Spread card
                ta, tb = cfg["ticker_a"], cfg["ticker_b"]
                if not df.empty and ta in df.columns and tb in df.columns:
                    s = (df[ta] - df[tb]).dropna()
                    if len(s) >= 2:
                        val, prev = s.iloc[-1], s.iloc[-2]
                        st.metric(cfg["short"], f"{val:.2f}", f"{val-prev:+.2f}")
                    else:
                        st.metric(cfg["short"], "—")
            else:
                if not df.empty and ticker in df.columns:
                    s = df[ticker].dropna()
                    if len(s) >= 2:
                        val, prev = s.iloc[-1], s.iloc[-2]
                        st.metric(cfg["short"], f"{val:.2f}", f"{val-prev:+.2f}")
                    else:
                        st.metric(cfg["short"], "—")
                else:
                    st.metric(cfg["short"], "—")


# ══════════════════════════════════════════════════════════════════════════════
# Coal CT table  (explicit Monthly / Quarterly / Yearly per commodity)
# ══════════════════════════════════════════════════════════════════════════════

def render_coal_ct_table(ct_df: pd.DataFrame):
    """Render the coal CT table grouped by commodity, then by contract type."""
    if ct_df.empty:
        st.info("No CT data yet. Run `python bloomberg_pull.py` to fetch.")
        return

    def colour_chg(val):
        if pd.isna(val) or not isinstance(val, (int, float)):
            return ""
        return "color: #00CC96" if val > 0 else "color: #EF553B" if val < 0 else ""

    fmt = {
        "Last":      "{:.2f}",
        "Chg":       "{:+.2f}",
        "Chg %":     "{:+.2f}",
        "Volume":    "{:,.0f}",
        "Open Int.": "{:,.0f}",
    }

    col_rename = {
        "contract":        "Contract",
        "px_last":         "Last",
        "chg_net_1d":      "Chg",
        "chg_pct_1d":      "Chg %",
        "px_volume":       "Volume",
        "open_int":        "Open Int.",
        "fut_last_trade_dt": "Expiry",
    }

    TYPE_ORDER = ["Monthly", "Quarterly", "Yearly"]
    commodities = [c for c in COAL_CT_CONTRACTS.keys() if c in ct_df["commodity"].values]

    tabs = st.tabs([f"  {c}  " for c in commodities])
    for tab, commodity in zip(tabs, commodities):
        with tab:
            color = COAL_CT_CONTRACTS[commodity]["color"]
            st.markdown(
                f"<div style='width:8px;height:8px;background:{color};"
                f"border-radius:50%;display:inline-block;margin-right:6px'></div>"
                f"<b>{commodity}</b>",
                unsafe_allow_html=True,
            )
            comm_df = ct_df[ct_df["commodity"] == commodity].copy()
            for ctype in TYPE_ORDER:
                sub = comm_df[comm_df["type"] == ctype].copy()
                if sub.empty:
                    continue
                sub = sub.rename(columns=col_rename)
                display_cols = ["Contract", "Last", "Chg", "Chg %", "Volume", "Open Int.", "Expiry"]
                sub = sub[[c for c in display_cols if c in sub.columns]]

                st.markdown(f"**{ctype}**")
                styled = (
                    sub.style
                    .format(fmt, na_rep="—")
                    .applymap(colour_chg, subset=[c for c in ["Chg", "Chg %"] if c in sub.columns])
                )
                st.dataframe(styled, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# Energy CT table  (18 monthly contracts per commodity)
# ══════════════════════════════════════════════════════════════════════════════

def render_energy_ct_table(ct_df: pd.DataFrame):
    """Render the energy CT table — one tab per commodity, monthly contracts only."""
    if ct_df.empty:
        st.info("No CT data yet. Run `python bloomberg_pull.py` to fetch.")
        return

    def colour_chg(val):
        if pd.isna(val) or not isinstance(val, (int, float)):
            return ""
        return "color: #00CC96" if val > 0 else "color: #EF553B" if val < 0 else ""

    fmt = {
        "Last":      "{:.2f}",
        "Chg":       "{:+.2f}",
        "Chg %":     "{:+.2f}",
        "Volume":    "{:,.0f}",
        "Open Int.": "{:,.0f}",
    }

    col_rename = {
        "contract":          "Contract",
        "px_last":           "Last",
        "chg_net_1d":        "Chg",
        "chg_pct_1d":        "Chg %",
        "px_volume":         "Volume",
        "open_int":          "Open Int.",
        "fut_last_trade_dt": "Expiry",
    }

    commodities = [c for c in ENERGY_CT_CONTRACTS.keys() if c in ct_df["commodity"].values]
    tabs = st.tabs([f"  {c}  " for c in commodities])

    for tab, commodity in zip(tabs, commodities):
        with tab:
            color = ENERGY_CT_CONTRACTS[commodity]["color"]
            st.markdown(
                f"<div style='width:8px;height:8px;background:{color};"
                f"border-radius:50%;display:inline-block;margin-right:6px'></div>"
                f"<b>{commodity}</b>",
                unsafe_allow_html=True,
            )
            sub = ct_df[ct_df["commodity"] == commodity].copy()
            sub = sub.rename(columns=col_rename)
            display_cols = ["Contract", "Last", "Chg", "Chg %", "Volume", "Open Int.", "Expiry"]
            sub = sub[[c for c in display_cols if c in sub.columns]]

            styled = (
                sub.style
                .format(fmt, na_rep="—")
                .applymap(colour_chg, subset=[c for c in ["Chg", "Chg %"] if c in sub.columns])
            )
            st.dataframe(styled, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
# App layout
# ══════════════════════════════════════════════════════════════════════════════

def main():
    # ── Header ──────────────────────────────────────────────────────────────
    h1, h2, h3 = st.columns([4, 1, 1])
    with h1:
        st.markdown("## ⚡ Energy & Coal Dashboard")
    with h2:
        st.markdown("<div style='padding-top:14px'>", unsafe_allow_html=True)
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with h3:
        st.markdown(
            f"<div style='padding-top:16px;font-size:11px;opacity:.6'>"
            f"Updated: {get_last_updated()}</div>",
            unsafe_allow_html=True,
        )
    st.divider()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        period = st.selectbox("Chart period", ["1M", "3M", "6M", "1Y", "2Y", "5Y"], index=3)
        period_days = {"1M": 30, "3M": 90, "6M": 180, "1Y": 365, "2Y": 730, "5Y": 1825}
        date_from = datetime.today() - timedelta(days=period_days[period])

        st.divider()
        st.markdown("**To refresh data:**")
        st.code("python bloomberg_pull.py", language="bash")
        st.caption("Bloomberg Terminal must be open on the same machine.")
        st.divider()
        st.caption("Dashboard built with Streamlit + Plotly\nData via Bloomberg Terminal (blpapi/xbbg)")

    # ── Load data ─────────────────────────────────────────────────────────────
    coal_df   = load_prices("coal_prices.csv")
    energy_df = load_prices("energy_prices.csv")
    macro_df  = load_macro_prices()
    tsy_df    = load_treasury()

    coal_chains   = {t: (load_chain(t), COAL_TICKERS[t])   for t in COAL_FUTURES_TICKERS}
    energy_chains = {t: (load_chain(t), ENERGY_TICKERS[t]) for t in ENERGY_FUTURES_TICKERS}
    coal_ct_df    = load_coal_ct()
    energy_ct_df  = load_energy_ct()

    # ── Tabs ──────────────────────────────────────────────────────────────────
    tab_coal, tab_energy, tab_macro = st.tabs(["🪨  Coal", "🛢️  Energy", "🌍  Macro"])

    # ════════════════════════════════════════════════════════════════════════
    # COAL TAB
    # ════════════════════════════════════════════════════════════════════════
    with tab_coal:
        # KPI bar — order: API4, API2, Freight, NEWC
        coal_kpi_items = [
            ("XO1 Comdty",  COAL_TICKERS["XO1 Comdty"]),
            ("XA1 Comdty",  COAL_TICKERS["XA1 Comdty"]),
            ("__spread__",  COAL_SPREAD),
            ("XW1 Comdty",  COAL_TICKERS["XW1 Comdty"]),
        ]
        kpi_row(coal_df, COAL_TICKERS, ordered_items=coal_kpi_items)

        st.markdown("#### Price History")

        st.plotly_chart(
            price_chart(coal_df, "XO1 Comdty",
                        COAL_TICKERS["XO1 Comdty"]["name"],
                        COAL_TICKERS["XO1 Comdty"]["color"], date_from,
                        height=420),
            use_container_width=True, config=_CHART_CFG,
        )
        st.plotly_chart(
            price_chart(coal_df, "XA1 Comdty",
                        COAL_TICKERS["XA1 Comdty"]["name"],
                        COAL_TICKERS["XA1 Comdty"]["color"], date_from,
                        height=420),
            use_container_width=True, config=_CHART_CFG,
        )
        st.plotly_chart(
            spread_chart(
                coal_df,
                COAL_SPREAD["ticker_a"], COAL_SPREAD["ticker_b"],
                COAL_SPREAD["name"], COAL_SPREAD["color"], date_from,
                height=420,
            ),
            use_container_width=True, config=_CHART_CFG,
        )
        st.plotly_chart(
            price_chart(coal_df, "XW1 Comdty",
                        COAL_TICKERS["XW1 Comdty"]["name"],
                        COAL_TICKERS["XW1 Comdty"]["color"], date_from,
                        height=420),
            use_container_width=True, config=_CHART_CFG,
        )

        st.divider()
        st.markdown("#### Forward Curves (CCRV)")
        st.plotly_chart(forward_curve_chart(coal_chains), use_container_width=True, config=_CHART_CFG)

        st.divider()
        st.markdown("#### Futures Contract Table (CT)")
        render_coal_ct_table(coal_ct_df)

    # ════════════════════════════════════════════════════════════════════════
    # ENERGY TAB
    # ════════════════════════════════════════════════════════════════════════
    with tab_energy:
        kpi_row(energy_df, ENERGY_TICKERS)

        st.markdown("#### Price History")

        st.plotly_chart(
            price_chart(energy_df, "CO1 Comdty",
                        ENERGY_TICKERS["CO1 Comdty"]["name"],
                        ENERGY_TICKERS["CO1 Comdty"]["color"], date_from, height=420),
            use_container_width=True, config=_CHART_CFG,
        )
        st.plotly_chart(
            price_chart(energy_df, "CL1 Comdty",
                        ENERGY_TICKERS["CL1 Comdty"]["name"],
                        ENERGY_TICKERS["CL1 Comdty"]["color"], date_from, height=420),
            use_container_width=True, config=_CHART_CFG,
        )
        st.plotly_chart(
            price_chart(energy_df, "TTFGBOM Comdty",
                        ENERGY_TICKERS["TTFGBOM Comdty"]["name"],
                        ENERGY_TICKERS["TTFGBOM Comdty"]["color"], date_from, height=420),
            use_container_width=True, config=_CHART_CFG,
        )
        st.plotly_chart(
            price_chart(energy_df, "NG1 Comdty",
                        ENERGY_TICKERS["NG1 Comdty"]["name"],
                        ENERGY_TICKERS["NG1 Comdty"]["color"], date_from, height=420),
            use_container_width=True, config=_CHART_CFG,
        )
        st.plotly_chart(
            price_chart(energy_df, "JKL1 Comdty",
                        ENERGY_TICKERS["JKL1 Comdty"]["name"],
                        ENERGY_TICKERS["JKL1 Comdty"]["color"], date_from, height=420),
            use_container_width=True, config=_CHART_CFG,
        )

        st.divider()
        st.markdown("#### Forward Curves (CCRV)")

        oil_tickers = ["CO1 Comdty", "CL1 Comdty"]
        gas_tickers  = ["NG1 Comdty", "JKL1 Comdty"]
        oil_chains  = {t: energy_chains[t] for t in oil_tickers if t in energy_chains}
        gas_chains  = {t: energy_chains[t] for t in gas_tickers if t in energy_chains}

        st.markdown("**Oil — Brent & WTI**")
        st.plotly_chart(forward_curve_chart(oil_chains, height=380), use_container_width=True, config=_CHART_CFG)
        st.markdown("**Gas — Henry Hub & JKM**")
        st.plotly_chart(forward_curve_chart(gas_chains, height=380), use_container_width=True, config=_CHART_CFG)

        st.divider()
        st.markdown("#### Futures Contract Table (CT)")
        render_energy_ct_table(energy_ct_df)

    # ════════════════════════════════════════════════════════════════════════
    # MACRO TAB
    # ════════════════════════════════════════════════════════════════════════
    with tab_macro:
        kpi_row(macro_df, MACRO_TICKERS)

        st.markdown("#### Price History")
        c1, c2, c3 = st.columns(3)

        with c1:
            st.plotly_chart(
                price_chart(macro_df, "USDZAR Curncy",
                            MACRO_TICKERS["USDZAR Curncy"]["name"],
                            MACRO_TICKERS["USDZAR Curncy"]["color"], date_from),
                use_container_width=True, config=_CHART_CFG,
            )
        with c2:
            st.plotly_chart(
                price_chart(macro_df, "XAU Curncy",
                            MACRO_TICKERS["XAU Curncy"]["name"],
                            MACRO_TICKERS["XAU Curncy"]["color"], date_from),
                use_container_width=True, config=_CHART_CFG,
            )
        with c3:
            st.plotly_chart(
                price_chart(macro_df, "XBTUSD Curncy",
                            MACRO_TICKERS["XBTUSD Curncy"]["name"],
                            MACRO_TICKERS["XBTUSD Curncy"]["color"], date_from),
                use_container_width=True, config=_CHART_CFG,
            )

        st.divider()
        st.markdown("#### US Treasury Actives Yield Curve (GC)")
        st.plotly_chart(treasury_curve_chart(tsy_df), use_container_width=True, config=_CHART_CFG)


if __name__ == "__main__":
    main()
