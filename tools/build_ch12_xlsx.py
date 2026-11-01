"""Build ch12/excel/ch12_excess_spread.xlsx (live formulas, tape embedded).
Run: python3 tools/build_ch12_xlsx.py data/thames_residential_2027_1_tape.csv ch12/excel/ch12_excess_spread.xlsx"""
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
NAVY = "1F2A44"; hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); M = "#,##0.00"
def head(ws, row, labels, col=1):
    for j, h in enumerate(labels, col):
        c = ws.cell(row, j, h); c.font = hdr; c.fill = fill; c.alignment = Alignment(horizontal="center", wrap_text=True)
tape = pd.read_csv(sys.argv[1], dtype={"current_balance": str, "current_rate": str})
n = len(tape); last = n + 1
wb = Workbook(); I = wb.active; I.title = "Inputs"
I["A1"] = "Chapter 12 - Thames excess spread at closing (annual run-rate, ILLUSTRATIVE rates)"; I["A1"].font = Font(bold=True, size=13, color=NAVY)
inputs = [("Compounded SONIA (% p.a.)", 3.75, "0.00"), ("Swap fixed rate paid (% p.a.)", 3.30, "0.00"),
          ("Swap notional (£)", 542600271.48, M), ("Bank Rate shift for trackers (%)", 0, "0.00"),
          ("SVR override (%, blank = tape)", None, "0.00"), ("Trustee fee (£ p.a.)", 25000, M),
          ("Paying agent and agent bank (£ p.a.)", 10000, M), ("Corporate services (£ p.a.)", 20000, M),
          ("Cash management (£ p.a.)", 50000, M), ("Other issuer expenses (£ p.a.)", 120000, M),
          ("Servicing fee (% of pool p.a.)", 0.15, "0.00"), ("Issuer profit (£ p.a., 4 IPDs)", 4000, M),
          ("Subordinated loan (£)", 9391500, M), ("Subordinated loan margin (%)", 4.00, "0.00")]
for i, (lab, v, f) in enumerate(inputs, 3):
    I.cell(i, 1, lab); c = I.cell(i, 2, v); c.fill = inp; c.number_format = f
I.column_dimensions["A"].width = 38; I.column_dimensions["B"].width = 18
# B3 sonia, B4 swap, B5 notional, B6 shift, B7 svr, B8..B12 fees, B13 servicing, B14 profit, B15 subloan, B16 sub margin
head(I, 18, ["Class", "Amount (£)", "Margin (%)", "Coupon (%)", "Interest (£ p.a.)"])
for i, (cl, a, mg) in enumerate([("A", 553000000, 0.62), ("B", 31800000, 1.10), ("C", 19100000, 1.50), ("D", 12700000, 2.20), ("E", 9500000, 3.50)]):
    r = 19 + i
    I.cell(r, 1, cl); c = I.cell(r, 2, a); c.fill = inp; c.number_format = M
    c = I.cell(r, 3, mg); c.fill = inp; c.number_format = "0.00"
    I.cell(r, 4, f"=$B$3+C{r}").number_format = "0.00"
    I.cell(r, 5, f"=ROUND(B{r}*D{r}/100,2)").number_format = M
for col in "CDE": I.column_dimensions[col].width = 16
T = wb.create_sheet("Tape")
head(T, 1, ["loan_id", "product_type", "current_balance", "current_rate", "fixed_rate_end_date", "Rate used (%)", "Balance x rate", "Fixed ends 2027"])
for i, row in enumerate(tape.itertuples(), 2):
    T.cell(i, 1, row.loan_id); T.cell(i, 2, row.product_type)
    T.cell(i, 3, float(row.current_balance)).number_format = M; T.cell(i, 4, float(row.current_rate))
    T.cell(i, 5, "" if pd.isna(row.fixed_rate_end_date) else row.fixed_rate_end_date)
    T.cell(i, 6, f'=IF(B{i}="Tracker",D{i}+Inputs!$B$6,IF(AND(B{i}="SVR",Inputs!$B$7<>""),Inputs!$B$7,D{i}))')
    T.cell(i, 7, f"=C{i}*F{i}")
    T.cell(i, 8, f'=IF(AND(ISNUMBER(SEARCH("Fixed",B{i})),LEFT(E{i},4)="2027"),1,0)')
for col, w in zip("ABCDEFGH", (12, 11, 16, 11, 16, 12, 18, 12)): T.column_dimensions[col].width = w
T.freeze_panes = "A2"
E = wb.create_sheet("ExcessSpread")
E["A1"] = "Annual excess spread at closing (GBP, illustrative)"; E["A1"].font = Font(bold=True, color=NAVY)
rows = [("Pool balance", f"=SUM(Tape!C2:C{last})", M),
        ("WA loan rate (%)", f"=SUM(Tape!G2:G{last})/B3", "0.0000"),
        ("Pool interest", f"=ROUND(SUM(Tape!G2:G{last})/100,2)", M),
        ("Swap: issuer receives", "=ROUND(Inputs!B5*Inputs!B3/100,2)", M),
        ("Swap: issuer pays", "=-ROUND(Inputs!B5*Inputs!B4/100,2)", M),
        ("Senior fees and profit", "=-ROUND(SUM(Inputs!B8:B12)+Inputs!B14+B3*Inputs!B13/100,2)", M),
        ("Class A-E interest", "=-SUM(Inputs!E19:E23)", M),
        ("Excess spread", "=SUM(B5:B9)", M),
        ("  as % of pool", "=B10/B3*100", "0.0000"),
        ("Subordinated loan interest", "=-ROUND(Inputs!B15*(Inputs!B3+Inputs!B16)/100,2)", M),
        ("Left for items 18-19", "=B10+B12", M)]
