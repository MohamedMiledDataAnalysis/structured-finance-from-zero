"""Chapter 22 - senior expenses of Thames Residential 2027-1:
annual budget at closing and the amount due on each of the
first four IPDs.
Run from the book folder:
  python3 ch22/python/ch22_senior_expenses.py \
      data/thames_performance_monthly.csv"""
import sys
from datetime import date
from decimal import Decimal as D, ROUND_HALF_UP
import pandas as pd

def r2(x):
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)

POOL = D("635671146.31")          # cut-off balance
FIXED = {"Trustee": D("25000"),
         "Paying agent and agent bank": D("10000"),
         "Corporate services": D("20000"),
         "Cash management": D("50000"),
         "Other issuer expenses": D("120000")}
SERV = D("0.0015")                # servicing fee p.a.
PROFIT = D("1000")                # issuer profit per IPD

def line(label, x):
    print(f"{label:<29}{x:>14,}")

serv_year = r2(POOL * SERV)
for k, v in FIXED.items():
    line(k, r2(v))
line("Servicing (0.15% of pool)", serv_year)
total = sum(FIXED.values()) + serv_year
print(f"{'Total senior expenses':<29}{total:>14,}"
      f"  {100 * total / POOL:.4f}% of pool")
line("Issuer profit (4 x 1,000)", r2(4 * PROFIT))
line("Total with issuer profit", total + 4 * PROFIT)

# ---- the first four IPDs ----
ipds = [date(2027, 3, 18), date(2027, 6, 15),
        date(2027, 9, 15), date(2027, 12, 15),
        date(2028, 3, 15)]           # closing date first
periods = [["2027-02", "2027-03", "2027-04", "2027-05"],
           ["2027-06", "2027-07", "2027-08"],
           ["2027-09", "2027-10", "2027-11"],
           ["2027-12", "2028-01", "2028-02"]]
perf = pd.read_csv(sys.argv[1], dtype=str)
opening = dict(zip(perf.collection_period,
                   perf.opening_balance))
print(f"\n{'IPD':<11}{'Days':>4}{'Fixed fees':>11}"
      f"{'Servicing':>12}{'Profit':>9}{'Total':>13}")
grand = D("0")
for i in range(4):
    days = (ipds[i + 1] - ipds[i]).days
    fixed = sum(r2(v * days / 365) for v in FIXED.values())
    serv = sum(r2(D(opening[p]) * SERV / 12)
               for p in periods[i])
    tot = fixed + serv + PROFIT
    grand += tot
    print(f"{ipds[i + 1].isoformat():<11}{days:>4}"
          f"{fixed:>11,}{serv:>12,}{r2(PROFIT):>9,}{tot:>13,}")
print(f"{'First year':<15}{'':>32}{grand:>13,}")
