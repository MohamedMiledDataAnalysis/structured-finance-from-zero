"""Build ch18/excel/ch18_loan_level.xlsx (live formulas; inputs yellow).
Run: python3 tools/build_ch18_xlsx.py data/thames_residential_2027_1_tape.csv \
        data/ch18_regional_hpi.csv ch18/excel/ch18_loan_level.xlsx"""
import sys
from datetime import date
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L

sys.path.insert(0, "ch18/python")
import ch18_loan_level as C

NAVY = "1F2A44"
hdr, hfill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
title = Font(bold=True, size=13, color=NAVY)
tape = pd.read_csv(sys.argv[1]); hpi = pd.read_csv(sys.argv[2])
wb = Workbook()

# ---------------- Criteria ----------------
cr = wb.active; cr.title = "Criteria"
cr["A1"] = "Chapter 18 - The agency's criteria in this book (ILLUSTRATIVE)"; cr["A1"].font = title
cr["A2"] = "Yellow cells are inputs. Every other cell in the workbook is a formula."
def header(ws, r, c, names):
    for j, n in enumerate(names):
        x = ws.cell(r, c + j, n); x.font = hdr; x.fill = hfill
        x.alignment = Alignment(horizontal="center")
def put(ws, r, c, v, fmt=None, yellow=True):
    x = ws.cell(r, c, v)
    if yellow: x.fill = inp
    if fmt: x.number_format = fmt
    return x
# FF grid A4:B13
header(cr, 4, 1, ["LTV from (%)", "Base FF (%)"])
for i, (lo, v) in enumerate(C.FF_GRID):
    put(cr, 5 + i, 1, lo, "0"); put(cr, 5 + i, 2, v, "0.00")
FF_RNG = ("Criteria!$A$5:$A$13", "Criteria!$B$5:$B$13")
# LTI D4:E7
header(cr, 4, 4, ["LTI from", "LTI adj"])
for i, (lo, v) in enumerate(C.LTI_ADJ):
    put(cr, 5 + i, 4, lo, "0.0"); put(cr, 5 + i, 5, v, "0.00")
LTI_RNG = ("Criteria!$D$5:$D$7", "Criteria!$E$5:$E$7")
# Seasoning G4:H8
header(cr, 4, 7, ["Payments from", "Seasoning adj"])
for i, (lo, v) in enumerate(C.SEAS_ADJ):
    put(cr, 5 + i, 7, lo, "0"); put(cr, 5 + i, 8, v, "0.00")
SEA_RNG = ("Criteria!$G$5:$G$8", "Criteria!$H$5:$H$8")
# other adjustments D10:E16
header(cr, 10, 4, ["Adjustment", "Factor"])
other = [("Self-employed", C.SELF_EMP), ("Repayment", 1.00), ("Part and part", 1.20),
         ("Interest-only", 1.40), ("1 month in arrears", 2.00)]
for i, (n, v) in enumerate(other):
    cr.cell(11 + i, 4, n); put(cr, 11 + i, 5, v, "0.00")
# multiples & MVD scale A16:C22
header(cr, 16, 1, ["Level", "FF multiple", "MVD scale"])
for i, k in enumerate(C.LEVELS):
    cr.cell(17 + i, 1, k); put(cr, 17 + i, 2, C.MULT[k], "0.00"); put(cr, 17 + i, 3, C.MVD_SCALE[k], "0.00")
# regions G10:J22  region, group, MVD AAA, sale months
header(cr, 10, 7, ["Region", "Group", "MVD at AAA", "Months to sale"])
for i, (reg, g) in enumerate(C.GROUP.items()):
    cr.cell(11 + i, 7, reg); put(cr, 11 + i, 8, g, "0")
    put(cr, 11 + i, 9, C.MVD_AAA[g], "0%")
    put(cr, 11 + i, 10, C.SALE_MONTHS.get(reg, C.SALE_MONTHS_OTHER), "0")
