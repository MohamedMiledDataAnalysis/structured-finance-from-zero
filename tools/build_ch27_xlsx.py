"""Build ch27/excel/ch27_investor_report.xlsx - reconciliations, first investor report note table, tests.
Run from the book folder:  python3 tools/build_ch27_xlsx.py ch27/excel/ch27_investor_report.xlsx"""
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter as L
NAVY = "1F2A44"; hdr = Font(bold=True, color="FFFFFF"); hf = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); M = "#,##0.00"; B = Font(bold=True, color=NAVY)
wb = Workbook(); first = wb.active

def data_sheet(name, df, numeric):
    ws = wb.create_sheet(name)
    for j, h in enumerate(df.columns, 1):
        c = ws.cell(1, j, h); c.font = hdr; c.fill = hf; ws.column_dimensions[L(j)].width = 16
    for i, row in enumerate(df.itertuples(index=False), 2):
        for j, v in enumerate(row, 1):
            h = df.columns[j - 1]
            c = ws.cell(i, j, float(v) if h in numeric else v); c.fill = inp
            if h in numeric: c.number_format = M
    return ws, len(df) + 1

st = pd.read_csv("data/ch27_thames_bank_statement_ipd1.csv", dtype=str)
dc = pd.read_csv("data/ch27_thames_daily_collections.csv", dtype=str)
res = pd.read_csv("data/thames_ipd_results.csv", dtype=str)
perf = pd.concat([pd.read_csv("data/thames_performance_monthly.csv", dtype=str),
                  pd.read_csv("data/ch26_thames_performance_2029_02.csv", dtype=str)])
S, ns = data_sheet("Statement", st, {"debit", "credit", "balance"})
S.column_dimensions["B"].width = 58
Dd, nd = data_sheet("Daily", dc, {"amount", "duplicate_included", "business_days_to_transfer"})
numres = set(res.columns) - {"ipd", "determination_date", "interest_period_start", "collection_periods"}
Rs, nr = data_sheet("Results", res, numres)
P, npf = data_sheet("Performance", perf, set(perf.columns) - {"collection_period"})
col = lambda df, name: L(list(df.columns).index(name) + 1)
RC = lambda name: f"Results!${col(res, name)}$2"          # first IPD value
SC = lambda name: f"Statement!${col(st, name)}$2:${col(st, name)}${ns}"
DC = lambda name: f"Daily!${col(dc, name)}$2:${col(dc, name)}${nd}"
PC = lambda name: f"Performance!${col(perf, name)}$2:${col(perf, name)}${npf}"

# Reconciliation
w = first; w.title = "Reconciliation"
w.column_dimensions["A"].width = 46; w.column_dimensions["B"].width = 18
w["A1"] = "Thames Residential 2027-1 - cash reconciliations for the IPD of 15 June 2027"; w["A1"].font = Font(bold=True, size=13, color=NAVY)
w["A3"] = "1. Collections: bank statement to servicer report"; w["A3"].font = B
rows = [
    (4, "Credits from Kingsbridge", f'=SUMIF({SC("description")},"Kingsbridge: coll*",{SC("credit")})'),
    (5, "less Direct Debit indemnity claim", f'=-SUMIF({SC("description")},"*indemnity*",{SC("debit")})'),
    (6, "less June receipts (next IPD)", f'=-SUMIF({DC("collection_period")},"2027-06",{DC("amount")})'),
    (7, "Feb-May collections per bank", "=SUM(B4:B6)"),
    (8, "Feb-May collections per servicer",
     "=" + "+".join(f'SUMPRODUCT(({PC("collection_period")}>="2027-02")*({PC("collection_period")}<="2027-05")*{PC(f)})'
                    for f in ["interest_collected", "arrears_interest_recovered", "scheduled_principal",
                              "prepayments", "principal_recoveries"])),
    (9, "Difference", "=ROUND(B7-B8,2)"),
    (10, "Longest sweep after closing (business days)",
     f'=MAX(IF({DC("receipt_date")}>="2027-03-18",{DC("business_days_to_transfer")}))'),
    (11, "Servicer termination limit (business days)", 3),
    (12, "Collections paid over in time?", '=IF(B10<=B11,"Yes","No - servicer termination event")'),
]
w["A14"] = "2. IPD payments: waterfall to bank statement"; w["A14"].font = B
rows += [
    (15, "Paid out per waterfall", f"={RC('available_revenue')}-{RC('r15_reserve_credit')}-{RC('r03_issuer_profit')}+{RC('available_principal')}"),
    (16, "Debits on 15 Jun per statement", f'=SUMIF({SC("date")},"2027-06-15",{SC("debit")})'),
    (17, "Difference", "=ROUND(B15-B16,2)"),
    (18, "Balance after the IPD", f"=INDEX({SC('balance')},{ns - 1})"),
    (19, "June receipts + issuer profit", f"=-B6+{RC('r03_issuer_profit')}"),
    (20, "Difference", "=ROUND(B18-B19,2)"),
]
for r, lab, f in rows:
    w.cell(r, 1, lab); c = w.cell(r, 2, f); c.number_format = "0" if r in (10, 11) else M
    if r == 11: c.fill = inp
w["B10"] = None
w.formula_attributes = {}
from openpyxl.worksheet.formula import ArrayFormula
w["B10"] = ArrayFormula("B10", f'=MAX(IF({DC("receipt_date")}>="2027-03-18",{DC("business_days_to_transfer")}))')

