"""Build ch31/excel/ch31_rhein_cashflow.xlsx - the Rhein Auto 2027-1 cash-flow model,
every calculated cell a live formula; base case and stress on two identical sheets.
Run from the book folder:
  python3 tools/build_ch31_xlsx.py data/ch31_rhein_scheduled_runoff.csv ch31/excel/ch31_rhein_cashflow.xlsx
"""
import sys, csv
from datetime import date, timedelta
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as CL

NAVY = "1F2A44"
HDR = Font(bold=True, color="FFFFFF"); HFILL = PatternFill("solid", fgColor=NAVY)
INP = PatternFill("solid", fgColor="FFF4D6"); TITLE = Font(bold=True, size=13, color=NAVY)
EUR, DT = "#,##0.00", "YYYY-MM-DD"

def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = divmod(b, 4); g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30; i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7; m = (a + 11 * h + 22 * l) // 451
    mo, da = divmod(h + l - 7 * m + 114, 31)
    return date(y, mo, da + 1)

wb = Workbook()
nt = wb.active; nt.title = "Notes"
nt["A1"] = "Chapter 31 - Rhein Auto 2027-1 cash-flow model"; nt["A1"].font = TITLE
for i, t in enumerate([
    "Yellow cells are inputs. Every other cell is a formula. Base and Stress sheets are identical except for their yellow scenario cells.",
    "Period t = collection month t after the 28 Feb 2027 cut-off (t = 1 is March 2027), paid on the 25th of month t+1, modified following, TARGET holidays (sheet Holidays).",
    "Every money amount is rounded to the cent with ROUND. Notes, swap and subordinated loan accrue Actual/360; pool interest and fees accrue 1/12 of the annual rate.",
    "Pool: defaults first (monthly default rate on the opening balance), then scheduled principal (Runoff profile), then prepayments (SMM).",
    "Revolving period: payment dates 1-12; principal target buys new receivables. Amortisation restarts the runoff profile at month 1.",
    "Pro rata: A, B, C and the subordinated loan each receive target x own balance / total, paid in that order. Sequential (trigger or call): A, then B, C, Sub.",
    "Clean-up call: first amortisation date on which the pool after collections is below 10% of the initial pool; seller buys the pool at its balance.",
    "WAL = sum(principal x years from closing 25 Mar 2027, Actual/365) / initial balance.",
], start=3):
    nt.cell(i, 1, t)
nt.column_dimensions["A"].width = 120

# ---------------- Inputs ----------------
ip = wb.create_sheet("Inputs")
ip["A1"] = "Deal inputs (Deal Fact Sheets and Chapter 31)"; ip["A1"].font = TITLE
deal = [("Initial pool (EUR)", 480929439.61, EUR), ("Class A (EUR)", 432800000, EUR),
        ("Class B (EUR)", 21600000, EUR), ("Class C (EUR)", 14400000, EUR),
        ("Subordinated loan (EUR)", 12129439.61, EUR), ("Class A margin", 0.0055, "0.00%"),
        ("Class B margin", 0.0125, "0.00%"), ("Class C margin", 0.021, "0.00%"),
        ("Subordinated loan rate", 0.06, "0.00%"), ("Swap fixed rate", 0.024, "0.00%"),
        ("Senior expenses (EUR p.a.)", 150000, EUR), ("Servicing fee (p.a. of pool)", 0.005, "0.00%"),
        ("Cash reserve at closing (EUR)", 4809294.40, EUR), ("Cash reserve floor (EUR)", 2400000, EUR),
        ("Cash reserve % of notes", 0.01, "0.00%"), ("Revolving payment dates", 12, "0"),
        ("Early amortisation CNL trigger", 0.008, "0.00%"), ("Clean-up call (% of initial pool)", 0.10, "0.00%"),
        ("Sequential trigger CNL, amort. months 1-12", 0.008, "0.00%"),
        ("Sequential trigger CNL, amort. months 13-24", 0.014, "0.00%"),
        ("Sequential trigger CNL, after month 24", 0.02, "0.00%"),
        ("Closing date", date(2027, 3, 25), DT)]
for i, (lab, v, fmt) in enumerate(deal, start=3):
    ip.cell(i, 1, lab); c = ip.cell(i, 2, v); c.number_format = fmt; c.fill = INP
