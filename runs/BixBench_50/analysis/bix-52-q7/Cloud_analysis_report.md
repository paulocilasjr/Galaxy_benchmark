# bix-52-q7: independent audit-of-the-audit

This report is a second-pass, read-only review of the existing `history_analysis.md` / `history_analysis_evidence.json` package for bix-52-q7. It does not rerun agent code, call live Galaxy APIs, or open hidden references. It follows `HISTORY_ANALYSIS_INSTRUCTIONS.md` Section 9.

## 1. Task, experimental design, evidence availability, matching rules

- Task prompt (`.task.prompt`): "How many individual methylation measurements (rows) are removed when filtering out measurements that do not show >90% or <10% methylation in the Zebra Finch dataset?" Source: `phylobio/BixBench-Verified-50`.
- 30 rows, all `status: trace_observed`. Two conditions x five model labels (Codex GPT-5.5, Codex GPT-5.6 Sol, Codex GPT-5.6 Luna, DeepSeek V4 Pro via Codex, DeepSeek V4 Pro via Claude Code superseded) x 3 replicates = 30, matching `run_manifest.json`.
- Coverage against an independent protocol is `unknown_protocol_inventory`; workbook links are the only inventory.
- Model identity runtime-verified; replicate numbers are labels only, no seed recorded.
- 15 galaxy-condition runs each have a public `usegalaxy.org` history; 15 open_ended_code runs have none.
- One run, `open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3`, is recorded with `result_status: "incomplete"`, `step_completion.steps[0] "agent_run_completed": false`, and `evidence_completeness.submitted_answer: "not_collected"` — the underlying agent run did not finish; this is an unresolved/incomplete run, not a missing record, and its evaluator score of 0 is a defined outcome of that incompleteness rather than an invented answer.

## 2. Main outcomes (kept separate)

- **Official evaluator score**: `outcome.original_evaluator_score` under `accuracy.score` is present for all 30/30 runs. Scores are not uniform on this task: 25 of 30 score 1, 5 score 0 (`galaxy_codex_gpt_5_6_sol_r3`, `galaxy_codex_gpt_5_6_luna_r2`, `galaxy_codex_gpt_5_6_luna_r3`, and `open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3`, plus the count already listed — verified directly by `jq`).
- **Observed execution**: retrieved public Galaxy histories expose 56 distinct analytical creating jobs (deduplicated by native job ID, excluding upload/fetch) across the 15 galaxy runs, of which 1 has `error`/`failed` status.
- **Auditor interpretation (this report)**: the majority answer across both conditions is "19159". Two galaxy-condition Codex-Sol/Luna runs answered "19160" (off by one) and scored 0; one Codex-Luna galaxy run answered "539" (a materially different number, likely a different filtering interpretation) and scored 0. This is a descriptive pattern — a small, mostly-consistent numeric answer with occasional off-by-one or divergent outliers concentrated in the galaxy condition for this task — not a claim about which condition is more reliable in general.

## 3. Manuscript Results-section walkthrough

**Accuracy and output agreement.** Recomputed per-model condition means from `.runs[].outcome.original_evaluator_score` match the Section 2 table exactly: codex_gpt_5_5 1/1 (0pp); codex_gpt_5_6_sol 0.667/1 (-33.3pp); codex_gpt_5_6_luna 0.333/1 (-66.7pp); deepseek_v4_pro_via_codex 1/1 (0pp); deepseek_v4_pro_via_claude_code_superseded 1/0.667 (+33.3pp, driven by the one incomplete open_ended_code run). No disagreement found. This is the one task among the five audited here where the two conditions diverge on more than a single outlier run, and where the sign of the difference is not uniformly in one condition's favor (Sol/Luna favor open_ended_code; the superseded DeepSeek harness favors galaxy) — consistent with the instructions' caution against asserting a general condition effect from one task.

