# Chapter 19 - Rating-level cash-flow stresses for Thames
# Residential 2027-1 plc (base R). Same model as the Python script.
# Run from the book folder:
#   Rscript ch19/r/ch19_stress_cashflow.R \
#     data/ch19_thames_schedules.csv \
#     data/ch18_rating_level_results.csv

args <- commandArgs(trailingOnly = TRUE)
POOL0 <- 635671146.31
CL <- c("A", "B", "C", "D", "E", "Z"); RATED <- CL[1:5]
SIZE <- c(A = 553000000, B = 31800000, C = 19100000,
          D = 12700000, E = 9500000, Z = 9571146.31)
MARGIN <- c(A = 0.62, B = 1.10, C = 1.50, D = 2.20, E = 3.50)
SUB <- sapply(1:5, function(i) 100 * sum(SIZE[-(1:i)]) / POOL0)
names(SUB) <- RATED                 # exact subordination, %
RF_PCT <- 100 * 9391500 / POOL0      # reserve fund, % of pool
CE <- SUB + RF_PCT                   # CE = subordination + reserve
SWAP_FIXED <- 3.30; RF_REQ <- 9391500; RF_FLOOR <- 3000000
FIXED_FEES <- 225000; PROFIT <- 1000; SONIA0 <- 3.75
STEP_UP_P <- 20; N_P <- 151
# ---- the agency's criteria in this book: cash-flow stresses ----
LEVELS <- c("AAA", "AA", "A", "BBB", "BB")
CPR_HIGH <- c(AAA = 25, AA = 22, A = 20, BBB = 18, BB = 16)
CPR_LOW <- 2
SONIA_UP <- c(AAA = 8.50, AA = 7.75, A = 7.00, BBB = 6.25,
              BB = 5.50)
SONIA_DOWN <- c(AAA = 0.25, AA = 0.50, A = 0.75, BBB = 1.00,
                BB = 1.50)
FLOAT_MARGIN <- c(AAA = 1.50, AA = 1.75, A = 2.00, BBB = 2.25,
                  BB = 2.50)
SERVICING <- 0.25; LAG <- 6
TIMING <- list(front = c(35, 30, 20, 10, 5),
               back = c(5, 10, 20, 30, 35))

ipd <- function(p) {
  m <- 6 + 3 * (p - 1)
  as.Date(sprintf("%d-%02d-15", 2027 + (m - 1) %/% 12,
                  (m - 1) %% 12 + 1))
}
DAYS <- as.numeric(diff(c(as.Date("2027-03-18"), ipd(1:N_P))))
sonia <- function(p, path, lvl) {
  tgt <- if (path == "up") SONIA_UP[[lvl]] else SONIA_DOWN[[lvl]]
  n <- if (path == "up") 12 else 8
  SONIA0 + (tgt - SONIA0) * min(p, n) / n
}
dshare <- function(p, timing)
  if (p <= 20) TIMING[[timing]][(p - 1) %/% 4 + 1] / 400 else 0

run <- function(sch, lvl, waff, wals, timing, cpr, path,
                size = SIZE) {
  S <- sch$sched_balance; F <- sch$sched_fixed_balance
  W <- sch$fixed_wac_pct          # S[p + 1] is period p's value
  bal <- size; pdl <- setNames(rep(0, 6), CL)
  dfr <- setNames(rep(0, 5), RATED)
  pool <- POOL0; rf <- RF_REQ; ended <- FALSE; enf <- FALSE
  D <- rep(0, N_P); a_short <- 0
  for (p in 1:N_P) {
    act <- if (ended) 0 else 1
    mon <- if (p == 1) 4 else 3
    dy <- DAYS[p]; so <- sonia(p, path, lvl)
    D[p] <- min(pool, waff * POOL0 * dshare(p, timing))
    perf <- pool - D[p]
    am <- if (S[p] == 0) 1 else 1 - S[p + 1] / S[p]
    sp <- perf * am
    pp <- (perf - sp) * (1 - (1 - cpr / 100)^(mon / 12))
    pool <- perf - sp - pp
    old <- if (p > LAG) D[p - LAG] else 0
    rec <- old * (1 - wals); loss <- old * wals
    pending <- sum(D[max(1, p - LAG + 1):p])
    is_end <- act == 1 && (p == N_P ||
                             (pool < 0.005 && pending < 0.005))
    fsh <- if (S[p] == 0) 0 else F[p] / S[p]
    yld <- fsh * W[p] + (1 - fsh) * (so + FLOAT_MARGIN[[lvl]])
    intr <- perf * yld / 100 * mon / 12
    swap <- F[p] * (so - SWAP_FIXED) / 100 * dy / 365
    fees <- act * ((FIXED_FEES + perf * SERVICING / 100) * mon / 12
                   + PROFIT)
    s_in <- max(swap, 0); s_out <- max(-swap, 0)
    up <- if (p >= STEP_UP_P) 2 else 1
    due <- act * ((bal[RATED] + dfr) * (so + up * MARGIN) / 100 *
                    dy / 365 + dfr)
    avail_p <- sp + pp + rec
    senior <- fees + s_out + due[["A"]]
    if (bal[["A"]] < 0.005) senior <- senior + due[["B"]]
    rev <- intr + s_in + rf
    pa <- if (enf) 0 else min(max(0, senior - rev), avail_p)
    if (enf) { rev <- rev + avail_p; avail_p <- 0 }
    rev <- rev + pa; avail_p <- avail_p - pa
    debit <- if (enf) 0 else loss + pa
    for (c in rev(CL)) {
      take <- min(debit, bal[[c]] - pdl[[c]])
      pdl[[c]] <- pdl[[c]] + take; debit <- debit - take
    }
    rem <- rev - min(rev, fees + s_out)
    cure <- 0; paid <- due * 0; prin_e <- setNames(rep(0, 6), CL)
    top <- RATED[bal[RATED] > 0.005][1]
    for (c in RATED) {
      paid[[c]] <- min(rem, due[[c]]); rem <- rem - paid[[c]]
      if (act == 1) dfr[[c]] <- due[[c]] - paid[[c]]
      cu <- min(rem, if (enf) bal[[c]] else pdl[[c]])
      rem <- rem - cu
      if (enf) prin_e[[c]] <- cu else {
        pdl[[c]] <- pdl[[c]] - cu; cure <- cure + cu }
    }
    open_ae <- sum(bal[RATED])
    tgt <- if (enf || is_end || open_ae < 0.005) 0 else
      if (bal[["A"]] > 0.005) RF_REQ else
        max(RF_FLOOR, 0.015 * open_ae)
    rf <- min(rem, tgt); rem <- rem - rf
    cu <- min(rem, if (enf) bal[["Z"]] else pdl[["Z"]])
    rem <- rem - cu
    if (enf) prin_e[["Z"]] <- cu else {
      pdl[["Z"]] <- pdl[["Z"]] - cu; cure <- cure + cu }
    prin <- avail_p + cure
    for (c in CL) {
      x <- if (enf) prin_e[[c]] else min(prin, bal[[c]])
      bal[[c]] <- bal[[c]] - x
      if (!enf) prin <- prin - x
    }
    a_short <- a_short + due[["A"]] - paid[["A"]]
    eod <- act == 1 && !is.na(top) && due[[top]] - paid[[top]] > 0.005
    if (is_end) ended <- TRUE
    if (eod) enf <- TRUE
  }
  list(short = bal[RATED] + dfr,
       u = sum(bal) / POOL0 * 100, a_short = a_short)
}

