"""Build ch19/excel/ch19_stress_cashflow.xlsx: the rating-level stress cash-flow
model of Thames Residential 2027-1 plc, with live formulas (inputs yellow).
Run: python3 tools/build_ch19_xlsx.py data/ch19_thames_schedules.csv \
        data/ch18_rating_level_results.csv ch19/excel/ch19_stress_cashflow.xlsx [check]
With 'check', builds a verification workbook with one sheet per scenario (40)
plus sizing sheets, used by tools/check_ch19.py."""
import sys
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter as L

sys.path.insert(0, "ch19/python")
import ch19_stress_cashflow as M

NAVY = "1F2A44"
HF, HFILL = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor=NAVY)
INP = PatternFill("solid", fgColor="FFF4D6")
TITLE = Font(bold=True, size=13, color=NAVY)
sched = pd.read_csv(sys.argv[1])
lvres = pd.read_csv(sys.argv[2]).set_index("level")
CHECK = len(sys.argv) > 4 and sys.argv[4] == "check"


def hdr(ws, r, c, v):
    x = ws.cell(r, c, v); x.font = HF; x.fill = HFILL
    x.alignment = Alignment(horizontal="center", wrap_text=True)


def inp(ws, ref, v, fmt=None):
    ws[ref] = v; ws[ref].fill = INP
    if fmt: ws[ref].number_format = fmt


wb = Workbook()
# ------------------------------------------------------------------ Inputs
I = wb.active; I.title = "Inputs"
I["A1"] = "Chapter 19 - Stress cash-flow model inputs (agency's criteria in this book: ILLUSTRATIVE)"
I["A1"].font = TITLE
I["A2"] = "Yellow cells are inputs. Every other cell is a formula."
scal = [("Pool balance at cut-off (GBP)", M.POOL0, "#,##0.00"), ("Swap fixed rate paid by issuer (%)", M.SWAP_FIXED, "0.00"),
        ("Reserve fund required (GBP)", M.RF_REQ, "#,##0.00"), ("Reserve fund floor (GBP)", M.RF_FLOOR, "#,##0.00"),
        ("Fixed senior fees (GBP p.a.)", M.FIXED_FEES, "#,##0.00"), ("Issuer profit per IPD (GBP)", M.PROFIT, "#,##0.00"),
        ("Servicing fee, stressed (% p.a.)", M.SERVICING, "0.00"), ("SONIA at closing (%)", M.SONIA0, "0.00"),
        ("First step-up IPD (period number)", M.STEP_UP_P, "0"), ("Recovery lag (quarters)", M.LAG, "0"),
        ("Low prepayment rate, all levels (CPR %)", M.CPR_LOW, "0.00")]
NAMES = {}
for i, (n, v, f) in enumerate(scal):
    I.cell(4 + i, 1, n); inp(I, f"B{4 + i}", v, f)
    NAMES[n.split(" (")[0]] = f"Inputs!$B${4 + i}"
POOL0, SWAPF, RFREQ, RFFLOOR, FIXF, PROF, SERV, SON0, STEPP, LAG, CPRLOW = (f"Inputs!$B${4 + i}" for i in range(11))
# classes A17:E23
for j, h in enumerate(["Class", "Size (GBP)", "Margin (%)", "Subordination (%)", "Index"]):
    hdr(I, 17, 1 + j, h)
for i, c in enumerate(M.CLASSES):
    r = 18 + i
    I.cell(r, 1, c); inp(I, f"B{r}", M.SIZE[c], "#,##0.00")
    if c != "Z":
        inp(I, f"C{r}", M.MARGIN[c], "0.00")
        I.cell(r, 4, f"=SUM(B{r + 1}:B23)/{POOL0}*100").number_format = "0.0000"
    else:
        inp(I, f"C{r}", 0, "0.00"); I.cell(r, 4, 0)
    I.cell(r, 5, i + 1)
