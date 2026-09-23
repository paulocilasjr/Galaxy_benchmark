# IWC recovery, completeness and evidence limitations

Audit revision: 23 September 2026. This document governs three terms that are routinely conflated in agent-benchmark reporting, and keeps them separate throughout:

- **Archive recovery** — retrieving and preserving evidence about a run.
- **Operational recovery** — a failed operation followed by a supported resolution of the *same* objective.
- **Scientific success** — a judgement by the applicable evaluator or by scientific assessment.

These endpoints are not interchangeable, and evidence for one is not evidence for another. A run can be fully archived, operationally recovered and still scientifically wrong; it can also be scientifically correct with an incomplete archive. This revision analyses existing local bytes only and leaves snapshots unchanged.

## 1. What is available locally

| Evidence category | Observed coverage | Interpretation |
|---|---:|---|
| Workbook-linked runs | 240 | All observed rows represented; prospective expected coverage unknown |
| Trace directories | 240 | Directory retrieval is not complete byte recovery |
| Retained trace files | 5,645; 2,932,706,102 bytes | Prompts, evaluators, invocations, logs, code and selected answers |
| Linked large trace-file records | 123 | Metadata and remote links retained; bytes absent locally |
| Evaluator files | 240 | All identify `iwc-final-answer-v2.2` |
| Numeric evaluator scores | 237 | Three explicit unsupported-route outcomes remain null |
| Harness run records | 240 `complete` | An operational state, not a scientific-success count |
| Terminal usage records | 240 | Exactly one selected terminal record per run |
| Detailed Galaxy histories | 118/120 | Current snapshots; original action ownership not fully resolved |
| Metadata-only Galaxy histories | 2/120 | Both amplicon-denoising histories exceeded the collector content cap |
| Galaxy job-file entries | 2,173 | Shared IDs collapse to 1,607 distinct creating jobs |
| Selected Galaxy output files | 1,278 | Retained bytes, not dataset metadata records |
| Explicitly skipped Galaxy outputs | 190 | Not an exhaustive count of all unretained contents |
| Evaluator-listed final-answer references | 286 retained / 360 listed | 74 unresolved local references; answer bytes are not fully recovered |

An earlier per-task aggregate counted 4,586 history-associated artifact records as selected outputs; those include metadata without downloaded bytes. The correct retained-output total is 1,278, resolved from collection manifests. Galaxy selections and evaluator-listed final-answer files are different populations and must not be summed.

The [scientific audit JSON](iwc_scientific_audit.json) is authoritative for this revision's extraction. Legacy `iwc_recovery_summary.json`, `iwc_overview_audit.json` and per-task reports remain preserved historical products. Their null score and usage fields reflect extraction limitations: the original evaluator and terminal usage records are present. Do not run the legacy report generator over the revised Markdown.

## 2. Unavailable and partially observed evidence

### Metadata-only histories

| Task and run | History ID | Reported content count | Consequence |
|---|---|---:|---|
| Amplicon denoising, Galaxy Luna r2 | `bbd44e69cb8906b5d30ea6e81e388ed2` | 421 | No detailed collected contents or job ledger |
| Amplicon denoising, Galaxy DeepSeek r2 | `bbd44e69cb8906b5ee1171e94c720212` | 421 | No detailed collected contents or job ledger |

The collector's `max_contents` setting was 300. These runs retain trace and evaluator evidence and enter score and usage summaries, but are excluded from denominators that require observed native jobs. **Their failure counts are unknown, not zero**, and a capped history is not a failed experiment. The [snapshot manifests](analysis/wf_005_amplicon_dada2_pe_denoising/source_snapshots/galaxy/) record the cap and collection status.

### Trace and artifact limitations

Selected JSONL traces contain 25 unparseable lines across 25 runs. Valid terminal usage survives, but event-level completeness cannot be assumed. Compressed traces take precedence where present, without adding duplicate representations; the plain Galaxy Sol pseudobulk r3 trace lacks a terminal event and its retained compressed counterpart supplies one. The audit records the selected source hash and line for every usage record.

