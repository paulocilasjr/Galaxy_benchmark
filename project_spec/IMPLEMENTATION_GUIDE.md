# Implementation Guide For Galaxy Benchmark v0.3

## Implementation Strategy

Implement the benchmark in layers so the scientific contract and the execution contract stay aligned.

## Phase 1. Contract Alignment

Update the benchmark assets so that:

- task schema supports preprocessing, parameter targets, human-baseline protocol, and confidence policies
- prompt schema supports context tier plus prompt-style metadata
- run schema supports immutable artifacts, score vectors, operational metrics, confidence, and Galaxy traces
- report schema supports benchmark-level endpoint reporting

## Phase 2. Task And Prompt Registry

Build or update loaders that:

- validate tasks and prompts against schemas
- preserve semantic linkage across prompt variants
- support environment comparisons without mutating task identity

## Phase 3. Run Orchestration

The orchestrator should:

- create immutable run directories
- record manifests and trace artifacts
- preserve attempt-specific outputs
- keep benchmark-valid runs distinct from simulated development runs

## Phase 4. Evaluation Engine

Implement:

- three-score vector calculation
- endpoint metrics
- prompt-variant robustness
- environment adaptability
- confidence-calibration calculations

## Phase 5. Reporting

Generate:

- per-run evaluation bundle
- per-task prompt and environment breakdowns
- per-agent summaries
- benchmark-level summaries with uncertainty and failure taxonomies

## Required Implementation Guarantees

### Lossless trace capture

Every important action must leave an artifact reference.

### No destructive overwrites

Retries must create versioned artifacts instead of replacing previous outputs.

### Explicit evidence mapping

Every score should map to concrete fields or trace evidence.

### Publication separation

Simulated harness runs and publication-eligible benchmark runs must remain distinguishable.

## Minimal Run Record Requirements

Every benchmark run record should include:

- benchmark version
- task id
- prompt variant
- environment
- agent id
- execution context
- artifact manifests
- retry chain
- score vector
- operational metrics
- confidence record

## Recommended Verification

Before treating the v0.3 implementation as stable:

- validate example JSON files against schemas
- run unit tests for scoring, loading, and aggregation
- validate report generation on mixed environments
- validate that missing artifacts or overwritten outputs are detected as benchmark-invalid
