# Reassessment of the revised Galaxy manuscript packages

Review date: 2 October 2026. This report supersedes the readiness assessment in `REVIEW_2026-10-02.md`; that earlier review is preserved for comparison.

The revisions substantially improve both papers. Their strongest supported contribution is now a transparent retrospective analysis of execution reliability and interface limitations. Neither the archive nor the prospective protocols establish Galaxy superiority, independent scientific reproducibility or a validated contract that transfers across workbenches. Further archive-supported corrections were implemented during this reassessment, and the four Word documents were rendered and visually checked.

## Scope and evidence

The reassessment covered both manuscript sources, generated Word documents, all 19 main and Extended Data figures and their Source Data workbooks, supplementary tables, protocols, reporting-summary drafts, shared builders and the principal project analyses. Independent checks used the 4,240-run aggregate, per-run archived grades and IWC evaluations, design records, all 69,812 parsed interface calls, parameter-fidelity records, voting sets and targeted audit evidence. Raw binary datasets and the entire trace archive were inventoried rather than read byte by byte. Hidden benchmark ground truth, credentials and the private CompBioBench key were not opened. No new benchmark task, Galaxy call, scientific replay or external message was performed.

The final build regenerates figures, workbooks, numeric estimates, supplementary tables and four DOCX files. It reuses frozen CompBioBench grades. Recomputing those grades independently still requires authorized evaluator access; the one-command build is not an independent scientific reproduction of the benchmark.

## Quality and scope of the two contributions

| Paper | Supported central narrative | Remaining inference limit | Requirement for a stronger contribution |
|---|---|---|---|
| User oriented | Assigned execution arms have similar observed benchmark accuracy; Galaxy has fewer discordant scored outcomes, at greater token and action cost. Installed tools can constrain implementation choices, while also fixing an unintended version or result. | Prompts, budgets, runtime environments and campaigns differ. Repeatability is measured; independent reproducibility and scientific acceptability are not. Only IWC's discordance interval excludes equality. | Independently validated references, matched comparisons including a pinned-code baseline, replay per assigned attempt and weighted expert review. |
| Galaxy oriented | A detailed operational audit separates failures, fidelity coverage, context use and execution attribution. The archive motivates six testable interface requirements. | Error categories do not reliably identify execution phase. Diagnostic excerpts are incomplete proxies. Successful later calls do not prove recovery of the original scientific goal. One public Galaxy deployment cannot establish transfer. | Implement and test interventions with positive, negative and mutation controls, then validate on a second deployment; test another workbench before claiming platform portability. |

The manuscripts now answer different questions. Keep the user paper centred on the reliability, inspectability and cost of the analysis a user receives. Keep the Galaxy paper centred on observable interface behaviour and the requirements it motivates. Shared descriptive measures and the common archive should be disclosed to editors, with the companion manuscript supplied and cited transparently. Two papers are defensible only if each has a substantial independent result; splitting one token-cost comparison into two narratives would not establish that independence.

## Additional corrections implemented

### Failure counts and interpretation

The total remains 7,987 failed Galaxy-interface calls out of 69,505. The full parsed table contains 69,812 calls, including 307 to other servers. The reconciliation is 7,383 Galaxy failures under the earlier extraction rule plus 604 additional exceptions. The legacy ledger's 7,389 includes six non-Galaxy calls; four were unclassified, explaining 258 versus 254 unclassified calls after filtering.

The additional 604 events are now described as transport or tool exceptions, not uniformly as adapter rejections before server execution. At least 47 have Galaxy HTTP-response evidence. Likewise, the 43.2% assigned to interface/input/transport categories cannot be interpreted as the fraction that failed before a job existed: 22 A-class calls returned job records. The manuscripts, figures, taxonomy and supplementary definitions now preserve the distinction between an error category and execution phase. Missing-history and unusable-history classes remain separate.

### Parameter fidelity and denominators

The installed-tool run population contains 17,981 calls. Its mutually exclusive classes are:

