# Experiment 1: Machine Learning Model

## Objective
Train a machine learning model to predict the response variable using the training dataset and evaluate its performance on the test dataset.

## Inputs and Datasets
- **Training Dataset**: `dataset/experiment_1/Chowell_train_Response.tsv`
- **Test Dataset**: `dataset/experiment_1/Chowell_test_Response.tsv`

## Planned Steps
1. **Validate Galaxy API credentials** – ensure `.env` contains a non‑empty `GALAXY_API_KEY`.
2. **Create a new Galaxy history** named `experiment_1`.
3. **Upload the training dataset** to the history.
4. **Upload the test dataset** to the history.
5. **Execute the Tabular Learner tool** with the following parameters:
   - *Tabular Input Dataset*: `Chowell_train_Response.tsv`
   - *Do you have a separate test dataset*: `yes`
   - *Tabular Test Dataset*: `Chowell_test_Response.tsv`
   - *Select the target column*: `c22: Response`
6. **Capture experiment outputs**:
   - `results/result.json`
   - `results/activity_log.jsonl`
   - `results/reproduce_experiment_1.py`
7. **Log reasoning** and **record any errors** in the designated directories.

## Expected Outputs
- `outputs/20260304_162800_experiment_1/plan/saved.md` (this plan)
- `outputs/20260304_162800_experiment_1/reasoning/reasoning.md`
- `outputs/20260304_162800_experiment_1/errors/error.json` (if errors occur)
- `outputs/20260304_162800_experiment_1/results/result.json`
- `outputs/20260304_162800_experiment_1/results/reproduce_experiment_1.py`
- `outputs/20260304_162800_experiment_1/results/activity_log.jsonl`

## Risks / Assumptions
- The workstation has stable internet access for API calls.
- The `.env` file contains a valid, non‑empty `GALAXY_API_KEY`.
- The two TSV files are correctly formatted and can be uploaded to Galaxy.
- The `Tabular Learner` tool is available on the Galaxy instance and its parameters are as described.
- No external dependencies (e.g., additional libraries) are required beyond what Galaxy provides.