"""Writes data/ch14_base_case.csv: the Chapter 10 base case with UNROUNDED lifetime default and severity (so that
Thames defaults and losses equal the Deal Fact Sheets figures £9,273,541 and £1,547,181), the stated CPR 11.15% and
18-month lag, and the yearly default timing vector as published (2 decimals, sums to 100.00).
Runs ch10/python/ch10_history.py (output suppressed) to read its variables.
Run: python3 tools/gen_ch14_base_case.py"""
import contextlib, io, runpy, sys
sys.argv = ["ch10_history.py", "data/kingsbridge_static_pool_defaults.csv", "data/kingsbridge_dynamic_book.csv"]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path("ch10/python/ch10_history.py")
timing = [5.73, 11.07, 23.34, 28.88, 19.09, 8.01, 2.70, 0.84, 0.26, 0.08]
T = g["T"]; yr = [round(100 * (T[12 * k] - (T[12 * k - 12] if k > 1 else 0)), 2) for k in range(1, 11)]
assert yr == timing, (yr, timing)
assert round(g["base_def"], 2) == 1.46 and round(100 * g["base_sev"], 2) == 16.68 and g["lag"] == 18
rows = [("lifetime_default_pct", repr(float(g["base_def"]))), ("severity_pct", repr(float(100 * g["base_sev"]))),
        ("lag_months", "18"), ("cpr_pct", "11.15")] + [(f"timing_year_{k}", f"{v:.2f}") for k, v in enumerate(timing, 1)]
with open("data/ch14_base_case.csv", "w") as f:
    f.write("parameter,value\n" + "".join(f"{a},{b}\n" for a, b in rows))
print(open("data/ch14_base_case.csv").read())
