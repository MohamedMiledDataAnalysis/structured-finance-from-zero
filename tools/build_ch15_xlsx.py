"""Build ch15/excel/ch15_swap.xlsx (all calculations live; yellow = inputs).
Run: python3 tools/build_ch15_xlsx.py data/thames_residential_2027_1_tape.csv data/thames_sonia_assumption.csv \
         data/ch15_sonia_daily_sample.csv ch15/excel/ch15_swap.xlsx"""
import sys
from datetime import date
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
sys.path.insert(0, "ch14/python")
import cashflow as cf

NAVY = "1F2A44"; hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); title = Font(bold=True, size=13, color=NAVY); M = "#,##0.00"
def head(ws, row, names, col=1):
    for j, h in enumerate(names):
        c = ws.cell(row, col + j, h); c.font = hdr; c.fill = fill; c.alignment = Alignment(horizontal="center", wrap_text=True)
def put(ws, ref, v, fmt=None, yellow=False):
    ws[ref] = v
    if fmt: ws[ref].number_format = fmt
    if yellow: ws[ref].fill = inp

tape_p, q_p, d_p, out = sys.argv[1:5]
t = cf.load_tape(tape_p); N0 = cf.fixed_sched_balance(t)
S = cf.sched_balance(t); POOL = cf.project_pool(S, **cf.load_base("data/ch14_base_case.csv", S[0]))
q = pd.read_csv(q_p); s = pd.read_csv(d_p)
wb = Workbook(); ip = wb.active; ip.title = "Inputs"
ip["A1"] = "Chapter 15 - Thames swap: inputs"; ip["A1"].font = title
rows = [("Swap fixed rate (%)", 3.30, "0.00"), ("SONIA, first period (%, illustrative)", 3.75, "0.00"),
        ("Closing date", date(2027, 3, 18), "dd mmm yyyy"), ("First IPD", date(2027, 6, 15), "dd mmm yyyy"),
        ("Class A amount (£)", 553000000.00, M), ("Class A margin (%)", 0.62, "0.00"),
        ("Classes A-E on SONIA (£)", 626100000.00, M), ("SVR loan balance (£)", float(t[t.product_type == "SVR"].current_balance.sum()), M),
        ("Base case CPR (%), reference only", 11.15, "0.00"), ("Base case lifetime default (%), reference only", 1.46, "0.00"), ("Stressed SONIA (%)", 2.30, "0.00"),
        ("Market swap rate up (%)", 4.30, "0.00"), ("Market swap rate down (%)", 2.30, "0.00")]
for i, (lab, v, f) in enumerate(rows, start=3):
    ip.cell(i, 1, lab); put(ip, f"B{i}", v, f, True)
ip.column_dimensions["A"].width = 40; ip.column_dimensions["B"].width = 18

fp = wb.create_sheet("FirstPeriod")
fp["A1"] = "First swap period (Actual/365)"; fp["A1"].font = title
items = [("Days", "=Inputs!B6-Inputs!B5", "0"), ("Notional (£)", N0[0], M),
         ("Fixed leg, issuer pays (£)", "=ROUND(B4*Inputs!B3/100*B3/365,2)", M),
         ("Floating leg, issuer receives (£)", "=ROUND(B4*Inputs!B4/100*B3/365,2)", M),
         ("Net to issuer (£)", "=B6-B5", M)]
for i, (lab, v, f) in enumerate(items, start=3):
    fp.cell(i, 1, lab); put(fp, f"B{i}", v, f, not str(v).startswith("="))
fp.column_dimensions["A"].width = 36; fp.column_dimensions["B"].width = 18

so = wb.create_sheet("SONIA")
so["A1"] = "Compounded SONIA in arrears, 5-day observation shift (ILLUSTRATIVE daily rates)"; so["A1"].font = title
head(so, 3, ["Observation date", "SONIA (%)", "Days", "Daily factor"])
for i, r in enumerate(s.itertuples(), start=4):
    so.cell(i, 1, r.observation_date).fill = inp
    c = so.cell(i, 2, float(r.sonia_pct)); c.fill = inp; c.number_format = "0.0000"
    so.cell(i, 3, int(r.days)).fill = inp
    so.cell(i, 4, f"=1+B{i}/100*C{i}/365").number_format = "0.0000000000"
last = 3 + len(s)
lab = [("Days in observation period", f"=SUM(C4:C{last})", "0"),
       ("Compounded rate (%)", f"=(PRODUCT(D4:D{last})-1)*365/B{last+2}*100", "0.00000"),
       ("Weighted average (%)", f"=SUMPRODUCT(B4:B{last},C4:C{last})/B{last+2}", "0.00000"),
       ("Class A interest, 14 days (£)", f"=ROUND(Inputs!B7*(ROUND(B{last+3},5)+Inputs!B8)/100*14/365,2)", M)]