REG = "Criteria!$G$11:$G$22"
# scalars A25:B31
sc = [("Forced-sale discount, flats", C.FSD_FLAT, "0%"), ("Forced-sale discount, houses", C.FSD_HOUSE, "0%"),
      ("Foreclosure cost, fixed (GBP)", C.COST_FIXED, "#,##0"), ("Foreclosure cost, % of sale price", C.COST_PCT, "0.0%"),
      ("Credit given to house price rises", C.UP_CREDIT, "0%"), ("Index quarter at cut-off", C.INDEX_Q, None)]
for i, (n, v, f) in enumerate(sc):
    cr.cell(25 + i, 1, n); put(cr, 25 + i, 2, v, f)
FSDF, FSDH, CFIX, CPCT, UPC, IDXQ = (f"Criteria!$B${25 + i}" for i in range(6))
for col, w in zip("ABCDEFGHIJ", [34, 14, 12, 18, 12, 3, 26, 8, 11, 14]):
    cr.column_dimensions[col].width = w

# ---------------- HPI ----------------
hs = wb.create_sheet("HPI")
header(hs, 1, 1, ["Region", "Quarter", "HPI"])
for i, r in enumerate(hpi.itertuples(), start=2):
    hs.cell(i, 1, r.region); hs.cell(i, 2, r.quarter); put(hs, i, 3, r.hpi, "0.0")
hs.column_dimensions["A"].width = 26
NH = len(hpi) + 1

# ---------------- Loans ----------------
ws = wb.create_sheet("Loans")
cols = ["loan_id", "origination_date", "payments_made", "original_balance", "current_balance",
        "repayment_type", "current_rate", "original_valuation", "region", "property_type",
        "employment_status", "gross_income", "months_in_arrears"]
calc = ["Quarter", "HPI at origination", "HPI at cut-off", "HPI ratio", "Indexed value", "Indexed LTV %",
        "LTI", "Base FF", "LTI adj", "Seasoning adj", "Employment adj", "Repayment adj", "Arrears adj",
        "Total adj", "Forced-sale discount", "Months to sale", "Accrued interest"]
lv = [f"{p} {k}" for k in C.LEVELS for p in ("FF", "LS")]
header(ws, 1, 1, cols + calc + lv)
col = {n: L(i + 1) for i, n in enumerate(cols + calc + lv)}
n = len(tape)
for i, r in enumerate(tape.itertuples(), start=2):
    for j, c in enumerate(cols):
        v = getattr(r, c)
        if c == "origination_date":
            v = date.fromisoformat(v)
        x = ws.cell(i, j + 1, v); x.fill = inp
        if c == "origination_date": x.number_format = "yyyy-mm-dd"
    g = lambda name: f"{col[name]}{i}"
    f = {}
    f["Quarter"] = f'=YEAR({g("origination_date")})&"Q"&ROUNDUP(MONTH({g("origination_date")})/3,0)'
    f["HPI at origination"] = f'=SUMIFS(HPI!$C$2:$C${NH},HPI!$A$2:$A${NH},{g("region")},HPI!$B$2:$B${NH},{g("Quarter")})'
    f["HPI at cut-off"] = f'=SUMIFS(HPI!$C$2:$C${NH},HPI!$A$2:$A${NH},{g("region")},HPI!$B$2:$B${NH},{IDXQ})'
    f["HPI ratio"] = f'={g("HPI at cut-off")}/{g("HPI at origination")}'
    f["Indexed value"] = (f'={g("original_valuation")}*IF({g("HPI ratio")}>1,1+{UPC}*({g("HPI ratio")}-1),'
                          f'{g("HPI ratio")})')
    f["Indexed LTV %"] = f'=100*{g("current_balance")}/{g("Indexed value")}'
    f["LTI"] = f'={g("original_balance")}/{g("gross_income")}'
    f["Base FF"] = f'=LOOKUP({g("Indexed LTV %")},{FF_RNG[0]},{FF_RNG[1]})/100'
    f["LTI adj"] = f'=LOOKUP({g("LTI")},{LTI_RNG[0]},{LTI_RNG[1]})'
    f["Seasoning adj"] = f'=LOOKUP({g("payments_made")},{SEA_RNG[0]},{SEA_RNG[1]})'
    f["Employment adj"] = f'=IF({g("employment_status")}="Self-employed",Criteria!$E$11,1)'
    f["Repayment adj"] = f'=INDEX(Criteria!$E$12:$E$14,MATCH({g("repayment_type")},Criteria!$D$12:$D$14,0))'
    f["Arrears adj"] = f'=IF({g("months_in_arrears")}>=1,Criteria!$E$15,1)'
    f["Total adj"] = (f'={g("LTI adj")}*{g("Seasoning adj")}*{g("Employment adj")}*'
                      f'{g("Repayment adj")}*{g("Arrears adj")}')
    f["Forced-sale discount"] = f'=IF({g("property_type")}="Flat",{FSDF},{FSDH})'
    f["Months to sale"] = f'=INDEX(Criteria!$J$11:$J$22,MATCH({g("region")},{REG},0))'
    f["Accrued interest"] = f'={g("current_balance")}*{g("current_rate")}/100*{g("Months to sale")}/12'
    for k_i, k in enumerate(C.LEVELS):
        rr = 17 + k_i
        f[f"FF {k}"] = f'=MIN(1,{g("Base FF")}*{g("Total adj")}*Criteria!$B${rr})'
        mvd = f'INDEX(Criteria!$I$11:$I$22,MATCH({g("region")},{REG},0))*Criteria!$C${rr}'
        sale = f'{g("Indexed value")}*(1-{mvd})*(1-{g("Forced-sale discount")})'
        f[f"LS {k}"] = (f'=MAX(0,{g("current_balance")}+{g("Accrued interest")}+{CFIX}+{CPCT}*{sale}-{sale})'
                        f'/{g("current_balance")}')
    for name, formula in f.items():
        x = ws.cell(i, cols.index(name) + 1 if name in cols else len(cols) + (calc + lv).index(name) + 1, formula)
        if name.startswith(("FF", "LS", "Base FF")): x.number_format = "0.00%"
        elif name in ("Indexed value", "Accrued interest"): x.number_format = "#,##0.00"
        elif name in ("Indexed LTV %",): x.number_format = "0.00"
        elif name in ("HPI ratio", "LTI", "Total adj"): x.number_format = "0.0000"
