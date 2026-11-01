"""Chapter 10 - Kingsbridge historical performance data:
default timing curve, extrapolation of immature vintages,
default-to-loss lag, loss severity, CPR, arrears roll rates
and the base case handed to the structuring desk.
Run from the book folder:
  python3 ch10/python/ch10_history.py \
      data/kingsbridge_static_pool_defaults.csv \
      data/kingsbridge_dynamic_book.csv
Add --charts to redraw the PNG charts in ch10/img/."""
import sys
import numpy as np
import pandas as pd

s = pd.read_csv(sys.argv[1])
d = pd.read_csv(sys.argv[2])
grid = lambda col: s.pivot(index="months_since_origination",
                           columns="vintage", values=col)
cd, nl = grid("cumulative_default_pct"), \
         grid("cumulative_net_loss_pct")
vol = s.groupby("vintage").originated_balance.first()
last = s.groupby("vintage").months_since_origination.max()

# ---- 1. Timing curve from the fully seasoned vintages
MAT = [v for v in cd.columns if last[v] >= 120]
T = cd.loc[:120, MAT].div(cd.loc[120, MAT]).mean(axis=1)
print("Fully seasoned vintages:", ", ".join(MAT))
print("Timing curve (% of 120-month defaults):")
for a in range(12, 121, 12):
    print(f"  month {a:>3}: {100 * T[a]:6.2f}")

# ---- 2. Extrapolate every vintage to 120 months
age = last.clip(upper=120)
obs = pd.Series({v: cd.loc[age[v], v] for v in cd.columns})
life = obs / T[age].values
print("Extrapolated lifetime default (%):")
print("  vintage  age  observed  timing  lifetime")
for v in ["2016Q1", "2019Q1", "2022Q1", "2023Q4", "2024Q4",
          "2025Q4"]:
    print(f"  {v}  {age[v]:>3}  {obs[v]:8.4f}"
          f"  {100 * T[age[v]]:6.2f}  {life[v]:8.4f}")

# ---- 3. Default-to-loss lag: compare the half-way points
def half_age(col):
    """Age at which a curve reaches half its 120-month value
    (straight-line interpolation between quarterly points)."""
    x = col.loc[:120]
    target = x[120] / 2
    i = int(np.argmax(x.values >= target))
    a0, a1 = x.index[i - 1], x.index[i]
    y0, y1 = x.values[i - 1], x.values[i]
    return a0 + (target - y0) / (y1 - y0) * (a1 - a0)

lags = [half_age(nl[v]) - half_age(cd[v]) for v in MAT]
lag = round(float(np.mean(lags)))
print(f"Default-to-loss lag: {np.mean(lags):.2f} months"
      f" -> {lag} months")

# ---- 4. Loss severity: loss today / defaults lag months ago
sev = pd.Series({v: nl.loc[last[v], v] / cd.loc[last[v] - lag, v]
                 for v in cd.columns if last[v] >= 36})

# ---- 5. Base-case default and severity (balance-weighted)
use = life[last >= 24]
base_def = (use * vol[use.index]).sum() / vol[use.index].sum()
base_sev = (sev * vol[sev.index]).sum() / vol[sev.index].sum()
print(f"Vintages used for default: {len(use)};"
      f" for severity: {len(sev)}")
print(f"Base-case lifetime default (%): {base_def:.2f}")
print(f"Base-case loss severity (%):    {100 * base_sev:.2f}")

# ---- 6. CPR: average through SMM, and the reset months
cpr = d.cpr_annualised_pct / 100
smm = 1 - (1 - cpr) ** (1 / 12)
base_cpr = 1 - (1 - smm.mean()) ** 12
mon = d.month.str[5:].astype(int)
spike = mon.isin([3, 9])
print(f"CPR simple average (%):         {100 * cpr.mean():.2f}")
print(f"Base-case CPR via SMM (%):      {100 * base_cpr:.2f}")
print(f"CPR in Mar and Sep (%):         "
      f"{100 * cpr[spike].mean():.2f}")
