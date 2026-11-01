"""Chapter 9 - eligibility criteria, pool cut and stratification
tables for Thames Residential 2027-1.
Run from the book folder:
  python3 ch09/python/ch09_pool_selection.py \
      data/ch09_thames_provisional_pool.csv
Writes ch09/python/ch09_strats_py.csv (all strat tables)."""
import sys
import pandas as pd

pool = pd.read_csv(sys.argv[1])
pool["cents"] = (pool.current_balance * 100).round().astype(int)
pool["oltv"] = pool.original_balance / pool.original_valuation
pool["cltv"] = pool.current_balance / pool.original_valuation

UK = ["London", "South East", "East of England", "South West",
      "West Midlands", "East Midlands",
      "Yorkshire and the Humber", "North West", "North East",
      "Wales", "Scotland", "Northern Ireland"]
PRODUCTS = ["2Y Fixed", "5Y Fixed", "Tracker", "SVR"]

# Eligibility criteria in the order of the mortgage sale agreement
CRITERIA = [
    ("E1 Property in the UK", lambda d: d.region.isin(UK)),
    ("E2 Owner-occupied", lambda d: d.occupancy == "Owner-occupied"),
    ("E3 Not shared ownership", lambda d: d.shared_ownership == "N"),
    ("E4 Permitted product", lambda d: d.product_type.isin(PRODUCTS)),
    ("E5 Original LTV <= 95%", lambda d: d.oltv <= 0.95),
    ("E6 Balance 25k to 1m", lambda d: d.current_balance.between(
        25000, 1000000)),
    ("E7 Term <= 420 months", lambda d: d.original_term_months <= 420),
    ("E8 One payment made", lambda d: d.payments_made >= 1),
    ("E9 Arrears <= 1 month", lambda d: d.months_in_arrears <= 1),
    ("E10 No forbearance", lambda d: d.forbearance_flag == "N"),
    ("E11 No further advance", lambda d:
        d.further_advance_pending == "N"),
]

def money(c):
    return f"{c / 100:,.2f}"

def pct(a, b):
    """Percentage to 2 dp, halves rounded up (Excel ROUND)."""
    from decimal import Decimal, ROUND_HALF_UP
    q = Decimal(int(a)) * 100 / Decimal(int(b))
    return q.quantize(Decimal("0.01"), ROUND_HALF_UP)

# ---- 1. Failures (a loan can fail several criteria) and the
#         pool cut: criteria applied in order (removal waterfall)
tests = pd.DataFrame({n: f(pool) for n, f in CRITERIA})
pool["eligible"] = tests.all(axis=1)
print(f"Provisional pool: {len(pool):,} loans, "
      f"GBP {money(pool.cents.sum())}")
print(f"  {'Criterion':<24}{'Fail':>5}{'Out':>5}"
      f"{'Balance out':>15}{'Left':>6}")
left = pool.copy()
for n, f in CRITERIA:
    keep = f(left)
    out = left[~keep]
    left = left[keep]
    print(f"  {n:<24}{(~tests[n]).sum():>5}{len(out):>5}"
          f"{money(out.cents.sum()):>15}{len(left):>6}")
final = pool[pool.eligible].copy()
tot, n = final.cents.sum(), len(final)
print(f"Final pool: {n:,} loans, GBP {money(tot)}")

# ---- 3. Stratification tables
ORDER = {}
def band(x, edges, labels):
    """label of the band (lower, upper]; first band (-inf, e1]."""
    ORDER[tuple(labels)] = labels
    return pd.cut(x, [-1e18] + edges, labels=labels).astype(str)

final["bal_band"] = band(final.current_balance,
    [1e5, 2e5, 3e5, 4e5, 5e5, 7.5e5, 1e6],
    ["0-100k", "100k-200k", "200k-300k", "300k-400k",
     "400k-500k", "500k-750k", "750k-1,000k"])
