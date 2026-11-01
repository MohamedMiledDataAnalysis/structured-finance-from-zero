"""Build ch06/excel/ch06_ltv_lti_wa.xlsx (every calculated cell is a live formula).
Run from the book folder:
  python3 tools/build_ch06_xlsx.py data/thames_residential_2027_1_tape.csv ch06/excel/ch06_ltv_lti_wa.xlsx"""
import sys, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
title = Font(bold=True, size=13, color=NAVY)
rows = list(csv.DictReader(open(sys.argv[1])))
N = len(rows); last = N + 1
wb = Workbook()

# ---- Notes
ws = wb.active; ws.title = "Notes"
ws["A1"] = "Chapter 6 - LTV, LTI and weighted averages (Thames Residential 2027-1)"; ws["A1"].font = title
notes = ["Yellow cells are inputs (the tape and the example assumptions). Every other number is a formula.",
         "Original LTV = original balance / original valuation (in %).",
         "Current LTV (unindexed) = current balance / original valuation (in %).",
         "LTI = original balance / gross annual income of all borrowers at origination.",
         "Weighted averages use the current balance at the cut-off date (31 January 2027) as the weight.",
         "Seasoning = payments made at the cut-off date (months since the first payment month)."]
for i, n in enumerate(notes, start=3): ws.cell(i, 1, n)
ws.column_dimensions["A"].width = 100

# ---- Tape
tp = wb.create_sheet("Tape")
cols = [("loan_id", "A"), ("original_balance", "B"), ("current_balance", "C"), ("original_valuation", "D"),
        ("gross_income", "E"), ("current_rate", "F"), ("payments_made", "G"), ("remaining_term_months", "H"),
        ("fixed_rate_end_date", "I"), ("product_type", "J")]
calc = [("orig_LTV_pct", "K"), ("curr_LTV_pct", "L"), ("LTI", "M"), ("LTI_ge_4.5", "N"), ("reverts_12m", "O")]
for j, (h, c) in enumerate(cols + calc, start=1):
    x = tp.cell(1, j, h); x.font = hdr; x.fill = fill; x.alignment = Alignment(horizontal="center")
    tp.column_dimensions[c].width = 15
num = {"original_balance", "current_balance", "original_valuation", "gross_income", "current_rate",
       "payments_made", "remaining_term_months"}
for i, r in enumerate(rows, start=2):
    for j, (h, c) in enumerate(cols, start=1):
        v = r[h]
        if h in num: v = float(v) if "." in v else int(v)
        cell = tp.cell(i, j, v); cell.fill = inp
        if h in ("original_balance", "current_balance"): cell.number_format = "#,##0.00"
    tp[f"K{i}"] = f"=100*B{i}/D{i}"
    tp[f"L{i}"] = f"=100*C{i}/D{i}"
    tp[f"M{i}"] = f"=B{i}/E{i}"
    tp[f"N{i}"] = f"=IF(M{i}>=Summary!$B$20,1,0)"
    tp[f"O{i}"] = f'=IF(AND(I{i}<>"",I{i}<=Summary!$B$21),1,0)'
    for c in "KLM": tp[f"{c}{i}"].number_format = "0.00"
tp.freeze_panes = "B2"

# ---- Summary
sm = wb.create_sheet("Summary", 1)
sm["A1"] = "Pool summary at the cut-off date"; sm["A1"].font = title
R = lambda c: f"Tape!{c}2:{c}{last}"
sm["A3"] = "Number of loans"; sm["B3"] = f"=COUNTA({R('A')})"
sm["A4"] = "Current balance (£)"; sm["B4"] = f"=SUM({R('C')})"; sm["B4"].number_format = "#,##0.00"
for j, h in enumerate(["Measure", "Weighted", "Simple"], start=1):
    x = sm.cell(6, j, h); x.font = hdr; x.fill = fill
meas = [("Original LTV (%)", "K"), ("Current LTV (%)", "L"), ("Interest rate (%)", "F"),
        ("Seasoning (months)", "G"), ("Remaining term (months)", "H"), ("LTI", "M")]
for i, (lab, c) in enumerate(meas, start=7):
    sm.cell(i, 1, lab)
    sm.cell(i, 2, f"=SUMPRODUCT({R(c)},{R('C')})/SUM({R('C')})").number_format = "0.00"
    sm.cell(i, 3, f"=AVERAGE({R(c)})").number_format = "0.00"
