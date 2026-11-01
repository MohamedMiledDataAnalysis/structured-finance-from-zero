"""Build ch25/excel/ch25_arrears.xlsx - roll-rate matrix and repossession recoveries, live formulas.
Run from the book folder:  python3 tools/build_ch25_xlsx.py ch25/excel/ch25_arrears.xlsx"""
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter as L
NAVY = "1F2A44"; hdr = Font(bold=True, color="FFFFFF"); hf = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); M = "#,##0.00"
wb = Workbook()
# States
s = wb.active; s.title = "States"
st = pd.read_csv("data/ch25_thames_arrears_states.csv")
for j, h in enumerate(st.columns, 1):
    c = s.cell(1, j, h); c.font = hdr; c.fill = hf
for i, row in enumerate(st.itertuples(index=False), 2):
    for j, v in enumerate(row, 1):
        s.cell(i, j, v if j == 1 else int(v)).fill = inp
s.freeze_panes = "B2"; N = len(st) + 1; LAST = L(len(st.columns))
FROM = f"States!$B$2:${L(len(st.columns)-1)}${N}"; TO = f"States!$C$2:${LAST}${N}"
# Matrix
m = wb.create_sheet("Matrix")
m["A1"] = "Roll-rate matrix: state at month t (rows) to state at month t+1 (columns), Feb 2027 - Jan 2029"
m["A1"].font = Font(bold=True, color=NAVY)
m["A2"] = "Codes: 0 up to date; 1-11 months in arrears; -1 redeemed; -2 property sold after possession"
bk = [("Current", 0, 0), ("1 month", 1, 1), ("2 months", 2, 2), ("3m+", 3, 11), ("Left pool", -2, -1)]
for j, h in enumerate(["Bucket", "Lowest code", "Highest code"], 1):
    c = m.cell(4, j, h); c.font = hdr; c.fill = hf
for i, (n, lo, hi) in enumerate(bk, 5):
    m.cell(i, 1, n); m.cell(i, 2, lo).fill = inp; m.cell(i, 3, hi).fill = inp
m.cell(11, 1, "Counts (loan-months)").font = Font(bold=True, color=NAVY)
m.cell(18, 1, "Roll rates (% of row)").font = Font(bold=True, color=NAVY)
for j in range(5):
    for r0 in (12, 19):
        c = m.cell(r0, 2 + j, f"=A{5+j}"); c.font = hdr; c.fill = hf
    m.cell(12, 1, "From / To").font = Font(bold=True); m.cell(19, 1, "From / To").font = Font(bold=True)
for i in range(4):
    r = 13 + i; m.cell(r, 1, f"=A{5+i}"); m.cell(20 + i, 1, f"=A{5+i}")
    for j in range(5):
        col = L(2 + j)
        m.cell(r, 2 + j, f"=SUMPRODUCT(({FROM}>=$B${5+i})*({FROM}<=$C${5+i})*({TO}>=$B${5+j})*({TO}<=$C${5+j}))").number_format = "#,##0"
        m.cell(20 + i, 2 + j, f"=ROUND({col}{r}/SUM($B{r}:$F{r})*100,2)").number_format = "0.00"
    m.cell(r, 7, f"=SUM(B{r}:F{r})").number_format = "#,##0"
m.cell(12, 7, "Total").font = Font(bold=True)
for j in range(1, 8): m.column_dimensions[L(j)].width = 14
# Recoveries
rv = wb.create_sheet("Recoveries")
rp = pd.read_csv("data/ch25_thames_repossessions.csv")
heads = ["Loan", "Period sold", "Months since cut-off", "Original valuation", "Balance owed", "Arrears owed",
         "House price index", "Gross sale price", "Net proceeds", "Sale costs", "Principal recovered",
         "Arrears interest recovered", "Realised loss", "Surplus to borrower"]
for j, h in enumerate(heads, 1):
    c = rv.cell(1, j, h); c.font = hdr; c.fill = hf; rv.column_dimensions[L(j)].width = 15
rv["P1"] = "Forced-sale price (% of indexed value)"; rv["Q1"] = 0.70
rv["P2"] = "Sale costs (% of sale price)"; rv["Q2"] = 0.05
rv["P3"] = "House prices: growth per year"; rv["Q3"] = 0.02
for a in ("Q1", "Q2", "Q3"): rv[a].fill = inp; rv[a].number_format = "0.00%"
rv.column_dimensions["P"].width = 36
for i, x in enumerate(rp.itertuples(), 2):
    y, mo = int(x.collection_period[:4]), int(x.collection_period[5:])
    rv.cell(i, 1, x.loan_id).fill = inp; rv.cell(i, 2, x.collection_period).fill = inp
    rv.cell(i, 3, (y - 2027) * 12 + mo - 1).fill = inp
    for j, v in ((4, x.original_valuation), (5, x.balance_at_sale), (6, x.arrears_owed)):
        c = rv.cell(i, j, float(v)); c.fill = inp; c.number_format = M
    f = {7: f"=(1+$Q$3)^(C{i}/12)", 8: f"=ROUND(D{i}*G{i}*$Q$1,2)", 9: f"=ROUND(D{i}*G{i}*$Q$1*(1-$Q$2),2)",
         10: f"=H{i}-I{i}", 11: f"=MIN(I{i},E{i})", 12: f"=MAX(MIN(I{i}-E{i},F{i}),0)",
         13: f"=MAX(E{i}-I{i},0)", 14: f"=MAX(I{i}-E{i}-F{i},0)"}
    for j, v in f.items():
        rv.cell(i, j, v).number_format = "0.000000" if j == 7 else M
n = len(rp) + 1; t = n + 1
rv.cell(t, 1, "Total").font = Font(bold=True)
for j in (5, 11, 12, 13, 14):
    rv.cell(t, j, f"=SUM({L(j)}2:{L(j)}{n})").number_format = M
rv.cell(t + 1, 1, "Loss severity (realised loss / balance owed)")
rv.cell(t + 1, 13, f"=ROUND(M{t}/E{t}*100,2)").number_format = "0.00"
wb.save(sys.argv[1])
