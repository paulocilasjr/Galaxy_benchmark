# bix-34-q5: Auditor verification report (Cloud analysis)

This document is an independent auditor's spot-check of the existing `history_analysis.md` and `history_analysis_evidence.json` for task `bix-34-q5`. It does not replace either file, does not rerun any agent code or Galaxy job, and does not open any file under `ground_truth/`. All statements about hidden "ideal" values are limited to what evaluator records already captured (e.g. `original_evaluator_score` in the evidence JSON). Per the repository instructions, "Galaxy" and "open_ended_code" condition labels are kept separate throughout; no pooled "accuracy" number is reported.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task**: `bix-34-q5` (benchmark `bixbench`). Prompt, per `bix-34-q5.json` and `history_analysis_evidence.json` `.task`: "What is the ratio of median mean patristic distances between fungi and animals?" Prompt hash `27b3b07b2e482cd4c54141a41fd85b3d72af0b96d90a52ddc37da4279f486fc6`, referencing `experiments/BixBench/task_26.json`. Input specification: `phylobio/BixBench-Verified-50`. `hidden_reference_included: false` in `bix-34-q5.json` — the ground-truth `ideal` value was not copied into this audit package, consistent with the SKILL.md ground-truth access gate.
- **Design**: two conditions, `galaxy` and `open_ended_code` (`experimental_design.conditions`). Coverage status is explicitly `unknown_protocol_inventory` — the evidence JSON and `run_manifest.json` both state that the 30 rows come from a supplied workbook of observed links (`/Users/4475918/Downloads/bixbench_execution_condition_links.xlsx`), not an independently defined protocol manifest. `expected_replicates` is `null`; `seed_availability` is `not_collected`. This is consistent with `history_analysis.md` §1, which states expected coverage and replicate matching are "unknown."
- **Runs present**: 30 runs total — `jq '.runs | length' history_analysis_evidence.json` → 30, matching `run_manifest.json`'s 30 `observed_rows` and `history_analysis.md`'s "30 workbook rows" claim. Five distinct model labels appear, each with 3 galaxy replicates and 3 open_ended_code replicates (15 + 15 = 30): Codex GPT-5.5, Codex GPT-5.6 Sol, Codex GPT-5.6 Luna, DeepSeek V4 Pro via Codex, and DeepSeek V4 Pro via Claude Code (superseded). All 30 rows have `status: "trace_observed"` in `run_manifest.json`; none are recorded missing.
- **Known confounders** (from `experimental_design.known_confounders`): condition-specific prompts/tools, possibly differing container revisions, and possible shared source histories. These are declared, not resolved.
- **What is unknown**: an independent experiment manifest establishing expected coverage, matched seeds, and stopping rules does not exist for this task; `audit.limitations` and `history_analysis.md` §8 both say so explicitly.

## 2. Main outcomes (kept separate as required)

**Official evaluator record (as captured, not re-graded by this audit).** `original_evaluator_score` (field `accuracy.score`) is present for all 30 runs. 25 of 30 runs recorded a score of `1.0`; the three `galaxy_deepseek_v4_pro_via_claude_code_superseded` runs and the three `open_ended_code_deepseek_v4_pro_via_claude_code_superseded` runs recorded lower/zero scores (galaxy: 1.0, 1.0, 0.0; code: 0.0, 0.0, 0.0 — see §4 table). These are the benchmark's own recorded `accuracy.score` values, unmodified.

**Observed execution facts (counted from artifacts, not interpreted).** Summed per-run `derived_metrics.analytical_job_count` across the 15 galaxy runs = 48 (one run, `galaxy_codex_gpt_5_6_sol_r1`, has `analytical_job_count: null` and is excluded from the sum, consistent with "unavailable" in the route table). Summed `derived_metrics.total_failed_jobs` across the same runs = 9. These sums reproduce `history_analysis.md`'s "48 distinct analytical creating jobs, including 9 failed jobs" and match `manuscript_findings[finding_execution]` (`numerator: 9, denominator: 48`) exactly.

