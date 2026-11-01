# Chapter 10 - Kingsbridge historical performance data. Base R.
# Run from the book folder:
#   Rscript ch10/r/ch10_history.R \
#       data/kingsbridge_static_pool_defaults.csv \
#       data/kingsbridge_dynamic_book.csv
args <- commandArgs(trailingOnly = TRUE)
s <- read.csv(args[1], stringsAsFactors = FALSE)
d <- read.csv(args[2], stringsAsFactors = FALSE)

grid <- function(col) {
  g <- tapply(s[[col]], list(s$months_since_origination, s$vintage),
              sum)
  g   # rows = age (3, 6, ...), columns = vintage; NA if not seen
}
cd <- grid("cumulative_default_pct")
nl <- grid("cumulative_net_loss_pct")
vol <- tapply(s$originated_balance, s$vintage, function(x) x[1])
last <- tapply(s$months_since_origination, s$vintage, max)
A <- function(a) as.character(a)   # row label of an age

# ---- 1. Timing curve from the fully seasoned vintages
MAT <- names(last)[last >= 120]
ages <- seq(3, 120, 3)
ratio <- sweep(cd[A(ages), MAT], 2, cd[A(120), MAT], "/")
T <- setNames(rowMeans(ratio), ages)
cat("Fully seasoned vintages: ", paste(MAT, collapse = ", "),
    "\n", sep = "")
cat("Timing curve (% of 120-month defaults):\n")
for (a in seq(12, 120, 12))
  cat(sprintf("  month %3d: %6.2f\n", a, 100 * T[A(a)]))

# ---- 2. Extrapolate every vintage to 120 months
age <- pmin(last, 120)
obs <- sapply(names(age), function(v) cd[A(age[v]), v])
life <- obs / T[A(age)]
names(life) <- names(age)
cat("Extrapolated lifetime default (%):\n")
cat("  vintage  age  observed  timing  lifetime\n")
for (v in c("2016Q1", "2019Q1", "2022Q1", "2023Q4", "2024Q4",
            "2025Q4"))
  cat(sprintf("  %s  %3d  %8.4f  %6.2f  %8.4f\n", v, age[v], obs[v],
              100 * T[A(age[v])], life[v]))

# ---- 3. Default-to-loss lag: compare the half-way points
half_age <- function(x) {
  x <- x[A(ages)]
  target <- x[A(120)] / 2
  i <- which(x >= target)[1]
  a0 <- ages[i - 1]; a1 <- ages[i]
  y0 <- x[i - 1]; y1 <- x[i]
  a0 + (target - y0) / (y1 - y0) * (a1 - a0)
}
lags <- sapply(MAT, function(v) half_age(nl[, v]) - half_age(cd[, v]))
lag <- round(mean(lags))
cat(sprintf("Default-to-loss lag: %.2f months -> %d months\n",
            mean(lags), lag))

# ---- 4. Loss severity: loss today / defaults lag months ago
sv <- names(last)[last >= 36]
sev <- sapply(sv, function(v)
  nl[A(last[v]), v] / cd[A(last[v] - lag), v])

# ---- 5. Base-case default and severity (balance-weighted)
uv <- names(last)[last >= 24]
base_def <- sum(life[uv] * vol[uv]) / sum(vol[uv])
base_sev <- sum(sev * vol[sv]) / sum(vol[sv])
cat(sprintf("Vintages used for default: %d; for severity: %d\n",
            length(uv), length(sv)))
cat(sprintf("Base-case lifetime default (%%): %.2f\n", base_def))
cat(sprintf("Base-case loss severity (%%):    %.2f\n", 100 * base_sev))

# ---- 6. CPR: average through SMM, and the reset months
cpr <- d$cpr_annualised_pct / 100
smm <- 1 - (1 - cpr)^(1 / 12)
base_cpr <- 1 - (1 - mean(smm))^12
spike <- as.integer(substr(d$month, 6, 7)) %in% c(3, 9)
cat(sprintf("CPR simple average (%%):         %.2f\n", 100 * mean(cpr)))
cat(sprintf("Base-case CPR via SMM (%%):      %.2f\n", 100 * base_cpr))
cat(sprintf("CPR in Mar and Sep (%%):         %.2f\n",
            100 * mean(cpr[spike])))
cat(sprintf("CPR in other months (%%):        %.2f\n",
            100 * mean(cpr[!spike])))

# ---- 7. Roll-rate proxies from arrears stocks, 3 months apart
lag3 <- function(x) c(rep(NA, 3), head(x, -3))
r1 <- d$arrears_3_6m_pct / lag3(d$arrears_1_3m_pct)
r2 <- d$arrears_6_12m_pct / lag3(d$arrears_3_6m_pct)
cat(sprintf("Roll 1-3m -> 3-6m (%%):          %.2f\n",
            100 * mean(r1, na.rm = TRUE)))
cat(sprintf("Roll 3-6m -> 6-12m (%%):         %.2f\n",
            100 * mean(r2, na.rm = TRUE)))
cat(sprintf("Base-case expected loss (%%):    %.4f\n",
            base_def * base_sev))
POOL <- 635671146.31   # Thames balance at cut-off
cat(sprintf("Thames base-case defaults (GBP): %s\n",
    formatC(POOL * base_def / 100, format = "f", digits = 0,
            big.mark = ",")))
cat(sprintf("Thames base-case loss (GBP):     %s\n",
    formatC(POOL * base_def * base_sev / 100, format = "f",
            digits = 0, big.mark = ",")))
