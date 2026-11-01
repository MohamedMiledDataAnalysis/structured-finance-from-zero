"""Chapter 20 rating sensitivities: model-implied rating of each Thames class when the
rating-level WAFF and/or WALS of Chapter 18 are increased. Uses the Chapter 19 model.
Run from the book folder: python3 tools/ch20_sensitivity.py"""
import sys
import pandas as pd
sys.path.insert(0, "ch19/python")
import ch19_stress_cashflow as M

sched = pd.read_csv("data/ch19_thames_schedules.csv")
base = pd.read_csv("data/ch18_rating_level_results.csv").set_index("level")
cases = [("Base case", 1.00, 1.00), ("Defaults +15%", 1.15, 1.00), ("Severity +15%", 1.00, 1.15),
         ("Both +15%", 1.15, 1.15), ("Defaults +30%", 1.30, 1.00)]
print("Model-implied rating by class")
print(f"{'Sensitivity':<15}" + "".join(f"{c:>6}" for c in M.RATED))
for name, fw, fs in cases:
    lv = base.copy()
    lv["waff_pct"] = (base["waff_pct"] * fw).round(2)
    lv["wals_pct"] = (base["wals_pct"] * fs).clip(upper=100).round(2)
    cells = []
    for c in M.RATED:
        best = "<BB"
        for lvl in M.LEVELS:
            if M.passes(sched, lv, lvl, c, M.SIZE):
                best = lvl
                break
        cells.append(best)
    print(f"{name:<15}" + "".join(f"{v:>6}" for v in cells))
print("AAA WAFF at +15%:", f"{base.loc['AAA', 'waff_pct'] * 1.15:.2f}",
      " AAA WALS at +15%:", f"{base.loc['AAA', 'wals_pct'] * 1.15:.2f}")
lv = base.copy()
lv["waff_pct"] = (base["waff_pct"] * 1.15).round(2)
for lvl, c in (("AAA", "A"), ("AA", "B")):
    print(f"CE needed at {lvl}, defaults +15%: {M.needed(sched, lv, lvl, c):.2f}")
