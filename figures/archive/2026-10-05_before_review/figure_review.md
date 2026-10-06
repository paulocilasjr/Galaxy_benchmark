# Figure review against the manuscript Results outline

Reviewed 2026-10-05. This review covers the five current PNG figures, their five Markdown legends, the figure source-data exports and relevant plotting code, and the existing accuracy, rigor, token and design interpretations. Archived figure versions were not used to judge the current layouts. No benchmark was executed and no private ground truth was opened. The figures themselves have not been changed.

The figures already form a useful narrative, and the condition colours, replicate markers and source-data exports are strengths. The largest gains will come from matching each claim to the quantity actually measured. Several panels currently show a useful proxy while their titles imply a stronger biological, causal or reproducibility result.

## Where the evidence meets the outline

| Results section | Current support | Main improvement |
|---|---|---|
| 1. Accuracy through Galaxy | Fig. 2 shows close observed performance on the two binary benchmarks and high IWC output agreement. | Lead with paired effect sizes and uncertainty; distinguish similarity from demonstrated equivalence, and keep IWC agreement separate from binary accuracy. |
| 2. Structured analyses | Fig. 3 shows execution routes, operational errors, parameter checks and candidate infrastructure improvements. | Separate requests, completed jobs and scientifically successful analyses; describe recovery as an association unless comparable failure episodes are evaluated. |
| 3. Model-dependent variability | Fig. 4 shows different answer-agreement rates and tool-request profiles. | Measure analytical routes more faithfully and connect verification to correctness. Tool-set overlap and repeated rejected answers do not establish analytical rigor. |
| 4. Inspectability and token demand | Fig. 5 shows input-token demand and interface activity. | Put inspectability in a visible panel, measured fairly in both conditions; retain benchmark-specific token results, including IWC. |

Work labels below distinguish **existing evidence** that can be displayed immediately, **reanalysis** of retained records, and **new validation** requiring additional annotation or execution. Proposed analyses are not reported as established results.

## Changes to make first

1. **Reconcile the recovery summaries.** Fig. 3d displays the error-bin-adjusted difference, +3.74 percentage points, P = 0.0034. Its legend supplies the unadjusted difference, +2.28 points, P = 0.0681, in parentheses without explicitly giving the adjusted estimate. These are different estimands, not competing calculations. Label both and mark the bin-adjusted analysis as exploratory. The curve also pools some adjacent error counts, whereas the legend says every point groups the same count. Sources: `fig3_source_data.csv:151`, `fig3_legend.md:10`, `make_fig3.py:293`.
2. **Replace equality language based on nonsignificant tests.** Fig. 2's repeated "n.s." brackets, Fig. 5a's "same accuracy" and Fig. 5b's "cost no more" encourage conclusions that the tests do not establish. Present estimates and confidence intervals. A prospective equivalence or noninferiority claim needs a scientifically justified margin; a margin selected after seeing these results should be explicitly exploratory.
3. **Repair the inspectability comparison before plotting it.** In `make_fig5.py:252`, several baseline measures are zero by construction: parameters and output links are counted only when `galaxy_step` is true, and version identification is also restricted to Galaxy. This measures native Galaxy fields, not the absence of reconstructable evidence in custom code. Likewise, retrieving a public history does not establish that it can be rerun successfully.
4. **Separate tool overlap from analytical routes.** Fig. 4c ignores order, repeated steps, tool versions and parameters, and collapses all UDTs to the same item. Two entirely different UDT analyses can therefore have similarity 1. Rename the present measure and perform a sensitivity analysis before drawing conclusions about path diversity.
5. **Remove the circularity from the rigor interpretation.** Fig. 4d uses each task's failure rate to define difficulty, including the failures being classified. A rise in three-replicate rejection is partly expected under that definition. Use independent or held-out difficulty and add direct verification evidence.

## Figure 1: study design

**What it supports.** The diagram explains the benchmark sources, four configurations, two execution conditions, three replicates and the extra provenance available through Galaxy. Keep this role: it should let a reader understand the unit of comparison before interpreting any scores.

**Strengthen the evidence.** Label the arithmetic as **3,840 primary runs**, followed by **3,816 scored runs across 159 tasks**. The 24 excluded runs correspond to the host-read removal task across four configurations, two conditions and three replicates. The larger archive contains 4,240 runs, including configurations outside the primary comparison; explain that selection in Methods or a supplementary flow diagram. Also show that the three replicates assess repeatability, rather than iterative improvement across attempts. The README explicitly distinguishes those designs.

