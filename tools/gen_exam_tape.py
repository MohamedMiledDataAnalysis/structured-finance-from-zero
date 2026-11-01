"""Final exam data: Medway Residential 2028-1 plc (fictional).
Run from the book folder:  python3 tools/gen_exam_tape.py
Writes (fixed seed, reproducible):
  data/exam_medway_tape.csv         1,000 rows (999 loans + 1 duplicate), report date 28 Feb 2029, 8 planted issues
  data/exam_medway_dq_key.csv       answer key of the 8 planted data-quality issues
  data/exam_medway_deal_terms.csv   deal terms used by the waterfall (parameter,value)
  data/exam_medway_ipd_inputs.csv   inputs of IPD 1 (15 Mar 2029, normal) and IPD 2 (15 Jun 2029, stressed)
All numbers are ILLUSTRATIVE."""
import csv, datetime as dt
from decimal import Decimal as D, ROUND_HALF_UP
import numpy as np

SEED = 20290228
rng = np.random.default_rng(SEED)
REPORT = dt.date(2029, 2, 28)
q2 = lambda x: D(str(x)).quantize(D("0.01"), rounding=ROUND_HALF_UP)

def add_months(d, n):
    y, m = divmod(d.month - 1 + n, 12)
    return dt.date(d.year + y, m + 1, d.day)

REGIONS = [("London", .20, 1.012), ("South East", .17, 1.022), ("East of England", .10, 1.026),
           ("South West", .09, 1.028), ("West Midlands", .08, 1.034), ("East Midlands", .07, 1.033),
           ("North West", .10, 1.038), ("Yorkshire and the Humber", .07, 1.036), ("North East", .03, 1.030),
           ("Wales", .04, 1.032), ("Scotland", .04, 1.031), ("Northern Ireland", .01, 1.045)]
VAL_MULT = {"London": 1.75, "South East": 1.30, "East of England": 1.15, "South West": 1.10}

N = 999
rows = []
for i in range(1, N + 1):
    reg = REGIONS[rng.choice(len(REGIONS), p=[r[1] for r in REGIONS])]
    region, hpi = reg[0], reg[2]
    # origination between Mar 2019 and Oct 2027 (Medway cut-off 31 Jan 2028)
    om = int(rng.integers(0, 104)); orig = add_months(dt.date(2019, 3, 1), om).replace(day=int(rng.integers(1, 29)))
    term = int(rng.choice([240, 300, 360, 420], p=[.12, .38, .36, .14]))
    mat = add_months(orig, term)
    oval = int(round(float(rng.lognormal(np.log(255000 * VAL_MULT.get(region, 0.95)), 0.33)), -3))
    oltv = float(np.clip(rng.normal(70, 12), 35, 95))
    obal = int(round(oval * oltv / 100, -2))
    rep = str(rng.choice(["Repayment", "Interest-only", "Part and part"], p=[.86, .10, .04]))
    rtype = str(rng.choice(["Fixed", "Tracker", "SVR"], p=[.82, .08, .10]))
    if rtype == "Fixed": rate = round(float(np.clip(rng.normal(4.55, .45), 3.39, 5.89)), 2)
    elif rtype == "Tracker": rate = round(3.65 + float(rng.choice([.49, .74, .99, 1.24, 1.49])), 2)
    else: rate = 7.24
    paid = (REPORT.year - orig.year) * 12 + REPORT.month - orig.month  # payments made to the report date
    r = rate / 1200
    def amort(p, n_left_total):
        pmt = p * r / (1 - (1 + r) ** -term)
        return p * (1 + r) ** paid - pmt * ((1 + r) ** paid - 1) / r
    over = 1 - float(rng.uniform(0, .04))
    if rep == "Repayment": cbal = amort(obal, term) * over
    elif rep == "Interest-only": cbal = obal
    else: cbal = obal / 2 + amort(obal / 2, term) * over
    cbal = q2(cbal)
    years = paid / 12
    ival = int(round(oval * hpi ** years * float(rng.uniform(.97, 1.03))))
    u = rng.random()
    arr = 0 if u < .962 else 1 if u < .979 else 2 if u < .987 else int(rng.integers(3, 6)) if u < .995 else int(rng.integers(6, 12))
    emp = str(rng.choice(["Employed", "Self-employed", "Retired", "Other"], p=[.72, .17, .07, .04]))
    rows.append(dict(loan_id=f"MRS-{i:05d}", origination_date=orig.isoformat(), maturity_date=mat.isoformat(),
                     original_term_months=term, original_balance=f"{obal:.2f}", current_balance=f"{cbal}",
                     original_valuation=oval, indexed_valuation=ival,
                     original_ltv=f"{q2(D(obal) / D(oval) * 100)}", indexed_ltv=f"{q2(cbal / D(ival) * 100)}",
                     current_rate=f"{rate:.2f}", rate_type=rtype, repayment_type=rep, region=region,
                     months_in_arrears=arr, employment_status=emp, report_date=REPORT.isoformat()))

