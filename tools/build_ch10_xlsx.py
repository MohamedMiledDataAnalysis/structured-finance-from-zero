"""Build ch10/excel/ch10_historical_performance.xlsx (live formulas).
Run: python3 tools/build_ch10_xlsx.py data/kingsbridge_static_pool_defaults.csv data/kingsbridge_dynamic_book.csv ch10/excel/ch10_historical_performance.xlsx"""
import sys, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter as L

NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); title = Font(bold=True, size=13, color=NAVY)
def head(ws, r, names, c0=1):
    for j, h in enumerate(names, c0):
        c = ws.cell(r, j, h); c.font = hdr; c.fill = fill

srows = list(csv.DictReader(open(sys.argv[1])))
drows = list(csv.DictReader(open(sys.argv[2])))
vints = sorted({r["vintage"] for r in srows})
NS, ND = len(srows) + 1, len(drows) + 1
ages = list(range(3, 130, 3))                      # 3..129

wb = Workbook()
nt = wb.active; nt.title = "Notes"
nt["A1"] = "Chapter 10 - Kingsbridge historical performance and the Thames base case"; nt["A1"].font = title
for i, t in enumerate([
    "StaticData and Dynamic hold the data supplied by Kingsbridge (one row per vintage and age; one row per month).",
    "Defaults and NetLoss: pivot-style grids built with SUMIFS (rows = months since origination, columns = vintage).",
    "Timing: share of 120-month defaults reached at each age, averaged over the fully seasoned vintages.",
    "Vintages: extrapolated lifetime default = observed cumulative default / timing factor at the same age.",
    "Lag: months between the half-way points of the default curve and the net loss curve.",
    "CPR: averaged through the single monthly mortality (SMM). Rolls: arrears stock 3 months later / stock now.",
    "Yellow cells are inputs (vintage thresholds, horizon). BaseCase collects the figures handed to the structuring desk."],
    start=3):
    nt.cell(i, 1, t)
nt.column_dimensions["A"].width = 110

# ---- StaticData
sd = wb.create_sheet("StaticData")
cols = ["vintage","originated_balance","months_since_origination","cumulative_default_pct",
        "cumulative_recovery_pct","cumulative_net_loss_pct"]
head(sd, 1, cols)
for i, r in enumerate(srows, 2):
    sd.cell(i, 1, r["vintage"])
    for j, c in enumerate(cols[1:], 2): sd.cell(i, j, float(r[c]))
SR = lambda c: f"StaticData!${c}$2:${c}${NS}"

# ---- Defaults and NetLoss grids
def grid(name, valcol):
    g = wb.create_sheet(name)
    g["A1"] = f"{name}: cumulative % of originated balance (blank = not yet observed)"; g["A1"].font = title
    head(g, 3, ["Age (m)"] + vints)
    for i, a in enumerate(ages, 4):
        g.cell(i, 1, a)
        for j, v in enumerate(vints, 2):
            col = L(j)
            g.cell(i, j, f'=IF(COUNTIFS({SR("A")},{col}$3,{SR("C")},$A{i})=0,"",'
                         f'SUMIFS({SR(valcol)},{SR("A")},{col}$3,{SR("C")},$A{i}))')
    g.freeze_panes = "B4"
    return g
grid("Defaults", "D"); grid("NetLoss", "F")
GLAST = 3 + len(ages)                               # last grid row (age 129)
ROW120 = 3 + ages.index(120) + 1                    # grid row of age 120

# ---- Timing
tm = wb.create_sheet("Timing")
tm["A1"] = "Timing curve from the fully seasoned vintages"; tm["A1"].font = title
tm["A2"] = "Fully seasoned vintages (inputs):"
mat = ["2016Q1", "2016Q2", "2016Q3", "2016Q4"]
for j, v in enumerate(mat, 2): tm.cell(2, j, v).fill = inp
head(tm, 4, ["Age (m)"] + [f"ratio {v}" for v in mat] + ["Timing factor"])
for i, a in enumerate(range(3, 121, 3), 5):
    tm.cell(i, 1, a)
    for j in range(2, 6):
        c = L(j)
        idx = f"MATCH({c}$2,Defaults!$B$3:$AO$3,0)"
        tm.cell(i, j, f"=INDEX(Defaults!$B$4:$AO${GLAST},MATCH($A{i},Defaults!$A$4:$A${GLAST},0),{idx})"
                      f"/INDEX(Defaults!$B${ROW120}:$AO${ROW120},1,{idx})")
    tm.cell(i, 6, f"=AVERAGE(B{i}:E{i})"); tm.cell(i, 6).number_format = "0.00%"
TLAST = 4 + 40

