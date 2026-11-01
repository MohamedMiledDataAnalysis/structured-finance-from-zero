"""Build ch08/excel/ch08_validation_aup.xlsx: every check of Chapter 8 as live formulas on the raw tape,
control totals, the ledger reconciliation, and the AUP sample on the clean pool.
Run from the book folder:
  python3 tools/build_ch08_xlsx.py data/ch08_thames_tape_raw.csv data/thames_residential_2027_1_tape.csv ch08/excel/ch08_validation_aup.xlsx"""
import sys, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter as L
NAVY = "1F2A44"; hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); title = Font(bold=True, size=13, color=NAVY)
raw = list(csv.DictReader(open(sys.argv[1]))); clean = list(csv.DictReader(open(sys.argv[2])))
FIELDS = list(raw[0].keys()); last = len(raw) + 1
NUMERIC = {"payments_made", "original_balance", "current_balance", "monthly_payment", "original_term_months",
           "remaining_term_months", "current_rate", "tracker_margin", "original_valuation", "borrower_count",
           "gross_income", "months_in_arrears"}
def val(f, v):
    if v == "": return None
    if f in NUMERIC:
        try: return float(v) if "." in v else int(v)
        except ValueError: return v
    return v
def head(ws, r, names, c0=1):
    for j, h in enumerate(names, c0):
        c = ws.cell(r, j, h); c.font = hdr; c.fill = fill
wb = Workbook(); nt = wb.active; nt.title = "Notes"
nt["A1"] = "Chapter 8 - data validation and agreed-upon procedures"; nt["A1"].font = title
for i, s in enumerate(["Raw: the tape as first extracted (yellow, columns A-X). Columns Y-AV: helper values and one column per check (1 = exception).",
    "Summary: control totals against the ledger and the number of exceptions per check.",
    "Ledger: the 3,000 loan IDs on Kingsbridge's ledger; column B flags any that is missing from the raw tape.",
    "Pool and AUP: the clean final pool and the auditors' systematic sample.",
    "Bank Rate 3.75% and SVR 7.49% are inputs on the Summary sheet."], start=3):
    nt.cell(i, 1, s)
nt.column_dimensions["A"].width = 120
# ---- Lists (allowed values)
ls = wb.create_sheet("Lists")
LISTS = {"J": ["Repayment", "Interest-only", "Part and part"], "K": ["2Y Fixed", "5Y Fixed", "Tracker", "SVR"],
         "P": ["London", "South East", "East of England", "South West", "West Midlands", "East Midlands",
               "Yorkshire and the Humber", "North West", "North East", "Wales", "Scotland", "Northern Ireland"],
         "Q": ["Detached", "Semi-detached", "Terraced", "Flat", "Bungalow"], "R": ["Owner-occupied"],
         "S": ["Y", "N"], "U": ["Employed", "Self-employed", "Retired"]}
LR = {}
for k, (col, vals) in enumerate(LISTS.items(), 1):
    ls.cell(1, k, "allowed: tape column " + col).font = hdr; ls.cell(1, k).fill = fill
    for i, v in enumerate(vals, 2): ls.cell(i, k, v).fill = inp
    LR[col] = f"Lists!${L(k)}$2:${L(k)}${1 + len(vals)}"
    ls.column_dimensions[L(k)].width = 24
# ---- Raw with checks
rw = wb.create_sheet("Raw")
HELP = ["orig_date", "first_pay", "fixed_months", "monthly_rate", "amort_principal", "pmt_amort", "pmt_recalc",
        "bal_recalc"]
