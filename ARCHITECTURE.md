# GalaxyAgentBench Architecture

This repository is a clean-architecture benchmark platform for evaluating agents in Galaxy across platform operation, prompt robustness, and Galaxy-native knowledge use.

## Design Goals

- preserve strict traceability, immutable artifacts, delayed ground-truth comparison, and explicit recovery analysis
- encode the three benchmark pillars directly in the schema and suite structure
- separate benchmark definition, execution, scoring, and reporting
- isolate Galaxy, agent, MCP, GTN, and IWC concerns behind ports
- make prompt tiers, access modes, and knowledge conditions first-class experimental factors

## Architectural Shape

- `domain`: benchmark pillars, task families, typed schemas, scoring records, failure records, run manifests
- `application`: migration, prompt generation, scoring, failure classification, suite loading, orchestration use cases
- `ports`: Galaxy, agent, knowledge, artifact-store, and repository contracts
- `infrastructure`: filesystem stores, JSON repositories, provider adapters, Galaxy adapters, knowledge adapters
- `interfaces`: CLI and serializer entry points

## Canonical Benchmark Concepts

- `BenchmarkTask`
- `PromptVariant`
- `RunConfiguration`
- `RunManifest`
- `GroundTruth`
- `ScoreCard`
- `FailureRecord`
- `EvaluationResult`

## Repository Structure Intent

- `benchmark/tasks/`: canonical tasks grouped by suite and family
- `benchmark/ground_truth/`: outcome gold plus process and failure expectations
- `benchmark/datasets/local/`: local benchmark assets referenced by canonical tasks
- `benchmark/prompts/templates/`: deterministic prompt templates
- `benchmark/prompts/novice/`, `benchmark/prompts/intermediate/`, `benchmark/prompts/expert/`: materialized prompt variants grouped by tier
- `benchmark/suites/`: suite manifests for core, GTN, IWC, recovery, and legacy migration inputs
- `runs/`: immutable execution artifacts for published results
- `benchmark/tasks/legacy/raw/` and `benchmark/ground_truth/legacy/raw/`: preserved legacy source snapshots

## Key Alignment Decisions

- benchmark identity is anchored on Galaxy as a real scientific workflow platform
- route-to-answer evidence is treated as benchmark data, not ancillary logging
- scoring uses the benchmark-weighted `0.5 outcome + 0.3 process + 0.2 robustness` composition
- GTN and IWC are modeled as explicit knowledge conditions rather than vague web search proxies

## Documentation Entry Points

- [Benchmark Overview](docs/benchmark_overview.md)
- [Benchmark Methodology](docs/benchmark_methodology.md)
- [Experimental Matrix](docs/experimental_matrix.md)
- [Task Families](docs/task_families.md)
- [Scoring Model](docs/scoring.md)
- [Failure Taxonomy](docs/failure_taxonomy.md)
- [Prompt Tiers](docs/prompt_tiers.md)
- [Baselines](docs/baselines.md)
- [Evaluation Protocol](docs/evaluation_protocol.md)
- [Migration From Main](docs/migration_from_main.md)

## ADR Index

- [ADR 0001: Project Structure](docs/architecture/adr-0001-project-structure.md)
- [ADR 0002: Task Schema](docs/architecture/adr-0002-task-schema.md)
- [ADR 0003: Scoring Model](docs/architecture/adr-0003-scoring-model.md)
- [ADR 0004: Agent Abstraction](docs/architecture/adr-0004-agent-abstraction.md)
- [ADR 0005: Galaxy Access Modes](docs/architecture/adr-0005-galaxy-access-modes.md)
