# Final exam - Medway Residential 2028-1 plc: solutions to Parts B and C (base R)
# Run from the book folder:
#   Rscript exam/r/exam_solutions.R data/exam_medway_tape.csv \
#       data/exam_medway_deal_terms.csv data/exam_medway_ipd_inputs.csv

# R's round() can send a half to the even digit; Excel sends it away from zero.
round2 <- function(x) sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
m  <- function(x) formatC(round2(x) + 0, format = "f", digits = 2, big.mark = ",")
f2 <- function(x) formatC(round2(x) + 0, format = "f", digits = 2)
pad <- function(s, w) formatC(s, width = w)            # right-aligned
lab <- function(s, w) formatC(s, width = -w)           # left-aligned
cnt <- function(n) formatC(n, format = "d", big.mark = ",")

args <- commandArgs(trailingOnly = TRUE)
tape  <- read.csv(args[1], colClasses = "character")
terms <- read.csv(args[2], colClasses = "character")
T <- setNames(as.numeric(terms$value), terms$parameter)
inp <- read.csv(args[3], colClasses = "character")
I <- lapply(c("ipd1", "ipd2"), function(k) setNames(inp[[k]], inp$item))

add_months <- function(d, n) {
  y <- as.integer(format(d, "%Y")); mo <- as.integer(format(d, "%m")) - 1 + n
  as.Date(sprintf("%04d-%02d-%s", y + mo %/% 12, mo %% 12 + 1, format(d, "%d")))
}
ARR_B <- c("Current", "1 month", "2 months", "3-5 months", "6+ months", "Unknown")
LTV_B <- c("0-50%", "50-60%", "60-70%", "70-75%", "75-80%", "80-85%", "85-90%", "Over 90%")
REP_B <- c("Repayment", "Interest-only", "Part and part")
REG_B <- c("London", "South East", "East of England", "South West", "West Midlands", "East Midlands",
           "North West", "Yorkshire and the Humber", "North East", "Wales", "Scotland",
           "Northern Ireland", "Unknown")
arrears_bucket <- function(a) ifelse(a < 0, "Unknown", ifelse(a == 0, "Current",
  ifelse(a == 1, "1 month", ifelse(a == 2, "2 months", ifelse(a <= 5, "3-5 months", "6+ months")))))
ltv_bucket <- function(v) {
  lims <- c(50, 60, 70, 75, 80, 85, 90)
  sapply(v, function(x) { k <- which(x <= lims)[1]; if (is.na(k)) "Over 90%" else LTV_B[k] })
}
ALL <- c("dup", "bal", "mat", "ltv", "region", "rate", "arrears")

# Build the reporting view; the raw columns are never overwritten
prepare <- function(t, treat = ALL) {
  if ("dup" %in% treat) t <- t[!duplicated(t$loan_id), ]
  bal <- as.numeric(t$current_balance)
  if ("bal" %in% treat) bal <- ifelse(bal > as.numeric(t$original_balance), round2(bal / 10), bal)
  orig <- as.Date(t$origination_date); mat <- as.Date(t$maturity_date)
  if ("mat" %in% treat) {
    bad <- which(mat < orig)
    for (k in bad) mat[k] <- add_months(orig[k], as.integer(t$original_term_months[k]))
  }
  rep <- as.Date(t$report_date)
  rem <- (as.integer(format(mat, "%Y")) - as.integer(format(rep, "%Y"))) * 12 +
         as.integer(format(mat, "%m")) - as.integer(format(rep, "%m"))
  ltv <- if ("ltv" %in% treat) round2(bal / as.numeric(t$indexed_valuation) * 100) else as.numeric(t$indexed_ltv)
  reg <- t$region
  if ("region" %in% treat) { reg[reg == ""] <- "Unknown"; reg[reg == "Yorkshire & Humber"] <- "Yorkshire and the Humber" }
  rate <- as.numeric(t$current_rate)
  rate_ok <- if ("rate" %in% treat) rate > 0 else rep(TRUE, length(rate))
  a <- as.integer(t$months_in_arrears)
  arr <- if ("arrears" %in% treat) arrears_bucket(a) else arrears_bucket(pmax(a, 0))
  data.frame(bal, rem, ltv, reg, rate, rate_ok, arr, rept = t$repayment_type, stringsAsFactors = FALSE)
}
wa <- function(b, x) sum(b * x) / sum(b)
headline <- function(L) list(count = nrow(L), total = sum(L$bal), average = round2(sum(L$bal) / nrow(L)),
  wa_rate = round2(wa(L$bal[L$rate_ok], L$rate[L$rate_ok])), wa_ltv = round2(wa(L$bal, L$ltv)),
  wa_rem = round2(wa(L$bal, L$rem)))

