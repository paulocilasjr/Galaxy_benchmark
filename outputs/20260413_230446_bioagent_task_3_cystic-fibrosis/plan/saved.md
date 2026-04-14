# BioAgent Task 3: cystic-fibrosis

- Experiment name: `bioagent_task_3_cystic-fibrosis`
- Initial objective: identify the recessive causal variant for cystic fibrosis in the simulated CEPH family sequencing dataset and produce the requested CSV fields.
- Inputs and datasets:
  - Task file: `experiments/BioAgent/task_3/description.json`
  - Dataset bundle URL: `https://osf.io/download/68b20df289a6df6718780c40/`
  - Reference bundle URL: `https://osf.io/download/68345adb08d1077918ab8378/`
- Ordered plan:
  1. Inspect the public task and stage a new Galaxy history for the run.
  2. Download the public dataset and reference assets into this run directory for local inspection only.
  3. Infer the available files and select a Galaxy-native path for variant filtering and annotation.
  4. Upload or remote-fetch the required files into Galaxy.
  5. Execute an initial Galaxy analysis to narrow candidate recessive variants shared by affected siblings.
  6. Extract the first result into `results/result.json` and write `results/reproduce_bioagent_task_3_cystic-fibrosis.py`.
  7. Only then read `ground_truth/BioAgent/task_3.json`, compare field by field, and plan an improved rerun.
  8. Execute an improved attempt and record the final comparison and score summary.
- Expected outputs:
  - `results/result.json`
  - `results/reproduce_bioagent_task_3_cystic-fibrosis.py`
  - comparison report against hidden truth after the first result exists
- Risks and assumptions:
  - The OSF bundles may be compressed archives that require local inspection before choosing Galaxy tools.
  - Family structure and affected status may need to be inferred from filenames or embedded metadata.
  - Galaxy tool availability may require an annotation path different from a local best-practice pipeline.
