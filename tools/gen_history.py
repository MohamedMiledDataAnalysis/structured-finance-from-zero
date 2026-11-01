"""Historical performance data supplied by the originators (Chapter 10 onwards). Seed 20261101.
Run: python3 gen_history.py <outdir>"""
import sys, csv
import numpy as np
OUT = sys.argv[1]; rng = np.random.default_rng(20261101)
def logistic(t, mid, k): return 1/(1+np.exp(-(t-mid)/k))

# ---- Kingsbridge: quarterly static pools 2016Q1-2025Q4, observed to Dec 2026 (month index from origination)
rows=[]
for y in range(2016,2026):
    for q in range(1,5):
        vint=f"{y}Q{q}"; orig_m = (y-2016)*12 + (q-1)*3          # months since Jan 2016
        age_max = (2026-2016)*12 + 11 - orig_m - 1                 # observed through Dec 2026
        vol = round(float(rng.uniform(380,620))*1e6, -5)
        life = 0.012 + (0.010 if y in (2022,2023) else 0) + (0.004 if y==2020 else 0) + rng.normal(0,0.0015)
        sev = float(np.clip(rng.normal(0.16 if y not in (2022,2023) else 0.19, 0.02), 0.08, 0.30))
        norm = logistic(120,40,10)
        for age in range(3, age_max+1, 3):
            cd = life*logistic(age,40,10)/norm
            cl = life*sev*logistic(age-18,40,10)/norm if age>18 else 0
            rec = cd*(1-sev)*min(1,max(0,(age-6)/24))
            rows.append(dict(vintage=vint, originated_balance=int(vol), months_since_origination=age,
                cumulative_default_pct=round(100*cd,4), cumulative_recovery_pct=round(100*min(rec,cd),4),
                cumulative_net_loss_pct=round(100*cl,4)))
with open(f"{OUT}/kingsbridge_static_pool_defaults.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

# ---- Kingsbridge: monthly dynamic book data Jan 2016-Dec 2026
rows=[]; bal=4.2e9
for i in range(132):
    y,m = 2016+i//12, i%12+1
    shock = 1.35 if (2023<=y<=2024) else (1.15 if y==2020 and m>=4 else 1.0)
    cpr = float(np.clip(rng.normal(11.0,1.2) + (3.0 if m in (3,9) else 0) - (2.5 if 2023<=y<=2024 else 0),4,25))
    a1 = round(float(rng.normal(0.95,0.05)*shock),3); a3 = round(float(rng.normal(0.42,0.03)*shock),3)
    a6 = round(float(rng.normal(0.25,0.02)*shock),3); a12 = round(float(rng.normal(0.18,0.02)*shock),3)
    new = float(rng.uniform(140,210))*1e6
    bal = bal*(1-cpr/100)**(1/12) - bal*0.0028 + new
    rows.append(dict(month=f"{y}-{m:02d}", book_balance=round(bal,-3), cpr_annualised_pct=round(cpr,2),
        arrears_1_3m_pct=a1, arrears_3_6m_pct=a3, arrears_6_12m_pct=a6, arrears_12m_plus_pct=a12,
        repossessions_in_month=int(rng.poisson(9*shock))))
with open(f"{OUT}/kingsbridge_dynamic_book.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

# ---- Rheinwagen Bank: monthly static pools Jan 2019 - Dec 2026, observed to Jan 2027
rows=[]
for i in range(96):
    y,m = 2019+i//12, i%12+1; vint=f"{y}-{m:02d}"
    age_max = 96 - i
    vol = round(float(rng.uniform(55,95))*1e6,-5)
    gl = 0.0105 + (0.003 if y in (2022,2023) else 0) + rng.normal(0,0.0012)
    recr = float(np.clip(rng.normal(0.55,0.05),0.35,0.70))
    norm = logistic(72,18,6)
    for age in range(1, age_max+1):
        cg = gl*logistic(age,18,6)/norm
        cr = cg*recr*min(1,max(0,(age-3)/9))
        rows.append(dict(vintage=vint, originated_balance=int(vol), months_since_origination=age,
            cumulative_gross_loss_pct=round(100*cg,4), cumulative_recovery_pct=round(100*cr,4),
            cumulative_net_loss_pct=round(100*(cg-cr),4)))
with open(f"{OUT}/rheinwagen_static_pool_losses.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)

rows=[]
for i in range(96):
    y,m = 2019+i//12, i%12+1
    rows.append(dict(month=f"{y}-{m:02d}", cpr_annualised_pct=round(float(np.clip(rng.normal(12.5,1.8),6,22)),2),
        delinquency_30_59_pct=round(float(rng.normal(0.85,0.08)),3), delinquency_60_89_pct=round(float(rng.normal(0.30,0.04)),3),
        delinquency_90_plus_pct=round(float(rng.normal(0.22,0.03)),3)))
with open(f"{OUT}/rheinwagen_dynamic_book.csv","w",newline="") as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
print("ok")
