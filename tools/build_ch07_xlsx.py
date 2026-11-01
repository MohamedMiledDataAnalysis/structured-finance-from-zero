"""Build ch07/excel/ch07_tape_template.xlsx: data dictionary checks on the full tape,
the field map, and the template-style extract for ten loans (all live formulas).
Run from the book folder:
  python3 tools/build_ch07_xlsx.py data/thames_residential_2027_1_tape.csv ch07/excel/ch07_tape_template.xlsx"""
import sys, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter as L
NAVY = "1F2A44"; hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); title = Font(bold=True, size=13, color=NAVY)
rows = list(csv.DictReader(open(sys.argv[1]))); N = len(rows); last = N + 1
FIELDS = list(rows[0].keys()); COL = {f: L(i + 1) for i, f in enumerate(FIELDS)}
NUMERIC = {"payments_made", "original_balance", "current_balance", "monthly_payment", "original_term_months",
           "remaining_term_months", "current_rate", "tracker_margin", "original_valuation", "borrower_count",
           "gross_income", "months_in_arrears"}
def head(ws, r, names):
    for j, h in enumerate(names, 1):
        c = ws.cell(r, j, h); c.font = hdr; c.fill = fill
wb = Workbook(); nt = wb.active; nt.title = "Notes"
nt["A1"] = "Chapter 7 - the loan tape, the data dictionary and the UK RRE template"; nt["A1"].font = title
for i, n in enumerate([
    "Tape: the Thames cut-off tape, one row per loan (yellow = inputs). Dates are stored as text (YYYY-MM-DD), as in the CSV file.",
    "Dictionary: one row per tape field; Blanks and Invalid are formulas over the whole tape.",
    "FieldMap: 41 template fields mapped to the tape (direct, transformed, derived, gap).",
    "Extract: the template-style extract for the ten loans typed in column A (yellow).",
    "Lists: allowed values of the list fields and the code tables used by the extract.",
    "The LEI in Lists!B2 is fictional."], start=3):
    nt.cell(i, 1, n)
nt.column_dimensions["A"].width = 110
# ---- Tape
tp = wb.create_sheet("Tape"); head(tp, 1, FIELDS)
for i, r in enumerate(rows, start=2):
    for j, f in enumerate(FIELDS, 1):
        v = r[f]
        if v == "": v = None
        elif f in NUMERIC: v = float(v) if "." in v else int(v)
        c = tp.cell(i, j, v); c.fill = inp
tp.freeze_panes = "B2"
# ---- Lists
ls = wb.create_sheet("Lists")
ls["A1"] = "Reporting entity LEI (fictional)"; ls["B2"] = "KBS0FICTIONAL0LEI027"; ls["B2"].fill = inp
LISTS = {"repayment_type": ["Repayment", "Interest-only", "Part and part"],
         "product_type": ["2Y Fixed", "5Y Fixed", "Tracker", "SVR"],
         "region": ["London", "South East", "East of England", "South West", "West Midlands", "East Midlands",
                    "Yorkshire and the Humber", "North West", "North East", "Wales", "Scotland", "Northern Ireland"],
         "property_type": ["Detached", "Semi-detached", "Terraced", "Flat", "Bungalow"],
         "occupancy": ["Owner-occupied"], "first_time_buyer": ["Y", "N"],
         "employment_status": ["Employed", "Self-employed", "Retired"]}
LCOL = {}
for k, (f, vals) in enumerate(LISTS.items()):
    c = L(k + 1); LCOL[f] = f"Lists!${c}$5:${c}${4 + len(vals)}"
    x = ls.cell(4, k + 1, f); x.font = hdr; x.fill = fill
    for i, v in enumerate(vals): ls.cell(5 + i, k + 1, v).fill = inp
    ls.column_dimensions[c].width = 22
CODES = {"emp": [("Employed", "EMUK"), ("Self-employed", "SFEM"), ("Retired", "PNNR")],
         "amort": [("Repayment", "FRXX"), ("Interest-only", "BLLT"), ("Part and part", "OTHR")],
         "prop": [("Detached", "RHOS"), ("Semi-detached", "RHOS"), ("Terraced", "RTHS"), ("Flat", "RFLT"),
                  ("Bungalow", "RBGL")],
         "occ": [("Owner-occupied", "FOWN")]}
