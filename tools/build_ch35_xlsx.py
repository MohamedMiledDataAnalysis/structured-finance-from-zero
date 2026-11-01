"""Build ch35/excel/ch35_sec_sa.xlsx - SEC-SA calculator for Thames.
Run from the book folder:
  python3 tools/build_ch35_xlsx.py ch35/excel/ch35_sec_sa.xlsx
Every calculated cell is a live formula; inputs are yellow."""
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF")
fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")

tape = pd.read_csv("data/thames_residential_2027_1_tape.csv")
wb = Workbook()
ws = wb.active
ws.title = "Inputs"
ws["A1"] = "Chapter 35 - SEC-SA for Thames Residential 2027-1 (UK, from 1 Jan 2027)"
ws["A1"].font = Font(bold=True, size=13, color=NAVY)
inputs = [
    (3, "Funded general reserve (GBP)", 9391500.00, "#,##0.00"),
    (4, "Risk weight of reserve cash (assumption)", 0.20, "0.00%"),
    (5, "Capital ratio", 0.08, "0.00%"),
    (6, "Secured share of property value (loan-splitting)", 0.55, "0.00%"),
    (7, "Risk weight, secured part", 0.20, "0.00%"),
    (8, "Risk weight, residual part (retail)", 0.75, "0.00%"),
    (9, "p, STS (Article 262)", 0.5, "0.00"),
    (10, "p, non-STS (Article 261)", 1.0, "0.00"),
    (11, "Risk-weight floor, senior STS", 0.10, "0.00%"),
    (12, "Risk-weight floor, all other positions", 0.15, "0.00%"),
]
for r, lab, val, fmt in inputs:
    ws.cell(r, 1, lab)
    c = ws.cell(r, 2, val)
    c.number_format = fmt
    c.fill = inp
outputs = [
    (14, "Pool balance (GBP)", "=ROUND(SUM(Pool!B:B),2)", "#,##0.00"),
    (15, "Loan RWA (GBP)", "=SUM(Pool!E:E)", "#,##0.00"),
    (16, "Average loan risk weight", "=B15/B14", "0.00%"),
    (17, "Total underlying exposures incl. reserve (GBP)", "=B14+B3", "#,##0.00"),
    (18, "KSA", "=B5*(B15+B4*B3)/B17", "0.0000%"),
    (19, "W (defaulted share, 3+ months in arrears)",
     '=SUMIF(Pool!D:D,">=3",Pool!B:B)/B14', "0.0000"),
    (20, "KA", "=(1-B19)*B18+B19*0.5", "0.0000%"),
    (21, "Class Z detachment point D", "=SECSA!B7/B17", "0.0000%"),
]
for r, lab, f, fmt in outputs:
    ws.cell(r, 1, lab)
    c = ws.cell(r, 2, f)
    c.number_format = fmt
ws.column_dimensions["A"].width = 48
ws.column_dimensions["B"].width = 18
ws["A23"] = "Yellow cells are inputs. Every other cell is a formula."
ws["A24"] = "Loss order: Z, then the reserve fund, then E, D, C, B, A (CRR Art 256(3))."

pool = wb.create_sheet("Pool")
heads = ["loan_id", "current_balance", "original_valuation",
         "months_in_arrears", "RWA (GBP)"]
for j, h in enumerate(heads, 1):
    c = pool.cell(1, j, h)
    c.font = hdr
    c.fill = fill
    pool.column_dimensions[chr(64 + j)].width = 18
for i, row in enumerate(tape.itertuples(index=False), start=2):
    pool.cell(i, 1, row.loan_id)
    pool.cell(i, 2, float(row.current_balance)).number_format = "#,##0.00"
    pool.cell(i, 3, float(row.original_valuation)).number_format = "#,##0.00"
    pool.cell(i, 4, int(row.months_in_arrears))
    pool.cell(i, 5, f"=Inputs!$B$7*MIN(B{i},Inputs!$B$6*C{i})"
                    f"+Inputs!$B$8*MAX(B{i}-Inputs!$B$6*C{i},0)"
              ).number_format = "#,##0.00"
