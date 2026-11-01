"""Thames Residential 2027-1 waterfall engine (Chapter 13).

Reusable by later chapters (Chapter 26 runs the real IPDs).
All money is decimal.Decimal; every amount is rounded to the
penny with ROUND_HALF_UP, exactly as Excel's ROUND does.

Interface
---------
    from waterfall import THAMES_TERMS, State, Period
    from waterfall import run_ipd, run_post_enforcement

    state = State(pool=..., notes={...}, pdl={...},
                  deferred={...}, reserve=..., subloan=...)
    period = Period(days=92, sonia=Decimal("3.75"),
                    revenue=..., sched_principal=...,
                    prepayments=..., recoveries=...,
                    losses=..., swap_notional=...)
    res = run_ipd(state, period)          # pre-enforcement
    res["lines"]      list of (item, label, due, paid)
    res["principal"]  list of (label, paid)
    res["state"]      State after the IPD (input to next IPD)
    res["info"]       dict: available revenue, PAA, reserve,
                      PDL debits/credits, shortfalls, EoD flag,
                      balance check (notes - PDL - pool), ...

Conventions (stated in Chapter 13)
----------------------------------
* State = balances at the start of the interest period, i.e.
  after the previous IPD. `pool` is the opening pool balance of
  the collection periods paid on this IPD.
* Note interest, swap and fees accrue Actual/365 on opening
  balances: amount = round2(balance x rate% / 100 x days / 365).
  Fixed annual fees accrue the same way. Issuer profit is a flat
  GBP 1,000 per IPD. Class Z pays no interest.
* Swap: net = notional x (fixed - SONIA) x days/365. Positive:
  the issuer pays it at item (4). Negative: the issuer receives
  it and it is part of revenue receipts.
* Available revenue receipts = revenue collections + net swap
  receipt + other revenue + general reserve fund balance.
* Principal receipts = scheduled principal + prepayments +
  principal recoveries. Realised losses are debited to the PDL.
* Principal addition amounts (PAA) cover any shortfall of
  available revenue receipts for items (1)-(4) and the interest
  of Class A (or of Class B while it is the most senior class
  outstanding). PAA are debited to the PDL.
* PDL debits go to sub-ledgers Z, E, D, C, B, A in turn, each
  capped at its class's outstanding balance.
* Interest not paid on Classes B-E while not the most senior
  class is deferred; deferred interest accrues interest at the
  class coupon. Unpaid interest on the most senior class sets
  info["eod_interest"] = True (issuer event of default after
  the 5-business-day grace period; the engine only flags it).
* General reserve required amount: GBP 9,391,500.00 while any
  Class A note is outstanding at the start of the period;
  otherwise max(1.50% of Classes A-E, GBP 3,000,000.00).
* Item (18) pays subordinated loan interest (SONIA + 4.00%,
  plus any unpaid interest from earlier IPDs), then repays
  subordinated loan principal from whatever revenue remains.
* Principal is applied strictly sequentially A, B, C, D, E, Z.
"""
from dataclasses import dataclass, field, replace
from decimal import Decimal as D, ROUND_HALF_UP

CLASSES = ["A", "B", "C", "D", "E", "Z"]
ZERO = D("0.00")


def round2(x):
    """Round to pennies, halves away from zero (Excel ROUND)."""
    return D(x).quantize(D("0.01"), rounding=ROUND_HALF_UP)


THAMES_TERMS = {
    "margins": {"A": D("0.62"), "B": D("1.10"), "C": D("1.50"),
                "D": D("2.20"), "E": D("3.50")},
    "swap_fixed": D("3.30"),
    "trustee_fee": D("25000"),
    # item (2), paid pro rata, in this order:
    "senior_fees": [("Paying agent, agent bank", D("10000")),
                    ("Corporate services", D("20000")),
                    ("Cash manager", D("50000")),
                    ("Servicer", None),   # 0.15% of pool
                    ("Other issuer expenses", D("120000"))],
    "servicing_pct": D("0.15"),
    "issuer_profit": D("1000"),
    "reserve_required": D("9391500.00"),
    "reserve_pct": D("1.50"),
    "reserve_floor": D("3000000.00"),
    "subloan_margin": D("4.00"),
}


@dataclass
class State:
    """Balances at the start of an interest period."""
    pool: D
    notes: dict
    pdl: dict = field(default_factory=lambda: {
        c: ZERO for c in CLASSES})
    deferred: dict = field(default_factory=lambda: {
        c: ZERO for c in CLASSES})
    reserve: D = ZERO
    subloan: D = ZERO
    subloan_unpaid_int: D = ZERO


