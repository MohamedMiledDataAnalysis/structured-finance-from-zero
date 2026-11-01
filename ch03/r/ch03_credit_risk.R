# Chapter 3 - credit risk: arrears at cut-off, loss on a
# defaulted loan, expected loss of the Thames pool, CPR and
# SMM, and concentration.
# Run from the book folder:
#   Rscript ch03/r/ch03_credit_risk.R \
#     data/thames_residential_2027_1_tape.csv \
#     data/kingsbridge_static_pool_defaults.csv \
#     data/kingsbridge_dynamic_book.csv

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
m  <- function(x) formatC(x, format = "f", digits = 2,
                          big.mark = ",")
p2 <- function(x) sprintf("%.2f%%", x)
p4 <- function(x) sprintf("%.4f%%", x)

args   <- commandArgs(trailingOnly = TRUE)
tape   <- read.csv(args[1])
static <- read.csv(args[2])
book   <- read.csv(args[3])
pool   <- sum(tape$current_balance)

# ---- 1. Arrears at cut-off -----------------------------
arr <- tape[tape$months_in_arrears > 0, ]
arr_bal <- sum(arr$current_balance)

# ---- 2. Loss on one defaulted loan (illustrative) ------
HPI_FALL <- 0.10; FORCED <- 0.15; COSTS <- 6000
MONTHS_UNPAID <- 21; LAG_YEARS <- 1.5
loan_loss <- function(id) {
  ln  <- tape[tape$loan_id == id, ]
  bal <- ln$current_balance
  unpaid <- round2(bal * ln$current_rate / 100 *
                   MONTHS_UNPAID / 12)
  claim <- bal + unpaid + COSTS
  sale  <- round2(ln$original_valuation * (1 - HPI_FALL) *
                  (1 - FORCED))
  loss  <- max(claim - sale, 0)
  list(ltv = bal / ln$original_valuation * 100, bal = bal,
       unpaid = unpaid, claim = claim, sale = sale,
       loss = loss, sev = loss / bal * 100,
       rate = ln$current_rate)
}

# ---- 3. Expected loss of the pool ----------------------
AGE <- 96
s <- static[static$months_since_origination == AGE, ]
w <- s$originated_balance
pd_pct <- sum(w * s$cumulative_default_pct) / sum(w)
lgd <- sum(w * s$cumulative_net_loss_pct) /
       sum(w * s$cumulative_default_pct)
el <- round2(pd_pct / 100 * lgd * pool)

# ---- 4. Prepayment: CPR and SMM ------------------------
cpr <- mean(book$cpr_annualised_pct[
  substr(book$month, 1, 4) == "2026"])
smm <- 1 - (1 - cpr / 100)^(1 / 12)
prepay_1 <- round2(pool * smm)
cpr_from_1 <- 1 - (1 - 0.01)^12

# ---- 5. Concentration ----------------------------------
reg <- sort(tapply(tape$current_balance, tape$region, sum),
            decreasing = TRUE)
top10 <- sum(sort(tape$current_balance,
                  decreasing = TRUE)[1:10])
big <- max(tape$current_balance)

cat("1. Arrears at cut-off\n")
cat("   Loans 1 month in arrears : ", nrow(arr), "\n", sep = "")
cat("   Their balance            : ", m(arr_bal), "\n", sep = "")
cat("   Share of pool balance    : ", p2(arr_bal / pool * 100),
    "\n", sep = "")
cat("2. Loss if the loan defaults (illustrative)\n")
for (id in c("KBS-001857", "KBS-000417")) {
  r <- loan_loss(id)
  cat("   ", id, ": LTV ", p2(r$ltv), ", claim ", m(r$claim),
      ", sale ", m(r$sale), "\n", sep = "")
  cat("     loss ", m(r$loss), ", severity ", p2(r$sev),
      ", surplus ", m(max(r$sale - r$claim, 0)), "\n", sep = "")
}
r <- loan_loss("KBS-001857")
pv_sale <- r$sale / (1 + r$rate / 100)^LAG_YEARS
cat("   KBS-001857 sale paid 18 months later, PV ", m(pv_sale),
    "\n", sep = "")
cat("3. Expected loss of the Thames pool\n")
cat("   Vintages with ", AGE, " months of history: ", nrow(s),
    " (", s$vintage[1], "-", s$vintage[nrow(s)], ")\n", sep = "")
cat("   PD  (cumulative default, ", AGE, " months): ", p4(pd_pct),
    "\n", sep = "")
cat("   LGD (net loss / default)          : ", p2(lgd * 100),
    "\n", sep = "")
cat("   EAD (pool balance at cut-off)     : ", m(pool), "\n",
    sep = "")
cat("   Expected loss                     : ", m(el), "\n", sep = "")
cat("   Expected loss, % of pool          : ", p4(el / pool * 100),
    "\n", sep = "")
cat("4. Prepayment\n")
cat("   Average CPR, Kingsbridge book 2026: ", p2(cpr), "\n",
    sep = "")
cat("   SMM                               : ", p4(smm * 100),
    "\n", sep = "")
cat("   One month's prepayment on the pool: ", m(prepay_1), "\n",
    sep = "")
cat("   CPR for an SMM of 1.00%           : ",
    p2(cpr_from_1 * 100), "\n", sep = "")
cat("5. Concentration\n")
cat("   Largest region   : ", names(reg)[1], " ",
    p2(reg[1] / pool * 100), "\n", sep = "")
cat("   Largest loan     : ", m(big), " (", p2(big / pool * 100),
    ")\n", sep = "")
cat("   Ten largest loans: ", m(top10), " (",
    p2(top10 / pool * 100), ")\n", sep = "")
