# Chapter 2 - bonds: Thames Class A coupon, fixed-rate bond
# price, yield, spread, accrued interest, duration, and the
# discount margin of a floating-rate note.
# Run from the book folder:
#   Rscript ch02/r/ch02_bonds.R data/thames_sonia_assumption.csv

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
f2 <- function(x) formatC(x, format = "f", digits = 2,
                          big.mark = ",")
f4 <- function(x) formatC(x, format = "f", digits = 4)

# ---- 1. Thames Class A: first interest period ----------
args  <- commandArgs(trailingOnly = TRUE)
son   <- read.csv(args[1])
sonia <- son$compounded_sonia_pct[1]
face_a <- 553000000
days <- as.numeric(as.Date("2027-06-15") -
                   as.Date("2027-03-18"))
rate <- (sonia + 0.62) / 100
coupon_a <- round2(face_a * rate * days / 365)
per_100k <- round2(100000 * rate * days / 365)

# ---- 2. A fixed-rate bond: price from yield -------------
price <- function(cpn, y, n, face = 100) {
  sum(cpn / (1 + y)^(1:n)) + face / (1 + y)^n
}
yield_from_price <- function(p, cpn, n, lo = 0, hi = 0.20) {
  for (i in 1:100) {
    mid <- (lo + hi) / 2
    if (price(cpn, mid, n) > p) lo <- mid else hi <- mid
  }
  (lo + hi) / 2
}
cpn <- 4.00; n <- 5; y <- 0.045
p <- price(cpn, y, n)
y_market <- yield_from_price(98.60, cpn, n)
gilt <- 0.039                     # illustrative gilt yield
spread_bp  <- (y - gilt) * 10000
spread_mkt <- (y_market - gilt) * 10000
acc <- cpn * 73 / 365
clean <- round2(p); dirty <- clean + acc
cf  <- c(rep(cpn, n - 1), cpn + 100)
pv  <- cf / (1 + y)^(1:n)
mac <- sum((1:n) * pv) / p
mod <- mac / (1 + y)
p_up <- price(cpn, y + 0.01, n)
approx_up <- p * (1 - mod * 0.01)
pv01 <- mod * p / 10000

# ---- 3. Floating-rate note: discount margin ------------
frn_price <- function(dm, s, qm, q) {
  c <- (s + qm) / 4; d <- 1 + (s + dm) / 400
  sum(c / d^(1:q)) + 100 / d^q
}
dm_from_price <- function(px, s, qm, q) {
  lo <- -5; hi <- 10
  for (i in 1:100) {
    mid <- (lo + hi) / 2
    if (frn_price(mid, s, qm, q) > px) lo <- mid else hi <- mid
  }
  (lo + hi) / 2
}
dm_par <- dm_from_price(100, sonia, 0.62, 20)
dm_995 <- dm_from_price(99.50, sonia, 0.62, 20)

# ---- 4. Amortising bond: 20 repaid each year ----------
out_bal <- 100 - 20 * (0:4)
amort_int <- sum(out_bal * cpn / 100)
wal <- sum((1:5) * 20) / 100

cat("1. Thames Class A, first interest period\n")
cat(sprintf("   Days: %d   coupon rate: %.2f%%\n", days, rate * 100))
cat("   Interest on Class A   : ", f2(coupon_a), "\n", sep = "")
cat("   Interest per 100,000  : ", f2(per_100k), "\n", sep = "")
cat("2. Fixed-rate bond: 4.00% annual, 5 years\n")
cat("   Price at 4.50% yield  : ", f4(p), "\n", sep = "")
cat(sprintf("   Yield at price 98.60  : %s%%\n", f4(y_market * 100)))
cat(sprintf("   Spread over gilt 3.90%%: %.0f bp (at 98.60: %.2f bp)\n",
            spread_bp, spread_mkt))
cat(sprintf("   Accrued (73 days) %s  clean %.2f  dirty %.2f\n",
            f4(acc), clean, dirty))
cat(sprintf("   Duration: Macaulay %s years, modified %s\n",
            f4(mac), f4(mod)))
cat(sprintf("   Price at 5.50%%: exact %s, estimate %s\n",
            f4(p_up), f4(approx_up)))
cat("   PV01 per 100          : ", f4(pv01), "\n", sep = "")
cat("3. Floating-rate note, SONIA + 0.62%, 20 quarters\n")
cat(sprintf("   Discount margin: %s%% at 100.00, %s%% at 99.50\n",
            f4(dm_par), f4(dm_995)))
cat("4. Amortising bond: 100 repaid 20 a year, 4.00%\n")
cat(sprintf("   Total interest %.2f (bullet %.2f), WAL %.2f years\n",
            amort_int, cpn * n, wal))