@dataclass
class Period:
    """Collections and rates for one IPD."""
    days: int
    sonia: D                  # compounded SONIA, % p.a.
    revenue: D                # interest collected + arrears
    sched_principal: D        # interest recovered etc.
    prepayments: D
    recoveries: D             # principal recoveries
    losses: D                 # realised losses
    swap_notional: D
    other_revenue: D = ZERO   # e.g. account interest
    sub_swap_termination: D = ZERO


def accrue(balance, rate_pct, days):
    """Actual/365 accrual, rounded to the penny."""
    return round2(balance * rate_pct / 100 * days / 365) + ZERO


def _most_senior(notes):
    for c in CLASSES:
        if notes[c] > 0:
            return c
    return None


def _debit_pdl(pdl, notes, amount):
    """Debit `amount` to sub-ledgers Z, E, D, C, B, A, each
    capped at its class balance.
    Returns (new pdl, debits, unallocated)."""
    pdl, debits, left = dict(pdl), {}, amount
    for c in reversed(CLASSES):
        room = max(ZERO, notes[c] - pdl[c])
        d = min(room, left)
        debits[c] = d
        pdl[c] += d
        left -= d
    return pdl, debits, left


def interest_due(state, period, terms=THAMES_TERMS):
    """Interest due per class this IPD: current interest plus
    deferred interest plus interest on the deferred amount."""
    due = {}
    for c in CLASSES[:-1]:
        cpn = period.sonia + terms["margins"][c]
        due[c] = (accrue(state.notes[c], cpn, period.days)
                  + state.deferred[c]
                  + accrue(state.deferred[c], cpn, period.days))
    due["Z"] = ZERO
    return due


def fees_due(state, period, terms=THAMES_TERMS):
    """Items (1) and (2) for the period."""
    trustee = accrue(terms["trustee_fee"], D(100), period.days)
    group = []
    for name, annual in terms["senior_fees"]:
        if annual is None:
            amt = accrue(state.pool, terms["servicing_pct"],
                         period.days)
        else:
            amt = accrue(annual, D(100), period.days)
        group.append((name, amt))
    return trustee, group


def required_reserve(state, terms=THAMES_TERMS):
    if state.notes["A"] > 0:
        return terms["reserve_required"]
    a_e = sum(state.notes[c] for c in CLASSES[:-1])
    return max(round2(a_e * terms["reserve_pct"] / 100),
               terms["reserve_floor"])


