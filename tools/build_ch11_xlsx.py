"""Build ch11/excel/ch11_tranching.xlsx (live formulas).
Run: python3 tools/build_ch11_xlsx.py ch11/excel/ch11_tranching.xlsx"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
M, P = "#,##0.00", "0.0000%"
def head(ws, row, labels, width=16):
    for j, h in enumerate(labels, 1):
        c = ws.cell(row, j, h); c.font = hdr; c.fill = fill
        c.alignment = Alignment(horizontal="center", wrap_text=True)
        ws.column_dimensions[c.column_letter].width = width
wb = Workbook(); s = wb.active; s.title = "Structure"
s["A1"] = "Chapter 11 - Thames Residential 2027-1 capital structure"; s["A1"].font = Font(bold=True, size=13, color=NAVY)
s["A2"] = "Pool balance at cut-off (£)"; s["B2"] = 635671146.31
s["A3"] = "Vertical slice, Classes A-E (Class Z: 100%)"; s["B3"] = 0.05
for c, f in (("B2", M), ("B3", "0.00%")): s[c].fill = inp; s[c].number_format = f
head(s, 4, ["Class", "Amount (£)", "% of pool", "Notes below (£)", "Attachment", "Detachment", "Thickness", "Kingsbridge holds (£)"])
s.column_dimensions["A"].width = 28
notes = [("A", 553000000), ("B", 31800000), ("C", 19100000), ("D", 12700000), ("E", 9500000), ("Z", 9571146.31)]
for i, (cl, amt) in enumerate(notes):
    r = 5 + i
    s.cell(r, 1, cl); c = s.cell(r, 2, amt); c.fill = inp; c.number_format = M
    s.cell(r, 3, f"=B{r}/$B$2").number_format = P
    s.cell(r, 4, f"=SUM(B{r+1}:B$10)" if r < 10 else 0).number_format = M
    s.cell(r, 5, f"=D{r}/$B$2").number_format = P
    s.cell(r, 6, f"=(D{r}+B{r})/$B$2").number_format = P
    s.cell(r, 7, f"=F{r}-E{r}").number_format = P
    s.cell(r, 8, f'=IF(A{r}="Z",B{r},ROUND(B{r}*$B$3,2))').number_format = M
s.cell(11, 1, "Total"); s.cell(11, 2, "=SUM(B5:B10)").number_format = M
s.cell(11, 3, "=SUM(C5:C10)").number_format = P
s.cell(11, 8, "=SUM(H5:H10)").number_format = M
s.cell(12, 1, "Check: notes minus pool (should be 0)"); s.cell(12, 2, "=B11-B2").number_format = M
s.cell(13, 1, "Retained as % of pool"); s.cell(13, 2, "=H11/B2").number_format = P
s["A15"] = "Yellow cells are inputs. Every other cell is a formula. Row 10 (Z) has nothing below it."
L = wb.create_sheet("Losses")
L["A1"] = "Loss allocation by subordination alone (no excess spread, no reserve fund)"; L["A1"].font = Font(bold=True, color=NAVY)
order = ["Z", "E", "D", "C", "B", "A"]; rowof = {cl: 5 + i for i, (cl, _) in enumerate(notes)}
head(L, 3, ["Pool loss %", "Pool loss (£)"] + [f"{c} loss (£)" for c in order] + [f"{c} % of class" for c in order], 14)
scen = [0.005, 0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.13, 0.15, 0.20]
for i, sc in enumerate(scen):
    r = 4 + i
    c = L.cell(r, 1, sc); c.fill = inp; c.number_format = "0.0%"
    L.cell(r, 2, f"=ROUND(Structure!$B$2*A{r},2)").number_format = M
    for j, cl in enumerate(order):
        sr = rowof[cl]
        col = L.cell(r, 3 + j, f"=MIN(Structure!$B${sr},MAX(0,$B{r}-Structure!$D${sr}))"); col.number_format = M
        L.cell(r, 9 + j, f"={col.coordinate}/Structure!$B${sr}").number_format = "0.00%"
    L.cell(r, 15, f"=SUM(C{r}:H{r})-B{r}").number_format = M
L.cell(3, 15, "Check (0)").font = hdr; L.cell(3, 15).fill = fill
R = wb.create_sheet("Retention")
R["A1"] = "Who bears the loss: Kingsbridge holds 5% of Classes A-E and all of Class Z"; R["A1"].font = Font(bold=True, color=NAVY)
R["A2"] = "Scenario row on Losses sheet"; R["B2"] = 7; R["B2"].fill = inp
head(R, 4, ["Class", "Class loss (£)", "Kingsbridge (£)", "Investors (£)"], 18)
for j, cl in enumerate(order):
    r = 5 + j
    R.cell(r, 1, cl)
    R.cell(r, 2, f"=INDEX(Losses!{chr(67+j)}:{chr(67+j)},$B$2)").number_format = M
    R.cell(r, 3, f'=IF(A{r}="Z",B{r},ROUND(B{r}*Structure!$B$3,2))').number_format = M
    R.cell(r, 4, f"=B{r}-C{r}").number_format = M
R.cell(11, 1, "Total")
for col in "BCD": R[f"{col}11"] = f"=SUM({col}5:{col}10)"; R[f"{col}11"].number_format = M
wb.save(sys.argv[1])
