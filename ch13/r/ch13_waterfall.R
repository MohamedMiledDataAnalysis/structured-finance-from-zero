# Chapter 13 - run the Thames waterfall engine on ILLUSTRATIVE
# quarters (not real Thames IPDs; Chapter 26 runs the real ones).
# Run from the book folder:
#   Rscript ch13/r/ch13_waterfall.R \
#       data/ch13_illustrative_scenarios.csv [scenario ...]
# Default scenarios: normal stressed.

args <- commandArgs(trailingOnly = TRUE)
file_arg <- sub("--file=", "", grep("--file=", commandArgs(),
                                    value = TRUE))
source(file.path(dirname(file_arg), "waterfall.R"))

load_scenarios <- function(path) {
  x <- read.csv(path, colClasses = c(scenario = "character"))
  out <- list()
  for (i in seq_len(nrow(x))) {
    r <- x[i, ]
    g <- function(p) setNames(sapply(CLASSES, function(cl) {
      v <- r[[paste0(p, cl)]]; if (is.null(v)) 0 else v }), CLASSES)
    st <- make_state(r$pool, g("note_"), g("pdl_"), g("def_"),
                     r$reserve, r$subloan, r$subloan_unpaid_int)
    pe <- make_period(r$days, r$sonia, r$revenue,
                      r$sched_principal, r$prepayments,
                      r$recoveries, r$losses, r$swap_notional)
    out[[r$scenario]] <- list(state = st, period = pe)
  }
  out
}

m <- function(x) formatC(round2(x) + 0, format = "f", digits = 2,
                         big.mark = ",")

# rows (label, values per scenario) for side-by-side printing
table_rows <- function(results) {
  i <- lapply(results, `[[`, "info")
  st <- lapply(results, `[[`, "state")
  v <- function(f) sapply(seq_along(results), function(k) f(k))
  out <- list(
    list("Available revenue receipts",
         v(function(k) i[[k]]$available_revenue)),
    list(" of which swap receipt", v(function(k) i[[k]]$swap_receipt)),
    list("Principal addition amounts", v(function(k) i[[k]]$paa)),
    list("REVENUE PAID", NULL))
  l0 <- results[[1]]$lines
  for (j in seq_len(nrow(l0)))
    out[[length(out) + 1]] <- list(
      sprintf("(%2s) %s", l0$item[j], substr(l0$label[j], 1, 24)),
      v(function(k) results[[k]]$lines$paid[j]))
  out[[length(out) + 1]] <- list("PRINCIPAL PAID", NULL)
  p0 <- results[[1]]$principal
  for (j in seq_len(nrow(p0))) {
    lab <- sub(" principal", "", p0$label[j])
    lab <- sub("Principal addition amounts",
               "Principal addition amts", lab)
    out[[length(out) + 1]] <- list(paste0("     ", lab),
      v(function(k) results[[k]]$principal$paid[j]))
  }
  out[[length(out) + 1]] <- list("AFTER THE IPD", NULL)
  out[[length(out) + 1]] <- list("Reserve fund",
                                  v(function(k) st[[k]]$reserve))
  out[[length(out) + 1]] <- list("Reserve draw",
                                  v(function(k) i[[k]]$reserve_draw))
  for (cl in CLASSES) out[[length(out) + 1]] <- list(
    paste("Class", cl, "note"), v(function(k) st[[k]]$notes[[cl]]))
  out[[length(out) + 1]] <- list("PDL balance (all classes)",
    v(function(k) sum(st[[k]]$pdl)))
  out[[length(out) + 1]] <- list("Deferred interest B-E",
    v(function(k) sum(st[[k]]$deferred)))
  out[[length(out) + 1]] <- list("Pool balance",
                                  v(function(k) st[[k]]$pool))
  out[[length(out) + 1]] <- list("Check: notes - PDL - pool",
    v(function(k) i[[k]]$balance_check))
  out[[length(out) + 1]] <- list("Senior interest unpaid",
    sapply(i, function(x) if (x$eod_interest) "True" else "False"))
  out
}

show <- function(results) {
  cat(sprintf("%-29s", "ILLUSTRATIVE quarter"),
      paste(sprintf("%16s", names(results)), collapse = ""), "\n",
      sep = "")
  for (r in table_rows(results)) {
    if (is.null(r[[2]])) { cat(r[[1]], "\n", sep = ""); next }
    vals <- if (is.character(r[[2]])) r[[2]] else m(r[[2]])
    cat(sprintf("%-29s", r[[1]]),
        paste(sprintf("%16s", vals), collapse = ""), "\n", sep = "")
  }
}

sc <- load_scenarios(args[1])
names_run <- if (length(args) > 1) args[-1] else
  c("normal", "stressed")
if (identical(names_run, "enforcement")) {
  x <- sc[["severe"]]
  r <- run_post_enforcement(x$state, x$period)
  cat("Severe quarter, post-enforcement (ILLUSTRATIVE)\n")
  cat(sprintf("%-29s%32s\n", "All receipts and reserve",
              m(r$pot_start)))
  cat(sprintf("%-29s%16s%16s\n", "", "due", "paid"))
  for (k in seq_len(nrow(r$lines)))
    cat(sprintf("%-29s%16s%16s\n", r$lines$label[k],
                m(r$lines$due[k]), m(r$lines$paid[k])))
} else {
  res <- lapply(names_run, function(n)
    run_ipd(sc[[n]]$state, sc[[n]]$period))
  names(res) <- names_run
  show(res)
}