Large linked files remain scientifically important even when excluded from collection. Their locations and collection metadata are preserved per run. The 123 trace links and 190 skipped Galaxy records are different populations and must not be summed as unique missing outputs. Absence from the selected-output directory does not prove that the original agent failed to create a dataset, and no linked file was assigned an invented hash.

All 120 Galaxy manifests state `tls_certificate_verified: false`. Retained SHA-256 hashes establish consistency with locally collected bytes, not server authenticity at retrieval. Any independently authenticated recollection should be versioned separately rather than silently overwriting these snapshots. The Hugging Face reference is `main`; hashes anchor this local collection, but no collection-wide immutable upstream revision was established.

## 3. Score recovery and unresolved adjudication

The earlier aggregate read a field the task extractor never populated. Reading the original `evaluation.json` `reference_accuracy` recovers 237 numeric records **without rerunning any evaluator**. Metric descriptions, errors, route declarations and versions are preserved in the supplement.

| Issue | Affected records | Reporting rule |
|---|---:|---|
| Unsupported host-removal route | GPT-5.5 open-ended code r1–r3 | Keep null; declarations are BWA / minimap2 / minimap2 |
| Host-removal evaluator/run-record conflicts | Five, including three nulls and Galaxy Luna r1/r3 | Preserve both scores; request route and reference adjudication |
| Chromatin-accessibility conflicts | Twelve | Report the saved evaluator version, retain the old `acc`, require freeze and lineage confirmation |
| Exactly zero saved scores | Six: two amplicon denoising, three assembly, one pseudobulk | Keep recorded zeros and their distinct meanings; no answer repair |

Conflict tolerance is an absolute difference greater than 1 × 10⁻⁹, or numeric-versus-null disagreement; there are 17 conflicting records. Galaxy Luna host-removal r1 and r3 carry saved scores of 0.27301 and 0.27299 against run-summary values of 0.9999 and 1.0, with no evaluator route record despite BWA-family declarations. Discrepancies are never resolved by choosing the more favourable source.

**These five records are load-bearing, not clerical.** They determine whether Luna's environment difference is +0.001 or −0.048, and — because only eight runs in the whole cohort score below 0.5 — whether Galaxy has one or three sub-0.5 runs. Two of the three sub-0.5 Galaxy runs are exactly these conflicted records. Score lineage is therefore a result in its own right, not a data-availability footnote.

## 4. Operational failures and recovery candidates

Server and job-ID deduplication yields 277 acquisition jobs (255 fetch, 22 upload) and 1,330 other creating jobs. All acquisition jobs are `ok`; other jobs comprise 1,112 `ok`, 202 `error` and 16 `deleted`. Other jobs include wrappers, utilities and interactive environments as well as domain analysis, so they are not 1,330 scientific attempts. Deleted states are not counted as errors.

Among the 118 Galaxy runs with detailed histories, 75 have at least one observed error job: 63.6%, median 1 per run, IQR 0–2.75, range 0–14. This includes error-free runs and does not discard zero-scored runs. No correctness-conditioned recovery rate is supplied, because the endpoint is continuous and no binary threshold is defined.

There are **41 candidate failure-to-success links across 26 runs**, involving **41 distinct failed endpoints and 27 distinct successful endpoints**; several failures share one success. The detector links the same tool and input HDA IDs to a later successful job. These are candidate operational resolutions, not validated diagnoses, independent scientific attempts or evidence of acceptable final answers. A denominator such as "41/202 recovered" would be unjustified.

**Two asymmetries prevent any cross-environment recovery claim.** First, the detector operates on Galaxy job records; **no equivalent detector exists for open-ended code**, whose shell exits are a different unit and may represent deliberate diagnostics. Second, failed-job stderr and launch commands are frequently absent, so corrective mechanisms cannot be attributed. Reporting a Galaxy recovery count beside a code shell-exit count would compare two incommensurable quantities.

