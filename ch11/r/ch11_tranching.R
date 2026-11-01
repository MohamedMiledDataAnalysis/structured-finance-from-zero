# Chapter 11 - Tranching the Thames Residential 2027-1 pool.
# Capital structure, loss allocation across pool-loss scenarios,
# and the 5% vertical slice retained by Kingsbridge. Base R only.
# Run from the book folder:
#   Rscript ch11/r/ch11_tranching.R \
#       data/thames_residential_2027_1_tape.csv

round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
money <- function(x) formatC(x, format = "f", digits = 2,
                             big.mark = ",")
pct4 <- function(x) sprintf("%.4f", round(x, 4))

notes <- data.frame(
  cls = c("A", "B", "C", "D", "E", "Z"),
  amount = c(553000000, 31800000, 19100000, 12700000,
             9500000, 9571146.31))
scen <- c(0.5, 1, 2, 3, 5, 8, 10, 13, 15, 20)

structure <- function(notes, pool) {
  # notes junior to each class = sum of the classes below it
  below <- rev(cumsum(rev(notes$amount))) - notes$amount
  notes$below <- round2(below)
  notes$pct <- notes$amount / pool * 100
  notes$att <- below / pool * 100
  notes$det <- (below + notes$amount) / pool * 100
  notes
}

allocate <- function(cs, loss) {
  # loss beyond the notes below, capped at the class size
  pmin(cs$amount, pmax(0, loss - cs$below))
}

args <- commandArgs(trailingOnly = TRUE)
tape <- read.csv(args[1])
pool <- round2(sum(tape$current_balance))
cs <- structure(notes, pool)
cat("Pool balance at cut-off: ", money(pool), "\n", sep = "")
cat("Total of notes          : ", money(sum(cs$amount)),
    "\n\n", sep = "")
cat(sprintf("%-3s%16s%10s%10s%10s\n", "Cl", "Amount",
            "% pool", "Attach", "Detach"))
for (i in seq_len(nrow(cs)))
  cat(sprintf("%-3s%16s%10s%10s%10s\n", cs$cls[i],
              money(cs$amount[i]), pct4(cs$pct[i]),
              pct4(cs$att[i]), pct4(cs$det[i])))
cat("\nLoss written off each class (% of class)\n")
ord <- match(c("Z", "E", "D", "C", "B", "A"), cs$cls)
cat(sprintf("%5s%16s", "Loss%", "Loss (GBP)"),
    paste(sprintf("%7s", cs$cls[ord]), collapse = ""),
    "\n", sep = "")
for (s in scen) {
  loss <- round2(pool * s / 100)
  a <- allocate(cs, loss)
  cat(sprintf("%5s%16s", format(s), money(loss)),
      paste(sprintf("%7.2f", (a / cs$amount * 100)[ord]),
            collapse = ""), "\n", sep = "")
}
loss <- round2(pool * 3 / 100)
a <- allocate(cs, loss)
cat("\n3% scenario: who bears the loss (GBP)\n")
cat(sprintf("%-3s%15s%14s%15s\n", "Cl", "Class loss",
            "Kingsbridge", "Investors"))
# Kingsbridge: 5% of Classes A-E and all of Class Z
kept <- function(cls, x) ifelse(cls == "Z", x, round2(x * 0.05))
k <- kept(cs$cls, a)
for (i in ord)
  cat(sprintf("%-3s%15s%14s%15s\n", cs$cls[i], money(a[i]),
              money(k[i]), money(round2(a[i] - k[i]))))
cat(sprintf("%-3s%15s%14s%15s\n", "Tot", money(sum(a)),
            money(sum(k)), money(round2(sum(a) - sum(k)))))
held <- kept(cs$cls, cs$amount)
cat("Kingsbridge holds at closing: ", money(sum(held)), " = ",
    pct4(sum(held) / pool * 100), "% of pool\n", sep = "")
