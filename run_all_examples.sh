#!/bin/bash
# Runs every Python and R example in the book, from this folder.
cd "$(dirname "$0")"
set -e
echo ">> python3 appC/python/appC_check_setup.py data"; python3 appC/python/appC_check_setup.py data > /dev/null
echo ">> Rscript appC/r/appC_check_setup.R data"; Rscript appC/r/appC_check_setup.R data > /dev/null
echo ">> python3 ch01/python/ch01_schedule.py data/thames_residential_2027_1_tape.csv"; python3 ch01/python/ch01_schedule.py data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> Rscript ch01/r/ch01_schedule.R data/thames_residential_2027_1_tape.csv"; Rscript ch01/r/ch01_schedule.R data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> python3 ch02/python/ch02_bonds.py data/thames_sonia_assumption.csv"; python3 ch02/python/ch02_bonds.py data/thames_sonia_assumption.csv > /dev/null
echo ">> Rscript ch02/r/ch02_bonds.R data/thames_sonia_assumption.csv"; Rscript ch02/r/ch02_bonds.R data/thames_sonia_assumption.csv > /dev/null
echo ">> python3 ch03/python/ch03_credit_risk.py data/thames_residential_2027_1_tape.csv data/kingsbridge_static_pool_defaults.csv data/kingsbridge_dynamic_book.csv"; python3 ch03/python/ch03_credit_risk.py data/thames_residential_2027_1_tape.csv data/kingsbridge_static_pool_defaults.csv data/kingsbridge_dynamic_book.csv > /dev/null
echo ">> Rscript ch03/r/ch03_credit_risk.R data/thames_residential_2027_1_tape.csv data/kingsbridge_static_pool_defaults.csv data/kingsbridge_dynamic_book.csv"; Rscript ch03/r/ch03_credit_risk.R data/thames_residential_2027_1_tape.csv data/kingsbridge_static_pool_defaults.csv data/kingsbridge_dynamic_book.csv > /dev/null
echo ">> python3 ch04/python/ch04_funding.py"; python3 ch04/python/ch04_funding.py > /dev/null
echo ">> Rscript ch04/r/ch04_funding.R"; Rscript ch04/r/ch04_funding.R > /dev/null
echo ">> python3 ch06/python/ch06_pool_metrics.py data/thames_residential_2027_1_tape.csv"; python3 ch06/python/ch06_pool_metrics.py data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> Rscript ch06/r/ch06_pool_metrics.R data/thames_residential_2027_1_tape.csv"; Rscript ch06/r/ch06_pool_metrics.R data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> python3 ch07/python/ch07_tape_template.py data/thames_residential_2027_1_tape.csv ch07_rrel_extract.csv"; python3 ch07/python/ch07_tape_template.py data/thames_residential_2027_1_tape.csv ch07_rrel_extract.csv > /dev/null
echo ">> Rscript ch07/r/ch07_tape_template.R data/thames_residential_2027_1_tape.csv ch07_rrel_extract.csv"; Rscript ch07/r/ch07_tape_template.R data/thames_residential_2027_1_tape.csv ch07_rrel_extract.csv > /dev/null
echo ">> python3 ch08/python/ch08_aup_sample.py data/thames_residential_2027_1_tape.csv"; python3 ch08/python/ch08_aup_sample.py data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> python3 ch08/python/ch08_validate.py data/ch08_thames_tape_raw.csv"; python3 ch08/python/ch08_validate.py data/ch08_thames_tape_raw.csv > /dev/null
echo ">> Rscript ch08/r/ch08_aup_sample.R data/thames_residential_2027_1_tape.csv"; Rscript ch08/r/ch08_aup_sample.R data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> Rscript ch08/r/ch08_validate.R data/ch08_thames_tape_raw.csv"; Rscript ch08/r/ch08_validate.R data/ch08_thames_tape_raw.csv > /dev/null
echo ">> python3 ch09/python/ch09_pool_selection.py data/ch09_thames_provisional_pool.csv"; python3 ch09/python/ch09_pool_selection.py data/ch09_thames_provisional_pool.csv > /dev/null
echo ">> Rscript ch09/r/ch09_pool_selection.R data/ch09_thames_provisional_pool.csv"; Rscript ch09/r/ch09_pool_selection.R data/ch09_thames_provisional_pool.csv > /dev/null
echo ">> python3 ch10/python/ch10_history.py data/kingsbridge_static_pool_defaults.csv data/kingsbridge_dynamic_book.csv"; python3 ch10/python/ch10_history.py data/kingsbridge_static_pool_defaults.csv data/kingsbridge_dynamic_book.csv > /dev/null
echo ">> Rscript ch10/r/ch10_history.R data/kingsbridge_static_pool_defaults.csv data/kingsbridge_dynamic_book.csv"; Rscript ch10/r/ch10_history.R data/kingsbridge_static_pool_defaults.csv data/kingsbridge_dynamic_book.csv > /dev/null
echo ">> python3 ch11/python/ch11_tranching.py data/thames_residential_2027_1_tape.csv"; python3 ch11/python/ch11_tranching.py data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> Rscript ch11/r/ch11_tranching.R data/thames_residential_2027_1_tape.csv"; Rscript ch11/r/ch11_tranching.R data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> python3 ch12/python/ch12_excess_spread.py data/thames_residential_2027_1_tape.csv"; python3 ch12/python/ch12_excess_spread.py data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> Rscript ch12/r/ch12_excess_spread.R data/thames_residential_2027_1_tape.csv"; Rscript ch12/r/ch12_excess_spread.R data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> python3 ch13/python/ch13_waterfall.py data/ch13_illustrative_scenarios.csv"; python3 ch13/python/ch13_waterfall.py data/ch13_illustrative_scenarios.csv > /dev/null
echo ">> Rscript ch13/r/ch13_waterfall.R data/ch13_illustrative_scenarios.csv"; Rscript ch13/r/ch13_waterfall.R data/ch13_illustrative_scenarios.csv > /dev/null
echo ">> python3 ch14/python/ch14_cashflow_model.py data/thames_residential_2027_1_tape.csv data/ch14_base_case.csv"; python3 ch14/python/ch14_cashflow_model.py data/thames_residential_2027_1_tape.csv data/ch14_base_case.csv > /dev/null
echo ">> Rscript ch14/r/ch14_cashflow_model.R data/thames_residential_2027_1_tape.csv data/ch14_base_case.csv"; Rscript ch14/r/ch14_cashflow_model.R data/thames_residential_2027_1_tape.csv data/ch14_base_case.csv > /dev/null
echo ">> python3 ch15/python/ch15_swap.py data/thames_residential_2027_1_tape.csv data/thames_sonia_assumption.csv data/ch15_sonia_daily_sample.csv data/ch14_base_case.csv"; python3 ch15/python/ch15_swap.py data/thames_residential_2027_1_tape.csv data/thames_sonia_assumption.csv data/ch15_sonia_daily_sample.csv data/ch14_base_case.csv > /dev/null
echo ">> Rscript ch15/r/ch15_swap.R data/thames_residential_2027_1_tape.csv data/thames_sonia_assumption.csv data/ch15_sonia_daily_sample.csv data/ch14_base_case.csv"; Rscript ch15/r/ch15_swap.R data/thames_residential_2027_1_tape.csv data/thames_sonia_assumption.csv data/ch15_sonia_daily_sample.csv data/ch14_base_case.csv > /dev/null
echo ">> python3 ch16/python/ch16_call_economics.py data/thames_residential_2027_1_tape.csv data/ch14_base_case.csv"; python3 ch16/python/ch16_call_economics.py data/thames_residential_2027_1_tape.csv data/ch14_base_case.csv > /dev/null
echo ">> Rscript ch16/r/ch16_call_economics.R data/thames_residential_2027_1_tape.csv data/ch14_base_case.csv"; Rscript ch16/r/ch16_call_economics.R data/thames_residential_2027_1_tape.csv data/ch14_base_case.csv > /dev/null
echo ">> python3 ch18/python/ch18_loan_level.py data/thames_residential_2027_1_tape.csv data/ch18_regional_hpi.csv data/kingsbridge_static_pool_defaults.csv"; python3 ch18/python/ch18_loan_level.py data/thames_residential_2027_1_tape.csv data/ch18_regional_hpi.csv data/kingsbridge_static_pool_defaults.csv > /dev/null
echo ">> Rscript ch18/r/ch18_loan_level.R data/thames_residential_2027_1_tape.csv data/ch18_regional_hpi.csv data/kingsbridge_static_pool_defaults.csv"; Rscript ch18/r/ch18_loan_level.R data/thames_residential_2027_1_tape.csv data/ch18_regional_hpi.csv data/kingsbridge_static_pool_defaults.csv > /dev/null
echo ">> python3 ch19/python/ch19_stress_cashflow.py data/ch19_thames_schedules.csv data/ch18_rating_level_results.csv"; python3 ch19/python/ch19_stress_cashflow.py data/ch19_thames_schedules.csv data/ch18_rating_level_results.csv > /dev/null
echo ">> Rscript ch19/r/ch19_stress_cashflow.R data/ch19_thames_schedules.csv data/ch18_rating_level_results.csv"; Rscript ch19/r/ch19_stress_cashflow.R data/ch19_thames_schedules.csv data/ch18_rating_level_results.csv > /dev/null
echo ">> python3 ch22/python/ch22_senior_expenses.py data/thames_performance_monthly.csv"; python3 ch22/python/ch22_senior_expenses.py data/thames_performance_monthly.csv > /dev/null
echo ">> Rscript ch22/r/ch22_senior_expenses.R data/thames_performance_monthly.csv"; Rscript ch22/r/ch22_senior_expenses.R data/thames_performance_monthly.csv > /dev/null
echo ">> python3 ch23/python/ch23_allocation.py data/ch23_thames_order_book.csv data/thames_residential_2027_1_tape.csv"; python3 ch23/python/ch23_allocation.py data/ch23_thames_order_book.csv data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> Rscript ch23/r/ch23_allocation.R data/ch23_thames_order_book.csv data/thames_residential_2027_1_tape.csv"; Rscript ch23/r/ch23_allocation.R data/ch23_thames_order_book.csv data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> python3 ch24/python/ch24_funds_flow.py"; python3 ch24/python/ch24_funds_flow.py > /dev/null
echo ">> Rscript ch24/r/ch24_funds_flow.R"; Rscript ch24/r/ch24_funds_flow.R > /dev/null
echo ">> python3 ch25/python/ch25_arrears.py data/ch25_thames_arrears_states.csv"; python3 ch25/python/ch25_arrears.py data/ch25_thames_arrears_states.csv > /dev/null
echo ">> Rscript ch25/r/ch25_arrears.R data/ch25_thames_arrears_states.csv"; Rscript ch25/r/ch25_arrears.R data/ch25_thames_arrears_states.csv > /dev/null
echo ">> python3 ch26/python/ch26_waterfall.py data/thames_performance_monthly.csv"; python3 ch26/python/ch26_waterfall.py data/thames_performance_monthly.csv > /dev/null
echo ">> Rscript ch26/r/ch26_waterfall.R data/thames_performance_monthly.csv"; Rscript ch26/r/ch26_waterfall.R data/thames_performance_monthly.csv > /dev/null
echo ">> python3 ch27/python/ch27_report.py data/thames_ipd_results.csv"; python3 ch27/python/ch27_report.py data/thames_ipd_results.csv > /dev/null
echo ">> Rscript ch27/r/ch27_report.R data/thames_ipd_results.csv"; Rscript ch27/r/ch27_report.R data/thames_ipd_results.csv > /dev/null
echo ">> python3 ch28/python/ch28_class_a_dm.py data/thames_performance_monthly.csv"; python3 ch28/python/ch28_class_a_dm.py data/thames_performance_monthly.csv > /dev/null
echo ">> Rscript ch28/r/ch28_class_a_dm.R data/thames_performance_monthly.csv"; Rscript ch28/r/ch28_class_a_dm.R data/thames_performance_monthly.csv > /dev/null
echo ">> python3 ch29/python/ch29_surveillance.py data/thames_ipd_results.csv"; python3 ch29/python/ch29_surveillance.py data/thames_ipd_results.csv > /dev/null
echo ">> Rscript ch29/r/ch29_surveillance.R data/thames_ipd_results.csv"; Rscript ch29/r/ch29_surveillance.R data/thames_ipd_results.csv > /dev/null
echo ">> python3 ch30/python/ch30_pool_analysis.py data/rhein_auto_2027_1_tape.csv data/rheinwagen_static_pool_losses.csv"; python3 ch30/python/ch30_pool_analysis.py data/rhein_auto_2027_1_tape.csv data/rheinwagen_static_pool_losses.csv > /dev/null
echo ">> python3 ch30/python/ch30_static_curves.py data/rheinwagen_static_pool_losses.csv ch30/ch30_static_curves.png"; python3 ch30/python/ch30_static_curves.py data/rheinwagen_static_pool_losses.csv ch30/ch30_static_curves.png > /dev/null
echo ">> Rscript ch30/r/ch30_pool_analysis.R data/rhein_auto_2027_1_tape.csv data/rheinwagen_static_pool_losses.csv"; Rscript ch30/r/ch30_pool_analysis.R data/rhein_auto_2027_1_tape.csv data/rheinwagen_static_pool_losses.csv > /dev/null
echo ">> python3 ch31/python/ch31_rhein_cashflow.py data/ch31_rhein_scheduled_runoff.csv"; python3 ch31/python/ch31_rhein_cashflow.py data/ch31_rhein_scheduled_runoff.csv > /dev/null
echo ">> Rscript ch31/r/ch31_rhein_cashflow.R data/ch31_rhein_scheduled_runoff.csv"; Rscript ch31/r/ch31_rhein_cashflow.R data/ch31_rhein_scheduled_runoff.csv > /dev/null
echo ">> python3 ch35/python/ch35_sec_sa.py data/thames_residential_2027_1_tape.csv"; python3 ch35/python/ch35_sec_sa.py data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> Rscript ch35/r/ch35_sec_sa.R data/thames_residential_2027_1_tape.csv"; Rscript ch35/r/ch35_sec_sa.R data/thames_residential_2027_1_tape.csv > /dev/null
echo ">> python3 ch37/python/ch37_clo_tests.py data/ch37_clo_portfolio.csv data/ch37_clo_notes.csv"; python3 ch37/python/ch37_clo_tests.py data/ch37_clo_portfolio.csv data/ch37_clo_notes.csv > /dev/null
echo ">> Rscript ch37/r/ch37_clo_tests.R data/ch37_clo_portfolio.csv data/ch37_clo_notes.csv"; Rscript ch37/r/ch37_clo_tests.R data/ch37_clo_portfolio.csv data/ch37_clo_notes.csv > /dev/null
echo ">> python3 exam/python/exam_solutions.py data/exam_medway_tape.csv data/exam_medway_deal_terms.csv data/exam_medway_ipd_inputs.csv"; python3 exam/python/exam_solutions.py data/exam_medway_tape.csv data/exam_medway_deal_terms.csv data/exam_medway_ipd_inputs.csv > /dev/null
echo "All examples ran successfully."
