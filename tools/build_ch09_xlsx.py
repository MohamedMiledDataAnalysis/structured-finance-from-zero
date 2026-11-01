"""Build ch09/excel/ch09_pool_selection.xlsx (live formulas).
Run: python3 tools/build_ch09_xlsx.py data/ch09_thames_provisional_pool.csv ch09/excel/ch09_pool_selection.xlsx"""
import sys, csv
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L

NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
title = Font(bold=True, size=13, color=NAVY)
rows = list(csv.DictReader(open(sys.argv[1])))
N = len(rows); LAST = N + 1

wb = Workbook()
# ---------------- Notes
nt = wb.active; nt.title = "Notes"
nt["A1"] = "Chapter 9 - Thames Residential 2027-1: eligibility, pool cut, stratification"; nt["A1"].font = title
for i, t in enumerate([
    "Pool: Kingsbridge provisional pool at the cut-off date 31 January 2027 (data, one row per loan).",
    "Criteria: yellow cells are the eligibility thresholds and permitted lists. Change them and every sheet updates.",
    "Pool columns S to AC test each criterion (TRUE = passes). AD = eligible (all TRUE). AE = first criterion failed (0 = none).",
    "PoolCut: removal waterfall in the order of the mortgage sale agreement.",
    "Strats: bands are (lower, upper], i.e. above the lower bound and up to and including the upper bound.",
    "Percentages are rounded to 2 decimals with ROUND (halves away from zero).",
    "LTV = balance / original valuation (not indexed). Seasoning = payments made (months)."], start=3):
    nt.cell(i, 1, t)
nt.column_dimensions["A"].width = 110

# ---------------- Criteria
cr = wb.create_sheet("Criteria")
cr["A1"] = "Eligibility thresholds (inputs)"; cr["A1"].font = title
th = [("Maximum original LTV", 0.95, "0.00%"), ("Minimum current balance (£)", 25000, "#,##0.00"),
      ("Maximum current balance (£)", 1000000, "#,##0.00"), ("Maximum original term (months)", 420, "0"),
      ("Minimum payments made", 1, "0"), ("Maximum months in arrears", 1, "0"),
      ("Required occupancy", "Owner-occupied", "@")]
for i, (lab, v, fmt) in enumerate(th, start=3):
    cr.cell(i, 1, lab); c = cr.cell(i, 2, v); c.fill = inp; c.number_format = fmt
cr["A12"] = "Permitted regions"; cr["A12"].font = Font(bold=True, color=NAVY)
regions = ["London","South East","East of England","South West","West Midlands","East Midlands",
           "Yorkshire and the Humber","North West","North East","Wales","Scotland","Northern Ireland"]
for i, r in enumerate(regions, start=13): cr.cell(i, 1, r).fill = inp           # A13:A24
cr["C12"] = "Permitted products"; cr["C12"].font = Font(bold=True, color=NAVY)
for i, p in enumerate(["2Y Fixed","5Y Fixed","Tracker","SVR"], start=13): cr.cell(i, 3, p).fill = inp  # C13:C16
cr.column_dimensions["A"].width = 32; cr.column_dimensions["B"].width = 16; cr.column_dimensions["C"].width = 18

# ---------------- Pool
po = wb.create_sheet("Pool")
cols = ["loan_id","current_balance","original_balance","original_valuation","original_term_months",
        "remaining_term_months","payments_made","product_type","current_rate","region","occupancy",
        "repayment_type","employment_status","first_time_buyer","months_in_arrears","shared_ownership",
        "forbearance_flag","further_advance_pending"]                       # A..R
num = {"current_balance","original_balance","original_valuation","original_term_months",
       "remaining_term_months","payments_made","current_rate","months_in_arrears"}
calc = ["original_ltv","current_ltv","E1 UK","E2 Owner-occ","E3 Not SO","E4 Product","E5 LTV",
        "E6 Balance","E7 Term","E8 Payment","E9 Arrears","E10 Forbear","E11 FA","eligible","first_fail",
        "eligible_balance"]                                                  # S..AH
heads = cols + calc
for j, h in enumerate(heads, 1):
    c = po.cell(1, j, h); c.font = hdr; c.fill = fill
