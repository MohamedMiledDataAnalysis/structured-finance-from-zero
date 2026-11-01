"""Build ch13/excel/ch13_waterfall.xlsx: the Thames pre-enforcement waterfall (one sheet per ILLUSTRATIVE quarter)
and a post-enforcement sheet, all with live formulas. Same conventions as ch13/python/waterfall.py.
Run from the book folder:
  python3 tools/build_ch13_xlsx.py data/ch13_illustrative_scenarios.csv ch13/excel/ch13_waterfall.xlsx
The cell map used by tools/check_ch13.py is written to build/ch13_cellmap.json."""
import sys, csv, json
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
NAVY = "1F2A44"; hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6"); M = "#,##0.00"; bold = Font(bold=True, color=NAVY)
CL = ["A", "B", "C", "D", "E", "Z"]

def head(ws, row, labels, col=1):
    for j, h in enumerate(labels, col):
        c = ws.cell(row, j, h); c.font = hdr; c.fill = fill; c.alignment = Alignment(horizontal="center", wrap_text=True)

def put(ws, ref, val, fmt=M, yellow=False):
    c = ws[ref]; c.value = val; c.number_format = fmt
    if yellow: c.fill = inp
    return c

rows = list(csv.DictReader(open(sys.argv[1])))
wb = Workbook(); T = wb.active; T.title = "Terms"
T["A1"] = "Thames Residential 2027-1 - waterfall terms (Deal Fact Sheets, Appendix D)"; T["A1"].font = Font(bold=True, size=13, color=NAVY)
terms = [("Swap fixed rate paid (%)", 3.30, "0.00"), ("Trustee fee (£ p.a.)", 25000, M),
         ("Paying agent, agent bank (£ p.a.)", 10000, M), ("Corporate services (£ p.a.)", 20000, M),
         ("Cash manager (£ p.a.)", 50000, M), ("Servicing fee (% of pool p.a.)", 0.15, "0.00"),
         ("Other issuer expenses (£ p.a.)", 120000, M), ("Issuer profit (£ per IPD)", 1000, M),
         ("Reserve required while Class A outstanding (£)", 9391500, M), ("Reserve % of A-E after Class A", 1.50, "0.00"),
         ("Reserve floor (£)", 3000000, M), ("Subordinated loan margin (%)", 4.00, "0.00")]
for i, (lab, v, f) in enumerate(terms, 3):
    T.cell(i, 1, lab); put(T, f"B{i}", v, f, True)
# B3 swap, B4 trustee, B5 PA, B6 CSP, B7 CM, B8 servicing %, B9 other, B10 profit, B11 req, B12 pct, B13 floor, B14 sub margin
head(T, 17, ["Class", "Margin (%)"])
for i, (c, mg) in enumerate(zip(CL[:5], [0.62, 1.10, 1.50, 2.20, 3.50]), 18):
    T.cell(i, 1, c); put(T, f"B{i}", mg, "0.00", True)
T.cell(23, 1, "Z"); put(T, "B23", 0, "0.00"); T["C23"] = "Class Z pays no interest"
T.column_dimensions["A"].width = 46; T.column_dimensions["B"].width = 16
T["A25"] = "Yellow cells are inputs. Every other cell in this workbook is a formula."
cellmap = {}

