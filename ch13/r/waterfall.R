# Thames Residential 2027-1 waterfall engine (Chapter 13). Base R.
# Reusable by later chapters (Chapter 26 runs the real IPDs).
# Same conventions as ch13/python/waterfall.py; results agree to
# the penny. Every amount is rounded with round2() (Excel ROUND).
#
# Interface
#   source("ch13/r/waterfall.R")
#   state  <- make_state(pool, notes, pdl, deferred, reserve,
#                        subloan, subloan_unpaid_int)
#   period <- make_period(days, sonia, revenue, sched_principal,
#                         prepayments, recoveries, losses,
#                         swap_notional, other_revenue = 0,
#                         sub_swap_termination = 0)
#   res <- run_ipd(state, period)        # pre-enforcement
#   res$lines     data.frame(item, label, due, paid)
#   res$principal data.frame(label, paid)
#   res$state     state after the IPD (input to the next IPD)
#   res$info      list: available_revenue, swap_receipt,
#                 swap_payment, principal_receipts, paa,
#                 pdl_debits, pdl_credits, reserve_required,
#                 reserve_draw, interest_shortfall, eod_interest,
#                 balance_check (notes - PDL - pool), ...
#   run_post_enforcement(state, period)  # combined waterfall
#
# Conventions (Chapter 13): opening balances; Actual/365 accrual
# rounded to the penny; issuer profit GBP 1,000 per IPD; swap net
# = notional x (fixed - SONIA) x days/365 (>0 paid at item 4,
# <0 received as revenue); available revenue receipts include the
# whole reserve; principal addition amounts (PAA) cover items 1-4
# and Class A interest (Class B while most senior) and are debited
# to the PDL; PDL debits Z, E, D, C, B, A capped at each class
# balance; unpaid B-E interest (not most senior) is deferred and
# bears interest at the class coupon; unpaid most-senior interest
# sets eod_interest = TRUE; reserve required GBP 9,391,500 while
# Class A is outstanding, else max(1.5% of A-E, GBP 3,000,000);
# item 18 pays sub loan interest then principal; principal is
# strictly sequential A, B, C, D, E, Z.

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}

CLASSES <- c("A", "B", "C", "D", "E", "Z")

THAMES_TERMS <- list(
  margins = c(A = 0.62, B = 1.10, C = 1.50, D = 2.20, E = 3.50),
  swap_fixed = 3.30,
  trustee_fee = 25000,
  senior_fees = c("Paying agent, agent bank" = 10000,
                  "Corporate services" = 20000,
                  "Cash manager" = 50000,
                  "Servicer" = NA,            # 0.15% of pool
                  "Other issuer expenses" = 120000),
  servicing_pct = 0.15,
  issuer_profit = 1000,
  reserve_required = 9391500,
  reserve_pct = 1.50,
  reserve_floor = 3000000,
  subloan_margin = 4.00)

zeros <- function() setNames(rep(0, 6), CLASSES)

make_state <- function(pool, notes, pdl = zeros(),
                       deferred = zeros(), reserve = 0,
                       subloan = 0, subloan_unpaid_int = 0) {
  list(pool = pool, notes = notes[CLASSES], pdl = pdl[CLASSES],
       deferred = deferred[CLASSES], reserve = reserve,
       subloan = subloan, subloan_unpaid_int = subloan_unpaid_int)
}

make_period <- function(days, sonia, revenue, sched_principal,
                        prepayments, recoveries, losses,
                        swap_notional, other_revenue = 0,
                        sub_swap_termination = 0) {
  list(days = days, sonia = sonia, revenue = revenue,
       sched_principal = sched_principal,
       prepayments = prepayments, recoveries = recoveries,
       losses = losses, swap_notional = swap_notional,
       other_revenue = other_revenue,
       sub_swap_termination = sub_swap_termination)
}

# Actual/365 accrual, rounded to the penny
accrue <- function(balance, rate_pct, days) {
  round2(balance * rate_pct / 100 * days / 365)
}

most_senior <- function(notes) {
  out <- CLASSES[notes > 0]
  if (length(out) == 0) NA else out[1]
}