for i, r in enumerate(rows, start=2):
    for j, h in enumerate(cols, 1):
        v = r[h]
        po.cell(i, j, float(v) if h in num and "." in v else int(v) if h in num else v)
    po.cell(i, 2).number_format = "#,##0.00"
    po[f"S{i}"] = f"=C{i}/D{i}"; po[f"T{i}"] = f"=B{i}/D{i}"
    po[f"U{i}"] = f"=COUNTIF(Criteria!$A$13:$A$24,J{i})>0"
    po[f"V{i}"] = f"=K{i}=Criteria!$B$9"
    po[f"W{i}"] = f'=P{i}="N"'
    po[f"X{i}"] = f"=COUNTIF(Criteria!$C$13:$C$16,H{i})>0"
    po[f"Y{i}"] = f"=S{i}<=Criteria!$B$3"
    po[f"Z{i}"] = f"=AND(B{i}>=Criteria!$B$4,B{i}<=Criteria!$B$5)"
    po[f"AA{i}"] = f"=E{i}<=Criteria!$B$6"
    po[f"AB{i}"] = f"=G{i}>=Criteria!$B$7"
    po[f"AC{i}"] = f"=O{i}<=Criteria!$B$8"
    po[f"AD{i}"] = f'=Q{i}="N"'
    po[f"AE{i}"] = f'=R{i}="N"'
    po[f"AF{i}"] = f"=AND(U{i}:AE{i})"
    po[f"AG{i}"] = f"=IFERROR(MATCH(FALSE,U{i}:AE{i},0),0)"
    po[f"AH{i}"] = f"=IF(AF{i},B{i},0)"
    po[f"S{i}"].number_format = po[f"T{i}"].number_format = "0.00%"
po.freeze_panes = "B2"
for j in range(1, len(heads) + 1): po.column_dimensions[L(j)].width = 13
R = lambda col: f"Pool!${col}$2:${col}${LAST}"

# ---------------- PoolCut
pc = wb.create_sheet("PoolCut")
pc["A1"] = "Pool cut: criteria applied in order (removal waterfall)"; pc["A1"].font = title
for j, h in enumerate(["Step","Criterion","Loans failing","Loans removed","Balance removed (£)",
                       "Loans remaining","Balance remaining (£)"], 1):
    c = pc.cell(3, j, h); c.font = hdr; c.fill = fill
pc["B4"] = "Provisional pool"; pc["F4"] = f"=COUNTA({R('A')})"; pc["G4"] = f"=ROUND(SUM({R('B')}),2)"
names = ["Property in the UK","Owner-occupied","Not shared ownership","Permitted product",
         "Original LTV <= 95%","Balance £25,000 to £1,000,000","Original term <= 420 months",
         "At least one payment made","Arrears <= 1 month","No forbearance in place","No further advance pending"]
tcols = ["U","V","W","X","Y","Z","AA","AB","AC","AD","AE"]
for k, (nm, tc) in enumerate(zip(names, tcols), start=1):
    r = k + 4
    pc.cell(r, 1, f"E{k}"); pc.cell(r, 2, nm)
    pc.cell(r, 3, f"=COUNTIF({R(tc)},FALSE)")
    pc.cell(r, 4, f"=COUNTIF({R('AG')},{k})")
    pc.cell(r, 5, f"=ROUND(SUMIF({R('AG')},{k},{R('B')}),2)")
    pc.cell(r, 6, f"=F{r-1}-D{r}")
    pc.cell(r, 7, f"=ROUND(G{r-1}-E{r},2)")
pc["B16"] = "Final pool (check)"; pc["F16"] = f"=COUNTIF({R('AF')},TRUE)"; pc["G16"] = f"=ROUND(SUM({R('AH')}),2)"
pc["B17"] = "Difference from waterfall (must be 0)"; pc["F17"] = "=F16-F15"; pc["G17"] = "=ROUND(G16-G15,2)"
for r in range(4, 18):
    for c in ("E", "G"): pc[f"{c}{r}"].number_format = "#,##0.00"
for c, w in zip("ABCDEFG", [7, 32, 13, 13, 18, 15, 20]): pc.column_dimensions[c].width = w

# ---------------- Strats
st = wb.create_sheet("Strats")
st["A1"] = "Stratification tables of the final pool (eligible loans only)"; st["A1"].font = title
st["A2"] = "Total loans"; st["B2"] = f"=COUNTIF({R('AF')},TRUE)"
st["A3"] = "Total balance (£)"; st["B3"] = f"=ROUND(SUM({R('AH')}),2)"; st["B3"].number_format = "#,##0.00"
ELIG = R("AF")
banded = [("Current balance", "B", [0,1e5,2e5,3e5,4e5,5e5,7.5e5,1e6],
           ["0-100k","100k-200k","200k-300k","300k-400k","400k-500k","500k-750k","750k-1,000k"]),
          ("Original LTV", "S", [0,.5,.6,.7,.75,.8,.85,.9,.95],
           ["<=50%","50-60%","60-70%","70-75%","75-80%","80-85%","85-90%","90-95%"]),
          ("Current LTV", "T", [0,.5,.6,.7,.75,.8,.85,.9,.95],
           ["<=50%","50-60%","60-70%","70-75%","75-80%","80-85%","85-90%","90-95%"]),
          ("Interest rate", "I", [0,3.5,4.0,4.5,5.0,5.5,99],
           ["<=3.50%","3.50-4.00%","4.00-4.50%","4.50-5.00%","5.00-5.50%",">5.50%"]),
          ("Seasoning", "G", [-1,12,24,36,48,60], ["0-12m","12-24m","24-36m","36-48m","48-60m"]),
          ("Remaining term", "F", [0,180,240,300,360,420], ["<=15y","15-20y","20-25y","25-30y","30-35y"])]
