# BixBench task 1 execution plan

## Objective

Execute the `experiments/BixBench/task_1.json` differential expression task in Galaxy using DESeq2, compare the full six-sample analysis against a reduced four-sample analysis excluding `KL3` and `WL3`, and evaluate the result against `ground_truth/BixBench/task_1.json`.

## Input datasets

- Task definition: `experiments/BixBench/task_1.json`
- Ground truth: `ground_truth/BixBench/task_1.json`
- Count matrix URL: `https://zenodo.org/records/14063261/files/count.csv`

## Intended workflow steps

1. Download the original count matrix from the task dataset URL.
2. Split the wide matrix into per-sample two-column count tables under the run directory for auditable preprocessing.
3. Create sample sheets for the full and replicate-filtered comparisons.
4. Create a new Galaxy history and upload the derived inputs.
5. Run Galaxy `DESeq2` once for `KL1-3` vs `WL1-3`.
6. Run Galaxy `DESeq2` again for `KL1-2` vs `WL1-2`.
7. Download the Galaxy DESeq2 result tables and supporting outputs.
8. Count genes meeting `p < 0.05`, `|log2FC| > 1`, and `baseMean > 10`.
9. Determine whether excluding the third replicates increases, decreases, or does not change the DEG count.
10. Compare the direction result against the BixBench ground truth artifact and write evaluation outputs.

## Intended tool choices

- Galaxy tool: `toolshed.g2.bx.psu.edu/repos/iuc/deseq2/deseq2/2.11.40.8+galaxy2`
- Galaxy history uploads via API
- Local deterministic preprocessing only for matrix splitting and result summarization

## Expected result files

- `results/result.json`
- `results/result.attempt_1.json`
- `results/derived_helpers/bixbench_task_1_direction_summary.csv`
- downloaded Galaxy DESeq2 outputs under `results/original_galaxy_outputs/`
- `evaluations/comparison.json`
- `evaluations/comparison.attempt_1.json`
- `evaluations/metrics_summary.json`

## Anticipated risks

- Galaxy DESeq2 sample-sheet payload shape may require one retry if a parameter key is wrong.
- The Galaxy wrapper does not expose a separate top-level shrinkage toggle in the API schema; this run assumes the standard DESeq2 result table produced by the wrapper is the appropriate Galaxy output for the prompt.
- The ground truth JSON appears partially inconsistent for this task, so comparison should rely on the explicit `ideal` field rather than the unrelated free-text `result` field.
