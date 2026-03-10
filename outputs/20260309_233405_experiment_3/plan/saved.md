- Experiment name: experiment_3
- Initial objective: Train and evaluate a multimodal survival prediction model in Galaxy using HANCOCK train/test CSV files and CD3/CD8 image ZIP, then report best Test ROC-AUC.
- Inputs and datasets:
  - CD3_CD8_images_3GB_jpeg.zip (Zenodo URL from experiments/experiment_3.json)
  - HANCOCK_test_split_3GB_jpeg.csv (Zenodo URL from experiments/experiment_3.json)
  - HANCOCK_train_split_3GB_jpeg.csv (Zenodo URL from experiments/experiment_3.json)
- Planned steps:
  1. Validate GALAXY_API_KEY in .env.
  2. Discover latest Multimodal Learner tool on usegalaxy.org.
  3. Create history named experiment_3.
  4. Upload all required datasets from URL and poll until ready.
  5. Run at least 5 Multimodal Learner attempts with different backbones and training settings.
  6. Poll jobs until terminal states and parse output metrics.
  7. Select best attempt by Test ROC-AUC.
  8. Write result.json and reproduce_experiment_3.py.
  9. Read ground truth and write comparison_report.md.
- Expected outputs:
  - results/result.json with tool_name, target, ROC-AUC
  - results/reproduce_experiment_3.py
  - results/activity_log.jsonl
  - results/attempt_summary.json
  - results/comparison_report.md
- Risks/assumptions:
  - Remote URL dataset import (especially 3GB ZIP) may be slow or intermittently fail.
  - Tool parameter schema may vary by installed tool version.
  - Metric output keys may differ across attempts and require robust parsing.
