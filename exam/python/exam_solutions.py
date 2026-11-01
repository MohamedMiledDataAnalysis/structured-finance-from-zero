"""Final exam - Medway Residential 2028-1 plc: solutions to Parts B and C.
Run from the book folder:
  python3 exam/python/exam_solutions.py data/exam_medway_tape.csv \
      data/exam_medway_deal_terms.csv data/exam_medway_ipd_inputs.csv
Add --diagnostics to print the figures of the common wrong answers.
Add --json to print the key results as JSON (used by tools/check_exam.py)."""
import csv, sys, json, datetime as dt
from decimal import Decimal as D, ROUND_HALF_UP

def r2(x, q="0.01"):
    return D(x).quantize(D(q), rounding=ROUND_HALF_UP)

def m(x):
    return f"{r2(x):,.2f}"

def add_months(d, n):
    y, mo = divmod(d.month - 1 + n, 12)
    return dt.date(d.year + y, mo + 1, d.day)

ARR_B = ["Current", "1 month", "2 months", "3-5 months", "6+ months", "Unknown"]
LTV_B = ["0-50%", "50-60%", "60-70%", "70-75%", "75-80%", "80-85%", "85-90%", "Over 90%"]
REP_B = ["Repayment", "Interest-only", "Part and part"]
REG_B = ["London", "South East", "East of England", "South West", "West Midlands", "East Midlands",
         "North West", "Yorkshire and the Humber", "North East", "Wales", "Scotland", "Northern Ireland", "Unknown"]
REGION_MAP = {"": "Unknown", "Yorkshire & Humber": "Yorkshire and the Humber"}
ALL = {"dup", "bal", "mat", "ltv", "region", "rate", "arrears"}

def arrears_bucket(a):
    if a < 0: return "Unknown"
    return ["Current", "1 month", "2 months"][a] if a <= 2 else "3-5 months" if a <= 5 else "6+ months"

def ltv_bucket(v):
    for lim, lab in zip([50, 60, 70, 75, 80, 85, 90], LTV_B):
        if v <= lim: return lab
    return "Over 90%"

def prepare(rows, treat=ALL):
    """Return the loans used for reporting. treat = the set of treatments applied.
    The raw rows are never changed: each treated value is a new field."""
    out, seen = [], set()
    for r in rows:
        if "dup" in treat and r["loan_id"] in seen: continue
        seen.add(r["loan_id"])
        o = dict(r)
        bal = D(r["current_balance"])
        if "bal" in treat and bal > D(r["original_balance"]): bal = bal / 10   # decimal shift
        o["bal"] = bal
        orig = dt.date.fromisoformat(r["origination_date"])
        mat = dt.date.fromisoformat(r["maturity_date"])
        if "mat" in treat and mat < orig: mat = add_months(orig, int(r["original_term_months"]))
        rep = dt.date.fromisoformat(r["report_date"])
        o["rem"] = D((mat.year - rep.year) * 12 + mat.month - rep.month)
        o["ltv"] = (r2(bal / D(r["indexed_valuation"]) * 100) if "ltv" in treat else D(r["indexed_ltv"]))
        o["reg"] = REGION_MAP.get(r["region"], r["region"]) if "region" in treat else r["region"]
        o["rate"] = D(r["current_rate"])
        o["rate_ok"] = o["rate"] > 0 or "rate" not in treat
        a = int(r["months_in_arrears"])
        o["arr"] = arrears_bucket(a) if "arrears" in treat else (arrears_bucket(max(a, 0)))
        out.append(o)
    return out

def wa(loans, f, cond=lambda o: True):
    w = [o for o in loans if cond(o)]
    return sum(o["bal"] * o[f] for o in w) / sum(o["bal"] for o in w)

def headline(loans):
    tot = sum(o["bal"] for o in loans)
    return dict(count=len(loans), total=tot, average=r2(tot / len(loans)),
                wa_rate=r2(wa(loans, "rate", lambda o: o["rate_ok"])),
                wa_ltv=r2(wa(loans, "ltv")), wa_rem=r2(wa(loans, "rem")))

