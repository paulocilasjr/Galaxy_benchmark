# GalaxyAgentBench

GalaxyAgentBench evaluates whether an agent can use Galaxy the way a competent scientist would: choose the right workflow or tools, configure parameters, recover from failures, use Galaxy-native knowledge resources, and leave a reproducible audit trail.

## Benchmark Identity

Working title:
- `GalaxyAgentBench: Evaluating LLM Agents for Scientific Workflow Execution, Prompt Robustness, and Knowledge Use in Galaxy`

Core claim:
- benchmark the route to the answer, not only the answer
- use Galaxy as a real scientific environment with histories, workflows, metadata, provenance, GTN, and IWC
- score outcome quality, process quality, and robustness separately

## Three Benchmark Pillars

- `platform_operation_capability`: can the agent operate Galaxy correctly across histories, datasets, tools, workflows, polling, and provenance
- `prompt_robustness_and_trust`: does performance hold across novice, intermediate, and expert prompts plus multiple prompt formats
- `ecosystem_knowledge_use`: can the agent retrieve, select, and adapt GTN, IWC, and Galaxy tool metadata correctly

## Experimental Matrix

- Agent type: external general agent, external agent with Galaxy wrapper, internal Galaxy-connected agent, internal Galaxy-connected agent with MCP
- Access mode: browser/UI only, API/BioBlend only, hybrid UI + API, MCP-exposed tools/resources/prompts
- Knowledge condition: prompt only, raw web, GTN, IWC, GTN + IWC, GTN + IWC via MCP

## Task Families

- `basic_galaxy_operations`
- `single_tool_execution`
- `workflow_retrieval_and_execution`
- `tutorial_grounded_execution`
- `optimization_and_parameter_search`
- `failure_recovery`
- `provenance_and_reproducibility`

## Repository Layout

- `src/galaxy_benchmark/`: typed benchmark package using clean architecture
- `benchmark/tasks/`: canonical task definitions and legacy migrated fixtures
- `benchmark/ground_truth/`: normalized gold standards
- `benchmark/datasets/local/`: local benchmark inputs used by canonical tasks
- `benchmark/prompts/`: prompt templates plus tiered prompt variants
- `benchmark/schemas/`: JSON schemas generated from the typed models
- `benchmark/suites/`: suite manifests and planning structure
- `runs/`: immutable benchmark run artifacts
- `benchmark/tasks/legacy/raw/` and `benchmark/ground_truth/legacy/raw/`: preserved legacy source snapshots within the new layout
- `docs/`: benchmark methodology, scoring, failure taxonomy, access matrix, baselines, ADRs

## Audit and Reproducibility Rules

- run artifacts are immutable
- logs are append-only
- ground truth is read only after result generation
- failures require evidence, normalized signatures, and explicit fix strategies before retry
- manifests record agent, access mode, MCP state, knowledge condition, prompt tier, run number, and timestamps

## Current Status

Implemented now:
- typed domain models, ports, migration tooling, prompt generation, scoring skeleton, artifact-store foundation, schemas, docs, and migrated legacy fixtures

Still scaffolded:
- live Galaxy/BioBlend execution adapter
- GTN and IWC retrieval adapters
- provider-backed agent adapters
- end-to-end `run-task` and `run-suite` orchestration

## Documentation Index

- [Architecture](ARCHITECTURE.md)
- [Benchmark Overview](docs/benchmark_overview.md)
- [Benchmark Methodology](docs/benchmark_methodology.md)
- [Experimental Matrix](docs/experimental_matrix.md)
- [Task Families](docs/task_families.md)
- [Scoring](docs/scoring.md)
- [Failure Taxonomy](docs/failure_taxonomy.md)
- [Prompt Tiers](docs/prompt_tiers.md)
- [Baselines](docs/baselines.md)
- [Evaluation Protocol](docs/evaluation_protocol.md)
- [Migration From Main](docs/migration_from_main.md)
