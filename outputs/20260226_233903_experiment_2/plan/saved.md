# Plan: experiment_2

## Experiment name
experiment_2

## Initial objective
Create a new history in Galaxy and upload the datasets. Train a machine learning model to classify images based on the given training dataset and evaluate its performance on the test dataset.

## Inputs and datasets
- selected_HAM10000_img_metadata_aug.csv: https://zenodo.org/records/18394055/files/selected_HAM10000_img_metadata_aug.csv
- skin_image.zip: https://zenodo.org/records/18394055/files/skin_image.zip

## Must-have requirement
- accuracy must be >= 0.7

## Planned steps
1. Validate Galaxy API credential from .env.
2. Discover Image Learner tool and select latest version.
3. Create Galaxy history named experiment_2.
4. Upload datasets from URLs.
5. Run leakage-safe multiclass image training with target=dx and sample_id=lesion_id.
6. Poll the Galaxy job every 1 minute after the first 15-30s check until terminal.
7. Extract test accuracy from training_progress.json in tool outputs.
8. If accuracy is below threshold, retry once with a stronger model and record revise/retry entries.
9. Write result.json and comparison table after reading ground truth.

## Expected outputs
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260226_233903_experiment_2/results/result.json
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260226_233903_experiment_2/results/activity_log.jsonl
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260226_233903_experiment_2/results/comparison_report.md

## Risks/assumptions
- Shared Galaxy queue/training time is variable.
- Tool output format may vary; extraction prefers training_progress.json payload.
- Leakage control uses sample_id_column=lesion_id to group augmented variants.