def strat(loans, key, buckets):
    tot = sum(o["bal"] for o in loans); res = []
    for b in buckets:
        g = [o for o in loans if key(o) == b]
        bal = sum((o["bal"] for o in g), D(0))
        res.append((b, len(g), bal, r2(bal / tot * 100), r2(wa(g, "ltv")) if g else D("0.00")))
    return res, tot

# ------------------------------------------------------------------ waterfall
def run_ipd(st, inp, T, order=("z", "b", "a"), basis=365):
    d = D(inp["days"]); s = D(T["sonia"])
    rate_a = (s + D(T["margin_a"])) / 100; rate_b = (s + D(T["margin_b"])) / 100
    st = dict(st)
    # 1. PDL debits: Z, then B, then A, each up to its note balance
    loss = D(inp["realised_losses"]); deb = {}
    for c in order:
        room = st[f"class_{c}"] - st[f"pdl_{c}"]
        deb[c] = min(loss, room); st[f"pdl_{c}"] += deb[c]; loss -= deb[c]
    # 2. available revenue receipts: collections + whole reserve
    arr = D(inp["revenue_collections"]) + st["reserve"]
    due = [("(1) Senior fees and expenses", r2(D(T["senior_fees_pa"]) * d / 365) + D(inp["extra_senior_expenses"])),
           ("(2) Servicing fee", r2(st["pool"] * D(T["servicing_pct"]) / 100 * d / 365)),
           ("(3) Class A interest", r2(st["class_a"] * rate_a * d / basis)),
           ("(4) Class A PDL", st["pdl_a"]),
           ("(5) Class B interest", r2(st["class_b"] * rate_b * d / 365) + st["deferred_b"]
            + r2(st["deferred_b"] * rate_b * d / 365)),
           ("(6) Class B PDL", st["pdl_b"]),
           ("(7) Reserve to required amount", D(T["reserve_required"])),
           ("(8) Class Z PDL", st["pdl_z"])]
    pot, lines = arr, []
    for lab, dd in due:
        p = min(dd, pot); pot -= p; lines.append((lab, dd, p))
    lines.append(("(9) Residual to Kingsbridge", pot, pot)); pot = D(0)
    paid = {lab[:3]: p for lab, _, p in lines}
    cure = {"a": paid["(4)"], "b": paid["(6)"], "z": paid["(8)"]}
    deferred = lines[4][1] - lines[4][2]
    res_open = st["reserve"]; res_close = paid["(7)"]
    for c in cure: st[f"pdl_{c}"] -= cure[c]
    # 3. principal waterfall: strictly sequential A -> B -> Z
    prin = D(inp["scheduled_principal"]) + D(inp["prepayments"]) + D(inp["recoveries"])
    apr = prin + sum(cure.values()); left = apr; ppaid = {}
    opening_notes = {c: st[f"class_{c}"] for c in "abz"}
    for c in "abz":
        ppaid[c] = min(left, st[f"class_{c}"]); st[f"class_{c}"] -= ppaid[c]; left -= ppaid[c]
    pool_open = st["pool"]
    st["pool"] = pool_open - prin - D(inp["realised_losses"])
    st["reserve"] = res_close; st["deferred_b"] = deferred
    notes = sum(st[f"class_{c}"] for c in "abz"); pdl = sum(st[f"pdl_{c}"] for c in "abz")
    pdl_open = sum(st[f"pdl_{c}"] + cure[c] - deb[c] for c in "abz")
    checks = [("Revenue: available - allocated", arr - sum(p for _, _, p in lines)),
              ("Principal: available - allocated", apr - sum(ppaid.values())),
              ("PDL: open + debits - cures - close", pdl_open + sum(deb.values()) - sum(cure.values()) - pdl),
              ("Notes: open - principal - close", sum(opening_notes.values()) - sum(ppaid.values()) - notes),
              ("Notes - PDL - pool", notes - pdl - st["pool"])]
    info = dict(arr=arr, apr=apr, prin=prin, deb=deb, cure=cure, deferred=deferred, res_open=res_open,
                res_close=res_close, draw=max(res_open - res_close, D(0)), topup=max(res_close - res_open, D(0)),
                ppaid=ppaid, pool_open=pool_open, notes=notes, pdl=pdl, unallocated_loss=loss)
    return lines, checks, info, st