# Debit an amount to sub-ledgers Z, E, D, C, B, A, each capped
# at its class balance
debit_pdl <- function(pdl, notes, amount) {
  debits <- zeros(); left <- amount
  for (cl in rev(CLASSES)) {
    room <- max(0, round2(notes[[cl]] - pdl[[cl]]))
    d <- min(room, left)
    debits[cl] <- d; pdl[cl] <- round2(pdl[[cl]] + d)
    left <- round2(left - d)
  }
  list(pdl = pdl, debits = debits, unallocated = left)
}

# Interest due: current + deferred + interest on deferred
interest_due <- function(state, period, terms = THAMES_TERMS) {
  due <- zeros()
  for (cl in CLASSES[1:5]) {
    cpn <- period$sonia + terms$margins[[cl]]
    due[cl] <- round2(accrue(state$notes[[cl]], cpn, period$days) +
      state$deferred[[cl]] +
      accrue(state$deferred[[cl]], cpn, period$days))
  }
  due
}

# Items (1) and (2)
fees_due <- function(state, period, terms = THAMES_TERMS) {
  trustee <- accrue(terms$trustee_fee, 100, period$days)
  g <- terms$senior_fees
  grp <- sapply(names(g), function(n) {
    if (is.na(g[[n]])) accrue(state$pool, terms$servicing_pct,
                              period$days)
    else accrue(g[[n]], 100, period$days)
  })
  list(trustee = trustee, group = grp)
}

required_reserve <- function(state, terms = THAMES_TERMS) {
  if (state$notes[["A"]] > 0) return(terms$reserve_required)
  max(round2(sum(state$notes[1:5]) * terms$reserve_pct / 100),
      terms$reserve_floor)
}

run_ipd <- function(state, period, terms = THAMES_TERMS) {
  s <- state; info <- list()
  swap_net <- accrue(period$swap_notional,
                     terms$swap_fixed - period$sonia, period$days)
  swap_pay <- max(swap_net, 0); swap_rec <- max(-swap_net, 0)
  prin_rec <- round2(period$sched_principal + period$prepayments +
                     period$recoveries)
  arr <- round2(period$revenue + swap_rec + period$other_revenue +
                s$reserve)
  info$swap_receipt <- swap_rec; info$swap_payment <- swap_pay
  info$principal_receipts <- prin_rec
  info$available_revenue <- arr
  f <- fees_due(s, period, terms)
  idue <- interest_due(s, period, terms)
  senior <- most_senior(s$notes)
  paa_class <- if (!is.na(senior) && senior %in% c("A", "B"))
    senior else NA
  need <- round2(f$trustee + sum(f$group) + terms$issuer_profit +
    swap_pay + (if (is.na(paa_class)) 0 else idue[[paa_class]]))
  paa <- min(max(round2(need - arr), 0), prin_rec)
  info$paa <- paa
  db <- debit_pdl(s$pdl, s$notes, round2(period$losses + paa))
  pdl <- db$pdl
  info$pdl_debits <- db$debits; info$pdl_unallocated <- db$unallocated
  pot <- round2(arr + paa)
  lines <- data.frame(item = character(), label = character(),
                      due = numeric(), paid = numeric())
  pay <- function(item, label, due) {
    paid <- min(due, max(pot, 0))
    pot <<- round2(pot - paid)
    lines[nrow(lines) + 1, ] <<- list(item, label, due, paid)
    paid
  }
  pay("1", "Trustee fees", f$trustee)
  gdue <- round2(sum(f$group)); gpaid <- min(gdue, pot)
  for (n in names(f$group)) {
    amt <- f$group[[n]]
    p <- if (gpaid == gdue) amt else round2(amt * gpaid / gdue)
    pot <- round2(pot - p)
    lines[nrow(lines) + 1, ] <- list("2", n, amt, p)
  }
  pay("3", "Issuer profit", terms$issuer_profit)
  pay("4", "Swap net payment", swap_pay)
  paid_int <- zeros(); credits <- zeros(); item <- 5
  for (cl in CLASSES[1:5]) {
    paid_int[cl] <- pay(as.character(item),
                        paste("Class", cl, "interest"), idue[[cl]])
    credits[cl] <- pay(as.character(item + 1),
                       paste("Class", cl, "PDL"), pdl[[cl]])
    item <- item + 2
  }
  req <- required_reserve(s, terms)
  new_reserve <- pay("15", "General reserve fund", req)
  credits["Z"] <- pay("16", "Class Z PDL", pdl[["Z"]])
  pay("17", "Sub swap termination", period$sub_swap_termination)
  sub_int <- round2(accrue(s$subloan, period$sonia +
    terms$subloan_margin, period$days) + s$subloan_unpaid_int)
  sub_int_paid <- pay("18", "Sub loan interest", sub_int)
  sub_prin <- pay("18", "Sub loan principal", s$subloan)
  lines[nrow(lines) + 1, ] <- list("19", "Deferred consideration",
                                   pot, pot)
  pot <- 0
  pdl <- round2(pdl - credits)
  deferred <- zeros(); info$eod_interest <- FALSE
  for (cl in CLASSES[1:5]) {
    short <- round2(idue[[cl]] - paid_int[[cl]])
    if (short > 0 && !is.na(senior) && cl == senior)
      info$eod_interest <- TRUE
    deferred[cl] <- short
  }
  info$interest_shortfall <- deferred
  apr <- round2(prin_rec - paa + sum(credits))
  info$available_principal <- apr; info$pdl_credits <- credits
  notes <- s$notes
  plines <- data.frame(label = "Principal addition amounts",
                       paid = paa)
  for (cl in CLASSES) {
    p <- min(apr, notes[[cl]])
    notes[cl] <- round2(notes[[cl]] - p); apr <- round2(apr - p)
    plines[nrow(plines) + 1, ] <- list(paste("Class", cl,
                                             "principal"), p)
  }
  info$principal_left <- apr
  pool_close <- round2(s$pool - prin_rec - period$losses)
  new <- make_state(pool_close, notes, pdl, deferred, new_reserve,
                    round2(s$subloan - sub_prin),
                    round2(sub_int - sub_int_paid))
  info$reserve_required <- req
  info$reserve_draw <- round2(s$reserve - new_reserve)
  info$balance_check <- round2(sum(notes) - sum(pdl) - pool_close)
  list(lines = lines, principal = plines, state = new, info = info)
}

