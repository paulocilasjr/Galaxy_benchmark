# Galaxy Benchmark

Galaxy Benchmark is an end-to-end benchmark for evaluating AI agents on real Galaxy-based biomedical and bioinformatics tasks. The repository is organized like a published benchmark release: it exposes task definitions, input data, hidden evaluation references, and a required artifact format for reproducible runs.

This benchmark does not score only final answers. It also evaluates whether a run is auditable and reproducible. Clear reporting is a first-class requirement: if an action, decision, retry, or failure analysis is not recorded in the run artifacts, it is treated as not performed.

`SKILL.md` is the concise executor-oriented companion. `README.md` is the benchmark reference, protocol, and reporting standard.

The explicit three-score formalization for this benchmark is documented in [docs/formal_score_model.md](/Users/4475918/Projects/Galaxy_benchmark/docs/formal_score_model.md).

## Benchmark Summary

- Task groups: 8
- Prompt variants per task: 3 (`low_context`, `medium_context`, `high_context`)
- Total benchmark instances: 24
- Platform: Galaxy (`https://usegalaxy.org/`)
- Output style: structured files under `outputs/`
- Evaluation style: produce results first, then compare against ground truth field by field with an explicit three-score summary

### Task Families

| Experiment | Task family |
|---|---|
| `experiment_1` | Biomedical tabular classification |
| `experiment_2` | Biomedical image classification |
| `experiment_3` | Biomedical multimodal survival prediction |
| `experiment_4` | ATAC-seq workflow execution |
| `experiment_5` | Paired-end RNA-seq workflow |
| `experiment_6` | Single-cell RNA-seq clustering |
| `experiment_7` | Metagenomics gene-catalog pipeline |
| `experiment_8` | Genome annotation and quality evaluation |

### Context Levels

Each task group is released in three prompt tiers with the same inputs and task family but different prompt specificity:

- `low_context`: open-ended task request with minimal procedural guidance
- `medium_context`: clearer task framing, expected metric/output, and methodological hints
- `high_context`: more prescriptive tool, workflow, parameter, or target-column guidance

This structure supports evaluation of instruction following under different context budgets without changing the underlying task.

## Repository Layout

```text
.
|-- README.md
|-- SKILL.md
|-- dataset/
|-- experiments/
|   |-- low_context/
|   |-- medium_context/
|   `-- high_context/
|-- evaluators/
|-- ground_truth/
`-- outputs/
```

### Directory Roles

- `experiments/`: public experiment definitions that agents read and execute
- `dataset/`: benchmark input files referenced by the experiment JSON files
- `evaluators/`: hidden evaluation metadata, rubric details, and benchmark-specific expectations; not part of the agent-facing prompt
- `ground_truth/`: reference answers used only after result generation is complete
- `outputs/`: the only writable location during benchmark execution

## Experiment Format

Each experiment file is a JSON task package. The structure is stable across prompt tiers:

```json
{
  "format_version": "galaxy_benchmark_task_input_v2",
  "task_id": "experiment_1",
  "task_group_id": "experiment_1_response_prediction_prompt_tiers",
  "level": "low_context",
  "task_family": "biomedical_tabular_classification",
  "benchmark_axes": {
    "scientist_level_band": "junior",
    "galaxy_complexity_band": "intermediate",
    "focus_capabilities": [
      "dataset inspection",
      "target identification",
      "Galaxy tool selection",
      "held-out test evaluation"
    ]
  },
  "required_result_format": {
    "format_name": "galaxy_benchmark_result_v2",
    "scientific_answer": {
      "required_fields": [
        "target",
        "primary_metric.name",
        "primary_metric.split",
        "primary_metric.value"
      ]
    },
    "galaxy_execution": {
      "required_fields": [
        "final_entity_type",
        "final_entity_name",
        "history_input_mode",
        "adaptation_summary"
      ]
    }
  },
  "execution_environment": {
    "platform": "Galaxy",
    "galaxy_instance": "https://usegalaxy.org/",
    "execution_rule": "After you form a plan for the analysis, execute that plan in Galaxy."
  },
  "inputs": {
    "datasets": [
      {"name": "example.tsv", "path": "dataset/experiment_1/example.tsv"}
    ]
  },
  "user_prompt": "..."
}
```

Important interpretation rules:

