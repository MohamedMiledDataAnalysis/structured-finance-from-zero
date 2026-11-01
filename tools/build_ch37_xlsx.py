"""Builds ch37/excel/ch37_clo_coverage_tests.xlsx (Calder Park CLO 1 DAC).
Run from the book folder:
  python3 tools/build_ch37_xlsx.py ch37/excel/ch37_clo_coverage_tests.xlsx"""
import sys
import csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF")
fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
MONEY, PCT = "#,##0.00", "0.00%"


def header(ws, row, names, widths=None):
    for j, h in enumerate(names, 1):
        c = ws.cell(row, j, h)
        c.font, c.fill = hdr, fill
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        if widths:
            ws.column_dimensions[chr(64 + j)].width = widths[j - 1]


wb = Workbook()
ws = wb.active
ws.title = "Inputs"
ws["A1"] = "Chapter 37 - Calder Park CLO 1 DAC: coverage tests (illustrative)"
ws["A1"].font = Font(bold=True, size=13, color=NAVY)
items = [("Principal cash (EUR)", 8150000, MONEY),
         ("CCC limit (% of performing par)", 0.075, PCT),
         ("3M EURIBOR (illustrative)", 0.0225, PCT),
         ("Days in period (Act/360)", 90, "0"),
         ("Senior expenses for the period (EUR)", 60000, MONEY),
         ("Senior management fee (p.a.)", 0.0015, PCT),
         ("Target par, fee base (EUR)", 400000000, MONEY)]
for i, (lab, val, fmt) in enumerate(items, start=3):
    ws.cell(i, 1, lab)
    c = ws.cell(i, 2, val)
    c.number_format, c.fill = fmt, inp
ws.column_dimensions["A"].width = 36
header(ws, 12, ["Class", "Balance (EUR)", "Margin", "OC trigger",
                "IC trigger", "Period interest", "Cumulative balance",
                "Cumulative interest"])
for col, w in zip("BCDEFGH", [16, 9, 11, 11, 15, 18, 18]):
    ws.column_dimensions[col].width = w
with open("data/ch37_clo_notes.csv") as fh:
    notes = list(csv.DictReader(fh))
r = 13
for n in notes:
    if n["class"] == "Subordinated":
        continue
    ws.cell(r, 1, n["class"])
    ws.cell(r, 2, float(n["balance_eur"])).number_format = MONEY
    ws.cell(r, 3, float(n["margin_pct"]) / 100).number_format = PCT
    for col, key in ((4, "oc_trigger_pct"), (5, "ic_trigger_pct")):
        if n[key]:
            ws.cell(r, col, float(n[key]) / 100).number_format = PCT
    for col in (2, 3, 4, 5):
        ws.cell(r, col).fill = inp
    ws.cell(r, 6, f"=ROUND(B{r}*($B$5+C{r})*$B$6/360,2)")
    ws.cell(r, 7, f"=B{r}" if r == 13 else f"=G{r-1}+B{r}")
    ws.cell(r, 8, f"=F{r}" if r == 13 else f"=H{r-1}+F{r}")
    for col in (6, 7, 8):
        ws.cell(r, col).number_format = MONEY
    r += 1
ws["A21"] = "Yellow cells are inputs. Every other cell is a formula."

# ---- Portfolio ----
pf = wb.create_sheet("Portfolio")
cols = ["Obligation", "Industry", "Country", "Rating", "Par (EUR)",
        "Price (%)", "Spread (bps)", "Defaulted", "Recovery rate (%)",
        "CCC (performing)", "CCC par priced lower", "Excess CCC part",
        "Haircut", "Defaulted carrying value", "Period interest"]
header(pf, 1, cols, [11, 18, 14, 7, 14, 9, 9, 9, 9, 9, 14, 14, 12, 14, 13])
with open("data/ch37_clo_portfolio.csv") as fh:
    rows = list(csv.DictReader(fh))