The container and clock icons currently imply a uniform execution procedure. The legend explains that CompBioBench custom code used host conda, and that budgets varied or were not stated. Replace the universal container label with "isolated workspace" and show a compact condition-specific design strip: execution location, available tools/UDTs, policy and budget. Use "four model configurations" consistently because reasoning settings differ.

**Display the finding better.** Reduce decorative icons and repeated task squares; preserve the benchmark counts and endpoint labels. Give the three scoring contracts their own short labels: evaluator acceptance, reconstructed-key agreement and continuous workflow-output agreement. Make "reference withheld until answer fixed" a clear gate between execution and evaluation. Move detailed runtime settings and bootstrap mechanics to the legend or Methods.

The existing design metadata also documents composite run campaigns and differences in prompts and budgets. These limit attribution to Galaxy itself; a supplementary design/selection table should accompany the comparison. Source: [design metadata](../manuscript_narrative/derived/design/design_metadata.md).

## Figure 2: accuracy and disagreement

**What it supports.** The observed binary-benchmark differences are small. The pooled Galaxy-minus-code differences in the current export are +1.33 percentage points on BixBench (95% CI -3.57 to +6.30) and +0.42 on CompBioBench (-1.58 to +2.42). This is convincing evidence of close point estimates, with appreciably different precision across benchmarks. It is not a demonstrated equivalence result. The existing [accuracy interpretation](../manuscript_narrative/original_layout/analysis/accuracy_interpretation.md) already makes this distinction clearly.

| Panel | Strengthen support | Improve the display |
|---|---|---|
| a: benchmark/model scores | Keep the paired design visible and state the endpoint for each benchmark. Include an IWC sensitivity to route definitions and zero-scored tasks in Extended Data. | Replace bars and 12 "n.s." brackets with paired points and intervals, in three benchmark facets. Give IWC a separate agreement axis, ideally 0-1. |
| b: differences | Display the primary score difference for each benchmark. IWC here changes from continuous agreement to a threshold of 0.99; make that secondary conversion explicit and check threshold sensitivity. All-three-correct is reliability, which can change without a change in average accuracy. | Make an effect-size forest plot the visual centre. Keep mean score and all-three-correct differences in separate aligned groups rather than mixing two estimands in each row. |
| c: paired replicate counts | This establishes where the environments agree in the number of successful replicates. It does not establish agreement of submitted answers or analytical methods. Retain benchmark-specific versions because scoring contracts differ. | Label the two off-diagonal regions "Galaxy higher" and "Custom code higher". Add the useful summaries already in the export: 509/636 pairs have equal counts, 70 favour Galaxy and 57 favour code. If log shading remains, provide its scale. |
| d: failure causes | The panel explains BixBench rejections, not specifically the cross-condition disagreements. Classify the discordant pairs directly, with shared failures shown separately. Identify AI-assisted attribution and show overlapping validation/specification causes. | Move the full six-bar census to Extended Data; use a compact disagreement-cause panel plus one traced example in the main figure. Keep counts and unique task/capsule coverage visible, particularly for small groups. |

For the outline's IWC question, avoid comparing 98% mean output agreement directly with 87% binary answer acceptance. They are different outcomes on different task populations. The larger observed all-three-correct gain on IWC is interesting but rests on nine tasks and is not significant under the figure's adjusted randomization tests.

For "why is accuracy preserved?", performance alone does not supply a mechanism. A concrete side-by-side case can show how equivalent evidence was produced in both environments, while a discordant case can show a tool-version or analytical-choice difference. Present these as explanations of selected cases.

Suggested figure title with the current evidence: **Agents show similar observed benchmark performance in Galaxy and custom code.**

## Figure 3: execution structure, errors and improvement opportunities

**What it supports.** This is the closest match to its Results subsection, including the infrastructure breakdown that the attached outline described as still missing. Panel f now maps 7,354 failed requests to candidate interventions, although the mapping has not established that those interventions would prevent each failure.