ip.column_dimensions["A"].width = 44; ip.column_dimensions["B"].width = 18
I = {k: f"Inputs!$B${i}" for i, k in enumerate(
    ["pool0", "A0", "B0", "C0", "S0", "mA", "mB", "mC", "subr", "fixed", "fees", "serv",
     "res0", "resfloor", "respct", "revn", "ea", "call", "t1", "t2", "t3", "closing"], start=3)}

# ---------------- Holidays ----------------
hl = wb.create_sheet("Holidays")
hl["A1"] = "TARGET closing days (besides weekends)"; hl["A1"].font = Font(bold=True, color=NAVY)
hol = []
for y in range(2027, 2035):
    e = easter(y)
    hol += [date(y, 1, 1), e - timedelta(2), e + timedelta(1), date(y, 5, 1), date(y, 12, 25), date(y, 12, 26)]
for i, d in enumerate(hol, start=2):
    c = hl.cell(i, 1, d); c.number_format = DT; c.fill = INP
HOL = f"Holidays!$A$2:$A${len(hol) + 1}"
hl.column_dimensions["A"].width = 14

# ---------------- Runoff ----------------
rr = wb.create_sheet("Runoff")
rows = list(csv.DictReader(open(sys.argv[1])))
heads = ["month", "opening", "interest", "regular_principal", "balloon_principal", "closing", "profile s_k"]
for j, h in enumerate(heads, 1):
    c = rr.cell(1, j, h); c.font = HDR; c.fill = HFILL
for i, r in enumerate(rows, start=2):
    for j, h in enumerate(heads[:-1], 1):
        c = rr.cell(i, j, float(r[h]) if h != "month" else int(r[h])); c.fill = INP
        if j > 1: c.number_format = EUR
    rr.cell(i, 7, f"=(D{i}+E{i})/B{i}").number_format = "0.000000"
NR = len(rows)
PROF = f"Runoff!$G$2:$G${NR + 1}"
for j in range(1, 8): rr.column_dimensions[CL(j)].width = 17

# ---------------- model sheets ----------------
cols = ["t", "Nominal date", "Following", "Payment date", "Days", "Pool opening", "Defaults",
        "Recoveries", "Cum. defaults", "Cum. recoveries", "CNL ratio", "Early amort.", "Revolving",
        "Revolving count", "Profile month k", "Profile s_k", "Scheduled principal", "Prepayments",
        "Interest collections", "Pool after collections", "Available (collections)",
        "A open", "B open", "C open", "Sub open", "Notes A-C", "Senior exp. + servicing",
        "Swap net (+ = issuer pays)", "A interest", "B interest", "C interest", "Available + swap in",
        "Senior items", "Reserve open", "Reserve draw", "Reserve after draw", "Available after interest",
        "Call", "Reserve req. pro rata", "Sequential", "Reserve required", "Available (call adj.)",
        "Reserve (call adj.)", "Reserve top-up", "Reserve after top-up", "Available after top-up",
        "Reserve release", "Reserve close", "Liabilities total", "Principal target", "Purchase",
        "Available for principal", "Pool close", "Seq. or call", "Pay A", "Avail. after A",
        "Target after A", "Pay B", "Avail. after B", "Target after B", "Pay C", "Avail. after C",
        "Target after C", "Pay Sub", "Avail. after Sub", "A close", "B close", "C close", "Sub close",
        "Sub loan interest", "Residual to Rheinwagen", "Years from closing"]
C = {name: CL(j) for j, name in enumerate(cols, 1)}
FIRST, NROWS = 12, 60