last = len(rows) + 1
for i, row in enumerate(rows, start=2):
    pf.cell(i, 1, row["obligation_id"])
    pf.cell(i, 2, row["industry"])
    pf.cell(i, 3, row["country"])
    pf.cell(i, 4, row["rating"])
    pf.cell(i, 5, float(row["par_eur"])).number_format = MONEY
    pf.cell(i, 6, float(row["market_price_pct"])).number_format = "0.00"
    pf.cell(i, 7, int(row["spread_bps"]))
    pf.cell(i, 8, row["defaulted"])
    if row["recovery_rate_pct"]:
        pf.cell(i, 9, float(row["recovery_rate_pct"]))
    for col in range(1, 10):
        pf.cell(i, col).fill = inp
    pf.cell(i, 10, f'=IF(AND(H{i}="N",LEFT(D{i},3)="CCC"),"Y","N")')
    pf.cell(i, 11, f'=IF(J{i}="Y",SUMIFS($E$2:$E${last},$J$2:$J${last},"Y",'
                   f'$F$2:$F${last},"<"&F{i}),0)')
    pf.cell(i, 12, f'=IF(J{i}="Y",MAX(0,MIN(E{i},Tests!$B$6-K{i})),0)')
    pf.cell(i, 13, f"=L{i}-ROUND(L{i}*F{i}/100,2)")
    pf.cell(i, 14, f'=IF(H{i}="Y",ROUND(E{i}*MIN(F{i},I{i})/100,2),0)')
    pf.cell(i, 15, f'=IF(H{i}="N",ROUND(E{i}*(Inputs!$B$5+G{i}/10000)'
                   f'*Inputs!$B$6/360,2),0)')
    for col in (11, 12, 13, 14, 15):
        pf.cell(i, col).number_format = MONEY
pf.freeze_panes = "B2"

# ---- Tests ----
ts = wb.create_sheet("Tests")
ts["A1"] = "Coverage tests on the determination date"
ts["A1"].font = Font(bold=True, size=13, color=NAVY)
E, H, J = (f"Portfolio!$E$2:$E${last}", f"Portfolio!$H$2:$H${last}",
           f"Portfolio!$J$2:$J${last}")
lines = [
    ("Performing par", f'=SUMIFS({E},{H},"N")'),
    ("CCC par (performing)", f'=SUMIFS({E},{J},"Y")'),
    ("CCC limit", "=ROUND(Inputs!B4*B3,2)"),
    ("CCC excess", "=MAX(0,B4-B5)"),
    ("CCC excess haircut", f"=SUM(Portfolio!M2:M{last})"),
    ("Defaulted par", f'=SUMIFS({E},{H},"Y")'),
    ("Defaulted carrying value", f"=SUM(Portfolio!N2:N{last})"),
    ("Principal cash", "=Inputs!B3"),
    ("Adjusted collateral principal amount (ACPA)", "=B3-B7+B9+B10"),
    ("Interest proceeds", f"=SUM(Portfolio!O2:O{last})"),
    ("Senior expenses and fee",
     "=Inputs!B7+ROUND(Inputs!B9*Inputs!B8*Inputs!B6/360,2)"),
    ("IC numerator", "=B12-B13"),
]
for i, (lab, f) in enumerate(lines, start=3):
    ts.cell(i, 1, lab)
    ts.cell(i, 2, f).number_format = MONEY
ts["C4"] = "=B4/B3"; ts["C4"].number_format = PCT; ts["D4"] = "of performing par"
ts.column_dimensions["A"].width = 40
header(ts, 17, ["Test", "Denominator (EUR)", "Ratio", "Trigger", "Result"])
for col, w in zip("BCDE", [18, 10, 10, 9]):
    ts.column_dimensions[col].width = w
tests = [("OC A/B", "G14", "D14", "oc"), ("IC A/B", "H14", "E14", "ic"),
         ("OC C", "G15", "D15", "oc"), ("IC C", "H15", "E15", "ic"),
         ("OC D", "G16", "D16", "oc"), ("IC D", "H16", "E16", "ic"),
         ("OC E", "G17", "D17", "oc"), ("OC F", "G18", "D18", "oc")]
for i, (lab, den, trig, kind) in enumerate(tests, start=18):
    ts.cell(i, 1, lab)
    ts.cell(i, 2, f"=Inputs!{den}").number_format = MONEY
    num = "$B$11" if kind == "oc" else "$B$14"
    ts.cell(i, 3, f"={num}/B{i}").number_format = PCT
    ts.cell(i, 4, f"=Inputs!{trig}").number_format = PCT
    ts.cell(i, 5, f'=IF(C{i}>=D{i},"PASS","FAIL")')
ts["A28"] = "Class F OC cure: Class A redemption needed"
ts["B28"] = "=ROUNDUP(Inputs!G18-B11/Inputs!D18,2)"
ts["A29"] = "Interest left after Class F interest"
ts["B29"] = "=B14-Inputs!H18"
ts["A30"] = "Amount diverted to redeem Class A"
ts["B30"] = "=MIN(B28,B29)"
for c in ("B28", "B29", "B30"):
    ts[c].number_format = MONEY
wb.save(sys.argv[1])
