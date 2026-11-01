"""Chapter 18 - Loan-level analysis of the Thames pool.
Applies the agency's criteria in this book (ILLUSTRATIVE)
loan by loan: foreclosure frequency (FF), loss severity (LS),
expected loss at six rating levels. Prints WAFF, WALS and EL, one worked
loan, and a comparison with Kingsbridge's history.

Run from the book folder:
  python3 ch18/python/ch18_loan_level.py \\
      data/thames_residential_2027_1_tape.csv \\
      data/ch18_regional_hpi.csv \\
      data/kingsbridge_static_pool_defaults.csv \\
      [data/ch18_rating_level_results.csv]
"""
import sys
import numpy as np
import pandas as pd

LEVELS = ["AAA", "AA", "A", "BBB", "BB", "B"]

# ---- the agency's criteria in this book (illustrative) ----
# base FF (%) by indexed current LTV band (lower bound, %)
FF_GRID = [(0, 1.0), (50, 1.5), (60, 2.1), (70, 2.8), (75, 3.6),
           (80, 4.5), (85, 5.6), (90, 7.0), (95, 9.0)]
LTI_ADJ = [(0, 1.00), (4.0, 1.10), (4.5, 1.25)]   # by LTI band
SEAS_ADJ = [(0, 1.00), (24, 0.95), (36, 0.90), (48, 0.85)]
SELF_EMP = 1.30
REPAY_ADJ = {"Repayment": 1.00, "Part and part": 1.20,
             "Interest-only": 1.40}
ARREARS_ADJ = {0: 1.00, 1: 2.00}   # by months in arrears
MULT = {"AAA": 8.51, "AA": 6.70, "A": 5.33, "BBB": 4.00,
        "BB": 2.50, "B": 1.00}
GROUP = {"London": 1, "South East": 2, "East of England": 2,
         "South West": 2, "East Midlands": 3,
         "West Midlands": 3,
         "Wales": 3, "Yorkshire and the Humber": 3,
         "North West": 4, "North East": 4, "Scotland": 4,
         "Northern Ireland": 5}
MVD_AAA = {1: 0.60, 2: 0.55, 3: 0.50, 4: 0.47, 5: 0.57}
MVD_SCALE = {"AAA": 1.00, "AA": 0.92, "A": 0.80, "BBB": 0.72,
             "BB": 0.57, "B": 0.40}
FSD_FLAT, FSD_HOUSE = 0.22, 0.17       # forced-sale discount
COST_FIXED, COST_PCT = 3000.0, 0.03    # foreclosure costs
SALE_MONTHS = {"Scotland": 24, "Northern Ireland": 30}
SALE_MONTHS_OTHER = 18
UP_CREDIT = 0.80                       # credit for HPI rises
INDEX_Q = "2026Q4"                     # latest index at cut-off


def band(x, grid):
    """Value of the band with the largest lower bound <= x."""
    out = grid[0][1]
    for lo, v in grid:
        if x >= lo:
            out = v
    return out


def quarter(d):
    return f"{d[:4]}Q{(int(d[5:7]) - 1) // 3 + 1}"


