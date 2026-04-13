"""
Sell-Side Lite | Institutional Equity Research Platform
Hedge-fund grade: DCF, EV/EBITDA Comps, Scenario Engineering, Macro Overlays
Colour palette: slate-blue, powder-blue, warm-cream, sage-mint, teal-slate
"""

import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sell-Side Lite | Institutional Research",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── COLOUR PALETTE (from uploaded swatch) ───────────────────────────────────
PALETTE = {
    "slate_blue":   "#6272a4",
    "powder_blue":  "#b8cce4",
    "warm_cream":   "#e8d5b7",
    "sage_mint":    "#b2c9bf",
    "teal_slate":   "#5f8c8a",
    "bg":           "#f7f6f3",
    "surface":      "#ffffff",
    "border":       "#dde3e8",
    "text_dark":    "#2c3e50",
    "text_mid":     "#5a6a7a",
    "text_light":   "#8a9baa",
    "buy":          "#5f8c8a",
    "hold":         "#b8a882",
    "sell":         "#b05a6a",
    "positive":     "#5f8c8a",
    "negative":     "#b05a6a",
    "neutral":      "#b8a882",
}

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

/* Global */
html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {PALETTE['bg']};
    color: {PALETTE['text_dark']};
}}

/* Main background */
.stApp {{
    background-color: {PALETTE['bg']};
}}

/* Sidebar */
[data-testid="stSidebar"] {{
    background-color: {PALETTE['surface']};
    border-right: 1px solid {PALETTE['border']};
}}

[data-testid="stSidebar"] .stMarkdown h2,
[data-testid="stSidebar"] .stMarkdown h3 {{
    font-family: 'Cormorant Garamond', serif;
    color: {PALETTE['slate_blue']};
    font-weight: 600;
    letter-spacing: 0.04em;
}}

/* Headers */
h1, h2, h3 {{
    font-family: 'Cormorant Garamond', serif !important;
    font-weight: 600 !important;
    color: {PALETTE['text_dark']} !important;
    letter-spacing: 0.03em;
}}

/* Metric cards */
[data-testid="metric-container"] {{
    background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 6px;
    padding: 16px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}

[data-testid="metric-container"] label {{
    font-family: 'DM Mono', monospace;
    font-size: 10px !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: {PALETTE['text_light']} !important;
}}

[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 26px !important;
    font-weight: 600;
    color: {PALETTE['text_dark']} !important;
}}

/* Dataframes */
[data-testid="stDataFrame"] {{
    border: 1px solid {PALETTE['border']};
    border-radius: 6px;
    overflow: hidden;
}}

/* Tabs */
[data-testid="stTabs"] [role="tab"] {{
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: {PALETTE['text_mid']};
}}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {{
    color: {PALETTE['slate_blue']};
    border-bottom: 2px solid {PALETTE['slate_blue']};
}}

/* Buttons */
.stButton > button {{
    background: {PALETTE['slate_blue']};
    color: white;
    border: none;
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 10px 24px;
    transition: all 0.2s;
}}

.stButton > button:hover {{
    background: {PALETTE['teal_slate']};
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(95,140,138,0.25);
}}

/* Inputs */
.stTextInput input, .stNumberInput input, .stSelectbox select {{
    border: 1px solid {PALETTE['border']};
    border-radius: 4px;
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    background: {PALETTE['surface']};
    color: {PALETTE['text_dark']};
}}

/* Slider */
.stSlider [data-baseweb="slider"] {{
    padding: 8px 0;
}}

/* Section cards */
.section-card {{
    background: {PALETTE['surface']};
    border: 1px solid {PALETTE['border']};
    border-radius: 8px;
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}}

/* Rating badges */
.badge-buy {{
    background: rgba(95,140,138,0.12);
    color: {PALETTE['buy']};
    border: 1px solid rgba(95,140,138,0.35);
    padding: 3px 12px;
    border-radius: 3px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.1em;
}}

.badge-hold {{
    background: rgba(184,168,130,0.15);
    color: {PALETTE['hold']};
    border: 1px solid rgba(184,168,130,0.4);
    padding: 3px 12px;
    border-radius: 3px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.1em;
}}

.badge-sell {{
    background: rgba(176,90,106,0.12);
    color: {PALETTE['sell']};
    border: 1px solid rgba(176,90,106,0.35);
    padding: 3px 12px;
    border-radius: 3px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.1em;
}}

/* Header strip */
.header-strip {{
    background: linear-gradient(135deg, {PALETTE['slate_blue']}18 0%, {PALETTE['powder_blue']}18 100%);
    border: 1px solid {PALETTE['powder_blue']};
    border-radius: 8px;
    padding: 20px 28px;
    margin-bottom: 24px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}}

.header-title {{
    font-family: 'Cormorant Garamond', serif;
    font-size: 32px;
    font-weight: 700;
    color: {PALETTE['slate_blue']};
    letter-spacing: 0.04em;
    margin: 0;
}}

.header-sub {{
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {PALETTE['text_light']};
    margin-top: 4px;
}}

/* Mono data */
.mono {{
    font-family: 'DM Mono', monospace;
    font-size: 12px;
}}

/* Divider */
hr {{
    border: none;
    border-top: 1px solid {PALETTE['border']};
    margin: 16px 0;
}}

/* Expander */
[data-testid="stExpander"] {{
    border: 1px solid {PALETTE['border']};
    border-radius: 6px;
    background: {PALETTE['surface']};
}}
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY TEMPLATE ─────────────────────────────────────────────────────────
PLOT_TEMPLATE = dict(
    layout=go.Layout(
        font=dict(family="DM Sans, sans-serif", color=PALETTE['text_dark'], size=11),
        paper_bgcolor=PALETTE['surface'],
        plot_bgcolor=PALETTE['bg'],
        title_font=dict(family="Cormorant Garamond, serif", size=18, color=PALETTE['text_dark']),
        xaxis=dict(gridcolor=PALETTE['border'], linecolor=PALETTE['border'], showgrid=True, zeroline=False),
        yaxis=dict(gridcolor=PALETTE['border'], linecolor=PALETTE['border'], showgrid=True, zeroline=False),
        legend=dict(bgcolor=PALETTE['surface'], bordercolor=PALETTE['border'], borderwidth=1),
        margin=dict(l=40, r=20, t=40, b=40),
        colorway=[PALETTE['slate_blue'], PALETTE['teal_slate'], PALETTE['warm_cream'], PALETTE['sage_mint'], PALETTE['powder_blue']],
    )
)

COLOR_SCALE = [
    [0.0, PALETTE['sell']],
    [0.5, PALETTE['warm_cream']],
    [1.0, PALETTE['buy']],
]

# ─── DATA FETCHING ────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def fetch_ticker_data(ticker: str):
    """Fetch comprehensive financial data from yfinance."""
    try:
        t = yf.Ticker(ticker)
        info = t.info or {}
        hist = t.history(period="2y", interval="1d")
        fin = t.financials
        bs = t.balance_sheet
        cf = t.cashflow
        return {"info": info, "hist": hist, "fin": fin, "bs": bs, "cf": cf, "valid": True}
    except Exception as e:
        return {"valid": False, "error": str(e)}

def safe_get(d, key, default=None):
    v = d.get(key, default)
    return default if v is None or (isinstance(v, float) and np.isnan(v)) else v