| Panel | Strengthen support | Improve the display |
|---|---|---|
| a: domains | "Tasks completed" currently means runs meeting a correctness threshold. Distinguish completed analyses from accepted results, especially where all steps ran but outputs disagreed. | Rename to "Correct runs by domain". Move the broad domain summary to Extended Data if space is needed; a task-level status matrix would answer "which tasks?" more directly. Add display padding at 100% so markers are not clipped. |
| b: installed tools/UDTs | Jobs submitted, jobs successful and analysis correct are separate states. A run with no observed job needs separate treatment from a missing trace. Route choice is selected by the agent, so route/correctness associations are descriptive. | Keep the current benchmark/model layout, but show outcome alongside route. A companion strip can distinguish no job, failed-only jobs and successful jobs. Show exact run denominators. |
| c: errors | Percent composition does not quantify risk. Give errors per relevant opportunity: installed-tool job, UDT job or eligible shell command. Also report total burden across all Galaxy channels, since Galaxy shell errors alone omit tool and UDT failures. Use consistent rules for expected nonzero exits and genuine failures. | Use aligned dot plots for rates plus a smaller composition panel. Collapse tiny segments and keep the full seven-category breakdown in Extended Data. Do not combine these event counts with panel f's failed-request counts. |
| d: recovery proxy | Final correctness after errors is not episode-level recovery. Error counts differ in meaning between conditions, and conditioning on them can select different tasks and runs. The bin adjustment was chosen after inspection. | Title it "Final correctness among runs with execution errors". Display binned estimates with counts and intervals, or facet by benchmark. Report adjusted and unadjusted differences together; reduce emphasis on sparse high-error tails. |
| e: parameter checks | Requested-versus-recorded agreement is distinct from scientifically appropriate parameterization. A mismatch may reflect coercion, defaults or serialization. Determine which flagged mismatches led to correction and which remaining mismatches affected results. | Retain the compact stacked bars, but distinguish substantive mismatches, documented transformations and unresolved checks. Avoid implying that every pre-job mismatch represents a prevented scientific error. |
| f: candidate fixes | Freeze a transparent codebook mapping failure classes to proposed changes; validate a sample and allow uncertain or overlapping causes. An invalid input may reflect an agent decision, unclear documentation or both. | Rename to "Failed requests and candidate infrastructure improvements". Sort comparable categories by count, retain the unresolved grey categories, and add affected-run counts so repeated failures cannot dominate invisibly. |

**New validation for a stronger recovery claim:** identify comparable failure episodes, the subsequent correction, successful execution of the affected step and whether the final result was scientifically accepted. Compare similar error classes/tasks, with uncertainty clustered at the task or source-capsule level. A controlled interface intervention would provide stronger causal evidence than observational conditioning on total errors.

A compact example of a detected parameter mismatch followed by a correction would make the structured-environment benefit tangible. Keep it separate from an example of a scientifically wrong parameter that passed interface validation.

## Figure 4: variability, agreement and rigor

**What it supports.** Answer agreement differs among configurations, and installed-tool request profiles differ. Those are useful observations. Current tool-set similarity has no clear pooled association with accuracy, but that does not establish that analytical diversity is beneficial, harmful or neutral.

| Panel | Strengthen support | Improve the display |
|---|---|---|
| a: top tools | `make_fig4.py:194` counts tool requests with an identifier, including requests without a submitted job. The UDT labels also count requests; Fig. 3b instead requires job records. Label the stage consistently. Generic tabular utilities do not reveal the main scientific method. | Replace four repeated bar charts with a heatmap of method/tool families by configuration and benchmark. Separate data handling from scientific methods, and add UDT method classes after annotation. Put the top-15 inventory in Extended Data. |
| b: same answer | Normalized textual agreement is not biological correctness. Three-significant-digit rounding can merge distinct answers, and missing submissions can count as agreement. Check task-aware numeric tolerance, units, identifiers and alternative valid expressions. State the multiplicity policy for the six model-effect tests. | Keep separate benchmark facets and pair condition markers. Add all-three-correct and agreed-but-rejected rates, or replace the pooled facet with this correctness breakdown. |
| c: tool-set overlap | Rename "trajectory similarity" to "tool-set similarity" for the current statistic. Report eligibility: all three runs must have a submitted job, so the statistic excludes some operational failures. Check results with installed-only, UDT-only and mixed routes separated. Annotate UDT methods, parameters and versions before interpreting analytical-route diversity. | Facet by benchmark. The export's task-level correlations differ markedly: BixBench -0.485, CompBioBench +0.083 and IWC +0.623; these are descriptive, not separate established effects. A single pooled near-zero correlation hides this structure. |
| d: rejected answers/difficulty | Rename "random error" to "discordant answers" and "systematic error" to "same rejected answer in all three runs". The current labels infer mechanisms from repetition. Reference ambiguity and scorer behaviour can also produce repeated rejection. Use held-out difficulty rather than including the focal outcomes. | Include all replicate sets, showing all correct, mixed outcomes, repeated rejection and missing submissions. Facet by configuration if the figure's main claim concerns configuration differences. Show uncertainty across tasks, rather than only failure-conditioned percentages. |

