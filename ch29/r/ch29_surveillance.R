# Chapter 29 - surveillance of Thames Residential 2027-1
# after the IPD of 15 March 2029. Run from the book folder:
#   Rscript ch29/r/ch29_surveillance.R \
#       data/thames_ipd_results.csv
# Reads the other inputs from the same folder.

args <- commandArgs(trailingOnly = TRUE)
D <- dirname(args[1])
ipd  <- read.csv(args[1], stringsAsFactors = FALSE)
perf <- rbind(
  read.csv(file.path(D, "thames_performance_monthly.csv")),
  read.csv(file.path(D, "ch26_thames_performance_2029_02.csv")))
req  <- read.csv(file.path(D, "ch29_required_ce.csv"),
                 stringsAsFactors = FALSE)
book <- read.csv(file.path(D, "kingsbridge_dynamic_book.csv"))

POOL0 <- 635671146.31; RESERVE <- 9391500
CLS <- c("a", "b", "c", "d", "e", "z")
RATING <- c(a = "AAA(sf)", b = "AA(sf)", c = "A(sf)",
            d = "BBB(sf)", e = "BB(sf)")
round2 <- function(x) sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100

# Chapter 10 base case, spread evenly within each year
DEFAULTS <- 9273541; SEV <- 0.166838; LAG <- 18
TIMING <- c(5.73, 11.07, 23.34, 28.88, 19.09,
            8.01, 2.70, 0.84, 0.26, 0.08)
DEF  <- round2(DEFAULTS * TIMING[(0:119) %/% 12 + 1] / 1200)
LOSS <- round2(DEF * SEV)
base_case <- function(t) {
  los <- if (t > LAG) sum(LOSS[1:(t - LAG)]) else 0
  c(100 * sum(DEF[1:t]) / POOL0, 100 * los / POOL0)
}

ce <- function(row, pool) {
  # CE of each rated class, % of pool:
  # classes below it plus the reserve
  sapply(1:5, function(i) {
    below <- sum(unlist(row[paste0("class_", CLS[(i + 1):6],
                                   "_balance_after")]))
    100 * (below + RESERVE) / pool
  })
}

big <- function(x, d = 2) formatC(x, format = "f", digits = d,
                                   big.mark = ",")
perf$arr3 <- perf$arrears_3_6m_pct + perf$arrears_6m_plus_pct
perf$cum_loss <- 100 * cumsum(perf$realised_losses) / POOL0
n <- nrow(perf); last <- perf[n, ]
b26 <- book[startsWith(book$month, "2026"), ]
bk3 <- mean(b26$arrears_3_6m_pct + b26$arrears_6_12m_pct +
            b26$arrears_12m_plus_pct)
bb <- base_case(n)
cdef <- 100 * sum(perf$defaulted_balance) / POOL0
sev <- sum(perf$realised_losses) / sum(perf$defaulted_balance)
el <- 100 * sum(LOSS) / POOL0
now <- ipd[nrow(ipd), ]
cat("THAMES RESIDENTIAL 2027-1  surveillance after IPD ",
    now$ipd, "\n", sep = "")
cat("Pool balance        : ", big(last$closing_balance),
    "  factor ", sprintf("%.2f%%",
    100 * last$closing_balance / POOL0), "\n", sep = "")
cat("Loans               : ", big(last$loans_closing, 0),
    "\n", sep = "")
cat("Cum. defaults       : ", big(sum(perf$defaulted_balance)),
    " = ", sprintf("%.4f%%", cdef), "\n", sep = "")
cat("  base case month ", n, ": ", sprintf("%.4f%%", bb[1]),
    "  actual/base ", sprintf("%.0f%%", 100 * cdef / bb[1]),
    "\n", sep = "")
cat("Cum. net loss       : ", big(sum(perf$realised_losses)),
    " = ", sprintf("%.4f%%", last$cum_loss), "\n", sep = "")
cat("  base case month ", n, ": ", sprintf("%.4f%%", bb[2]),
    "  actual/base ", sprintf("%.0f%%", 100 * last$cum_loss / bb[2]),
    "\n", sep = "")
