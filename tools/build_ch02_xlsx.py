"""Build ch02/excel/ch02_bonds.xlsx (Chapter 2 - Bonds).
Run: python3 tools/build_ch02_xlsx.py ch02/excel/ch02_bonds.xlsx"""
import sys
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); title = Font(bold=True, size=13, color=NAVY)


def block(ws, items, start=3):
    for i, (lab, val, fmt) in enumerate(items, start=start):
        ws.cell(i, 1, lab); c = ws.cell(i, 2, val); c.number_format = fmt
        if not (isinstance(val, str) and val.startswith("=")): c.fill = inp
    ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 18


def header(ws, row, names, width=14):
    for j, h in enumerate(names, 1):
        c = ws.cell(row, j, h); c.font = hdr; c.fill = fill
        c.alignment = Alignment(horizontal="center")
        if j > 2: ws.column_dimensions[chr(64 + j)].width = width


wb = Workbook()
# ---- ClassA
ws = wb.active; ws.title = "ClassA"
ws["A1"] = "Chapter 2 - Thames Class A, first interest period"; ws["A1"].font = title
block(ws, [
    ("Class A principal (£)", 553000000, "#,##0.00"),                 # B3
    ("Compounded SONIA (illustrative)", 0.0375, "0.00%"),           # B4
    ("Class A margin", 0.0062, "0.00%"),                             # B5
    ("Period start (closing date)", date(2027, 3, 18), "dd mmm yyyy"),  # B6
    ("Period end (first IPD)", date(2027, 6, 15), "dd mmm yyyy"),   # B7
    ("Days in period", "=B7-B6", "0"),                               # B8
    ("Coupon rate", "=B4+B5", "0.00%"),                              # B9
    ("Interest on Class A (£)", "=ROUND(B3*B9*B8/365,2)", "#,##0.00"),  # B10
    ("Interest per £100,000 (£)", "=ROUND(100000*B9*B8/365,2)", "#,##0.00"),  # B11
])
ws["A13"] = "Day count Actual/365 (Fixed): actual days / 365. Yellow cells are inputs."

# ---- FixedBond
fb = wb.create_sheet("FixedBond")
fb["A1"] = "A five-year bond, 4.00% coupon paid once a year (illustrative)"; fb["A1"].font = title
block(fb, [
    ("Coupon per 100 face", 4.00, "0.00"),                  # B3
    ("Years to maturity", 5, "0"),                           # B4
    ("Yield to maturity", 0.045, "0.00%"),                   # B5
    ("Market price", 98.60, "0.00"),                         # B6
    ("Gilt yield, 5 years (illustrative)", 0.039, "0.00%"),  # B7
    ("Days since last coupon", 73, "0"),                     # B8
    ("Price at yield in B5", "=PV(B5,B4,-B3,-100)", "0.0000"),        # B9
    ("Yield at price in B6", "=RATE(B4,B3,-B6,100)", "0.0000%"),      # B10
    ("Spread over gilt at B5 (bp)", "=(B5-B7)*10000", "0"),          # B11
    ("Spread over gilt at B6 (bp)", "=(B10-B7)*10000", "0.00"),      # B12
    ("Accrued interest", "=B3*B8/365", "0.0000"),                    # B13
    ("Clean price (quoted)", "=ROUND(B9,2)", "0.00"),                # B14
    ("Dirty price (paid)", "=B14+B13", "0.00"),                      # B15
    ("Macaulay duration (years)", "=SUM(D22:D26)/B9", "0.0000"),     # B16
    ("Modified duration", "=B16/(1+B5)", "0.0000"),                  # B17
    ("Price at yield +1.00% (exact)", "=PV(B5+0.01,B4,-B3,-100)", "0.0000"),  # B18
    ("Price at yield +1.00% (duration)", "=B9*(1-B17*0.01)", "0.0000"),       # B19
])
fb["A20"] = "PV01 per 100"; fb["B20"] = "=B17*B9/10000"; fb["B20"].number_format = "0.0000"
header(fb, 21, ["Year t", "Cash flow", "PV of cash flow", "t x PV"])
for t in range(1, 6):
    r = 21 + t
    fb.cell(r, 1, t)
    fb.cell(r, 2, f"=$B$3+IF(A{r}=$B$4,100,0)")
    fb.cell(r, 3, f"=B{r}/(1+$B$5)^A{r}")
    fb.cell(r, 4, f"=A{r}*C{r}")
    for j in (2, 3, 4): fb.cell(r, j).number_format = "0.0000"
fb["A27"] = "Total"; fb["C27"] = "=SUM(C22:C26)"; fb["C27"].number_format = "0.0000"

# ---- FRN
fr = wb.create_sheet("FRN")
fr["A1"] = "Floating-rate note: discount margin (flat SONIA, repaid after 20 quarters)"; fr["A1"].font = title
block(fr, [
    ("SONIA (flat, illustrative)", 0.0375, "0.00%"),         # B3
    ("Quoted margin", 0.0062, "0.00%"),                       # B4
    ("Quarters to repayment", 20, "0"),                       # B5
    ("Price", 99.50, "0.00"),                                 # B6
    ("Quarterly coupon per 100", "=(B3+B4)/4*100", "0.0000"),            # B7
    ("Quarterly discount rate", "=RATE(B5,B7,-B6,100)", "0.000000%"),     # B8
    ("Discount margin", "=B8*4-B3", "0.0000%"),                           # B9
    ("Discount margin at par (check)", "=RATE(B5,B7,-100,100)*4-B3", "0.0000%"),  # B10
])

# ---- Amortising
am = wb.create_sheet("Amortising")
am["A1"] = "Amortising bond: 100 repaid 20 a year, 4.00% coupon"; am["A1"].font = title
block(am, [("Coupon rate", 0.04, "0.00%"), ("Principal repaid each year", 20, "0.00")])
header(am, 6, ["Year", "Opening", "Interest", "Principal", "Closing"])
for t in range(1, 6):
    r = 6 + t
    am.cell(r, 1, t)
    am.cell(r, 2, 100 if t == 1 else f"=E{r-1}")
    am.cell(r, 3, f"=B{r}*$B$3"); am.cell(r, 4, "=$B$4"); am.cell(r, 5, f"=B{r}-D{r}")
    for j in range(2, 6): am.cell(r, j).number_format = "0.00"
am["A13"] = "Total interest"; am["C13"] = "=SUM(C7:C11)"
am["A14"] = "Weighted average life (years)"; am["C14"] = "=SUMPRODUCT(A7:A11,D7:D11)/SUM(D7:D11)"
am["C13"].number_format = am["C14"].number_format = "0.00"
wb.save(sys.argv[1])
