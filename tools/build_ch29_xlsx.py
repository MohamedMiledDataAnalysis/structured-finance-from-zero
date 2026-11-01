"""Build ch29/excel/ch29_surveillance_dashboard.xlsx (Chapter 29).
Run from the book folder: python3 tools/build_ch29_xlsx.py ch29/excel/ch29_surveillance_dashboard.xlsx"""
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.chart import LineChart, BarChart, Reference
NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
perf = pd.concat([pd.read_csv("data/thames_performance_monthly.csv"),
                  pd.read_csv("data/ch26_thames_performance_2029_02.csv")], ignore_index=True)
ipd = pd.read_csv("data/thames_ipd_results.csv")
req = pd.read_csv("data/ch29_required_ce.csv")
book = pd.read_csv("data/kingsbridge_dynamic_book.csv"); b26 = book[book.month.str.startswith("2026")]
def head(ws, row, names, col0=1):
    for j, h in enumerate(names):
        c = ws.cell(row, col0 + j, h); c.font = hdr; c.fill = fill
        ws.column_dimensions[c.column_letter].width = max(ws.column_dimensions[c.column_letter].width or 0, 13)
def put(ws, r, c, v, fmt=None, yellow=False):
    cell = ws.cell(r, c, v)
    if fmt: cell.number_format = fmt
    if yellow: cell.fill = inp
    return cell
wb = Workbook(); ws = wb.active; ws.title = "Inputs"
ws["A1"] = "Chapter 29 - Thames Residential 2027-1 surveillance dashboard"; ws["A1"].font = Font(bold=True, size=13, color=NAVY)
put(ws, 3, 1, "Pool at cut-off (£)"); put(ws, 3, 2, 635671146.31, "#,##0.00", True)
put(ws, 4, 1, "Reserve required (£)"); put(ws, 4, 2, 9391500, "#,##0.00", True)
put(ws, 5, 1, "Clean-up call threshold"); put(ws, 5, 2, 0.10, "0%", True)
ws.column_dimensions["A"].width = 30
put(ws, 3, 4, "Ch 10 lifetime defaults (£)"); put(ws, 3, 5, 9273541, "#,##0.00", True)
put(ws, 4, 4, "Ch 10 severity"); put(ws, 4, 5, 0.166838, "0.0000%", True)
put(ws, 5, 4, "Ch 10 recovery lag (months)"); put(ws, 5, 5, 18, "0", True)
head(ws, 31, ["Year", "Timing %", "Monthly default (£)", "Monthly loss (£)"])
for y, sh in enumerate([5.73, 11.07, 23.34, 28.88, 19.09, 8.01, 2.70, 0.84, 0.26, 0.08], 1):
    rr = 31 + y
    put(ws, rr, 1, y); put(ws, rr, 2, sh, "0.00", True)
    put(ws, rr, 3, f"=ROUND($E$3*B{rr}/1200,2)", "#,##0.00"); put(ws, rr, 4, f"=ROUND(C{rr}*$E$4,2)", "#,##0.00")
put(ws, 43, 1, "Lifetime expected loss % of cut-off"); put(ws, 43, 4, "=12*SUM(D32:D41)/B3*100", "0.0000")
ws.column_dimensions["D"].width = 28
head(ws, 7, ["Rating", "Required CE at closing %", "Required CE now %"])
for i, r in req.iterrows():
    put(ws, 8 + i, 1, r.rating, yellow=True); put(ws, 8 + i, 2, r.closing_required_ce_pct, "0.00", True)
    put(ws, 8 + i, 3, r.surveillance_required_ce_pct, "0.00", True)
ws["A14"] = "Required CE levels are ILLUSTRATIVE rating agency model outputs. Yellow cells are inputs."
head(ws, 16, ["Kingsbridge book 2026", "3-6m %", "6-12m %", "12m+ %", "3m+ %"])
for i, (_, r) in enumerate(b26.iterrows()):
    rr = 17 + i
    put(ws, rr, 1, r.month, yellow=True)
    for j, c in enumerate(["arrears_3_6m_pct", "arrears_6_12m_pct", "arrears_12m_plus_pct"]):
        put(ws, rr, 2 + j, r[c], "0.000", True)
    put(ws, rr, 5, f"=B{rr}+C{rr}+D{rr}", "0.000")
put(ws, 29, 1, "Average 3m+ arrears 2026 %"); put(ws, 29, 5, "=AVERAGE(E17:E28)", "0.000")

m = wb.create_sheet("Monthly")
cols = ["Period", "Closing balance", "Loans", "Realised losses", "Arrears 1-3m %", "Arrears 3-6m %",
        "Arrears 6m+ %", "CPR %", "Defaulted balance", "Arrears 3m+ %", "Cum. loss %", "Base default (£)",
        "Base loss (£)", "Base cum. default %", "Base cum. loss %", "Cum. default %"]
