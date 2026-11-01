"""Build ch22/excel/ch22_senior_expenses.xlsx (live formulas).
Run from the book folder: python3 tools/build_ch22_xlsx.py"""
import datetime as dt
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
NAVY = "1F2A44"; M2 = "#,##0.00"
hdr, fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
def head(ws, row, names, width=15):
    for j, h in enumerate(names, 1):
        c = ws.cell(row, j, h); c.font = hdr; c.fill = fill
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        ws.column_dimensions[c.column_letter].width = width
wb = Workbook(); ws = wb.active; ws.title = "Budget"
ws["A1"] = "Chapter 22 - Thames Residential 2027-1: senior expenses"; ws["A1"].font = Font(bold=True, size=13, color=NAVY)
head(ws, 3, ["Item", "Basis", "Annual amount (£)"], 30)
ws["A4"], ws["B4"] = "Pool balance at cut-off (£)", "input"; ws["C4"] = 635671146.31
ws["A5"], ws["B5"] = "Servicing fee rate p.a.", "input"; ws["C5"] = 0.0015
ws["A6"], ws["B6"] = "Issuer profit per IPD (£)", "input"; ws["C6"] = 1000
for c in ("C4", "C5", "C6"): ws[c].fill = inp
ws["C4"].number_format = M2; ws["C5"].number_format = "0.00%"; ws["C6"].number_format = M2
fees = [("Trustee", 25000), ("Paying agent and agent bank", 10000), ("Corporate services", 20000),
        ("Cash management", 50000), ("Other issuer expenses", 120000)]
for i, (n, v) in enumerate(fees, 8):
    ws.cell(i, 1, n); ws.cell(i, 2, "fixed, per year"); c = ws.cell(i, 3, v); c.fill = inp; c.number_format = M2
ws["A13"], ws["B13"], ws["C13"] = "Servicing", "0.15% of pool", "=ROUND(C4*C5,2)"
ws["A14"], ws["C14"] = "Total senior expenses", "=SUM(C8:C13)"
ws["A15"], ws["C15"] = "As % of pool", "=C14/C4"
ws["A16"], ws["C16"] = "Issuer profit (4 IPDs)", "=4*C6"
ws["A17"], ws["C17"] = "Total with issuer profit", "=C14+C16"
for c in ("C13", "C14", "C16", "C17"): ws[c].number_format = M2
ws["C15"].number_format = "0.0000%"
ws["A19"] = "Yellow cells are inputs. Every other cell is a formula."
# monthly servicing fees
perf = pd.read_csv("data/thames_performance_monthly.csv", dtype=str)
mo = wb.create_sheet("Monthly")
head(mo, 1, ["Collection period", "Opening balance (£)", "Servicing fee (£)", "Paid on IPD"], 18)
ipd_of = {"2027-02": 1, "2027-03": 1, "2027-04": 1, "2027-05": 1, "2027-06": 2, "2027-07": 2, "2027-08": 2,
          "2027-09": 3, "2027-10": 3, "2027-11": 3, "2027-12": 4, "2028-01": 4, "2028-02": 4}
for i, p in enumerate(ipd_of, 2):
    mo.cell(i, 1, p).fill = inp
    c = mo.cell(i, 2, float(perf.set_index("collection_period").opening_balance[p])); c.fill = inp; c.number_format = M2
    mo.cell(i, 3, f"=ROUND(B{i}*Budget!$C$5/12,2)").number_format = M2
    mo.cell(i, 4, ipd_of[p]).fill = inp
# per IPD
ip = wb.create_sheet("PerIPD")
head(ip, 1, ["IPD no.", "Period start", "IPD", "Days", "Trustee", "PA and AB", "Corporate services",
             "Cash management", "Other expenses", "Fixed fees", "Servicing", "Issuer profit", "Total"], 13)
dates = [dt.date(2027, 3, 18), dt.date(2027, 6, 15), dt.date(2027, 9, 15), dt.date(2027, 12, 15), dt.date(2028, 3, 15)]
for k in range(4):
    i = k + 2
    ip.cell(i, 1, k + 1)
    c = ip.cell(i, 2, dates[k]); c.fill = inp; c.number_format = "dd-mmm-yyyy"
    c = ip.cell(i, 3, dates[k + 1]); c.fill = inp; c.number_format = "dd-mmm-yyyy"
    ip.cell(i, 4, f"=C{i}-B{i}")
    for j, row in zip(range(5, 10), range(8, 13)):
        ip.cell(i, j, f"=ROUND(Budget!$C${row}*$D{i}/365,2)").number_format = M2
    ip.cell(i, 10, f"=SUM(E{i}:I{i})").number_format = M2
    ip.cell(i, 11, f"=SUMIF(Monthly!$D$2:$D$14,A{i},Monthly!$C$2:$C$14)").number_format = M2
    ip.cell(i, 12, "=Budget!$C$6").number_format = M2
    ip.cell(i, 13, f"=J{i}+K{i}+L{i}").number_format = M2
ip.cell(6, 1, "First year"); ip.cell(6, 4, "=SUM(D2:D5)")
for j in range(5, 14):
    ip.cell(6, j, f"=SUM({ip.cell(2, j).column_letter}2:{ip.cell(5, j).column_letter}5)").number_format = M2
wb.save("ch22/excel/ch22_senior_expenses.xlsx"); print("saved")
