"""Chapter 29 - surveillance of Thames Residential 2027-1
after the IPD of 15 March 2029. Run from the book folder:
  python3 ch29/python/ch29_surveillance.py \
      data/thames_ipd_results.csv [--plot]
Reads the other inputs from the same folder."""
import os, sys
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

D = os.path.dirname(sys.argv[1])
ipd = pd.read_csv(sys.argv[1])
perf = pd.concat([
    pd.read_csv(f"{D}/thames_performance_monthly.csv"),
    pd.read_csv(f"{D}/ch26_thames_performance_2029_02.csv")],
    ignore_index=True)
req = pd.read_csv(f"{D}/ch29_required_ce.csv")
book = pd.read_csv(f"{D}/kingsbridge_dynamic_book.csv")

POOL0, RESERVE = 635_671_146.31, 9_391_500.00
CLS = ["a", "b", "c", "d", "e", "z"]
RATING = {"a": "AAA(sf)", "b": "AA(sf)", "c": "A(sf)",
          "d": "BBB(sf)", "e": "BB(sf)"}

def round2(x):
    return float(Decimal(repr(float(x))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP))

# Chapter 10 base case, spread evenly within each year
DEFAULTS, SEV, LAG = 9_273_541.00, 0.166838, 18
TIMING = [5.73, 11.07, 23.34, 28.88, 19.09,
          8.01, 2.70, 0.84, 0.26, 0.08]