def run_ipd(state, period, terms=THAMES_TERMS):
    """Run the pre-enforcement revenue and principal priorities
    of payments for one IPD. Returns a dict (see module doc)."""
    s = state
    info = {}
    # --- receipts ---------------------------------------------
    swap_net = accrue(period.swap_notional,
                      terms["swap_fixed"] - period.sonia,
                      period.days)        # >0: issuer pays
    swap_pay = max(swap_net, ZERO)
    swap_rec = max(-swap_net, ZERO)
    principal_receipts = (period.sched_principal
                          + period.prepayments
                          + period.recoveries)
    arr = (period.revenue + swap_rec + period.other_revenue
           + s.reserve)
    info.update(swap_receipt=swap_rec, swap_payment=swap_pay,
                principal_receipts=principal_receipts,
                available_revenue=arr)
    # --- amounts due ------------------------------------------
    trustee, group = fees_due(s, period, terms)
    idue = interest_due(s, period, terms)
    senior = _most_senior(s.notes)
    paa_class = senior if senior in ("A", "B") else None
    # --- principal addition amounts ---------------------------
    need = (trustee + sum(a for _, a in group)
            + terms["issuer_profit"] + swap_pay
            + (idue[paa_class] if paa_class else ZERO))
    paa = min(max(need - arr, ZERO), principal_receipts)
    info["paa"] = paa
    # --- PDL debits: losses and PAA ---------------------------
    pdl, debits, unalloc = _debit_pdl(s.pdl, s.notes,
                                      period.losses + paa)
    info.update(pdl_debits=debits, pdl_unallocated=unalloc)
    # --- revenue priority of payments -------------------------
    pot = arr + paa
    lines = []

    def pay(item, label, due):
        nonlocal pot
        paid = min(due, max(pot, ZERO))
        pot -= paid
        lines.append((item, label, due, paid))
        return paid

    pay("1", "Trustee fees", trustee)
    gdue = sum(a for _, a in group)
    gpaid = min(gdue, pot)
    for name, amt in group:
        p = amt if gpaid == gdue else round2(amt * gpaid / gdue)
        pot -= p
        lines.append(("2", name, amt, p))
    pay("3", "Issuer profit", terms["issuer_profit"])
    pay("4", "Swap net payment", swap_pay)
    paid_int, credits = {}, {}
    item = 5
    for c in CLASSES[:-1]:
        paid_int[c] = pay(str(item), f"Class {c} interest",
                          idue[c])
        credits[c] = pay(str(item + 1), f"Class {c} PDL",
                         pdl[c])
        item += 2
    req = required_reserve(s, terms)
    new_reserve = pay("15", "General reserve fund", req)
    credits["Z"] = pay("16", "Class Z PDL", pdl["Z"])
    pay("17", "Sub swap termination",
        period.sub_swap_termination)
    sub_int = (accrue(s.subloan, period.sonia
                      + terms["subloan_margin"], period.days)
               + s.subloan_unpaid_int)
    sub_int_paid = pay("18", "Sub loan interest", sub_int)
    sub_prin = pay("18", "Sub loan principal", s.subloan)
    dc = pot
    pot = ZERO
    lines.append(("19", "Deferred consideration", dc, dc))
    for c in CLASSES:
        pdl[c] -= credits[c]
    # --- interest shortfalls: deferral or event of default ----
    deferred = {c: ZERO for c in CLASSES}
    info["eod_interest"] = False
    for c in CLASSES[:-1]:
        short = idue[c] - paid_int[c]
        if short > 0 and c == senior:
            info["eod_interest"] = True
        deferred[c] = short
    info["interest_shortfall"] = deferred
    # --- principal priority of payments -----------------------
    apr = principal_receipts - paa + sum(credits.values())
    info["available_principal"] = apr
    info["pdl_credits"] = credits
    notes, plines = dict(s.notes), []
    plines.append(("Principal addition amounts", paa))
    for c in CLASSES:
        p = min(apr, notes[c])
        notes[c] -= p
        apr -= p
        plines.append((f"Class {c} principal", p))
    info["principal_left"] = apr
    # --- new state --------------------------------------------
    pool_close = (s.pool - principal_receipts - period.losses)
    new = State(pool=pool_close, notes=notes, pdl=pdl,
                deferred=deferred, reserve=new_reserve,
                subloan=s.subloan - sub_prin,
                subloan_unpaid_int=sub_int - sub_int_paid)
    info["reserve_required"] = req
    # positive = drawn, negative = replenished
    info["reserve_draw"] = s.reserve - new_reserve
    info["balance_check"] = (sum(notes.values())
                             - sum(pdl.values()) - pool_close)
    return {"lines": lines, "principal": plines, "state": new,
            "info": info}


def run_post_enforcement(state, period, terms=THAMES_TERMS):
    """Post-enforcement priority of payments: one pot of all
    receipts (revenue, principal, swap receipt, reserve) paid
    in the order trustee -> senior expenses (pro rata) ->
    swap -> for each class A..E: interest then full
    principal -> Class Z principal -> subordinated swap
    termination -> subordinated loan interest then principal
    -> deferred consideration.
    Returns {"lines": [(label, due, paid)],
             "pot_start": total receipts}."""
    s = state
    swap_net = accrue(period.swap_notional,
                      terms["swap_fixed"] - period.sonia,
                      period.days)
    pot = (period.revenue + period.other_revenue
           + period.sched_principal + period.prepayments
           + period.recoveries + max(-swap_net, ZERO)
           + s.reserve)
    start, lines = pot, []

    def pay(label, due):
        nonlocal pot
        paid = min(due, max(pot, ZERO))
        pot -= paid
        lines.append((label, due, paid))

    trustee, group = fees_due(s, period, terms)
    pay("Trustee fees", trustee)
    gdue = sum(a for _, a in group)
    gpaid = min(gdue, pot)
    for name, amt in group:
        p = amt if gpaid == gdue else round2(amt * gpaid / gdue)
        pot -= p
        lines.append((name, amt, p))
    pay("Swap net payment", max(swap_net, ZERO))
    idue = interest_due(s, period, terms)
    for c in CLASSES[:-1]:
        pay(f"Class {c} interest", idue[c])
        pay(f"Class {c} principal", s.notes[c])
    pay("Class Z principal", s.notes["Z"])
    pay("Sub swap termination",
        period.sub_swap_termination)
    pay("Sub loan interest",
        accrue(s.subloan,
               period.sonia + terms["subloan_margin"],
               period.days) + s.subloan_unpaid_int)
    pay("Sub loan principal", s.subloan)
    lines.append(("Deferred consideration", pot, pot))
    return {"lines": lines, "pot_start": start}
