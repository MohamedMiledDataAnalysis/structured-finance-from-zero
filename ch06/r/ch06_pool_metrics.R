# Chapter 6 - LTV, LTI and weighted averages on the
# Thames Residential 2027-1 tape.
# Run from the book folder:
#   Rscript ch06/r/ch06_pool_metrics.R \
#       data/thames_residential_2027_1_tape.csv

args <- commandArgs(trailingOnly = TRUE)
t <- read.csv(args[1], stringsAsFactors = FALSE)

# 1. Loan-level ratios (LTV in %, LTI as a multiple)
t$oltv <- 100 * t$original_balance / t$original_valuation
t$cltv <- 100 * t$current_balance / t$original_valuation
t$lti  <- t$original_balance / t$gross_income

# 2. Weighted average: the weights are current balances
wa <- function(x, w = t$current_balance) sum(x * w) / sum(w)
f2 <- function(x, w = 0) formatC(x, format = "f", digits = 2,
                                 width = w)

bal <- sum(t$current_balance)
cat("Thames tape: ", nrow(t), " loans, balance ", f2(bal),
    "\n", sep = "")

ex <- t[t$loan_id == "KBS-000417", ]
cat("Loan KBS-000417\n")
cat("  original LTV (%)  ", f2(ex$oltv, 10), "\n", sep = "")
cat("  current LTV (%)   ", f2(ex$cltv, 10), "\n", sep = "")
cat("  LTI               ", f2(ex$lti, 10), "\n", sep = "")

cat("Pool averages            weighted   simple\n")
rows <- list(c("original LTV (%)", "oltv"),
             c("current LTV (%)", "cltv"),
             c("interest rate (%)", "current_rate"),
             c("seasoning (months)", "payments_made"),
             c("remaining term (m)", "remaining_term_months"),
             c("LTI", "lti"))
for (r in rows) {
  x <- t[[r[2]]]
  cat("  ", formatC(r[1], width = -21), f2(wa(x), 9),
      f2(mean(x), 9), "\n", sep = "")
}

# 3. High LTI loans (FPC threshold: LTI of 4.5 or more)
hi <- t[t$lti >= 4.5, ]
hb <- sum(hi$current_balance)
cat("LTI >= 4.5: ", nrow(hi), " loans, ",
    f2(100 * nrow(hi) / nrow(t)), "% of loans\n", sep = "")
cat("  balance ", f2(hb), ", ", f2(100 * hb / bal),
    "% of pool\n", sep = "")

# 4. Fixed-rate loans whose fixed period ends
#    within 12 months of the cut-off date
fx <- t$fixed_rate_end_date
rev <- t[fx != "" & !is.na(fx) & fx <= "2028-01-31", ]
cat("Fixed loans reverting by 2028-01-31: ", nrow(rev),
    "\n", sep = "")
cat("  balance ", f2(sum(rev$current_balance)), "\n", sep = "")
