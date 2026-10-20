# Independent audit-of-the-audit: bix-30-q3

Auditor note: this document is a fresh, independent read-through and spot-check of the existing `history_analysis.md` / `history_analysis_evidence.json` package in this directory, produced per `HISTORY_ANALYSIS_INSTRUCTIONS.md`. No existing file was modified or deleted. No agent code was rerun, no Galaxy API was called, and no hidden reference/answer key was opened. All counts below were recomputed from the saved evidence JSON and directory listings using `jq`, `find`, and direct file reads (auditor actions), not by replaying agent transcripts or recovered scripts.

## 1. Task, experimental design, evidence availability, and matching rules

- Benchmark/task: `bixbench` / `bix-30-q3`. Prompt (from `bix-30-q3.json` and confirmed identical in `history_analysis_evidence.json:task.prompt`): "What is the ratio of significant (p <= 0.05) differentially expressed miRNAs between patient and control groups identified following Bonferroni correction compared to Benjamini-Yekutieli correction? Provide your answer as a ratio in the format 'Bonferroni:Benjamini-Yekutieli'." Source dataset `phylobio/BixBench-Verified-50`; `hidden_reference_included: false`.
- 30 observed rows are present in `run_manifest.json` and mirrored 1:1 as 30 run records in `history_analysis_evidence.json:runs` (`jq '.runs | length'` = 30). These cover 5 model labels (Codex GPT-5.5, Codex GPT-5.6 Sol, Codex GPT-5.6 Luna, DeepSeek V4 Pro via Codex, DeepSeek V4 Pro via Claude Code [superseded]) x 2 conditions (`galaxy`, `open_ended_code`) x 3 replicates = 30. Condition labels are preserved verbatim (`original_condition_label`: "Galaxy-API code with skills" / "Open-ended code with skills"); replicate numbers are explicitly documented as labels, not matched seeds (`experimental_design.matching_rule`).
- `experimental_design.coverage_status` = `"unknown_protocol_inventory"` and `expected_replicates: null` — no independent protocol manifest exists beyond the supplied workbook, so expected coverage (as opposed to observed coverage) is genuinely unknown, consistent with what `history_analysis.md` states.
- Known confounders are recorded explicitly: condition-specific prompts/tools, possible container-revision drift, and possible shared source histories.
- Seeds are `not_collected` for all runs; timestamps are largely `null` except `history_create_time` for Galaxy runs.
- 15 distinct Galaxy history IDs are represented in `sources` (verified below), one per (model, replicate) galaxy run, i.e. no history is shared across supplied rows in this task's evidence.
- TLS certificates for the retrieval were **not verified** (`audit.limitations`, `sources[].tls_certificate_verified: false`) — retained-byte hashes do not authenticate the origin server. This is a real, disclosed limitation, not an oversight.

## 2. Main outcomes

**(a) Official accuracy/evaluator score, as recorded.** Each of the 30 runs carries an `outcome.original_evaluator_score` (field name `accuracy.score`, mode `str_verifier`) sourced from each run's own `evaluation.json`. All 30 values are non-null (verified by `jq -r '.runs[] | .outcome.original_evaluator_score'`, all `1.0` or `0.0`). These are the benchmark's own recorded scores for a fixed submitted answer string; they are not an auditor regrade.

**(b) Observed execution facts, as recorded.** The 15 Galaxy-condition runs collectively show 51 distinct Galaxy analytical creating jobs (`sum of .derived_metrics.analytical_job_count` across galaxy runs = 51) of which 23 have a failed/error job status (`sum of .derived_metrics.total_failed_jobs` = 23). These are raw job/event counts from retrieved public Galaxy histories, deduplicated by native job ID; they say nothing about the correctness of the submitted answer. Shell-call counts (`completed_shell_calls`, `nonzero_exit_shell_calls`) are a separate per-run tally that exists for both conditions and is not the same unit as a Galaxy job.

