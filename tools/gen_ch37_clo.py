"""Chapter 37 - synthetic portfolio of the fictional CLO 'Calder Park CLO 1 DAC'.
Writes data/ch37_clo_portfolio.csv (one row per obligation) and
data/ch37_clo_notes.csv (capital structure and test triggers).
Fixed seed: the files are reproducible.
Run from the book folder: python3 tools/gen_ch37_clo.py"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(20261137)
N = 160
industries = ["Healthcare", "Business services", "Software", "Chemicals",
              "Leisure", "Telecoms", "Food and beverage", "Building materials",
              "Media", "Retail", "Industrial machinery", "Insurance services"]
countries = ["France", "Germany", "Netherlands", "United Kingdom", "Spain",
             "Italy", "Luxembourg", "Sweden", "Belgium", "Ireland"]
ratings = ["BB", "BB-", "B+", "B", "B-", "CCC+", "CCC", "CCC-"]
rating_p = [0.04, 0.06, 0.16, 0.34, 0.285, 0.055, 0.045, 0.015]

rows = []
used_ccc_prices = set()
for i in range(1, N + 1):
    rating = rng.choice(ratings, p=rating_p)
    par = float(rng.integers(140, 350)) * 10_000          # EUR 1.5m - 3.6m
    spread = int(rng.integers(300, 476) // 5 * 5)         # bps over 3M EURIBOR
    defaulted = "N"
    recovery = np.nan
    if rating.startswith("CCC"):
        while True:
            price = round(float(rng.uniform(58, 92)), 2)
            if price not in used_ccc_prices:
                used_ccc_prices.add(price)
                break
        spread += 125
    elif rating.startswith("BB"):
        price = round(float(rng.uniform(99.0, 100.75)), 2)
    else:
        price = round(float(rng.uniform(95.5, 100.5)), 2)
    rows.append([f"CP-{i:03d}", str(rng.choice(industries)),
                 str(rng.choice(countries)), rating, par, price, spread,
                 defaulted, recovery])

df = pd.DataFrame(rows, columns=["obligation_id", "industry", "country",
                                 "rating", "par_eur", "market_price_pct",
                                 "spread_bps", "defaulted", "recovery_rate_pct"])
# four defaulted obligations, carried at the lower of price and recovery rate
for idx, (price, rec) in zip([17, 44, 58, 101, 122, 140],
                             [(38.50, 45.0), (61.00, 45.0), (52.25, 45.0),
                              (31.75, 35.0), (44.25, 40.0), (47.00, 40.0)]):
    df.loc[idx, ["rating", "market_price_pct", "defaulted", "recovery_rate_pct"]] = \
        ["D", price, "Y", rec]
df.to_csv("data/ch37_clo_portfolio.csv", index=False, float_format="%.2f")

notes = pd.DataFrame({
    "class": ["A", "B", "C", "D", "E", "F", "Subordinated"],
    "balance_eur": [248_000_000, 40_000_000, 24_000_000, 28_000_000,
                    18_000_000, 12_000_000, 34_600_000],
    "margin_pct": [1.30, 1.95, 2.40, 3.40, 5.90, 8.25, None],
    "oc_trigger_pct": [None, 129.00, 120.00, 112.00, 106.00, 103.50, None],
    "ic_trigger_pct": [None, 120.00, 115.00, 110.00, None, None, None],
})
notes.to_csv("data/ch37_clo_notes.csv", index=False)
print(len(df), round(df.par_eur.sum(), 2))
