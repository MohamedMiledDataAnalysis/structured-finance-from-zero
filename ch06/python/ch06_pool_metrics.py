"""Chapter 6 - LTV, LTI and weighted averages on the
Thames Residential 2027-1 tape.
Run from the book folder:
  python3 ch06/python/ch06_pool_metrics.py \
      data/thames_residential_2027_1_tape.csv"""
import sys
import pandas as pd

t = pd.read_csv(sys.argv[1])

# 1. Loan-level ratios (LTV in %, LTI as a multiple)
t["oltv"] = 100 * t.original_balance / t.original_valuation
t["cltv"] = 100 * t.current_balance / t.original_valuation
t["lti"] = t.original_balance / t.gross_income

# 2. Weighted average: the weights are current balances
def wa(col):
    w = t.current_balance
    return (t[col] * w).sum() / w.sum()

bal = t.current_balance.sum()
print(f"Thames tape: {len(t)} loans, balance {bal:.2f}")

ex = t.loc[t.loan_id == "KBS-000417"].iloc[0]
print("Loan KBS-000417")
print(f"  original LTV (%)  {ex.oltv:10.2f}")
print(f"  current LTV (%)   {ex.cltv:10.2f}")
print(f"  LTI               {ex.lti:10.2f}")

print("Pool averages            weighted   simple")
rows = [("original LTV (%)", "oltv"),
        ("current LTV (%)", "cltv"),
        ("interest rate (%)", "current_rate"),
        ("seasoning (months)", "payments_made"),
        ("remaining term (m)", "remaining_term_months"),
        ("LTI", "lti")]
for label, col in rows:
    print(f"  {label:<21}{wa(col):9.2f}"
          f"{t[col].mean():9.2f}")

# 3. High LTI loans (FPC threshold: LTI of 4.5 or more)
hi = t[t.lti >= 4.5]
hb = hi.current_balance.sum()
print(f"LTI >= 4.5: {len(hi)} loans, "
      f"{100 * len(hi) / len(t):.2f}% of loans")
print(f"  balance {hb:.2f}, {100 * hb / bal:.2f}% of pool")

# 4. Fixed-rate loans whose fixed period ends
#    within 12 months of the cut-off date
rev = t[t.fixed_rate_end_date.notna()
        & (t.fixed_rate_end_date <= "2028-01-31")]
print(f"Fixed loans reverting by 2028-01-31: {len(rev)}")
print(f"  balance {rev.current_balance.sum():.2f}")