def scenario_sheet(r):
    ws = wb.create_sheet(r["scenario"].capitalize()); cm = {}
    ws["A1"] = f"ILLUSTRATIVE {r['scenario']} quarter - pre-enforcement waterfall (not a real Thames IPD)"; ws["A1"].font = Font(bold=True, size=12, color=NAVY)
    ins = [("Days in interest period", "days", "0"), ("Compounded SONIA (%)", "sonia", "0.00"), ("Revenue collections (£)", "revenue", M),
           ("Scheduled principal (£)", "sched_principal", M), ("Prepayments (£)", "prepayments", M), ("Principal recoveries (£)", "recoveries", M),
           ("Realised losses (£)", "losses", M), ("Swap notional (£)", "swap_notional", M), ("Opening pool balance (£)", "pool", M),
           ("Opening reserve fund (£)", "reserve", M), ("Subordinated loan outstanding (£)", "subloan", M),
           ("Unpaid sub loan interest (£)", "subloan_unpaid_int", M), ("Other revenue (£)", None, M), ("Sub swap termination (£)", None, M)]
    for i, (lab, key, f) in enumerate(ins, 3):
        ws.cell(i, 1, lab); v = 0 if key is None else (int(r[key]) if key == "days" else float(r[key]))
        put(ws, f"B{i}", v, f, True)
    # B3 days B4 sonia B5 rev B6 sched B7 prepay B8 recov B9 loss B10 notional B11 pool B12 reserve B13 sub B14 subunpaid B15 other B16 subswap
    head(ws, 18, ["Class", "Opening note", "Opening PDL", "Opening deferred", "Coupon (%)", "Interest due", "PDL room", "PDL debit", "PDL before cure"])
    for i, c in enumerate(CL):
        rr = 19 + i
        ws.cell(rr, 1, c)
        put(ws, f"B{rr}", float(r[f"note_{c}"]), M, True); put(ws, f"C{rr}", float(r[f"pdl_{c}"]), M, True)
        put(ws, f"D{rr}", float(r.get(f"def_{c}", 0) or 0), M, c != "Z")
        put(ws, f"E{rr}", f"=IF(A{rr}=\"Z\",0,$B$4+Terms!B{18 + i})", "0.00")
        put(ws, f"F{rr}", f"=IF(A{rr}=\"Z\",0,ROUND(B{rr}*E{rr}/100*$B$3/365,2)+D{rr}+ROUND(D{rr}*E{rr}/100*$B$3/365,2))")
        put(ws, f"G{rr}", f"=MAX(0,B{rr}-C{rr})")
        put(ws, f"H{rr}", f"=MIN(G{rr},$B$43)" if c == "Z" else f"=MIN(G{rr},$B$43-SUM(H{rr + 1}:H$24))")
        put(ws, f"I{rr}", f"=C{rr}+H{rr}")
    calc = [(27, "Swap net (+ issuer pays)", "=ROUND(B10*(Terms!B3-B4)/100*B3/365,2)"),
            (28, "Swap net payment", "=MAX(B27,0)"), (29, "Swap net receipt", "=MAX(-B27,0)"),
            (30, "Principal receipts", "=B6+B7+B8"), (31, "Available revenue receipts", "=B5+B29+B15+B12"),
            (32, "Trustee fees due", "=ROUND(Terms!B4*B3/365,2)"), (33, "Paying agent, agent bank due", "=ROUND(Terms!B5*B3/365,2)"),
            (34, "Corporate services due", "=ROUND(Terms!B6*B3/365,2)"), (35, "Cash manager due", "=ROUND(Terms!B7*B3/365,2)"),
            (36, "Servicer due", "=ROUND(B11*Terms!B8/100*B3/365,2)"), (37, "Other issuer expenses due", "=ROUND(Terms!B9*B3/365,2)"),
            (38, "Item (2) total due", "=SUM(B33:B37)"),
            (39, "Most senior class outstanding", '=IF(B19>0,"A",IF(B20>0,"B",IF(B21>0,"C",IF(B22>0,"D",IF(B23>0,"E","Z")))))'),
            (40, "Interest covered by PAA", '=IF(B39="A",F19,IF(B39="B",F20,0))'),
            (41, "Items (1)-(4) + that interest", "=B32+B38+Terms!B10+B28+B40"),
            (42, "Principal addition amounts", "=MIN(MAX(B41-B31,0),B30)"),
            (43, "PDL debit: losses + PAA", "=B9+B42"),
            (44, "Reserve required amount", "=IF(B19>0,Terms!B11,MAX(ROUND(SUM(B19:B23)*Terms!B12/100,2),Terms!B13))"),
            (45, "Sub loan interest due", "=ROUND(B13*(B4+Terms!B14)/100*B3/365,2)+B14")]
    for rr, lab, f in calc:
        ws.cell(rr, 1, lab); put(ws, f"B{rr}", f, "@" if rr == 39 else M)
    cm.update(arr="B31", paa="B42", swap_rec="B29")
    head(ws, 48, ["Item", "Revenue priority of payments", "Due", "Paid", "Remaining"])
    ws["A47"] = "Funds at start (ARR + PAA)"; put(ws, "E47", "=B31+B42")
    items = [("1", "Trustee fees", "=B32"), ("2", "Paying agent, agent bank", "=B33"), ("2", "Corporate services", "=B34"),
             ("2", "Cash manager", "=B35"), ("2", "Servicer", "=B36"), ("2", "Other issuer expenses", "=B37"),
             ("3", "Issuer profit", "=Terms!B10"), ("4", "Swap net payment", "=B28")]
    for i, c in enumerate(CL[:5]):
        items += [(str(5 + 2 * i), f"Class {c} interest", f"=F{19 + i}"), (str(6 + 2 * i), f"Class {c} PDL", f"=I{19 + i}")]
    items += [("15", "General reserve fund", "=B44"), ("16", "Class Z PDL", "=I24"), ("17", "Sub swap termination", "=B16"),
              ("18", "Sub loan interest", "=B45"), ("18", "Sub loan principal", "=B13"), ("19", "Deferred consideration", None)]
    first = 49; lines = []
    ws["G48"] = "Item (2) paid in total"; ws["G48"].font = bold
    for k, (it, lab, due) in enumerate(items):
        rr = first + k; prev = f"E{rr - 1}" if k else "E47"
        ws.cell(rr, 1, it); ws.cell(rr, 2, lab)
        if due is None:
            put(ws, f"C{rr}", f"=MAX({prev},0)"); put(ws, f"D{rr}", f"=C{rr}")
        elif it == "2":
            put(ws, f"C{rr}", due)
            put(ws, f"D{rr}", f"=IF($G$49=$B$38,C{rr},ROUND(C{rr}*$G$49/$B$38,2))")
        else:
            put(ws, f"C{rr}", due); put(ws, f"D{rr}", f"=MIN(C{rr},MAX({prev},0))")
        put(ws, f"E{rr}", f"={prev}-D{rr}")
        lines.append((it, lab, rr))
    put(ws, "G49", f"=MIN(B38,E{first})")   # funds after item (1)
    cm["lines"] = lines
    row = {lab: rr for _, lab, rr in lines}
    pr = first + len(items) + 2
    head(ws, pr, ["", "Principal priority of payments", "Due", "Paid", "Remaining"])
    credits = "+".join(f"D{row[f'Class {c} PDL']}" for c in CL)
    ws.cell(pr + 1, 2, "Available principal"); put(ws, f"E{pr + 1}", f"=B30-B42+{credits}")
    ws.cell(pr + 2, 2, "Principal addition amounts (memo)"); put(ws, f"D{pr + 2}", "=B42")
    plines = [("Principal addition amounts", f"D{pr + 2}")]
    prev = f"E{pr + 1}"
    for i, c in enumerate(CL):
        rr = pr + 3 + i
        ws.cell(rr, 2, f"Class {c} principal"); put(ws, f"C{rr}", f"=B{19 + i}")
        put(ws, f"D{rr}", f"=MIN(C{rr},MAX({prev},0))"); put(ws, f"E{rr}", f"={prev}-D{rr}")
        prev = f"E{rr}"; plines.append((f"Class {c} principal", f"D{rr}"))
    cm["principal"] = plines
    cr = pr + 11
    head(ws, cr, ["Class", "Closing note", "Closing PDL", "Deferred interest", "Interest shortfall"])
    for i, c in enumerate(CL):
        rr = cr + 1 + i
        ws.cell(rr, 1, c)
        put(ws, f"B{rr}", f"=B{19 + i}-D{pr + 3 + i}")
        put(ws, f"C{rr}", f"=I{19 + i}-D{row[f'Class {c} PDL']}")
        if c == "Z":
            put(ws, f"D{rr}", 0); put(ws, f"E{rr}", 0)
        else:
            put(ws, f"D{rr}", f"=F{19 + i}-D{row[f'Class {c} interest']}"); put(ws, f"E{rr}", f"=D{rr}")
    s0 = cr + 8
    summ = [("Reserve fund after the IPD", f"=D{row['General reserve fund']}"), ("Reserve draw (+) / top-up (-)", f"=B12-B{s0}"),
            ("Sub loan outstanding", f"=B13-D{row['Sub loan principal']}"), ("Pool balance after the period", "=B11-B30-B9"),
            ("Check: notes - PDL - pool (0)", f"=SUM(B{cr + 1}:B{cr + 6})-SUM(C{cr + 1}:C{cr + 6})-B{s0 + 3}"),
            ("Senior interest unpaid (EoD)", f'=INDEX(E{cr + 1}:E{cr + 6},MATCH(B39,A{cr + 1}:A{cr + 6},0))>0')]
    for k, (lab, f) in enumerate(summ):
        ws.cell(s0 + k, 1, lab); put(ws, f"B{s0 + k}", f, "General" if k == 5 else M)
    cm.update(closing_first=cr + 1, reserve=f"B{s0}", draw=f"B{s0 + 1}", pool=f"B{s0 + 3}", check=f"B{s0 + 4}", eod=f"B{s0 + 5}")
    ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 32
    for col in "CDEFGHI": ws.column_dimensions[col].width = 17
    ws.freeze_panes = "A3"
    cellmap[ws.title] = cm

