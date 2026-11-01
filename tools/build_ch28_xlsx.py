"""Build ch28/excel/ch28_class_a_pricing.xlsx (Chapter 28).
Run: python3 tools/build_ch28_xlsx.py ch28/excel/ch28_class_a_pricing.xlsx"""
import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
NAVY = "1F2A44"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
wb = Workbook(); ws = wb.active; ws.title = "Inputs"
ws["A1"] = "Chapter 28 - Thames Residential 2027-1 Class A pricing"; ws["A1"].font = Font(bold=True, size=13, color=NAVY)
items = [("Pool balance at cut-off (£)", 635671146.31, "#,##0.00"),        # B3
         ("Class A at closing (£)", 553000000, "#,##0.00"),                 # B4
         ("SONIA, flat (illustrative)", 0.0375, "0.00%"),                  # B5
         ("Class A margin", 0.0062, "0.00%"),                              # B6
         ("Scheduled amortisation per month", 0.002, "0.00%"),            # B7
         ("Settlement date (closing)", "=DATE(2027,3,18)", "dd/mm/yyyy"),  # B8
         ("DM 1", 0.0055, "0.00%"), ("DM 2", 0.0062, "0.00%"),            # B9, B10
         ("DM 3", 0.0070, "0.00%"), ("DM 4", 0.0080, "0.00%")]            # B11, B12
for i, (lab, val, fmt) in enumerate(items, start=3):
    ws.cell(i, 1, lab); c = ws.cell(i, 2, val); c.number_format = fmt
    if not str(val).startswith("="): c.fill = inp
ws.column_dimensions["A"].width = 34; ws.column_dimensions["B"].width = 18
ws["A13"] = "Lifetime defaults, Chapter 10 (£)"; ws["B13"] = 9273541; ws["B13"].fill = inp; ws["B13"].number_format = "#,##0.00"
ws["A17"] = "Recovery lag (months)"; ws["B17"] = 18; ws["B17"].fill = inp
ws["D2"] = "Year"; ws["E2"] = "Default timing %"
for y, sh in enumerate([5.73, 11.07, 23.34, 28.88, 19.09, 8.01, 2.70, 0.84, 0.26, 0.08], 1):
    ws.cell(2 + y, 4, y); c = ws.cell(2 + y, 5, sh); c.fill = inp; c.number_format = "0.00"
ws["A19"] = "Yellow cells are inputs. Every other cell is a formula."
ws["A20"] = "Assumptions: defaults return to the notes in full after the lag (recovery + loss cured by excess spread);"
ws["A21"] = "issuer call exercised on 15 March 2032; IPDs adjusted to the next business day."

