# Industrial Sector Equity Screening & Valuation Model

Screens and values industrials-sector equities using integrated 3-statement financial modeling, DCF valuation, and EV/EBITDA comparable company analysis. Macro drivers — capex trends, PMI data, and rate-cycle indicators — are incorporated as forecast overlays. Output replicates sell-side research report standards.

## Structure

```
industrial_equity_screener/
├── screener.py        # Core: data loading, DCF, comps, screening metrics, rating
├── dcf_model.py       # DCF sensitivity table (WACC x terminal growth)
├── comps.py           # Peer benchmarking and EV/EBITDA comps table
├── outputs/           # CSV exports (auto-generated)
├── data/              # Raw financials / macro data 
├── notebooks/         # Exploratory analysis notebooks
└── requirements.txt
```

## Methodology

### 3-Statement Model
- P&L: Revenue → EBITDA → EBIT → Net Income
- Balance Sheet: PPE, current assets, debt, equity
- Cash Flow: Net income + D&A − Capex − NWC changes = FCF

### DCF Valuation
- 5-year explicit FCF projection using forward revenue growth and FCF margin assumptions
- Gordon Growth terminal value
- WACC-based discounting
- Sensitivity table: WACC (7%–11%) × Terminal Growth (1.5%–3.5%)

### EV/EBITDA Comps
- LTM multiples vs. sub-sector peer medians
- Premium/discount to peer median
- Buy/hold/sell thresholds: >10% discount → BUY, >15% premium → SELL

### Macro Overlay
- ISM Manufacturing PMI (expansion/contraction flag)
- 10-year UST yield (rate-cycle indicator)
- Industrial capex growth rate

### Rating Framework
Scores ROIC, revenue CAGR, EBITDA margin, net leverage, and PMI regime. BUY ≥ 8/11, HOLD ≥ 5/11, SELL otherwise.

## Usage

```python
# Run full screen on industrials universe
python screener.py

# DCF sensitivity for a single name
python dcf_model.py

# Build peer comps table
python comps.py
```

## Configuration

Replace simulated data in `load_financials()` and `load_macro_indicators()` with live Bloomberg/FactSet pulls or Excel ingestion via `openpyxl`. WACC and sector multiples are parameterized and easily overridden.

## Requirements

```
numpy
pandas
openpyxl
```

## Notes

Data in this repo is synthetically generated for demonstration. In production, financials should be sourced from Bloomberg Terminal, FactSet, or SEC EDGAR filings. Macro indicators from FRED API or Bloomberg.
