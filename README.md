# Galaxy-Bench

## Project Title

Galaxy-Bench: A Benchmark for Evaluating Iterative, Robust, and Scientifically Valid Agent Execution in Biomedical Research

Galaxy-Bench evaluates biomedical AI agents as iterative scientific problem-solvers rather than as single-shot task executors.

## Significance

AI agents are increasingly proposed as interfaces for biomedical analysis, but current evaluation frameworks still miss the properties that determine scientific usefulness.

Three limitations are especially important:

- reliance on implicit or single-path ground truth
- insufficient support for multiple scientifically acceptable workflows and parameterizations
- lack of evaluation of iterative scientific improvement across attempts

In biomedical research, analytical correctness is rarely defined by one workflow alone. Multiple preprocessing strategies, tool combinations, and parameter settings may all yield scientifically acceptable analyses. Real scientific work is also iterative: analysts refine methods after seeing outputs, revising preprocessing, models, and parameters over multiple runs.

Galaxy provides a useful execution substrate for this benchmark because it:

- standardizes workflow execution
- preserves tool and parameter provenance
- stores persistent workflow histories
- supports reproducibility and auditability

Using Galaxy as the execution layer lets the benchmark evaluate not only whether an agent finished a task, but whether it iteratively converged toward a scientifically valid analysis under realistic conditions.

## Innovation

Galaxy-Bench introduces four core innovations.

### 1. Procedural execution benchmarking

The benchmark decouples part of reasoning from execution by using Galaxy to standardize workflows and isolate procedural specification.

### 2. Solution-aware evaluation under non-unique ground truth

The benchmark moves beyond single-reference scoring and allows multiple scientifically valid workflows and parameterizations when justified by the task.

### 3. Iterative evaluation of scientific improvement

Inspired by MLE-bench, the benchmark evaluates agents across multiple attempts per task rather than only a single pass.

Primary iterative views include:

- `first_run_completion_rate`
- `best_of_n_completion_rate`
- `improvement_trajectory`

### 4. Human-informed validation of scientific acceptability

Scientific correctness is not reduced to exact parameter matching. The benchmark supports contextual adjudication that distinguishes:

- invalid analyses
- acceptable but suboptimal analyses
- high-quality analyses

## Central Hypothesis

Galaxy-mediated execution, combined with iterative evaluation across multiple agent runs, enables a benchmark that measures procedural competence, robustness, and scientific validity more accurately than single-run, ground-truth-only evaluation.

## Specific Aims

### Aim 1. Quantify how Galaxy-mediated execution and iterative refinement influence agent performance across biomedical analysis tasks

Galaxy-Bench evaluates agents along two benchmark dimensions:

- execution setting: `open` vs `galaxy`
- iteration setting: `single_run` vs `multi_run`

In `multi_run`, agents are allowed to refine:

- preprocessing steps
- tool selection
- workflow structure
- parameter configuration

Primary outcomes:

- `first_run_completion_rate`
- `best_of_n_completion_rate`
- `improvement_trajectory`

Default multi-run budget:

- up to 3 attempts per task instance unless the task defines a different cap

### Aim 2. Characterize how agents orchestrate Galaxy workflows and explore alternative analytical strategies

The benchmark evaluates how agents:

- select tools
- sequence workflow steps
- revise parameters
- recover from failures
- switch between valid workflow classes

Primary outcomes:

- `tool_selection_accuracy`
- `workflow_coherence`
- `parameterization_accuracy`
- `exploration_exploitation_profile`
- `failure_recovery_quality`
- `alternative_valid_workflow_classes`

### Aim 3. Determine robustness and reliability under variability in user prompt formulation

Each task is tested under multiple semantically equivalent prompt variants and under both `single_run` and `multi_run` settings where applicable.

Primary outcomes:

- `performance_consistency`
- `workflow_agreement`
- `iterative_stability`
- `confidence_calibration`

### Aim 4. Define and evaluate preprocessing and parameterization strategies that yield scientifically valid analyses under multiple acceptable solutions

This aim addresses the non-unique ground truth problem directly.

Primary outcomes:

- `preprocessing_accuracy`
- `parameter_configuration_accuracy`
- `result_quality`
- `scientific_acceptability`

## Benchmark Positioning

Galaxy-Bench sits between:

- human-level or analyst-level evaluation
- harness-aware agent benchmarks such as MLE-Bench
- biomedical agent benchmarks such as BioAgent Bench

Its distinctive contribution is the combination of:

- Galaxy-mediated procedural execution
- explicit multi-attempt evaluation
- support for multiple acceptable scientific solutions
- human-informed scientific acceptability review

## Core Benchmark Unit

The benchmark unit is:

`task × prompt_variant × environment × iteration_setting × agent`

### Environments

- `open`: standalone execution baseline
- `galaxy`: Galaxy-mediated execution baseline
- `galaxy_skills`: optional procedural-support diagnostic environment

### Iteration settings

