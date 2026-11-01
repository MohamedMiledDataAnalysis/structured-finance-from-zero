"""Chapter 14 - reusable cash-flow engine,
Thames Residential 2027-1.

Import from other chapters:
    sys.path.insert(0, "ch14/python"); import cashflow as cf

Conventions (stated in Chapter 14):
- month 1 = collection period Feb 2027 (cut-off 31 Jan 2027);
- loans amortise at their current rate over their remaining term
  (closed-form annuity balance, no monthly penny rounding);
- part-and-part loans: half the ORIGINAL balance is
  interest-only,
  the rest of the current balance amortises;
- base case (Chapter 10): lifetime default x cut-off balance,
  spread by year with the timing vector, evenly by month;
- order in each month: defaults, then scheduled principal,
  then prepayments (all proportional to the performing balance);
- recoveries arrive `lag` months after default; the loss
  (severity x default) is cured by excess spread through
  the PDL, so the notes receive the full defaulted amount
  at recovery time;
- IPD 1 (15 Jun 2027) pays months 1-4; IPD k>1 pays 3k-1..3k+1;
- WAL in years from closing (18 Mar 2027), Actual/365,
  unadjusted IPD dates (the 15th).
"""
from datetime import date
import numpy as np
import pandas as pd

CLOSING = date(2027, 3, 18)
CLASSES = [("A", 553_000_000.00), ("B", 31_800_000.00),
           ("C", 19_100_000.00), ("D", 12_700_000.00),
           ("E", 9_500_000.00), ("Z", 9_571_146.31)]
CALL_IPD = 20          # 15 March 2032 = IPD number 20
H = 433                # months projected (to Feb 2063)


def load_tape(path):
    t = pd.read_csv(path)
    io_part = np.where(t.repayment_type == "Interest-only",
                       t.current_balance, 0.0)
    pp = t.repayment_type == "Part and part"
    io_part = np.where(pp, t.original_balance / 2, io_part)
    t["io_part"] = io_part
    t["rep_part"] = t.current_balance - t.io_part
    t["r"] = t.current_rate / 1200
    t["n"] = t.remaining_term_months
    end = pd.to_datetime(t.fixed_rate_end_date)
    t["fix_end_m"] = ((end.dt.year - 2027) * 12
                      + end.dt.month - 1)       # Feb 2027 -> 1
    return t


def sched_balance(t, months=H, only=None):
    """Scheduled (0% CPR, 0% CDR) balance at the end of
    months 0..months, summed over the loans of the tape."""
    k = np.arange(months + 1)[:, None]          # months x loans
    r, n = t.r.values[None, :], t.n.values[None, :]
    g = (1 + r) ** n
    rep = t.rep_part.values * (g - (1 + r) ** k) / (g - 1)
    alive = k < n
    bal = (rep + t.io_part.values) * alive
    if only is not None:                 # e.g. fixed only
        bal = bal * only(k)
    return bal.sum(axis=1)


def fixed_sched_balance(t, months=H):
    """Scheduled balance of loans in their fixed period."""
    isfix = t.product_type.str.contains("Fixed").values
    m_end = t.fix_end_m.fillna(0).values
    return sched_balance(
        t, months, only=lambda k: isfix & (k < m_end))


def smm(annual_pct):
    return 1 - (1 - annual_pct / 100) ** (1 / 12)


def load_base(path, S0, months=H):
    """Chapter 10 base case: lifetime default (% of the cut-off
    balance) spread by the yearly timing vector, evenly
    across the months of each year."""
    b = pd.read_csv(path, index_col=0).value
    life = b.lifetime_default_pct / 100 * S0
    dvec = np.zeros(months + 1)
    for y in range(1, 11):
        share = b[f"timing_year_{y}"] / 100
        dvec[12 * y - 11: 12 * y + 1] = life * share / 12
    return dict(cpr=b.cpr_pct, sev=b.severity_pct,
                lag=int(b.lag_months), dvec=dvec)


def project_pool(S, cpr, cdr=0.0, sev=0.0, lag=0, dvec=None):
    """Monthly projection of the pool from schedule S. Defaults
    come from a CDR or from a vector of amounts (dvec)."""
    m_pre, m_def = smm(cpr), smm(cdr)
    n = len(S) - 1
    B = np.zeros(n + 1); B[0] = S[0]
    D, Sch, P = (np.zeros(n + 1) for _ in range(3))
    for m in range(1, n + 1):
        D[m] = (m_def * B[m - 1] if dvec is None
                else min(dvec[m], B[m - 1]))
        f = 1 - S[m] / S[m - 1] if S[m - 1] > 0 else 1.0
        Sch[m] = (B[m - 1] - D[m]) * f
        P[m] = m_pre * (B[m - 1] - D[m] - Sch[m])
        B[m] = B[m - 1] - D[m] - Sch[m] - P[m]
    Dlag = np.concatenate([np.zeros(lag), D])[: n + 1]
    rec, loss = (1 - sev / 100) * Dlag, sev / 100 * Dlag
    return pd.DataFrame({"month": np.arange(n + 1),
        "balance": B, "defaults": D, "scheduled": Sch,
        "prepaid": P, "recoveries": rec, "losses": loss,
        "to_notes": Sch + P + rec + loss})


def ipd_date(k):
    m = 6 + 3 * (int(k) - 1)            # IPD 1 = June 2027
    return date(2027 + (m - 1) // 12, (m - 1) % 12 + 1, 15)


def ipd_of_month(m):
    return 1 if m <= 4 else (m - 2) // 3 + 1


def project_notes(pool, call=False):
    """Sequential A->Z principal waterfall on each IPD."""
    pool = pool[pool.month >= 1]
    k = pool.month.map(ipd_of_month)
    avail = pool.groupby(k).to_notes.sum()
    bal = dict(CLASSES)
    rows = []
    for ipd, cash in avail.items():
        row = {"ipd": ipd, "date": ipd_date(ipd),
               "available": cash}
        for c, _ in CLASSES:
            pay = min(bal[c], cash)
            if call and ipd == CALL_IPD:
                pay = bal[c]                    # redeem at par
            bal[c] -= pay; cash = max(cash - pay, 0)
            row[c] = pay
        rows.append(row)
        if call and ipd == CALL_IPD:
            break
    return pd.DataFrame(rows)


def wal_and_maturity(notes):
    t = notes.date.map(lambda d: (d - CLOSING).days / 365)
    out = {}
    for c, amt in CLASSES:
        paid = notes[c]
        last = notes.date[paid > 0.005].iloc[-1]
        out[c] = ((paid * t).sum() / paid.sum(), last)
    return out


def rep_lines(t, keys):
    """Collapse the tape into representative lines: sums of the
    balances, balance-weighted rate and remaining term."""
    t = t.copy(); t["w"] = t.current_balance
    g = t.groupby(keys)
    rl = pd.DataFrame({
        "current_balance": g.current_balance.sum(),
        "rep_part": g.rep_part.sum(),
        "io_part": g.io_part.sum(),
        "r": g.apply(lambda x: (x.r * x.w).sum() / x.w.sum(),
                     include_groups=False),
        "n": g.apply(lambda x: round((x.n * x.w).sum()
                     / x.w.sum()), include_groups=False)})
    return rl.reset_index()