CHECKS = ["K1", "K2", "V1", "V2", "V3", "C1", "C2", "C3", "C4", "C5", "C6", "R1", "R2", "R3", "R4", "P1", "P2"]
head(rw, 1, FIELDS + HELP + CHECKS)
HC = {h: L(25 + j) for j, h in enumerate(HELP)}
CC = {c: L(25 + len(HELP) + j) for j, c in enumerate(CHECKS)}
A = f"$A$2:$A${last}"
for i, r in enumerate(raw, start=2):
    for j, f in enumerate(FIELDS, 1):
        c = rw.cell(i, j, val(f, r[f])); c.fill = inp
    o, fp, fm, m, am, pa, pr, br = (f"{HC[h]}{i}" for h in HELP)
    F = {
     o: f'=IFERROR(DATEVALUE(B{i}),"")', fp: f'=IFERROR(DATEVALUE(C{i}),"")',
     fm: f'=IF(K{i}="2Y Fixed",24,IF(K{i}="5Y Fixed",60,0))',
     m: f'=IF(ISNUMBER(L{i}),L{i}/1200,"")',
     am: f'=IF(J{i}="Part and part",ROUND(E{i}/2,2),E{i})',
     pa: f'=IF(J{i}="Interest-only",ROUND(E{i}*{m},2),ROUND(PMT({m},H{i},-{am}),2))',
     pr: f'=IF(J{i}="Part and part",{pa}+ROUND({am}*{m},2),{pa})',
     br: f'=IF(J{i}="Interest-only",E{i},-FV({m},D{i},-{pa},{am})+IF(J{i}="Part and part",{am},0))',
     f"{CC['K1']}{i}": f"=COUNTBLANK(A{i}:L{i})+COUNTBLANK(O{i}:X{i})",
     f"{CC['K2']}{i}": f"=IF(COUNTIF({A},A{i})>1,1,0)",
     f"{CC['V1']}{i}": "=" + "+".join(f'IF(AND({c}{i}<>"",COUNTIF({LR[c]},{c}{i})=0),1,0)' for c in LISTS),
     f"{CC['V2']}{i}": "=" + "+".join(f'IF(AND({c}{i}<>"",ISERROR(DATEVALUE({c}{i}))),1,0)' for c in "BCMX"),
     f"{CC['V3']}{i}": "=" + "+".join(f'IF(AND({c}{i}<>"",NOT(ISNUMBER({c}{i}))),1,0)' for c in "DEFGHILNOTVW"),
     f"{CC['C1']}{i}": f"=IF(I{i}<>H{i}-D{i},1,0)",
     f"{CC['C2']}{i}": f'=IF(AND(ISNUMBER({o}),ISNUMBER({fp})),IF({fp}<>EDATE({o},1),1,0),0)',
     f"{CC['C3']}{i}": (f'=IF(AND(ISNUMBER({o}),{fm}>0),IF(IFERROR(DATEVALUE(M{i}),0)<>EDATE({o},{fm}),1,0),'
                        f'IF(AND(COUNTIF({LR["K"]},K{i})>0,{fm}=0,M{i}<>""),1,0))'),
     f"{CC['C4']}{i}": (f'=IF(K{i}="Tracker",IF(N{i}="",1,IF(ABS(L{i}-Summary!$G$3-N{i})>0.005,1,0)),'
                        f'IF(AND(COUNTIF({LR["K"]},K{i})>0,N{i}<>""),1,0))'),
     f"{CC['C5']}{i}": f'=IF(K{i}="SVR",IF(ABS(L{i}-Summary!$G$4)>0.005,1,0),0)',
     f"{CC['C6']}{i}": (f'=IF(ISNUMBER({fp}),IF((YEAR(Summary!$G$5)-YEAR({fp}))*12+MONTH(Summary!$G$5)'
                        f'-MONTH({fp})+IF(DAY({fp})<=DAY(Summary!$G$5),1,0)<>D{i},1,0),0)'),
     f"{CC['R1']}{i}": f'=IF(AND(ISNUMBER(E{i}),ISNUMBER(O{i})),IF(OR(100*E{i}/O{i}<10,100*E{i}/O{i}>100),1,0),0)',
     f"{CC['R2']}{i}": f'=IF(AND(ISNUMBER(E{i}),ISNUMBER(V{i})),IF(OR(E{i}/V{i}<1,E{i}/V{i}>6),1,0),0)',
     f"{CC['R3']}{i}": f'=IF(ISNUMBER(L{i}),IF(OR(L{i}<1,L{i}>10),1,0),0)',
     f"{CC['R4']}{i}": f"=IF(W{i}>1,1,0)",
     f"{CC['P1']}{i}": f'=IF(COUNTIF({LR["J"]},J{i})>0,IF(ABS({pr}-G{i})>0.005,1,0),0)',
     f"{CC['P2']}{i}": f'=IF(COUNTIF({LR["J"]},J{i})>0,IF(ABS({br}-F{i})>1,1,0),0)'}
    for ref, fml in F.items(): rw[ref] = fml
rw.freeze_panes = "B2"
# ---- Ledger
lg = wb.create_sheet("Ledger"); head(lg, 1, ["ledger loan_id", "missing from raw tape"])
for i in range(2, 3002):
    lg.cell(i, 1, f'="KBS-"&TEXT(ROW()-1,"000000")')
    lg.cell(i, 2, f'=IF(COUNTIF(Raw!{A},A{i})=0,1,0)')
