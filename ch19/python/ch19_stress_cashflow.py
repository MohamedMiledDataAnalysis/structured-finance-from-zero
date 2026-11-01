"""Chapter 19 - Rating-level cash-flow stresses for Thames Residential
2027-1 plc. Quarterly pool and pre-enforcement waterfall model under
the agency's criteria in this book (ILLUSTRATIVE). For each rating
level it runs 8 stress combinations (default timing x prepayment x
interest rates), finds the worst case and prints a pass/fail table.

Run from the book folder:
  python3 ch19/python/ch19_stress_cashflow.py \\
      data/ch19_thames_schedules.csv \\
      data/ch18_rating_level_results.csv
"""
import sys
from datetime import date
import pandas as pd

POOL0 = 635671146.31
CLASSES = ["A", "B", "C", "D", "E", "Z"]
RATED = ["A", "B", "C", "D", "E"]
SIZE = {"A": 553000000.00, "B": 31800000.00, "C": 19100000.00,
        "D": 12700000.00, "E": 9500000.00, "Z": 9571146.31}
MARGIN = {"A": 0.62, "B": 1.10, "C": 1.50, "D": 2.20, "E": 3.50}
SUB = {c: 100 * sum(SIZE[d] for d in CLASSES[i + 1:]) / POOL0
       for i, c in enumerate(RATED)}   # exact subordination, %
RF_PCT = 100 * 9391500.00 / POOL0       # reserve fund, % of pool
CE = {c: SUB[c] + RF_PCT for c in RATED}  # CE = sub. + reserve
SWAP_FIXED = 3.30          # issuer pays 3.30% fixed, receives SONIA
RF_REQ, RF_FLOOR = 9391500.00, 3000000.00
FIXED_FEES = 225000.00     # p.a.: trustee, CSP, agents, CM, other
PROFIT = 1000.00           # issuer profit per IPD
SONIA0 = 3.75
STEP_UP_P = 20             # 15 March 2032 is IPD number 20
N_P = 151                  # IPD 151 = 15 December 2064 (legal final)

# ---- the agency's criteria in this book: cash-flow stresses ----
LEVELS = ["AAA", "AA", "A", "BBB", "BB"]
CPR_HIGH = {"AAA": 25, "AA": 22, "A": 20, "BBB": 18, "BB": 16}
CPR_LOW = 2
SONIA_UP = {"AAA": 8.50, "AA": 7.75, "A": 7.00, "BBB": 6.25,
            "BB": 5.50}    # peak, reached after 12 quarters
SONIA_DOWN = {"AAA": 0.25, "AA": 0.50, "A": 0.75, "BBB": 1.00,
              "BB": 1.50}  # floor, reached after 8 quarters
FLOAT_MARGIN = {"AAA": 1.50, "AA": 1.75, "A": 2.00, "BBB": 2.25,
                "BB": 2.50}  # stressed margin over SONIA
SERVICING = 0.25           # % p.a. (replacement servicer cost)
LAG = 6                    # recovery lag in quarters (18 months)
TIMING = {"front": [35, 30, 20, 10, 5],
          "back": [5, 10, 20, 30, 35]}   # % of defaults per year


