"""Chapter 3 - credit risk: arrears at cut-off, loss on a
defaulted loan, expected loss of the Thames pool, CPR and
SMM, and concentration.
Run from the book folder:
  python3 ch03/python/ch03_credit_risk.py \\
    data/thames_residential_2027_1_tape.csv \\
    data/kingsbridge_static_pool_defaults.csv \\
    data/kingsbridge_dynamic_book.csv
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd


def round2(x):
    """Round to pennies as Excel's ROUND does."""
    return Decimal(str(x)).quantize(Decimal("0.01"),
                                    rounding=ROUND_HALF_UP)


tape = pd.read_csv(sys.argv[1])
static = pd.read_csv(sys.argv[2])
book = pd.read_csv(sys.argv[3])
pool = tape.current_balance.sum()

# ---- 1. Arrears at cut-off -----------------------------
arr = tape[tape.months_in_arrears > 0]
arr_bal = arr.current_balance.sum()

# ---- 2. Loss on one defaulted loan (illustrative) ------
HPI_FALL, FORCED, COSTS = 0.10, 0.15, 6000.00
MONTHS_UNPAID, LAG_YEARS = 21, 1.5


def loan_loss(loan_id):
    ln = tape.loc[tape.loan_id == loan_id].iloc[0]
    bal = ln.current_balance
    unpaid = round(bal * ln.current_rate / 100
                   * MONTHS_UNPAID / 12, 2)
    claim = bal + unpaid + COSTS
    sale = round(ln.original_valuation * (1 - HPI_FALL)
                 * (1 - FORCED), 2)
    loss = max(claim - sale, 0.0)
    return dict(ltv=bal / ln.original_valuation * 100,
                bal=bal, unpaid=unpaid, claim=claim,
                sale=sale, loss=loss, sev=loss / bal * 100,
                rate=ln.current_rate)


# ---- 3. Expected loss of the pool ----------------------
AGE = 96
s = static[static.months_since_origination == AGE]
w = s.originated_balance
pd_pct = (w * s.cumulative_default_pct).sum() / w.sum()
lgd = ((w * s.cumulative_net_loss_pct).sum()
       / (w * s.cumulative_default_pct).sum())
el = round2(pd_pct / 100 * lgd * pool)

# ---- 4. Prepayment: CPR and SMM ------------------------
cpr = book[book.month.str.startswith("2026")] \
    .cpr_annualised_pct.mean()
smm = 1 - (1 - cpr / 100) ** (1 / 12)
prepay_1 = round2(pool * smm)
cpr_from_1 = 1 - (1 - 0.01) ** 12

# ---- 5. Concentration ----------------------------------
reg = tape.groupby("region").current_balance.sum() \
    .sort_values(ascending=False)
top10 = tape.current_balance.nlargest(10).sum()

print("1. Arrears at cut-off")
print(f"   Loans 1 month in arrears : {len(arr)}")
print(f"   Their balance            : {arr_bal:,.2f}")
print(f"   Share of pool balance    : "
      f"{arr_bal / pool * 100:.2f}%")
print("2. Loss if the loan defaults (illustrative)")
for lid in ("KBS-001857", "KBS-000417"):
    r = loan_loss(lid)
    print(f"   {lid}: LTV {r['ltv']:.2f}%, claim"
          f" {r['claim']:,.2f}, sale {r['sale']:,.2f}")
    print(f"     loss {r['loss']:,.2f}, severity"
          f" {r['sev']:.2f}%, surplus"
          f" {max(r['sale'] - r['claim'], 0):,.2f}")
r = loan_loss("KBS-001857")
pv_sale = r["sale"] / (1 + r["rate"] / 100) ** LAG_YEARS
print(f"   KBS-001857 sale paid 18 months later,"
      f" PV {pv_sale:,.2f}")
print("3. Expected loss of the Thames pool")
print(f"   Vintages with {AGE} months of history: {len(s)}"
      f" ({s.vintage.iloc[0]}-{s.vintage.iloc[-1]})")
print(f"   PD  (cumulative default, {AGE} months): "
      f"{pd_pct:.4f}%")
print(f"   LGD (net loss / default)          : "
      f"{lgd * 100:.2f}%")
print(f"   EAD (pool balance at cut-off)     : {pool:,.2f}")
print(f"   Expected loss                     : {el:,}")
print(f"   Expected loss, % of pool          : "
      f"{float(el) / pool * 100:.4f}%")
print("4. Prepayment")
print(f"   Average CPR, Kingsbridge book 2026: {cpr:.2f}%")
print(f"   SMM                               : "
      f"{smm * 100:.4f}%")
print(f"   One month's prepayment on the pool: "
      f"{prepay_1:,}")
print(f"   CPR for an SMM of 1.00%           : "
      f"{cpr_from_1 * 100:.2f}%")
print("5. Concentration")
print(f"   Largest region   : {reg.index[0]}"
      f" {reg.iloc[0] / pool * 100:.2f}%")
print(f"   Largest loan     : {tape.current_balance.max():,.2f}"
      f" ({tape.current_balance.max() / pool * 100:.2f}%)")
print(f"   Ten largest loans: {top10:,.2f}"
      f" ({top10 / pool * 100:.2f}%)")
