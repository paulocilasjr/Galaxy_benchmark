# Independent audit-of-audit: bix-18-q1 (BixBench)

This document is an independent, retrospective re-check of the existing retrospective audit package in this directory (`history_analysis.md`, `history_analysis_evidence.json`, and the associated manifests/subfolders). It follows the structure required by Section 9 of `HISTORY_ANALYSIS_INSTRUCTIONS.md`. No agent code was rerun, no Galaxy API calls were made, and no hidden reference/answer key was opened. This report only reads and cross-checks artifacts already present on disk.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task**: bix-18-q1 (benchmark `bixbench`). Prompt (`bix-18-q1.json`, `task` field in `history_analysis_evidence.json`): "In a P. aeruginosa swarming analysis, what is the mean circularity measurement for the genotype showing the largest mean area?" Allowed task metadata reference: `experiments/BixBench/task_12.json` (hash recorded, not opened here). `hidden_reference_included: false` in `bix-18-q1.json`.
- **Conditions**: `galaxy` and `open_ended_code`, preserved as distinct labels throughout `run_manifest.json` and `history_analysis_evidence.json` (`experimental_design.conditions`). Original condition labels ("Galaxy-API code with skills", "Open-ended code with skills") are retained per-row in `run_manifest.json`.
- **Models present**: 5 supplied model labels, each with 3 replicates per condition (30 rows total): `Codex GPT-5.5`, `Codex GPT-5.6 Sol`, `Codex GPT-5.6 Luna`, `DeepSeek V4 Pro via Codex`, `DeepSeek V4 Pro via Claude Code (superseded)`. Verified by counting `run_manifest.json` observed_rows (30) and `history_analysis_evidence.json` `.runs` (30).
- **Coverage**: `experimental_design.coverage_status = "unknown_protocol_inventory"`; no independent protocol/manifest was supplied, so expected replicate counts and matching are unknown outside of what was observed. This audit does not treat the 30 observed rows as a confirmed complete design.
- **Evidence availability**: all 30 rows have `status: "trace_observed"` in both `run_manifest.json` and `history_analysis_evidence.json`. 15 of the 30 rows (the `galaxy` condition rows) carry a `galaxy_url` and a corresponding retrieved public Galaxy history snapshot under `source_snapshots/galaxy/<history_id>/`; the 15 `open_ended_code` rows have `galaxy_url: null` (not applicable — there is no Galaxy history for that condition).
- **Matching rule**: `experimental_design.matching_rule` — "Same task and supplied model label; replicate numbers are labels, not matched seeds." `seed_availability: "not_collected"`.

## 2. Main outcomes (kept visibly separate)

### 2a. Official evaluator score (as recorded, not reinterpreted)
All 30 runs carry `original_evaluator_score = 1.0` on `original_evaluator_score_field = "accuracy.score"`, `original_evaluator_mode = "range_verifier"` (verified directly in `history_analysis_evidence.json` `.runs[].outcome`). All 30 `submitted_answer` values equal `"0.076"`. Coverage: 30/30 runs have this original score field populated; no missing evaluator scores were found.

