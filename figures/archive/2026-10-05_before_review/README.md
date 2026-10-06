# Figures before the figure review (2026-10-05)

Snapshot of Figures 1–5 as approved after the outline-v2 reorganization and before the changes requested in `figure_review.md` (kept here alongside them).
These are the versions in pull requests #4 (Fig. 1), #5 (Fig. 2), #6 (Fig. 3), #10 (Fig. 4) and #7 (Fig. 5) of the manuscript repository at the time of the snapshot.

| Figure | Title | Panels |
|---|---|---|
| 1 | Study design and isolated execution pipeline | a benchmarks, design and evaluation; b isolated execution pipeline |
| 2 | Agents maintain bioinformatics accuracy when operating through Galaxy | a accuracy bars by benchmark and model; b difference by benchmark; c 4 × 4 paired matrix; d causes by incorrect runs in the set |
| 3 | Galaxy provides a structured environment for agent analyses | a tasks completed by domain; b routes; c error types by channel; d recovery curves; e parameter checks; f what would prevent failed requests |
| 4 | Task solution variability is model-dependent | a tools per model; b same answer by model; c trajectory similarity and task accuracy; d random or systematic wrong answers |
| 5 | Galaxy increases analysis inspectability at higher token cost | a accuracy and token trade-off; b correct and incorrect runs; c tokens against actions; d interface requests and replies |

To regenerate one of these, copy its `make_fig*.py` back into `figures/` first: the scripts locate the repository root relative to their own folder and write into `figures/`.