head(m, 1, cols)
for i, r in perf.iterrows():
    rr = 2 + i
    vals = [r.collection_period, r.closing_balance, int(r.loans_closing), r.realised_losses, r.arrears_1_3m_pct,
            r.arrears_3_6m_pct, r.arrears_6m_plus_pct, r.cpr_annualised_pct, r.defaulted_balance]
    fmts = [None, "#,##0.00", "#,##0", "#,##0.00", "0.000", "0.000", "0.000", "0.00", "#,##0.00"]
    for j, (v, f) in enumerate(zip(vals, fmts)): put(m, rr, 1 + j, v, f, True)
    put(m, rr, 10, f"=F{rr}+G{rr}", "0.000")
    put(m, rr, 11, f"=SUM($D$2:D{rr})/Inputs!$B$3*100", "0.0000")
    put(m, rr, 12, f"=INDEX(Inputs!$C$32:$C$41,INT({i}/12)+1)", "#,##0.00")
    put(m, rr, 13, f"=INDEX(Inputs!$D$32:$D$41,INT({i}/12)+1)", "#,##0.00")
    put(m, rr, 14, f"=SUM($L$2:L{rr})/Inputs!$B$3*100", "0.0000")
    lag_sum = f"SUM($M$2:INDEX($M$2:$M$26,{i + 1}-Inputs!$E$5))"
    put(m, rr, 15, f"=IF({i + 1}>Inputs!$E$5,{lag_sum},0)/Inputs!$B$3*100", "0.0000")
    put(m, rr, 16, f"=SUM($I$2:I{rr})/Inputs!$B$3*100", "0.0000")
m.freeze_panes = "B2"

q = wb.create_sheet("IPD")
cls = list("abcdez")
inc = (["IPD", "Pool end"] + [f"Class {c.upper()}" for c in cls] + ["Reserve after"] +
       [f"PDL {c.upper()}" for c in cls] + ["r16 Z PDL", "r17", "r18 interest", "r18 principal", "r19",
       "Reserve drawn", "Principal additions"])
head(q, 1, inc)
src = (["ipd", "pool_balance_end"] + [f"class_{c}_balance_after" for c in cls] + ["reserve_balance_after"] +
       [f"pdl_{c}_after" for c in cls] + ["r16_class_z_pdl", "r17_sub_swap_termination", "r18_sub_loan_interest",
       "r18_sub_loan_principal", "r19_deferred_consideration", "reserve_drawn", "principal_addition_amounts"])
calc = ["Factor %", "CE A %", "CE B %", "CE C %", "CE D %", "CE E %", "PDL total", "Excess spread", "Realised losses"]
head(q, 1, calc, col0=len(inc) + 1)
L = lambda k: q.cell(1, k).column_letter
for i, r in ipd.iterrows():
    rr = 2 + i
    for j, s in enumerate(src):
        put(q, rr, 1 + j, r[s], None if j == 0 else "#,##0.00", True)
    k0 = len(inc) + 1
    put(q, rr, k0, f"=B{rr}/Inputs!$B$3*100", "0.00")
    for n in range(5):   # CE of class n: classes below + reserve
        below = "+".join(f"{L(4 + x)}{rr}" for x in range(n, 5))   # columns of classes n+1..Z
        put(q, rr, k0 + 1 + n, f"=({below}+Inputs!$B$4)/B{rr}*100", "0.00")
    put(q, rr, k0 + 6, f"=SUM({L(10)}{rr}:{L(15)}{rr})", "#,##0.00")
    put(q, rr, k0 + 7, f"=SUM({L(16)}{rr}:{L(20)}{rr})", "#,##0.00")
    put(q, rr, k0 + 8, r.realised_losses, "#,##0.00", True)

