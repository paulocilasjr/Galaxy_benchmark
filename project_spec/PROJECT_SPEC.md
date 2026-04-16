# Galaxy-Bench v0.3 – Project Specification

## 1. Purpose

Galaxy-Bench v0.3 evaluates the combined performance of an agent and its harness on biomedical tasks, with special emphasis on:

- how Galaxy-mediated execution changes performance
- how performance changes when agents are allowed to iterate across multiple attempts
- whether the resulting analyses are scientifically acceptable under non-unique ground truth

## 2. Benchmark Philosophy

Galaxy-Bench treats biomedical analysis as:

- procedural
- iterative
- non-unique in valid solution space
- sensitive to preprocessing and parameter choices

The benchmark should not reward hidden-pipeline imitation alone when that would be scientifically misleading.

It instead distinguishes:

- scientific usefulness of the result
- adherence to any explicitly requested standard path
- operational competence inside Galaxy
- quality of iterative improvement
- scientific acceptability under multiple valid solutions

## 3. Core Benchmark Unit

The core unit is:

`task × prompt_variant × environment × iteration_setting × agent`

### Prompt variants

- `low_context`
- `medium_context`
- `high_context`

### Environments

- `open`
- `galaxy`
- `galaxy_skills`

### Iteration settings

- `single_run`
- `multi_run`

Primary methodological comparisons:

- `open` versus `galaxy`
- `single_run` versus `multi_run`

## 4. Scientific Aims And Endpoints

### Aim 1. Quantify how Galaxy-mediated execution and iterative refinement influence performance

Primary endpoints:

- `first_run_completion_rate`
- `best_of_n_completion_rate`
- `improvement_trajectory`

### Aim 2. Characterize workflow orchestration and strategy search

Primary metrics:

- `tool_selection_accuracy`
- `workflow_coherence`
- `parameterization_accuracy`
- `exploration_exploitation_profile`
- `failure_recovery_quality`

### Aim 3. Measure robustness to prompt variability

Primary metrics:

- `performance_consistency`
- `workflow_agreement`
- `iterative_stability`
- `confidence_calibration`

### Aim 4. Evaluate preprocessing, parameterization, and scientific acceptability under multiple valid solutions

Primary metrics:

- `preprocessing_accuracy`
- `parameter_configuration_accuracy`
- `result_quality`
- `scientific_acceptability`

## 5. Run-Level Score Vector

Each run preserves:

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

These remain mandatory and separate.

They are complemented by:

- completion endpoints
- iteration endpoints
- mechanistic operational metrics
- scientific acceptability review outputs

## 6. Task Requirements

Each task must include:

- `task_id`
- `title`
- `domain`
- `scientist_help_band`
- `galaxy_complexity_band`
- `description`
- `datasets`
- `task_objective`
- `required_final_artifacts`
- `required_steps`
- `preprocessing_requirements`
- `parameter_targets`
- `acceptable_tool_classes`
- `acceptable_workflow_classes`
- `acceptable_solution_families`
- `iteration_policy`
- `human_baseline_protocol`
- `confidence_query_policy`
- `scientific_acceptability_policy`
- `evaluation_spec`
- `ground_truth_contract`

Tasks should be designed so that:

- the same task survives across all prompt variants
- the final artifact contract is explicit
- multiple scientifically valid methods can receive credit where justified
- iterative refinement can be measured across attempts
- Galaxy operations can be audited directly

## 7. Prompt Requirements

Each task should have exactly three canonical prompt variants:

- `low_context`
- `medium_context`
- `high_context`

Prompts must vary:

- wording
- structure
- user sophistication
- ambiguity level

Prompts must not vary:

- the underlying biomedical objective
- attached inputs
- hidden evaluation target

## 8. Environment Requirements

Each environment runner must return:

- outputs
- artifacts
- trace manifests
- timing
- execution context
- failure modes
- confidence record if queried
- attempt-level summaries

Galaxy environments must additionally preserve:

- history IDs
- invocation IDs
- job IDs
- dataset IDs
- workflow IDs when applicable
- parameter payloads or equivalent trace evidence
- workflow differences between attempts when iteration occurs

## 9. Iteration Contract

Iteration is a first-class benchmark feature.

Each task must define:

- whether iteration is allowed
- the maximum number of attempts
- what counts as a materially new attempt
- whether early stopping is allowed

Recommended default:

- `multi_run` permits up to 3 attempts

Each attempt should preserve:

- its own plan update
- its own reasoning update
- its own result artifact
- any workflow or parameter changes
- evaluation output if scored

## 10. Run Artifact Contract

Each run must preserve immutable artifacts for:

- planning
- reasoning
- execution logs
- error history
- Galaxy trace snapshots
- workflow differences across attempts
- final outputs
- attempt-specific outputs
- field-level evaluation
- iteration summary
- scientific acceptability review
- score summary
- artifact manifests

No benchmark-valid run may depend on ephemeral in-memory reasoning or unstored execution state.

## 11. Scoring Layers

### 11.1 Attempt-level

Each attempt may receive:

- the three-score vector
- operational metrics
- scientific acceptability status

### 11.2 Run-level

Each benchmark run must support:

- first-attempt metrics
- best-of-N metrics
- improvement-trajectory metrics

### 11.3 Task-level

Aggregate across prompt variants for each environment and iteration setting.

### 11.4 Benchmark-level

Aggregate across tasks and environments to report:

- environment performance
- iteration benefit
- robustness
- Galaxy effect
- confidence calibration
- scientific acceptability distribution

## 12. Human-Informed Validation

The benchmark should support human-informed adjudication when deterministic scoring alone cannot distinguish:

- invalid analyses
- acceptable but suboptimal analyses
- high-quality analyses

Human-informed review should be:

- structured
- bounded by explicit rubrics
- traceable to concrete artifacts

## 13. Publication Readiness Requirements

The benchmark must support claims about:

- capability
- robustness
- reproducibility
- scientific readiness
- iterative improvement

Publication-facing bundles should include:

- benchmark version
- task inventory
- prompt inventory
- environment definitions
- iteration policy
- scoring definitions
- uncertainty reporting
- failure taxonomy
- scientific acceptability rubric summary
- dataset governance manifest
