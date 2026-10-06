# Response to the figure review (2026-10-05)

Point-by-point record of how `figure_review.md` was applied. Previous versions are in `archive/2026-10-05_before_review/`. Every number below is written by the figure scripts to the Source Data files.

## Changes made first

| Review item | Done | Where |
|---|---|---|
| 1. Reconcile the recovery summaries | Both estimands are now in the panel: unadjusted +2.3 points (*P* = 0.07, primary) and error-bin-adjusted +3.7 (*P* = 0.003), labelled exploratory. The logistic curves were replaced by binned estimates with run counts, so no point pools unlike bins. | Fig. 3d, legend |
| 2. Replace equality language | Titles and labels no longer claim "same accuracy", "cost no more" or "n.s." brackets. They now give estimates with intervals. The Fig. 2 legend states that the tests do not establish equivalence and that no margin was prespecified. | Figs 2, 5 |
| 3. Repair the inspectability comparison | Rebuilt from the per-step evidence. Each element is classed as a structured record, free text in the retained trace, partial (environment image or metadata only), or not retained (unknown). Custom code is no longer scored zero by construction: parameters and commands count as free text, exit codes as structured, and versions printed in the trace as free text. The history row says "retrieved; no rerun". | Fig. 5c |
| 4. Separate tool overlap from analytical routes | Renamed "tool-set similarity", with eligibility per benchmark and a statement that order, versions, parameters and UDT methods are ignored. Sensitivity analyses (UDT items dropped; installed-only cells; cells with any UDT) are in Extended Data Fig. 4b. | Fig. 4c |
| 5. Remove the circularity from the rigor interpretation | Difficulty is now held out: the incorrect runs among the task's other 21 runs. Labels are "same rejected answer in all three runs", "all rejected, answers differ" and "mixed". All replicate sets are shown, faceted by model, with intervals. The legend no longer infers rigor. | Fig. 4d |

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
- c: failures per opportunity (installed-tool jobs 9.1%, UDT jobs 44%, shell commands 5.0% in Galaxy runs and 8.6% in custom-code runs), total errors per run, and a four-group composition. The seven types are in Extended Data.
- d: see item 1.
- e: substantive mismatches (Galaxy would set, or did set, a different value) are separated from values with no recorded counterpart and from unresolved checks. A blocked request was followed by a completed job of the same tool in 71% of cases, and the legend adds that matching parameters are not scientific appropriateness.
- f: renamed "Failed requests and candidate infrastructure improvements"; comparable groups are sorted, grey groups kept and affected runs added. The codebook is frozen in `fig3_failure_class_codebook.csv`, marked unvalidated.
- Extended Data Fig. 3: a task-level status matrix, all seven error types, and recovery by benchmark.

**Fig. 4.**
- Title: "Answer agreement and tool use vary across model configurations".
- a: a method-family heatmap at the completed-job stage, consistent with Fig. 3b, with data handling separated from methods and UDTs as one row. The codebook is in `fig4_tool_family_codebook.csv`; the top-15 inventory moved to Extended Data.
- b: benchmark facets with paired condition markers. Missing submissions no longer count as agreement. The multiplicity policy is stated: primary pooled tests, Holm over two; secondary per-benchmark tests, Holm over four.
- c and d: see items 4 and 5.
- Extended Data Fig. 4c: agreement under three answer-matching rules.

**Fig. 5.**
- Title: "Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks".
- a: Galaxy / custom-code ratios for each benchmark, for total input, uncached input and output tokens. Two estimators are shown, with the paired geometric mean as primary and the ratio of totals as aggregate. The IWC exception is visible (1.7×, 0.8–3.5; aggregate 0.90×). The sibling comparison is now a ratio plot headed "No clear input-token difference between correct and incorrect siblings".
- b: action and tokens-per-action ratios by benchmark, and returned characters by request type and benchmark. Labels say "returned characters", "inspected but not executed" and "cached input" literally.
- c: the repaired inspectability comparison (item 3).
- d: one matched analysis record, bix-45-q1.
- Extended Data Fig. 5: the model trade-off by benchmark with intervals, sibling distributions, and tokens against actions.

## Not done: needs new annotation or new runs

These are recorded so that the text does not claim them.
- Blinded validation of the failure-cause audit and of the failure-class codebook (Figs 2d, 3f), including uncertain or overlapping causes beyond the recorded primary and secondary cause.
- Annotation of UDT methods, and route similarity that accounts for order, parameters and versions (Fig. 4a, c).
- Coding of verification steps in successful as well as failed runs, and the selected variant-status case (Fig. 4d). Without these, the figure does not support a claim about rigor.
- Task-aware answer matching (numeric tolerance, units, identifiers) beyond the three text rules. The three sets with the same answer graded differently are counted as "mixed" and not investigated further.
- A held-out model or an external task-complexity label as a second difficulty measure.
- Episode-level recovery (comparable failure episodes and their correction), and a controlled interface intervention (Fig. 3d).
- A worked example of a detected parameter mismatch followed by its correction (Fig. 3e gives the rate only).
- Reruns of Galaxy histories or custom-code analyses, and blinded reviewer reconstruction time (Fig. 5c, d).
- Monetary cost: model prices were not applied.
- Efficiency interventions such as compact replies or reusable discovery results.

## Layout

- The most important labels are 5.5–6.5 pt.
- Every panel states its unit and denominator.
- Vector text is editable (SVG `fonttype none`, PDF Type 42), and PNGs are 600 dpi RGB.
- Main figures are 180 mm wide and 116–170 mm tall.
- Legends are 310–350 words.
