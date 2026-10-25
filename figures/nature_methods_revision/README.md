# Nature Methods figure revision

Revises the attached Brief Communication Fig. 1 only. Originals remain untouched.

Build from the repository root:

```
.venv/bin/python figures/nature_methods_revision/make_figure.py
```

Outputs: editable SVG, vector PDF with embedded TrueType text, 600 dpi PNG, screen preview, and plotted estimates CSV. Canvas: 183 × 111 mm; Arial 5–7 pt, with 8 pt bold panel labels.

Design references reviewed on 22 October 2026:
- Nature research figure specifications: https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/
- Liu et al., Nature Methods (2025), “Benchmarking methods for mapping functional connectivity in the brain,” Fig. 1: https://www.nature.com/articles/s41592-025-02704-4

The revision simplifies the workflow, uses black labels with blue/orange condition keys, aligns the three forest plots and separates pooled estimates. It removes background gridlines and the original unexplained ±5 percentage-point shading; no equivalence claim is introduced.

Data are read from figures/fig2_source_data.csv and figures/scored_runs.csv, exactly as in the source Brief Communication script. Estimates and confidence intervals are preserved; IWC percentages are converted to agreement units by division by 100. No ground-truth files were accessed and no inferential statistics were recomputed. The full manuscript legend is still needed to define the estimator, clustering and bootstrap procedure.
