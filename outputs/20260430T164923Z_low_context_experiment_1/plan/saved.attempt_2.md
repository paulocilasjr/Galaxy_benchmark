# Attempt 2 Plan

Attempt 1 created the Galaxy history and uploaded both TSV inputs successfully, but the training submission failed validation before a Galaxy job was created. The error signature was:

- `Parameter 'col1': an invalid option (None) was selected`

Root cause: the uploaded tabular datasets retained the header row in the file preview but Galaxy metadata did not expose header names as selectable column metadata. The wrapper therefore rejected the `Response` header-name selector.

Attempt 2 keeps the same Galaxy history and uploaded datasets, but changes column selection to index-based values:

- predictors: all columns except column 22
- target: column 22

The model and prediction choices remain unchanged: train `LogisticRegression` with `Generalized linear models`, then predict held-out labels with `Model Prediction`.
