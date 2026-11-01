"""Generate the two reproducible synthetic loan tapes for Book 1.
Seed: 20261031. Run: python3 gen_data.py <outdir>"""
import sys, csv
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import numpy as np

OUT = sys.argv[1]
rng = np.random.default_rng(20261031)
C = Decimal("0.01")

def r2(x): return Decimal(x).quantize(C, ROUND_HALF_UP)

def add_months(d, m):
    y, mo = divmod(d.month - 1 + m, 12)
    return date(d.year + y, mo + 1, min(d.day, 28))

def payment(P, annual, n, fv=Decimal(0)):
    r = Decimal(annual) / Decimal(1200)
    if r == 0: return r2((P - fv) / n)
    f = (1 + r) ** n
    return r2((P * r * f - fv * r) / (f - 1))

def balance_after(P, annual, n, k, fv=Decimal(0), io=False):
    """Balance after k payments with monthly rounding (Excel ROUND convention)."""
    if io: return r2(P)
    r = Decimal(annual) / Decimal(1200)
    pmt = payment(P, annual, n, fv); b = P
    for _ in range(k):
        i = r2(b * r); b = b - (pmt - i)
    return r2(b), pmt

# ---------------- Thames Residential 2027-1 (UK prime RMBS) ----------------
CUT = date(2027, 1, 31)
regions = ["London","South East","East of England","South West","West Midlands","East Midlands",
           "Yorkshire and the Humber","North West","North East","Wales","Scotland","Northern Ireland"]
rw = np.array([16,18,11,10,8,7,7,9,3,4,5,2], float); rw /= rw.sum()
hpi = dict(zip(regions,[1.0]*12))
ptypes = ["Detached","Semi-detached","Terraced","Flat","Bungalow"]; pw=[.24,.30,.26,.15,.05]
rows = []
for i in range(1, 3001):
    lid = f"KBS-{i:06d}"
    prod = rng.choice(["2Y Fixed","5Y Fixed","Tracker","SVR"], p=[.40,.45,.10,.05])
    if prod == "2Y Fixed":
        orig = add_months(date(2025,2,1), int(rng.integers(0,22)))
    else:
        orig = add_months(date(2022,2,1), int(rng.integers(0,53)))
    orig = date(orig.year, orig.month, int(rng.integers(1,29)))
    region = rng.choice(regions, p=rw)
    val_mult = {"London":2.0,"South East":1.45,"East of England":1.3}.get(region,1.0)
    value = int(round(rng.lognormal(np.log(260000*val_mult),0.35)/1000))*1000
    ltv = float(np.clip(rng.beta(6,3)*0.95, 0.30, 0.95))
    P = Decimal(int(round(value*ltv/500))*500)
    term = int(rng.choice([180,240,300,360,420], p=[.08,.17,.40,.28,.07]))
    rep = rng.choice(["Repayment","Interest-only","Part and part"], p=[.92,.06,.02])
    if prod == "2Y Fixed": rate = round(rng.normal(4.45,0.30),2); end = add_months(orig,24)
    elif prod == "5Y Fixed": rate = round(rng.normal(4.20,0.35),2); end = add_months(orig,60)
    elif prod == "Tracker": margin = round(rng.normal(0.80,0.25),2); rate=None; end=None
    else: rate = 7.49; end=None
    if prod == "Tracker": base=3.75; rate = round(base+margin,2)
    trk = f"{margin:.2f}" if prod=="Tracker" else ""
    first = add_months(orig,1); k = 0
    while add_months(orig,k+1) <= CUT: k += 1
    if rep == "Interest-only":
        bal = r2(P); pmt = r2(P*Decimal(str(rate))/1200)
    elif rep == "Part and part":
        half = r2(P/2); b, pm = balance_after(half, Decimal(str(rate)), term, k)
        bal = r2(b + half); pmt = r2(pm + r2(half*Decimal(str(rate))/1200))
    else:
        bal, pmt = balance_after(P, Decimal(str(rate)), term, k)
    emp = rng.choice(["Employed","Self-employed","Retired"], p=[.82,.15,.03])
    income = int(round(float(P)/rng.uniform(3.0,4.6)/100))*100
    arr = int(rng.choice([0,1,2,3,4,6], p=[.965,.017,.008,.005,.003,.002])); arr = arr if arr <= 1 else 0  # eligibility: max 1 month in arrears at cut-off
    rows.append(dict(loan_id=lid, origination_date=orig.isoformat(), first_payment_date=first.isoformat(),
        payments_made=k, original_balance=f"{P:.2f}", current_balance=f"{bal:.2f}", monthly_payment=f"{pmt:.2f}",
        original_term_months=term, remaining_term_months=term-k, repayment_type=rep, product_type=prod,
        current_rate=f"{rate:.2f}", fixed_rate_end_date=end.isoformat() if end else "",
        tracker_margin=trk, original_valuation=value, region=region,
        property_type=rng.choice(ptypes,p=pw), occupancy="Owner-occupied",
        first_time_buyer=rng.choice(["Y","N"],p=[.28,.72]), borrower_count=int(rng.choice([1,2],p=[.45,.55])),
        employment_status=emp, gross_income=income, months_in_arrears=arr, cut_off_date=CUT.isoformat()))

