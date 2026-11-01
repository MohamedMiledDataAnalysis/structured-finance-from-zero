"""Chapter 14 - Thames Residential 2027-1 cash-flow model:
pool projection, sequential principal waterfall, WAL and
expected maturity, call and no call. Base case from Chapter 10.
Run from the book folder:
  python3 ch14/python/ch14_cashflow_model.py \
      data/thames_residential_2027_1_tape.csv \
      data/ch14_base_case.csv"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cashflow as cf

CPRS = [0, 5, 10, 15, 20, 25]


def money(x):
    return f"{x:,.2f}"


t = cf.load_tape(sys.argv[1])
S = cf.sched_balance(t)
base = cf.load_base(sys.argv[2], S[0])
print("Thames Residential 2027-1 - Chapter 14 cash-flow model")
print("Pool at cut-off:", money(S[0]))
print("Scheduled balance after 60 months:", money(S[60]))
print(f"Base case: CPR {base['cpr']:.2f}%, severity"
      f" {base['sev']:.2f}%, lag {base['lag']} months")
print(f"SMM {100 * cf.smm(base['cpr']):.4f}%")
pool = cf.project_pool(S, **base)
m1 = pool.iloc[1]
print("Month 1 (Feb 2027)")
for lab, v in [("opening balance", pool.balance[0]),
               ("defaults", m1.defaults),
               ("scheduled principal", m1.scheduled),
               ("prepayments", m1.prepaid),
               ("closing balance", m1.balance)]:
    print(f"  {lab:<22}{money(v):>18}")
print("Lifetime defaults:", money(pool.defaults.sum()),
      " losses:", money(pool.losses.sum()))
n = cf.project_notes(pool)
print(f"IPD 1 (15 Jun 2027): principal {money(n.available[0])}")
wb_c = cf.wal_and_maturity(cf.project_notes(pool, True))
wb_n = cf.wal_and_maturity(n)
print(f"Base case Class A WAL: {wb_c['A'][0]:.2f} with call,"
      f" {wb_n['A'][0]:.2f} without")
print(f"Base case Class A maturity, no call: {wb_n['A'][1]:%b %Y}")
print("Base case B-Z WAL, no call:",
      *(f"{wb_n[c][0]:.2f}" for c in "BCDEZ"))
m = pool[pool.balance < 0.1 * S[0]].month.iloc[0]
print(f"Pool below 10% of cut-off: month {m}, IPD"
      f" {cf.ipd_date(cf.ipd_of_month(m)):%b %Y}")

res = {}
for cpr in CPRS:
    p = cf.project_pool(S, **{**base, "cpr": cpr})
    for call in (True, False):
        res[cpr, call] = cf.wal_and_maturity(
            cf.project_notes(p, call))
print("\nClass A: WAL (years) and expected maturity")
print("CPR   WAL call  Maturity  WAL no call  Maturity")
for cpr in CPRS:
    wc, mc = res[cpr, True]["A"]
    wn, mn = res[cpr, False]["A"]
    print(f"{cpr:>2}%  {wc:>8.2f}  {mc:%b %Y}  {wn:>11.2f}"
          f"  {mn:%b %Y}")
print("\nClasses B-Z: WAL (years), no call")
print("CPR       B       C       D       E       Z")
for cpr in CPRS:
    print(f"{cpr:>2}%" + "".join(f"{res[cpr, False][c][0]:>8.2f}"
                                for c in "BCDEZ"))
print("\nClasses B-Z: expected maturity, no call")
print("CPR       B         C         D         E         Z")
for cpr in CPRS:
    print(f"{cpr:>2}%" + "".join(
        f"  {res[cpr, False][c][1]:%b %Y}" for c in "BCDEZ"))
wbz = {f"{res[c, True][k][0]:.2f}" for c in CPRS for k in "BCDEZ"}
print("With call, Classes B-Z WAL at every CPR:", *wbz)

print("\nBase case WAL, no call: loan level versus rep lines")
t["pool"] = "all"
t["term_bucket"] = (t.n // 60) * 5
for lab, keys in [("loan level", None), ("1 rep line", ["pool"]),
                  ("15 lines: type x 5-yr term",
                   ["repayment_type", "term_bucket"])]:
    s = S if keys is None else cf.sched_balance(
        cf.rep_lines(t, keys))
    w = cf.wal_and_maturity(cf.project_notes(
        cf.project_pool(s, **base)))
    print(f"  {lab:<28}A {w['A'][0]:.2f}  Z {w['Z'][0]:.2f}")
