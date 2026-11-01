"""Chapter 8 - validate a Thames loan tape: completeness,
validity, consistency, reasonableness and recalculation,
with an exception report and control totals.
Run from the book folder:
  python3 ch08/python/ch08_validate.py \
      data/ch08_thames_tape_raw.csv"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

t = pd.read_csv(sys.argv[1], dtype=str, keep_default_na=False)
LEDGER_N, LEDGER_BAL = 3000, Decimal("635671146.31")
CUT = pd.Timestamp("2027-01-31")
BANK_RATE, SVR = 3.75, 7.49

LISTS = {
  "repayment_type": ["Repayment", "Interest-only",
                     "Part and part"],
  "product_type": ["2Y Fixed", "5Y Fixed", "Tracker", "SVR"],
  "region": ["London", "South East", "East of England",
             "South West", "West Midlands", "East Midlands",
             "Yorkshire and the Humber", "North West",
             "North East", "Wales", "Scotland",
             "Northern Ireland"],
  "property_type": ["Detached", "Semi-detached", "Terraced",
                    "Flat", "Bungalow"],
  "occupancy": ["Owner-occupied"],
  "first_time_buyer": ["Y", "N"],
  "employment_status": ["Employed", "Self-employed",
                        "Retired"]}
DATES = ["origination_date", "first_payment_date",
         "fixed_rate_end_date", "cut_off_date"]
OPTIONAL = ["fixed_rate_end_date", "tracker_margin"]
NUMS = ["payments_made", "original_balance",
        "current_balance", "monthly_payment",
        "original_term_months", "remaining_term_months",
        "current_rate", "tracker_margin",
        "original_valuation", "borrower_count",
        "gross_income", "months_in_arrears"]

# ---- typed copies: invalid or blank values become NaN/NaT
d = {f: pd.to_datetime(t[f], format="%Y-%m-%d",
                       errors="coerce") for f in DATES}
n = {f: pd.to_numeric(t[f], errors="coerce") for f in NUMS}
ok = {f: t[f].isin(v) for f, v in LISTS.items()}
exc = []                                   # exception report

def flag(mask, check, text):
    for i in t.index[mask.fillna(False)]:
        exc.append((t.loan_id[i], check, text(i)))

# ---- K: completeness
for f in t.columns:
    if f not in OPTIONAL:
        flag(t[f] == "", "K1", lambda i, f=f: f"{f} is blank")
dup = t.loan_id[t.loan_id.duplicated()]
for lid in dup.unique():
    exc.append((lid, "K2", "loan_id appears twice"))
ids = {f"KBS-{k:06d}" for k in range(1, LEDGER_N + 1)}
for lid in sorted(ids - set(t.loan_id)):
    exc.append((lid, "K3", "loan on ledger, not on tape"))

# ---- V: validity against the data dictionary
for f in LISTS:
    flag((t[f] != "") & ~ok[f], "V1",
         lambda i, f=f: f"{f} = '{t[f][i]}'")
for f in DATES:
    flag((t[f] != "") & d[f].isna(), "V2",
         lambda i, f=f: f"{f} = {t[f][i]}")
for f in NUMS:
    flag((t[f] != "") & n[f].isna(), "V3",
         lambda i, f=f: f"{f} not a number")

# ---- C: consistency between fields
o, fp, fe = (d["origination_date"], d["first_payment_date"],
             d["fixed_rate_end_date"])
plus = lambda s, m: s + pd.DateOffset(months=m)
flag(n["remaining_term_months"] != n["original_term_months"]
     - n["payments_made"], "C1",
     lambda i: "remaining term <> term - payments")
flag(o.notna() & fp.notna() & (fp != o.apply(plus, m=1)),
     "C2", lambda i: "first payment <> origination + 1m")
months = t.product_type.map({"2Y Fixed": 24, "5Y Fixed": 60})
fx = ok["product_type"] & months.notna() & o.notna()
due = pd.Series(pd.NaT, index=t.index)
due[fx] = [plus(o[i], int(months[i])) for i in t.index[fx]]
flag(fx & (fe != due), "C3",
     lambda i: "fixed end date <> origination + period")
flag(ok["product_type"] & months.isna()
     & (t.fixed_rate_end_date != ""), "C3",
     lambda i: "end date on a non-fixed loan")
trk = ok["product_type"] & (t.product_type == "Tracker")
flag(trk & ((t.tracker_margin == "") | ((n["current_rate"]
     - BANK_RATE - n["tracker_margin"]).abs() > 0.005)),
     "C4", lambda i: "tracker rate <> Bank Rate + margin")
flag(ok["product_type"] & ~trk & (t.tracker_margin != ""),
     "C4", lambda i: "margin on a non-tracker loan")
flag(ok["product_type"] & (t.product_type == "SVR")
     & ((n["current_rate"] - SVR).abs() > 0.005), "C5",
     lambda i: "SVR loan not at 7.49%")
k = ((CUT.year - fp.dt.year) * 12 + CUT.month - fp.dt.month
     + (fp.dt.day <= CUT.day).astype(int))
flag(fp.notna() & (k != n["payments_made"]), "C6",
     lambda i: "payments made <> payment dates")

# ---- R: reasonableness
oltv = 100 * n["original_balance"] / n["original_valuation"]
lti = n["original_balance"] / n["gross_income"]
flag((oltv < 10) | (oltv > 100), "R1",
     lambda i: f"original LTV {oltv[i]:.2f}%")
flag((lti < 1) | (lti > 6), "R2", lambda i: f"LTI {lti[i]:.2f}")
r = n["current_rate"]
flag((r < 1) | (r > 10), "R3", lambda i: f"rate {r[i]}%")
flag(n["months_in_arrears"] > 1, "R4",
     lambda i: f"{t.months_in_arrears[i]} months in arrears")

# ---- P: recalculation (Chapter 1 schedule, closed form)
def r2(x):
    """Pennies, halves away from zero, as Excel's ROUND.
    Formatting to 9 decimals first absorbs binary noise:
    827.2249999999 is the exact half 827.225."""
    return float(Decimal(f"{x:.9f}").quantize(
        Decimal("0.01"), ROUND_HALF_UP))

def recalc(P, rate, term, k, kind):
    """Scheduled payment and balance after k payments."""
    m = rate / 1200
    if kind == "Interest-only":
        return r2(P * m), P
    amort = r2(P / 2) if kind == "Part and part" else P
    pmt = r2(amort * m / (1 - (1 + m) ** -term))
    g = (1 + m) ** k
    bal = amort * g - pmt * (g - 1) / m
    if kind == "Part and part":
        return pmt + r2(amort * m), bal + amort
    return pmt, bal

for i in t.index:
    if not ok["repayment_type"][i]:
        continue
    pmt, bal = recalc(n["original_balance"][i], r[i],
                      n["original_term_months"][i],
                      n["payments_made"][i],
                      t.repayment_type[i])
    if abs(pmt - n["monthly_payment"][i]) > 0.005:
        exc.append((t.loan_id[i], "P1",
                    f"payment {pmt:.2f} vs tape "
                    f"{n['monthly_payment'][i]:.2f}"))
    if abs(bal - n["current_balance"][i]) > 1.00:
        exc.append((t.loan_id[i], "P2",
                    f"balance {bal:.2f} vs tape "
                    f"{n['current_balance'][i]:.2f}"))

# ---- Report
bal = sum(Decimal(b) for b in t.current_balance if b)
print(f"Tape: {len(t)} rows, "
      f"{t.loan_id.nunique()} distinct loan IDs")
print("Control totals      ledger          tape    difference")
print(f"  loans   {LEDGER_N:>12}{len(t):>14}"
      f"{len(t) - LEDGER_N:>14}")
print(f"  balance {LEDGER_BAL:>12}{bal:>14}"
      f"{bal - LEDGER_BAL:>14}")
GROUPS = [("Completeness", "K1 K2 K3"),
          ("Validity", "V1 V2 V3"),
          ("Consistency", "C1 C2 C3 C4 C5 C6"),
          ("Reasonableness", "R1 R2 R3 R4"),
          ("Recalculation", "P1 P2")]
rep = pd.DataFrame(exc, columns=["loan_id", "check", "detail"])
print("Exceptions by check")
for g, cs in GROUPS:
    cells = [f"{c} {(rep.check == c).sum()}"
             for c in cs.split()]
    print(f"  {g:<15} " + "  ".join(cells))
print(f"Total: {len(rep)} exceptions on "
      f"{rep.loan_id.nunique()} loans")
if len(rep):
    print("Exception report")
    rep = rep.sort_values(["loan_id", "check"], kind="stable")
    for _, e in rep.iterrows():
        print(f"  {e.loan_id} {e.check} {e.detail}")
