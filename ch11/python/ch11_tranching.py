"""Chapter 11 - Tranching the Thames Residential 2027-1 pool.
Capital structure (% of pool, attachment, detachment, thickness),
loss allocation across pool-loss scenarios, and the 5% vertical
slice retained by Kingsbridge.
Run from the book folder:
  python3 ch11/python/ch11_tranching.py \
      data/thames_residential_2027_1_tape.csv
"""
import sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

def round2(x):
    """Round to pennies as Excel's ROUND does."""
    return Decimal(x).quantize(Decimal("0.01"),
                               rounding=ROUND_HALF_UP)

# Notes from the Deal Fact Sheets (Appendix D), senior first (GBP)
NOTES = [("A", "553000000.00"), ("B", "31800000.00"),
         ("C", "19100000.00"), ("D", "12700000.00"),
         ("E", "9500000.00"), ("Z", "9571146.31")]
SCEN = ["0.5", "1", "2", "3", "5", "8", "10", "13",
        "15", "20"]

def structure(notes, pool):
    """Attachment = notes junior to the class / pool;
    detachment = attachment + class size / pool."""
    rows, below = [], Decimal(0)
    for cls, amt in reversed(notes):   # junior first
        amt = Decimal(amt)
        rows.append(dict(cls=cls, amount=amt,
                         below=below,
                         pct=amt / pool * 100,
                         att=below / pool * 100,
                         det=(below + amt) / pool * 100))
        below += amt
    return pd.DataFrame(rows[::-1])    # senior first

def allocate(cs, loss):
    """Loss to each class: what exceeds the notes
    below it, capped at the class size."""
    return {r.cls: min(r.amount,
                       max(Decimal(0), loss - r.below))
            for r in cs.itertuples()}

def kept(cls, x):
    """Kingsbridge's share: 5% of Classes A-E (vertical
    slice) and all of Class Z."""
    return x if cls == "Z" else round2(x * Decimal("0.05"))

def pct4(x):
    return f"{x.quantize(Decimal('0.0001'), ROUND_HALF_UP):.4f}"

def money(x):
    return f"{x:,.2f}"

if __name__ == "__main__":
    tape = pd.read_csv(sys.argv[1], dtype={"current_balance": str})
    pool = sum(Decimal(b) for b in tape.current_balance)
    cs = structure(NOTES, pool)
    print("Pool balance at cut-off:", money(pool))
    print("Total of notes          :",
          money(sum(cs.amount)))
    print()
    print(f"{'Cl':<3}{'Amount':>16}{'% pool':>10}"
          f"{'Attach':>10}{'Detach':>10}")
    for r in cs.itertuples():
        print(f"{r.cls:<3}{money(r.amount):>16}"
              f"{pct4(r.pct):>10}{pct4(r.att):>10}"
              f"{pct4(r.det):>10}")
    print()
    print("Loss written off each class (% of class)")
    print(f"{'Loss%':>5}{'Loss (GBP)':>16}" +
          "".join(f"{c:>7}" for c in "ZEDCBA"))
    for s in SCEN:
        loss = round2(pool * Decimal(s) / 100)
        a = allocate(cs, loss)
        amt = dict(zip(cs.cls, cs.amount))
        cells = "".join(
            f"{float(a[c] / amt[c] * 100):>7.2f}"
            for c in "ZEDCBA")
        print(f"{s:>5}{money(loss):>16}{cells}")
    print()
    loss = round2(pool * Decimal("3") / 100)
    a = allocate(cs, loss)
    print("3% scenario: who bears the loss (GBP)")
    print(f"{'Cl':<3}{'Class loss':>15}{'Kingsbridge':>14}"
          f"{'Investors':>15}")
    tk = Decimal(0)
    for c in "ZEDCBA":
        k = kept(c, a[c])
        tk += k
        print(f"{c:<3}{money(a[c]):>15}{money(k):>14}"
              f"{money(a[c] - k):>15}")
    print(f"{'Tot':<3}{money(sum(a.values())):>15}"
          f"{money(tk):>14}"
          f"{money(sum(a.values()) - tk):>15}")
    held = [kept(c, x) for c, x in zip(cs.cls, cs.amount)]
    print("Kingsbridge holds at closing:", money(sum(held)),
          f"= {pct4(sum(held) / pool * 100)}% of pool")
