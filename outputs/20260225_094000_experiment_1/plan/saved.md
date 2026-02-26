# Experiment 1 Plan

## Experiment Name
experiment_1

## Initial Objective
Create a new history in Galaxy and upload the datasets. Train a machine learning model to predict the response variable based on the given training dataset and evaluate its performance on the test dataset.

## Inputs and Datasets
- Chowell_train_Response.tsv: Training dataset located at dataset/experiment_1/Chowell_train_Response.tsv
- Chowell_test_Response.tsv: Test dataset located at dataset/experiment_1/Chowell_test_Response.tsv

## Planned Steps
1. Create a new history named "experiment_1" in Galaxy.
2. Upload Chowell_train_Response.tsv to the history.
3. Upload Chowell_test_Response.tsv to the history.
4. Run the "Tabular Learner" tool with parameters:
   - Tabular Input Dataset: Chowell_train_Response.tsv
   - Do you have a separate test dataset: yes
   - Tabular Test Dataset: Chowell_test_Response.tsv
   - Select the target column: c22: Response
5. Poll for job completion.
6. Extract the required outputs: tool_name, target, roc-auc from the results.
7. Write result.json with the extracted values.

## Expected Outputs
- result.json containing:
  - tool_name: "Tabular Learner"
  - target: Value from the report
  - roc-auc: ROC-AUC value from test summary

## Risks/Assumptions
- Galaxy API is accessible and API key is valid.
- Datasets are in correct format.
- Tool parameters are correct.
- No network issues during execution.