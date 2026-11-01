"""Build ch04/excel/ch04_funding.xlsx (Chapter 4 - Why securitise). All market rates illustrative.
Run: python3 tools/build_ch04_xlsx.py ch04/excel/ch04_funding.xlsx"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); title = Font(bold=True, size=13, color=NAVY)
wb = Workbook(); ws = wb.active; ws.title = "Funding"
ws["A1"] = "Chapter 4 - Cost of Thames funding (illustrative SONIA and costs)"; ws["A1"].font = title
for j, h in enumerate(["Class", "Amount (£)", "Margin", "Amount x margin"], 1):
    c = ws.cell(3, j, h); c.font = hdr; c.fill = fill; c.alignment = Alignment(horizontal="center")
for i, (cl, a, m) in enumerate([("A", 553000000, 0.0062), ("B", 31800000, 0.011), ("C", 19100000, 0.015),
                                ("D", 12700000, 0.022), ("E", 9500000, 0.035)], start=4):
    ws.cell(i, 1, cl); ws.cell(i, 2, a).fill = inp; ws.cell(i, 3, m).fill = inp
    ws.cell(i, 4, f"=B{i}*C{i}")
    ws.cell(i, 2).number_format = ws.cell(i, 4).number_format = "#,##0.00"; ws.cell(i, 3).number_format = "0.00%"
ws["A9"] = "Total"; ws["B9"] = "=SUM(B4:B8)"; ws["D9"] = "=SUM(D4:D8)"
ws["B9"].number_format = ws["D9"].number_format = "#,##0.00"
items = [  # row, label, value, format
    (11, "SONIA (flat, illustrative)", 0.0375, "0.00%"),
    (12, "Weighted average margin", "=D9/B9", "0.0000%"),
    (13, "Annual interest on A-E (£)", "=ROUND(B9*(B11+B12),2)", "#,##0.00"),
    (14, "Trustee fee (£ a year)", 25000, "#,##0.00"),
    (15, "Corporate services (£ a year)", 20000, "#,##0.00"),
    (16, "Paying agent and agent bank (£ a year)", 10000, "#,##0.00"),
    (17, "Other issuer expenses (£ a year)", 120000, "#,##0.00"),
    (18, "Issuer profit (£ per IPD)", 1000, "#,##0.00"),
    (19, "Third-party running costs (£ a year)", "=SUM(B14:B17)+4*B18", "#,##0.00"),
    (20, "Running costs, % a year", "=B19/B9", "0.0000%"),
    (21, "Upfront costs (£, illustrative)", 3000000, "#,##0.00"),
    (22, "Years to first optional redemption", 5, "0"),
    (23, "Upfront costs, % a year", "=B21/B22/B9", "0.0000%"),
    (24, "All-in spread over SONIA", "=B12+B20+B23", "0.0000%"),
    (25, "All-in rate", "=B11+B24", "0.0000%"),
]
for r, lab, v, fmt in items:
    ws.cell(r, 1, lab); c = ws.cell(r, 2, v); c.number_format = fmt
    if not (isinstance(v, str) and v.startswith("=")): c.fill = inp
ws["A27"] = "Spread over SONIA by source"; ws["A27"].font = Font(bold=True, color=NAVY)
ws["A28"] = "Retail savings rate"; ws["B28"] = 0.041; ws["B28"].fill = inp
ws["A29"] = "Retail savings, spread"; ws["B29"] = "=B28-B11"
ws["A30"] = "Covered bond, 5 years, spread"; ws["B30"] = 0.0045; ws["B30"].fill = inp
ws["A31"] = "Thames RMBS, all-in spread"; ws["B31"] = "=B24"
for c in ("B28", "B29", "B30", "B31"): ws[c].number_format = "0.0000%"
ws.column_dimensions["A"].width = 40; ws.column_dimensions["B"].width = 18
ws.column_dimensions["C"].width = 10; ws.column_dimensions["D"].width = 18

wh = wb.create_sheet("Warehouse")
wh["A1"] = "Warehouse to term (illustrative non-bank lender)"; wh["A1"].font = title
for r, lab, v, fmt in [(3, "Mortgage pool (£)", 300000000, "#,##0.00"), (4, "Advance rate", 0.90, "0.00%"),
                       (5, "Warehouse margin over SONIA", 0.0175, "0.00%"), (6, "SONIA", "=Funding!B11", "0.00%"),
                       (7, "Days in warehouse", 182, "0"), (8, "Senior warehouse funding (£)", "=B3*B4", "#,##0.00"),
                       (9, "Lender's own funding (£)", "=B3-B8", "#,##0.00"),
                       (10, "Warehouse interest (£)", "=ROUND(B8*(B6+B5)*B7/365,2)", "#,##0.00"),
                       (11, "Term margin (Thames weighted average)", "=Funding!B12", "0.0000%"),
                       (12, "Saving a year at term (£)", "=ROUND(B8*(B5-B11),2)", "#,##0.00")]:
    wh.cell(r, 1, lab); c = wh.cell(r, 2, v); c.number_format = fmt
    if not (isinstance(v, str) and v.startswith("=")): c.fill = inp
wh.column_dimensions["A"].width = 40; wh.column_dimensions["B"].width = 18
wb.save(sys.argv[1])