# ---- Lag
lg = wb.create_sheet("Lag")
lg["A1"] = "Default-to-loss lag: half-way points of the two curves (fully seasoned vintages)"; lg["A1"].font = title
head(lg, 3, ["Vintage", "Default at 120 m", "Default half-way age", "Loss at 120 m", "Loss half-way age", "Lag (m)"])
def half(sheet, r, valcell):
    col = f"INDEX({sheet}!$B$4:$AO$46,0,MATCH($A{r},{sheet}!$B$3:$AO$3,0))"
    k = f"MATCH({valcell}/2,{col},1)"
    y0 = f"INDEX({col},{k})"; y1 = f"INDEX({col},{k}+1)"
    a0 = f"INDEX({sheet}!$A$4:$A$46,{k})"
    return f"={a0}+({valcell}/2-{y0})/({y1}-{y0})*3"
for r, v in enumerate(mat, 4):
    lg.cell(r, 1, f"=Timing!{L(r-2)}2")
    lg.cell(r, 2, f"=INDEX(Defaults!$B${ROW120}:$AO${ROW120},1,MATCH($A{r},Defaults!$B$3:$AO$3,0))")
    lg.cell(r, 3, half("Defaults", r, f"B{r}"))
    lg.cell(r, 4, f"=INDEX(NetLoss!$B${ROW120}:$AO${ROW120},1,MATCH($A{r},NetLoss!$B$3:$AO$3,0))")
    lg.cell(r, 5, half("NetLoss", r, f"D{r}"))
    lg.cell(r, 6, f"=E{r}-C{r}")
lg["A9"] = "Average lag (m)"; lg["F9"] = "=AVERAGE(F4:F7)"
lg["A10"] = "Lag used (whole months)"; lg["F10"] = "=ROUND(F9,0)"
for c, w in zip("ABCDEF", [24, 16, 20, 14, 18, 10]): lg.column_dimensions[c].width = w

# ---- Vintages
vt = wb.create_sheet("Vintages")
vt["A1"] = "Extrapolated lifetime default and loss severity by vintage"; vt["A1"].font = title
vt["A2"] = "Minimum age for default base case (m)"; vt["E2"] = 24; vt["E2"].fill = inp
vt["A3"] = "Minimum age for severity (m)"; vt["E3"] = 36; vt["E3"].fill = inp
head(vt, 5, ["Vintage", "Originated (£)", "Last age", "Age used", "Observed default %",
             "Timing factor", "Lifetime default %", "Severity", "Use default?", "Use severity?"])
DEF = "Defaults!$B$4:$AO$46"; NLG = "NetLoss!$B$4:$AO$46"; AG = "Defaults!$A$4:$A$46"; HD = "Defaults!$B$3:$AO$3"
for r, v in enumerate(vints, 6):
    vt.cell(r, 1, v)
    vt.cell(r, 2, f'=INDEX({SR("B")},MATCH(A{r},{SR("A")},0))')
    vt.cell(r, 3, f'=_xlfn.MAXIFS({SR("C")},{SR("A")},A{r})')
    vt.cell(r, 4, f"=MIN(C{r},120)")
    vt.cell(r, 5, f"=INDEX({DEF},MATCH(D{r},{AG},0),MATCH(A{r},{HD},0))")
    vt.cell(r, 6, f"=INDEX(Timing!$F$5:$F${TLAST},MATCH(D{r},Timing!$A$5:$A${TLAST},0))")
    vt.cell(r, 7, f"=E{r}/F{r}")
    vt.cell(r, 8, f'=IF(C{r}>=$E$3,INDEX({NLG},MATCH(C{r},{AG},0),MATCH(A{r},{HD},0))'
                  f'/INDEX({DEF},MATCH(C{r}-Lag!$F$10,{AG},0),MATCH(A{r},{HD},0)),0)')
    vt.cell(r, 9, f"=C{r}>=$E$2"); vt.cell(r, 10, f"=C{r}>=$E$3")
    vt.cell(r, 2).number_format = "#,##0"; vt.cell(r, 6).number_format = "0.00%"
    vt.cell(r, 7).number_format = "0.0000"; vt.cell(r, 8).number_format = "0.00%"
VL = 5 + len(vints)
for c, w in zip("ABCDEFGHIJ", [10, 15, 9, 9, 12, 12, 12, 10, 11, 11]): vt.column_dimensions[c].width = w

# ---- Dynamic + CPR + rolls
dy = wb.create_sheet("Dynamic")
dcols = ["month","book_balance","cpr_annualised_pct","arrears_1_3m_pct","arrears_3_6m_pct",
         "arrears_6_12m_pct","arrears_12m_plus_pct","repossessions_in_month"]
