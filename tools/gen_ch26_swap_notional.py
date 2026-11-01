"""Chapter 26: Thames swap notional schedule (annexed to the swap confirmation at closing).
Notional for the interest period ending on IPD k = scheduled balance of the loans that were
fixed-rate at the cut-off date and whose fixed period has not ended on the notional calculation
date (cut-off date for IPD 1, otherwise the last day of the collection periods of IPD k-1),
amortised by contractual monthly payments only (no prepayments, no defaults):
  principal due = monthly_payment - ROUND(balance x rate / 12, 2), floored at 0, capped at balance.
Run from the book folder:  python3 tools/gen_ch26_swap_notional.py data
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd
D = sys.argv[1]
C = Decimal("0.01")
def r2(x): return Decimal(x).quantize(C, rounding=ROUND_HALF_UP)
t = pd.read_csv(f"{D}/thames_residential_2027_1_tape.csv", dtype=str)
fx = t[t.product_type.str.contains("Fixed")].copy()
ipds = ["2027-06-15","2027-09-15","2027-12-15","2028-03-15","2028-06-15","2028-09-15","2028-12-15","2029-03-15"]
calc = ["2027-01-31","2027-05-31","2027-08-31","2027-11-30","2028-02-29","2028-05-31","2028-08-31","2028-11-30"]
npay = [0, 4, 7, 10, 13, 16, 19, 22]
bal = {r.loan_id: Decimal(r.current_balance) for r in fx.itertuples()}
rate = {r.loan_id: Decimal(r.current_rate) / 1200 for r in fx.itertuples()}
pmt = {r.loan_id: Decimal(r.monthly_payment) for r in fx.itertuples()}
fend = dict(zip(fx.loan_id, fx.fixed_rate_end_date))
rows, done = [], 0
for k in range(8):
    while done < npay[k]:
        for lid in bal:
            due = pmt[lid] - r2(bal[lid] * rate[lid])
            due = min(max(due, Decimal(0)), bal[lid])
            bal[lid] -= due
        done += 1
    live = [lid for lid in bal if fend[lid] > calc[k]]
    rows.append(dict(ipd=ipds[k], notional_calculation_date=calc[k], scheduled_payments=npay[k],
                     fixed_loans_in_notional=len(live), swap_notional=str(sum(bal[l] for l in live))))
out = pd.DataFrame(rows)
out.to_csv(f"{D}/ch26_thames_swap_notional.csv", index=False)
print(out.to_string(index=False))
