"""Build ch30/excel/ch30_rhein_pool.xlsx (every calculated cell is a live formula).
Run from the book folder:
  python3 tools/build_ch30_xlsx.py data/rhein_auto_2027_1_tape.csv \
      data/rheinwagen_static_pool_losses.csv ch30/excel/ch30_rhein_pool.xlsx
"""
import sys, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L

NAVY = "1F2A44"
HDR = Font(bold=True, color="FFFFFF"); HFILL = PatternFill("solid", fgColor=NAVY)
INP = PatternFill("solid", fgColor="FFF4D6")
TITLE = Font(bold=True, size=13, color=NAVY)
EUR, PCT2, N0 = "#,##0.00", "0.00", "#,##0"

def header(ws, row, names, col=1):
    for j, h in enumerate(names, col):
        c = ws.cell(row, j, h); c.font = HDR; c.fill = HFILL
        c.alignment = Alignment(horizontal="center", wrap_text=True)

def widths(ws, ws_w):
    for j, w in enumerate(ws_w, 1):
        ws.column_dimensions[L(j)].width = w

wb = Workbook()
# ---------------- Notes ----------------
nt = wb.active; nt.title = "Notes"
nt["A1"] = "Chapter 30 - Rhein Auto 2027-1 pool analysis"; nt["A1"].font = TITLE
for i, t in enumerate([
    "Yellow cells are inputs (data pasted from the CSV files). Every other cell is a formula.",
    "Tape: data/rhein_auto_2027_1_tape.csv, cut-off 28 Feb 2027, 30,000 loans.",
    "Percentages are of the current balance at cut-off (EUR 480,929,439.61).",
    "LTV at origination = original_balance / vehicle_price x 100; bands are right-closed (80.00 is in '<= 80%').",
    "Balloon due month = cut-off month (Feb 2027) + remaining_term_months; month 1 = March 2027.",
    "Static pools: data/rheinwagen_static_pool_losses.csv; volume-weighted chain ladder to 96 months.",
    "Base case uses vintages with at least 12 months of history (85 vintages).",
    "Instalments: interest = ROUND(balance x rate/12, 2) each month (Excel ROUND rule).",
], start=3):
    nt.cell(i, 1, t)
nt.column_dimensions["A"].width = 100

# ---------------- Tape ----------------
rows = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
tp = wb.create_sheet("Tape")
cols = list(rows[0].keys())
numeric = {"vehicle_price", "down_payment", "original_balance", "interest_rate",
           "original_term_months", "balloon_amount", "monthly_instalment",
           "payments_made", "current_balance", "remaining_term_months", "months_in_arrears"}
header(tp, 1, cols + ["ltv_pct", "ltv_band", "due_index", "due_year"])
N = len(rows)
for i, r in enumerate(rows, start=2):
    for j, c in enumerate(cols, 1):
        v = r[c]
        cell = tp.cell(i, j, float(v) if c in numeric else v)
        cell.fill = INP
    tp.cell(i, 20, f"=G{i}/E{i}*100")
    tp.cell(i, 21, f'=IF(T{i}<=80,"<= 80%",IF(T{i}<=90,"80-90%","90-100%"))')
    tp.cell(i, 22, f'=IF(J{i}="Y",O{i},"")')          # months from cut-off to balloon
    tp.cell(i, 23, f'=IF(J{i}="Y",INT((24325+O{i})/12),"")')
LAST = N + 1
rng = lambda col: f"Tape!${col}$2:${col}${LAST}"
tp.freeze_panes = "A2"

# ---------------- Summary ----------------
sm = wb.create_sheet("Summary")
sm["A1"] = "Pool at cut-off (28 Feb 2027)"; sm["A1"].font = TITLE
bal = rng("N")
items = [
    ("Loans", f"=COUNTA({rng('A')})", N0),
    ("Current balance (EUR)", f"=SUM({bal})", EUR),
    ("Average balance (EUR)", "=B4/B3", EUR),
    ("WA interest rate (%)", f"=SUMPRODUCT({rng('H')},{bal})/B4", PCT2),
    ("WA remaining term (months)", f"=SUMPRODUCT({rng('O')},{bal})/B4", PCT2),
    ("WA seasoning (months)", f"=SUMPRODUCT({rng('M')},{bal})/B4", PCT2),
    ("WA LTV at origination (%)", f"=SUMPRODUCT({rng('T')},{bal})/B4", PCT2),
]
for i, (lab, f, fmt) in enumerate(items, start=3):
    sm.cell(i, 1, lab); c = sm.cell(i, 2, f); c.number_format = fmt
