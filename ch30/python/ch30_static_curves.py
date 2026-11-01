"""Chapter 30 - figure: cumulative net loss curves of Rheinwagen
static pools, averaged by year of origination (balance-weighted).
Run from the book folder:
  python3 ch30/python/ch30_static_curves.py \\
      data/rheinwagen_static_pool_losses.csv ch30/ch30_static_curves.png
"""
import sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

s = pd.read_csv(sys.argv[1])
s["year"] = s.vintage.str[:4]
s["w"] = s.originated_balance * s.cumulative_net_loss_pct
g = s.groupby(["year", "months_since_origination"])
curve = (g.w.sum() / g.originated_balance.sum()).unstack(0)
# keep only ages seen by all 12 vintages of the year, so the
# average is not distorted by a changing mix of vintages
full = g.vintage.nunique().unstack(0) == 12
curve = curve.where(full)
curve = curve.loc[:72]

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8})
fig, ax = plt.subplots(figsize=(4.4, 2.8), dpi=300)
GREY, HL = "#b4b2ab", {"2022": "#2a78d6", "2023": "#eb6834"}
for y in curve.columns:
    c = curve[y].dropna()
    col = HL.get(y, GREY)
    ax.plot(c.index, c.values, color=col, lw=2 if y in HL else 1.2,
            zorder=3 if y in HL else 2)
    if y in HL or y in ("2019", "2020", "2021", "2024"):
        ax.annotate(y, (c.index[-1], c.values[-1]),
                    xytext=(3, 0), textcoords="offset points",
                    va="center", color="#0b0b0b", fontsize=7)
ax.set_xlabel("Months since origination")
ax.set_ylabel("Cumulative net loss (% of originated)")
ax.set_xlim(0, 80)
ax.set_ylim(0, None)
ax.grid(axis="y", color="#e6e5e0", lw=0.6)
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)
fig.tight_layout()
fig.savefig(sys.argv[2])
print("saved", sys.argv[2])
