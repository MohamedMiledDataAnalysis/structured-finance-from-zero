"""Chapter 23 - allocate the Class A order book of Thames
Residential 2027-1 and compare the blended cost of funding
with the pool yield (illustrative SONIA 3.75%, swap 3.30%).
Run from the book folder:
  python3 ch23/python/ch23_allocation.py \
      data/ch23_thames_order_book.csv \
      data/thames_residential_2027_1_tape.csv"""
import sys
from decimal import Decimal as D, ROUND_HALF_UP
import pandas as pd

WEIGHT = {"Asset manager": 1.00, "Insurer or pension": 1.00,
          "Bank treasury": 0.85, "Hedge fund": 0.50}
UNIT = 1_000                      # allocation step (£)

def r2(x):
    return D(str(x)).quantize(D("0.01"), ROUND_HALF_UP)

def allocate(book, size, final_bp):
    lim = book.limit_margin_bp
    ok = book[lim.isna() | (lim <= final_bp)].copy()
    ok["w"] = ok.investor_type.map(WEIGHT)
    wo = ok.w * ok.order_gbp
    ok["raw"] = size * wo / wo.sum()
    ok["floor"] = (ok.raw // UNIT) * UNIT
    left = int((size - ok["floor"].sum()) // UNIT)
    ok["frac"] = ok.raw / UNIT - ok["floor"] / UNIT
    order = ok.sort_values(["frac", "time_entered",
                            "order_id"],
                           ascending=[False, True, True])
    extra = order.index[:left]
    ok["alloc"] = ok["floor"]
    ok.loc[extra, "alloc"] += UNIT
    assert ok.alloc.sum() == size
    assert (ok.alloc <= ok.order_gbp).all()
    return ok

book = pd.read_csv(sys.argv[1])
a = book[book.note_class == "A"]
al = allocate(a, 525_350_000, 62)
m = lambda x: f"{x:>13,.0f}"
print("Class A orders received   :", len(a),
      m(a.order_gbp.sum()))
print("Orders valid at SONIA+62bp:", len(al),
      m(al.order_gbp.sum()))
cov = al.order_gbp.sum() / 525_350_000
print(f"Coverage at final spread  : {cov:.2f}x")
print(f"{'Investor type':<19}{'Orders':>13}{'Allocated':>13}"
      f"{'Fill':>8}")
for t, g in al.groupby("investor_type"):
    o, x = g.order_gbp.sum(), g.alloc.sum()
    print(f"{t:<19}{m(o)}{m(x)}{100 * x / o:>7.2f}%")
o, x = al.order_gbp.sum(), al.alloc.sum()
print(f"{'Total':<19}{m(o)}{m(x)}{100 * x / o:>7.2f}%")
for i in ["A01", "A02", "A03"]:
    r = al[al.order_id == i].iloc[0]
    print(f"{i}  {r.investor_type:<19}{m(r.order_gbp)}"
          f"{m(r.alloc)}")

# ---- blended cost of funding against the pool yield ----
S, SWAP = D("0.0375"), D("0.0330")      # illustrative
notes = {"A": ("553000000", "0.62"), "B": ("31800000", "1.10"),
         "C": ("19100000", "1.50"), "D": ("12700000", "2.20"),
         "E": ("9500000", "3.50")}
bal = sum(D(b) for b, m in notes.values())
wam = sum(D(b) * D(m) for b, m in notes.values()) / bal
note_int = sum(D(b) * (S + D(m) / 100)
               for b, m in notes.values())
tape = pd.read_csv(sys.argv[2])
pool = sum(D(str(x)) for x in tape.current_balance)
pool_int = sum(D(str(b)) * D(str(r)) / 100 for b, r in
               zip(tape.current_balance, tape.current_rate))
fixed = sum(D(str(b)) for b, p in
            zip(tape.current_balance, tape.product_type)
            if "Fixed" in p)
swap_net = fixed * (S - SWAP)
fees = D("225000") + r2(pool * D("0.0015"))
profit = D("4000")
xs = pool_int + swap_net - note_int - fees - profit
pct = lambda x: f"{100 * x / pool:8.4f}%"
g = lambda x: f"{r2(x):>14,}"
print("Weighted average margin A-E:", f"{wam:.4f}%")
for lab, x in [("Note interest A-E, 1 year", note_int),
               ("Pool interest, 1 year", pool_int),
               ("Swap net receipt, 1 year", swap_net),
               ("Senior expenses + profit", fees + profit),
               ("Annual excess spread", xs)]:
    print(f"{lab:<27}:", g(x), pct(x))