# ---------- plant the 8 data-quality issues ----------
idx = list(rng.permutation(N))
pick = lambda cond: next(k for k in idx if cond(rows[k]) and not rows[k].get("_used"))
key = []
def mark(k, **kw):
    rows[k]["_used"] = True; key.append(dict(loan_id=rows[k]["loan_id"], **kw))

# DQ02 current balance above original: decimal shifted (x10) on a repayment loan
k = pick(lambda r: r["repayment_type"] == "Repayment" and r["months_in_arrears"] == 0 and 120000 < float(r["current_balance"]) < 220000)
true = rows[k]["current_balance"]; rows[k]["current_balance"] = f"{D(true) * 10:.2f}"
mark(k, issue_id="DQ02", field="current_balance", raw_value=rows[k]["current_balance"],
     issue="Current balance above original balance (decimal shifted: 10 times the true balance)",
     treatment=f"Use {true} (reported value / 10; agrees with indexed_ltv and original balance); confirm with servicer")
# DQ03 maturity before origination: century error
k = pick(lambda r: r["months_in_arrears"] == 0)
m = dt.date.fromisoformat(rows[k]["maturity_date"]); rows[k]["maturity_date"] = m.replace(year=m.year - 100).isoformat()
mark(k, issue_id="DQ03", field="maturity_date", raw_value=rows[k]["maturity_date"],
     issue="Maturity date before origination date (century error)",
     treatment=f"Use origination date + original term = {m.isoformat()}")
# DQ04 indexed LTV inconsistent with balance / indexed valuation (stale: equals original LTV)
k = pick(lambda r: float(r["original_ltv"]) - float(r["indexed_ltv"]) > 15)
rows[k]["indexed_ltv"] = rows[k]["original_ltv"]
mark(k, issue_id="DQ04", field="indexed_ltv", raw_value=rows[k]["indexed_ltv"],
     issue="Indexed LTV inconsistent with current balance / indexed valuation (field equals original LTV)",
     treatment="Recompute indexed LTV for every loan from current balance and indexed valuation")
# DQ05 missing region
k = pick(lambda r: True); reg_true = rows[k]["region"]; rows[k]["region"] = ""
mark(k, issue_id="DQ05", field="region", raw_value="(blank)", issue="Region missing",
     treatment="Report in an Unknown row of the region strat; request the property postcode")
# DQ07 zero interest rate on a fixed-rate loan
k = pick(lambda r: r["rate_type"] == "Fixed"); rows[k]["current_rate"] = "0.00"
mark(k, issue_id="DQ07", field="current_rate", raw_value="0.00", issue="Zero current interest rate on a fixed-rate loan",
     treatment="Exclude from the WA current rate (keep in all other figures); query servicer")
# DQ08 impossible arrears value
k = pick(lambda r: r["months_in_arrears"] == 0); rows[k]["months_in_arrears"] = -2
mark(k, issue_id="DQ08", field="months_in_arrears", raw_value="-2", issue="Negative months in arrears (impossible)",
     treatment="Report in an Unknown row of the arrears strat; query servicer")
# DQ06 region spelled two ways
yh = [j for j in idx if rows[j]["region"] == "Yorkshire and the Humber" and not rows[j].get("_used")][:9]
for j in yh: rows[j]["region"] = "Yorkshire & Humber"
key.append(dict(issue_id="DQ06", loan_id=";".join(sorted(rows[j]["loan_id"] for j in yh)), field="region",
                raw_value="Yorkshire & Humber", issue=f"Region spelled two ways ({len(yh)} loans)",
                treatment="Map to Yorkshire and the Humber"))
# DQ01 duplicate loan ID: an exact copy of one row, inserted later in the file
k = pick(lambda r: r["months_in_arrears"] == 0 and r["region"] not in ("", "Yorkshire & Humber") and int(r["loan_id"][4:]) < 600)
rows[k]["_used"] = True
dup = dict(rows[k]); key.append(dict(issue_id="DQ01", loan_id=rows[k]["loan_id"], field="loan_id", raw_value=rows[k]["loan_id"],
                                      issue="Duplicate loan ID (identical row appears twice)",
                                      treatment="Count the loan once (exclude the second row)"))
pos = int(rng.integers(k + 200, N)); rows.insert(pos, dup)
assert len(rows) == 1000

FIELDS = ["loan_id", "origination_date", "maturity_date", "original_term_months", "original_balance", "current_balance",
          "original_valuation", "indexed_valuation", "original_ltv", "indexed_ltv", "current_rate", "rate_type",
          "repayment_type", "region", "months_in_arrears", "employment_status", "report_date"]
