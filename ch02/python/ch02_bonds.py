"""Chapter 2 - bonds: Thames Class A coupon, fixed-rate bond
price, yield, spread, accrued interest, duration, and the
discount margin of a floating-rate note.
Run from the book folder:
  python3 ch02/python/ch02_bonds.py data/thames_sonia_assumption.csv
"""
import sys
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd


def round2(x):
    """Round to pennies as Excel's ROUND does."""
    return Decimal(x).quantize(Decimal("0.01"),
                               rounding=ROUND_HALF_UP)


# ---- 1. Thames Class A: first interest period ----------
son = pd.read_csv(sys.argv[1])
sonia = Decimal(str(son.compounded_sonia_pct.iloc[0]))
margin = Decimal("0.62")
face_a = Decimal("553000000.00")
days = (date(2027, 6, 15) - date(2027, 3, 18)).days
rate = (sonia + margin) / 100
coupon_a = round2(face_a * rate * days / 365)
per_100k = round2(Decimal(100000) * rate * days / 365)


# ---- 2. A fixed-rate bond: price from yield -------------
def price(cpn, y, n, face=100.0):
    """Price per 100 of an annual-coupon bond
    with n whole years left."""
    pv = sum(cpn / (1 + y) ** t for t in range(1, n + 1))
    return pv + face / (1 + y) ** n


def yield_from_price(p, cpn, n, lo=0.0, hi=0.20):
    """Find the yield that gives price p
    (bisection: halve the interval 100 times)."""
    for _ in range(100):
        mid = (lo + hi) / 2
        if price(cpn, mid, n) > p:
            lo = mid      # price too high: yield too low
        else:
            hi = mid
    return (lo + hi) / 2


cpn, n, y = 4.00, 5, 0.045
p = price(cpn, y, n)
p_market = 98.60
y_market = yield_from_price(p_market, cpn, n)
gilt = 0.039                      # illustrative gilt yield
spread_bp = (y - gilt) * 10000
spread_mkt = (y_market - gilt) * 10000

# accrued interest: 73 days since the last coupon
acc = cpn * 73 / 365
clean = round(p, 2)
dirty = clean + acc

# duration
pv_t = [(t, (cpn if t < n else cpn + 100) / (1 + y) ** t)
        for t in range(1, n + 1)]
mac = sum(t * v for t, v in pv_t) / p
mod = mac / (1 + y)
p_up = price(cpn, y + 0.01, n)
approx_up = p * (1 - mod * 0.01)
pv01 = mod * p / 10000


# ---- 3. Floating-rate note: discount margin ------------
def frn_price(dm, son_pct, qm_pct, q):
    """Price per 100 of a quarterly floating-rate note,
    flat SONIA, repaid in full after q quarters."""
    c = (son_pct + qm_pct) / 4
    d = 1 + (son_pct + dm) / 400
    return sum(c / d ** k for k in range(1, q + 1)) \
        + 100 / d ** q


def dm_from_price(px, son_pct, qm_pct, q):
    lo, hi = -5.0, 10.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if frn_price(mid, son_pct, qm_pct, q) > px:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


# ---- 4. Amortising bond: 20 repaid each year ----------
out_bal = [100 - 20 * k for k in range(5)]   # start of year
amort_int = sum(b * cpn / 100 for b in out_bal)
wal = sum(t * 20 for t in range(1, 6)) / 100

s, qm, q = float(sonia), float(margin), 20
dm_par = dm_from_price(100.0, s, qm, q)
dm_995 = dm_from_price(99.50, s, qm, q)

print("1. Thames Class A, first interest period")
print(f"   Days: {days}   coupon rate: {rate * 100:.2f}%")
print(f"   Interest on Class A   : {coupon_a:,}")
print(f"   Interest per 100,000  : {per_100k:,}")
print("2. Fixed-rate bond: 4.00% annual, 5 years")
print(f"   Price at 4.50% yield  : {p:.4f}")
print(f"   Yield at price 98.60  : {y_market * 100:.4f}%")
print(f"   Spread over gilt 3.90%: {spread_bp:.0f} bp"
      f" (at 98.60: {spread_mkt:.2f} bp)")
print(f"   Accrued (73 days) {acc:.4f}"
      f"  clean {clean:.2f}  dirty {dirty:.2f}")
print(f"   Duration: Macaulay {mac:.4f} years,"
      f" modified {mod:.4f}")
print(f"   Price at 5.50%: exact {p_up:.4f},"
      f" estimate {approx_up:.4f}")
print(f"   PV01 per 100          : {pv01:.4f}")
print("3. Floating-rate note, SONIA + 0.62%, 20 quarters")
print(f"   Discount margin: {dm_par:.4f}% at 100.00,"
      f" {dm_995:.4f}% at 99.50")
print("4. Amortising bond: 100 repaid 20 a year, 4.00%")
print(f"   Total interest {amort_int:.2f}"
      f" (bullet {cpn * n:.2f}), WAL {wal:.2f} years")
