# Chapter 9 - eligibility criteria, pool cut and stratification
# tables for Thames Residential 2027-1. Base R only.
# Run from the book folder:
#   Rscript ch09/r/ch09_pool_selection.R \
#       data/ch09_thames_provisional_pool.csv
# Writes ch09/r/ch09_strats_r.csv (all strat tables).
args <- commandArgs(trailingOnly = TRUE)
pool <- read.csv(args[1], stringsAsFactors = FALSE)
pool$cents <- round(pool$current_balance * 100)
pool$oltv <- pool$original_balance / pool$original_valuation
pool$cltv <- pool$current_balance / pool$original_valuation

UK <- c("London", "South East", "East of England", "South West",
        "West Midlands", "East Midlands",
        "Yorkshire and the Humber", "North West", "North East",
        "Wales", "Scotland", "Northern Ireland")
PRODUCTS <- c("2Y Fixed", "5Y Fixed", "Tracker", "SVR")

criteria <- list(
  "E1 Property in the UK"   = function(d) d$region %in% UK,
  "E2 Owner-occupied"       = function(d)
    d$occupancy == "Owner-occupied",
  "E3 Not shared ownership" = function(d) d$shared_ownership == "N",
  "E4 Permitted product"    = function(d)
    d$product_type %in% PRODUCTS,
  "E5 Original LTV <= 95%"  = function(d) d$oltv <= 0.95,
  "E6 Balance 25k to 1m"    = function(d)
    d$current_balance >= 25000 & d$current_balance <= 1000000,
  "E7 Term <= 420 months"   = function(d)
    d$original_term_months <= 420,
  "E8 One payment made"     = function(d) d$payments_made >= 1,
  "E9 Arrears <= 1 month"   = function(d) d$months_in_arrears <= 1,
  "E10 No forbearance"      = function(d) d$forbearance_flag == "N",
  "E11 No further advance"  = function(d)
    d$further_advance_pending == "N")

money <- function(c) formatC(c / 100, format = "f", digits = 2,
                             big.mark = ",")
# percentage to 2 dp, halves rounded up as Excel's ROUND does
pct <- function(a, b) {
  x <- a * 100 / b
  sprintf("%.2f", floor(x * 100 + 0.5 + 1e-9) / 100)
}

# ---- 1. Failures (a loan can fail several criteria) and the
#         pool cut: criteria applied in order (removal waterfall)
tests <- sapply(criteria, function(f) f(pool))
pool$eligible <- apply(tests, 1, all)
cat(sprintf("Provisional pool: %s loans, GBP %s\n",
            format(nrow(pool), big.mark = ","), money(sum(pool$cents))))
cat(sprintf("  %-24s%5s%5s%15s%6s\n", "Criterion", "Fail", "Out",
            "Balance out", "Left"))
left <- pool
for (n in names(criteria)) {
  keep <- criteria[[n]](left)
  out <- left[!keep, ]
  left <- left[keep, ]
  cat(sprintf("  %-24s%5d%5d%15s%6d\n", n, sum(!tests[, n]),
              nrow(out), money(sum(out$cents)), nrow(left)))
}
fin <- pool[pool$eligible, ]
tot <- sum(fin$cents); n <- nrow(fin)
cat(sprintf("Final pool: %s loans, GBP %s\n",
            format(n, big.mark = ","), money(tot)))

# ---- 3. Stratification tables: bands are (lower, upper]
band <- function(x, edges, labels)
  as.character(cut(x, c(-Inf, edges), labels = labels))
LTV_E <- c(.5, .6, .7, .75, .8, .85, .9, .95)
LTV_L <- c("<=50%", "50-60%", "60-70%", "70-75%", "75-80%",
           "80-85%", "85-90%", "90-95%")