def model_sheet(name, cdr, rec, cpr):
    ws = wb.create_sheet(name)
    ws["A1"] = f"Rhein Auto 2027-1 - {name}"; ws["A1"].font = TITLE
    pars = [("Annual default rate (CDR)", cdr, "0.00%"), ("Recovery rate", rec, "0.00%"),
            ("Annual prepayment rate (CPR)", cpr, "0.00%"), ("1M EURIBOR (flat, illustrative)", 0.0225, "0.00%"),
            ("Pool interest rate", 0.0477, "0.00%"), ("Recovery lag (months)", 6, "0")]
    for i, (lab, v, fmt) in enumerate(pars, start=3):
        ws.cell(i, 1, lab); c = ws.cell(i, 2, v); c.number_format = fmt; c.fill = INP
    ws["D3"] = "Monthly default rate"; ws["E3"] = "=1-(1-B3)^(1/12)"
    ws["D4"] = "Monthly prepayment rate (SMM)"; ws["E4"] = "=1-(1-B5)^(1/12)"
    ws["D5"] = "EURIBOR floored at 0"; ws["E5"] = "=MAX(B6,0)"
    for c in ("E3", "E4", "E5"): ws[c].number_format = "0.000000%"
    for j, h in enumerate(cols, 1):
        c = ws.cell(FIRST - 1, j, h); c.font = HDR; c.fill = HFILL
        c.alignment = Alignment(wrap_text=True, horizontal="center")
        ws.column_dimensions[CL(j)].width = 14
    ws.row_dimensions[FIRST - 1].height = 45
    last = FIRST + NROWS - 1
    for t in range(1, NROWS + 1):
        r = FIRST + t - 1; p = r - 1; first = t == 1
        f = lambda col, row=r: f"{C[col]}{row}"
        prev = lambda col: f"{C[col]}{p}"
        F = {}
        F["t"] = t
        F["Nominal date"] = f"=DATE(2027,3+{f('t')},25)"
        F["Following"] = f"=WORKDAY({f('Nominal date')}-1,1,{HOL})"
        F["Payment date"] = (f"=IF(MONTH({f('Following')})<>MONTH({f('Nominal date')}),"
                             f"WORKDAY({f('Nominal date')}+1,-1,{HOL}),{f('Following')})")
        F["Days"] = f"={f('Payment date')}-" + (I["closing"] if first else prev("Payment date"))
        F["Pool opening"] = f"={I['pool0']}" if first else f"={prev('Pool close')}"
        F["Defaults"] = f"=ROUND({f('Pool opening')}*$E$3,2)"
        F["Recoveries"] = (f"=IF({f('t')}>$B$8,ROUND(INDEX(${C['Defaults']}${FIRST}:${C['Defaults']}${last},"
                           f"{f('t')}-$B$8)*$B$4,2),0)")
        F["Cum. defaults"] = f"=SUM(${C['Defaults']}${FIRST}:{f('Defaults')})"
        F["Cum. recoveries"] = f"=SUM(${C['Recoveries']}${FIRST}:{f('Recoveries')})"
        F["CNL ratio"] = f"=({f('Cum. defaults')}-{f('Cum. recoveries')})/{I['pool0']}"
        ea_new = f"AND({f('t')}<={I['revn']},{f('CNL ratio')}>{I['ea']})"
        F["Early amort."] = f"={ea_new}" if first else f"=OR({prev('Early amort.')},{ea_new})"
        F["Revolving"] = f"=AND({f('t')}<={I['revn']},NOT({f('Early amort.')}))"
        F["Revolving count"] = f"=COUNTIF(${C['Revolving']}${FIRST}:{f('Revolving')},TRUE())"
        F["Profile month k"] = f"=IF({f('Revolving')},{f('t')},{f('t')}-{f('Revolving count')})"
        F["Profile s_k"] = f"=IF({f('Profile month k')}<={NR},INDEX({PROF},{f('Profile month k')}),1)"
        F["Scheduled principal"] = f"=ROUND(({f('Pool opening')}-{f('Defaults')})*{f('Profile s_k')},2)"
        F["Prepayments"] = (f"=ROUND(({f('Pool opening')}-{f('Defaults')}-{f('Scheduled principal')})"
                            f"*$E$4,2)")
        F["Interest collections"] = f"=ROUND(({f('Pool opening')}-{f('Defaults')})*$B$7/12,2)"
        F["Pool after collections"] = (f"=ROUND({f('Pool opening')}-{f('Defaults')}-"
                                       f"{f('Scheduled principal')}-{f('Prepayments')},2)")
        F["Available (collections)"] = (f"=ROUND({f('Interest collections')}+{f('Scheduled principal')}+"
                                        f"{f('Prepayments')}+{f('Recoveries')},2)")
        for k, key in (("A", "A0"), ("B", "B0"), ("C", "C0"), ("Sub", "S0")):
            F[f"{k} open"] = f"={I[key]}" if first else f"={prev(k + ' close')}"
        F["Notes A-C"] = f"={f('A open')}+{f('B open')}+{f('C open')}"
        F["Senior exp. + servicing"] = f"=ROUND({I['fees']}/12+{f('Pool opening')}*{I['serv']}/12,2)"
        F["Swap net (+ = issuer pays)"] = f"=ROUND({f('Notes A-C')}*({I['fixed']}-$E$5)*{f('Days')}/360,2)"
        for k, m in (("A", "mA"), ("B", "mB"), ("C", "mC")):
            F[f"{k} interest"] = f"=ROUND({f(k + ' open')}*($E$5+{I[m]})*{f('Days')}/360,2)"
        F["Available + swap in"] = f"=ROUND({f('Available (collections)')}+MAX(0,-{f('Swap net (+ = issuer pays)')}),2)"
        F["Senior items"] = (f"=ROUND({f('Senior exp. + servicing')}+MAX(0,{f('Swap net (+ = issuer pays)')})+"
                             f"{f('A interest')}+{f('B interest')}+{f('C interest')},2)")
        F["Reserve open"] = f"={I['res0']}" if first else f"={prev('Reserve close')}"
        F["Reserve draw"] = f"=ROUND(MIN({f('Reserve open')},MAX(0,{f('Senior items')}-{f('Available + swap in')})),2)"
        F["Reserve after draw"] = f"=ROUND({f('Reserve open')}-{f('Reserve draw')},2)"
        F["Available after interest"] = (f"=ROUND(MAX(0,{f('Available + swap in')}+{f('Reserve draw')}-"
                                         f"{f('Senior items')}),2)")
        F["Call"] = f"=AND(NOT({f('Revolving')}),{f('Pool after collections')}<{I['call']}*{I['pool0']})"
        F["Reserve req. pro rata"] = f"=MIN({I['res0']},MAX({I['respct']}*{f('Notes A-C')},{I['resfloor']}))"
        thr = (f"IF({f('Profile month k')}<=12,{I['t1']},IF({f('Profile month k')}<=24,{I['t2']},{I['t3']}))")
        test = (f"IF(AND(NOT({f('Revolving')}),NOT({f('Call')})),OR({f('CNL ratio')}>{thr},"
                f"{f('Reserve after draw')}<{f('Reserve req. pro rata')}-0.005),FALSE())")
        F["Sequential"] = f"={test}" if first else f"=IF({prev('Sequential')},TRUE(),{test})"
        F["Reserve required"] = (f"=IF({f('Call')},0,IF(OR({f('Revolving')},{f('Sequential')}),{I['res0']},"
                                 f"{f('Reserve req. pro rata')}))")
        F["Available (call adj.)"] = (f"=IF({f('Call')},ROUND({f('Available after interest')}+"
                                      f"{f('Reserve after draw')},2),{f('Available after interest')})")
        F["Reserve (call adj.)"] = f"=IF({f('Call')},0,{f('Reserve after draw')})"
        F["Reserve top-up"] = (f"=ROUND(MIN(MAX(0,{f('Reserve required')}-{f('Reserve (call adj.)')}),"
                               f"{f('Available (call adj.)')}),2)")
        F["Reserve after top-up"] = f"=ROUND({f('Reserve (call adj.)')}+{f('Reserve top-up')},2)"
        F["Available after top-up"] = f"=ROUND({f('Available (call adj.)')}-{f('Reserve top-up')},2)"
        F["Reserve release"] = f"=ROUND(MAX(0,{f('Reserve after top-up')}-{f('Reserve required')}),2)"
        F["Reserve close"] = f"=ROUND({f('Reserve after top-up')}-{f('Reserve release')},2)"
        F["Liabilities total"] = f"=ROUND({f('A open')}+{f('B open')}+{f('C open')}+{f('Sub open')},2)"
        F["Principal target"] = (f"=IF({f('Call')},{f('Liabilities total')},ROUND(MAX(0,{f('Liabilities total')}-"
                                 f"{f('Pool after collections')}),2))")
        F["Purchase"] = f"=IF({f('Revolving')},ROUND(MIN({f('Principal target')},{f('Available after top-up')}),2),0)"
        F["Available for principal"] = (f"=IF({f('Revolving')},ROUND({f('Available after top-up')}-{f('Purchase')},2),"
                                        f"IF({f('Call')},ROUND({f('Available after top-up')}+"
                                        f"{f('Pool after collections')},2),{f('Available after top-up')}))")
        F["Pool close"] = (f"=IF({f('Revolving')},ROUND({f('Pool after collections')}+{f('Purchase')},2),"
                           f"IF({f('Call')},0,{f('Pool after collections')}))")
        F["Seq. or call"] = f"=OR({f('Sequential')},{f('Call')})"
        avail_prev, tgt_prev = "Available for principal", "Principal target"
        for k, nxt in (("A", "B"), ("B", "C"), ("C", "Sub"), ("Sub", None)):
            want = (f"IF({f('Seq. or call')},MIN({f(k + ' open')},{f(tgt_prev)}),"
                    f"ROUND({f('Principal target')}*{f(k + ' open')}/{f('Liabilities total')},2))")
            F[f"Pay {k}"] = f"=IF({f('Revolving')},0,ROUND(MIN({want},{f(avail_prev)}),2))"
            F[f"Avail. after {k}"] = f"=ROUND({f(avail_prev)}-{f('Pay ' + k)},2)"
            if nxt:
                F[f"Target after {k}"] = (f"=IF({f('Seq. or call')},ROUND({f(tgt_prev)}-{f('Pay ' + k)},2),"
                                          f"{f('Principal target')})")
                tgt_prev = f"Target after {k}"
            avail_prev = f"Avail. after {k}"
        for k in ("A", "B", "C", "Sub"):
            F[f"{k} close"] = f"=ROUND({f(k + ' open')}-{f('Pay ' + k)},2)"
        F["Sub loan interest"] = (f"=ROUND(MIN({f('Avail. after Sub')},{f('Sub open')}*{I['subr']}*"
                                  f"{f('Days')}/360),2)")
        F["Residual to Rheinwagen"] = f"=ROUND({f('Avail. after Sub')}-{f('Sub loan interest')},2)"
        F["Years from closing"] = f"=({f('Payment date')}-{I['closing']})/365"
        for j, h in enumerate(cols, 1):
            c = ws.cell(r, j, F[h])
            if h in ("Nominal date", "Following", "Payment date"): c.number_format = DT
            elif h in ("CNL ratio",): c.number_format = "0.0000%"
            elif h in ("Profile s_k",): c.number_format = "0.000000"
            elif h in ("t", "Days", "Revolving count", "Profile month k"): c.number_format = "0"
            elif h == "Years from closing": c.number_format = "0.0000"
            elif not isinstance(F[h], str) or "AND(" not in F[h][:5]: c.number_format = EUR
    ws.freeze_panes = ws.cell(FIRST, 5)
    return ws