def extract_fundamentals(data):
    """Extract and normalise fundamental metrics from yfinance data."""
    info = data["info"]
    fin = data["fin"]
    bs = data["bs"]
    cf = data["cf"]

    def row_val(df, keywords, idx=0):
        if df is None or df.empty:
            return None
        for k in keywords:
            matches = [c for c in df.index if k.lower() in c.lower()]
            if matches:
                try:
                    v = df.loc[matches[0]].iloc[idx]
                    return float(v) if pd.notna(v) else None
                except:
                    pass
        return None

    rev = safe_get(info, "totalRevenue")
    mkt_cap = safe_get(info, "marketCap")
    ev = safe_get(info, "enterpriseValue")
    ebitda = safe_get(info, "ebitda")
    ebit = row_val(fin, ["EBIT", "Operating Income"], 0)
    net_inc = safe_get(info, "netIncomeToCommon")
    total_debt = safe_get(info, "totalDebt", 0)
    cash = safe_get(info, "totalCash", 0) or safe_get(info, "cashAndCashEquivalentsAtCarryingValue", 0)
    equity = safe_get(info, "bookValue")
    shares = safe_get(info, "sharesOutstanding")
    beta = safe_get(info, "beta", 1.0)
    pe = safe_get(info, "trailingPE")
    pb = safe_get(info, "priceToBook")
    ps = safe_get(info, "priceToSalesTrailing12Months")
    roe = safe_get(info, "returnOnEquity")
    roa = safe_get(info, "returnOnAssets")
    gross_margin = safe_get(info, "grossMargins")
    op_margin = safe_get(info, "operatingMargins")
    net_margin = safe_get(info, "profitMargins")
    rev_growth = safe_get(info, "revenueGrowth")
    eps = safe_get(info, "trailingEps")
    forward_eps = safe_get(info, "forwardEps")
    price = safe_get(info, "currentPrice") or safe_get(info, "regularMarketPrice")
    sector = safe_get(info, "sector", "Unknown")
    industry = safe_get(info, "industry", "Unknown")
    name = safe_get(info, "longName", safe_get(info, "shortName", "N/A"))

    # Free cash flow
    fcf = row_val(cf, ["Free Cash Flow", "FreeCashFlow"], 0)
    if fcf is None and cf is not None and not cf.empty:
        op_cf = row_val(cf, ["Operating Cash Flow", "Total Cash From Operating Activities"], 0)
        capex = row_val(cf, ["Capital Expenditure", "Capital Expenditures"], 0)
        if op_cf and capex:
            fcf = op_cf + capex  # capex is negative in yf

    # D&A
    da = row_val(cf, ["Depreciation", "Depreciation And Amortization"], 0) or 0

    # Net leverage
    net_debt = (total_debt or 0) - (cash or 0)
    net_lev = net_debt / ebitda if ebitda and ebitda != 0 else None

    # ROIC
    invested_capital = (total_debt or 0) + (equity * shares if equity and shares else 0)
    nopat = ebit * (1 - 0.21) if ebit else None
    roic = nopat / invested_capital if nopat and invested_capital and invested_capital != 0 else None

    # EV/EBITDA
    ev_ebitda = ev / ebitda if ev and ebitda and ebitda != 0 else None

    return {
        "name": name, "ticker": safe_get(info, "symbol", ""),
        "sector": sector, "industry": industry,
        "price": price, "mkt_cap": mkt_cap, "ev": ev,
        "rev": rev, "ebitda": ebitda, "ebit": ebit, "net_inc": net_inc,
        "eps": eps, "forward_eps": forward_eps,
        "total_debt": total_debt, "cash": cash, "net_debt": net_debt,
        "equity": equity, "shares": shares, "beta": beta,
        "da": da, "fcf": fcf,
        "pe": pe, "pb": pb, "ps": ps, "ev_ebitda": ev_ebitda,
        "roe": roe, "roa": roa, "roic": roic,
        "gross_margin": gross_margin, "op_margin": op_margin, "net_margin": net_margin,
        "rev_growth": rev_growth, "net_lev": net_lev,
    }

# ─── DCF ENGINE ───────────────────────────────────────────────────────────────
def run_dcf(f, wacc_pct, tgr_pct, rev_cagr_pct, fcf_margin_pct, years=5):
    """5-year FCF DCF with Gordon Growth terminal value."""
    wacc = wacc_pct / 100
    g = tgr_pct / 100
    cagr = rev_cagr_pct / 100
    fcf_m = fcf_margin_pct / 100
    base_rev = f["rev"] or 0

    if wacc <= g:
        return None

    proj = []
    pv_fcfs = []
    for i in range(1, years + 1):
        rev_i = base_rev * (1 + cagr) ** i
        fcf_i = rev_i * fcf_m
        pv = fcf_i / (1 + wacc) ** i
        proj.append({"year": f"Y+{i}", "revenue": rev_i, "fcf": fcf_i, "pv_fcf": pv})
        pv_fcfs.append(pv)

    last_fcf = proj[-1]["fcf"] * (1 + g)
    tv = last_fcf / (wacc - g)
    pv_tv = tv / (1 + wacc) ** years
    intrinsic_ev = sum(pv_fcfs) + pv_tv
    net_debt = f.get("net_debt", 0) or 0
    equity_val = intrinsic_ev - net_debt
    shares = f.get("shares") or 1
    intrinsic_price = equity_val / shares if shares else None
    current_price = f.get("price") or 0
    upside = ((intrinsic_price - current_price) / current_price * 100) if intrinsic_price and current_price else None

    return {
        "projections": proj,
        "pv_fcfs": sum(pv_fcfs),
        "tv": tv,
        "pv_tv": pv_tv,
        "intrinsic_ev": intrinsic_ev,
        "equity_val": equity_val,
        "intrinsic_price": intrinsic_price,
        "current_price": current_price,
        "upside": upside,
    }

def dcf_sensitivity(f, wacc_range, tgr_range, rev_cagr, fcf_margin):
    """Build sensitivity table of intrinsic EV vs WACC x TGR."""
    rows = {}
    for w in wacc_range:
        row = {}
        for g in tgr_range:
            res = run_dcf(f, w, g, rev_cagr, fcf_margin)
            if res:
                row[g] = round(res["intrinsic_ev"] / 1e9, 1)
            else:
                row[g] = None
        rows[w] = row
    return pd.DataFrame(rows, index=tgr_range).T  # WACC as rows, TGR as columns

def dcf_price_sensitivity(f, wacc_range, tgr_range, rev_cagr, fcf_margin):
    """Sensitivity of intrinsic price per share."""
    rows = {}
    for w in wacc_range:
        row = {}
        for g in tgr_range:
            res = run_dcf(f, w, g, rev_cagr, fcf_margin)
            if res and res["intrinsic_price"]:
                row[g] = round(res["intrinsic_price"], 2)
            else:
                row[g] = None
        rows[w] = row
    return pd.DataFrame(rows, index=tgr_range).T