d = wb.create_sheet("Dashboard", 1)
d["A1"] = "Surveillance dashboard after the last IPD"; d["A1"].font = Font(bold=True, size=13, color=NAVY)
last_m, last_q = 1 + len(perf), 1 + len(ipd)
CE0 = len(inc) + 2   # column of CE A
rows = [("Pool balance (£)", f"=Monthly!B{last_m}", "#,##0.00"),
        ("Pool factor %", f"=Monthly!B{last_m}/Inputs!B3*100", "0.00"),
        ("Loans", f"=Monthly!C{last_m}", "#,##0"),
        ("Cumulative losses (£)", f"=SUM(Monthly!D2:D{last_m})", "#,##0.00"),
        ("Cumulative loss % of cut-off", f"=Monthly!K{last_m}", "0.0000"),
        ("Base case loss %, same month", f"=Monthly!O{last_m}", "0.0000"),
        ("Actual / base case loss %", "=B7/B8*100", "0"),
        ("3m+ arrears %", f"=Monthly!J{last_m}", "0.000"),
        ("Kingsbridge book 3m+ 2026 %", "=Inputs!E29", "0.000"),
        ("CPR, 3-month average %", f"=AVERAGE(Monthly!H{last_m-2}:H{last_m})", "0.00"),
        ("CPR, 12-month average %", f"=AVERAGE(Monthly!H{last_m-11}:H{last_m})", "0.00"),
        ("Reserve at required amount", f'=IF(IPD!{L(9)}{last_q}>=Inputs!B4,"YES","NO")', None),
        ("All PDL sub-ledgers at zero", f'=IF(IPD!{L(CE0+5)}{last_q}=0,"YES","NO")', None),
        ("Reserve ever drawn", f'=IF(SUM(IPD!{L(21)}2:{L(21)}{last_q})>0,"YES","NO")', None),
        ("Principal paid interest", f'=IF(SUM(IPD!{L(22)}2:{L(22)}{last_q})>0,"YES","NO")', None),
        ("Pool above clean-up (10%)", f'=IF(IPD!B{last_q}>Inputs!B5*Inputs!B3,"YES","NO")', None),
        ("Cumulative default %", f"=Monthly!P{last_m}", "0.0000"),
        ("Base case default %, same month", f"=Monthly!N{last_m}", "0.0000"),
        ("Severity to date %", "=B6/SUM(Monthly!I2:I26)*100", "0.00"),
        ("Share of lifetime EL %", "=B7/Inputs!D43*100", "0.0")]
for i, (lab, f, fmt) in enumerate(rows):
    d.cell(3 + i, 1, lab); put(d, 3 + i, 2, f, fmt)
d.column_dimensions["A"].width = 30; d.column_dimensions["B"].width = 18
head(d, 25, ["Class", "Rating", "CE now %", "Passes", "Cushion"])
for n, (c, rt) in enumerate(zip("ABCDE", ["AAA(sf)", "AA(sf)", "A(sf)", "BBB(sf)", "BB(sf)"])):
    rr = 26 + n
    d.cell(rr, 1, c); d.cell(rr, 2, rt)
    put(d, rr, 3, f"=IPD!{L(CE0 + n)}{last_q}", "0.00")
    put(d, rr, 4, f'=INDEX(Inputs!$A$8:$A$12,COUNTIF(Inputs!$C$8:$C$12,">"&C{rr})+1)')
    put(d, rr, 5, f'=C{rr}-INDEX(Inputs!$C$8:$C$12,COUNTIF(Inputs!$C$8:$C$12,">"&C{rr})+1)', "0.00")
head(d, 32, ["Next category", "Gain per IPD", "Gap", "IPDs needed"])
for n, (c, nxt_row) in enumerate([("C", 9), ("D", 10), ("E", 11)]):
    rr = 33 + n; ce_col = L(CE0 + 2 + n)
    d.cell(rr, 1, f"{c} to " + req.rating[nxt_row - 8])
    put(d, rr, 2, f"=(IPD!{ce_col}{last_q}-IPD!{ce_col}{last_q-4})/4", "0.0000")
    put(d, rr, 3, f"=Inputs!C{nxt_row}-C{28 + n}", "0.00")
    put(d, rr, 4, f"=ROUNDUP(C{rr}/B{rr},0)", "0")
def chart(kind, title, ytitle, ws, cols_, rows_, cat_col, anchor, w=12, h=6.5):
    ch = LineChart() if kind == "line" else BarChart()
    ch.title = title; ch.y_axis.title = ytitle; ch.height = h; ch.width = w; ch.legend.position = "b"
    for c in cols_:
        ch.add_data(Reference(ws, min_col=c, min_row=1, max_row=rows_), titles_from_data=True)
    ch.set_categories(Reference(ws, min_col=cat_col, min_row=2, max_row=rows_))
    d.add_chart(ch, anchor)
chart("line", "Arrears", "% of pool", m, [5, 10], last_m, 1, "G2")
chart("line", "CPR", "% a year", m, [8], last_m, 1, "P2")
chart("line", "Cumulative net loss vs base case", "% of cut-off", m, [11, 15], last_m, 1, "G16")
chart("line", "Credit enhancement by class", "% of pool", q, [CE0 + n for n in range(5)], last_q, 1, "P16")
chart("bar", "Reserve fund", "GBP", q, [9], last_q, 1, "G30")
chart("bar", "PDL: debited and balance", "GBP", q, [len(inc) + 9, CE0 + 5], last_q, 1, "P30")
wb.save(sys.argv[1])
