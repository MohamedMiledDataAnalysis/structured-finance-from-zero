"""Chapter 12 - Annualised excess spread of Thames Residential
2027-1 at closing, and its sensitivity to rates and prepayments.
ILLUSTRATIVE base case: compounded SONIA flat 3.75%, Bank Rate
3.75%, SVR 7.49%. All figures are annual run-rates on closing
balances (rate x balance), not a forecast.
Run from the book folder:
  python3 ch12/python/ch12_excess_spread.py \
      data/thames_residential_2027_1_tape.csv
"""
import sys
from decimal import Decimal as D, ROUND_HALF_UP
import pandas as pd

def round2(x):
    """Round to pennies as Excel's ROUND does."""
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)

NOTES = {"A": ("553000000.00", "0.62"),
         "B": ("31800000.00", "1.10"),
         "C": ("19100000.00", "1.50"),
         "D": ("12700000.00", "2.20"),
         "E": ("9500000.00", "3.50")}
FIXED_FEES = D(25000 + 20000 + 10000 + 50000 + 120000)
SERVICING = D("0.15")       # % a year of pool balance
ISSUER_PROFIT = D(4000)     # GBP 1,000 per IPD x 4
SWAP_NOTIONAL = D("542600271.48")
SUBLOAN, SUBLOAN_MARGIN = D("9391500.00"), D("4.00")

def excess_spread(tape, sonia=D("3.75"), swap=D("3.30"),
                  bank_shift=D(0), svr=None, a_paydown=D(0)):
    """Annual excess spread (GBP) and its parts.
    tape: rows with current_balance, current_rate (str)
    and product_type. bank_shift moves tracker rates;
    svr replaces the SVR loans' rate; a_paydown
    reduces Class A (used when loans leave the pool)."""
    bal = tape.current_balance.map(D)
    rate = tape.current_rate.map(D)
    trk = tape.product_type == "Tracker"
    rate = rate.where(~trk, rate + bank_shift)
    if svr is not None:
        rate = rate.where(tape.product_type != "SVR", svr)
    pool = sum(bal)
    p = {"pool": pool,
         "wa_rate": sum(bal * rate) / pool,
         "pool_int": round2(sum(bal * rate) / 100),
         "swap_pay": round2(SWAP_NOTIONAL * swap / 100),
         "swap_rec": round2(SWAP_NOTIONAL * sonia / 100),
         "fees": round2(FIXED_FEES + ISSUER_PROFIT
                        + pool * SERVICING / 100)}
    p["notes"] = D(0)
    for c, (amt, m) in NOTES.items():
        amt = D(amt) - (a_paydown if c == "A" else 0)
        p["notes"] += round2(amt * (sonia + D(m)) / 100)
    p["es"] = (p["pool_int"] + p["swap_rec"] - p["swap_pay"]
               - p["fees"] - p["notes"])
    p["sub"] = round2(SUBLOAN * (sonia + SUBLOAN_MARGIN) / 100)
    return p

def m(x):
    return f"{x:,.2f}"

if __name__ == "__main__":
    tape = pd.read_csv(sys.argv[1], dtype={
        "current_balance": str, "current_rate": str})
    b = excess_spread(tape)
    lines = [
        ("Pool balance", m(b["pool"])),
        ("WA loan rate (%)", f"{b['wa_rate']:.4f}"),
        ("Pool interest", m(b["pool_int"])),
        ("Swap: issuer receives", m(b["swap_rec"])),
        ("Swap: issuer pays", m(-b["swap_pay"])),
        ("Senior fees and profit", m(-b["fees"])),
        ("Class A-E interest", m(-b["notes"])),
        ("Excess spread", m(b["es"])),
        ("  as % of pool", f"{b['es'] / b['pool'] * 100:.4f}"),
        ("Subordinated loan int.", m(-b["sub"])),
        ("Left for items 18-19", m(b["es"] - b["sub"]))]
    print("Annual run-rate at closing (GBP, illustrative)")
    for k, v in lines:
        print(f"{k:<24}{v:>18}")
    svr = tape.product_type == "SVR"
    svr_bal = sum(tape.current_balance[svr].map(D))
    rev = tape[tape.product_type.str.contains("Fixed")
               & (tape.fixed_rate_end_date < "2028-01-01")]
    up = round2(sum(rev.current_balance.map(D) *
                    (D("7.49") - rev.current_rate.map(D)))
                / 100)
    scen = [
        ("SONIA, Bank Rate +1%",
         excess_spread(tape, sonia=D("4.75"),
                       bank_shift=D(1))),
        ("SONIA, Bank Rate -1%",
         excess_spread(tape, sonia=D("2.75"),
                       bank_shift=D(-1))),
        ("SONIA +0.25% only",
         excess_spread(tape, sonia=D("4.00"))),
        ("SVR cut to 6.49%",
         excess_spread(tape, svr=D("6.49"))),
        ("All SVR loans prepay",
         excess_spread(tape[~svr], a_paydown=svr_bal))]
    print()
    print("Sensitivities (annual excess spread, GBP)")
    for k, s in scen:
        print(f"{k:<24}{m(s['es']):>18}"
              f"{m(s['es'] - b['es']):>16}")
    print(f"{'2027 fixed-end loans':<24}"
          f"{m(b['es'] + up):>18}{m(up):>16}")
    print(f"  ({len(rev)} loans, {m(sum(rev.current_balance.map(D)))}"
          " stay on SVR)")
    print(f"  (SVR loans: {int(svr.sum())},"
          f" {m(svr_bal)})")
