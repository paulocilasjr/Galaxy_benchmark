# Task Score Recalculation

This file recalculates the scores for the runs currently present under `outputs/` using the project's current score definitions from [docs/formal_score_model.md](/Users/4475918/Projects/Galaxy_benchmark/docs/formal_score_model.md:1).

## Scope

Runs reviewed:

- `outputs/20260413_004047_bioagent_task_1_alzheimer-mouse`
- `outputs/20260413_140010_bioagent_task_2_comparative-genomics`
- `outputs/20260413_230446_bioagent_task_3_cystic-fibrosis`
- `outputs/20260414_012109_bioagent_task_4_deseq`

## Important Caveat

These BioAgent legacy runs do not have the current hidden evaluator schema with:

- `score_model`
- `tier_specific_expectations`
- field-level weighted rules in `galaxy_benchmark_ground_truth_v2`

The old hidden task files in `ground_truth/BioAgent/task_*.json` only specify the expected output shape. Because of that, these are not official scorer outputs from [tools/benchmark_scorer.py](/Users/4475918/Projects/Galaxy_benchmark/tools/benchmark_scorer.py:1). They are a project-aligned fallback recalculation from the available run artifacts.

## Fallback Calculation Rules

### 1. `scientific_solution_score`

Calculated as the mean of observable scientific comparison checks from the run's comparison artifact.

For legacy comparison rows:

- `match = 1.0`
- `partial = 0.5`
- `mismatch = 0.0`
- `missing = 0.0`
- `not_applicable` is excluded

Formula:

`scientific_solution_score = sum(scientific_check_scores) / number_of_applicable_scientific_checks`

### 2. `standard_analysis_score`

The project definition says this score should only use explicit standard-path constraints. The BioAgent legacy task files do not contain prompt-tier metadata or `tier_specific_expectations`, so this score is treated as:

- `not_applicable`

for all legacy BioAgent runs in `outputs/`.

### 3. `galaxy_execution_score`

Calculated from Galaxy-operational evidence and auditability, using current project concepts:

- `galaxy_instance` valid when explicitly reported as `https://usegalaxy.org/`
- `history_id` present
- `history_input_mode` present
- `adaptation_summary` present and valid
- `final_entity_name` present
- core artifact fraction over:
  - `plan/saved.md`
  - `reasoning/reasoning.md`
  - `errors/error.json`
  - `results/result.json`
  - `results/activity_log.jsonl`
  - `results/reproduce_<experiment>.py`
- activity-log category fraction over required categories
- valid benchmark error envelope in `errors/error.json`

Weights:

- direct Galaxy fields: weight `1.0` each
- auditability fractions and error-envelope checks: weight `0.75` each

Formula:

`galaxy_execution_score = sum(check_score * check_weight) / sum(check_weight)`

### 4. Status Thresholds

Project thresholds:

- `pass >= 0.85`
- `partial >= 0.50 and < 0.85`
- `fail < 0.50`
- `not_applicable` when there is no meaningful score basis

## Per-Task Calculations

### Task 1: Alzheimer Mouse

Run:
- `outputs/20260413_004047_bioagent_task_1_alzheimer-mouse`

Scientific evidence source:
- [comparison.md](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_004047_bioagent_task_1_alzheimer-mouse/results/01_final/comparison.md)

Scientific checks:

| Check | Legacy status | Numeric score |
|---|---:|---:|
| `scientific_answer.output_file` | match | 1.0 |
| `scientific_answer.pathway_rows` | match | 1.0 |
| `scientific_answer.matched_reference_rows` | partial | 0.5 |
| `scientific_answer.5xFAD_pvalue` | partial | 0.5 |
| `scientific_answer.3xTG_AD_pvalue` | partial | 0.5 |
| `scientific_answer.PS3O1S_pvalue` | mismatch | 0.0 |

Scientific calculation:

`(1.0 + 1.0 + 0.5 + 0.5 + 0.5 + 0.0) / 6 = 0.5833`

Galaxy execution checks:

| Check | Score | Weight | Weighted contribution |
|---|---:|---:|---:|
| valid `galaxy_instance` | 1.0 | 1.0 | 1.0000 |
| present `history_id` | 1.0 | 1.0 | 1.0000 |
| present `final_entity_name` | 1.0 | 1.0 | 1.0000 |
| core artifact fraction `5/6` | 0.8333 | 0.75 | 0.6250 |
| activity categories fraction `5/5` | 1.0 | 0.75 | 0.7500 |
| valid error envelope | 1.0 | 0.75 | 0.7500 |

Galaxy execution calculation:

`(1.0000 + 1.0000 + 1.0000 + 0.6250 + 0.7500 + 0.7500) / (1.0 + 1.0 + 1.0 + 0.75 + 0.75 + 0.75) = 5.1250 / 5.25 = 0.9762`

Task 1 recalculated scores:

| Score | Value | Status |
|---|---:|---|
| `scientific_solution_score` | `0.5833` | `partial` |
| `standard_analysis_score` | `not_applicable` | `not_applicable` |
| `galaxy_execution_score` | `0.9762` | `pass` |

### Task 2: Comparative Genomics

