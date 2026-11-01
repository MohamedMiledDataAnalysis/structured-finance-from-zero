# Chapter 26 - the real Thames Residential 2027-1 waterfall,
# 8 IPDs (15 Jun 2027 - 15 Mar 2029), per the Deal Fact Sheets.
# Run from the book folder:
#   python3 ch26/python/ch26_waterfall.py \
#       data/thames_performance_monthly.csv
# Also reads, in the same folder:
#   ch26_thames_performance_2029_02.csv,
#   thames_sonia_assumption.csv, ch26_thames_swap_notional.csv.
# Writes data/thames_ipd_results.csv (or the 2nd argument).
import sys, os, datetime as dt
from decimal import Decimal as D, ROUND_HALF_UP
import pandas as pd

def r2(x):
    """Round to pennies, halves away from zero (Excel)."""
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)

# ---------- deal terms (the Deal Fact Sheets) ----------
CLOSING = dt.date(2027, 3, 18)
NOTES = {"A": ("553000000.00", "0.62"),
         "B": ("31800000.00", "1.10"),
         "C": ("19100000.00", "1.50"),
         "D": ("12700000.00", "2.20"),
         "E": ("9500000.00", "3.50"),
         "Z": ("9571146.31", None)}      # Z: no coupon
SWAP_FIXED = D("3.30")                     # % p.a.
RESERVE_REQUIRED = D("9391500.00")
SUB_LOAN_MARGIN = D("4.00")
FEES_PA = {"trustee": D("25000"), "paying_agent": D("10000"),
           "corporate_services": D("20000"),
           "cash_manager": D("50000"),
           "other_expenses": D("120000")}
SERVICING_PCT = D("0.15")                  # % p.a. of pool
ISSUER_PROFIT = D("1000.00")
# collection periods paid on each IPD (first IPD: 4 months)
IPDS = [dt.date(2027, 6, 15), dt.date(2027, 9, 15),
        dt.date(2027, 12, 15), dt.date(2028, 3, 15),
        dt.date(2028, 6, 15), dt.date(2028, 9, 15),
        dt.date(2028, 12, 15), dt.date(2029, 3, 15)]
MONTHS = [["2027-02", "2027-03", "2027-04", "2027-05"],
          ["2027-06", "2027-07", "2027-08"],
          ["2027-09", "2027-10", "2027-11"],
          ["2027-12", "2028-01", "2028-02"],
          ["2028-03", "2028-04", "2028-05"],
          ["2028-06", "2028-07", "2028-08"],
          ["2028-09", "2028-10", "2028-11"],
          ["2028-12", "2029-01", "2029-02"]]
# England and Wales bank holidays 2027-2029
HOLS = {dt.date(*d) for d in [
    (2027, 1, 1), (2027, 3, 26), (2027, 3, 29), (2027, 5, 3),
    (2027, 5, 31), (2027, 8, 30), (2027, 12, 27),
    (2027, 12, 28), (2028, 1, 3), (2028, 4, 14),
    (2028, 4, 17), (2028, 5, 1), (2028, 5, 29),
    (2028, 8, 28), (2028, 12, 25), (2028, 12, 26),
    (2029, 1, 1), (2029, 3, 30), (2029, 4, 2)]}

def is_bd(d):
    return d.weekday() < 5 and d not in HOLS

def mod_following(d):
    x = d
    while not is_bd(x):
        x += dt.timedelta(days=1)
    if x.month != d.month:              # went into next month
        x = d
        while not is_bd(x):
            x -= dt.timedelta(days=1)
    return x

def minus_bd(d, n):
    while n > 0:
        d -= dt.timedelta(days=1)
        n -= is_bd(d)
    return d

def load(perf_path):
    folder = os.path.dirname(perf_path)
    perf = pd.concat([
        pd.read_csv(perf_path, dtype=str),
        pd.read_csv(os.path.join(
            folder, "ch26_thames_performance_2029_02.csv"),
            dtype=str)]).set_index("collection_period")
    son = pd.read_csv(os.path.join(
        folder, "thames_sonia_assumption.csv"), dtype=str)
    swp = pd.read_csv(os.path.join(
        folder, "ch26_thames_swap_notional.csv"), dtype=str)
    return perf, list(son.compounded_sonia_pct.map(D)), \
        list(swp.swap_notional.map(D))

