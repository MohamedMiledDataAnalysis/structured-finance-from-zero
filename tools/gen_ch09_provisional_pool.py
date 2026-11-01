"""Chapter 9: Kingsbridge provisional pool for Thames Residential 2027-1.
= the 3,000 loans of the final tape + 181 extra loans that each fail at least
one documented eligibility criterion. Applying the criteria returns exactly the
final tape (3,000 loans, GBP 635,671,146.31).
Seed 20261109. Run from the book folder:
    python3 tools/gen_ch09_provisional_pool.py data/thames_residential_2027_1_tape.csv data/ch09_thames_provisional_pool.csv
"""
import sys, csv
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import numpy as np

TAPE, OUT = sys.argv[1], sys.argv[2]
rng = np.random.default_rng(20261109)
CUT = date(2027, 1, 31)
C = Decimal("0.01")
def r2(x): return Decimal(x).quantize(C, ROUND_HALF_UP)
def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    return date(d.year + y, mo + 1, min(d.day, 28))
def payment(P, annual, n):
    r = Decimal(annual) / Decimal(1200); f = (1 + r) ** n
    return r2(P * r * f / (f - 1))
def balance_after(P, annual, n, k):
    r = Decimal(annual) / Decimal(1200); pmt = payment(P, annual, n); b = P
    for _ in range(k):
        b = b - (pmt - r2(b * r))
    return r2(b), pmt

with open(TAPE) as f:
    tape = list(csv.DictReader(f))
FIELDS = list(tape[0].keys())
EXTRA = ["shared_ownership", "forbearance_flag", "further_advance_pending"]
for r in tape:
    for e in EXTRA: r[e] = "N"

regions = ["London","South East","East of England","South West","West Midlands","East Midlands",
           "Yorkshire and the Humber","North West","North East","Wales","Scotland","Northern Ireland"]
rw = np.array([16,18,11,10,8,7,7,9,3,4,5,2], float); rw /= rw.sum()

def make(i, *, occupancy="Owner-occupied", prod=None, ltv=None, P=None, term=None,
         orig=None, arrears=0, so="N", fb="N", fa="N", region=None, rep="Repayment"):
    prod = prod or str(rng.choice(["2Y Fixed","5Y Fixed","Tracker","SVR"], p=[.40,.45,.10,.05]))
    if orig is None:
        orig = add_months(date(2022,2,1), int(rng.integers(0,57)))
        orig = date(orig.year, orig.month, int(rng.integers(1,29)))
    region = region or str(rng.choice(regions, p=rw))
    term = term or int(rng.choice([240,300,360], p=[.25,.45,.30]))
    if ltv is None: ltv = float(np.clip(rng.beta(6,3)*0.95, 0.35, 0.90))
    if P is None:
        value = int(round(rng.lognormal(np.log(260000),0.30)/1000))*1000
        P = Decimal(int(round(value*ltv/500))*500)
    else:
        value = int(round(float(P)/ltv/1000))*1000
    if prod == "2Y Fixed": rate = round(rng.normal(4.45,0.30),2); end = add_months(orig,24)
    elif prod == "5Y Fixed": rate = round(rng.normal(4.20,0.35),2); end = add_months(orig,60)
    elif prod in ("Tracker","Offset"):
        margin = round(rng.normal(0.80,0.25),2); rate = round(3.75+margin,2); end = None
    else: rate = 7.49; end = None
    k = 0
    while add_months(orig,k+1) <= CUT: k += 1
    if rep == "Interest-only":
        bal = r2(P); pmt = r2(P*Decimal(str(rate))/1200)
    else:
        bal, pmt = balance_after(P, Decimal(str(rate)), term, k)
    income = int(round(float(P)/rng.uniform(3.0,4.6)/100))*100
    return dict(loan_id=f"KBS-{i:06d}", origination_date=orig.isoformat(),
        first_payment_date=add_months(orig,1).isoformat(), payments_made=k,
        original_balance=f"{P:.2f}", current_balance=f"{bal:.2f}", monthly_payment=f"{pmt:.2f}",
        original_term_months=term, remaining_term_months=term-k, repayment_type=rep,
        product_type=prod, current_rate=f"{rate:.2f}",
        fixed_rate_end_date=end.isoformat() if end else "",
        tracker_margin=f"{margin:.2f}" if prod in ("Tracker","Offset") else "",
        original_valuation=value, region=region,
        property_type=str(rng.choice(["Detached","Semi-detached","Terraced","Flat","Bungalow"],p=[.24,.30,.26,.15,.05])),
        occupancy=occupancy, first_time_buyer=str(rng.choice(["Y","N"],p=[.28,.72])),
        borrower_count=int(rng.choice([1,2],p=[.45,.55])),
        employment_status=str(rng.choice(["Employed","Self-employed","Retired"],p=[.82,.15,.03])),
        gross_income=income, months_in_arrears=arrears, cut_off_date=CUT.isoformat(),
        shared_ownership=so, forbearance_flag=fb, further_advance_pending=fa)

extra = []; i = 3001
def add(n, **kw):
    global i
    for _ in range(n):
        k2 = {key: (v() if callable(v) else v) for key, v in kw.items()}
        extra.append(make(i, **k2)); i += 1

jan27 = lambda: date(2027, 1, int(rng.integers(1,29)))
arr = lambda: int(rng.choice([2,3,4,6], p=[.45,.30,.15,.10]))
add(38, occupancy="Buy-to-let", rep=lambda: str(rng.choice(["Interest-only","Repayment"],p=[.7,.3])))
add(3,  occupancy="Buy-to-let", arrears=arr)                         # fails E2 and E9
add(17, so="Y", ltv=lambda: float(rng.uniform(0.55,0.75)))
add(22, prod="Offset")
add(1,  prod="Offset", ltv=0.97)                                     # fails E4 and E5
add(9,  ltv=lambda: float(rng.uniform(0.955,1.0)))
add(13, P=lambda: Decimal(int(rng.integers(30,49))*500), term=180,
        orig=lambda: date(2022, int(rng.integers(2,13)), int(rng.integers(1,29))),
        ltv=lambda: float(rng.uniform(0.10,0.20)))                   # small balance
add(4,  P=lambda: Decimal(int(rng.integers(2110,2800))*500), region="London",
        ltv=lambda: float(rng.uniform(0.55,0.70)))                   # large balance
add(11, term=480)
add(16, orig=jan27)                                                  # no payment yet
add(22, arrears=arr)
add(5,  arrears=arr, fb="Y")                                         # fails E9 and E10
add(12, fb="Y")
add(8,  fa="Y")

rows = tape + extra
rows.sort(key=lambda r: r["loan_id"])
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS + EXTRA); w.writeheader(); w.writerows(rows)
print(len(rows), "loans;", len(extra), "extra")
