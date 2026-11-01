"""Chapters 25-26: extension of the Thames performance simulation.
Re-runs EXACTLY the loan-level simulation of tools/gen_thames_performance.py
(same seed 20261102, same random draws) for 25 months instead of 24, and:
  1. asserts that the first 24 pool-level rows equal data/thames_performance_monthly.csv;
  2. writes data/ch26_thames_performance_2029_02.csv  (the 25th collection period, Feb 2029,
     needed for the 8th IPD, 15 March 2029);
  3. writes data/ch25_thames_arrears_states.csv  (one row per loan: months in arrears at cut-off
     and at the end of each month Feb 2027 - Jan 2029; -1 = redeemed, -2 = possession sold);
  4. writes data/ch25_thames_repossessions.csv  (one row per property sold, Feb 2027 - Jan 2029).
Run from the book folder:  python3 tools/gen_ch25_ch26_thames_extension.py data
"""
import sys
import numpy as np, pandas as pd
D = sys.argv[1]; rng = np.random.default_rng(20261102)
t = pd.read_csv(f"{D}/thames_residential_2027_1_tape.csv")
n = len(t)
bal = t.current_balance.to_numpy(float).copy()
rate = t.current_rate.to_numpy(float)/1200
rem = t.remaining_term_months.to_numpy(int).copy()
rep = t.repayment_type.to_numpy()
prod = t.product_type.to_numpy()
fend = pd.to_datetime(t.fixed_rate_end_date)
val = t.original_valuation.to_numpy(float)
state = np.zeros(n, int)
state[:] = t.months_in_arrears.to_numpy()
arrears_amt = np.zeros(n)
months = pd.period_range("2027-02", "2029-02", freq="M")      # 25 months (was 24)
hpi = 1.0
rows = []; states = {"s2027_01": state.copy()}; repo_rows = []
for mi, per in enumerate(months):
    hpi *= 1.02 ** (1/12)
    open_bal = bal[state >= 0].sum(); open_n = int((state >= 0).sum())
    sched = pre = intr = defaults = recov = loss = arr_rec = 0.0; redeemed = repos = 0
    for i in range(n):
        if state[i] < 0: continue
        b = bal[i]; r = rate[i]
        if rep[i] == "Interest-only": due_p = 0.0
        elif rep[i] == "Part and part":
            half = t.original_balance.iat[i]/2; io_part = half
            amort = max(b - io_part, 0)
            due_p = amort*r/(1-(1+r)**-max(rem[i],1)) - amort*r if amort > 0 else 0.0
        else:
            due_p = b*r/(1-(1+r)**-max(rem[i],1)) - b*r
        due_i = b*r
        if state[i] == 0:
            if rng.random() < (0.0018 + (0.010 if t.original_balance.iat[i]/val[i] > 0.80 else 0.0)): state[i] = 1; arrears_amt[i] += due_i + due_p; continue
        else:
            if rng.random() < 0.20:
                intr += due_i + arrears_amt[i]*0.0; state[i] = 0; arrears_amt[i] = 0.0
            else:
                state[i] += 1; arrears_amt[i] += due_i + due_p
                if state[i] >= 12:
                    sale = val[i]*hpi*0.70*(1 - 0.05)
                    recov += min(sale, b); arr_rec += max(min(sale - b, arrears_amt[i]), 0.0); defaults += b; loss += max(b - sale, 0.0)
                    repo_rows.append(dict(collection_period=str(per), loan_id=t.loan_id.iat[i],
                        balance_at_sale=round(b, 2), arrears_owed=round(arrears_amt[i], 2),
                        original_valuation=val[i], hpi_index=round(hpi, 6),
                        gross_sale_price=round(val[i]*hpi*0.70, 2), sale_costs=round(round(val[i]*hpi*0.70, 2) - round(sale, 2), 2),
                        net_sale_proceeds=round(sale, 2), principal_recovered=round(min(sale, b), 2),
                        arrears_interest_recovered=round(max(min(sale - b, arrears_amt[i]), 0.0), 2),
                        realised_loss=round(max(b - sale, 0.0), 2)))
                    state[i] = -2; repos += 1; bal[i] = 0.0
                continue
        if state[i] != 0: continue
        intr += due_i; sched += due_p; b -= due_p; rem[i] -= 1
        cpr = 0.07
        if prod[i] in ("2Y Fixed","5Y Fixed") and pd.Timestamp(fend.iat[i]).to_period("M") == per: cpr = 0.55
        smm = 1 - (1-cpr)**(1/12)
        if rng.random() < smm*0.85 or rem[i] <= 0:
            pre += b; b = 0.0; state[i] = -1; redeemed += 1
        elif rng.random() < 0.02:
            op = min(b, b*rng.uniform(0.01, 0.10)); pre += op; b -= op
        bal[i] = b
    live = state >= 0
    close_bal = bal[live].sum()
    def bucket(lo, hi): return bal[(state>=lo)&(state<=hi)].sum()/close_bal*100
    smm_obs = pre/(open_bal - sched) if open_bal > sched else 0
    rows.append(dict(collection_period=str(per), opening_balance=round(open_bal,2), loans_opening=open_n,
        interest_collected=round(intr,2), scheduled_principal=round(sched,2), prepayments=round(pre,2),
        defaulted_balance=round(defaults,2), principal_recoveries=round(recov,2), arrears_interest_recovered=round(arr_rec,2), realised_losses=round(loss,2),
        closing_balance=round(close_bal,2), loans_closing=int(live.sum()), loans_redeemed=redeemed, repossessions_sold=repos,
        arrears_1_3m_pct=round(bucket(1,3),3), arrears_3_6m_pct=round(bucket(4,6),3), arrears_6m_plus_pct=round(bucket(7,99),3),
        cpr_annualised_pct=round((1-(1-smm_obs)**12)*100,2), hpi_index=round(hpi,4)))
    states["s" + str(per).replace("-", "_")] = state.copy()

out = pd.DataFrame(rows)
pub = pd.read_csv(f"{D}/thames_performance_monthly.csv")
mine = pd.read_csv(pd.io.common.StringIO(out.iloc[:24].to_csv(index=False)))
assert list(mine.columns) == list(pub.columns)
assert mine.equals(pub), "first 24 months differ from the published file"
out.iloc[24:].to_csv(f"{D}/ch26_thames_performance_2029_02.csv", index=False)
st = pd.DataFrame({"loan_id": t.loan_id})
for k, v in states.items():
    if k != "s2029_02": st[k] = v
st.to_csv(f"{D}/ch25_thames_arrears_states.csv", index=False)
rp = pd.DataFrame(repo_rows)
rp[rp.collection_period <= "2029-01"].to_csv(f"{D}/ch25_thames_repossessions.csv", index=False)
print("First 24 months identical to thames_performance_monthly.csv: OK")
print(out.iloc[24:].T.to_string())
print(rp.to_string())
