# Plan for bioagent_task_1_alzheimer-mouse

- Experiment name: bioagent_task_1_alzheimer-mouse
- Initial objective: Run the BioAgent alzheimer-mouse task in Galaxy, producing the requested pathway CSV and benchmark run artifacts.
- Inputs and datasets: experiments/BioAgent/task_1/description.json; remote dataset https://osf.io/download/68b20d383e0a583200f9906f/
- Ordered plan:
  1. Fetch and inspect the task dataset bundle.
  2. Determine the minimal valid Galaxy-native analysis path from the input structure.
  3. Create a Galaxy history and upload the required inputs.
  4. Execute the analysis in Galaxy, monitoring jobs and capturing IDs and outputs.
  5. Extract the requested CSV, write result artifacts, then score against ground truth.
- Expected outputs: results/result.json; results/reproduce_bioagent_task_1_alzheimer-mouse.py; results/activity_log.jsonl; results/comparison.md
- Risks/assumptions: BioAgent tasks are not wired into the native workbench; execution will follow the benchmark protocol manually. Input format may constrain the exact Galaxy tool chain. External resources such as KEGG-capable tooling on usegalaxy.org may vary.