I["A24"] = "Total"; I["B24"] = "=SUM(B18:B23)"; I["B24"].number_format = "#,##0.00"
I["A25"] = "Check: total = pool"; I["B25"] = f"=B24-{POOL0}"; I["B25"].number_format = "0.00"
# level table G3:N8
for j, h in enumerate(["Level", "WAFF (%)", "WALS (%)", "High CPR (%)", "SONIA peak, up (%)",
                       "SONIA floor, down (%)", "Floating margin (%)"]):
    hdr(I, 3, 7 + j, h)
for i, k in enumerate(M.LEVELS):
    r = 4 + i
    I.cell(r, 7, k)
    for j, v in enumerate([lvres.loc[k, "waff_pct"], lvres.loc[k, "wals_pct"], M.CPR_HIGH[k], M.SONIA_UP[k],
                           M.SONIA_DOWN[k], M.FLOAT_MARGIN[k]]):
        x = I.cell(r, 8 + j, float(v)); x.fill = INP; x.number_format = "0.00"
LVL = "Inputs!$G$4:$G$8"
# timing G12:I17
for j, h in enumerate(["Year", "front", "back"]):
    hdr(I, 12, 7 + j, h)
for y in range(5):
    I.cell(13 + y, 7, y + 1)
    for j, t in enumerate(["front", "back"]):
        x = I.cell(13 + y, 8 + j, M.TIMING[t][y]); x.fill = INP
I["G18"] = "Total"; I["H18"] = "=SUM(H13:H17)"; I["I18"] = "=SUM(I13:I17)"
I.column_dimensions["A"].width = 38; I.column_dimensions["B"].width = 18
for c in "CDEFGHIJKLMN":
    I.column_dimensions[c].width = 13
# ---------------------------------------------------------------- Schedule
SC = wb.create_sheet("Schedule")
SC["A1"] = "Scheduled balances (zero prepayment, zero default), from tools/gen_ch19_schedules.py"
for j, h in enumerate(["Period", "Scheduled pool balance", "Scheduled fixed balance (swap notional)",
                       "WA fixed rate (%)"]):
    hdr(SC, 2, 1 + j, h)
for i, r in enumerate(sched.itertuples()):
    SC.cell(3 + i, 1, r.period)
    for j, v in enumerate([r.sched_balance, r.sched_fixed_balance, r.fixed_wac_pct]):
        x = SC.cell(3 + i, 2 + j, float(v)); x.fill = INP
        x.number_format = "0.0000" if j == 2 else "#,##0.00"
for c, w in zip("ABCD", [8, 22, 22, 14]):
    SC.column_dimensions[c].width = w
# row of period p in Schedule = p + 3

# ------------------------------------------------------------ model sheet
COLS = ["p", "IPD", "Days", "Months", "SONIA", "S start", "S end", "Swap notional", "Fixed WAC", "Default share",
        "Active", "Defaults", "Performing", "Sched. am. rate", "Sched. principal", "Prepayments", "Pool closing",
        "Recoveries", "Losses", "Pending defaults", "End flag", "Fixed share", "Pool yield", "Interest",
        "Swap net", "Senior fees", "Swap in", "Swap out", "Step-up factor"] + \
       [f"Int due {c}" for c in M.RATED] + \
       ["Principal avail. (gross)", "Senior due", "Revenue before PA", "Enforced", "Principal additions",
        "Revenue available", "Principal avail.", "PDL debit"] + \
       [f"Debit to {c}" for c in reversed(M.CLASSES)] + \
       ["Revenue after senior"] + \
       [x for c in M.RATED for x in (f"Int paid {c}", f"Cure/prin {c}", f"Remaining {c}")] + \
       ["A-E open", "RF target", "Reserve closing", f"Cure/prin Z", "Excess released", "Cures total",
        "Principal to notes"] + \
       [f"Prin paid {c}" for c in M.CLASSES] + [f"Bal {c}" for c in M.CLASSES] + \
       [f"PDL {c}" for c in M.CLASSES] + [f"Deferred {c}" for c in M.RATED] + \
       ["A int shortfall", "Most senior shortfall", "Event of default", "Ended", "Enforced next"]