- The `user_prompt` is the task instruction to execute.
- The `inputs` block defines the files available to the run.
- `execution_environment` constrains the intended platform.
- `benchmark_axes` label the scientist-help level and Galaxy-operation complexity the task is meant to probe.
- `required_result_format` defines the structured result contract the benchmark expects under `results/result.json`.
- Across prompt tiers for the same experiment, the primary benchmark variable is the prompt wording, not the input data.

## Result Format

Benchmark runs should write `results/result.json` using the shared schema `galaxy_benchmark_result_v2`:

```json
{
  "scientific_answer": {
    "...": "task-specific scientific output fields"
  },
  "galaxy_execution": {
    "final_entity_type": "tool|workflow|mixed",
    "final_entity_name": "...",
    "history_input_mode": "local_upload|remote_fetch|mixed",
    "adaptation_summary": "single_valid_run|justified_retry|stopped_with_documented_blocker"
  }
}
```

Design intent:

- `scientific_answer` measures the quality of the biomedical or analytical conclusion.
- `galaxy_execution` measures whether the agent can operate competently inside Galaxy.
- This separation is deliberate so the benchmark can answer both:
  - what level of scientist the agent can help
  - how trustworthy the agent is inside the Galaxy environment

## Formal Score Model

Each benchmark run should be interpreted with three explicit scores:

- `scientific_solution_score`: how scientifically useful the solution is for the biomedical problem
- `standard_analysis_score`: how closely the run followed the requested or benchmark-standard analysis path
- `galaxy_execution_score`: how competently the agent manipulated and accessed the Galaxy environment, independent of whether the chosen analysis was scientifically ideal

These three scores should remain separate in benchmark analysis.

Practical interpretation:

- `scientific_solution_score` is driven primarily by `scientific_answer`
- `standard_analysis_score` is driven primarily by explicit standard-path constraints, especially in `high_context`
- `galaxy_execution_score` is driven primarily by `galaxy_execution` and the run trace

Tier behavior:

- `low_context`: emphasize `scientific_solution_score` and `galaxy_execution_score`; use `standard_analysis_score` only when a standard path is explicitly requested
- `medium_context`: all three may apply, but `standard_analysis_score` should only reflect constraints that are actually stated
- `high_context`: all three apply, and `standard_analysis_score` is expected to matter most because this tier tests detailed instruction adherence

The full benchmark-wide definition lives in [docs/formal_score_model.md](/Users/4475918/Projects/Galaxy_benchmark/docs/formal_score_model.md).

## Operational Scorer

The repository now includes an executable scorer at [tools/benchmark_scorer.py](/Users/4475918/Projects/Galaxy_benchmark/tools/benchmark_scorer.py). It reads a run directory, normalizes legacy result payloads when needed, applies the hidden ground-truth rules, and emits both:

- `results/comparison.scored.md`
- `results/score_summary.json`

Example usage:

```bash
python3 tools/benchmark_scorer.py \
  --run-dir outputs/20260319_222516_experiment_6 \
  --level high_context
```

Notes:

- `--level` is optional for runs whose directory name already contains `low_context`, `medium_context`, or `high_context`.
- For historical runs created before prompt tiers were encoded in the path, pass `--level` explicitly if you want `standard_analysis_score`.
- `--stdout-only` prints the machine-readable score summary without writing files.

## Ground Truth Format

Ground-truth files now follow `galaxy_benchmark_ground_truth_v2`. They are hidden benchmark assets and are designed for fair comparison rather than brittle exact matching.

Ground-truth files can specify:

- exact matches where the benchmark truly requires an exact answer
- alias matches for common naming differences such as `Response` vs `c22: Response`
- threshold-based metrics when higher values are better
- tolerance-based numeric comparison when live Galaxy workflow versions may drift slightly
- set-overlap rules for outputs such as marker-gene panels
- explicit `score_model_support` mappings that tie `scientific_solution_score`, `standard_analysis_score`, and `galaxy_execution_score` to the appropriate hidden sections
- `preserve_three_score_vector` so downstream scoring does not collapse the run into a single opaque number

This is important for fairness. The benchmark should not penalize an agent for:

- achieving a better valid metric than the reference threshold
- using equivalent naming for the same scientific target
- small workflow-size differences caused by validated workflow updates
- equivalent Galaxy execution paths that satisfy the task goal and reporting contract

Ground-truth and evaluator design should preserve the distinction between:

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

## Execution Protocol

No single runner command is mandated. Any implementation is acceptable if it follows the benchmark protocol and write boundary.

### Prerequisites

