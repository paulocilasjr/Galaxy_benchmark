- Experiment name: experiment_2
- Initial objective: Train and evaluate an image classification model in Galaxy using provided HAM10000 metadata and image zip, then report best Test ROC-AUC.
- Inputs and datasets:
  - selected_HAM10000_img_metadata_aug.csv (Zenodo URL from experiments/experiment_2.json)
  - skin_image.zip (Zenodo URL from experiments/experiment_2.json)
- Planned steps:
  1. Validate GALAXY_API_KEY in .env.
  2. Discover latest Image Learner tool on usegalaxy.org.
  3. Create history named experiment_2.
  4. Download and upload the two datasets.
  5. Run at least 5 training attempts with different architectures/parameters.
  6. Poll jobs until terminal states and parse output metrics.
  7. Select best attempt by Test ROC-AUC.
  8. Write result.json and reproduce_experiment_2.py.
  9. Read ground truth and write comparison_report.md.
- Expected outputs:
  - results/result.json with tool_name, target, ROC-AUC
  - results/reproduce_experiment_2.py
  - results/activity_log.jsonl
  - results/attempt_summary.json
  - results/comparison_report.md
- Risks/assumptions:
  - Galaxy tool parameter schema may vary by tool version.
  - Dataset upload or job execution may fail/intermittently stall and require retry.
  - Metric names in outputs may differ and require robust parsing.
