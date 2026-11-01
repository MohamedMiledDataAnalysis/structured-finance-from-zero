# Chapter 28 - Thames Residential 2027-1 Class A: cash flows,
# WAL, price and discount margin at different CPRs and spreads.
# Run from the book folder:
#   Rscript ch28/r/ch28_class_a_dm.R \
#       data/thames_performance_monthly.csv

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}

mod_following <- function(d) {
  a <- d
  while (as.POSIXlt(a)$wday %in% c(0, 6)) a <- a + 1
  if (format(a, "%m") != format(d, "%m")) {
    a <- d
    while (as.POSIXlt(a)$wday %in% c(0, 6)) a <- a - 1
  }
  a
}

SETTLE  <- as.Date("2027-03-18")    # closing date
CLASS_A <- 553000000
SONIA   <- 0.0375                   # flat, illustrative
MARGIN  <- 0.0062
SCHED   <- 0.0020                   # scheduled amortisation
# Chapter 10 base case: defaults, timing, lag
DEFAULTS <- 9273541
TIMING <- c(5.73, 11.07, 23.34, 28.88, 19.09,
            8.01, 2.70, 0.84, 0.26, 0.08)   # % by year
LAG <- 18                           # months to recovery
DEF <- round2(DEFAULTS * TIMING[(0:119) %/% 12 + 1] / 1200)

raw  <- seq(as.Date("2027-06-15"), as.Date("2032-03-15"),
            by = "3 months")
IPDS <- do.call(c, lapply(raw, mod_following))

pool_months <- function(pool0, cpr) {
  smm <- 1 - (1 - cpr)^(1 / 12)
  b <- pool0
  ym <- numeric(61); coll <- numeric(61)
  for (k in 0:60) {
    y <- 2027 + (1 + k) %/% 12; m <- (1 + k) %% 12 + 1
    d <- DEF[k + 1]
    sched <- round2((b - d) * SCHED)
    prep  <- round2((b - d - sched) * smm)
    back  <- if (k >= LAG) DEF[k + 1 - LAG] else 0
    ym[k + 1] <- y * 100 + m; coll[k + 1] <- sched + back + prep
    b <- round2(b - d - sched - prep)
  }
  data.frame(ym = ym, coll = coll)
}

class_a_flows <- function(pool0, cpr) {
  pm <- pool_months(pool0, cpr)
  n <- length(IPDS); bal <- CLASS_A; prev <- SETTLE
  out <- data.frame(ipd = IPDS, days = 0, opening = 0,
                    interest = 0, principal = 0)
  for (i in 1:n) {
    d <- IPDS[i]
    ymd <- function(x) as.numeric(format(x, "%Y")) * 100 +
      as.numeric(format(x, "%m"))
    lo <- if (i == 1) 202702 else ymd(IPDS[i - 1])
    coll <- sum(pm$coll[pm$ym >= lo & pm$ym < ymd(d)])
    days <- as.numeric(d - prev)
    intr <- round2(bal * (SONIA + MARGIN) * days / 365)
    princ <- if (i == n) bal else min(bal, round2(coll))
    out[i, 2:5] <- c(days, bal, intr, princ)
    bal <- round2(bal - princ); prev <- d
  }
  out
}

price <- function(cf, dm) {
  df <- cumprod(1 / (1 + (SONIA + dm) * cf$days / 365))
  100 * sum((cf$interest + cf$principal) * df) / CLASS_A
}

wal <- function(cf) {
  t <- as.numeric(cf$ipd - SETTLE) / 365
  sum(cf$principal * t) / CLASS_A
}

dm_from_price <- function(cf, target) {
  lo <- -0.02; hi <- 0.05             # bisection on DM
  for (k in 1:100) {
    mid <- (lo + hi) / 2
    if (price(cf, mid) > target) lo <- mid else hi <- mid
  }
  mid
}

f2 <- function(x, w = 0) formatC(x, format = "f", digits = 2,
                                 big.mark = ",", width = w)
args <- commandArgs(trailingOnly = TRUE)
perf <- read.csv(args[1])
pool0 <- perf$opening_balance[1]
cat("Pool at cut-off      : ", f2(pool0), "\n", sep = "")
cat("Scheduled amortisation: ", sprintf("%.4f%%",
    100 * perf$scheduled_principal[1] / pool0),
    " of balance (Feb 2027 actual)\n", sep = "")
base <- class_a_flows(pool0, 0.1115)
cat("\nClass A at 11.15% CPR, first two IPDs (GBP)\n")
for (i in 1:2) {
  r <- base[i, ]
  cat(format(r$ipd), "  ", sprintf("%3d", r$days), "d  open ",
      f2(r$opening, 15), "  int ", f2(r$interest, 12),
      "\n", strrep(" ", 12), "principal ",
      f2(r$principal, 14), "\n", sep = "")
}
n <- nrow(base)
cat(format(base$ipd[n]), "  call: principal ",
    f2(base$principal[n]), "\n", sep = "")
cat("\nCPR     WAL   price at DM 0.55% 0.62% 0.70% 0.80%\n")
for (cpr in c(0.05, 0.1115, 0.15, 0.20)) {
  cf <- class_a_flows(pool0, cpr)
  p <- sapply(c(0.0055, 0.0062, 0.0070, 0.0080),
              function(dm) price(cf, dm))
  cat(sprintf("%5.2f%%", 100 * cpr), "  ",
      sprintf("%5.2f", wal(cf)), "  ",
      paste(sprintf("%7.3f", p), collapse = "  "), "\n",
      sep = "")
}
dm <- dm_from_price(base, 99.80)
cat(sprintf("\nDM at price 99.80, 11.15%% CPR: %.4f%%\n",
            dm * 100))
cat(sprintf("Price change for +1bp DM : %.4f\n",
            price(base, 0.0063) - 100))
if (length(args) > 1) {               # optional CPR in %
  c <- as.numeric(args[2]) / 100
  cf <- class_a_flows(pool0, c)
  p <- sapply(c(0.0055, 0.0062, 0.0070, 0.0080),
              function(dm) price(cf, dm))
  cat(sprintf("\nCPR %.1f%%: WAL %.2f  prices ", 100 * c,
              wal(cf)), paste(sprintf("%7.3f", p),
              collapse = "  "), "\n", sep = "")
}