CRNG = {}; r0 = 20
for k, (name, pairs) in enumerate(CODES.items()):
    c1, c2 = L(2 * k + 1), L(2 * k + 2)
    ls.cell(r0, 2 * k + 1, f"{name}: tape value").font = hdr; ls.cell(r0, 2 * k + 1).fill = fill
    ls.cell(r0, 2 * k + 2, "template code").font = hdr; ls.cell(r0, 2 * k + 2).fill = fill
    for i, (a, b) in enumerate(pairs):
        ls.cell(r0 + 1 + i, 2 * k + 1, a).fill = inp; ls.cell(r0 + 1 + i, 2 * k + 2, b).fill = inp
    CRNG[name] = f"Lists!${c1}${r0+1}:${c2}${r0+len(pairs)}"
# ---- Dictionary
dc = wb.create_sheet("Dictionary", 1)
dc["A1"] = "Data dictionary checks on the whole tape"; dc["A1"].font = title
head(dc, 3, ["Field", "Type", "Rule", "Optional", "Blanks", "Invalid"])
INTS = {"payments_made": (0, 480), "original_term_months": (60, 480), "remaining_term_months": (1, 480),
        "original_valuation": (10000, 10000000), "borrower_count": (1, 4), "gross_income": (1, 10000000),
        "months_in_arrears": (0, 99)}
RATES = {"current_rate": (0.01, 15), "tracker_margin": (-5, 5)}
DATES = ["origination_date", "first_payment_date", "fixed_rate_end_date", "cut_off_date"]
MONEY = ["original_balance", "current_balance", "monthly_payment"]
OPTIONAL = ["fixed_rate_end_date", "tracker_margin"]
for i, f in enumerate(FIELDS, start=4):
    R = f"Tape!{COL[f]}2:{COL[f]}{last}"
    if f == "loan_id":
        typ, rule = "Identifier", "KBS- + 6 digits, unique"
        inv = (f'=SUMPRODUCT(((LEFT({R},4)<>"KBS-")+(LEN({R})<>10)+ISERROR(VALUE(MID({R},5,6)))'
               f'+(COUNTIF({R},{R})>1)>0)*1)')
    elif f in LISTS:
        typ, rule = "List", "value in Lists sheet"
        inv = f'=SUMPRODUCT(({R}<>"")*(COUNTIF({LCOL[f]},{R})=0))'
    elif f in DATES:
        typ, rule = "Date", "YYYY-MM-DD, real date"
        inv = f'=SUMPRODUCT(({R}<>"")*((ISERROR(DATEVALUE({R}))+(LEN({R})<>10))>0))'
    elif f in INTS:
        lo, hi = INTS[f]; typ, rule = "Integer", f"whole number {lo} to {hi}"
        inv = f'=SUMPRODUCT(({R}<>"")*((({R}<>INT({R}))+({R}<{lo})+({R}>{hi}))>0))'
    elif f in MONEY:
        typ, rule = "Money (GBP)", "> 0, whole pence"
        inv = f'=SUMPRODUCT(({R}<>"")*((({R}<=0)+(ROUND({R}*100,6)<>INT(ROUND({R}*100,6))))>0))'
    elif f in RATES:
        lo, hi = RATES[f]; typ, rule = "Percentage", f"{lo} to {hi} (% p.a.)"
        inv = f'=SUMPRODUCT(({R}<>"")*((({R}<{lo})+({R}>{hi}))>0))'
    dc.cell(i, 1, f); dc.cell(i, 2, typ); dc.cell(i, 3, rule)
    dc.cell(i, 4, "Y" if f in OPTIONAL else "N")
    dc.cell(i, 5, f"=COUNTBLANK({R})"); dc.cell(i, 6, inv)