widths(sm, [32, 20])

# ---------------- Strats ----------------
sg = wb.create_sheet("Strats")
sg["A1"] = "Stratification tables (% of current balance)"; sg["A1"].font = TITLE
blocks = [
    ("Product (balloon flag)", "J", [("Balloon", "Y"), ("Classic", "N")]),
    ("Vehicle condition", "C", [("New", "New"), ("Used", "Used")]),
    ("Fuel type", "D", [(x, x) for x in ["Diesel", "Electric", "Hybrid", "Petrol"]]),
    ("Borrower type", "P", [(x, x) for x in ["Commercial", "Private"]]),
    ("Original term (months)", "I", [(str(x), x) for x in [24, 36, 48, 60, 72]]),
    ("LTV at origination", "U", [(x, x) for x in ["<= 80%", "80-90%", "90-100%"]]),
    ("Federal state (top 3)", "Q", [(x, x) for x in ["Nordrhein-Westfalen", "Bayern", "Baden-Württemberg"]]),
]
r = 3
for title, col, keys in blocks:
    header(sg, r, [title, "Loans", "Balance (EUR)", "% of pool"]); r += 1
    for lab, key in keys:
        crit = f'"{key}"' if isinstance(key, str) else str(key)
        sg.cell(r, 1, lab)
        sg.cell(r, 2, f"=COUNTIFS({rng(col)},{crit})").number_format = N0
        sg.cell(r, 3, f"=SUMIFS({bal},{rng(col)},{crit})").number_format = EUR
        sg.cell(r, 4, f"=C{r}/Summary!$B$4*100").number_format = PCT2
        r += 1
    r += 1
widths(sg, [26, 10, 18, 10])

# ---------------- Balloons ----------------
bl = wb.create_sheet("Balloons")
bl["A1"] = "Balloon concentration"; bl["A1"].font = TITLE
bl["A3"] = "Balloon loans"; bl["B3"] = f'=COUNTIFS({rng("J")},"Y")'; bl["B3"].number_format = N0
bl["A4"] = "Their current balance (EUR)"; bl["B4"] = f'=SUMIFS({bal},{rng("J")},"Y")'
bl["C4"] = "=B4/Summary!B4*100"
bl["A5"] = "Balloon amounts (EUR)"; bl["B5"] = f"=SUM({rng('K')})"
bl["C5"] = "=B5/Summary!B4*100"
for c in ("B4", "B5"): bl[c].number_format = EUR
for c in ("C4", "C5"): bl[c].number_format = PCT2
header(bl, 7, ["Due year", "Balloon amounts (EUR)", "% of pool"])
for i, y in enumerate(range(2027, 2033), start=8):
    bl.cell(i, 1, y)
    bl.cell(i, 2, f"=SUMIFS({rng('K')},{rng('W')},A{i})").number_format = EUR
    bl.cell(i, 3, f"=B{i}/Summary!$B$4*100").number_format = PCT2
header(bl, 15, ["Fuel type", "Balloon amounts (EUR)", "Vehicle price of balloon loans (EUR)", "Balloon % of price"])
for i, f in enumerate(["Diesel", "Electric", "Hybrid", "Petrol"], start=16):
    bl.cell(i, 1, f)
    bl.cell(i, 2, f'=SUMIFS({rng("K")},{rng("D")},A{i},{rng("J")},"Y")').number_format = EUR
    bl.cell(i, 3, f'=SUMIFS({rng("E")},{rng("D")},A{i},{rng("J")},"Y")').number_format = EUR
    bl.cell(i, 4, f"=B{i}/C{i}*100").number_format = PCT2
header(bl, 21, ["Month from cut-off", "Calendar month", "Balloon amounts (EUR)"])
for m in range(1, 71):
    i = 21 + m
    bl.cell(i, 1, m)
    bl.cell(i, 2, f'=TEXT(DATE(2027,2+A{i},1),"YYYY-MM")')
    bl.cell(i, 3, f"=SUMIFS({rng('K')},{rng('V')},A{i})").number_format = EUR
