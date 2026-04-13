# Reporting Requirements

The reporting layer should emit:

## Per-run outputs
- run record JSON
- component scores
- performance score
- execution mode and publication-eligibility flags
- normalized execution context for Galaxy provenance
- trace references
- artifacts manifest

## Per-task outputs
- prompt-level performance table
- environment comparison
- robustness score
- failure analysis

## Per-agent outputs
- overall performance
- robustness by environment
- adaptability to Galaxy
- adaptability to Skills
- user-level confidence
- performance by complexity tier

## Suggested report files
- `benchmark_summary.json`
- `per_agent_summary.json`
- `per_task_summary.json`
- `per_run_records.jsonl`
