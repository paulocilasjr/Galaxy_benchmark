# Initial Plan

Experiment: `experiment_1`
Level: `low_context`
Objective: Use Galaxy to train a supervised model from `Chowell_train_Response.tsv` and evaluate treatment-response prediction on `Chowell_test_Response.tsv`.

## Input Datasets

- `dataset/experiment_1/Chowell_train_Response.tsv`
- `dataset/experiment_1/Chowell_test_Response.tsv`

Both files are tabular TSVs with numeric features and a binary `Response` target column.

## Intended Galaxy Workflow

1. Verify Galaxy API credentials without exposing the secret.
2. Create a dedicated Galaxy history for this benchmark run.
3. Upload the two TSV files into the history.
4. Use Galaxy machine-learning tooling if available to fit a binary classifier on the training table and evaluate against the test table.
5. Prefer a standard, auditable classifier that can handle numeric tabular predictors with a binary target; random forest or logistic regression are acceptable first-pass models.
6. Preserve Galaxy history, dataset, job, and provenance snapshots.
7. Download final Galaxy outputs unchanged into `results/`.
8. After Galaxy execution is complete, read task ground truth only for evaluation and write comparison artifacts.

## Intended Tool Choices

- Galaxy upload API for input registration.
- Galaxy machine learning / tabular modeling tools discovered from the target Galaxy instance.
- If no suitable Galaxy ML tool is available, record that blocker with evidence and use the closest Galaxy-executable tabular analysis route available.

## Expected Result Files

- Original Galaxy output file containing test-set predictions and/or evaluation metrics.
- A transformed Galaxy-derived output may be created only if the original output contains the needed values in a tool-native shape.
- `result.json` summarizing the model, outputs, and evaluation.

## Anticipated Risks

- The available Galaxy instance may not expose a suitable supervised classification tool.
- Tool IDs and parameters may differ from expected wrappers.
- Upload or job execution may fail or take longer than a short polling loop.
- Ground-truth evaluation must be delayed until after the Galaxy run is complete.
