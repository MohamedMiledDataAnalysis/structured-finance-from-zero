"""Chapter 27: Kingsbridge daily collections report and the Thames issuer transaction account statement,
cut-off 1 Feb 2027 to the first IPD (15 Jun 2027). Seed 20261127.
Rules used (documented in Chapter 27):
- monthly collection totals (interest + arrears interest + scheduled principal + prepayments + recoveries) come
  from thames_performance_monthly.csv; each month's total is spread over its business days (Dirichlet weights)
  and rounded to the penny, the last business day absorbing the rounding;
- receipts of 1 Feb - 17 Mar 2027 (before closing) are paid over by Kingsbridge in one transfer on the
  closing date, 18 Mar 2027; from closing, each day's receipts are swept to the issuer account on the
  next business day; one exception: receipts of 20 Apr 2027 swept on 22 Apr 2027 (payment-system outage);
- on 15 Apr 2027 the April payment of KBS-000417 (GBP 1,006.36) was collected twice by error; the duplicate
  is in the 15 Apr receipts and was refunded to the borrower under the Direct Debit Guarantee; Kingsbridge's
  bank recovered it from the issuer account on 7 May 2027 (indemnity claim). The servicer's April collections
  exclude the duplicate;
- IPD payments of 15 Jun 2027 come from data/thames_ipd_results.csv (row 1). The general reserve is held on a
  separate reserve account; the issuer profit (GBP 1,000) stays on the transaction account.
Run from the book folder:  python3 tools/gen_ch27_bank_statement.py data
Writes data/ch27_thames_daily_collections.csv and data/ch27_thames_bank_statement_ipd1.csv."""
import sys, datetime as dt
from decimal import Decimal as D, ROUND_HALF_UP
import numpy as np, pandas as pd
Dd = sys.argv[1]; rng = np.random.default_rng(20261127)
r2 = lambda x: D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)
HOLS = {dt.date.fromisoformat(x) for x in ["2027-01-01", "2027-03-26", "2027-03-29", "2027-05-03", "2027-05-31",
                                           "2027-08-30"]}
bd = lambda d: d.weekday() < 5 and d not in HOLS
def next_bd(d, n=1):
    while n:
        d += dt.timedelta(days=1); n -= bd(d)
    return d
perf = pd.read_csv(f"{Dd}/thames_performance_monthly.csv", dtype=str).set_index("collection_period")
F = ["interest_collected", "arrears_interest_recovered", "scheduled_principal", "prepayments", "principal_recoveries"]
CLOSING = dt.date(2027, 3, 18); IPD = dt.date(2027, 6, 15); DUP = D("1006.36")
rec = []
for per in ["2027-02", "2027-03", "2027-04", "2027-05", "2027-06"]:
    tot = sum(D(perf.loc[per, f]) for f in F)
    y, m = map(int, per.split("-"))
    days = [dt.date(y, m, 1) + dt.timedelta(days=i) for i in range(31)]
    days = [d for d in days if d.month == m and bd(d)]
    w = rng.dirichlet(np.full(len(days), 6.0))
    amts = [r2(tot * D(repr(float(x)))) for x in w[:-1]]
    amts.append(tot - sum(amts))
    for d, a in zip(days, amts):
        if d == dt.date(2027, 4, 15): a += DUP
        if d < CLOSING: t = CLOSING
        elif d == dt.date(2027, 4, 20): t = next_bd(d, 2)
        else: t = next_bd(d)
        rec.append(dict(receipt_date=d, collection_period=per, amount=a, transfer_date=t,
                        duplicate_included=DUP if d == dt.date(2027, 4, 15) else D(0)))
dc = pd.DataFrame(rec)
lag = []
for r in dc.itertuples():
    n, d = 0, r.receipt_date
    while d < r.transfer_date:
        d += dt.timedelta(days=1); n += bd(d)
    lag.append(n)
dc["business_days_to_transfer"] = lag
dc = dc[dc.transfer_date <= IPD]
fmt = lambda df, cols: df.assign(**{c: df[c].map(lambda v: f"{v:.2f}") for c in cols})
fmt(dc, ["amount", "duplicate_included"]).to_csv(f"{Dd}/ch27_thames_daily_collections.csv", index=False)
# statement
lines = []
pre = dc[dc.receipt_date < CLOSING].amount.sum()
lines.append((CLOSING, "Kingsbridge: collections 1 Feb - 17 Mar 2027 paid over at closing", D(0), pre))
for t, g in dc[dc.receipt_date >= CLOSING].groupby("transfer_date"):
    lines.append((t, "Kingsbridge: collections sweep", D(0), sum(g.amount)))
lines.append((dt.date(2027, 5, 7), "Direct Debit indemnity claim KBS-000417 (duplicate 15 Apr)", DUP, D(0)))
res = pd.read_csv(f"{Dd}/thames_ipd_results.csv", dtype=str).iloc[0]
g = lambda k: D(res[k])
ipd = [("Northgate Bank plc: swap net amount", D(0), g("swap_net_received")),
       ("Albion Trustee Services: trustee fee", g("r01_trustee"), D(0)),
       ("Albion Bank: paying agent and agent bank fee", g("r02_paying_agent"), D(0)),
       ("Meridian: corporate services fee", g("r02_corporate_services"), D(0)),
       ("Kingsbridge: cash management fee", g("r02_cash_manager"), D(0)),
       ("Kingsbridge: servicing fee", g("r02_servicer"), D(0)),
       ("Issuer expenses (listing, audit, ratings)", g("r02_other_expenses"), D(0)),
       ("Paying agent: Class A interest and principal", g("r05_class_a_interest") + g("class_a_principal"), D(0)),
       ("Paying agent: Class B interest", g("r07_class_b_interest"), D(0)),
       ("Paying agent: Class C interest", g("r09_class_c_interest"), D(0)),
       ("Paying agent: Class D interest", g("r11_class_d_interest"), D(0)),
       ("Paying agent: Class E interest", g("r13_class_e_interest"), D(0)),
       ("Kingsbridge: subordinated loan interest and principal",
        g("r18_sub_loan_interest") + g("r18_sub_loan_principal"), D(0))]
lines += [(IPD, a, b, c) for a, b, c in ipd]
st = pd.DataFrame(lines, columns=["date", "description", "debit", "credit"])
st["k"] = range(len(st)); st = st.sort_values(["date", "k"]).drop(columns="k")
bal, b = [], D(0)
for r in st.itertuples():
    b = b + r.credit - r.debit; bal.append(b)
st["balance"] = bal
fmt(st, ["debit", "credit", "balance"]).to_csv(f"{Dd}/ch27_thames_bank_statement_ipd1.csv", index=False)
print(st.to_string()); print("max lag from closing:", dc[dc.receipt_date >= CLOSING].business_days_to_transfer.max())