The short-read QC GPT-5.5 Galaxy r3 case illustrates the limit: two failed fastp launches precede one successful launch on the same paired-read IDs, with a changed collection association and a final agreement of 1.0. Because failure messages are missing, the corrective mechanism is unresolved. The [results report](result_section_iwc.md) links the raw jobs and records parameters, times and output counts. It is a case study, not evidence that either environment improves recovery.

## 5. Completion does not imply correctness

All 240 harness records report `complete`, yet six runs score zero for three distinct, diagnosable reasons: altered sample-identifier casing in two amplicon-denoising runs; FDR values inconsistent with Benjamini–Hochberg adjustment of the submitted p-values in one pseudobulk run; and sequence-content disagreement in three assembly runs, one of which is a Galaxy run. None of these is detectable from harness status, exit code or Galaxy job state.

This is the clearest completeness finding in the archive: **process-level evidence and final-artifact validity are independent axes**, and an evaluation that monitors only the former would have reported a fully successful cohort. Conversely, near-unity agreement does not guarantee an identical scientific decision — one RNA-seq run scoring 0.999966 reported 12 significant genes against 13 in the reference. Final-artifact contract checks and component-level diagnostics are therefore necessary alongside execution monitoring, in both environments.

## 6. Verification and provenance

The [audit script](audit_iwc_results.py) performs these local checks, and [the regression suite](test_iwc_scientific_audit.py) guards them:

- Joins workbook task and run IDs and verifies 240 unique runs in 80 three-replicate analysis cells.
- Extracts both score sources, original metric, version and route fields, runtime model and reasoning settings, prompt and input hashes, and budgets.
- Selects exactly one terminal usage record per run and records malformed-line locations rather than assuming complete traces.
- Checks 9,096 retained trace, output and job-file entries against manifest hashes, with sizes where recorded: **zero mismatches**. Job-file entries can share native IDs and are deduplicated separately for analysis.
- Hashes 1,667 source files used by the aggregate, including task evidence, workbook, collection manifests, evaluators, run records, invocations, selected traces, prompts, method declarations and the calculation script.
- Preserves included run IDs for paired comparisons and finding sets, with seeded task-bootstrap calculations and no imputation of null scores.

The [sensitivity analysis](iwc_sensitivity_analysis.py) adds distribution, leave-one-task-out influence and zero-run mechanism checks over the same audited records, reading only the audit JSON.

These checks establish local preservation and internal accounting — not source-claim truth, full chronology, independent scoring validity or completeness of unretained files. Original task evidence, redacted derivatives and collection manifests remain untouched. This revision neither opened hidden references nor executed archived analysis code.

## 7. Next evidence priorities

1. Resolve the 17 score conflicts and freeze evaluator and reference lineage with authenticated provenance, beginning with host removal, since five records there change a headline comparison.
2. Obtain a dated protocol, prospective inventory, seeds and run-independence metadata.
3. Recover the two capped histories and the scientifically necessary linked bytes under authenticated transport.
4. Establish run-owned event windows and shared input/output provenance, so history-associated counts become agent-attributable.
5. Build a **symmetric** stage, attempt and recovery codebook applied to both environments, replacing the current Galaxy-only detector.
6. Add final-artifact contract checks — identifier normalization, statistical self-consistency, content agreement — as first-class reported outcomes rather than incidental evaluator behaviour.

Resource and interpretability claims additionally need a common billing basis, measured compute costs, stage-level token attribution and a prespecified blinded reviewer study. Higher typical token usage does not prove more retries, and structured provenance does not prove faster review. This archive supports auditable exploratory analysis; it should not be described as a complete independent reproduction of the original runs.

No additional downloads, benchmark executions, hidden-ground-truth access, commits or pushes were performed for this revision.
