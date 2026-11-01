# Chapter 8 - validate a Thames loan tape: completeness,
# validity, consistency, reasonableness and recalculation,
# with an exception report and control totals.
# Run from the book folder:
#   Rscript ch08/r/ch08_validate.R \
#       data/ch08_thames_tape_raw.csv

args <- commandArgs(trailingOnly = TRUE)
t <- read.csv(args[1], colClasses = "character",
              na.strings = character(0))
LEDGER_N <- 3000; LEDGER_BAL <- 63567114631    # pence
CUT <- as.Date("2027-01-31"); BANK_RATE <- 3.75; SVR <- 7.49

LISTS <- list(
  repayment_type = c("Repayment", "Interest-only",
                     "Part and part"),
  product_type = c("2Y Fixed", "5Y Fixed", "Tracker", "SVR"),
  region = c("London", "South East", "East of England",
             "South West", "West Midlands", "East Midlands",
             "Yorkshire and the Humber", "North West",
             "North East", "Wales", "Scotland",
             "Northern Ireland"),
  property_type = c("Detached", "Semi-detached", "Terraced",
                    "Flat", "Bungalow"),
  occupancy = "Owner-occupied",
  first_time_buyer = c("Y", "N"),
  employment_status = c("Employed", "Self-employed",
                        "Retired"))
DATES <- c("origination_date", "first_payment_date",
           "fixed_rate_end_date", "cut_off_date")
OPTIONAL <- c("fixed_rate_end_date", "tracker_margin")
NUMS <- c("payments_made", "original_balance",
          "current_balance", "monthly_payment",
          "original_term_months", "remaining_term_months",
          "current_rate", "tracker_margin",
          "original_valuation", "borrower_count",
          "gross_income", "months_in_arrears")

todate <- function(s) {          # NA unless a real ISO date
  x <- as.Date(s, format = "%Y-%m-%d", optional = TRUE)
  x[is.na(x) | format(x, "%Y-%m-%d") != s] <- NA
  x
}
plus <- function(x, m) {         # add whole months
  lt <- as.POSIXlt(x); lt$mon <- lt$mon + m; as.Date(lt)
}
d <- lapply(setNames(DATES, DATES), function(f) todate(t[[f]]))
n <- lapply(setNames(NUMS, NUMS), function(f)
  suppressWarnings(as.numeric(t[[f]])))
ok <- lapply(LISTS, function(v) NULL)
for (f in names(LISTS)) ok[[f]] <- t[[f]] %in% LISTS[[f]]
exc <- data.frame(loan_id = character(0), check = character(0),
                  detail = character(0))
add <- function(id, check, detail) {
  if (length(id)) exc <<- rbind(exc, data.frame(
    loan_id = id, check = check, detail = detail))
}
flag <- function(mask, check, text) {
  i <- which(mask %in% TRUE)
  if (length(i)) add(t$loan_id[i], check, text(i))
}

# ---- K: completeness
for (f in names(t)) if (!(f %in% OPTIONAL))
  flag(t[[f]] == "", "K1", function(i) paste(f, "is blank"))
for (id in unique(t$loan_id[duplicated(t$loan_id)]))
  add(id, "K2", "loan_id appears twice")
ids <- sprintf("KBS-%06d", 1:LEDGER_N)
for (id in sort(setdiff(ids, t$loan_id)))
  add(id, "K3", "loan on ledger, not on tape")

# ---- V: validity against the data dictionary
for (f in names(LISTS))
  flag(t[[f]] != "" & !ok[[f]], "V1",
       function(i) sprintf("%s = '%s'", f, t[[f]][i]))
for (f in DATES)
  flag(t[[f]] != "" & is.na(d[[f]]), "V2",
       function(i) sprintf("%s = %s", f, t[[f]][i]))
for (f in NUMS)
  flag(t[[f]] != "" & is.na(n[[f]]), "V3",
       function(i) paste(f, "not a number"))

# ---- C: consistency between fields
o <- d$origination_date; fp <- d$first_payment_date
fe <- d$fixed_rate_end_date
flag(n$remaining_term_months != n$original_term_months -
     n$payments_made, "C1",
     function(i) "remaining term <> term - payments")
flag(!is.na(o) & !is.na(fp) & fp != plus(o, 1), "C2",
     function(i) "first payment <> origination + 1m")
months <- c("2Y Fixed" = 24, "5Y Fixed" = 60)[t$product_type]
fx <- ok$product_type & !is.na(months) & !is.na(o)
due <- rep(as.Date(NA), nrow(t))
due[fx] <- plus(o[fx], months[fx])
flag(fx & (is.na(fe) | fe != due), "C3",
     function(i) "fixed end date <> origination + period")
