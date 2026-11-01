"""Build ch26/excel/ch26_waterfall.xlsx - the real Thames waterfall, 8 IPDs, live formulas.
Run from the book folder:  python3 tools/build_ch26_xlsx.py ch26/excel/ch26_waterfall.xlsx
Column A of sheet Waterfall holds the field name used in data/thames_ipd_results.csv (for checking)."""
import sys, datetime as dt
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L

NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); hfill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); bold = Font(bold=True, color=NAVY)
M = "#,##0.00"
wb = Workbook()

# ---------------- Inputs ----------------
ws = wb.active; ws.title = "Inputs"
ws["A1"] = "Chapter 26 - Thames Residential 2027-1: deal terms (Deal Fact Sheets)"; ws["A1"].font = Font(bold=True, size=13, color=NAVY)
inputs = [  # row, label, value, fmt
    (3, "Closing date", dt.date(2027, 3, 18), "dd mmm yyyy"),
    (4, "Swap fixed rate (% p.a.)", 3.30, "0.00"),
    (5, "General reserve required amount", 9391500.00, M),
    (6, "Subordinated loan margin over SONIA (%)", 4.00, "0.00"),
    (7, "Servicing fee (% p.a. of pool)", 0.15, "0.00"),
    (8, "Issuer profit per IPD", 1000.00, M),
    (9, "Trustee fee p.a.", 25000.00, M),
    (10, "Paying agent and agent bank fee p.a.", 10000.00, M),
    (11, "Corporate services fee p.a.", 20000.00, M),
    (12, "Cash manager fee p.a.", 50000.00, M),
    (13, "Other issuer expenses p.a.", 120000.00, M),
    (14, "Day-count basis (Actual/365 Fixed)", 365, "0"),
    (15, "Subordinated loan at closing", 9391500.00, M),
]
for r, lab, v, f in inputs:
    ws.cell(r, 1, lab); c = ws.cell(r, 2, v); c.number_format = f; c.fill = inp
for j, h in enumerate(["Class", "Original balance", "Margin (%)"], 1):
    c = ws.cell(16, j, h); c.font = hdr; c.fill = hfill
notes = [("A", 553000000.00, 0.62), ("B", 31800000.00, 1.10), ("C", 19100000.00, 1.50),
         ("D", 12700000.00, 2.20), ("E", 9500000.00, 3.50), ("Z", 9571146.31, None)]
for i, (k, b, m) in enumerate(notes):
    r = 17 + i
    ws.cell(r, 1, k); c = ws.cell(r, 2, b); c.number_format = M; c.fill = inp
    if m is not None:
        c = ws.cell(r, 3, m); c.number_format = "0.00"; c.fill = inp
ws.cell(23, 1, "Total"); ws.cell(23, 2, "=SUM(B17:B22)").number_format = M
ws.column_dimensions["A"].width = 40; ws.column_dimensions["B"].width = 18; ws.column_dimensions["C"].width = 12
ws["A25"] = "Yellow cells are inputs. Every other cell in the workbook is a formula."
NOTE_ROW = {k: 17 + i for i, (k, _, _) in enumerate(notes)}

# ---------------- IPD inputs ----------------
ip = wb.create_sheet("IPDs")
son = pd.read_csv("data/thames_sonia_assumption.csv")
swp = pd.read_csv("data/ch26_thames_swap_notional.csv")
for j, h in enumerate(["IPD no.", "IPD date", "Compounded SONIA (%)", "Swap notional"], 1):
    c = ip.cell(1, j, h); c.font = hdr; c.fill = hfill; ip.column_dimensions[L(j)].width = 20
for k in range(8):
    r = k + 2
    ip.cell(r, 1, k + 1)
    c = ip.cell(r, 2, dt.date.fromisoformat(son.interest_payment_date[k])); c.number_format = "dd mmm yyyy"; c.fill = inp
    c = ip.cell(r, 3, float(son.compounded_sonia_pct[k])); c.number_format = "0.00"; c.fill = inp
    c = ip.cell(r, 4, float(swp.swap_notional[k])); c.number_format = M; c.fill = inp

