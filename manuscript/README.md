# Manuscript builds

The current figures are in [figures/](../figures/). The manuscript text is in the separate repository goeckslab/agent-galaxy-benchmark-manuscript.

| Folder | Contents | Status |
|---|---|---|
| [result_evaluation/](result_evaluation/) | Panel-by-panel evaluation of the current figures (`Galaxy_benchmark_figure_evaluation.pdf/.docx`). It holds a self-contained copy of the figure pipeline, lab-meeting figures, and a presentation deck with its figures. `integrity_scan/` holds the first answer-source scan. | Current (October 2026) |
| [manuscript_material/](manuscript_material/) | Display items, Supplementary Tables, Source Data and statements built for the September Results text. `source_data/derived/run_summaries.jsonl.gz` (per-run trace summaries) is still read by the figure scripts. | Frozen 2026-09-28; uses archive scores, not the site-matched ones |
| [manuscript_narrative/](manuscript_narrative/) | Two narrative drafts (user-oriented, galaxy-oriented) and the original-layout package. `original_layout/analysis/` holds the per-run accuracy, token and UDT tables that the figure scripts read. | Frozen 2026-10-02 |

The frozen builds were not updated to the 2026-10-07 site-matched scores. For per-run scores use `figures/scored_runs.csv`.