C = {n: L(i + 1) for i, n in enumerate(COLS)}
R0 = 31                    # row of period 0 (initial state)


def model_sheet(name, level, timing, prep, rates, test_class, sub):
    ws = wb.create_sheet(name)
    ws["A1"] = f"Stress run - rating level {level}"; ws["A1"].font = TITLE
    ws["A2"] = "Yellow cells are inputs: change the scenario, the class tested or its subordination."
    lab = ["Rating level", "Default timing (front/back)", "Prepayment (high/low)", "Interest rates (up/down)",
           "Class tested", "Subordination tested (%, blank = Thames)"]
    vals = [level, timing, prep, rates, test_class, sub]
    for i, (a, v) in enumerate(zip(lab, vals)):
        ws.cell(3 + i, 1, a); inp(ws, f"B{3 + i}", v, "0.00" if i == 5 else None)
    d = [("WAFF", f"=INDEX(Inputs!$H$4:$H$8,MATCH($B$3,{LVL},0))/100", "0.00%"),
         ("WALS", f"=INDEX(Inputs!$I$4:$I$8,MATCH($B$3,{LVL},0))/100", "0.00%"),
         ("CPR (%)", f'=IF($B$5="high",INDEX(Inputs!$J$4:$J$8,MATCH($B$3,{LVL},0)),{CPRLOW})', "0.00"),
         ("SONIA target (%)", f'=IF($B$6="up",INDEX(Inputs!$K$4:$K$8,MATCH($B$3,{LVL},0)),'
                              f'INDEX(Inputs!$L$4:$L$8,MATCH($B$3,{LVL},0)))', "0.00"),
         ("Quarters to reach target", '=IF($B$6="up",12,8)', "0"),
         ("Floating margin (%)", f"=INDEX(Inputs!$M$4:$M$8,MATCH($B$3,{LVL},0))", "0.00"),
         ("Index of class tested", "=MATCH($B$7,Inputs!$A$18:$A$23,0)", "0"),
         ("Size of classes below tested (term sheet)", "=SUMPRODUCT((Inputs!$E$18:$E$23>B15)*Inputs!$B$18:$B$23)",
          "#,##0.00")]
    for i, (a, f, fm) in enumerate(d):
        ws.cell(9 + i, 1, a); ws.cell(9 + i, 2, f).number_format = fm
    WAFF, WALS, CPR, STGT, NRAMP, FM, TIDX, BELOW = (f"$B${9 + i}" for i in range(8))
    # class sizes used D3:J9
    for j, h in enumerate(["Class", "Size used (GBP)", "Margin (%)", "Unpaid principal", "Unpaid deferred int.",
                           "Shortfall", "Result"]):
        hdr(ws, 3, 4 + j, h)
    for i, c in enumerate(M.CLASSES):
        r = 4 + i
        ws.cell(r, 4, c)
        ws.cell(r, 5, f"=IF({i + 1}<{TIDX},Inputs!B{18 + i},IF({i + 1}>{TIDX},"
                      f"Inputs!B{18 + i}*$B$8/100*{POOL0}/{BELOW},0))").number_format = "#,##0.00"
        ws.cell(r, 6, f"=Inputs!C{18 + i}").number_format = "0.00"
    # tested class takes the remainder
    for i in range(6):
        r = 4 + i
        others = "+".join(f"IF({j + 1}={TIDX},0,E{4 + j})" for j in range(6) if j != i)
        ws.cell(r, 5).value = (f'=IF($B$8="",Inputs!B{18 + i},IF({i + 1}={TIDX},{POOL0}-({others}),'
                               f'{ws.cell(r, 5).value[1:]}))')
    LASTR = R0 + M.N_P
    for i, c in enumerate(M.CLASSES):
        r = 4 + i
        ws.cell(r, 7, f"={C['Bal ' + c]}{LASTR}").number_format = "#,##0.00"
        if c != "Z":
            ws.cell(r, 8, f"={C['Deferred ' + c]}{LASTR}").number_format = "#,##0.00"
            ws.cell(r, 9, f"=G{r}+H{r}").number_format = "#,##0.00"
            extra = f"+IF(D{r}=\"A\",$B$25,0)" if c == "A" else ""
            ws.cell(r, 10, f'=IF(I{r}{extra}>0.005,"fail","pass")')
    ws["D11"] = "Class A interest shortfall (sum)"; ws["B25"] = f"=SUM({C['A int shortfall']}{R0 + 1}:{C['A int shortfall']}{LASTR})"
    ws["A25"] = "Class A interest shortfall (GBP)"; ws["B25"].number_format = "#,##0.00"
    ws["A26"] = "Total defaults (GBP)"; ws["B26"] = f"=SUM({C['Defaults']}{R0 + 1}:{C['Defaults']}{LASTR})"
    ws["A27"] = "Total losses (GBP)"; ws["B27"] = f"=SUM({C['Losses']}{R0 + 1}:{C['Losses']}{LASTR})"
    ws["A28"] = "Total swap net (GBP, + received)"; ws["B28"] = f"=SUM({C['Swap net']}{R0 + 1}:{C['Swap net']}{LASTR})"
    ws["A29"] = "Principal written off, all notes (% pool)"
    ws["B29"] = f"=SUM(G4:G9)/{POOL0}*100"
    ws["D11"] = None
    for ref in ("B26", "B27", "B28"):
        ws[ref].number_format = "#,##0.00"
    ws["B29"].number_format = "0.00"
    # header row
    for j, h in enumerate(COLS):
        hdr(ws, R0 - 1, j + 1, h)
    # period 0 state row
    r = R0
    ws[f"A{r}"] = 0
    ws[f"{C['Pool closing']}{r}"] = f"={POOL0}"
    ws[f"{C['Reserve closing']}{r}"] = f"={RFREQ}"
    ws[f"{C['Defaults']}{r}"] = 0
    for i, c in enumerate(M.CLASSES):
        ws[f"{C['Bal ' + c]}{r}"] = f"=$E${4 + i}"
        ws[f"{C['PDL ' + c]}{r}"] = 0
    for c in M.RATED:
        ws[f"{C['Deferred ' + c]}{r}"] = 0
    ws[f"{C['Ended']}{r}"] = 0
    ws[f"{C['Enforced next']}{r}"] = 0
    for p in range(1, M.N_P + 1):
        r = R0 + p; q = r - 1
        g = lambda n, row=r: f"{C[n]}{row}"
        pv = lambda n: f"{C[n]}{q}"
        f = {}
        f["p"] = p
        f["IPD"] = f"=DATE(2027+INT((6+3*({p}-1)-1)/12),MOD(6+3*({p}-1)-1,12)+1,15)"
        f["Days"] = f"={g('IPD')}-DATE(2027,3,18)" if p == 1 else f"={g('IPD')}-{pv('IPD')}"
        f["Months"] = 4 if p == 1 else 3
        f["SONIA"] = f"={SON0}+({STGT}-{SON0})*MIN({g('p')},{NRAMP})/{NRAMP}"
        f["S start"] = f"=INDEX(Schedule!$B$3:$B$154,{g('p')})"
        f["S end"] = f"=INDEX(Schedule!$B$3:$B$154,{g('p')}+1)"
        f["Swap notional"] = f"=INDEX(Schedule!$C$3:$C$154,{g('p')})"
        f["Fixed WAC"] = f"=INDEX(Schedule!$D$3:$D$154,{g('p')})"
        f["Default share"] = (f"=IF({g('p')}<=20,INDEX(Inputs!$H$13:$I$17,INT(({g('p')}-1)/4)+1,"
                              f"MATCH($B$4,Inputs!$H$12:$I$12,0))/400,0)")
        f["Active"] = f"=IF({pv('Ended')}=1,0,1)"
        f["Defaults"] = f"=MIN({pv('Pool closing')},{WAFF}*{POOL0}*{g('Default share')})"
        f["Performing"] = f"={pv('Pool closing')}-{g('Defaults')}"
        f["Sched. am. rate"] = f"=IF({g('S start')}=0,1,1-{g('S end')}/{g('S start')})"
        f["Sched. principal"] = f"={g('Performing')}*{g('Sched. am. rate')}"
        f["Prepayments"] = f"=({g('Performing')}-{g('Sched. principal')})*(1-(1-{CPR}/100)^({g('Months')}/12))"
        f["Pool closing"] = f"={g('Performing')}-{g('Sched. principal')}-{g('Prepayments')}"
        lagged = f"OFFSET({g('Defaults')},-{LAG},0)"
        f["Recoveries"] = f"=IF({g('p')}>{LAG},{lagged}*(1-{WALS}),0)"
        f["Losses"] = f"=IF({g('p')}>{LAG},{lagged}*{WALS},0)"
        f["Pending defaults"] = (f"=SUM(OFFSET({g('Defaults')},-(MIN({g('p')},{LAG})-1),0,"
                                 f"MIN({g('p')},{LAG}),1))")
        f["End flag"] = (f"=IF(AND({g('Active')}=1,OR({g('p')}={M.N_P},AND({g('Pool closing')}<0.005,"
                         f"{g('Pending defaults')}<0.005))),1,0)")
        f["Fixed share"] = f"=IF({g('S start')}=0,0,{g('Swap notional')}/{g('S start')})"
        f["Pool yield"] = f"={g('Fixed share')}*{g('Fixed WAC')}+(1-{g('Fixed share')})*({g('SONIA')}+{FM})"
        f["Interest"] = f"={g('Performing')}*{g('Pool yield')}/100*{g('Months')}/12"
        f["Swap net"] = f"={g('Swap notional')}*({g('SONIA')}-{SWAPF})/100*{g('Days')}/365"
        f["Senior fees"] = (f"={g('Active')}*(({FIXF}+{g('Performing')}*{SERV}/100)*{g('Months')}/12"
                            f"+{PROF})")
        f["Swap in"] = f"=MAX({g('Swap net')},0)"
        f["Swap out"] = f"=MAX(-{g('Swap net')},0)"
        f["Step-up factor"] = f"=IF({g('p')}>={STEPP},2,1)"
        for i, c in enumerate(M.RATED):
            f[f"Int due {c}"] = (f"={g('Active')}*(({pv('Bal ' + c)}+{pv('Deferred ' + c)})*({g('SONIA')}+"
                                 f"{g('Step-up factor')}*$F${4 + i})/100*{g('Days')}/365+{pv('Deferred ' + c)})")
        f["Principal avail. (gross)"] = f"={g('Sched. principal')}+{g('Prepayments')}+{g('Recoveries')}"
        f["Senior due"] = (f"={g('Senior fees')}+{g('Swap out')}+{g('Int due A')}+"
                           f"IF({pv('Bal A')}<0.005,{g('Int due B')},0)")
        f["Revenue before PA"] = f"={g('Interest')}+{g('Swap in')}+{pv('Reserve closing')}"
        f["Enforced"] = f"={pv('Enforced next')}"
        f["Principal additions"] = (f"=IF({g('Enforced')}=1,0,MIN(MAX(0,{g('Senior due')}-"
                                    f"{g('Revenue before PA')}),{g('Principal avail. (gross)')}))")
        f["Revenue available"] = (f"={g('Revenue before PA')}+{g('Principal additions')}+"
                                  f"IF({g('Enforced')}=1,{g('Principal avail. (gross)')},0)")
        f["Principal avail."] = (f"=IF({g('Enforced')}=1,0,{g('Principal avail. (gross)')}-"
                                 f"{g('Principal additions')})")
        f["PDL debit"] = f"=IF({g('Enforced')}=1,0,{g('Losses')}+{g('Principal additions')})"
        taken = []
        for c in reversed(M.CLASSES):
            left = f"{g('PDL debit')}" + "".join(f"-{t}" for t in taken)
            f[f"Debit to {c}"] = f"=MIN({left},{pv('Bal ' + c)}-{pv('PDL ' + c)})"
            taken.append(g(f"Debit to {c}"))
        f["Revenue after senior"] = (f"={g('Revenue available')}-MIN({g('Revenue available')},"
                                     f"{g('Senior fees')}+{g('Swap out')})")
        prev_rem = g("Revenue after senior")
        for c in M.RATED:
            f[f"Int paid {c}"] = f"=MIN({prev_rem},{g('Int due ' + c)})"
            pdl_after = f"({pv('PDL ' + c)}+{g('Debit to ' + c)})"
            f[f"Cure/prin {c}"] = (f"=MIN({prev_rem}-{g('Int paid ' + c)},IF({g('Enforced')}=1,"
                                   f"{pv('Bal ' + c)},{pdl_after}))")
            f[f"Remaining {c}"] = f"={prev_rem}-{g('Int paid ' + c)}-{g('Cure/prin ' + c)}"
            prev_rem = g(f"Remaining {c}")
        f["A-E open"] = "=" + "+".join(pv(f"Bal {c}") for c in M.RATED)
        f["RF target"] = (f"=IF(OR({g('Enforced')}=1,{g('End flag')}=1,{g('A-E open')}<0.005),0,"
                          f"IF({pv('Bal A')}>0.005,{RFREQ},MAX({RFFLOOR},0.015*{g('A-E open')})))")
        f["Reserve closing"] = f"=MIN({g('Remaining E')},{g('RF target')})"
        f["Cure/prin Z"] = (f"=MIN({g('Remaining E')}-{g('Reserve closing')},IF({g('Enforced')}=1,"
                            f"{pv('Bal Z')},{pv('PDL Z')}+{g('Debit to Z')}))")
        f["Excess released"] = f"={g('Remaining E')}-{g('Reserve closing')}-{g('Cure/prin Z')}"
        f["Cures total"] = (f"=IF({g('Enforced')}=1,0," + "+".join(g(f"Cure/prin {c}") for c in M.CLASSES) + ")")
        f["Principal to notes"] = f"={g('Principal avail.')}+{g('Cures total')}"
        paid_before = []
        for c in M.CLASSES:
            left = f"{g('Principal to notes')}" + "".join(f"-{t}" for t in paid_before)
            f[f"Prin paid {c}"] = (f"=IF({g('Enforced')}=1,{g('Cure/prin ' + c)},MIN({left},"
                                   f"{pv('Bal ' + c)}))")
            paid_before.append(g(f"Prin paid {c}"))
        for c in M.CLASSES:
            f[f"Bal {c}"] = f"={pv('Bal ' + c)}-{g('Prin paid ' + c)}"
            f[f"PDL {c}"] = (f"=IF({g('Enforced')}=1,{pv('PDL ' + c)},{pv('PDL ' + c)}+{g('Debit to ' + c)}-"
                             f"{g('Cure/prin ' + c)})")
        for c in M.RATED:
            f[f"Deferred {c}"] = (f"=IF({g('Active')}=1,{g('Int due ' + c)}-{g('Int paid ' + c)},"
                                  f"{pv('Deferred ' + c)})")
        f["A int shortfall"] = f"={g('Int due A')}-{g('Int paid A')}"
        sh = "0"
        for c in reversed(M.RATED):
            sh = f"IF({pv('Bal ' + c)}>0.005,{g('Int due ' + c)}-{g('Int paid ' + c)},{sh})"
        f["Most senior shortfall"] = "=" + sh
        f["Event of default"] = f"=IF(AND({g('Active')}=1,{g('Most senior shortfall')}>0.005),1,0)"
        f["Ended"] = f"=IF(OR({pv('Ended')}=1,{g('End flag')}=1),1,0)"
        f["Enforced next"] = f"=IF(OR({g('Enforced')}=1,{g('Event of default')}=1),1,0)"
        for n, v in f.items():
            x = ws[g(n)]; x.value = v
            if n == "IPD": x.number_format = "yyyy-mm-dd"
            elif n in ("SONIA", "Pool yield", "Fixed WAC"): x.number_format = "0.0000"
            elif n in ("Sched. am. rate", "Fixed share", "Default share"): x.number_format = "0.000000"
            elif n in ("p", "Days", "Months", "Active", "End flag", "Enforced", "Step-up factor",
                       "Event of default", "Ended", "Enforced next"): x.number_format = "0"
            else: x.number_format = "#,##0.00"
    ws.column_dimensions["A"].width = 36; ws.column_dimensions["B"].width = 16
    for j in range(3, len(COLS) + 1):
        ws.column_dimensions[L(j)].width = 14
    ws.freeze_panes = ws[f"C{R0 + 1}"]
    return ws


