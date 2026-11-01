# Chapter 30 - Rhein Auto 2027-1: pool stratification, balloon
# concentration and base-case net loss from Rheinwagen static pools.
# Run from the book folder:
#   Rscript ch30/r/ch30_pool_analysis.R \
#     data/rhein_auto_2027_1_tape.csv \
#     data/rheinwagen_static_pool_losses.csv

invisible(Sys.setlocale("LC_CTYPE", "C.UTF-8"))
args <- commandArgs(trailingOnly = TRUE)
tape <- read.csv(args[1], encoding = "UTF-8")
stat <- read.csv(args[2])
POOL <- sum(tape$current_balance)

eur <- function(x) formatC(x, format = "f", digits = 2,
                           big.mark = ",")
num <- function(x) formatC(x, format = "d", big.mark = ",")
pad <- function(s, n) paste0(s, strrep(" ", max(0, n - nchar(s))))
lpad <- function(s, n) paste0(strrep(" ", max(0, n - nchar(s))), s)
f2 <- function(x) sprintf("%.2f", x)
wavg <- function(x, w) sum(x * w) / sum(w)
round2 <- function(x) sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100

# ---------- 1. Pool summary ----------
w <- tape$current_balance
tape$ltv <- 100 * tape$original_balance / tape$vehicle_price
cat("POOL AT CUT-OFF (28 Feb 2027)\n")
cat("Loans                     : ", num(nrow(tape)), "\n", sep = "")
cat("Current balance (EUR)     : ", eur(POOL), "\n", sep = "")
cat("Average balance (EUR)     : ", eur(POOL / nrow(tape)), "\n", sep = "")
cat("WA interest rate (%)      : ", f2(wavg(tape$interest_rate, w)), "\n", sep = "")
cat("WA remaining term (months): ",
    f2(wavg(tape$remaining_term_months, w)), "\n", sep = "")
cat("WA seasoning (months)     : ", f2(wavg(tape$payments_made, w)), "\n", sep = "")
cat("WA LTV at origination (%) : ", f2(wavg(tape$ltv, w)), "\n", sep = "")

# ---------- 2. Stratification tables ----------
tape$product <- ifelse(tape$balloon == "Y", "Balloon", "Classic")
tape$ltv_band <- as.character(cut(tape$ltv, c(0, 80, 90, 100),
  labels = c("<= 80%", "80-90%", "90-100%"), right = TRUE))

strat <- function(col) {
  keys <- if (col == "ltv_band") c("<= 80%", "80-90%", "90-100%") else
    sort(unique(tape[[col]]))
  cat("\nBy ", col, "\n", sep = "")
  for (k in keys) {
    sel <- tape[[col]] == k
    b <- sum(tape$current_balance[sel])
    cat("  ", pad(as.character(k), 10), " ", lpad(num(sum(sel)), 6),
        " ", lpad(eur(b), 16), " ", sprintf("%6.2f", 100 * b / POOL),
        "%\n", sep = "")
  }
}
for (c in c("product", "vehicle_condition", "fuel_type",
            "borrower_type", "original_term_months", "ltv_band"))
  strat(c)
st <- sort(tapply(tape$current_balance, tape$federal_state, sum),
           decreasing = TRUE)
cat("\nTop 3 federal states (% of pool)\n")
for (k in names(st)[1:3])
  cat("  ", pad(k, 22), " ", sprintf("%6.2f", 100 * st[[k]] / POOL),
      "%\n", sep = "")

# ---------- 3. Balloon concentration ----------
b <- tape[tape$balloon == "Y", ]
cat("\nBALLOON CONCENTRATION\n")
cat("Balloon loans             : ", num(nrow(b)), "\n", sep = "")
cat("Their current balance     : ", eur(sum(b$current_balance)), " (",
    f2(100 * sum(b$current_balance) / POOL), "% of pool)\n", sep = "")
cat("Balloon amounts           : ", eur(sum(b$balloon_amount)), " (",
    f2(100 * sum(b$balloon_amount) / POOL), "% of pool)\n", sep = "")
