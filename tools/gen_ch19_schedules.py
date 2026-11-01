"""Chapter 19 input: scheduled (zero-prepayment, zero-default) balances of
the Thames pool at the end of each quarterly collection period, the
scheduled balance of loans still in their fixed-rate period (the swap
notional schedule) and the weighted average fixed rate of those loans.
Repayment loans amortise at their current rate and payment; interest-only
loans repay at maturity; part-and-part loans are split 50/50.
Run: python3 tools/gen_ch19_schedules.py \
        data/thames_residential_2027_1_tape.csv data/ch19_thames_schedules.csv"""
import sys
import numpy as np
import pandas as pd

t = pd.read_csv(sys.argv[1])
NM = 456                                   # months Feb 2027 .. Jan 2065
n = t["remaining_term_months"].to_numpy()
bal0 = t["current_balance"].to_numpy()
r = t["current_rate"].to_numpy() / 1200
io_share = t["repayment_type"].map({"Repayment": 0.0, "Interest-only": 1.0,
                                    "Part and part": 0.5}).to_numpy()
B = np.zeros((NM + 1, len(t)))
B[0] = bal0
am = bal0 * (1 - io_share)                 # amortising part
pmt = am * r / (1 - (1 + r) ** -n)
for m in range(1, NM + 1):
    # amortising part: annuity balance after m payments
    k = np.minimum(m, n)
    am_bal = am * (1 + r) ** k - pmt * ((1 + r) ** k - 1) / r
    am_bal = np.where(m >= n, 0.0, np.maximum(am_bal, 0.0))
    io_bal = np.where(m >= n, 0.0, bal0 * io_share)
    B[m] = am_bal + io_bal
# month m ends on the last day of month (Jan 2027 = month 0)
fx_end = pd.to_datetime(t["fixed_rate_end_date"])
fx_months = ((fx_end.dt.year - 2027) * 12 + fx_end.dt.month - 1).to_numpy()
fx_months = np.where(t["fixed_rate_end_date"].isna(), -1, fx_months)
rows = []
for p in range(0, 152):
    m = 0 if p == 0 else 4 + 3 * (p - 1)
    m = min(m, NM)
    infix = fx_months > m                   # still fixed at end of month m
    fb = B[m][infix].sum()
    wac = (B[m][infix] * t["current_rate"].to_numpy()[infix]).sum() / fb if fb > 0 else 0.0
    rows.append(dict(period=p, month_end=m, sched_balance=round(B[m].sum(), 2),
                     sched_fixed_balance=round(fb, 2), fixed_wac_pct=round(wac, 4)))
pd.DataFrame(rows).to_csv(sys.argv[2], index=False)
print(pd.DataFrame(rows).head(12).to_string(index=False))