hol = ["2027-01-01","2027-03-26","2027-03-29","2027-05-03","2027-05-31","2027-08-30","2027-12-27","2027-12-28",
       "2028-01-03","2028-04-14","2028-04-17","2028-05-01","2028-05-29","2028-08-28","2028-12-25","2028-12-26",
       "2029-01-01","2029-03-30","2029-04-02"]
c = ip.cell(1, 6, "England and Wales bank holidays"); c.font = hdr; c.fill = hfill; ip.column_dimensions["F"].width = 30
for i, h in enumerate(hol):
    c = ip.cell(i + 2, 6, dt.date.fromisoformat(h)); c.number_format = "dd mmm yyyy"; c.fill = inp

# ---------------- Collections ----------------
co = wb.create_sheet("Collections")
perf = pd.concat([pd.read_csv("data/thames_performance_monthly.csv"),
                  pd.read_csv("data/ch26_thames_performance_2029_02.csv")], ignore_index=True)
cols = ["collection_period", "opening_balance", "interest_collected", "arrears_interest_recovered",
        "scheduled_principal", "prepayments", "principal_recoveries", "realised_losses", "closing_balance"]
heads = ["IPD no."] + cols + ["Servicing fee"]
for j, h in enumerate(heads, 1):
    c = co.cell(1, j, h); c.font = hdr; c.fill = hfill; co.column_dimensions[L(j)].width = 17
ipd_of = [1]*4 + [k for k in range(2, 9) for _ in range(3)]
for i, row in perf.iterrows():
    r = i + 2
    c = co.cell(r, 1, ipd_of[i]); c.fill = inp
    c = co.cell(r, 2, row.collection_period); c.fill = inp
    for j, f in enumerate(cols[1:], 3):
        c = co.cell(r, j, float(row[f])); c.number_format = M; c.fill = inp
    co.cell(r, 11, f"=ROUND(C{r}*Inputs!$B$7/100/12,2)").number_format = M
NC = len(perf) + 1
co.freeze_panes = "C2"

# ---------------- Waterfall ----------------
w = wb.create_sheet("Waterfall")
w.column_dimensions["A"].width = 28; w.column_dimensions["B"].width = 44
for j in range(3, 11): w.column_dimensions[L(j)].width = 16
w["B1"] = "Thames Residential 2027-1 - pre-enforcement waterfalls, IPDs 1 to 8"; w["B1"].font = Font(bold=True, size=13, color=NAVY)
row = [2]; R = {}
def line(key, label, f, fmt=M, b=False):
    row[0] += 1; r = row[0]; R[key] = r
    w.cell(r, 1, key).font = Font(color="808080", size=8)
    w.cell(r, 2, label)
    if b: w.cell(r, 2).font = Font(bold=True)
    for k in range(8):
        col = L(3 + k); prev = L(2 + k)
        v = f(k, col, prev)
        c = w.cell(r, 3 + k, v); c.number_format = fmt
        if b: c.font = Font(bold=True)
    return r
def head(text):
    row[0] += 2; r = row[0]
    c = w.cell(r, 2, text); c.font = hdr; c.fill = hfill
    for k in range(8): w.cell(r, 3 + k).fill = hfill
SUM = lambda f, col: f"SUMIF(Collections!$A$2:$A${NC},{col}$3,Collections!{f}$2:{f}${NC})"
line("ipd_no", "IPD number", lambda k, c, p: k + 1, "0", True)
line("ipd", "Interest payment date", lambda k, c, p: f"=INDEX(IPDs!$B$2:$B$9,{c}{R['ipd_no']})", "dd mmm yyyy", True)
line("determination_date", "Determination date (5 business days before)",
     lambda k, c, p: f"=WORKDAY({c}{R['ipd']},-5,IPDs!$F$2:$F$20)", "dd mmm yyyy")
line("interest_period_start", "Interest period start",
     lambda k, c, p: "=Inputs!B3" if k == 0 else f"={p}{R['ipd']}", "dd mmm yyyy")
