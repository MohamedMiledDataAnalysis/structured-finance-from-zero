# Chapter 23 - allocate the Class A order book of Thames
# Residential 2027-1 and compare the blended cost of funding
# with the pool yield (illustrative SONIA 3.75%, swap 3.30%).
# Run from the book folder:
#   Rscript ch23/r/ch23_allocation.R \
#       data/ch23_thames_order_book.csv \
#       data/thames_residential_2027_1_tape.csv
args <- commandArgs(trailingOnly = TRUE)
round2 <- function(x) {
  sign(x) * floor(abs(x) * 100 + 0.5 + 1e-9) / 100
}
WEIGHT <- c("Asset manager" = 1.00, "Insurer or pension" = 1.00,
            "Bank treasury" = 0.85, "Hedge fund" = 0.50)
UNIT <- 1000

allocate <- function(book, size, final_bp) {
  ok <- book[is.na(book$limit_margin_bp) |
             book$limit_margin_bp <= final_bp, ]
  wo <- WEIGHT[ok$investor_type] * ok$order_gbp
  ok$raw <- size * wo / sum(wo)
  ok$floor <- floor(ok$raw / UNIT) * UNIT
  left <- (size - sum(ok$floor)) %/% UNIT
  ok$frac <- ok$raw / UNIT - ok$floor / UNIT
  o <- order(-ok$frac, ok$time_entered, ok$order_id)
  ok$alloc <- ok$floor
  top <- o[seq_len(left)]
  ok$alloc[top] <- ok$alloc[top] + UNIT
  stopifnot(sum(ok$alloc) == size,
            all(ok$alloc <= ok$order_gbp))
  ok
}
m <- function(x) formatC(x, format = "f", digits = 0,
                         big.mark = ",", width = 13)
book <- read.csv(args[1], stringsAsFactors = FALSE)
a <- book[book$note_class == "A", ]
al <- allocate(a, 525350000, 62)
cat(sprintf("Class A orders received   : %d %s\n", nrow(a),
            m(sum(a$order_gbp))))
cat(sprintf("Orders valid at SONIA+62bp: %d %s\n", nrow(al),
            m(sum(al$order_gbp))))
cat(sprintf("Coverage at final spread  : %.2fx\n",
            sum(al$order_gbp) / 525350000))
cat(sprintf("%-19s%13s%13s%8s\n", "Investor type", "Orders",
            "Allocated", "Fill"))
for (t in sort(unique(al$investor_type))) {
  g <- al[al$investor_type == t, ]
  o <- sum(g$order_gbp); x <- sum(g$alloc)
  cat(sprintf("%-19s%s%s%7.2f%%\n", t, m(o), m(x), 100 * x / o))
}
o <- sum(al$order_gbp); x <- sum(al$alloc)
cat(sprintf("%-19s%s%s%7.2f%%\n", "Total", m(o), m(x),
            100 * x / o))
for (i in c("A01", "A02", "A03")) {
  r <- al[al$order_id == i, ]
  cat(sprintf("%s  %-19s%s%s\n", i, r$investor_type,
              m(r$order_gbp), m(r$alloc)))
}

# ---- blended cost of funding against the pool yield ----
S <- 0.0375; SWAP <- 0.0330
bal <- c(553000000, 31800000, 19100000, 12700000, 9500000)
mar <- c(0.62, 1.10, 1.50, 2.20, 3.50)
wam <- sum(bal * mar) / sum(bal)
note_int <- sum(bal * (S + mar / 100))
tape <- read.csv(args[2], stringsAsFactors = FALSE)
pool <- sum(tape$current_balance)
pool_int <- sum(tape$current_balance * tape$current_rate / 100)
fixed <- sum(tape$current_balance[grepl("Fixed",
                                        tape$product_type)])
swap_net <- fixed * (S - SWAP)
fees <- 225000 + round2(pool * 0.0015)
profit <- 4000
xs <- pool_int + swap_net - note_int - fees - profit
g <- function(x) formatC(round2(x), format = "f", digits = 2,
                         big.mark = ",", width = 14)
cat(sprintf("Weighted average margin A-E: %.4f%%\n", wam))
lab <- c("Note interest A-E, 1 year", "Pool interest, 1 year",
         "Swap net receipt, 1 year", "Senior expenses + profit",
         "Annual excess spread")
val <- c(note_int, pool_int, swap_net, fees + profit, xs)
for (k in 1:5) cat(sprintf("%-27s: %s %8.4f%%\n", lab[k],
                           g(val[k]), 100 * val[k] / pool))
