# Chapter 35 - SEC-SA risk weights for the Thames notes.
# Usage (from the book folder):
#   Rscript ch35/r/ch35_sec_sa.R \
#       data/thames_residential_2027_1_tape.csv
# Same method as ch35/python/ch35_sec_sa.py:
# loan-splitting risk weights (20% up to 55% of value, 75%
# above), funded reserve as a tranche with 20% RW cash,
# then the SEC-SA formula (CRR Articles 261 and 262).

args    <- commandArgs(trailingOnly = TRUE)
tape    <- read.csv(args[1])
reserve <- 9391500.00
cash_rw <- 0.20
classes <- data.frame(
  name   = c("A", "B", "C", "D", "E", "Z"),
  amount = c(553000000, 31800000, 19100000, 12700000,
             9500000, 9571146.31))

loan_rwa <- function(balance, value) {
  secured <- pmin(balance, 0.55 * value)
  0.20 * secured + 0.75 * (balance - secured)
}

k_ssfa <- function(A, D, ka, p) {
  a <- -1 / (p * ka)
  u <- D - ka
  l <- max(A - ka, 0)
  (exp(a * u) - exp(a * l)) / (a * (u - l))
}

sec_sa_rw <- function(A, D, ka, p, floor) {
  if (D <= ka) return(12.5)
  if (A >= ka) return(max(floor, 12.5 * k_ssfa(A, D, ka, p)))
  rw <- (ka - A) / (D - A) * 12.5 +
        (D - ka) / (D - A) * 12.5 * k_ssfa(A, D, ka, p)
  max(floor, rw)
}

pool  <- round(sum(tape$current_balance), 2)
rwa   <- sum(loan_rwa(tape$current_balance,
                      tape$original_valuation))
total <- pool + reserve
ksa   <- 0.08 * (rwa + cash_rw * reserve) / total
dflt  <- tape$months_in_arrears >= 3
w     <- sum(tape$current_balance[dflt]) / pool
ka    <- (1 - w) * ksa + w * 0.5

cat(sprintf("Pool balance (GBP)       : %.2f\n", pool))
cat(sprintf("Reserve fund (GBP)       : %.2f\n", reserve))
cat(sprintf("Loan RWA (GBP)           : %.2f\n", rwa))
cat(sprintf("Average loan risk weight : %.2f%%\n",
            rwa / pool * 100))
cat(sprintf("KSA                      : %.4f%%\n", ksa * 100))
cat(sprintf("W                        : %.4f\n", w))
cat(sprintf("KA                       : %.4f%%\n", ka * 100))
cat("Class  A (%)    D (%)    RW STS  RW non-STS\n")
above <- total
res <- list()
for (i in 1:5) {
  D <- above / total
  above <- above - classes$amount[i]
  A <- above / total
  fl <- if (classes$name[i] == "A") 0.10 else 0.15
  rs <- sec_sa_rw(A, D, ka, 0.5, fl)
  rn <- sec_sa_rw(A, D, ka, 1.0, 0.15)
  res[[i]] <- c(rs, rn)
  cat(sprintf("%-5s%7.4f %8.4f %8.2f%% %9.2f%%\n",
              classes$name[i], A * 100, D * 100,
              rs * 100, rn * 100))
}
cat(sprintf("Z    D = %.4f%% <= KA, RW = 1250.00%%\n",
            classes$amount[6] / total * 100))
cat("Capital per GBP 1m held (STS / non-STS):\n")
for (i in 1:5) {
  cat(sprintf("  %s: %10.2f / %10.2f\n", classes$name[i],
              round(res[[i]][1] * 0.08 * 1e6, 2),
              round(res[[i]][2] * 0.08 * 1e6, 2)))
}
