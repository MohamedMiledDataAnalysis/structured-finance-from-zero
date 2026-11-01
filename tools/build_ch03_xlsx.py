"""Build ch03/excel/ch03_credit_risk.xlsx (Chapter 3 - Credit risk).
Run from the book folder: python3 tools/build_ch03_xlsx.py ch03/excel/ch03_credit_risk.xlsx"""
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); title = Font(bold=True, size=13, color=NAVY)
tape = pd.read_csv("data/thames_residential_2027_1_tape.csv")
static = pd.read_csv("data/kingsbridge_static_pool_defaults.csv")
book = pd.read_csv("data/kingsbridge_dynamic_book.csv")


def data_sheet(wb, name, df, cols):
    ws = wb.create_sheet(name)
    for j, c in enumerate(cols, 1):
        h = ws.cell(1, j, c); h.font = hdr; h.fill = fill
        ws.column_dimensions[chr(64 + j)].width = 16
    for i, row in enumerate(df[cols].itertuples(index=False), start=2):
        for j, v in enumerate(row, 1):
            ws.cell(i, j, v.item() if hasattr(v, "item") else v)
    ws.freeze_panes = "A2"
    return ws


def block(ws, items, start, col=1):
    for i, (lab, val, fmt) in enumerate(items, start=start):
        ws.cell(i, col, lab); c = ws.cell(i, col + 1, val); c.number_format = fmt
        if not (isinstance(val, str) and val.startswith("=")): c.fill = inp


wb = Workbook(); calc = wb.active; calc.title = "Calc"
data_sheet(wb, "Tape", tape, ["loan_id", "current_balance", "current_rate", "original_valuation",
                               "region", "months_in_arrears"])                 # rows 2..3001
data_sheet(wb, "StaticPool", static, list(static.columns))                     # rows 2..941
data_sheet(wb, "DynamicBook", book, ["month", "cpr_annualised_pct"])           # rows 2..133
N, S, B = len(tape) + 1, len(static) + 1, len(book) + 1
T = lambda c: f"Tape!{c}2:{c}{N}"
SP = lambda c: f"StaticPool!{c}2:{c}{S}"

calc["A1"] = "Chapter 3 - Credit risk on the Thames pool"; calc["A1"].font = title
block(calc, [
    ("Loans in arrears at cut-off", f'=COUNTIF({T("F")},">0")', "0"),                       # B3
    ("Their balance (£)", f'=SUMIF({T("F")},">0",{T("B")})', "#,##0.00"),                   # B4
    ("Pool balance at cut-off (£)", f'=SUM({T("B")})', "#,##0.00"),                         # B5
    ("Share in arrears", "=B4/B5", "0.00%"),                                                 # B6
], 3)
calc["A7"] = "Expected loss"; calc["A7"].font = Font(bold=True, color=NAVY)
block(calc, [
    ("Months since origination used", 96, "0"),                                              # B8
    ("Vintages with that history", f'=COUNTIF({SP("C")},B8)', "0"),                          # B9
    ("PD: weighted cumulative default",
     f'=SUMPRODUCT(({SP("C")}=B8)*{SP("B")}*{SP("D")})/SUMPRODUCT(({SP("C")}=B8)*{SP("B")})/100', "0.0000%"),  # B10
    ("LGD: weighted net loss / default",
     f'=SUMPRODUCT(({SP("C")}=B8)*{SP("B")}*{SP("F")})/SUMPRODUCT(({SP("C")}=B8)*{SP("B")}*{SP("D")})', "0.00%"),  # B11
    ("EAD: pool balance (£)", "=B5", "#,##0.00"),                                            # B12
    ("Expected loss (£)", "=ROUND(B10*B11*B12,2)", "#,##0.00"),                             # B13
    ("Expected loss, % of pool", "=B13/B12", "0.0000%"),                                     # B14
], 8)
calc["A15"] = "Prepayment"; calc["A15"].font = Font(bold=True, color=NAVY)
yr = f"LEFT(DynamicBook!A2:A{B},4)=B16"
block(calc, [
    ("Year of Kingsbridge book data", "2026", "@"),                                          # B16
    ("Average CPR",
     f"=SUMPRODUCT(({yr})*DynamicBook!B2:B{B})/SUMPRODUCT(--({yr}))/100", "0.00%"),         # B17
    ("SMM = 1-(1-CPR)^(1/12)", "=1-(1-B17)^(1/12)", "0.0000%"),                              # B18
    ("One month's prepayment (£)", "=ROUND(B5*B18,2)", "#,##0.00"),                         # B19
    ("SMM to convert", 0.01, "0.00%"),                                                       # B20
    ("CPR = 1-(1-SMM)^12", "=1-(1-B20)^12", "0.00%"),                                        # B21
], 16)
calc["A22"] = "Concentration"; calc["A22"].font = Font(bold=True, color=NAVY)
block(calc, [
    ("Largest region share", "=MAX(E26:E37)/B5", "0.00%"),                                   # B23
    ("Largest region", "=INDEX(D26:D37,MATCH(MAX(E26:E37),E26:E37,0))", "@"),                # B24
], 23)
calc["D25"] = "Region"; calc["E25"] = "Balance (£)"
for c in ("D25", "E25"): calc[c].font = hdr; calc[c].fill = fill
for i, rgn in enumerate(sorted(tape.region.unique()), start=26):
    calc.cell(i, 4, rgn); calc.cell(i, 5, f'=SUMIF({T("E")},D{i},{T("B")})').number_format = "#,##0.00"