end = 3 + len(FIELDS)
dc.cell(end + 2, 1, "Blanks in required fields"); dc.cell(end + 2, 6, f'=SUMIF(D4:D{end},"N",E4:E{end})')
dc.cell(end + 3, 1, "Values outside the dictionary"); dc.cell(end + 3, 6, f"=SUM(F4:F{end})+F{end+2}")
for c, w in zip("ABCDEF", (24, 13, 26, 9, 9, 9)): dc.column_dimensions[c].width = w
# ---- FieldMap
MAPROWS = [
 ("RREL1","Unique Identifier","LEI + N + 2027 + 01","derived"),
 ("RREL2","Original Underlying Exposure Identifier","loan_id","direct"),
 ("RREL4","Original Obligor Identifier","not on tape: core system","gap"),
 ("RREL6","Data Cut-Off Date","cut_off_date","direct"),
 ("RREL11","Geographic Region - Obligor","not on tape: NUTS3 from postcode","gap"),
 ("RREL13","Employment Status","employment_status -> code","transformed"),
 ("RREL16","Primary Income","gross_income if one borrower, else ND3","transformed"),
 ("RREL17","Primary Income Type","GRAN (gross annual income)","derived"),
 ("RREL19","Primary Income Verification","not on tape: underwriting system","gap"),
 ("RREL23","Origination Date","origination_date","direct"),
 ("RREL24","Maturity Date","origination_date + original term","derived"),
 ("RREL25","Original Term","original_term_months","direct"),
 ("RREL27","Purpose","not on tape: application system","gap"),
 ("RREL28","Currency Denomination","GBP","derived"),
 ("RREL29","Original Principal Balance","original_balance","direct"),
 ("RREL30","Current Principal Balance","current_balance","direct"),
 ("RREL35","Amortisation Type","repayment_type -> code","transformed"),
 ("RREL37","Scheduled Principal Payment Frequency","MNTH","derived"),
 ("RREL38","Scheduled Interest Payment Frequency","MNTH","derived"),
 ("RREL39","Payment Due","monthly_payment","direct"),
 ("RREL42","Interest Rate Type","product_type -> FLCF / FLIF","transformed"),
 ("RREL43","Current Interest Rate","current_rate","direct"),
 ("RREL44","Current Interest Rate Index","product_type -> BOER / LDOR / ND5","transformed"),
 ("RREL46","Current Interest Rate Margin","tracker_margin; SVR 0.00; fixed ND5","transformed"),
 ("RREL51","Interest Revision Date 1","fixed_rate_end_date; else ND5","transformed"),
 ("RREL58","Number Of Payments Before Securitisation","payments_made","direct"),
 ("RREL67","Arrears Balance","not on tape: servicing system","gap"),
 ("RREL68","Number Of Days In Arrears","not on tape: servicing system","gap"),
 ("RREL69","Account Status","months_in_arrears -> PERF / ARRE","transformed"),
 ("RREC6","Geographic Region - Collateral","not on tape: NUTS3 from postcode","gap"),
 ("RREC7","Occupancy Type","occupancy -> FOWN","transformed"),
 ("RREC9","Property Type","property_type -> code","transformed"),
 ("RREC12","Current Loan-To-Value","not on tape: needs indexed value","gap"),
 ("RREC13","Current Valuation Amount","not on tape: indexation","gap"),
 ("RREC14","Current Valuation Method","not on tape: indexation (IDXD)","gap"),
 ("RREC15","Current Valuation Date","not on tape: indexation","gap"),
 ("RREC16","Original Loan-To-Value","original_balance / original_valuation","derived"),
 ("RREC17","Original Valuation Amount","original_valuation","direct"),
 ("RREC18","Original Valuation Method","not on tape: valuation system","gap"),
 ("RREC19","Original Valuation Date","not on tape: valuation system","gap"),
 ("RREC22","Collateral Currency","GBP","derived")]
fm = wb.create_sheet("FieldMap", 2)
fm["A1"] = "Field map: Kingsbridge tape -> UK residential real estate template"; fm["A1"].font = title
head(fm, 3, ["Code", "Template field", "Kingsbridge source / rule", "Category"])
for i, row in enumerate(MAPROWS, start=4):
    for j, v in enumerate(row, 1): fm.cell(i, j, v)