out <- character(0); P <- function(s) out <<- c(out, s)
L <- prepare(tape); h <- headline(L); R <- prepare(tape, character(0)); hr <- headline(R)
hl <- function(s, v) P(paste0(lab(s, 32), pad(v, 18)))
P("MEDWAY RESIDENTIAL 2028-1 - FINAL EXAM SOLUTIONS")
P("PART B - REPORTING POOL AT 28 FEBRUARY 2029")
hl("Rows on the tape", cnt(nrow(tape)))
hl("Loans in the reporting pool", cnt(h$count))
hl("Total current balance (GBP)", m(h$total))
hl("Average balance (GBP)", m(h$average))
hl("WA current rate (%)", f2(h$wa_rate))
hl("WA indexed LTV (%)", f2(h$wa_ltv))
hl("WA remaining term (months)", f2(h$wa_rem))
P("AS DELIVERED (no treatment)")
hl("Rows counted as loans", cnt(hr$count))
hl("Total current balance (GBP)", m(hr$total))
hl("Average balance (GBP)", m(hr$average))
hl("WA current rate (%)", f2(hr$wa_rate))
hl("WA indexed LTV, tape field (%)", f2(hr$wa_ltv))
hl("WA remaining term (months)", f2(hr$wa_rem))

strat <- function(name, key, buckets) {
  P(paste0("STRAT BY ", name))
  P(paste0(lab("Bucket", 25), pad("Loans", 6), pad("Balance", 17), pad("% bal", 8), pad("WA LTV", 8)))
  for (b in buckets) {
    g <- key == b; bal <- sum(L$bal[g])
    w <- if (any(g)) wa(L$bal[g], L$ltv[g]) else 0
    P(paste0(lab(b, 25), pad(sum(g), 6), pad(m(bal), 17), pad(f2(bal / h$total * 100), 8), pad(f2(w), 8)))
  }
  inb <- key %in% buckets; sb <- sum(L$bal[inb]); sn <- sum(inb)
  P(paste0(lab("Total", 25), pad(sn, 6), pad(m(sb), 17), pad(f2(sb / h$total * 100), 8), pad(f2(h$wa_ltv), 8)))
  P(paste0(lab("Check: strat - pool", 25), pad(sn - h$count, 6), pad(m(sb - h$total), 17)))
}
strat("ARREARS", L$arr, ARR_B)
strat("INDEXED LTV", ltv_bucket(L$ltv), LTV_B)
strat("REPAYMENT TYPE", L$rept, REP_B)
strat("REGION", L$reg, REG_B)

# ------------------------------------------------------------- waterfall
run_ipd <- function(st, x) {
  d <- as.numeric(x["days"]); s <- T["sonia"]
  ra <- (s + T["margin_a"]) / 100; rb <- (s + T["margin_b"]) / 100
  loss <- as.numeric(x["realised_losses"]); deb <- c(a = 0, b = 0, z = 0)
  for (c in c("z", "b", "a")) {                       # PDL debits: Z, then B, then A
    room <- round2(st[[paste0("class_", c)]] - st[[paste0("pdl_", c)]])
    deb[c] <- min(loss, room); st[[paste0("pdl_", c)]] <- round2(st[[paste0("pdl_", c)]] + deb[c])
    loss <- round2(loss - deb[c])
  }
  arr <- round2(as.numeric(x["revenue_collections"]) + st$reserve)
  labs <- c("(1) Senior fees and expenses", "(2) Servicing fee", "(3) Class A interest",
            "(4) Class A PDL", "(5) Class B interest", "(6) Class B PDL",
            "(7) Reserve to required amount", "(8) Class Z PDL", "(9) Residual to Kingsbridge")
  due <- c(round2(T["senior_fees_pa"] * d / 365) + as.numeric(x["extra_senior_expenses"]),
           round2(st$pool * T["servicing_pct"] / 100 * d / 365),
           round2(st$class_a * ra * d / 365), st$pdl_a,
           round2(st$class_b * rb * d / 365) + st$deferred_b + round2(st$deferred_b * rb * d / 365),
           st$pdl_b, T["reserve_required"], st$pdl_z)
  due <- round2(due); paid <- numeric(9); pot <- arr
  for (j in 1:8) { paid[j] <- min(due[j], pot); pot <- round2(pot - paid[j]) }
  due[9] <- pot; paid[9] <- pot
  cure <- c(a = paid[4], b = paid[6], z = paid[8])
  deferred <- round2(due[5] - paid[5]); res_open <- st$reserve; res_close <- paid[7]
  for (c in names(cure)) st[[paste0("pdl_", c)]] <- round2(st[[paste0("pdl_", c)]] - cure[c])
  prin <- round2(as.numeric(x["scheduled_principal"]) + as.numeric(x["prepayments"]) + as.numeric(x["recoveries"]))
  apr <- round2(prin + sum(cure)); left <- apr; ppaid <- c(a = 0, b = 0, z = 0)
  notes_open <- st$class_a + st$class_b + st$class_z
  for (c in c("a", "b", "z")) {
    ppaid[c] <- min(left, st[[paste0("class_", c)]])
    st[[paste0("class_", c)]] <- round2(st[[paste0("class_", c)]] - ppaid[c]); left <- round2(left - ppaid[c])
  }
  pool_open <- st$pool
  st$pool <- round2(pool_open - prin - as.numeric(x["realised_losses"]))
  st$reserve <- res_close; st$deferred_b <- deferred
  notes <- st$class_a + st$class_b + st$class_z; pdl <- st$pdl_a + st$pdl_b + st$pdl_z
  pdl_open <- pdl + sum(cure) - sum(deb)
  checks <- c(arr - sum(paid), apr - sum(ppaid), pdl_open + sum(deb) - sum(cure) - pdl,
              notes_open - sum(ppaid) - notes, notes - pdl - st$pool)
  list(labs = labs, due = due, paid = paid, checks = round2(checks), st = st,
       info = list(arr = arr, apr = apr, prin = prin, deb = deb, cure = cure, deferred = deferred,
                   res_open = res_open, res_close = res_close, draw = max(res_open - res_close, 0),
                   topup = max(res_close - res_open, 0), ppaid = ppaid, pool_open = pool_open,
                   notes = notes, pdl = pdl))
}
o <- I[[1]]; n <- function(k) as.numeric(o[paste0("open_", k)])
st <- list(pool = n("opening_pool"), reserve = n("reserve"), deferred_b = n("deferred_b"),
           class_a = n("class_a"), class_b = n("class_b"), class_z = n("class_z"),
           pdl_a = n("pdl_a"), pdl_b = n("pdl_b"), pdl_z = n("pdl_z"))
