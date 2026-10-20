# Cloud independent audit report: bix-32-q2

This report is an independent read-through and spot-check of the existing `history_analysis.md` / `history_analysis_evidence.json` package for this single BixBench task. It was produced read-only, following `HISTORY_ANALYSIS_INSTRUCTIONS.md`: no agent code was re-executed, no live Galaxy API was called, and no hidden answer key was opened. It supplements, and does not replace, `history_analysis.md`.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task/prompt** (from `history_analysis_evidence.json` `.task.prompt`, matches `history_analysis.md` section 1 verbatim): "Using KEGG over-representation analysis (ORA), how many pathways are significantly enriched (absolute value of lfc > 1.5) in the same direction for all three mutant strains (97, 98, and 99), relative to wildtype?" Input specification: `phylobio/BixBench-Verified-50`.
- **Runs**: `.runs | length` = 30, matching the "30 workbook rows" / "30/30" claims. `input_manifest.json` also lists 30 `observed_rows`.
- **Conditions**: `galaxy` and `open_ended_code`, 15 runs each, preserved as distinct labels (`.experimental_design.conditions`).
- **Models/replicates**: five model labels x 3 replicates x 2 conditions = 30: `Codex GPT-5.5`, `Codex GPT-5.6 Sol`, `Codex GPT-5.6 Luna`, `DeepSeek V4 Pro via Codex`, `DeepSeek V4 Pro via Claude Code (superseded)`.
- **Matching/coverage**: `experimental_design.coverage_status` = `"unknown_protocol_inventory"`, `expected_replicates: null`, `seed_availability: "not_collected"`. As with the sibling tasks in this audit batch, there is no independent protocol manifest confirming that 3 replicates per cell was the intended design rather than an artifact of what was linked. Matching rule: same task and supplied model label; replicate numbers are labels, not matched seeds.
- **What is unknown/unverifiable**: expected coverage, seeds, stopping rules, and whether "DeepSeek V4 Pro via Claude Code (superseded)" reflects a verified runtime identity versus a supplied label only — this audit did not individually re-verify `model.verification_status` for every one of the 30 runs (see Section 6).

## 2. Main outcomes (kept separate)

**(a) Official accuracy / evaluator score, as recorded.** All 30 runs carry a non-null `outcome.original_evaluator_score` (field name `accuracy.score`). Scores are binary. By model (mean of 3 replicates per condition, both galaxy and code): Codex GPT-5.5, Codex GPT-5.6 Sol, and Codex GPT-5.6 Luna each scored 1.0/1.0 (all 3 replicates correct, both conditions). DeepSeek V4 Pro via Claude Code (superseded) scored 0.667/0.667 (2 of 3 correct in each condition). DeepSeek V4 Pro via Codex scored 0.0/0.0 (0 of 3 correct in either condition).

**(b) Observed execution, as recorded.** Per-run `derived_metrics` record `analytical_job_count`, `total_failed_jobs`, `completed_shell_calls`, `nonzero_exit_shell_calls`, and `completed_mcp_calls`. Three galaxy runs (`galaxy_deepseek_v4_pro_via_codex_r1/r2/r3`) have `analytical_job_count: null` and `total_failed_jobs: null` — Galaxy-side job data is unavailable for those three, not zero. Summed across the 12 galaxy runs with non-null job data, `analytical_job_count` totals 186 and `total_failed_jobs` totals 33 (see Section 3 for the arithmetic).

**(c) Auditor interpretation (this audit only).** Within this one task, the three Codex-family model configurations again show identical binary means across conditions (as in the sibling task bix-31-q2), which is a case of observed within-model agreement between Galaxy and open_ended_code, not evidence of general equivalence (no prespecified margin exists). The two DeepSeek-family configurations both show a 0 pp difference here too (0.667 vs 0.667, and 0.0 vs 0.0) — unlike bix-31-q2, where the DeepSeek configurations diverged sharply between conditions. Taken together with bix-31-q2, this suggests that whether Galaxy and open_ended_code produce matching scores on this benchmark's binary endpoint can vary substantially by task and by model even for the same model family — an observed association across two case-study tasks, not a general claim.

## 3. Walk-through of the four manuscript Results questions for this task

