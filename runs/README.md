# Run archives

Evidence of the completed agent runs, one folder per benchmark. Each task has a package under `<benchmark>/analysis/<task>/`, built by the read-only collector in [analysis/analysis_execution/](../analysis/analysis_execution/):

- `source_snapshots/huggingface_traces/files/<run_id>/`: the run as published on Hugging Face. It holds the prompt, agent trace (`codex_events.jsonl` or `claude_events.jsonl`), answer, `run_record.json` and evaluation files.
- `source_snapshots/galaxy/<history_id>/`: the run's Galaxy history snapshot.
- `job_ledgers/`, `selected_outputs/`, `recovered_code/`: derived evidence.
- `history_analysis_evidence.json`, `history_analysis.md`: the validated evidence record and report.

Treat these packages as immutable evidence. Their manifests record SHA-256 hashes, and some records still name the paths used before the 2026-10-14 re-layout ([docs/REPOSITORY_LAYOUT.md](../docs/REPOSITORY_LAYOUT.md)).

| Folder | Runs | Notes |
|---|---|---|
| [BixBench_50/](BixBench_50/) | 1,500: 50 tasks × 5 model configurations × 2 conditions × 3 replicates | The DeepSeek-via-Claude-Code configuration is superseded and not part of the primary set. Overview: `bixBench50_overview.md`. |
| [CompBio/](CompBio/) | 2,500: 100 tasks × 4 configurations × 2 conditions × 3 replicates, plus 100 GPT-6 Astra open-ended runs | 53 Galaxy runs were replaced by reviewed reruns on 2026-10-05 ([reruns_20261005/](CompBio/reruns_20261005/)); each original is kept under `analysis/<task>/versions/pre_rerun_20261005/`. 12 Galaxy runs have no archived trace. |
| [IWC/](IWC/) | 240: 10 workflow tasks × 4 configurations × 2 conditions × 3 replicates | The scores are in `iwc_scientific_audit.json`. The results site replaced the 24 wf_007 runs on 2026-10-12 ([replacement_wf007_20261012/](IWC/replacement_wf007_20261012/)). The archive holds only the superseded runs' traces. |
| [token_optimization/](token_optimization/) | 150: GPT-5.6 Sol, BixBench Galaxy condition, October 2026 | Supplementary token-use experiment ([README](token_optimization/README.md)). |

Each benchmark folder also holds its run-link workbook (`*_execution_condition_links.xlsx`), overview and recovery summaries, and solution-path analysis. Per-run scores used by the figures are in [figures/scored_runs.csv](../figures/scored_runs.csv). [analysis/site_verification/](../analysis/site_verification/) checks them against the public results site. [analysis/integrity_audit/](../analysis/integrity_audit/) lists rule breaks found in the traces.
