# Figures before the outline-v2 redesign (2026-10-05)

Snapshot of Figures 1–4 as approved before they were reorganized to follow the Results outline in `agent-galaxy-benchmark-manuscript/manuscript/outline.md` (commit `c22f7ef`, 2026-10-05).
These are the versions in pull requests #4 (Fig. 1), #5 (Fig. 2), #6 (Fig. 3) and #7 (Fig. 4, after commit `20cb790`) of the manuscript repository.

| Figure | Title | Panels |
|---|---|---|
| 1 | Study design and isolated execution pipeline | a benchmarks and design; b isolated execution pipeline |
| 2 | Galaxy matches agent performance with open-ended code | a accuracy by model; b replicate sets with 3/3 correct; c accuracy by benchmark and model in Galaxy; d 15 most used Galaxy tools |
| 3 | Galaxy records trace most failures beyond the workbench | a replicate sets with 1, 2 or 3 incorrect runs; b recovery from execution errors; c causes of incorrect BixBench runs; d majority vote |
| 4 | Galaxy trades input tokens for analysis provenance | a replicate scatter of accuracy against input tokens; b incorrect versus correct runs; c tokens against actions; d what Galaxy requests and replies were for |

To regenerate one of these, copy its `make_fig*.py` back into `figures/` first: the scripts locate the repository root relative to their own folder and write into `figures/`.