cats = [("Region", "J", regions), ("Product type", "H", ["2Y Fixed","5Y Fixed","Tracker","SVR"]),
        ("Repayment type", "L", ["Repayment","Interest-only","Part and part"]),
        ("Employment", "M", ["Employed","Self-employed","Retired"]),
        ("First-time buyer", "N", ["Y","N"]), ("Months in arrears", "O", [0, 1])]
order = ["Current balance","Original LTV","Current LTV","Region","Product type","Interest rate",
         "Seasoning","Remaining term","Repayment type","Employment","First-time buyer","Months in arrears"]
spec = {t: ("band", c, e, l) for t, c, e, l in banded}
spec.update({t: ("cat", c, None, l) for t, c, l in cats})
r = 5
for tname in order:
    kind, col, edges, labels = spec[tname]
    st.cell(r, 1, tname).font = Font(bold=True, color=NAVY); r += 1
    for j, h in enumerate(["Band","Lower (excl.)","Upper (incl.)","Loans","% loans","Balance (£)","% balance"], 1):
        c = st.cell(r, j, h); c.font = hdr; c.fill = fill
    r += 1; first = r
    for k, lab in enumerate(labels):
        st.cell(r, 1, lab)
        if kind == "band":
            st.cell(r, 2, edges[k]).fill = inp; st.cell(r, 3, edges[k + 1]).fill = inp
            crit = f'{R(col)},">"&B{r},{R(col)},"<="&C{r}'
        else:
            crit = f"{R(col)},A{r}"
        st.cell(r, 4, f"=COUNTIFS({ELIG},TRUE,{crit})")
        st.cell(r, 5, f"=ROUND(D{r}/$B$2*100,2)")
        st.cell(r, 6, f"=ROUND(SUMIFS({R('B')},{ELIG},TRUE,{crit}),2)")
        st.cell(r, 7, f"=ROUND(F{r}/$B$3*100,2)")
        st.cell(r, 6).number_format = "#,##0.00"
        r += 1
    st.cell(r, 1, "Total"); st.cell(r, 4, f"=SUM(D{first}:D{r-1})"); st.cell(r, 6, f"=ROUND(SUM(F{first}:F{r-1}),2)")
    st.cell(r, 5, f"=SUM(E{first}:E{r-1})"); st.cell(r, 7, f"=SUM(G{first}:G{r-1})")
    st.cell(r, 6).number_format = "#,##0.00"
    for j in range(1, 8): st.cell(r, j).font = Font(bold=True)
    r += 2
for c, w in zip("ABCDEFG", [24, 13, 13, 9, 9, 18, 10]): st.column_dimensions[c].width = w

# ---------------- Summary
sm = wb.create_sheet("Summary")
sm["A1"] = "Pool summary: weighted averages (weights = current balance) and concentration"; sm["A1"].font = title
B, E = R("B"), R("AF")
items = [("Number of loans", "=Strats!B2", "#,##0"),
         ("Total current balance (£)", "=Strats!B3", "#,##0.00"),
         ("Average balance (£)", "=ROUND(B4/B3,2)", "#,##0.00"),
         ("Largest loan (£)", f"=MAX({R('AH')})", "#,##0.00"),
         ("WA original LTV (%)", f"=ROUND(SUMPRODUCT({R('AH')},{R('S')})/B4*100,2)", "0.00"),
         ("WA current LTV (%)", f"=ROUND(SUMPRODUCT({R('AH')},{R('T')})/B4*100,2)", "0.00"),
         ("WA interest rate (%)", f"=ROUND(SUMPRODUCT({R('AH')},{R('I')})/B4,2)", "0.00"),
         ("WA seasoning (months)", f"=ROUND(SUMPRODUCT({R('AH')},{R('G')})/B4,2)", "0.00"),
         ("WA remaining term (months)", f"=ROUND(SUMPRODUCT({R('AH')},{R('F')})/B4,2)", "0.00"),
         ("Top 10 loans (£)", f"=SUMPRODUCT(LARGE({R('AH')},{{1,2,3,4,5,6,7,8,9,10}}))", "#,##0.00"),
         ("Top 10 loans (% pool)", "=ROUND(B12/B4*100,2)", "0.00"),
         ("London (% pool)", f'=ROUND(SUMIFS({R("AH")},{R("J")},"London")/B4*100,2)', "0.00")]
for i, (lab, f, fmt) in enumerate(items, start=3):
    sm.cell(i, 1, lab); c = sm.cell(i, 2, f); c.number_format = fmt
sm.column_dimensions["A"].width = 30; sm.column_dimensions["B"].width = 18
wb.save(sys.argv[2])
print("saved", sys.argv[2])
