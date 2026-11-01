"""Build ch14/excel/ch14_cashflow_model.xlsx (all calculations live).
Run: python3 tools/build_ch14_xlsx.py data/thames_residential_2027_1_tape.csv ch14/excel/ch14_cashflow_model.xlsx"""
import sys
from datetime import date
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); title = Font(bold=True, size=13, color=NAVY)
M = "#,##0.00"
CPRS = [0, 5, 10, 15, 20, 25]
SHEETS = [(f"CPR{c}", c) for c in CPRS] + [("Base", 11.15)]
CLASSES = [("A", 553000000.00), ("B", 31800000.00), ("C", 19100000.00),
           ("D", 12700000.00), ("E", 9500000.00), ("Z", 9571146.31)]
H = 433

def head(ws, row, col, names, width=None):
    for j, h in enumerate(names):
        c = ws.cell(row, col + j, h); c.font = hdr; c.fill = fill
        c.alignment = Alignment(horizontal="center", wrap_text=True)

tape = pd.read_csv(sys.argv[1])
wb = Workbook()
rd = wb.active; rd.title = "ReadMe"
rd["A1"] = "Chapter 14 - Thames Residential 2027-1 cash-flow model"; rd["A1"].font = title
for i, line in enumerate([
    "Yellow cells are inputs. Every other number is a live formula.",
    "Tape: one row per loan; columns G-J split each loan into a repayment part and an interest-only part.",
    "Sched: scheduled pool balance at 0% CPR and 0% CDR, loan by loan (closed-form annuity balance), months 0-433.",
    "CPR0 ... CPR25: monthly pool projection (columns A-J) and quarterly note payments (columns L-AA).",
    "Order each month: defaults (Chapter 10 vector), scheduled principal (scheduled factor), prepayments (SMM x rest).",
    "Recoveries arrive 'lag' months after default; losses are cured by excess spread through the PDL.",
    "IPD 1 (15 Jun 2027) pays collection months 1-4 (Feb-May 2027); IPD k>1 pays months 3k-1 to 3k+1.",
    "WAL in years from closing (18 Mar 2027), Actual/365, unadjusted IPD dates. Call: all classes redeemed on IPD 20 (15 Mar 2032).",
    "WAL_Table: the prospectus table, read from the six CPR sheets."], start=3):
    rd.cell(i, 1, line)
rd.column_dimensions["A"].width = 120

ip = wb.create_sheet("Inputs")
ip["A1"] = "Inputs (base case of the structuring desk; SONIA not needed for principal)"; ip["A1"].font = title
BASE = pd.read_csv("data/ch14_base_case.csv", index_col=0).value
rows = [("Lifetime default (% of cut-off balance)", float(BASE.lifetime_default_pct) / 100, "0.0000%"),
        ("Loss severity", float(BASE.severity_pct) / 100, "0.00%"),
        ("Recovery lag (months)", int(BASE.lag_months), "0"), ("Closing date", date(2027, 3, 18), "dd mmm yyyy"),
        ("Call IPD number (15 Mar 2032)", 20, "0"), ("Pool at cut-off (£)", "=Sched!B2", M),
        ("Clean-up threshold (10% of cut-off, £)", "=0.1*B8", M)]
for i, (lab, v, f) in enumerate(rows, start=3):
    ip.cell(i, 1, lab); c = ip.cell(i, 2, v); c.number_format = f
    if not str(v).startswith("="): c.fill = inp
head(ip, 10, 1, ["Class", "Amount (£)"])
for i, (c, a) in enumerate(CLASSES, start=11):
    ip.cell(i, 1, c); x = ip.cell(i, 2, a); x.fill = inp; x.number_format = M
ip.cell(17, 1, "Total"); ip.cell(17, 2, "=SUM(B11:B16)").number_format = M
ip.cell(18, 1, "Check: notes - pool (should be 0)"); ip.cell(18, 2, "=B17-B8").number_format = M
head(ip, 20, 1, ["Year", "Share of lifetime defaults"])
for y in range(1, 11):
    ip.cell(20 + y, 1, y); c = ip.cell(20 + y, 2, float(BASE[f"timing_year_{y}"]) / 100); c.fill = inp; c.number_format = "0.00%"
ip.cell(31, 1, "Total (must be 100%)"); ip.cell(31, 2, "=SUM(B21:B30)").number_format = "0.00%"
ip.column_dimensions["A"].width = 38; ip.column_dimensions["B"].width = 18

tp = wb.create_sheet("Tape")
head(tp, 1, 1, ["loan_id", "repayment_type", "original_balance", "current_balance",
                "current_rate (%)", "remaining_term", "IO part", "Repayment part",
                "Monthly rate", "(1+r)^n"])