# due month = cut-off month (Feb 2027) + remaining term
m0 <- 2027 * 12 + 1                      # Feb 2027 as a month index
due <- m0 + b$remaining_term_months
b$due_year <- due %/% 12
b$due_month <- sprintf("%d-%02d", due %/% 12, due %% 12 + 1)
cat("Balloons falling due by calendar year\n")
by_y <- tapply(b$balloon_amount, b$due_year, sum)
for (y in names(by_y))
  cat("  ", y, "  ", lpad(eur(by_y[[y]]), 15), "  ",
      sprintf("%5.2f", 100 * by_y[[y]] / POOL), "%\n", sep = "")
pk <- tapply(b$balloon_amount, b$due_month, sum)
cat("Largest month: ", names(pk)[which.max(pk)], "  ",
    eur(max(pk)), "\n", sep = "")
cat("Balloon as % of vehicle price, by fuel type\n")
for (k in sort(unique(b$fuel_type))) {
  s <- b[b$fuel_type == k, ]
  cat("  ", pad(k, 9), " ",
      sprintf("%6.2f", 100 * sum(s$balloon_amount) / sum(s$vehicle_price)),
      "%\n", sep = "")
}

# ---------- 4. One balloon loan: RA-000002 ----------
balloon_pmt <- function(p, rate_pct, n, fv) {
  r <- rate_pct / 1200
  f <- (1 + r)^n
  round2((p * r * f - fv * r) / (f - 1))
}
ln <- tape[tape$loan_id == "RA-000002", ]
n <- ln$original_term_months
r <- ln$interest_rate / 1200
pmt <- balloon_pmt(ln$original_balance, ln$interest_rate, n,
                   ln$balloon_amount)
classic <- balloon_pmt(ln$original_balance, ln$interest_rate, n, 0)
bal <- ln$original_balance
sched <- numeric(n)
for (m in 1:n) {
  i <- round2(bal * r)
  bal <- round2(bal - (pmt - i))
  sched[m] <- bal
}
k <- ln$payments_made
cat("\nLOAN RA-000002 (balloon)\n")
cat("Instalment with balloon   : ", eur(pmt), "\n", sep = "")
cat("Instalment without balloon: ", eur(classic), "\n", sep = "")
cat("Balance after ", k, " payments : ", eur(sched[k]),
    "   tape: ", eur(ln$current_balance), "\n", sep = "")
cat("Final payment (month ", n, ")  : ", eur(pmt + sched[n]), "\n",
    sep = "")

# ---------- 5. Static pools: chain ladder ----------
stat$mx <- ave(stat$months_since_origination, stat$vintage, FUN = max)
AGE <- stat$months_since_origination
to_ultimate <- function(col) {
  wv <- stat$originated_balance * stat[[col]]
  cdf <- numeric(96); cdf[96] <- 1
  for (a in 95:1) {
    numr <- sum(wv[AGE == a + 1])
    den <- sum(wv[AGE == a & stat$mx >= a + 1])
    cdf[a] <- cdf[a + 1] * numr / den
  }
  last <- stat[AGE == stat$mx, ]
  last$life <- last[[col]] * cdf[last$mx]
  list(cdf = cdf, last = last)
}
nt <- to_ultimate("cumulative_net_loss_pct")
gr <- to_ultimate("cumulative_gross_loss_pct")
cat("\nSTATIC POOLS: factor to ultimate (net loss)\n")
for (a in c(12, 24, 36))
  cat("  at ", a, " months: ", sprintf("%.4f", nt$cdf[a]), "\n", sep = "")
wa <- function(d) sum(d$life * d$originated_balance) /
  sum(d$originated_balance)
net <- nt$last; gross <- gr$last
mature <- net$mx >= 12
cat("Vintages with >= 12 months: ", sum(mature), "\n", sep = "")
gl <- wa(gross[gross$mx >= 12, ]); nl <- wa(net[mature, ])
cat("Base-case lifetime gross loss : ", f2(gl), "%\n", sep = "")
cat("Base-case lifetime net loss   : ", f2(nl), "%\n", sep = "")
cat("Implied recovery rate         : ",
    sprintf("%.1f", 100 * (1 - nl / gl)), "%\n", sep = "")
cat("Projected lifetime net loss by year of origination\n")
net$year <- substr(net$vintage, 1, 4)
for (y in sort(unique(net$year[mature])))
  cat("  ", y, ": ", f2(wa(net[mature & net$year == y, ])), "%\n",
      sep = "")
