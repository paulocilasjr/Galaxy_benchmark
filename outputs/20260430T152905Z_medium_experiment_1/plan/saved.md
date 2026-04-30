# Initial Plan

Experiment: `experiment_1` from `experiments/medium_context/experiment_1.json`

Objective: create a new Galaxy history, upload the Chowell training and test TSV datasets, run Galaxy Tabular Learner as a classification task to predict `Response`, output predicted probabilities, and test using classification probability threshold `0.25`.

Input datasets:
- `dataset/experiment_1/Chowell_train_Response.tsv`
- `dataset/experiment_1/Chowell_test_Response.tsv`

Intended Galaxy steps:
1. Create a new Galaxy history named for this run.
2. Upload both TSV files as tabular datasets.
3. Locate the Galaxy Tabular Learner tool and inspect its input contract.
4. Configure classification with `Response` as the target column, training dataset as `Chowell_train_Response.tsv`, separate test dataset as `Chowell_test_Response.tsv`, predicted probabilities enabled, and threshold `0.25`.
5. Submit the tool, poll until completion, and preserve history, dataset, job, and provenance snapshots.
6. Download final Galaxy output files unchanged.
7. If needed, create a format-only transformed output derived solely from downloaded Galaxy output for prompt and ground-truth comparison.
8. Evaluate prompt compliance, transformed prompt compliance, direct ground-truth match, transformed ground-truth match, and agent execution in Galaxy.

Expected result files:
- Galaxy Tabular Learner output containing classification metrics and predicted probabilities for the separate test dataset.
- Preserved original downloaded Galaxy output file(s).
- Structured `result.json`, comparison JSON, metrics summary, manifests, and reproduction script.

Anticipated risks:
- Galaxy tool input names or accepted values may differ from local expectations.
- The target column may need to be specified as a column index rather than by name.
- Tool execution may fail if the dataset datatype is not inferred as tabular.
- Output format may be tool-native and require a format-only transformation for benchmark scoring.