print(f"CPR in other months (%):        "
      f"{100 * cpr[~spike].mean():.2f}")

# ---- 7. Roll-rate proxies from arrears stocks, 3 months apart
r1 = d.arrears_3_6m_pct / d.arrears_1_3m_pct.shift(3)
r2 = d.arrears_6_12m_pct / d.arrears_3_6m_pct.shift(3)
print(f"Roll 1-3m -> 3-6m (%):          {100 * r1.mean():.2f}")
print(f"Roll 3-6m -> 6-12m (%):         {100 * r2.mean():.2f}")
print(f"Base-case expected loss (%):    "
      f"{base_def * base_sev:.4f}")
POOL = 635671146.31   # Thames balance at cut-off
print(f"Thames base-case defaults (GBP):"
      f" {POOL * base_def / 100:,.0f}")
print(f"Thames base-case loss (GBP):    "
      f" {POOL * base_def * base_sev / 100:,.0f}")

if "--charts" in sys.argv:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    NAVY, GOLD, GREY = "#1F2A44", "#A8841A", "#B8BECB"
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False,
                         "axes.spines.right": False})
    # Chart 1: cumulative default curves by vintage
    fig, ax = plt.subplots(figsize=(5.2, 3.2))
    for v in cd.columns:
        y = cd[v].dropna()
        hot = v[:4] in ("2022", "2023")
        ax.plot(y.index, y.values, lw=1.4 if hot else 0.8,
                color=GOLD if hot else GREY, zorder=3 if hot else 1)
    for v in MAT:
        y = cd[v].dropna()
        ax.plot(y.index, y.values, lw=1.4, color=NAVY, zorder=2)
    ax.text(58, 2.05, "2022-2023 vintages", color=GOLD)
    ax.text(92, 0.62, "2016 vintages\n(fully seasoned)", color=NAVY)
    ax.text(86, 1.52, "other vintages", color="#6B7385")
    ax.set_xlabel("Months since origination")
    ax.set_ylabel("Cumulative default (% of originated)")
    ax.set_xlim(0, 132); ax.set_ylim(0, 2.5)
    ax.grid(axis="y", color="#E6E8EE", lw=0.6)
    fig.tight_layout(); fig.savefig("ch10/img/ch10_default_curves.png",
                                    dpi=200)
    # Chart 2: timing curve
    fig, ax = plt.subplots(figsize=(5.2, 2.7))
    ax.plot(T.index, 100 * T.values, color=NAVY, lw=2)
    for a in (24, 48, 60):
        ax.plot(a, 100 * T[a], "o", color=GOLD, ms=6)
        ax.annotate(f"{100 * T[a]:.2f}% at {a} m", (a, 100 * T[a]),
                    xytext=(8, -12), textcoords="offset points")
    ax.set_xlabel("Months since origination")
    ax.set_ylabel("% of 120-month defaults")
    ax.set_xlim(0, 122); ax.set_ylim(0, 105)
    ax.grid(axis="y", color="#E6E8EE", lw=0.6)
    fig.tight_layout(); fig.savefig("ch10/img/ch10_timing_curve.png",
                                    dpi=200)
    # Chart 3: CPR history with March and September highlighted
    fig, ax = plt.subplots(figsize=(5.2, 2.8))
    x = pd.to_datetime(d.month)
    ax.plot(x, 100 * cpr, color=NAVY, lw=1.1)
    ax.plot(x[spike], 100 * cpr[spike], "o", color=GOLD, ms=4,
            label="March and September")
    ax.axhline(100 * base_cpr, color=NAVY, ls="--", lw=0.8)
    ax.text(x.iloc[1], 4.6,
            f"dashed line: base case {100 * base_cpr:.2f}%",
            color=NAVY)
    ax.set_ylabel("CPR (% a year)")
    ax.set_ylim(4, 20); ax.legend(frameon=False, loc="upper right")
    ax.grid(axis="y", color="#E6E8EE", lw=0.6)
    fig.tight_layout(); fig.savefig("ch10/img/ch10_cpr_history.png",
                                    dpi=200)