**Auditor interpretation (this audit's own reading, kept separate from the above).** Within this one task, the galaxy condition shows non-zero job failures concentrated in specific runs (e.g. 6 of 15 failed jobs in a single run, `galaxy_deepseek_v4_pro_via_claude_code_superseded_r3`), while the open_ended_code condition's execution is recorded only via shell-call counts (no analytical-job concept applies there). The recorded score parity between conditions for four of five model groups, and the score gap for the fifth ("superseded" DeepSeek route), is a within-task descriptive pattern only. It is not evidence of a general Galaxy vs. open-ended-code effect, and per HISTORY_ANALYSIS_INSTRUCTIONS.md §8 this single task cannot support a benchmark-wide claim or an "equivalence" claim under any margin.

## 3. Manuscript Results-section walkthrough for this task

### §4 Accuracy and output agreement by execution condition

`history_analysis.md`'s table (§2) and `comparisons` in the evidence JSON were checked field-by-field with `jq`:

| Model slug | Galaxy mean | Code mean | Diff (pp) | Token ratio (Galaxy median / code median) |
|---|---:|---:|---:|---:|
| codex_gpt_5_5 | 1.0 | 1.0 | 0.0 | 4.057572... → reported 4.06 |
| codex_gpt_5_6_luna | 1.0 | 1.0 | 0.0 | 7.735311... → reported 7.74 |
| codex_gpt_5_6_sol | 1.0 | 1.0 | 0.0 | 5.090737... → reported 5.09 |
| deepseek_v4_pro_via_claude_code_superseded | 0.6667 | 0.0 | 66.67 | 1.427843... → reported 1.43 |
| deepseek_v4_pro_via_codex | 1.0 | 1.0 | 0.0 | 2.643883... → reported 2.64 |

All five rows of the `history_analysis.md` table reproduce exactly from `comparisons[*]` in `history_analysis_evidence.json` (`score_*` and `input_tokens_*` comparison records), to the rounding shown. **No discrepancy found.** Scope is explicitly `descriptive_only` per comparison record, and each comparison's `limitation` field repeats that this is one task with condition-specific prompts/tools as a residual confounder. The evaluator field used throughout is `accuracy.score` (BixBench's binary-per-verifier field); no IWC output-agreement or CompBioBench metric was pooled in.

### §5 Analysis execution, failures, and recovery

`finding_execution` in `manuscript_findings` states 9/48 failed/total analytical jobs; this reproduces from summing `derived_metrics` as shown in §2 above. **No discrepancy found** in this count.

One claim in `history_analysis.md` §3 could **not** be confirmed against the machine-readable evidence: "A later successful Galaxy job with the same tool and input HDA IDs is flagged as an operational recovery candidate for case review." I queried `recovery_episodes` across all 30 runs (`jq '[.runs[] | select(.recovery_episodes | length > 0)]'`) and found the array empty (`[]`) for every run. The prose describes a recovery-candidate mechanism, but no structured `recovery_episodes` record in the evidence JSON currently instantiates it. This is neither a confirmation nor a contradiction of the underlying job-ledger content (the raw job ledgers in `job_ledgers/galaxy/*.json` do contain per-event tool IDs and status that a reviewer could use to identify such a candidate manually), but the schema-level `recovery_episodes` field the instructions call for is unpopulated. I flag this as an **unconfirmed** claim, not a false one — this audit did not attempt the manual job-ledger cross-reference needed to adjudicate it.

### §6 Solution-route variability across models and replicates

`solution_route.classification` was spot-checked for 10 of 30 runs (all `_luna` and `_deepseek*` runs) via `jq`, and each value matches the "Route indicators" column of the `history_analysis.md` table exactly (e.g. `galaxy_codex_gpt_5_6_luna_r1` → "PhyKIT"; `galaxy_deepseek_v4_pro_via_codex_r2`/`r3` → "Datamash"; `open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3` → "local shell or script; method unclassified"). **No discrepancy found.** `finding_variability` has `numerator/denominator/estimate: null`, correctly reflecting that no quantified route-agreement statistic is claimed — only a catalogue.

