# Chapter 12 - Annualised excess spread of Thames Residential
# 2027-1 at closing, and its sensitivity to rates and prepayments.
# ILLUSTRATIVE base case: SONIA flat 3.75%, Bank Rate 3.75%,
# SVR 7.49%. Annual run-rates on closing balances. Base R only.
# Run from the book folder:
#   Rscript ch12/r/ch12_excess_spread.R \
#       data/thames_residential_2027_1_tape.csv

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
m <- function(x) formatC(round2(x), format = "f", digits = 2,
                         big.mark = ",")

notes <- data.frame(cls = c("A", "B", "C", "D", "E"),
  amount = c(553000000, 31800000, 19100000, 12700000, 9500000),
  margin = c(0.62, 1.10, 1.50, 2.20, 3.50))
fixed_fees <- 25000 + 20000 + 10000 + 50000 + 120000
servicing <- 0.15; issuer_profit <- 4000
swap_notional <- 542600271.48
subloan <- 9391500; subloan_margin <- 4.00

excess_spread <- function(tape, sonia = 3.75, swap = 3.30,
                          bank_shift = 0, svr = NA,
                          a_paydown = 0) {
  # Annual excess spread (GBP) and its parts.
  rate <- tape$current_rate
  trk <- tape$product_type == "Tracker"
  rate[trk] <- rate[trk] + bank_shift
  if (!is.na(svr)) rate[tape$product_type == "SVR"] <- svr
  bal <- tape$current_balance
  pool <- round2(sum(bal))
  p <- list(pool = pool,
            wa_rate = sum(bal * rate) / pool,
            pool_int = round2(sum(bal * rate) / 100),
            swap_pay = round2(swap_notional * swap / 100),
            swap_rec = round2(swap_notional * sonia / 100),
            fees = round2(fixed_fees + issuer_profit +
                          pool * servicing / 100))
  amt <- notes$amount - c(a_paydown, 0, 0, 0, 0)
  p$notes <- sum(round2(amt * (sonia + notes$margin) / 100))
  p$es <- round2(p$pool_int + p$swap_rec - p$swap_pay -
                 p$fees - p$notes)
  p$sub <- round2(subloan * (sonia + subloan_margin) / 100)
  p
}

args <- commandArgs(trailingOnly = TRUE)
tape <- read.csv(args[1])
b <- excess_spread(tape)
out <- list(
  c("Pool balance", m(b$pool)),
  c("WA loan rate (%)", sprintf("%.4f", b$wa_rate)),
  c("Pool interest", m(b$pool_int)),
  c("Swap: issuer receives", m(b$swap_rec)),
  c("Swap: issuer pays", m(-b$swap_pay)),
  c("Senior fees and profit", m(-b$fees)),
  c("Class A-E interest", m(-b$notes)),
  c("Excess spread", m(b$es)),
  c("  as % of pool", sprintf("%.4f", b$es / b$pool * 100)),
  c("Subordinated loan int.", m(-b$sub)),
  c("Left for items 18-19", m(b$es - b$sub)))
cat("Annual run-rate at closing (GBP, illustrative)\n")
for (x in out) cat(sprintf("%-24s%18s\n", x[1], x[2]))
svr <- tape$product_type == "SVR"
svr_bal <- round2(sum(tape$current_balance[svr]))
rev <- tape[grepl("Fixed", tape$product_type) &
            tape$fixed_rate_end_date < "2028-01-01", ]
up <- round2(sum(rev$current_balance *
                 (7.49 - rev$current_rate)) / 100)
scen <- list(
  list("SONIA, Bank Rate +1%",
       excess_spread(tape, sonia = 4.75, bank_shift = 1)),
  list("SONIA, Bank Rate -1%",
       excess_spread(tape, sonia = 2.75, bank_shift = -1)),
  list("SONIA +0.25% only", excess_spread(tape, sonia = 4.00)),
  list("SVR cut to 6.49%", excess_spread(tape, svr = 6.49)),
  list("All SVR loans prepay",
       excess_spread(tape[!svr, ], a_paydown = svr_bal)))
cat("\nSensitivities (annual excess spread, GBP)\n")
for (s in scen)
  cat(sprintf("%-24s%18s%16s\n", s[[1]], m(s[[2]]$es),
              m(s[[2]]$es - b$es)))
cat(sprintf("%-24s%18s%16s\n", "2027 fixed-end loans",
            m(b$es + up), m(up)))
cat(sprintf("  (%d loans, %s stay on SVR)\n", nrow(rev),
            m(sum(rev$current_balance))))
cat(sprintf("  (SVR loans: %d, %s)\n", sum(svr), m(svr_bal)))
