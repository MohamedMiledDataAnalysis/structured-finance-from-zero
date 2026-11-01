"""Build ch16/excel/ch16_call_economics.xlsx (live formulas; yellow = inputs).
Principal paid to each class on each IPD (no call) is copied from the Chapter 14 model, base case.
Run: python3 tools/build_ch16_xlsx.py data/thames_residential_2027_1_tape.csv data/ch14_base_case.csv ch16/excel/ch16_call_economics.xlsx"""
import sys
from datetime import date
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
sys.path.insert(0, "ch14/python")
import cashflow as cf
NAVY = "1F2A44"; hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); title = Font(bold=True, size=13, color=NAVY); M = "#,##0.00"
def head(ws, row, names, col=1):
    for j, h in enumerate(names):
        c = ws.cell(row, col + j, h); c.font = hdr; c.fill = fill; c.alignment = Alignment(horizontal="center", wrap_text=True)

t = cf.load_tape(sys.argv[1]); S = cf.sched_balance(t)
nc = cf.project_notes(cf.project_pool(S, **cf.load_base(sys.argv[2], S[0])))
wb = Workbook(); ip = wb.active; ip.title = "Inputs"
ip["A1"] = "Chapter 16 - call economics: inputs"; ip["A1"].font = title
ip["A3"] = "SONIA, flat (%, illustrative)"; ip["B3"] = 3.75
ip["A4"] = "Closing date"; ip["B4"] = date(2027, 3, 18); ip["B4"].number_format = "dd mmm yyyy"
ip["A5"] = "First optional redemption IPD"; ip["B5"] = 20
ip["A6"] = "Price 1 (% of par)"; ip["B6"] = 100.00
ip["A7"] = "Price 2 (% of par)"; ip["B7"] = 99.75
for r in range(3, 8): ip.cell(r, 2).fill = inp
head(ip, 9, ["Class", "Amount (£)", "Margin (%)", "Step-up margin (%)", "Increase (%)"])
for i, (c, a) in enumerate(cf.CLASSES):
    r = 10 + i
    ip.cell(r, 1, c); x = ip.cell(r, 2, a); x.fill = inp; x.number_format = M
    if c != "Z":
        m = {"A": 0.62, "B": 1.10, "C": 1.50, "D": 2.20, "E": 3.50}[c]
        ip.cell(r, 3, m).fill = inp; ip.cell(r, 4, f"=2*C{r}"); ip.cell(r, 5, f"=D{r}-C{r}")
    else:
        ip.cell(r, 3, 0); ip.cell(r, 4, 0); ip.cell(r, 5, 0)
ip.column_dimensions["A"].width = 32
for c in "BCDE": ip.column_dimensions[c].width = 16

no = wb.create_sheet("Notes")
no["A1"] = "Principal paid per IPD, no call (from the Chapter 14 model, base case), and opening balances"; no["A1"].font = title
cols = "ABCDEZ"
head(no, 3, ["IPD", "Date", "Days"] + [f"{c} paid" for c in cols] + [f"{c} opening" for c in cols] + ["Extra interest if not called (£)"])
K = len(nc)
for i in range(K):
    r = 4 + i
    no.cell(r, 1, int(nc.ipd[i])); no.cell(r, 2, f"=DATE(2027,6+3*(A{r}-1),15)").number_format = "dd mmm yyyy"
    no.cell(r, 3, "=B4-Inputs!B4" if i == 0 else f"=B{r}-B{r-1}")
    for j, c in enumerate(cols):
        x = no.cell(r, 4 + j, float(nc[c][i])); x.fill = inp; x.number_format = M
        pc = no.cell(r, 4 + j).column_letter
        no.cell(r, 10 + j, f"=Inputs!$B${10+j}-SUM({pc}$3:{pc}{r})+{pc}{r}").number_format = M
    terms = "+".join(f"{no.cell(r, 10 + j).column_letter}{r}*Inputs!$E${10+j}" for j in range(5))
    no.cell(r, 16, f"=IF(A{r}>Inputs!$B$5,({terms})/100*C{r}/365,0)").number_format = M