line("days", "Days in interest period", lambda k, c, p: f"={c}{R['ipd']}-{c}{R['interest_period_start']}", "0")
line("compounded_sonia_pct", "Compounded SONIA (%)", lambda k, c, p: f"=INDEX(IPDs!$C$2:$C$9,{c}{R['ipd_no']})", "0.00")
line("year_fraction", "Year fraction (days / 365)", lambda k, c, p: f"={c}{R['days']}/Inputs!$B$14", "0.000000")
head("Revenue receipts")
line("interest_collected", "Interest collected", lambda k, c, p: "=" + SUM("D", c))
line("arrears_interest_recovered", "Arrears interest recovered", lambda k, c, p: "=" + SUM("E", c))
line("revenue_collections", "Revenue collections", lambda k, c, p: f"={c}{R['interest_collected']}+{c}{R['arrears_interest_recovered']}", b=True)
line("swap_notional", "Swap notional", lambda k, c, p: f"=INDEX(IPDs!$D$2:$D$9,{c}{R['ipd_no']})")
line("swap_fixed_leg", "Swap fixed leg (issuer pays)", lambda k, c, p: f"=ROUND({c}{R['swap_notional']}*Inputs!$B$4/100*{c}{R['year_fraction']},2)")
line("swap_floating_leg", "Swap floating leg (issuer receives)", lambda k, c, p: f"=ROUND({c}{R['swap_notional']}*{c}{R['compounded_sonia_pct']}/100*{c}{R['year_fraction']},2)")
line("swap_net_received", "Swap net amount received", lambda k, c, p: f"=MAX({c}{R['swap_floating_leg']}-{c}{R['swap_fixed_leg']},0)")
line("reserve_brought_forward", "General reserve brought forward",
     lambda k, c, p: "=Inputs!B5" if k == 0 else f"={p}{{RES_AFTER}}")
line("available_revenue", "Available revenue receipts",
     lambda k, c, p: f"={c}{R['revenue_collections']}+{c}{R['swap_net_received']}+{c}{R['reserve_brought_forward']}", b=True)
head("Amounts due this IPD")
for key, lab, cell in (("fee_trustee", "Trustee fee due (Act/365)", "B9"), ("fee_pa", "Paying agent fee due", "B10"),
                       ("fee_csp", "Corporate services fee due", "B11"), ("fee_cm", "Cash manager fee due", "B12"),
                       ("fee_other", "Other issuer expenses due", "B13")):
    line(key, lab, lambda k, c, p, cell=cell: f"=ROUND(Inputs!${cell[0]}${cell[1:]}*{c}{R['days']}/Inputs!$B$14,2)")
line("servicing_due", "Servicing fee due", lambda k, c, p: f"=SUMIF(Collections!$A$2:$A${NC},{c}$3,Collections!K$2:K${NC})")
line("swap_net_due", "Swap net amount payable", lambda k, c, p: f"=MAX({c}{R['swap_fixed_leg']}-{c}{R['swap_floating_leg']},0)")
OPEN = {}
for k_, cl in enumerate("ABCDEZ"):
    OPEN[cl] = line(f"class_{cl.lower()}_open", f"Class {cl} balance before IPD",
                    lambda k, c, p, cl=cl: f"=Inputs!$B${NOTE_ROW[cl]}" if k == 0 else f"={p}{{BAL_{cl}}}")
INTDUE = {}
for cl in "ABCDE":
    INTDUE[cl] = line(f"class_{cl.lower()}_interest_due", f"Class {cl} interest due",
        lambda k, c, p, cl=cl: f"=ROUND({c}{OPEN[cl]}*({c}{R['compounded_sonia_pct']}+Inputs!$C${NOTE_ROW[cl]})/100*{c}{R['year_fraction']},2)")
line("sub_open", "Subordinated loan before IPD", lambda k, c, p: "=Inputs!B15" if k == 0 else f"={p}{{SUB_AFTER}}")
line("sub_loan_interest_due", "Subordinated loan interest due (incl. unpaid b/f)",
     lambda k, c, p: f"=ROUND({c}{R['sub_open']}*({c}{R['compounded_sonia_pct']}+Inputs!$B$6)/100*{c}{R['year_fraction']},2)"
     + ("" if k == 0 else f"+{p}{{SUB_UNPAID}}"))
