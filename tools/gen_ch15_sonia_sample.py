"""Writes data/ch15_sonia_daily_sample.csv: ILLUSTRATIVE daily SONIA fixings (not real data) for the observation period
of a sample accrual period 1-15 June 2027, shifted 5 London business days (observation period 24 May - 8 June 2027;
31 May 2027 is the Spring bank holiday). 'days' = calendar days each fixing applies (to the next London business day,
or to the end of the observation period). Deterministic; no random numbers.
Run: python3 tools/gen_ch15_sonia_sample.py"""
from datetime import date, timedelta
hol = {date(2027, 5, 31)}
def bd(d): return d.weekday() < 5 and d not in hol
start, end = date(2027, 5, 24), date(2027, 6, 8)
rates = [3.7290, 3.7285, 3.7290, 3.7300, 3.7310, 3.7280, 3.7270, 3.7275, 3.7260, 3.7255]
days = [d for d in (start + timedelta(i) for i in range((end - start).days)) if bd(d)]
assert len(days) == len(rates)
with open("data/ch15_sonia_daily_sample.csv", "w") as f:
    f.write("observation_date,sonia_pct,days\n")
    for i, d in enumerate(days):
        nxt = days[i + 1] if i + 1 < len(days) else end
        f.write(f"{d:%d %b %Y},{rates[i]:.4f},{(nxt - d).days}\n")
print(open("data/ch15_sonia_daily_sample.csv").read())
