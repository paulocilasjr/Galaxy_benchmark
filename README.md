# Galaxy Benchmark v0.3

Galaxy Benchmark is a biomedical agent benchmark for measuring how well an AI system can translate a user's analysis goal into a valid, auditable Galaxy execution.

This repository is being reshaped around a stronger benchmark logic:

- benchmark the combined capability of a model and its harness
- compare standalone execution against Galaxy-augmented execution
- preserve human-auditable evidence for every decision and action
- score both scientific usefulness and operational competence
- quantify robustness to prompt variation and confidence calibration

## Why This Benchmark Exists

Agent benchmarks usually compare task outputs against a ground truth. In biomedical settings that is necessary but insufficient:

- many tasks admit multiple scientifically valid solution paths
- exact output matching can be unfair when live infrastructure or workflow versions drift
- a model may reason correctly but fail operationally
- a system may execute successfully but still produce a scientifically weak answer

Galaxy changes the benchmark design space because execution is not just free-form tool calling. Galaxy provides:

- curated community tools
- parameterized workflow execution
- managed computational infrastructure
- persistent histories and provenance
- reproducibility-oriented artifact storage

The benchmark therefore asks a narrower and more useful question:

Can an agent connect a user's biomedical intent to the right Galaxy operations, configure those operations correctly, adapt when they fail, and produce a scientifically useful result with full provenance?

## Benchmark Positioning

This benchmark is designed to sit between prior work on:

- human-level or analyst-level evaluation
- agentic benchmark performance
- harness-aware evaluation such as MLE-Bench and BioAgent Bench

Galaxy Benchmark extends those ideas by using Galaxy as a constrained execution substrate. That reduces avoidable execution variance while preserving difficult scientific decisions:

- tool selection
- workflow composition
- preprocessing
- parameterization
- failure recovery
- output interpretation

## Scientific Aims

### Aim 1. Effect Of Galaxy Workbench On Agent Performance

Question:
- How much does Galaxy improve agent success relative to standalone execution?

Primary comparison:
- `open` environment: BioAgent-style standalone execution
- `galaxy` environment: Galaxy-Workbench execution

Primary endpoint:
- `pipeline_completion_rate`

Definition:
- fraction of tasks for which the agent completes the required analysis steps and produces the required final artifact in the expected format

Secondary endpoints:
- final artifact validity
- task success under blind scoring
- failure mode distribution

### Aim 2. Mechanistic Analysis Of Galaxy Interaction

Question:
- How do agents select, sequence, and configure Galaxy tools?

Primary mechanistic metrics:
- `tool_selection_accuracy`
- `workflow_coherence`
- `parameterization_accuracy`

Evidence sources:
- Galaxy histories
- job and invocation traces
- tool selections
- parameter payloads
- retry chains

### Aim 3. Robustness To Prompt Variability And Confidence

Question:
- How sensitive is performance to user phrasing, ambiguity, and style?

Per-task prompt variants:
- `low_context`
- `medium_context`
- `high_context`

Primary robustness metrics:
- `performance_consistency`
- `output_agreement`
- `confidence_calibration`

### Aim 4. Preprocessing And Configuration Competence

Question:
- Can the agent transform raw inputs into Galaxy-compatible forms and configure tools correctly enough to support reproducible analysis?

Primary metrics:
- `preprocessing_accuracy`
- `parameter_configuration_accuracy`
- `result_quality`

## What v0.3 Keeps vs Replaces

### Retained From Earlier Versions

- realistic end-to-end biomedical tasks
- multiple prompt variants for the same task
- separate hidden ground truth
- explicit output artifacts
- environment-aware evaluation
- benchmark-level reporting and aggregation
- auditability as a core design principle

### Replaced Or Tightened In v0.3

- replace underspecified “performance only” framing with explicit study aims and endpoints
- replace weak run-trace requirements with immutable trace contracts
- replace prompt-only robustness framing with prompt-style robustness plus confidence calibration
- replace vague execution scoring with explicit Galaxy-operational metrics
- replace single-result reporting with versioned attempts, evaluations, and manifests
- replace ad hoc run directories with a stricter lossless artifact layout

## Canonical Benchmark Unit

The benchmark unit is:

`task × prompt_variant × environment × agent`

Recommended environments:

- `open`: standalone BioAgent-style execution baseline
- `galaxy`: Galaxy-Workbench execution baseline
- `galaxy_skills`: optional Galaxy execution with explicit procedural support

The published benchmark emphasis is:

- primary comparison: `open` vs `galaxy`
- secondary diagnostic comparison: `galaxy` vs `galaxy_skills`

## Task Design Requirements

Every benchmark task must:

- represent a real biomedical objective that can be executed in Galaxy
- include attached public inputs under `dataset/`
- define an explicit final artifact contract
- support hidden evaluation without leaking the solution path
- encode required preprocessing expectations
- encode tool-class and parameter expectations where relevant
- support failure analysis and recovery scoring
- support prompt variants without changing the underlying task

Each task should also declare:

