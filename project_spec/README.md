# Galaxy-Bench v0.3 Specification Bundle

This directory is the internal implementation scaffold for the benchmark redesign.

It is aligned to the v0.3 benchmark logic:

- compare standalone execution with Galaxy-augmented execution
- compare `single_run` and `multi_run` settings
- preserve the three-score run vector
- add mechanistic operational metrics
- add explicit iteration metrics and best-of-N reporting
- support multiple acceptable scientific solutions
- support human-informed scientific acceptability review
- add robustness and confidence-calibration endpoints
- require lossless execution traces

Included:

- `PROJECT_SPEC.md`: benchmark architecture and scientific rationale
- `IMPLEMENTATION_GUIDE.md`: implementation roadmap
- `schemas/`: task, prompt, run, and report schemas
- `evaluation/SCORING_SPEC.md`: endpoint definitions and aggregation rules
- `examples/`: v0.3-shaped example assets
- `tasks/README.md`: task authoring guidance
- `prompts/README.md`: prompt authoring guidance
- `environments/README.md`: environment abstraction guidance
- `agents/README.md`: agent adapter guidance
- `skills/README.md`: skills/environment support guidance
- `reports/README.md`: report and publication-output guidance

This bundle should be treated as the source of truth for implementation work when the legacy repository shape and the v0.3 benchmark logic diverge.