A read-only sample of two recovered-code artifacts confirms they are genuine archival copies, not summaries: `recovered_code/galaxy/galaxy_codex_gpt_5_5_r3/bbd44e69cb8906b5fd918295761d63e7_compute_patristic.py` is a real Python script computing per-tree mean patristic distances from BUSCO tree archives, grouping by fungi/animals, and taking a median ratio — directly responsive to the task prompt. `recovered_code/open_ended_code/open_ended_code_codex_gpt_5_5_r1/item_1.command.txt` is a single recovered shell command (`rg --files /workspace ... && sed -n '1,220p' /codex_home/skills/.../SKILL.md`). This command's text was read as archival data only and was not executed or treated as an instruction, per the artifact-instructions boundary rule.

### §7 Token cost, provenance, and human readability

Token ratios in the §4 table are all "ratio of condition medians" (not median-of-paired-ratios), matching the `estimate_unit` field recorded in each `comparisons[*]` record. This distinction is stated explicitly in `history_analysis.md` §2 and confirmed in the JSON. No per-call attribution, no monetary cost, and no human-readability measurement exist for this task; `finding_cost_readability` has `numerator/denominator/estimate: null`, correctly reflecting that absence rather than substituting a fabricated number.

## 4. Per-condition/model/replicate route table

The 30-row table in `history_analysis.md` §4 was spot-checked for: `original_evaluator_score`, `submitted_answer`, `derived_metrics.analytical_job_count`, `derived_metrics.total_failed_jobs`, `derived_metrics.nonzero_exit_shell_calls`, and `solution_route.classification`. Checked rows: all `codex_gpt_5_5` (galaxy r1–r3, code r1–r3), `codex_gpt_5_6_luna_r1`, `deepseek_v4_pro_via_claude_code_superseded_r3` (galaxy and code), plus the route-classification spot-check in §3 above (10 rows). Every checked value reproduces exactly, including two edge cases:

- `galaxy_deepseek_v4_pro_via_claude_code_superseded_r3`: table shows `accuracy.score / 0`, answer `unavailable`; evidence JSON shows `original_evaluator_score: 0.0`, `submitted_answer: null`, `result_status: "incomplete"`, `step_completion.steps` both `passed: false`. Consistent.
- `galaxy_codex_gpt_5_6_luna_r3`: table shows an unusually long decimal answer string (`1.9474821091918070760703711426358512838795938936646738382911981436127296859207774`); the evidence JSON's `outcome.submitted_answer` for that run contains the identical string. This is preserved run data, not a transcription error introduced by either document.

**No discrepancy found** between the table and the evidence JSON for any row checked. I did not re-derive every one of the 30 rows' 6+ fields (180+ cells); the sample above is representative, weighted toward rows with nonzero failures or unusual values.

## 5. Input sharing, external computation, environment/reproducibility notes