model_sheet("Base", 0.0048, 0.55, 0.1266)
model_sheet("Stress", 0.0096, 0.50, 0.1266)

# ---------------- Summary ----------------
sm = wb.create_sheet("Summary", 1)
sm["A1"] = "Results: base case and stress"; sm["A1"].font = TITLE
last = FIRST + NROWS - 1
def R(sh, col): return f"{sh}!${C[col]}${FIRST}:${C[col]}${last}"
labels = [
    ("First payment date", lambda s: f"={s}!{C['Payment date']}{FIRST}", DT),
    ("Days in first period", lambda s: f"={s}!{C['Days']}{FIRST}", "0"),
    ("Class A interest, PD 1", lambda s: f"={s}!{C['A interest']}{FIRST}", EUR),
    ("Swap net paid, PD 1", lambda s: f"={s}!{C['Swap net (+ = issuer pays)']}{FIRST}", EUR),
    ("Revolving payment dates", lambda s: f"=COUNTIF({R(s,'Revolving')},TRUE())", "0"),
    ("Receivables bought", lambda s: f"=SUM({R(s,'Purchase')})", EUR),
    ("CNL end of revolving", lambda s: f"=INDEX({R(s,'CNL ratio')},B7)", "0.00%"),
    ("Sequential trigger date", lambda s: f'=IFERROR(INDEX({R(s,"Payment date")},MATCH(TRUE(),{R(s,"Sequential")},0)),"not hit")', DT),
    ("Sequential: amortisation month", lambda s: f'=IFERROR(INDEX({R(s,"Profile month k")},MATCH(TRUE(),{R(s,"Sequential")},0)),"-")', "0"),
    ("Sequential: CNL on that date", lambda s: f'=IFERROR(INDEX({R(s,"CNL ratio")},MATCH(TRUE(),{R(s,"Sequential")},0)),"-")', "0.00%"),
    ("Clean-up call row", lambda s: f"=MATCH(TRUE(),{R(s,'Call')},0)", "0"),
    ("Clean-up call date", lambda s: f"=INDEX({R(s,'Payment date')},B13)", DT),
    ("Pool bought back at call", lambda s: f"=INDEX({R(s,'Pool after collections')},B13)", EUR),
    ("Owed after the call", lambda s: f"=INDEX({R(s,'A close')},B13)+INDEX({R(s,'B close')},B13)+INDEX({R(s,'C close')},B13)+INDEX({R(s,'Sub close')},B13)", EUR),
    ("CNL at call", lambda s: f"=INDEX({R(s,'CNL ratio')},B13)", "0.00%"),
    ("WAL Class A (years)", lambda s: f"=SUMPRODUCT({R(s,'Pay A')},{R(s,'Years from closing')})/{I['A0']}", "0.00"),
    ("WAL Class B (years)", lambda s: f"=SUMPRODUCT({R(s,'Pay B')},{R(s,'Years from closing')})/{I['B0']}", "0.00"),
    ("WAL Class C (years)", lambda s: f"=SUMPRODUCT({R(s,'Pay C')},{R(s,'Years from closing')})/{I['C0']}", "0.00"),
    ("WAL subordinated loan (years)", lambda s: f"=SUMPRODUCT({R(s,'Pay Sub')},{R(s,'Years from closing')})/{I['S0']}", "0.00"),
]
for j, h in enumerate(["Result", "Base", "Stress"], 1):
    c = sm.cell(2, j, h); c.font = HDR; c.fill = HFILL
