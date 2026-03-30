# GalaxyAgentBench Architecture

This repository is a clean-architecture benchmark platform for evaluating agents in Galaxy across platform operation, prompt robustness, and Galaxy-native knowledge use.

## Design Goals

- preserve strict traceability, immutable artifacts, delayed ground-truth comparison, and explicit recovery analysis
- encode the three benchmark pillars directly in the schema and prompt tiers
- separate benchmark definition, execution, scoring, and reporting
- isolate Galaxy, agent, MCP, GTN, and IWC concerns behind ports
- keep the checked-in benchmark assets flat and easy to scan

## Architectural Shape

- `domain`: benchmark pillars, task families, typed schemas, scoring records, failure records, run manifests
- `application`: prompt generation, scoring, failure classification, suite loading, orchestration use cases
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

- `benchmark/tasks/`: canonical task files
- `benchmark/ground_truth/`: outcome gold plus process and failure expectations
- `benchmark/datasets/local/`: local benchmark assets referenced by canonical tasks
- `benchmark/prompts/template.txt`: deterministic benchmark brief template
- `benchmark/prompts/novice/`, `benchmark/prompts/intermediate/`, `benchmark/prompts/expert/`: materialized prompt variants grouped by tier
- `benchmark/suites.json`: compact suite metadata
- `runs/`: immutable execution artifacts for published results

## Key Alignment Decisions

- benchmark identity is anchored on Galaxy as a real scientific workflow platform
- prompts use one fixed sectioned brief inspired by recent agent instruction-following benchmarks
- route-to-answer evidence is treated as benchmark data, not ancillary logging
- scoring uses the benchmark-weighted `0.5 outcome + 0.3 process + 0.2 robustness` composition
- GTN and IWC are modeled as explicit knowledge conditions rather than vague web search proxies

## Documentation Entry Points

- [Benchmark Design](docs/benchmark.md)
- [Evaluation](docs/evaluation.md)
- [Migration From Main](docs/migration_from_main.md)
