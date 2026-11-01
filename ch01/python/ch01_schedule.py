"""Chapter 1 - amortisation schedule for loan KBS-000417 (Thames Residential 2027-1).
Run from the book folder:
  python3 ch01/python/ch01_schedule.py data/thames_residential_2027_1_tape.csv"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

def round2(x):
    """Round to pennies as Excel's ROUND does
    (halves away from zero)."""
    return Decimal(x).quantize(Decimal("0.01"),
                               rounding=ROUND_HALF_UP)

def schedule(principal, annual_rate_pct, n_months):
    r = Decimal(str(annual_rate_pct)) / 1200   # monthly rate
    p = Decimal(str(principal))
    pmt = round2(p * r / (1 - (1 + r) ** -n_months))
    rows, bal = [], p
    for m in range(1, n_months + 1):
        interest = round2(bal * r)
        # the last payment clears the balance exactly
        pay = pmt if m < n_months else bal + interest
        princ = pay - interest
        rows.append((m, bal, pay, interest, princ,
                     bal - princ))
        bal = bal - princ
    return pd.DataFrame(rows, columns=[
        "month", "opening", "payment",
        "interest", "principal", "closing"])

tape = pd.read_csv(sys.argv[1])
loan = tape.loc[tape.loan_id == "KBS-000417"].iloc[0]
s = schedule(loan.original_balance, loan.current_rate, int(loan.original_term_months))
k = int(loan.payments_made)
print("Monthly payment      :", s.payment.iloc[0])
print("First month interest :", s.interest.iloc[0], " principal:", s.principal.iloc[0])
print("Balance after", k, "payments:", s.closing.iloc[k - 1])
print("  tape says:              ", f"{loan.current_balance:.2f}")
print("Final payment        :", s.payment.iloc[-1])
print("Total interest paid  :", s.interest.sum())