for i, (l, f, fm) in enumerate(lab, start=last + 2):
    so.cell(i, 1, l); so.cell(i, 2, f).number_format = fm
for c, w in zip("ABCD", (20, 12, 8, 16)): so.column_dimensions[c].width = w

sw = wb.create_sheet("Swap8")
sw["A1"] = "First eight IPDs: scheduled notional (from the Chapter 14 model), SONIA assumption file"; sw["A1"].font = title
head(sw, 3, ["IPD", "Date", "Days", "Month of notional", "Scheduled notional (£)", "SONIA (%)", "Net to issuer (£)",
             "Actual fixed balance (£)", "Excess notional (£)", "Pool factor B/S, base case (Chapter 14 model)"])
for k in range(1, 9):
    r = 3 + k; m = 0 if k == 1 else 3 * k - 2
    sw.cell(r, 1, k); sw.cell(r, 2, f"=DATE(2027,6+3*(A{r}-1),15)").number_format = "mmm yyyy"
    sw.cell(r, 3, "=B4-Inputs!B5" if k == 1 else f"=B{r}-B{r-1}")
    sw.cell(r, 4, m)
    put(sw, f"E{r}", float(N0[m]), M, True)
    put(sw, f"F{r}", float(q.compounded_sonia_pct[k - 1]), "0.00", True)
    sw.cell(r, 7, f"=ROUND(E{r}*F{r}/100*C{r}/365,2)-ROUND(E{r}*Inputs!$B$3/100*C{r}/365,2)").number_format = M
    put(sw, f"J{r}", float(POOL.balance[m] / S[m]), "0.0000000000", True)
    sw.cell(r, 8, f"=E{r}*J{r}").number_format = M
    sw.cell(r, 9, f"=E{r}-H{r}").number_format = M
sw["A13"] = "Total net to issuer (£)"; sw["G13"] = "=SUM(G4:G11)"; sw["G13"].number_format = M
sw["A14"] = "Cost of excess notional on IPD 8 if SONIA = stressed rate (£)"
sw["G14"] = "=ROUND(I11*(Inputs!B3-Inputs!B13)/100*C11/365,2)"; sw["G14"].number_format = M
for c, w in zip("ABCDEFGHIJ", (6, 11, 7, 9, 18, 9, 16, 18, 16, 16)): sw.column_dimensions[c].width = w

ba = wb.create_sheet("Basis")
ba["A1"] = "Basis risk, annual (illustrative)"; ba["A1"].font = title
for i, (l, f) in enumerate([("Notes on SONIA not matched by the swap (£)", "=Inputs!B9-FirstPeriod!B4"),
                            ("SONIA +0.25%, Bank Rate unchanged: cost (£)", "=ROUND(B3*0.25%,2)"),
                            ("SVR cut by 0.50%: lost income (£)", "=ROUND(Inputs!B10*0.5%,2)")], start=3):
    ba.cell(i, 1, l); ba.cell(i, 2, f).number_format = M
ba.column_dimensions["A"].width = 46; ba.column_dimensions["B"].width = 18

va = wb.create_sheet("Value")
va["A1"] = "Simplified value of the swap to the issuer at closing"; va["A1"].font = title
head(va, 3, ["IPD", "Date", "Days in period", "Days from closing", "Scheduled notional (£)", "Term, rate up", "Term, rate down"])
k = 1; rows_v = []
while True:
    m = 0 if k == 1 else 3 * k - 2
    if N0[m] <= 0: break
    r = 3 + k
    va.cell(r, 1, k); va.cell(r, 2, f"=DATE(2027,6+3*(A{r}-1),15)").number_format = "mmm yyyy"
    va.cell(r, 3, "=B4-Inputs!B5" if k == 1 else f"=B{r}-B{r-1}"); va.cell(r, 4, f"=B{r}-Inputs!$B$5")
    put(va, f"E{r}", float(N0[m]), M, True)
    for col, ref in ((6, "$B$14"), (7, "$B$15")):
        va.cell(r, col, f"=E{r}*(Inputs!{ref}-Inputs!$B$3)/100*C{r}/365/(1+Inputs!{ref}/100)^(D{r}/365)").number_format = M
    k += 1
lr = 3 + k - 1
va.cell(lr + 2, 1, "Value to issuer (£)"); va.cell(lr + 2, 6, f"=ROUND(SUM(F4:F{lr}),2)").number_format = M
va.cell(lr + 2, 7, f"=ROUND(SUM(G4:G{lr}),2)").number_format = M
for c, w in zip("ABCDEFG", (6, 11, 9, 9, 18, 16, 16)): va.column_dimensions[c].width = w
wb.save(out); print("saved", out, "value rows", k - 1)
