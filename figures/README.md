# Manuscript figures (current)

The current figure set and the per-run score table behind it. The manuscript repository (goeckslab/agent-galaxy-benchmark-manuscript) reads `scored_runs.csv` and the panel data from here, so this folder keeps its path.

## Build

Every per-run score matches the public results site. `make_scored_runs.py` writes `scored_runs.csv` from the archive and `site_snapshot/`, and stops on any mismatch. Then run the figure scripts, which need the plotting stack pinned in `manuscript/manuscript_material/scripts/requirements.txt` (Python 3.12):

```sh
python figures/make_scored_runs.py          # --fetch refreshes site_snapshot/ from the live site
python figures/make_answer_exposure.py      # answer_exposure_tiers.csv
python figures/make_udt_methods.py          # udt_methods.csv
python figures/make_supp_table_design.py    # supp_table_design.csv/.md
python figures/make_failure_episodes.py     # failure_episodes.csv
python figures/make_wf003_errors.py         # wf003_*.csv
python figures/make_fig1_a.py; python figures/make_fig2.py; python figures/make_fig3.py
python figures/make_fig4.py; python figures/make_fig5.py; python figures/make_ed_validation.py
```

Each figure script writes `<figure>.pdf/.png/.svg`, `<figure>_legend.md`, `<figure>_source_data.csv` and `panel_data/<script>.json`.

## Files

| File | Contents |
|---|---|
| `scored_runs.csv` | 3,840 primary runs on 160 tasks with the score the site displays, the archive score and its source |
| `site_snapshot/` | Per-run grades fetched from the site (no answers) |
| `replaced_runs.py` | IWC wf_007: the runs the site replaced on 2026-10-12, and how figures take them |
| `make_fig1_a.py` … `make_fig5.py`, `make_ed_validation.py` | Figures 1–5 and Extended Data Figs 2–7 |
| `make_answer_exposure.py`, `answer_exposure_tiers.csv` | Each run's exposure to published reference answers (verified / probable / attempted / none). [analysis/integrity_audit/](../analysis/integrity_audit/) extends it to every rule. |
| `make_udt_methods.py`, `make_failure_episodes.py`, `make_wf003_errors.py`, `make_supp_table_design.py` | Supporting tables |
| `annotations/` | Coded samples (codebooks A1, A2, D) used by Extended Data Fig. 6 |
| `panel_io.py`, `panel_data/`, `port_figures.py` | Panel data and the port of the drawing code to the manuscript repository |
| `compare_source_data.py`, `source_data_changes/` | Differences from the previous figure set |
| `figure_review.md`, `figure_review_response.md` | The 2026-10-05 review and response |
| `archive/` | Earlier figure sets (2026-10-05 ×2, 2026-10-07 before site scores) |
