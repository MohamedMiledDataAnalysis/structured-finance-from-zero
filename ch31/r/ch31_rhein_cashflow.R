# Chapter 31 - Rhein Auto 2027-1 monthly cash-flow model:
# 12-month revolving period, then pro rata amortisation with
# sequential triggers, clean-up call at 10% of the initial pool.
# Run from the book folder:
#   Rscript ch31/r/ch31_rhein_cashflow.R \
#     data/ch31_rhein_scheduled_runoff.csv
# Same conventions as the Python script and the workbook.

round2 <- function(x) sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
args <- commandArgs(trailingOnly = TRUE)
ro <- read.csv(args[1])
prof <- (ro$regular_principal + ro$balloon_principal) / ro$opening

# ---------- deal inputs ----------
POOL0 <- 480929439.61
NOTES0 <- c(A = 432800000, B = 21600000, C = 14400000,
            Sub = 12129439.61)
MARGIN <- c(A = 0.0055, B = 0.0125, C = 0.0210)
SUB_RATE <- 0.06; SWAP_FIXED <- 0.024
FEES_PA <- 150000; SERVICING <- 0.005
RES0 <- 4809294.40; RES_FLOOR <- 2400000; RES_PCT <- 0.01
REVOLVING <- 12; EA_CNL <- 0.008; CALL <- 0.10
CLOSING <- as.Date("2027-03-25")
seq_threshold <- function(k) if (k <= 12) 0.008 else
  if (k <= 24) 0.014 else 0.020

# ---------- TARGET calendar, modified following ----------
easter <- function(y) {
  a <- y %% 19; b <- y %/% 100; c <- y %% 100
  d <- b %/% 4; e <- b %% 4; g <- (8 * b + 13) %/% 25
  h <- (19 * a + b - d - g + 15) %% 30
  i <- c %/% 4; k <- c %% 4
  l <- (32 + 2 * e + 2 * i - h - k) %% 7
  m <- (a + 11 * h + 22 * l) %/% 451
  n <- h + l - 7 * m + 114
  as.Date(sprintf("%d-%02d-%02d", y, n %/% 31, n %% 31 + 1))
}
closed <- function(d) {
  y <- as.integer(format(d, "%Y")); e <- easter(y)
  md <- format(d, "%m-%d")
  as.integer(format(d, "%u")) >= 6 ||
    md %in% c("01-01", "05-01", "12-25", "12-26") ||
    d == e - 2 || d == e + 1
}
mod_following <- function(d) {
  x <- d
  while (closed(x)) x <- x + 1
  if (format(x, "%m") != format(d, "%m")) {
    x <- d
    while (closed(x)) x <- x - 1
  }
  x
}
payment_date <- function(t) {
  mm <- 3 + t - 1
  mod_following(as.Date(sprintf("%d-%02d-25", 2027 + mm %/% 12,
                                mm %% 12 + 1)))
}

# ---------- the model ----------
run <- function(cdr, rr, cpr, euribor = 0.0225, war = 0.0477,
                lag = 6) {
  mdr <- 1 - (1 - cdr)^(1 / 12); smm <- 1 - (1 - cpr)^(1 / 12)
  idx <- max(euribor, 0)
  bal <- POOL0; res <- RES0; L <- NOTES0
  seq <- FALSE; ea <- FALSE; rev_done <- 0; prev <- CLOSING
  dflt <- c(); cum_d <- 0; cum_r <- 0; out <- list()
  for (t in 1:199) {
    pdt <- payment_date(t); days <- as.numeric(pdt - prev); prev <- pdt
    d <- round2(bal * mdr)
    r <- if (t > lag) round2(dflt[t - lag] * rr) else 0
    dflt <- c(dflt, d); cum_d <- cum_d + d; cum_r <- cum_r + r
    cnl <- (cum_d - cum_r) / POOL0
    ea <- ea || (t <= REVOLVING && cnl > EA_CNL)
    rev <- t <= REVOLVING && !ea
    rev_done <- rev_done + rev
    k <- if (rev) t else t - rev_done
    s <- if (k <= length(prof)) prof[k] else 1
    sched <- round2((bal - d) * s)
    prepay <- round2((bal - d - sched) * smm)
    inter <- round2((bal - d) * war / 12)
    pool_end <- round2(bal - d - sched - prepay)
    avail <- round2(inter + sched + prepay + r); avail0 <- avail
    notes <- sum(L[c("A", "B", "C")])
    fees <- round2(FEES_PA / 12 + bal * SERVICING / 12)
    swap <- round2(notes * (SWAP_FIXED - idx) * days / 360)
    ints <- sapply(names(MARGIN), function(c)
      round2(L[[c]] * (idx + MARGIN[[c]]) * days / 360))
    avail <- round2(avail + max(0, -swap))
    senior <- round2(fees + max(0, swap) + sum(ints))
    draw <- round2(min(res, max(0, senior - avail)))
    res <- round2(res - draw)
    avail <- round2(max(0, avail + draw - senior))
    call <- !rev && pool_end < CALL * POOL0
    req_pr <- min(RES0, max(RES_PCT * notes, RES_FLOOR))
    if (!rev && !call && !seq)
      seq <- cnl > seq_threshold(k) || res < req_pr - 0.005
    req <- if (call) 0 else if (rev || seq) RES0 else req_pr
    if (call) { avail <- round2(avail + res); res <- 0 }
    top <- round2(min(max(0, req - res), avail))
    res <- round2(res + top); avail <- round2(avail - top)
    release <- round2(max(0, res - req)); res <- round2(res - release)
    Ltot <- round2(sum(L))
    target <- if (call) Ltot else round2(max(0, Ltot - pool_end))
    pay <- c(A = 0, B = 0, C = 0, Sub = 0); buy <- 0
    if (rev) {
      buy <- round2(min(target, avail)); avail <- round2(avail - buy)
      bal <- round2(pool_end + buy)
    } else {
      if (call) avail <- round2(avail + pool_end)
      bal <- if (call) 0 else pool_end
      for (c in c("A", "B", "C", "Sub")) {
        want <- if (seq || call) min(L[[c]], target) else
          round2(target * L[[c]] / Ltot)
        pay[[c]] <- round2(min(want, avail))
        avail <- round2(avail - pay[[c]])
        if (seq || call) target <- round2(target - pay[[c]])
      }
      L <- round2(L - pay)
    }
    sub_int <- round2(min(avail, (L[["Sub"]] + pay[["Sub"]]) *
                             SUB_RATE * days / 360))
    avail <- round2(avail - sub_int)
    out[[t]] <- data.frame(t = t, date = pdt, days = days, rev = rev,
      seq = seq, call = call, k = k, recovery = r, sched = sched,
      prepay = prepay, interest = inter, pool_end = pool_end,
      cnl = cnl, buy = buy, pool = bal, residual = avail,
      intA = ints[["A"]], intB = ints[["B"]], intC = ints[["C"]],
      swap = swap, avail0 = avail0, fees = fees, top = top,
      sub_int = sub_int, payA = pay[["A"]], payB = pay[["B"]],
      payC = pay[["C"]], paySub = pay[["Sub"]], balA = L[["A"]],
      balB = L[["B"]], balC = L[["C"]], balSub = L[["Sub"]])
    if (call || sum(L) < 0.005) break
  }
  do.call(rbind, out)
}