# Worked-example loan used in Chapter 1 (fixed attributes, documented in the book)
ex = next(r for r in rows if r["loan_id"]=="KBS-000417")
orig = date(2023,3,15); P = Decimal("185000"); rate = Decimal("4.29"); term = 300
k = 0
while add_months(orig,k+1) <= CUT: k += 1
bal, pmt = balance_after(P, rate, term, k)
ex.update(origination_date=orig.isoformat(), first_payment_date=add_months(orig,1).isoformat(), payments_made=k,
    original_balance="185000.00", current_balance=f"{bal:.2f}", monthly_payment=f"{pmt:.2f}",
    original_term_months=term, remaining_term_months=term-k, repayment_type="Repayment", product_type="5Y Fixed",
    current_rate="4.29", fixed_rate_end_date=add_months(orig,60).isoformat(), tracker_margin="",
    original_valuation=245000, region="South West", property_type="Semi-detached", months_in_arrears=0,
    gross_income=52000, employment_status="Employed")

with open(f"{OUT}/thames_residential_2027_1_tape.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)

# ---------------- Rhein Auto 2027-1 (German auto loan ABS) ----------------
CUT2 = date(2027, 2, 28)
states = ["Nordrhein-Westfalen","Bayern","Baden-Württemberg","Niedersachsen","Hessen","Sachsen","Rheinland-Pfalz",
          "Berlin","Schleswig-Holstein","Brandenburg","Sachsen-Anhalt","Thüringen","Hamburg",
          "Mecklenburg-Vorpommern","Saarland","Bremen"]
sw = np.array([21.5,15.9,13.4,9.6,7.6,4.9,4.9,4.4,3.5,3.0,2.6,2.5,2.3,1.9,1.2,0.8]); sw/=sw.sum()
rows2 = []
for i in range(1, 30001):
    cond = rng.choice(["New","Used"], p=[.58,.42])
    fuel = rng.choice(["Petrol","Diesel","Hybrid","Electric"], p=[.38,.22,.24,.16])
    price = int(round(rng.lognormal(np.log(38000 if cond=="New" else 22000),0.35)/100))*100
    down = int(round(price*rng.uniform(0.0,0.30)/100))*100
    P = Decimal(price-down)
    term = int(rng.choice([24,36,48,60,72], p=[.08,.30,.30,.24,.08]))
    balloon = rng.random() < .45
    bamt = Decimal(int(round(price*rng.uniform(0.30,0.45)*(36/term if term>36 else 1)/100))*100) if balloon else Decimal(0)
    bamt = min(bamt, r2(P*Decimal("0.6")))
    rate = Decimal(str(round(float(np.clip(rng.normal(5.6 if cond=="Used" else 4.4, 0.9),0.99,9.9)),2)))
    orig = add_months(date(2023,3,1), int(rng.integers(0,46))); orig = date(orig.year,orig.month,int(rng.integers(1,29)))
    k = 0
    while add_months(orig,k+1) <= CUT2 and k < term: k += 1
    if k >= term: k = term-1
    bal, pmt = balance_after(P, rate, term, k, fv=bamt)
    rows2.append(dict(loan_id=f"RA-{i:06d}", origination_date=orig.isoformat(), vehicle_condition=cond, fuel_type=fuel,
        vehicle_price=price, down_payment=down, original_balance=f"{P:.2f}", interest_rate=f"{rate:.2f}",
        original_term_months=term, balloon="Y" if balloon else "N", balloon_amount=f"{bamt:.2f}",
        monthly_instalment=f"{pmt:.2f}", payments_made=k, current_balance=f"{bal:.2f}",
        remaining_term_months=term-k, borrower_type=rng.choice(["Private","Commercial"],p=[.86,.14]),
        federal_state=rng.choice(states,p=sw),
        months_in_arrears=(lambda a: a if a <= 1 else 0)(int(rng.choice([0,1,2,3,4],p=[.972,.015,.007,.004,.002]))), cut_off_date=CUT2.isoformat()))
with open(f"{OUT}/rhein_auto_2027_1_tape.csv","w",newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows2[0].keys())); w.writeheader(); w.writerows(rows2)
print("ok", ex["payments_made"], ex["monthly_payment"], ex["current_balance"])
