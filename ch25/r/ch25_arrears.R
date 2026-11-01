# Chapter 25 - Thames arrears roll-rate matrix and
# repossession recoveries.
# Run from the book folder:
#   Rscript ch25/r/ch25_arrears.R \
#       data/ch25_thames_arrears_states.csv
# Also reads data/ch25_thames_repossessions.csv.

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-6) / 100
}
money <- function(x) {
  formatC(x, format = "f", digits = 2, big.mark = ",")
}

# state codes: 0 up to date, 1..11 months in arrears,
# -1 redeemed, -2 property sold after possession
bk <- data.frame(name = c("Current", "1 month", "2 months",
                          "3m+", "Left"),
                 lo = c(0, 1, 2, 3, -2),
                 hi = c(0, 1, 2, 11, -1))

args <- commandArgs(trailingOnly = TRUE)
st <- as.matrix(read.csv(args[1])[, -1])
frm <- st[, -ncol(st)]; to <- st[, -1]   # month t, month t+1
m <- matrix(0L, 4, 5)
for (i in 1:4) {
  fi <- frm >= bk$lo[i] & frm <= bk$hi[i]
  for (j in 1:5)
    m[i, j] <- sum(fi & to >= bk$lo[j] & to <= bk$hi[j])
}
cat("Roll-rate matrix: loan-months, Feb 2027-Jan 2029\n")
cat(sprintf("%-10s", "From / To"),
    sprintf("%10s", bk$name), "\n", sep = "")
for (i in 1:4)
  cat(sprintf("%-10s", bk$name[i]),
      sprintf("%10s", formatC(m[i, ], big.mark = ",",
                              format = "d")), "\n", sep = "")
cat("Roll rates (% of each row)\n")
for (i in 1:4)
  cat(sprintf("%-10s", bk$name[i]),
      sprintf("%10.2f", round2(m[i, ] * 100 / sum(m[i, ]))),
      "\n", sep = "")

rp <- read.csv(file.path(dirname(args[1]),
                         "ch25_thames_repossessions.csv"))
yy <- as.integer(substr(rp$collection_period, 1, 4))
mm <- as.integer(substr(rp$collection_period, 6, 7))
rp$months <- (yy - 2027) * 12 + mm - 1   # since Jan 2027
idx <- 1.02^(rp$months / 12)
value <- rp$original_valuation * idx
gross <- round2(value * 0.70)               # forced-sale price
net <- round2(value * 0.70 * 0.95)          # less 5% costs
costs <- round2(gross - net)
prin <- pmin(net, rp$balance_at_sale)
ints <- round2(pmax(pmin(net - rp$balance_at_sale,
                         rp$arrears_owed), 0))
loss <- round2(pmax(rp$balance_at_sale - net, 0))
surplus <- round2(pmax(net - rp$balance_at_sale -
                       rp$arrears_owed, 0))
k <- which(rp$loan_id == "KBS-001411")
cat("KBS-001411: net proceeds ", money(net[k]), " loss ",
    money(loss[k]), "\n", sep = "")
cat("All", nrow(rp), "properties sold\n")
tot <- c("balance at sale" = sum(rp$balance_at_sale),
         "principal recovered" = sum(prin),
         "arrears interest recovered" = sum(ints),
         "realised losses" = sum(loss),
         "surplus paid to borrowers" = sum(surplus))
for (t in names(tot))
  cat(sprintf("  %-26s%14s\n", t, money(round2(tot[[t]]))))
cat(sprintf("  %-26s%13.2f%%\n", "loss severity",
            round2(sum(loss) * 100 / sum(rp$balance_at_sale))))
