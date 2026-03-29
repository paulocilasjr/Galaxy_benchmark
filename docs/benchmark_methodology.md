# Benchmark Methodology

## Execution Model

Each task is executed as an auditable trial with:

- a canonical task definition
- a prompt variant
- an agent/access/knowledge configuration
- an immutable run directory
- outcome, process, and robustness scoring

## Required Trial Sequence

1. load a canonical task or migrate a legacy task into canonical form
2. select the agent type, access mode, and knowledge condition
3. generate or load the prompt variant
4. create a normalized run manifest
5. execute the task through the agent and Galaxy ports
6. capture plan, reasoning, events, errors, and artifacts
7. extract structured outputs
8. compare to ground truth only after result generation
9. score outcome, process, and robustness
10. aggregate per-task and per-suite summaries

## Benchmark Principles

- do not benchmark only the answer; benchmark the route to the answer
- no hidden manual steps
- no silent mutation of prior artifacts
- no direct domain dependency on SDK details or filesystem layout
- no benchmark claim without audit evidence

## Legacy Preservation

Legacy benchmark definitions are preserved inside the rebuilt tree under `benchmark/tasks/legacy/raw/` and `benchmark/ground_truth/legacy/raw/`. The canonical benchmark uses typed tasks, normalized ground truths, suite manifests, benchmark-local datasets, and immutable `runs/`.
