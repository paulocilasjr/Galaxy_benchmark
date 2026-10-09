# Result-evaluation figures (scores matched to the results site)

These are the figures shown in `../Galaxy_benchmark_figure_evaluation.pdf` (and `.docx`).
They are produced by the same drawing and statistics code as the manuscript figures in `figures/`.
The differences are in the per-run scores:
- every scored run carries the score that the public results site displays (https://goeckslab.github.io/galaxy-agent-benchmark/);
- the IWC host-read removal task (wf_003) is included.

The repository's `figures/` now holds the same set: identical PNGs, Source Data and panel data. The earlier set is kept in `figures/archive/2026-10-07_before_site_scores/`.

## What changed relative to the earlier set

| | Earlier set (`figures/archive/2026-10-07_before_site_scores/`) | Here and in `figures/` |
|---|---|---|
| Scored primary runs | 3,816 on 159 tasks | **3,840 on 160 tasks** |
| IWC | 9 tasks (216 runs); wf_003 excluded | **10 tasks (240 runs)**; wf_003 scored from `run_record.json`, the value the site shows |
| BixBench-Verified-50 grades | original evaluator (`evaluation.json`) | **site grades**: bix-53-q2 accepts "increase" (18 runs now correct; the 6 DeepSeek V4 Pro runs stay incorrect, as displayed), bix-43-q2 uses platform-specific two-decimal scoring (5 runs now correct, 4 now incorrect). 27 runs differ. |
| CompBioBench grades | official leaderboard | unchanged (the site's headline scores) |
| Population sensitivities (Extended Data Fig. 2b) | read from the archive's `accuracy_sensitivities.csv` | recomputed on these scores with the primary estimator |
| Failure causes (Fig. 2d, Extended Data Fig. 2a) | run-level audit | run-level audit; the 4 bix-43-q2 runs graded incorrect only by the site take the task-level audit's cause (benchmark specification or scoring), flagged in the code |
| Verification-check outcomes (Fig. 4d, Extended Data Fig. 7a) | grade at sampling time | current grade: D079 (bix-53-q2) is now correct, so the groups hold 41 correct and 39 incorrect runs |
| Extended Data Fig. 6d and Fig. 3f subtitles | 71% (pandas-3 bug counted 30 requests without an improvement group as misses) | 89% (107 of 120), the intended statistic |

Every IWC value was checked against the site at its displayed precision, and every BixBench-Verified-50 grade against the site's table; `make_scored_runs.py` stops on any mismatch.
The run results were also verified against the traces, submitted files and Galaxy histories (see `../figure_consistency_notes.md`).

## Files

- `make_scored_runs.py`: builds `scored_runs.csv`, the per-run scores used by every script here, from the archive's `accuracy_primary_runs.csv` and `site_snapshot/` (grades and values read from the site; no answers are stored). Use `--fetch` to refresh the snapshot.
- `make_wf003_errors.py`: execution errors of the 24 wf_003 runs, extracted with the archive's own rules (`manuscript_material/scripts/fig_on_demand.py`). The archive's error tables omit the task.
- `make_fig1_a.py` … `make_ed_validation.py`, `make_failure_episodes.py`, `panel_io.py`: the scripts in `figures/`, with paths that write here. Changes from the earlier scripts are marked `result_evaluation:` in the code.
- `fig*.{png,pdf,svg}`, `ed_fig*.{png,pdf,svg}`: the figures.
- `*_source_data.csv`: every plotted value.
- `*_legend.md`: legends with the updated numbers.
- `panel_data/`: the recorded drawing calls used to split the panels.
- `compare_source_data.py` and `source_data_changes/`: every Source Data value that differs from the earlier set.

Annotations, answer-exposure tiers and UDT method classes are read unchanged from `figures/`.

## Rebuild

From the repository root, with the figure environment (`manuscript_material/scripts/requirements.txt`):

```bash
python result_evaluation/figures/make_scored_runs.py          # add --fetch to re-read the site
python result_evaluation/figures/make_wf003_errors.py
python result_evaluation/figures/make_failure_episodes.py
for s in make_fig1_a make_fig2 make_fig3 make_fig4 make_fig5 make_ed_validation; do
  PANEL_DATA=1 python result_evaluation/figures/$s.py
done
python result_evaluation/build.py                             # panels, DOCX and PDF
```
