"""Chapter 37 - coverage tests of Calder Park CLO 1 DAC.
Run from the book folder:
  python3 ch37/python/ch37_clo_tests.py \\
      data/ch37_clo_portfolio.csv data/ch37_clo_notes.csv"""
import sys
from decimal import Decimal as D, ROUND_HALF_UP, ROUND_CEILING
import pandas as pd

# ---- inputs (same as the yellow cells of the workbook) ----
PRINCIPAL_CASH = D("8150000.00")  # uninvested principal
CCC_LIMIT = D("0.075")            # 7.5% of performing par
EURIBOR = D("0.0225")             # 3M EURIBOR, illustrative
DAYS = 90                         # 15 Jan to 15 Apr 2027
SENIOR_EXP = D("60000.00")        # trustee, admin, agents
MGMT_FEE = D("0.0015")            # senior fee, p.a.
TARGET_PAR = D("400000000.00")    # fee base

def r2(x):
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)

def pct(x):
    return f"{(x * 100).quantize(D('0.01'), ROUND_HALF_UP)}%"

pf = pd.read_csv(sys.argv[1])
nt = pd.read_csv(sys.argv[2])
pf["par"] = [D(f"{v:.2f}") for v in pf.par_eur]
pf["px"] = [D(f"{v:.2f}") for v in pf.market_price_pct]
perf = pf[pf.defaulted == "N"]
dflt = pf[pf.defaulted == "Y"]

# 1. performing par and the CCC bucket
perf_par = sum(perf.par)
ccc = perf[perf.rating.str.startswith("CCC")]
ccc = ccc.sort_values("market_price_pct")
ccc_par = sum(ccc.par)
excess = max(D(0), ccc_par - r2(CCC_LIMIT * perf_par))

# 2. excess CCC carried at market value:
#    the lowest-priced CCC assets form the excess
haircut, left = D(0), excess
for par, px in zip(ccc.par, ccc.px):
    part = min(par, left)
    haircut += part - r2(part * px / 100)
    left -= part

# 3. defaulted assets at lower of price and recovery rate
dflt_cv = sum(r2(p * min(px, D(f"{rr:.2f}")) / 100)
              for p, px, rr in zip(dflt.par, dflt.px,
                                   dflt.recovery_rate_pct))

acpa = perf_par - haircut + dflt_cv + PRINCIPAL_CASH

# 4. interest proceeds for the period (Actual/360)
yf = D(DAYS) / D(360)
int_proc = sum(r2(p * (EURIBOR + D(int(s)) / 10000) * yf)
               for p, s in zip(perf.par, perf.spread_bps))
fee = r2(TARGET_PAR * MGMT_FEE * yf)
ic_num = int_proc - SENIOR_EXP - fee

print("Performing par            :", perf_par)
print("CCC par                   :", ccc_par,
      f"({pct(ccc_par / perf_par)} of performing)")
print("CCC limit (7.5%)          :", r2(CCC_LIMIT * perf_par))
print("CCC excess                :", excess)
print("CCC excess haircut        :", haircut)
print("Defaulted par             :", sum(dflt.par))
print("Defaulted carrying value  :", dflt_cv)
print("Principal cash            :", PRINCIPAL_CASH)
print("Adjusted collateral (ACPA):", acpa)
print("Interest proceeds         :", int_proc)
print("Senior expenses and fee   :", SENIOR_EXP + fee)

print("\nTest       Ratio    Trigger  Result")
notes = nt[nt["class"] != "Subordinated"]
cum_bal, cum_int, fails = D(0), D(0), []
for _, n in notes.iterrows():
    bal = D(int(n.balance_eur))
    cum_bal += bal
    cum_int += r2(bal * (EURIBOR + D(str(n.margin_pct)) / 100)
                  * yf)
    lab = "A/B" if n["class"] == "B" else n["class"]
    if n["class"] == "A":
        continue
    oc = acpa / cum_bal
    trig = D(str(n.oc_trigger_pct)) / 100
    res = "PASS" if oc >= trig else "FAIL"
    print(f"OC {lab:<5} {pct(oc):>8} {pct(trig):>8}  {res}")
    if res == "FAIL":
        fails.append((lab, cum_bal, trig, cum_int))
    if not pd.isna(n.ic_trigger_pct):
        ic = ic_num / cum_int
        t = D(str(n.ic_trigger_pct)) / 100
        res = "PASS" if ic >= t else "FAIL"
        print(f"IC {lab:<5} {pct(ic):>8} {pct(t):>8}  {res}")

for lab, s, trig, ci in fails:
    cure = (s - acpa / trig).quantize(D("0.01"), ROUND_CEILING)
    left_int = int_proc - SENIOR_EXP - fee - ci
    print(f"\nClass {lab} OC cure (redeem Class A):", cure)
    print("Interest left after Class", lab, "interest:",
          left_int)
    print("Amount diverted           :", min(cure, left_int))
