# Chapter 8 - agreed-upon procedures: sample size,
# systematic sample selection and upper error rates.
# Run from the book folder:
#   Rscript ch08/r/ch08_aup_sample.R \
#       data/thames_residential_2027_1_tape.csv

args <- commandArgs(trailingOnly = TRUE)
t <- read.csv(args[1], stringsAsFactors = FALSE)
t <- t[order(t$loan_id), ]
CONF <- 0.99; TOL <- 0.01     # confidence, tolerable error
f2 <- function(x, w = 0) formatC(x, format = "f", digits = 2,
                                 width = w)

# 1. Sample size with zero expected errors
n <- ceiling(log(1 - CONF) / log(1 - TOL))
N <- nrow(t)
cat("Pool: ", N, " loans, balance ", f2(sum(t$current_balance)),
    "\n", sep = "")
cat("Sample size (99% confidence, 1% tolerable): ", n, "\n",
    sep = "")

# 2. Systematic selection: start 3.2, interval N / n.
#    Integer arithmetic so every tool picks the same loans.
pos <- (32 * n + (0:(n - 1)) * 10 * N) %/% (10 * n)
s <- t[pos, ]
cat("Interval ", formatC(N / n, format = "f", digits = 4),
    ", first positions ", paste(pos[1:5], collapse = " "),
    "\n", sep = "")
cat("First loans: ", paste(s$loan_id[1:3], collapse = " "),
    "\n", sep = "")
sb <- sum(s$current_balance)
cat("Sample balance ", f2(sb), " (",
    f2(100 * sb / sum(t$current_balance)), "% of pool)\n",
    sep = "")

# 3. Is the sample like the pool?
profile <- function(d) {
  w <- d$current_balance
  fx <- d$product_type %in% c("2Y Fixed", "5Y Fixed")
  oltv <- 100 * d$original_balance / d$original_valuation
  c(100 * sum(w[fx]) / sum(w), sum(oltv * w) / sum(w),
    sum(d$current_rate * w) / sum(w))
}
a <- profile(s); b <- profile(t)
labs <- c("fixed rate (% bal)", "WA original LTV",
          "WA interest rate")
cat("                       sample    pool\n")
for (j in 1:3)
  cat("  ", formatC(labs[j], width = -19), f2(a[j], 9),
      f2(b[j], 8), "\n", sep = "")

# 4. Upper error rate at 99% confidence (Clopper-Pearson)
cat("Upper error rate, 99% confidence\n")
for (k in 0:2) {
  u <- qbeta(CONF, k + 1, n - k)
  cat("  ", k, " errors in ", n, ": ",
      formatC(100 * u, format = "f", digits = 3), "%\n",
      sep = "")
}
