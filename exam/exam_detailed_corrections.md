# Final Exam — Detailed Corrections

Medway Residential 2028-1 plc is fictional and every figure is illustrative. Every number below is printed by `exam/python/exam_solutions.py` (add `--diagnostics` for the figures of the wrong answers). The R script prints the same solution output, line for line, and `exam/excel/exam_solutions.xlsx` returns the same values with live formulas.

## How to use these corrections

1. **Attempt the whole exam first**, closed book, in the time allowed (165 minutes). A correction read before you attempt the question teaches you nothing: you recognise the answer, but you have not built it.
2. **Mark yourself against the answer key in the book** (the Final Exam's *Answer key*). Give the mark only when your figure matches to the penny or to the two decimals stated, and only when the working is visible. A right number typed into a cell scores zero, as on the desk: nobody can check it.
3. **Read the diagnosis of every wrong answer.** Each question below lists the wrong answers candidates give most often, as "*If you found X:*", with the mistake that produces X. Find your number in the list. If it is there, you know your mistake; fix it and redo the question. If it is not there, work through the step-by-step working line by line until your figure and mine part company: that line is your mistake.
4. **Read the reasoning even when you scored the mark.** The multiple-choice questions explain why each wrong option is wrong. A right answer reached by elimination or by luck fails at the desk, where nobody gives you four options.
5. **Revise the chapter named at the end of each question**, then redo the question without looking at the correction.

## Part A — Concepts

### A1. Monthly payment

**Answer: £1,375.19.**

1. Convert the annual rate to a monthly rate: $r = 4.80\% / 12 = 0.40\% = 0.004$.
2. Count the payments: $n = 300$ months.
3. Apply the annuity formula of Chapter 1: $\text{PMT} = P \times r / (1 - (1 + r)^{-n})$.
4. $\text{PMT} = 240{,}000 \times 0.004 / (1 - 1.004^{-300}) = £1{,}375.19$.

*If you found £960.00:* you calculated the interest only, $240{,}000 \times 0.004$. That is the payment of an interest-only mortgage; a repayment mortgage adds principal to it (Chapter 1).

*If you found £11,520.01:* you used 4.80% as the monthly rate. The rate in a mortgage offer is annual; divide it by 12 before the formula.

*If you found £1,390.74:* you calculated an annual annuity over 25 years and divided it by 12. Monthly payments reduce the balance every month, so less interest accrues: the monthly annuity is cheaper.

*If you found £1,760.00:* you added a straight-line principal of $240{,}000 / 300 = £800.00$ to the first month's interest. That is the first payment of a constant-principal loan, not of an annuity; a UK repayment mortgage pays a constant amount.

**Revise:** Chapter 1.

### A2. Class A interest for 92 days

**Answer: £52,679.45.**

1. Class A pays SONIA + 0.58%: $3.60\% + 0.58\% = 4.18\%$ a year.
2. Medway notes use Actual/365 (Fixed): the year fraction is $92/365$.
3. Interest $= 5{,}000{,}000 \times 4.18\% \times 92/365 = £52{,}679.45$.

*If you found £53,411.11:* you divided by 360. Sterling notes, Medway's included, are Actual/365 (Fixed) (Chapter 2).

*If you found £45,369.86:* you used SONIA alone, 3.60%. The coupon is SONIA plus the margin.

*If you found £7,309.59:* you used the margin alone, 0.58%. The margin is the spread over SONIA, not the coupon.

*If you found £52,250.00:* you took a quarter as one quarter of a year. Interest accrues on actual days: this period has 92, so the fraction is $92/365$, not $1/4$.

**Revise:** Chapter 2 (day counts), Chapter 15 (SONIA).

### A3. Expected loss

**Answer: £612,000.00.**

1. $EL = EAD \times PD \times LGD$ (Chapter 3).
2. $EL = 200{,}000{,}000 \times 1.80\% \times 17.00\% = £612{,}000.00$.

*If you found £3,600,000.00:* you stopped at $EAD \times PD$, the balance expected to default. Part of that balance is recovered from the property sale; LGD is the share that is lost.

*If you found £2,988,000.00:* you multiplied by the recovery rate, 83.00%, instead of the LGD, 17.00%. LGD $= 1 -$ recovery rate.

*If you found £34,000,000.00:* you multiplied the pool by LGD only, as if every loan defaulted. PD says how many default.

**Revise:** Chapter 3.

### A4. What securitisation does not do

**Answer: (c).** Kingsbridge keeps all of Class Z and a 5% vertical slice of Classes A and B, so it still bears the first losses of the pool and 5% of every loss that reaches A or B.

- (a) is a result: the notes are sold to capital-market investors, so Kingsbridge funds the loans beyond its deposit base.
- (b) is a result: the notes repay as the loans repay, so the funding lasts as long as the assets it funds. Deposits can leave at any time.
- (d) is a result: pension funds, insurers and asset managers that never lend to a building society buy its AAA(sf) notes.

**Revise:** Chapter 4.

### A5. Orphan SPV and true sale

**Answer: (b).** The issuer is owned by a charitable trust, not by Kingsbridge, and it owns the loans outright after a true sale. If Kingsbridge became insolvent, its administrator could not claim the loans or consolidate the issuer.

- (a) is wrong: insolvency remoteness lowers the risk of the notes, and therefore their coupon.
- (c) is wrong: a prospectus is required for a listing on a regulated market (Chapter 21), whatever the issuer's ownership.
- (d) is wrong: a true sale is final. Kingsbridge repurchases only loans that breach a warranty, or exercises a call written in the documents; "at will" would undo the sale.

**Revise:** Chapters 5 and 21.

### A6. The cut-off date

**Answer: (b).** The cut-off date, 31 January 2028 for Medway, is the date at which the tape balances are measured. The sale is effective from that date, so every collection received after it belongs to the issuer, even before closing.

- (a) is wrong: the pricing date is when the coupons are fixed in the bookbuild (Chapter 23).
- (c) is wrong: the first IPD falls after closing (16 March 2028), on one of the March, June, September and December dates.
- (d) is wrong: the legal final maturity is the last date on which the notes must be repaid.

**Revise:** Chapter 7.

### A7. Weighted average LTV and banding

**Answer: 68.00%; the 60–70% band.**

1. Weight each LTV by its balance: $120{,}000 \times 50 + 200{,}000 \times 70 + 80{,}000 \times 90 = 27{,}200{,}000$.
2. Divide by the total balance: $27{,}200{,}000 / 400{,}000 = 68.00\%$.
3. Book convention (Chapter 9): each band includes its upper limit, so 70.00% belongs to 60–70%, not 70–75%.

*If you found 70.00%:* you took the simple average of the three LTVs. A £200,000 loan carries two and a half times the weight of an £80,000 loan.

*If you placed 70.00% in 70–75%:* you used lower-inclusive bands. Both conventions exist; the book's rule includes the upper limit, and the investor report states its rule under the table.

**Revise:** Chapters 6 and 9.

### A8. From SMM to CPR

**Answer: 9.19%.**

1. Each month 99.20% of the balance survives: $1 - 0.008 = 0.992$.
2. After 12 months, $0.992^{12}$ survives.
3. $\text{CPR} = 1 - 0.992^{12} = 9.19\%$.

*If you found 9.60%:* you multiplied the SMM by 12. Each month's 0.80% applies to a balance already reduced by earlier prepayments, so the annual rate is below 12 times the monthly one.

*If you found 10.03%:* you calculated $1.008^{12} - 1$, which compounds the rate upwards like interest. Prepayments remove balance; they do not grow it.

**Revise:** Chapter 10.

### A9. Class A subordination at closing

**Answer: 8.39%.**

1. Subordination is the share of the pool funded by the notes below Class A: Classes B and Z.
2. $(14{,}400{,}000.00 + 4{,}568{,}431.27) / 225{,}968{,}431.27 = 8.39\%$: Class B 6.37% plus Class Z 2.02%.

*If you found 6.37%:* you forgot Class Z. It is unrated, but it absorbs losses before Class A.

*If you found 9.37%:* you added the reserve (0.98% of the pool once full). The reserve adds to credit enhancement but is not subordination; at closing it held £0.00 (Chapter 12).

*If you found 91.61%:* you gave the share of Class A itself. Subordination is what sits below the class.

**Revise:** Chapters 11 and 12.

### A10. First protection against losses

**Answer: (b) excess spread.** Each realised loss is debited to the PDL, and the revenue waterfall cures the PDL from the revenue left after fees and interest. If the cure is paid, no note bears the loss.

- (a) is wrong: Class Z bears a loss only when excess spread and the reserve cannot cure the PDL before the deal ends.
- (c) is wrong: the reserve forms part of available revenue and covers fees and interest when revenue falls short; it protects against loss only after the excess spread is used.
- (d) is wrong: Class B is debited only once the Class Z sub-ledger is full, £4,568,431.27 of losses.

In Medway the Class Z PDL, item (8), ranks below the reserve top-up, item (7): while the reserve is below £2,214,000.00, excess spread refills the reserve first and the Class Z PDL waits, as IPD 1 of Part C shows.

**Revise:** Chapter 12.

### A11. Where a PDL cure goes

**Answer: (b).** A cure is a transfer from the revenue pot to the principal pot. It joins the available principal receipts, which pay Class A first.

- (a) is wrong: Class Z pays no interest, and a cure is never interest to anyone.
- (c) is wrong: Kingsbridge receives only the residual at item (9), after the cure.
- (d) is wrong: the reserve is item (7), a separate line above the cure.

**Revise:** Chapter 13.

### A12. Weighted average life

**Answer: 3.20 years.**

1. Weight each repayment time by the principal repaid: $1 \times 20 + 3 \times 50 + 5 \times 30 = 320$.
2. Divide by the total principal: $320 / 100$ = 3.20 years.

*If you found 3.00 years:* you averaged the three dates without weights. Half the principal comes back at year 3.

*If you found 5.00 years:* you gave the final maturity. WAL measures when the average pound comes back, not when the last one does.

**Revise:** Chapter 14.

### A13. Net swap payment

**Answer: Northgate pays the issuer £113,424.66.**

1. Issuer pays fixed: $150{,}000{,}000 \times 3.30\% \times 92/365 = £1{,}247{,}671.23$.
2. Issuer receives SONIA: $150{,}000{,}000 \times 3.60\% \times 92/365 = £1{,}361{,}095.89$.
3. The two legs are netted: $1{,}361{,}095.89 - 1{,}247{,}671.23 = £113{,}424.66$, paid by Northgate, because SONIA is above the fixed rate.

*If you said the issuer pays:* you reversed the legs. The floating payer, Northgate, pays when SONIA exceeds the fixed rate (Chapter 15).

*If you found £1,247,671.23 or £1,361,095.89:* you gave one leg. Swap legs on the same date are netted; only the difference changes hands.

*If you found £115,000.00:* you used Actual/360.

**Revise:** Chapter 15.

### A14. The step-up

**Answer: (b).** After the first optional redemption date the margin rises, so the notes become expensive for the issuer. Kingsbridge then has an economic reason to call and refinance, and investors price the notes to the call date.

- (a) is wrong: the step-up is fixed in the documents at closing; it does not follow losses.
- (c) is wrong: no regulation requires a step-up; it is a market convention.
- (d) is wrong: trustee fees are senior fees at item (1), unrelated to the coupon.

**Revise:** Chapter 16.

### A15. What AAA(sf) means

**Answer: (b).** A rating is the agency's opinion of the note's ability to pay as promised; AAA(sf) means the note withstands the agency's most severe stress. Agencies monitor the deal and can downgrade it (Chapter 29).

- (a) is wrong: a AAA(sf) note can lose money; the rating states the stress it withstands, not a certainty.
- (c) is wrong: the arranger guarantees nothing.
- (d) is wrong: the agency assigns the rating; the regulator registers and supervises the agency.

**Revise:** Chapters 17 and 20.

### A16. Release of the documents on closing day

**Answer: (b).** The documents are signed in advance and held in escrow. They are released on the closing call once every condition precedent on the checklist is satisfied, and only then does cash move.

- (a) is wrong: listing is one condition precedent, not the trigger of release.
- (c) is wrong: the presale report is published before pricing, weeks before closing.
- (d) is wrong: the first IPD comes after closing, from the collections of the first collection period.

**Revise:** Chapters 21 and 24.

### A17. A late sweep

**Answer: (b) a servicer termination event.** Under the Thames servicing agreement, which Medway shares, Kingsbridge must pay collections to the issuer within 3 business days of receipt. Five days late breaches that limit.

- (a) is wrong: an issuer event of default concerns the issuer, for example a Class A interest shortfall; a late sweep is a failure of the servicer.
- (c) is wrong: the clean-up call depends on the pool falling below 10% of its cut-off balance.
- (d) is wrong: the limit is written in the servicing agreement, and the trustee may replace the servicer.

**Revise:** Chapters 25 and 27.

### A18. Subordination under sequential amortisation

**Answer: (a) rises.** Class A shrinks while Classes B and Z stay, so their share of a smaller pool grows. Part C shows it: Class A subordination is 8.39% at closing and 9.54% after IPD 1.

- (b) would be true only if losses consumed B and Z faster than Class A amortised.
- (c) would be true under pro rata amortisation, where every class shrinks in proportion.
- (d) is wrong: SONIA changes interest, not principal.

**Revise:** Chapters 28 and 29.

### A19. The Rhein Auto set-off reserve

**Answer: (b).** Rheinwagen Bank takes deposits. A borrower who holds deposits above the €100,000 statutory guarantee could set them off against the car loan if the bank failed, and the issuer would receive less. The set-off reserve covers that amount.

- (a) is wrong: balloon payments are paid by the borrower or by the car sale.
- (c) is wrong: swap payments rank in the waterfall.
- (d) is wrong: defaulted loans are losses, covered by credit enhancement.

**Revise:** Chapter 30.

### A20. Retention and the capital hierarchy

**Answer: (a) £10,350,000.00; (b) SEC-IRBA.**

1. A vertical slice is at least 5% of each tranche sold: $5\% \times 207{,}000{,}000.00 = £10{,}350{,}000.00$ of Class A, and 5% of Class B as well, £720,000.00 (Chapter 33).
2. The CRR hierarchy is SEC-IRBA, then SEC-SA, then SEC-ERBA. A bank with approved internal models for the loans calculates KIRB, so SEC-IRBA comes first (Chapter 35).

*If you found £11,070,000.00:* you took 5% of Classes A and B together. The question asks for Class A.

*If you found £11,298,421.56:* you took 5% of all three classes. Kingsbridge holds all of Class Z, not 5% of it; Kingsbridge's whole retained holding is £15,638,431.27.

*If you answered SEC-SA:* that is the method for a bank without internal models for the loans, as the Thames investor in Chapter 35.

**Revise:** Chapters 33–35.

## Part B — The loan tape

### B1. The eight planted issues

| ID | How to detect it | Impact | Treatment |
|:---|:---|:---|:---|
| DQ01 | `COUNTIF(loan_id) > 1`: MRS-00024 twice | +1 loan, +£241,812.02 | Count once |
| DQ02 | current > original balance: MRS-00217 £1,460,872.80 vs £161,000.00 | +£1,314,785.52; its LTV 724.64% | £146,087.28 (÷ 10) |
| DQ03 | maturity < origination: MRS-00699 1956-07-09 | remaining term −871 months | origination + term: 329 months |
| DQ04 | field ≠ balance ÷ indexed value: MRS-00439 62.91 vs 42.97 | WA LTV 55.86% | recompute all LTVs |
| DQ05 | region blank: MRS-00982 | strat misses one loan | Unknown row |
| DQ06 | distinct region list: "Yorkshire & Humber" | 9 loans, £1,311,245.15 on a second row | map to standard name |
| DQ07 | rate ≤ 0: MRS-00501 | WA rate 4.82% | leave out of WA rate |
| DQ08 | arrears < 0: MRS-00199 | no valid bucket | Unknown row |

: The planted issues, their test and their effect

The detection lines below assume three things. In Excel, the tape sheet `Data_Medway_Tape` is protected, so every test is a formula in a new sheet (as `Clean_View` does in `exam_solutions.xlsx`), written in row 2 and filled down to row 1001; the columns are A `loan_id`, B `origination_date`, C `maturity_date`, D `original_term_months`, E `original_balance`, F `current_balance`, H `indexed_valuation`, J `indexed_ltv`, K `current_rate`, N `region` and O `months_in_arrears`. In Python, `t = pd.read_csv(path, keep_default_na=False)`, so a blank region stays an empty string. In R, `t <- read.csv(path, colClasses = c(region = "character"))`. `tools/exam_corrections_figures.py` runs every Python and R line below and asserts that it finds exactly the planted loans.

**Marking.** 1.5 marks per issue, to a maximum of 12: 0.5 for the loan and field, 0.5 for the test that finds it, 0.5 for a treatment that keeps the raw sheet unchanged. A log that says "MRS-00217 looks wrong" scores half; a log that names the test (current balance above original balance on a repayment loan), the evidence (the `indexed_ltv` field, 72.46, matches the balance divided by 10, not the balance as reported) and the treatment scores full marks.

#### DQ01 — duplicate row, MRS-00024

**What it is.** The same loan appears twice, every field identical. The tape has 1,000 rows but 999 loans.

**Detect it.**

- Excel: `=COUNTIF(Data_Medway_Tape!$A$2:$A$1001,Data_Medway_Tape!A2)` and filter for values above 1: two rows, both MRS-00024. Flag the first occurrence with `=IF(COUNTIF(Data_Medway_Tape!$A$2:A2,A2)=1,1,0)`, as `Clean_View` column B does.
- Python: `t[t.loan_id.duplicated(keep=False)]`.
- R: `t$loan_id[duplicated(t$loan_id)]`.

**Impact.** Left untreated alone: 1,000 loans, total £198,114,019.03 (+£241,812.02), average £198,114.02, WA indexed LTV 55.85%, WA remaining term 267.97 months.

**Treatment.** Count the loan once and exclude the second row from every figure. The rows are identical, so the tape itself proves that the second is a copy. Ask the servicer why its extract repeats a row: a join on a one-to-many table (two borrowers, two accounts) produces duplicates, and the next tape will repeat them.

#### DQ02 — decimal shift, MRS-00217

**What it is.** The current balance, £1,460,872.80, is above the original balance, £161,000.00, on a repayment loan that has paid for more than three years. A repayment balance only falls. The value is ten times £146,087.28: a decimal point moved one place.

**Detect it.**

- Excel: `=Data_Medway_Tape!F2>Data_Medway_Tape!E2`, filter TRUE: one row. Confirm with `=ROUND(Data_Medway_Tape!F2/Data_Medway_Tape!H2*100,2)`, 724.64, against the tape's own field `J`, 72.46.
- Python: `t[t.current_balance > t.original_balance]`.
- R: `t$loan_id[t$current_balance > t$original_balance]`.

**Impact.** Left untreated alone: total £199,186,992.53 (+£1,314,785.52, nine times the true balance), average £199,386.38, WA indexed LTV 60.73% instead of 55.84%, WA remaining term 267.85 months. One loan at 724.64% LTV moves the pool's WA LTV by 4.89 points, and puts one loan with £1,460,872.80 in the "Over 90%" band, which is otherwise empty.

**Treatment.** Use £146,087.28 in a new column, and log the rule. Two facts on the tape prove the corrected value: the reported value divided by 10 is below the original balance, as a repayment balance must be; and the `indexed_ltv` field, 72.46, equals £146,087.28 ÷ £201,601.00 indexed valuation. Confirm with the servicer before the next report.

#### DQ03 — century error, MRS-00699

**What it is.** The maturity date, 1956-07-09, is before the origination date, 2026-07-09. A loan cannot mature 70 years before it starts. The original term, 360 months, added to the origination date gives 2056-07-09: the century was typed as 19 instead of 20.

**Detect it.**

- Excel: `=Data_Medway_Tape!C2<Data_Medway_Tape!B2`, filter TRUE. Correct with `=EDATE(Data_Medway_Tape!B2,Data_Medway_Tape!D2)`, as `Clean_View` column H does.
- Python: `t[t.maturity_date < t.origination_date]` (ISO dates compare correctly as text).
- R: `t$loan_id[as.Date(t$maturity_date) < as.Date(t$origination_date)]`.

**Impact.** The loan's remaining term is −871 months instead of 329. Left untreated alone, the WA remaining term falls from 267.91 to 266.65 months. The loan's balance, £206,965.21, is unchanged.

**Treatment.** Use origination date plus original term, 2056-07-09, in a new column. The tape proves it: two of its own fields give the right date. Run the test for every date field: a tape that has one century error from a manual entry has a process that allows more.

#### DQ04 — stale indexed LTV, MRS-00439

**What it is.** The `indexed_ltv` field shows 62.91, which is the loan's original LTV. The balance £199,352.94 divided by the indexed valuation gives 42.97. The servicer's system did not update the field.

**Detect it.**

- Excel: `=ABS(Data_Medway_Tape!J2-ROUND(Data_Medway_Tape!F2/Data_Medway_Tape!H2*100,2))>0.01`, filter TRUE.
- Python: `calc = (t.current_balance / t.indexed_valuation * 100).round(2)`, then `t[(t.indexed_ltv - calc).abs() > 0.01]`.
- R: `calc <- round(t$current_balance / t$indexed_valuation * 100, 2)`, then `t$loan_id[abs(t$indexed_ltv - calc) > 0.01]`.

The test returns two loans: MRS-00439, and MRS-00217, whose field is right and whose balance is wrong (DQ02). Read each hit before you correct it.

**Impact.** Left untreated alone, the WA indexed LTV is 55.86% instead of 55.84%, and MRS-00439 sits in the 60–70% band instead of 0–50%.

**Treatment.** Recompute the indexed LTV for every loan from current balance and indexed valuation, rounded to two decimals per loan, as the reporting conventions require. Never patch only the loans you found: a field that is wrong once is unreliable everywhere.

#### DQ05 — blank region, MRS-00982

**What it is.** The `region` field is empty. The tape cannot prove where the property is.

**Detect it.**

- Excel: `=TRIM(Data_Medway_Tape!N2)=""`, filter TRUE; or `=COUNTBLANK(Data_Medway_Tape!N2:N1001)`, which returns 1.
- Python: `t[t.region.str.strip() == ""]`.
- R: `t$loan_id[trimws(t$region) == ""]`.

**Impact.** No headline figure moves. A region strat without an Unknown row holds 998 loans and £197,743,367.93, and fails its check by £128,839.08.

**Treatment.** Keep the loan in every total and report it in an Unknown row of the region strat. Request the property postcode from the servicer. Guessing the region from the borrower's address or from the valuation would put an unproven value in an investor report.

#### DQ06 — two spellings of one region, 9 loans

**What it is.** Nine loans show "Yorkshire & Humber"; 64 others show the standard name, "Yorkshire and the Humber". The region is the same; the text is not.

**Detect it.**

- Excel: open the filter drop-down on column N, or list the distinct values with `=UNIQUE(Data_Medway_Tape!N2:N1001)`: 14 entries for 12 regions (one variant spelling, one blank). Count the variant with `=COUNTIF(Data_Medway_Tape!$N$2:$N$1001,"Yorkshire & Humber")`: 9.
- Python: `t.region.value_counts()`, then `t[t.region == "Yorkshire & Humber"]`.
- R: `table(t$region)`, then `sum(t$region == "Yorkshire & Humber")`.

**Impact.** No headline figure moves. Built from the raw text, the region strat shows "Yorkshire & Humber" with 9 loans and £1,311,245.15 (0.66% of the pool) on a second row, and "Yorkshire and the Humber" with 64 loans and £9,758,762.12. An investor reading the strat sees two regions and understates the exposure to the region by £1,311,245.15.

**Treatment.** Map the variant to the standard name in a mapping table (`DQ_Log`, "Region mapping") and build the strat from the mapped column. The mapping is proven: both spellings name the same ONS region.

#### DQ07 — zero rate, MRS-00501

**What it is.** A fixed-rate loan with £194,548.83 outstanding shows a current rate of 0.00%. No Kingsbridge product charges nothing, and the loan is current, so the borrower pays something.

**Detect it.**

- Excel: `=Data_Medway_Tape!K2<=0`, filter TRUE.
- Python: `t[t.current_rate <= 0]`.
- R: `t$loan_id[t$current_rate <= 0]`.

**Impact.** Including the 0.00% gives a WA current rate of 4.82% (4.824% to three decimals) instead of 4.83% (4.829%).

**Treatment.** Keep the loan and its balance in every figure, and leave it out of the WA current rate only: the numerator and the denominator of that average both exclude it. The tape cannot prove the true rate, so no correction is made; the log states the exclusion and the query to the servicer.

*If you logged "loans with a rate of 7.24%":* that is the SVR, not an error. All 106 SVR loans carry 7.24%; check the rate type before you call a rate an outlier.

#### DQ08 — negative arrears, MRS-00199

**What it is.** The `months_in_arrears` field is −2. A borrower cannot be minus two months behind. A borrower who overpays is in credit, which the tape does not record in this field.

**Detect it.**

- Excel: `=Data_Medway_Tape!O2<0`, filter TRUE.
- Python: `t[t.months_in_arrears < 0]`.
- R: `t$loan_id[t$months_in_arrears < 0]`.

**Impact.** No headline figure moves. The loan, £169,935.32, fits no arrears bucket. Dropped, it leaves an arrears strat of 998 loans and £197,702,271.69; forced into Current, it gives Current 956 loans and £189,488,604.18.

**Treatment.** Keep the loan in every total and report it in an Unknown row of the arrears strat. The tape cannot prove whether the borrower is current or two months behind, and the difference matters: two months of arrears is one step from the default definition.

*If you corrected the raw sheet:* you lose the audit trail. The next tape arrives with the same error and nobody can show what was changed. Corrections go in new columns, with the rule in the log.

### B2. Headline statistics

| Figure | Formula | Result |
|:---|:---|---:|
| Loans | count of first occurrences | 999 |
| Total balance | sum of treated balances | £197,872,207.01 |
| Average balance | total ÷ loans | £198,070.28 |
| WA current rate | $\sum B_i r_i / \sum B_i$, rate > 0 only | 4.83% |
| WA indexed LTV | $\sum B_i \text{LTV}_i / \sum B_i$ | 55.84% |
| WA remaining term | $\sum B_i n_i / \sum B_i$ | 267.91 months |

: Part B2 working

Each formula, in the solution workbook:

- **Loans:** `=SUM(Clean_View!$B$2:$B$1001)`, the sum of the first-occurrence flags.
- **Total balance:** `=SUM(Clean_View!$D$2:$D$1001)`, where column D is the flag times the treated balance.
- **Average balance:** `=ROUND(C6/C5,2)`, total divided by loans, rounded once.
- **WA current rate:** the sum of balance × rate over loans with a positive rate, divided by the sum of their balances. Both sums carry the same condition, otherwise the average is diluted.
- **WA indexed LTV:** the sum of balance × recomputed LTV over the total balance.
- **WA remaining term:** for each loan, $n_i = 12 \times (\text{year}_{mat} - 2029) + (\text{month}_{mat} - 2)$, then weighted by balance. In Excel, `=(YEAR(H2)-2029)*12+MONTH(H2)-2` on the treated maturity date.

Round each weighted average once, at the end. In years, the WA remaining term is 22.33 years.

*If you found 1,000 loans and £198,114,019.03:* you kept the duplicate row of MRS-00024. It also moves the average to £198,114.02, the WA LTV to 55.85% and the WA remaining term to 267.97 months. Test `loan_id` for uniqueness before any total.

*If you found an average balance of £197,872.21:* you removed the duplicate from the total but divided by the 1,000 rows. Count and total must come from the same set of loans.

*If you found £199,186,992.53 and a WA LTV of 60.73%:* you kept the balance of MRS-00217 at £1,460,872.80 (average £199,386.38, WA remaining term 267.85 months).

*If you found a WA remaining term of 266.65 months:* you kept the 1956 maturity date of MRS-00699, which gives −871 months.

*If you found a WA remaining term of 263.49 months:* you took the simple average of the terms. Investor reports weight every average by current balance (Chapter 9).

*If you found a WA indexed LTV of 55.86%:* you used the `indexed_ltv` field instead of recomputing it; the field is stale for MRS-00439.

*If you found 53.12%:* you took the simple average of the LTVs. Investor reports weight by current balance (Chapter 9).

*If you found a WA rate of 4.82%:* you included the 0.00% rate of MRS-00501.

*If you found a WA rate of 4.84%:* you took the simple average of the positive rates. Small loans then count as much as large ones.

*If you found £199,428,804.55:* you summed the tape as delivered: all the issues at once.

**Marking.** One mark for each figure; two marks for the checks and the visible formulas. The check is that the count and the total of every strat equal the headline count and total, and that the total of each strat's WA LTV equals the headline 55.84%.

### B3. The four stratifications

A stratification splits the reporting pool into buckets of one field. Every row needs the same four figures: loans, balance, % of balance and WA indexed LTV. The total row must equal the headline figures of B2, and the check row shows the difference, which must be 0 loans and £0.00.

**The reconciliation logic.** Each loan goes into exactly one bucket. So the bucket counts add up to 999, the bucket balances add up to £197,872,207.01, and the total WA LTV, computed from the unrounded bucket sums, is 55.84%. If a check fails, one of three things happened: a loan fell into no bucket (an unexpected value: a blank, a −2, a variant spelling), a loan fell into two buckets (overlapping limits), or the strat was built on a different set of loans (the raw tape, or a filtered list).

| Arrears | Loans | Balance (£) | % bal. | WA LTV |
|:---|---:|---:|---:|---:|
| Current | 955 | 189,318,668.86 | 95.68 | 55.82 |
| 1 month | 18 | 3,723,753.44 | 1.88 | 55.43 |
| 2 months | 7 | 1,072,920.82 | 0.54 | 54.90 |
| 3–5 months | 11 | 2,485,450.86 | 1.26 | 58.52 |
| 6+ months | 7 | 1,101,477.71 | 0.56 | 57.23 |
| Unknown | 1 | 169,935.32 | 0.09 | 46.37 |
| Total | 999 | 197,872,207.01 | 100.00 | 55.84 |

: Arrears

| Indexed LTV | Loans | Balance (£) | % bal. | WA LTV |
|:---|---:|---:|---:|---:|
| 0–50% | 422 | 66,376,929.10 | 33.55 | 43.03 |
| 50–60% | 308 | 61,138,924.92 | 30.90 | 55.11 |
| 60–70% | 182 | 45,145,505.58 | 22.82 | 64.57 |
| 70–75% | 46 | 13,347,008.54 | 6.75 | 72.39 |
| 75–80% | 28 | 7,575,488.32 | 3.83 | 77.48 |
| 80–85% | 10 | 3,464,300.41 | 1.75 | 82.12 |
| 85–90% | 3 | 824,050.14 | 0.42 | 86.47 |
| Over 90% | 0 | 0.00 | 0.00 | 0.00 |
| Total | 999 | 197,872,207.01 | 100.00 | 55.84 |

: Indexed LTV

| Repayment type | Loans | Balance (£) | % bal. | WA LTV |
|:---|---:|---:|---:|---:|
| Repayment | 863 | 167,168,006.30 | 84.48 | 54.91 |
| Interest-only | 97 | 22,554,700.00 | 11.40 | 62.03 |
| Part and part | 39 | 8,149,500.71 | 4.12 | 57.91 |
| Total | 999 | 197,872,207.01 | 100.00 | 55.84 |

: Repayment type

| Region | Loans | Balance (£) | % bal. | WA LTV |
|:---|---:|---:|---:|---:|
| London | 209 | 60,108,274.50 | 30.38 | 59.81 |
| South East | 171 | 36,777,636.39 | 18.59 | 55.65 |
| East of England | 93 | 16,583,248.79 | 8.38 | 53.78 |
| South West | 104 | 18,521,000.26 | 9.36 | 55.11 |
| West Midlands | 65 | 9,541,677.99 | 4.82 | 54.32 |
| East Midlands | 72 | 11,045,056.63 | 5.58 | 52.66 |
| North West | 89 | 14,397,636.09 | 7.28 | 51.81 |
| Yorkshire and the Humber | 73 | 11,070,007.27 | 5.59 | 51.94 |
| North East | 31 | 4,770,157.16 | 2.41 | 57.03 |
| Wales | 46 | 7,268,273.26 | 3.67 | 51.95 |
| Scotland | 35 | 6,158,092.45 | 3.11 | 54.98 |
| Northern Ireland | 10 | 1,502,307.14 | 0.76 | 51.75 |
| Unknown | 1 | 128,839.08 | 0.07 | 66.18 |
| Total | 999 | 197,872,207.01 | 100.00 | 55.84 |

: Region

**How each strat is built.**

- **Arrears.** Bucket on the integer `months_in_arrears`: 0 is Current, 1 and 2 have their own rows, 3 to 5 share a row, 6 and more share a row, and a negative value goes to Unknown. In Excel, a helper column with nested `IF`s, then `COUNTIFS` and `SUMIFS` on it.
- **Indexed LTV.** Bucket on the recomputed LTV, rounded to two decimals per loan, with the upper limit included: a loan at exactly 60.00% belongs to 50–60%. In Excel, compare with `<=`: `=IF(E2<=50,"0-50%",IF(E2<=60,"50-60%",...))`.
- **Repayment type.** Bucket on the field as given; the three values are clean.
- **Region.** Bucket on the mapped region, with Unknown for the blank.

**Typical bucket-boundary errors.**

*If your 0–50% row shows 421 loans and £65,972,993.89, and 50–60% shows 309 loans and £61,542,860.13:* you moved MRS-00162 across a limit. Its LTV is £403,935.21 ÷ indexed valuation = 50.0022%, which rounds to 50.00, exactly on the limit. Two mistakes produce this result: lower-inclusive bands (`<` instead of `<=`), or banding on the unrounded ratio. The conventions say round per loan, then band with the upper limit included; MRS-00162 is the only loan the choice moves, and the note under the table states the rule.

*If your 3–5 months row shows 12 loans and £2,629,893.84:* you put the loan at exactly 6 months (£144,442.98) into 3–5 months, by testing `< 6` for the 6+ row instead of `>= 6`. Six months is the first month of 6+.

*If your arrears strat totals 998 loans and £197,702,271.69:* you dropped MRS-00199 because −2 matches no bucket. The check row catches it: a strat that does not reconcile to the pool is not finished.

*If your Current row shows 956 loans and £189,488,604.18:* you put the −2 into Current. That hides a data error inside the best bucket; an investor reading the report would never know.

*If your region strat has a row "Yorkshire & Humber" with 9 loans and £1,311,245.15:* you reported the spelling, not the region. Build the strat from a mapped column, never from the raw text.

*If your region strat totals 998 loans and £197,743,367.93:* you dropped the blank region of MRS-00982. Add an Unknown row.

*If your total WA LTV differs from 55.84% by 0.01:* you averaged the rounded bucket WAs. Weighting the rounded repayment-type WAs by balance gives 55.85%, and weighting the rounded arrears WAs by the rounded % column also gives 55.85%. Weight the unrounded sums, then round once.

*If your total WA LTV is 68.74%:* you took the simple average of the seven non-empty LTV bucket WAs. The 85–90% bucket holds three loans and counts as much as the 0–50% bucket with 422.

*If your % column totals 100.02 (LTV strat) or 100.01 (arrears strat):* you summed the rounded percentages. Compute the total row from the unrounded balances: it is 100.00 by construction. The region strat's rounded column happens to sum to 100.00.

*If your London row shows 30.14%:* you divided by the delivered total, £199,428,804.55, instead of the reporting-pool total. The denominator of every % column is the B2 total.

**Marking.** Three marks per strat: one for the buckets and their rule, one for correct rows, one for the total and check rows reconciling to B2.

### B4. Impact and treatment

| Figure | Reporting pool | As delivered |
|:---|---:|---:|
| Loans | 999 | 1,000 |
| Total balance (£) | 197,872,207.01 | 199,428,804.55 |
| Average balance (£) | 198,070.28 | 199,428.80 |
| WA current rate | 4.83% | 4.82% |
| WA indexed LTV | 55.84% | 55.98% |
| WA remaining term (months) | 267.91 | 266.67 |

: The six figures on the tape as delivered

"As delivered" means every row and every field as given: 1,000 rows counted as loans, the reported balances, the `indexed_ltv` field, the raw maturity dates and the 0.00% rate.

**Which issue moves which figure.**

- **Loans and total.** The difference of £1,556,597.54 is the duplicate (£241,812.02) plus nine times the true balance of MRS-00217 (£1,314,785.52). Nothing else changes a balance.
- **Average balance.** £199,428.80 is the inflated total over 1,000 rows: both DQ01 and DQ02 push it up.
- **WA current rate.** DQ07 alone: the 0.00% rate dilutes the average from 4.83% to 4.82%. DQ01 and DQ02 add weight to rates of 4.43% and 5.05%, which does not move the second decimal.
- **WA indexed LTV.** As delivered it is 55.98%, from three effects: the `indexed_ltv` field of MRS-00217 is 72.46 (the right value) but it carries the weight of £1,460,872.80; the stale 62.91 of MRS-00439 adds two basis points; the duplicate adds one. With the duplicate removed and the field kept, the figure is 55.97%. The 60.73% of a corrected-LTV-but-raw-balance calculation does not appear here, because the delivered figure uses the field.
- **WA remaining term.** As delivered it is 266.67 months, 1.24 months below the reporting pool: the −871 months of MRS-00699 does it, with a small effect from the extra weights of DQ01 and DQ02.
- **Strats only.** DQ05, DQ06 and DQ08 move no headline figure; they break the strats (rows missing or split).

| Issue | Figure moved | Untreated | Treated |
|:---|:---|---:|---:|
| DQ01 duplicate | loans; total | 1,000; £198,114,019.03 | 999; £197,872,207.01 |
| DQ02 decimal shift | total; WA LTV | £199,186,992.53; 60.73% | £197,872,207.01; 55.84% |
| DQ03 century error | WA remaining term | 266.65 | 267.91 |
| DQ04 stale LTV | WA indexed LTV | 55.86% | 55.84% |
| DQ07 zero rate | WA current rate | 4.82% | 4.83% |
| DQ05, 06, 08 | strats only | rows missing or split | Unknown and mapped rows |

: Each issue left untreated on its own, all others treated

Fixing issues one at a time from the tape as delivered shows the same thing from the other side. Removing only the duplicate leaves £199,186,992.53 and a field-based WA LTV of 55.97%; correcting only MRS-00217 leaves £198,114,019.03; recomputing only the LTVs, with the raw balance, gives 60.74%; correcting only the maturity date restores 267.91 months, because the duplicate and the decimal shift do not move the second decimal of the WA term.

**Why these treatments.** An investor report must reconcile, and every figure in it must be traceable to the tape. So the report corrects a value only where the tape proves the right one: the duplicate is identical, the decimal shift agrees with the tape's own LTV field and original balance, and the maturity follows from origination plus term. Where the tape cannot prove the value (blank region, zero rate, negative arrears), the loan stays in the pool and in every total, the unknown value goes to an Unknown row or is left out of one average, and the log asks the servicer.

**Trade-off to keep in mind.** Each data issue offers three treatments: exclude the loan, correct the value, or flag it and report it as delivered.

- *Exclude.* Removing MRS-00217 until the servicer confirms is cautious: the report then shows 998 loans, £197,726,119.73, an average of £198,122.36 and a WA LTV of 55.83%. The cost is the tie with the waterfall: the cash manager's pool is £197,872,207.01, so the report misses by £146,087.28 and understates the pool.
- *Correct.* Using £146,087.28 gives the right total today, and that total ties to the cash manager's pool (Part D1). The risk is that a correction is wrong; it is acceptable only because the tape's own fields prove it, and the log records it.
- *Flag and report as delivered.* Keeping £1,460,872.80 with a note is transparent but publishes a total of £199,186,992.53 and a WA LTV of 60.73% that are wrong, and an investor reading the headline will not read the footnote.

For a single, provable error, correct and flag. For anything you cannot prove, leave the value out of the figure it would distort, keep the balance in, and ask. The same logic decides the zero rate: including it at 0.00% understates the WA rate (4.82%); excluding it assumes the loan earns what the others earn (4.83%). The difference is one basis point; the log must say which you chose. And it decides the negative arrears: Unknown keeps the strat honest; Current (956 loans) hides the error in the best bucket; exclusion (998 loans) breaks the reconciliation.

**Marking.** Two marks for the six as-delivered figures; four for naming which issue moves which figure, with the amount; two for the justification and the alternative with its trade-off.

## Part C — The waterfall

### How to run a Medway IPD

The order of the steps matters as much as the arithmetic.

1. **Debit the PDL** with the realised losses of the period, before anything is paid: Class Z sub-ledger up to the Class Z balance, then Class B, then Class A.
2. **Compute available revenue receipts**: revenue collections plus the whole reserve balance.
3. **Compute every amount due**, items (1) to (8), from the opening balances. Item (7) is the full required amount, because the whole reserve has been put into available revenue: the reserve is rebuilt from zero at item (7) each IPD.
4. **Pay down the revenue waterfall**: each item receives the lower of its amount due and the cash left. Unpaid Class B interest is deferred.
5. **Run the principal waterfall**: scheduled principal, prepayments, recoveries and the PDL cures paid at items (4), (6) and (8), strictly sequential A, then B, then Z.
6. **Roll the balances forward**: notes, PDL, pool, reserve, deferred interest.
7. **Run the five zero-checks.**

### IPD 1 (15 March 2029, 90 days, normal)

**Step 1 — PDL debit.** The loss of £38,417.62 goes to the Class Z sub-ledger, which has room of £4,568,431.27 − £61,884.15 = £4,506,547.12. Class Z PDL: £61,884.15 + £38,417.62 = £100,301.77, 2.20% of Class Z.

**Step 2 — Available revenue receipts.** £2,400,538.74 + reserve £384,612.90 = £2,785,151.64.

**Step 3 — Amounts due.**

- (1) $190{,}000 \times 90/365 = £46{,}849.32$; no extraordinary expense.
- (2) $204{,}225{,}518.76 \times 0.15\% \times 90/365 = £75{,}535.47$, on the pool at the start of the period.
- (3) $185{,}318{,}971.64 \times 4.18\% \times 90/365 = £1{,}910{,}054.72$.
- (4) Class A PDL: £0.00.
- (5) $14{,}400{,}000.00 \times 4.95\% \times 90/365 = £175{,}758.90$; no deferred interest brought forward.
- (6) Class B PDL: £0.00.
- (7) the required amount, £2,214,000.00, because the whole reserve was put into available revenue.
- (8) the Class Z PDL, £100,301.77.

**Step 4 — Payments.**

| Item | Due (£) | Paid (£) | Left (£) |
|:---|---:|---:|---:|
| Available | | | 2,785,151.64 |
| (1) Senior fees | 46,849.32 | 46,849.32 | 2,738,302.32 |
| (2) Servicing | 75,535.47 | 75,535.47 | 2,662,766.85 |
| (3) Class A interest | 1,910,054.72 | 1,910,054.72 | 752,712.13 |
| (5) Class B interest | 175,758.90 | 175,758.90 | 576,953.23 |
| (7) Reserve | 2,214,000.00 | 576,953.23 | 0.00 |
| (8) Class Z PDL | 100,301.77 | 0.00 | 0.00 |

: IPD 1 revenue waterfall (items (4), (6) and (9) receive £0.00)

Items (1) to (3) take £2,032,439.51 and items (1) to (5) are paid in full: they need £2,208,198.41, and the collections alone are £2,400,538.74. £576,953.23 remains: item (7) takes all of it. The reserve rises from £384,612.90 to £576,953.23, a top-up of £192,340.33, which is the quarter's excess spread (collections minus items (1) to (5)). Item (8) receives nothing: the Class Z PDL ranks below the reserve and stays at £100,301.77. Item (9) receives nothing. The reserve is still £1,637,046.77 short of its required amount.

**Step 5 — Principal.** £1,446,445.83 + £4,725,188.30 + £143,260.00 = £6,314,894.13, no cures: all to Class A, which falls from £185,318,971.64 to £179,004,077.51. Classes B and Z receive nothing: the principal waterfall is strictly sequential.

**Step 6 — Closing state.** Pool: £204,225,518.76 − £6,314,894.13 − £38,417.62 = £197,872,207.01 (a reduction of £6,353,311.75). Notes £197,972,508.78; PDL £100,301.77; reserve £576,953.23; deferred interest nil.

**Step 7 — Checks.** (i) £2,785,151.64 − £2,785,151.64 = 0.00. (ii) £6,314,894.13 − £6,314,894.13 = 0.00. (iii) £61,884.15 + £38,417.62 − £0.00 − £100,301.77 = 0.00. (iv) £204,287,402.91 − £6,314,894.13 − £197,972,508.78 = 0.00. (v) Notes £197,972,508.78 − PDL £100,301.77 = £197,872,207.01 = pool. That pool is the tape's reporting-pool total from Part B: the check "Tape pool − IPD 1 closing pool" reads 0.00. Class A credit enhancement is 9.54%; Class B's, $(Z - \text{PDL}) / \text{pool}$, is 2.26%.

### IPD 2 (15 June 2029, 92 days, stressed)

**Step 1 — PDL debit.** The loss of £712,946.38 goes to the Class Z sub-ledger, which has room of £4,568,431.27 − £100,301.77 = £4,468,129.50, more than the loss. Classes B and A are not touched. Class Z PDL: £100,301.77 + £712,946.38 = £813,248.15, 17.80% of Class Z. The loss comes from repossessions sold for £1,874,350.00 against balances of £2,587,296.38: the sales recovered 72.44% of the balance.

**Step 2 — Available revenue receipts.** £1,583,472.28 + the whole reserve, £576,953.23 = £2,160,425.51.

**Step 3 — Amounts due.**

- (1) $190{,}000 \times 92/365 = £47{,}890.41$, plus the extraordinary senior expense of £74,500.00: £122,390.41.
- (2) $197{,}872{,}207.01 \times 0.15\% \times 92/365 = £74{,}811.96$, on the IPD 1 closing pool, which is the IPD 2 opening pool.
- (3) $179{,}004{,}077.51 \times 4.18\% \times 92/365 = £1{,}885{,}967.34$, on the Class A balance after the IPD 1 redemption.
- (4) Class A PDL: £0.00.
- (5) $14{,}400{,}000.00 \times 4.95\% \times 92/365 = £179{,}664.66$; nothing was deferred in IPD 1, so no deferred amount and no interest on it.
- (6) Class B PDL: £0.00.
- (7) the required amount, £2,214,000.00.
- (8) the Class Z PDL, £813,248.15.

**Step 4 — Payments.**

| Item | Due (£) | Paid (£) | Left (£) |
|:---|---:|---:|---:|
| Available | | | 2,160,425.51 |
| (1) Senior fees | 122,390.41 | 122,390.41 | 2,038,035.10 |
| (2) Servicing | 74,811.96 | 74,811.96 | 1,963,223.14 |
| (3) Class A interest | 1,885,967.34 | 1,885,967.34 | 77,255.80 |
| (5) Class B interest | 179,664.66 | 77,255.80 | 0.00 |
| (7) Reserve | 2,214,000.00 | 0.00 | 0.00 |
| (8) Class Z PDL | 813,248.15 | 0.00 | 0.00 |

: IPD 2 revenue waterfall (items (4), (6) and (9) receive £0.00)

Items (1) to (3) take £2,083,169.71, leaving £77,255.80 for Class B, which is owed £179,664.66. Class B receives £77,255.80, 43.00% of its interest, and £102,408.86 (57.00%) is deferred. Nothing reaches items (6) to (9): the reserve closes at £0.00, a draw of £576,953.23, and the Class Z PDL is not cured. Items (1) to (5) needed £2,262,834.37, £679,362.09 more than the revenue collections; the reserve covers £576,953.23 of it, and the last £102,408.86 is Class B interest deferred.

**Step 5 — Principal.** £1,389,062.89 + £2,435,806.87 + £1,874,350.00 = £5,699,219.76, no cures. All of it goes to Class A, which falls from £179,004,077.51 to £173,304,857.75. Classes B and Z receive nothing.

**Step 6 — Closing state.** Pool: £197,872,207.01 − £5,699,219.76 − £712,946.38 = £191,460,040.87 (a reduction of £6,412,166.14). Notes £192,273,289.02; PDL £813,248.15; reserve £0.00; deferred Class B interest £102,408.86, due on the IPD of 15 September 2029.

**Step 7 — Checks.** (i) £2,160,425.51 − £2,160,425.51 = 0.00. (ii) £5,699,219.76 − £5,699,219.76 = 0.00. (iii) £100,301.77 + £712,946.38 − £0.00 − £813,248.15 = 0.00. (iv) £197,972,508.78 − £5,699,219.76 − £192,273,289.02 = 0.00. (v) Notes £192,273,289.02 − PDL £813,248.15 = £191,460,040.87 = pool. All five checks are 0.00. Class A credit enhancement is 9.48%; Class B's is 1.96%.

### Why each item ranks where it does

- **(1) Senior fees and expenses.** The trustee, cash manager, paying agent, corporate services provider and auditors keep the issuer running. If they are not paid they resign, and nobody runs the next IPD. So they come before every investor, including the extraordinary expense of IPD 2.
- **(2) Servicing fee.** Kingsbridge collects the cash that pays everyone. An unpaid servicer has no reason to chase arrears, and a back-up servicer would charge more; the fee sits above all note interest.
- **(3) Class A interest.** The AAA(sf) class is paid first because a Class A shortfall is an event of default: the rating promises timely interest.
- **(4) Class A PDL.** A loss that reached Class A is cured next, before any junior interest, so excess spread restores the senior class first. The cure becomes principal and pays Class A.
- **(5) Class B interest.** Class B is paid after Class A is whole for interest and principal losses. Its interest can be deferred without an event of default, which is what lets it rank here.
- **(6) Class B PDL.** The same logic one class down: cure the Class B losses before the reserve and the junior ledger.
- **(7) Reserve top-up.** The reserve protects next quarter's liquidity for items (1) to (6). Medway refills it before curing the Class Z PDL, so the rated notes' liquidity comes before the unrated class's principal.
- **(8) Class Z PDL.** Class Z is the first-loss piece held by Kingsbridge; its losses are cured only when everything above is satisfied.
- **(9) Residual.** What remains is Kingsbridge's profit on the deal, paid last so that it never takes cash the noteholders need.

### The five zero-checks

Each check proves one identity. A non-zero value always means a mistake, and its size tells you which one.

**(i) Revenue: available − allocated.** *Proves* that every pound of available revenue was paid to exactly one item, including the residual at (9). *Non-zero tells you* that cash was lost or created: a negative value means you paid more than you had (for example, the reserve at its required amount of £2,214,000.00 when only £576,953.23 was left gives −£1,637,046.77); a positive value means cash was left unallocated, for example a missing residual line.

**(ii) Principal: available − allocated.** *Proves* that the principal receipts plus the cures were all paid to the notes. *Non-zero tells you* that a cure was paid at (4), (6) or (8) but not added to available principal, or that principal was paid to Class B while Class A was outstanding and then counted twice.

**(iii) PDL: opening + debits − cures − closing.** *Proves* that the ledger rolls forward: every loss was recorded and every cure was taken off. *Non-zero tells you* that a debit or a cure is missing; a check of £61,884.15 in IPD 1 means you set the closing ledger to the period's debit and forgot the opening balance.

**(iv) Notes: opening − principal paid − closing.** *Proves* that the note balances fell by exactly the principal paid. *Non-zero tells you* that a note was reduced by something other than principal, for example a loss written off, or by a different figure from the one paid: if Class A is paid £6,314,894.13 but reduced by scheduled principal and prepayments only, to £179,147,337.51, the check reads −£143,260.00.

**(v) Notes − PDL − pool.** *Proves* the deal's balance sheet: the notes, less the losses not yet cured, equal the loans that back them. *Non-zero tells you* that the pool and the notes were rolled forward on different amounts: −£38,417.62 in IPD 1 means a loss was taken off a note and debited to the PDL as well; −£712,946.38 in IPD 2 means the losses were left in the pool or added to principal; +£1,874,350.00 means the recoveries reduced the pool but did not redeem the notes. This is also the check that ties Part B to Part C (D1).

### If you found …

*If your IPD 2 shows Class A interest short by £499,697.43 and you declared an event of default:* you left the reserve out of available revenue receipts. Items (1) to (3) need £2,083,169.71; the collections alone are £1,583,472.28. The reserve is part of available revenue (as in Chapter 13), and with it Class A is paid in full. Without it, Class B would have been owed £179,664.66 with nothing to pay it.

*If your IPD 1 servicing fee is £73,185.61:* you used the closing pool. The fee accrues on the pool at the start of the period. Your reserve then closes at £579,303.09 instead of £576,953.23.

*If your IPD 2 servicing fee is £77,214.03:* you used the IPD 1 opening pool, £204,225,518.76, again. Each IPD uses its own opening pool, here £197,872,207.01. Your deferral then becomes £104,810.93.

*If your IPD 1 Class A interest is £1,936,583.25:* you used Actual/360. Your reserve then closes at £550,424.70 instead of £576,953.23.

*If your IPD 2 Class A interest is £1,952,500.38:* you accrued on the IPD 1 opening balance, £185,318,971.64. Class A was redeemed by £6,314,894.13 in IPD 1; interest runs on the balance after that redemption. Your deferral then becomes £168,941.90.

*If your IPD 2 senior fees are £121,349.32:* you used 90 days, the length of IPD 1. IPD 2 runs from 15 March to 15 June: 92 days. Your deferral then becomes £101,367.77.

*If your IPD 2 deferral is £27,908.86:* you forgot the extraordinary senior expense of £74,500.00 at item (1).

*If your IPD 2 Class B interest due is £151,716.82:* you used the Class A rate, 4.18%, instead of SONIA + 1.35% = 4.95%. Your deferral then becomes £74,461.02.

*If your IPD 1 reserve is £538,535.61 and Class A receives £6,353,311.75:* you debited the loss to Class A first. Losses climb the capital structure from the bottom: Class Z first.

*If your Class Z note after IPD 1 is £4,530,013.65 and check (v) reads −38,417.62:* you wrote the loss off the note and debited the PDL as well. Medway never writes down a note: the PDL records the loss, and the note keeps its full claim until the PDL is cured or the deal ends. If you wrote the loss off the note *instead of* debiting the PDL, check (v) still balances, but the cure mechanism disappears: the next quarters' excess spread could no longer restore Class Z.

*If you cured the Class Z PDL in IPD 1 (£100,301.77) and your reserve closes at £476,651.46:* you put item (8) above item (7). While the reserve is below £2,214,000.00, excess spread refills it first. Your Class A then receives £6,415,195.90 instead of £6,314,894.13.

*If your IPD 2 Class A receives £3,824,869.76 and check (v) reads 1,874,350.00:* you left the recoveries out of available principal. Sale proceeds of repossessed properties are principal receipts. Class A would then close at £175,179,207.75.

*If your IPD 2 Class A receives £6,412,166.14:* you added the realised losses to available principal. A loss is cash that never arrived; it goes to the PDL, not to the notes. Check (v) shows −712,946.38.

*If your IPD 2 closing pool is £192,172,987.25:* you reduced the pool by principal receipts only. The loans sold at a loss leave the pool for their whole balance, recovered and lost parts together. Check (v) shows −712,946.38.

*If your IPD 1 reserve closes at £961,566.13:* you added the top-up to the opening balance, £384,612.90 + £576,953.23. The whole opening reserve was already in available revenue; the closing reserve is what item (7) receives, £576,953.23.

*If your IPD 1 revenue check (i) reads −1,637,046.77:* you paid item (7) its amount due, £2,214,000.00, instead of the cash left. Each item receives the lower of due and available.

*If your IPD 3 Class B amount due is £179,664.66 only:* you dropped the deferred interest from the closing state. The deferral of £102,408.86 is due on the next IPD with interest at the Class B rate, £1,277.73 for 92 days: £103,686.59 would be missing. The full amount due on 15 September 2029 is £283,351.25.

*If you added the PDL cures to the payments to Class Z:* a cure is not a payment to anyone. It moves cash from the revenue pot to the principal pot, which pays Class A first (Chapter 13).

### Trade-offs the exam tests

**Trade-off to keep in mind: the reserve in available revenue versus a separate liquidity reserve.** Putting the whole reserve into available revenue (the Thames and Medway design) gives the most liquidity to every item down to Class B interest, so Class B is protected as well as Class A. The cost is that the reserve can be used up by mezzanine interest in a single bad quarter, as IPD 2 shows: the reserve closes at £0.00. A separate liquidity reserve that may pay only items (1) to (3) behaves differently on the same data. In IPD 2 the collections fall £499,697.43 short of items (1) to (3); the liquidity reserve pays that, keeps £77,255.80, and Class B receives £0.00 and defers its full £179,664.66. The senior notes keep a cushion for the next quarter, and Class B bears the whole stress at once. IPD 1 is identical under both designs. Rating analysts size the reserve and its permitted uses together.

**Trade-off to keep in mind: the reserve top-up above versus below the Class Z PDL cure.** Medway refills the reserve at (7) before curing the Class Z PDL at (8). Reversing the two in IPD 1 cures the Class Z PDL in full (£100,301.77), redeems Class A further to £178,903,775.74 and raises its credit enhancement to 9.59%, against 9.54%. But the reserve closes at £476,651.46 instead of £576,953.23, and IPD 2 then has £2,060,123.74 of available revenue against £2,082,112.95 due at items (1) to (3). Class A interest receives £1,862,921.37 of £1,884,910.58: a shortfall of £21,989.21, which is an event of default, and Class B receives £0.00. Curing junior losses early improves the senior's subordination in good times; keeping liquidity first protects timely payment in bad times. The rating of Class A depends on timely interest, so Medway puts liquidity first.

**Trade-off to keep in mind: deferral of Class B interest versus an event of default.** Medway lets Class B interest defer while Class A is outstanding. In IPD 2 that turns a £102,408.86 shortfall into a debt of the issuer, due on 15 September 2029 with £1,277.73 of interest: £283,351.25 in all. The deal keeps running, Class A keeps receiving all the principal, and revenue can recover. If a Class B shortfall were an event of default, the trustee could accelerate the notes in a quarter in which Class A was paid in full. All cash would then run through the post-enforcement waterfall (Chapters 13 and 27), the deal could no longer wait for revenue to recover, and the AAA(sf) holders, who were paid in full, would face an enforcement they did not need. The price of deferral is borne by Class B: its holders wait, with no remedy while Class A is outstanding. That is why a deferrable class carries a wider margin, 1.35% against 0.58%.

**Trade-off to keep in mind: PDL versus direct write-down.** Medway records losses in a PDL; the notes keep their full balance. Under a write-down design, Class Z would stand at £4,468,129.50 after IPD 1 and £3,755,183.12 after IPD 2, and the losses would be gone for good. With a PDL, later excess spread cures the ledger, the cure redeems Class A, and Class Z recovers its claim: the £813,248.15 debited by IPD 2 is a debt the deal can still repay. Both designs give the same credit enhancement today (Class B 1.96% after IPD 2) and pass check (v), because in a write-down design the notes and the pool fall together. The difference is who keeps future excess spread: with a PDL it goes to the noteholders through the principal waterfall; with a write-down it falls to the residual and goes to Kingsbridge. A PDL therefore protects investors more, at the cost of a more complex ledger and of Class Z's balance overstating its expected recovery.

**Marking.** C1: 6 marks for IPD 1, 8 for IPD 2 (available revenue, each item due and paid, the deferral). C2: 4 marks. C3: 4 marks. C4: 3 marks. C5: 5 marks, one per check, and a check counts only if it is a formula that returns 0.00 on both IPDs.

## Part D — Linking and judgement

Each question is worth two marks and allows three lines. Full marks need the right figures and the mechanism that links them; a correct mechanism without figures, or figures without the mechanism, earns half.

### D1. The tie between the tape and the waterfall

**Model answer.** The reporting-pool total, £197,872,207.01, is the pool after IPD 1 and the opening pool of IPD 2 (notes £197,972,508.78 − PDL £100,301.77). The tape as delivered gives £199,428,804.55, £1,556,597.54 too much: £241,812.02 for the duplicate and £1,314,785.52 (nine times £146,087.28) for the decimal shift. A tape total that does not tie to the cash manager's pool means one of the two is wrong, and the investor report cannot be published until the difference is explained (Chapters 26 and 27).

**Marking guide.**

- *Full marks (2):* names the reporting-pool total and the IPD 1 closing pool, states that the check is 0.00, and gives the as-delivered difference with its two causes.
- *Half marks (1):* the tie is right but the as-delivered difference is missing or unexplained; or the difference is right but tied to the wrong waterfall figure.
- *Zero:* ties the tape to the notes outstanding (£197,972,508.78), or to the IPD 2 closing pool.

**Common weak answers.** "The pool total ties to the waterfall" misses which figure and when: the tape is dated 28 February 2029, the end of the collection period of IPD 1, so it ties to the IPD 1 closing pool. Tying to the notes ignores the PDL: the notes exceed the pool by the uncured losses, £100,301.77.

### D2. Arrears in the IPD 2 waterfall

**Model answer.** Borrowers in arrears do not pay all their interest. On the tape, 43 loans with £8,383,602.83 (4.24% of the pool) are at least one month behind, so revenue collections fall below the interest the pool should earn; in IPD 2 revenue is 34.04% lower than in IPD 1. Loans at three months or more (18 loans, £3,586,928.57, 1.81%) meet Kingsbridge's default definition: when their properties are sold, the shortfalls become realised losses, debited to the PDL. Arrears hit Medway twice: less revenue to cure losses, and more losses to cure (Chapters 3, 25 and 26).

**Marking guide.**

- *Full marks (2):* both channels, revenue and losses, each with a figure from the tape and its effect in the waterfall (reserve drawn, Class B deferred, PDL debited).
- *Half marks (1):* one channel only, or both channels without figures.
- *Zero:* "arrears reduce principal", or arrears treated as losses already.

**Common weak answers.** "Arrears cause losses" misses the first and faster channel: unpaid interest reduces revenue in the same quarter, long before a property is sold. "Arrears loans are written off" confuses arrears with realised loss: a loan in arrears is still in the pool, and most borrowers in one month of arrears pay it back.

### D3. The strats that drive expected loss

**Model answer.** Expected loss is PD × LGD × EAD. The arrears strat measures how many borrowers are on the way to default (PD); the indexed LTV strat measures how much of each defaulted loan the property sale recovers (LGD): at 55.84% WA indexed LTV, house prices must fall a long way before a sale fails to repay a loan. Region and repayment type refine both: London and the South East hold 48.96% of the pool, so a fall in their house prices moves LGD across half the pool, and interest-only and part-and-part loans (15.52%) carry maturity risk (Chapters 3 and 18).

**Marking guide.**

- *Full marks (2):* arrears to PD and indexed LTV to LGD, each with its reason.
- *Half marks (1):* the two strats named without the component, or the components swapped once.
- *Zero:* region and repayment type as the two drivers, with no link to PD or LGD.

**Common weak answers.** Naming original LTV instead of indexed LTV misses the point of indexation: LGD depends on today's value of the property, not the value at origination. Linking LTV to PD is half right (high-LTV borrowers default more), but the question asks for the main channel, which is severity.

### D4. An £18,000 difference with the bank statement

**Model answer.** Start with timing, then with content. (1) Did the report and the bank statement cut the collection period on the same day? Receipts after month-end belong to the next period. (2) Direct-debit recalls and indemnity claims reverse earlier credits. (3) Duplicate or unidentified receipts. (4) Revenue booked as principal or the reverse: the total can agree while each pot is wrong. (5) The net swap amount. Then confirm that every sweep reached the issuer within 3 business days: a late sweep is a servicer termination event (Chapter 27).

**Marking guide.**

- *Full marks (2):* at least four causes in a defensible order, timing first, and the sweep deadline.
- *Half marks (1):* a list of causes without an order, or an order with only two causes.
- *Zero:* "adjust the report to the bank statement", or "ask the servicer" with no investigation.

**Common weak answers.** Forcing the report to the bank figure hides the cause, and the same difference returns next quarter. Starting with the swap misses that the revenue collections are stated after the net swap flow and that timing differences are the most frequent cause. Ignoring the split between revenue and principal leaves the worst error undetected: a total that agrees while each waterfall is wrong.

### D5. The rating analyst's view after IPD 2

**Model answer.** Class A received all its interest and all available principal; its subordination is 9.48% of the pool after IPD 2, against 9.54% after IPD 1 and 8.39% at closing. Its rating holds. Class B is under pressure: it deferred £102,408.86, 57.00% of its interest; the reserve is empty against £2,214,000.00 required; and the Class Z PDL has consumed 17.80% of Class Z, leaving Class B 1.96% of subordination. The analyst places Class B on review for downgrade and asks for the next two quarters of arrears, collections and recoveries before the committee (Chapters 19, 20 and 29).

**Marking guide.**

- *Full marks (2):* a separate conclusion for each class, each supported by at least two figures from Part C.
- *Half marks (1):* the right conclusions without figures, or figures for one class only.
- *Zero:* "both classes are downgraded" or "Class A defaults", or no conclusion.

**Common weak answers.** "Class B defaulted" confuses deferral with default: the documents allow the deferral, and it is not an event of default while Class A is outstanding. "Downgrade Class A because losses rose" ignores that Class A's enhancement is 9.48%, above its 8.39% at closing. Downgrading Class B at once, without review, ignores that the committee needs evidence that the stress persists.

## Your score and what to do next

| Score | Level | What to do next |
|:---|:-------|:-----------|
| 85–100 | Ready for a junior desk role | Redo only the questions you missed; then read the trade-offs of Part C again |
| 65–84 | Ready; revise the flagged parts | Reread the chapter of every lost mark, then redo those questions closed book |
| 45–64 | Not yet | Revise Parts II, III and VII (Chapters 6–16 and 25–27), then sit the exam again |
| Below 45 | Restart | Restart from Part I and redo the exercises of each chapter |

: Bands. Whatever your total, a part below half its marks sends you back to its chapters.

The total out of 100 tells you whether you are ready. The parts tell you what to revise. Apply the rule of the table caption first: a part below half its marks (Part A below 10, Part B below 20, Part C below 15, Part D below 5) sends you back to its chapters, whatever your total.

**85–100: ready for a junior desk role.** You can do the month-one tasks unsupervised. Redo every question you missed until you can explain the diagnosis aloud. Then read the four trade-offs of Part C and B4 again: a director asks why the deal is built as it is, not only what it pays.

**65–84: ready, with gaps.** Your method is sound; specific skills are missing. List every lost mark with its chapter (the table *Where each question is taught*, in the book's Answer key), reread those chapters' Course and Common mistakes sections, redo their exercises, and redo the exam questions closed book one week later.

**45–64: not yet.** The marks are lost in the core of the job: the tape and the waterfall. Revise Parts II, III and VII in order, doing every exercise with the datasets, then sit the whole exam again after two weeks, without looking at these corrections in between.

**Below 45: restart.** The basics of Part I are not yet secure, and later chapters build on them. Restart from Chapter 1, do every exercise of each chapter before moving on, and sit the exam again only after Chapter 27.

**A revision plan for each weak area.**

| Weak area | Signs in your script | Revise | Then redo |
|:---|:---|:---|:---|
| Loan and bond arithmetic | A1, A2, A8, A12 wrong | Chapters 1, 2, 10, 14 | A1, A2, A8, A12 |
| Credit risk and enhancement | A3, A9, A10, D3 wrong | Chapters 3, 11, 12, 18 | A3, A9, A10, D3 |
| Deal structure and parties | A4–A6, A16, A17 wrong | Chapters 4, 5, 7, 21, 24, 25 | A4–A6, A16, A17 |
| Rates, ratings, regulation | A13–A15, A19, A20 wrong | Chapters 15–17, 20, 30, 33–35 | A13–A15, A19, A20 |
| Tape validation | fewer than six issues in B1; raw sheet changed | Chapters 7 and 8 | B1, B4 |
| Strats and reporting | B2 or B3 checks not 0; simple averages | Chapter 9 | B2, B3 |
| Waterfall mechanics | C1 or C2 wrong; reserve or PDL order | Chapters 12, 13, 26 | C1–C5 |
| Checks and reconciliation | C5 not 0; D1, D4 weak | Chapters 26, 27 | C5, D1, D4 |
| Judgement | D2, D5 without figures | Chapters 19, 20, 25, 29 | D2, D5 |

: Revision plan by weak area

Work through the plan in the order of the table: the arithmetic of the first row is used by every row below it. After each block of chapters, redo the questions in the last column closed book and mark them with these corrections. Sit the whole exam again only when every block scores at least three quarters of its marks.
