# Experiment name
experiment_2

# Initial objective
Create a new Galaxy history, upload the provided image metadata CSV and image ZIP, train Image Learner models for skin-lesion classification, evaluate on test data, and report the best test accuracy.

# Inputs and datasets
- selected_HAM10000_img_metadata_aug.csv: https://zenodo.org/records/18394055/files/selected_HAM10000_img_metadata_aug.csv
- skin_image.zip: https://zenodo.org/records/18394055/files/skin_image.zip
- Galaxy instance: https://usegalaxy.org/
- Galaxy history name: experiment_2

# Planned steps
1. Validate `GALAXY_API_KEY` from `.env` and initialize BioBlend client.
2. Discover `Image Learner` tool candidates and select the latest stable tool version.
3. Retrieve tool input schema to map required training/test/target parameters.
4. Create Galaxy history `experiment_2` and upload both URL-based datasets.
5. Run at least 5 attempts with different architectures/parameters while avoiding data leakage.
6. Poll each job until terminal state and log checks/retries.
7. Extract test accuracy from each attempt report and pick the best run.
8. Write `results/result.json` and `results/reproduce_experiment_2.py`.
9. Read `ground_truth/experiment_2.json` only after writing results, then generate comparison table.

# Expected outputs
- outputs/20260226_233043_experiment_2/results/result.json
- outputs/20260226_233043_experiment_2/results/reproduce_experiment_2.py
- outputs/20260226_233043_experiment_2/results/activity_log.jsonl
- outputs/20260226_233043_experiment_2/results/comparison_report.md

# Risks/assumptions
- Image Learner runtime may be long and variable.
- Tool parameter schema can vary across versions.
- Accuracy extraction may require parsing HTML/JSON report artifacts.
