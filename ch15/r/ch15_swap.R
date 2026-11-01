# Chapter 15 - the Thames fixed-to-floating swap (base R).
# Run from the book folder:
#   Rscript ch15/r/ch15_swap.R \
#       data/thames_residential_2027_1_tape.csv \
#       data/thames_sonia_assumption.csv \
#       data/ch15_sonia_daily_sample.csv \
#       data/ch14_base_case.csv
invisible(Sys.setlocale("LC_TIME", "C"))
args <- commandArgs(trailingOnly = TRUE)
here <- dirname(sub("--file=", "", grep("--file=",
                commandArgs(FALSE), value = TRUE)))
source(file.path(here, "..", "..", "ch14", "r", "cashflow.R"))

FIXED <- 3.30
NOTES_AE <- 626100000.00
round2 <- function(x) sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
money <- function(x) formatC(round2(x), format = "f", digits = 2,
                             big.mark = ",")
pad <- function(s, w) formatC(s, width = w)
leg <- function(notional, rate_pct, days)
  round2(notional * rate_pct / 100 * days / 365)
compounded <- function(rates, weights, d)
  (prod(1 + rates / 100 * weights / 365) - 1) * 365 / d * 100
p <- function(...) cat(..., "\n", sep = "")

t <- load_tape(args[1])
fx <- t[grepl("Fixed", t$product_type), ]
wa <- sum(fx$current_balance * fx$current_rate) / sum(fx$current_balance)
tr <- t[t$product_type == "Tracker", ]
sv <- t[t$product_type == "SVR", ]
p("Thames Residential 2027-1 - Chapter 15 swap")
p("Fixed-rate loans: ", formatC(nrow(fx), big.mark = ","),
  "  balance ", money(sum(fx$current_balance)))
p(sprintf("  weighted average fixed rate %.4f%%", wa))
p("Trackers: ", nrow(tr), "  ", money(sum(tr$current_balance)),
  "  SVR: ", nrow(sv), "  ", money(sum(sv$current_balance)))

N0 <- fixed_sched_balance(t)          # N0[m + 1] = month m
d1 <- as.numeric(ipd_date(1) - CLOSING)
fl <- leg(N0[1], FIXED, d1); fi <- leg(N0[1], 3.75, d1)
p("\nFirst period 18 Mar 2027 - 15 Jun 2027 (", d1, " days)")
p("  notional               ", pad(money(N0[1]), 16))
p("  fixed leg, 3.30%       ", pad(money(fl), 16), "  issuer pays")
p("  floating leg, 3.75%    ", pad(money(fi), 16), "  issuer gets")
p("  net to issuer          ", pad(money(fi - fl), 16))

s <- read.csv(args[3], stringsAsFactors = FALSE)
p("\nCompounded SONIA, illustrative daily rates")
d_obs <- sum(s$days)
comp <- compounded(s$sonia_pct, s$days, d_obs)
simple <- sum(s$sonia_pct * s$days) / d_obs
p("Days in observation period: ", d_obs)
p(sprintf("Compounded rate: %.5f%%   weighted average: %.5f%%",
          comp, simple))
ia <- leg(553000000.00, round(comp, 5) + 0.62, 14)
p("Class A interest, 1-15 Jun 2027 (14 days): ", money(ia))

S <- sched_balance(t)
b <- load_base(args[4], S[1])
pool <- project_pool(S, b$cpr, sev = b$sev, lag = b$lag, dvec = b$dvec)
q <- read.csv(args[2])
p("\nSwap on the first eight IPDs (SONIA assumption file)")
p("IPD       Days  SONIA        Notional     Net to issuer")
rows <- data.frame(); prev <- CLOSING
for (k in 1:8) {
  m <- if (k == 1) 0 else 3 * k - 2
  dt <- ipd_date(k); days <- as.numeric(dt - prev); prev <- dt
  son <- q$compounded_sonia_pct[k]
  net <- leg(N0[m + 1], son, days) - leg(N0[m + 1], FIXED, days)
  act <- N0[m + 1] * pool$balance[m + 1] / S[m + 1]
  rows <- rbind(rows, data.frame(k = k, dt = dt, days = days,
                n = N0[m + 1], son = son, net = net, act = act))
  p(format(dt, "%b %Y"), "  ", sprintf("%4d", days), "   ",
    sprintf("%.2f", son), "  ", pad(money(N0[m + 1]), 14), "  ",
    pad(money(net), 16))
}
p("Total net to issuer, 8 IPDs: ", money(sum(rows$net)))
p("\nActual fixed balance and excess notional (base case)")
p("IPD         Actual fixed  Excess notional")
for (i in 1:8) p(format(rows$dt[i], "%b %Y"), "  ",
  pad(money(rows$act[i]), 14), "  ", pad(money(rows$n[i] - rows$act[i]), 15))
l <- rows[8, ]
cost <- leg(l$n - l$act, FIXED - 2.30, l$days)
p("SONIA 2.30% on ", format(l$dt, "%d %b %Y"),
  ": excess notional costs ", money(cost))

unhedged <- NOTES_AE - N0[1]
p("\nBasis risk (annual, illustrative)")
p("Notes on SONIA not matched by the swap: ", money(unhedged))
p("  SONIA +0.25%, Bank Rate unchanged: cost ",
  money(unhedged * 0.0025))
p("  SVR cut by 0.50%: lost income ",
  money(sum(sv$current_balance) * 0.005))

p("\nSwap value to the issuer at closing if the market rate moves")
prev <- CLOSING; sched <- NULL
for (k in 1:39) {
  m <- if (k == 1) 0 else 3 * k - 2
  if (N0[m + 1] <= 0) break
  dt <- ipd_date(k)
  sched <- rbind(sched, c(as.numeric(dt - prev),
                          as.numeric(dt - CLOSING), N0[m + 1]))
  prev <- dt
}
p("Periods with a notional: ", nrow(sched), " (last IPD ",
  format(ipd_date(nrow(sched)), "%b %Y"), ")")
for (mkt in c(4.30, 2.30)) {
  v <- sum(sched[, 3] * (mkt - FIXED) / 100 * sched[, 1] / 365 /
           (1 + mkt / 100)^(sched[, 2] / 365))
  who <- if (v > 0) "Northgate owes issuer" else "issuer owes Northgate"
  p(sprintf("  market %.2f%%: ", mkt), pad(money(v), 15), "  ", who)
}