| Class | Calls |
|---|---:|
| Reported ok, compared parameters matched | 9,318 |
| Mismatch during request validation | 3,709 |
| Reported failed | 2,713 |
| Reported ok, dataset checks only and zero parameters compared | 1,140 |
| Reported mismatch after execution | 1,098 |
| Reported ok, comparison counts present but parameters not comparable | 3 |

Thus the previous 1,143-call statement combined 1,140 zero-comparison calls with three non-comparable BUILD_LIST calls that had positive comparison counts. Both subgroups remain a verification gap, but they are no longer described as identical. The user paper's comparable-parameter denominator excludes those three calls: 14,503 of 17,180 comparable calls matched.

The independent parameter-mismatch flag identifies 4,999 installed-tool calls, including 251 whose exclusive class is failed. There are 213 dataset-input mismatches and 5,065 calls with either kind. Counting reported mismatch classes alone misses flagged failures and includes some dataset-only mismatches. One additional user-defined-tool call gives 5,000 flagged parameter mismatches across all operation types. Source Data now exposes these overlaps instead of merging incompatible denominators.

### Voting, sensitivity and case evidence

Majority voting is explicitly retrospective. Answers are grouped without looking at correctness, using ten significant digits in rule A and three in rule B; percentage units are retained. The earliest-replicate submitted answer in a majority group is selected, and its archived grade is reused. Choosing the majority grade within the group would introduce outcome information and is no longer used. No-consensus sets and member-grade disagreements are exported. The two-correct-run oracle is only a reference statistic; it is not an upper bound on voting under coarser answer grouping.

For BixBench-Verified-50, rule A produces 84.5% code and 85.5% Galaxy accuracy; rule B produces 87.0% and 87.5%. For CompBioBench, the corresponding values are 89.0% and 87.0%, then 88.5% and 87.0%. These values do not support a universal recommendation to replace one Galaxy run with three code runs.

The headline accuracy sensitivities remain as reported in the revision: the BixBench difference changes from about +1.3 to −1.0 percentage points after removing 15 flagged tasks, and CompBioBench changes from +0.4 to −0.3 after removing 66 paired cells containing outcome-named Galaxy runs. The BixBench exclusion is now consistently described as reference, grading or answer-exposure problems: it includes C1, C2, C3 and C6. Outcome-named campaigns are an observed selection concern, not proof that every such run was selected using its result.

IWC's +0.040 agreement difference reduces to +0.004 after removing the three tasks with a zero-scored run. Its matched-budget subset gives +0.069, but restricting budgets does not match all other arm differences. ATAC references calibrated from evaluated agent runs remain disclosed. IWC agreement is not scientific-validity adjudication, and the omitted significant-gene component remains visible.

The ATAC case now distinguishes seven runs that computed untrimmed peak counts from one additional run that copied a pilot answer. The bix-30-q3 ambiguity and answer exposure, the scientifically defensible bix-45-q1 result and the association wording for PepQuery are retained. A shell-command screen is described as unvalidated; it establishes neither an upper nor a lower bound on off-platform computation. Recovery episodes refer to a later successful call in the same version-stripped tool family, not proven repair of the original analysis. Diagnostic-content claims refer to 240-character archived excerpts, not complete payloads.

### Source Data and build integrity

The workbooks now include per-run sensitivity eligibility, complete-cell token observations, voting-set selection and fidelity/status overlaps needed to reconstruct the displayed contrasts. All 19 workbooks have README and dictionary sheets, with concrete definitions covering every data column. Generic fallback descriptions were removed.

The actual bundled document library is docx 9.6.1, and the package pin and reporting notes now agree with it. The builder accepts confirmed values from `author_metadata.json`; it leaves unknown author facts highlighted. `validate_package.py` checks build tokens, citations, numeric provenance, workbook documentation, figure dimensions, XML structure, file counts and independently audited call-count invariants. It also produces SHA-256 input/artifact hashes and records the actual runtime. These are structural and artifact-consistency checks, not new full OOXML schema validation or biological validation.

## Answers to the remaining decisions