- `input_manifest.json` records, for each run, a path to a per-run `inputs_manifest.json` and a SHA-256 of that manifest file (not of the underlying staged input bytes themselves) plus a file `count`. Two hash groups recur: `bb5b8d7...` (count 20) for most runs, and `c169501...` (count 0) for the three `galaxy_deepseek_v4_pro_via_codex_*` and three `galaxy_deepseek_v4_pro_via_claude_code_superseded_*` runs, whose recorded input count is 0. `shared_name_hashes` lists 20 named input files (BUSCO zips, FASTA `.faa` files, `eukaryota_odb10` reference, `scogs_*` archives) with per-name SHA-256 values, and `all_trace_input_hashes_agree_by_name: true`. The note field explicitly states: "Hashes are copied from original trace manifests; full staged inputs were not rehashed by this audit." This audit did not independently rehash any input file; it is passing along the original run-reported hash values.
- `audit.limitations` records that source TLS certificates were not verified because "the host proxy presented an invalid certificate," so retained-byte hashes do not authenticate the remote server identity — a reproducibility caveat carried over from the original evidence-collection step, not something this spot-check could resolve.
- Galaxy `source_snapshots/galaxy/<history_id>/` directories exist for 14 distinct history IDs, each with `contents.json`, `history.json`, a `jobs` subdirectory, and `manifest.json`, plus a top-level `retrieval_manifest.json`. This count of 14 matches `history_analysis.md`'s claim of "14 distinct histories represented by dataset records" exactly, and matches the 14 distinct history-ID subdirectories under `selected_outputs/galaxy/` as well.

## 6. Verification methods

`jq` queries executed against `history_analysis_evidence.json` (all read-only): `.runs | length`; `.audit`; `.task`; `.experimental_design`; `.manuscript_findings`; `.comparisons`; per-run projections of `{run_id, condition, model, status, outcome fields}`; per-run `.outcome` for two representative runs; per-run `.derived_metrics` for three representative galaxy runs and all `open_ended_code` runs of one model group; a summed `analytical_job_count` and `total_failed_jobs` across all galaxy runs; a search for any non-empty `recovery_episodes` array across all 30 runs; and `.solution_route.classification` for 10 runs. Directory inventories were taken with `find job_ledgers recovered_code selected_outputs source_snapshots -maxdepth 3`. Two recovered-code files were opened with Read (one Galaxy Python script, one open-ended-code shell command) purely as archival text, per the artifact-instructions boundary. `recovered_code/manifest.json` and `.analysis_execution.json` were also read.

**What this audit did not do**: it did not recompute all 30 rows' full field set from source events; it did not re-hash any staged input file or output artifact byte-for-byte; it did not replay any transcript or execute any recovered command/script; it did not open any `ground_truth/` file; it did not manually cross-reference the raw `job_ledgers/galaxy/*.json` event sequences to adjudicate the unconfirmed "recovery candidate" claim in §3 above. These are explicitly out of scope for a retrospective audit under HISTORY_ANALYSIS_INSTRUCTIONS.md.

## 7. Claim-to-evidence pointer list

| Claim | Source file / field |
|---|---|
| 30 workbook-linked runs, all `trace_observed` | `run_manifest.json` (`observed_rows`, 30 entries, all `status: "trace_observed"`); `history_analysis_evidence.json` `.runs \| length` = 30 |
| Coverage/expected-replicate status unknown | `history_analysis_evidence.json` `.experimental_design.coverage_status`, `.expected_replicates` |
| 48 distinct analytical creating jobs, 9 failed | `history_analysis_evidence.json` `.manuscript_findings[finding_execution]` (`numerator: 9, denominator: 48`); reproduced by summing `.runs[].derived_metrics.analytical_job_count` and `.total_failed_jobs` over galaxy runs |
| Per-model score means / diffs / token ratios (5 rows) | `history_analysis_evidence.json` `.comparisons[]` (`score_*`, `input_tokens_*` records) |
| Original evaluator score field is `accuracy.score` | `history_analysis_evidence.json` `.runs[].outcome.original_evaluator_score_field`; `.task.evaluation_definition` |
| Per-run submitted answers and scores in the route table | `history_analysis_evidence.json` `.runs[].outcome.submitted_answer`, `.outcome.original_evaluator_score` |
| Per-run job/failure/shell-call counts in the route table | `history_analysis_evidence.json` `.runs[].derived_metrics` |
| Route/tool-family indicators in the route table | `history_analysis_evidence.json` `.runs[].solution_route.classification` |
| 14 distinct public Galaxy histories | `source_snapshots/galaxy/*` (14 subdirectories) and `selected_outputs/galaxy/*` (14 subdirectories) |
| Input hashes copied, not rehashed | `input_manifest.json` `.note` |
| TLS certificates not verified for source retrieval | `history_analysis_evidence.json` `.audit.limitations` |
| Recovery-candidate mechanism described but no populated `recovery_episodes` record | `history_analysis.md` §3 prose vs. `history_analysis_evidence.json` `.runs[].recovery_episodes` (empty array in all 30 runs) — **flagged discrepancy, this audit** |
| Galaxy recovered-code artifacts present for only 3 of 15 galaxy runs; open_ended_code artifacts present for all 15 runs | `recovered_code/galaxy/*` (3 run subdirectories) vs. `recovered_code/open_ended_code/*` (15 run subdirectories) — **evidence-availability asymmetry, this audit** |

