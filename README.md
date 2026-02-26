# Galaxy Benchmark

This README is the execution guide for an agent running the Galaxy Benchmark.

## Objective
For each experiment in `experiments/`, execute the task, produce a structured result, and compare it to the ground truth only after result generation is complete.

## Run Entrypoint (No Command)
To start a benchmark run:
1. Open the `experiments/` directory.
2. Read the experiment files one by one.
3. Execute one experiment at a time from start to finish (do not mix steps from multiple experiments).
4. For each experiment, complete all required outputs before moving to the next experiment file.

## Galaxy API Prerequisite
Before starting any Galaxy action, validate API credentials:

- The Galaxy API key must be available in the root `.env` file as `GALAXY_API_KEY`.
- The key must be non-empty.
- If `GALAXY_API_KEY` is missing or empty, stop execution and report a blocking issue so the user can provide it.

Recommended blocking message:
- `Missing required credential: GALAXY_API_KEY in .env. Provide this key before running Galaxy API tasks.`

## Input Directory
- `experiments/`
  - Contains experiment JSON files with instructions and an `experiment_outputs` structure to fill.

## Required Output Structure
For each experiment file (example: `experiment_1.json`), create:

- `outputs/<date_time>_<experiment_name>/plan/saved.md`
- `outputs/<date_time>_<experiment_name>/reasoning/reasoning.md`
- `outputs/<date_time>_<experiment_name>/errors/error.json`
- `outputs/<date_time>_<experiment_name>/results/result.json`
- `outputs/<date_time>_<experiment_name>/results/reproduce_<experiment_name>.py`
- `outputs/<date_time>_<experiment_name>/results/activity_log.jsonl`

Notes:
- The run directory inside `outputs/` must be named as `<date_time>_<experiment_name>`.
- Use a sortable timestamp format for `<date_time>` (recommended: `YYYYMMDD_HHMMSS`).
- Example for `experiment_1`: `outputs/20260226_153000_experiment_1/`.
- Each new run/attempt must use a new `<date_time>_<experiment_name>` directory to avoid overwriting previous runs.
- The result JSON must follow the structure defined in `experiment_outputs` in the experiment file.
- `results/reproduce_<name_of_experiment>.py` must reproduce all benchmark actions through command-line steps and include comments/annotations that explain each step for a human reader.
- Any additional artifact not explicitly part of `plan/`, `reasoning/`, or `errors/` must be written in `results/`.
- `results/activity_log.jsonl` is mandatory and must contain a chronological categorical record of all planned, executed, checked, and retried actions.

## Execution Steps (Per Experiment)
1. Read the experiment JSON file from `experiments/`.
2. Create a run-specific experiment directory in `outputs/` named `<date_time>_<experiment_name>` and create subdirectories:
   - `plan/`
   - `reasoning/`
   - `errors/`
   - `results/`
3. Before execution starts, write the initial plan in `plan/saved.md`.
4. Execute the experiment tasks exactly as instructed.
5. Log ongoing reasoning and decision process in `reasoning/reasoning.md`.
6. Log all errors/status issues in `errors/error.json` throughout execution.
7. Continuously append categorical records to `results/activity_log.jsonl` for every planned, executed, checked, and retried action.
8. Fill `results/result.json` using `experiment_outputs` as the template.
9. Create `results/reproduce_<name_of_experiment>.py` with annotated, step-by-step CLI reproduction instructions for everything the agent executed.
10. Only after steps 8 and 9 are complete, read the matching ground truth file.
11. Build a comparison report table between `results/result.json` and ground truth using this format:

| Field | Agent Result | Ground Truth | Match Status | Notes |
|---|---|---|---|---|
| tool_name | ... | ... | match/mismatch | ... |
| target | ... | ... | match/mismatch | ... |
| roc-auc | ... | ... | match/mismatch | ... |

Use this table as the primary benchmark analysis instead of a single aggregate score.

## Logging Format (Flexible but Structured)
The benchmark requires logs in `plan/`, `reasoning/`, and `errors/`. Use the following format rules to keep logs easy to read while allowing flexibility.

### plan/saved.md
Use this structure:
- Experiment name
- Initial objective
- Inputs and datasets
- Planned steps (ordered list)
- Expected outputs
- Risks/assumptions

### reasoning/reasoning.md
Log chronological reasoning entries with:
- Timestamp
- Step reference
- Decision made
- Why this decision was made
- Next action

