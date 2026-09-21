# Cloud independent audit report: bix-31-q2

This report is an independent read-through and spot-check of the existing `history_analysis.md` / `history_analysis_evidence.json` package for this single BixBench task. It was produced read-only, following `HISTORY_ANALYSIS_INSTRUCTIONS.md`: no agent code was re-executed, no live Galaxy API was called, and no hidden answer key was opened. It does not replace `history_analysis.md`; it is a second-pass verification layer.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task/prompt** (from `history_analysis_evidence.json` `.task.prompt`, confirmed identical to the prose in `history_analysis.md` section 1): "Using the batch-corrected read counts with batch as a covariate in the design formula, perform a sex-specific (M vs F) differential expression analysis (abs lfc>0.5, basemean>10 and using lfc shrinkage), what is the log2 fold change of FAM138A? Use pydeseq2 with default shrinkage method." Input specification: `phylobio/BixBench-Verified-50`.
- **Runs**: `.runs | length` = 30, matching the "30 workbook rows" / "30/30" claims in `history_analysis.md`. `input_manifest.json` also lists exactly 30 `observed_rows`.
- **Conditions**: `galaxy` (15 runs) and `open_ended_code` (15 runs), preserved as distinct labels throughout; `experimental_design.conditions` in the evidence JSON lists exactly these two.
- **Models/replicates**: five model labels, three replicates each, 2 conditions x 5 models x 3 replicates = 30: `Codex GPT-5.5`, `Codex GPT-5.6 Sol`, `Codex GPT-5.6 Luna`, `DeepSeek V4 Pro via Codex`, `DeepSeek V4 Pro via Claude Code (superseded)`.
- **Coverage/matching**: `experimental_design.coverage_status` = `"unknown_protocol_inventory"` and `expected_replicates: null` — there is no independently supplied protocol manifest, so whether 3 replicates per condition/model was the intended design (versus an artifact of what happened to be linked) is unknown. The matching rule recorded is "same task and supplied model label; replicate numbers are labels, not matched seeds." Seed availability is `not_collected`.
- **What is unknown/unverifiable**: expected coverage, seeds, stopping rules, whether replicate 1/2/3 across conditions used matched seeds, and whether the "DeepSeek V4 Pro via Claude Code (superseded)" label reflects a verified runtime identity or a supplied label only (the evidence JSON's `model` object should be checked per-run for `verification_status`; this audit did not exhaustively re-verify that field for every run, see Section 6).

## 2. Main outcomes (kept separate)

**(a) Official accuracy / evaluator score, as recorded.** All 30 runs carry a non-null `outcome.original_evaluator_score` under field name `accuracy.score`, evaluator mode `"range_verifier"`. Scores are binary (0.0 or 1.0) per run in this evidence set. Aggregated by model (mean of 3 replicates per condition): Codex GPT-5.5, Codex GPT-5.6 Sol, and Codex GPT-5.6 Luna each scored 1.0/1.0 in both conditions (all 3 replicates correct in both galaxy and open_ended_code). DeepSeek V4 Pro via Claude Code (superseded) scored galaxy=1.0 mean, open_ended_code=0.0 mean. DeepSeek V4 Pro via Codex scored galaxy=0.333 mean, open_ended_code=0.667 mean. These are the original evaluator's numbers, not an auditor recomputation of correctness.

**(b) Observed execution, as recorded.** Per-run `derived_metrics` in the evidence JSON record `analytical_job_count`, `total_failed_jobs`, `completed_shell_calls`, `nonzero_exit_shell_calls`, and `completed_mcp_calls` for each run (null where evidence was unavailable, e.g. `galaxy_deepseek_v4_pro_via_codex_r2` has `analytical_job_count: null`). Summed across the 15 galaxy runs, `analytical_job_count` totals 71 when the one null value is excluded, and `total_failed_jobs` totals 19 under the same exclusion — see Section 3 for the calculation.

**(c) Auditor interpretation (this audit only).** Within this one task, the three Codex-family models show identical binary scores across both conditions (all runs = 1), so this task does not by itself provide a case where Galaxy and open_ended_code diverge for those models — it is a case of observed agreement, not evidence of general equivalence (no margin was prespecified, so "equivalent" is not asserted here). The two DeepSeek-family configurations move in opposite directions (one favors galaxy by 100 pp, the other favors open_ended_code by 33.3 pp), which is consistent with high run-to-run/model-to-model variability on n=3 replicates rather than a stable condition effect; this is an observed association within one task, not a generalizable causal claim about Galaxy versus open-ended code.

## 3. Walk-through of the four manuscript Results questions for this task

### Accuracy and output agreement by execution condition
All 30 runs have an original `accuracy.score` value (never null), so evaluator coverage is complete for this task. Scores are binary and are not pooled across conditions in `history_analysis.md`'s table or in this audit — Galaxy and open_ended_code means are reported side by side, not merged. `history_analysis.md`'s table (Section 2) reports, e.g., `deepseek_v4_pro_via_claude_code_superseded`: Galaxy=1, Code=0, diff=100 pp; `deepseek_v4_pro_via_codex`: Galaxy=0.333, Code=0.667, diff=-33.3pp. I recomputed these directly from `.comparisons[]` in the evidence JSON (`comparison_id: score_deepseek_v4_pro_via_claude_code_superseded` → `galaxy_mean: 1.0, code_mean: 0.0, estimate: 100.0`; `comparison_id: score_deepseek_v4_pro_via_codex` → `galaxy_mean: 0.333…, code_mean: 0.667…, estimate: -33.33…`) and they match the table exactly. Unresolved: no independently defined difficulty label, no seed matching, and no benchmark-wide inference is possible from n=3 replicates per cell.

### Analysis execution, failures, and recovery
`history_analysis.md` states "71 distinct analytical creating jobs, including 19 failed jobs" (public Galaxy histories only). I recomputed this by summing `derived_metrics.analytical_job_count` and `derived_metrics.total_failed_jobs` across the 15 `condition == "galaxy"` run records (one run, `galaxy_deepseek_v4_pro_via_codex_r2`, has both fields `null` and was excluded from the sum, consistent with "unavailable" rather than zero):
- Sum of `analytical_job_count` over the 14 non-null galaxy runs = 71.
- Sum of `total_failed_jobs` over the same 14 runs = 19.
Both figures match `history_analysis.md` exactly. No discrepancy found on this claim. The document is careful to say these are deduplicated distinct creating jobs (not raw shell/MCP call counts), which is consistent with the evidence JSON's separate `completed_shell_calls`/`completed_mcp_calls` fields being much larger (e.g. `galaxy_deepseek_v4_pro_via_codex_r3`: 375 shell calls, 33 nonzero-exit, vs. only 38 analytical jobs / 3 failed) — this is the same distinction the instructions require (tool-call count ≠ job count ≠ scientific-attempt count), and the document respects it. `failed_jobs_before_first_supported_result` and `failed_attempts_before_first_correct_answer` are `null` for every run inspected — the document does not report a "failures before result" statistic, which is consistent with not having chronology-confirmed endpoints.

### Solution-route variability across models and replicates
`solution_route.classification` is `null` for every run I sampled (e.g. run 1's `solution_route` block: `"classification": null`, `"tool_ids": ["pydeseq2_sex_m_vs_f_batch_covariate_v1"]`, `"biological_method": null`). `history_analysis.md`'s route table correspondingly marks every galaxy row "unclassified" and every open_ended_code row "local shell or script; method unclassified" rather than asserting a route codebook classification. This is consistent — the document does not overclaim route classification beyond what the evidence supports.

### Token cost, provenance, and human readability
`history_analysis.md`'s Section 2 table reports Galaxy/code median input-token ratios per model: e.g. `deepseek_v4_pro_via_codex`: 10.7. The evidence JSON's `comparisons[]` records `comparison_id: input_tokens_deepseek_v4_pro_via_codex` → `galaxy_median: 61136991, code_median: 5695558, estimate: 10.734153001338939`. 61136991/5695558 = 10.734…, rounds to 10.7 — matches. I also checked `codex_gpt_5_5` (0.443 in the table vs. `estimate: 0.443241694626908` in the JSON — matches), `codex_gpt_5_6_luna` (0.433 vs 0.4325907284372302 — matches), `codex_gpt_5_6_sol` (0.265 vs 0.26504315577200815 — matches), and `deepseek_v4_pro_via_claude_code_superseded` (0.851 vs 0.8506804122100495 — matches). All five reported ratios reproduce from `.comparisons[]` medians. No per-call attribution, no cost-in-dollars figures, and no human-readability measurement are claimed in the document, consistent with none being present in the evidence JSON.

**No unresolved discrepancy was found between `history_analysis.md`'s stated numbers and the evidence JSON for any of the values checked above** (run count, per-run scores/answers, per-model score means/differences, job/failure sums, and all five token-ratio figures).

## 4. Per-condition/model/replicate route table

Reused from `history_analysis.md` Section 4 (30 rows); verified against the evidence JSON as follows:
- All 30 `run_id`s in the table match `.runs[].run_id` in the evidence JSON exactly (checked via `jq '.runs[].run_id'`).
- Every `outcome.original_evaluator_score` and `outcome.submitted_answer` value I extracted per run (via `jq -c '.runs[] | {run_id, score: .outcome.original_evaluator_score, answer: .outcome.submitted_answer}'`) matches the table's "Score field/value" and "Answer" columns verbatim, including the long floating-point answer strings.
- Every `derived_metrics.analytical_job_count` / `derived_metrics.total_failed_jobs` pair matches the table's "Galaxy analytical jobs / failed" column, including the two runs marked "unavailable / unavailable" (`galaxy_deepseek_v4_pro_via_codex_r2`, where both underlying fields are JSON `null`).
- Every `derived_metrics.nonzero_exit_shell_calls` value matches the table's "Nonzero shell calls" column for all 30 runs, both galaxy and open_ended_code.

No discrepancy found in the route table.

## 5. Input sharing, external computation, environment/reproducibility notes

- `input_manifest.json` records a `shared_name_hashes` block showing that five named input files (`BatchCorrectedReadCounts_Zenodo.csv`, `FlowSorterFraction_Zenodo.csv`, `GeneMetaInfo_Zenodo.csv`, `RawReadCounts_Zenodo.csv`, `Sample_annotated_Zenodo.csv`) have a single hash each across all runs that report a non-zero input count, with `all_trace_input_hashes_agree_by_name: true`. The manifest explicitly notes: "Hashes are copied from original trace manifests; full staged inputs were not rehashed by this audit" — so byte-identity is supported by name+hash agreement in the original trace manifests, not by independent re-hashing in this audit chain.
- Three DeepSeek-via-Codex/Claude-Code galaxy runs (`_r1`, `_r2`, `_r3` for both model variants) show `count: 0` for `inputs_manifest.json`, meaning no local input-file manifest was captured for those six runs; this is recorded as `status: "retrieved"` for the manifest file itself but with zero listed inputs, not as a missing-file error.
- Public Galaxy history retrieval is explicitly flagged as not TLS-verified: `audit.limitations` states "Source TLS certificates were not verified because the host proxy presented an invalid certificate; local retained-byte hashes do not authenticate the remote server." This is a real reproducibility caveat that should carry forward into any manuscript language about Galaxy-side provenance.
- `recovered_code/manifest.json`'s top-level `execution_claim` field states "Archival extraction only; no recovered code executed," consistent with the retrospective-only scope boundary.

## 6. Verification methods

**What was checked**: `ls -la` on the task directory; full reads of `README.md`, the current `history_analysis.md`, `run_manifest.json`, and `input_manifest.json`; the following `jq` queries against `history_analysis_evidence.json`: `.runs | length`; `.audit, .task, .experimental_design`; `.runs[0] | keys` and `.runs[0].outcome` (to locate the correct score/answer field paths); `.runs[] | {run_id, condition, model: .model.supplied_label, status, score: .outcome.official_score}` (initial pass, revealed a wrong field-path guess, corrected below); `.runs[] | {run_id, score: .outcome.original_evaluator_score, answer: .outcome.submitted_answer}` for all 30 runs; `.runs[0].derived_metrics, .runs[0].solution_route`; `.runs[] | select(.condition=="galaxy") | {run_id, derived_metrics}` and the open_ended_code equivalent for `nonzero_exit_shell_calls`; `.comparisons` (full array, 10 entries — 5 score comparisons + 5 token-ratio comparisons); `.manuscript_findings[] | {finding_id, section}`. Directory inventory via `find job_ledgers recovered_code selected_outputs source_snapshots -maxdepth 3` plus targeted `find`/`ls` counts per condition subfolder. Two recovered-code files were opened and read: `recovered_code/galaxy/galaxy_codex_gpt_5_5_r1/…_run_pydeseq2.py` (a plausible pydeseq2 wrapper script with sex/batch validation logic) and `recovered_code/open_ended_code/open_ended_code_codex_gpt_5_5_r1/item_2.command.txt` (a plausible shell heredoc checking the installed `pydeseq2` version).

**What was not checked**: byte-level re-hashing of any staged input or output file (the audit's own `input_manifest.json` already discloses it did not rehash large inputs, and this second-pass audit did not either); full transcript replay or execution of any recovered script/command; verification of `model.verification_status`/runtime-ID confirmation for every one of the 30 runs individually (only run 0's structure was inspected in depth); exhaustive review of all 489 `recovered_code/open_ended_code` files or all 30 `job_ledgers` files (a small sample was read); the `history_analysis_evidence.schema.json` was not used to run a formal schema validation pass in this audit (that is a distinct, heavier check `validate.py` is described as performing per `history_analysis.md` Section 6).

## 7. Claim-to-evidence pointer list

| Claim in this report | Source file / field |
|---|---|
| 30 runs, 15 galaxy / 15 open_ended_code | `history_analysis_evidence.json` `.runs | length`; `.runs[] | .condition` tally |
| Task prompt and input specification | `history_analysis_evidence.json` `.task.prompt`, `.task.input_specification` |
| Coverage/matching unknown, no expected replicate count | `history_analysis_evidence.json` `.experimental_design.coverage_status`, `.expected_replicates` |
| Per-model/condition score means and pp differences | `history_analysis_evidence.json` `.comparisons[]` (`comparison_id` starting `score_`) |
| 71 analytical jobs / 19 failed jobs (galaxy) | `history_analysis_evidence.json` `.runs[] | select(condition=="galaxy") | .derived_metrics.analytical_job_count / .total_failed_jobs`, summed by this audit |
| Token ratio figures (0.443, 0.433, 0.265, 0.851, 10.7) | `history_analysis_evidence.json` `.comparisons[]` (`comparison_id` starting `input_tokens_`) |
| Route table run IDs, scores, answers, job counts, shell-call counts | `history_analysis_evidence.json` `.runs[].outcome`, `.runs[].derived_metrics`, cross-checked against `history_analysis.md` Section 4 table |
| Shared input hashes across runs | `input_manifest.json` `.shared_name_hashes`, `.all_trace_input_hashes_agree_by_name` |
| TLS not verified for Galaxy retrieval | `history_analysis_evidence.json` `.audit.limitations` |
| No recovered code executed | `recovered_code/manifest.json` `.execution_claim` |
| Recovered code samples look genuine | Direct read of `recovered_code/galaxy/galaxy_codex_gpt_5_5_r1/…run_pydeseq2.py` and `recovered_code/open_ended_code/open_ended_code_codex_gpt_5_5_r1/item_2.command.txt` |

## 8. Missing evidence / open gaps

- No independent experimental-protocol manifest exists to confirm that 3 replicates per condition/model was the intended design rather than the set of links that happened to be supplied.
- Seed values are not collected for any run; replicate numbers cannot be treated as matched seeds.
- `galaxy_deepseek_v4_pro_via_codex_r2` has null `analytical_job_count`/`total_failed_jobs` — this run's Galaxy-side execution detail is unavailable, not zero, and is excluded from the 71/19 totals above (consistent with `history_analysis.md`'s own "unavailable/unavailable" table entry for that run).
- `failed_jobs_before_first_supported_result` and `failed_attempts_before_first_correct_answer` are null for all runs sampled; no chronology-confirmed "failures before result" statistic exists for this task.
- Solution-route classification is null for every run; no biological-method or parameter-level route codebook has been applied.
- No per-call token attribution, monetary cost, or human-readability review exists for this task.
- Runtime-model-ID verification status was not individually re-confirmed for all 30 runs in this audit pass (only inspected in the run-1 example).

### Abstract-ready paragraph

For BixBench task bix-31-q2, 30 audited runs (15 Galaxy, 15 open_ended_code; 5 models x 3 replicates each) all carry a non-null original `accuracy.score`. Three Codex-family model configurations recorded identical mean scores (1.0) in both conditions across 3 replicates each; the two DeepSeek-family configurations diverged, one favoring Galaxy by 100 percentage points and the other favoring open_ended_code by 33.3 percentage points (n=3 replicates per cell, no prespecified equivalence margin). Retrieved public Galaxy histories exposed 71 distinct analytical creating jobs across 14 of 15 galaxy runs with usable job counts (one run's job data was unavailable), of which 19 carried a failed/error status. Galaxy/open_ended_code median input-token ratios ranged from 0.265 to 10.7 across the five model configurations, computed as ratios of condition medians rather than of paired-run ratios. These are single-task, retrospective, case-study figures and do not support benchmark-wide or causal claims about either execution condition.
