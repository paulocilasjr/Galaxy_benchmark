# Initial Plan: high_context experiment_1

## Objective
Run Galaxy Tabular Learner on separate Chowell treatment-response train and test TSV files, using `c22: Response` as the classification target and classification probability threshold `0.25`.

## Input Datasets
- `dataset/experiment_1/Chowell_train_Response.tsv` as the training dataset.
- `dataset/experiment_1/Chowell_test_Response.tsv` as the separate test dataset.

## Intended Galaxy Steps
1. Create a new Galaxy history for this benchmark run.
2. Upload both TSV files as tabular datasets.
3. Discover/confirm the installed Galaxy Tabular Learner tool and its accepted parameter schema.
4. Execute Tabular Learner with train/test inputs, target column `c22: Response`, Logistic Regression where the tool exposes model selection, and classification probability threshold `0.25`.
5. Poll Galaxy datasets/jobs to terminal state and snapshot history, datasets, jobs, and provenance.
6. Download original Galaxy outputs used for evaluation unchanged into `results/`.
7. Compare available output metrics with `ground_truth/experiment_1.json`, preserving both direct and transformed evaluation records if a tool-native output needs reshaping.

## Expected Result Files
- Original Galaxy output files from Tabular Learner, including model/evaluation statistics or classification outputs.
- A canonical `results/result.json` summarizing Galaxy IDs, output paths, and parsed metrics.
- Evaluation files under `evaluations/`.

## Risks and Fallbacks
- The Tabular Learner parameter schema may differ from the prompt wording; I will snapshot tool metadata and only make schema-compatible parameter choices.
- Galaxy may have queue latency; polling will preserve state checks at the required cadence.
- If the first tool submission fails due to schema mismatch, I will snapshot the error, record the root cause, and create attempt-specific retry artifacts before trying a corrected invocation.
