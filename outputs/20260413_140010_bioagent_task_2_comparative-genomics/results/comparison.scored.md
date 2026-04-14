# Comparison Report

Ground truth was read from [ground_truth/BioAgent/task_2.json](/Users/4475918/Projects/Galaxy_benchmark/ground_truth/BioAgent/task_2.json), which points to the OSF bundle extracted at `results/ground_truth_task2/results/cluster_annotation_mapping.csv`.

| Field | Agent Result | Ground Truth | Match Status | Notes |
|---|---|---|---|---|
| scientific_answer.output_csv | `results/comparative_genomics_clusters.csv` | `results/ground_truth_task2/results/cluster_annotation_mapping.csv` | partial | Both are CSV outputs with the expected columns. |
| scientific_answer.cluster_count | 875 | 18 rows / 16 unique annotations | mismatch | The fallback method produced many shared annotations, but not the expected truth set. |
| scientific_answer.exact_annotation_overlap_count | 0 | at least 1 required | mismatch | BioAgent task rule requires at least one exact `consensus_annotation` string overlap. |
| galaxy_execution.blocked_job_id | `bbd44e69cb8906b5a35fb97c2361f2af` | terminal Galaxy completion expected | mismatch | `Roary` never reached a usable terminal output state on `usegalaxy.org`. |

| Score | Value | Status | Basis | Notes |
|---|---|---|---|---|
| scientific_solution_score | 0.0 | fail | exact consensus_annotation overlap | The produced CSV had zero exact overlaps with the 16 unique truth annotations. |
| standard_analysis_score | 0.0 | fail | task-specific expected output semantics | The fallback Prokka-intersection output did not reproduce the expected cluster annotations. |
| galaxy_execution_score | 0.5 | partial | Galaxy run trace | Four uploads and four Prokka runs succeeded; `Roary` stalled indefinitely on `usegalaxy.org`. |