WORST = {"AAA": ("front", "high", "down"), "AA": ("front", "high", "down"), "A": ("front", "high", "down"),
         "BBB": ("back", "high", "down"), "BB": ("back", "high", "down")}
sheets = []
if not CHECK:
    for lvl, c in zip(M.LEVELS, M.RATED):
        t, pr, ra = WORST[lvl]
        model_sheet(lvl, lvl, t, pr, ra, c, None); sheets.append(lvl)
    # Results sheet
    R = wb.create_sheet("Results", 1)
    R["A1"] = "Results - worst-case scenario at each rating level, on the Thames structure"; R["A1"].font = TITLE
    for j, h in enumerate(["Sheet", "Timing", "Prepayment", "Rates", "Class A", "Class B", "Class C", "Class D",
                           "Class E", "Written off (% pool)"]):
        hdr(R, 3, 1 + j, h)
    for i, s in enumerate(sheets):
        r = 4 + i
        R.cell(r, 1, s)
        for j, ref in enumerate(["B4", "B5", "B6"]):
            R.cell(r, 2 + j, f"='{s}'!{ref}")
        for j in range(5):
            R.cell(r, 5 + j, f"='{s}'!J{4 + j}")
        R.cell(r, 10, f"='{s}'!B29").number_format = "0.00"
    R["A11"] = ("Each level sheet runs one scenario. Change the yellow selectors on a sheet to run the other seven, "
                "or type a subordination in B8 to test the credit enhancement needed.")
    for c, w in zip("ABCDEFGHIJ", [8, 10, 12, 8, 9, 9, 9, 9, 9, 20]):
        R.column_dimensions[c].width = w
else:
    k = 0
    for lvl in M.LEVELS:
        for t, pr, ra in M.combos():
            k += 1
            model_sheet(f"S{k}", lvl, t, pr, ra, "A", None)
    lv = pd.read_csv(sys.argv[2]).set_index("level")
    for lvl, c in zip(M.LEVELS, M.RATED):
        n = M.needed(sched, lv, lvl, c)
        t, pr, ra = WORST[lvl]
        model_sheet(f"N_{lvl}", lvl, t, pr, ra, c, n - M.RF_PCT)
        model_sheet(f"M_{lvl}", lvl, t, pr, ra, c, n - 0.01 - M.RF_PCT)
wb.save(sys.argv[3])
print("saved", sys.argv[3])