head(dy, 1, dcols + ["SMM", "Calendar month", "Roll 1-3 to 3-6", "Roll 3-6 to 6-12"])
for i, r in enumerate(drows, 2):
    dy.cell(i, 1, r["month"])
    for j, c in enumerate(dcols[1:], 2): dy.cell(i, j, float(r[c]))
    dy.cell(i, 9, f"=1-(1-C{i}/100)^(1/12)"); dy.cell(i, 10, f"=VALUE(RIGHT(A{i},2))")
    if i >= 5:
        dy.cell(i, 11, f"=E{i}/D{i-3}"); dy.cell(i, 12, f"=F{i}/E{i-3}")
DR = lambda c: f"Dynamic!${c}$2:${c}${ND}"

cp = wb.create_sheet("CPR")
cp["A1"] = "Prepayment history"; cp["A1"].font = title
cp["A3"] = "CPR simple average (%)"; cp["B3"] = f"=AVERAGE({DR('C')})"
cp["A4"] = "Average SMM"; cp["B4"] = f"=AVERAGE({DR('I')})"
cp["A5"] = "Base-case CPR via SMM (%)"; cp["B5"] = "=100*(1-(1-B4)^12)"
cp["A6"] = "CPR in March and September (%)"
cp["B6"] = f"=(SUMIFS({DR('C')},{DR('J')},3)+SUMIFS({DR('C')},{DR('J')},9))/(COUNTIF({DR('J')},3)+COUNTIF({DR('J')},9))"
cp["A7"] = "CPR in other months (%)"
cp["B7"] = f"=(SUM({DR('C')})-B6*(COUNTIF({DR('J')},3)+COUNTIF({DR('J')},9)))/(COUNT({DR('C')})-COUNTIF({DR('J')},3)-COUNTIF({DR('J')},9))"
head(cp, 9, ["Calendar month", "Average CPR (%)"])
for m in range(1, 13):
    cp.cell(9 + m, 1, m); cp.cell(9 + m, 2, f"=AVERAGEIF({DR('J')},A{9+m},{DR('C')})")
cp["D3"] = "Roll 1-3m to 3-6m (%)"; cp["E3"] = f"=100*AVERAGE({DR('K')})"
cp["D4"] = "Roll 3-6m to 6-12m (%)"; cp["E4"] = f"=100*AVERAGE({DR('L')})"
cp.column_dimensions["A"].width = 32; cp.column_dimensions["D"].width = 24

# ---- BaseCase
bc = wb.create_sheet("BaseCase")
bc["A1"] = "Base case handed to the structuring desk (Thames Residential 2027-1)"; bc["A1"].font = title
VR = lambda c: f"Vintages!${c}$6:${c}${VL}"
items = [
    ("Base-case lifetime default (% of balance)",
     f"=SUMPRODUCT({VR('G')}*{VR('B')}*{VR('I')})/SUMPRODUCT({VR('B')}*{VR('I')})", "0.0000"),
    ("Base-case loss severity (%)",
     f"=100*SUMPRODUCT({VR('H')}*{VR('B')}*{VR('J')})/SUMPRODUCT({VR('B')}*{VR('J')})", "0.0000"),
    ("Default-to-loss (recovery) lag (months)", "=Lag!F10", "0"),
    ("Base-case CPR (% a year)", "=CPR!B5", "0.0000"),
    ("Base-case expected loss (% of balance)", "=B3*B4/100", "0.0000"),
    ("Vintages used for default", f"=COUNTIF({VR('I')},TRUE)", "0"),
    ("Vintages used for severity", f"=COUNTIF({VR('J')},TRUE)", "0")]
for i, (lab, f, fmt) in enumerate(items, 3):
    bc.cell(i, 1, lab); c = bc.cell(i, 2, f); c.number_format = fmt
head(bc, 11, ["Year after origination", "Share of lifetime defaults (%)"])
for y in range(1, 11):
    r = 11 + y
    bc.cell(r, 1, y)
    now = f"INDEX(Timing!$F$5:$F${TLAST},MATCH({12*y},Timing!$A$5:$A${TLAST},0))"
    prev = "0" if y == 1 else f"INDEX(Timing!$F$5:$F${TLAST},MATCH({12*(y-1)},Timing!$A$5:$A${TLAST},0))"
    bc.cell(r, 2, f"=100*({now}-{prev})"); bc.cell(r, 2).number_format = "0.00"
bc["D3"] = "Thames pool at cut-off (£)"; bc["E3"] = 635671146.31; bc["E3"].fill = inp
bc["D4"] = "Thames base-case defaults (£)"; bc["E4"] = "=ROUND(E3*B3/100,0)"
bc["D5"] = "Thames base-case loss (£)"; bc["E5"] = "=ROUND(E3*B3*B4/10000,0)"
for c in ("E3", "E4", "E5"): bc[c].number_format = "#,##0.00"
bc.column_dimensions["D"].width = 30; bc.column_dimensions["E"].width = 18
bc.column_dimensions["A"].width = 44; bc.column_dimensions["B"].width = 18
wb.save(sys.argv[3]); print("saved", sys.argv[3])
