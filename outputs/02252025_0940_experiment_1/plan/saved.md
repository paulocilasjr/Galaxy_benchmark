# Plan: experiment_1

## Experiment name
experiment_1

## Initial objective
Create a new history in Galaxy and upload the datasets. Train a machine learning model to predict the response variable based on the given training dataset and evaluate its performance on the test dataset.

## Inputs and datasets
- Chowell_train_Response.tsv: dataset/experiment_1/Chowell_train_Response.tsv
- Chowell_test_Response.tsv: dataset/experiment_1/Chowell_test_Response.tsv

## Planned steps
1. Validate Galaxy API credential from .env.
2. Discover Tabular Learner tool and select latest available version.
3. Create Galaxy history named experiment_1.
4. Upload train and test TSV datasets to the history.
5. Run Tabular Learner with separate test dataset and target column c22: Response.
6. Poll Galaxy job until terminal state.
7. Read tool outputs and extract target + ROC-AUC.
8. Write result.json and reproduce_experiment_1.py artifacts.
9. Read ground truth and generate comparison table.

## Expected outputs
- outputs/experiment_1/results/result.json
- outputs/experiment_1/results/reproduce_experiment_1.py
- outputs/experiment_1/results/activity_log.jsonl
- outputs/experiment_1/results/comparison_report.md

## Risks/assumptions
- Galaxy remote job runtime may be variable.
- Tool output format may vary by version; extraction uses resilient text matching.
- API operations require a valid GALAXY_API_KEY and network reachability.
