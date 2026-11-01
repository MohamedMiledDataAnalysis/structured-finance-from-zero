"""Build ch23/excel/ch23_order_book_and_funding.xlsx (live formulas).
Run from the book folder: python3 tools/build_ch23_xlsx.py"""
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
NAVY = "1F2A44"
hdr, fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
M0, M2, P4 = "#,##0", "#,##0.00", "0.0000%"
def head(ws, row, names, width=16):
    for j, h in enumerate(names, 1):
        c = ws.cell(row, j, h); c.font = hdr; c.fill = fill
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        ws.column_dimensions[c.column_letter].width = width
wb = Workbook()
ws = wb.active; ws.title = "Inputs"
ws["A1"] = "Chapter 23 - Thames Residential 2027-1: pricing inputs (illustrative)"
ws["A1"].font = Font(bold=True, size=13, color=NAVY)
rows = [("Class A offered to investors (£)", 525350000, M0),
        ("Class A final margin (bp)", 62, "0"),
        ("Allocation step (£)", 1000, M0),
        ("SONIA (illustrative)", 0.0375, "0.00%"),
        ("Swap fixed rate paid by issuer", 0.0330, "0.00%"),
        ("Fixed senior fees per year (£)", 225000, M2),
        ("Servicing fee rate", 0.0015, "0.00%"),
        ("Issuer profit per year (£)", 4000, M2)]
for i, (l, v, f) in enumerate(rows, 3):
    ws.cell(i, 1, l); c = ws.cell(i, 2, v); c.number_format = f; c.fill = inp
ws["A12"] = "Allocation weights by investor type"; ws["A12"].font = Font(bold=True, color=NAVY)
for i, (t, w) in enumerate([("Asset manager", 1), ("Insurer or pension", 1),
                            ("Bank treasury", 0.85), ("Hedge fund", 0.5)], 13):
    ws.cell(i, 1, t); c = ws.cell(i, 2, w); c.fill = inp; c.number_format = "0.00"
ws.column_dimensions["A"].width = 36; ws.column_dimensions["B"].width = 16
ws["A18"] = "Yellow cells are inputs. Every other cell in the workbook is a formula."
# ---- order book (Class A), sorted by time entered then order id
book = pd.read_csv("data/ch23_thames_order_book.csv", dtype={"time_entered": str})
a = book[book.note_class == "A"].sort_values(["time_entered", "order_id"]).reset_index(drop=True)
ob = wb.create_sheet("OrderBook")
head(ob, 1, ["Order", "Investor type", "Time", "Order (£)", "Limit (bp)", "Valid?",
             "Weight", "Weighted order", "Raw share (£)", "Floor (£)", "Remainder",
             "Rank", "Allocation (£)", "Fill"], 14)
n = len(a); last = n + 1
for k, r in a.iterrows():
    i = k + 2
    ob.cell(i, 1, r.order_id).fill = inp; ob.cell(i, 2, r.investor_type).fill = inp
    ob.cell(i, 3, r.time_entered).fill = inp
    c = ob.cell(i, 4, int(r.order_gbp)); c.fill = inp; c.number_format = M0
    c = ob.cell(i, 5, None if pd.isna(r.limit_margin_bp) else int(r.limit_margin_bp)); c.fill = inp
    ob.cell(i, 6, f'=IF(OR(E{i}="",E{i}<=Inputs!$B$4),1,0)')
    ob.cell(i, 7, f"=VLOOKUP(B{i},Inputs!$A$13:$B$16,2,FALSE)")
    ob.cell(i, 8, f"=F{i}*G{i}*D{i}").number_format = M2
    ob.cell(i, 9, f"=Inputs!$B$3*H{i}/SUM($H$2:$H${last})").number_format = M2
    ob.cell(i, 10, f"=ROUNDDOWN(I{i}/Inputs!$B$5,0)*Inputs!$B$5").number_format = M0
    ob.cell(i, 11, f"=IF(F{i}=1,I{i}/Inputs!$B$5-J{i}/Inputs!$B$5,-1)").number_format = "0.000000"
    ob.cell(i, 12, f"=SUMPRODUCT(($K$2:$K${last}>K{i})+($K$2:$K${last}=K{i})*(ROW($K$2:$K${last})<ROW()))+1")
    ob.cell(i, 13, f"=J{i}+IF(L{i}<=$B${last+3},Inputs!$B$5,0)").number_format = M0
    ob.cell(i, 14, f"=IF(D{i}>0,M{i}/D{i},0)").number_format = "0.00%"
