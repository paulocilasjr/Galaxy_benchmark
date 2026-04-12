# Benchmark Card

## Name

Galaxy Benchmark

## Version Scope

This repository currently defines a Galaxy-only benchmark with:

- 11 task groups
- 3 prompt tiers per task
- 33 benchmark instances

## Primary Goal

Measure whether an AI agent can act as a useful biomedical assistant while executing real work in Galaxy with auditable provenance.

## What Is Evaluated

Each scored run preserves three separate scores:

- `scientific_solution_score`
- `standard_analysis_score`
- `galaxy_execution_score`

The benchmark is designed to answer two different questions:

1. What level of scientist can the agent meaningfully help on this task?
2. How competently can the agent work inside Galaxy as an execution environment?

## Benchmark Composition

### Scientist-help bands

- `junior`: 2 tasks
- `intermediate`: 6 tasks
- `advanced`: 3 tasks

### Galaxy-complexity bands

- `intermediate`: 2 tasks
- `advanced`: 9 tasks

### Major task families

- tabular classification
- image classification
- multimodal prediction
- ATAC-seq workflow execution
- RNA-seq workflow execution
- single-cell RNA-seq clustering
- metagenomics workflow execution
- genome annotation and quality assessment
- workflow authoring and export
- workflow replay and equivalence comparison
- paper-faithful RNA-seq reproduction

### Input access modes

- local-upload only tasks: 7
- remote-fetch only tasks: 4

## Intended Use

Use this benchmark to evaluate:

- end-to-end agent performance on realistic Galaxy tasks
- instruction following across low-, medium-, and high-context prompts
- separation between scientific usefulness and Galaxy-operational competence
- auditability and failure recovery quality

## Out of Scope

This benchmark is not intended to:

- replace task-specific wet-lab validation
- serve as a general benchmark for non-Galaxy agents
- rank agents from a single headline score alone
- claim safety or clinical suitability from benchmark performance

## Recommended Reporting

Paper- or release-level reporting should include:

- model/agent identity
- benchmark version
- Galaxy instance and date range
- number of repeated runs per task/tier
- mean and uncertainty for each score
- failure taxonomy
- cost/runtime envelope
- any excluded or failed runs with reasons

## Baseline Policy

Benchmark publications should report at least:

- one transparent heuristic or rules-based baseline where feasible
- one strong general-purpose agent baseline
- one benchmark-executor configuration intended as the primary system under study

If human or analyst baselines are used, the protocol should specify:

- expertise assumptions
- tooling access
- time budget
- whether the evaluator could inspect hidden assets

## Known Limitations

- Some tasks depend on live Galaxy behavior, queue state, and workflow-version drift.
- Some public inputs are remote URLs and therefore depend on third-party persistence unless mirrored at release time.
- The benchmark emphasizes execution and reporting quality, so it does not cover every dimension of scientific reliability.
- Archived `outputs/` in the authoring repository are useful for development but should not be treated as part of a blind public evaluation release.

## Intended Misuse to Avoid

- collapsing the score vector into a single opaque value without preserving the component scores
- claiming scientific correctness from `galaxy_execution_score` alone
- using hidden ground-truth assets during blind execution
- interpreting one clean run as sufficient evidence of robustness

## Release References

- [README.md](/Users/4475918/Projects/Galaxy_benchmark/README.md)
- [docs/formal_score_model.md](/Users/4475918/Projects/Galaxy_benchmark/docs/formal_score_model.md)
- [docs/publication_release.md](/Users/4475918/Projects/Galaxy_benchmark/docs/publication_release.md)
- [docs/dataset_governance_manifest.json](/Users/4475918/Projects/Galaxy_benchmark/docs/dataset_governance_manifest.json)
