# BioAgent Task 1 Run Guide

This run directory is organized to make the final outcome, the hidden-reference comparison, and the supporting Galaxy analysis artifacts easy to inspect.

## Start Here

- Final benchmark summary: [results/01_final/comparison.md](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/01_final/comparison.md)
- Final score summary: [results/01_final/score_summary.json](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/01_final/score_summary.json)
- Final machine-readable result: [results/01_final/result.json](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/01_final/result.json)
- User prompt history: [user_prompts.md](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/user_prompts.md)
- Completion postmortem: [postmortem.md](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/postmortem.md)

## Final Outputs

- Run-produced pathway table: [results/01_final/final_pathway_pvalues_from_run.csv](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/01_final/final_pathway_pvalues_from_run.csv)
- Row-wise comparison to hidden reference: [results/01_final/final_pathway_comparison_vs_ground_truth.csv](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/01_final/final_pathway_comparison_vs_ground_truth.csv)

## Hidden Reference

- Original hidden reference download: [results/02_reference/ground_truth_task1.csv](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/02_reference/ground_truth_task1.csv)
- Decompressed hidden reference table: [results/02_reference/ground_truth_task1.decompressed.csv](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/02_reference/ground_truth_task1.decompressed.csv)

## Analysis Files

- DESeq2 outputs and DE setup files: [results/03_analysis/deseq2](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/03_analysis/deseq2)
- goseq KEGG outputs and gene-length resources: [results/03_analysis/goseq](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/03_analysis/goseq)

## Inputs

- Original downloaded task bundle and extracted files: [results/04_inputs/original](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/04_inputs/original)
- Prepared DESeq2 and goseq inputs: [results/04_inputs/prepared](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/04_inputs/prepared)
- Derived workaround inputs, including integerized 5xFAD files: [results/04_inputs/derived](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/04_inputs/derived)

## Logs

- Execution log: [results/activity_log.jsonl](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/activity_log.jsonl)
- Plan: [plan/saved.md](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/plan/saved.md)
- Reasoning log: [reasoning/reasoning.md](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/reasoning/reasoning.md)
- Error ledger: [errors/error.json](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/errors/error.json)
- Reproduction script: [results/reproduce_bioagent_task_1_alzheimer-mouse.py](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/reproduce_bioagent_task_1_alzheimer-mouse.py)
