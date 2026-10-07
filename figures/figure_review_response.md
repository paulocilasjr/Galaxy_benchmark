# Response to the figure review (2026-10-05)

Point-by-point record of how `figure_review.md` was applied. Previous versions are in `archive/2026-10-05_before_review/`. Every number below is written by the figure scripts to the Source Data files.

## Changes made first

| Review item | Done | Where |
|---|---|---|
| 1. Reconcile the recovery summaries | Both estimands are now in the panel: unadjusted +2.1 points (*P* = 0.10, primary) and error-bin-adjusted +3.4 (*P* = 0.01), labelled exploratory. The logistic curves were replaced by binned estimates with run counts, so no point pools unlike bins. | Fig. 3d, legend |
| 2. Replace equality language | Titles and labels no longer claim "same accuracy", "cost no more" or "n.s." brackets. They now give estimates with intervals. The Fig. 2 legend states that the tests do not establish equivalence and that no margin was prespecified. | Figs 2, 5 |
| 3. Repair the inspectability comparison | Rebuilt from the per-step evidence. Each element is classed as a structured record, free text in the retained trace, partial (environment image or metadata only), or not retained (unknown). Custom code is no longer scored zero by construction: parameters and commands count as free text, exit codes as structured, and versions printed in the trace as free text. The history row says "retrieved; no rerun". | Fig. 5d |
| 4. Separate tool overlap from analytical routes | Renamed "tool-set similarity", with eligibility per benchmark and a statement that order, versions, parameters and UDT methods are ignored. Sensitivity analyses (UDT items dropped; installed-only cells; cells with any UDT) are in Extended Data Fig. 4b. | Fig. 4c |
| 5. Remove the circularity from the rigor interpretation | Difficulty is now held out: the incorrect runs among the task's other 21 runs. Labels are "same rejected answer in all three runs", "all rejected, answers differ" and "mixed". All replicate sets are shown, faceted by model, with intervals. The legend no longer infers rigor. | Fig. 4e |

## Figure by figure

**Fig. 1.**
- Selection is shown as 3,840 primary runs, 3,816 scored runs on 159 tasks, and 4,240 archived runs.
- Replicates are labelled "3 independent runs".
- The container is now an "isolated workspace".
- A condition strip shows where analysis ran, the tools, the prompt and the time limit.
- The figure says "four model configurations".
- Benchmark boxes give the three scoring contracts.
- A gate marks that the reference is opened only after the answer is fixed.
- The task squares, clock and bootstrap text were removed.
- New: `supp_table_design.{csv,md}` (built by `make_supp_table_design.py`).

**Fig. 2.**
- Title: "Agents show similar observed benchmark performance in Galaxy and custom code".
- a: paired points in benchmark facets; IWC on its own 0–1 agreement axis.
- b: the paired-difference forest is now the centre of the figure, with per-model and pooled rows and two separate estimands. The IWC primary estimate is agreement, not the 0.99 threshold.
- c: one matrix per benchmark with region labels, summaries and a log-scale key.
- d: causes are split into discordant pairs and shared failures. The panel names the AI-assisted audit, hatches runs where validation and specification causes overlap, and gives run and task coverage. It adds one traced case (bix-45-q1, PhyKIT version).
- Extended Data Fig. 2: the full cause census, the IWC threshold sensitivity (0.95, 0.99, 1) and the archive's population sensitivities, which include zero-scored IWC tasks and route definitions.

**Fig. 3.**
- a: renamed "Correct runs by domain"; the axis is padded so markers at 100% are not clipped.
- b: route by completed jobs, with separate categories for failed-only runs and runs with no job. It shows exact run counts and the share correct per row; route by correctness is marked descriptive.
- c: failures per opportunity (installed-tool jobs 9.2%, UDT jobs 41%, shell commands 4.9% in Galaxy runs and 8.6% in custom-code runs), total errors per run, and a four-group composition. The seven types are in Extended Data.
- d: see item 1.
- e: substantive mismatches (Galaxy would set, or did set, a different value) are separated from values with no recorded counterpart and from unresolved checks. A blocked request was followed by a completed job of the same tool in 71% of cases, and the legend adds that matching parameters are not scientific appropriateness.
- f: renamed "Failed requests and candidate infrastructure improvements"; comparable groups are sorted, grey groups kept and affected runs added. The codebook is frozen in `fig3_failure_class_codebook.csv`, marked unvalidated.
- Extended Data Fig. 3: a task-level status matrix, all seven error types, and recovery by benchmark.