head("Principal deficiency ledger (losses debited Z first)")
line("realised_losses", "Realised losses this IPD", lambda k, c, p: "=" + SUM("I", c))
PDLPRE = {}; prev_debits = []
for cl in "ZEDCBA":
    before = "0" if True else ""
    dr = line(f"pdl_{cl.lower()}_debit", f"PDL debit, Class {cl}",
        lambda k, c, p, cl=cl, pdv=list(prev_debits): (
            f"=MIN({c}{R['realised_losses']}" + "".join(f"-{c}{x}" for x in pdv) +
            f",{c}{OPEN[cl]}-" + ("0" if k == 0 else f"{p}{{PDL_{cl}}}") + ")"))
    prev_debits.append(dr)
    PDLPRE[cl] = line(f"pdl_{cl.lower()}_before_cure", f"PDL Class {cl} before cure",
        lambda k, c, p, cl=cl, dr=dr: f"={c}{dr}" + ("" if k == 0 else f"+{p}{{PDL_{cl}}}"))
head("Revenue priority of payments")
first = row[0] + 1
AV = R["available_revenue"]
def left(c):  # available revenue minus everything already paid above
    return f"({c}{AV}-SUM({c}${first}:{c}{row[0]-1}))"
line("r01_trustee", "(1) Note and security trustee", lambda k, c, p: f"=MIN({c}{R['fee_trustee']},{c}{AV})")
two = [("r02_paying_agent", "(2) Paying agent and agent bank", "{c}" + str(R["fee_pa"])),
       ("r02_corporate_services", "(2) Corporate services provider", "{c}" + str(R["fee_csp"])),
       ("r02_cash_manager", "(2) Cash manager", "{c}" + str(R["fee_cm"])),
       ("r02_servicer", "(2) Servicer", None),
       ("r02_other_expenses", "(2) Other issuer expenses", "{c}" + str(R["fee_other"]))]
tot2 = "({c}" + str(R["fee_pa"]) + "+{c}" + str(R["fee_csp"]) + "+{c}" + str(R["fee_cm"]) + "+{c}" + str(R["fee_other"]) + "+{c}" + str(R["servicing_due"]) + ")"
r01 = R["r01_trustee"]
for key, lab, due in two:
    line(key, lab, lambda k, c, p, due=due: (
        lambda d: f"=IF({c}{AV}-{c}{r01}>={tot2.format(c=c)},{d},ROUND(({c}{AV}-{c}{r01})*{d}/{tot2.format(c=c)},2))")(
        due.format(c=c) if due else f"{c}{R['servicing_due']}"))
line("r03_issuer_profit", "(3) Issuer profit", lambda k, c, p: f"=MIN(Inputs!$B$8,{left(c)})")
line("r04_swap_net_payment", "(4) Swap net payment", lambda k, c, p: f"=MIN({c}{R['swap_net_due']},{left(c)})")
CURE = []
for cl, n in zip("ABCDE", (5, 7, 9, 11, 13)):
    line(f"r{n:02d}_class_{cl.lower()}_interest", f"({n}) Class {cl} interest", lambda k, c, p, cl=cl: f"=MIN({c}{INTDUE[cl]},{left(c)})")
    CURE.append(line(f"r{n+1:02d}_class_{cl.lower()}_pdl", f"({n+1}) Class {cl} PDL", lambda k, c, p, cl=cl: f"=MIN({c}{PDLPRE[cl]},{left(c)})"))