- A valid Galaxy API key must exist in the repository root `.env` file as `GALAXY_API_KEY`.
- The key must be non-empty before any Galaxy interaction starts.
- If the key is missing or empty, stop and report:
  - `Missing required credential: GALAXY_API_KEY in .env. Provide this key before running Galaxy API tasks.`

### Per-Experiment Workflow

1. Read one experiment JSON from `experiments/<level>/`.
2. Execute one experiment at a time from start to finish.
3. Create a new run directory under `outputs/` named `outputs/<date_time>_<level>_<experiment_name>/`.
4. Create the required subdirectories: `plan/`, `reasoning/`, `errors/`, and `results/`.
5. Write the initial plan before execution starts.
6. Execute the task in Galaxy exactly as instructed by the experiment file.
7. Continuously log planning, execution, checks, revisions, and retries.
8. Write the final structured result artifact.
9. Write a reproduction artifact that documents the run in executable, annotated form.
10. Only after the result and reproduction artifacts exist, read the matching ground-truth file.
11. Generate a field-by-field comparison report between the produced result and the ground truth.

## Required Output Artifacts

For each run, create the following structure:

```text
outputs/<date_time>_<level>_<experiment_name>/
|-- plan/
|   `-- saved.md
|-- reasoning/
|   `-- reasoning.md
|-- errors/
|   `-- error.json
`-- results/
    |-- result.json
    |-- reproduce_<experiment_name>.py
    |-- activity_log.jsonl
    `-- <comparison-report>.md
