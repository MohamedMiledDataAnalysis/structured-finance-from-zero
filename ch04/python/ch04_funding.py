"""Chapter 4 - why securitise: the cost of Thames funding
compared with other sources, and a warehouse-to-term
illustration. All market rates are ILLUSTRATIVE.
Run from the book folder:
  python3 ch04/python/ch04_funding.py
"""
from decimal import Decimal, ROUND_HALF_UP


def round2(x):
    """Round to pennies as Excel's ROUND does."""
    return Decimal(str(x)).quantize(Decimal("0.01"),
                                    rounding=ROUND_HALF_UP)


SONIA = 3.75                      # % a year, illustrative
# Thames Classes A-E: amount (GBP) and margin (% over SONIA)
notes = {"A": (553_000_000.00, 0.62),
         "B": (31_800_000.00, 1.10),
         "C": (19_100_000.00, 1.50),
         "D": (12_700_000.00, 2.20),
         "E": (9_500_000.00, 3.50)}
total = sum(a for a, m in notes.values())
wa_margin = sum(a * m for a, m in notes.values()) / total

# running costs paid to third parties (fees in the Deal Fact Sheets, Appendix D);
# cash management and servicing go to Kingsbridge itself
third_party = 25_000 + 20_000 + 10_000 + 120_000 + 4 * 1_000
UPFRONT, YEARS = 3_000_000.00, 5   # illustrative
running_pct = third_party / total * 100
upfront_pct = UPFRONT / YEARS / total * 100
all_in = wa_margin + running_pct + upfront_pct
interest = round2(total * (SONIA + wa_margin) / 100)

# other sources, spread over SONIA (illustrative)
sources = [("Retail savings (rate 4.10%)", 4.10 - SONIA),
           ("Covered bond, 5 years", 0.45),
           ("Thames RMBS, all-in", all_in)]

# warehouse to term (illustrative non-bank lender)
POOL, ADVANCE, WH_MARGIN = 300_000_000.00, 0.90, 1.75
senior = POOL * ADVANCE
wh_6m = round2(senior * (SONIA + WH_MARGIN) / 100
               * 182 / 365)
saving = round2(senior * (WH_MARGIN - wa_margin) / 100)

print("1. Thames Classes A-E")
print(f"   Total amount           : {total:,.2f}")
print(f"   Weighted average margin: {wa_margin:.4f}%")
print(f"   Annual interest at SONIA {SONIA:.2f}%: {interest:,}")
print("2. All-in cost of Thames funding, % a year")
print(f"   Note margin            : {wa_margin:.4f}%")
print(f"   Third-party running    : {running_pct:.4f}%"
      f"  ({third_party:,.2f} a year)")
print(f"   Upfront costs / {YEARS} yrs  : {upfront_pct:.4f}%")
print(f"   All-in spread          : SONIA + {all_in:.4f}%")
print(f"   All-in rate            : {SONIA + all_in:.4f}%")
print("3. Spread over SONIA by source (illustrative)")
for name, spr in sources:
    print(f"   {name:<28}: {spr:.4f}%")
print("4. Warehouse to term (illustrative)")
print(f"   Senior warehouse funding: {senior:,.2f}")
print(f"   Interest, 182 days      : {wh_6m:,}")
print(f"   Saving a year at term   : {saving:,}")