with open("data/exam_medway_tape.csv", "w", newline="") as f:
    w = csv.DictWriter(f, FIELDS, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
key.sort(key=lambda d: d["issue_id"])
with open("data/exam_medway_dq_key.csv", "w", newline="") as f:
    w = csv.DictWriter(f, ["issue_id", "loan_id", "field", "raw_value", "issue", "treatment"]); w.writeheader(); w.writerows(key)

# ---------- reporting pool total (treatment as in the answer key) ----------
seen, T = set(), D(0)
for r in rows:
    if r["loan_id"] in seen: continue
    seen.add(r["loan_id"]); b = D(r["current_balance"])
    if r["loan_id"] == next(x["loan_id"] for x in key if x["issue_id"] == "DQ02"): b = b / 10
    T += b
wa_rate = sum(D(r["current_balance"]) * D(r["current_rate"]) for r in rows) / sum(D(r["current_balance"]) for r in rows)

# ---------- deal terms ----------
terms = dict(class_a_closing="207000000.00", class_b_closing="14400000.00", pool_cutoff="225968431.27",
             margin_a="0.58", margin_b="1.35", senior_fees_pa="190000.00", servicing_pct="0.15",
             reserve_required="2214000.00", reserve_at_closing="0.00", sonia="3.60")
terms["class_z_closing"] = f"{D(terms['pool_cutoff']) - D(terms['class_a_closing']) - D(terms['class_b_closing']):.2f}"
with open("data/exam_medway_deal_terms.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["parameter", "value"]); [w.writerow([k, v]) for k, v in terms.items()]

# ---------- IPD inputs ----------
# IPD 1 (15 Dec 2028 -> 15 Mar 2029, 90 days, collections Dec 2028 - Feb 2029): a normal quarter
sched1, prep1, rec1, loss1 = q2(T * D("0.00731")), q2(T * D("0.02388")), D("143260.00"), D("38417.62")
pool1 = T + sched1 + prep1 + rec1 + loss1
zpdl_open = D("61884.15")               # losses at earlier IPDs, not yet cured (reserve still building)
B, Z = D(terms["class_b_closing"]), D(terms["class_z_closing"])
A1 = pool1 + zpdl_open - B - Z
rev1 = q2(pool1 * wa_rate / 100 * 90 / 365 * D("0.988"))
# IPD 2 (15 Mar -> 15 Jun 2029, 92 days, collections Mar - May 2029): stressed
sched2, prep2, rec2, loss2 = q2(T * D("0.00702")), q2(T * D("0.01231")), D("1874350.00"), D("712946.38")
extra2 = D("74500.00")
s, ms = D(terms["sonia"]), (D(terms["margin_a"]), D(terms["margin_b"]))
fees = lambda d: q2(D(terms["senior_fees_pa"]) * d / 365)
serv = lambda p, d: q2(p * D(terms["servicing_pct"]) / 100 * d / 365)
intr = lambda b, m, d: q2(b * (s + m) / 100 * d / 365)
due1 = fees(90) + serv(pool1, 90) + intr(A1, ms[0], 90) + intr(B, ms[1], 90)
rf_open1 = D("384612.90")
excess1 = rev1 - due1
assert 0 < excess1 < D(terms["reserve_required"]) - rf_open1, excess1
rf1 = rf_open1 + excess1
A1c = A1 - (sched1 + prep1 + rec1)
due2_senior = fees(92) + extra2 + serv(T, 92) + intr(A1c, ms[0], 92)
bint2 = intr(B, ms[1], 92)
rev2 = q2(due2_senior + bint2 * D("0.43") - rf1)
inputs = [("ipd_date", "2029-03-15", "2029-06-15"), ("period_start", "2028-12-15", "2029-03-15"),
          ("days", "90", "92"), ("collection_periods", "Dec 2028 - Feb 2029", "Mar 2029 - May 2029"),
          ("revenue_collections", f"{rev1}", f"{rev2}"), ("scheduled_principal", f"{sched1}", f"{sched2}"),
          ("prepayments", f"{prep1}", f"{prep2}"), ("recoveries", f"{rec1}", f"{rec2}"),
          ("realised_losses", f"{loss1}", f"{loss2}"), ("extra_senior_expenses", "0.00", f"{extra2}")]
opening = [("opening_pool", f"{pool1}"), ("class_a", f"{A1:.2f}"), ("class_b", f"{B}"), ("class_z", f"{Z}"),
           ("pdl_a", "0.00"), ("pdl_b", "0.00"), ("pdl_z", f"{zpdl_open}"), ("reserve", f"{rf_open1}"),
           ("deferred_b", "0.00")]
with open("data/exam_medway_ipd_inputs.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["item", "ipd1", "ipd2"])
    for it in inputs: w.writerow(it)
    for k2, v in opening: w.writerow([f"open_{k2}", v, ""])
print("reporting pool", T, "opening pool IPD1", pool1, "A1", A1, "rev1", rev1, "excess1", excess1,
      "rev2", rev2, "rev2/rev1", round(rev2 / rev1, 3), "wa_rate", round(wa_rate, 3))
