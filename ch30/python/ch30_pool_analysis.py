"""Chapter 30 - Rhein Auto 2027-1: pool stratification, balloon
concentration and base-case net loss from Rheinwagen static pools.
Run from the book folder:
  python3 ch30/python/ch30_pool_analysis.py \\
      data/rhein_auto_2027_1_tape.csv \\
      data/rheinwagen_static_pool_losses.csv
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

tape = pd.read_csv(sys.argv[1])
stat = pd.read_csv(sys.argv[2])
POOL = tape.current_balance.sum()

def eur(x):
    return f"{x:,.2f}"

def wavg(col, w):
    return (tape[col] * w).sum() / w.sum()

# ---------- 1. Pool summary ----------
w = tape.current_balance
tape["ltv"] = 100 * tape.original_balance / tape.vehicle_price
print("POOL AT CUT-OFF (28 Feb 2027)")
print(f"Loans                     : {len(tape):,}")
print(f"Current balance (EUR)     : {eur(POOL)}")
print(f"Average balance (EUR)     : {eur(POOL / len(tape))}")
print(f"WA interest rate (%)      : {wavg('interest_rate', w):.2f}")
print(f"WA remaining term (months): "
      f"{wavg('remaining_term_months', w):.2f}")
print(f"WA seasoning (months)     : {wavg('payments_made', w):.2f}")
print(f"WA LTV at origination (%) : {wavg('ltv', w):.2f}")

# ---------- 2. Stratification tables ----------
tape["product"] = tape.balloon.map(
    {"Y": "Balloon", "N": "Classic"})
tape["ltv_band"] = pd.cut(
    tape.ltv, [0, 80, 90, 100],
    labels=["<= 80%", "80-90%", "90-100%"])

def strat(col):
    g = tape.groupby(col, observed=True).agg(
        loans=("loan_id", "size"),
        balance=("current_balance", "sum"))
    g["pct"] = 100 * g.balance / POOL
    print(f"\nBy {col}")
    for k, r in g.iterrows():
        print(f"  {str(k):<10} {int(r.loans):>6,} "
              f"{eur(r.balance):>16} {r.pct:6.2f}%")

for c in ["product", "vehicle_condition", "fuel_type",
          "borrower_type", "original_term_months", "ltv_band"]:
    strat(c)
st = tape.groupby("federal_state").current_balance.sum()
print("\nTop 3 federal states (% of pool)")
for k, v in st.sort_values(ascending=False).head(3).items():
    print(f"  {k:<22} {100 * v / POOL:6.2f}%")

# ---------- 3. Balloon concentration ----------
b = tape[tape.balloon == "Y"].copy()
print("\nBALLOON CONCENTRATION")
print(f"Balloon loans             : {len(b):,}")
print(f"Their current balance     : {eur(b.current_balance.sum())}"
      f" ({100 * b.current_balance.sum() / POOL:.2f}% of pool)")
print(f"Balloon amounts           : {eur(b.balloon_amount.sum())}"
      f" ({100 * b.balloon_amount.sum() / POOL:.2f}% of pool)")
# due month = cut-off month + remaining term (month 1 = Mar 2027)
due = pd.Period("2027-02", "M") + b.remaining_term_months
b["due_year"] = due.map(lambda p: p.year)
b["due_month"] = due.astype(str)
print("Balloons falling due by calendar year")
for y, v in b.groupby("due_year").balloon_amount.sum().items():
    print(f"  {y}  {eur(v):>15}  {100 * v / POOL:5.2f}%")
pk = b.groupby("due_month").balloon_amount.sum()
print(f"Largest month: {pk.idxmax()}  {eur(pk.max())}")
print("Balloon as % of vehicle price, by fuel type")
g = b.groupby("fuel_type")[["balloon_amount",
                            "vehicle_price"]].sum()
for k, r in g.iterrows():
    print(f"  {k:<9} "
          f"{100 * r.balloon_amount / r.vehicle_price:6.2f}%")

# ---------- 4. One balloon loan: RA-000002 ----------
def round2(x):
    return Decimal(x).quantize(Decimal("0.01"),
                               rounding=ROUND_HALF_UP)

def balloon_pmt(p, rate_pct, n, fv):
    r = Decimal(str(rate_pct)) / 1200
    p, fv = Decimal(str(p)), Decimal(str(fv))
    f = (1 + r) ** n
    return round2((p * r * f - fv * r) / (f - 1)), r

ln = tape.loc[tape.loan_id == "RA-000002"].iloc[0]
n = int(ln.original_term_months)
pmt, r = balloon_pmt(ln.original_balance, ln.interest_rate,
                     n, ln.balloon_amount)
classic, _ = balloon_pmt(ln.original_balance,
                         ln.interest_rate, n, 0)
bal, sched = Decimal(str(ln.original_balance)), []
for m in range(1, n + 1):
    i = round2(bal * r)
    bal = bal - (pmt - i)
    sched.append(bal)
k = int(ln.payments_made)
print("\nLOAN RA-000002 (balloon)")
print(f"Instalment with balloon   : {eur(pmt)}")
print(f"Instalment without balloon: {eur(classic)}")
print(f"Balance after {k} payments : {eur(sched[k - 1])}"
      f"   tape: {eur(ln.current_balance)}")
print(f"Final payment (month {n})  : {eur(pmt + sched[-1])}")

# ---------- 5. Static pools: chain ladder ----------
stat["mx"] = stat.groupby("vintage") \
    .months_since_origination.transform("max")
AGE = stat.months_since_origination

def to_ultimate(col):
    """Volume-weighted development factors, chained to 96m."""
    wv = stat.originated_balance * stat[col]
    cdf = {96: 1.0}
    for a in range(95, 0, -1):
        num = wv[AGE == a + 1].sum()
        den = wv[(AGE == a) & (stat.mx >= a + 1)].sum()
        cdf[a] = cdf[a + 1] * num / den
    last = stat[AGE == stat.mx].copy()
    last["life"] = last[col] * last.mx.map(cdf)
    return cdf, last

cdf_n, net = to_ultimate("cumulative_net_loss_pct")
cdf_g, gross = to_ultimate("cumulative_gross_loss_pct")
print("\nSTATIC POOLS: factor to ultimate (net loss)")
for a in (12, 24, 36):
    print(f"  at {a} months: {cdf_n[a]:.4f}")
mature = net.mx >= 12
def wa(df):
    return ((df.life * df.originated_balance).sum()
            / df.originated_balance.sum())
print(f"Vintages with >= 12 months: {mature.sum()}")
gl, nl = wa(gross[mature]), wa(net[mature])
print(f"Base-case lifetime gross loss : {gl:.2f}%")
print(f"Base-case lifetime net loss   : {nl:.2f}%")
print(f"Implied recovery rate         : "
      f"{100 * (1 - nl / gl):.1f}%")
print("Projected lifetime net loss by year of origination")
net["year"] = net.vintage.str[:4]
for y, d in net[mature].groupby("year"):
    print(f"  {y}: {wa(d):.2f}%")