combos <- expand.grid(rates = c("up", "down"),
                      cprk = c("high", "low"),
                      timing = c("front", "back"),
                      stringsAsFactors = FALSE)[, 3:1]

resize <- function(x, s) {
  i <- match(x, CL); below <- CL[-(1:i)]
  size <- SIZE
  size[below] <- SIZE[below] * s / 100 * POOL0 / sum(SIZE[below])
  size[[x]] <- POOL0 - sum(size[CL != x])
  size
}

passes <- function(sch, lv, lvl, x, size, rows) {
  for (j in rows) {
    cb <- combos[j, ]
    cpr <- if (cb$cprk == "high") CPR_HIGH[[lvl]] else CPR_LOW
    r <- run(sch, lvl, lv[lvl, "waff_pct"] / 100,
             lv[lvl, "wals_pct"] / 100, cb$timing, cpr, cb$rates,
             size)
    if (r$short[[x]] > 0.005 || (x == "A" && r$a_short > 0.005))
      return(FALSE)
  }
  TRUE
}

needed <- function(sch, lv, lvl, x, rows = 1:8) {
  lo <- 0; hi <- 3000                  # hundredths of a per cent
  while (hi - lo > 1) {
    mid <- (lo + hi) %/% 2
    sub <- mid / 100 - RF_PCT
    ok <- sub >= 0 && passes(sch, lv, lvl, x, resize(x, sub),
                             rows)
    if (ok) hi <- mid else lo <- mid
  }
  hi / 100
}

sch <- read.csv(args[1])
lv <- read.csv(args[2], row.names = 1)
cat("CE needed (% of pool) by scenario\n")
cat("Scenario          ", sprintf("%7s", LEVELS), "\n", sep = "")
need <- matrix(0, 8, 5, dimnames = list(NULL, LEVELS))
for (j in 1:8) {
  for (k in 1:5)
    need[j, k] <- needed(sch, lv, LEVELS[k], RATED[k], j)
  cat(sprintf("%-6s%-5s%-7s", combos$timing[j], combos$cprk[j],
              combos$rates[j]), sprintf("%7.2f", need[j, ]),
      "\n", sep = "")
}
cat("\nLevel Class  needed  available  cushion  worst case\n")
for (k in 1:5) {
  n <- max(need[, k]); j <- which.max(need[, k])
  x <- RATED[k]
  cat(sprintf("%-5s %-5s %7.2f %10.2f %8.2f  %s %s %s\n",
              LEVELS[k], x, n, CE[[x]], CE[[x]] - n,
              combos$timing[j], combos$cprk[j], combos$rates[j]))
}
cat("\nPass/fail on the Thames structure (8 scenarios)\n")
cat("Class ", paste(sprintf("%4s", LEVELS), collapse = " "), "\n",
    sep = "")
for (x in RATED) {
  cells <- sapply(LEVELS, function(l)
    if (passes(sch, lv, l, x, SIZE, 1:8)) "pass" else "fail")
  cat(sprintf("%-5s ", x), paste(sprintf("%4s", cells),
                                  collapse = " "), "\n", sep = "")
}