lg.column_dimensions["A"].width = 16; lg.column_dimensions["B"].width = 22
# ---- Summary
sm = wb.create_sheet("Summary", 1)
sm["A1"] = "Validation summary - raw tape"; sm["A1"].font = title
head(sm, 3, ["Control total", "Ledger", "Tape", "Difference"])
sm["A4"] = "Loans"; sm["B4"] = 3000; sm["C4"] = f"=COUNTA(Raw!{A})"; sm["D4"] = "=C4-B4"
sm["A5"] = "Balance (£)"; sm["B5"] = 635671146.31; sm["C5"] = f"=SUM(Raw!F2:F{last})"; sm["D5"] = "=C5-B5"
sm["B4"].fill = sm["B5"].fill = inp
for c in ("B5", "C5", "D5"): sm[c].number_format = "#,##0.00"
sm["A6"] = "Distinct loan IDs"; sm["C6"] = f"=SUMPRODUCT(1/COUNTIF(Raw!{A},Raw!{A}))"
head(sm, 8, ["Check", "Exceptions"])
row = 9
for c in ["K1", "K2", "K3"] + CHECKS[2:]:
    sm.cell(row, 1, c)
    if c == "K2":
        sm.cell(row, 2, f"=SUMPRODUCT(Raw!{CC['K2']}2:{CC['K2']}{last}/COUNTIF(Raw!{A},Raw!{A}))")
    elif c == "K3":
        sm.cell(row, 2, "=SUM(Ledger!B2:B3001)")
    else:
        sm.cell(row, 2, f"=SUM(Raw!{CC[c]}2:{CC[c]}{last})")
    row += 1
sm["A27"] = "Total exceptions"; sm["B27"] = "=SUM(B9:B26)"
sm["F2"] = "Inputs"; sm["F2"].font = Font(bold=True, color=NAVY)
import datetime
for r_, (lab, v) in zip((3, 4, 5), [("Bank Rate (%)", 3.75), ("Kingsbridge SVR (%)", 7.49),
                                     ("Cut-off date", datetime.date(2027, 1, 31))]):
    sm.cell(r_, 6, lab); c = sm.cell(r_, 7, v); c.fill = inp
sm["G5"].number_format = "yyyy-mm-dd"
for c, w in zip("ABCDEFG", (22, 16, 16, 14, 4, 22, 12)): sm.column_dimensions[c].width = w
# ---- Pool (clean final pool) and AUP
pl = wb.create_sheet("Pool")
PF = ["loan_id", "current_balance", "product_type", "original_balance", "original_valuation", "current_rate"]
head(pl, 1, PF)
for i, r in enumerate(sorted(clean, key=lambda x: x["loan_id"]), start=2):
    for j, f in enumerate(PF, 1): pl.cell(i, j, val(f, r[f])).fill = inp
au = wb.create_sheet("AUP", 2)
au["A1"] = "Agreed-upon procedures - sample size and systematic selection"; au["A1"].font = title
items = [("Confidence level", 0.99), ("Tolerable error rate", 0.01), ("Pool size N", "=COUNTA(Pool!A2:A3001)"),
         ("Sample size n", "=CEILING(LN(1-B3)/LN(1-B4),1)"), ("Interval N / n", "=B5/B6"),
         ("Random start", 3.2), ("Sample balance (£)", "=SUM(F16:F474)"),
         ("% of pool balance", "=100*B9/SUM(Pool!B2:B3001)"),
         ("Upper error rate, 0 errors", "=_xlfn.BETA.INV(B3,1,B6)"), ("Upper error rate, 1 error", "=_xlfn.BETA.INV(B3,2,B6-1)"),
         ("Upper error rate, 2 errors", "=_xlfn.BETA.INV(B3,3,B6-2)")]
for i, (lab, v) in enumerate(items, start=3):
    au.cell(i, 1, lab); c = au.cell(i, 2, v)
    if not str(v).startswith("="): c.fill = inp
for c in ("B3", "B4", "B11", "B12", "B13"): au[c].number_format = "0.000%"
head(au, 15, ["i", "position", "loan_id", "product", "fixed?", "current_balance"])
for k in range(459):
    r = 16 + k
    au.cell(r, 1, k)
    au.cell(r, 2, f"=INT((ROUND($B$8*10,0)*$B$6+A{r}*10*$B$5)/(10*$B$6))")
    au.cell(r, 3, f"=INDEX(Pool!$A$2:$A$3001,B{r})")
    au.cell(r, 4, f"=INDEX(Pool!$C$2:$C$3001,B{r})")
    au.cell(r, 5, f'=IF(OR(D{r}="2Y Fixed",D{r}="5Y Fixed"),1,0)')
    au.cell(r, 6, f"=INDEX(Pool!$B$2:$B$3001,B{r})")
au["D3"] = "Fixed-rate share of sample balance (%)"; au["G3"] = "=100*SUMPRODUCT(E16:E474,F16:F474)/B9"
au.column_dimensions["A"].width = 30; au.column_dimensions["B"].width = 16; au.column_dimensions["C"].width = 13
wb.save(sys.argv[3]); print("saved", sys.argv[3])