**(c) Auditor interpretation (this audit).** Taken together, in this one task, all Galaxy-condition runs scored 1.0 despite containing a substantial number of failed Galaxy jobs (23/51, i.e. ~45%), while several open-ended-code runs scored 0.0. This case-study pattern is consistent with the Galaxy condition tolerating job-level failures without losing the final scored answer, and with open-ended-code failures (where they occur) being scored as answer misses rather than tallied against a comparable job-failure denominator (no per-job ledger exists for open-ended-code by design — see Section 5). This is a descriptive association for one task, not a claim that Galaxy "recovers better" or is "equivalent" — no comparative recovery-rate or equivalence analysis with a prespecified margin was computed, and none should be inferred from this note.

## 3. Manuscript Results-section questions applied to this task

### Section 4 — Accuracy and output agreement
`history_analysis.md`'s model-by-condition score table (Section 2) reports, for each of the five model labels, a Galaxy mean, a code mean, a percentage-point difference, and a token ratio. I recomputed every cell directly from `history_analysis_evidence.json` (via `.outcome.original_evaluator_score` per run, grouped by model/condition, and via `.comparisons[]` for the pre-computed aggregates) and obtained identical values for all five rows:
- codex_gpt_5_5: galaxy 1.0 vs code 0.667 (33.3 pp) — matches.
- codex_gpt_5_6_luna: 1.0 vs 0.667 (33.3 pp) — matches.
- codex_gpt_5_6_sol: 1.0 vs 0.0 (100 pp) — matches.
- deepseek_v4_pro_via_claude_code_superseded: 1.0 vs 0.667 (33.3 pp) — matches.
- deepseek_v4_pro_via_codex: 1.0 vs 0.0 (100 pp) — matches.
No discrepancy found on any of these ten score values or five differences. The per-run answer strings ("0:0" vs "1:0") were also individually checked against `.outcome.submitted_answer` for all 30 runs and matched the route table in `history_analysis.md` exactly. What remains unresolved: whether "0:0" or "1:0" is the biologically correct ratio is outside this audit's access gate (no hidden reference was opened), so accuracy here means agreement with the fixed-answer evaluator, not verified scientific correctness. Task-level or benchmark-wide equivalence claims are correctly avoided in the source document.

### Section 5 — Execution, failures, and recovery
`history_analysis.md` states "51 distinct analytical creating jobs, including 23 failed jobs" in both Section 2 and Section 3. `jq` recomputation confirms both numbers exactly: `analytical_job_count` sums to 51 across the 15 galaxy runs, `total_failed_jobs` sums to 23, and the `finding_execution` manuscript-finding record independently states `numerator: 23, denominator: 51` with 51 listed `evidence_refs` (one per distinct job event) — internally consistent. Per-run job/failure counts in the Section-4 route table of `history_analysis.md` (e.g. `galaxy_deepseek_v4_pro_via_claude_code_superseded_r1`: "6 / 5" jobs/failed) also matched `derived_metrics.analytical_job_count` / `derived_metrics.total_failed_jobs` for every one of the 15 galaxy rows I checked, and nonzero-shell-call counts matched `derived_metrics.nonzero_exit_shell_calls` for all 30 rows. No discrepancy found here.
Only 2 of 30 runs (`galaxy_deepseek_v4_pro_via_codex_r1`, `galaxy_deepseek_v4_pro_via_claude_code_superseded_r3`) carry a `recovery_episodes` entry, and both are explicitly labelled `"classification_status": "candidate_requires_case_review"` rather than confirmed recoveries — this matches the restrained "candidate for case review" language `history_analysis.md` uses in Section 3, and I found no inflation of this into a stronger recovery claim. "Galaxy only" completion is not asserted anywhere in `history_analysis.md` for this task, correctly, since Galaxy-condition runs also contain non-Galaxy shell/orchestration events (documentation reads, `find`/`ls` probes) that are not analytical computation.

