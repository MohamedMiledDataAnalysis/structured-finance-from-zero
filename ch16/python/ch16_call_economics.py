"""Chapter 16 - call economics for Thames Residential 2027-1:
balances at the first optional redemption date, cost of the
step-up to the issuer, and the Class A investor's yield with
and without the call. Base case of Chapters 10 and 14; SONIA
flat 3.75% (illustrative).
Run from the book folder:
  python3 ch16/python/ch16_call_economics.py \
      data/thames_residential_2027_1_tape.csv \
      data/ch14_base_case.csv"""
import os
import sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "ch14",
                                "python"))
import cashflow as cf

SONIA = 3.75
MARGIN = {"A": 0.62, "B": 1.10, "C": 1.50, "D": 2.20, "E": 3.50}
STEP = {c: 2 * m for c, m in MARGIN.items()}  # margins double


def money(x):
    return f"{x:,.2f}"


def balances(notes):
    """Opening balance of each class on each IPD."""
    out = notes[["ipd", "date"]].copy()
    for c, amt in cf.CLASSES:
        out[c] = amt - notes[c].cumsum() + notes[c]
    return out


def xirr(flows):
    """Annual yield y with sum CF / (1+y)^(days/365) = 0."""
    d0 = flows[0][0]
    f = lambda y: sum(cf_ / (1 + y) ** ((d - d0).days / 365)
                      for d, cf_ in flows)
    lo, hi = -0.5, 1.0
    for _ in range(200):                 # bisection
        mid = (lo + hi) / 2
        if f(lo) * f(mid) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def class_a_flows(notes, price, call):
    bal = balances(notes)
    flows = [(cf.CLOSING, -553_000_000.00 * price / 100)]
    prev = cf.CLOSING
    for (_, n), (_, b) in zip(notes.iterrows(), bal.iterrows()):
        if b.A <= 0.005:
            break
        m = MARGIN["A"] if (call or n.ipd < cf.CALL_IPD) \
            else STEP["A"]
        days = (n.date - prev).days
        interest = b.A * (SONIA + m) / 100 * days / 365
        flows.append((n.date, interest + n.A))
        prev = n.date
    return flows


t = cf.load_tape(sys.argv[1])
S = cf.sched_balance(t)
pool = cf.project_pool(S, **cf.load_base(sys.argv[2], S[0]))
nc, wc = cf.project_notes(pool), cf.project_notes(pool, True)
bal = balances(nc)
k = cf.CALL_IPD - 1
print("Thames Residential 2027-1 - Chapter 16 call economics")
print("Base case (Chapter 10), SONIA flat 3.75%")
print(f"\nOn 15 Mar 2032 (IPD {cf.CALL_IPD}), before payments")
print("Class   Outstanding    Margin  Step-up  Extra a year")
after = {c: bal[c][k] - nc[c][k] for c, _ in cf.CLASSES}
extra_year = 0.0
for c, _ in cf.CLASSES:
    if c in MARGIN:
        x = after[c] * (STEP[c] - MARGIN[c]) / 100
        extra_year += x
        print(f"  {c}  {money(bal[c][k]):>16}  {MARGIN[c]:.2f}%"
              f"  {STEP[c]:.2f}%  {money(x):>12}")
    else:
        print(f"  {c}  {money(bal[c][k]):>16}  none")
tot = sum(bal[c][k] for c, _ in cf.CLASSES)
print(f"  Total {money(tot):>14}")
print("Principal collected for that IPD:",
      money(nc.available[k]))
print("If not called, outstanding after the IPD:"
      f" {money(sum(after.values()))}")
print(f"Step-up cost in the first year: {money(extra_year)}")
prev, total_extra = cf.ipd_date(cf.CALL_IPD), 0.0
for i in range(k + 1, len(nc)):
    d = nc.date[i]; days = (d - prev).days; prev = d
    total_extra += sum(bal[c][i] * (STEP[c] - MARGIN[c]) / 100
                       * days / 365 for c in MARGIN)
print(f"Extra interest if never called: {money(total_extra)}")

print("\nClass A yield (annual, Actual/365), SONIA flat 3.75%")
print("Price     With call   No call   Difference")
for price in (100.00, 99.75):
    yc = xirr(class_a_flows(wc, price, True)) * 100
    yn = xirr(class_a_flows(nc, price, False)) * 100
    print(f"{price:6.2f}   {yc:8.3f}%  {yn:7.3f}%"
          f"  {yn - yc:8.3f}%")

print("\nClean-up call threshold (10% of cut-off):"
      f" {money(0.1 * S[0])}")