ob.cell(last + 2, 1, "Totals"); ob.cell(last + 2, 4, f"=SUM(D2:D{last})").number_format = M0
ob.cell(last + 2, 10, f"=SUM(J2:J{last})").number_format = M0
ob.cell(last + 2, 13, f"=SUM(M2:M{last})").number_format = M0
ob.cell(last + 3, 1, "Steps left after floors")
ob.cell(last + 3, 2, f"=(Inputs!B3-J{last+2})/Inputs!B5")
ob.cell(last + 4, 1, "Check: allocated - offered"); ob.cell(last + 4, 2, f"=M{last+2}-Inputs!B3")
ob.freeze_panes = "A2"
# ---- summary by investor type
sm = wb.create_sheet("Summary")
head(sm, 1, ["Investor type", "Valid orders (£)", "Allocated (£)", "Fill"], 20)
types = ["Asset manager", "Bank treasury", "Hedge fund", "Insurer or pension"]
for i, t in enumerate(types, 2):
    sm.cell(i, 1, t)
    sm.cell(i, 2, f'=SUMPRODUCT((OrderBook!$B$2:$B${last}=A{i})*OrderBook!$F$2:$F${last}*OrderBook!$D$2:$D${last})').number_format = M0
    sm.cell(i, 3, f'=SUMIF(OrderBook!$B$2:$B${last},A{i},OrderBook!$M$2:$M${last})').number_format = M0
    sm.cell(i, 4, f"=C{i}/B{i}").number_format = "0.00%"
sm.cell(6, 1, "Total"); sm.cell(6, 2, "=SUM(B2:B5)").number_format = M0
sm.cell(6, 3, "=SUM(C2:C5)").number_format = M0; sm.cell(6, 4, "=C6/B6").number_format = "0.00%"
sm.cell(8, 1, "Orders received"); sm.cell(8, 2, f"=COUNTA(OrderBook!A2:A{last})")
sm.cell(9, 1, "Orders valid at final margin"); sm.cell(9, 2, f"=SUM(OrderBook!F2:F{last})")
sm.cell(10, 1, "Book received (£)"); sm.cell(10, 2, f"=OrderBook!D{last+2}").number_format = M0
sm.cell(11, 1, "Coverage at final margin"); sm.cell(11, 2, "=B6/Inputs!B3").number_format = '0.00"x"'
# ---- tape extract
tp = wb.create_sheet("Tape")
t = pd.read_csv("data/thames_residential_2027_1_tape.csv")
head(tp, 1, ["loan_id", "product_type", "current_balance", "current_rate"], 16)
for k, r in enumerate(t.itertuples(), 2):
    tp.cell(k, 1, r.loan_id); tp.cell(k, 2, r.product_type)
    tp.cell(k, 3, float(r.current_balance)).number_format = M2; tp.cell(k, 4, float(r.current_rate))
T = len(t) + 1
# ---- funding
fu = wb.create_sheet("Funding")
head(fu, 1, ["Class", "Balance (£)", "Margin", "Coupon", "Interest, 1 year (£)"], 20)
for i, (c, b, m) in enumerate([("A", 553000000, .0062), ("B", 31800000, .011), ("C", 19100000, .015),
                               ("D", 12700000, .022), ("E", 9500000, .035)], 2):
    fu.cell(i, 1, c); x = fu.cell(i, 2, b); x.fill = inp; x.number_format = M2
    x = fu.cell(i, 3, m); x.fill = inp; x.number_format = "0.00%"
    fu.cell(i, 4, f"=Inputs!$B$6+C{i}").number_format = "0.00%"
    fu.cell(i, 5, f"=B{i}*D{i}").number_format = M2
fu.cell(7, 1, "Total A-E"); fu.cell(7, 2, "=SUM(B2:B6)").number_format = M2
fu.cell(7, 5, "=SUM(E2:E6)").number_format = M2
lines = [("Weighted average margin A-E", "=SUMPRODUCT(B2:B6,C2:C6)/B7", P4),
         ("Pool balance (£)", f"=SUM(Tape!C2:C{T})", M2),
         ("Fixed-rate balance (£)", f'=SUMIF(Tape!B2:B{T},"*Fixed",Tape!C2:C{T})', M2),
         ("Pool interest, 1 year (£)", f"=SUMPRODUCT(Tape!C2:C{T},Tape!D2:D{T})/100", M2),
         ("Swap net receipt, 1 year (£)", "=B11*(Inputs!B6-Inputs!B7)", M2),
         ("Senior expenses + profit (£)", "=Inputs!B8+ROUND(B10*Inputs!B9,2)+Inputs!B10", M2),
         ("Note interest A-E (£)", "=E7", M2),
         ("Annual excess spread (£)", "=B12+B13-B14-B15", M2)]
for i, (l, f, nf) in enumerate(lines, 9):
    fu.cell(i, 1, l); fu.cell(i, 2, f).number_format = nf
    if i >= 12: fu.cell(i, 3, f"=B{i}/$B$10").number_format = P4
fu.column_dimensions["A"].width = 32
wb.save("ch23/excel/ch23_order_book_and_funding.xlsx")
print("saved")