for i, l in enumerate(tape.itertuples(), start=2):
    tp.cell(i, 1, l.loan_id); tp.cell(i, 2, l.repayment_type)
    tp.cell(i, 3, float(l.original_balance)); tp.cell(i, 4, float(l.current_balance))
    tp.cell(i, 5, float(l.current_rate)); tp.cell(i, 6, int(l.remaining_term_months))
    tp.cell(i, 7, f'=IF(B{i}="Interest-only",D{i},IF(B{i}="Part and part",C{i}/2,0))')
    tp.cell(i, 8, f"=D{i}-G{i}"); tp.cell(i, 9, f"=E{i}/1200"); tp.cell(i, 10, f"=(1+I{i})^F{i}")
    for j in (3, 4, 7, 8): tp.cell(i, j).number_format = M
N = len(tape) + 1
for j, w in zip("ABCDEFGHIJ", (13, 15, 15, 15, 12, 12, 15, 15, 12, 12)):
    tp.column_dimensions[j].width = w
tp.freeze_panes = "A2"

sc = wb.create_sheet("Sched")
head(sc, 1, 1, ["Month", "Scheduled pool balance (£)"])
rng = lambda col: f"Tape!${col}$2:${col}${N}"
for m in range(H + 1):
    r = m + 2
    sc.cell(r, 1, m)
    sc.cell(r, 2, f"=SUMPRODUCT({rng('H')}*({rng('J')}-(1+{rng('I')})^A{r})/({rng('J')}-1)*(A{r}<{rng('F')}))"
                  f"+SUMIF({rng('F')},\">\"&A{r},{rng('G')})").number_format = M
sc.column_dimensions["A"].width = 8; sc.column_dimensions["B"].width = 26
sc.freeze_panes = "A2"