pool.freeze_panes = "A2"

s = wb.create_sheet("SECSA")
cols = ["Class", "Amount (GBP)", "D", "A", "STS floor", "a (STS)",
        "u", "l", "KSSFA STS", "RW STS", "a (non-STS)",
        "KSSFA non-STS", "RW non-STS", "Capital/GBP1m STS",
        "Capital/GBP1m non-STS"]
for j, h in enumerate(cols, 1):
    c = s.cell(1, j, h)
    c.font = hdr
    c.fill = fill
    c.alignment = Alignment(horizontal="center", wrap_text=True)
    s.column_dimensions[chr(64 + j)].width = 14
classes = [("A", 553000000.00), ("B", 31800000.00), ("C", 19100000.00),
           ("D", 12700000.00), ("E", 9500000.00), ("Z", 9571146.31)]
T, KA = "Inputs!$B$17", "Inputs!$B$20"
for i, (name, amt) in enumerate(classes, start=2):
    s.cell(i, 1, name)
    c = s.cell(i, 2, amt)
    c.fill = inp
    c.number_format = "#,##0.00"
    if name == "Z":
        s.cell(i, 3, f"=B{i}/{T}").number_format = "0.0000%"
        s.cell(i, 4, 0).number_format = "0.0000%"
        s.cell(i, 10, f"=IF(C{i}<={KA},12.5,\"check\")").number_format = "0.00%"
        s.cell(i, 13, f"=IF(C{i}<={KA},12.5,\"check\")").number_format = "0.00%"
        continue
    s.cell(i, 3, f"=({T}-SUM(B$1:B{i-1}))/{T}").number_format = "0.0000%"
    s.cell(i, 4, f"=({T}-SUM(B$2:B{i}))/{T}").number_format = "0.0000%"
    s.cell(i, 5, f'=IF(A{i}="A",Inputs!$B$11,Inputs!$B$12)').number_format = "0.00%"
    s.cell(i, 6, f"=-1/(Inputs!$B$9*{KA})").number_format = "0.0000"
    s.cell(i, 7, f"=C{i}-{KA}").number_format = "0.000000"
    s.cell(i, 8, f"=MAX(D{i}-{KA},0)").number_format = "0.000000"
    s.cell(i, 9, f"=(EXP(F{i}*G{i})-EXP(F{i}*H{i}))/(F{i}*(G{i}-H{i}))"
           ).number_format = "0.000000"
    s.cell(i, 10, f"=IF(C{i}<={KA},12.5,IF(D{i}>={KA},MAX(E{i},12.5*I{i}),"
                  f"MAX(E{i},({KA}-D{i})/(C{i}-D{i})*12.5"
                  f"+(C{i}-{KA})/(C{i}-D{i})*12.5*I{i})))").number_format = "0.00%"
    s.cell(i, 11, f"=-1/(Inputs!$B$10*{KA})").number_format = "0.0000"
    s.cell(i, 12, f"=(EXP(K{i}*G{i})-EXP(K{i}*H{i}))/(K{i}*(G{i}-H{i}))"
           ).number_format = "0.000000"
    s.cell(i, 13, f"=IF(C{i}<={KA},12.5,IF(D{i}>={KA},MAX(Inputs!$B$12,12.5*L{i}),"
                  f"MAX(Inputs!$B$12,({KA}-D{i})/(C{i}-D{i})*12.5"
                  f"+(C{i}-{KA})/(C{i}-D{i})*12.5*L{i})))").number_format = "0.00%"
    s.cell(i, 14, f"=ROUND(J{i}*Inputs!$B$5*1000000,2)").number_format = "#,##0.00"
    s.cell(i, 15, f"=ROUND(M{i}*Inputs!$B$5*1000000,2)").number_format = "#,##0.00"
s.freeze_panes = "B2"
wb.save(sys.argv[1])
print("saved", sys.argv[1])
