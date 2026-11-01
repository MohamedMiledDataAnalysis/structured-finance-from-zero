"""Chapter 31 - Rhein Auto 2027-1 monthly cash-flow model:
12-month revolving period, then pro rata amortisation with
sequential triggers, clean-up call at 10% of the initial pool.
Run from the book folder:
  python3 ch31/python/ch31_rhein_cashflow.py \\
      data/ch31_rhein_scheduled_runoff.csv
Conventions (identical in Excel and R):
- period t = collection month t after cut-off (t=1: March 2027),
  paid on the 25th of month t+1 (modified following, TARGET);
- every money amount is rounded to the cent (Excel ROUND rule);
- notes, swap and subordinated loan: Actual/360;
  pool interest, fees: 1/12 of the annual rate.
"""
import sys
from datetime import date, timedelta
import pandas as pd

def round2(x):
    s = -1 if x < 0 else 1
    return s * int(abs(x) * 100 + 0.5 + 1e-9) / 100

# ---------- deal inputs (Deal Fact Sheets, Chapter 31) ----------
POOL0 = 480_929_439.61
NOTES0 = {"A": 432_800_000.00, "B": 21_600_000.00,
          "C": 14_400_000.00, "Sub": 12_129_439.61}
MARGIN = {"A": 0.0055, "B": 0.0125, "C": 0.0210}
SUB_RATE, SWAP_FIXED = 0.06, 0.024
FEES_PA, SERVICING = 150_000.00, 0.005
RES0, RES_FLOOR, RES_PCT = 4_809_294.40, 2_400_000.00, 0.01
REVOLVING, EA_CNL, CALL = 12, 0.008, 0.10
CLOSING = date(2027, 3, 25)

def seq_threshold(k):          # k = month of amortisation
    return 0.008 if k <= 12 else 0.014 if k <= 24 else 0.020

# ---------- TARGET calendar, modified following ----------
def easter(y):
    a, b, c = y % 19, y // 100, y % 100
    d, e = divmod(b, 4)
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    i, k = divmod(c, 4)
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    mo, da = divmod(h + l - 7 * m + 114, 31)
    return date(y, mo, da + 1)

def closed(d):
    e = easter(d.year)
    fixed = [(1, 1), (5, 1), (12, 25), (12, 26)]
    return (d.weekday() >= 5 or (d.month, d.day) in fixed
            or d in (e - timedelta(2), e + timedelta(1)))

def mod_following(d):
    x = d
    while closed(x):
        x += timedelta(1)
    if x.month != d.month:
        x = d
        while closed(x):
            x -= timedelta(1)
    return x

def payment_date(t):
    y, m = divmod(3 + t - 1, 12)      # t=1 -> April 2027
    return mod_following(date(2027 + y, m + 1, 25))

# ---------- the model ----------
def run(cdr, rr, cpr, euribor=0.0225, war=0.0477, lag=6):
    ro = pd.read_csv(sys.argv[1])
    prof = list((ro.regular_principal + ro.balloon_principal)
                / ro.opening)
    mdr = 1 - (1 - cdr) ** (1 / 12)
    smm = 1 - (1 - cpr) ** (1 / 12)
    idx = max(euribor, 0.0)
    bal, res = POOL0, RES0
    L = dict(NOTES0)
    seq = ea = False
    rev_done, prev = 0, CLOSING
    dflt, cum_d, cum_r = [], 0.0, 0.0
    rows = []
    for t in range(1, 200):
        pdt = payment_date(t)
        days = (pdt - prev).days
        prev = pdt
        # 1. pool collections for month t
        d = round2(bal * mdr)
        r = round2(dflt[t - 1 - lag] * rr) if t > lag else 0.0
        dflt.append(d)
        cum_d, cum_r = cum_d + d, cum_r + r
        cnl = (cum_d - cum_r) / POOL0
        ea = ea or (t <= REVOLVING and cnl > EA_CNL)
        rev = t <= REVOLVING and not ea
        rev_done += rev
        k = t if rev else t - rev_done   # profile month
        s = prof[k - 1] if k <= len(prof) else 1.0
        sched = round2((bal - d) * s)
        prepay = round2((bal - d - sched) * smm)
        inter = round2((bal - d) * war / 12)
        pool_end = round2(bal - d - sched - prepay)
        avail = round2(inter + sched + prepay + r)
        avail0 = avail
        # 2. senior items: fees, swap, note interest
        notes = L["A"] + L["B"] + L["C"]
        fees = round2(FEES_PA / 12 + bal * SERVICING / 12)
        swap = round2(notes * (SWAP_FIXED - idx) * days / 360)
        ints = {c: round2(L[c] * (idx + MARGIN[c]) * days / 360)
                for c in MARGIN}
        avail = round2(avail + max(0.0, -swap))
        senior = round2(fees + max(0.0, swap) + sum(ints.values()))
        draw = round2(min(res, max(0.0, senior - avail)))
        res = round2(res - draw)
        avail = round2(max(0.0, avail + draw - senior))
        # 3. triggers
        call = (not rev) and pool_end < CALL * POOL0
        req_pr = min(RES0, max(RES_PCT * notes, RES_FLOOR))
        if not rev and not call and not seq:
            seq = (cnl > seq_threshold(k)
                   or res < req_pr - 0.005)
        req = 0.0 if call else (RES0 if rev or seq else req_pr)
        # 4. cash reserve: top up, release excess
        if call:
            avail, res = round2(avail + res), 0.0
        top = round2(min(max(0.0, req - res), avail))
        res, avail = round2(res + top), round2(avail - top)
        release = round2(max(0.0, res - req))
        res = round2(res - release)
        # 5. principal: buy receivables or redeem notes
        Ltot = round2(sum(L.values()))
        target = Ltot if call else round2(max(0.0, Ltot - pool_end))
        pay = {c: 0.0 for c in L}
        buy = 0.0
        if rev:
            buy = round2(min(target, avail))
            avail = round2(avail - buy)
            bal = round2(pool_end + buy)
        else:
            if call:
                avail = round2(avail + pool_end)
            bal = 0.0 if call else pool_end
            for c in ("A", "B", "C", "Sub"):
                if seq or call:
                    want = min(L[c], target)
                else:
                    want = round2(target * L[c] / Ltot)
                pay[c] = round2(min(want, avail))
                avail = round2(avail - pay[c])
                if seq or call:
                    target = round2(target - pay[c])
            for c in L:
                L[c] = round2(L[c] - pay[c])
        # 6. subordinated loan interest, then residual
        sub_int = round2(min(avail,
                             (L["Sub"] + pay["Sub"]) * SUB_RATE
                             * days / 360))
        avail = round2(avail - sub_int)
        rows.append(dict(t=t, date=pdt, days=days, rev=rev,
                         seq=seq, call=call, k=k, default=d,
                         recovery=r, sched=sched, prepay=prepay,
                         pool_end=pool_end,
                         interest=inter, cnl=cnl, buy=buy,
                         pool=bal, res=res, residual=avail,
                         intA=ints["A"], swap=swap, avail0=avail0,
                         intB=ints["B"], intC=ints["C"],
                         fees=fees, top=top, sub_int=sub_int,
                         **{f"pay{c}": pay[c] for c in L},
                         **{f"bal{c}": L[c] for c in L}))
        if call or sum(L.values()) < 0.005:
            break
    return pd.DataFrame(rows)

