# Analysis

Code and outputs that read the run archives in [runs/](../runs/). Run every script from the repository root.

| Folder | Contents | Status |
|---|---|---|
| [analysis_execution/](analysis_execution/) | Read-only collector: reads a run-link workbook, downloads traces and Galaxy history snapshots, writes and validates the per-task evidence packages in `runs/*/analysis/`. Unit tests in `tests/`. | Current |
| [scripts/](scripts/) | Benchmark audits (`audit_bixbench50_overview.py`, `audit_compbio_overview.py`, `enrich_compbio_evidence.py`, `summarize_bixbench50_recovery.py`) and the cross-benchmark result tables (`build_result_tables.py`) | Current |
| [site_verification/](site_verification/) | Comparison of the archive with the public results site | 2026-10-14 |
| [integrity_audit/](integrity_audit/) | Rule breaks and behaviour outside the spirit of the benchmark, for every archived run | 2026-10-14 |
| [BixBench50_CompBio_analysis/](BixBench50_CompBio_analysis/) | Cross-benchmark analysis behind [docs/reports/Result_table.md](../docs/reports/Result_table.md) (`analysis.json`, `source_manifest.json`) | Rebuilt 2026-10-14 without changes; archive scores |
| [galaxy_improvement_20260924/](galaxy_improvement_20260924/) | Trace audit of Galaxy failures behind [docs/reports/Galaxy_improvement_report.md](../docs/reports/Galaxy_improvement_report.md); `v2_trace_friction/` holds the failure ledger that Fig. 2 reads | Frozen 2026-09-25 |