### Section 6 — Solution-route variability
`history_analysis.md`'s route table marks nearly every run "unclassified" except one ("Datamash," for `galaxy_codex_gpt_5_6_luna_r2`). Checking `solution_route.classification` in the evidence JSON for that run confirms `"classification": "Datamash"` with tool IDs including `datamash_transpose`, `Univariate`, and `xlsx2tsv` — a real, specific route indicator, not a placeholder. All other route classifications I sampled were indeed `null`/unclassified in the evidence, consistent with the table. Difficulty is explicitly unclassified (no independent source), and the document correctly declines to infer biological-method equivalence from wrapper/tool similarity. This section is appropriately thin for a single task with mostly unclassified routes; no discrepancy found, and no over-claiming of cross-replicate consistency was observed.

### Section 7 — Token cost, provenance, and readability
All five token-ratio values in the Section-2 table (5.36, 6.08, 5.63, 6.11, 9.02) were recomputed from `.comparisons[]` entries `input_tokens_codex_gpt_5_5` (5.359), `input_tokens_codex_gpt_5_6_luna` (6.081), `input_tokens_codex_gpt_5_6_sol` (5.628), `input_tokens_deepseek_v4_pro_via_claude_code_superseded` (6.110), and `input_tokens_deepseek_v4_pro_via_codex` (9.023). All five match the displayed rounded values. Each comparison record explicitly states `"estimate_unit": "ratio of condition medians"`, matching the document's disclaimer that this is a ratio of condition medians, not a median of paired ratios. No per-call token attribution, stage attribution, monetary cost, or human-readability measurement exists in the evidence, and `history_analysis.md` correctly reports these as unmeasured rather than estimating them.

## 4. Per-condition/model/replicate route table

The 30-row table in `history_analysis.md` Section 4 was re-verified against `history_analysis_evidence.json` field-by-field for: `outcome.original_evaluator_score`, `outcome.submitted_answer`, `derived_metrics.analytical_job_count`, `derived_metrics.total_failed_jobs`, `derived_metrics.nonzero_exit_shell_calls`, and `solution_route.classification`. All 30 rows matched exactly; no cell-level discrepancy was found. I did not rebuild the table from scratch since the existing table is complete and reproducible from the evidence file as checked.

One completeness note (not a discrepancy): each run's `outcome` also carries a `step_completion` sub-object (e.g. `{"score": 0.5, "passed": false, "steps": [...]}`) that is not surfaced anywhere in `history_analysis.md`. This is a distinct workflow/process-completion signal, separate from `original_evaluator_score`, and its omission does not misstate anything already reported — but a reader relying solely on `history_analysis.md` would not know this second scored field exists in the evidence.

## 5. Input sharing, external computation, environment/reproducibility notes

`input_manifest.json` records that 24 of 30 runs share an identical `inputs_manifest.json` SHA-256 (`f260c3f5...2830e`, `count: 1`) and the remaining 6 galaxy runs (`galaxy_deepseek_v4_pro_via_codex_r1/r2/r3` and `galaxy_deepseek_v4_pro_via_claude_code_superseded_r1/r2/r3`) share a second hash (`c16950...81bf`) with `count: 0`, meaning no input file entries were recorded for those 6 galaxy runs by this trace format. A `shared_name_hashes` block also flags `pone.0150501.s002.xls` as appearing under one particular hash across runs. The manifest explicitly disclaims rehashing: "Hashes are copied from original trace manifests; full staged inputs were not rehashed by this audit" — I did not rehash them either, consistent with the retrospective, read-only scope. `environment` fields per run record the Galaxy server (`https://usegalaxy.org`) and a docker image tag distinguishing three harness/date variants (`adaptive-search-20260715`, and later variants implied by the `run_traces_july31_...`, `run_traces_august15_...` trace-URL path segments), which is a real potential confounder across model batches that `history_analysis.md` flags generically as "container revisions may differ" without resolving it further — appropriately left open.