r1 <- run_ipd(st, I[[1]]); r2r <- run_ipd(r1$st, I[[2]]); RR <- list(r1, r2r)
row <- function(s, a, b) P(paste0(lab(s, 32), pad(m(a), 16), pad(m(b), 16)))
inf <- function(k) c(RR[[1]]$info[[k]], RR[[2]]$info[[k]])
P("PART C - WATERFALL (ILLUSTRATIVE)")
P(paste0(lab("", 32), pad("IPD 1", 16), pad("IPD 2", 16)))
row("Opening pool", r1$info$pool_open, r2r$info$pool_open)
row("Realised losses to PDL", sum(r1$info$deb), sum(r2r$info$deb))
row("Available revenue receipts", r1$info$arr, r2r$info$arr)
P("REVENUE: AMOUNT DUE")
for (j in 1:8) row(r1$labs[j], r1$due[j], r2r$due[j])
P("REVENUE: AMOUNT PAID")
for (j in 1:9) row(r1$labs[j], r1$paid[j], r2r$paid[j])
row("Class B interest deferred", r1$info$deferred, r2r$info$deferred)
P("PRINCIPAL")
row("Principal receipts", r1$info$prin, r2r$info$prin)
row("plus PDL cures", sum(r1$info$cure), sum(r2r$info$cure))
row("Available principal receipts", r1$info$apr, r2r$info$apr)
for (c in c("a", "b", "z")) row(paste0("Class ", toupper(c), " principal paid"), r1$info$ppaid[c], r2r$info$ppaid[c])
P("RESERVE AND PDL")
row("Reserve opening", r1$info$res_open, r2r$info$res_open)
row("Reserve drawn", r1$info$draw, r2r$info$draw)
row("Reserve topped up", r1$info$topup, r2r$info$topup)
row("Reserve closing", r1$info$res_close, r2r$info$res_close)
for (c in c("a", "b", "z")) {
  C <- toupper(c)
  row(paste0("PDL ", C, " debit"), r1$info$deb[c], r2r$info$deb[c])
  row(paste0("PDL ", C, " cure"), r1$info$cure[c], r2r$info$cure[c])
  row(paste0("PDL ", C, " closing"), r1$st[[paste0("pdl_", c)]], r2r$st[[paste0("pdl_", c)]])
}
P("CLOSING BALANCES")
for (c in c("a", "b", "z")) row(paste0("Class ", toupper(c), " note"), r1$st[[paste0("class_", c)]], r2r$st[[paste0("class_", c)]])
row("Notes outstanding", r1$info$notes, r2r$info$notes)
row("PDL balance", r1$info$pdl, r2r$info$pdl)
row("Closing pool", r1$st$pool, r2r$st$pool)
row("Class B deferred interest", r1$st$deferred_b, r2r$st$deferred_b)
ce <- function(r, cls) round2(sum(unlist(r$st[paste0("class_", cls)])) - r$info$pdl) / r$st$pool * 100
P(paste0(lab("Class A CE: (B+Z-PDL)/pool (%)", 32), pad(f2(ce(r1, c("b", "z"))), 16), pad(f2(ce(r2r, c("b", "z"))), 16)))
P(paste0(lab("Class B CE: (Z-PDL)/pool (%)", 32), pad(f2(ce(r1, "z")), 16), pad(f2(ce(r2r, "z")), 16)))
P("ZERO-CHECKS")
cl <- c("Revenue: available - allocated", "Principal: available - allocated",
        "PDL: open + debits - cures - close", "Notes: open - principal - close", "Notes - PDL - pool")
for (j in 1:5) row(cl[j], r1$checks[j], r2r$checks[j])
P(paste0(lab("Tape pool - IPD 1 closing pool", 32), pad(m(h$total - r1$st$pool), 16)))
cat(out, sep = "\n")
