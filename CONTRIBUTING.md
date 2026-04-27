# Contributing

## Scope

This repository mixes benchmark assets, hidden scoring metadata, and implementation tooling. Contributions should preserve the benchmark contract before they optimize convenience or code structure.

## Contribution Rules

1. Do not change the scientific meaning of an existing experiment tier without updating the paired hidden metadata and documenting the rationale.
2. Preserve prompt-tier alignment across `low_context`, `medium_context`, and `high_context`.
3. Keep benchmark-science changes and tooling/refactor changes in separate commits when possible.
4. Do not commit secrets, local credentials, or ad hoc benchmark outputs intended only for private runs.
5. Run the local validation suite before opening a pull request:
   - `make test`
   - `make scorer-test`
   - `make audit`

## Benchmark-Facing Changes

Changes to benchmark assets or scoring behavior should include:

- a short rationale
- expected effect on scientific scoring, standard-analysis scoring, and agent-in-Galaxy execution scoring
- whether historical results remain comparable
- whether a benchmark version bump is required

## Release Expectations

Publication-facing changes should keep these files current:

- `README.md`
- `docs/benchmark_card.md`
- `docs/publication_release.md`
- `docs/dataset_governance_manifest.json`
- `CITATION.cff`