e = 3 + len(MAPROWS)
for k, cat in enumerate(["direct", "transformed", "derived", "gap"]):
    fm.cell(e + 2 + k, 2, cat); fm.cell(e + 2 + k, 4, f'=COUNTIF(D4:D{e},B{e+2+k})')
fm.cell(e + 6, 2, "total"); fm.cell(e + 6, 4, f"=SUM(D{e+2}:D{e+5})")
for c, w in zip("ABCD", (9, 40, 42, 12)): fm.column_dimensions[c].width = w
# ---- Extract
ex = wb.create_sheet("Extract", 3)
OUTF = ["RREL1","RREL2","RREL6","RREL13","RREL16","RREL17","RREL23","RREL24","RREL25","RREL28","RREL29",
        "RREL30","RREL35","RREL37","RREL39","RREL42","RREL43","RREL44","RREL46","RREL51","RREL58","RREL69",
        "RREC7","RREC9","RREC16","RREC17"]
head(ex, 1, ["loan (input)", "tape row"] + OUTF)
LOANS = ["KBS-000001","KBS-000002","KBS-000003","KBS-000004","KBS-000005","KBS-000006",
         "KBS-000012","KBS-000042","KBS-000059","KBS-000417"]
for i, lid in enumerate(LOANS, start=2):
    ex.cell(i, 1, lid).fill = inp
    ex.cell(i, 2, f"=MATCH(A{i},Tape!$A:$A,0)")
    g = lambda f: f"INDEX(Tape!${COL[f]}:${COL[f]},$B{i})"
    fixed = f'OR({g("product_type")}="2Y Fixed",{g("product_type")}="5Y Fixed")'
    F = {"RREL1": '=Lists!$B$2&"N202701"', "RREL2": f"={g('loan_id')}", "RREL6": f"={g('cut_off_date')}",
         "RREL13": f"=VLOOKUP({g('employment_status')},{CRNG['emp']},2,0)",
         "RREL16": f'=IF({g("borrower_count")}=1,TEXT({g("gross_income")},"0.00"),"ND3")',
         "RREL17": '="GRAN"', "RREL23": f"={g('origination_date')}",
         "RREL24": f'=TEXT(EDATE(DATEVALUE({g("origination_date")}),{g("original_term_months")}),"yyyy-mm-dd")',
         "RREL25": f"={g('original_term_months')}", "RREL28": '="GBP"',
         "RREL29": f'=TEXT({g("original_balance")},"0.00")', "RREL30": f'=TEXT({g("current_balance")},"0.00")',
         "RREL35": f"=VLOOKUP({g('repayment_type')},{CRNG['amort']},2,0)", "RREL37": '="MNTH"',
         "RREL39": f'=TEXT({g("monthly_payment")},"0.00")',
         "RREL42": f'=IF({fixed},"FLCF","FLIF")', "RREL43": f'=TEXT({g("current_rate")},"0.00")',
         "RREL44": f'=IF({fixed},"ND5",IF({g("product_type")}="Tracker","BOER","LDOR"))',
         "RREL46": f'=IF({fixed},"ND5",IF({g("tracker_margin")}="","0.00",TEXT({g("tracker_margin")},"0.00")))',
         "RREL51": f'=IF({fixed},{g("fixed_rate_end_date")},"ND5")', "RREL58": f"={g('payments_made')}",
         "RREL69": f'=IF({g("months_in_arrears")}=0,"PERF","ARRE")',
         "RREC7": f"=VLOOKUP({g('occupancy')},{CRNG['occ']},2,0)",
         "RREC9": f"=VLOOKUP({g('property_type')},{CRNG['prop']},2,0)",
         "RREC16": f'=TEXT(ROUND(100*{g("original_balance")}/{g("original_valuation")},2),"0.00")',
         "RREC17": f'=TEXT({g("original_valuation")},"0.00")'}
    for j, f in enumerate(OUTF, start=3): ex.cell(i, j, F[f])
for j in range(1, len(OUTF) + 3): ex.column_dimensions[L(j)].width = 13
ex.column_dimensions["C"].width = 30
wb.save(sys.argv[2]); print("saved", sys.argv[2])