eur <- function(x) formatC(x, format = "f", digits = 2, big.mark = ",")
eur0 <- function(x, w) formatC(round(x), format = "d", big.mark = ",",
                               width = w)
wal <- function(df, c) sum(df[[paste0("pay", c)]] *
  as.numeric(df$date - CLOSING) / 365) / NOTES0[[c]]

report <- function(name, df) {
  cat("\n", name, "\n", sep = "")
  f <- df[1, ]
  cat("First payment date      : ", format(f$date), " (", f$days,
      " days)\n", sep = "")
  cat("Class A interest, PD 1  : ", eur(f$intA), "\n", sep = "")
  cat("Swap net paid, PD 1     : ", eur(f$swap), "\n", sep = "")
  rv <- df[df$rev, ]
  cat("Revolving payment dates : ", nrow(rv), "\n", sep = "")
  cat("Receivables bought      : ", eur(sum(rv$buy)), "\n", sep = "")
  cat("CNL end of revolving    : ",
      sprintf("%.2f", 100 * rv$cnl[nrow(rv)]), "%\n", sep = "")
  sq <- df[df$seq, ]
  if (nrow(sq) > 0) {
    cat("Sequential trigger      : ", format(sq$date[1]),
        " (amort. month ", sq$k[1], ", CNL ",
        sprintf("%.2f", 100 * sq$cnl[1]), "%)\n", sep = "")
  } else cat("Sequential trigger      : not hit\n")
  l <- df[nrow(df), ]
  cat("Clean-up call           : ", format(l$date), " (pool ",
      eur(l$pool_end), ")\n", sep = "")
  cat("Owed after the call     : ",
      eur(l$balA + l$balB + l$balC + l$balSub), "\n", sep = "")
  cat("CNL at call             : ", sprintf("%.2f", 100 * l$cnl),
      "%\n", sep = "")
  cat("WAL from closing (years): ", paste(sapply(c("A", "B", "C",
      "Sub"), function(c) paste(c, sprintf("%.2f", wal(df, c)))),
      collapse = "  "), "\n", sep = "")
}
snapshot <- function(df, ts) {
  cat("  PD          Pool        Class A      Class B     Class C\n")
  for (t in ts) {
    r <- df[df$t == t, ]
    cat("  ", format(r$date), " ", eur0(r$pool, 14), " ",
        eur0(r$balA, 12), " ", eur0(r$balB, 11), " ",
        eur0(r$balC, 11), "\n", sep = "")
  }
}
waterfall <- function(df, t) {
  r <- df[df$t == t, ]
  lines <- list(c("Interest collections", r$interest),
    c("Scheduled principal", r$sched), c("Prepayments", r$prepay),
    c("Recoveries", r$recovery),
    c("Available distribution amount", r$avail0),
    c("1 Senior expenses and servicing", -r$fees),
    c("2 Swap net payment", -r$swap), c("3 Class A interest", -r$intA),
    c("4 Class B interest", -r$intB), c("5 Class C interest", -r$intC),
    c("6 Cash reserve top-up", -r$top),
    c("7 Purchase of new receivables", -r$buy),
    c("8 Subordinated loan interest", -r$sub_int),
    c("9 Residual to Rheinwagen Bank", -r$residual))
  cat("\nWATERFALL, payment date ", format(r$date), "\n", sep = "")
  for (x in lines) {
    v <- as.numeric(x[2]); if (v == 0) v <- 0
    lab <- x[1]
    cat("  ", lab, strrep(" ", 32 - nchar(lab)),
        formatC(v, format = "f", digits = 2, big.mark = ",",
                width = 16), "\n", sep = "")
  }
}

CPR <- 0.1266
base <- run(cdr = 0.0048, rr = 0.55, cpr = CPR)
stress <- run(cdr = 0.0096, rr = 0.50, cpr = CPR)
report("BASE CASE (CDR 0.48%, recovery 55%, CPR 12.66%)", base)
snapshot(base, c(12, 13, 16, 24, 36))
waterfall(base, 1)
report("STRESS (CDR 0.96%, recovery 50%, CPR 12.66%)", stress)
snapshot(stress, c(12, 13, 16, 24, 36))
