# Publication And Release Policy

## Purpose

This document records the repository's publication-facing release expectations for reproducibility, baselines, uncertainty reporting, and live-Galaxy drift.

## Reproducibility Standard

For publication releases, the target is:

- Bronze: data references, code, and scoring logic are archived and citable
- Silver: dependencies and validation commands are documented and runnable with one setup path
- Gold: benchmark validation can be reproduced with a single command path in a pinned environment

Repository support for this policy includes:

- `pyproject.toml`
- `Dockerfile`
- `Makefile`
- `.github/workflows/ci.yml`
- `tools/audit_benchmark_assets.py`
- `tools/build_reliability_report.py`
- `tools/build_publication_results_bundle.py`
- `tools/build_release_packages.py`

## Baselines And Uncertainty

Publication-facing benchmark results should not be reported from a single run per task unless the paper explicitly frames them as illustrative only.

Minimum recommendation:

- at least 3 repeated runs per benchmark instance for stochastic agents
- report mean, standard deviation, and 95% confidence interval
- preserve the three-score vector in all tables
- report failure counts and non-completions separately from successful scored runs

The repository provides `tools/build_reliability_report.py` to summarize repeated `run_record.json` artifacts.

The canonical machine-readable publication summary lives in:

- [docs/publication_results_source.json](/Users/4475918/Projects/Galaxy_benchmark/docs/publication_results_source.json)
- [docs/publication_results_bundle.json](/Users/4475918/Projects/Galaxy_benchmark/docs/publication_results_bundle.json)
- [docs/publication_results_summary.md](/Users/4475918/Projects/Galaxy_benchmark/docs/publication_results_summary.md)

## Dataset Governance

All benchmark inputs should have:

- stable source identifiers
- citation metadata
- access date
- checksum when mirrored or stored locally
- persistence policy
- redistribution note or license note

The current governance registry lives in:

- [docs/dataset_governance_manifest.json](/Users/4475918/Projects/Galaxy_benchmark/docs/dataset_governance_manifest.json)

## Live-Galaxy Drift Policy

Because the benchmark executes against a live Galaxy instance, releases should record the execution context needed to interpret drift:

- Galaxy instance URL
- run date
- workflow identifiers and revision metadata when available
- tool IDs and versions when available
- key queue/scheduler blockers when they materially affected a run
- any benchmark-level tolerances invoked because of workflow or tool drift

When a live-Galaxy change affects comparability:

1. preserve the old release assets
2. document the drift in the release notes
3. bump the benchmark version if the scoring-relevant contract changed
4. prefer additive tolerances over silent ground-truth rewrites

## Public Release Boundary

For an external benchmark release:

- publish public tasks, dataset references, documentation, tooling, and schemas
- keep blind scoring assets separate if the release is meant to support ongoing blind evaluation
- exclude local credentials and developer-only configuration
- exclude committed run artifacts under `outputs/`; keep only the placeholder directory in the public blind package

Release-package staging command:

```bash
python3 tools/build_release_packages.py --output-dir /tmp/galaxy_benchmark_release
```

## Governance Metadata

Publication releases should update:

- `CITATION.cff`
- `README.md`
- `docs/benchmark_card.md`
- `docs/dataset_governance_manifest.json`
- this document

## Release Checklist

Before tagging a benchmark release:

1. Run `make test`
2. Run `make scorer-test`
3. Run `make audit`
4. Rebuild any publication summary tables from current scored run records
5. Rebuild `docs/publication_results_bundle.json` and `docs/publication_results_summary.md`
6. Verify that dataset-governance entries cover every public benchmark input
7. Verify that benchmark-facing docs still match the implemented runtime contract