ws.freeze_panes = "B2"
for j in range(1, len(cols) + len(calc) + len(lv) + 1):
    ws.column_dimensions[L(j)].width = 13
last = n + 1

# ---------------- Summary ----------------
sm = wb.create_sheet("Summary", 1)
sm["A1"] = "Thames pool - WAFF, WALS and expected loss by rating level"; sm["A1"].font = title
BAL = f"Loans!${col['current_balance']}$2:${col['current_balance']}${last}"
header(sm, 3, 1, ["Level", "WAFF", "WALS", "Expected loss (% pool)", "Expected loss (GBP)"])
for k_i, k in enumerate(C.LEVELS):
    r = 4 + k_i
    FF = f"Loans!${col['FF ' + k]}$2:${col['FF ' + k]}${last}"
    LS = f"Loans!${col['LS ' + k]}$2:${col['LS ' + k]}${last}"
    sm.cell(r, 1, k)
    sm.cell(r, 2, f"=SUMPRODUCT({BAL},{FF})/SUM({BAL})").number_format = "0.00%"
    sm.cell(r, 5, f"=SUMPRODUCT({BAL},{FF},{LS})").number_format = "#,##0.00"
    sm.cell(r, 3, f"=E{r}/SUMPRODUCT({BAL},{FF})").number_format = "0.00%"
    sm.cell(r, 4, f"=E{r}/SUM({BAL})").number_format = "0.00%"
sm["A11"] = "Pool balance (GBP)"; sm["B11"] = f"=SUM({BAL})"; sm["B11"].number_format = "#,##0.00"
LTVc = col["Indexed LTV %"]
sm["A12"] = "WA indexed LTV (%)"; sm["B12"] = f"=SUMPRODUCT({BAL},Loans!${LTVc}$2:${LTVc}${last})/B11"
sm["B12"].number_format = "0.00"
sm["A13"] = "Check: EL = WAFF x WALS (AAA)"; sm["B13"] = "=D4-B4*C4"; sm["B13"].number_format = "0.000000"
for c_, w in zip("ABCDE", [30, 12, 12, 22, 20]):
    sm.column_dimensions[c_].width = w
wb.save(sys.argv[3])
print("saved", sys.argv[3])
