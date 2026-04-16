# Galaxy Benchmark v0.3 – Project Specification

## 1. Purpose

Galaxy Benchmark v0.3 evaluates the combined performance of an agent and its harness on biomedical tasks, with special emphasis on how Galaxy Workbench changes that performance.

The benchmark is designed to support four claims:

1. whether Galaxy improves execution reliability relative to standalone execution
2. whether agents can operate Galaxy coherently and reproducibly
3. whether performance is robust to prompt variation
4. whether agents can perform preprocessing and parameter configuration accurately enough for valid analysis

## 2. Benchmark Philosophy

The benchmark should not reward hidden-pipeline imitation alone.

It should instead distinguish:

- scientific usefulness of the result
- adherence to an explicitly requested standard analysis path
- operational competence inside Galaxy

It should also expose the mechanisms underlying performance:

- tool choice
- workflow sequencing
- parameterization
- preprocessing
- retry behavior
- provenance capture
- confidence calibration

## 3. Core Benchmark Unit

The core unit is:

`task × prompt_variant × environment × agent`

### Prompt variants

- `low_context`
- `medium_context`
- `high_context`

### Environments

- `open`: standalone execution baseline analogous to BioAgent-style execution
- `galaxy`: Galaxy Workbench execution baseline
- `galaxy_skills`: optional Galaxy execution with procedural support

The primary scientific comparison is `open` versus `galaxy`.

## 4. Study Aims And Endpoints

### Aim 1. Galaxy effect on agent performance

Primary endpoint:

- `pipeline_completion_rate`

Secondary endpoints:

- final artifact validity
- task success rate
- failure mode profile

### Aim 2. Mechanistic analysis of Galaxy interaction

Primary metrics:

- `tool_selection_accuracy`
- `workflow_coherence`
- `parameterization_accuracy`

### Aim 3. Robustness and confidence under prompt variability

Primary metrics:

- `performance_consistency`
- `output_agreement`
- `confidence_calibration`

### Aim 4. Preprocessing and configuration competence

Primary metrics:

- `preprocessing_accuracy`
- `parameter_configuration_accuracy`
- `result_quality`

## 5. Run-Level Score Vector

Each run preserves:

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

These scores remain mandatory and separate.

They are complemented by endpoint metrics that support benchmark-level reporting.

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
- `acceptable_solution_families`
- `human_baseline_protocol`
- `confidence_query_policy`
- `evaluation_spec`
- `ground_truth_contract`

Tasks should be designed so that:

- the same task survives across all prompt variants
- the final artifact contract is explicit
- multiple scientifically valid methods can receive credit when appropriate
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

Galaxy environments must additionally preserve:

- history IDs
- invocation IDs
- job IDs
- dataset IDs
- workflow IDs when applicable
- parameter payloads or equivalent trace evidence

## 9. Run Artifact Contract

Each run must preserve immutable artifacts for:

- planning
- reasoning
- execution logs
- error history
- Galaxy trace snapshots
- final outputs
- attempt-specific outputs
- field-level evaluation
- score summary
- artifact manifests

No benchmark-valid run may depend on ephemeral in-memory reasoning or unstored execution state.

## 10. Scoring Layers

### 10.1 Run-level

Mandatory:

- three-score vector
- operational metrics
- confidence record

### 10.2 Task-level

Aggregate across prompt variants for each environment.

### 10.3 Benchmark-level

Aggregate across tasks and environments to report:

- environment performance
- robustness
- Galaxy effect
- Skills effect
- user support bands
- confidence calibration

## 11. Human-Level And Harness-Aware Framing

The benchmark should support comparison against:

- transparent heuristic baselines
- strong agent baselines
- optional human or analyst reference protocols

Reporting must clearly distinguish:

- model capability
- harness capability
- environment effect

## 12. Publication Readiness Requirements

The benchmark must be able to support publication claims about:

- scientific usefulness
- operational competence
- robustness
- reproducibility
- confidence calibration

Publication-facing benchmark bundles should include:

- benchmark version
- task inventory
- prompt inventory
- environment definitions
- scoring definitions
- uncertainty reporting
- failure taxonomy
- dataset governance manifest

## 13. Deprecated Concepts

The following older patterns should not be expanded in v0.3:

- prompt labels only as `vague/specific/very_specific` without contextual semantics
- performance-only reporting without operational endpoints
- overwrite-prone run outputs
- scores with no field-level justification
- benchmark claims that do not separate Galaxy competence from scientific answer quality