def loan_level(tape, hpi):
    t = tape.copy()
    h = hpi.set_index(["region", "quarter"])["hpi"]
    i0 = np.array([h[(r, quarter(d))] for r, d in
                   zip(t["region"], t["origination_date"])])
    i1 = np.array([h[(r, INDEX_Q)] for r in t["region"]])
    t["hpi_ratio"] = i1 / i0
    up = 1 + UP_CREDIT * (t["hpi_ratio"] - 1)
    t["indexed_value"] = t["original_valuation"] * np.where(
        t["hpi_ratio"] > 1, up, t["hpi_ratio"])
    bal = t["current_balance"]
    t["ltv_idx"] = 100 * bal / t["indexed_value"]
    t["lti"] = t["original_balance"] / t["gross_income"]
    t["base_ff"] = [band(x, FF_GRID) / 100
                    for x in t["ltv_idx"]]
    t["a_lti"] = [band(x, LTI_ADJ) for x in t["lti"]]
    t["a_seas"] = [band(x, SEAS_ADJ)
                   for x in t["payments_made"]]
    emp = t["employment_status"] == "Self-employed"
    t["a_emp"] = np.where(emp, SELF_EMP, 1.0)
    t["a_rep"] = t["repayment_type"].map(REPAY_ADJ)
    t["a_arr"] = t["months_in_arrears"].map(ARREARS_ADJ)
    t["adj"] = (t["a_lti"] * t["a_seas"] * t["a_emp"]
                * t["a_rep"] * t["a_arr"])
    t["fsd"] = np.where(t["property_type"] == "Flat",
                        FSD_FLAT, FSD_HOUSE)
    t["sale_m"] = t["region"].map(SALE_MONTHS).fillna(
        SALE_MONTHS_OTHER)
    t["accrued"] = (bal * t["current_rate"] / 100
                    * t["sale_m"] / 12)
    for k in LEVELS:
        ff = t["base_ff"] * t["adj"] * MULT[k]
        t[f"ff_{k}"] = np.minimum(1.0, ff)
        mvd = t["region"].map(GROUP).map(MVD_AAA) * MVD_SCALE[k]
        sale = t["indexed_value"] * (1 - mvd) * (1 - t["fsd"])
        cost = COST_FIXED + COST_PCT * sale
        loss = np.maximum(0.0, bal + t["accrued"] + cost - sale)
        t[f"ls_{k}"] = loss / bal
    return t


def summary(t):
    bal = t["current_balance"]
    rows = []
    for k in LEVELS:
        ff, ls = t[f"ff_{k}"], t[f"ls_{k}"]
        el_gbp = (bal * ff * ls).sum()
        rows.append((k, (bal * ff).sum() / bal.sum(),
                     el_gbp / (bal * ff).sum(),
                     el_gbp / bal.sum(), el_gbp))
    return pd.DataFrame(rows, columns=["level", "WAFF", "WALS",
                                       "EL", "EL_gbp"])


def history(s):
    """Lifetime results of vintages observed for 96+ months."""
    last = s.sort_values("months_since_origination")
    last = last.groupby("vintage").tail(1)
    m = last[last["months_since_origination"] >= 96]
    d = m["cumulative_default_pct"]
    n = m["cumulative_net_loss_pct"]
    return len(m), d.mean(), d.max(), n.mean(), (n / d).mean()


if __name__ == "__main__":
    t = loan_level(pd.read_csv(sys.argv[1]),
                   pd.read_csv(sys.argv[2]))
    bal = t["current_balance"]
    wa = lambda c: (t[c] * bal).sum() / bal.sum()
    print(f"Loans {len(t)}  pool {bal.sum():,.2f}")
    print(f"WA indexed LTV {wa('ltv_idx'):.2f}%  "
          f"WA base FF {100 * wa('base_ff'):.2f}%")
    print(f"WA adjustment factor {wa('adj'):.4f}")
    s = summary(t)
    print("Level  WAFF %  WALS %   EL %        EL (GBP)")
    for r in s.itertuples():
        print(f"{r.level:<5}{100 * r.WAFF:7.2f}{100 * r.WALS:8.2f}"
              f"{100 * r.EL:7.2f}{r.EL_gbp:16,.2f}")
    x = t[t["loan_id"] == "KBS-000417"].iloc[0]
    print(f"KBS-000417 indexed value {x.indexed_value:,.2f}")
    print(f"  LTV {x.ltv_idx:.2f}%  base FF {100 * x.base_ff:.2f}%"
          f"  adj {x.adj:.4f}")
    print(f"  AAA: FF {100 * x.ff_AAA:.2f}%  LS {100 * x.ls_AAA:.2f}%")
    print(f"  B:   FF {100 * x.ff_B:.2f}%  LS {100 * x.ls_B:.2f}%")
    n, dm, dx, nm, sv = history(pd.read_csv(sys.argv[3]))
    print(f"History, {n} vintages of 96+ months:")
    print(f"  default mean {dm:.2f}% max {dx:.2f}%")
    print(f"  net loss mean {nm:.2f}%  severity {100 * sv:.2f}%")
    if len(sys.argv) > 4:
        out = pd.DataFrame({
            "level": s["level"],
            "waff_pct": (100 * s["WAFF"]).round(2),
            "wals_pct": (100 * s["WALS"]).round(2),
            "el_pct": (100 * s["EL"]).round(2)})
        out.to_csv(sys.argv[4], index=False)
