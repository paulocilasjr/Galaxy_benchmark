---
name: galaxy-benchmark-executor
description: Execute Galaxy Benchmark v0.3 runs with immutable trace capture, versioned retries, Galaxy provenance preservation, and post-run evaluation artifacts.
metadata:
  short-description: Run Galaxy benchmark experiment(s) with lossless auditability
---

# Galaxy Benchmark Executor

Use this skill when the task is to execute benchmark experiments in this repository.

## Core Principle

The run is not valid unless a third party can reconstruct:

- what the agent planned
- what it did
- what Galaxy executed
- what failed
- why the agent changed course
- what the final outputs were
- how those outputs were evaluated

If that evidence is not stored in artifacts, it does not count.

## Write Boundary

During execution, only write under:

- `outputs/<timestamp>_<level>_<experiment>/`

Never write benchmark-execution artifacts anywhere else.

## Run Directory Contract

Every run must create:

```text
outputs/<timestamp>_<level>_<experiment>/
|-- plan/
|   |-- saved.md
|   `-- saved.attempt_<N>.md
|-- reasoning/
|   |-- reasoning.md
|   `-- reasoning.attempt_<N>.md
|-- errors/
|   `-- error.json
|-- traces/
|   |-- galaxy/
|   |   |-- histories/
|   |   |-- invocations/
|   |   |-- jobs/
|   |   `-- datasets/
|   `-- local/
|-- evaluations/
|   |-- comparison.scored.md
|   |-- field_comparisons.json
|   `-- score_summary.json
`-- results/
    |-- result.json
    |-- result.attempt_<N>.json
    |-- activity_log.jsonl
    |-- run_record.json
    |-- artifacts_manifest.json
    |-- evaluation_manifest.json
    `-- reproduce_<experiment>.py
```

Optional extra artifacts may be added, but only under these directories.

## Immutability Rules

- `saved.md` is the initial plan and must not be overwritten.
- Every retry must create a new attempt-specific plan and result artifact.
- `reasoning/reasoning.md` is append-only.
- `results/activity_log.jsonl` is append-only.
- Do not replace or delete prior evaluation artifacts.
- If a correction is needed, write a new versioned artifact and update manifests.

## Credential Gate

Before any Galaxy action:

- verify `.env` contains `GALAXY_API_KEY`
- stop if missing or empty

Do not print, log, or persist secret values.

## Required Evidence Capture

### Planning

Record in `plan/`:

- objective
- dataset inventory
- intended analysis path
- expected outputs
- likely risks
- fallback branches

### Reasoning

Record in `reasoning/`:

- tool discovery and selection rationale
- rejected alternatives
- parameter decisions
- preprocessing decisions
- assumptions and uncertainty
- confidence estimate or proxy before major execution milestones
- root-cause analysis after each failure
- fix strategy before each retry

### Activity Log

Append JSONL entries for:

- `plan`
- `execute`
- `check`
- `retry`
- `revise`
- `evaluate`
- `snapshot`

Every record should include relevant IDs, paths, parameters, and outcomes.

### Galaxy Trace Snapshots

Store structured Galaxy evidence under `traces/galaxy/` whenever available:

- history metadata
- job state and provenance
- workflow invocation state
- dataset metadata
- stderr/stdout or equivalent failure messages

If a Galaxy object is important to execution or debugging, snapshot it.

### Evaluation

After result generation is complete:

- write field comparisons
- write score summaries
- write evaluation manifests
- keep comparisons for every attempt if multiple attempts were evaluated

## Failure Recovery Protocol

Never blind-retry.

For every failed attempt:

1. Snapshot the failure evidence.
2. Extract a stable error signature.
3. Record the inferred root cause.
4. Record the fix strategy.
5. Log a `revise` record before launching the retry.
6. Write new attempt artifacts instead of overwriting old ones.

If the same signature repeats:

- do not continue with superficial parameter sweeps
- change the failing mechanism or stop with a documented blocker

## Required Final Files

A benchmark-valid completed run must end with:

- `results/result.json`
- `results/reproduce_<experiment>.py`
- `results/run_record.json`
- `results/artifacts_manifest.json`
- `results/evaluation_manifest.json`
- `results/activity_log.jsonl`
- `evaluations/comparison.scored.md`
- `evaluations/field_comparisons.json`
- `evaluations/score_summary.json`
- `errors/error.json`

## Completion Requirements

Before declaring the run complete, verify:

- required outputs exist
- manifests reference all preserved artifacts
- activity log covers planning, execution, checks, retries, revisions, and evaluation
- Galaxy IDs referenced in result artifacts are preserved in traces
- final `errors/error.json` status is terminal
- no prior attempt artifact was overwritten