B <- list(
  bal_band = list(c(1e5, 2e5, 3e5, 4e5, 5e5, 7.5e5, 1e6),
    c("0-100k", "100k-200k", "200k-300k", "300k-400k",
      "400k-500k", "500k-750k", "750k-1,000k")),
  rate_band = list(c(3.5, 4.0, 4.5, 5.0, 5.5, 99),
    c("<=3.50%", "3.50-4.00%", "4.00-4.50%", "4.50-5.00%",
      "5.00-5.50%", ">5.50%")),
  season_band = list(c(12, 24, 36, 48, 60),
    c("0-12m", "12-24m", "24-36m", "36-48m", "48-60m")),
  rem_band = list(c(180, 240, 300, 360, 420),
    c("<=15y", "15-20y", "20-25y", "25-30y", "30-35y")))
fin$bal_band <- band(fin$current_balance, B$bal_band[[1]],
                     B$bal_band[[2]])
fin$oltv_band <- band(fin$oltv, LTV_E, LTV_L)
fin$cltv_band <- band(fin$cltv, LTV_E, LTV_L)
fin$rate_band <- band(fin$current_rate, B$rate_band[[1]],
                      B$rate_band[[2]])
fin$season_band <- band(fin$payments_made, B$season_band[[1]],
                        B$season_band[[2]])
fin$rem_band <- band(fin$remaining_term_months, B$rem_band[[1]],
                     B$rem_band[[2]])
fin$arrears <- as.character(fin$months_in_arrears)

strats <- list(
  c("Current balance", "bal_band"), c("Original LTV", "oltv_band"),
  c("Current LTV", "cltv_band"), c("Region", "region"),
  c("Product type", "product_type"), c("Interest rate", "rate_band"),
  c("Seasoning", "season_band"), c("Remaining term", "rem_band"),
  c("Repayment type", "repayment_type"),
  c("Employment", "employment_status"),
  c("First-time buyer", "first_time_buyer"),
  c("Months in arrears", "arrears"))
keys <- list(bal_band = B$bal_band[[2]], oltv_band = LTV_L,
  cltv_band = LTV_L, region = UK, product_type = PRODUCTS,
  rate_band = B$rate_band[[2]], season_band = B$season_band[[2]],
  rem_band = B$rem_band[[2]],
  repayment_type = c("Repayment", "Interest-only", "Part and part"),
  employment_status = c("Employed", "Self-employed", "Retired"),
  first_time_buyer = c("Y", "N"), arrears = c("0", "1"))
out <- NULL
for (s in strats) {
  col <- s[2]
  for (k in keys[[col]]) {
    sel <- fin[[col]] == k
    if (!any(sel)) next
    c <- sum(sel); b <- sum(fin$cents[sel])
    out <- rbind(out, data.frame(table = s[1], band = k, loans = c,
      pct_loans = pct(c, n), balance = sprintf("%.2f", b / 100),
      pct_balance = pct(b, tot)))
  }
}
write.csv(out, "ch09/r/ch09_strats_r.csv", row.names = FALSE)

# ---- 4. Weighted averages and concentration
wa <- function(x) sum(x * fin$cents) / tot
top10 <- sum(sort(fin$cents, decreasing = TRUE)[1:10])
lon <- sum(fin$cents[fin$region == "London"])
summ <- data.frame(measure = c("Average balance (GBP)",
  "Largest loan (GBP)", "WA original LTV (%)", "WA current LTV (%)",
  "WA interest rate (%)", "WA seasoning (months)",
  "WA remaining term (months)", "Top 10 loans (GBP)",
  "Top 10 loans (% pool)", "London (% pool)"),
  value = c(sprintf("%.2f", tot / n / 100),
  sprintf("%.2f", max(fin$cents) / 100),
  sprintf("%.2f", 100 * wa(fin$oltv)),
  sprintf("%.2f", 100 * wa(fin$cltv)),
  sprintf("%.2f", wa(fin$current_rate)),
  sprintf("%.2f", wa(fin$payments_made)),
  sprintf("%.2f", wa(fin$remaining_term_months)),
  sprintf("%.2f", top10 / 100), pct(top10, tot), pct(lon, tot)))
write.csv(summ, "ch09/r/ch09_summary_r.csv", row.names = FALSE)
cat(sprintf("WA current LTV %s%%, top 10 loans %s%%\n",
            summ$value[4], summ$value[9]))
cat(sprintf("Written: %d summary rows, %d strat rows\n",
            nrow(summ), nrow(out)))
