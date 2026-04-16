# Galaxy Benchmark v0.3 Scoring Specification

## 1. Run-Level Score Vector

Each run preserves three mandatory scores in `[0,1]`:

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

Status thresholds:

- `pass >= 0.85`
- `partial >= 0.50 and < 0.85`
- `fail < 0.50`
- `not_applicable` when the benchmark contract does not define a meaningful basis

## 2. Primary Endpoint

### `pipeline_completion_rate`

Definition:

- fraction of task instances where the agent executes all required task steps and produces the required final artifact in the correct format

Run-level scoring:

- `1.0` if all required steps are completed and final artifact contract is met
- `0.5` if a valid partial execution exists but one or more required steps or final artifact conditions are unmet
- `0.0` otherwise

## 3. Secondary Operational Metrics

All operational metrics are normalized to `[0,1]`.

### `tool_selection_accuracy`

Definition:

- proportion of required steps for which the selected Galaxy tool or acceptable tool class matches the task contract

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

- scientific correctness of the final artifact relative to task-specific hidden criteria

### `output_agreement`

Definition:

- similarity of final outputs across prompt variants for the same task and environment

### `confidence_calibration`

Definition:

- agreement between the agent’s predicted success or confidence proxy and observed outcome

Suggested scoring:

- `1 - mean_absolute_error(confidence, realized_success)`

## 4. Legacy Performance Aggregate

The project may still report a legacy performance aggregate for implementation continuity:

`Perf(t,p,e) = w_c*C + w_x*X + w_s*S + w_r*R + w_i*I`

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

## 5. Prompt-Level Aggregation

For each task and environment:

`Perf(t,e) = Σ_p w_p * Perf(t,p,e)`

Default prompt weights:

- `low_context = 0.33`
- `medium_context = 0.33`
- `high_context = 0.34`

Alternative practical-support weighting:

- `low_context = 0.40`
- `medium_context = 0.35`
- `high_context = 0.25`

## 6. Robustness

For each task and environment:

`Robust(t,e) = α * mean_p(Perf(t,p,e)) - β * var_p(Perf(t,p,e))`

Recommended defaults:

- `α = 1.0`
- `β = 0.5`

Also report:

- prompt-wise variance
- output agreement
- confidence-calibration drift across prompt styles

## 7. Environment Adaptation

Primary Galaxy effect:

`Adapt_G(t,p) = Perf(t,p,galaxy) - Perf(t,p,open)`

Optional Skills effect:

`Adapt_S(t,p) = Perf(t,p,galaxy_skills) - Perf(t,p,galaxy)`

Prompt-aggregated:

`Adapt_G(t) = Σ_p w_p * Adapt_G(t,p)`

`Adapt_S(t) = Σ_p w_p * Adapt_S(t,p)`

## 8. Benchmark-Level Reporting

Report at minimum:

- mean `pipeline_completion_rate` by environment
- mean score-vector components by environment
- robustness by environment
- adaptation metrics
- tool selection accuracy
- workflow coherence
- parameterization accuracy
- preprocessing accuracy
- result quality
- confidence calibration

Benchmark-level aggregation should preserve task weighting explicitly.

## 9. User-Support Interpretation

Map prompt variants to user support levels:

- `low_context -> novice`
- `medium_context -> intermediate`
- `high_context -> expert`

User-level confidence:

`ULC(p,e) = count_t[ Perf(t,p,e) >= tau ] / |T|`

Suggested thresholds:

- usable: `0.70`
- reliable: `0.85`
- expert-grade: `0.93`

## 10. Reviewer-Facing Scoring Rules

- never replace the three-score vector with a single aggregate in primary reporting
- do not claim scientific correctness from operational scores alone
- do not claim Galaxy competence from final artifact correctness alone
- score preprocessing and parameterization explicitly where they affect result validity
- preserve uncertainty and failure taxonomy in benchmark-level reports
