---
name: galaxy-benchmark-executor
description: Execute Galaxy-Bench runs with immutable trace capture, explicit attempt-by-attempt planning, Galaxy provenance preservation, downloaded result artifacts, and structured evaluation outputs.
metadata:
  short-description: Run Galaxy-Bench experiment(s) with lossless auditability
---

# Galaxy-Bench Executor

Use this skill when the task is to execute benchmark experiments in this repository.

## Core Principle

The run is not valid unless a third party can reconstruct:

- what the agent planned before each attempt
- what it reasoned and decided as it progressed
- what Galaxy executed
- what failed
- how the failure was interpreted and fixed
- what outputs were produced
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
|   |-- comparison.json
|   |-- comparison.attempt_<N>.json
|   `-- metrics_summary.json
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

## Artifact Requirements

The necessary artifacts are:

### 1. `plan/`

Before running the experiment in Galaxy, the agent must write the plan.

Minimum contents:

- experiment objective
- input datasets
- intended workflow steps
- intended tool choices
- expected result files
- anticipated risks

If another run or retry is performed:

- create a new plan file with the attempt number
- describe what changed from the previous plan
- explain why the new attempt is being launched

Required files:

- `plan/saved.md`
- `plan/saved.attempt_<N>.md`

### 2. `reasoning/`

All decision-making must be recorded here as the agent progresses so information is not lost.

This includes:

- tools considered and selected
- parameters considered and selected
- preprocessing decisions
- why a specific plan was chosen
- errors encountered
- how errors were interpreted
- how errors were fixed
- changes to the plan
- retries and stopping decisions
- any important intermediate reasoning or judgments

This file must be updated during execution, not reconstructed afterward.

Required files:

- `reasoning/reasoning.md`
- optionally `reasoning/reasoning.attempt_<N>.md` when an attempt-specific record is helpful

### 3. `errors/`

The error artifact must be a JSON file that records:

- the source of the error
- which tool or workflow step failed
- the error message
- when the error happened
- whether the error was fixed
- what was changed in response

Required file:

- `errors/error.json`

### 4. `traces/`

This directory stores Galaxy execution logs and all identifiers needed to track what happened in Galaxy.

It should preserve, whenever available:

- history names and IDs
- dataset names and HIDs
- job IDs
- invocation IDs
- workflow IDs
- tool IDs
- state transitions and polling results
- provenance and Galaxy metadata snapshots

This section must also include a script file that logs all commands the agent used to run the experiment.

The script log may be:

- Python
- Bash
- another language

but it must be updated as the agent executes and should preserve the actual commands used.

Required trace expectations:

- structured Galaxy evidence under `traces/galaxy/`
- command log or script log under `traces/local/` or `results/`
- `results/reproduce_<experiment>.py` must remain present as the canonical replay script

### 5. `results/`

This directory stores:

- the final structured result
- attempt-specific result versions
- all output files produced as final results
- downloaded result files from Galaxy
- the output formats produced

The agent should download the relevant Galaxy result artifacts and place them here.

Required files:

- `results/result.json`
- `results/result.attempt_<N>.json`
- downloaded result files and supporting artifacts

### 6. `evaluations/`

The evaluation outputs must be split into two files with distinct purposes:

- `evaluations/comparison.json`
  This is the detailed evaluation record. It should contain the full evaluation evidence, the scoring logic, and the four required metrics with enough detail for auditability.
- `evaluations/metrics_summary.json`
  This is the concise summary file. It must contain only the four final metric values and no extra helper metrics or metadata fields.

The required four metrics are:

#### i. `prompt_result_evaluation`

Read the prompt and evaluate whether the produced output meets the prompt requirements.

Examples of prompt requirements:

- required file format
- required headers
- required output fields
- required deliverable type

Scoring rule:

- count the number of prompt requirements checked
- count the number of prompt requirements matched
- score = `matches / checks`

The `ground_truth` file has a key called `expected_outputs` written in plain text. Use it to understand what the prompt expects as a result.

#### ii. `transformed_prompt_result_evaluation`

This uses the same scoring logic as `prompt_result_evaluation`, but the agent is allowed to transform the original Galaxy output into the prompt-required format first.

Rules:

- the original Galaxy output file or files must still be preserved unchanged
- any transformed file used for this metric must be stored separately
- the transformed file may only be derived from the original downloaded Galaxy output file or files chosen as the evaluation target
- this metric is only for prompt-format compliance after transformation; it does not replace the original-output scoring

Allowed transformations:

- renaming columns
- reordering rows or columns
- selecting subsets of rows or columns
- delimiter changes
- file-format conversion
- deterministic joins across original Galaxy output files when all scored values already exist in those original Galaxy outputs

Disallowed transformations:

- adding inferred or externally sourced annotations
- recomputing scientific results outside the original Galaxy output content
- filling missing values with guessed, inferred, or newly derived content
- normalizing values through external mappings that are not already present in the original Galaxy output
- creating scored values that are not directly traceable to the original Galaxy output file or files
- forcing the transformed output to match the prompt by introducing information that Galaxy did not actually produce

Provenance requirements:

- the transformed file must list the exact original Galaxy source file or files it was derived from
- the evaluation record must state whether the transformation is `format-only` or `content-altering`
- the evaluation record must explain the transformation steps succinctly enough for auditability

Validity rule:

- every scored value in the transformed file must be traceable to values already present in the original downloaded Galaxy output file or files
- if any scored value is newly introduced rather than reshaped from the original Galaxy output, this metric is not valid for that run
- if any content-altering transformation occurred, the evaluation must mark `transformed_prompt_result_evaluation` as invalid or not eligible instead of awarding a normal success score

Scoring rule:

- count the number of prompt requirements checked
- count the number of prompt requirements matched by the transformed file
- score = `matches / checks`

#### iii. `ground_truth_result_evaluation`

Open the ground truth file referenced for the task, read the result file it points to, then compare it to the output file produced from Galaxy.

The scored comparison target must be the original output file that Galaxy produced:

- download the exact Galaxy output file that will be used for evaluation
- preserve that downloaded file unchanged under the run directory
- perform the evaluation against that original downloaded Galaxy file
- do not modify, normalize, regenerate, rewrite, or synthesize a substitute file for the scored comparison

If helper files are needed for interpretation or reporting:

- keep them separate from the scored comparison artifact
- make it explicit that they are derived helper artifacts and not the evaluation target

Example:

- if the ground truth file has 3 columns and 5 rows, then there are `3 x 5 = 15` items to compare
- score = `matched_items / compared_items`

The comparison should be item-level, not only file-level.

#### iv. `galaxy_performance_score`

This measures the agent’s setup and execution performance in Galaxy.

Scoring rule:

- start at `100`
- if the required output was not achieved, deduct `50`
- for each failure, deduct `10`
- if the run fails completely with no output and no steps completed, score `0`

The evaluation JSON should make the calculation explicit.

Suggested fields for `evaluations/comparison.json`:

- `prompt_result_evaluation`
- `transformed_prompt_result_evaluation`
- `ground_truth_result_evaluation`
- `galaxy_performance_score`
- `calculation_notes`

Required rule for `evaluations/metrics_summary.json`:

- include only:
  - `prompt_result_score`
  - `transformed_prompt_result_score`
  - `ground_truth_result_score`
  - `galaxy_performance_score`
- do not include helper metrics such as overlap counts, revision markers, timestamps, or explanatory text

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
- changes between attempts
- stopping rationale

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
- dataset metadata and HIDs
- job state and provenance
- workflow invocation state
- stderr/stdout or equivalent failure messages

If a Galaxy object is important to execution or debugging, snapshot it.

### Polling And Wait Policy

When a Galaxy job or output dataset is still active:

- do not stop after a short ad hoc polling loop
- wait for the job to complete unless there is a clear terminal failure signature
- start with a sleep time of `1 minute` between checks
- keep that `1 minute` polling cadence until `6 minutes` of total wait time have elapsed
- after `6 minutes`, increase the sleep time to `15 minutes` between checks

At each check, preserve:

- the check timestamp
- the observed state
- the latest relevant `update_time`
- any newly available stderr/stdout or other failure details

Only stop waiting early if:

- the job or dataset enters a terminal error state
- there is a stable repeated blocker with preserved evidence
- the run is being resumed from an already preserved Galaxy state with a documented reason

### Evaluation

After result generation is complete:

- write comparison JSON artifacts
- write metric summaries
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

- `plan/saved.md`
- `reasoning/reasoning.md`
- `errors/error.json`
- `results/result.json`
- `results/reproduce_<experiment>.py`
- `results/run_record.json`
- `results/artifacts_manifest.json`
- `results/evaluation_manifest.json`
- `results/activity_log.jsonl`
- `evaluations/comparison.json`
- `evaluations/metrics_summary.json`
- the original downloaded Galaxy output file used for evaluation, preserved unchanged

Attempt-specific variants must exist when retries happened.

## Completion Requirements

Before declaring the run complete, verify:

- required outputs exist
- manifests reference all preserved artifacts
- activity log covers planning, execution, checks, retries, revisions, and evaluation
- Galaxy IDs referenced in result artifacts are preserved in traces
- final `errors/error.json` status is terminal
- no prior attempt artifact was overwritten
- evaluation JSON explicitly shows the three requested evaluation metrics