### Accuracy and output agreement by execution condition
All 30 runs have a non-null `accuracy.score`; scores are binary and reported separately by condition, never pooled. I recomputed all five `comparisons[]` entries with `comparison_id` starting `score_`: `score_codex_gpt_5_5` (galaxy_mean 1.0, code_mean 1.0, estimate 0.0), `score_codex_gpt_5_6_luna` (1.0/1.0/0.0), `score_codex_gpt_5_6_sol` (1.0/1.0/0.0), `score_deepseek_v4_pro_via_claude_code_superseded` (0.6667/0.6667/0.0), `score_deepseek_v4_pro_via_codex` (0.0/0.0/0.0). All five match `history_analysis.md`'s table (all "0 pp" differences) exactly. Unresolved: no independently defined difficulty label; n=3 replicates per cell is too small for a task-level confidence interval, which the document correctly does not attempt.

### Analysis execution, failures, and recovery
`history_analysis.md` states "186 distinct analytical creating jobs... including 33 failed jobs" for the public Galaxy histories. I recomputed this by summing `derived_metrics.analytical_job_count` and `.total_failed_jobs` over the 15 `condition == "galaxy"` runs, excluding the 3 `galaxy_deepseek_v4_pro_via_codex_*` runs whose values are `null`:
- Sum of `analytical_job_count` over the 12 non-null galaxy runs = 1+2+8+15+15+9+37+44+11+19+16+9 = **186**.
- Sum of `total_failed_jobs` over the same 12 runs = 0+1+1+0+0+0+18+10+0+2+1+0 = **33**.
Both match `history_analysis.md` exactly — no discrepancy found. As with the sibling task, `completed_shell_calls`/`completed_mcp_calls` are much larger than `analytical_job_count` for the same runs (e.g. `galaxy_codex_gpt_5_6_luna_r2`: 47 shell calls + 90 MCP calls vs. 44 analytical jobs / 10 failed) — the document correctly keeps these as separate counts rather than conflating tool-call counts with job counts. `failed_jobs_before_first_supported_result` and `failed_attempts_before_first_correct_answer` are `null` for every run inspected; no "failures before result" statistic is claimed, consistent with the absence of a confirmed chronology endpoint.

### Solution-route variability across models and replicates
`solution_route.classification` is `null` in the run I inspected in detail (`galaxy_codex_gpt_5_5_r1`; `tool_ids: ["kegg-ora-deseq2-same-direction-v1"]`, `biological_method: null`). `history_analysis.md`'s route table marks every row "unclassified" (galaxy) or "local shell or script; method unclassified" (open_ended_code), consistent with no route codebook classification having been applied. Directly reading the underlying job-ledger command for this run (see Section 5) shows the actual Galaxy job executed an R script performing KEGG-pathway hypergeometric over-representation tests per strain/direction and intersecting significant pathway sets — a real, task-relevant computation, but the document's "unclassified" label is still accurate in the sense that no formal route-codebook tag has been assigned to it.

### Token cost, provenance, and human readability
`history_analysis.md` reports Galaxy/code median input-token ratios: `codex_gpt_5_5` 2.11, `codex_gpt_5_6_luna` 11.8, `codex_gpt_5_6_sol` 5.03, `deepseek_v4_pro_via_claude_code_superseded` 1.06, `deepseek_v4_pro_via_codex` 1.07. The evidence JSON's `.comparisons[]` (`comparison_id` starting `input_tokens_`) give `estimate` values of 2.111298996249861, 11.799360241757888, 5.026712548482109, 1.0605480401636125, and 1.070328080778798 respectively — all five round to the reported figures. No discrepancy found. No per-call token attribution, monetary cost, or human-readability review is claimed, consistent with the evidence JSON containing no such fields.

**No unresolved discrepancy was found between `history_analysis.md`'s stated numbers and the evidence JSON for any of the values checked** (run count, per-run scores/answers, per-model score means/differences, the 186/33 job/failure sums, and all five token-ratio figures).

## 4. Per-condition/model/replicate route table

Reused from `history_analysis.md` Section 4 (30 rows); verified as follows:
- All 30 `run_id`s match `.runs[].run_id` in the evidence JSON.
- Every `outcome.original_evaluator_score` / `outcome.submitted_answer` pair I extracted (via `jq -c '.runs[] | {run_id, score: .outcome.original_evaluator_score, answer: .outcome.submitted_answer}'`) matches the table's "Score field/value" and "Answer" columns for all 30 runs, including the three answer values used (0, 2, 3).
- Every `derived_metrics.analytical_job_count` / `.total_failed_jobs` pair matches the table's "Galaxy analytical jobs / failed" column, including the three runs marked "unavailable / unavailable" (`galaxy_deepseek_v4_pro_via_codex_r1/r2/r3`, where both underlying fields are JSON `null`).