for r in rows:
    scenario_sheet(r)

# post-enforcement sheet for the severe scenario (inputs taken from the Severe sheet)
P = wb.create_sheet("PostEnforcement")
P["A1"] = "ILLUSTRATIVE severe quarter - post-enforcement priority of payments (one combined pot)"; P["A1"].font = Font(bold=True, size=12, color=NAVY)
P["A3"] = "All receipts and reserve"; put(P, "E3", "=Severe!B5+Severe!B15+Severe!B30+Severe!B29+Severe!B12")
head(P, 4, ["", "Post-enforcement", "Due", "Paid", "Remaining"])
pe = [("Trustee fees", "=Severe!B32")] + [(lab, f"=Severe!B{33 + i}") for i, lab in enumerate(
    ["Paying agent, agent bank", "Corporate services", "Cash manager", "Servicer", "Other issuer expenses"])] + [("Swap net payment", "=Severe!B28")]
for i, c in enumerate(CL[:5]):
    pe += [(f"Class {c} interest", f"=Severe!F{19 + i}"), (f"Class {c} principal", f"=Severe!B{19 + i}")]
pe += [("Class Z principal", "=Severe!B24"), ("Sub swap termination", "=Severe!B16"), ("Sub loan interest", "=Severe!B45"),
       ("Sub loan principal", "=Severe!B13"), ("Deferred consideration", None)]
