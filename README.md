# GalaxyAgentBench

GalaxyAgentBench evaluates whether an agent can use Galaxy the way a competent scientist would: choose the right workflow or tools, configure parameters, recover from failures, use Galaxy-native knowledge resources, and leave a reproducible audit trail.

This branch merges the refactored benchmark package with the legacy v0.2 benchmark assets. The refactored layout under `benchmark/` and `src/galaxy_benchmark/` is the canonical direction. The legacy `experiments/`, `evaluators/`, `ground_truth/`, and `tools/benchmark_scorer.py` assets are retained for migration, historical run replay, and the explicit three-score evaluator used in the earlier release.

## Benchmark Identity

Working title:
- `GalaxyAgentBench: Evaluating LLM Agents for Scientific Workflow Execution, Prompt Robustness, and Knowledge Use in Galaxy`

Core claim:
- benchmark the route to the answer, not only the answer
- use Galaxy as a real scientific environment with histories, workflows, metadata, provenance, GTN, and IWC
- score outcome quality, process quality, and robustness separately in the refactored benchmark
- preserve the legacy v0.2 scientific-usefulness, standard-analysis, and Galaxy-execution score vector for backward-compatible evaluation

## Scoring Models

The repository currently carries two scoring views:

- Canonical refactored benchmark: `outcome`, `process`, and `robustness`
  - documented in [docs/evaluation.md](/Users/4475918/Projects/Galaxy_benchmark/docs/evaluation.md)
  - implemented in [scorers.py](/Users/4475918/Projects/Galaxy_benchmark/src/galaxy_benchmark/application/scoring/scorers.py)
- Legacy v0.2 benchmark: `scientific_solution_score`, `standard_analysis_score`, and `galaxy_execution_score`
  - documented in [formal_score_model.md](/Users/4475918/Projects/Galaxy_benchmark/docs/formal_score_model.md)
  - operationalized in [benchmark_scorer.py](/Users/4475918/Projects/Galaxy_benchmark/tools/benchmark_scorer.py)

The legacy scorer now uses weighted score aggregation, explicit pass and partial thresholds, trace-backed metric provenance, and audit-trace checks inside `galaxy_execution_score`.

## Repository Layout

- `src/galaxy_benchmark/`: typed benchmark package using clean architecture
- `benchmark/tasks/`: canonical task definitions for the refactored benchmark
- `benchmark/ground_truth/`: canonical ground truths for the refactored benchmark
- `benchmark/datasets/local/`: canonical local benchmark inputs
- `benchmark/prompts/`: prompt template plus tiered prompt variants
- `benchmark/schemas/`: JSON schemas generated from typed models
- `benchmark/suites.json`: suite definitions
- `runs/`: immutable benchmark run artifacts for the refactored system
- `docs/`: benchmark, evaluation, migration, and formal scoring notes
- `experiments/`: legacy v0.2 prompt-tier task packages retained for migration and replay
- `evaluators/`: legacy hidden evaluator specs retained for migration and replay
- `ground_truth/`: legacy hidden ground truths retained for migration and replay
- `tools/benchmark_scorer.py`: legacy operational scorer for archived v0.2-style runs
- `SKILL.md`: legacy executor workflow retained for the v0.2 experiment layout

## Benchmark Pillars

- `platform_operation_capability`: can the agent operate Galaxy correctly across histories, datasets, tools, workflows, polling, and provenance
- `prompt_robustness_and_trust`: does performance hold across novice, intermediate, and expert prompts
- `ecosystem_knowledge_use`: can the agent retrieve, select, and adapt GTN, IWC, and Galaxy tool metadata correctly

## Audit And Reproducibility Rules

- run artifacts are immutable
- logs are append-only
- ground truth is read only after result generation
- failures require evidence, normalized signatures, and explicit fix strategies before retry
- manifests record agent, access mode, MCP state, knowledge condition, prompt tier, run number, and timestamps

For the legacy v0.2 benchmark, auditability is also part of scoring: missing trace support should reduce Galaxy-execution credit instead of being silently ignored.

## Legacy v0.2 Notes

The legacy benchmark release contains:

- 8 task groups
- 3 prompt tiers per task: `low_context`, `medium_context`, `high_context`
- public task files under `experiments/`
- hidden scoring assets under `evaluators/` and `ground_truth/`
- archived run artifacts under `outputs/`

Use [SKILL.md](/Users/4475918/Projects/Galaxy_benchmark/SKILL.md) when executing those legacy experiments. Use [formal_score_model.md](/Users/4475918/Projects/Galaxy_benchmark/docs/formal_score_model.md) and [benchmark_scorer.py](/Users/4475918/Projects/Galaxy_benchmark/tools/benchmark_scorer.py) when scoring archived legacy runs.

## Documentation Index

- [Architecture](ARCHITECTURE.md)
- [Benchmark Design](docs/benchmark.md)
- [Evaluation](docs/evaluation.md)
- [Migration From Main](docs/migration_from_main.md)
- [Legacy Formal Score Model](docs/formal_score_model.md)