DEF = [round2(DEFAULTS * TIMING[k // 12] / 1200)
       for k in range(120)]
LOSS = [round2(d * SEV) for d in DEF]

def base_case(t):
    """Cumulative base-case default and loss, % of
    cut-off pool, after t months."""
    dft = sum(DEF[:t])
    los = sum(LOSS[:max(t - LAG, 0)])
    return 100 * dft / POOL0, 100 * los / POOL0

def ce(row, pool):
    """CE of each rated class, % of pool: classes
    below it plus the reserve."""
    out = {}
    for i, c in enumerate(CLS[:-1]):
        below = sum(row[f"class_{x}_balance_after"]
                    for x in CLS[i + 1:])
        out[c] = 100 * (below + RESERVE) / pool
    return out

# monthly collateral indicators
perf["arr3"] = perf.arrears_3_6m_pct + perf.arrears_6m_plus_pct
perf["cum_loss"] = 100 * perf.realised_losses.cumsum() / POOL0
perf["base_loss"] = [base_case(t)[1]
                     for t in range(1, len(perf) + 1)]
last = perf.iloc[-1]
cdef = 100 * perf.defaulted_balance.sum() / POOL0
b26 = book[book.month.str.startswith("2026")]
bk3 = (b26.arrears_3_6m_pct + b26.arrears_6_12m_pct
       + b26.arrears_12m_plus_pct).mean()
bd, bl = base_case(len(perf))
now = ipd.iloc[-1]
print("THAMES RESIDENTIAL 2027-1  surveillance after IPD",
      now.ipd)
print(f"Pool balance        : {last.closing_balance:,.2f}"
      f"  factor {100 * last.closing_balance / POOL0:.2f}%")
print(f"Loans               : {last.loans_closing:,}")
print(f"Cum. defaults       : "
      f"{perf.defaulted_balance.sum():,.2f} = {cdef:.4f}%")
print(f"  base case month {len(perf)}: {bd:.4f}%"
      f"  actual/base {100 * cdef / bd:.0f}%")
print(f"Cum. net loss       : "
      f"{perf.realised_losses.sum():,.2f}"
      f" = {last.cum_loss:.4f}%")
print(f"  base case month {len(perf)}: {bl:.4f}%"
      f"  actual/base {100 * last.cum_loss / bl:.0f}%")
sev = perf.realised_losses.sum() / perf.defaulted_balance.sum()
print(f"Severity to date    : {100 * sev:.2f}%"
      f"  (base {100 * SEV:.2f}%)")
el = 100 * sum(LOSS) / POOL0
print(f"Share of lifetime EL: {100 * last.cum_loss / el:.1f}%"
      f" of {el:.4f}%")
print(f"3m+ arrears         : {last.arr3:.3f}%"
      f"  (Kingsbridge book 2026: {bk3:.3f}%)")
print(f"CPR 3m / 12m average: "
      f"{perf.cpr_annualised_pct.tail(3).mean():.2f}% / "
      f"{perf.cpr_annualised_pct.tail(12).mean():.2f}%"
      "  (base 11.15%)")

print("\nIPD         factor   CE A   CE B   CE C   CE D   CE E")
hist = []
for _, r in ipd.iterrows():
    e = ce(r, r.pool_balance_end)
    hist.append(e)
    print(f"{r.ipd}  {100 * r.pool_balance_end / POOL0:6.2f}%"
          + "".join(f"{e[c]:7.2f}" for c in CLS[:-1]))

xs = (ipd.r16_class_z_pdl + ipd.r17_sub_swap_termination
      + ipd.r18_sub_loan_interest
      + ipd.r18_sub_loan_principal
      + ipd.r19_deferred_consideration)
print("\nIPD         reserve        PDL     excess spread")
for i, r in ipd.iterrows():
    pdl = sum(r[f"pdl_{c}_after"] for c in CLS)
    print(f"{r.ipd}  {r.reserve_balance_after:,.2f}"
          f"  {pdl:6.2f}  {xs[i]:14,.2f}")

print("\nTrigger checks at", now.ipd)
yn = lambda t: "YES" if t else "NO"
pdl = sum(now[f"pdl_{c}_after"] for c in CLS)
print("  Reserve at required amount :",
      yn(now.reserve_balance_after >= RESERVE))
print("  All PDL sub-ledgers at zero:", yn(pdl == 0))
print("  Reserve ever drawn         :",
      yn(ipd.reserve_drawn.sum() > 0))
print("  Principal paid interest    :",
      yn(ipd.principal_addition_amounts.sum() > 0))
print("  Pool above clean-up (10%)  :",
      yn(now.pool_balance_end > 0.10 * POOL0))

print("\nRating test, required CE (illustrative)")
print("Class  rating   CE now  passes   cushion")
cur = hist[-1]
for c in CLS[:-1]:
    ok = req[req.surveillance_required_ce_pct <= cur[c]]
    top = ok.iloc[0]
    print(f"  {c.upper()}    {RATING[c]:8s} {cur[c]:6.2f}  "
          f"{top.rating:8s} "
          f"{cur[c] - top.surveillance_required_ce_pct:5.2f}")

# classes below AAA: IPDs to reach the next category
print("\nNext category  gain/IPD   gap   IPDs needed")
order = list(req.rating)
for c in ["c", "d", "e"]:
    nxt = order[order.index(RATING[c]) - 1]
    need = req.loc[req.rating == nxt,
                   "surveillance_required_ce_pct"].iloc[0]
    step = (hist[-1][c] - hist[-5][c]) / 4
    gap = need - cur[c]
    print(f"  {c.upper()} to {nxt:8s}  {step:7.4f}  {gap:5.2f}"
          f"  {-(-gap // step):4.0f}")

if "--plot" in sys.argv:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    NAVY, GREY = "#1F2A44", "#8a8a85"
    COL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
           "#e87ba4"]
    x = pd.PeriodIndex(perf.collection_period,
                       freq="M").to_timestamp()
    xi = pd.to_datetime(ipd.ipd)
    fig, ax = plt.subplots(3, 2, figsize=(6.6, 7.6))
    fig.subplots_adjust(hspace=0.55, wspace=0.32,
                        left=0.09, right=0.97,
                        top=0.95, bottom=0.06)
    def style(a, title, unit):
        a.set_title(title, fontsize=9, loc="left",
                    color=NAVY, fontweight="bold")
        a.set_ylabel(unit, fontsize=7, color=GREY)
        a.tick_params(labelsize=6.5, colors="#52514e")
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.grid(axis="y", color="#e5e4df", lw=0.6)
        a.set_axisbelow(True)
    a = ax[0, 0]
    a.plot(x, perf.arrears_1_3m_pct, color=COL[0], lw=1.6,
           label="1-3 months")
    a.plot(x, perf.arr3, color=NAVY, lw=1.6,
           label="3 months +")
    a.axhline(bk3, color=GREY, lw=1, ls="--",
              label="Book 3m+ (2026)")
    a.legend(fontsize=6, frameon=False)
    style(a, "Arrears", "% of pool")
    a = ax[0, 1]
    a.plot(x, perf.cpr_annualised_pct, color=NAVY, lw=1.6)
    style(a, "Prepayment rate (CPR)", "% a year")
    a = ax[1, 0]
    a.plot(x, perf.cum_loss, color=NAVY, lw=1.6,
           label="Actual")
    a.plot(x, perf.base_loss, color=GREY,
           lw=1.2, ls="--", label="Base case")
    a.legend(fontsize=6, frameon=False)
    style(a, "Cumulative net loss", "% of cut-off pool")
    a = ax[1, 1]
    for k, c in enumerate(CLS[:-1]):
        y = [h[c] for h in hist]
        a.plot(xi, y, color=COL[k], lw=1.6, marker="o",
               ms=2.5)
        a.text(xi.iloc[-1], y[-1], f" {c.upper()}",
               fontsize=6.5, va="center", color="#0b0b0b")
    style(a, "Credit enhancement by class", "% of pool")
    a = ax[2, 0]
    a.bar(xi, ipd.reserve_balance_after / 1e6, width=50,
          color=NAVY)
    a.set_ylim(0, 12)
    style(a, "Reserve fund", "GBP million")
    a = ax[2, 1]
    a.bar(xi, ipd.realised_losses / 1e3, width=50,
          color=COL[1], label="Debited")
    a.plot(xi, [sum(r[f"pdl_{c}_after"] for c in CLS) / 1e3
                for _, r in ipd.iterrows()], color=NAVY,
           lw=1.6, marker="o", ms=2.5,
           label="Balance after IPD")
    a.legend(fontsize=6, frameon=False)
    style(a, "Principal deficiency ledger", "GBP thousand")
    for a in ax.flat:
        for lab in a.get_xticklabels():
            lab.set_rotation(30)
    os.makedirs("ch29/figures", exist_ok=True)
    out = "ch29/figures/ch29_dashboard.png"
    fig.savefig(out, dpi=220, facecolor="white")
    from PIL import Image          # no alpha channel in print
    Image.open(out).convert("RGB").save(out)
    print("\nDashboard saved: ch29/figures/ch29_dashboard.png")
