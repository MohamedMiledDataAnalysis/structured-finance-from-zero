# Chapter 26 - the real Thames Residential 2027-1 waterfall,
# 8 IPDs (15 Jun 2027 - 15 Mar 2029), per the Deal Fact Sheets.
# Run from the book folder:
#   Rscript ch26/r/ch26_waterfall.R \
#       data/thames_performance_monthly.csv
# Writes build/ch26_r_ipd_results.csv (or the 2nd argument)
# so it can be compared with data/thames_ipd_results.csv.

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-6) / 100
}
money <- function(x) {
  formatC(x, format = "f", digits = 2, big.mark = ",")
}

# ---------- deal terms (the Deal Fact Sheets) ----------
closing <- as.Date("2027-03-18")
cls <- c("A", "B", "C", "D", "E", "Z")
orig <- c(A = 553000000, B = 31800000, C = 19100000,
          D = 12700000, E = 9500000, Z = 9571146.31)
mrg <- c(A = 0.62, B = 1.10, C = 1.50, D = 2.20, E = 3.50)
swap_fixed <- 3.30
reserve_req <- 9391500
sub_margin <- 4.00
fee_pa <- c(trustee = 25000, paying_agent = 10000,
            corporate_services = 20000, cash_manager = 50000,
            other_expenses = 120000)
servicing_pct <- 0.15
issuer_profit <- 1000
ipds <- as.Date(c("2027-06-15", "2027-09-15", "2027-12-15",
                  "2028-03-15", "2028-06-15", "2028-09-15",
                  "2028-12-15", "2029-03-15"))
months <- list(c("2027-02", "2027-03", "2027-04", "2027-05"),
               c("2027-06", "2027-07", "2027-08"),
               c("2027-09", "2027-10", "2027-11"),
               c("2027-12", "2028-01", "2028-02"),
               c("2028-03", "2028-04", "2028-05"),
               c("2028-06", "2028-07", "2028-08"),
               c("2028-09", "2028-10", "2028-11"),
               c("2028-12", "2029-01", "2029-02"))
hols <- as.Date(c("2027-01-01", "2027-03-26", "2027-03-29",
  "2027-05-03", "2027-05-31", "2027-08-30", "2027-12-27",
  "2027-12-28", "2028-01-03", "2028-04-14", "2028-04-17",
  "2028-05-01", "2028-05-29", "2028-08-28", "2028-12-25",
  "2028-12-26", "2029-01-01", "2029-03-30", "2029-04-02"))
is_bd <- function(d) {
  !(format(d, "%u") %in% c("6", "7")) && !(d %in% hols)
}
mod_following <- function(d) {
  x <- d
  while (!is_bd(x)) x <- x + 1
  if (format(x, "%m") != format(d, "%m")) {
    x <- d
    while (!is_bd(x)) x <- x - 1
  }
  x
}
minus_bd <- function(d, n) {
  while (n > 0) { d <- d - 1; if (is_bd(d)) n <- n - 1 }
  d
}

args <- commandArgs(trailingOnly = TRUE)
folder <- dirname(args[1])
perf <- rbind(read.csv(args[1]),
  read.csv(file.path(folder,
                     "ch26_thames_performance_2029_02.csv")))
sonia <- read.csv(file.path(folder,
  "thames_sonia_assumption.csv"))$compounded_sonia_pct
notional <- read.csv(file.path(folder,
  "ch26_thames_swap_notional.csv"))$swap_notional

