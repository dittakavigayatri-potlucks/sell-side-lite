"""
dcf_model.py
============
Standalone DCF sensitivity analysis module.
Generates a WACC x Terminal Growth rate sensitivity table for a given ticker.
"""

import numpy as np
import pandas as pd
from screener import load_financials, dcf_valuation


def sensitivity_table(
    ticker: str,
    wacc_range: list  = None,
    tgr_range:  list  = None,
) -> pd.DataFrame:
    """
    Returns a DataFrame: rows = WACC, cols = Terminal Growth Rate.
    Each cell = implied DCF price per share.
    """
    if wacc_range is None:
        wacc_range = [0.07, 0.08, 0.09, 0.10, 0.11]
    if tgr_range is None:
        tgr_range  = [0.015, 0.020, 0.025, 0.030, 0.035]

    fin  = load_financials(ticker)
    rows = {}
    for wacc in wacc_range:
        row = {}
        for tgr in tgr_range:
            dcf = dcf_valuation(fin, wacc=wacc, terminal_growth=tgr)
            row[f"TGR={tgr:.1%}"] = round(dcf["Price_Per_Share"], 2)
        rows[f"WACC={wacc:.1%}"] = row

    df = pd.DataFrame(rows).T
    return df


if __name__ == "__main__":
    ticker = "HON"
    print(f"\nDCF Sensitivity Table for {ticker}")
    print("=" * 60)
    tbl = sensitivity_table(ticker)
    print(tbl.to_string())
    tbl.to_csv(f"outputs/{ticker}_dcf_sensitivity.csv")
    print(f"\nSaved to outputs/{ticker}_dcf_sensitivity.csv")