P["G4"] = "Senior expenses paid in total"; put(P, "G5", "=MIN(Severe!B38,E5)")
plist = []
for k, (lab, due) in enumerate(pe):
    rr = 5 + k; prev = f"E{rr - 1}" if k else "E3"
    P.cell(rr, 2, lab)
    if due is None:
        put(P, f"C{rr}", f"=MAX({prev},0)"); put(P, f"D{rr}", f"=C{rr}")
    elif 1 <= k <= 5:
        put(P, f"C{rr}", due); put(P, f"D{rr}", f"=IF($G$5=Severe!$B$38,C{rr},ROUND(C{rr}*$G$5/Severe!$B$38,2))")
    else:
        put(P, f"C{rr}", due); put(P, f"D{rr}", f"=MIN(C{rr},MAX({prev},0))")
    put(P, f"E{rr}", f"={prev}-D{rr}")
    plist.append((lab, rr))
P["G5"] = "=MIN(Severe!B38,E5)"
P.column_dimensions["B"].width = 30
for col in "CDEG": P.column_dimensions[col].width = 18
cellmap["PostEnforcement"] = {"lines": plist, "pot": "E3"}
wb.save(sys.argv[2])
json.dump(cellmap, open("build/ch13_cellmap.json", "w"), indent=1)
print("saved", sys.argv[2])
