"""Chapter 31 - scheduled (contractual) runoff of the Rhein Auto 2027-1 cut-off pool.
No prepayments, no defaults. Each loan amortises from its current_balance with its own
monthly_instalment; interest = round(balance x rate/1200, 2) each month (Excel ROUND
rule); the final month pays the remaining balance (the balloon, if any).
Month 1 = March 2027 (first collection period after the 28 Feb 2027 cut-off).
Run from the book folder:
  python3 tools/ch31_pool_runoff.py data/rhein_auto_2027_1_tape.csv data/ch31_rhein_scheduled_runoff.csv
"""
import sys
import numpy as np
import pandas as pd

def round2(x):
    return np.sign(x) * np.floor(np.abs(x) * 100 + 0.5 + 1e-9) / 100

tape = pd.read_csv(sys.argv[1])
bal = tape.current_balance.to_numpy(float)
r = tape.interest_rate.to_numpy(float) / 1200
pmt = tape.monthly_instalment.to_numpy(float)
rem = tape.remaining_term_months.to_numpy(int)
balloon = tape.balloon_amount.to_numpy(float)
rows = []
for m in range(1, rem.max() + 1):
    live = rem >= m
    opening = bal.sum()
    interest = np.where(live, round2(bal * r), 0.0)
    last = rem == m
    princ = np.where(live, round2(pmt - interest), 0.0)
    # final month: whole remaining balance is repaid
    princ = np.where(last, bal, princ)
    ball = np.where(last, np.minimum(balloon, bal), 0.0)
    bal = round2(bal - princ)
    rows.append(dict(month=m, opening=round(opening, 2),
                     interest=round(interest.sum(), 2),
                     regular_principal=round((princ - ball).sum(), 2),
                     balloon_principal=round(ball.sum(), 2),
                     closing=round(bal.sum(), 2)))
out = pd.DataFrame(rows)
out.to_csv(sys.argv[2], index=False, float_format="%.2f")
print(out.head(3).to_string(index=False))
print("months:", len(out), " balloons:", round(out.balloon_principal.sum(), 2),
      " total principal:", round(out.regular_principal.sum() + out.balloon_principal.sum(), 2))
