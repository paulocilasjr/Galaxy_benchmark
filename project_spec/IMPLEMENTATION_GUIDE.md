# Implementation Guide

## Architecture

The benchmark should be implemented as a pipeline with six major subsystems:

1. **Task Registry**
   - Loads benchmark tasks from structured JSON/YAML files
   - Validates tasks against `schemas/task.schema.json`

2. **Prompt Generator**
   - Creates or loads three prompt variants per task
   - Ensures semantic equivalence across prompt levels
   - Validates prompt files against `schemas/prompt.schema.json`

3. **Environment Runner**
   - Standardizes execution in:
     - `open`
     - `galaxy`
     - `galaxy_skills`
   - Returns a run record with outputs, traces, artifacts, and metadata

4. **Agent Adapter Layer**
   - Wraps each agent behind a consistent interface:
     - `prepare(task, prompt, environment)`
     - `execute()`
     - `collect_outputs()`

5. **Evaluation Engine**
   - Computes component-level scores
   - Computes run-level performance
   - Computes task-level prompt-weighted scores
   - Computes robustness, adaptability, and user-level confidence

6. **Report Generator**
   - Produces per-run, per-task, per-agent, and benchmark summary outputs
   - Separates simulated harness runs from publication-eligible benchmark runs
   - Captures normalized execution context needed for live-Galaxy drift interpretation

## Recommended implementation order

### Phase 1
- Implement JSON schemas
- Create schema validation in CI

### Phase 2
- Create example task and prompt files
- Build task loader and prompt loader

### Phase 3
- Build environment abstraction
- Build stub agent adapters

### Phase 4
- Build run orchestration over all task × prompt × environment combinations

### Phase 5
- Implement scoring functions from `evaluation/SCORING_SPEC.md`

### Phase 6
- Generate reports and benchmark summary artifacts

## Minimal execution contract

Every environment runner must return:
- `status`
- `outputs`
- `artifacts`
- `trace`
- `timing`
- `failure_modes`

Every run must be reproducible from:
- task spec
- prompt spec
- environment spec
- agent id
- random seed if applicable