## 6. Verification methods

I ran (via `jq`, `find`, `cat`/`Read` — all auditor actions, no execution of agent code):
- `jq '.runs | length'`, `.runs[] | {run_id, condition, model, replicate_id, status}` — confirmed 30 runs, labels, and condition assignment.
- `jq '.audit, .task, .experimental_design'` — cross-checked task prompt, coverage-unknown status, confounders.
- `jq -r '.runs[] | [.run_id, .condition, .outcome.original_evaluator_score, .outcome.submitted_answer] | @tsv'` — recomputed every score and submitted answer, cross-checked against the Section-4 table.
- `jq '[.runs[] | select(.condition=="galaxy") | .derived_metrics.analytical_job_count] | add'` and the equivalent for `.total_failed_jobs` — recomputed the 51/23 job/failure totals.
- `jq -r '.runs[] | select(.condition=="galaxy"|"open_ended_code") | [...derived_metrics fields...] | @tsv'` — recomputed per-run job/failed/shell-call counts and cross-checked against the route table.
- `jq '.comparisons[] | select(.comparison_id | test("input_tokens"))'` — recomputed all five token-ratio values.
- `jq '.manuscript_findings'`, `.sources`, `.validation` — checked finding numerator/denominator consistency, source/history counts, and schema validation status.
- `find job_ledgers recovered_code selected_outputs source_snapshots -maxdepth 3` — inventoried all four evidence-category subdirectories; confirmed `recovered_code/` contains only an `open_ended_code/` subtree (15 runs, 276 command files, manifest-documented), `job_ledgers/` contains both `galaxy/` and `open_ended_code/` per-run JSON files, `selected_outputs/open_ended_code/manifest.json` explicitly records `"status": "not_collected"` (no code replay), and `source_snapshots/galaxy/<history_id>/` holds `contents.json`, `history.json`, `jobs/`, and `manifest.json` per history.
- Read two `recovered_code/open_ended_code/.../item_*.command.txt` files directly — confirmed they contain real shell command text (e.g. `sed -n '1,220p' /codex_home/skills/transcriptomics/SKILL.md`) with matching SHA-256 hashes in `recovered_code/manifest.json`, not placeholder content.
- Read `run_manifest.json`, `input_manifest.json`, `bix-30-q3.json`, `.analysis_execution.json`, `README.md` in full.

**Not checked / explicitly out of scope:** full byte-level rehashing of all `selected_outputs` and `source_snapshots` files (only the manifest-recorded hashes were read, not recomputed); full replay of all 30 agent transcripts event-by-event (only representative events and derived-metric aggregates were inspected); execution of any recovered command; live Galaxy API access; opening of any hidden BixBench reference/answer key; independent verification of the `input_manifest.json` inventory-source SHA-256 against the original `.xlsx` workbook (not present in this directory).

## 7. Claim-to-evidence pointer list

