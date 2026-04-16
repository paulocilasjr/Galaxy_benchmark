# Execution Trace Contract

Galaxy Benchmark v0.3 requires a lossless execution trace.

## A run is only benchmark-valid if it preserves:

- initial plan
- evolving reasoning
- every executed action
- every check or poll
- every retry and revision
- all important Galaxy identifiers
- failure evidence
- attempt-specific outputs
- final evaluation artifacts

## Minimum required directories

- `plan/`
- `reasoning/`
- `errors/`
- `traces/`
- `evaluations/`
- `results/`

## Minimum required files

- `plan/saved.md`
- `reasoning/reasoning.md`
- `errors/error.json`
- `results/activity_log.jsonl`
- `results/result.json`
- `results/run_record.json`
- `results/artifacts_manifest.json`
- `results/evaluation_manifest.json`
- `results/reproduce_<experiment>.py`
- `evaluations/comparison.scored.md`
- `evaluations/field_comparisons.json`
- `evaluations/score_summary.json`

## Immutability rules

- do not delete prior attempt artifacts
- do not overwrite prior attempt artifacts
- retries create new versioned files
- logs are append-only

## If an action mattered but no artifact preserves it:

That action should be treated as non-creditable for benchmark purposes.
