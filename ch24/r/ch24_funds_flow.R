# Chapter 24 - closing-day funds flow of Thames Residential
# 2027-1 (18 March 2027). Upfront costs are illustrative.
# Run from the book folder:
#   Rscript ch24/r/ch24_funds_flow.R
round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
NOTES <- c(A = 553000000, B = 31800000, C = 19100000,
           D = 12700000, E = 9500000, Z = 9571146.31)
COMM <- c(A = 0.0015, B = 0.0035, C = 0.0035, D = 0.0035,
          E = 0.0035)
SUB_LOAN <- 9391500
PRICE <- 635671146.31
COSTS <- c("Rating agency 1" = 340000,
           "Rating agency 2" = 310000,
           "Carver Whitlock LLP" = 900000,
           "Pemberton Hale LLP" = 132000,
           "Harper & Lane LLP (AUP)" = 157532.5,
           "STS Verification Partners" = 72000,
           "Albion Trustee Services" = 18000,
           "Albion Bank plc (agency)" = 6000,
           "Meridian Corporate Services" = 12000,
           "FCA and LSE fees" = 21385)

ae <- NOTES[c("A", "B", "C", "D", "E")]
keep <- round2(ae * 0.05)                  # 5% vertical slice
placed <- round2(sum(ae - keep))
retained <- round2(sum(keep) + NOTES["Z"]) # all of Z kept
comm <- round2(sum(round2((ae - keep) * COMM)))
costs <- round2(sum(COSTS))

show <- function(label, x) {
  cat(sprintf("%-38s%16s\n", label,
              formatC(round2(x), format = "f", digits = 2,
                      big.mark = ",")))
}
cat("SOURCES AND USES\n")
show("Placed notes (95% of A-E)", placed)
show("Retained notes (5% of A-E, all of Z)", retained)
show("Subordinated loan", SUB_LOAN)
src <- placed + retained + SUB_LOAN
show("Total sources", src)
show("Initial consideration to Kingsbridge", PRICE)
show("General reserve fund", SUB_LOAN)
use <- PRICE + SUB_LOAN
show("Total uses", use)
show("Sources - uses", src - use)

cat("\nHOW THE CONSIDERATION IS SETTLED\n")
show("Initial consideration", PRICE)
show("less retained notes delivered", -retained)
show("less JLM commission (deducted)", -comm)
show("less third-party costs paid", -costs)
show("less subordinated loan (netted)", -SUB_LOAN)
net <- round2(PRICE - retained - comm - costs - SUB_LOAN)
show("Net cash to Kingsbridge", net)

cat("\nTRANSACTION ACCOUNT ON 18 MARCH 2027\n")
show("JLMs pay in, net of commission", placed - comm)
show("Paid to third parties", -costs)
show("Paid to Kingsbridge", -net)
bal <- round2(placed - comm - costs - net)
show("Balance after settlement", bal)
show("Check: balance - reserve required", bal - SUB_LOAN)
