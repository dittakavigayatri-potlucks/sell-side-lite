# ◈ Sell-Side Lite — Institutional Equity Research Platform

Hedge-fund grade equity screener with integrated DCF, EV/EBITDA comps, scenario engineering, and Monte Carlo simulation. Replicates sell-side research standards.

## Features

| Module | Capability |
|---|---|
| **Screener** | Live universe screening with BUY/HOLD/SELL ratings, composite scoring (0-11), sparklines |
| **Deep Dive** | Price history, MA overlays, volatility bands, full KPI dashboard per ticker |
| **EV/EBITDA Comps** | Bubble chart, comps table with premium/discount to sector median |
| **DCF Sensitivity** | WACC × Terminal Growth heatmap (EV and per-share price) |
| **Scenario Engine** | Bull/Base/Bear + custom scenarios, tornado chart, FCF projection comparison |
| **Monte Carlo** | 2,000–10,000 simulations, P5/P25/P50/P75/P95 distribution, probability of upside |

## Colour Palette
Soft institutional palette: Slate Blue · Powder Blue · Warm Cream · Sage Mint · Teal Slate

## Installation

```bash
pip install -r requirements.txt
```

## Run Locally

```bash
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this folder to a GitHub repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and set `app.py` as the entrypoint
4. Deploy — no API keys needed (uses Yahoo Finance)

## Deploy to Railway / Render / Fly.io

Add a `Procfile`:
```
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

## Usage

1. Enter tickers in the sidebar (comma or line-separated, e.g. `CAT, DE, HON, RTX, GE`)
2. Adjust DCF parameters: WACC, Terminal Growth Rate, Revenue CAGR, FCF Margin
3. Set macro overlays: ISM PMI, 10Y UST Yield, Industrial Capex Growth
4. Apply screens: minimum rating, max net leverage, min ROIC
5. Click **▶ RUN SCREEN** to refresh

## Data Source
Yahoo Finance via `yfinance`. For production use, replace `fetch_ticker_data()` with Bloomberg/FactSet API calls.

## Methodology

### 3-Statement Model
- Revenue → EBITDA → EBIT → Net Income
- FCF = Operating CF − Capex

### DCF Valuation
- 5-year explicit FCF projection (configurable 3–10 years)
- Gordon Growth terminal value
- WACC-based discounting
- Sensitivity table: WACC (6%–13%) × TGR (1.5%–3.5%)

### EV/EBITDA Comps
- LTM multiples vs universe median
- Premium/discount analysis
- Buy threshold: >10% discount · Sell threshold: >15% premium

### Rating Framework (0–11 composite)
- ROIC: 2pts (>15%), 1pt (>10%)
- Revenue Growth: 2pts (>10%), 1pt (>5%)
- Operating Margin: 2pts (>20%), 1pt (>12%)
- Net Leverage: 2pts (<1.5x), 1pt (<3x)
- DCF Upside: 2pts (>20%), 1pt (>5%)
- EV/EBITDA vs Peers: 1pt (>10% discount)
- **BUY ≥ 8 · HOLD ≥ 5 · SELL < 5**

### Monte Carlo
- Samples WACC ~ N(base, 0.5), TGR ~ N(base, 0.25), CAGR ~ N(base, 2.5), FCF Margin ~ N(base, 2.0)
- Returns P5/P25/P50/P75/P95 intrinsic price distribution

## Disclaimer
For informational purposes only. Not investment advice.