**Fig. 4.**
- Title: "Answer agreement and tool use vary across model configurations".
- a: a method-family heatmap at the completed-job stage, consistent with Fig. 3b, with data handling separated from methods and UDTs as one row. The codebook is in `fig4_tool_family_codebook.csv`; the top-15 inventory moved to Extended Data.
- b: benchmark facets with paired condition markers. Missing submissions no longer count as agreement. The multiplicity policy is stated: primary pooled tests, Holm over two; secondary per-benchmark tests, Holm over four.
- c and e: see items 4 and 5.
- Extended Data Fig. 4c: agreement under three answer-matching rules.

**Fig. 5.**
- Title: "Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks".
- a: Galaxy / custom-code ratios for each benchmark, for total input, uncached input and output tokens. Two estimators are shown, with the paired geometric mean as primary and the ratio of totals as aggregate. The IWC exception is visible (1.7×, 0.8–3.5; aggregate 0.90×). The sibling comparison is now a ratio plot headed "No clear input-token difference between correct and incorrect siblings".
- b: action and tokens-per-action ratios by benchmark, and returned characters by request type and benchmark. Labels say "returned characters", "inspected but not executed" and "cached input" literally.
- c (new, 2026-10-07): reducing Galaxy token use. Galaxy / custom-code tokens per complete 50-task BixBench-Verified-50 run before and after each round of interface changes, from run records: July, GPT-5.5, 5.48× to 2.81× (Galaxy tokens −55%); October, GPT-5.6 Sol, 3.45× to 1.53× (−56%), with the single intermediate replicate (2.42×) from the batch summary. Data in `token_improvment/`.
- d: the repaired inspectability comparison (item 3).
- e: one matched analysis record, bix-45-q1.
- Extended Data Fig. 5: the model trade-off by benchmark with intervals, sibling distributions, and tokens against actions.

## Follow-up (2026-10-06): items done with the retained material