for i, (lab, f, fmt) in enumerate(rows, 3):
    E.cell(i, 1, lab); E.cell(i, 2, f).number_format = fmt
E.column_dimensions["A"].width = 30; E.column_dimensions["B"].width = 20
S = wb.create_sheet("Sensitivity")
S["A1"] = "Sensitivities: annual excess spread under one change at a time (base inputs: SONIA 3.75%, no shift)"; S["A1"].font = Font(bold=True, color=NAVY)
head(S, 3, ["Scenario", "SONIA (%)", "Bank shift (%)", "Pool interest", "Swap net", "Senior fees", "Note interest", "Excess spread", "Change"])
S["A13"] = "Helpers"; S["A13"].font = Font(bold=True, color=NAVY)
S["A14"] = "Tracker balance"; S["B14"] = f'=SUMIF(Tape!B2:B{last},"Tracker",Tape!C2:C{last})'
S["A15"] = "SVR balance"; S["B15"] = f'=SUMIF(Tape!B2:B{last},"SVR",Tape!C2:C{last})'
S["A16"] = "SVR balance x rate"; S["B16"] = f'=SUMIF(Tape!B2:B{last},"SVR",Tape!G2:G{last})'
S["A17"] = "Uplift if 2027 fixed-end loans stay on SVR"; S["B17"] = f"=ROUND(SUMPRODUCT(Tape!H2:H{last},Tape!C2:C{last},7.49-Tape!D2:D{last})/100,2)"
S["A18"] = "Loans whose fixed rate ends in 2027"; S["B18"] = f"=SUM(Tape!H2:H{last})"
S["A19"] = "Balance of those loans"; S["B19"] = f"=SUMPRODUCT(Tape!H2:H{last},Tape!C2:C{last})"
for c in ("B14", "B15", "B16", "B17", "B19"): S[c].number_format = M
P = "ExcessSpread!$B$3"; G = f"SUM(Tape!$G$2:$G${last})"
def notes(son, pd_="0"):
    return (f"=-(ROUND((Inputs!$B$19-{pd_})*({son}+Inputs!$C$19)/100,2)"
            f"+SUMPRODUCT(ROUND(Inputs!$B$20:$B$23*({son}+Inputs!$C$20:$C$23)/100,2)))")
fees = "=-ROUND(SUM(Inputs!$B$8:$B$12)+Inputs!$B$14+({pool})*Inputs!$B$13/100,2)"
scen = [("Base case", 3.75, 0, f"=ROUND({G}/100,2)", P, "0"),
        ("SONIA, Bank Rate +1%", 4.75, 1, f"=ROUND(({G}+C5*$B$14)/100,2)", P, "0"),
        ("SONIA, Bank Rate -1%", 2.75, -1, f"=ROUND(({G}+C6*$B$14)/100,2)", P, "0"),
        ("SONIA +0.25% only", 4.00, 0, f"=ROUND({G}/100,2)", P, "0"),
        ("SVR cut to 6.49%", 3.75, 0, f"=ROUND(({G}-1*$B$15)/100,2)", P, "0"),
        ("All SVR loans prepay", 3.75, 0, f"=ROUND(({G}-$B$16)/100,2)", f"{P}-$B$15", "$B$15")]
for i, (lab, son, sh, pint, pool, pd_) in enumerate(scen, 4):
    S.cell(i, 1, lab); c = S.cell(i, 2, son); c.fill = inp; c = S.cell(i, 3, sh); c.fill = inp
    S.cell(i, 4, pint); S.cell(i, 5, f"=ROUND(Inputs!$B$5*B{i}/100,2)-ROUND(Inputs!$B$5*Inputs!$B$4/100,2)")
    S.cell(i, 6, fees.format(pool=pool)); S.cell(i, 7, notes(f"B{i}", pd_))
    S.cell(i, 8, f"=SUM(D{i}:G{i})"); S.cell(i, 9, f"=H{i}-$H$4")
    for j in range(4, 10): S.cell(i, j).number_format = M
S.cell(10, 1, "2027 fixed-end loans stay on SVR"); S.cell(10, 8, "=H4+B17").number_format = M; S.cell(10, 9, "=H10-$H$4").number_format = M
S.column_dimensions["A"].width = 40
for col in "BCDEFGHI": S.column_dimensions[col].width = 16
wb.save(sys.argv[2])