# ─── RATING ENGINE ───────────────────────────────────────────────────────────
def compute_rating(f, dcf_res, comps_median_ev_ebitda=None):
    """Composite score (0–11): ROIC, rev growth, EBITDA margin, net lev, DCF upside, EV/EBITDA vs peers."""
    score = 0
    details = {}

    roic = f.get("roic") or 0
    if roic > 0.15: score += 2
    elif roic > 0.10: score += 1
    details["ROIC"] = f"{roic*100:.1f}%" if roic else "N/A"

    rg = f.get("rev_growth") or 0
    if rg > 0.10: score += 2
    elif rg > 0.05: score += 1
    details["Rev Growth"] = f"{rg*100:.1f}%" if rg else "N/A"

    em = f.get("op_margin") or 0
    if em > 0.20: score += 2
    elif em > 0.12: score += 1
    details["Op Margin"] = f"{em*100:.1f}%" if em else "N/A"

    nl = f.get("net_lev")
    if nl is not None:
        if nl < 1.5: score += 2
        elif nl < 3.0: score += 1
    details["Net Leverage"] = f"{nl:.1f}x" if nl is not None else "N/A"

    if dcf_res and dcf_res.get("upside") is not None:
        up = dcf_res["upside"]
        if up > 20: score += 2
        elif up > 5: score += 1
        details["DCF Upside"] = f"{up:.1f}%"
    else:
        details["DCF Upside"] = "N/A"

    if comps_median_ev_ebitda and f.get("ev_ebitda"):
        disc = (f["ev_ebitda"] - comps_median_ev_ebitda) / comps_median_ev_ebitda * 100
        if disc < -10: score += 1
        details["vs Comps"] = f"{disc:+.1f}%"
    else:
        details["vs Comps"] = "N/A"

    if score >= 8: rating = "BUY"
    elif score >= 5: rating = "HOLD"
    else: rating = "SELL"

    return rating, score, details

# ─── CHARTS ──────────────────────────────────────────────────────────────────
def plot_price_history(hist, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist["Close"],
        name="Price",
        line=dict(color=PALETTE["slate_blue"], width=2),
        fill='tozeroy',
        fillcolor=f"rgba(98,114,164,0.08)",
    ))
    # 50-day MA
    ma50 = hist["Close"].rolling(50).mean()
    fig.add_trace(go.Scatter(
        x=hist.index, y=ma50,
        name="50D MA",
        line=dict(color=PALETTE["teal_slate"], width=1.5, dash="dot"),
    ))
    ma200 = hist["Close"].rolling(200).mean()
    fig.add_trace(go.Scatter(
        x=hist.index, y=ma200,
        name="200D MA",
        line=dict(color=PALETTE["warm_cream"], width=1.5, dash="dash"),
    ))
    fig.update_layout(
        **PLOT_TEMPLATE["layout"].to_plotly_json(),
        title=f"{ticker} — Price & Moving Averages",
        xaxis_title=None, yaxis_title="Price (USD)",
        height=320,
        hovermode="x unified",
    )
    return fig

def plot_dcf_waterfall(dcf_res, ticker):
    proj = dcf_res["projections"]
    years = [p["year"] for p in proj]
    fcfs = [p["pv_fcf"] / 1e9 for p in proj]
    tv_pv = dcf_res["pv_tv"] / 1e9
    total = dcf_res["intrinsic_ev"] / 1e9

    fig = go.Figure()
    colors = [PALETTE["powder_blue"]] * len(years) + [PALETTE["teal_slate"], PALETTE["slate_blue"]]
    vals = fcfs + [tv_pv, total]
    labels = years + ["Terminal Value PV", "Intrinsic EV"]

    fig.add_trace(go.Bar(
        x=labels, y=vals,
        marker_color=colors,
        text=[f"${v:.1f}B" for v in vals],
        textposition="outside",
        textfont=dict(family="DM Mono, monospace", size=10),
    ))
    fig.update_layout(
        **PLOT_TEMPLATE["layout"].to_plotly_json(),
        title=f"{ticker} — DCF Valuation Bridge ($B)",
        yaxis_title="Value ($B)",
        height=320,
        showlegend=False,
    )
    return fig

def plot_sensitivity_heatmap(sens_df, ticker, label="Intrinsic EV ($B)"):
    wacc_vals = [f"{w}%" for w in sens_df.index]
    tgr_vals = [f"{g}%" for g in sens_df.columns]
    z = sens_df.values.tolist()

    fig = go.Figure(data=go.Heatmap(
        z=z,
        x=tgr_vals,
        y=wacc_vals,
        colorscale=[
            [0.0, PALETTE["sell"]],
            [0.35, "#d4a5b0"],
            [0.5, PALETTE["warm_cream"]],
            [0.65, PALETTE["sage_mint"]],
            [1.0, PALETTE["teal_slate"]],
        ],
        text=[[f"${v:.1f}B" if v else "—" for v in row] for row in z],
        texttemplate="%{text}",
        textfont=dict(family="DM Mono, monospace", size=10, color=PALETTE["text_dark"]),
        hovertemplate="WACC: %{y}<br>TGR: %{x}<br>" + label + ": %{text}<extra></extra>",
        showscale=True,
        colorbar=dict(
            title=label,
            titlefont=dict(family="DM Mono, monospace", size=10),
            tickfont=dict(family="DM Mono, monospace", size=9),
        )
    ))
    fig.update_layout(
        **PLOT_TEMPLATE["layout"].to_plotly_json(),
        title=f"{ticker} — Sensitivity: WACC × Terminal Growth",
        xaxis_title="Terminal Growth Rate",
        yaxis_title="WACC",
        height=380,
    )
    return fig

def plot_comps_bubble(comps_data):
    tickers = [c["ticker"] for c in comps_data]
    ev_ebitda = [c.get("ev_ebitda") or 0 for c in comps_data]
    op_margin = [(c.get("op_margin") or 0) * 100 for c in comps_data]
    mkt_cap = [(c.get("mkt_cap") or 1e9) / 1e9 for c in comps_data]
    rev_growth = [(c.get("rev_growth") or 0) * 100 for c in comps_data]

    fig = go.Figure()
    colors = [PALETTE["slate_blue"], PALETTE["teal_slate"], PALETTE["sage_mint"],
              PALETTE["powder_blue"], PALETTE["warm_cream"], "#8fa8c8", "#7a9e9c", "#c8bba0"]

    for i, (t, ev, om, mc, rg) in enumerate(zip(tickers, ev_ebitda, op_margin, mkt_cap, rev_growth)):
        fig.add_trace(go.Scatter(
            x=[rg], y=[ev],
            mode='markers+text',
            name=t,
            text=[t],
            textposition="top center",
            textfont=dict(family="DM Mono, monospace", size=10),
            marker=dict(
                size=max(12, min(50, mc / 20)),
                color=colors[i % len(colors)],
                opacity=0.85,
                line=dict(width=1.5, color='white'),
            ),
            hovertemplate=f"<b>{t}</b><br>EV/EBITDA: {ev:.1f}x<br>Op Margin: {om:.1f}%<br>Rev Growth: {rg:.1f}%<br>Mkt Cap: ${mc:.0f}B<extra></extra>",
        ))

    # Sector median lines
    valid_ev = [e for e in ev_ebitda if e > 0]
    if valid_ev:
        med_ev = np.median(valid_ev)
        fig.add_hline(y=med_ev, line_dash="dash", line_color=PALETTE["text_light"],
                      annotation_text=f"Median: {med_ev:.1f}x",
                      annotation_font=dict(family="DM Mono, monospace", size=9))

    fig.update_layout(
        **PLOT_TEMPLATE["layout"].to_plotly_json(),
        title="Comps Universe — EV/EBITDA vs Revenue Growth (bubble = Mkt Cap)",
        xaxis_title="Revenue Growth (%)",
        yaxis_title="EV / EBITDA (x)",
        height=420,
        showlegend=False,
    )
    return fig

