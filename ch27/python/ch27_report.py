# Chapter 27 - Thames first investor report, cash
# reconciliations and trigger tests for the 8 IPDs.
# Run from the book folder:
#   python3 ch27/python/ch27_report.py \
#       data/thames_ipd_results.csv
# Also reads, in the same folder:
#   thames_performance_monthly.csv,
#   ch26_thames_performance_2029_02.csv,
#   ch27_thames_bank_statement_ipd1.csv,
#   ch27_thames_daily_collections.csv.
import sys, os
from decimal import Decimal as D, ROUND_HALF_UP
import pandas as pd

def r2(x, q="0.01"):
    return D(x).quantize(D(q), rounding=ROUND_HALF_UP)

def mo(x):
    return f"{x:,.2f}"

CUTOFF_POOL = D("635671146.31")
MARGIN = {"A": "0.62", "B": "1.10", "C": "1.50",
          "D": "2.20", "E": "3.50"}
ORIG = {"A": "553000000.00", "B": "31800000.00",
        "C": "19100000.00", "D": "12700000.00",
        "E": "9500000.00", "Z": "9571146.31"}
FIELDS = ["interest_collected", "arrears_interest_recovered",
          "scheduled_principal", "prepayments",
          "principal_recoveries"]

folder = os.path.dirname(sys.argv[1])
rd = lambda f: pd.read_csv(os.path.join(folder, f), dtype=str)
res = pd.read_csv(sys.argv[1], dtype=str)
perf = pd.concat([rd("thames_performance_monthly.csv"),
                  rd("ch26_thames_performance_2029_02.csv")])
perf = perf.set_index("collection_period")
st = rd("ch27_thames_bank_statement_ipd1.csv")
dc = rd("ch27_thames_daily_collections.csv")
for c in ("debit", "credit", "balance"):
    st[c] = st[c].map(D)
dc["amount"] = dc["amount"].map(D)
x = res.iloc[0]
g = lambda k: D(x[k])

# ---- 1. collections to bank statement ----
kb = st.description.str.startswith("Kingsbridge: coll")
credits = st[kb].credit.sum()
ind = st.description.str.contains("indemnity")
indem = st[ind].debit.sum()
june = dc[dc.collection_period == "2027-06"].amount.sum()
bank = credits - indem - june
serv = sum(D(perf.loc[m, f]) for m in
           ["2027-02", "2027-03", "2027-04", "2027-05"]
           for f in FIELDS)
lag = dc[dc.receipt_date >= "2027-03-18"]
lag = lag.business_days_to_transfer.astype(int).max()
print("1. Collections: bank statement to servicer report")
for t, v in [("Credits from Kingsbridge", credits),
             ("less Direct Debit indemnity claim", -indem),
             ("less June receipts (next IPD)", -june),
             ("Feb-May collections per bank", bank),
             ("Feb-May collections per servicer", serv),
             ("Difference", bank - serv)]:
    print(f"  {t:<34}{mo(v):>16}")
print(f"  Longest sweep after closing: {lag} business days"
      " (limit 3)")

# ---- 2. waterfall to bank statement ----
paid = st[st.date == "2027-06-15"].debit.sum()
wf = (g("available_revenue") - g("r15_reserve_credit")
      - g("r03_issuer_profit") + g("available_principal"))
print("2. IPD payments: waterfall to bank statement")
print(f"  {'Paid out per waterfall':<34}{mo(wf):>16}")
print(f"  {'Debits on 15 Jun per statement':<34}"
      f"{mo(paid):>16}")
print(f"  {'Difference':<34}{mo(wf - paid):>16}")
end = st.balance.iloc[-1]
print(f"  {'Balance after the IPD':<34}{mo(end):>16}")
print(f"  {'= June receipts + issuer profit':<34}"
      f"{mo(june + g('r03_issuer_profit')):>16}")

# ---- 3. note table of the first investor report ----
print("3. Notes after the IPD of 15 June 2027")
print(f"{'Class':<6}{'Before':>16}{'Principal':>15}"
      f"{'After':>16}{'Factor':>9}")
for c in "ABCDEZ":
    before = D(ORIG[c])            # first IPD: original
    p = g(f"class_{c.lower()}_principal")
    after = g(f"class_{c.lower()}_balance_after")
    f = r2(after / D(ORIG[c]), "0.000001")
    print(f"{c:<6}{mo(before):>16}{mo(p):>15}"
          f"{mo(after):>16}{f:>9}")
print(f"{'Class':<6}{'Rate %':>8}{'Interest paid':>16}")
for c, n in zip("ABCDE", (5, 7, 9, 11, 13)):
    rate = g("compounded_sonia_pct") + D(MARGIN[c])
    k = f"r{n:02d}_class_{c.lower()}_interest"
    print(f"{c:<6}{rate:>8}{mo(g(k)):>16}")

# ---- 4. tests on every IPD ----
print("4. Tests at each IPD")
print(f"{'IPD':<11}{'Reserve':>14}{'PDL':>6}{'>3m %':>7}"
      f"{'Cum loss %':>11}{'Pool %':>8}")
cum = D(0)
for _, y in res.iterrows():
    last = y.collection_periods[-7:]
    arr = (D(perf.loc[last, "arrears_3_6m_pct"])
           + D(perf.loc[last, "arrears_6m_plus_pct"]))
    cum += D(y.realised_losses)
    pdl = sum(D(y[f"pdl_{c}_after"]) for c in "abcdez")
    pool = r2(D(y.pool_balance_end) * 100 / CUTOFF_POOL)
    print(f"{y.ipd:<11}{mo(D(y.reserve_balance_after)):>14}"
          f"{mo(pdl):>6}"
          f"{arr:>7}"
          f"{r2(cum * 100 / CUTOFF_POOL, '0.0001'):>11}"
          f"{pool:>8}")
