# Chapter 4 - why securitise: the cost of Thames funding
# compared with other sources, and a warehouse-to-term
# illustration. All market rates are ILLUSTRATIVE.
# Run from the book folder:
#   Rscript ch04/r/ch04_funding.R

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
m  <- function(x) formatC(x, format = "f", digits = 2,
                          big.mark = ",")
p4 <- function(x) sprintf("%.4f%%", x)

SONIA <- 3.75                     # % a year, illustrative
amount <- c(A = 553000000, B = 31800000, C = 19100000,
            D = 12700000, E = 9500000)
margin <- c(A = 0.62, B = 1.10, C = 1.50, D = 2.20, E = 3.50)
total <- sum(amount)
wa_margin <- sum(amount * margin) / total

# running costs paid to third parties (fees in the Deal Fact Sheets, Appendix D);
# cash management and servicing go to Kingsbridge itself
third_party <- 25000 + 20000 + 10000 + 120000 + 4 * 1000
UPFRONT <- 3000000; YEARS <- 5     # illustrative
running_pct <- third_party / total * 100
upfront_pct <- UPFRONT / YEARS / total * 100
all_in <- wa_margin + running_pct + upfront_pct
interest <- round2(total * (SONIA + wa_margin) / 100)

sources <- data.frame(
  name = c("Retail savings (rate 4.10%)", "Covered bond, 5 years",
           "Thames RMBS, all-in"),
  spread = c(4.10 - SONIA, 0.45, all_in))

POOL <- 300000000; ADVANCE <- 0.90; WH_MARGIN <- 1.75
senior <- POOL * ADVANCE
wh_6m  <- round2(senior * (SONIA + WH_MARGIN) / 100 * 182 / 365)
saving <- round2(senior * (WH_MARGIN - wa_margin) / 100)

cat("1. Thames Classes A-E\n")
cat("   Total amount           : ", m(total), "\n", sep = "")
cat("   Weighted average margin: ", p4(wa_margin), "\n", sep = "")
cat(sprintf("   Annual interest at SONIA %.2f%%: %s\n", SONIA,
            m(interest)))
cat("2. All-in cost of Thames funding, % a year\n")
cat("   Note margin            : ", p4(wa_margin), "\n", sep = "")
cat("   Third-party running    : ", p4(running_pct), "  (",
    m(third_party), " a year)\n", sep = "")
cat("   Upfront costs / ", YEARS, " yrs  : ", p4(upfront_pct), "\n",
    sep = "")
cat("   All-in spread          : SONIA + ", p4(all_in), "\n",
    sep = "")
cat("   All-in rate            : ", p4(SONIA + all_in), "\n",
    sep = "")
cat("3. Spread over SONIA by source (illustrative)\n")
for (i in seq_len(nrow(sources))) {
  cat(sprintf("   %-28s: %s\n", sources$name[i],
              p4(sources$spread[i])))
}
cat("4. Warehouse to term (illustrative)\n")
cat("   Senior warehouse funding: ", m(senior), "\n", sep = "")
cat("   Interest, 182 days      : ", m(wh_6m), "\n", sep = "")
cat("   Saving a year at term   : ", m(saving), "\n", sep = "")
