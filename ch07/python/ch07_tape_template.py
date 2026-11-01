"""Chapter 7 - data dictionary checks, field map and a
template-style extract (UK residential real estate
template, RREL/RREC fields) for ten Thames loans.
Run from the book folder:
  python3 ch07/python/ch07_tape_template.py \
      data/thames_residential_2027_1_tape.csv \
      ch07_rrel_extract.csv"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

t = pd.read_csv(sys.argv[1], dtype=str, keep_default_na=False)
out = (sys.argv[2] if len(sys.argv) > 2
       else "ch07_rrel_extract.csv")

# ---- 1. The data dictionary: type and rule for each field
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
INTS = {"payments_made": (0, 480),
        "original_term_months": (60, 480),
        "remaining_term_months": (1, 480),
        "original_valuation": (10000, 10000000),
        "borrower_count": (1, 4),
        "gross_income": (1, 10000000),
        "months_in_arrears": (0, 99)}
MONEY = ["original_balance", "current_balance",
         "monthly_payment"]
RATES = {"current_rate": (0.01, 15), "tracker_margin": (-5, 5)}
DATES = ["origination_date", "first_payment_date",
         "fixed_rate_end_date", "cut_off_date"]
OPTIONAL = ["fixed_rate_end_date", "tracker_margin"]

def num(s):
    return pd.to_numeric(s, errors="coerce")

def invalid(f, s):
    """True where a non-blank value breaks the dictionary."""
    x = s[s != ""]
    if f == "loan_id":
        bad = ~x.str.fullmatch(r"KBS-\d{6}") | x.duplicated(
            keep=False)
    elif f in LISTS:
        bad = ~x.isin(LISTS[f])
    elif f in DATES:
        d = pd.to_datetime(x, format="%Y-%m-%d",
                           errors="coerce")
        bad = d.isna()
    elif f in INTS:
        v = num(x); lo, hi = INTS[f]
        bad = v.isna() | (v % 1 != 0) | (v < lo) | (v > hi)
    elif f in MONEY:
        v = num(x)
        cents = (v * 100).round(6)
        bad = v.isna() | (v <= 0) | (cents % 1 != 0)
    elif f in RATES:
        v = num(x); lo, hi = RATES[f]
        bad = v.isna() | (v < lo) | (v > hi)
    return int(bad.sum())

blank_report, n_bad = [], 0
for f in t.columns:
    blanks = int((t[f] == "").sum())
    if blanks and f not in OPTIONAL:
        n_bad += blanks
    if blanks:
        blank_report.append(f"{f} {blanks}")
    n_bad += invalid(f, t[f])
print(f"Data dictionary checks: {len(t.columns)} fields, "
      f"{len(t)} loans")
print("  blanks (optional fields only):")
for b in blank_report:
    print("    " + b)
print(f"  values outside the dictionary: {n_bad}")

# ---- 2. The field map: Kingsbridge tape -> template field
MAP = {"direct": "RREL2 RREL6 RREL23 RREL25 RREL29 RREL30 "
                 "RREL39 RREL43 RREL58 RREC17",
       "transformed": "RREL13 RREL16 RREL35 RREL42 RREL44 "
                      "RREL46 RREL51 RREL69 RREC7 RREC9",
       "derived": "RREL1 RREL17 RREL24 RREL28 RREL37 RREL38 "
                  "RREC16 RREC22",
       "gap": "RREL4 RREL11 RREL19 RREL27 RREL67 RREL68 RREC6 "
              "RREC12 RREC13 RREC14 RREC15 RREC18 RREC19"}
n_map = sum(len(v.split()) for v in MAP.values())
print(f"Field map: {n_map} template fields")
print("  " + ", ".join(f"{k} {len(v.split())}"
                       for k, v in MAP.items()))

# ---- 3. Template-style extract for ten loans
LOANS = ["KBS-000001", "KBS-000002", "KBS-000003",
         "KBS-000004", "KBS-000005", "KBS-000006",
         "KBS-000012", "KBS-000042", "KBS-000059",
         "KBS-000417"]
EMP = {"Employed": "EMUK", "Self-employed": "SFEM",
       "Retired": "PNNR"}
AMORT = {"Repayment": "FRXX", "Interest-only": "BLLT",
         "Part and part": "OTHR"}
PROP = {"Detached": "RHOS", "Semi-detached": "RHOS",
        "Terraced": "RTHS", "Flat": "RFLT", "Bungalow": "RBGL"}
OCC = {"Owner-occupied": "FOWN"}
LEI = "KBS0FICTIONAL0LEI027"         # fictional LEI

def pct2(a, b):
    """a / b in %, 2 dp, halves away from zero (Excel)."""
    q = Decimal(a) * 100 / Decimal(b)
    return str(q.quantize(Decimal("0.01"), ROUND_HALF_UP))

def plus_months(iso, m):
    d = pd.Timestamp(iso) + pd.DateOffset(months=int(m))
    return d.strftime("%Y-%m-%d")

def money(s):
    return f"{Decimal(s):.2f}"

rows = []
for _, r in t[t.loan_id.isin(LOANS)].iterrows():
    fixed = r.product_type in ("2Y Fixed", "5Y Fixed")
    rows.append({
      "RREL1": LEI + "N202701",
      "RREL2": r.loan_id,
      "RREL6": r.cut_off_date,
      "RREL13": EMP[r.employment_status],
      "RREL16": money(r.gross_income)
                if r.borrower_count == "1" else "ND3",
      "RREL17": "GRAN",
      "RREL23": r.origination_date,
      "RREL24": plus_months(r.origination_date,
                            r.original_term_months),
      "RREL25": r.original_term_months,
      "RREL28": "GBP",
      "RREL29": money(r.original_balance),
      "RREL30": money(r.current_balance),
      "RREL35": AMORT[r.repayment_type],
      "RREL37": "MNTH",
      "RREL39": money(r.monthly_payment),
      "RREL42": "FLCF" if fixed else "FLIF",
      "RREL43": r.current_rate,
      "RREL44": "ND5" if fixed else
                ("BOER" if r.product_type == "Tracker"
                 else "LDOR"),
      "RREL46": "ND5" if fixed else
                (r.tracker_margin or "0.00"),
      "RREL51": r.fixed_rate_end_date if fixed else "ND5",
      "RREL58": r.payments_made,
      "RREL69": "PERF" if r.months_in_arrears == "0"
                else "ARRE",
      "RREC7": OCC[r.occupancy],
      "RREC9": PROP[r.property_type],
      "RREC16": pct2(r.original_balance,
                     r.original_valuation),
      "RREC17": money(r.original_valuation)})
ext = pd.DataFrame(rows)
ext.to_csv(out, index=False)
print(f"Extract: {len(ext)} loans x {ext.shape[1]} fields "
      f"-> {out}")
show = ["RREL2", "RREL35", "RREL42", "RREL44", "RREL46",
        "RREL69", "RREC16"]
print(ext[show].to_string(index=False))