LTV_E = [.5, .6, .7, .75, .8, .85, .9, .95]
LTV_L = ["<=50%", "50-60%", "60-70%", "70-75%", "75-80%",
         "80-85%", "85-90%", "90-95%"]
final["oltv_band"] = band(final.oltv, LTV_E, LTV_L)
final["cltv_band"] = band(final.cltv, LTV_E, LTV_L)
final["rate_band"] = band(final.current_rate,
    [3.5, 4.0, 4.5, 5.0, 5.5, 99],
    ["<=3.50%", "3.50-4.00%", "4.00-4.50%", "4.50-5.00%",
     "5.00-5.50%", ">5.50%"])
final["season_band"] = band(final.payments_made,
    [12, 24, 36, 48, 60],
    ["0-12m", "12-24m", "24-36m", "36-48m", "48-60m"])
final["rem_band"] = band(final.remaining_term_months,
    [180, 240, 300, 360, 420],
    ["<=15y", "15-20y", "20-25y", "25-30y", "30-35y"])
final["arrears"] = final.months_in_arrears.astype(str)

STRATS = [("Current balance", "bal_band"),
          ("Original LTV", "oltv_band"),
          ("Current LTV", "cltv_band"), ("Region", "region"),
          ("Product type", "product_type"),
          ("Interest rate", "rate_band"),
          ("Seasoning", "season_band"),
          ("Remaining term", "rem_band"),
          ("Repayment type", "repayment_type"),
          ("Employment", "employment_status"),
          ("First-time buyer", "first_time_buyer"),
          ("Months in arrears", "arrears")]
KEYS = {"region": UK, "product_type": PRODUCTS,
        "repayment_type": ["Repayment", "Interest-only",
                           "Part and part"],
        "employment_status": ["Employed", "Self-employed",
                              "Retired"],
        "first_time_buyer": ["Y", "N"], "arrears": ["0", "1"]}
for labels in ORDER.values():
    for col in final.columns:
        if final[col].isin(labels).all() and col not in KEYS:
            KEYS[col] = labels
rows = []
for title, col in STRATS:
    g = final.groupby(col).cents.agg(["count", "sum"])
    keys = KEYS[col]
    for k in keys:
        if k in g.index:
            c, s = g.loc[k]
            rows.append((title, k, int(c), pct(c, n),
                         f"{s / 100:.2f}", pct(s, tot)))
strats = pd.DataFrame(rows, columns=["table", "band", "loans",
    "pct_loans", "balance", "pct_balance"])
strats.to_csv("ch09/python/ch09_strats_py.csv", index=False)

# ---- 4. Weighted averages and concentration
def wa(x):
    return (x * final.cents).sum() / tot

top10 = final.cents.nlargest(10).sum()
lon = final.loc[final.region == "London", "cents"].sum()
summ = pd.DataFrame([
    ("Average balance (GBP)", f"{tot / n / 100:.2f}"),
    ("Largest loan (GBP)", f"{final.cents.max() / 100:.2f}"),
    ("WA original LTV (%)", f"{100 * wa(final.oltv):.2f}"),
    ("WA current LTV (%)", f"{100 * wa(final.cltv):.2f}"),
    ("WA interest rate (%)", f"{wa(final.current_rate):.2f}"),
    ("WA seasoning (months)", f"{wa(final.payments_made):.2f}"),
    ("WA remaining term (months)",
     f"{wa(final.remaining_term_months):.2f}"),
    ("Top 10 loans (GBP)", f"{top10 / 100:.2f}"),
    ("Top 10 loans (% pool)", f"{pct(top10, tot)}"),
    ("London (% pool)", f"{pct(lon, tot)}")],
    columns=["measure", "value"])
summ.to_csv("ch09/python/ch09_summary_py.csv", index=False)
print(f"WA current LTV {summ.value[3]}%, "
      f"top 10 loans {summ.value[8]}%")
print(f"Written: {len(summ)} summary rows, "
      f"{len(strats)} strat rows")