bal <- orig
pdl <- setNames(rep(0, 6), cls)
reserve <- reserve_req; sub_loan <- reserve_req
sub_unpaid <- 0              # unpaid sub-loan interest c/f
start <- closing; rows <- list()
for (k in 1:8) {
  ipd <- mod_following(ipds[k])
  days <- as.numeric(ipd - start)
  s <- sonia[k]; yf <- days / 365
  m <- perf[perf$collection_period %in% months[[k]], ]
  col <- function(f) round2(sum(m[[f]]))
  r <- list(ipd = format(ipd),
            determination_date = format(minus_bd(ipd, 5)),
            interest_period_start = format(start),
            days = days, compounded_sonia_pct = s,
            collection_periods = paste(months[[k]][1], "to",
              months[[k]][length(months[[k]])]))
  # --- revenue receipts ---
  r$interest_collected <- col("interest_collected")
  r$arrears_interest_recovered <-
    col("arrears_interest_recovered")
  r$revenue_collections <- round2(r$interest_collected +
    r$arrears_interest_recovered)
  n <- notional[k]
  fixed <- round2(n * swap_fixed / 100 * yf)
  flt <- round2(n * s / 100 * yf)
  r$swap_notional <- n; r$swap_fixed_leg <- fixed
  r$swap_floating_leg <- flt
  r$swap_net_received <- max(round2(flt - fixed), 0)
  r$reserve_brought_forward <- reserve
  avail <- round2(r$revenue_collections +
    r$swap_net_received + reserve)
  r$available_revenue <- avail
  # --- amounts due ---
  fee_q <- round2(fee_pa * days / 365)       # Actual/365
  serv <- round2(sum(round2(m$opening_balance *
    servicing_pct / 100 / 12)))
  swap_pay <- max(round2(fixed - flt), 0)
  nint <- round2(bal[1:5] * (s + mrg) / 100 * yf)
  # --- PDL debit: losses, Z sub-ledger first ---
  loss <- col("realised_losses")
  r$realised_losses <- loss
  left <- loss
  for (c in rev(cls)) {
    d <- min(left, round2(bal[c] - pdl[c]))
    pdl[c] <- round2(pdl[c] + d); left <- round2(left - d)
  }
  # --- revenue priority of payments ---
  pay <- function(due) {
    p <- min(avail, due)
    avail <<- round2(avail - p)
    p
  }
  r$r01_trustee <- pay(fee_q[["trustee"]])
  two <- c(paying_agent = fee_q[["paying_agent"]],
           corporate_services = fee_q[["corporate_services"]],
           cash_manager = fee_q[["cash_manager"]],
           servicer = serv,
           other_expenses = fee_q[["other_expenses"]])
  if (avail >= sum(two)) {
    p2 <- two
  } else {                                   # pro rata
    p2 <- round2(avail * two / sum(two))
  }
  avail <- round2(avail - sum(p2))
  for (x in names(two)) r[[paste0("r02_", x)]] <- p2[[x]]
  r$r03_issuer_profit <- pay(issuer_profit)
  r$r04_swap_net_payment <- pay(swap_pay)
  cure <- 0
  num <- c(A = 5, B = 7, C = 9, D = 11, E = 13)
  for (c in c("A", "B", "C", "D", "E")) {
    i <- num[[c]]
    r[[sprintf("r%02d_class_%s_interest", i, tolower(c))]] <-
      pay(nint[[c]])
    p <- pay(pdl[[c]])
    r[[sprintf("r%02d_class_%s_pdl", i + 1, tolower(c))]] <- p
    pdl[c] <- round2(pdl[c] - p); cure <- round2(cure + p)
  }
  reserve <- pay(reserve_req)
  r$r15_reserve_credit <- reserve
  p <- pay(pdl[["Z"]])
  r$r16_class_z_pdl <- p
  pdl["Z"] <- round2(pdl["Z"] - p); cure <- round2(cure + p)
  r$r17_sub_swap_termination <- 0
  sl_int <- round2(round2(sub_loan * (s + sub_margin) / 100 *
                          yf) + sub_unpaid)
  r$r18_sub_loan_interest <- pay(sl_int)
  r$r18_sub_loan_principal <- pay(sub_loan)
  sub_loan <- round2(sub_loan - r$r18_sub_loan_principal)
  sub_unpaid <- round2(sl_int - r$r18_sub_loan_interest)
  r$r19_deferred_consideration <- avail
  r$reserve_drawn <- round2(reserve_req - reserve)
  stopifnot(r$r05_class_a_interest == nint[["A"]],
            r$r19_deferred_consideration >= 0)
  # --- principal priority of payments ---
  r$scheduled_principal <- col("scheduled_principal")
  r$prepayments <- col("prepayments")
  r$principal_recoveries <- col("principal_recoveries")
  r$principal_collections <- round2(r$scheduled_principal +
    r$prepayments + r$principal_recoveries)
  r$pdl_cured_from_revenue <- cure
  r$principal_addition_amounts <- 0
  pa <- round2(r$principal_collections + cure)
  r$available_principal <- pa
  for (c in cls) {
    p <- min(pa, bal[[c]])
    r[[paste0("class_", tolower(c), "_principal")]] <- p
    bal[c] <- round2(bal[c] - p); pa <- round2(pa - p)
  }
  stopifnot(pa == 0)
  for (c in cls)
    r[[paste0("class_", tolower(c), "_balance_after")]] <-
      bal[[c]]
  r$notes_total_after <- round2(sum(bal))
  for (c in cls)
    r[[paste0("pdl_", tolower(c), "_after")]] <- pdl[[c]]
  r$reserve_balance_after <- reserve
  r$sub_loan_balance_after <- sub_loan
  r$pool_balance_end <- m$closing_balance[nrow(m)]
  r$sub_loan_interest_due <- sl_int
  r$sub_loan_interest_unpaid_after <- sub_unpaid
  rows[[k]] <- r
  start <- ipd
}
res <- do.call(rbind, lapply(rows, as.data.frame))
out <- if (length(args) > 1) args[2] else
  "build/ch26_r_ipd_results.csv"
dir.create(dirname(out), showWarnings = FALSE, recursive = TRUE)
csv <- res
txt <- c("ipd", "determination_date", "interest_period_start",
         "days", "compounded_sonia_pct", "collection_periods")
for (c in setdiff(names(csv), txt))
  csv[[c]] <- formatC(csv[[c]], format = "f", digits = 2)
write.csv(csv, out, row.names = FALSE, quote = FALSE)

f <- rows[[1]]
cat("First IPD ", f$ipd, " - days ", f$days, " - SONIA ",
    f$compounded_sonia_pct, "\n", sep = "")
for (k in c("revenue_collections", "swap_net_received",
            "reserve_brought_forward", "available_revenue",
            "r02_servicer", "r05_class_a_interest",
            "r07_class_b_interest", "r13_class_e_interest",
            "r15_reserve_credit", "r18_sub_loan_interest",
            "r18_sub_loan_principal",
            "r19_deferred_consideration",
            "available_principal", "class_a_balance_after"))
  cat(sprintf("  %-28s%17s\n", k, money(f[[k]])))
cat("IPD         Avail revenue   Class A paid",
    "    Class A after\n", sep = "")
for (x in rows)
  cat(sprintf("%s%16s%15s%17s\n", x$ipd,
              money(x$available_revenue),
              money(x$class_a_principal),
              money(x$class_a_balance_after)))
cat("Total realised losses debited to PDL: ",
    money(sum(res$realised_losses)), "\n", sep = "")
last <- rows[[8]]
cat("PDL outstanding after last IPD: ",
    money(sum(unlist(last[paste0("pdl_",
      tolower(cls), "_after")]))), "\n", sep = "")
cat("Wrote ", out, "\n", sep = "")
