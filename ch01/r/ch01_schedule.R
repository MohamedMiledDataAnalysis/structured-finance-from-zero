# Chapter 1 - amortisation schedule for loan KBS-000417 (Thames Residential 2027-1)
# Run from the book folder:
#   Rscript ch01/r/ch01_schedule.R data/thames_residential_2027_1_tape.csv

# R's round() can send a half to the even digit;
# Excel sends it away from zero. round2 copies Excel.
round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}

schedule <- function(principal, annual_rate_pct, n_months) {
  r   <- annual_rate_pct / 1200
  pmt <- round2(principal * r / (1 - (1 + r)^(-n_months)))
  out <- data.frame(month = 1:n_months, opening = 0,
                    payment = 0, interest = 0,
                    principal = 0, closing = 0)
  bal <- principal
  for (m in 1:n_months) {
    interest <- round2(bal * r)
    pay <- if (m < n_months) pmt else round2(bal + interest)
    princ <- round2(pay - interest)
    out[m, 2:6] <- c(bal, pay, interest, princ,
                     round2(bal - princ))
    bal <- round2(bal - princ)
  }
  out
}

args <- commandArgs(trailingOnly = TRUE)
tape <- read.csv(args[1])
loan <- tape[tape$loan_id == "KBS-000417", ]
s <- schedule(loan$original_balance, loan$current_rate, loan$original_term_months)
k <- loan$payments_made
f <- function(x) formatC(x, format = "f", digits = 2, big.mark = "")
cat("Monthly payment      :", f(s$payment[1]), "\n")
cat("First month interest :", f(s$interest[1]), " principal:", f(s$principal[1]), "\n")
cat("Balance after", k, "payments:", f(s$closing[k]), "\n")
cat("  tape says:              ", f(loan$current_balance), "\n")
cat("Final payment        :", f(s$payment[nrow(s)]), "\n")
cat("Total interest paid  :", f(sum(s$interest)), "\n")