def pay(avail, due):
    """Pay min(available, due); return (paid, left)."""
    p = min(avail, due)
    return p, avail - p

def run(perf, sonia, notional):
    bal = {c: D(a) for c, (a, m) in NOTES.items()}
    pdl = {c: D("0") for c in NOTES}
    reserve, sub_loan = RESERVE_REQUIRED, RESERVE_REQUIRED
    sub_unpaid = D(0)          # unpaid sub-loan interest c/f
    rows, start = [], CLOSING
    for k, ipd in enumerate(IPDS):
        ipd = mod_following(ipd)
        days = (ipd - start).days
        s, yf = sonia[k], D(days) / D(365)
        m = perf.loc[MONTHS[k]]
        col = lambda f: sum(m[f].map(D))
        r = {"ipd": ipd.isoformat(),
             "determination_date": minus_bd(ipd, 5).isoformat(),
             "interest_period_start": start.isoformat(),
             "days": days, "compounded_sonia_pct": s,
             "collection_periods":
                 MONTHS[k][0] + " to " + MONTHS[k][-1]}
        # --- revenue receipts ---
        r["interest_collected"] = col("interest_collected")
        r["arrears_interest_recovered"] = \
            col("arrears_interest_recovered")
        r["revenue_collections"] = (r["interest_collected"]
            + r["arrears_interest_recovered"])
        n = notional[k]
        fixed = r2(n * SWAP_FIXED / 100 * yf)
        flt = r2(n * s / 100 * yf)
        r.update(swap_notional=n, swap_fixed_leg=fixed,
                 swap_floating_leg=flt,
                 swap_net_received=max(flt - fixed, D(0)))
        r["reserve_brought_forward"] = reserve
        avail = (r["revenue_collections"]
                 + r["swap_net_received"] + reserve)
        r["available_revenue"] = avail
        # --- amounts due ---
        fee = lambda k: r2(FEES_PA[k] * days / 365)
        serv = sum(r2(D(x) * SERVICING_PCT / 100 / 12)
                   for x in m["opening_balance"])
        due = {"r01_trustee": fee("trustee"),     # Act/365
               "r02_paying_agent": fee("paying_agent"),
               "r02_corporate_services":
                   fee("corporate_services"),
               "r02_cash_manager": fee("cash_manager"),
               "r02_servicer": serv,
               "r02_other_expenses": fee("other_expenses"),
               "r03_issuer_profit": ISSUER_PROFIT,
               "r04_swap_net_payment": max(fixed - flt, D(0))}
        nint = {c: r2(bal[c] * (s + D(mg)) / 100 * yf)
                for c, (a, mg) in NOTES.items() if mg}
        # --- PDL debit: losses, Z sub-ledger first ---
        loss = col("realised_losses")
        r["realised_losses"] = loss
        left = loss
        for c in "ZEDCBA":
            d = min(left, bal[c] - pdl[c])
            pdl[c] += d
            left -= d
        # --- revenue priority of payments ---
        paid = {}
        two = ["r02_paying_agent", "r02_corporate_services",
               "r02_cash_manager", "r02_servicer",
               "r02_other_expenses"]
        paid["r01_trustee"], avail = pay(avail,
                                         due["r01_trustee"])
        tot2 = sum(due[x] for x in two)
        if avail >= tot2:
            for x in two:
                paid[x] = due[x]
            avail -= tot2
        else:                            # pro rata
            for x in two:
                paid[x] = r2(avail * due[x] / tot2)
            avail -= sum(paid[x] for x in two)
        for x in ("r03_issuer_profit", "r04_swap_net_payment"):
            paid[x], avail = pay(avail, due[x])
        cure = D(0)
        num = {"A": 5, "B": 7, "C": 9, "D": 11, "E": 13}
        for c in "ABCDE":
            i = num[c]
            paid[f"r{i:02d}_class_{c.lower()}_interest"], \
                avail = pay(avail, nint[c])
            p, avail = pay(avail, pdl[c])
            paid[f"r{i+1:02d}_class_{c.lower()}_pdl"] = p
            pdl[c] -= p
            cure += p
        p, avail = pay(avail, RESERVE_REQUIRED)
        paid["r15_reserve_credit"] = p
        reserve = p
        p, avail = pay(avail, pdl["Z"])
        paid["r16_class_z_pdl"] = p
        pdl["Z"] -= p
        cure += p
        paid["r17_sub_swap_termination"] = D(0)
        sl_int = r2(sub_loan * (s + SUB_LOAN_MARGIN) / 100
                    * yf) + sub_unpaid
        paid["r18_sub_loan_interest"], avail = pay(avail,
                                                   sl_int)
        paid["r18_sub_loan_principal"], avail = pay(avail,
                                                    sub_loan)
        sub_loan -= paid["r18_sub_loan_principal"]
        sub_unpaid = sl_int - paid["r18_sub_loan_interest"]
        paid["r19_deferred_consideration"] = avail
        r.update(paid)
        r["reserve_drawn"] = RESERVE_REQUIRED - reserve
        # shortfalls in items 1-5 would be met from principal;
        # stop if that ever happens (not the case on Thames)
        short = sum(due[x] - paid[x] for x in due) \
            + nint["A"] - paid["r05_class_a_interest"]
        assert short == 0, "principal addition amount needed"
        assert all(paid[f"r{num[c]:02d}_class_{c.lower()}"
                        "_interest"] == nint[c] for c in "BCDE")
        # --- principal priority of payments ---
        r["scheduled_principal"] = col("scheduled_principal")
        r["prepayments"] = col("prepayments")
        r["principal_recoveries"] = col("principal_recoveries")
        r["principal_collections"] = (r["scheduled_principal"]
            + r["prepayments"] + r["principal_recoveries"])
        r["pdl_cured_from_revenue"] = cure
        r["principal_addition_amounts"] = D(0)
        pa = r["principal_collections"] + cure
        r["available_principal"] = pa
        for c in "ABCDEZ":
            p, pa = pay(pa, bal[c])
            r[f"class_{c.lower()}_principal"] = p
            bal[c] -= p
        assert pa == 0
        for c in "ABCDEZ":
            r[f"class_{c.lower()}_balance_after"] = bal[c]
        r["notes_total_after"] = sum(bal.values())
        for c in "ABCDEZ":
            r[f"pdl_{c.lower()}_after"] = pdl[c]
        r["reserve_balance_after"] = reserve
        r["sub_loan_balance_after"] = sub_loan
        r["pool_balance_end"] = D(
            m["closing_balance"].iloc[-1])
        r["sub_loan_interest_due"] = sl_int
        r["sub_loan_interest_unpaid_after"] = sub_unpaid
        rows.append(r)
        start = ipd
    return pd.DataFrame(rows)