**Execution, failures, recovery.** Recomputing distinct Galaxy jobs per run from `job_ledgers/galaxy/*.json` (dedup by `native_job_id`, tool-name exclusion) reproduces the route table exactly, e.g. `galaxy_codex_gpt_5_6_luna_r3` = 11 jobs/1 failed (the task's only recorded Galaxy job failure), `galaxy_codex_gpt_5_6_sol_r2` = 5/0. Summed: 56 total jobs, 1 failed — matches `finding_execution` (`numerator: 1, denominator: 56`) and the Section 2 headline exactly. Notably, the run with the one job failure (`galaxy_codex_gpt_5_6_luna_r3`) also produced the most divergent wrong answer ("539") and scored 0 — the report does not claim the job failure caused the wrong answer, and this audit likewise does not draw that causal link without inspecting the specific event chronology, which is out of scope here (see Section 6).

**Solution-route variability.** Most galaxy-condition rows are "unclassified"; one row (`galaxy_codex_gpt_5_6_luna_r3`) is labeled "Datamash," confirmed against its job ledger `.tool` field. open_ended_code routes are uniformly "local shell or script; method unclassified." Sampled a recovered open_ended_code command (`head -n 5 inputs/ZF_AgeRelated_CpG_noMT_Final.csv`) — consistent with a real inspection command.

**Token cost, provenance, readability.** Reported ratios (11.9, 44.3, 15.4, 13.3, 12.2) were not independently re-derived here; the flat `usage.input_tokens` field returned null on sampled runs in this task package, same limitation as the other four tasks in this audit set. No human-readability measurement exists.

## 4. Per-condition/model/replicate route table

Checked against evidence JSON and job ledgers for run ID, model, `accuracy.score`, submitted answer, and Galaxy job/failed counts. All checked cells matched exactly, including the one run with a null/`"unavailable"` submitted answer, which the evidence JSON confirms as `submitted_answer: null` with `evidence_completeness.submitted_answer: "not_collected"` (not an invented zero-length answer). No discrepancy found; table reused as-is.

## 5. Input sharing, external computation, environment/reproducibility

- `input_manifest.json`: `all_trace_input_hashes_agree_by_name: true`, consistent with a shared staged-input bundle (same Zebra Finch CpG/chromosome-length CSVs used across the bix-52 task family in this audit set).
- Environment: `usegalaxy.org`, per-run Docker image tags, read-only API key mode. TLS verification not performed by the auditor (stated limitation).
- **Gap noted**: `recovered_code/` in this task directory contains only an `open_ended_code/` subfolder (146 items, all from open_ended_code runs) — no `recovered_code/galaxy/` subfolder exists here, unlike the sibling bix-52-q2 and bix-52-q6 packages, each of which retained one representative Galaxy job Python payload. The underlying Galaxy commands are still fully present in `job_ledgers/galaxy/*.json` (each `analysis`-type event carries a `command` field), so this is a gap in the curated `recovered_code` sample, not in the underlying job-ledger evidence.

## 6. Verification methods

Checked: `.runs | length` (30); `.task`; `.manuscript_findings` numerator/denominator/estimate for all four findings; per-run and per-model `outcome.original_evaluator_score` and `submitted_answer` recomputation (scores/answers match table, including the one incomplete/null-answer run); per-run Galaxy job/failure counts recomputed from `job_ledgers/galaxy/*.json` via `execution_location=="galaxy_job"` filter + `native_job_id` dedup, summed to 56/1 matching `history_analysis.md`; `recovered_code/manifest.json` structure and run-ID coverage (confirmed no galaxy-condition items present); one open_ended_code command file sampled.

Not checked / out of scope: byte-level rehashing of large payloads; full transcript replay of the one incomplete run to determine why it did not finish; independent reconstruction of the five reported input-token ratios (usage field returned null on sampled runs); event-level chronology linking the one Galaxy job failure to the divergent "539" answer (would require inspecting the full ordered event stream for that run, which this pass did not do); TLS/server authentication.

## 7. Claim-to-evidence pointer list

| Claim | Source |
|---|---|
| 30/30 runs have a numeric evaluator score; 25/30 score 1, 5/30 score 0 | `history_analysis_evidence.json` `.runs[].outcome.original_evaluator_score` |
| Per-model score means/differences (Section 2 table) | Recomputed from `.runs[].outcome.original_evaluator_score` grouped by model+condition |
| 56 distinct analytical jobs, 1 failed | Recomputed from `job_ledgers/galaxy/*.json`; matches `.manuscript_findings[1]` (`finding_execution`) |
| Per-run job/failed counts in route table | Recomputed per-run from `job_ledgers/galaxy/<run>.json`; exact match |
| One incomplete run with null submitted answer | `.runs[] .outcome.result_status == "incomplete"`, `.evidence_completeness.submitted_answer == "not_collected"` |
| No `recovered_code/galaxy` sample for this task | `find recovered_code`, `recovered_code/manifest.json` run-ID list (open_ended_code only) |
| Shared staged inputs | `input_manifest.json` `all_trace_input_hashes_agree_by_name: true` |

## 8. Missing evidence / open gaps

- Independent protocol manifest for expected coverage/seeds is absent.
- Reported input-token ratios not independently reproduced from the top-level `usage.input_tokens` field in this pass.
- `recovered_code/galaxy/` sample is entirely absent for this task (0 of 15 galaxy runs sampled into `recovered_code`, versus 1 sampled in each of bix-52-q2 and bix-52-q6); the underlying job commands remain in `job_ledgers/galaxy/*.json`.
- The chronological relationship between the one Galaxy job failure and the divergent wrong answer in `galaxy_codex_gpt_5_6_luna_r3` is not established by this audit; the original report correctly avoids asserting causation, and this review does not add a stronger claim.
- No independently defined task difficulty label; no human-reviewer readability assessment.

### Abstract-ready paragraph

For bix-52-q7, 30 supplied runs (5 models x 2 conditions x 3 replicates) returned an original evaluator score for all runs: 25 scored 1 and 5 scored 0, including one open_ended_code run recorded as incomplete with no submitted answer. Retrieved public Galaxy histories for the 15 galaxy-condition runs exposed 56 distinct analytical creating jobs (deduplicated by native job ID), of which 1 had failed/error status — a count this audit independently reproduced run-by-run and confirmed matches `history_analysis.md` exactly. Per-model score differences ranged from 0 to -66.7 percentage points (galaxy versus open_ended_code, codex_gpt_5_6_luna) and +33.3 percentage points in the opposite direction for one model, illustrating that this single task does not support a uniform condition effect. These are case-study counts and do not extrapolate to the benchmark.