DMS = ["Inputs!$B$9", "Inputs!$B$10", "Inputs!$B$11", "Inputs!$B$12"]
for cpr in (5, 11.15, 15, 20):
    s = wb.create_sheet(f"CPR {cpr}%")
    s["A1"] = "CPR"; s["B1"] = cpr / 100; s["B1"].fill = inp; s["B1"].number_format = "0.0%"
    s["C1"] = "SMM"; s["D1"] = "=1-(1-B1)^(1/12)"; s["D1"].number_format = "0.0000%"
    for j, h in enumerate(["Month", "Opening pool", "Scheduled", "Prepayment", "Closing pool", "Collected"], 1):
        c = s.cell(3, j, h); c.font = hdr; c.fill = fill; s.column_dimensions[chr(64 + j)].width = 15
    for k in range(61):
        r = 4 + k
        s.cell(r, 1, f"=DATE(2027,2+{k},1)").number_format = "mmm yyyy"
        s.cell(r, 2, "=Inputs!$B$3" if k == 0 else f"=E{r-1}")
        s.cell(r, 21, f"=ROUND(Inputs!$B$13*INDEX(Inputs!$E$3:$E$12,INT({k}/12)+1)/1200,2)").number_format = "#,##0.00"
        s.cell(r, 22, f"=IF({k}>=Inputs!$B$17,INDEX($U$4:$U$64,{k}+1-Inputs!$B$17),0)").number_format = "#,##0.00"
        s.cell(r, 3, f"=ROUND((B{r}-U{r})*Inputs!$B$7,2)")
        s.cell(r, 4, f"=ROUND((B{r}-U{r}-C{r})*$D$1,2)")
        s.cell(r, 5, f"=B{r}-U{r}-C{r}-D{r}")
        s.cell(r, 6, f"=C{r}+D{r}+V{r}")
        for j in range(2, 7): s.cell(r, j).number_format = "#,##0.00"
    heads = ["IPD", "Days", "Collections", "Class A open", "Interest", "Principal", "Cash flow", "Years",
             "DF 1", "DF 2", "DF 3", "DF 4"]
    for j, h in enumerate(heads):
        c = s.cell(3, 8 + j, h); c.font = hdr; c.fill = fill
        s.column_dimensions[c.column_letter].width = 14
    for n in range(20):
        r = 4 + n
        s[f"H{r}"] = f"=WORKDAY(EDATE(DATE(2027,6,15),{3*n})-1,1)"; s[f"H{r}"].number_format = "dd/mm/yyyy"
        s[f"I{r}"] = f"=H{r}-Inputs!$B$8" if n == 0 else f"=H{r}-H{r-1}"
        lo = "DATE(2027,2,1)" if n == 0 else f"DATE(YEAR(H{r-1}),MONTH(H{r-1}),1)"
        s[f"J{r}"] = f'=SUMIFS($F$4:$F$64,$A$4:$A$64,">="&{lo},$A$4:$A$64,"<"&DATE(YEAR(H{r}),MONTH(H{r}),1))'
        s[f"K{r}"] = "=Inputs!$B$4" if n == 0 else f"=K{r-1}-M{r-1}"
        s[f"L{r}"] = f"=ROUND(K{r}*(Inputs!$B$5+Inputs!$B$6)*I{r}/365,2)"
        s[f"M{r}"] = f"=K{r}" if n == 19 else f"=MIN(K{r},ROUND(J{r},2))"
        s[f"N{r}"] = f"=L{r}+M{r}"
        s[f"O{r}"] = f"=(H{r}-Inputs!$B$8)/365"
        for q, col in enumerate("PQRS"):
            prev = "1" if n == 0 else f"{col}{r-1}"
            s[f"{col}{r}"] = f"={prev}/(1+(Inputs!$B$5+{DMS[q]})*I{r}/365)"
            s[f"{col}{r}"].number_format = "0.000000"
        for col in "JKLMN": s[f"{col}{r}"].number_format = "#,##0.00"
        s[f"O{r}"].number_format = "0.0000"
    for j, h in ((21, "Defaults"), (22, "Defaults returned")):
        c = s.cell(3, j, h); c.font = hdr; c.fill = fill; s.column_dimensions[c.column_letter].width = 15
    if cpr == 11.15:
        s["T3"] = "DF trial"; s["T3"].font = hdr; s["T3"].fill = fill
        for n in range(20):
            r = 4 + n; prev = "1" if n == 0 else f"T{r-1}"
            s[f"T{r}"] = f"={prev}/(1+(Inputs!$B$5+'DM solver'!$B$3)*I{r}/365)"; s[f"T{r}"].number_format = "0.000000"
    s["H25"] = "WAL (years)"; s["K25"] = "=SUMPRODUCT(M4:M23,O4:O23)/Inputs!$B$4"; s["K25"].number_format = "0.00"
    s["H26"] = "Price at DM 1..4"
    for q, col in enumerate("PQRS"):
        s[f"{col}26"] = f"=100*SUMPRODUCT($N$4:$N$23,{col}4:{col}23)/Inputs!$B$4"; s[f"{col}26"].number_format = "0.000"
    s.freeze_panes = "A4"
sm = wb.create_sheet("Summary", 1)
sm["A1"] = "Class A price (per 100) by CPR and discount margin"; sm["A1"].font = Font(bold=True, color=NAVY)
for j, h in enumerate(["CPR", "WAL (years)", "=Inputs!B9", "=Inputs!B10", "=Inputs!B11", "=Inputs!B12"], 1):
    c = sm.cell(3, j, h); c.font = hdr; c.fill = fill; c.number_format = "0.00%"; sm.column_dimensions[c.column_letter].width = 13
for i, cpr in enumerate((5, 11.15, 15, 20)):
    r = 4 + i; sh = f"'CPR {cpr}%'"
    sm.cell(r, 1, f"={sh}!B1").number_format = "0.00%"
    sm.cell(r, 2, f"={sh}!K25").number_format = "0.00"
    for q, col in enumerate("PQRS"):
        sm.cell(r, 3 + q, f"={sh}!{col}26").number_format = "0.000"
gs = wb.create_sheet("DM solver", 2)
gs["A1"] = "Find the DM for a given price (11.15% CPR) with Data > What-If Analysis > Goal Seek"; gs["A1"].font = Font(bold=True, color=NAVY)
gs["A3"] = "Trial DM"; gs["B3"] = 0.0062; gs["B3"].fill = inp; gs["B3"].number_format = "0.0000%"
gs["A4"] = "Price at trial DM"; gs["B4"] = "=100*SUMPRODUCT('CPR 11.15%'!N4:N23,'CPR 11.15%'!T4:T23)/Inputs!B4"
gs["A5"] = "Target price"; gs["B5"] = 99.80; gs["B5"].fill = inp
gs["A6"] = "Difference (Goal Seek: set B6 to 0 by changing B3)"; gs["B6"] = "=B4-B5"
for c in ("B4", "B6"): gs[c].number_format = "0.0000"
gs.column_dimensions["A"].width = 48; gs.column_dimensions["B"].width = 14
wb.save(sys.argv[1])