def wal(df, c):
    yrs = df.date.map(lambda d: (d - CLOSING).days / 365)
    return (df[f"pay{c}"] * yrs).sum() / NOTES0[c]

def report(name, df):
    eur = lambda x: f"{x:,.2f}"
    print(f"\n{name}")
    first = df.iloc[0]
    print(f"First payment date      : {first.date} "
          f"({first.days} days)")
    print(f"Class A interest, PD 1  : {eur(first.intA)}")
    print(f"Swap net paid, PD 1     : {eur(first.swap)}")
    rv = df[df.rev]
    print(f"Revolving payment dates : {len(rv)}")
    print(f"Receivables bought      : {eur(rv.buy.sum())}")
    print(f"CNL end of revolving    : "
          f"{100 * rv.cnl.iloc[-1]:.2f}%")
    sq = df[df.seq]
    if len(sq):
        s0 = sq.iloc[0]
        print(f"Sequential trigger      : {s0.date} (amort."
              f" month {s0.k}, CNL {100 * s0.cnl:.2f}%)")
    else:
        print("Sequential trigger      : not hit")
    last = df.iloc[-1]
    print(f"Clean-up call           : {last.date} "
          f"(pool {eur(last.pool_end)})")
    left = sum(last[f"bal{c}"] for c in ("A", "B", "C", "Sub"))
    print(f"Owed after the call     : {eur(left)}")
    print(f"CNL at call             : {100 * last.cnl:.2f}%")
    print("WAL from closing (years): " + "  ".join(
        f"{c} {wal(df, c):.2f}" for c in ("A", "B", "C", "Sub")))

def snapshot(df, ts):
    print("  PD          Pool        Class A      Class B"
          "     Class C")
    for t in ts:
        r = df[df.t == t].iloc[0]
        print(f"  {r.date} {r.pool:>14,.0f} {r.balA:>12,.0f}"
              f" {r.balB:>11,.0f} {r.balC:>11,.0f}")

def waterfall(df, t):
    r = df[df.t == t].iloc[0]
    lines = [("Interest collections", r.interest),
             ("Scheduled principal", r.sched),
             ("Prepayments", r.prepay),
             ("Recoveries", r.recovery),
             ("Available distribution amount", r.avail0),
             ("1 Senior expenses and servicing", -r.fees),
             ("2 Swap net payment", -r.swap),
             ("3 Class A interest", -r.intA),
             ("4 Class B interest", -r.intB),
             ("5 Class C interest", -r.intC),
             ("6 Cash reserve top-up", -r.top),
             ("7 Purchase of new receivables", -r.buy),
             ("8 Subordinated loan interest", -r.sub_int),
             ("9 Residual to Rheinwagen Bank", -r.residual)]
    print(f"\nWATERFALL, payment date {r.date}")
    for lab, v in lines:
        v = v if v != 0 else 0.0     # no "-0.00"
        print(f"  {lab:<32}{v:>16,.2f}")

CPR = 0.1266
base = run(cdr=0.0048, rr=0.55, cpr=CPR)
stress = run(cdr=0.0096, rr=0.50, cpr=CPR)
report("BASE CASE (CDR 0.48%, recovery 55%, CPR 12.66%)", base)
snapshot(base, [12, 13, 16, 24, 36])
waterfall(base, 1)
report("STRESS (CDR 0.96%, recovery 50%, CPR 12.66%)", stress)
snapshot(stress, [12, 13, 16, 24, 36])
