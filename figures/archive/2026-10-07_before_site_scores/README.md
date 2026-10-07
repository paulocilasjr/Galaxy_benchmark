# Figures before site-matched scores (2026-10-07)

Snapshot of Figures 1–5 and Extended Data Figures 2–7 before every run was scored as the public results site shows it (https://goeckslab.github.io/galaxy-agent-benchmark/).
These are the versions in pull requests #4 (Fig. 1), #5 (Fig. 2), #6 (Fig. 3), #10 (Fig. 4), #7 (Fig. 5) and #11 (Extended Data Figs 2–7) of the manuscript repository at commit b3cbb94 of this archive, before this update.

What changed afterwards (see `figures/figure_review_response.md`, section "Scores matched to the results site"):
- the IWC host-read removal task is scored (3,840 runs on 160 tasks, was 3,816 on 159);
- BixBench-Verified-50 grades follow the site, which regraded bix-53-q2 and bix-43-q2 (27 runs);
- the population sensitivities of Extended Data Fig. 2b are recomputed;
- the 71% in the Fig. 3f and Extended Data Fig. 6d subtitles (a pandas-3 bug) became 89%.

These scripts read `manuscript_narrative/original_layout/analysis/accuracy_primary_runs.csv`. To regenerate one of them, copy its `make_*.py` back into `figures/` first: the scripts locate the repository root relative to their own folder and write into `figures/`.
