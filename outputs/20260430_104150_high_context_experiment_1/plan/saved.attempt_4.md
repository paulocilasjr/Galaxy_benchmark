# Attempt 4 Plan

## What Changed
Attempt 3 completed with target column `22`, but Galaxy still resolved the separate-test and advanced-threshold conditionals to defaults (`has_test_file=no`, `customize_defaults=false`). This produced a usable Tabular Learner output but not full prompt compliance.

## Retry Strategy
Use the same flat Tabular Learner `0.1.3` wrapper, but submit conditional controls as flattened Galaxy API keys such as `test_data_choice|has_test_file`, `test_data_choice|test_file`, `advanced_settings|customize_defaults`, and `advanced_settings|probability_threshold`.

## Stopping Rule
If Galaxy still resolves the conditionals to defaults, stop with the partial result and record that the wrapper API did not expose the required conditional controls through the attempted encodings.