flag(ok$product_type & is.na(months) &
     t$fixed_rate_end_date != "", "C3",
     function(i) "end date on a non-fixed loan")
trk <- ok$product_type & t$product_type == "Tracker"
gap <- abs(n$current_rate - BANK_RATE - n$tracker_margin)
flag(trk & (t$tracker_margin == "" | gap > 0.005), "C4",
     function(i) "tracker rate <> Bank Rate + margin")
flag(ok$product_type & !trk & t$tracker_margin != "", "C4",
     function(i) "margin on a non-tracker loan")
flag(ok$product_type & t$product_type == "SVR" &
     abs(n$current_rate - SVR) > 0.005, "C5",
     function(i) "SVR loan not at 7.49%")
y <- as.numeric(format(fp, "%Y"))
m <- as.numeric(format(fp, "%m"))
k <- (2027 - y) * 12 + 1 - m +
     (as.numeric(format(fp, "%d")) <= 31)
flag(!is.na(fp) & k != n$payments_made, "C6",
     function(i) "payments made <> payment dates")

# ---- R: reasonableness
oltv <- 100 * n$original_balance / n$original_valuation
lti <- n$original_balance / n$gross_income
r <- n$current_rate
flag(oltv < 10 | oltv > 100, "R1",
     function(i) sprintf("original LTV %.2f%%", oltv[i]))
flag(lti < 1 | lti > 6, "R2",
     function(i) sprintf("LTI %.2f", lti[i]))
flag(r < 1 | r > 10, "R3",
     function(i) paste0("rate ", r[i], "%"))
flag(n$months_in_arrears > 1, "R4",
     function(i) paste(t$months_in_arrears[i],
                       "months in arrears"))

# ---- P: recalculation (Chapter 1 schedule, closed form)
round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
recalc <- function(P, rate, term, k, kind) {
  mm <- rate / 1200
  if (kind == "Interest-only") return(c(round2(P * mm), P))
  am <- if (kind == "Part and part") round2(P / 2) else P
  pmt <- round2(am * mm / (1 - (1 + mm)^(-term)))
  g <- (1 + mm)^k
  bal <- am * g - pmt * (g - 1) / mm
  if (kind == "Part and part")
    return(c(pmt + round2(am * mm), bal + am))
  c(pmt, bal)
}
for (i in which(ok$repayment_type)) {
  v <- recalc(n$original_balance[i], r[i],
              n$original_term_months[i], n$payments_made[i],
              t$repayment_type[i])
  if (abs(v[1] - n$monthly_payment[i]) > 0.005)
    add(t$loan_id[i], "P1", sprintf("payment %.2f vs tape %.2f",
        v[1], n$monthly_payment[i]))
  if (abs(v[2] - n$current_balance[i]) > 1.00)
    add(t$loan_id[i], "P2", sprintf("balance %.2f vs tape %.2f",
        v[2], n$current_balance[i]))
}

# ---- Report
cents <- sum(round(as.numeric(t$current_balance[
  t$current_balance != ""]) * 100))
p2 <- function(x) sprintf("%.2f", x / 100)
cat("Tape: ", nrow(t), " rows, ", length(unique(t$loan_id)),
    " distinct loan IDs\n", sep = "")
cat("Control totals      ledger          tape    difference\n")
cat(sprintf("  loans   %12d%14d%14d\n", LEDGER_N, nrow(t),
            nrow(t) - LEDGER_N))
cat(sprintf("  balance %12s%14s%14s\n", p2(LEDGER_BAL),
            p2(cents), p2(cents - LEDGER_BAL)))
GROUPS <- list(Completeness = "K1 K2 K3",
               Validity = "V1 V2 V3",
               Consistency = "C1 C2 C3 C4 C5 C6",
               Reasonableness = "R1 R2 R3 R4",
               Recalculation = "P1 P2")
cat("Exceptions by check\n")
for (g in names(GROUPS)) {
  cs <- strsplit(GROUPS[[g]], " ")[[1]]
  cells <- sapply(cs, function(c) paste(c, sum(exc$check == c)))
  cat(sprintf("  %-15s %s\n", g, paste(cells, collapse = "  ")))
}
cat("Total: ", nrow(exc), " exceptions on ",
    length(unique(exc$loan_id)), " loans\n", sep = "")
if (nrow(exc)) {
  cat("Exception report\n")
  exc <- exc[order(exc$loan_id, exc$check, method = "radix"), ]
  for (j in seq_len(nrow(exc)))
    cat("  ", exc$loan_id[j], " ", exc$check[j], " ",
        exc$detail[j], "\n", sep = "")
}
