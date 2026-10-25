# Scope, presentation and remaining requirements

Revised 2 October 2026. This document applies to the integrated original-layout package; the earlier user-oriented and galaxy-oriented drafts are preserved separately.

## Nature Methods structure

The comparative scope fits an **Analysis**: an unreferenced abstract of at most 150 words (currently 147), up to 3,000 words of main text excluding Methods, references and legends (currently 2,526), up to six display items (six figures), an unheaded introduction, topical Results and Methods subheadings and an unsectioned Discussion. Meeting these limits does not establish editorial suitability. [Nature Methods content types](https://www.nature.com/nmeth/content).

**CellVoyager** separates framework, benchmark evaluation, expert review and biological case studies into successive figures; its expert assessment is real evidence, so this draft does not substitute AI-assisted labels for that component. [CellVoyager](https://www.nature.com/articles/s41592-026-03029-6). **Ahlmann-Eltze et al.** compare added method complexity directly against baselines with robustness analyses; this draft adopts that comparison style. [Gene perturbation prediction benchmark](https://www.nature.com/articles/s41592-025-02772-6).

Results state each finding with its estimate and interval; design and evidence limitations are collected in the Discussion and Methods rather than repeated in every Results sentence.

## What the archive supports

| Requested assertion | Manuscript statement | Requirement for a stronger statement |
|---|---|---|
| Galaxy matches code | Similar performance, differences within about one point of zero on binary benchmarks under sensitivities | Prespecified equivalence margin, matched assignment and adequate power |
| No model fits all | The best configuration depended on the benchmark; leaders' intervals overlap | Registered interaction test with controlled configurations |
| Galaxy stabilizes correct answers | More all-three-correct sets in every configuration's point estimate; the gain is in sporadic failures, persistent failures recur in both arms | More independent clusters and a registered repeatability endpoint |
| Failures reflect rigor, not knowledge | Census of every failing task: agent analysis 57.5%, verification tagged in 57.5% (81.0% of agent-analysis tasks), domain knowledge alone 5.5%, Galaxy platform 9.6%, benchmark-side 31.5% | Blinded expert adjudication with inter-rater agreement; independent knowledge assessment |
| 1–2 errors = trajectory; 3 errors = specification or rigor | Persistent failures enriched for benchmark-side causes (12/25 versus 11/48); Galaxy platform failures almost always sporadic; verification gaps in both | Larger task sample; run-level adjudication |
| Galaxy errors recover better | Not claimed; no matched Galaxy/shell failure episodes | Linked equivalent failure and repair episodes |
| Galaxy uses more tokens everywhere | Ratio of totals 4.25 (BixBench), 2.70 (CompBioBench), 0.90 (IWC); uncached input point estimates higher in all 12 comparisons | Contemporaneous, budget-matched rerun |
| Sol is best per token | GPT-5.5 and Sol form the frontier (6/6 and 5/6 views); Luna and DeepSeek dominated | Prespecified objective and uncertainty-aware ranking |
| Search, UDTs and API calls are the problems | Measured: discovery share, inspected-never-run tools, nonexistent tool IDs, failure classes, UDT failures without diagnostics, identical resubmissions, actions–token correlation | Relevance labels for search; controlled intervention |
| Interface changes reduce tokens | Explicit RESULTS PENDING placeholder; archived 2.82× reference point | Frozen intervention diffs and matched benchmark results with guardrails |

CompBioBench reconstructed-key agreement is distinguished from independent accuracy, IWC workflow agreement from scientific validity, UDT calls from completed jobs, and returned characters from model tokens. Primary and all-archive populations are labelled and reconciled (failure classes sum to the failure union in both populations).

## Changes in this revision

- Token arm comparison switched to the ratio of totals, with uncached input and the median of within-cell ratios as secondary measures; the IWC exception is stated; the archived GPT-5.5 BixBench ratio reproduces the team's 2.8×.
- The audit is described and analysed as a census of failing tasks, with census coverage asserted in the build; new persistent-versus-sporadic and cross-arm analyses (Fig. 4c,d).
- Fig. 6 now shows measured failure classes, UDT call outcomes and responses to failures without diagnostics; Fig. 6f is the placeholder.
- Fig. 1c is a population flow diagram; Fig. 4a,b are charts rather than text; Fig. 5 label overlaps and floating caption removed.
- Model frontier statement corrected (GPT-5.5 on the frontier in all six views).
- Internal file names, package references and collaborator-discussion references removed from the manuscript; the validator now checks for them.

## Work still required

1. **Confirm independent evaluation.** Resolve CompBioBench official-key access and benchmark-side ambiguity; confirm or replace the calibrated IWC routes.
2. **Validate the failure labels.** Blinded expert review with registered codebooks, inter-rater agreement and a probability sample that includes successful runs.
3. **Explain the outcome-named campaigns.** Document the selection rule for the 86 CompBioBench Galaxy runs from campaigns named for wrong answers or target scores.
4. **Complete the intervention loop.** Follow `TOKEN_REDUCTION_PLACEHOLDER.md`; obtain the run records behind the historical 13× and 5.5× ratios.
5. **Establish replay and transfer.** Replay retained artifacts and test a second Galaxy deployment.
6. **Finalize author statements and release identifiers**, and decide the relationship to the two earlier narratives.