- `scientist_help_band`
- `galaxy_complexity_band`
- `required_steps`
- `acceptable_tool_classes`
- `acceptable_solution_families`
- `preprocessing_requirements`
- `parameter_targets`
- `confidence_query_policy`

## Prompt Variant Contract

Each task should have three prompt variants:

- `low_context`
- `medium_context`
- `high_context`

Rules:

- all three prompts must preserve the same task
- only specificity and user style may vary
- `low_context` emphasizes inference
- `medium_context` emphasizes informed planning
- `high_context` emphasizes instruction adherence

Prompt variation should deliberately include real-world user diversity:

- concise
- verbose
- ambiguous
- informal
- goal-driven
- method-constrained

## Evaluation Model

Galaxy Benchmark preserves a three-score run-level vector:

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

These remain the core per-run scores. In v0.3 they are complemented by endpoint metrics that answer the scientific aims:

- `pipeline_completion_rate`
- `tool_selection_accuracy`
- `workflow_coherence`
- `parameterization_accuracy`
- `preprocessing_accuracy`
- `result_quality`
- `output_agreement`
- `confidence_calibration`

Interpretation:

- the score vector explains the quality of an individual run
- the endpoint metrics support benchmark-level scientific claims

See:

- [docs/formal_score_model.md](/Users/4475918/Projects/Galaxy_benchmark/docs/formal_score_model.md)
- [project_spec/evaluation/SCORING_SPEC.md](/Users/4475918/Projects/Galaxy_benchmark/project_spec/evaluation/SCORING_SPEC.md)

## Required Run Artifact Layout

Each run must write a new immutable directory:

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
|   |-- comparison.scored.md
|   |-- field_comparisons.json
|   `-- score_summary.json
`-- results/
    |-- result.json
    |-- result.attempt_<N>.json
    |-- activity_log.jsonl
    |-- run_record.json
    |-- artifacts_manifest.json
    |-- evaluation_manifest.json
    `-- reproduce_<experiment>.py
```

Rules:

- never overwrite a previous attempt artifact
- append to `activity_log.jsonl`; do not rewrite history
- store Galaxy evidence snapshots under `traces/`
- record every evaluation artifact under `evaluations/`
- keep `result.json` as the latest canonical result and preserve prior attempt versions

## Traceability And Immutability

For v0.3, lossless trace capture is non-negotiable.

If a decision or action affected execution, it must be recoverable from artifacts:

- tool discovery
- rejected alternatives
- parameter decisions
- upload mode
- history creation
- polling checks
- failure evidence
- root-cause analysis
- retry rationale
- final evaluation

If it is not recorded, it does not count toward benchmark credit.

## Hidden Evaluation Assets

Public assets:

- `dataset/`
- `experiments/`

Hidden assets:

- `ground_truth/`

Hidden assets must support:

- exact checks only where justified
- threshold scoring for better-is-better metrics
- tolerant scoring for live-Galaxy drift
- overlap scoring for set-like outputs
- explicit mapping from checks to the three-score vector
- step-level operational scoring for preprocessing, tool choice, and parameterization

## Reviewer-Facing Design Safeguards

v0.3 is designed to answer common review questions up front.

### Fairness

- valid alternative biomedical solutions can receive credit
- hidden exact matching is not the default scientific criterion
- score attribution separates scientific value from operational quality

### Reproducibility

- all benchmark-valid runs require immutable trace artifacts
- Galaxy histories and execution evidence are preserved
- benchmark releases should ship schema, scoring, and task contracts

### Robustness

- prompt-style variability is part of the benchmark design, not post hoc augmentation
- robustness is evaluated across semantically equivalent prompts
- confidence calibration is reported against actual outcomes

### Harness Awareness

- the benchmark evaluates the full system, not the language model in isolation
- comparisons across environments are explicit
- model and harness contributions are not conflated in reporting

### Scientific Usefulness

- the benchmark supports assessment against analyst usefulness, not only hidden-reference imitation
- preprocessing and parameter choices are evaluated because they affect biological validity

## Repository Guide

- [AGENTS.md](/Users/4475918/Projects/Galaxy_benchmark/AGENTS.md): repository startup and authoring rules
- [SKILL.md](/Users/4475918/Projects/Galaxy_benchmark/SKILL.md): benchmark execution skill
- [project_spec/PROJECT_SPEC.md](/Users/4475918/Projects/Galaxy_benchmark/project_spec/PROJECT_SPEC.md): formal v0.3 implementation scaffold
- [project_spec/IMPLEMENTATION_GUIDE.md](/Users/4475918/Projects/Galaxy_benchmark/project_spec/IMPLEMENTATION_GUIDE.md): implementation guidance
- [docs/benchmark_card.md](/Users/4475918/Projects/Galaxy_benchmark/docs/benchmark_card.md): concise benchmark card

## Current Development Status

This repository contains both:

- canonical benchmark assets used for execution and scoring
- a stronger v0.3 specification scaffold for the next benchmark revision

Where older assets and the v0.3 spec disagree, use the v0.3 benchmark contract for new authoring and benchmark-methodology work.
