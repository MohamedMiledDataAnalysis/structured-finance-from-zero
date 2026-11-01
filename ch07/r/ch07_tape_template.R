# Chapter 7 - data dictionary checks, field map and a
# template-style extract (UK residential real estate
# template, RREL/RREC fields) for ten Thames loans.
# Run from the book folder:
#   Rscript ch07/r/ch07_tape_template.R \
#       data/thames_residential_2027_1_tape.csv \
#       ch07_rrel_extract.csv

args <- commandArgs(trailingOnly = TRUE)
t <- read.csv(args[1], colClasses = "character",
              na.strings = character(0))
out <- if (length(args) > 1) args[2] else
  "ch07_rrel_extract.csv"

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}

# ---- 1. The data dictionary: type and rule for each field
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
INTS <- list(payments_made = c(0, 480),
             original_term_months = c(60, 480),
             remaining_term_months = c(1, 480),
             original_valuation = c(10000, 10000000),
             borrower_count = c(1, 4),
             gross_income = c(1, 10000000),
             months_in_arrears = c(0, 99))
MONEY <- c("original_balance", "current_balance",
           "monthly_payment")
RATES <- list(current_rate = c(0.01, 15),
              tracker_margin = c(-5, 5))
DATES <- c("origination_date", "first_payment_date",
           "fixed_rate_end_date", "cut_off_date")
OPTIONAL <- c("fixed_rate_end_date", "tracker_margin")

num <- function(s) suppressWarnings(as.numeric(s))
isodate <- function(s) {
  d <- as.Date(s, format = "%Y-%m-%d", optional = TRUE)
  !is.na(d) & grepl("^\\d{4}-\\d{2}-\\d{2}$", s) &
    format(d, "%Y-%m-%d") == s
}

invalid <- function(f, s) {
  x <- s[s != ""]
  if (f == "loan_id") {
    bad <- !grepl("^KBS-\\d{6}$", x) | x %in% x[duplicated(x)]
  } else if (f %in% names(LISTS)) {
    bad <- !(x %in% LISTS[[f]])
  } else if (f %in% DATES) {
    bad <- !isodate(x)
  } else if (f %in% names(INTS)) {
    v <- num(x); r <- INTS[[f]]
    bad <- is.na(v) | v %% 1 != 0 | v < r[1] | v > r[2]
  } else if (f %in% MONEY) {
    v <- num(x); cents <- round(v * 100, 6)
    bad <- is.na(v) | v <= 0 | cents %% 1 != 0
  } else if (f %in% names(RATES)) {
    v <- num(x); r <- RATES[[f]]
    bad <- is.na(v) | v < r[1] | v > r[2]
  }
  sum(bad, na.rm = FALSE)
}

blank_report <- character(0); n_bad <- 0
for (f in names(t)) {
  blanks <- sum(t[[f]] == "")
  if (blanks > 0 && !(f %in% OPTIONAL)) n_bad <- n_bad + blanks
  if (blanks > 0) blank_report <- c(blank_report,
                                    paste(f, blanks))
  n_bad <- n_bad + invalid(f, t[[f]])
}
cat("Data dictionary checks: ", ncol(t), " fields, ", nrow(t),
    " loans\n", sep = "")
cat("  blanks (optional fields only):\n")
for (b in blank_report) cat("    ", b, "\n", sep = "")
cat("  values outside the dictionary: ", n_bad, "\n", sep = "")

# ---- 2. The field map: Kingsbridge tape -> template field
MAP <- list(
  direct = paste("RREL2 RREL6 RREL23 RREL25 RREL29 RREL30",
                 "RREL39 RREL43 RREL58 RREC17"),
  transformed = paste("RREL13 RREL16 RREL35 RREL42 RREL44",
                      "RREL46 RREL51 RREL69 RREC7 RREC9"),
  derived = paste("RREL1 RREL17 RREL24 RREL28 RREL37 RREL38",
                  "RREC16 RREC22"),
  gap = paste("RREL4 RREL11 RREL19 RREL27 RREL67 RREL68 RREC6",
              "RREC12 RREC13 RREC14 RREC15 RREC18 RREC19"))
