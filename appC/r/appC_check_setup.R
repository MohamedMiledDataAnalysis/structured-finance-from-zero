# Appendix C - checks that R and the data folder work.
# Run from the book folder:
#   Rscript appC/r/appC_check_setup.R data
args <- commandArgs(trailingOnly = TRUE)
t <- read.csv(file.path(args[1], "thames_residential_2027_1_tape.csv"))
r <- read.csv(file.path(args[1], "rhein_auto_2027_1_tape.csv"))
f2 <- function(x) formatC(x, format = "f", digits = 2)
cat("Thames loans  : ", nrow(t), "\n", sep = "")
cat("Thames balance: ", f2(sum(t$current_balance)), "\n", sep = "")
cat("Rhein loans   : ", nrow(r), "\n", sep = "")
cat("Rhein balance : ", f2(sum(r$current_balance)), "\n", sep = "")
cat("Setup OK\n")
