# Experiment Plan

## 2026-03-12T22:08:10Z | Primary Execution Plan

- Experiment name: experiment_4
- Initial objective: Run the IWC-validated ATACseq workflow on the provided paired FASTQ files and capture required output evidence.
- Inputs and datasets:
  - experiments/experiment_4.json
  - dataset/experiment_4/forward.fastqsanger.gz
  - dataset/experiment_4/reverse.fastqsanger.gz
- Planned steps:
  1. Validate GALAXY_API_KEY and connect to https://usegalaxy.org/.
  2. Discover/select IWC workflow for ATAC-seq analysis and inspect required inputs.
  3. Create a new Galaxy history and upload both FASTQ files.
  4. Build list:paired collection expected by workflow input step.
  5. Invoke workflow with runtime parameters and poll to completion.
  6. Extract final artifact metadata, input format confirmation, and workflow tool-step count.
  7. Write result.json, reproduce_experiment_4.py, activity_log.jsonl, errors/error.json, and comparison_report.md.
- Expected outputs:
  - outputs/<timestamp>_experiment_4/... required benchmark artifacts
- Risks/assumptions:
  - Workflow runtime depends on Galaxy queueing.
  - Reference genome selection assumes human hg38 with effective genome size 2,700,000,000.

## 2026-03-12T22:41:06Z | Blocker Snapshot Plan

- Experiment name: experiment_4
- Initial objective: Execute IWC-validated ATACseq workflow on provided paired FASTQ files.
- Inputs and datasets:
  - experiments/experiment_4.json
  - dataset/experiment_4/forward.fastqsanger.gz
  - dataset/experiment_4/reverse.fastqsanger.gz
- Planned steps:
  1. Read benchmark instructions and experiment spec.
  2. Discover/select IWC ATACseq workflow.
  3. Upload inputs and create list:paired collection.
  4. Invoke workflow and poll until terminal.
  5. Record outputs and compare with ground truth.
- Expected outputs:
  - required files under outputs/<timestamp>_experiment_4/
- Risks/assumptions:
  - Galaxy queue/runtime may delay or block terminal completion.
