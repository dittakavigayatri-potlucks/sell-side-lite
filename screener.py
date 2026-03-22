"""
Industrial Sector Equity Screening & Valuation Model
=====================================================
Screens and values industrials-sector equities using:
  - 3-statement financial modeling (P&L, Balance Sheet, Cash Flow)
  - DCF valuation
  - EV/EBITDA comparable company analysis
  - Macro drivers: capex trends, PMI data, rate-cycle indicators

Author: Naga Siva Gayatri Dittakavi
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------------
# 1. DATA LAYER
# ---------------------------------------------------------------------------

def load_financials(ticker: str) -> dict:
    """
    Load or simulate 3-statement financials for a given ticker.
    In production: replace with Bloomberg/FactSet API pull or Excel ingestion.
    Returns dict with keys: income_statement, balance_sheet, cash_flow (DataFrames, 5yr history).
    """
    np.random.seed(hash(ticker) % (2**31))
    years = [2019, 2020, 2021, 2022, 2023]

    # --- Income Statement ---
    revenue_base = np.random.uniform(2e9, 20e9)
    revenue_growth = np.array([1.0, 0.92, 1.08, 1.12, 1.06])
    revenue = revenue_base * revenue_growth.cumprod()

    cogs_pct      = np.random.uniform(0.55, 0.70)
    sga_pct       = np.random.uniform(0.08, 0.14)
    da_pct        = np.random.uniform(0.03, 0.06)
    interest_rate = np.random.uniform(0.03, 0.06)
    tax_rate      = 0.21

    gross_profit  = revenue * (1 - cogs_pct)
    ebitda        = gross_profit - revenue * sga_pct
    da            = revenue * da_pct
    ebit          = ebitda - da
    debt_base     = revenue_base * np.random.uniform(1.5, 3.0)
    interest_exp  = debt_base * interest_rate
    ebt           = ebit - interest_exp
    net_income    = ebt * (1 - tax_rate)

    income_stmt = pd.DataFrame({
        "Year":        years,
        "Revenue":     revenue,
        "COGS":        revenue * cogs_pct,
        "Gross_Profit":gross_profit,
        "SGA":         revenue * sga_pct,
        "EBITDA":      ebitda,
        "DA":          da,
        "EBIT":        ebit,
        "Interest_Exp":interest_exp,
        "EBT":         ebt,
        "Net_Income":  net_income,
    }).set_index("Year")

    # --- Balance Sheet ---
    total_assets    = revenue * np.random.uniform(1.2, 2.0)
    current_assets  = total_assets * 0.35
    ppe_net         = total_assets * 0.40
    other_assets    = total_assets - current_assets - ppe_net
    total_debt      = np.full(5, debt_base) * np.linspace(1.0, 0.85, 5)
    equity          = total_assets - total_debt - total_assets * 0.15

    balance_sheet = pd.DataFrame({
        "Year":           years,
        "Current_Assets": current_assets,
        "PPE_Net":        ppe_net,
        "Other_Assets":   other_assets,
        "Total_Assets":   total_assets,
        "Total_Debt":     total_debt,
        "Equity":         equity,
    }).set_index("Year")

    # --- Cash Flow Statement ---
    capex     = revenue * np.random.uniform(0.04, 0.09)
    nwc_chg   = revenue * 0.02 * np.random.choice([-1, 1], 5)
    fcf       = net_income + da - capex - nwc_chg

    cash_flow = pd.DataFrame({
        "Year":        years,
        "Net_Income":  net_income,
        "DA":          da,
        "Capex":       capex,
        "NWC_Change":  nwc_chg,
        "FCF":         fcf,
    }).set_index("Year")

    return {
        "income_statement": income_stmt,
        "balance_sheet":    balance_sheet,
        "cash_flow":        cash_flow,
        "metadata": {
            "ticker":   ticker,
            "tax_rate": tax_rate,
            "debt":     float(total_debt[-1]),
            "shares":   float(revenue_base / np.random.uniform(20, 60)),
        }
    }


def load_macro_indicators() -> pd.DataFrame:
    """
    Simulated macro drivers: ISM PMI, 10yr yield, industrial capex growth.
    In production: pull from FRED, Bloomberg, or proprietary sources.
    """
    np.random.seed(42)
    months = pd.date_range("2019-01", "2023-12", freq="MS")
    return pd.DataFrame({
        "Date":          months,
        "ISM_PMI":       50 + np.cumsum(np.random.randn(len(months)) * 1.5),
        "UST_10Y":       2.5 + np.cumsum(np.random.randn(len(months)) * 0.08),
        "Capex_Growth":  np.random.randn(len(months)) * 0.03,
    }).set_index("Date")


# ---------------------------------------------------------------------------
# 2. VALUATION ENGINE
# ---------------------------------------------------------------------------

def dcf_valuation(
    financials: dict,
    wacc: float = 0.09,
    terminal_growth: float = 0.025,
    projection_years: int = 5,
    revenue_growth_fwd: float = 0.06,
    fcf_margin_fwd: float = None,
) -> dict:
    """
    5-year DCF with Gordon Growth terminal value.
    Returns: intrinsic equity value per share, bridge components.
    """
    cf      = financials["cash_flow"]
    meta    = financials["metadata"]
    is_     = financials["income_statement"]

    base_rev = is_["Revenue"].iloc[-1]
    if fcf_margin_fwd is None:
        fcf_margin_fwd = float((cf["FCF"] / is_["Revenue"]).mean())

    projected_fcf = []
    for t in range(1, projection_years + 1):
        rev_t = base_rev * ((1 + revenue_growth_fwd) ** t)
        fcf_t = rev_t * fcf_margin_fwd
        projected_fcf.append(fcf_t / ((1 + wacc) ** t))

    pv_fcf      = sum(projected_fcf)
    terminal_fcf = projected_fcf[-1] * (1 + wacc) ** projection_years  # unlevel
    terminal_fcf = (base_rev * ((1 + revenue_growth_fwd) ** projection_years)
                    * fcf_margin_fwd * (1 + terminal_growth))
    terminal_pv  = (terminal_fcf / (wacc - terminal_growth)) / ((1 + wacc) ** projection_years)

    enterprise_value = pv_fcf + terminal_pv
    equity_value     = enterprise_value - meta["debt"]
    price_per_share  = equity_value / meta["shares"] if meta["shares"] > 0 else np.nan

    return {
        "EV_DCF":          enterprise_value,
        "Equity_Value":    equity_value,
        "Price_Per_Share": price_per_share,
        "PV_FCF":          pv_fcf,
        "Terminal_PV":     terminal_pv,
        "WACC":            wacc,
        "Terminal_Growth": terminal_growth,
    }


def ev_ebitda_comps(
    financials: dict,
    sector_multiples: dict = None,
) -> dict:
    """
    EV/EBITDA comparable company valuation.
    Uses sector median multiple; override with custom peer set.
    """
    if sector_multiples is None:
        # Industrials sector median EV/EBITDA range: 10x-14x
        sector_multiples = {"low": 10.0, "median": 12.5, "high": 14.5}

    ebitda_ltm = financials["income_statement"]["EBITDA"].iloc[-1]
    meta       = financials["metadata"]

    results = {}
    for label, mult in sector_multiples.items():
        ev    = ebitda_ltm * mult
        eq    = ev - meta["debt"]
        pps   = eq / meta["shares"] if meta["shares"] > 0 else np.nan
        results[f"EV_{label}"] = ev
        results[f"Price_{label}"] = pps

    results["EBITDA_LTM"] = ebitda_ltm
    results["Multiples"]  = sector_multiples
    return results


# ---------------------------------------------------------------------------
# 3. SCREENING & RATING
# ---------------------------------------------------------------------------

def compute_screening_metrics(financials: dict, macro: pd.DataFrame) -> dict:
    """
    Compute key screening ratios: ROIC, FCF yield, leverage, momentum.
    """
    is_  = financials["income_statement"]
    bs   = financials["balance_sheet"]
    cf   = financials["cash_flow"]
    meta = financials["metadata"]

    invested_capital = bs["Total_Debt"] + bs["Equity"]
    nopat            = is_["EBIT"] * (1 - meta["tax_rate"])
    roic             = (nopat / invested_capital).mean()

    revenue_cagr = (is_["Revenue"].iloc[-1] / is_["Revenue"].iloc[0]) ** (1/4) - 1
    ebitda_margin = (is_["EBITDA"] / is_["Revenue"]).mean()
    fcf_yield     = (cf["FCF"].iloc[-1] / (meta["debt"] * 1.2))  # approx EV proxy
    leverage      = meta["debt"] / is_["EBITDA"].iloc[-1]

    # Macro overlay: PMI expansion flag
    pmi_latest     = macro["ISM_PMI"].iloc[-1]
    pmi_expanding  = pmi_latest > 50

    return {
        "ROIC":           roic,
        "Revenue_CAGR":   revenue_cagr,
        "EBITDA_Margin":  ebitda_margin,
        "FCF_Yield":      fcf_yield,
        "Net_Leverage":   leverage,
        "PMI_Expanding":  pmi_expanding,
        "PMI_Latest":     pmi_latest,
    }


RATING_THRESHOLDS = {
    "buy":  {"ROIC": 0.12, "Revenue_CAGR": 0.05, "EBITDA_Margin": 0.14, "Net_Leverage": 3.0},
    "hold": {"ROIC": 0.08, "Revenue_CAGR": 0.02, "EBITDA_Margin": 0.10, "Net_Leverage": 4.5},
}

def assign_rating(metrics: dict, dcf: dict, comps: dict) -> str:
    score = 0

    if metrics["ROIC"]          >= RATING_THRESHOLDS["buy"]["ROIC"]:          score += 2
    elif metrics["ROIC"]        >= RATING_THRESHOLDS["hold"]["ROIC"]:         score += 1

    if metrics["Revenue_CAGR"]  >= RATING_THRESHOLDS["buy"]["Revenue_CAGR"]:  score += 2
    elif metrics["Revenue_CAGR"]>= RATING_THRESHOLDS["hold"]["Revenue_CAGR"]: score += 1

    if metrics["EBITDA_Margin"] >= RATING_THRESHOLDS["buy"]["EBITDA_Margin"]: score += 2
    elif metrics["EBITDA_Margin"]>= RATING_THRESHOLDS["hold"]["EBITDA_Margin"]:score += 1

    if metrics["Net_Leverage"]  <= RATING_THRESHOLDS["buy"]["Net_Leverage"]:  score += 2
    elif metrics["Net_Leverage"]<= RATING_THRESHOLDS["hold"]["Net_Leverage"]: score += 1

    if metrics["PMI_Expanding"]:                                               score += 1

    if   score >= 8: return "BUY"
    elif score >= 5: return "HOLD"
    else:            return "SELL"


# ---------------------------------------------------------------------------
# 4. REPORT GENERATION
# ---------------------------------------------------------------------------

def run_full_screen(tickers: list, wacc: float = 0.09) -> pd.DataFrame:
    macro = load_macro_indicators()
    rows  = []

    for ticker in tickers:
        fin     = load_financials(ticker)
        dcf     = dcf_valuation(fin, wacc=wacc)
        comps   = ev_ebitda_comps(fin)
        metrics = compute_screening_metrics(fin, macro)
        rating  = assign_rating(metrics, dcf, comps)

        rows.append({
            "Ticker":         ticker,
            "Rating":         rating,
            "DCF_Price":      round(dcf["Price_Per_Share"], 2),
            "Comps_Low":      round(comps["Price_low"], 2),
            "Comps_Median":   round(comps["Price_median"], 2),
            "Comps_High":     round(comps["Price_high"], 2),
            "EBITDA_LTM_$M":  round(comps["EBITDA_LTM"] / 1e6, 1),
            "ROIC_%":         round(metrics["ROIC"] * 100, 1),
            "Rev_CAGR_%":     round(metrics["Revenue_CAGR"] * 100, 1),
            "EBITDA_Mgn_%":   round(metrics["EBITDA_Margin"] * 100, 1),
            "Net_Lev_x":      round(metrics["Net_Leverage"], 2),
            "PMI_Expanding":  metrics["PMI_Expanding"],
            "WACC_%":         round(wacc * 100, 1),
        })

    df = pd.DataFrame(rows).set_index("Ticker")
    df = df.sort_values("Rating", key=lambda x: x.map({"BUY": 0, "HOLD": 1, "SELL": 2}))
    return df


# ---------------------------------------------------------------------------
# 5. ENTRY POINT
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    INDUSTRIALS_UNIVERSE = [
        "GE", "HON", "MMM", "CAT", "DE", "ITW", "EMR", "PH",
        "ROK", "XYL", "GNRC", "CARR", "OTIS", "TXT", "HII"
    ]

    print("Running Industrial Sector Equity Screener...\n")
    results = run_full_screen(INDUSTRIALS_UNIVERSE, wacc=0.09)

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 160)
    print(results.to_string())

    results.to_csv("outputs/screening_results.csv")
    print("\nResults saved to outputs/screening_results.csv")