Run:
- `outputs/20260413_140010_bioagent_task_2_comparative-genomics`

Scientific evidence source:
- [comparison.scored.md](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_140010_bioagent_task_2_comparative-genomics/results/comparison.scored.md)

Scientific checks:

| Check | Legacy status | Numeric score |
|---|---:|---:|
| `scientific_answer.output_csv` | partial | 0.5 |
| `scientific_answer.cluster_count` | mismatch | 0.0 |
| `scientific_answer.exact_annotation_overlap_count` | mismatch | 0.0 |

Scientific calculation:

`(0.5 + 0.0 + 0.0) / 3 = 0.1667`

Galaxy execution checks:

| Check | Score | Weight | Weighted contribution |
|---|---:|---:|---:|
| valid `galaxy_instance` | 1.0 | 1.0 | 1.0000 |
| present `history_id` | 1.0 | 1.0 | 1.0000 |
| present `history_input_mode` | 1.0 | 1.0 | 1.0000 |
| present `adaptation_summary` | 1.0 | 1.0 | 1.0000 |
| present `final_entity_name` | 1.0 | 1.0 | 1.0000 |
| core artifact fraction `6/6` | 1.0 | 0.75 | 0.7500 |
| activity categories fraction `5/5` | 1.0 | 0.75 | 0.7500 |
| valid error envelope | 1.0 | 0.75 | 0.7500 |

Galaxy execution calculation:

`(1 + 1 + 1 + 1 + 1 + 0.75 + 0.75 + 0.75) / (1 + 1 + 1 + 1 + 1 + 0.75 + 0.75 + 0.75) = 1.0000`

Task 2 recalculated scores:

| Score | Value | Status |
|---|---:|---|
| `scientific_solution_score` | `0.1667` | `fail` |
| `standard_analysis_score` | `not_applicable` | `not_applicable` |
| `galaxy_execution_score` | `1.0000` | `pass` |

Note:
- There is also a non-canonical truth-informed rerun under the same directory, but the calculation above is for the primary `results/result.json` and `results/comparison.scored.md` outputs.

### Task 3: Cystic Fibrosis

Run:
- `outputs/20260413_230446_bioagent_task_3_cystic-fibrosis`

Scientific evidence source:
- [comparison.scored.md](/Users/4475918/Projects/Galaxy_benchmark/outputs/20260413_230446_bioagent_task_3_cystic-fibrosis/results/comparison.scored.md)

Scientific checks:

There are 16 reported scientific fields in the comparison table, and all 16 are marked `match`.

Scientific calculation:

`16 / 16 = 1.0000`

Galaxy execution checks:

| Check | Score | Weight | Weighted contribution |
|---|---:|---:|---:|
| present `history_id` | 1.0 | 1.0 | 1.0000 |
| present `history_input_mode` | 1.0 | 1.0 | 1.0000 |
| present `adaptation_summary` | 1.0 | 1.0 | 1.0000 |
| present `final_entity_name` | 1.0 | 1.0 | 1.0000 |
| core artifact fraction `6/6` | 1.0 | 0.75 | 0.7500 |
| activity categories fraction `5/5` | 1.0 | 0.75 | 0.7500 |
| valid error envelope | 1.0 | 0.75 | 0.7500 |

Galaxy execution calculation:

`(1 + 1 + 1 + 1 + 0.75 + 0.75 + 0.75) / (1 + 1 + 1 + 1 + 0.75 + 0.75 + 0.75) = 1.0000`

Task 3 recalculated scores:

| Score | Value | Status |
|---|---:|---|
| `scientific_solution_score` | `1.0000` | `pass` |
| `standard_analysis_score` | `not_applicable` | `not_applicable` |
| `galaxy_execution_score` | `1.0000` | `pass` |

### Task 4: DESeq

Run:
- `outputs/20260414_012109_bioagent_task_4_deseq`

Current state:

- `errors/error.json` reports `run_status = running`
- there is no final `results/result.json`
- there is no scored comparison artifact
- there is no scientific output to compare against ground truth yet

Task 4 recalculated scores:

| Score | Value | Status |
|---|---:|---|
| `scientific_solution_score` | `not_applicable` | `not_applicable` |
| `standard_analysis_score` | `not_applicable` | `not_applicable` |
| `galaxy_execution_score` | `not_applicable` | `not_applicable` |

## Summary Table

| Task | Scientific | Standard | Galaxy Execution |
|---|---:|---:|---:|
| Alzheimer mouse | `0.5833` `partial` | `not_applicable` | `0.9762` `pass` |
| Comparative genomics | `0.1667` `fail` | `not_applicable` | `1.0000` `pass` |
| Cystic fibrosis | `1.0000` `pass` | `not_applicable` | `1.0000` `pass` |
| DESeq | `not_applicable` | `not_applicable` | `not_applicable` |

## Interpretation

Using the current project definition:

- the old BioAgent runs do support recalculation of `scientific_solution_score`
- they do support recalculation of `galaxy_execution_score`
- they do not support a defensible `standard_analysis_score` because explicit standard-path constraints are not encoded in the legacy hidden task files

This is why the recalculated scores differ from the older ad hoc score summaries already stored inside some run directories.