bl["E22"] = "Largest month"; bl["F22"] = "=INDEX(B22:B91,MATCH(MAX(C22:C91),C22:C91,0))"
bl["E23"] = "Amount (EUR)"; bl["F23"] = "=MAX(C22:C91)"; bl["F23"].number_format = EUR
widths(bl, [26, 22, 24, 16, 16, 18])

# ---------------- RA-000002 ----------------
lo = wb.create_sheet("RA-000002")
lo["A1"] = "Balloon loan RA-000002"; lo["A1"].font = TITLE
inputs = [("Amount financed (EUR)", 21200, EUR), ("Annual rate", 0.0384, "0.00%"),
          ("Term (months)", 36, "0"), ("Balloon (EUR)", 8900, EUR), ("Payments made", 6, "0"),
          ("Tape current balance (EUR)", 19246.98, EUR)]
for i, (lab, v, fmt) in enumerate(inputs, start=3):
    lo.cell(i, 1, lab); c = lo.cell(i, 2, v); c.number_format = fmt; c.fill = INP
calc = [("Monthly rate", "=B4/12", "0.0000%"),
        ("Instalment with balloon", "=ROUND(PMT(B9,B5,-B3,B6),2)", EUR),
        ("Instalment without balloon", "=ROUND(PMT(B9,B5,-B3),2)", EUR),
        ("Balance after payments made", "=INDEX(F17:F52,B7)", EUR),
        ("Check against tape", "=B12-B8", "0.00"),
        ("Final payment", "=B10+F52", EUR)]
for i, (lab, f, fmt) in enumerate(calc, start=9):
    lo.cell(i, 1, lab); c = lo.cell(i, 2, f); c.number_format = fmt
header(lo, 16, ["Month", "Opening", "Instalment", "Interest", "Principal", "Closing"])
for m in range(1, 37):
    i = 16 + m
    lo.cell(i, 1, m)
    lo.cell(i, 2, "=B3" if m == 1 else f"=F{i-1}")
    lo.cell(i, 3, "=$B$10")
    lo.cell(i, 4, f"=ROUND(B{i}*$B$9,2)")
    lo.cell(i, 5, f"=C{i}-D{i}")
    lo.cell(i, 6, f"=B{i}-E{i}")
    for j in range(2, 7): lo.cell(i, j).number_format = EUR
widths(lo, [30, 16, 14, 12, 12, 14])

# ---------------- StaticPool ----------------
srows = list(csv.DictReader(open(sys.argv[2])))
sp = wb.create_sheet("StaticPool")
header(sp, 1, ["vintage", "originated_balance", "months", "cum_gross_pct", "cum_recovery_pct",
               "cum_net_pct", "vintage_max_age", "w_net", "w_gross"])
S = len(srows) + 1
for i, r in enumerate(srows, start=2):
    sp.cell(i, 1, r["vintage"]).fill = INP
    for j, c in enumerate(["originated_balance", "months_since_origination", "cumulative_gross_loss_pct",
                           "cumulative_recovery_pct", "cumulative_net_loss_pct"], start=2):
        sp.cell(i, j, float(r[c])).fill = INP
    sp.cell(i, 7, f"=_xlfn.MAXIFS($C$2:$C${S},$A$2:$A${S},A{i})")
    sp.cell(i, 8, f"=B{i}*F{i}")
    sp.cell(i, 9, f"=B{i}*D{i}")
sp.freeze_panes = "A2"
srng = lambda col: f"StaticPool!${col}$2:${col}${S}"

# ---------------- ChainLadder ----------------
cl = wb.create_sheet("ChainLadder")
cl["A1"] = "Volume-weighted development factors and factor to ultimate (96 months)"; cl["A1"].font = TITLE
header(cl, 3, ["Age a", "Net: sum w(a+1)", "Net: sum w(a), seen at a+1", "Net factor",
               "Net to ultimate", "Gross: sum w(a+1)", "Gross: sum w(a), seen at a+1",
               "Gross factor", "Gross to ultimate"])
