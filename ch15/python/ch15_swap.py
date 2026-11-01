"""Chapter 15 - the Thames fixed-to-floating swap: legs,
compounded SONIA with observation shift, scheduled notional
against the actual fixed balance, basis risk and a simplified
valuation.
Run from the book folder:
  python3 ch15/python/ch15_swap.py \
      data/thames_residential_2027_1_tape.csv \
      data/thames_sonia_assumption.csv \
      data/ch15_sonia_daily_sample.csv \
      data/ch14_base_case.csv"""
import os
import sys
from datetime import date
import math
import pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "ch14",
                                "python"))
import cashflow as cf

FIXED = 3.30          # swap fixed rate, % p.a.
NOTES_AE = 626_100_000.00


def r2(x):
    """Round half away from zero to the penny, as Excel's
    ROUND and the R helper round2 do."""
    return math.copysign(math.floor(abs(x) * 100 + 0.5 + 1e-9)
                         / 100, x)


def money(x):
    return f"{r2(x):,.2f}"


def leg(notional, rate_pct, days):
    return r2(notional * rate_pct / 100 * days / 365)


def compounded(rates, weights, d):
    """SONIA compounded in arrears: product of daily factors."""
    f = 1.0
    for r, n in zip(rates, weights):
        f *= 1 + r / 100 * n / 365
    return (f - 1) * 365 / d * 100


tape, sonia_q, daily, base_p = sys.argv[1:5]
t = cf.load_tape(tape)
fx = t[t.product_type.str.contains("Fixed")]
wa = (fx.current_balance * fx.current_rate).sum() \
    / fx.current_balance.sum()
tr = t[t.product_type == "Tracker"]
sv = t[t.product_type == "SVR"]
print("Thames Residential 2027-1 - Chapter 15 swap")
print(f"Fixed-rate loans: {len(fx):,}  balance"
      f" {money(fx.current_balance.sum())}")
print(f"  weighted average fixed rate {wa:.4f}%")
print(f"Trackers: {len(tr)}  {money(tr.current_balance.sum())}"
      f"  SVR: {len(sv)}  {money(sv.current_balance.sum())}")

# --- first swap period ---------------------------------------
N0 = cf.fixed_sched_balance(t)
d1 = (cf.ipd_date(1) - cf.CLOSING).days
fl, fi = leg(N0[0], FIXED, d1), leg(N0[0], 3.75, d1)
print(f"\nFirst period 18 Mar 2027 - 15 Jun 2027 ({d1} days)")
print(f"  notional               {money(N0[0]):>16}")
print(f"  fixed leg, 3.30%       {money(fl):>16}  issuer pays")
print(f"  floating leg, 3.75%    {money(fi):>16}  issuer gets")
print(f"  net to issuer          {money(fi - fl):>16}")

# --- compounded SONIA, observation shift ----------------------
s = pd.read_csv(daily)
print("\nCompounded SONIA, illustrative daily rates")
d_obs = int(s.days.sum())
comp = compounded(s.sonia_pct, s.days, d_obs)
simple = (s.sonia_pct * s.days).sum() / d_obs
print(f"Days in observation period: {d_obs}")
print(f"Compounded rate: {comp:.5f}%   weighted average:"
      f" {simple:.5f}%")
ia = leg(553_000_000.00, round(comp, 5) + 0.62, 14)
print(f"Class A interest, 1-15 Jun 2027 (14 days): {money(ia)}")

# --- eight IPDs: scheduled notional vs actual fixed ----------
S = cf.sched_balance(t)
pool = cf.project_pool(S, **cf.load_base(base_p, S[0]))
q = pd.read_csv(sonia_q)
print("\nSwap on the first eight IPDs (SONIA assumption file)")
print("IPD       Days  SONIA        Notional     Net to issuer")
rows, prev = [], cf.CLOSING
for k in range(1, 9):
    m = 0 if k == 1 else 3 * k - 2      # start of collections
    dt = cf.ipd_date(k); days = (dt - prev).days; prev = dt
    son = q.compounded_sonia_pct[k - 1]
    net = leg(N0[m], son, days) - leg(N0[m], FIXED, days)
    actual = N0[m] * pool.balance[m] / S[m]
    rows.append((k, dt, days, N0[m], son, net, actual))
    print(f"{dt:%b %Y}  {days:>4}   {son:.2f}"
          f"  {money(N0[m]):>14}  {money(net):>16}")
print(f"Total net to issuer, 8 IPDs: "
      f"{money(sum(r[5] for r in rows))}")
print("\nActual fixed balance and excess notional (base case)")
print("IPD         Actual fixed  Excess notional")
for k, dt, days, n, son, net, act in rows:
    print(f"{dt:%b %Y}  {money(act):>14}  {money(n - act):>15}")
k, dt, days, n, son, net, act = rows[-1]
cost = leg(n - act, FIXED - 2.30, days)
print(f"SONIA 2.30% on {dt:%d %b %Y}: excess notional"
      f" costs {money(cost)}")

# --- basis risk ----------------------------------------------
unhedged = NOTES_AE - N0[0]
print("\nBasis risk (annual, illustrative)")
print(f"Notes on SONIA not matched by the swap:"
      f" {money(unhedged)}")
print(f"  SONIA +0.25%, Bank Rate unchanged: cost"
      f" {money(unhedged * 0.0025)}")
print(f"  SVR cut by 0.50%: lost income"
      f" {money(sv.current_balance.sum() * 0.005)}")

# --- simplified valuation of the swap -------------------------
print("\nSwap value to the issuer at closing if the market rate"
      " moves")
prev, sched = cf.CLOSING, []
for k in range(1, 40):
    m = 0 if k == 1 else 3 * k - 2
    if N0[m] <= 0:
        break
    dt = cf.ipd_date(k)
    sched.append(((dt - prev).days, (dt - cf.CLOSING).days,
                  N0[m]))
    prev = dt
print(f"Periods with a notional: {len(sched)} (last IPD"
      f" {cf.ipd_date(len(sched)):%b %Y})")
for mkt in (4.30, 2.30):
    v = sum(n * (mkt - FIXED) / 100 * d / 365
            / (1 + mkt / 100) ** (tt / 365)
            for d, tt, n in sched)
    who = "Northgate owes issuer" if v > 0 else \
        "issuer owes Northgate"
    print(f"  market {mkt:.2f}%: {money(v):>15}  {who}")
