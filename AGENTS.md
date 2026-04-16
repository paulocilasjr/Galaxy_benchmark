# Galaxy Benchmark Codex Guide

Read this file first when working in this repository.

Then use:

- [README.md](/Users/4475918/Projects/Galaxy_benchmark/README.md) for the benchmark definition
- [SKILL.md](/Users/4475918/Projects/Galaxy_benchmark/SKILL.md) when executing benchmark runs
- [project_spec/PROJECT_SPEC.md](/Users/4475918/Projects/Galaxy_benchmark/project_spec/PROJECT_SPEC.md) when changing benchmark structure or implementation scaffolding

## Repository Mission

Galaxy Benchmark evaluates the combined capability of an agent and its harness to:

- interpret a biomedical request
- map it to Galaxy-compatible operations
- execute with auditable provenance
- recover from failure
- produce a scientifically useful result

The benchmark is intended to support Nature Methods-tier evaluation claims. That means every benchmark change should improve at least one of:

- scientific realism
- evaluation fairness
- execution auditability
- reproducibility
- reviewer-facing clarity

## High-Level Questions

When authoring or revising the benchmark, preserve the ability to answer:

1. How much does Galaxy Workbench improve agent performance compared with standalone execution?
2. How competently does the agent manipulate Galaxy itself?
3. How robust is the agent to prompt variability?
4. How well does the agent handle preprocessing, parameterization, and reproducibility-critical setup?
5. How well calibrated is the agent’s stated or inferred confidence?

## What To Preserve

Keep these existing strengths:

- realistic end-to-end biomedical tasks
- multiple prompt variants for the same underlying task
- hidden reference answers and evaluator metadata
- explicit run artifacts
- separate reporting of scientific and operational performance
- strong emphasis on failure recovery and traceability

## What To Tighten In v0.3

Prefer changes that add:

- explicit primary and secondary endpoints
- mechanistic metrics for Galaxy interaction
- confidence-calibration support
- preprocessing and parameter-configuration scoring
- immutable versioned run artifacts
- reviewer-readable methodology and reporting language

Avoid changes that:

- collapse the benchmark to a single opaque score
- reward hidden-pipeline imitation when not scientifically justified
- reduce artifact traceability
- allow destructive overwrites of benchmark evidence

## Authoring vs Execution

### Benchmark authoring

You may edit:

- `README.md`
- `AGENTS.md`
- `SKILL.md`
- `docs/`
- `project_spec/`
- `experiments/`
- `ground_truth/`
- `dataset/`
- source code and tools supporting the benchmark

### Benchmark execution

When the task is to run experiments, follow [SKILL.md](/Users/4475918/Projects/Galaxy_benchmark/SKILL.md) and only write under `outputs/`.

## Immutable Artifact Policy

This repository now assumes a lossless trace model.

If a run is executed:

- never overwrite a previous plan, result, comparison, or reproduction artifact
- keep append-only logs where appropriate
- create versioned attempt artifacts for retries
- preserve Galaxy evidence snapshots and IDs
- preserve evaluation artifacts that justify each score

Minimum expectation for every benchmark-valid run:

- initial plan
- updated reasoning after each material decision
- structured error envelope
- append-only activity log
- canonical result plus attempt versions
- reproduction script
- Galaxy trace captures
- evaluation outputs
- artifact manifests

## Required Run Layout

The expected benchmark run layout is:

```text
outputs/<timestamp>_<level>_<experiment>/
|-- plan/
|-- reasoning/
|-- errors/
|-- traces/
|-- evaluations/
`-- results/
```

Required preservation rules:

- `plan/saved.md` is the initial plan and should stay immutable
- retries create `plan/saved.attempt_<N>.md`
- `reasoning/reasoning.md` is append-only and may be supplemented by attempt-specific files
- `errors/error.json` must preserve the full error history
- `results/activity_log.jsonl` is append-only
- `results/result.json` is the latest canonical output, while older attempts remain as `result.attempt_<N>.json`
- `evaluations/` stores all field comparisons and score summaries
- `traces/` stores Galaxy and local execution evidence

## Ground Truth Discipline

Do not leak hidden evaluator or reference-answer details into public prompts.

Ground truth should support:

- scientific scoring
- standard-analysis scoring
- Galaxy-execution scoring
- endpoint metrics such as completion rate, tool choice accuracy, parameterization accuracy, preprocessing accuracy, and confidence calibration

## Review Standard

When revising the benchmark, assume reviewers will ask:

- Is the benchmark scientifically meaningful?
- Is the scoring fair to valid alternative solutions?
- Is Galaxy actually being evaluated rather than merely used?
- Is the benchmark reproducible?
- Are prompts realistic?
- Are the claims about robustness and confidence supported by design?
- Can failures be audited after the fact?

Good benchmark changes answer those questions in the repository artifacts themselves, not only in prose explanations.