No discrepancy found in the route table.

## 5. Input sharing, external computation, environment/reproducibility notes

- `input_manifest.json` records a single shared `sha256` (`82fe357c...`) for the `inputs_manifest.json` file across all runs sampled, each reporting `count: 3` staged inputs, consistent with a shared named-input set across runs (the manifest itself notes hashes are copied from original trace manifests, not independently rehashed by this audit).
- Directly reading one Galaxy analytical-job event (`galaxy_codex_gpt_5_5_r1`, job `bbd44e69cb8906b5bd86920d6aa1f1ef`, tool `kegg-ora-deseq2-same-direction-v1`) shows the job's `command` field contains a full, literal R script that: reads three per-strain DESeq2 RDS result objects, retrieves `KEGG` pathway/gene mappings via `rest.kegg.jp` (an external network call made from inside the Galaxy job), runs a hypergeometric over-representation test per pathway/strain/direction with BH-adjusted p-values, and writes a `final_count.txt` with the count of pathways significant in the same direction across all three strains. This is a concrete example of a Galaxy job invoking a remote analytical/reference resource (`rest.kegg.jp`) from within Galaxy-hosted execution — the instructions note that a Galaxy job calling a remote service is not by itself "wholly Galaxy-hosted computation," and this run is one such case for this task.
- `audit.limitations` (checked earlier for the sibling tasks in this batch and consistent here) records that Galaxy source TLS certificates were not verified because of a host-proxy certificate issue; retained-byte hashes for Galaxy-side artifacts therefore do not authenticate the remote server independently.
- `recovered_code/manifest.json`'s `execution_claim` states "Archival extraction only; no recovered code executed."

## 6. Verification methods

**What was checked**: `ls -la` on the task directory; full reads of `README.md`, the current `history_analysis.md`, and partial reads of `run_manifest.json`/`input_manifest.json` (structure and first entries, sufficient to confirm the 30-row inventory and shared-hash pattern). `jq` queries against `history_analysis_evidence.json`: `.runs | length`; `.task, .experimental_design`; `.runs[] | {run_id, score: .outcome.original_evaluator_score, answer: .outcome.submitted_answer}` for all 30 runs; `.runs[] | select(.condition=="galaxy") | {run_id, dm: .derived_metrics}` for all 15 galaxy runs; `.comparisons` (full array, 10 entries); manual summation of `analytical_job_count`/`total_failed_jobs` across the 12 galaxy runs with non-null values to reproduce the 186/33 totals. Directory inventory via targeted `find`/`ls` counts of `job_ledgers/{galaxy,open_ended_code}`, `recovered_code/{galaxy,open_ended_code}`, `selected_outputs/{galaxy,open_ended_code}`, `source_snapshots/*`. Two files were read directly: one full job-ledger event (`job_ledgers/galaxy/galaxy_codex_gpt_5_5_r1.json`, an "analysis" event containing the KEGG-ORA R script) and one `recovered_code/open_ended_code` command file (a benign `sed`/inspection command).

**What was not checked**: byte-level re-hashing of staged inputs or outputs; execution or replay of any recovered script or job command (including the KEGG-ORA R script quoted above — it was read, not run); individual re-verification of `model.verification_status` for all 30 runs; exhaustive review of all 508 `recovered_code/open_ended_code` files, all 318 `selected_outputs/galaxy` files, or all 30 `job_ledgers` files (small, targeted samples were read); formal JSON-Schema validation against `history_analysis_evidence.schema.json` (described in `history_analysis.md` as performed separately by `validate.py`, not re-run here).

