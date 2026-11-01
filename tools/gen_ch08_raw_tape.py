"""Chapter 8: build the 'raw' Thames tape with 20 documented injected faults.
Start: the clean cut-off tape (data/thames_residential_2027_1_tape.csv).
Output: data/ch08_thames_tape_raw.csv (the tape as first extracted, with faults)
        data/ch08_fault_log.csv       (answer key: one row per injected fault)
Correcting every fault in the log returns exactly the clean tape (asserted below).
Seed 20261108. Run from the book folder:
    python3 tools/gen_ch08_raw_tape.py data/thames_residential_2027_1_tape.csv data/ch08_thames_tape_raw.csv data/ch08_fault_log.csv
"""
import sys, csv
from datetime import date
from decimal import Decimal
import numpy as np

CLEAN, RAW, LOG = sys.argv[1:4]
rng = np.random.default_rng(20261108)
rows = list(csv.DictReader(open(CLEAN)))
FIELDS = list(rows[0].keys())
by_id = {r["loan_id"]: r for r in rows}
USED = {f"KBS-{i:06d}" for i in list(range(1, 13)) + [42, 59, 417]}   # loans used as examples in Ch 1, 6, 7

def pick(cond):
    ids = [r["loan_id"] for r in rows if cond(r) and r["loan_id"] not in USED]
    lid = str(rng.choice(ids)); USED.add(lid); return lid

log = []
def fault(no, lid, field, new, category, check, description):
    old = by_id[lid][field] if field else ""
    log.append(dict(fault=f"F{no:02d}", loan_id=lid, field=field, clean_value=old, raw_value=new,
                    category=category, check=check, description=description))
    if field: raw[lid][field] = new

raw = {r["loan_id"]: dict(r) for r in rows}
rep = lambda r: r["repayment_type"] == "Repayment"
fixed = lambda r: r["product_type"] in ("2Y Fixed", "5Y Fixed")
# ---- completeness
a = pick(rep); fault(1, a, "gross_income", "", "Completeness", "K1", "income not loaded (blank)")
a = pick(rep); fault(2, a, "gross_income", "", "Completeness", "K1", "income not loaded (blank)")
a = pick(rep); fault(3, a, "original_valuation", "", "Completeness", "K1", "valuation not loaded (blank)")
missing = pick(rep); fault(4, missing, "", "(row missing)", "Completeness", "K3/K4", "loan dropped from the extract")
dup = pick(rep); fault(5, dup, "", "(row twice)", "Completeness", "K2/K4", "loan extracted twice")
# ---- validity
a = pick(lambda r: rep(r) and fixed(r) and r["origination_date"][5:7] == "02")
fault(6, a, "origination_date", raw[a]["origination_date"][:8] + "30", "Validity", "V2", "impossible date (30 February)")
a = pick(lambda r: rep(r) and r["product_type"] == "5Y Fixed")
fault(7, a, "product_type", "5Y Fixd", "Validity", "V1", "list value mistyped")
a = pick(lambda r: rep(r) and r["region"] == "London")
fault(8, a, "region", "Greater London", "Validity", "V1", "value not in the region list")
# ---- reasonableness
a = pick(lambda r: rep(r) and fixed(r))
fault(9, a, "current_rate", f"{Decimal(raw[a]['current_rate']) / 100:.4f}", "Reasonableness", "R3/P1/P2",
      "rate entered as a decimal, not a percentage")
a = pick(lambda r: rep(r) and r["months_in_arrears"] == "0")
fault(10, a, "months_in_arrears", "3", "Reasonableness", "R4", "arrears above the eligibility limit of 1 month")
a = pick(rep); fault(11, a, "original_valuation", str(int(raw[a]["original_valuation"]) * 10), "Reasonableness", "R1",
                     "valuation with an extra zero")
a = pick(rep); fault(12, a, "gross_income", str(int(raw[a]["gross_income"]) * 10), "Reasonableness", "R2",
                     "income with an extra zero")
# ---- consistency (cross-field)
a = pick(rep); fault(13, a, "remaining_term_months", str(int(raw[a]["remaining_term_months"]) + 12), "Consistency",
                     "C1", "remaining term not equal to original term minus payments made")
a = pick(rep); fault(14, a, "remaining_term_months", str(int(raw[a]["original_term_months"])), "Consistency",
                     "C1", "remaining term equal to original term (not updated)")
a = pick(lambda r: rep(r) and r["product_type"] == "2Y Fixed")
d = raw[a]["fixed_rate_end_date"]; fault(15, a, "fixed_rate_end_date", str(int(d[:4]) - 2) + d[4:], "Consistency",
                                         "C3", "fixed-rate end date two years early (before the cut-off date)")
a = pick(lambda r: rep(r) and r["product_type"] == "Tracker")
fault(16, a, "tracker_margin", "", "Consistency", "C4", "tracker loan with no margin")
a = pick(lambda r: rep(r) and int(r["first_payment_date"][8:]) <= 18)
d = raw[a]["first_payment_date"]; fault(17, a, "first_payment_date", d[:8] + f"{int(d[8:]) + 10:02d}", "Consistency",
                                        "C2", "first payment date not one month after origination")
# ---- recalculation
a = pick(lambda r: r["repayment_type"] == "Interest-only")
fault(18, a, "current_balance", f"{Decimal(raw[a]['current_balance']) - Decimal('5000'):.2f}", "Recalculation",
      "P2", "interest-only balance below the original balance")
a = pick(rep); b = raw[a]["current_balance"]; i = b.index(".")
sw = b[:i-3] + b[i-2] + b[i-3] + b[i-1:]          # swap hundreds and tens digits
if sw == b: raise SystemExit("choose another loan")
fault(19, a, "current_balance", sw, "Recalculation", "P2", "two digits of the balance transposed")
a = pick(rep); p = Decimal(raw[a]["monthly_payment"])
fault(20, a, "monthly_payment", f"{p + Decimal('18.00'):.2f}", "Recalculation", "P1", "payment mistyped (+18.00)")

# ---- write the raw tape (missing loan dropped, duplicate row repeated next to the original)
out = []
for r in rows:
    lid = r["loan_id"]
    if lid == missing: continue
    out.append(raw[lid])
    if lid == dup: out.append(dict(raw[lid]))
with open(RAW, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=FIELDS); w.writeheader(); w.writerows(out)
with open(LOG, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(log[0].keys())); w.writeheader(); w.writerows(log)

# ---- prove that correcting the log returns the clean tape
fixed_rows, seen = [], set()
for r in csv.DictReader(open(RAW)):
    if r["loan_id"] in seen: continue
    seen.add(r["loan_id"]); fixed_rows.append(dict(r))
fx = {r["loan_id"]: r for r in fixed_rows}
for L in log:
    if L["field"]: fx[L["loan_id"]][L["field"]] = L["clean_value"]
fx[missing] = dict(by_id[missing])
assert [fx[r["loan_id"]] for r in rows] == rows
print(f"raw tape: {len(out)} rows; faults: {len(log)}; corrected raw == clean tape")
