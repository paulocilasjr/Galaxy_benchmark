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

## Input Directory
- `experiments/`
  - Contains experiment JSON files with instructions and an `experiment_outputs` structure to fill.

## Required Output Structure
For each experiment file (example: `experiment_1.json`), create:

- `output/experiment_1/plan/saved.md`
- `output/experiment_1/reasoning/reasoning.md`
- `output/experiment_1/errors/error.json`
- `output/experiment_1/results/result.json`
- `output/experiment_1/reproduce_experiment_1.py`

Notes:
- The output directory name must match the experiment JSON filename without extension.
- The result JSON must follow the structure defined in `experiment_outputs` in the experiment file.
- `reproduce_<name_of_experiment>.py` must reproduce all benchmark actions through command-line steps and include comments/annotations that explain each step for a human reader.

## Execution Steps (Per Experiment)
1. Read the experiment JSON file from `experiments/`.
2. Create the experiment output directory in `output/` and create subdirectories:
   - `plan/`
   - `reasoning/`
   - `errors/`
   - `results/`
3. Before execution starts, write the initial plan in `plan/saved.md`.
4. Execute the experiment tasks exactly as instructed.
5. Log ongoing reasoning and decision process in `reasoning/reasoning.md`.
6. Log all errors/status issues in `errors/error.json` throughout execution.
7. Fill `results/result.json` using `experiment_outputs` as the template.
8. Create `reproduce_<name_of_experiment>.py` with annotated, step-by-step CLI reproduction instructions for everything the agent executed.
9. Only after steps 7 and 8 are complete, read the matching ground truth file.
10. Build a comparison report table between `results/result.json` and ground truth using this format:

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
