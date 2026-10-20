# Repository layout (re-organized 2026-10-14)

On 2026-10-14 the top-level folders were grouped by purpose. File contents inside the moved folders are unchanged. The only edits are path references in code and documentation, listed at the end.

| Before | Now |
|---|---|
| `experiments/`, `ground_truth/`, `dataset/` | `benchmark/experiments/`, `benchmark/ground_truth/`, `benchmark/dataset/` |
| `BixBench_50/`, `CompBio/`, `IWC/` | `runs/BixBench_50/`, `runs/CompBio/`, `runs/IWC/` |
| `token_improvment/` | `runs/token_optimization/` |
| `analysis_execution/` | `analysis/analysis_execution/` |
| `scripts/` | `analysis/scripts/` |
| `BixBench50_CompBio_analysis/` | `analysis/BixBench50_CompBio_analysis/` |
| `analysis_reports/galaxy_improvement_20260924/` | `analysis/galaxy_improvement_20260924/` |
| `manuscript_material/`, `manuscript_narrative/`, `result_evaluation/` | `manuscript/manuscript_material/`, `manuscript/manuscript_narrative/`, `manuscript/result_evaluation/` |
| `Journal.md`, `HISTORY_ANALYSIS_INSTRUCTIONS.md` | `docs/` |
| `Result_table.md`, `Galaxy_improvement_report.md`, `individual_error_analysis.md`, `individual_error_analysis_codex.md` | `docs/reports/` |
| `figures/`, `README.md`, `AGENTS.md`, `SKILL.md` | unchanged; `figures/scored_runs.csv` keeps its path because the manuscript repository reads it |

New: [analysis/site_verification/](../analysis/site_verification/), [analysis/integrity_audit/](../analysis/integrity_audit/), and a README in each top-level folder.

## Records that still use the earlier paths

These are evidence or frozen outputs. They were left unchanged so that their hashes and provenance stay valid. Read their paths through the table above.

- **Run evidence.** Everything under `runs/*/analysis/` (`history_analysis_evidence.json`, `run_manifest.json`, `input_manifest.json`, task reports, snapshots, ledgers). The workbook paths in their provenance fields are absolute paths on the collection machine.
- **Frozen analysis data.** In `analysis/galaxy_improvement_20260924/`: `run_index.json`, `trace_inventory.json` and the other derived JSON. In `manuscript/manuscript_narrative/`: `release_manifest.json`, `package_validation.json` and `submission_validation.json`. In `manuscript/manuscript_material/`: `figure_data.json` and `source_data/`.
- **Pilot package.** `runs/BixBench_50/bix-11-q1/history_analysis.md` links to `../../experiments/BixBench/task_1.json`, which is now `benchmark/experiments/BixBench/task_1.json`.

Code that reads paths out of these records maps them on the fly:
- `narrative_common.path()` in `manuscript/manuscript_narrative/`;
- `result_table_deep_analysis.py` and `audit_bixbench50_overview.py` in `analysis/scripts/`;
- `build_report.py` in `analysis/galaxy_improvement_20260924/`;
- `old_path()` in `runs/CompBio/reruns_20261005/check_unchanged.py`, which reads files at the pre-layout commit `7ed8048c9`.

## What was edited

- **Code.** Paths into moved folders were updated in every script, and so was each script's route back to the repository root, since folders are one level deeper.
- **Documentation.** Relative Markdown links were recomputed for the new locations, and root-relative paths in prose and commands were updated.
- **Benchmark task files.** Input paths now point to `benchmark/dataset/...`.
- **Run summaries.** `manuscript/manuscript_material/source_data/derived/run_summaries.jsonl.gz` stores absolute trace paths, which the figure scripts open; they were rewritten to the new locations.
- **Tables in `runs/token_optimization/`.** The `local_path` column of `run_inventory.csv` and `token_optimization_runs.csv`.
- **Rebuilt outputs.** `analysis/BixBench50_CompBio_analysis/` and `docs/reports/Result_table.md` were rebuilt. The rebuild is identical except for paths and the hashes of the edited sources.
- **`.gitignore`.** The ignored large CompBio input moved to `runs/CompBio/...`.

Checks run after the move:
- every Python file parses;
- `figures/make_scored_runs.py` reproduces `figures/scored_runs.csv` byte for byte;
- all figure scripts reproduce their source data and panel data byte for byte;
- the IWC, BixBench and CompBio audits reproduce their outputs, except for the recorded hashes of the edited scripts;
- no Markdown link broke apart from the pilot-package link above;
- the collector's unit tests pass except two that already failed before the move (they assert values from before the 2026-10-05 CompBio reruns).
