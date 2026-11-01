# Chapter 37 - coverage tests of Calder Park CLO 1 DAC
# Run from the book folder:
#   Rscript ch37/r/ch37_clo_tests.R \
#       data/ch37_clo_portfolio.csv data/ch37_clo_notes.csv

# ---- inputs (same as the yellow cells of the workbook) ----
PRINCIPAL_CASH <- 8150000.00  # uninvested principal
CCC_LIMIT  <- 0.075           # 7.5% of performing par
EURIBOR    <- 0.0225          # 3M EURIBOR, illustrative
DAYS       <- 90              # 15 Jan to 15 Apr 2027
SENIOR_EXP <- 60000.00        # trustee, admin, agents
MGMT_FEE   <- 0.0015          # senior fee, p.a.
TARGET_PAR <- 400000000.00    # fee base

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
f2  <- function(x) formatC(x, format = "f", digits = 2,
                           big.mark = "")
pct <- function(x) paste0(f2(round2(x * 100)), "%")
say <- function(...) cat(paste(...), "\n", sep = "")

args <- commandArgs(trailingOnly = TRUE)
pf <- read.csv(args[1], stringsAsFactors = FALSE)
nt <- read.csv(args[2], stringsAsFactors = FALSE)
perf <- pf[pf$defaulted == "N", ]
dflt <- pf[pf$defaulted == "Y", ]

# 1. performing par and the CCC bucket
perf_par <- sum(perf$par_eur)
ccc <- perf[startsWith(perf$rating, "CCC"), ]
ccc <- ccc[order(ccc$market_price_pct), ]
ccc_par <- sum(ccc$par_eur)
ccc_lim <- round2(CCC_LIMIT * perf_par)
excess  <- max(0, ccc_par - ccc_lim)

# 2. excess CCC carried at market value:
#    the lowest-priced CCC assets form the excess
haircut <- 0; left <- excess
for (i in seq_len(nrow(ccc))) {
  part <- min(ccc$par_eur[i], left)
  haircut <- haircut + part -
    round2(part * ccc$market_price_pct[i] / 100)
  left <- left - part
}
haircut <- round2(haircut)

# 3. defaulted assets at lower of price and recovery rate
dflt_cv <- sum(round2(dflt$par_eur *
  pmin(dflt$market_price_pct, dflt$recovery_rate_pct) / 100))

acpa <- round2(perf_par - haircut + dflt_cv + PRINCIPAL_CASH)

# 4. interest proceeds for the period (Actual/360)
yf <- DAYS / 360
int_proc <- round2(sum(round2(perf$par_eur *
  (EURIBOR + perf$spread_bps / 10000) * yf)))
fee <- round2(TARGET_PAR * MGMT_FEE * yf)
ic_num <- int_proc - SENIOR_EXP - fee

say("Performing par            :", f2(perf_par))
say("CCC par                   :", f2(ccc_par),
    paste0("(", pct(ccc_par / perf_par), " of performing)"))
say("CCC limit (7.5%)          :", f2(ccc_lim))
say("CCC excess                :", f2(excess))
say("CCC excess haircut        :", f2(haircut))
say("Defaulted par             :", f2(sum(dflt$par_eur)))
say("Defaulted carrying value  :", f2(dflt_cv))
say("Principal cash            :", f2(PRINCIPAL_CASH))
say("Adjusted collateral (ACPA):", f2(acpa))
say("Interest proceeds         :", f2(int_proc))
say("Senior expenses and fee   :", f2(SENIOR_EXP + fee))

cat("\nTest       Ratio    Trigger  Result\n")
notes <- nt[nt$class != "Subordinated", ]
cum_bal <- 0; cum_int <- 0; fails <- list()
for (i in seq_len(nrow(notes))) {
  n <- notes[i, ]
  cum_bal <- cum_bal + n$balance_eur
  cum_int <- cum_int + round2(n$balance_eur *
    (EURIBOR + n$margin_pct / 100) * yf)
  if (n$class == "A") next
  lab <- if (n$class == "B") "A/B" else n$class
  oc <- acpa / cum_bal; trig <- n$oc_trigger_pct / 100
  res <- if (round(oc, 10) >= trig) "PASS" else "FAIL"
  cat(sprintf("OC %-5s %8s %8s  %s\n", lab, pct(oc),
              pct(trig), res))
  if (res == "FAIL") fails[[length(fails) + 1]] <-
    list(lab = lab, s = cum_bal, trig = trig, ci = cum_int)
  if (!is.na(n$ic_trigger_pct)) {
    ic <- ic_num / cum_int; t <- n$ic_trigger_pct / 100
    res <- if (ic >= t) "PASS" else "FAIL"
    cat(sprintf("IC %-5s %8s %8s  %s\n", lab, pct(ic),
                pct(t), res))
  }
}

for (fl in fails) {
  cure <- ceiling((fl$s - acpa / fl$trig) * 100 - 1e-6) / 100
  left_int <- round2(int_proc - SENIOR_EXP - fee - fl$ci)
  cat("\n"); say("Class", fl$lab, "OC cure (redeem Class A):",
      f2(cure))
  say("Interest left after Class", fl$lab, "interest:",
      f2(left_int))
  say("Amount diverted           :", f2(min(cure, left_int)))
}
