# Result evaluation: figure-by-figure evidence

`Galaxy_benchmark_figure_evaluation.pdf` (and `.docx`) presents every panel of the figures on its own page:

1. a title, phrased as the question the panel answers;
2. the panel image;
3. the rationale: the data and their source, the variables plotted, the estimators, intervals and tests, and how to read the plot;
4. the conclusion: what the evidence shows in answer to the title, and where its inference stops.

It covers 43 panels: 5 main figures and 6 Extended Data figures (Fig. 1–5, Extended Data Fig. 2–7).

The figures are regenerated in `figures/` inside this folder. Every run carries the score that the public results site displays (https://goeckslab.github.io/galaxy-agent-benchmark/), and the IWC host-read removal task is included. All 3,840 primary runs on 160 tasks are scored. The repository's `figures/` holds the same updated set. `figures/README.md` lists every difference from the earlier set, which is kept in the repository's `figures/archive/2026-10-07_before_site_scores/`.

## Files

| Path | What it is |
|---|---|
| `Galaxy_benchmark_figure_evaluation.pdf`, `.docx` | The document. |
| `figures/` | The regenerated figures: PNG, PDF and SVG, plus Source Data, legends and the scripts that make them. Read its `README.md` first. |
| `figures/scored_runs.csv` | The per-run scores every figure uses, matched to the results site, with the archive's value and the source of each score. |
| `figures/site_snapshot/` | Grades and values read from the results site (no answers), used by `make_scored_runs.py`. |
| `figures/source_data_changes/` | Every Source Data value that differs from the earlier figure set. |
| `text/*.md` | The text of each figure and panel (title question, rationale, conclusion). Edit these and rebuild. |
| `panels/<id>.png`, `.pdf` | One image per panel, split from `figures/`, e.g. `fig2b`, `ed4e`. `panels/manifest.csv` lists them. |
| `split_panels.py` | Writes `panels/` from the figure scripts and their recorded panel data. |
| `build_document.js` | Writes the DOCX from `text/` and `panels/` (npm package `docx`). |
| `build.py` | Runs panels, DOCX, PDF (LibreOffice) and a second pass that adds page numbers to the contents. |
| `figure_consistency_notes.md` | The run-result audit (site, run records, traces, histories) and inconsistencies found in legends, figures and Source Data. |
| `build/` | Intermediate files: page numbers, heading anchors, build stamp. |

## How the panels were made

The panels are not cropped from the PNGs.
`split_panels.py` imports each figure script in `figures/` and replays the drawing calls recorded in `figures/panel_data/*.json`, so no estimate is recomputed.
While a figure is redrawn, the artists each panel adds are tracked. A panel is one drawing call (`draw_a`, `ed_census`, …), or, for Extended Data Figs 6–7, everything drawn from one `label()` call to the next.
Each panel is then saved alone with a tight bounding box.
Fig. 1 is a single millimetre canvas, so its two panels are cut at the gap between them.
With `--check`, every redrawn composite is compared with its PNG; all 11 match pixel for pixel.

## Where the text comes from

Each panel's text was written from the figure's legend (`figures/*_legend.md`), the methods in its script, its Source Data (`figures/*_source_data.csv`) and the rendered panel.
Every number in the text was checked against those files.
The shared definitions (conditions, benchmarks, scoring, intervals, *P* values) are stated once, at the start of the document.

## Rebuild

From the repository root, with the figure environment (Python 3.12, `manuscript_material/scripts/requirements.txt`, plus `pypdf`), Node.js with the npm package `docx`, and LibreOffice:

```bash
python result_evaluation/figures/make_scored_runs.py           # add --fetch to re-read the results site
python result_evaluation/figures/make_wf003_errors.py
python result_evaluation/figures/make_failure_episodes.py
for s in make_fig1_a make_fig2 make_fig3 make_fig4 make_fig5 make_ed_validation; do
  PANEL_DATA=1 python result_evaluation/figures/$s.py
done
python result_evaluation/build.py                              # panels, DOCX and PDF
python result_evaluation/build.py --skip-panels                # after editing text/ only
```

`build.py` looks for `docx` under `NODE_PATH` (default: the local Codex runtime's `node_modules`) and for LibreOffice as `$SOFFICE`, then `soffice` on `PATH`, then the Codex runtime's copy.