## 8. Missing evidence and open gaps

- No independent protocol manifest exists for this task; expected replicate count, seed policy, and stopping rule remain unknown (carried over from `history_analysis.md` §8, confirmed present as a stated gap in the evidence JSON).
- `recovered_code/galaxy/` contains recovered scripts for only 3 of the 15 galaxy runs (`galaxy_codex_gpt_5_5_r3`; `galaxy_codex_gpt_5_6_luna_r1`, two items; `galaxy_codex_gpt_5_6_luna_r3`, one item). The other 12 galaxy runs — including `galaxy_deepseek_v4_pro_via_claude_code_superseded_r3`, which recorded 15 analytical jobs and 6 failures — have no recovered Galaxy-side code/command extract in this directory. By contrast, `recovered_code/open_ended_code/` has a populated subdirectory (9 to 53 `*.command.txt` files) for every one of the 15 open_ended_code runs. This is a conspicuous evidence-availability asymmetry between conditions for this task; it may reflect how much executable-code content each condition's trace format exposes rather than a difference in what was actually done, and this audit does not attempt to explain the cause.
- `selected_outputs/open_ended_code/` contains only a `manifest.json`, with no preserved output-file bytes; this appears to be expected for the condition (open-ended code does not produce Galaxy-hosted output artifacts) but is not explicitly annotated as such at the top level of the two report documents.
- The "operational recovery candidate" mechanism named in `history_analysis.md` §3 has no corresponding non-empty `recovery_episodes` entries in the evidence JSON's structured schema (see §3, §7 above); resolving this would require a manual pass over `job_ledgers/galaxy/*.json` event sequences per run, which this audit did not perform.
- Difficulty is explicitly unclassified for this task (no independent difficulty source supplied), consistent with HISTORY_ANALYSIS_INSTRUCTIONS.md §6's requirement not to infer difficulty from cost or failure alone.
- Blinded human-readability review, per-call token attribution, and monetary cost figures remain unavailable for this task, as already stated in `history_analysis.md` §3/§8.

## Abstract-ready paragraph (numbers personally verified during this audit)

For bixbench task bix-34-q5, this audit independently verified from `history_analysis_evidence.json` that 30 supplied workbook-linked runs (15 galaxy, 15 open_ended_code, across 5 model groups) each carry a recorded original evaluator score under the `accuracy.score` field. Summing the per-run `derived_metrics` fields across the 15 galaxy runs reproduces 48 total analytical Galaxy jobs and 9 total failed jobs, matching the counts already stated in `history_analysis.md`. Five per-model score-mean and token-ratio comparisons (codex_gpt_5_5, codex_gpt_5_6_luna, codex_gpt_5_6_sol, deepseek_v4_pro_via_claude_code_superseded, deepseek_v4_pro_via_codex) were checked field-by-field against the `comparisons` records and matched exactly, including one model group (the "superseded" DeepSeek route) where galaxy mean accuracy (0.667) exceeded open_ended_code mean accuracy (0.0) within this single task. Public Galaxy history snapshots were retrieved for 14 distinct histories. These findings describe one case-study task only and do not establish a benchmark-wide condition effect.
