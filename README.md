# Structured Finance from Zero — Book 1: UK and European Deals
### Companion files (bonus materials)

These are the free companion files for the book *Structured Finance from Zero — Book 1: UK and European Deals* by Mohamed Miled. You can read the book without them; you need them to do the exercises and to rerun every calculation in the book yourself. The Final Exam's detailed worked corrections are in `exam/exam_detailed_corrections.md`.

## What is here

| Folder | Contents |
|---|---|
| `data/` | Every dataset used in the book, as CSV files: the Thames Residential 2027-1 and Rhein Auto 2027-1 loan tapes, the originators' history, 24 months of Thames performance, the payment-date results and the chapter datasets |
| `chNN/excel/` | The Excel workbook for chapter NN (live formulas; yellow cells are inputs) |
| `chNN/python/`, `chNN/r/` | The Python and R scripts for chapter NN; both print the same results |
| `exam/` | The Final Exam: candidate workbook, solution workbook, Python and R solutions, detailed corrections |
| `appC/` | The set-up check described in Appendix C |
| `tools/` | The generators that rebuild every dataset from a fixed random seed, and the builders of the workbooks |

## Getting started

1. Download this repository (**Code › Download ZIP**) and unzip it. GitHub names the folder `structured-finance-from-zero-main`; rename it `structured-finance-from-zero`, the name the book uses. Keep the folder structure exactly as it is.
2. Open a terminal in the unzipped folder, the "book folder", and run the set-up check:
   `python3 appC/python/appC_check_setup.py data` and `Rscript appC/r/appC_check_setup.R data`
3. Run any chapter script from the book folder, exactly as printed in the book, for example:
   `python3 ch01/python/ch01_schedule.py data/thames_residential_2027_1_tape.csv`
4. To run every example in the book in one go: `bash run_all_examples.sh`

**Requirements**
- **Python:** 3.12 or later, with pandas, numpy, openpyxl and matplotlib.
- **R:** 4.x, base R only.
- **Spreadsheet:** Excel 2019, Excel 2021, Microsoft 365, or LibreOffice Calc 7 or later.

Every workbook recalculates when it opens.

## Reproducibility

Every dataset is synthetic and generated with a published seed. Running the generators in `tools/` (the command is in each file's header) recreates the files in `data/` byte for byte.

## Important

- All companies, deals, people and loan data in these files are **fictional**. Any resemblance to real entities or transactions is coincidental.
- For education only. Nothing here is legal, tax, accounting or investment advice.
- See `LICENSE` for the terms of use.