- `single_run`
- `multi_run`

Primary comparisons:

- `open` vs `galaxy`
- `single_run` vs `multi_run`

## Evaluation Model

Each run preserves the three-score vector:

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

These remain mandatory and are complemented by benchmark endpoints:

- `pipeline_completion_rate`
- `first_run_completion_rate`
- `best_of_n_completion_rate`
- `improvement_trajectory`
- `tool_selection_accuracy`
- `workflow_coherence`
- `parameterization_accuracy`
- `preprocessing_accuracy`
- `result_quality`
- `scientific_acceptability`
- `output_agreement`
- `confidence_calibration`

Interpretation:

- the score vector explains the quality of a given run
- the endpoint metrics explain iterative behavior, robustness, and benchmark-level scientific claims

## Task Design Requirements

Every task must:

- represent a real biomedical objective executable in Galaxy
- define an explicit final artifact contract
- define required step classes
- define preprocessing expectations
- define parameter targets
- support evaluation under multiple acceptable solutions where justified
- support iterative refinement analysis
- support human-informed scientific acceptability review when deterministic scoring is insufficient

Each task should declare:

- `scientist_help_band`
- `galaxy_complexity_band`
- `iteration_policy`
- `acceptable_solution_families`
- `acceptable_workflow_classes`
- `preprocessing_requirements`
- `parameter_targets`
- `scientific_acceptability_policy`
- `confidence_query_policy`

## Prompt Variant Contract

Each task should have three canonical prompt variants:

- `low_context`
- `medium_context`
- `high_context`

The prompts must preserve the same task and vary only:

- user phrasing
- level of detail
- style
- ambiguity

## Required Run Artifact Layout

Each run must write a new immutable directory:

```text
outputs/<timestamp>_<level>_<experiment>/
|-- experiment_summary.json
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
|   |   |-- datasets/
|   |   `-- workflow_diffs/
|   `-- local/
|-- evaluations/
|   |-- comparison.scored.md
|   |-- field_comparisons.json
|   |-- score_summary.json
|   |-- iteration_summary.json
|   `-- scientific_acceptability_review.json
`-- results/
    |-- result.json
    |-- result.attempt_<N>.json
    |-- activity_log.jsonl
    |-- run_record.json
    |-- artifacts_manifest.json
    |-- evaluation_manifest.json
    |-- attempt_manifest.json
    `-- reproduce_<experiment>.py
```

Each completed non-BixBench run also writes `experiment_summary.json` at the run-directory root. This file is the reviewer-facing index for the run and records the experiment name, ground-truth files used for comparison, Galaxy tools used, final Galaxy result files and preserved local paths, transformed Galaxy-derived outputs used for comparison, and `Experiment_score` with `prompt_score`, `transformed_prompt_score`, `direct_ground_truth_match_score`, `transformed_ground_truth_match_score`, and `agent_performance_in_galaxy_score`.

BixBench runs use a reduced `experiment_summary.json` shape because they are final-answer benchmarks. For BixBench, keep only `experiment`, `Ground_truth_path`, `Galaxy_tools_used`, `Galaxy_results`, and `Experiment_score` with `ideal`, `Galaxy_answer`, and `direct_ground_truth_match_score`.

The non-BixBench run summary must answer these distinct questions:

- whether the original Galaxy outputs satisfy the prompt requirements
- whether agent-rearranged Galaxy outputs satisfy the prompt requirements
- whether the original Galaxy outputs directly match the ground truth
- whether an agent-rearranged Galaxy-derived output matches the ground truth
- whether the agent successfully executed and recovered inside Galaxy

## Traceability And Immutability

Galaxy-Bench depends on lossless trace capture.

If a decision or action affected execution, it must be recoverable from artifacts:

- tool discovery
- preprocessing choice
- parameter choice
- workflow modification
- failure interpretation
- retry rationale
- confidence statement or proxy
- cross-attempt comparison
- final evaluation

If it is not recorded, it does not count toward benchmark credit.

## Reviewer-Facing Safeguards

Galaxy-Bench is intended to answer the questions reviewers will ask:

- Does the benchmark support multiple valid solutions?
- Does it evaluate iterative improvement?
- Does it separate model behavior from harness and environment effects?
- Does it preserve execution evidence strongly enough for audit?
- Does it measure scientific acceptability rather than exact imitation alone?

See:

- [docs/formal_score_model.md](/Users/4475918/Projects/Galaxy_benchmark/docs/formal_score_model.md)
- [project_spec/PROJECT_SPEC.md](/Users/4475918/Projects/Galaxy_benchmark/project_spec/PROJECT_SPEC.md)
- [project_spec/evaluation/SCORING_SPEC.md](/Users/4475918/Projects/Galaxy_benchmark/project_spec/evaluation/SCORING_SPEC.md)
- [docs/reviewer_readiness.md](/Users/4475918/Projects/Galaxy_benchmark/docs/reviewer_readiness.md)
