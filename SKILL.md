---
name: galaxy-benchmark-executor
description: Execute Galaxy benchmark experiments from experiments/*.json with strict traceability, output boundaries, logging, and failure-recovery requirements.
metadata:
  short-description: Run Galaxy benchmark experiment(s)
---

# Galaxy Benchmark Executor

Use this skill to run one or more benchmark experiments in this repository with full auditability.

## When To Use

Use this skill when the user asks to:
- run a benchmark experiment in `experiments/`
- execute experiment 1/2/3 (or any future experiment file)
- generate benchmark outputs and compare to ground truth

## Required Inputs

- Experiment definitions in `experiments/*.json`
- Galaxy API key in root `.env` as `GALAXY_API_KEY`
- Ground truth files in `ground_truth/*.json` (read only after result generation)

## Non-Negotiable Rules

1. Write boundary:
- Only write inside `outputs/`.
- Never create, modify, move, rename, or delete files outside `outputs/`.

2. Run directory naming:
- Use `outputs/<date_time>_<experiment_name>/`.
- Recommended timestamp format: `YYYYMMDD_HHMMSS`.
- Every new run/attempt must use a new directory.

3. Credential check:
- `GALAXY_API_KEY` must exist and be non-empty in `.env` before any Galaxy call.
- If missing, stop with:
  - `Missing required credential: GALAXY_API_KEY in .env. Provide this key before running Galaxy API tasks.`

4. Ground truth gate:
- Do not read `ground_truth/<experiment>.json` until both are complete:
  - `results/result.json`
  - `results/reproduce_<experiment_name>.py`

5. Secret handling:
- Never print/log/expose API keys in artifacts, output, or command traces.

6. Traceability:
- Every meaningful action and decision must be logged.
- If it is not logged, it is treated as not performed.

7. Immutability:
- Do not overwrite prior run artifacts.
- Corrections must be new versioned artifacts (for example `result.attempt_2.json`).

## Required Output Structure

For each experiment run, create:
- `outputs/<date_time>_<experiment_name>/plan/saved.md`
- `outputs/<date_time>_<experiment_name>/reasoning/reasoning.md`
- `outputs/<date_time>_<experiment_name>/errors/error.json`
- `outputs/<date_time>_<experiment_name>/results/result.json`
- `outputs/<date_time>_<experiment_name>/results/reproduce_<experiment_name>.py`
- `outputs/<date_time>_<experiment_name>/results/activity_log.jsonl`

Optional/additional artifacts must live under `results/`.

## Execution Workflow (Per Experiment)

1. Read `experiments/<experiment>.json`.
2. Create run directory and required subfolders (`plan`, `reasoning`, `errors`, `results`).
3. Write initial plan to `plan/saved.md` before execution starts.
4. Initialize `errors/error.json` with `run_status=running`.
5. Append planned actions to `results/activity_log.jsonl` (category `plan`).
6. Execute tasks from experiment prompt in order.
7. Continuously log:
- execution actions (`execute`)
- polling/validation checks (`check`)
- retries (`retry`)
- changes between attempts (`revise`)
8. Fill `results/result.json` using `experiment_outputs` schema from the experiment file.
9. Write `results/reproduce_<experiment_name>.py` with reproducible CLI/API steps and annotations.
10. Read matching ground truth and generate comparison table report.
11. Mark `errors/error.json` final `run_status` as one of:
- `completed`
- `completed_with_errors`
- `failed`

## Logging Requirements

### plan/saved.md

Include:
- Experiment name
- Initial objective
- Inputs and datasets
- Ordered plan
- Expected outputs
- Risks/assumptions

### reasoning/reasoning.md

Chronological entries with:
- Timestamp
- Step reference
- Decision made
- Why that decision was made
- Next action

Must include decision-level detail for:
- tool/workflow discovery
- accepted/rejected alternatives
- interface choice (for example BioBlend vs direct API)
- parameter mapping rationale
- evidence references (IDs, responses, artifacts)
- failure interpretation and fix strategy

### errors/error.json

Use this envelope:

```json
{
  "experiment_name": "experiment_1",
  "run_status": "running",
  "started_at": "2026-02-26T12:00:00Z",
  "updated_at": "2026-02-26T12:00:00Z",
  "summary": {
    "total_errors": 0,
    "open_errors": 0,
    "resolved_errors": 0
  },
  "errors": []
}
```

Rules:
- Keep valid JSON at all times.
- Keep `errors` as an array.
- Update `summary` counts whenever errors change.
- Use `context` and `additional_data` for variable details.

### results/activity_log.jsonl

One JSON object per line, append-only, chronological.

Required categories:
- `plan`
- `execute`
- `check`
- `retry`
- `revise`

Example:

```json
{"timestamp":"2026-02-26T12:10:00Z","step":"tool_run","category":"execute","action":"Run Tabular Learner","status":"started","details":{"tool_id":"tabular_learner","history_id":"abc123"}}
```

## Galaxy Polling Policy

After launching any Galaxy job/workflow:
1. Immediately capture IDs (job ID and invocation ID if applicable).
2. First status check after 15-30 seconds.
3. If non-terminal, poll every 1 minute.
4. Stop polling at terminal state (`ok`, `error`, `failed`, `deleted`, or equivalent).
5. Do not run downstream dependent steps before upstream terminal completion.

## Failure Recovery Protocol (Mandatory)

For every failed attempt:
1. Read concrete evidence first:
- stderr/stdout
- traceback text
- exit code/state
- failed outputs/provenance
2. Record normalized error signature:
- error type + core message + failing step/tool + exit code/state
3. Record root cause in `reasoning/reasoning.md` with evidence references.
4. Define a signature-specific fix strategy before retrying.
5. Log recovery actions in `activity_log.jsonl`:
- `check` (evidence review)
- `revise` (what changed and why)
- `retry` (new attempt start)
- `execute` (rerun actions)
6. If the same signature repeats, do not blind-retry. Change mechanism/tool/interface/input mapping or stop with documented blocker.

## Comparison Report Format

Use this table format:

| Field | Agent Result | Ground Truth | Match Status | Notes |
|---|---|---|---|---|
| tool_name | ... | ... | match/mismatch | ... |
| target | ... | ... | match/mismatch | ... |
| ROC-AUC | ... | ... | match/mismatch | ... |

## Completion Checklist

Before considering a run complete, verify:
- All required output files exist.
- `result.json` matches experiment `experiment_outputs` schema.
- `reproduce_<experiment>.py` is present and executable/readable.
- `activity_log.jsonl` covers planning, execution, checks, and retries/revisions.
- Ground truth comparison report exists.
- `errors/error.json` has final status and accurate summary counts.

## Hard Stop Conditions

Stop and report blocker if:
- writing outside `outputs/` would be required
- `GALAXY_API_KEY` is missing/empty
- required upstream Galaxy job never reaches terminal state and no safe fallback exists
- a repeated failure signature persists without a justified mechanism change
