# Token-usage reduction experiment (BixBench, October 2026)

This folder holds the lab's supplementary experiment on reducing Galaxy token use. It is kept separate from the main archive: nothing here changes `BixBench_50/`, the run-link workbooks or any analysis table.

## Experiment

- **Runs:** GPT-5.6 Sol (high reasoning, Fast service tier) on the 50 BixBench-Verified-50 tasks in the Galaxy-API code condition, three new replicates, 150 runs. Workers used only the benchmark's Galaxy tools; account-connected tools were disabled.
- **Interface changes:**
  - shorter successful replies;
  - deduplicated outputs and schemas;
  - generic submission templates;
  - fewer false parameter-mismatch retries;
  - longer waits between model requests.

  The site describes them under "What changed in the third optimization round". Savings were not measured for each change separately.
- **Software:** Codex CLI 0.156.0; the baselines used 0.146.0.
- **Source:** goeckslab.github.io/galaxy-agent-benchmark/bixbench/token-optimization-oct2026/, with traces in the private HF dataset `goeckslab/galaxy-agent-benchmark-run-traces`, folder `bixbench/run_traces_october06_codex_gpt56_sol_token_optimization` at revision `4def1c34763afd79d6271ffe86663d3d6be2a426`.

Site summary (tokens are input plus output; cached input is part of input):

| Stage | Replicates | Mean tokens per 50-task run | Relative to open-ended code |
|---|---:|---:|---:|
| Open-ended code (archived Sol runs) | 3 | 35.51M | 1.00× |
| Previous Galaxy (archived Sol runs) | 3 | 122.41M | 3.45× |
| Intermediate round (`mcp_v2`, statistics only) | 1 | 85.93M | 2.42× |
| Final optimized Galaxy (this batch) | 3 | 54.35M | 1.53× |

The final batch: 137 of 150 runs passed; replicates 46, 46 and 45 of 50.

## Contents

| Path | Contents |
|---|---|
| `collect_token_optimization.py` | Rebuilds everything here (`snapshot`, `inventory`, `batch`, `collect`, `verify`). Run from the repository root with `HF_TOKEN` and `GALAXY_API_KEY` in the environment. |
| `site_snapshot/` | The experiment page, `summary.json` (per-run results and stage statistics) and the 50 item pages, with SHA-256 in `manifest.json`. |
| `run_inventory.csv` | Every run card on the 50 item pages: 1,650 runs. |
| `token_optimization_runs.csv` | The 150 new runs from `summary.json`: pass, answer, input, cached input and output tokens, trace path, history ID, and whether the history is published or importable. |
| `token_optimization_oct2026_links.xlsx` | The run-link workbook the collector reads (150 rows). |
| `hf_batch/` | Batch-level files from the HF folder (README, token comparison, file and run indexes, protocol), with hashes in `manifest.json`. |
| `analysis/<task>/` | One package per task, built by `analysis_execution/run.py` in the same layout as `BixBench_50/analysis` (details below). |
| `verification.json` | Per run: whether the collected answer and token usage match `summary.json`, and whether the Galaxy history was retrieved. |

Each `analysis/<task>/` package holds:
- the three runs' trace folders under `source_snapshots/huggingface_traces/files/galaxy_codex_gpt_5_6_sol_token_optimization_oct_2026_r{1,2,3}/`;
- the Galaxy history snapshots under `source_snapshots/galaxy/<history_id>/`;
- `history_analysis_evidence.json` and `history_analysis.md`.

`run_inventory.csv` has one row per run card, in three groups:
- **`token_optimization_oct2026`:** the 150 new runs, stored in `analysis/`.
- **`archive_galaxy` and `archive_open_ended_code`:** 750 runs each, five model configurations × 3 replicates per task. These are the runs of the main archive. Their trace and history links are identical to the archived ones (`links_match_archive`), so they are not copied again; `local_path` points to `BixBench_50/analysis/...`. Their tokens and pass status come from the archive's run summaries.

## Collection result (2026-10-06)

- **Answers and tokens:** all 150 runs' submitted answers and input, cached-input and output token counts match `summary.json` exactly (`verification.json`).
- **Traces:** all 150 retrieved with every file except `galaxy_execution_records.tar.gz` (see the notes below). That is why every trace manifest says `partial`.
- **Galaxy histories:** 142 of 150 complete.
  - Seven bix-12 histories (q2, q4, q5 and q6) have 505 to 1,517 items, above the collector's 300-item limit (the same limit as the main archive), so only their history metadata is kept.
  - bix-43-q4 replicate 3 has all 5 job records, but one small output file failed to download.
- **Size:** 143 MB.

## Notes for the analysis

- **Baselines:** the site's baselines are the archived GPT-5.6 Sol runs, which are the `archive_*` rows with model `Codex GPT-5.6 Sol`. They differ from the new runs in the Codex CLI version and in the interface, so the comparison is observational, batch against batch.
- **Per-request detail:** each new run's folder has `native_api_usage.json` (per-request usage) and `execution_records_index.json`. It also has `galaxy_execution_records.tar.gz`, the full Galaxy requests, replies and job details that the shortened conversation no longer shows.
  - The collector does not keep binary archives, which could conceal credentials, so the tarballs are listed with their hashes in each run's manifest but not stored.
  - They can be fetched separately if a later analysis needs them.
- **Run selection:** the HF batch manifest records which attempt was kept for each item; original attempts were kept by the lab, not published.
- **Access:** the histories are importable by link but not published. The trace dataset is private, and this repository is public, so decide before committing the trace folders.