Reasoning entries must also capture decision-critical technical details:
- Tool discovery method (how available Galaxy tools/workflows were retrieved).
- Candidate tools considered and why each was accepted or rejected.
- Interface choice for execution (for example `BioBlend` vs direct Galaxy API calls), including rationale and tradeoffs.
- Parameter-selection rationale (how parameter values were chosen from experiment instructions and tool metadata).
- Evidence used for decisions (tool IDs, API responses, history/dataset IDs, validation checks).
- Any assumption or constraint that changes execution strategy.

If it affected execution decisions, it must be recorded in `reasoning/reasoning.md`.

### errors/error.json
Use a structured JSON envelope with flexible context fields. Keep required keys stable and store variable details under `context` and `additional_data`.

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
  "errors": [
    {
      "id": "err-0001",
      "timestamp": "2026-02-26T12:10:00Z",
      "step": "tool_run",
      "phase": "execution",
      "severity": "error",
      "category": "tool",
      "status": "open",
      "message": "Human-readable description of the issue.",
      "job_id": "optional-job-id",
      "invocation_id": "optional-invocation-id",
      "action_taken": "What the agent did after the error.",
      "resolution": "How it was resolved, if resolved.",
      "retry_count": 0,
      "context": {},
      "additional_data": {}
    }
  ]
}
```

Error logging rules:
- Always keep valid JSON.
- Keep `errors` as an array (empty array if no errors occurred).
- Use `context` for variable details (API responses, parameters, paths, traceback snippets).
- Update `summary` counts whenever `errors` entries change.
- Mark final `run_status` as `completed`, `completed_with_errors`, or `failed`.

### results/activity_log.jsonl
This is the single categorical record file for execution history. Append one JSON object per line in chronological order.

Required categories:
- `plan`
- `execute`
- `check`
- `retry`
- `revise`

Record format (one line example):

```json
{"timestamp":"2026-02-26T12:10:00Z","step":"tool_run","category":"execute","action":"Run Tabular Learner","status":"started","details":{"tool_id":"tabular_learner","history_id":"abc123"}}
```

Activity log rules:
- Every planned action must have a `plan` record.
- Every execution action must have an `execute` record.
- Every verification/status polling action must have a `check` record.
- Every retry attempt must have a `retry` record, with reason in `details`.
- Any modification from a previous attempt (script changes, writing/content changes, parameter changes) must be captured as one `revise` record.
- A `revise` record must include, in `details`, at least: `attempt`, `changed_items`, `reason`, and `new_artifact_path`.
- Keep entries append-only; never rewrite history.

Immutability policy:
- Previously written artifacts are immutable. In-place edits or overwrites are not permitted.
- If a correction is needed, create a new versioned artifact instead of editing the old one (example: `results/result.attempt_2.json`, `results/reproduce_experiment_1.attempt_2.py`).
- Never delete or replace prior versions; keep all versions for traceability.

## Galaxy Execution and Polling Rules
Use this status policy for Galaxy tool jobs and workflow invocations:

1. After triggering a tool or workflow, immediately confirm submission and capture IDs (job ID and, if applicable, workflow invocation ID).
2. Perform a first status check after 15-30 seconds to confirm the run has entered a valid non-terminal state (for example `new`, `queued`, or `running`) or reached a terminal state.
3. If still non-terminal, poll every 1 minute.
4. Continue polling every 1 minute until terminal state (`ok`, `error`, `failed`, `deleted`, or equivalent).
5. Do not execute dependent downstream steps until required upstream jobs are terminal and outputs are available.
6. Independent work is allowed while waiting (for example, preparing logs, validating previous outputs, or launching unrelated branches of the workflow).

This replaces a fixed 1-minute cooldown for every action. The 1-minute interval is for active async monitoring, not for blocking all actions.

## Rules to Follow
- Follow experiment instructions in order.
- Do not skip required logs (`plan`, `reasoning`, `errors`, `results`).
- Do not read ground truth before producing the final result JSON.
- Keep outputs deterministic and structured.
- Record failures explicitly in `errors/error.json` instead of silently continuing.
- Apply dependency-aware progression: wait for required Galaxy outputs, but do not idle when independent actions can proceed safely.
- Write-scope restriction (strict): agents may write files only inside `outputs/<date_time>_<experiment_name>/` for the active run. Writing anywhere outside this directory is never allowed.
- Secret handling (strict): never expose the Galaxy API key. Do not print, log, store, echo, or include `GALAXY_API_KEY` in any artifact, report, script output, or command history.
- Recordkeeping (strict): anything planned, executed, checked, or retried must be logged in `results/activity_log.jsonl` with a category tag.
- Immutability (strict): never modify previously written files. Any script/writing/parameter change after a prior attempt must be recorded as a new `revise` entry and written to a new versioned artifact path.
