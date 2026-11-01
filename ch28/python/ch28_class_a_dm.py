"""Chapter 28 - Thames Residential 2027-1 Class A: cash flows,
WAL, price and discount margin at different CPRs and spreads.
Run from the book folder:
  python3 ch28/python/ch28_class_a_dm.py \
      data/thames_performance_monthly.csv"""
import sys
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

def round2(x):
    return float(Decimal(repr(float(x))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP))

def mod_following(d):
    """Weekend adjustment, modified following."""
    a = d
    while a.weekday() >= 5:
        a += timedelta(days=1)
    if a.month != d.month:
        a = d
        while a.weekday() >= 5:
            a -= timedelta(days=1)
    return a

SETTLE = date(2027, 3, 18)        # closing date
CLASS_A = 553_000_000.00
SONIA = 0.0375                    # flat, illustrative
MARGIN = 0.0062
SCHED = 0.0020                    # scheduled amortisation
# Chapter 10 base case: defaults, timing, lag
DEFAULTS = 9_273_541.00           # lifetime, GBP
TIMING = [5.73, 11.07, 23.34, 28.88, 19.09,
          8.01, 2.70, 0.84, 0.26, 0.08]   # % by year
LAG = 18                          # months to recovery
DEF = [round2(DEFAULTS * TIMING[k // 12] / 1200)
       for k in range(120)]       # month 1 = Feb 2027

# IPDs: 15 Jun 2027 ... 15 Mar 2032 (first call date)
IPDS = [mod_following(date(y, m, 15))
        for y in range(2027, 2033) for m in (3, 6, 9, 12)
        if date(2027, 6, 1) < date(y, m, 15)
        <= date(2032, 3, 15)]

def pool_months(pool0, cpr):
    """Monthly pool run-off, Feb 2027 to Feb 2032.
    Notes receive scheduled + prepaid principal and,
    LAG months after a default, the defaulted amount
    (recovery plus the loss cured by excess spread)."""
    smm = 1 - (1 - cpr) ** (1 / 12)
    b, out = pool0, []
    for k in range(61):
        y, m = 2027 + (1 + k) // 12, (1 + k) % 12 + 1
        d = DEF[k]
        sched = round2((b - d) * SCHED)
        prep = round2((b - d - sched) * smm)
        back = DEF[k - LAG] if k >= LAG else 0.0
        out.append((y, m, sched + back, prep))
        b = round2(b - d - sched - prep)
    return out

def class_a_flows(pool0, cpr):
    months = pool_months(pool0, cpr)
    rows, bal, prev = [], CLASS_A, SETTLE
    for i, d in enumerate(IPDS):
        # collections: months before the IPD month
        lo = (2027, 2) if i == 0 else (
            IPDS[i - 1].year, IPDS[i - 1].month)
        coll = sum(s + p for (y, m, s, p) in months
                   if lo <= (y, m) < (d.year, d.month))
        days = (d - prev).days
        intr = round2(bal * (SONIA + MARGIN) * days / 365)
        princ = bal if d == IPDS[-1] else min(bal, round2(coll))
        rows.append(dict(ipd=d, days=days, opening=bal,
                         interest=intr, principal=princ))
        bal = round2(bal - princ)
        prev = d
    return pd.DataFrame(rows)

def price(cf, dm):
    df, pv = 1.0, 0.0
    for _, r in cf.iterrows():
        df /= 1 + (SONIA + dm) * r.days / 365
        pv += (r.interest + r.principal) * df
    return 100 * pv / CLASS_A

def wal(cf):
    t = [(d - SETTLE).days / 365 for d in cf.ipd]
    return (cf.principal * t).sum() / CLASS_A

def dm_from_price(cf, target):
    lo, hi = -0.02, 0.05              # bisection on DM
    for _ in range(100):
        mid = (lo + hi) / 2
        if price(cf, mid) > target:
            lo = mid
        else:
            hi = mid
    return mid

perf = pd.read_csv(sys.argv[1])
pool0 = perf.opening_balance.iloc[0]
print("Pool at cut-off      :", f"{pool0:,.2f}")
print("Scheduled amortisation: "
      f"{perf.scheduled_principal.iloc[0] / pool0:.4%}"
      " of balance (Feb 2027 actual)")
base = class_a_flows(pool0, 0.1115)
print("\nClass A at 11.15% CPR, first two IPDs (GBP)")
for _, r in base.head(2).iterrows():
    print(f"{r.ipd}  {r.days:3d}d  open {r.opening:>15,.2f}"
          f"  int {r.interest:>12,.2f}\n"
          f"{'':12s}principal {r.principal:>14,.2f}")
last = base.iloc[-1]
print(f"{last.ipd}  call: principal {last.principal:,.2f}")
print("\nCPR     WAL   price at DM 0.55% 0.62% 0.70% 0.80%")
for cpr in (0.05, 0.1115, 0.15, 0.20):
    cf = class_a_flows(pool0, cpr)
    p = [price(cf, dm) for dm in
         (0.0055, 0.0062, 0.0070, 0.0080)]
    print(f"{100 * cpr:5.2f}%  {wal(cf):5.2f}  " +
          "  ".join(f"{x:7.3f}" for x in p))
dm = dm_from_price(base, 99.80)
print(f"\nDM at price 99.80, 11.15% CPR: {dm * 100:.4f}%")
p1 = price(base, 0.0063)
print(f"Price change for +1bp DM : {p1 - 100:.4f}")
if len(sys.argv) > 2:                 # optional CPR in %
    c = float(sys.argv[2]) / 100
    cf = class_a_flows(pool0, c)
    p = [price(cf, dm) for dm in
         (0.0055, 0.0062, 0.0070, 0.0080)]
    print(f"\nCPR {c:.1%}: WAL {wal(cf):.2f}  prices " +
          "  ".join(f"{x:7.3f}" for x in p))
