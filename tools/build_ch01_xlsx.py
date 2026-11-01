import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
NAVY, GOLD = "1F2A44", "C9A227"
wb = Workbook(); ws = wb.active; ws.title = "Inputs"
hdr = Font(bold=True, color="FFFFFF"); fill = PatternFill("solid", fgColor=NAVY)
inp = PatternFill("solid", fgColor="FFF4D6")
ws["A1"] = "Chapter 1 - Loan KBS-000417 (Thames Residential 2027-1)"; ws["A1"].font = Font(bold=True, size=13, color=NAVY)
items = [("Loan amount (£)",185000,"#,##0.00"),("Annual interest rate",0.0429,"0.00%"),("Term (months)",300,"0"),
         ("Monthly rate","=B4/12","0.000000%"),("Monthly payment (£)","=ROUND(PMT(B6,B5,-B3),2)","#,##0.00"),
         ("Payments made at cut-off",46,"0"),("Balance at cut-off (£)","=INDEX(Schedule!F:F,B8+1)","#,##0.00"),
         ("Tape current balance (£)",167784.59,"#,##0.00"),("Check (should be 0)","=B9-B10","0.00"),
         ("Final payment (£)","=Schedule!C301","#,##0.00"),("Total interest (£)","=SUM(Schedule!D2:D301)","#,##0.00")]
for i,(lab,val,fmt) in enumerate(items, start=3):
    ws.cell(i,1,lab); c = ws.cell(i,2,val); c.number_format = fmt
    if not str(val).startswith("="): c.fill = inp
ws.column_dimensions["A"].width = 30; ws.column_dimensions["B"].width = 16
ws["A15"] = "Yellow cells are inputs. Every other cell is a formula."
sc = wb.create_sheet("Schedule")
for j,h in enumerate(["Month","Opening balance","Payment","Interest","Principal","Closing balance"],1):
    c = sc.cell(1,j,h); c.font = hdr; c.fill = fill; c.alignment = Alignment(horizontal="center")
    sc.column_dimensions[chr(64+j)].width = 17
for m in range(1,301):
    r = m+1
    sc.cell(r,1,m)
    sc.cell(r,2,"=Inputs!B3" if m==1 else f"=F{r-1}")
    sc.cell(r,4,f"=ROUND(B{r}*Inputs!$B$6,2)")
    sc.cell(r,3,f"=IF(A{r}=Inputs!$B$5,B{r}+D{r},Inputs!$B$7)")
    sc.cell(r,5,f"=C{r}-D{r}")
    sc.cell(r,6,f"=B{r}-E{r}")
    for j in range(2,7): sc.cell(r,j).number_format = "#,##0.00"
sc.freeze_panes = "A2"
io = wb.create_sheet("Interest-only")
io["A1"]="Same loan as interest-only"; io["A1"].font=Font(bold=True,color=NAVY)
io["A3"]="Monthly payment (£)"; io["B3"]="=ROUND(Inputs!B3*Inputs!B6,2)"
io["A4"]="Balance after 300 payments (£)"; io["B4"]="=Inputs!B3"
io["A5"]="Total interest over the term (£)"; io["B5"]="=B3*Inputs!B5"
for c in ("B3","B4","B5"): io[c].number_format="#,##0.00"
io.column_dimensions["A"].width=34; io.column_dimensions["B"].width=16
fl = wb.create_sheet("Floating")
fl["A1"]="Tracker loan: rate = Bank Rate + margin (illustrative rates)"; fl["A1"].font=Font(bold=True,color=NAVY)
for j,h in enumerate(["Month","Bank Rate","Margin","Loan rate","Opening","Payment","Interest","Principal","Closing"],1):
    c=fl.cell(3,j,h); c.font=hdr; c.fill=fill; fl.column_dimensions[chr(64+j)].width=13
bank=[3.75]*6+[4.00]*6
for m in range(1,13):
    r=m+3
    fl.cell(r,1,m); fl.cell(r,2,bank[m-1]/100).fill=inp; fl.cell(r,3,0.0075).fill=inp
    fl.cell(r,4,f"=B{r}+C{r}")
    fl.cell(r,5,185000 if m==1 else f"=I{r-1}")
    fl.cell(r,6,f"=ROUND(PMT(D{r}/12,300-A{r}+1,-E{r}),2)")
    fl.cell(r,7,f"=ROUND(E{r}*D{r}/12,2)"); fl.cell(r,8,f"=F{r}-G{r}"); fl.cell(r,9,f"=E{r}-H{r}")
    for j in (2,3,4): fl.cell(r,j).number_format="0.00%"
    for j in range(5,10): fl.cell(r,j).number_format="#,##0.00"
wb.save(sys.argv[1])
