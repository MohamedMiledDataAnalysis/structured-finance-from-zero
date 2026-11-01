# Chapter 16 - call economics for Thames Residential 2027-1
# (base R). Run from the book folder:
#   Rscript ch16/r/ch16_call_economics.R \
#       data/thames_residential_2027_1_tape.csv \
#       data/ch14_base_case.csv
invisible(Sys.setlocale("LC_TIME", "C"))
args <- commandArgs(trailingOnly = TRUE)
here <- dirname(sub("--file=", "", grep("--file=",
                commandArgs(FALSE), value = TRUE)))
source(file.path(here, "..", "..", "ch14", "r", "cashflow.R"))

SONIA <- 3.75
MARGIN <- c(A = 0.62, B = 1.10, C = 1.50, D = 2.20, E = 3.50)
STEP <- 2 * MARGIN                       # margins double
money <- function(x) formatC(x, format = "f", digits = 2,
                             big.mark = ",")
pad <- function(s, w) formatC(s, width = w)
p <- function(...) cat(..., "\n", sep = "")

balances <- function(notes) {            # opening balance per IPD
  out <- notes[, c("ipd", "date")]
  for (c in names(CLASSES))
    out[[c]] <- CLASSES[[c]] - cumsum(notes[[c]]) + notes[[c]]
  out
}

xirr <- function(dates, flows) {
  f <- function(y) sum(flows / (1 + y)^(as.numeric(dates -
                                         dates[1]) / 365))
  lo <- -0.5; hi <- 1.0
  for (i in 1:200) {                     # bisection
    mid <- (lo + hi) / 2
    if (f(lo) * f(mid) <= 0) hi <- mid else lo <- mid
  }
  (lo + hi) / 2
}

class_a_flows <- function(notes, price, call) {
  bal <- balances(notes)
  dates <- CLOSING; flows <- -553000000.00 * price / 100
  prev <- CLOSING
  for (i in seq_len(nrow(notes))) {
    if (bal$A[i] <= 0.005) break
    m <- if (call || notes$ipd[i] < CALL_IPD) MARGIN[["A"]] else
      STEP[["A"]]
    days <- as.numeric(notes$date[i] - prev)
    int <- bal$A[i] * (SONIA + m) / 100 * days / 365
    dates <- c(dates, notes$date[i]); flows <- c(flows, int + notes$A[i])
    prev <- notes$date[i]
  }
  list(dates = dates, flows = flows)
}

t <- load_tape(args[1])
S <- sched_balance(t)
b <- load_base(args[2], S[1])
pool <- project_pool(S, b$cpr, sev = b$sev, lag = b$lag, dvec = b$dvec)
nc <- project_notes(pool); wc <- project_notes(pool, TRUE)
bal <- balances(nc)
k <- CALL_IPD
p("Thames Residential 2027-1 - Chapter 16 call economics")
p("Base case (Chapter 10), SONIA flat 3.75%")
p("\nOn 15 Mar 2032 (IPD ", CALL_IPD, "), before payments")
p("Class   Outstanding    Margin  Step-up  Extra a year")
after <- sapply(names(CLASSES), function(c) bal[[c]][k] - nc[[c]][k])
extra <- 0
for (c in names(CLASSES)) {
  if (c %in% names(MARGIN)) {
    x <- after[[c]] * (STEP[[c]] - MARGIN[[c]]) / 100
    extra <- extra + x
    p("  ", c, "  ", pad(money(bal[[c]][k]), 16), "  ",
      sprintf("%.2f%%  %.2f%%", MARGIN[[c]], STEP[[c]]), "  ",
      pad(money(x), 12))
  } else p("  ", c, "  ", pad(money(bal[[c]][k]), 16), "  none")
}
p("  Total ", pad(money(sum(sapply(names(CLASSES),
  function(c) bal[[c]][k]))), 14))
p("Principal collected for that IPD: ", money(nc$available[k]))
p("If not called, outstanding after the IPD: ", money(sum(after)))
p("Step-up cost in the first year: ", money(extra))
prev <- ipd_date(CALL_IPD); tot <- 0
for (i in (k + 1):nrow(nc)) {
  d <- nc$date[i]; days <- as.numeric(d - prev); prev <- d
  for (c in names(MARGIN))
    tot <- tot + bal[[c]][i] * (STEP[[c]] - MARGIN[[c]]) / 100 *
      days / 365
}
p("Extra interest if never called: ", money(tot))

p("\nClass A yield (annual, Actual/365), SONIA flat 3.75%")
p("Price     With call   No call   Difference")
for (price in c(100.00, 99.75)) {
  a <- class_a_flows(wc, price, TRUE)
  z <- class_a_flows(nc, price, FALSE)
  yc <- 100 * xirr(a$dates, a$flows); yn <- 100 * xirr(z$dates, z$flows)
  p(sprintf("%6.2f   %8.3f%%  %7.3f%%  %8.3f%%", price, yc, yn, yn - yc))
}
p("\nClean-up call threshold (10% of cut-off): ", money(0.1 * S[1]))
