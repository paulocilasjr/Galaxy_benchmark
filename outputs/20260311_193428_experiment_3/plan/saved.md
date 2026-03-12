# Experiment name
experiment_3

# Initial objective
Create a new Galaxy history, upload the three HANCOCK multimodal datasets, train multimodal models for patient survival prediction, run at least five architecture/parameter variants, and report the best test ROC-AUC.

# Inputs and datasets
- Galaxy instance: https://usegalaxy.org/
- History name: experiment_3
- Datasets:
  - CD3_CD8_images_3GB_jpeg.zip
  - HANCOCK_train_split_3GB_jpeg.csv
  - HANCOCK_test_split_3GB_jpeg.csv

# Planned steps (ordered list)
1. Validate `GALAXY_API_KEY` from `.env` without exposing secret value.
2. Discover `multimodal_learner` tool versions and select the latest available version.
3. Create a new history named `experiment_3`.
4. Upload all three datasets to the new history using Galaxy fetch-from-URL.
5. Confirm uploaded datasets are terminal `ok` and map train/test/image dataset IDs.
6. Run attempt 1 baseline multimodal configuration and poll to terminal state.
7. Run attempts 2-5 with revised architectures/parameter settings; log each revision rationale.
8. Parse output JSON from each successful attempt and extract test ROC-AUC.
9. Select the best attempt by test ROC-AUC and write `results/result.json`.
10. Write reproduction script, attempt summary, and activity log.
11. After result generation is complete, compare against `ground_truth/experiment_3.json` and write comparison report.

# Expected outputs
- `results/result.json` with: tool_name, target, ROC-AUC
- `results/attempt_summary.json` with per-attempt settings/outcomes
- `results/reproduce_experiment_3.py`
- `results/activity_log.jsonl`
- `results/comparison_report.md`

# Risks/assumptions
- Upload or queue delays for large datasets may require extended polling.
- Some multimodal configurations may fail; failures will be analyzed and logged before retries.
- The target label column is assumed to be column 3 (`target`) in HANCOCK CSV files.