cat("Severity to date    : ", sprintf("%.2f%%", 100 * sev),
    "  (base ", sprintf("%.2f%%", 100 * SEV), ")\n", sep = "")
cat("Share of lifetime EL: ",
    sprintf("%.1f%% of %.4f%%", 100 * last$cum_loss / el, el),
    "\n", sep = "")
cat("3m+ arrears         : ", sprintf("%.3f%%", last$arr3),
    "  (Kingsbridge book 2026: ", sprintf("%.3f%%", bk3), ")\n",
    sep = "")
cat("CPR 3m / 12m average: ",
    sprintf("%.2f%% / %.2f%%",
            mean(tail(perf$cpr_annualised_pct, 3)),
            mean(tail(perf$cpr_annualised_pct, 12))),
    "  (base 11.15%)\n", sep = "")

cat("\nIPD         factor   CE A   CE B   CE C   CE D   CE E\n")
hist <- t(sapply(1:nrow(ipd), function(i)
  ce(ipd[i, ], ipd$pool_balance_end[i])))
for (i in 1:nrow(ipd)) {
  cat(ipd$ipd[i], "  ", sprintf("%6.2f%%",
      100 * ipd$pool_balance_end[i] / POOL0),
      paste(sprintf("%7.2f", hist[i, ]), collapse = ""),
      "\n", sep = "")
}

xs <- with(ipd, r16_class_z_pdl + r17_sub_swap_termination +
             r18_sub_loan_interest + r18_sub_loan_principal +
             r19_deferred_consideration)
pdl_of <- function(i) sum(unlist(ipd[i, paste0("pdl_", CLS,
                                                "_after")]))
cat("\nIPD         reserve        PDL     excess spread\n")
for (i in 1:nrow(ipd)) {
  cat(ipd$ipd[i], "  ", big(ipd$reserve_balance_after[i]),
      "  ", sprintf("%6.2f", pdl_of(i)), "  ",
      formatC(xs[i], format = "f", digits = 2, big.mark = ",",
              width = 14), "\n", sep = "")
}

yn <- function(t) if (t) "YES" else "NO"
k <- nrow(ipd)
cat("\nTrigger checks at ", now$ipd, "\n", sep = "")
tr <- function(label, v) cat("  ", label, " ", yn(v), "\n",
                             sep = "")
tr("Reserve at required amount :",
   now$reserve_balance_after >= RESERVE)
tr("All PDL sub-ledgers at zero:", pdl_of(k) == 0)
tr("Reserve ever drawn         :", sum(ipd$reserve_drawn) > 0)
tr("Principal paid interest    :",
   sum(ipd$principal_addition_amounts) > 0)
tr("Pool above clean-up (10%)  :",
   now$pool_balance_end > 0.10 * POOL0)

cat("\nRating test, required CE (illustrative)\n")
cat("Class  rating   CE now  passes   cushion\n")
cur <- hist[k, ]
for (j in 1:5) {
  ok <- req[req$surveillance_required_ce_pct <= cur[j], ]
  cat("  ", toupper(CLS[j]), "    ",
      formatC(RATING[CLS[j]], width = -8), " ",
      sprintf("%6.2f", cur[j]), "  ",
      formatC(ok$rating[1], width = -8), " ",
      sprintf("%5.2f", cur[j] - ok$surveillance_required_ce_pct[1]),
      "\n", sep = "")
}

# classes below AAA: IPDs to reach the next category
cat("\nNext category  gain/IPD   gap   IPDs needed\n")
for (j in 3:5) {
  nxt <- req$rating[match(RATING[CLS[j]], req$rating) - 1]
  need <- req$surveillance_required_ce_pct[req$rating == nxt]
  step <- (hist[k, j] - hist[k - 4, j]) / 4
  gap <- need - cur[j]
  cat("  ", toupper(CLS[j]), " to ", formatC(nxt, width = -8),
      "  ", sprintf("%7.4f", step), "  ", sprintf("%5.2f", gap),
      "  ", sprintf("%4.0f", ceiling(gap / step)), "\n",
      sep = "")
}