The current normalization produces 36 sets in which all three runs were accepted but their normalized answers differed (`fig4_source_data.csv:451`). That is a useful reminder that exact answer identity is not required for acceptance. Also investigate the three sets labelled "same answer, graded differently" before treating agreement as a scientific endpoint.

**Reanalysis for difficulty:** for each focal task/configuration/condition set, estimate difficulty from the other 21 runs of that task, excluding its three replicates. Show a sensitivity using a held-out model or external task-complexity label. This reduces direct reuse of the outcome; the resulting association still does not identify its cause.

**New validation for rigor:** code actual verification steps across both successful and failed runs: denominator checks, read-position checks, held-out evaluation, independent methods, sensitivity analyses and checks of biological plausibility. Distinguish a check being performed from its evidence changing the conclusion. The existing [rigor interpretation](../manuscript_narrative/original_layout/analysis/rigor_claims.md) has failure-focused annotations and useful cases, but a sample of successful runs is needed to estimate how verification relates to accuracy. Absence of visible reasoning should remain unknown.

The variant-status example in the outline could anchor a small evidence panel: read-position diagnostic, resulting genotype call and outcome across replicates. Label it as a selected case. For consensus, the existing `accuracy_answer_vote_sensitivity.csv` offers a starting point for an outcome-blind majority-answer analysis; answer voting and consensus across independent analytical methods are different interventions.

Suggested figure title: **Answer agreement and tool use vary across model configurations.** Retain the stronger solution-variability wording after the route measurements are improved.

## Figure 5: token demand and inspectability

**What it supports.** Galaxy uses more input tokens on BixBench and CompBioBench under the deployed conditions, and interface activity is strongly associated with accumulated input. The current figure mostly explains token demand; the benefit promised by "inspectability" is confined to source-data rows and prose.

| Panel | Strengthen support | Improve the display |
|---|---|---|
| a: accuracy/token trade-off | It pools the two binary benchmarks, although Fig. 1 says accuracy is not pooled. The displayed 4.7-fold ratio is a geometric mean of paired-cell ratios, which differs from a ratio of totals. Specify the estimand and use matched eligible tasks for both axes. Token counts across different models are not identical monetary costs. | Put log token demand on the horizontal axis and score on the vertical axis, with paired condition points and intervals. Facet by benchmark. Use a small forest plot for Galaxy/code token ratios, including cached and uncached input. |
| b: correct/incorrect runs | The boxes show all runs, but the annotations come only from sets containing both outcomes. The pooled sibling ratios are 1.09 for code (95% CI 0.87-1.37) and 1.07 for Galaxy (0.76-1.51). These intervals permit meaningful differences and do not establish equal cost. Final answer rejection is also different from operational retries. | Replace the large boxes with a ratio forest plot from the actual matched sets, with a reference line at 1. Rename to "No clear input-token difference between correct and incorrect siblings". Move full distributions to Extended Data. |
| c: actions/tokens | Cumulative input and action count are structurally related because later calls include retained context. Correct-run selection also needs a full-run sensitivity. The 2.5-fold action and 1.9-fold tokens/action ratios describe an association, not a proven causal decomposition. | Use a compact paired comparison of actions and tokens/action with intervals; retain the scatter as secondary evidence. Display benchmark-specific results before pooling. |
| d: interface replies | Finding tools accounts for 47.6% of returned characters, not 47.6% of token cost. Unexecuted inspected tools may still be useful candidates. The 96% statistic is the median cached-input share; it does not establish that every reply is retained and reread at every later step. | Keep the discovery emphasis, but label "returned characters", "inspected but not executed" and "cached input" literally. Separate benchmark summaries and move long explanations to the caption. |

