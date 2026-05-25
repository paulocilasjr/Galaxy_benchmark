# Galaxy Benchmark Agent Guide

Read this file first when you enter the repository. Its purpose is orientation only: it explains what this project is, where the important files live, and which document to read next.

## What This Project Is

Galaxy Benchmark evaluates whether an agent can turn a biomedical analysis request into a scientifically useful, auditable Galaxy-based execution.

The benchmark is designed to test more than final-answer correctness. It also evaluates whether the agent can:

- understand a realistic biomedical task
- choose Galaxy-compatible tools and parameters
- execute through Galaxy with preserved provenance
- recover from failures without losing evidence
- produce outputs that can be compared fairly against ground truth
- preserve enough artifacts for a reviewer to audit the run later

The repository supports Nature Methods-tier evaluation claims, so changes should improve scientific realism, fairness, auditability, reproducibility, or reviewer clarity.

## Where To Go Next

- Use [README.md](/Users/4475918/Projects/Galaxy_benchmark/README.md) to understand the benchmark definition, aims, task design, and evaluation model.
- Use [SKILL.md](/Users/4475918/Projects/Galaxy_benchmark/SKILL.md) when executing any benchmark task. It contains the rules, run layout, artifact contract, tool boundaries, credential gate, scoring details, and BixBench-specific procedure.
- Use task files under `experiments/` to find the prompt and allowed inputs for a run.
- Use files under `ground_truth/` only when the evaluation procedure permits it. BixBench ground truth is hidden until the submitted answer is fixed, as specified in `SKILL.md`.
- Use `outputs/` only for benchmark execution artifacts.

If the user asks you to execute a benchmark task, read `SKILL.md` before taking any Galaxy or local execution action.

## Repository Layout

```text
.
|-- AGENTS.md
|-- README.md
|-- SKILL.md
|-- dataset/
|-- experiments/
|   |-- low_context/
|   |-- medium_context/
|   |-- high_context/
|   |-- BioAgent/
|   `-- BixBench/
|-- ground_truth/
|   |-- GalaxyBench/
|   |-- BioAgent/
|   `-- BixBench/
|-- outputs/
`-- scripts/
```

Key directories:

- `dataset/`: local datasets used by GalaxyBench-style tasks.
- `experiments/low_context`, `experiments/medium_context`, `experiments/high_context`: prompt variants for the same underlying GalaxyBench tasks.
- `experiments/BioAgent`: BioAgent-derived benchmark tasks and metadata.
- `experiments/BixBench`: BixBench task prompts and allowed input references.
- `ground_truth/`: evaluator/reference material. Treat it as controlled access, not general context.
- `outputs/`: immutable run directories created during benchmark execution.
- `scripts/`: helper scripts for repository maintenance or evaluation support.

## Task Families

GalaxyBench tasks use prompt variants across low, medium, and high context. They emphasize Galaxy workflow execution, output preservation, and multi-part scoring against prompt requirements and ground truth.

BioAgent tasks provide biomedical benchmark cases with their own experiment metadata and ground-truth metrics.

BixBench tasks are final-answer benchmarks. They still require Galaxy execution evidence, but the scientific score is binary and based on a fixed submitted answer. Do not open BixBench ground truth until the access gate in `SKILL.md` allows it.

## How To Approach Work

For benchmark execution:

1. Read this file for orientation.
2. Read the relevant experiment file under `experiments/`.
3. Read `SKILL.md` completely enough to follow the execution contract.
4. Create all execution artifacts only under a new `outputs/<timestamp>_<level>_<experiment>/` directory.

For benchmark authoring or maintenance:

- Keep prompts realistic and scientifically meaningful.
- Preserve separate scientific, prompt-compliance, ground-truth, and Galaxy-execution evaluation concepts.
- Avoid changes that collapse evidence into a single opaque score.
- Do not weaken traceability, versioning, or ground-truth discipline.

## Reviewer Lens

When changing this repository, assume reviewers will ask:

- Is the task scientifically meaningful?
- Is the scoring fair to valid alternative solutions?
- Is Galaxy being evaluated as an execution environment, not merely mentioned?
- Can the run be reproduced and audited from preserved artifacts?
- Are failures, retries, tool choices, parameters, and outputs visible after the fact?

Good changes make those answers clear in repository artifacts, not only in prose.