```

Notes:

- Use a sortable timestamp such as `YYYYMMDD_HHMMSS`.
- Every new benchmark run should use a new top-level run directory.
- Additional run artifacts are allowed, but they must be stored under `results/`.
- A comparison report is required under `results/`; `comparison.md` is the recommended filename.
- Do not overwrite prior artifacts. If a correction is needed within a run, create a new versioned artifact instead.

## Reporting Standard

The benchmark requires explicit, reconstructable reporting. Traceability is part of benchmark compliance, not optional housekeeping.

### Core Rule

- If an action or decision is not recorded in the run artifacts, it is considered not performed.

### What Must Be Reported

- The initial plan and expected outputs
- Tool and workflow discovery steps
- Candidate approaches considered and why they were accepted or rejected
- Interface choice and tradeoffs when multiple execution paths exist
- Parameter-selection rationale
- Concrete evidence used for decisions, including relevant IDs and artifact paths
- All execution actions
- All status checks and polling actions
- All failures, normalized error signatures, and root-cause interpretations
- All changes between attempts, including why the new attempt should fix the previous failure
- The final structured result and the post hoc comparison to ground truth

### Required Artifact Semantics

#### `plan/saved.md`

Record:

- experiment name
- initial objective
- inputs and datasets
- ordered plan
- expected outputs
- risks and assumptions

#### `reasoning/reasoning.md`

Write chronological entries that include:

- timestamp
- step reference
- decision made
- why that decision was made
- next action

Decision-level reporting is required. Do not collapse multiple independent decisions into one vague summary.

#### `errors/error.json`

Keep this file valid JSON throughout the run. Use a stable envelope:

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

- Keep `errors` as an array.
- Update `summary` counts when error entries change.
- Store variable details under `context` and `additional_data`.
- Mark final `run_status` as `completed`, `completed_with_errors`, or `failed`.

#### `results/activity_log.jsonl`

This is the append-only categorical execution log. Write one JSON object per line in chronological order.

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

Minimum expectations:

- Every planned action has a `plan` record.
- Every executed action has an `execute` record.
- Every verification, inspection, or polling action has a `check` record.
- Every retry has a `retry` record with its reason.
- Every change in parameters, scripts, inputs, or workflow configuration has a `revise` record.

#### `results/result.json`

This is the structured task result used for evaluation. All tasks use the shared top-level sections:

- `scientific_answer`
- `galaxy_execution`

The task-specific required fields are declared in the experiment file under `required_result_format`.

#### `results/reproduce_<experiment_name>.py`

This file must reproduce the benchmark run through explicit, annotated command-line or API steps. It should be understandable by a human reviewer and sufficient to reconstruct what the agent did.

#### `results/<comparison-report>.md`

After result generation is complete, compare the produced result against the matching ground-truth file using a field-by-field table. Then add a three-score summary section. Use this format:

| Field | Agent Result | Ground Truth | Match Status | Notes |
|---|---|---|---|---|
| `scientific_answer.target` | ... | ... | match/mismatch | ... |
| `scientific_answer.primary_metric.value` | ... | ... | match/mismatch | ... |
| `galaxy_execution.final_entity_name` | ... | ... | match/mismatch | ... |

Then append a score summary table:

| Score | Value | Status | Basis | Notes |
|---|---|---|---|---|
| `scientific_solution_score` | ... | pass/partial/fail | `scientific_answer` | ... |
| `standard_analysis_score` | ... | pass/partial/fail/not_applicable | `tier_specific_expectations` | ... |
| `galaxy_execution_score` | ... | pass/partial/fail | `galaxy_execution` and run trace | ... |

This comparison is the primary benchmark analysis artifact, not an optional summary. `comparison.md` is the recommended standard filename.

## Galaxy Execution Rules

### Polling Policy

After launching a Galaxy tool or workflow:

1. Immediately capture submission identifiers such as job ID and workflow invocation ID.
2. Perform a first status check after 15 to 30 seconds.
3. If the run is still non-terminal, poll every 1 minute.
4. Continue until a terminal state is reached (`ok`, `error`, `failed`, `deleted`, or equivalent).
5. Do not execute downstream dependent steps until required upstream jobs are complete.
6. Independent work may continue while waiting if it does not violate dependencies.

### Failure-Recovery Protocol

Blind retries are non-compliant. For every failed attempt:

1. Read the failure evidence first.
2. Extract a stable error signature such as error type, core message, failing step or tool, and exit code or state.
3. Record the inferred root cause with evidence references.
4. Define a signature-specific fix strategy before retrying.
5. Log the recovery cycle in `activity_log.jsonl` using `check`, `revise`, `retry`, and `execute` entries as appropriate.
6. If the same error signature reappears, do not continue parameter sweeps alone; change the failing mechanism or stop with a documented blocker.

## Data Access and Compliance Rules

### Non-Negotiable Write Boundary

Write operations are restricted to `outputs/` only.

- Never create, modify, rename, move, or delete files outside `outputs/` during benchmark execution.
- Treat `experiments/`, `dataset/`, `evaluators/`, `ground_truth/`, and project-root files as read-only.
- If a step would require writing outside `outputs/`, stop and report a blocking violation.

### Ground-Truth Gate

- Do not read `ground_truth/<experiment>.json` until both `results/result.json` and `results/reproduce_<experiment_name>.py` are complete.

### Secret Handling

- Never print, log, store, or expose `GALAXY_API_KEY` in any artifact, report, or command trace.

### Immutability

- Previously written artifacts are immutable.
- Do not overwrite prior versions.
- If a correction is required, write a new versioned artifact and record the change in `results/activity_log.jsonl`.

## Recommended Reporting for Papers or Benchmark Releases

If you publish results derived from this benchmark, report at minimum:

- experiment ID and context level
- Galaxy instance used
- tool or workflow chosen
- key task outputs requested by the experiment
- final metric or requested evaluation value
- terminal run status
- whether retries were needed
- location of the comparison artifact or equivalent field-by-field analysis

This repository is designed so that benchmark claims can be backed by inspectable run artifacts rather than only a headline score.

## Fair Scoring Principles

The benchmark is designed to answer two questions fairly:

1. What level of scientist can the agent help on biomedical tasks?
2. How reliably can the agent work inside Galaxy?

To support those goals:

- scientific-task scoring and Galaxy-operation scoring should be reported separately before any aggregate score
- held-out test metrics should be preferred over train-only or validation-only metrics
- threshold scoring should be used for optimization tasks where better performance should count as success
- exact output matching should be reserved for fields that are genuinely deterministic
- workflow provenance, upload mode, history navigation, retries, and recovery behavior should be judged from run artifacts, not only from final text

## Completion Checklist

Before treating a run as complete, verify:

- all required output files exist under the run directory
- `result.json` is populated with the task-specific result fields
- `reproduce_<experiment_name>.py` exists and is readable
- `activity_log.jsonl` covers planning, execution, checks, revisions, and retries
- `error.json` has a correct final status and summary counts
- a comparison report exists under `results/` and was generated only after the ground-truth gate was satisfied

## Hard Stop Conditions

Stop and report a blocker if:

- `GALAXY_API_KEY` is missing or empty
- writing outside `outputs/` would be required
- a required Galaxy job never reaches a usable terminal state and no safe fallback exists
- the same failure signature repeats without a materially different corrective action