for a in range(1, 97):
    i = 3 + a
    cl.cell(i, 1, a)
    if a < 96:
        cl.cell(i, 2, f"=SUMIFS({srng('H')},{srng('C')},A{i}+1)")
        cl.cell(i, 3, f'=SUMIFS({srng("H")},{srng("C")},A{i},{srng("G")},">="&(A{i}+1))')
        cl.cell(i, 4, f"=B{i}/C{i}")
        cl.cell(i, 5, f"=E{i+1}*D{i}")
        cl.cell(i, 6, f"=SUMIFS({srng('I')},{srng('C')},A{i}+1)")
        cl.cell(i, 7, f'=SUMIFS({srng("I")},{srng("C")},A{i},{srng("G")},">="&(A{i}+1))')
        cl.cell(i, 8, f"=F{i}/G{i}")
        cl.cell(i, 9, f"=I{i+1}*H{i}")
    else:
        cl.cell(i, 5, 1); cl.cell(i, 9, 1)
    for j in (4, 5, 8, 9): cl.cell(i, j).number_format = "0.0000"
widths(cl, [8, 18, 22, 12, 14, 18, 22, 12, 14])

# ---------------- Vintages ----------------
vt = wb.create_sheet("Vintages")
vt["A1"] = "Projected lifetime loss per vintage"; vt["A1"].font = TITLE
header(vt, 3, ["Vintage", "Originated (EUR)", "Months seen", "Last net %", "Lifetime net %",
               "Last gross %", "Lifetime gross %", "Mature (>=12m)", "Year"])
vints = sorted({r["vintage"] for r in srows})
for k, v in enumerate(vints):
    i = 4 + k
    vt.cell(i, 1, v)
    vt.cell(i, 2, f"=INDEX({srng('B')},MATCH(A{i},{srng('A')},0))").number_format = N0
    vt.cell(i, 3, f"=_xlfn.MAXIFS({srng('C')},{srng('A')},A{i})")
    vt.cell(i, 4, f"=SUMIFS({srng('F')},{srng('A')},A{i},{srng('C')},C{i})")
    vt.cell(i, 5, f"=D{i}*INDEX(ChainLadder!$E$4:$E$99,C{i})")
    vt.cell(i, 6, f"=SUMIFS({srng('D')},{srng('A')},A{i},{srng('C')},C{i})")
    vt.cell(i, 7, f"=F{i}*INDEX(ChainLadder!$I$4:$I$99,C{i})")
    vt.cell(i, 8, f"=IF(C{i}>=12,1,0)")
    vt.cell(i, 9, f"=LEFT(A{i},4)")
    for j in (4, 5, 6, 7): vt.cell(i, j).number_format = "0.0000"
VL = 3 + len(vints)
vr = lambda c: f"${c}$4:${c}${VL}"
vt["K3"] = "Base case (mature vintages)"; vt["K3"].font = Font(bold=True, color=NAVY)
vt["K4"] = "Mature vintages"; vt["L4"] = f"=SUM({vr('H')})"
vt["K5"] = "Lifetime gross loss %"; vt["L5"] = f"=SUMPRODUCT({vr('G')},{vr('B')},{vr('H')})/SUMPRODUCT({vr('B')},{vr('H')})"
vt["K6"] = "Lifetime net loss %"; vt["L6"] = f"=SUMPRODUCT({vr('E')},{vr('B')},{vr('H')})/SUMPRODUCT({vr('B')},{vr('H')})"
vt["K7"] = "Implied recovery rate %"; vt["L7"] = "=(1-L6/L5)*100"
for c in ("L5", "L6", "L7"): vt[c].number_format = "0.00"
header(vt, 9, ["Year", "Lifetime net %"], col=11)
for k, y in enumerate(range(2019, 2027)):
    i = 10 + k
    vt.cell(i, 11, str(y))
    vt.cell(i, 12, f'=SUMPRODUCT(({vr("I")}=K{i})*{vr("E")}*{vr("B")}*{vr("H")})/SUMPRODUCT(({vr("I")}=K{i})*{vr("B")}*{vr("H")})').number_format = "0.00"
widths(vt, [10, 16, 12, 12, 14, 12, 14, 14, 8, 2, 28, 14])

wb.save(sys.argv[3])
print("saved", sys.argv[3])
