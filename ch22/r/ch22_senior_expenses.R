# Chapter 22 - senior expenses of Thames Residential 2027-1:
# annual budget at closing and the amount due on each of the
# first four IPDs.
# Run from the book folder:
#   Rscript ch22/r/ch22_senior_expenses.R \
#       data/thames_performance_monthly.csv
args <- commandArgs(trailingOnly = TRUE)
round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
f <- function(x, w) formatC(x, format = "f", digits = 2,
                            big.mark = ",", width = w)
POOL <- 635671146.31
FIXED <- c("Trustee" = 25000,
           "Paying agent and agent bank" = 10000,
           "Corporate services" = 20000,
           "Cash management" = 50000,
           "Other issuer expenses" = 120000)
SERV <- 0.0015
PROFIT <- 1000

serv_year <- round2(POOL * SERV)
for (k in names(FIXED)) {
  cat(sprintf("%-29s%s\n", k, f(FIXED[k], 14)))
}
cat(sprintf("%-29s%s\n", "Servicing (0.15% of pool)",
            f(serv_year, 14)))
total <- sum(FIXED) + serv_year
cat(sprintf("%-29s%s  %.4f%% of pool\n",
            "Total senior expenses", f(total, 14),
            100 * total / POOL))
cat(sprintf("%-29s%s\n", "Issuer profit (4 x 1,000)",
            f(4 * PROFIT, 14)))
cat(sprintf("%-29s%s\n", "Total with issuer profit",
            f(total + 4 * PROFIT, 14)))

# ---- the first four IPDs ----
ipds <- as.Date(c("2027-03-18", "2027-06-15", "2027-09-15",
                  "2027-12-15", "2028-03-15"))  # closing first
periods <- list(c("2027-02", "2027-03", "2027-04", "2027-05"),
                c("2027-06", "2027-07", "2027-08"),
                c("2027-09", "2027-10", "2027-11"),
                c("2027-12", "2028-01", "2028-02"))
perf <- read.csv(args[1], stringsAsFactors = FALSE)
opening <- setNames(perf$opening_balance,
                    perf$collection_period)
cat(sprintf("\n%-11s%4s%11s%12s%9s%13s\n", "IPD", "Days",
            "Fixed fees", "Servicing", "Profit", "Total"))
grand <- 0
for (i in 1:4) {
  days <- as.numeric(ipds[i + 1] - ipds[i])
  fixed <- sum(round2(FIXED * days / 365))
  serv <- sum(round2(opening[periods[[i]]] * SERV / 12))
  tot <- round2(fixed + serv + PROFIT)
  grand <- round2(grand + tot)
  cat(sprintf("%-11s%4d%s%s%s%s\n", format(ipds[i + 1]), days,
              f(fixed, 11), f(serv, 12), f(PROFIT, 9),
              f(tot, 13)))
}
cat(sprintf("%-15s%32s%s\n", "First year", "", f(grand, 13)))
