# Figure consistency notes (7 October 2026)

These notes cover the figures before and after every run was scored as the results site shows it. The earlier set is in `figures/archive/2026-10-07_before_site_scores/`. The updated set is in `figures/`, and is identical to `result_evaluation/figures/`, which the evaluation document shows.

## Run-result audit and what the regenerated figures use

Each run's result was compared across four sources:
- the public results site;
- the run's `run_record.json` and `evaluation.json`, both checked identical to the live Hugging Face traces;
- the archive table the manuscript figures use (`accuracy_primary_runs.csv`);
- for IWC host-read removal (wf_003), the submitted FASTQ files and the Galaxy histories.

The updated figures use the site's results (`figures/scored_runs.csv`; see `result_evaluation/figures/README.md`).

### Where the scores live

- **IWC.** `run_record.json` holds `acc`.
- **BixBench-Verified-50.** `run_record.json` is a preparation record with no score; the grade is in `evaluation.json`.
- **CompBioBench.** No per-run score file exists on Hugging Face.

### IWC host-read removal (wf_003): now included

The manuscript archive dropped this task. Two Luna Galaxy runs scored 0.273 against the Bowtie2 reference, and three GPT-5.5 custom-code runs had no score. The re-scored values in `run_record.json`, which the site shows, were independently reproduced for all 24 runs from the submitted files against the benchmark's route references.

All 12 Galaxy answers are Galaxy job outputs: 9 byte-identical and 3 with identical reads. The live data equal the archive snapshot.

Caveat: the minimap2 route reference is byte-identical to GPT-5.5 custom-code replicate 3's own submission. That run's 1.000 is therefore self-referential, and replicate 2's 0.996 is agreement with replicate 3.

### IWC wf_006 (ATAC-seq): 12 stale `run_record.json` values

For the 12 runs on route bowtie2+macs2, `run_record.json` holds 0.39–0.51. That is a single-variant score. The registry accepts the closest of three calibrated MACS2 variants, giving 0.99–1.00; this is the value in `evaluation.json`, on the site and in both figure sets.

Several wf_006 references were "calibrated from the sole complete … execution record" (route registry), so those runs' 1.0 scores are also self-referential. Extended Data Fig. 2b keeps the sensitivity analysis without these routes.

### BixBench-Verified-50: 27 primary runs regraded by the site

The site applies documented scoring corrections:
- **bix-53-q2:** "increase" is accepted, making 18 runs correct.
- **bix-43-q2:** platform-specific two-decimal scoring makes 5 runs correct and 4 incorrect.
- **bix-53-q5:** one run on the superseded harness, outside the primary set.

The site still marks the six DeepSeek V4 Pro bix-53-q2 runs incorrect, although each answered "increase". The regenerated figures keep those cells as displayed.

### CompBioBench: no change

The archive's grades sum to the official-leaderboard score of every replicate, which is the site's headline. The site's per-item table grades 114 runs on 7 items against alternative references (genome-coords, lung-cancer-sc, tissue-fibroblast, protein-shape, odd-one-out, annotate-variant-regulatory-overlap, encode-atac-pipeline), so its totals differ from its own headline. The regenerated figures follow the headline.

## Issues in the figures

Item 1 was reproduced independently. The other items were found by recomputing from the archive files or by reading the code; they have not been re-run a second time.
Item 1 is fixed in the updated figures. The other items concern legends, labels and Source Data that the update did not change, so they still apply unless stated.

## Likely errors

1. **Extended Data Fig. 6d and Fig. 3f subtitles: the 71% is a pandas-version bug; the intended value is 89%.** (Reproduced.)
   - `make_ed_validation.py: second_rater_classes()` maps classes B3, X and Z to `None` and means to drop them before computing `fix_supported`.
   - Under pandas 3.0.6, `rule.map(FIX)` turns `None` into `NaN`. `NaN` is truthy, so `if f` keeps those 30 requests, and each one scores as a mismatch.
   - The published value is 107 of 150 = 71%. The intended value is 107 of 120 = 89%.
   - The same 71% appears in the Fig. 3f subtitle ("named the same improvement for 71% of requests").
   - Fix: test `isinstance(f, str)` (or `pd.notna(f)`) instead of `if f`, then regenerate Fig. 3 and Extended Data Fig. 6.
   - **Fixed in the updated figures** (`figures/` and `result_evaluation/figures/`), which show 89%. The earlier set in `figures/archive/2026-10-07_before_site_scores/` shows 71%.

2. **Extended Data Fig. 7b, right column: weighted by failed step, not by run.**
   - The label says "Runs correct: re-run / not" and the legend says "the share of runs that ended correct". The code weights by failed step (episode).
   - Per-run values differ:

     | Channel | Published (per step) | Per run |
     |---|---|---|
     | Installed-tool jobs | 81% / 75% | 83.6% / 80.5% |
     | UDT jobs | 84% / 81% | 88.6% / 81.8% |
     | Shell, Galaxy runs | 74% / 71% | 73.4% / 77.1% |
     | Shell, custom-code runs | 71% / 76% | 79.7% / 79.9% |

   - Either relabel the column as per failed step or compute it per run.