# Report note table
r = wb.create_sheet("Report", 1)
r["A1"] = "Investor report extract - notes after the IPD of 15 June 2027"; r["A1"].font = Font(bold=True, size=13, color=NAVY)
heads = ["Class", "Original", "Principal paid", "After IPD", "Pool factor", "Margin %", "Rate %", "Interest paid"]
for j, h in enumerate(heads, 1):
    c = r.cell(3, j, h); c.font = hdr; c.fill = hf; r.column_dimensions[L(j)].width = 17
orig = {"A": 553000000.00, "B": 31800000.00, "C": 19100000.00, "D": 12700000.00, "E": 9500000.00, "Z": 9571146.31}
mg = {"A": 0.62, "B": 1.10, "C": 1.50, "D": 2.20, "E": 3.50}
num = {"A": 5, "B": 7, "C": 9, "D": 11, "E": 13}
for i, c_ in enumerate("ABCDEZ", 4):
    r.cell(i, 1, c_)
    c = r.cell(i, 2, orig[c_]); c.fill = inp; c.number_format = M
    r.cell(i, 3, f"={RC(f'class_{c_.lower()}_principal')}").number_format = M
    r.cell(i, 4, f"={RC(f'class_{c_.lower()}_balance_after')}").number_format = M
    r.cell(i, 5, f"=ROUND(D{i}/B{i},6)").number_format = "0.000000"
    if c_ in mg:
        c = r.cell(i, 6, mg[c_]); c.fill = inp; c.number_format = "0.00"
        r.cell(i, 7, f"={RC('compounded_sonia_pct')}+F{i}").number_format = "0.00"
        r.cell(i, 8, f"={RC(f'r{num[c_]:02d}_class_{c_.lower()}_interest')}").number_format = M
r.cell(10, 1, "Total"); r.cell(10, 2, "=SUM(B4:B9)").number_format = M
r.cell(10, 3, "=SUM(C4:C9)").number_format = M; r.cell(10, 4, "=SUM(D4:D9)").number_format = M
r.cell(10, 8, "=SUM(H4:H8)").number_format = M
# Rating triggers (illustrative ratings)
r["A13"] = "Rating triggers (ratings are illustrative inputs; scale position: AAA=1 ... BBB-=10)"; r["A13"].font = B
for j, h in enumerate(["Counterparty / role", "Rating now", "Rank now", "Trigger", "Rank of trigger", "Breached?"], 1):
    c = r.cell(14, j, h); c.font = hdr; c.fill = hf
scale = ["AAA", "AA+", "AA", "AA-", "A+", "A", "A-", "BBB+", "BBB", "BBB-", "BB+"]
r["J3"] = "Rating scale"; r["J3"].font = B
for i, s_ in enumerate(scale, 4):
    r.cell(i, 10, s_).fill = inp; r.cell(i, 11, i - 3).fill = inp
trig = [("Northgate Bank plc - account bank", "A+", "A"),
        ("Northgate Bank plc - swap: collateral", "A+", "A"),
        ("Northgate Bank plc - swap: replacement", "A+", "BBB+"),
        ("Kingsbridge - servicer: back-up servicer", "A-", "BBB-")]
for i, (who, now, t) in enumerate(trig, 15):
    r.cell(i, 1, who); r.cell(i, 2, now).fill = inp
    r.cell(i, 3, f"=MATCH(B{i},$J$4:$J$14,0)"); r.cell(i, 4, t).fill = inp
    r.cell(i, 5, f"=MATCH(D{i},$J$4:$J$14,0)")
    r.cell(i, 6, f'=IF(C{i}>E{i},"Yes","No")')
r.column_dimensions["A"].width = 40

# Tests across IPDs
t = wb.create_sheet("Tests", 2)
t["A1"] = "Tests at each IPD"; t["A1"].font = Font(bold=True, size=13, color=NAVY)
t["H1"] = "Pool at cut-off"; t["I1"] = 635671146.31; t["I1"].fill = inp; t["I1"].number_format = M
t["H2"] = "Reserve required"; t["I2"] = 9391500.00; t["I2"].fill = inp; t["I2"].number_format = M
heads = ["IPD", "Last collection month", "Reserve after", "Reserve at required?", "PDL after", ">3m arrears %",
         "Cumulative losses", "Cum loss %", "Pool % of cut-off", "Clean-up call available?"]
for j, h in enumerate(heads, 1):
    c = t.cell(3, j, h); c.font = hdr; c.fill = hf; t.column_dimensions[L(j)].width = 17
for k in range(8):
    i = 4 + k; rr = k + 2
    rc = lambda name: f"Results!{col(res, name)}{rr}"
    t.cell(i, 1, f"={rc('ipd')}")
    t.cell(i, 2, f"=RIGHT({rc('collection_periods')},7)")
    t.cell(i, 3, f"={rc('reserve_balance_after')}").number_format = M
    t.cell(i, 4, f'=IF(C{i}>=$I$2,"Yes","No")')
    t.cell(i, 5, "=" + "+".join(rc(f"pdl_{c}_after") for c in "abcdez")).number_format = M
    t.cell(i, 6, f"=INDEX({PC('arrears_3_6m_pct')},MATCH(B{i},{PC('collection_period')},0))"
                 f"+INDEX({PC('arrears_6m_plus_pct')},MATCH(B{i},{PC('collection_period')},0))").number_format = "0.000"
    t.cell(i, 7, f"={rc('realised_losses')}" + (f"+G{i-1}" if k else "")).number_format = M
    t.cell(i, 8, f"=ROUND(G{i}/$I$1*100,4)").number_format = "0.0000"
    t.cell(i, 9, f"=ROUND({rc('pool_balance_end')}/$I$1*100,2)").number_format = "0.00"
    t.cell(i, 10, f'=IF(I{i}<10,"Yes","No")')
wb.save(sys.argv[1])