LR = 3 + K
no.cell(LR + 2, 1, "Extra interest if never called (£)"); no.cell(LR + 2, 16, f"=SUM(P4:P{LR})").number_format = M
for j in range(1, 17): no.column_dimensions[no.cell(3, j).column_letter].width = 15

su = wb.create_sheet("StepUp")
su["A1"] = "On the first optional redemption date (IPD 20, 15 Mar 2032)"; su["A1"].font = title
head(su, 3, ["Class", "Outstanding before payment (£)", "Principal paid (£)", "Outstanding after (£)", "Extra a year if not called (£)"])
rr = 3 + 20
for j, c in enumerate(cols):
    r = 4 + j; L = no.cell(3, 10 + j).column_letter; P = no.cell(3, 4 + j).column_letter
    su.cell(r, 1, c); su.cell(r, 2, f"=Notes!{L}{rr}").number_format = M; su.cell(r, 3, f"=Notes!{P}{rr}").number_format = M
    su.cell(r, 4, f"=B{r}-C{r}").number_format = M; su.cell(r, 5, f"=D{r}*Inputs!E{10+j}/100").number_format = M
su["A10"] = "Total"; su["B10"] = "=SUM(B4:B9)"; su["D10"] = "=SUM(D4:D9)"; su["E10"] = "=SUM(E4:E9)"
for c in "BDE": su[f"{c}10"].number_format = M
su["A12"] = "Clean-up call threshold (10% of cut-off, £)"; su["B12"] = f"=0.1*{S[0]}"; su["B12"].number_format = M
for c, w in zip("ABCDE", (10, 22, 18, 22, 22)): su.column_dimensions[c].width = w

ya = wb.create_sheet("ClassA_Yield")
ya["A1"] = "Class A investor cash flows and yield (XIRR: annual, Actual/365)"; ya["A1"].font = title
head(ya, 3, ["Date", "Opening balance", "Margin no call (%)", "Flow no call, price 1", "Flow call, price 1",
             "Flow no call, price 2", "Flow call, price 2"])
ya.cell(4, 1, "=Inputs!B4").number_format = "dd mmm yyyy"
for col, pr in ((4, "B6"), (5, "B6"), (6, "B7"), (7, "B7")):
    ya.cell(4, col, f"=-Inputs!$B$10*Inputs!${pr[0]}${pr[1:]}/100").number_format = M
NA = int((nc.A > 0.005).sum())
for i in range(NA):
    r = 5 + i; n = 4 + i
    ya.cell(r, 1, f"=Notes!B{n}").number_format = "dd mmm yyyy"
    ya.cell(r, 2, f"=Notes!J{n}").number_format = M
    ya.cell(r, 3, f"=IF(Notes!A{n}<Inputs!$B$5,Inputs!$C$10,Inputs!$D$10)")
    nocall = f"B{r}*(Inputs!$B$3+C{r})/100*Notes!C{n}/365+Notes!D{n}"
    call = f"IF(Notes!A{n}<Inputs!$B$5,B{r}*(Inputs!$B$3+Inputs!$C$10)/100*Notes!C{n}/365+Notes!D{n},IF(Notes!A{n}=Inputs!$B$5,B{r}*(1+(Inputs!$B$3+Inputs!$C$10)/100*Notes!C{n}/365),0))"
    for col, f in ((4, nocall), (5, call), (6, nocall), (7, call)):
        ya.cell(r, col, "=" + f).number_format = M
L2 = 4 + NA
ya.cell(L2 + 2, 1, "Yield (%)")
for col in range(4, 8):
    cl = ya.cell(3, col).column_letter
    ya.cell(L2 + 2, col, f"=XIRR({cl}4:{cl}{L2},$A$4:$A${L2})*100").number_format = "0.000"
for j, w in zip("ABCDEFG", (13, 18, 12, 18, 18, 18, 18)): ya.column_dimensions[j].width = w
wb.save(sys.argv[3]); print("saved", sys.argv[3], "IPDs", K, "Class A rows", NA, "yield row", L2 + 2)