sm["A14"] = "Loans with LTI >= threshold"; sm["B14"] = f"=SUM({R('N')})"
sm["A15"] = "  % of loans"; sm["B15"] = "=100*B14/B3"; sm["B15"].number_format = "0.00"
sm["A16"] = "  balance (£)"; sm["B16"] = f"=SUMPRODUCT({R('N')},{R('C')})"; sm["B16"].number_format = "#,##0.00"
sm["A17"] = "  % of pool balance"; sm["B17"] = "=100*B16/B4"; sm["B17"].number_format = "0.00"
sm["A18"] = "Fixed loans reverting by the date in B21"; sm["B18"] = f"=SUM({R('O')})"
sm["A19"] = "  balance (£)"; sm["B19"] = f"=SUMPRODUCT({R('O')},{R('C')})"; sm["B19"].number_format = "#,##0.00"
sm["A20"] = "High LTI threshold (FPC)"; sm["B20"] = 4.5; sm["B20"].fill = inp
sm["A21"] = "Reversion window end (text date)"; sm["B21"] = "2028-01-31"; sm["B21"].fill = inp
sm.column_dimensions["A"].width = 40; sm.column_dimensions["B"].width = 18; sm.column_dimensions["C"].width = 12

# ---- Examples
ex = wb.create_sheet("Examples", 2)
ex["A1"] = "Worked examples from the chapter"; ex["A1"].font = title
ex["A3"] = "KBS-000417"; ex["A3"].font = Font(bold=True, color=NAVY)
items = [("Original balance (£)", 185000), ("Original valuation (£)", 245000), ("Current balance (£)", 167784.59),
         ("Gross income (£ a year)", 52000), ("Original LTV (%)", "=100*B4/B5"), ("Current LTV (%)", "=100*B6/B5"),
         ("LTI", "=B4/B7"), ("Illustrative HPI at origination", 100.0), ("Illustrative HPI at cut-off", 106.2),
         ("Indexed valuation (£)", "=ROUND(B5*B12/B11,2)"), ("Indexed current LTV (%)", "=100*B6/B13")]
for i, (lab, v) in enumerate(items, start=4):
    ex.cell(i, 1, lab); c = ex.cell(i, 2, v); c.number_format = "#,##0.00"
    if not str(v).startswith("="): c.fill = inp
ex["A16"] = "Weighted average on three loans"; ex["A16"].font = Font(bold=True, color=NAVY)
for j, h in enumerate(["Loan", "Current balance", "Original LTV %", "Balance x LTV"], start=1):
    x = ex.cell(17, j, h); x.font = hdr; x.fill = fill
for i in range(3):
    r = 18 + i; tr = i + 2
    ex.cell(r, 1, f"=Tape!A{tr}"); ex.cell(r, 2, f"=Tape!C{tr}").number_format = "#,##0.00"
    ex.cell(r, 3, f"=ROUND(Tape!K{tr},2)").number_format = "0.00"
    ex.cell(r, 4, f"=B{r}*C{r}").number_format = "#,##0.00"
ex["A21"] = "Total"; ex["B21"] = "=SUM(B18:B20)"; ex["D21"] = "=SUM(D18:D20)"
ex["B21"].number_format = ex["D21"].number_format = "#,##0.00"
ex["A22"] = "Weighted average LTV (%)"; ex["B22"] = "=D21/B21"; ex["B22"].number_format = "0.00"
ex["A23"] = "Simple average LTV (%)"; ex["B23"] = "=AVERAGE(C18:C20)"; ex["B23"].number_format = "0.00"
ex["A25"] = "Affordability with a stressed rate (illustrative applicant)"; ex["A25"].font = Font(bold=True, color=NAVY)
aff = [("Loan amount (£)", 280000), ("Term (months)", 360), ("Product rate (2-year fixed)", 0.0445),
       ("Kingsbridge SVR", 0.0749), ("Add-on to product rate", 0.03),
       ("Stress rate", "=MAX(B29,B28+B30)"), ("Payment at product rate (£)", "=ROUND(PMT(B28/12,B27,-B26),2)"),
       ("Payment at stress rate (£)", "=ROUND(PMT(B31/12,B27,-B26),2)"), ("Net monthly income (£)", 4420),
       ("Committed expenditure (£)", 350), ("Essential household spending (£)", 1600),
       ("Surplus after stressed payment (£)", "=B34-B35-B36-B33")]
for i, (lab, v) in enumerate(aff, start=26):
    ex.cell(i, 1, lab); c = ex.cell(i, 2, v)
    c.number_format = "0.00%" if i in (28, 29, 30, 31) else ("0" if i == 27 else "#,##0.00")
    if not str(v).startswith("="): c.fill = inp
ex.column_dimensions["A"].width = 38; ex.column_dimensions["B"].width = 16
ex.column_dimensions["C"].width = 15; ex.column_dimensions["D"].width = 18
wb.save(sys.argv[2])
print("saved", sys.argv[2])
