# Attempt 3 Plan

Attempt 2 also failed at Galaxy API validation on the ML wrapper dynamic column selector. The new mechanism avoids ML-wrapper column selection entirely.

Workflow changes:

1. Reuse the existing Galaxy history and uploaded TSV datasets.
2. Run Galaxy `Cut` (`Cut1`) on the training table to create:
   - training features: columns 1-21
   - training labels: column 22
3. Run Galaxy `Cut` (`Cut1`) on the test table to create:
   - test features: columns 1-21
4. Train `LogisticRegression` with `Generalized linear models`, using `all_columns` for both the feature and label datasets.
5. Predict held-out labels with `Model Prediction`, using `all_columns` for the test-feature dataset.

This preserves Galaxy execution while replacing the failing parameter mechanism with explicit Galaxy preprocessing.