run_post_enforcement <- function(state, period,
                                 terms = THAMES_TERMS) {
  s <- state
  swap_net <- accrue(period$swap_notional,
                     terms$swap_fixed - period$sonia, period$days)
  pot <- round2(period$revenue + period$other_revenue +
    period$sched_principal + period$prepayments +
    period$recoveries + max(-swap_net, 0) + s$reserve)
  start <- pot
  lines <- data.frame(label = character(), due = numeric(),
                      paid = numeric())
  pay <- function(label, due) {
    paid <- min(due, max(pot, 0)); pot <<- round2(pot - paid)
    lines[nrow(lines) + 1, ] <<- list(label, due, paid)
  }
  f <- fees_due(s, period, terms)
  pay("Trustee fees", f$trustee)
  gdue <- round2(sum(f$group)); gpaid <- min(gdue, pot)
  for (n in names(f$group)) {
    amt <- f$group[[n]]
    p <- if (gpaid == gdue) amt else round2(amt * gpaid / gdue)
    pot <- round2(pot - p)
    lines[nrow(lines) + 1, ] <- list(n, amt, p)
  }
  pay("Swap net payment", max(swap_net, 0))
  idue <- interest_due(s, period, terms)
  for (cl in CLASSES[1:5]) {
    pay(paste("Class", cl, "interest"), idue[[cl]])
    pay(paste("Class", cl, "principal"), s$notes[[cl]])
  }
  pay("Class Z principal", s$notes[["Z"]])
  pay("Sub swap termination", period$sub_swap_termination)
  pay("Sub loan interest", round2(accrue(s$subloan, period$sonia +
    terms$subloan_margin, period$days) + s$subloan_unpaid_int))
  pay("Sub loan principal", s$subloan)
  lines[nrow(lines) + 1, ] <- list("Deferred consideration", pot,
                                   pot)
  list(lines = lines, pot_start = start)
}
