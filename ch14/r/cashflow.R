# Chapter 14 - reusable cash-flow engine for Thames Residential
# 2027-1 (base R). Same conventions as ch14/python/cashflow.py:
# month 1 = Feb 2027; closed-form annuity balances at the
# current rate; part and part = half the original balance
# interest-only;
# defaults, then scheduled principal, then prepayments; losses
# cured by excess spread through the PDL; IPD 1 pays months 1-4,
# IPD k > 1 pays months 3k-1 to 3k+1; WAL from 18 Mar 2027,
# Actual/365.
# Use from other chapters: source("ch14/r/cashflow.R")

CLOSING <- as.Date("2027-03-18")
CLASSES <- c(A = 553000000.00, B = 31800000.00, C = 19100000.00,
             D = 12700000.00, E = 9500000.00, Z = 9571146.31)
CALL_IPD <- 20
H <- 433

load_tape <- function(path) {
  t <- read.csv(path, stringsAsFactors = FALSE)
  t$io_part <- ifelse(t$repayment_type == "Interest-only",
                      t$current_balance, 0)
  pp <- t$repayment_type == "Part and part"
  t$io_part[pp] <- t$original_balance[pp] / 2
  t$rep_part <- t$current_balance - t$io_part
  t$r <- t$current_rate / 1200
  t$n <- t$remaining_term_months
  end <- as.POSIXlt(as.Date(ifelse(t$fixed_rate_end_date == "",
                    NA, t$fixed_rate_end_date)))
  t$fix_end_m <- (end$year + 1900 - 2027) * 12 + end$mon
  t
}

sched_balance <- function(t, months = H, keep = NULL) {
  k <- 0:months
  g <- (1 + t$r)^t$n
  out <- numeric(length(k))
  for (j in seq_along(k)) {
    alive <- k[j] < t$n
    if (!is.null(keep)) alive <- alive & keep(k[j])
    rep <- t$rep_part * (g - (1 + t$r)^k[j]) / (g - 1)
    out[j] <- sum((rep + t$io_part)[alive])
  }
  out
}

fixed_sched_balance <- function(t, months = H) {
  isfix <- grepl("Fixed", t$product_type)
  m_end <- ifelse(is.na(t$fix_end_m), 0, t$fix_end_m)
  sched_balance(t, months, keep = function(k) isfix & k < m_end)
}

smm <- function(annual_pct) 1 - (1 - annual_pct / 100)^(1 / 12)

load_base <- function(path, S0, months = H) {
  b <- read.csv(path, stringsAsFactors = FALSE)
  v <- setNames(b$value, b$parameter)
  life <- v[["lifetime_default_pct"]] / 100 * S0
  dvec <- numeric(months + 1)          # dvec[m + 1] = month m
  for (y in 1:10) {
    share <- v[[paste0("timing_year_", y)]] / 100
    dvec[(12 * y - 10):(12 * y + 1)] <- life * share / 12
  }
  list(cpr = v[["cpr_pct"]], sev = v[["severity_pct"]],
       lag = v[["lag_months"]], dvec = dvec)
}

project_pool <- function(S, cpr, cdr = 0, sev = 0, lag = 0,
                         dvec = NULL) {
  mp <- smm(cpr); md <- smm(cdr); n <- length(S) - 1
  B <- numeric(n + 1); B[1] <- S[1]
  D <- Sch <- P <- numeric(n + 1)
  for (m in 2:(n + 1)) {             # R index m = month m - 1
    D[m] <- if (is.null(dvec)) md * B[m - 1] else
      min(dvec[m], B[m - 1])
    f <- if (S[m - 1] > 0) 1 - S[m] / S[m - 1] else 1
    Sch[m] <- (B[m - 1] - D[m]) * f
    P[m] <- mp * (B[m - 1] - D[m] - Sch[m])
    B[m] <- B[m - 1] - D[m] - Sch[m] - P[m]
  }
  Dlag <- c(rep(0, lag), D)[1:(n + 1)]
  rec <- (1 - sev / 100) * Dlag; loss <- sev / 100 * Dlag
  data.frame(month = 0:n, balance = B, defaults = D,
             scheduled = Sch, prepaid = P, recoveries = rec,
             losses = loss, to_notes = Sch + P + rec + loss)
}

ipd_date <- function(k) {
  m <- 6 + 3 * (k - 1)
  as.Date(sprintf("%d-%02d-15", 2027 + (m - 1) %/% 12,
                  (m - 1) %% 12 + 1))
}

ipd_of_month <- function(m) ifelse(m <= 4, 1, (m - 2) %/% 3 + 1)

project_notes <- function(pool, call = FALSE) {
  pool <- pool[pool$month >= 1, ]
  avail <- tapply(pool$to_notes, ipd_of_month(pool$month), sum)
  bal <- CLASSES
  ks <- as.integer(names(avail))
  out <- data.frame(ipd = ks, available = as.numeric(avail))
  out$date <- ipd_date(ks)
  pay <- matrix(0, length(ks), 6, dimnames = list(NULL,
                names(CLASSES)))
  for (i in seq_along(ks)) {
    cash <- avail[[i]]
    for (c in names(CLASSES)) {
      p <- min(bal[[c]], cash)
      if (call && ks[i] == CALL_IPD) p <- bal[[c]]
      bal[[c]] <- bal[[c]] - p; cash <- max(cash - p, 0)
      pay[i, c] <- p
    }
    if (call && ks[i] == CALL_IPD) break
  }
  out <- cbind(out, pay)
  if (call) out <- out[out$ipd <= CALL_IPD, ]
  out
}

wal_and_maturity <- function(notes) {
  tt <- as.numeric(notes$date - CLOSING) / 365
  lapply(setNames(names(CLASSES), names(CLASSES)), function(c) {
    paid <- notes[[c]]
    list(wal = sum(paid * tt) / sum(paid),
         maturity = max(notes$date[paid > 0.005]))
  })
}

rep_lines <- function(t, keys) {
  grp <- interaction(t[keys], drop = TRUE)
  w <- t$current_balance
  data.frame(
    current_balance = as.numeric(tapply(w, grp, sum)),
    rep_part = as.numeric(tapply(t$rep_part, grp, sum)),
    io_part = as.numeric(tapply(t$io_part, grp, sum)),
    r = as.numeric(tapply(t$r * w, grp, sum) /
                   tapply(w, grp, sum)),
    n = round(as.numeric(tapply(t$n * w, grp, sum) /
                         tapply(w, grp, sum))))
}
