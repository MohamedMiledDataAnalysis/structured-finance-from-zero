# Chapter 25 - Thames arrears roll-rate matrix and
# repossession recoveries.
# Run from the book folder:
#   python3 ch25/python/ch25_arrears.py \
#       data/ch25_thames_arrears_states.csv
# Also reads data/ch25_thames_repossessions.csv.
import sys, os
from decimal import Decimal as D, ROUND_HALF_UP
import numpy as np
import pandas as pd

def r2(x):
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)

# state codes: 0 up to date, 1..11 months in arrears,
# -1 redeemed, -2 property sold after possession
BUCKETS = [("Current", 0, 0), ("1 month", 1, 1),
           ("2 months", 2, 2), ("3m+", 3, 11),
           ("Left", -2, -1)]

def roll_matrix(states):
    x = states.iloc[:, 1:].to_numpy()
    frm, to = x[:, :-1], x[:, 1:]       # month t, month t+1
    m = np.zeros((4, 5), dtype=int)
    for i, (_, lo, hi) in enumerate(BUCKETS[:4]):
        fi = (frm >= lo) & (frm <= hi)
        for j, (_, lo2, hi2) in enumerate(BUCKETS):
            m[i, j] = (fi & (to >= lo2) & (to <= hi2)).sum()
    return m

def recovery(row):
    """Sale proceeds of one repossessed property."""
    idx = D(1.02) ** (D(row.months_since_cutoff) / 12)
    value = D(str(row.original_valuation)) * idx
    gross = r2(value * D("0.70"))       # forced-sale price
    net = r2(value * D("0.70") * D("0.95"))  # less 5% costs
    bal = D(str(row.balance_at_sale))
    arr = D(str(row.arrears_owed))
    prin = min(net, bal)
    ints = max(min(net - bal, arr), D(0))
    return dict(index=idx, gross=gross, costs=gross - net,
                net=net, balance=bal, arrears=arr,
                principal=prin, arrears_int=ints,
                loss=max(bal - net, D(0)),
                surplus=max(net - bal - arr, D(0)))

if __name__ == "__main__":
    st = pd.read_csv(sys.argv[1])
    m = roll_matrix(st)
    print("Roll-rate matrix: loan-months, Feb 2027-Jan 2029")
    print(f"{'From / To':<10}" + "".join(
        f"{b[0]:>10}" for b in BUCKETS))
    for i in range(4):
        print(f"{BUCKETS[i][0]:<10}" + "".join(
            f"{v:>10,}" for v in m[i]))
    print("Roll rates (% of each row)")
    for i in range(4):
        pct = [r2(D(int(v)) * 100 / int(m[i].sum()))
               for v in m[i]]
        print(f"{BUCKETS[i][0]:<10}" + "".join(
            f"{p:>10}" for p in pct))
    rp = pd.read_csv(os.path.join(os.path.dirname(
        sys.argv[1]), "ch25_thames_repossessions.csv"))
    per = pd.PeriodIndex(rp.collection_period, freq="M")
    rp["months_since_cutoff"] = [
        (p - pd.Period("2027-01", "M")).n for p in per]
    res = [recovery(r) for r in rp.itertuples()]
    one = res[list(rp.loan_id).index("KBS-001411")]
    print("KBS-001411: net proceeds", f"{one['net']:,.2f}",
          "loss", f"{one['loss']:,.2f}")
    tb = sum(r["balance"] for r in res)
    tl = sum(r["loss"] for r in res)
    print("All", len(res), "properties sold")
    tot = {"balance at sale": tb,
           "principal recovered":
               sum(r["principal"] for r in res),
           "arrears interest recovered":
               sum(r["arrears_int"] for r in res),
           "realised losses": tl,
           "surplus paid to borrowers":
               sum(r["surplus"] for r in res)}
    for t, v in tot.items():
        print(f"  {t:<26}{v:>14,.2f}")
    print(f"  {'loss severity':<26}"
          f"{r2(tl * 100 / tb):>13}%")
