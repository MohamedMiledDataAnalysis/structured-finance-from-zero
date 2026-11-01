"""Build ch24/excel/ch24_funds_flow.xlsx (live formulas).
Run from the book folder: python3 tools/build_ch24_xlsx.py"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
NAVY = "1F2A44"; M2 = "#,##0.00"
hdr, fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
def head(ws, row, names, width=16):
    for j, h in enumerate(names, 1):
        c = ws.cell(row, j, h); c.font = hdr; c.fill = fill
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        ws.column_dimensions[c.column_letter].width = width
wb = Workbook(); ws = wb.active; ws.title = "Notes"
ws["A1"] = "Chapter 24 - Thames Residential 2027-1: closing funds flow, 18 March 2027 (illustrative costs)"
ws["A1"].font = Font(bold=True, size=13, color=NAVY)
head(ws, 3, ["Class", "Principal (£)", "Retained share", "Retained (£)", "Placed (£)", "Commission rate", "Commission (£)"])
for i, (c, a, k, cr) in enumerate([("A", 553000000, .05, .0015), ("B", 31800000, .05, .0035),
        ("C", 19100000, .05, .0035), ("D", 12700000, .05, .0035), ("E", 9500000, .05, .0035),
        ("Z", 9571146.31, 1, 0)], 4):
    ws.cell(i, 1, c)
    for j, v, f in ((2, a, M2), (3, k, "0%"), (6, cr, "0.00%")):
        x = ws.cell(i, j, v); x.fill = inp; x.number_format = f
    ws.cell(i, 4, f"=ROUND(B{i}*C{i},2)").number_format = M2
    ws.cell(i, 5, f"=B{i}-D{i}").number_format = M2
    ws.cell(i, 7, f"=ROUND(E{i}*F{i},2)").number_format = M2
ws.cell(10, 1, "Total")
for j in (2, 4, 5, 7):
    L = ws.cell(4, j).column_letter
    ws.cell(10, j, f"=SUM({L}4:{L}9)").number_format = M2
co = wb.create_sheet("Costs")
head(co, 1, ["Payee", "Amount (£)"], 34)
costs = [("Rating agency 1", 340000), ("Rating agency 2", 310000), ("Carver Whitlock LLP", 900000),
         ("Pemberton Hale LLP", 132000), ("Harper & Lane LLP (AUP)", 157532.5),
         ("STS Verification Partners", 72000), ("Albion Trustee Services", 18000),
         ("Albion Bank plc (agency)", 6000), ("Meridian Corporate Services", 12000), ("FCA and LSE fees", 21385)]
for i, (n, v) in enumerate(costs, 2):
    co.cell(i, 1, n); x = co.cell(i, 2, v); x.fill = inp; x.number_format = M2
co.cell(12, 1, "Total third-party costs"); co.cell(12, 2, "=SUM(B2:B11)").number_format = M2
co.cell(13, 1, "JLM commission"); co.cell(13, 2, "=Notes!G10").number_format = M2
co.cell(14, 1, "Total upfront costs"); co.cell(14, 2, "=B12+B13").number_format = M2
co.cell(15, 1, "As % of pool"); co.cell(15, 2, "=B14/Flow!B3").number_format = "0.0000%"
fl = wb.create_sheet("Flow")
head(fl, 1, ["Line", "Amount (£)"], 40)
rows = [
 ("Initial consideration (pool at cut-off)", 635671146.31, True),
 ("Subordinated loan (= reserve required)", 9391500, True),
 ("SOURCES AND USES", None, False),
 ("Placed notes (95% of A-E)", "=Notes!E10-Notes!E9", False),
 ("Retained notes (5% of A-E, all of Z)", "=Notes!D10", False),
 ("Subordinated loan", "=B4", False),
 ("Total sources", "=B6+B7+B8", False),
 ("Initial consideration to Kingsbridge", "=B3", False),
 ("General reserve fund", "=B4", False),
 ("Total uses", "=B10+B11", False),
 ("Sources - uses", "=B9-B12", False),
 ("HOW THE CONSIDERATION IS SETTLED", None, False),
 ("Initial consideration", "=B3", False),
 ("less retained notes delivered", "=-B7", False),
 ("less JLM commission (deducted)", "=-Costs!B13", False),
 ("less third-party costs paid", "=-Costs!B12", False),
 ("less subordinated loan (netted)", "=-B4", False),
 ("Net cash to Kingsbridge", "=SUM(B15:B19)", False),
 ("TRANSACTION ACCOUNT ON 18 MARCH 2027", None, False),
 ("JLMs pay in, net of commission", "=B6-Costs!B13", False),
 ("Paid to third parties", "=-Costs!B12", False),
 ("Paid to Kingsbridge", "=-B20", False),
 ("Balance after settlement", "=SUM(B22:B24)", False),
 ("Check: balance - reserve required", "=B25-B4", False)]
for i, (l, v, is_inp) in enumerate(rows, 3):
    fl.cell(i, 1, l)
    if v is None: fl.cell(i, 1).font = Font(bold=True, color=NAVY); continue
    x = fl.cell(i, 2, v); x.number_format = M2
    if is_inp: x.fill = inp
fl["A28"] = "Yellow cells are inputs. Every other cell is a formula. Both checks must show 0.00."
wb.move_sheet("Flow", offset=-2)
wb.save("ch24/excel/ch24_funds_flow.xlsx"); print("saved")