| Claim in this report | Source file / field / jq path |
|---|---|
| 30 runs, 5 models x 2 conditions x 3 replicates | `run_manifest.json:observed_rows`; `history_analysis_evidence.json: .runs \| length` = 30 |
| Prompt text and task ID | `bix-30-q3.json:prompt`; `history_analysis_evidence.json:.task.prompt` |
| Coverage unknown (no independent protocol) | `history_analysis_evidence.json:.experimental_design.coverage_status` |
| 15 distinct Galaxy histories | `history_analysis_evidence.json:.sources[] | select(source_id ~ "^src_galaxy_")` sorted-unique count = 15 |
| TLS not verified | `history_analysis_evidence.json:.sources[].tls_certificate_verified` = false; `.audit.limitations` |
| Per-run evaluator score / submitted answer (all 30) | `history_analysis_evidence.json:.runs[].outcome.{original_evaluator_score,submitted_answer}` |
| Model-by-condition mean scores and pp differences (5 rows) | `history_analysis_evidence.json:.comparisons[] | select(comparison_id ~ "^score_")` |
| Token ratios (5 values: 5.36/6.08/5.63/6.11/9.02) | `history_analysis_evidence.json:.comparisons[] | select(comparison_id ~ "^input_tokens_")` |
| 51 distinct analytical jobs / 23 failed | `history_analysis_evidence.json:.runs[*].derived_metrics.analytical_job_count` (sum=51) and `.total_failed_jobs` (sum=23); cross-checked against `.manuscript_findings[] | select(finding_id=="finding_execution")` numerator/denominator |
| Per-run job/failed/shell-call counts (route table) | `history_analysis_evidence.json:.runs[].derived_metrics.{analytical_job_count,total_failed_jobs,nonzero_exit_shell_calls}` |
| Only one classified route ("Datamash") | `history_analysis_evidence.json:.runs[] | select(run_id=="galaxy_codex_gpt_5_6_luna_r2") | .solution_route.classification` |
| Only 2/30 runs have recovery episodes, both "candidate" status | `history_analysis_evidence.json:.runs[] | select(.recovery_episodes | length>0)` |
| `step_completion` field present but not surfaced in history_analysis.md | `history_analysis_evidence.json:.runs[0].outcome.step_completion` |
| recovered_code scoped to open_ended_code only (15 runs, 276 files) | `recovered_code/manifest.json:.items`; `find recovered_code -maxdepth 2` |
| selected_outputs/open_ended_code not collected (no replay) | `selected_outputs/open_ended_code/manifest.json` |
| Shared input hash across 24/30 runs; 6 galaxy runs with count:0 | `input_manifest.json:.runs`, `.shared_name_hashes` |
| Schema validation passed | `history_analysis_evidence.json:.validation.schema.validation_status` |

## 8. Missing evidence and open gaps (specific to this task)

- No independent experiment manifest/protocol exists to define expected replicate counts or seed matching; coverage is genuinely unknown, not merely unreported.
- TLS was not verified for the retrieval session; retained hashes authenticate local bytes, not the remote server identity.
- `input_manifest.json` counts are copied from original per-run trace manifests, not independently rehashed by any audit; the original `.xlsx` inventory workbook itself is not present in this directory to re-verify `inventory_source_sha256` against.
- No comparable per-job ledger exists for `open_ended_code` runs (by design — that condition has no Galaxy jobs), so job-level failure/recovery comparisons across conditions cannot be constructed on a common unit without a separately defined cross-condition "scientific attempt" codebook, which is not present here.
- Scientific (as opposed to evaluator-string) correctness of either submitted answer ("0:0" vs "1:0") cannot be assessed without opening a hidden reference, which this and the underlying audit correctly decline to do.
- No human-readability review, per-call token attribution, or monetary cost data exist for this task.

## Abstract-ready paragraph

For bixbench task bix-30-q3, I independently re-derived the following from `history_analysis_evidence.json` and confirmed they match `history_analysis.md`: all 30 supplied runs (5 model labels x 2 conditions x 3 replicates) carry a non-null original evaluator score; the five model-level Galaxy-vs-open_ended_code score comparisons (33.3, 33.3, 100, 33.3, and 100 percentage points) and the five Galaxy/code median input-token ratios (5.36, 6.08, 5.63, 6.11, 9.02) recompute exactly from the underlying per-run fields and comparison records. The 15 Galaxy-condition runs' retrieved public histories expose 51 distinct analytical creating jobs, of which 23 carry a failed/error status, both values recomputed by summing per-run `derived_metrics` and cross-checked against the evidence file's own `finding_execution` numerator/denominator. Only 2 of 30 runs carry a recorded recovery episode, and both are explicitly flagged as requiring further case review rather than confirmed as scientific recoveries. These are case-study counts for one task and do not support benchmark-wide, causal, or equivalence claims.
