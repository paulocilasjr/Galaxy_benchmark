# Galaxy Agent Benchmark Specification Bundle

This directory is retained as an internal specification scaffold for implementation work. It is not the canonical published benchmark definition for the Galaxy Benchmark release in this repository.

This bundle contains a project-ready specification scaffold for implementing the Galaxy Agent Benchmark.

Included:
- `PROJECT_SPEC.md`: benchmark overview and architecture
- `IMPLEMENTATION_GUIDE.md`: developer-oriented implementation details
- `schemas/`: JSON Schemas for tasks, prompts, runs, and benchmark reports
- `evaluation/SCORING_SPEC.md`: scoring formulas and code-ready pseudocode
- `examples/`: example task, prompts, run record, and report outputs
- `tasks/README.md`: task authoring guide
- `prompts/README.md`: prompt authoring guide
- `environments/README.md`: environment abstraction spec
- `agents/README.md`: agent adapter spec
- `skills/README.md`: Galaxy Skills support spec
- `reports/README.md`: reporting/output expectations

Suggested first implementation order:
1. Validate example JSON files against the schemas
2. Build run orchestration for task × prompt × environment
3. Implement run-level scoring
4. Add task-level aggregation
5. Add benchmark-level aggregation and reports