def load(argv):
    rows = list(csv.DictReader(open(argv[0])))
    T = {r["parameter"]: r["value"] for r in csv.DictReader(open(argv[1]))}
    inp = list(csv.DictReader(open(argv[2])))
    ipd = [{r["item"]: r[k] for r in inp} for k in ("ipd1", "ipd2")]
    o = ipd[0]
    st = dict(pool=D(o["open_opening_pool"]), reserve=D(o["open_reserve"]), deferred_b=D(o["open_deferred_b"]))
    for c in "abz":
        st[f"class_{c}"] = D(o[f"open_class_{c}"]); st[f"pdl_{c}"] = D(o[f"open_pdl_{c}"])
    return rows, T, ipd, st

def main(argv):
    flags = {a for a in argv if a.startswith("--")}; argv = [a for a in argv if not a.startswith("--")]
    rows, T, ipd, st0 = load(argv)
    loans = prepare(rows); h = headline(loans)
    raw = prepare(rows, treat=set()); hr = headline(raw)
    strats = [("ARREARS", lambda o: o["arr"], ARR_B), ("INDEXED LTV", lambda o: ltv_bucket(o["ltv"]), LTV_B),
              ("REPAYMENT TYPE", lambda o: o["repayment_type"], REP_B), ("REGION", lambda o: o["reg"], REG_B)]
    out = []; P = out.append
    P("MEDWAY RESIDENTIAL 2028-1 - FINAL EXAM SOLUTIONS")
    P("PART B - REPORTING POOL AT 28 FEBRUARY 2029")
    P(f"{'Rows on the tape':<32}{len(rows):>18,}")
    P(f"{'Loans in the reporting pool':<32}{h['count']:>18,}")
    P(f"{'Total current balance (GBP)':<32}{m(h['total']):>18}")
    P(f"{'Average balance (GBP)':<32}{m(h['average']):>18}")
    P(f"{'WA current rate (%)':<32}{h['wa_rate']:>18}")
    P(f"{'WA indexed LTV (%)':<32}{h['wa_ltv']:>18}")
    P(f"{'WA remaining term (months)':<32}{h['wa_rem']:>18}")
    P("AS DELIVERED (no treatment)")
    P(f"{'Rows counted as loans':<32}{hr['count']:>18,}")
    P(f"{'Total current balance (GBP)':<32}{m(hr['total']):>18}")
    P(f"{'Average balance (GBP)':<32}{m(hr['average']):>18}")
    P(f"{'WA current rate (%)':<32}{hr['wa_rate']:>18}")
    P(f"{'WA indexed LTV, tape field (%)':<32}{hr['wa_ltv']:>18}")
    P(f"{'WA remaining term (months)':<32}{hr['wa_rem']:>18}")
    js = dict(headline={k: str(v) for k, v in h.items()}, raw={k: str(v) for k, v in hr.items()}, strats={}, ipd=[])
    for name, key, buckets in strats:
        res, tot = strat(loans, key, buckets)
        P(f"STRAT BY {name}")
        P(f"{'Bucket':<25}{'Loans':>6}{'Balance':>17}{'% bal':>8}{'WA LTV':>8}")
        for b, n, bal, pct, w in res:
            P(f"{b:<25}{n:>6}{m(bal):>17}{pct:>8}{w:>8}")
        sb = sum(x[2] for x in res); sn = sum(x[1] for x in res)
        P(f"{'Total':<25}{sn:>6}{m(sb):>17}{r2(sb / tot * 100):>8}{r2(wa(loans, 'ltv')):>8}")
        P(f"{'Check: strat - pool':<25}{sn - h['count']:>6}{m(sb - h['total']):>17}")
        js["strats"][name] = [[b, n, str(bal), str(pct), str(w)] for b, n, bal, pct, w in res]
    P("PART C - WATERFALL (ILLUSTRATIVE)")
    st = st0; runs = []
    for k in range(2):
        lines, checks, info, st = run_ipd(st, ipd[k], T); runs.append((lines, checks, info, dict(st)))
    def row(lab, a, b): P(f"{lab:<32}{m(a):>16}{m(b):>16}")
    P(f"{'':<32}{'IPD 1':>16}{'IPD 2':>16}")
    row("Opening pool", runs[0][2]["pool_open"], runs[1][2]["pool_open"])
    row("Realised losses to PDL", sum(runs[0][2]["deb"].values()), sum(runs[1][2]["deb"].values()))
    row("Available revenue receipts", runs[0][2]["arr"], runs[1][2]["arr"])
    P("REVENUE: AMOUNT DUE")
    for j in range(8): row(runs[0][0][j][0], runs[0][0][j][1], runs[1][0][j][1])
    P("REVENUE: AMOUNT PAID")
    for j in range(9): row(runs[0][0][j][0], runs[0][0][j][2], runs[1][0][j][2])
    row("Class B interest deferred", runs[0][2]["deferred"], runs[1][2]["deferred"])
    P("PRINCIPAL")
    row("Principal receipts", runs[0][2]["prin"], runs[1][2]["prin"])
    row("plus PDL cures", sum(runs[0][2]["cure"].values()), sum(runs[1][2]["cure"].values()))
    row("Available principal receipts", runs[0][2]["apr"], runs[1][2]["apr"])
    for c in "abz": row(f"Class {c.upper()} principal paid", runs[0][2]["ppaid"][c], runs[1][2]["ppaid"][c])
    P("RESERVE AND PDL")
    row("Reserve opening", runs[0][2]["res_open"], runs[1][2]["res_open"])
    row("Reserve drawn", runs[0][2]["draw"], runs[1][2]["draw"])
    row("Reserve topped up", runs[0][2]["topup"], runs[1][2]["topup"])
    row("Reserve closing", runs[0][2]["res_close"], runs[1][2]["res_close"])
    for c in "abz":
        row(f"PDL {c.upper()} debit", runs[0][2]["deb"][c], runs[1][2]["deb"][c])
        row(f"PDL {c.upper()} cure", runs[0][2]["cure"][c], runs[1][2]["cure"][c])
        row(f"PDL {c.upper()} closing", runs[0][3][f"pdl_{c}"], runs[1][3][f"pdl_{c}"])
    P("CLOSING BALANCES")
    for c in "abz": row(f"Class {c.upper()} note", runs[0][3][f"class_{c}"], runs[1][3][f"class_{c}"])
    row("Notes outstanding", runs[0][2]["notes"], runs[1][2]["notes"])
    row("PDL balance", runs[0][2]["pdl"], runs[1][2]["pdl"])
    row("Closing pool", runs[0][3]["pool"], runs[1][3]["pool"])
    row("Class B deferred interest", runs[0][3]["deferred_b"], runs[1][3]["deferred_b"])
    ce = lambda k, cls: r2(sum(runs[k][3][f"class_{c}"] for c in cls) - runs[k][2]["pdl"]) / runs[k][3]["pool"] * 100
    P(f"{'Class A CE: (B+Z-PDL)/pool (%)':<32}{r2(ce(0, 'bz')):>16}{r2(ce(1, 'bz')):>16}")
    P(f"{'Class B CE: (Z-PDL)/pool (%)':<32}{r2(ce(0, 'z')):>16}{r2(ce(1, 'z')):>16}")
    P("ZERO-CHECKS")
    for j in range(5): row(runs[0][1][j][0], runs[0][1][j][1], runs[1][1][j][1])
    P(f"{'Tape pool - IPD 1 closing pool':<32}{m(h['total'] - runs[0][3]['pool']):>16}")
    for lines, checks, info, stc in runs:
        js["ipd"].append(dict(lines=[[a, str(b), str(c)] for a, b, c in lines], checks=[str(v) for _, v in checks],
                              info={k: (str(v) if not isinstance(v, dict) else {a: str(b) for a, b in v.items()})
                                    for k, v in info.items()}, state={k: str(v) for k, v in stc.items()}))
    if "--diagnostics" in flags:
        P("DIAGNOSTICS: ONE TREATMENT LEFT OUT AT A TIME")
        for t in ["dup", "bal", "mat", "ltv", "region", "rate", "arrears"]:
            x = headline(prepare(rows, ALL - {t}))
            P(f"without {t:<8} n={x['count']} tot={m(x['total'])} avg={m(x['average'])} rate={x['wa_rate']} "
              f"ltv={x['wa_ltv']} rem={x['wa_rem']}")
        simple = r2(sum(D(o['ltv']) for o in loans) / len(loans))
        P(f"simple average indexed LTV = {simple}")
        P(f"WA rate with zero-rate loan at 0% = {r2(wa(loans, 'rate'))}")
        raw_by_id = {r["loan_id"]: r for r in rows}
        bad = next(r for r in rows if D(r["current_balance"]) > D(r["original_balance"]))
        P(f"DQ02 {bad['loan_id']} LTV on raw balance = {r2(D(bad['current_balance']) / D(bad['indexed_valuation']) * 100)}"
          f" field = {bad['indexed_ltv']} original balance = {m(D(bad['original_balance']))}")
        st4 = next(o for o in loans if o["loan_id"] == "MRS-00439")
        P(f"DQ04 MRS-00439 field = {st4['indexed_ltv']} recomputed = {st4['ltv']}")
        rm = next(o for o in raw if o["loan_id"] == "MRS-00699"); rt = next(o for o in loans if o["loan_id"] == "MRS-00699")
        P(f"DQ03 MRS-00699 remaining term raw = {rm['rem']} treated = {rt['rem']}")
        yh = [o for o in prepare(rows, ALL - {"region"}) if o["reg"] == "Yorkshire & Humber"]
        P(f"DQ06 variant spelling: {len(yh)} loans {m(sum(o['bal'] for o in yh))}")
        cur = [o for o in prepare(rows, ALL - {"arrears"}) if o["arr"] == "Current"]
        P(f"DQ08 left as current: Current = {len(cur)} loans {m(sum(o['bal'] for o in cur))}")
        lims = [D(x) for x in (50, 60, 70, 75, 80, 85, 90)]
        P(f"loans exactly on a band limit = {sum(1 for o in loans if o['ltv'] in lims)}")
        nod = [o for o in loans if o["arr"] != "Unknown"]
        P(f"arrears strat without Unknown row: {len(nod)} loans {m(sum(o['bal'] for o in nod))}")
        s0, i1, i2 = st0, ipd[0], ipd[1]
        d1 = runs[0][2]; s1 = runs[0][3]
        P(f"IPD1 servicing on closing pool = {m(r2(s1['pool'] * D(T['servicing_pct']) / 100 * 90 / 365))}")
        _, _, x360, _ = run_ipd(s0, i1, T, basis=360)
        P(f"IPD1 Class A interest Act/360 = {m(r2(s0['class_a'] * (D(T['sonia']) + D(T['margin_a'])) / 100 * 90 / 360))}"
          f" reserve then = {m(x360['res_close'])}")
        _, _, xa, sa = run_ipd(s0, i1, T, order=("a", "b", "z"))
        P(f"IPD1 losses to A first: reserve = {m(xa['res_close'])} A cure = {m(xa['cure']['a'])} A paid = {m(xa['ppaid']['a'])}")
        P(f"IPD1 loss written off Z note: Z = {m(s0['class_z'] - D(i1['realised_losses']))}"
          f" check = {m(-D(i1['realised_losses']))}")
        sen2 = sum(runs[1][0][j][2] for j in range(3))
        P(f"IPD2 items 1-3 = {m(sen2)} shortfall without reserve = {m(sen2 - D(i2['revenue_collections']))}")
        no_extra = runs[1][0][4][1] - (runs[1][2]['arr'] - (sen2 - D(i2['extra_senior_expenses'])))
        P(f"IPD2 without the extraordinary expense: B deferred = {m(no_extra)}")
        P(f"IPD2 losses Z only check: Z PDL / Z = {r2(runs[1][3]['pdl_z'] / runs[1][3]['class_z'] * 100)}")
    if "--json" in flags:
        print(json.dumps(js)); return
    print("\n".join(out))

if __name__ == "__main__":
    main(sys.argv[1:])