**Include the IWC exception.** The existing [token interpretation](../manuscript_narrative/original_layout/analysis/token_results_summary.md) reports Galaxy/code ratios of total input of 4.25 on BixBench, 2.70 on CompBioBench and 0.90 on IWC (IWC 95% CI 0.46-2.88). Its uncached IWC ratio is 1.42 (1.06-2.23). These use a different estimator from the current pooled 4.7-fold figure. Show both the typical paired-task demand and aggregate consumption, with one clearly designated primary. A blanket token-increase claim across all benchmarks would omit the IWC result.

**Add an inspectability panel, after measurement repair.** Compare the evidence actually available for the same analysis units in both conditions: identifiable software/version or environment, recoverable parameters, input/output links and checksums, preserved commands/code and retrievable execution status. Separate native structured metadata from information reconstructable from scripts, logs and environment files. Include UDT source, container/dependencies and parameters. Mark unavailable evidence as unknown rather than assigning absence by execution condition.

The current export's 98.1% Galaxy history figure is evidence of history retrieval, not successful rerunning. A native-provenance comparison can be shown now with precise labels; a stronger reproducibility claim needs a sample of actual reruns and output checks. Blinded reviewer time and agreement in reconstructing an analysis would directly measure the inspectability benefit promised by the subsection.

A main layout with four panels would be more balanced: **benchmark-specific token ratios; actions and reply volume; provenance/evidence availability; one matched analysis record showing what can be inspected.** Keep the model trade-off and sibling distributions in Extended Data if needed. Efficiency changes such as compact replies, reusable discovery results and better diagnostics should be tested as interventions before claiming savings without loss of auditability.

## Layout and caption improvements across the set

- Retain the current orange/blue condition mapping and square/circle redundancy. Where colour represents models, as in Figs. 4 and 5, keep the same model palette and make condition shapes explicit. Use benchmark facets wherever they prevent endpoint mixing.
- Increase the visual priority of estimates and intervals; reduce repeated P values and explanatory paragraphs inside panels. Put one supported finding in each short panel title and detailed definitions in the caption.
- Use 6-7 pt for important labels where space permits, instead of relying on the current 5 pt minimum throughout. The current SVG widths are 180 mm and Fig. 3 is already 170 mm tall, so moving secondary detail to Extended Data is preferable to further shrinking text. Nature's guide specifies 5-7 pt ordinary text, 8 pt bold lowercase panel labels, accessible colours and editable vector artwork. Source: [Nature research figure specifications](https://research-figure-guide.nature.com/figures/preparing-figures-our-specifications/).
- State the unit and denominator for every percentage: requests, jobs, runs, task/configuration sets, tasks or source capsules. Provide coverage/exclusion counts for each panel, particularly comparisons joining grades to traces.
- Distinguish evaluator acceptance, output agreement, analytical correctness, parameter fidelity and successful execution. These are complementary endpoints, not interchangeable names for accuracy.
- Generate captions and annotations from the same exported statistics where possible. A check comparing those values would have caught the recovery-summary ambiguity. Preserve the existing vector exports and source-data tables.

## Recommended work order

| Priority | Action | Work required |
|---|---|---|
| 1 | Correct claim wording, recovery estimand labels, endpoint names and denominator labels. | Existing evidence. |
| 2 | Promote paired accuracy differences; keep IWC continuous; show benchmark-specific token ratios and the IWC exception. | Existing estimates plus layout changes. |
| 3 | Replace tool-request/trajectory labels; expose failed and missing routes; check answer normalization and held-out difficulty. | Reanalysis of retained records. |
| 4 | Repair and display the provenance comparison; add matched concrete examples. | Reanalysis plus limited annotation. |
| 5 | Validate failure attribution and verification in successful as well as failed runs. | New blinded annotation. |
| 6 | Test recovery, replayability and interface improvements directly if causal or reproducibility claims are retained. | New validation or controlled experiments. |

The outline names `results.qmd`, `analysis/` and `data/results_manifest.csv`; those paths are not present at the stated locations in this checkout. The current scripts instead read `manuscript_narrative/original_layout/analysis/`, `manuscript_narrative/derived/galaxy_calls/` and other archived evidence exports. Update manuscript source pointers and retain a traceable chain from plotted statistic to eligible runs, source records, extraction script/version and input hashes.