def money(x):
    return f"{x:,.2f}"

if __name__ == "__main__":
    perf, sonia, notional = load(sys.argv[1])
    res = run(perf, sonia, notional)
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        os.path.dirname(sys.argv[1]), "thames_ipd_results.csv")
    csv = res.copy()
    for c in csv.columns:             # money: always 2 decimals
        if c != "compounded_sonia_pct" and \
                isinstance(csv[c].iloc[0], D):
            csv[c] = csv[c].map(lambda v: f"{r2(v):.2f}")
    csv.to_csv(out, index=False)
    f = res.iloc[0]
    print("First IPD", f.ipd, "- days", f.days,
          "- SONIA", f.compounded_sonia_pct)
    for k in ["revenue_collections", "swap_net_received",
              "reserve_brought_forward", "available_revenue",
              "r02_servicer", "r05_class_a_interest",
              "r07_class_b_interest", "r13_class_e_interest",
              "r15_reserve_credit", "r18_sub_loan_interest",
              "r18_sub_loan_principal",
              "r19_deferred_consideration",
              "available_principal", "class_a_balance_after"]:
        print(f"  {k:<28}{money(f[k]):>17}")
    print("IPD         Avail revenue   Class A paid"
          "    Class A after")
    for _, x in res.iterrows():
        print(f"{x.ipd}{money(x.available_revenue):>16}"
              f"{money(x.class_a_principal):>15}"
              f"{money(x.class_a_balance_after):>17}")
    print("Total realised losses debited to PDL:",
          money(res.realised_losses.sum()))
    print("PDL outstanding after last IPD:",
          money(sum(res.iloc[-1][f"pdl_{c}_after"]
                    for c in "abcdez")))
    print("Wrote", out)
