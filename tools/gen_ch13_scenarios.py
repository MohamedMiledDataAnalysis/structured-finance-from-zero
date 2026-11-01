"""Write data/ch13_illustrative_scenarios.csv: three ILLUSTRATIVE quarters for the Chapter 13 waterfall engine.
No randomness (fixed inputs). These are NOT Thames IPDs: the real IPDs are computed in Chapter 26.
Run from the book folder: python3 tools/gen_ch13_scenarios.py"""
import csv
notes = {"A": "497328853.69", "B": "31800000.00", "C": "19100000.00", "D": "12700000.00", "E": "9500000.00", "Z": "9571146.31"}
common = dict(days=92, sonia="3.75", swap_notional="490000000.00", subloan="6000000.00", subloan_unpaid_int="0.00",
              **{f"note_{c}": v for c, v in notes.items()}, **{f"def_{c}": "0.00" for c in "BCDE"})
rows = [
    dict(scenario="normal", pool="580000000.00", reserve="9391500.00", revenue="6520000.00", sched_principal="3700000.00",
         prepayments="12800000.00", recoveries="0.00", losses="0.00",
         pdl_A="0.00", pdl_B="0.00", pdl_C="0.00", pdl_D="0.00", pdl_E="0.00", pdl_Z="0.00"),
    dict(scenario="stressed", pool="572000000.00", reserve="9391500.00", revenue="5700000.00", sched_principal="3200000.00",
         prepayments="7500000.00", recoveries="2500000.00", losses="3000000.00",
         pdl_A="0.00", pdl_B="0.00", pdl_C="0.00", pdl_D="0.00", pdl_E="0.00", pdl_Z="8000000.00"),
    dict(scenario="severe", pool="565000000.00", reserve="400000.00", revenue="4300000.00", sched_principal="3000000.00",
         prepayments="4000000.00", recoveries="3000000.00", losses="4000000.00",
         pdl_A="0.00", pdl_B="0.00", pdl_C="0.00", pdl_D="0.00", pdl_E="5428853.69", pdl_Z="9571146.31"),
]
cols = ["scenario", "days", "sonia", "pool", "revenue", "sched_principal", "prepayments", "recoveries", "losses", "swap_notional",
        "reserve", "subloan", "subloan_unpaid_int"] + [f"note_{c}" for c in notes] + [f"pdl_{c}" for c in notes] + [f"def_{c}" for c in "BCDE"]
with open("data/ch13_illustrative_scenarios.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
    for r in rows: w.writerow({**common, **r})
print("wrote data/ch13_illustrative_scenarios.csv")