def plot_scenario_tornado(scenarios, ticker):
    """Tornado chart showing sensitivity of intrinsic price across scenarios."""
    base_price = scenarios.get("Base", {}).get("intrinsic_price", 0) or 0
    labels, lows, highs = [], [], []

    for name, res in scenarios.items():
        if res and res.get("intrinsic_price"):
            diff = res["intrinsic_price"] - base_price
            labels.append(name)
            if diff >= 0:
                lows.append(0)
                highs.append(diff)
            else:
                lows.append(diff)
                highs.append(0)

    fig = go.Figure()
    for i, (label, lo, hi) in enumerate(zip(labels, lows, highs)):
        color = PALETTE["teal_slate"] if hi >= 0 else PALETTE["sell"]
        val = hi if hi != 0 else lo
        fig.add_trace(go.Bar(
            x=[val], y=[label],
            orientation='h',
            base=[lo],
            marker_color=color,
            text=[f"${base_price + val:.2f}"],
            textposition="outside",
            textfont=dict(family="DM Mono, monospace", size=10),
            showlegend=False,
        ))

    fig.add_vline(x=0, line_color=PALETTE["text_mid"], line_width=1)
    fig.update_layout(
        **PLOT_TEMPLATE["layout"].to_plotly_json(),
        title=f"{ticker} — Scenario Intrinsic Price vs Base (delta $)",
        xaxis_title="Delta vs Base Case ($)",
        height=max(280, len(labels) * 55),
        barmode='overlay',
    )
    return fig

def plot_monte_carlo(f, base_cagr, base_fcf_margin, base_wacc, base_tgr, n_sims=2000):
    """Monte Carlo simulation of intrinsic price."""
    results = []
    for _ in range(n_sims):
        cagr = np.random.normal(base_cagr, 2.5)
        fcf_m = np.random.normal(base_fcf_margin, 2.0)
        wacc = np.random.normal(base_wacc, 0.5)
        tgr = np.random.normal(base_tgr, 0.25)
        tgr = min(tgr, wacc - 0.5)  # TGR must be < WACC
        res = run_dcf(f, max(wacc, 5), max(tgr, 0.5), max(cagr, 0), max(fcf_m, 1))
        if res and res["intrinsic_price"] and res["intrinsic_price"] > 0:
            results.append(res["intrinsic_price"])

    results = np.array(results)
    p5, p25, p50, p75, p95 = np.percentile(results, [5, 25, 50, 75, 95])

    fig = go.Figure()
    fig.add_trace(go.Histogram(
        x=results,
        nbinsx=60,
        marker_color=PALETTE["powder_blue"],
        marker_line_color=PALETTE["slate_blue"],
        marker_line_width=0.5,
        opacity=0.85,
        name="Simulated Price",
    ))
    for pct, val, color in [
        (5, p5, PALETTE["sell"]),
        (50, p50, PALETTE["slate_blue"]),
        (95, p95, PALETTE["teal_slate"]),
    ]:
        fig.add_vline(
            x=val,
            line_color=color,
            line_dash="dash" if pct != 50 else "solid",
            annotation_text=f"P{pct}: ${val:.0f}",
            annotation_font=dict(family="DM Mono, monospace", size=9, color=color),
        )
    if f.get("price"):
        fig.add_vline(
            x=f["price"],
            line_color=PALETTE["warm_cream"],
            line_width=2,
            annotation_text=f"Market: ${f['price']:.0f}",
            annotation_font=dict(family="DM Mono, monospace", size=9),
        )

    fig.update_layout(
        **PLOT_TEMPLATE["layout"].to_plotly_json(),
        title=f"Monte Carlo — Intrinsic Price Distribution ({n_sims:,} simulations)",
        xaxis_title="Intrinsic Price per Share ($)",
        yaxis_title="Frequency",
        height=360,
        showlegend=False,
    )
    return fig, {"p5": p5, "p25": p25, "p50": p50, "p75": p75, "p95": p95, "mean": results.mean(), "std": results.std()}

def plot_return_attribution(hist):
    """Rolling 252d return with vol bands."""
    returns = hist["Close"].pct_change().dropna()
    roll_ret = returns.rolling(21).mean() * 252  # annualised
    roll_vol = returns.rolling(21).std() * np.sqrt(252)
    upper = roll_ret + roll_vol
    lower = roll_ret - roll_vol

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=roll_ret.index, y=upper * 100,
        fill=None, line=dict(color="rgba(0,0,0,0)"), showlegend=False,
    ))
    fig.add_trace(go.Scatter(
        x=roll_ret.index, y=lower * 100,
        fill='tonexty',
        fillcolor=f"rgba(98,114,164,0.10)",
        line=dict(color="rgba(0,0,0,0)"),
        name="±1 Vol Band",
    ))
    fig.add_trace(go.Scatter(
        x=roll_ret.index, y=roll_ret * 100,
        name="21D Ann. Return",
        line=dict(color=PALETTE["slate_blue"], width=2),
    ))
    fig.add_hline(y=0, line_color=PALETTE["border"], line_width=1)
    fig.update_layout(
        **PLOT_TEMPLATE["layout"].to_plotly_json(),
        title="21D Rolling Annualised Return with Volatility Band",
        yaxis_title="Annualised Return (%)",
        height=280,
        hovermode="x unified",
    )
    return fig

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt_b(v):
    if v is None: return "—"
    if abs(v) >= 1e12: return f"${v/1e12:.2f}T"
    if abs(v) >= 1e9: return f"${v/1e9:.1f}B"
    if abs(v) >= 1e6: return f"${v/1e6:.0f}M"
    return f"${v:.0f}"

def fmt_pct(v, decimals=1):
    if v is None: return "—"
    return f"{v*100:.{decimals}f}%"

def fmt_x(v, decimals=1):
    if v is None: return "—"
    return f"{v:.{decimals}f}x"

def fmt_num(v, decimals=2, prefix=""):
    if v is None: return "—"
    return f"{prefix}{v:.{decimals}f}"

def badge_html(rating):
    cls = f"badge-{rating.lower()}"
    return f'<span class="{cls}">{rating}</span>'

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ◈ Sell-Side Lite")
    st.markdown("*Institutional Research Platform*")
    st.markdown("---")

    st.markdown("### Universe")
    tickers_input = st.text_area(
        "Enter tickers (comma or line separated)",
        value="CAT, DE, HON, RTX, GE",
        height=80,
        help="e.g. CAT, DE, HON, RTX, GE"
    )
    tickers = [t.strip().upper() for t in tickers_input.replace("\n", ",").split(",") if t.strip()]

    st.markdown("---")
    st.markdown("### DCF Assumptions")
    wacc = st.slider("WACC (%)", 5.0, 15.0, 9.0, 0.25)
    tgr = st.slider("Terminal Growth (%)", 1.0, 4.0, 2.5, 0.25)
    rev_cagr = st.slider("Revenue CAGR (%)", 0.0, 20.0, 6.0, 0.5)
    fcf_margin = st.slider("FCF Margin (%)", 2.0, 30.0, 12.0, 0.5)
    dcf_years = st.slider("Projection Years", 3, 10, 5)

    st.markdown("---")
    st.markdown("### Macro Overlays")
    ism_pmi = st.slider("ISM Manufacturing PMI", 40.0, 65.0, 52.3, 0.1)
    ust_10y = st.slider("10Y UST Yield (%)", 2.0, 7.0, 4.35, 0.05)
    capex_growth = st.slider("Industrial Capex Growth (%)", -15.0, 25.0, 7.2, 0.5)
    pmi_regime = "EXPANSION" if ism_pmi > 50 else "CONTRACTION"
    rate_regime = "RESTRICTIVE" if ust_10y > 4.5 else ("ACCOMMODATIVE" if ust_10y < 3.0 else "NEUTRAL")

    st.markdown("---")
    st.markdown("### Screens")
    min_rating = st.selectbox("Minimum Rating", ["All", "BUY", "HOLD"])
    max_net_lev = st.slider("Max Net Leverage (x)", 0.5, 8.0, 6.0, 0.25)
    min_roic = st.slider("Min ROIC (%)", 0.0, 30.0, 0.0, 0.5)

    run_btn = st.button("▶ RUN SCREEN", use_container_width=True)

