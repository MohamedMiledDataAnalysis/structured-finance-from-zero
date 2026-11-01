"""Chapter 35 - SEC-SA risk weights for the Thames notes.

Usage (from the book folder):
  python3 ch35/python/ch35_sec_sa.py \
      data/thames_residential_2027_1_tape.csv

Steps
1. Risk weight of each loan under the UK standardised
   approach from 1 January 2027 (loan-splitting): 20% on the
   part of the balance up to 55% of the property value, 75%
   (retail) on the rest.
2. KSA = 8% x risk-weighted assets / underlying exposures.
   The funded general reserve (GBP 9,391,500.00) counts as a
   tranche and its cash as an underlying exposure (CRR
   Article 256(3)); the cash takes a 20% risk weight
   (short-term exposure to the account bank, an assumption).
3. W = share of defaulted exposures (90+ days past due).
4. SEC-SA formula (CRR Article 261; STS: Article 262) for
   Classes A to E, STS (p = 0.5) and non-STS (p = 1).
"""
import math
import sys

import pandas as pd

RESERVE = 9_391_500.00          # funded general reserve
CASH_RW = 0.20                  # assumed RW of reserve cash
CLASSES = [("A", 553_000_000.00), ("B", 31_800_000.00),
           ("C", 19_100_000.00), ("D", 12_700_000.00),
           ("E", 9_500_000.00), ("Z", 9_571_146.31)]


def loan_rwa(balance, value):
    """Loan-splitting: 20% up to 55% of value, 75% above."""
    secured = min(balance, 0.55 * value)
    return 0.20 * secured + 0.75 * (balance - secured)


def k_ssfa(a_pt, d_pt, ka, p):
    a = -1.0 / (p * ka)
    u = d_pt - ka
    l = max(a_pt - ka, 0.0)
    return (math.exp(a * u) - math.exp(a * l)) / (a * (u - l))


def sec_sa_rw(a_pt, d_pt, ka, p, floor):
    if d_pt <= ka:
        return 12.5                        # 1,250%
    if a_pt >= ka:
        return max(floor, 12.5 * k_ssfa(a_pt, d_pt, ka, p))
    w_below = (ka - a_pt) / (d_pt - a_pt)
    w_above = (d_pt - ka) / (d_pt - a_pt)
    rw = w_below * 12.5 + w_above * 12.5 * k_ssfa(
        a_pt, d_pt, ka, p)
    return max(floor, rw)


def main(path):
    tape = pd.read_csv(path)
    rwa = [loan_rwa(b, v) for b, v in
           zip(tape.current_balance, tape.original_valuation)]
    pool = round(tape.current_balance.sum(), 2)
    loan_rwa_total = sum(rwa)
    total = pool + RESERVE
    ksa = 0.08 * (loan_rwa_total + CASH_RW * RESERVE) / total
    defaulted = tape.loc[tape.months_in_arrears >= 3,
                         "current_balance"].sum()
    w = defaulted / pool
    ka = (1 - w) * ksa + w * 0.5

    print(f"Pool balance (GBP)       : {pool:.2f}")
    print(f"Reserve fund (GBP)       : {RESERVE:.2f}")
    print(f"Loan RWA (GBP)           : {loan_rwa_total:.2f}")
    print(f"Average loan risk weight : "
          f"{loan_rwa_total / pool * 100:.2f}%")
    print(f"KSA                      : {ksa * 100:.4f}%")
    print(f"W                        : {w:.4f}")
    print(f"KA                       : {ka * 100:.4f}%")
    print("Class  A (%)    D (%)    RW STS  RW non-STS")
    # Order of loss absorption: Z, then reserve, then E ... A
    above = total            # balance of tranches at/above
    rows = []
    for name, amount in CLASSES[:5]:
        d_pt = above / total
        above -= amount
        a_pt = above / total
        sts_floor = 0.10 if name == "A" else 0.15
        rw_s = sec_sa_rw(a_pt, d_pt, ka, 0.5, sts_floor)
        rw_n = sec_sa_rw(a_pt, d_pt, ka, 1.0, 0.15)
        rows.append((name, a_pt, d_pt, rw_s, rw_n))
        print(f"{name:<5}{a_pt * 100:7.4f} {d_pt * 100:8.4f}"
              f" {rw_s * 100:8.2f}% {rw_n * 100:9.2f}%")
    z_d = CLASSES[5][1] / total
    print(f"Z    D = {z_d * 100:.4f}% <= KA, RW = 1250.00%")
    print("Capital per GBP 1m held (STS / non-STS):")
    for name, _, _, rw_s, rw_n in rows:
        cap_s = round(rw_s * 0.08 * 1_000_000, 2)
        cap_n = round(rw_n * 0.08 * 1_000_000, 2)
        print(f"  {name}: {cap_s:10.2f} / {cap_n:10.2f}")


if __name__ == "__main__":
    main(sys.argv[1])
