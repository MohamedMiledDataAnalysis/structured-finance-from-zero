"""Chapter 8 - agreed-upon procedures: sample size,
systematic sample selection and upper error rates.
Run from the book folder:
  python3 ch08/python/ch08_aup_sample.py \
      data/thames_residential_2027_1_tape.csv"""
import sys, math
import pandas as pd
from scipy.stats import beta

t = pd.read_csv(sys.argv[1]).sort_values("loan_id")
t = t.reset_index(drop=True)
CONF, TOL = 0.99, 0.01        # confidence, tolerable error

# 1. Sample size with zero expected errors
n = math.ceil(math.log(1 - CONF) / math.log(1 - TOL))
N = len(t)
print(f"Pool: {N} loans, balance "
      f"{t.current_balance.sum():.2f}")
print(f"Sample size (99% confidence, 1% tolerable): {n}")

# 2. Systematic selection: start 3.2, interval N / n.
#    Integer arithmetic so every tool picks the same loans.
pos = [(32 * n + i * 10 * N) // (10 * n) for i in range(n)]
s = t.iloc[[p - 1 for p in pos]]
print(f"Interval {N / n:.4f}, first positions "
      + " ".join(str(p) for p in pos[:5]))
print("First loans: " + " ".join(s.loan_id[:3]))
sb = s.current_balance.sum()
print(f"Sample balance {sb:.2f} "
      f"({100 * sb / t.current_balance.sum():.2f}% of pool)")

# 3. Is the sample like the pool?
def profile(d):
    w = d.current_balance
    fx = d.product_type.isin(["2Y Fixed", "5Y Fixed"])
    oltv = 100 * d.original_balance / d.original_valuation
    return (100 * w[fx].sum() / w.sum(),
            (oltv * w).sum() / w.sum(),
            (d.current_rate * w).sum() / w.sum())
print("                       sample    pool")
for lab, a, b in zip(["fixed rate (% bal)", "WA original LTV",
                      "WA interest rate"],
                     profile(s), profile(t)):
    print(f"  {lab:<19}{a:9.2f}{b:8.2f}")

# 4. Upper error rate at 99% confidence (Clopper-Pearson)
print("Upper error rate, 99% confidence")
for k in range(3):
    u = beta.ppf(CONF, k + 1, n - k)
    print(f"  {k} errors in {n}: {100 * u:.3f}%")
