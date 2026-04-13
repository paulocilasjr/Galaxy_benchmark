# Publication Results Summary

This file is a release-facing summary artifact that intentionally excludes field-level ground-truth tables.
It may cite historical run identifiers even when the underlying `outputs/` directories are no longer shipped in the repository.

## Coverage

- Benchmark instances: 33
- Scored instances: 7
- Missing instances: 26

## Aggregate Scores

| Score | N | Mean | Stddev | 95% CI |
|---|---:|---:|---:|---:|
| galaxy_execution_score | 8 | 0.943 | 0.070 | 0.895 to 0.992 |
| scientific_solution_score | 8 | 0.958 | 0.118 | 0.877 to 1.040 |

## Baseline Inventory

| Baseline | Status | Description |
|---|---|---|
| transparent_heuristic_baseline | protocol_defined | Transparent benchmark-specific heuristic or rules baseline for paper tables. |
| strong_general_agent_baseline | protocol_defined | Strong general-purpose agent baseline executed under the canonical Galaxy protocol. |
| primary_system_under_study | release_specific | Primary agent or executor configuration evaluated in the publication. |

