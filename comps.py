"""
comps.py
========
Comparable company (EV/EBITDA, EV/EBIT, P/E) valuation module.
Builds a peer benchmarking table and generates buy/hold/sell based on
discount to peer median.
"""

import pandas as pd
import numpy as np
from screener import load_financials


PEER_MULTIPLES = {
    # Industrials sub-sector medians (illustrative; refresh from Bloomberg/FactSet)
    "Diversified Industrials": {"EV_EBITDA": 12.5, "EV_EBIT": 16.0, "PE": 22.0},
    "Aerospace & Defense":     {"EV_EBITDA": 14.0, "EV_EBIT": 18.5, "PE": 24.0},
    "Machinery":               {"EV_EBITDA": 11.0, "EV_EBIT": 14.5, "PE": 20.0},
    "Electrical Equipment":    {"EV_EBITDA": 13.5, "EV_EBIT": 17.0, "PE": 23.0},
}


def build_comps_table(tickers: list, subsector: str = "Diversified Industrials") -> pd.DataFrame:
    """
    For each ticker, compute LTM multiples and compare vs. peer medians.
    Returns full peer benchmarking DataFrame.
    """
    multiples = PEER_MULTIPLES.get(subsector, PEER_MULTIPLES["Diversified Industrials"])
    rows = []

    for ticker in tickers:
        fin   = load_financials(ticker)
        is_   = fin["income_statement"]
        meta  = fin["metadata"]

        ebitda_ltm = is_["EBITDA"].iloc[-1]
        ebit_ltm   = is_["EBIT"].iloc[-1]
        ni_ltm     = is_["Net_Income"].iloc[-1]

        # Approximate market cap (EV-based back-solve from assumed target price)
        ev_implied  = ebitda_ltm * multiples["EV_EBITDA"]
        mktcap      = ev_implied - meta["debt"]
        price_impl  = mktcap / meta["shares"] if meta["shares"] > 0 else np.nan

        ev_ebitda_ltm = ev_implied / ebitda_ltm if ebitda_ltm > 0 else np.nan
        ev_ebit_ltm   = ev_implied / ebit_ltm   if ebit_ltm   > 0 else np.nan
        pe_ltm        = mktcap    / ni_ltm       if ni_ltm     > 0 else np.nan

        rows.append({
            "Ticker":          ticker,
            "EBITDA_LTM_$M":   round(ebitda_ltm / 1e6, 1),
            "EBIT_LTM_$M":     round(ebit_ltm   / 1e6, 1),
            "NI_LTM_$M":       round(ni_ltm     / 1e6, 1),
            "EV_EBITDA":       round(ev_ebitda_ltm, 1),
            "EV_EBIT":         round(ev_ebit_ltm, 1),
            "P/E":             round(pe_ltm, 1),
            "Peer_EV_EBITDA":  multiples["EV_EBITDA"],
            "Prem_Disc_%":     round((ev_ebitda_ltm / multiples["EV_EBITDA"] - 1) * 100, 1),
            "Implied_Price":   round(price_impl, 2),
        })

    df = pd.DataFrame(rows).set_index("Ticker")
    # Highlight discount to peer
    df["Recommendation"] = df["Prem_Disc_%"].apply(
        lambda x: "BUY" if x < -10 else ("SELL" if x > 15 else "HOLD")
    )
    return df


if __name__ == "__main__":
    universe = ["GE", "HON", "MMM", "CAT", "DE", "ITW", "EMR"]
    print("Peer Comps Table (Diversified Industrials)\n" + "=" * 80)
    tbl = build_comps_table(universe)
    print(tbl.to_string())
    tbl.to_csv("outputs/comps_table.csv")
    print("\nSaved to outputs/comps_table.csv")
