# Experiment name
experiment_7

# Initial objective
Execute the metagenomic genes catalogue workflow that matches the experiment_7 prompt on Galaxy, produce all required benchmark artifacts, and extract the mapper, pipeline step count, and assembly tool from the executed workflow version.

# Inputs and datasets
- Experiment definition: /Users/4475918/Projects/Galaxy_benchmark/experiments/experiment_7.json
- meta_genomic_R1.fastqsanger.gz -> /Users/4475918/Projects/Galaxy_benchmark/dataset/experiment_7/meta_genomics_R1.fastqsanger.gz
- meta_genomic_R2.fastqsanger.gz -> /Users/4475918/Projects/Galaxy_benchmark/dataset/experiment_7/meta_genomics_R2.fastqsanger.gz
- Workflow source candidate: https://workflowhub.eu/workflows/2024?version=4
- Pinned workflow export: https://raw.githubusercontent.com/iwc-workflows/metagenomic-genes-catalogue/c5bb240/metagenomic-genes-catalogue.ga

# Planned steps
1. Validate the experiment definition and resolve the local FASTQ inputs referenced by the prompt.
2. Download and save the pinned workflow export matching the prompt.
3. Create a fresh Galaxy history on usegalaxy.org for this benchmark run.
4. Upload the paired FASTQ files and build the required list:paired collection.
5. Import the pinned workflow into the authenticated Galaxy account.
6. Invoke the workflow with the resolved inputs and benchmark-documented parameter values.
7. Poll Galaxy until the workflow reaches a terminal state, then capture history and invocation evidence.
8. Extract the requested output fields from the workflow definition used for the run and write result.json.
9. Write the reproduction script before reading ground truth.
10. Read ground truth and write a comparison report table.
11. Record the prior attempt failure signature and the retry fix before re-launching Galaxy actions.

# Expected outputs
- results/result.json
- results/reproduce_experiment_7.py
- results/activity_log.jsonl
- results/workflow_export.json
- results/history_contents.json
- results/comparison.md

# Risks/assumptions
- The prompt paths point to ./dataset/meta_genomic_*.fastqsanger.gz, but the repository stores experiment_7 reads under dataset/experiment_7/meta_genomics_*.fastqsanger.gz; this run resolves to the existing local files and records the discrepancy.
- The prompt does not specify the boolean branch value. This run uses the source-published workflow test configuration with Full genes catalogue=false because it is the only explicit upstream runnable parameterization for the pinned workflow version.
- The pipeline step count is reported as execution steps excluding workflow inputs and parameter-input controls, while supplementary metadata will preserve the other step-count views for auditability.
- A previous attempt in outputs/20260321_015411_experiment_7 failed at MMseqs2 taxonomy because the prefilter step was OOM-killed on usegalaxy.org. This retry keeps the same workflow and database but increases MMseqs2 prefilter splitting to reduce memory pressure.