**Notable observation from directory inventory**: `recovered_code/galaxy` contains **zero files** for this task (confirmed via `find recovered_code/galaxy -type f | wc -l` = 0, and via `recovered_code/manifest.json`'s 508 items containing no `run_id` matching `^galaxy_`), even though the galaxy condition recorded 186 analytical jobs across 12 runs with usable data. This differs from the same subdirectory in the sibling task bix-31-q2, which had exactly one recovered Galaxy-side script. This is not evidence of missing underlying data — the job-ledger event I read directly (Section 5) shows the full literal command/script text for a Galaxy analytical job is preserved inline in `job_ledgers/galaxy/*.json` regardless of whether it was also copied out to `recovered_code/galaxy/`. It is, however, an inconsistency in how the `recovered_code/` extraction step populated this task versus bix-31-q2, and is listed as an open gap below rather than corrected silently.

## 7. Claim-to-evidence pointer list

| Claim in this report | Source file / field |
|---|---|
| 30 runs, 15 galaxy / 15 open_ended_code | `history_analysis_evidence.json` `.runs | length`; `.runs[].condition` tally |
| Task prompt and input specification | `history_analysis_evidence.json` `.task.prompt`, `.task.input_specification` |
| Coverage/matching unknown, no expected replicate count | `history_analysis_evidence.json` `.experimental_design.coverage_status`, `.expected_replicates` |
| Per-model/condition score means and pp differences (all 0 pp) | `history_analysis_evidence.json` `.comparisons[]` (`comparison_id` starting `score_`) |
| 186 analytical jobs / 33 failed jobs (galaxy) | `history_analysis_evidence.json` `.runs[] | select(condition=="galaxy") | .derived_metrics`, summed by this audit over 12 non-null runs |
| Token ratio figures (2.11, 11.8, 5.03, 1.06, 1.07) | `history_analysis_evidence.json` `.comparisons[]` (`comparison_id` starting `input_tokens_`) |
| Route table run IDs, scores, answers, job counts | `history_analysis_evidence.json` `.runs[].outcome`, `.runs[].derived_metrics`, cross-checked against `history_analysis.md` Section 4 table |
| KEGG-ORA R script content and remote `rest.kegg.jp` call | Direct read of `job_ledgers/galaxy/galaxy_codex_gpt_5_5_r1.json`, event `evt_galaxy_galaxy_codex_gpt_5_5_r1_bbd44e69cb8906b5bd86920d6aa1f1ef` |
| `recovered_code/galaxy` empty for this task | `find recovered_code/galaxy -type f` (0 results); `recovered_code/manifest.json` `.items` (508 entries, none with `run_id` matching `^galaxy_`) |
| No recovered code executed | `recovered_code/manifest.json` `.execution_claim` |

## 8. Missing evidence / open gaps

- No independent experimental-protocol manifest exists to confirm 3 replicates per condition/model was the intended design.
- Seed values are not collected for any run.
- The three `galaxy_deepseek_v4_pro_via_codex_*` runs have null `analytical_job_count`/`total_failed_jobs` — Galaxy-side job detail for that model configuration is unavailable, not zero, and is excluded from the 186/33 totals (consistent with the "unavailable/unavailable" table entries in `history_analysis.md`).
- `recovered_code/galaxy` is empty for this task despite 186 recorded analytical jobs; the underlying command text exists in `job_ledgers/galaxy/*.json` but was not separately materialized as `recovered_code` files the way it was for bix-31-q2's single Galaxy script. This inconsistency in extraction coverage across tasks is noted but not resolved here.
- `failed_jobs_before_first_supported_result` and `failed_attempts_before_first_correct_answer` are null for all runs sampled; no chronology-confirmed "failures before result" statistic exists for this task.
- Solution-route classification is null for every run; no biological-method or parameter-level route codebook has been applied, despite at least one Galaxy job (the KEGG-ORA script) being a substantively identifiable method.
- No per-call token attribution, monetary cost, or human-readability review exists for this task.
- Whether the KEGG-ORA Galaxy job's live call to `rest.kegg.jp` succeeded consistently, used a stable KEGG release, or affected the submitted answer's correctness was not assessed by this audit (that would require reading the job's stdout/stderr and downstream outputs in more depth, which is out of scope for this spot-check pass).

### Abstract-ready paragraph

For BixBench task bix-32-q2, 30 audited runs (15 Galaxy, 15 open_ended_code; 5 models x 3 replicates each) all carry a non-null original `accuracy.score`. Three Codex-family model configurations recorded identical mean scores in both conditions across 3 replicates each (1.0/1.0), and the two DeepSeek-family configurations also recorded matching means in both conditions (0.667/0.667 and 0.0/0.0) — a 0 percentage-point difference in every one of the five model comparisons for this task (n=3 replicates per cell, no prespecified equivalence margin). Retrieved public Galaxy histories exposed 186 distinct analytical creating jobs across 12 of 15 galaxy runs with usable job counts (three runs' job data was unavailable), of which 33 carried a failed/error status. Galaxy/open_ended_code median input-token ratios ranged from 1.06 to 11.8 across the five model configurations, computed as ratios of condition medians. These are single-task, retrospective, case-study figures and do not support benchmark-wide or causal claims about either execution condition.