# ─── HEADER ──────────────────────────────────────────────────────────────────
pmi_color = PALETTE["teal_slate"] if ism_pmi > 50 else PALETTE["sell"]
rate_color = PALETTE["sell"] if ust_10y > 4.5 else PALETTE["teal_slate"]

st.markdown(f"""
<div class="section-card" style="background: linear-gradient(135deg, rgba(98,114,164,0.06) 0%, rgba(95,140,138,0.06) 100%); border-color: {PALETTE['powder_blue']};">
  <div style="display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
    <div>
      <p class="header-title" style="font-family:'Cormorant Garamond',serif; font-size:28px; font-weight:700; color:{PALETTE['slate_blue']}; margin:0;">◈ Sell-Side Lite</p>
      <p class="header-sub" style="font-family:'DM Mono',monospace; font-size:10px; letter-spacing:0.18em; text-transform:uppercase; color:{PALETTE['text_light']}; margin:4px 0 0;">Institutional Equity Research · Industrial Sector</p>
    </div>
    <div style="display:flex; gap:24px; flex-wrap:wrap;">
      <div style="text-align:center;">
        <div style="font-family:'DM Mono',monospace; font-size:9px; text-transform:uppercase; letter-spacing:0.1em; color:{PALETTE['text_light']};">ISM PMI</div>
        <div style="font-family:'Cormorant Garamond',serif; font-size:20px; font-weight:700; color:{pmi_color};">{ism_pmi:.1f} <span style="font-size:11px;">({pmi_regime})</span></div>
      </div>
      <div style="text-align:center;">
        <div style="font-family:'DM Mono',monospace; font-size:9px; text-transform:uppercase; letter-spacing:0.1em; color:{PALETTE['text_light']};">10Y UST</div>
        <div style="font-family:'Cormorant Garamond',serif; font-size:20px; font-weight:700; color:{rate_color};">{ust_10y:.2f}% <span style="font-size:11px;">({rate_regime})</span></div>
      </div>
      <div style="text-align:center;">
        <div style="font-family:'DM Mono',monospace; font-size:9px; text-transform:uppercase; letter-spacing:0.1em; color:{PALETTE['text_light']};">Capex Growth</div>
        <div style="font-family:'Cormorant Garamond',serif; font-size:20px; font-weight:700; color:{PALETTE['teal_slate'] if capex_growth >= 0 else PALETTE['sell']};">{capex_growth:+.1f}%</div>
      </div>
      <div style="text-align:center;">
        <div style="font-family:'DM Mono',monospace; font-size:9px; text-transform:uppercase; letter-spacing:0.1em; color:{PALETTE['text_light']};">Universe</div>
        <div style="font-family:'Cormorant Garamond',serif; font-size:20px; font-weight:700; color:{PALETTE['slate_blue']};">{len(tickers)} Names</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── MAIN TABS ────────────────────────────────────────────────────────────────
tab_screener, tab_single, tab_comps, tab_dcf, tab_scenario, tab_monte = st.tabs([
    "⬡  SCREENER", "◈  DEEP DIVE", "⬢  EV/EBITDA COMPS", "◇  DCF SENSITIVITY", "⟁  SCENARIO ENGINE", "⊕  MONTE CARLO"
])

# ─── LOAD DATA ────────────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)
def load_all(tickers_tuple):
    results = {}
    for t in tickers_tuple:
        data = fetch_ticker_data(t)
        if data["valid"]:
            f = extract_fundamentals(data)
            f["_hist"] = data["hist"]
            results[t] = f
    return results

with st.spinner("Fetching market data…"):
    all_data = load_all(tuple(tickers))

# Run DCF for all tickers
all_dcf = {}
for t, f in all_data.items():
    if f.get("rev"):
        all_dcf[t] = run_dcf(f, wacc, tgr, rev_cagr, fcf_margin, dcf_years)

# Compute ratings
all_ratings = {}
sector_ev_ebitdas = [f.get("ev_ebitda") for f in all_data.values() if f.get("ev_ebitda")]
sector_median = np.median(sector_ev_ebitdas) if sector_ev_ebitdas else None
for t, f in all_data.items():
    rating, score, details = compute_rating(f, all_dcf.get(t), sector_median)
    all_ratings[t] = {"rating": rating, "score": score, "details": details}

# ─── TAB 1: SCREENER ─────────────────────────────────────────────────────────
with tab_screener:
    rows = []
    for t, f in all_data.items():
        r = all_ratings[t]
        dcf_res = all_dcf.get(t)
        row = {
            "Ticker": t,
            "Name": (f.get("name") or "")[:28],
            "Sector": f.get("industry", "")[:22],
            "Price": f.get("price"),
            "Mkt Cap": f.get("mkt_cap"),
            "EV/EBITDA": f.get("ev_ebitda"),
            "EV/EBITDA vs Med": ((f.get("ev_ebitda") - sector_median) / sector_median * 100) if f.get("ev_ebitda") and sector_median else None,
            "DCF Upside %": dcf_res.get("upside") if dcf_res else None,
            "Intrinsic Price": dcf_res.get("intrinsic_price") if dcf_res else None,
            "EBITDA Margin": f.get("op_margin"),
            "Rev Growth": f.get("rev_growth"),
            "ROIC": f.get("roic"),
            "Net Leverage": f.get("net_lev"),
            "Beta": f.get("beta"),
            "Score": r["score"],
            "Rating": r["rating"],
        }
        # Apply screens
        if min_rating != "All":
            order = {"BUY": 3, "HOLD": 2, "SELL": 1}
            if order.get(r["rating"], 0) < order.get(min_rating, 0):
                continue
        if row["Net Leverage"] is not None and row["Net Leverage"] > max_net_lev:
            continue
        if row["ROIC"] is not None and row["ROIC"] * 100 < min_roic:
            continue
        rows.append(row)

    if rows:
        df = pd.DataFrame(rows)

        # Summary row
        buys = sum(1 for r in rows if r["Rating"] == "BUY")
        holds = sum(1 for r in rows if r["Rating"] == "HOLD")
        sells = sum(1 for r in rows if r["Rating"] == "SELL")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Universe", len(rows))
        with c2:
            st.metric("BUY", buys, delta=None)
        with c3:
            st.metric("HOLD", holds)
        with c4:
            st.metric("SELL", sells)

        st.markdown("---")

        # Format for display
        disp = df.copy()
        disp["Price"] = disp["Price"].apply(lambda v: f"${v:.2f}" if v else "—")
        disp["Mkt Cap"] = disp["Mkt Cap"].apply(fmt_b)
        disp["EV/EBITDA"] = disp["EV/EBITDA"].apply(lambda v: f"{v:.1f}x" if v else "—")
        disp["EV/EBITDA vs Med"] = disp["EV/EBITDA vs Med"].apply(lambda v: f"{v:+.1f}%" if v else "—")
        disp["DCF Upside %"] = disp["DCF Upside %"].apply(lambda v: f"{v:+.1f}%" if v else "—")
        disp["Intrinsic Price"] = disp["Intrinsic Price"].apply(lambda v: f"${v:.2f}" if v else "—")
        disp["EBITDA Margin"] = disp["EBITDA Margin"].apply(lambda v: f"{v*100:.1f}%" if v else "—")
        disp["Rev Growth"] = disp["Rev Growth"].apply(lambda v: f"{v*100:.1f}%" if v else "—")
        disp["ROIC"] = disp["ROIC"].apply(lambda v: f"{v*100:.1f}%" if v else "—")
        disp["Net Leverage"] = disp["Net Leverage"].apply(lambda v: f"{v:.1f}x" if v else "—")
        disp["Beta"] = disp["Beta"].apply(lambda v: f"{v:.2f}" if v else "—")

        # Colour rating column
        def style_rating(val):
            if val == "BUY": return f"color: {PALETTE['buy']}; font-weight: 600;"
            if val == "SELL": return f"color: {PALETTE['sell']}; font-weight: 600;"
            return f"color: {PALETTE['hold']}; font-weight: 600;"

        styled = disp.style.applymap(style_rating, subset=["Rating"])
        st.dataframe(styled, use_container_width=True, height=380)

        # Mini sparklines row
        st.markdown("### Price Sparklines")
        cols = st.columns(min(len(rows), 4))
        for i, row in enumerate(rows[:8]):
            t = row["Ticker"]
            with cols[i % 4]:
                hist = all_data[t].get("_hist")
                if hist is not None and not hist.empty:
                    closes = hist["Close"].tail(90)
                    color = PALETTE["teal_slate"] if closes.iloc[-1] >= closes.iloc[0] else PALETTE["sell"]
                    fig_mini = go.Figure(go.Scatter(
                        y=closes, x=list(range(len(closes))),
                        line=dict(color=color, width=2),
                        fill='tozeroy',
                        fillcolor=f"rgba({'95,140,138' if color == PALETTE['teal_slate'] else '176,90,106'},0.08)",
                    ))
                    fig_mini.update_layout(
                        paper_bgcolor=PALETTE["surface"],
                        plot_bgcolor=PALETTE["bg"],
                        margin=dict(l=4, r=4, t=28, b=4),
                        height=110,
                        title=dict(text=f"<b>{t}</b> — {row['Rating']}", font=dict(size=11, family="DM Mono, monospace"), x=0.05),
                        xaxis=dict(visible=False),
                        yaxis=dict(visible=False),
                        showlegend=False,
                    )
                    st.plotly_chart(fig_mini, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No tickers match current screens. Adjust filters in the sidebar.")

# ─── TAB 2: DEEP DIVE ─────────────────────────────────────────────────────────
with tab_single:
    if not all_data:
        st.info("No valid tickers loaded.")
    else:
        sel = st.selectbox("Select ticker for deep dive", list(all_data.keys()))
        f = all_data[sel]
        dcf_res = all_dcf.get(sel)
        rating, score, details = all_ratings[sel]["rating"], all_ratings[sel]["score"], all_ratings[sel]["details"]

        # Header
        price_chg = None
        hist = f.get("_hist")
        if hist is not None and not hist.empty and len(hist) >= 2:
            price_chg = (hist["Close"].iloc[-1] - hist["Close"].iloc[-2]) / hist["Close"].iloc[-2] * 100

        st.markdown(f"""
        <div class="section-card">
          <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
            <div>
              <div style="font-family:'Cormorant Garamond',serif; font-size:36px; font-weight:700; color:{PALETTE['slate_blue']}; line-height:1;">{sel}</div>
              <div style="font-family:'DM Sans',sans-serif; font-size:13px; color:{PALETTE['text_mid']}; margin-top:4px;">{f.get('name','')} · {f.get('industry','')}</div>
            </div>
            <div style="display:flex; gap:32px; align-items:center;">
              <div>
                <div style="font-family:'Cormorant Garamond',serif; font-size:32px; font-weight:700; color:{PALETTE['text_dark']};">${f['price']:.2f if f.get('price') else '—'}</div>
                <div style="font-family:'DM Mono',monospace; font-size:11px; color:{PALETTE['teal_slate'] if price_chg and price_chg>=0 else PALETTE['sell']};">{f'+{price_chg:.2f}%' if price_chg else ''}</div>
              </div>
              <div>{badge_html(rating)}<div style="font-family:'DM Mono',monospace; font-size:10px; color:{PALETTE['text_light']}; margin-top:6px; text-align:center;">Score: {score}/11</div></div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # KPI row
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("Market Cap", fmt_b(f.get("mkt_cap")))
        k2.metric("EV", fmt_b(f.get("ev")))
        k3.metric("EV/EBITDA", fmt_x(f.get("ev_ebitda")))
        k4.metric("Net Leverage", fmt_x(f.get("net_lev")))
        k5.metric("ROIC", fmt_pct(f.get("roic")))
        k6.metric("Beta", fmt_num(f.get("beta")))

        k7, k8, k9, k10, k11, k12 = st.columns(6)
        k7.metric("Revenue", fmt_b(f.get("rev")))
        k8.metric("EBITDA", fmt_b(f.get("ebitda")))
        k9.metric("FCF", fmt_b(f.get("fcf")))
        k10.metric("Op Margin", fmt_pct(f.get("op_margin")))
        k11.metric("Rev Growth", fmt_pct(f.get("rev_growth")))
        k12.metric("P/E", fmt_x(f.get("pe")))

        # Price chart
        if hist is not None and not hist.empty:
            st.plotly_chart(plot_price_history(hist, sel), use_container_width=True)
            st.plotly_chart(plot_return_attribution(hist), use_container_width=True)

        # DCF result
        if dcf_res:
            st.markdown("### DCF Valuation")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Intrinsic EV", fmt_b(dcf_res.get("intrinsic_ev")))
            d2.metric("Equity Value", fmt_b(dcf_res.get("equity_val")))
            d3.metric("Intrinsic Price", f"${dcf_res['intrinsic_price']:.2f}" if dcf_res.get("intrinsic_price") else "—")
            d4.metric("DCF Upside", f"{dcf_res['upside']:+.1f}%" if dcf_res.get("upside") else "—")
            st.plotly_chart(plot_dcf_waterfall(dcf_res, sel), use_container_width=True)

        # Rating breakdown
        st.markdown("### Rating Breakdown")
        rb_cols = st.columns(len(details))
        for i, (k, v) in enumerate(details.items()):
            rb_cols[i].metric(k, v)

# ─── TAB 3: EV/EBITDA COMPS ──────────────────────────────────────────────────
with tab_comps:
    comps_data = list(all_data.values())
    valid_comps = [c for c in comps_data if c.get("ev_ebitda") and c.get("op_margin")]

    if not valid_comps:
        st.info("Insufficient data for comps.")
    else:
        st.plotly_chart(plot_comps_bubble(valid_comps), use_container_width=True)

        st.markdown("### Comparable Company Table")
        ev_ebitdas_all = [c["ev_ebitda"] for c in valid_comps]
        median_ev_ebitda = np.median(ev_ebitdas_all)

        comp_rows = []
        for c in comps_data:
            ev_e = c.get("ev_ebitda")
            prem_disc = ((ev_e - median_ev_ebitda) / median_ev_ebitda * 100) if ev_e and median_ev_ebitda else None
            comp_rows.append({
                "Ticker": c.get("ticker", ""),
                "Name": (c.get("name") or "")[:28],
                "Revenue": fmt_b(c.get("rev")),
                "EBITDA": fmt_b(c.get("ebitda")),
                "EV": fmt_b(c.get("ev")),
                "EV/EBITDA": fmt_x(ev_e),
                "vs Median": f"{prem_disc:+.1f}%" if prem_disc else "—",
                "Op Margin": fmt_pct(c.get("op_margin")),
                "Rev Growth": fmt_pct(c.get("rev_growth")),
                "Net Lev": fmt_x(c.get("net_lev")),
                "P/E": fmt_x(c.get("pe")),
                "ROE": fmt_pct(c.get("roe")),
            })

        # Add median row
        comp_rows.append({
            "Ticker": "— MEDIAN —",
            "Name": "",
            "Revenue": "—",
            "EBITDA": "—",
            "EV": "—",
            "EV/EBITDA": f"{median_ev_ebitda:.1f}x",
            "vs Median": "0.0%",
            "Op Margin": fmt_pct(np.median([c["op_margin"] for c in valid_comps if c.get("op_margin")])),
            "Rev Growth": "—",
            "Net Lev": "—",
            "P/E": "—",
            "ROE": "—",
        })

        comp_df = pd.DataFrame(comp_rows)

        def style_vs_median(val):
            try:
                v = float(val.replace("%","").replace("+",""))
                if v < -10: return f"color:{PALETTE['buy']}; font-weight:600;"
                if v > 15: return f"color:{PALETTE['sell']}; font-weight:600;"
            except:
                pass
            return ""

        styled_comp = comp_df.style.applymap(style_vs_median, subset=["vs Median"])
        st.dataframe(styled_comp, use_container_width=True, height=420)

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Median EV/EBITDA", fmt_x(median_ev_ebitda))
        m2.metric("Median Op Margin", fmt_pct(np.median([c["op_margin"] for c in valid_comps if c.get("op_margin")])))
        if ev_ebitdas_all:
            m3.metric("Min EV/EBITDA", fmt_x(min(ev_ebitdas_all)))
            m4.metric("Max EV/EBITDA", fmt_x(max(ev_ebitdas_all)))

# ─── TAB 4: DCF SENSITIVITY ──────────────────────────────────────────────────
with tab_dcf:
    if not all_data:
        st.info("No data loaded.")
    else:
        sel_dcf = st.selectbox("Select ticker for sensitivity", list(all_data.keys()), key="dcf_sel")
        f_dcf = all_data[sel_dcf]

        wacc_range = np.arange(6.0, 13.5, 0.5).tolist()
        tgr_range = [1.5, 2.0, 2.5, 3.0, 3.5]

        c_sens, c_price = st.columns(2)
        with c_sens:
            if f_dcf.get("rev"):
                sens = dcf_sensitivity(f_dcf, wacc_range, tgr_range, rev_cagr, fcf_margin)
                sens.index = [f"{w:.1f}%" for w in sens.index]
                sens.columns = [f"{g:.1f}%" for g in tgr_range]
                st.plotly_chart(plot_sensitivity_heatmap(
                    dcf_sensitivity(f_dcf, wacc_range, tgr_range, rev_cagr, fcf_margin),
                    sel_dcf, "Intrinsic EV ($B)"
                ), use_container_width=True)
        with c_price:
            if f_dcf.get("rev"):
                st.plotly_chart(plot_sensitivity_heatmap(
                    dcf_price_sensitivity(f_dcf, wacc_range, tgr_range, rev_cagr, fcf_margin),
                    sel_dcf, "Intrinsic Price ($)"
                ), use_container_width=True)

        if f_dcf.get("rev"):
            st.markdown("### Full Sensitivity Table — Intrinsic EV ($B)")
            sens_df = dcf_sensitivity(f_dcf, wacc_range, tgr_range, rev_cagr, fcf_margin)
            sens_df.index = [f"{w:.1f}%" for w in sens_df.index]
            sens_df.columns = [f"TGR {g:.1f}%" for g in tgr_range]

            def highlight_sens(val):
                cur_ev = (f_dcf.get("ev") or 0) / 1e9
                if cur_ev == 0: return ""
                try:
                    diff_pct = (val - cur_ev) / cur_ev * 100
                    if diff_pct > 20: return f"background-color: rgba(95,140,138,0.25); color:{PALETTE['buy']}; font-weight:600;"
                    if diff_pct > 5: return f"background-color: rgba(178,201,191,0.2);"
                    if diff_pct < -15: return f"background-color: rgba(176,90,106,0.2); color:{PALETTE['sell']}; font-weight:600;"
                except:
                    pass
                return ""

            st.dataframe(
                sens_df.style.applymap(highlight_sens).format("{:.1f}"),
                use_container_width=True
            )

# ─── TAB 5: SCENARIO ENGINE ──────────────────────────────────────────────────
with tab_scenario:
    st.markdown("### ⟁ Scenario Engineering")
    st.markdown("*Define bull, base, and bear cases — or build custom scenarios with full parameter control.*")

    sel_sc = st.selectbox("Select ticker", list(all_data.keys()), key="sc_sel")
    f_sc = all_data[sel_sc]

    st.markdown("---")

    # Three scenario columns
    col_bear, col_base, col_bull = st.columns(3)

    with col_bear:
        bear_color = PALETTE["sell"]
        st.markdown(f"<h4 style='color:{bear_color};'>⬇ Bear Case</h4>", unsafe_allow_html=True)
        bear_cagr = st.slider("Rev CAGR (%)", -5.0, 20.0, max(rev_cagr - 4, 0.0), 0.25, key="bear_cagr")
        bear_fcf = st.slider("FCF Margin (%)", 1.0, 30.0, max(fcf_margin - 4, 2.0), 0.5, key="bear_fcf")
        bear_wacc = st.slider("WACC (%)", 5.0, 16.0, min(wacc + 1.5, 15.0), 0.25, key="bear_wacc")
        bear_tgr = st.slider("Terminal Growth (%)", 0.5, 4.0, max(tgr - 0.5, 0.5), 0.25, key="bear_tgr")
        bear_label = st.text_input("Scenario name", "Bear", key="bear_label")

    with col_base:
        base_color = PALETTE["slate_blue"]
        st.markdown(f"<h4 style='color:{base_color};'>◆ Base Case</h4>", unsafe_allow_html=True)
        base_cagr = st.slider("Rev CAGR (%)", -5.0, 20.0, rev_cagr, 0.25, key="base_cagr")
        base_fcf = st.slider("FCF Margin (%)", 1.0, 30.0, fcf_margin, 0.5, key="base_fcf")
        base_wacc = st.slider("WACC (%)", 5.0, 16.0, wacc, 0.25, key="base_wacc")
        base_tgr = st.slider("Terminal Growth (%)", 0.5, 4.0, tgr, 0.25, key="base_tgr")
        base_label = st.text_input("Scenario name", "Base", key="base_label")

    with col_bull:
        bull_color = PALETTE["buy"]
        st.markdown(f"<h4 style='color:{bull_color};'>⬆ Bull Case</h4>", unsafe_allow_html=True)
        bull_cagr = st.slider("Rev CAGR (%)", -5.0, 20.0, min(rev_cagr + 4, 20.0), 0.25, key="bull_cagr")
        bull_fcf = st.slider("FCF Margin (%)", 1.0, 30.0, min(fcf_margin + 4, 30.0), 0.5, key="bull_fcf")
        bull_wacc = st.slider("WACC (%)", 5.0, 16.0, max(wacc - 1.0, 5.0), 0.25, key="bull_wacc")
        bull_tgr = st.slider("Terminal Growth (%)", 0.5, 4.0, min(tgr + 0.5, 4.0), 0.25, key="bull_tgr")
        bull_label = st.text_input("Scenario name", "Bull", key="bull_label")

    # Custom scenario
    with st.expander("+ Add Custom Scenario"):
        c1, c2, c3, c4, c5 = st.columns(5)
        with c1: custom_cagr = st.number_input("Rev CAGR (%)", -10.0, 30.0, rev_cagr)
        with c2: custom_fcf = st.number_input("FCF Margin (%)", 0.0, 40.0, fcf_margin)
        with c3: custom_wacc = st.number_input("WACC (%)", 4.0, 20.0, wacc)
        with c4: custom_tgr = st.number_input("TGR (%)", 0.5, 5.0, tgr)
        with c5: custom_label = st.text_input("Label", "Custom")
        use_custom = st.checkbox("Include custom scenario", value=False)

    st.markdown("---")

    # Run scenarios
    scenarios_params = {
        bear_label: (bear_cagr, bear_fcf, bear_wacc, bear_tgr),
        base_label: (base_cagr, base_fcf, base_wacc, base_tgr),
        bull_label: (bull_cagr, bull_fcf, bull_wacc, bull_tgr),
    }
    if use_custom:
        scenarios_params[custom_label] = (custom_cagr, custom_fcf, custom_wacc, custom_tgr)

    scenario_results = {}
    for name, (c_, f_, w_, g_) in scenarios_params.items():
        if f_sc.get("rev"):
            scenario_results[name] = run_dcf(f_sc, w_, g_, c_, f_, dcf_years)

    # Summary table
    sc_rows = []
    for name, res in scenario_results.items():
        if res:
            sc_rows.append({
                "Scenario": name,
                "Rev CAGR": f"{scenarios_params[name][0]:.1f}%",
                "FCF Margin": f"{scenarios_params[name][1]:.1f}%",
                "WACC": f"{scenarios_params[name][2]:.2f}%",
                "TGR": f"{scenarios_params[name][3]:.2f}%",
                "Intrinsic EV": fmt_b(res.get("intrinsic_ev")),
                "Equity Value": fmt_b(res.get("equity_val")),
                "Intrinsic Price": f"${res['intrinsic_price']:.2f}" if res.get("intrinsic_price") else "—",
                "DCF Upside": f"{res['upside']:+.1f}%" if res.get("upside") else "—",
            })

    if sc_rows:
        sc_df = pd.DataFrame(sc_rows)

        def style_upside(val):
            try:
                v = float(val.replace("%","").replace("+",""))
                if v > 15: return f"color:{PALETTE['buy']}; font-weight:700;"
                if v < -10: return f"color:{PALETTE['sell']}; font-weight:700;"
            except: pass
            return ""

        st.dataframe(
            sc_df.style.applymap(style_upside, subset=["DCF Upside"]),
            use_container_width=True
        )

    # Tornado chart
    if scenario_results:
        st.plotly_chart(plot_scenario_tornado(scenario_results, sel_sc), use_container_width=True)

    # FCF Projection comparison
    st.markdown("### FCF Projection Comparison")
    fig_fc = go.Figure()
    colors_sc = [PALETTE["sell"], PALETTE["slate_blue"], PALETTE["buy"], PALETTE["teal_slate"]]
    for i, (name, res) in enumerate(scenario_results.items()):
        if res and res.get("projections"):
            proj = res["projections"]
            fig_fc.add_trace(go.Scatter(
                x=[p["year"] for p in proj],
                y=[p["fcf"] / 1e9 for p in proj],
                name=name,
                line=dict(color=colors_sc[i % len(colors_sc)], width=2.5),
                mode="lines+markers",
                marker=dict(size=7),
            ))
    fig_fc.update_layout(
        **PLOT_TEMPLATE["layout"].to_plotly_json(),
        title=f"{sel_sc} — Projected FCF by Scenario ($B)",
        yaxis_title="Free Cash Flow ($B)",
        height=340,
    )
    st.plotly_chart(fig_fc, use_container_width=True)

# ─── TAB 6: MONTE CARLO ──────────────────────────────────────────────────────
with tab_monte:
    st.markdown("### ⊕ Monte Carlo Simulation")
    st.markdown("*Stochastic valuation sampling WACC, TGR, Revenue CAGR, and FCF Margin from normal distributions.*")

    sel_mc = st.selectbox("Select ticker", list(all_data.keys()), key="mc_sel")
    f_mc = all_data[sel_mc]

    mc_c1, mc_c2 = st.columns(2)
    with mc_c1:
        n_sims = st.slider("Simulations", 500, 10000, 2000, 500)
    with mc_c2:
        st.markdown(f"""
        <div style="font-family:'DM Mono',monospace; font-size:11px; color:{PALETTE['text_mid']}; padding-top:8px;">
        Base: WACC {wacc}% ± 0.5σ · TGR {tgr}% ± 0.25σ<br>
        CAGR {rev_cagr}% ± 2.5σ · FCF Margin {fcf_margin}% ± 2.0σ
        </div>
        """, unsafe_allow_html=True)

    if f_mc.get("rev") and f_mc.get("shares"):
        fig_mc, mc_stats = plot_monte_carlo(f_mc, rev_cagr, fcf_margin, wacc, tgr, n_sims)
        st.plotly_chart(fig_mc, use_container_width=True)

        # Percentile table
        mc1, mc2, mc3, mc4, mc5, mc6 = st.columns(6)
        mc1.metric("P5 (Bear)", f"${mc_stats['p5']:.0f}")
        mc2.metric("P25", f"${mc_stats['p25']:.0f}")
        mc3.metric("P50 (Median)", f"${mc_stats['p50']:.0f}")
        mc4.metric("P75", f"${mc_stats['p75']:.0f}")
        mc5.metric("P95 (Bull)", f"${mc_stats['p95']:.0f}")
        mc6.metric("Std Dev", f"${mc_stats['std']:.0f}")

        # Probability of upside
        mkt_price = f_mc.get("price") or 0
        if mkt_price:
            prob_up = (mc_stats["p50"] > mkt_price)
            pct_above = 100 * sum(
                1 for _ in range(200)
                if (run_dcf(f_mc,
                    max(np.random.normal(wacc, 0.5), 5),
                    max(np.random.normal(tgr, 0.25), 0.5),
                    max(np.random.normal(rev_cagr, 2.5), 0),
                    max(np.random.normal(fcf_margin, 2.0), 1)) or {}).get("intrinsic_price", 0) > mkt_price
            ) / 200

            st.markdown("---")
            col_a, col_b = st.columns(2)
            col_a.metric(
                "Current Market Price",
                f"${mkt_price:.2f}",
                delta=f"P50 upside: {((mc_stats['p50']-mkt_price)/mkt_price*100):+.1f}%"
            )
            col_b.metric(
                "Prob. Intrinsic > Market",
                f"{pct_above:.0f}%",
                delta="based on simulation"
            )
    else:
        st.warning("Insufficient data for Monte Carlo simulation on this ticker.")

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(f"""
<div style="text-align:center; font-family:'DM Mono',monospace; font-size:9px; color:{PALETTE['text_light']}; letter-spacing:0.15em; padding:12px 0;">
  SELL-SIDE LITE · INSTITUTIONAL RESEARCH PLATFORM · FOR INFORMATIONAL PURPOSES ONLY · NOT INVESTMENT ADVICE
  <br>DATA VIA YAHOO FINANCE · DCF ENGINE · EV/EBITDA COMPS · MONTE CARLO · SCENARIO ENGINEERING
</div>
""", unsafe_allow_html=True)
