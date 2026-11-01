# Chapter 18 - Loan-level analysis of the Thames pool (base R).
# The agency's criteria in this book (ILLUSTRATIVE): FF, LS and
# expected loss loan by loan at six rating levels.
# Run from the book folder:
#   Rscript ch18/r/ch18_loan_level.R \
#     data/thames_residential_2027_1_tape.csv \
#     data/ch18_regional_hpi.csv \
#     data/kingsbridge_static_pool_defaults.csv

args <- commandArgs(trailingOnly = TRUE)
levels <- c("AAA", "AA", "A", "BBB", "BB", "B")

# ---- the agency's criteria in this book (illustrative) ----
ff_lo  <- c(0, 50, 60, 70, 75, 80, 85, 90, 95)     # LTV band
ff_val <- c(1.0, 1.5, 2.1, 2.8, 3.6, 4.5, 5.6, 7.0, 9.0)
lti_lo <- c(0, 4.0, 4.5);  lti_val <- c(1.00, 1.10, 1.25)
sea_lo <- c(0, 24, 36, 48); sea_val <- c(1.00, 0.95, 0.90, 0.85)
self_emp <- 1.30
repay_adj <- c("Repayment" = 1.00, "Part and part" = 1.20,
               "Interest-only" = 1.40)
arrears_adj <- c(1.00, 2.00)                  # 0 and 1 month
mult <- c(AAA = 8.51, AA = 6.70, A = 5.33, BBB = 4.00,
          BB = 2.50, B = 1.00)
group <- c("London" = 1, "South East" = 2,
           "East of England" = 2, "South West" = 2, "East Midlands" = 3,
           "West Midlands" = 3, "Wales" = 3,
           "Yorkshire and the Humber" = 3, "North West" = 4,
           "North East" = 4, "Scotland" = 4,
           "Northern Ireland" = 5)
mvd_aaa <- c(0.60, 0.55, 0.50, 0.47, 0.57)    # by group 1..5
mvd_scale <- c(AAA = 1.00, AA = 0.92, A = 0.80, BBB = 0.72,
               BB = 0.57, B = 0.40)
fsd_flat <- 0.22; fsd_house <- 0.17
cost_fixed <- 3000; cost_pct <- 0.03
up_credit <- 0.80; index_q <- "2026Q4"

band <- function(x, lo, val) val[findInterval(x, lo)]

loan_level <- function(t, h) {
  key <- paste(h$region, h$quarter)
  od <- t$origination_date
  q0 <- paste0(substr(od, 1, 4), "Q",
               (as.integer(substr(od, 6, 7)) - 1) %/% 3 + 1)
  i0 <- h$hpi[match(paste(t$region, q0), key)]
  i1 <- h$hpi[match(paste(t$region, index_q), key)]
  ratio <- i1 / i0
  t$indexed_value <- t$original_valuation *
    ifelse(ratio > 1, 1 + up_credit * (ratio - 1), ratio)
  bal <- t$current_balance
  t$ltv_idx <- 100 * bal / t$indexed_value
  t$lti <- t$original_balance / t$gross_income
  t$base_ff <- band(t$ltv_idx, ff_lo, ff_val) / 100
  t$adj <- band(t$lti, lti_lo, lti_val) *
    band(t$payments_made, sea_lo, sea_val) *
    ifelse(t$employment_status == "Self-employed",
           self_emp, 1) *
    repay_adj[t$repayment_type] *
    arrears_adj[t$months_in_arrears + 1]
  fsd <- ifelse(t$property_type == "Flat", fsd_flat, fsd_house)
  sale_m <- ifelse(t$region == "Scotland", 24,
             ifelse(t$region == "Northern Ireland", 30, 18))
  accrued <- bal * t$current_rate / 100 * sale_m / 12
  for (k in levels) {
    ff <- t$base_ff * t$adj * mult[k]
    t[[paste0("ff_", k)]] <- pmin(1, ff)
    mvd <- mvd_aaa[group[t$region]] * mvd_scale[k]
    sale <- t$indexed_value * (1 - mvd) * (1 - fsd)
    loss <- pmax(0, bal + accrued + cost_fixed + cost_pct * sale
                 - sale)
    t[[paste0("ls_", k)]] <- loss / bal
  }
  t
}

t <- loan_level(read.csv(args[1], stringsAsFactors = FALSE),
                read.csv(args[2], stringsAsFactors = FALSE))
bal <- t$current_balance
wa <- function(x) sum(x * bal) / sum(bal)
gbp <- function(x) formatC(x, format = "f", digits = 2,
                           big.mark = ",")
cat(sprintf("Loans %d  pool %s\n", nrow(t), gbp(sum(bal))))
cat(sprintf("WA indexed LTV %.2f%%  WA base FF %.2f%%\n",
            wa(t$ltv_idx), 100 * wa(t$base_ff)))
cat(sprintf("WA adjustment factor %.4f\n", wa(t$adj)))
cat("Level  WAFF %  WALS %   EL %        EL (GBP)\n")
for (k in levels) {
  ff <- t[[paste0("ff_", k)]]; ls <- t[[paste0("ls_", k)]]
  el <- sum(bal * ff * ls)
  cat(sprintf("%-5s%7.2f%8.2f%7.2f%16s\n", k,
              100 * sum(bal * ff) / sum(bal),
              100 * el / sum(bal * ff), 100 * el / sum(bal),
              gbp(el)))
}
x <- t[t$loan_id == "KBS-000417", ]
cat(sprintf("KBS-000417 indexed value %s\n", gbp(x$indexed_value)))
cat(sprintf("  LTV %.2f%%  base FF %.2f%%  adj %.4f\n",
            x$ltv_idx, 100 * x$base_ff, x$adj))
cat(sprintf("  AAA: FF %.2f%%  LS %.2f%%\n", 100 * x$ff_AAA,
            100 * x$ls_AAA))
cat(sprintf("  B:   FF %.2f%%  LS %.2f%%\n", 100 * x$ff_B,
            100 * x$ls_B))
s <- read.csv(args[3], stringsAsFactors = FALSE)
s <- s[order(s$vintage, s$months_since_origination), ]
last <- s[!duplicated(s$vintage, fromLast = TRUE), ]
m <- last[last$months_since_origination >= 96, ]
d <- m$cumulative_default_pct; n <- m$cumulative_net_loss_pct
cat(sprintf("History, %d vintages of 96+ months:\n", nrow(m)))
cat(sprintf("  default mean %.2f%% max %.2f%%\n", mean(d), max(d)))
cat(sprintf("  net loss mean %.2f%%  severity %.2f%%\n", mean(n),
            100 * mean(n / d)))