def ipd(p):
    m = 6 + 3 * (p - 1)
    return date(2027 + (m - 1) // 12, (m - 1) % 12 + 1, 15)


def days(p):
    prev = date(2027, 3, 18) if p == 1 else ipd(p - 1)
    return (ipd(p) - prev).days


def sonia(p, path, lvl):
    tgt = SONIA_UP[lvl] if path == "up" else SONIA_DOWN[lvl]
    n = 12 if path == "up" else 8
    return SONIA0 + (tgt - SONIA0) * min(p, n) / n


def dshare(p, timing):
    return TIMING[timing][(p - 1) // 4] / 400 if p <= 20 else 0.0


def run(sched, lvl, waff, wals, timing, cpr, path, size=SIZE):
    S = sched["sched_balance"].tolist()
    F = sched["sched_fixed_balance"].tolist()
    W = sched["fixed_wac_pct"].tolist()
    bal = dict(size)
    pdl = {c: 0.0 for c in CLASSES}
    dfr = {c: 0.0 for c in RATED}
    pool, rf, ended, enf = POOL0, RF_REQ, False, False
    D = [0.0] * (N_P + 1)
    rows = []
    for p in range(1, N_P + 1):
        act = 0.0 if ended else 1.0
        mon = 4 if p == 1 else 3
        dy, so = days(p), sonia(p, path, lvl)
        # ---- pool ----
        D[p] = min(pool, waff * POOL0 * dshare(p, timing))
        perf = pool - D[p]
        am = 1.0 if S[p - 1] == 0 else 1 - S[p] / S[p - 1]
        sp = perf * am
        pp = (perf - sp) * (1 - (1 - cpr / 100) ** (mon / 12))
        pool = perf - sp - pp
        old = D[p - LAG] if p > LAG else 0.0
        rec, loss = old * (1 - wals), old * wals
        pending = sum(D[max(1, p - LAG + 1):p + 1])
        is_end = act == 1 and (p == N_P or (pool < 0.005
                                              and pending < 0.005))
        fsh = 0.0 if S[p - 1] == 0 else F[p - 1] / S[p - 1]
        yld = fsh * W[p - 1] + (1 - fsh) * (so + FLOAT_MARGIN[lvl])
        intr = perf * yld / 100 * mon / 12
        swap = F[p - 1] * (so - SWAP_FIXED) / 100 * dy / 365
        # ---- amounts due ----
        fees = act * ((FIXED_FEES + perf * SERVICING / 100)
                      * mon / 12 + PROFIT)
        s_in, s_out = max(swap, 0.0), max(-swap, 0.0)
        up = 2 if p >= STEP_UP_P else 1
        due = {c: act * ((bal[c] + dfr[c]) * (so + up * MARGIN[c])
                         / 100 * dy / 365 + dfr[c]) for c in RATED}
        # ---- principal additions (senior expenses, A interest;
        #      B interest while B is the most senior class) ----
        avail_p = sp + pp + rec
        senior = fees + s_out + due["A"]
        if bal["A"] < 0.005:
            senior += due["B"]
        rev = intr + s_in + rf
        pa = 0.0 if enf else min(max(0.0, senior - rev), avail_p)
        if enf:                       # post-enforcement: one pot
            rev += avail_p
            avail_p = 0.0
        rev += pa
        avail_p -= pa
        # ---- PDL debits (losses + principal additions), Z first ----
        debit = 0.0 if enf else loss + pa
        for c in reversed(CLASSES):
            take = min(debit, bal[c] - pdl[c])
            pdl[c] += take
            debit -= take
        # ---- revenue priority of payments; after enforcement the
        #      combined priority (interest then principal by class) --
        rem = rev - min(rev, fees + s_out)
        cure = 0.0
        paid, prin_e = {}, {}
        top = next((c for c in RATED if bal[c] > 0.005), None)
        for c in RATED:
            paid[c] = min(rem, due[c])
            rem -= paid[c]
            dfr[c] = due[c] - paid[c] if act else dfr[c]
            cu = min(rem, bal[c] if enf else pdl[c])
            rem -= cu
            if enf:
                prin_e[c] = cu
            else:
                pdl[c] -= cu
                cure += cu
        open_ae = sum(bal[c] for c in RATED)
        if enf or is_end or open_ae < 0.005:
            tgt = 0.0
        elif bal["A"] > 0.005:
            tgt = RF_REQ
        else:
            tgt = max(RF_FLOOR, 0.015 * open_ae)
        rf = min(rem, tgt)
        rem -= rf
        cu = min(rem, bal["Z"] if enf else pdl["Z"])
        rem -= cu
        if enf:
            prin_e["Z"] = cu
        else:
            pdl["Z"] -= cu
            cure += cu
        # ---- principal priority of payments (sequential) ----
        prin = avail_p + cure
        for c in CLASSES:
            x = prin_e[c] if enf else min(prin, bal[c])
            bal[c] -= x
            prin -= 0.0 if enf else x
        # event of default: most senior class interest not paid
        eod = act == 1 and top is not None and \
            due[top] - paid[top] > 0.005
        rows.append(dict(p=p, ipd=ipd(p), sonia=so, defaults=D[p],
                         pool=pool, interest=intr, swap=swap,
                         loss=loss, recovery=rec, pa=pa, fees=fees,
                         rf=rf, excess=rem + prin,
                         a_short=due["A"] - paid["A"], enforced=enf,
                         **{f"bal_{c}": bal[c] for c in CLASSES},
                         **{f"pdl_{c}": pdl[c] for c in CLASSES},
                         **{f"dfr_{c}": dfr[c] for c in RATED}))
        if is_end:
            ended = True
        if eod:
            enf = True
    return pd.DataFrame(rows)


def results(df):
    """Unpaid principal + deferred interest per class at the end;
    U = principal written off on all notes, % of the pool."""
    last = df.iloc[-1]
    short = {c: last[f"bal_{c}"] + last[f"dfr_{c}"] for c in RATED}
    u = sum(last[f"bal_{c}"] for c in CLASSES) / POOL0 * 100
    return short, u, df["a_short"].sum()


def combos():
    for timing in ["front", "back"]:
        for cprk in ["high", "low"]:
            for path in ["up", "down"]:
                yield timing, cprk, path


def all_runs(sched, lv):
    out = []
    for lvl in LEVELS:
        waff = lv.loc[lvl, "waff_pct"] / 100
        wals = lv.loc[lvl, "wals_pct"] / 100
        for timing, cprk, path in combos():
            cpr = CPR_HIGH[lvl] if cprk == "high" else CPR_LOW
            df = run(sched, lvl, waff, wals, timing, cpr, path)
            short, u, ash = results(df)
            out.append(dict(level=lvl, timing=timing, cpr=cpr,
                            rates=path, u=u, a_int_short=ash,
                            **{f"short_{c}": short[c]
                               for c in RATED}))
    return pd.DataFrame(out)


def resize(x, s):
    """Structure in which class x has subordination s (% of pool):
    classes above x keep their size, classes below x are scaled
    pro rata to total s, class x takes the remainder."""
    i = CLASSES.index(x)
    below = sum(SIZE[c] for c in CLASSES[i + 1:])
    size = dict(SIZE)
    for c in CLASSES[i + 1:]:
        size[c] = SIZE[c] * s / 100 * POOL0 / below
    size[x] = POOL0 - sum(size[c] for c in CLASSES if c != x)
    return size


def passes(sched, lv, lvl, x, size, only=None):
    waff = lv.loc[lvl, "waff_pct"] / 100
    wals = lv.loc[lvl, "wals_pct"] / 100
    for timing, cprk, path in combos():
        if only and only != (timing, cprk, path):
            continue
        cpr = CPR_HIGH[lvl] if cprk == "high" else CPR_LOW
        df = run(sched, lvl, waff, wals, timing, cpr, path, size)
        short, u, ash = results(df)
        if short[x] > 0.005 or (x == "A" and ash > 0.005):
            return False
    return True


def needed(sched, lv, lvl, x, only=None):
    """Smallest credit enhancement (subordination + reserve, to
    0.01% of pool) at which class x passes every scenario at
    rating level lvl (bisection)."""
    lo, hi = 0, 3000                  # hundredths of a per cent
    while hi - lo > 1:
        mid = (lo + hi) // 2
        sub = mid / 100 - RF_PCT
        if sub >= 0 and passes(sched, lv, lvl, x,
                               resize(x, sub), only):
            hi = mid
        else:
            lo = mid
    return hi / 100

if __name__ == "__main__":
    sched = pd.read_csv(sys.argv[1])
    lv = pd.read_csv(sys.argv[2]).set_index("level")
    print("CE needed (% of pool) by scenario")
    print("Scenario          " + "".join(f"{l:>7}" for l in LEVELS))
    need = {l: [] for l in LEVELS}
    for cb in combos():
        cells = []
        for lvl, x in zip(LEVELS, RATED):
            n = needed(sched, lv, lvl, x, cb)
            need[lvl].append(n)
            cells.append(f"{n:7.2f}")
        print(f"{cb[0]:<6}{cb[1]:<5}{cb[2]:<7}" + "".join(cells))
    print("\nLevel Class  needed  available  cushion  worst case")
    labels = [" ".join(cb) for cb in combos()]
    for lvl, x in zip(LEVELS, RATED):
        n = max(need[lvl])
        w = labels[need[lvl].index(n)]
        print(f"{lvl:<5} {x:<5} {n:7.2f} {CE[x]:10.2f} "
              f"{CE[x] - n:8.2f}  {w}")
    r = all_runs(sched, lv)
    print("\nPass/fail on the Thames structure (8 scenarios)")
    print("Class " + " ".join(f"{l:>4}" for l in LEVELS))
    for c in RATED:
        cells = []
        for lvl in LEVELS:
            x = r[r.level == lvl]
            ok = (x[f"short_{c}"] < 0.005).all()
            if c == "A":
                ok = ok and (x["a_int_short"] < 0.005).all()
            cells.append("pass" if ok else "fail")
        print(f"{c:<5} " + " ".join(f"{v:>4}" for v in cells))