line("r15_reserve_credit", "(15) General reserve to required amount", lambda k, c, p: f"=MIN(Inputs!$B$5,{left(c)})")
CURE.append(line("r16_class_z_pdl", "(16) Class Z PDL", lambda k, c, p: f"=MIN({c}{PDLPRE['Z']},{left(c)})"))
line("r17_sub_swap_termination", "(17) Subordinated swap termination", lambda k, c, p: "=0")
line("r18_sub_loan_interest", "(18) Subordinated loan interest", lambda k, c, p: f"=MIN({c}{R['sub_loan_interest_due']},{left(c)})")
line("r18_sub_loan_principal", "(18) Subordinated loan principal", lambda k, c, p: f"=MIN({c}{R['sub_open']},{left(c)})")
line("r19_deferred_consideration", "(19) Deferred consideration", lambda k, c, p: f"={left(c)}")
last = row[0]
line("revenue_check", "Check: available minus paid (must be 0)", lambda k, c, p: f"={c}{AV}-SUM({c}{first}:{c}{last})")
line("reserve_drawn", "Reserve used this IPD", lambda k, c, p: f"=Inputs!$B$5-{c}{R['r15_reserve_credit']}")
head("Principal receipts and priority of payments")
line("scheduled_principal", "Scheduled principal", lambda k, c, p: "=" + SUM("F", c))
line("prepayments", "Prepayments", lambda k, c, p: "=" + SUM("G", c))
line("principal_recoveries", "Principal recoveries", lambda k, c, p: "=" + SUM("H", c))
line("principal_collections", "Principal collections", lambda k, c, p: f"=SUM({c}{R['scheduled_principal']}:{c}{R['principal_recoveries']})", b=True)
line("pdl_cured_from_revenue", "PDL cured from revenue", lambda k, c, p: "=" + "+".join(f"{c}{x}" for x in CURE))
line("principal_addition_amounts", "Principal addition amounts", lambda k, c, p: "=0")
line("available_principal", "Available principal receipts",
     lambda k, c, p: f"={c}{R['principal_collections']}+{c}{R['pdl_cured_from_revenue']}-{c}{R['principal_addition_amounts']}", b=True)
pfirst = row[0] + 1
for cl in "ABCDEZ":
    line(f"class_{cl.lower()}_principal", f"Class {cl} principal",
         lambda k, c, p, cl=cl: f"=MIN({c}{OPEN[cl]},{c}{R['available_principal']}" + (
             f"-SUM({c}${pfirst}:{c}{row[0]-1}))" if row[0] > pfirst else ")"))
head("Balances after the IPD")
for cl in "ABCDEZ":
    line(f"class_{cl.lower()}_balance_after", f"Class {cl} balance after",
         lambda k, c, p, cl=cl: f"={c}{OPEN[cl]}-{c}{R[f'class_{cl.lower()}_principal']}")
line("notes_total_after", "All notes after", lambda k, c, p: f"=SUM({c}{R['class_a_balance_after']}:{c}{R['class_z_balance_after']})", b=True)
CUREOF = dict(zip("ABCDEZ", CURE))
for cl in "ABCDEZ":
    line(f"pdl_{cl.lower()}_after", f"PDL Class {cl} after", lambda k, c, p, cl=cl: f"={c}{PDLPRE[cl]}-{c}{CUREOF[cl]}")
line("reserve_balance_after", "General reserve after", lambda k, c, p: f"={c}{R['r15_reserve_credit']}")
line("sub_loan_balance_after", "Subordinated loan after", lambda k, c, p: f"={c}{R['sub_open']}-{c}{R['r18_sub_loan_principal']}")
line("sub_loan_interest_unpaid_after", "Subordinated loan interest unpaid c/f",
     lambda k, c, p: f"={c}{R['sub_loan_interest_due']}-{c}{R['r18_sub_loan_interest']}")
line("pool_balance_end", "Pool balance at end of last collection period",
     lambda k, c, p: f"=INDEX(Collections!$J$2:$J${NC},MATCH({c}$3,Collections!$A$2:$A${NC},1))")
line("notes_minus_pool", "Notes minus pool (rounding)", lambda k, c, p: f"={c}{R['notes_total_after']}-{c}{R['pool_balance_end']}")
# resolve forward references {RES_AFTER}, {BAL_x}, {PDL_x}, {SUB_AFTER}
rep = {"{RES_AFTER}": str(R["reserve_balance_after"]), "{SUB_AFTER}": str(R["sub_loan_balance_after"]),
       "{SUB_UNPAID}": str(R["sub_loan_interest_unpaid_after"])}
for cl in "ABCDEZ":
    rep["{BAL_" + cl + "}"] = str(R[f"class_{cl.lower()}_balance_after"])
    rep["{PDL_" + cl + "}"] = str(R[f"pdl_{cl.lower()}_after"])
for rr in w.iter_rows(min_row=3, max_row=row[0], min_col=3, max_col=10):
    for c in rr:
        if isinstance(c.value, str):
            for a, b in rep.items(): c.value = c.value.replace(a, b)
w.freeze_panes = "C4"
wb.save(sys.argv[1])
print("rows:", row[0])