3. **Extended Data Fig. 4c legend: the "three sets" sentence does not match the current data.**
   - The legend says rounding to three significant digits "merged distinct numeric answers in three sets; the primary task-aware rule does not".
   - Recomputed, only 1 set agrees at three significant digits but not under the task-aware rule: encode-atac-pipeline-q1, GPT-5.6 Luna, custom code.
   - The evaluation text leaves this claim out.

4. **Fig. 3f subtitle wording.**
   - "Reproduced 92% of the classes" is really the share of sampled requests given the same class: 120 of 130 in classes A1–B5. Only 8 of 13 classes matched on all 10 items.
   - "Named the same improvement" overstates the match. The rater could name several improvements, and did in 35% of requests. See also item 1.

## Labels and legends to tighten

5. **Fig. 3c draws failed Galaxy jobs from two sources.**
   - The failure shares on the left come from agent-interface call records: about 1,054 failed installed-tool jobs and 1,896 failed UDT jobs.
   - The error-type bars, the errors per run, Fig. 3d and Extended Data Fig. 3b use jobs in the error state from the archived job records: 1,433 installed-tool and 2,018 UDT job errors.
   - Shell-command counts agree between the two sources. The legend does not say there are two sources.

6. **Extended Data Fig. 2 legend.**
   - It describes the diamonds as only the per-benchmark primary means. The two IWC ≥ 0.99 rows are also drawn as bold diamonds.
   - It points to "exact sign-flip *P* values in Source Data". `ed_fig2_source_data.csv` has *P* values only for the six threshold rows; the five archive sensitivities have none.

7. **Fig. 2d "Same count (21 pairs)".** The 21 is computed in `draw_d` as equal-count pairs with at least one incorrect run. It is not in Source Data, which lists `pairs_equal` = 170, and the legend does not define it.

8. **Fig. 2b group header.** "IWC (agreement × 100)" spans both columns. In the "All three runs correct" column, the IWC rows are shares of replicate sets at ≥ 0.99, not agreement × 100.

9. **`fig4_source_data.csv`, panel b.** The two pooled-test rows are labelled "Holm over 4", but their `p_holm` values are Holm over two, as the legend says.

10. **Extended Data Fig. 6a legend.** "Most exposure came from DeepSeek V4 Pro and GPT-5.6 Luna runs, in both conditions" holds in both conditions only for DeepSeek V4 Pro (79 of 94 exposed runs, 40 Galaxy and 39 custom code). GPT-5.6 Luna has 13 exposed runs, 11 of them custom code.

11. **Untraced runs.** Twelve CompBioBench Galaxy runs have no trace. Extended Data Fig. 6a counts them as "no benchmark search" without saying so.

12. **Extended Data Fig. 7b legend, "intervals over tasks".** For BixBench-Verified-50 the clusters are the 33 analysis capsules, not tasks.

13. **Fig. 5c legend, "the agent CLI version also changed".** `token_improvment/` records a CLI change only for October (0.146.0 to 0.156.0), not for July. The legend also leaves out one round-3 change listed in the batch README ("fewer false parameter-mismatch retries"). The one-replicate intermediate round is documented only as "the earlier local MCP-only selected trial".

14. **Fig. 1a time limit.** "120 min†" for CompBioBench custom code covers 1,194 runs. Six runs had stated limits of 240 or 480 min (Supplementary Table: `supp_table_design.md`). CompBioBench Galaxy prompts state no limit.

## Scope differences between panels (not errors, but unstated)

- **Different run sets.**
  - Fig. 4a, Extended Data Fig. 4a and Fig. 5b (right) count all 1,908 traced Galaxy runs. In the earlier set that included 12 runs of the then-unscored IWC host-read removal task; in the updated figures the task is scored, so this mismatch is gone.
  - Fig. 4c, Extended Data Fig. 4b and Fig. 5a use scored runs only.
  - Fig. 5d covers all 1,920 primary runs per condition.
- **Fig. 3b IWC "Correct".** In the earlier set it was computed over 27 scored runs, while the Runs column showed 30. Resolved in the updated figures (30 of 30 scored).
- **Extended Data Fig. 5c.** Two CompBioBench runs (`reverse-search-gwas-q1`; 590M and 447M input tokens) fall outside the axis limits and are not drawn.
- **Extended Data Fig. 4d.** The bin edges of the 18-run definition (0, 1–2, 3–8, 9–18) appear only in Source Data.
- **Fig. 4d and Extended Data Fig. 7a.**
  - The 80-run sample is not balanced by model: DeepSeek V4 Pro supplies 29.
  - Coded run D075 describes a run that was later replaced by a rerun. Both versions were incorrect.

## Stale metadata

- **Module docstrings.**
  - `make_fig3.py` says *P* values are Holm-adjusted within each panel; only Fig. 3a is.
  - `make_fig4.py` lists the old panel set, Holm over four for panel b, and "three" answer-matching rules (the figure shows four).
- **Saved titles.** The title stored in the Extended Data Fig. 4 PDF/SVG differs from the legend title.
- **Terminology.** The legend title says "route similarity" while the panels say "tool-set similarity".
- **`figures/figure_review_response.md`.**
  - It refers to Fig. 5c for the structured-record rule (now Fig. 5d).
  - It gives the pooled model-effect *P* values as 0.01; the figure shows 0.009 and 0.007.
