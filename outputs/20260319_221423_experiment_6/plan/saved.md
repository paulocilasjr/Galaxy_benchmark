# Experiment Plan

- Experiment name: experiment_6
- Initial objective: Execute the GTN single-cell RNA-seq Scanpy workflow on the provided Matrix Market PBMC 3k inputs and capture the normalization method, workflow tool-step count, and dotplot marker-gene list.
- Inputs and datasets:
  - experiments/experiment_6.json
  - https://zenodo.org/record/3581213/files/barcodes.tsv
  - https://zenodo.org/record/3581213/files/genes.tsv
  - https://zenodo.org/record/3581213/files/matrix.mtx
- Planned steps:
  1. Validate GALAXY_API_KEY from .env for authenticated Galaxy API calls.
  2. Reconstruct pre-run discovery evidence that selected the GTN workflow source and usegalaxy.org execution server.
  3. Create a fresh Galaxy history for attempt 1 and fetch the three remote inputs by URL.
  4. Download the published GTN workflow export, import it into usegalaxy.org, and invoke it with inputs_by=name.
  5. Poll Galaxy invocation/history status until terminal completion or a documented failure.
  6. If attempt 1 fails, analyze the concrete error signature and retry with the documented native usegalaxy.org published fallback workflow.
  7. Capture workflow export, history contents, and key visualization outputs (dotplot and UMAP plots).
  8. Write results/result.json and keep this reproduce_experiment_6.py script as the executable reproduction artifact.
  9. Only after result.json exists, read ground_truth/experiment_6.json and write comparison_report.md.
- Expected outputs:
  - outputs/<timestamp>_experiment_6/plan/saved.md
  - outputs/<timestamp>_experiment_6/reasoning/reasoning.md
  - outputs/<timestamp>_experiment_6/errors/error.json
  - outputs/<timestamp>_experiment_6/results/result.json
  - outputs/<timestamp>_experiment_6/results/reproduce_experiment_6.py
  - outputs/<timestamp>_experiment_6/results/activity_log.jsonl
- Risks/assumptions:
  - The local shell trust store rejects some remote TLS chains, so authenticated requests use verify=False as an environment workaround rather than a workflow choice.
  - usegalaxy.eu hosts the exact GTN workflow but the current API key is not valid there, so the workflow must be exported and imported into usegalaxy.org.
  - Galaxy queue time can be significant; polling follows the benchmark's 15-30 second first check and 1 minute subsequent interval.