| Item | What was done | Result | Where |
|---|---|---|---|
| Validation of the failure-cause audit | Independent AI second rater, blind to the audit, on 45 stratified incorrect BixBench-Verified-50 runs (transcript, submitted and reference answers) | Agreement 78% on the cause group (κ = 0.56); 96% counting secondary causes; 27 of 30 benchmark-attributed runs confirmed | Extended Data Fig. 6c |
| Validation of the failure-class codebook | Independent AI second rater, blind to the rule, on 150 failed requests (10 per class), assigning a class and the changes that would prevent each failure (multiple allowed) | 92% of classified requests reproduced (κ = 0.92); the codebook's improvement group was among the rater's in 71%; more than one improvement was plausible in 35% | Extended Data Fig. 6d |
| Verification in successful and failed runs | 80 runs, 10 per benchmark × condition × outcome, coded for six kinds of check by AI coders blind to the grade | Checks in 88% of both correct and incorrect runs. Counts (62% vs 42%) and independent recomputation (42% vs 25%) were more frequent in correct runs. Checks were more frequent in custom-code runs (95%) than in Galaxy runs (80%) | Extended Data Fig. 7a |
| UDT methods | Deterministic classes from 5,077 UDT definitions (code first, then a tool-specific container) | 35% of all UDT requests (41–52% of each model's completed CompBioBench UDT jobs) ran a script supplied as a dataset, which the request cannot classify. 95.9% of UDTs named a versioned container, which now counts as a structured software record in Fig. 5c | Extended Data Fig. 4e; Fig. 5c |
| Route similarity with order, versions and parameters | Edit distance on ordered job sequences; Jaccard on versioned tools; Jaccard on tools with identical non-dataset parameters | The BixBench-Verified-50 negative correlation persists with order or versions (−0.26, −0.29) and vanishes with parameters (−0.02) | Extended Data Fig. 4b |
| Task-aware answer matching | Numbers within the BixBench evaluator's tolerance (otherwise 0.1%), lists as sets, identifier versions ignored; now the primary rule | All three sets "same answer, graded differently" were rounding artefacts. The pooled model effect holds (custom code *P* = 0.01, Galaxy *P* = 0.01) | Fig. 4b, e; Extended Data Fig. 4c |
| Second difficulty definition | Difficulty from the other three models' 18 runs | Same pattern: 42% of sets with the same rejected answer in the hardest bin (45% with the 21-run definition) | Extended Data Fig. 4d |
| Failure-level recovery | Failed steps later re-run without error in the same run | Installed-tool jobs 62%, UDT jobs 56%, shell commands 55% (Galaxy runs) vs 54% (custom code) | Extended Data Fig. 7b |
| Worked parameter check | bix-43-q4: nested library key blocked before the job, then resubmitted with flat keys | Job ran with matched parameters | Extended Data Fig. 7c |
| Variant-status case | Outcomes of all 24 runs and which ran a read-position diagnostic (answers withheld) | 4 of 24 accepted; GPT-5.6 Sol in Galaxy ran the diagnostic as a UDT in replicates 2 and 3, both accepted | Extended Data Fig. 7d |

## New finding: runs that reached benchmark answers

While coding, a coder noticed an agent downloading the public BixBench dataset, which includes the reference answers. A scan of every primary trace (`make_answer_exposure.py`) found the following:
- **Verified exposure (43 runs):** reference answers, or other agents' recorded answers, appeared in a command or connector output.
- **Probable exposure (51 runs):** the run opened a page that publishes them; web page content is not logged.
- **Searched for the benchmark or task (277 runs):** no answer source was opened.

Exposure came mostly from DeepSeek V4 Pro and GPT-5.6 Luna, in both conditions. Exposed runs were not more often correct. Excluding them leaves the condition differences essentially unchanged:
- BixBench-Verified-50: +1.5 points instead of +1.3;
- CompBioBench: +0.2 instead of +0.3.

The results are in Extended Data Fig. 6a,b. The Methods should disclose this, and the harness should block benchmark sources in future runs.

## Main-figure updates with these results

- **Fig. 2b:** a note gives the condition differences without the 94 runs that reached benchmark answers (BixBench-Verified-50 +1.5, CompBioBench +0.2 points).
- **Fig. 2d:** the subtitle reports the independent second rater, who agreed on the cause for 35 of 45 runs (κ = 0.56).
- **Fig. 3c:** a new column gives the share of failed steps later re-run without error: installed-tool jobs 62%, UDT jobs 56%, shell commands 55% in Galaxy runs and 54% in custom-code runs.
- **Fig. 3f:** the subtitle reports the codebook check (92% of classes reproduced; same improvement named for 71% of requests).
- **Fig. 4d (new panel):** verification checks in correct and incorrect runs. The replicate-outcome panel is now e, so letters follow reading order.
- **Fig. 5d:** UDT jobs with a versioned container count as structured software records.
- **Primary analysis:** all runs stay in it; answer exposure is reported as a sensitivity analysis.

## Reviewed CompBioBench reruns (2026-10-06)

All numbers above are recomputed after 53 CompBioBench Galaxy runs were replaced by their reviewed reruns (`CompBio/reruns_20261005/`). The rule was to keep every other run's result as it was and substitute only the rerun runs.

**What was swapped in:**
- **Sources:** each rerun's trace and Galaxy history, collected with the repository's own collector, plus its answer and grade.
- **Checks:**
  - Every file matches the Hugging Face commit pinned in the lab's rerun record.
  - The per-run grades reproduce all 24 official replicate scores. The lab results file used for this check differs from the previous one only by the rerun updates.
- **Originals:** archived in each task package under `versions/pre_rerun_20261005/`.

**What else changed:**
- **Other runs:** none. `check_unchanged.py` compares every per-run table with the last commit before the swap (7ed8048c9); only the 53 rerun records differ.
- **Grades:** 17 changed (8 to correct, 9 to incorrect). Official Galaxy scores changed for the replicates with changed answers (for example GPT-5.5 r2, 89 to 87).
- **UDT error audit (On-demand Fig. 7c):** the 10 entries for replaced runs were set aside (the full previous file is kept) and the 14 incoming incorrect UDT runs were coded with the same codebook by two AI reviewers; 134 runs are now audited.
- **Expected counts:** two hard-coded totals in the scripts were updated with their arithmetic:
  - failed Galaxy requests, 6,904 + 237 = 7,141;
  - audited UDT runs, 130 − 10 + 14 = 134.

**Numbers that moved:**

| Panel | Before | After |
|---|---|---|
| Fig. 2b, CompBioBench, all runs | +0.4 points | +0.3 points |
| Fig. 2b, CompBioBench, without exposed runs | +0.3 points | +0.2 points |
| Fig. 3c, failed steps (installed-tool / UDT / shell, Galaxy) | 9.1% / 44% / 5.0% | 9.2% / 41% / 4.9% |
| Fig. 3c, fixed later (installed-tool / UDT / shell, Galaxy) | 60% / 46% / 57% | 62% / 56% / 55% |
| Fig. 3d, unadjusted difference | +2.3 points, *P* = 0.07 | +2.1 points, *P* = 0.10 |
| Fig. 3d, error-bin-adjusted (exploratory) | +3.7 points, *P* = 0.003 | +3.4 points, *P* = 0.01 |
| Fig. 3e, installed-tool requests checked | 17,180 | 16,757 |
| Fig. 3f, failed requests | 7,354 | 7,141 |
| Fig. 4a, installed tools in the codebook | 401 (the legend said 422, already out of date) | 397 |
| Fig. 4b, CompBioBench model effect, Galaxy | *P* = 0.18 | *P* = 0.07 |
| Fig. 4c, CompBioBench task correlation | ρ = 0.13, *P* = 0.21 | ρ = 0.06, *P* = 0.56 |
| Fig. 4c, models compared on the same task | ρ = 0.07, *P* = 0.14 | ρ = 0.04, *P* = 0.38 |

The IWC and BixBench-Verified-50 results did not change.

**Not yet updated:**
- **Task-level failure-cause audit (`individual_error_analysis.md`):** its CompBioBench entries describe the replaced runs. Two tasks now have incorrect runs and no entry (reverse-encode-q1, perturb-seq-align-q1), and the per-task correct counts no longer match. `rigor_analysis.py` and the original-layout manuscript build stop on this; the figures in this folder do not use it.
- **Verification sample (Extended Data Fig. 7a):** one coded run, D075 (conservation-lookup-q1, DeepSeek r3), was replaced. Its codes describe the original run. Both the original and the rerun were incorrect, so the run's outcome stratum is unchanged.

**What the reruns differ in:**
- **Unchanged:** the task prompt, model, reasoning effort, time limit and skills.
- **Changed:**
  - the agent container image;
  - none of the reruns used web search;
  - 30 used Codex app connectors to Galaxy, GitHub or Hugging Face.
- **Exposure:** one rerun (lung-cancer-sc-q1, GPT-5.5 r3) fetched the project's own results page through the GitHub connector, then reused other runs' published histories. Under the exposure scan's existing rules it counts only as "attempted"; the rule was not extended, so that other runs keep their tiers.

## Scores matched to the results site (2026-10-07)

Every run is now scored as the public results site shows it (https://goeckslab.github.io/galaxy-agent-benchmark/), and the IWC host-read removal task is scored.
The previous figures are kept in `archive/2026-10-07_before_site_scores/`.

**Where the scores come from:**
- `make_scored_runs.py` writes `scored_runs.csv`, which every figure script now reads in place of the archive's `accuracy_primary_runs.csv`.
- It starts from the archive's table and takes the site's values from `site_snapshot/`: grades and values only, no answers.
- It stops if any BixBench-Verified-50 grade or IWC value differs from the site.

**What changed:**
- **BixBench-Verified-50:** grades follow the site, which regraded two items after the original evaluation; 27 primary runs changed.
  - bix-53-q2 accepts "increase": 18 runs now correct. The site still shows the six DeepSeek V4 Pro runs as incorrect, and they are kept as shown.
  - bix-43-q2 uses platform-specific two-decimal scoring: 5 runs now correct, 4 now incorrect.
- **CompBioBench:** unchanged. The archive's grades sum to the official-leaderboard score of every replicate, which is the site's headline.
- **IWC host-read removal (wf_003):** scored from each run's `run_record.json`, the value the site shows.
  - This adds 24 runs: 3,840 scored runs on 160 tasks, 240 for IWC.
  - Its earlier exclusion rested on evaluator problems: two BWA runs were scored against the Bowtie2 reference, and three runs had unregistered aligner names or routes.
  - The site values were reproduced from the submitted files against the benchmark's route references. Every Galaxy answer is a Galaxy job output.
  - Caveat: the minimap2 route reference is GPT-5.5 custom-code replicate 3's own submission, so that run's 1.000 is self-referential.
  - `make_wf003_errors.py` extracts the 24 runs' execution errors with `fig_on_demand.py`'s own rules. The on-demand workbook omits the task.
- **Failure causes (Fig. 2d, Extended Data Fig. 2a):**
  - Audited runs that the site grades correct leave the census.
  - The 4 bix-43-q2 runs graded incorrect only by the site have no audit entry. They take the task-level audit's cause, benchmark specification or scoring (`individual_error_analysis.md`).
- **Population sensitivities (Extended Data Fig. 2b):** recomputed on these scores with the primary estimator, instead of read from `accuracy_sensitivities.csv`.
- **Verification sample (Fig. 4d, Extended Data Fig. 7a):** outcomes use the current grade. D079 (bix-53-q2) is now correct, so the groups hold 41 correct and 39 incorrect runs.
- **Fig. 5c:** "Galaxy correct" uses the site's grades: the primary grades for the archived runs, and the site's 6 July page for the round-1 batch.
- **Fixed:** the improvement-group agreement in the Fig. 3f and Extended Data Fig. 6d subtitles read 71%. Under pandas 3, the 30 requests without a group were counted as misses; it is now 89% (107 of 120).

**Numbers that moved:**

| Panel | Before | After |
|---|---|---|
| Fig. 1a, scored runs | 3,816 on 159 tasks | 3,840 on 160 tasks |
| Fig. 2a, GPT-5.5 BixBench-Verified-50 (custom code / Galaxy) | 87.3% / 89.3% | 90.0% / 91.3% |
| Fig. 2b, BixBench-Verified-50, pooled | +1.3 points (−3.6 to 6.3) | +0.5 points (−3.9 to 4.8) |
| Fig. 2b, BixBench-Verified-50, without exposed runs | +1.5 points | +0.6 points |
| Fig. 2b, IWC agreement, pooled | +4.0 points (0.7 to 7.8), *P* = 0.06 | +3.6 points (0.6 to 7.4), *P* = 0.055 |
| Fig. 2b, smallest Holm-adjusted *P* | 0.38 | 0.19 |
| Fig. 2d, incorrect BixBench-Verified-50 runs | 170 | 151 |
| Fig. 3d, unadjusted / error-bin-adjusted | +2.1, *P* = 0.10 / +3.4, *P* = 0.01 | +1.6, *P* = 0.18 / +2.8, *P* = 0.02 |
| Fig. 3f and Extended Data Fig. 6d, improvement group named | 71% | 89% |
| Fig. 4c, IWC task correlation | ρ = 0.91, *P* = 0.001 (9 tasks) | ρ = 0.74, *P* = 0.02 (10 tasks) |
| Fig. 4d, coded runs correct / incorrect | 40 / 40 | 41 / 39 |
| Fig. 5a, IWC input, Galaxy / custom code | 1.7× (0.8–3.5) | 1.8× (0.9–3.4) |
| Fig. 5c, Galaxy correct by stage | 91%, 89%, 89%, 91% | 93%, 91%, 91%, 91% |
| Extended Data Fig. 2b, largest IWC estimate | +16.7 points | +15.0 points |
| Extended Data Fig. 3c, IWC among runs with errors | +7.2, *P* = 0.07 | +6.9, *P* = 0.052 |
| Extended Data Fig. 7b, failed steps | 6,061 | 6,114 |

No conclusion changed direction and no test crossed *P* = 0.05.
Every changed Source Data value is listed in `source_data_changes/` (`compare_source_data.py`).

**Not yet updated:**
- **`individual_error_analysis.md`:** it still describes bix-53-q2 and bix-43-q2 under the original evaluator's grades.
- **Second rater (Extended Data Fig. 6c):** 7 of its 45 sampled runs are now graded correct. The check measures agreement on the cause at audit time; both raters attributed all 7 to the benchmark.

## Still not possible with the retained material

| Item | Why it cannot be done now |
|---|---|
| Human blinded validation of the audits | Needs human annotators; the AI second ratings above do not replace it |
| Blinding coders to condition | The condition is visible in every transcript (Galaxy calls) |
| Reruns of Galaxy histories | Needs credentials and new jobs on usegalaxy.org, an external action requiring approval; the archive's audit policy also forbids executing agent code |
| Reruns of custom-code analyses | Workspaces and environments were not retained (CompBioBench custom code ran in an unexported host conda environment) |
| Reviewer reconstruction time | Needs a human study |
| Monetary cost | The archive holds no dated price sheets for these models and service tiers; a dated price table would be needed |
| Efficiency or interface interventions, and controlled recovery experiments | Need new benchmark runs with a modified interface |
| Methods of scripts supplied to UDTs as datasets | The script is a dataset in the Galaxy history, not in the request; classifying it needs the history snapshots and code annotation |

## Build order

`make_udt_methods.py`, `make_failure_episodes.py` and `make_answer_exposure.py` write the tables that `make_fig4.py`, `make_fig5.py` and `make_ed_validation.py` read. `annotations/build_samples.py` regenerates the coding samples.

## Layout

- The most important labels are 5.5–6.5 pt.
- Every panel states its unit and denominator.
- Vector text is editable (SVG `fonttype none`, PDF Type 42), and PNGs are 600 dpi RGB.
- Main figures are 180 mm wide and 116–170 mm tall.
- Legends are 310–350 words.