**Publishing the CompBioBench reference value.** Maintainer approval is not established. The [official dataset card](https://huggingface.co/datasets/Genentech/compbiobench-data-v1/blob/main/README.md) identifies CC BY 4.0 for the public questions, metadata and inputs; it does not supply a maintainer decision about disclosure of private grader answers. Prior appearance in `individual_error_analysis.md` is not that approval. Explicit CompBioBench numeric answers were withheld from manuscript case figures and their Source Data while preserving the execution and agreement categories. `COMPBIO_REFERENCE_REQUEST.md` contains an unsent request covering publication permission and independent item-key verification. No maintainer was contacted. Restore the reference only after a documented release decision.

**Author placeholders and AI disclosures.** These cannot be completed from the supplied archive. Thirteen distinct fields remain unresolved across 23 occurrences. The input file records null values and three pending attestations for human audit, release identifiers and CompBioBench evaluator-access terms. Confirm author order, affiliations, contributions, funding, interests, real release identifiers, companion wording, human-review records and AI-tool details. Exact served model versions and completed human verification are not inferred from an assistant role or a subagent audit. The manuscripts explicitly state the pending human-review status.

**New scientific work.** Both supplementary notes are stronger executable study designs. The user protocol adds flexible-code, pinned-code and Galaxy arms; independent references; matched resource policies; replay denominators retaining failed or unreconstructable assigned attempts; weighted expert sampling; a 90% power target, multiplicity control and registration gates. The Galaxy protocol adds measurable intervention effects, biological guardrails, diagnostic-payload preservation and conformance mutation controls. Actual task counts, practical effect targets, any non-inferiority margin and the immutable registration identifier still need to be chosen and frozen. These protocols supply no new empirical result.

**Visual checking.** The bundled runtime successfully renders all four DOCX files without a desktop LibreOffice installation. Every rendered page was inspected. The manuscripts have 27 and 25 pages; the two notes have four and three pages. The heading-only figure page, duplicate footer numbering, figure-width overflow and a cropped border in user Fig. 1 were fixed. Native figure PDFs remain 180 mm wide. Internal reading PDFs and page images are QA intermediates, not submission deliverables.

## Nature Methods fit and the next evidence threshold

The [journal's Analysis guidance](https://www.nature.com/nmeth/content) permits a 150-word abstract, 3,000-word main text and six main display items. The current user and Galaxy abstracts have 149 and 144 words; their main texts have 2,929 and 2,788 words. Each has six main figures and separate Methods, legends and supplementary material. This improves format readiness; it does not guarantee editorial suitability.

The useful style lesson from [Luecken et al.'s integration benchmark](https://www.nature.com/articles/s41592-021-01336-8) is to connect heterogeneous endpoints to decisions researchers need to make, rather than collapse them into a universal ranking. [CellVoyager](https://www.nature.com/articles/s41592-026-03029-6) connects its agent evaluation to expert assessment and biological case studies. Its accessible abstract and figure list informed this comparison; subscription-only prose was not treated as fully reviewed. The editorial interpretation here is that a convincing field contribution needs validated scientific utility or tested infrastructure requirements alongside extensive operational data.

For the user paper, prioritize independent reference adjudication and the result users actually need: a scientifically acceptable analysis that another person can reconstruct or replay within a common intervention budget. For the Galaxy paper, prioritize implementation of the six requirements and evidence that they reduce silent semantic failures without suppressing valid analyses. Preserve the archive as a reproducible diagnostic resource even if a matched prospective comparison shows no accuracy advantage.

## Final verification and readiness

The full build succeeded with pinned analysis dependencies and bundled document dependencies. Default package validation passes with pending submission fields. Submission-mode validation deliberately fails for the 23 unresolved field occurrences and three attestations. `package_validation.json`, `submission_validation.json`, `visual_validation.json` and `release_manifest.json` record the separate outcomes.

Archive-supported editorial, counting, inference and artifact defects found in this reassessment are addressed. Author facts, publication authorization, human verification, independent reference validation and the prospective scientific studies remain open. The two packages are substantially stronger retrospective Analysis drafts, but a claim that all submission or scientific gaps are closed would be inaccurate. Nothing was committed or published.
