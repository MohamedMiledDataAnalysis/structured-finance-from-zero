"""Thames Residential 2027-1: simulated monthly collateral performance, Feb 2027 - Jan 2029 (24 collection periods).
Loan-level simulation from the cut-off tape. Seed 20261102. Run: python3 gen_thames_performance.py <datadir>
Outputs: thames_performance_monthly.csv (pool level) and thames_sonia_assumption.csv (illustrative compounded SONIA)."""
import sys, csv
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
state = np.zeros(n, int)          # months in arrears (0 = performing); -1 = redeemed; -2 = repossessed & sold
state[:] = t.months_in_arrears.to_numpy()
arrears_amt = np.zeros(n)
months = pd.period_range("2027-02", "2029-01", freq="M")
hpi = 1.0
rows = []
for mi, per in enumerate(months):
    hpi *= 1.02 ** (1/12)
    open_bal = bal[state >= 0].sum(); open_n = int((state >= 0).sum())
    sched = pre = intr = defaults = recov = loss = arr_rec = 0.0; redeemed = repos = 0
    for i in range(n):
        if state[i] < 0: continue
        b = bal[i]; r = rate[i]
        # payment due
        if rep[i] == "Interest-only": due_p = 0.0
        elif rep[i] == "Part and part":
            half = t.original_balance.iat[i]/2; io_part = half
            amort = max(b - io_part, 0)
            due_p = amort*r/(1-(1+r)**-max(rem[i],1)) - amort*r if amort > 0 else 0.0
        else:
            due_p = b*r/(1-(1+r)**-max(rem[i],1)) - b*r
        due_i = b*r
        # arrears transitions
        if state[i] == 0:
            if rng.random() < (0.0018 + (0.010 if t.original_balance.iat[i]/val[i] > 0.80 else 0.0)): state[i] = 1; arrears_amt[i] += due_i + due_p; continue
        else:
            if rng.random() < 0.20:         # cure
                intr += due_i + arrears_amt[i]*0.0; state[i] = 0; arrears_amt[i] = 0.0
            else:
                state[i] += 1; arrears_amt[i] += due_i + due_p
                if state[i] >= 12:           # repossession sold this month
                    sale = val[i]*hpi*0.70*(1 - 0.05)          # 30% forced-sale discount, 5% costs
                    claim = b + arrears_amt[i]
                    recov += min(sale, b); arr_rec += max(min(sale - b, arrears_amt[i]), 0.0); defaults += b; loss += max(b - sale, 0.0)
                    state[i] = -2; repos += 1; bal[i] = 0.0
                continue
        if state[i] != 0: continue
        intr += due_i; sched += due_p; b -= due_p; rem[i] -= 1
        # prepayment: base 7% CPR, spike at fixed-rate end (refinance), seasonality
        cpr = 0.07
        if prod[i] in ("2Y Fixed","5Y Fixed") and pd.Timestamp(fend.iat[i]).to_period("M") == per: cpr = 0.55
        smm = 1 - (1-cpr)**(1/12)
        if rng.random() < smm*0.85 or rem[i] <= 0:
            pre += b; b = 0.0; state[i] = -1; redeemed += 1
        elif rng.random() < 0.02:                      # partial overpayment
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
pd.DataFrame(rows).to_csv(f"{D}/thames_performance_monthly.csv", index=False)
# illustrative compounded SONIA per interest period (annualised %) and swap
ipds = ["2027-06-15","2027-09-15","2027-12-15","2028-03-15","2028-06-15","2028-09-15","2028-12-15","2029-03-15"]
son = [3.75,3.75,3.70,3.60,3.50,3.50,3.45,3.40]
pd.DataFrame(dict(interest_payment_date=ipds, compounded_sonia_pct=son)).to_csv(f"{D}/thames_sonia_assumption.csv", index=False)
print(pd.DataFrame(rows)[["collection_period","opening_balance","prepayments","realised_losses","closing_balance","cpr_annualised_pct","arrears_1_3m_pct"]].to_string())
