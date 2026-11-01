# Chapter 27 - Thames first investor report, cash
# reconciliations and trigger tests for the 8 IPDs.
# Run from the book folder:
#   Rscript ch27/r/ch27_report.R data/thames_ipd_results.csv
# Also reads, in the same folder:
#   thames_performance_monthly.csv,
#   ch26_thames_performance_2029_02.csv,
#   ch27_thames_bank_statement_ipd1.csv,
#   ch27_thames_daily_collections.csv.

round2 <- function(x, d = 2) {
  sign(x) * floor(abs(x) * 10^d + 0.5 + 1e-6) / 10^d
}
mo <- function(x) {
  formatC(round2(x), format = "f", digits = 2, big.mark = ",")
}
cutoff_pool <- 635671146.31
margin <- c(A = 0.62, B = 1.10, C = 1.50, D = 2.20, E = 3.50)
orig <- c(A = 553000000, B = 31800000, C = 19100000,
          D = 12700000, E = 9500000, Z = 9571146.31)
fields <- c("interest_collected", "arrears_interest_recovered",
            "scheduled_principal", "prepayments",
            "principal_recoveries")

args <- commandArgs(trailingOnly = TRUE)
folder <- dirname(args[1])
rd <- function(f) read.csv(file.path(folder, f))
res <- read.csv(args[1])
perf <- rbind(rd("thames_performance_monthly.csv"),
              rd("ch26_thames_performance_2029_02.csv"))
rownames(perf) <- perf$collection_period
st <- rd("ch27_thames_bank_statement_ipd1.csv")
dc <- rd("ch27_thames_daily_collections.csv")
x <- res[1, ]
line <- function(t, v) cat(sprintf("  %-34s%16s\n", t, mo(v)))

# ---- 1. collections to bank statement ----
kb <- startsWith(st$description, "Kingsbridge: coll")
credits <- round2(sum(st$credit[kb]))
indem <- round2(sum(st$debit[grepl("indemnity",
                                   st$description)]))
june <- round2(sum(dc$amount[dc$collection_period ==
                               "2027-06"]))
bank <- round2(credits - indem - june)
serv <- round2(sum(as.matrix(perf[c("2027-02", "2027-03",
                                    "2027-04", "2027-05"),
                                  fields])))
lag <- max(dc$business_days_to_transfer[
  dc$receipt_date >= "2027-03-18"])
cat("1. Collections: bank statement to servicer report\n")
line("Credits from Kingsbridge", credits)
line("less Direct Debit indemnity claim", -indem)
line("less June receipts (next IPD)", -june)
line("Feb-May collections per bank", bank)
line("Feb-May collections per servicer", serv)
line("Difference", bank - serv)
cat("  Longest sweep after closing: ", lag,
    " business days (limit 3)\n", sep = "")

# ---- 2. waterfall to bank statement ----
paid <- round2(sum(st$debit[st$date == "2027-06-15"]))
wf <- round2(x$available_revenue - x$r15_reserve_credit -
             x$r03_issuer_profit + x$available_principal)
cat("2. IPD payments: waterfall to bank statement\n")
line("Paid out per waterfall", wf)
line("Debits on 15 Jun per statement", paid)
line("Difference", wf - paid)
end <- st$balance[nrow(st)]
line("Balance after the IPD", end)
line("= June receipts + issuer profit",
     june + x$r03_issuer_profit)

# ---- 3. note table of the first investor report ----
cat("3. Notes after the IPD of 15 June 2027\n")
cat(sprintf("%-6s%16s%15s%16s%9s\n", "Class", "Before",
            "Principal", "After", "Factor"))
for (c in names(orig)) {
  p <- x[[paste0("class_", tolower(c), "_principal")]]
  after <- x[[paste0("class_", tolower(c), "_balance_after")]]
  cat(sprintf("%-6s%16s%15s%16s%9.6f\n", c, mo(orig[[c]]),
              mo(p), mo(after), round2(after / orig[[c]], 6)))
}
cat(sprintf("%-6s%8s%16s\n", "Class", "Rate %",
            "Interest paid"))
num <- c(A = 5, B = 7, C = 9, D = 11, E = 13)
for (c in names(margin)) {
  k <- sprintf("r%02d_class_%s_interest", num[[c]], tolower(c))
  cat(sprintf("%-6s%8.2f%16s\n", c,
              x$compounded_sonia_pct + margin[[c]], mo(x[[k]])))
}

# ---- 4. tests on every IPD ----
cat("4. Tests at each IPD\n")
cat(sprintf("%-11s%14s%6s%7s%11s%8s\n", "IPD", "Reserve", "PDL",
            ">3m %", "Cum loss %", "Pool %"))
cum <- 0
for (i in seq_len(nrow(res))) {
  y <- res[i, ]
  last <- substr(y$collection_periods,
                 nchar(y$collection_periods) - 6,
                 nchar(y$collection_periods))
  arr <- perf[last, "arrears_3_6m_pct"] +
    perf[last, "arrears_6m_plus_pct"]
  cum <- round2(cum + y$realised_losses)
  pdl <- sum(unlist(y[paste0("pdl_", c("a", "b", "c", "d",
                                       "e", "z"), "_after")]))
  cat(sprintf("%-11s%14s%6s%7.3f%11.4f%8.2f\n", y$ipd,
              mo(y$reserve_balance_after), mo(pdl), arr,
              round2(cum * 100 / cutoff_pool, 4),
              round2(y$pool_balance_end * 100 / cutoff_pool)))
}
