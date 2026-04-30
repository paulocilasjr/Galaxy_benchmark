# Attempt 3 Plan

## What Changed
Attempt 2 still resolved the nested `0.1.4` wrapper inputs to defaults despite explicit case markers. The repeated signature shows the API payload is incompatible with the nested section wrapper for the dynamic target/test/threshold fields.

## Retry Strategy
- Use Tabular Learner `0.1.3`, which exposes the same required controls with a flatter schema.
- Create a new Galaxy history and upload the same train/test TSVs.
- Submit flat inputs: training dataset, separate test dataset selected, target selector for `Response`, Logistic Regression candidate, advanced settings enabled, and probability threshold `0.25`.
- Preserve the attempt-3 job parameters and command line for audit.

## Stopping Rule
If this flat-wrapper attempt still resolves the target, test dataset, or threshold to defaults, stop with a documented Galaxy API/tool-wrapper blocker.