for i, (lab, fn, fmt) in enumerate(labels, start=3):
    sm.cell(i, 1, lab)
    for j, s in ((2, "Base"), (3, "Stress")):
        formula = fn(s)
        if j == 3: formula = formula.replace(",B7)", ",C7)").replace(",B13)", ",C13)")
        c = sm.cell(i, j, formula); c.number_format = fmt
sm.column_dimensions["A"].width = 34; sm.column_dimensions["B"].width = 18; sm.column_dimensions["C"].width = 18

# ---------------- Waterfall PD 1 ----------------
wf = wb.create_sheet("Waterfall PD1", 2)
wf["A1"] = "Base case: first payment date (26 April 2027)"; wf["A1"].font = TITLE
lines = [("Interest collections", "Interest collections", 1), ("Scheduled principal", "Scheduled principal", 1),
         ("Prepayments", "Prepayments", 1), ("Recoveries", "Recoveries", 1),
         ("Available distribution amount", "Available (collections)", 1),
         ("1 Senior expenses and servicing", "Senior exp. + servicing", -1),
         ("2 Swap net payment", "Swap net (+ = issuer pays)", -1), ("3 Class A interest", "A interest", -1),
         ("4 Class B interest", "B interest", -1), ("5 Class C interest", "C interest", -1),
         ("6 Cash reserve top-up", "Reserve top-up", -1), ("7 Purchase of new receivables", "Purchase", -1),
         ("8 Subordinated loan interest", "Sub loan interest", -1),
         ("9 Residual to Rheinwagen Bank", "Residual to Rheinwagen", -1)]
for i, (lab, col, sg) in enumerate(lines, start=3):
    wf.cell(i, 1, lab)
    wf.cell(i, 2, f"={'-' if sg < 0 else ''}Base!{C[col]}{FIRST}").number_format = EUR
wf["A18"] = "Check: available less items 1-9 (should be 0)"; wf["B18"] = "=B7+SUM(B8:B16)"; wf["B18"].number_format = EUR
wf.column_dimensions["A"].width = 40; wf.column_dimensions["B"].width = 18

wb.save(sys.argv[2])
print("saved", sys.argv[2])
