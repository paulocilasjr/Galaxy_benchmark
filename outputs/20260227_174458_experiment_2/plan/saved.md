# Experiment name
experiment_2

# Initial objective
Create a Galaxy history, upload the provided metadata CSV and image ZIP, run Image Learner model training/evaluation, and report final benchmark outputs for at least 5 attempts.

# Inputs and datasets
- selected_HAM10000_img_metadata_aug.csv: https://zenodo.org/records/18394055/files/selected_HAM10000_img_metadata_aug.csv
- skin_image.zip: https://zenodo.org/records/18394055/files/skin_image.zip
- Galaxy instance: https://usegalaxy.org/
- Galaxy history name: experiment_2

# Planned steps
1. Validate `GALAXY_API_KEY` from `.env`.
2. Discover latest `Image Learner` tool and inspect parameter schema.
3. Create history `experiment_2`, download input files locally in run scope, upload to Galaxy.
4. If upload stalls, use a documented retry+revise fallback to copy datasets from prior `experiment_2` history.
5. Run at least 5 attempts with architecture/parameter revisions and leakage mitigation.
6. Poll every job to terminal state and parse best test ROC-AUC evidence.
7. Write `results/result.json` and `results/reproduce_experiment_2.py`.
8. Read ground truth only after result generation and write comparison table.

# Expected outputs
- outputs/20260227_174458_experiment_2/results/result.json
- outputs/20260227_174458_experiment_2/results/reproduce_experiment_2.py
- outputs/20260227_174458_experiment_2/results/activity_log.jsonl
- outputs/20260227_174458_experiment_2/results/comparison_report.md

# Risks/assumptions
- Galaxy queue/runtime can vary; polling and fallback are needed.
- Metric fields can differ by output format; extraction uses robust JSON/text parsing.
- Parameter bounds must match tool constraints (e.g., learning rate minimum).
