# Galaxy-Bench v0.3 Scoring Specification

## 1. Mandatory Run-Level Score Vector

Each run preserves three mandatory scores in `[0,1]`:

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

Status thresholds:

- `pass >= 0.85`
- `partial >= 0.50 and < 0.85`
- `fail < 0.50`
- `not_applicable` when the benchmark contract does not define a meaningful basis

## 2. Iteration-Aware Primary Endpoints

### `first_run_completion_rate`

Definition:

- fraction of task instances where attempt 1 completes all required steps and produces the required final artifact in the correct format

### `best_of_n_completion_rate`

Definition:

- fraction of task instances where any attempt within the allowed attempt budget completes all required steps and produces the required final artifact in the correct format

### `improvement_trajectory`

Definition:

- normalized improvement in performance across attempts within a task instance

Suggested run-level summary:

- `best_attempt_score - first_attempt_score`

## 3. Core Operational Metrics

All operational metrics are normalized to `[0,1]`.

### `pipeline_completion_rate`

Definition:

- proportion of required task steps completed with the required final artifact generated in the correct format

### `tool_selection_accuracy`

Definition:

- proportion of required steps for which the selected tool or acceptable tool class matches the task contract

### `workflow_coherence`

Definition:

- proportion of required edges in the intended step graph that are satisfied by the executed workflow sequence

### `parameterization_accuracy`

Definition:

- weighted accuracy of task-critical parameter settings

### `preprocessing_accuracy`

Definition:

- proportion of preprocessing requirements satisfied before downstream execution

### `result_quality`

Definition:

- scientific correctness and usefulness of the final artifact relative to hidden task criteria

### `scientific_acceptability`

Definition:

- task-specific judgment of whether the analysis is methodologically acceptable under one of the allowed valid solution classes

Recommended encoding:

- `0.0 = invalid`
- `0.5 = acceptable but suboptimal`
- `1.0 = high-quality acceptable`

### `output_agreement`

Definition:

- similarity of final outputs across prompt variants for the same task, environment, and iteration setting

### `confidence_calibration`

Definition:

- alignment between the agent’s predicted success or confidence proxy and observed outcome

Suggested scoring:

- `1 - mean_absolute_error(confidence, realized_success)`

## 4. Iteration Mechanism Metrics

### `exploration_exploitation_profile`

Definition:

- characterization of whether the agent explores materially different workflows or narrowly tunes an existing one

### `failure_recovery_quality`

Definition:

- quality of the agent’s response to failure evidence across attempts

Suggested ingredients:

- evidence reading
- root-cause identification
- materially changed next attempt
- successful recovery where possible

## 5. Legacy Performance Aggregate

The project may still report a legacy aggregate for implementation continuity:

`Perf(t,p,e,a) = w_c*C + w_x*X + w_s*S + w_r*R + w_i*I`

Where:

- `C = correctness`
- `X = execution success`
- `S = scientific validity`
- `R = reproducibility / provenance`
- `I = interpretation / iteration quality`

Recommended default weights:

- correctness: `0.35`
- execution: `0.20`
- scientific_validity: `0.20`
- reproducibility: `0.15`
- interpretation: `0.10`

This aggregate is secondary to the score vector plus endpoint metrics.

## 6. Prompt-Level Aggregation

For each task, environment, and iteration setting:

`Perf(t,e,i) = Σ_p w_p * Perf(t,p,e,i)`

Default prompt weights:

- `low_context = 0.33`
- `medium_context = 0.33`
- `high_context = 0.34`

## 7. Robustness

For each task, environment, and iteration setting:

`Robust(t,e,i) = α * mean_p(Perf(t,p,e,i)) - β * var_p(Perf(t,p,e,i))`

Recommended defaults:

- `α = 1.0`
- `β = 0.5`

Also report:

- prompt-wise variance
- output agreement
- iterative stability
- confidence-calibration drift across prompt styles

## 8. Environment And Iteration Adaptation

Galaxy effect:

`Adapt_G(t,p,i) = Perf(t,p,galaxy,i) - Perf(t,p,open,i)`

Iteration effect:

`Adapt_I(t,p,e) = Perf_best_of_n(t,p,e) - Perf_first_run(t,p,e)`

Optional Skills effect:

`Adapt_S(t,p,i) = Perf(t,p,galaxy_skills,i) - Perf(t,p,galaxy,i)`

## 9. Benchmark-Level Reporting

Report at minimum:

- mean `first_run_completion_rate`
- mean `best_of_n_completion_rate`
- mean `improvement_trajectory`
- mean score-vector components by environment and iteration setting
- robustness by environment and iteration setting
- adaptation metrics
- tool selection accuracy
- workflow coherence
- parameterization accuracy
- preprocessing accuracy
- result quality
- scientific acceptability
- confidence calibration

Benchmark-level aggregation should preserve task weighting explicitly.

## 10. Reviewer-Facing Scoring Rules

- never replace the three-score vector with a single aggregate in primary reporting
- never report only best-of-N success without first-run performance
- do not claim scientific correctness from operational scores alone
- do not claim Galaxy competence from final artifact correctness alone
- support multiple acceptable valid solutions when the task justifies it
- preserve uncertainty and failure taxonomy in benchmark-level reports
- preserve attempt-level evidence for any claimed iterative improvement
