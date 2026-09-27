# Code availability

All analysis code is available at https://github.com/paulocilasjr/Galaxy_benchmark [Authors: archive a tagged release on Zenodo and cite its DOI here]. The code covers the trace-level audit and the generation of every figure, table and data file in this paper.

The trace-level audit is in `analysis_reports/galaxy_improvement_20260924/v2_trace_friction/`:
- trace extraction;
- classification of failed Galaxy interface calls by cause;
- detection of parameter substitution and of direct Galaxy API calls;
- the failure ledger;
- the divergence-mechanism analysis of split replicate sets.

The cross-benchmark statistics and archive tables are in `BixBench50_CompBio_analysis/`. The bootstrap uses 20,000 resamples with seed 20260922 (Python 3.12.13, NumPy 2.4.1).

Figure, table and supplement generation is in `manuscript_material/scripts/`:
- `build_data.py` assembles all panel data from the archive;
- `fig_main.py` and `fig_ed.py` render the figures and their Source Data;
- `make_supplement.py` builds the Supplementary Tables, Supplementary Data and Supplementary Information;
- `glossary.py` holds the official terminology used in every figure, table and data file;
- `md_to_docx.py` converts the legends and statements to Word files.

The analysis is read-only: it executes no agent code and contacts no Galaxy server. The Galaxy interface (Model Context Protocol server) and agent harnesses used to generate the runs are [Authors: cite repository and version].
