# Formal Score Model

Galaxy Benchmark should report three explicit scores for each run.

These scores answer different questions and should not be collapsed into one brittle judgment by default.

## Score Names

### `scientific_solution_score`

Definition:
- Measures how scientifically useful the agent's solution is for the user's biomedical problem.
- This score is about the quality of the analytical solution, not whether it copied one hidden reference workflow.

What it should capture:
- whether the agent solved the right scientific problem
- whether the reported scientific output is valid and usable
- whether the requested metric, artifact, interpretation, or result field is scientifically correct
- whether equivalent valid methods reached an acceptable answer

What it should not capture:
- exact adherence to a named tool or workflow when the prompt did not require it
- Galaxy interface behavior that is unrelated to the scientific answer itself

Primary evidence sources:
- `scientific_answer`
- task-specific thresholds, aliases, overlap rules, and acceptable artifact classes in `ground_truth/`

### `standard_analysis_score`

Definition:
- Measures how closely the agent followed the requested or benchmark-standard analysis path.
- This is the instruction-following and reference-adherence score.

What it should capture:
- compliance with explicitly requested tools, workflows, parameters, stages, or reporting conventions
- reproduction of a named standard analysis when the prompt requires one
- adherence to task-specific methodological constraints that define the intended standard path

What it should not capture:
- hidden pipeline imitation when the user prompt did not ask for it
- scientific failure caused only by Galaxy execution issues if the requested standard was otherwise followed

Primary evidence sources:
- `tier_specific_expectations`
- exact-match or stage-pattern checks in `ground_truth/`
- `high_context` deterministic checks in `evaluators/`

### `galaxy_execution_score`

Definition:
- Measures how competently the agent manipulated and accessed the Galaxy environment, independent of whether the chosen analysis was scientifically ideal.

What it should capture:
- local upload and remote fetch behavior
- history creation, navigation, and inspection
- tool and workflow invocation inside Galaxy
- parameter entry and execution control
- monitoring, polling, and state handling
- recovery from failures using evidence rather than blind retries
- provenance extraction and auditable reporting of Galaxy actions

What it should not capture:
- whether the final scientific method was the best one for the biomedical question
- exact compliance with a named analysis standard unless that compliance is expressed as Galaxy-operational behavior

Primary evidence sources:
- `galaxy_execution`
- activity logs, retry records, failure analyses, and reproduction artifacts
- Galaxy-oriented deterministic checks in `evaluators/`

## Tier Behavior

The same task may emphasize the three scores differently across prompt tiers.

- `low_context`:
  Prioritize `scientific_solution_score` and `galaxy_execution_score`.
  `standard_analysis_score` should usually be low-weight or not applicable unless the prompt explicitly names a required standard.

- `medium_context`:
  All three scores may apply.
  `standard_analysis_score` should only reflect constraints that are actually stated or strongly implied by the prompt.

- `high_context`:
  All three scores apply.
  `standard_analysis_score` should be emphasized because this tier is intended to test adherence to detailed instructions.

## Scoring Rules

- Each score should be reported separately on a normalized `0.0` to `1.0` scale.
- Each score should be computed as a weighted mean over its applicable checks.
- Benchmark-wide score status thresholds should be consistent across experiments: `pass >= 0.85`, `partial >= 0.50`, `fail < 0.50`.
- `standard_analysis_score` may be reported as `not_applicable` when a task instance does not define a meaningful standard path.
- The benchmark should always preserve the score vector even if a paper later reports an optional aggregate.
- A low `standard_analysis_score` does not automatically mean the run was scientifically bad.
- A high `scientific_solution_score` does not automatically mean the run was compliant with a requested standard method.
- A high `galaxy_execution_score` does not automatically mean the scientific solution was correct.
- `galaxy_execution_score` should include audit-trace compliance, because Galaxy competence is not fully creditable without inspectable provenance.
- Missing or ambiguous reporting provenance should not silently receive full credit; if a metric split or artifact identity is unreported, full credit should require trace-backed evidence.

## Mapping To Current Benchmark Files

- `scientific_solution_score` maps primarily to base-level `scientific_answer` criteria.
- `standard_analysis_score` maps primarily to explicit standard-path checks, especially `high_context` expectations.
- `galaxy_execution_score` maps primarily to `galaxy_execution` expectations and run-trace evidence.

This means the benchmark should prefer:
- flexible base criteria for scientifically valid alternatives
- explicit tier-specific constraints for standard-path adherence
- separate Galaxy-operation checks that do not depend on whether the chosen analysis was scientifically optimal

## Hidden-Asset Encoding

To keep the score model explicit in repository assets:

- each `evaluators/experiment_N.json` should include a `score_model` block
- each `ground_truth/experiment_N.json` should include `fair_scoring.score_model_support` and `fair_scoring.preserve_three_score_vector`
- evaluator `score_model` blocks should use the same aggregation method and score-status thresholds across experiments
- ground-truth `fair_scoring` blocks should state that auditability contributes to `galaxy_execution_score`
- each comparison artifact should include both field-level comparison and the three-score summary

## Authoring Rules

When creating or revising a task:

- ensure the task can support all three scores conceptually
- keep `scientific_solution_score` independent from exact hidden-pipeline matching unless the prompt requires exact matching
- define `standard_analysis_score` only from explicit standard-analysis constraints
- keep `galaxy_execution_score` restricted to Galaxy interaction, manipulation, monitoring, recovery, and provenance
- avoid embedding Galaxy-execution facts inside scientific-answer scoring when they can be scored separately

## Recommended Score Output Shape

If a scorer emits a machine-readable summary, prefer a structure like:

```json
{
  "scientific_solution_score": {
    "value": 0.84,
    "status": "pass",
    "evidence": ["scientific_answer.primary_metric.value"]
  },
  "standard_analysis_score": {
    "value": 0.92,
    "status": "pass",
    "applicability": "required",
    "evidence": ["tier_specific_expectations.high_context"]
  },
  "galaxy_execution_score": {
    "value": 0.78,
    "status": "partial",
    "evidence": ["galaxy_execution.history_input_mode", "galaxy_execution.adaptation_summary"]
  }
}
```

This score summary should remain secondary to the full field-level comparison and run artifacts.