block(calc, [
    ("Largest loan (£)", f'=MAX({T("B")})', "#,##0.00"),                                    # B39
    ("Largest loan, % of pool", "=B39/B5", "0.00%"),                                         # B40
    ("Ten largest loans (£)", f'=SUMPRODUCT(LARGE({T("B")},{{1,2,3,4,5,6,7,8,9,10}}))', "#,##0.00"),  # B41
    ("Ten largest, % of pool", "=B41/B5", "0.00%"),                                          # B42
], 39)
calc.column_dimensions["A"].width = 36; calc.column_dimensions["B"].width = 18
calc.column_dimensions["D"].width = 26; calc.column_dimensions["E"].width = 18

# ---- Loss example
le = wb.create_sheet("LossExample", 1)
le["A1"] = "Loss if a loan defaults (illustrative assumptions in yellow)"; le["A1"].font = title
block(le, [("House price fall", 0.10, "0.00%"), ("Forced-sale discount", 0.15, "0.00%"),
           ("Enforcement and sale costs (£)", 6000, "#,##0.00"), ("Months of unpaid interest", 21, "0"),
           ("Recovery lag (years)", 1.5, "0.0")], 3)                                         # B3..B7
le["B9"] = "KBS-001857"; le["C9"] = "KBS-000417"
for c in ("A9", "B9", "C9"): le[c].font = hdr; le[c].fill = fill
le["A9"] = "Loan"; le["B9"].fill = le["C9"].fill = fill
rows = [("Balance (£)", "INDEX(Tape!$B$2:$B${N},MATCH({c}$9,Tape!$A$2:$A${N},0))", "#,##0.00"),       # 10
        ("Rate", "INDEX(Tape!$C$2:$C${N},MATCH({c}$9,Tape!$A$2:$A${N},0))/100", "0.00%"),            # 11
        ("Valuation (£)", "INDEX(Tape!$D$2:$D${N},MATCH({c}$9,Tape!$A$2:$A${N},0))", "#,##0.00"),    # 12
        ("LTV", "{c}10/{c}12", "0.00%"),                                                               # 13
        ("Unpaid interest (£)", "ROUND({c}10*{c}11*$B$6/12,2)", "#,##0.00"),                           # 14
        ("Claim (£)", "{c}10+{c}14+$B$5", "#,##0.00"),                                                 # 15
        ("Sale proceeds (£)", "ROUND({c}12*(1-$B$3)*(1-$B$4),2)", "#,##0.00"),                         # 16
        ("Loss (£)", "MAX({c}15-{c}16,0)", "#,##0.00"),                                                # 17
        ("Loss severity (loss / balance)", "{c}17/{c}10", "0.00%"),                                    # 18
        ("Surplus to borrower (£)", "MAX({c}16-{c}15,0)", "#,##0.00"),                                 # 19
        ("PV of sale proceeds (£)", "{c}16/(1+{c}11)^$B$7", "#,##0.00")]                               # 20
for i, (lab, f, fmt) in enumerate(rows, start=10):
    le.cell(i, 1, lab)
    for c, col in (("B", 2), ("C", 3)):
        le.cell(i, col, "=" + f.format(c=c, N=N)).number_format = fmt
le.column_dimensions["A"].width = 34; le.column_dimensions["B"].width = 16; le.column_dimensions["C"].width = 16
wb.save(sys.argv[1])
