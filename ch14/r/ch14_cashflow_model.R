# Chapter 14 - Thames Residential 2027-1 cash-flow model:
# pool projection, sequential principal waterfall, WAL and
# expected maturity, call and no call. Base case from Chapter 10.
# Run from the book folder:
#   Rscript ch14/r/ch14_cashflow_model.R \
#       data/thames_residential_2027_1_tape.csv \
#       data/ch14_base_case.csv
invisible(Sys.setlocale("LC_TIME", "C"))
args <- commandArgs(trailingOnly = TRUE)
here <- dirname(sub("--file=", "", grep("--file=",
                commandArgs(FALSE), value = TRUE)))
source(file.path(here, "cashflow.R"))

CPRS <- c(0, 5, 10, 15, 20, 25)
money <- function(x) formatC(x, format = "f", digits = 2,
                             big.mark = ",")
mmm <- function(d) format(d, "%b %Y")
f2 <- function(x, w) formatC(x, format = "f", digits = 2, width = w)
p <- function(...) cat(..., "\n", sep = "")
run <- function(S, cpr = base$cpr)
  project_pool(S, cpr, sev = base$sev, lag = base$lag,
               dvec = base$dvec)

t <- load_tape(args[1])
S <- sched_balance(t)
base <- load_base(args[2], S[1])
p("Thames Residential 2027-1 - Chapter 14 cash-flow model")
p("Pool at cut-off: ", money(S[1]))
p("Scheduled balance after 60 months: ", money(S[61]))
p(sprintf("Base case: CPR %.2f%%, severity %.2f%%, lag %d months",
          base$cpr, base$sev, base$lag))
p(sprintf("SMM %.4f%%", 100 * smm(base$cpr)))
pool <- run(S)
m1 <- pool[2, ]
p("Month 1 (Feb 2027)")
labs <- c("opening balance", "defaults", "scheduled principal",
          "prepayments", "closing balance")
vals <- c(pool$balance[1], m1$defaults, m1$scheduled, m1$prepaid,
          m1$balance)
for (i in 1:5) p(sprintf("  %-22s%18s", labs[i], money(vals[i])))
p("Lifetime defaults: ", money(sum(pool$defaults)),
  "  losses: ", money(sum(pool$losses)))
n <- project_notes(pool)
p("IPD 1 (15 Jun 2027): principal ", money(n$available[1]))
wc <- wal_and_maturity(project_notes(pool, TRUE))
wn <- wal_and_maturity(n)
p(sprintf("Base case Class A WAL: %.2f with call, %.2f without",
          wc$A$wal, wn$A$wal))
p("Base case Class A maturity, no call: ", mmm(wn$A$maturity))
p("Base case B-Z WAL, no call: ", paste(sapply(c("B", "C", "D",
  "E", "Z"), function(c) sprintf("%.2f", wn[[c]]$wal)), collapse = " "))
m <- pool$month[pool$balance < 0.1 * S[1]][1]
p("Pool below 10% of cut-off: month ", m, ", IPD ",
  mmm(ipd_date(ipd_of_month(m))))

res <- list()
for (cpr in CPRS) {
  pp <- run(S, cpr)
  for (call in c(TRUE, FALSE))
    res[[paste(cpr, call)]] <- wal_and_maturity(project_notes(pp, call))
}
g <- function(cpr, call, c) res[[paste(cpr, call)]][[c]]
BZ <- c("B", "C", "D", "E", "Z")
p("\nClass A: WAL (years) and expected maturity")
p("CPR   WAL call  Maturity  WAL no call  Maturity")
for (cpr in CPRS) p(sprintf("%2d%%  %s  %s  %s  %s", cpr,
    f2(g(cpr, TRUE, "A")$wal, 8), mmm(g(cpr, TRUE, "A")$maturity),
    f2(g(cpr, FALSE, "A")$wal, 11), mmm(g(cpr, FALSE, "A")$maturity)))
p("\nClasses B-Z: WAL (years), no call")
p("CPR       B       C       D       E       Z")
for (cpr in CPRS) p(sprintf("%2d%%", cpr), paste0(sapply(BZ,
    function(c) f2(g(cpr, FALSE, c)$wal, 8)), collapse = ""))
p("\nClasses B-Z: expected maturity, no call")
p("CPR       B         C         D         E         Z")
for (cpr in CPRS) p(sprintf("%2d%%", cpr), paste0("  ", sapply(BZ,
    function(c) mmm(g(cpr, FALSE, c)$maturity)), collapse = ""))
wbz <- unique(unlist(lapply(CPRS, function(cpr) sapply(BZ,
    function(c) f2(g(cpr, TRUE, c)$wal, 0)))))
p("With call, Classes B-Z WAL at every CPR: ", wbz)

p("\nBase case WAL, no call: loan level versus rep lines")
t$pool <- "all"
t$term_bucket <- (t$n %/% 60) * 5
tests <- list(list("loan level", NULL), list("1 rep line", "pool"),
              list("15 lines: type x 5-yr term",
                   c("repayment_type", "term_bucket")))
for (x in tests) {
  s <- if (is.null(x[[2]])) S else sched_balance(rep_lines(t, x[[2]]))
  w <- wal_and_maturity(project_notes(run(s)))
  p(sprintf("  %-28sA %.2f  Z %.2f", x[[1]], w$A$wal, w$Z$wal))
}