### 2b. Observed execution facts (independent of the score above)
- Galaxy condition (15 runs): `derived_metrics.analytical_job_count` sums to **55**, `derived_metrics.total_failed_jobs` sums to **8** (both independently recomputed by this audit with `jq`, matching the evidence JSON's own `manuscript_findings[finding_execution]` numerator/denominator of 8/55).
- Open-ended-code condition (15 runs): `analytical_job_count` and `total_failed_jobs` are `null` for every run (Galaxy-specific metrics are `not_applicable` to this condition by design, not missing data).
- Nonzero-exit shell calls and MCP-call counts differ per run and are recorded per run in `derived_metrics`.
- A separate step-completion rubric (`outcome.step_completion`) exists in the evidence and disagrees in places with the binary `accuracy.score`: e.g. every Galaxy run's `step_completion.score` is 0.5 (`passed: false`, failing the `fresh_galaxy_history_recorded` step while passing `final_deliverable_written`), while every open-ended-code run's `step_completion.score` is 1.0 (`passed: true`). This is a distinct, secondary operational checklist, not the benchmark's official score, and `history_analysis.md` does not surface it in its outcomes table — see Section 3 below for discussion.

### 2c. This auditor's interpretation
Within this one task, the original evaluator score is identical (1.0, i.e. correct) across both conditions and all five model labels in these 30 audited runs. This is a within-task descriptive observation only; it does not establish equivalence (no prespecified margin was defined) and does not generalize beyond bix-18-q1. Separately, the Galaxy condition shows a nonzero rate of failed analytical jobs (8/55, about 15%) that has no counterpart Galaxy-specific measurement in the open-ended-code condition (job/failure concepts are not applicable there), so no cross-condition failure-rate comparison is possible for this task.

## 3. The four manuscript Results questions, applied to this task

### Accuracy and output agreement (Section 4)
All 30 runs report the same original evaluator field (`accuracy.score = 1.0`) and the same submitted answer text (`0.076`), which matches the reference computation visible in the retained open-ended-code trace excerpt (`job_ledgers/open_ended_code/open_ended_code_codex_gpt_5_5_r1.json`: the recovered Python snippet computes `Wildtype` as the genotype with the largest mean area and a mean circularity of `0.076`, consistent with the submitted answer). Both conditions and all five models are tied at 1.0/1.0 (0 pp difference) for this one task — this is a single-task case study, not a benchmark-wide accuracy estimate, and `history_analysis.md` correctly frames it this way ("No task-level confidence interval or equivalence conclusion is calculated from this one task"). No disagreement found between the two documents on this point.

### Execution, failures, and recovery (Section 5)
`history_analysis.md` states 55 distinct analytical creating jobs and 8 failed jobs for the retrieved Galaxy histories. This audit independently recomputed both numbers directly from `history_analysis_evidence.json` (`sum(derived_metrics.analytical_job_count)` over `condition=="galaxy"` = 55; `sum(derived_metrics.total_failed_jobs)` = 8) and cross-checked one run at the raw ledger level: `job_ledgers/galaxy/galaxy_deepseek_v4_pro_via_codex_r3.json` contains 9 Galaxy tool-job-status events (`ok`/`error`), one of which (`__DATA_FETCH__`) is a data-fetch job excluded by the stated methodology, leaving 8 analytical jobs with 1 error (`Grouping1`) — this matches the run's `derived_metrics` value of `jobs: 8, failed: 1` exactly. No discrepancy found.
`history_analysis.md` explicitly declines to assert cross-condition "Galaxy only" completion or scientific recovery from a later successful command alone, consistent with Section 5's evidentiary bar; this audit did not find any place where the report overstepped that bar.
One item this audit surfaced that `history_analysis.md` does not mention: the evidence JSON's `outcome.step_completion` field shows all 15 Galaxy runs failing an internal `fresh_galaxy_history_recorded` check (score 0.5) even though the official `accuracy.score` is 1.0 for the same runs. This is not a contradiction (they are different, independently-defined fields, as required by Section 3 "Outcome" of the instructions), but it is a place where the underlying evidence carries more nuance than the narrative report currently exposes.

### Solution-route variability (Section 6)
`history_analysis.md`'s per-run table labels Galaxy routes as "Datamash" or "unclassified," and open-ended-code routes uniformly as "local shell or script; method unclassified." Spot-checking `solution_route` records in the evidence JSON confirms these labels are taken verbatim from `solution_route.classification` (e.g. `galaxy_codex_gpt_5_5_r1.solution_route.classification = "Datamash"` with `tool_ids` including `datamash_ops`; `galaxy_codex_gpt_5_5_r2.solution_route.classification = null`, shown in the table as "unclassified"). No discrepancy found. Difficulty is explicitly left unclassified in both documents, consistent with Section 6's requirement not to infer difficulty from failure or cost.

### Token cost, provenance, and readability (Section 7)
The five Galaxy/code median input-token ratios in `history_analysis.md`'s outcomes table (14.1, 25.6, 12.9, 8.65, 21) were independently recomputed from `history_analysis_evidence.json.comparisons` and matched: 14.114153336547936 → 14.1, 25.633064759490615 → 25.6, 12.885004858949621 → 12.9, 8.650109675429276 → 8.65, 21.04182223535416 → 21. All five agree with the rounded values in the report to the stated precision. The `usage` block for one run pair (`galaxy_codex_gpt_5_5_r1/r2/r3` vs `open_ended_code_codex_gpt_5_5_r1/r2/r3`) was independently re-derived from raw `provider_reported_input_tokens` (Galaxy: 642237, 1090719, 673231 → median 673231; code: 44255, 47951, 47699 → median 47699), reproducing the `comparisons` record's `galaxy_median`/`code_median` and the reported ratio of condition medians (not a median of paired ratios — this distinction is stated correctly in both documents). No per-call token attribution or human-readability measurement exists for this task in either document; both correctly label this as unmeasured rather than inferring a benefit.

## 4. Per-condition/model/replicate route table

The 30-row table in `history_analysis.md` Section 4 was checked against `history_analysis_evidence.json` for every model group (all 5 groups' Galaxy job/failed counts, all 5 groups' nonzero-shell-call counts, and all evaluator scores/answers). Every value checked — `accuracy.score`/1, answer `0.076`, Galaxy job counts, Galaxy failed-job counts, and nonzero shell-call counts, per run — matched exactly between the table and the evidence JSON's `outcome` and `derived_metrics` blocks. No rebuilt table is provided here since the existing one is confirmed accurate on every field this audit checked; readers can regenerate it from `history_analysis_evidence.json` `.runs[].{outcome,derived_metrics,solution_route}`.

## 5. Input sharing, external computation, and reproducibility

- `input_manifest.json` records a single shared-by-name input file, `Swarm_1.csv`, with one recorded SHA-256 (`e37edc1c...badd41`) across the runs that reference it; the manifest explicitly notes these hashes were copied from original trace manifests and were **not** rehashed by any audit (`"note": "Hashes are copied from original trace manifests; full staged inputs were not rehashed by this audit"`), and flags `all_trace_input_hashes_agree_by_name: true` as a name-based, not byte-level, agreement claim.
- Two distinct family hashes appear across the 30 runs' `inputs_manifest.json` records (`44e2ab71f2d2...`, count 1, for most runs; `c1695013...`, count 0, for `galaxy_deepseek_v4_pro_via_codex_*` and `galaxy_deepseek_v4_pro_via_claude_code_superseded_*` runs). The `count: 0` entries indicate these six Galaxy runs' local `inputs_manifest.json` recorded zero staged input files at that path, distinct from the "1 file" pattern seen elsewhere; this is a real difference in what each trace's local manifest recorded, not an artifact of this audit.
- Public Galaxy history retrieval is documented per-history under `source_snapshots/galaxy/<history_id>/{history.json,contents.json,jobs/,manifest.json}` for 15 distinct history IDs, one per Galaxy run — consistent with the "15 distinct histories" claim in `history_analysis.md` Section 1.
- `.audit.limitations` in the evidence JSON records that "Source TLS certificates were not verified because the host proxy presented an invalid certificate; local retained-byte hashes do not authenticate the remote server" — an explicit, stated reproducibility caveat that this audit did not attempt to resolve (out of scope; would require live network re-verification).
- `recovered_code/manifest.json` states `execution_claim: "Archival extraction only; no recovered code executed"` for all 50 catalogued recovered-command items; this audit spot-opened two of the 50 files (`open_ended_code_codex_gpt_5_5_r1/item_1.command.txt`, a shell inspection command, and `open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1/call_00_...command.txt`, a two-line answer-writing command) and both read as plausible, genuine recovered command text consistent with their run's job ledger, not placeholder or corrupted content.

## 6. Verification methods (what was checked, what was not)

**Checked in this audit:**
- Read `README.md`, `history_analysis.md` (current version only — `.v1`/`.v2`/`.v3` snapshots were not treated as ground truth), `run_manifest.json`, `input_manifest.json`, `bix-18-q1.json`, `.analysis_execution.json` in full.
- `jq` queries against `history_analysis_evidence.json` for: `.runs | length`; `.schema_version`; `.audit`; `.task`; `.experimental_design`; `.runs[] | {run_id, condition, model, status}`; `.runs[].outcome` (all 30); `.comparisons` (all 10 records); `.manuscript_findings` (all 4 records); `.runs[].derived_metrics` (all 30, including sums by condition); `.runs[].solution_route` (sample); `.runs[].usage` (sample, with manual median recomputation); `.runs[].source_ids` (all 15 Galaxy rows); `.validation`.
- Directory inventory via `find -maxdepth 3` of `job_ledgers/`, `recovered_code/`, `selected_outputs/`, `source_snapshots/`.
- Raw job-ledger cross-check: full read of `job_ledgers/galaxy/galaxy_deepseek_v4_pro_via_codex_r3.json` (54 events) and `job_ledgers/open_ended_code/open_ended_code_codex_gpt_5_5_r1.json` (2 events), reconciling native event statuses against the run's `derived_metrics`.
- Sample-opened 2 of 50 `recovered_code/` command files and confirmed they contain plausible real command text.
- Confirmed `recovered_code/manifest.json` item count (50) equals the count of `.command.txt` files found by `find`.
- Confirmed `selected_outputs/open_ended_code/manifest.json` explicitly documents `status: "not_collected"` (an intentional, labelled gap) rather than a silent omission.

**Not checked / explicitly out of scope:**
- No agent code was executed, no Galaxy API was called live, and no hidden BixBench reference/answer key was opened.
- No byte-level rehashing of large inputs or source snapshots was performed; all hash checks in this audit relied on hashes already recorded in the evidence/manifest files.
- Not all 50 `recovered_code` files, all 15 `source_snapshots/galaxy/*` history folders, or all 30 `job_ledgers` files were opened individually — this audit sampled representative files per category rather than exhaustively re-deriving every count from first principles.
- No new statistical test, confidence interval, or equivalence analysis was computed; this audit only reproduced the point estimates already present in `history_analysis_evidence.json.comparisons` and `manuscript_findings`.
- TLS/server-identity verification for the retrieved Galaxy histories was not attempted (flagged as unresolved in `.audit.limitations` already).

## 7. Claim-to-evidence pointer list

| Claim | Source file / field |
|---|---|
| 30 runs, 30/30 with original evaluator score, `accuracy.score`=1.0 for all | `history_analysis_evidence.json` `.runs[].outcome.original_evaluator_score`, `.runs \| length` |
| 15 distinct Galaxy histories | `run_manifest.json` (15 rows with non-null `galaxy_url`); `history_analysis_evidence.json` `.runs[].source_ids`; `source_snapshots/galaxy/<history_id>/` (15 subfolders) |
| 55 distinct analytical Galaxy jobs, 8 failed | `history_analysis_evidence.json` `.manuscript_findings[finding_execution].{numerator,denominator}` = 8/55; independently summed from `.runs[].derived_metrics.{analytical_job_count,total_failed_jobs}` |
| Per-run job/failed/shell counts in `history_analysis.md` Section 4 table | `history_analysis_evidence.json` `.runs[].derived_metrics` (matched for all 30 runs) |
| Galaxy/code median input-token ratios (14.1, 25.6, 12.9, 8.65, 21) | `history_analysis_evidence.json` `.comparisons[].estimate` for the 5 `input_tokens_*` comparison records |
| Solution-route classifications ("Datamash"/"unclassified"/"local shell or script") | `history_analysis_evidence.json` `.runs[].solution_route.classification` |
| Submitted answer `0.076` for all 30 runs, consistent with the prompt's genotype/circularity computation | `history_analysis_evidence.json` `.runs[].outcome.submitted_answer`; `job_ledgers/open_ended_code/open_ended_code_codex_gpt_5_5_r1.json` recovered Python computation |
| Shared input `Swarm_1.csv`, hashes not independently rehashed | `input_manifest.json` (`shared_name_hashes`, `note`) |
| No code executed, no hidden reference opened, TLS not verified | `history_analysis_evidence.json` `.audit.limitations`; `README.md` |
| `step_completion` internal rubric diverges from `accuracy.score` for Galaxy runs | `history_analysis_evidence.json` `.runs[].outcome.step_completion` (all 15 Galaxy runs: score 0.5, `fresh_galaxy_history_recorded` failed) |
| `selected_outputs/open_ended_code` intentionally empty | `selected_outputs/open_ended_code/manifest.json` (`status: "not_collected"`) |
| Schema validation and reference integrity passed | `history_analysis_evidence.json` `.validation` |

## 8. Missing evidence and open gaps

- No independent experiment/protocol manifest exists for bix-18-q1; expected replicate counts, seeds, and stopping rules remain unknown (`experimental_design.coverage_status = "unknown_protocol_inventory"`), so the 30 observed rows cannot be confirmed as a complete or representative design.
- `recovered_code/` has no `galaxy/` subdirectory of extracted command text (only `open_ended_code/` and the top-level `manifest.json`); Galaxy-side "recovered code" equivalents (e.g. custom tool wrapper payloads, if any) are represented only inside `source_snapshots/galaxy/<history_id>/jobs/`, not as a separate recovered-code category. This is a real asymmetry between conditions in what is catalogued, not necessarily a defect, but it limits direct route-level comparison of "recovered code artifacts" across conditions.
- `selected_outputs/open_ended_code/manifest.json` is explicitly `not_collected`, so no open-ended-code output-artifact bytes are staged in this package outside the raw trace snapshots.
- TLS server identity for the retrieved Galaxy histories was not verified at collection time; retained-byte hashes do not authenticate the remote server (stated limitation, unresolved).
- No stage-level (discovery/input-acquisition/analysis/retry/reporting) token attribution exists for either condition; only whole-run provider totals are available.
- No human-readability review of any kind was performed for this task; provenance completeness (structured manifests/ledgers) is documented, but this is not a substitute for measured review speed or accuracy.
- The `outcome.step_completion` sub-rubric (Galaxy runs consistently failing `fresh_galaxy_history_recorded`) is not discussed anywhere in `history_analysis.md`'s narrative; a fuller treatment would explain what that internal check measures and why it diverges from the official `accuracy.score`.

### Abstract-ready paragraph

For BixBench task bix-18-q1, this audit independently verified 30 supplied runs (15 Galaxy, 15 open-ended-code) across 5 model labels and 3 replicates each, all carrying an original evaluator `accuracy.score` of 1.0 and an identical submitted answer of 0.076. Retrieved public Galaxy history snapshots for the 15 Galaxy runs exposed 55 distinct analytical creating jobs, of which 8 were in a failed/error state, both figures independently recomputed from `history_analysis_evidence.json` and reconciled against one run's raw job ledger. Galaxy-to-code median input-token ratios for the five model groups were independently recomputed as 14.1, 25.6, 12.9, 8.65, and 21, matching the values reported in `history_analysis.md`. These are single-task, retrospective, case-study counts with an unknown expected-coverage baseline; they do not establish a benchmark-wide accuracy difference, a causal recovery benefit, or a measured readability improvement for either execution condition.