n <- sapply(MAP, function(v) length(strsplit(v, " ")[[1]]))
cat("Field map: ", sum(n), " template fields\n", sep = "")
cat("  ", paste(names(n), n, collapse = ", "), "\n", sep = "")

# ---- 3. Template-style extract for ten loans
LOANS <- c("KBS-000001", "KBS-000002", "KBS-000003",
           "KBS-000004", "KBS-000005", "KBS-000006",
           "KBS-000012", "KBS-000042", "KBS-000059",
           "KBS-000417")
EMP <- c(Employed = "EMUK", "Self-employed" = "SFEM",
         Retired = "PNNR")
AMORT <- c(Repayment = "FRXX", "Interest-only" = "BLLT",
           "Part and part" = "OTHR")
PROP <- c(Detached = "RHOS", "Semi-detached" = "RHOS",
          Terraced = "RTHS", Flat = "RFLT", Bungalow = "RBGL")
OCC <- c("Owner-occupied" = "FOWN")
LEI <- "KBS0FICTIONAL0LEI027"        # fictional LEI

money <- function(s) formatC(num(s), format = "f", digits = 2)
plus_months <- function(iso, m) {
  format(seq(as.Date(iso), by = paste(m, "months"),
             length.out = 2)[2], "%Y-%m-%d")
}

x <- t[t$loan_id %in% LOANS, ]
fixed <- x$product_type %in% c("2Y Fixed", "5Y Fixed")
idx <- ifelse(x$product_type == "Tracker", "BOER", "LDOR")
mar <- ifelse(x$tracker_margin == "", "0.00", x$tracker_margin)
ext <- data.frame(
  RREL1 = paste0(LEI, "N202701"),
  RREL2 = x$loan_id,
  RREL6 = x$cut_off_date,
  RREL13 = unname(EMP[x$employment_status]),
  RREL16 = ifelse(x$borrower_count == "1",
                  money(x$gross_income), "ND3"),
  RREL17 = "GRAN",
  RREL23 = x$origination_date,
  RREL24 = mapply(plus_months, x$origination_date,
                  x$original_term_months),
  RREL25 = x$original_term_months,
  RREL28 = "GBP",
  RREL29 = money(x$original_balance),
  RREL30 = money(x$current_balance),
  RREL35 = unname(AMORT[x$repayment_type]),
  RREL37 = "MNTH",
  RREL39 = money(x$monthly_payment),
  RREL42 = ifelse(fixed, "FLCF", "FLIF"),
  RREL43 = x$current_rate,
  RREL44 = ifelse(fixed, "ND5", idx),
  RREL46 = ifelse(fixed, "ND5", mar),
  RREL51 = ifelse(fixed, x$fixed_rate_end_date, "ND5"),
  RREL58 = x$payments_made,
  RREL69 = ifelse(x$months_in_arrears == "0", "PERF", "ARRE"),
  RREC7 = unname(OCC[x$occupancy]),
  RREC9 = unname(PROP[x$property_type]),
  RREC16 = formatC(round2(100 * num(x$original_balance) /
                          num(x$original_valuation)),
                   format = "f", digits = 2),
  RREC17 = money(x$original_valuation),
  row.names = NULL)
write.csv(ext, out, row.names = FALSE, quote = FALSE)
cat("Extract: ", nrow(ext), " loans x ", ncol(ext),
    " fields -> ", out, "\n", sep = "")
show <- c("RREL2", "RREL35", "RREL42", "RREL44", "RREL46",
          "RREL69", "RREC16")
# right-aligned columns, one space apart
cols <- lapply(show, function(k) {
  v <- c(k, ext[[k]])
  formatC(v, width = max(nchar(v)))
})
for (i in seq_len(nrow(ext) + 1))
  cat(paste(sapply(cols, `[`, i), collapse = " "), "\n",
      sep = "")
