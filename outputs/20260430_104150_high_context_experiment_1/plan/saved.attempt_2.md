# Attempt 2 Plan

## What Changed
Attempt 1 submitted nested conditional values without Galaxy's explicit `__current_case__` markers. Galaxy accepted the request but resolved defaults incorrectly: it used `target_feature` as column `1`, did not attach the separate test file, and kept probability threshold `0.5`. The job failed during stratified splitting on the wrong target (`TMB`).

## Retry Strategy
- Create a new Galaxy history to avoid mixing retry outputs with the failed attempt.
- Re-upload the same two TSV inputs.
- Submit Tabular Learner with explicit conditional case indices: separate test dataset case `yes`, sample ID case `no`, classification model case, and cross-validation enabled case.
- Pass target column as `22`, the Galaxy selector value for `c22: Response`, and pass probability threshold as string `0.25` so Galaxy preserves the value.
- Poll to terminal state, snapshot job parameters, and verify the command line contains `--target_col '22'`, `--test_file`, and `--probability_threshold '0.25'` before evaluation.

## Stopping Rule
If the same parameter-resolution signature repeats, stop and record the blocker instead of doing a superficial retry.