FIRST, LAST = 8, 8 + H          # monthly rows (month 0 .. H)
K = (H - 2) // 3 + 1            # number of IPDs
IFIRST, ILAST = 8, 8 + K - 1
cols = "PQRSTU"; ccols = "VWXYZ" + "AA"
ccols = ["V", "W", "X", "Y", "Z", "AA"]
for name, cpr in SHEETS:
    ws = wb.create_sheet(name)
    ws["A1"] = f"Pool and notes at CPR {cpr}%" + (" (Chapter 10 base case)" if name == "Base" else ""); ws["A1"].font = title
    ws["A2"] = "CPR (annual)"; ws["B2"] = cpr / 100; ws["B2"].fill = inp; ws["B2"].number_format = "0.00%"
    ws["A3"] = "SMM"; ws["B3"] = "=1-(1-B2)^(1/12)"; ws["B3"].number_format = "0.0000%"
    ws["A4"] = "Defaults: lifetime default x cut-off x yearly share / 12 (years 1-10)"
    head(ws, 7, 1, ["Month", "IPD", "Closing balance", "Defaults", "Sched. factor",
                    "Scheduled principal", "Prepayments", "Recoveries", "Losses (cured)", "Principal to notes"])
    for m in range(H + 1):
        r = FIRST + m; s = m + 2
        ws.cell(r, 1, m)
        if m == 0:
            ws.cell(r, 2, ""); ws.cell(r, 3, "=Sched!B2")
            for j in range(4, 11): ws.cell(r, j, 0)
        else:
            ws.cell(r, 2, f"=IF(A{r}<=4,1,INT((A{r}-2)/3)+1)")
            ws.cell(r, 4, f"=IF(A{r}>120,0,MIN(Inputs!$B$3*Inputs!$B$8*INDEX(Inputs!$B$21:$B$30,INT((A{r}-1)/12)+1)/12,C{r-1}))")
            ws.cell(r, 5, f"=IF(Sched!B{s-1}>0,1-Sched!B{s}/Sched!B{s-1},1)")
            ws.cell(r, 6, f"=(C{r-1}-D{r})*E{r}")
            ws.cell(r, 7, f"=$B$3*(C{r-1}-D{r}-F{r})")
            ws.cell(r, 3, f"=C{r-1}-D{r}-F{r}-G{r}")
            lagged = f"IF(A{r}>=Inputs!$B$5,INDEX($D${FIRST}:$D${LAST},A{r}-Inputs!$B$5+1),0)"
            ws.cell(r, 8, f"={lagged}*(1-Inputs!$B$4)")
            ws.cell(r, 9, f"={lagged}*Inputs!$B$4")
            ws.cell(r, 10, f"=F{r}+G{r}+H{r}+I{r}")
        for j in (3, 4, 6, 7, 8, 9, 10): ws.cell(r, j).number_format = M
        ws.cell(r, 5).number_format = "0.000000%"
    head(ws, 7, 12, ["IPD", "Date", "Years from closing", "Principal available"]
         + [f"Class {c} paid (no call)" for c, _ in CLASSES]
         + [f"Class {c} paid (call)" for c, _ in CLASSES])
    for k in range(1, K + 1):
        r = IFIRST + k - 1
        ws.cell(r, 12, k)
        ws.cell(r, 13, f"=DATE(2027,6+3*(L{r}-1),15)").number_format = "dd mmm yyyy"
        ws.cell(r, 14, f"=(M{r}-Inputs!$B$6)/365").number_format = "0.0000"
        ws.cell(r, 15, f"=SUMIF($B${FIRST}:$B${LAST},L{r},$J${FIRST}:$J${LAST})").number_format = M
        for i, c in enumerate(cols):
            prev = "".join(f"-{cols[q]}{r}" for q in range(i))
            ws.cell(r, 16 + i, f"=MAX(0,MIN(Inputs!$B${11+i}-SUM({c}$7:{c}{r-1}),$O{r}{prev}))").number_format = M
            cc = ccols[i]
            ws.cell(r, 22 + i, f"=IF($L{r}<Inputs!$B$7,{c}{r},IF($L{r}=Inputs!$B$7,"
                               f"Inputs!$B${11+i}-SUM({c}$7:{c}{r-1}),0))").number_format = M
    # summary block, rows 2-5, columns N.. : WAL and maturity per class
    ws["L2"] = "WAL no call"; ws["L3"] = "WAL call"; ws["L4"] = "Maturity no call"; ws["L5"] = "Maturity call"
    for i, (c, _) in enumerate(CLASSES):
        pc, cc = cols[i], ccols[i]
        col = 16 + i
        ws.cell(1, col, f"Class {c}").font = Font(bold=True, color=NAVY)
        ws.cell(2, col, f"=SUMPRODUCT({pc}{IFIRST}:{pc}{ILAST},$N${IFIRST}:$N${ILAST})/SUM({pc}{IFIRST}:{pc}{ILAST})").number_format = "0.00"
        ws.cell(3, col, f"=SUMPRODUCT({cc}{IFIRST}:{cc}{ILAST},$N${IFIRST}:$N${ILAST})/SUM({cc}{IFIRST}:{cc}{ILAST})").number_format = "0.00"
        ws.cell(4, col, f'=_xlfn.MAXIFS($M${IFIRST}:$M${ILAST},{pc}{IFIRST}:{pc}{ILAST},">0.005")').number_format = "mmm yyyy"
        ws.cell(5, col, f'=_xlfn.MAXIFS($M${IFIRST}:$M${ILAST},{cc}{IFIRST}:{cc}{ILAST},">0.005")').number_format = "mmm yyyy"
    ws["D2"] = "Clean-up month"; ws["E2"] = f'=_xlfn.MINIFS($A${FIRST}:$A${LAST},$C${FIRST}:$C${LAST},"<"&Inputs!$B$9)'
    ws["D3"] = "Clean-up IPD"; ws["E3"] = "=DATE(2027,6+3*(IF(E2<=4,1,INT((E2-2)/3)+1)-1),15)"; ws["E3"].number_format = "mmm yyyy"
    for j in range(1, 28):
        ws.column_dimensions[ws.cell(1, j).column_letter].width = 15
    ws.freeze_panes = "B8"

wt = wb.create_sheet("WAL_Table", 1)
wt["A1"] = "Thames Residential 2027-1 - WAL (years) and expected maturity"; wt["A1"].font = title
wt["A2"] = "Defaults, severity and lag from Inputs (Chapter 10 base case); CPR from each CPR sheet. Row 11: base case, 11.15% CPR."
head(wt, 4, 1, ["CPR"] + [f"{c} WAL call" for c, _ in CLASSES] + [f"{c} WAL no call" for c, _ in CLASSES])
head(wt, 13, 1, ["CPR"] + [f"{c} maturity call" for c, _ in CLASSES] + [f"{c} maturity no call" for c, _ in CLASSES])
for i, (name, cpr) in enumerate(SHEETS):
    r1, r2 = 5 + i, 14 + i
    wt.cell(r1, 1, f"={name}!B2").number_format = "0.00%"
    wt.cell(r2, 1, f"={name}!B2").number_format = "0.00%"
    for j in range(6):
        col = wb[name].cell(1, 16 + j).column_letter
        wt.cell(r1, 2 + j, f"={name}!{col}3").number_format = "0.00"
        wt.cell(r1, 8 + j, f"={name}!{col}2").number_format = "0.00"
        wt.cell(r2, 2 + j, f"={name}!{col}5").number_format = "mmm yyyy"
        wt.cell(r2, 8 + j, f"={name}!{col}4").number_format = "mmm yyyy"
for j in range(1, 14):
    wt.column_dimensions[wt.cell(4, j).column_letter].width = 12
wb.save(sys.argv[2])
print("saved", sys.argv[2])
