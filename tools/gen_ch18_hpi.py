"""Illustrative quarterly regional house price index, 2016Q1-2026Q4 (Chapter 18).
Synthetic data for teaching indexation; NOT an official index. Seed 20261117.
Run: python3 tools/gen_ch18_hpi.py data/ch18_regional_hpi.csv"""
import sys, csv
import numpy as np
rng = np.random.default_rng(20261117)
# national annual growth (%), by calendar year
nat = {2016: 4.5, 2017: 4.0, 2018: 2.5, 2019: 1.5, 2020: 6.0, 2021: 9.5,
       2022: 7.0, 2023: -2.0, 2024: 2.5, 2025: 2.0, 2026: 1.5}
# regional premium over national growth (% points per year)
prem = {"London": -1.2, "South East": -0.3, "East of England": -0.2,
        "South West": 0.2, "East Midlands": 0.5, "West Midlands": 0.5,
        "Wales": 0.6, "Yorkshire and the Humber": 0.6,
        "North West": 0.9, "North East": 0.4, "Scotland": 0.3,
        "Northern Ireland": 1.5}
rows = []
for reg, p in prem.items():
    idx = 100.0
    for y in range(2016, 2027):
        for q in range(1, 5):
            if not (y == 2016 and q == 1):
                g = (nat[y] + p) / 4 + rng.normal(0, 0.25)
                idx *= 1 + g / 100
            rows.append(dict(region=reg, quarter=f"{y}Q{q}",
                             hpi=round(idx, 1)))
with open(sys.argv[1], "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["region", "quarter", "hpi"])
    w.writeheader(); w.writerows(rows)
print(len(rows), "rows")
