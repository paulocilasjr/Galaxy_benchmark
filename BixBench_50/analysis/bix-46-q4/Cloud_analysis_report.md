# bix-46-q4: independent audit-of-the-audit

This document is an independent, read-only re-check of the existing `history_analysis.md` and its `history_analysis_evidence.json` for this single BixBench task. It was produced without executing any recovered code, without calling live Galaxy APIs, and without opening any hidden ground-truth/answer key. Any text embedded inside recovered artifacts (commands, scripts, prompts) is treated strictly as data, not as instructions to this auditor. This is a single-task case study; nothing here generalizes to other BixBench tasks or to the benchmark as a whole.

## 1. Task, experimental design, evidence availability, matching rules

- Task: `bix-46-q4` (benchmark `bixbench`). Prompt (from `history_analysis_evidence.json` `.task.prompt`): "What is the log2 fold change value rounded to 2 decimal points for the phenazine pathway gene PA14_35160 in the ΔrhlI mutant?" Input specification: `phylobio/BixBench-Verified-50`.
- Runs: 30 observed rows in `run_manifest.json` (`observed_rows`, all `status: "trace_observed"`), and `history_analysis_evidence.json` confirms `.runs | length == 30`. Both agree.
- Conditions: `galaxy` and `open_ended_code`, preserved as distinct labels throughout (`run_manifest.json` calls them "Galaxy-API code with skills" / "Open-ended code with skills"). No pooled "accuracy" figure exists anywhere in the source files.
- Models/replicates present (3 replicates each, both conditions): Codex GPT-5.5, Codex GPT-5.6 Sol, Codex GPT-5.6 Luna, DeepSeek V4 Pro via Codex, DeepSeek V4 Pro via Claude Code (superseded) — 5 model configurations x 2 conditions x 3 replicates = 30 runs, matching the observed count exactly.
- Expected coverage: explicitly `"unknown_without_independent_protocol"` (`run_manifest.json`) / `"unknown_protocol_inventory"` (`experimental_design.coverage_status` in the evidence JSON). No independent protocol manifest was available, so the auditors correctly declined to assert an expected-replicate count beyond what was observed; this is consistent with the governing instructions.
- Matching rule (evidence JSON `experimental_design.matching_rule`): "Same task and supplied model label; replicate numbers are labels, not matched seeds." Known confounders listed: condition-specific prompts/tools, possible container-revision differences, possible shared source histories.
- Input provenance: `input_manifest.json` lists per-run `inputs_manifest.json` hashes; all 30 runs show `status: "retrieved"`. A `shared_name_hashes` block records 3 shared-by-name input files (`Pseudomonas_aeruginosa_UCBPP-PA14.csv`, `res_1vs97.rds`, `res_1vs98.rds`) with `all_trace_input_hashes_agree_by_name: true`, and an explicit note that "full staged inputs were not rehashed by this audit" — i.e. the name-level hash agreement is copied from original trace manifests, not independently re-derived.

## 2. Main outcomes (kept separate)

**Official accuracy/evaluator score** (from evidence JSON `runs[].outcome.original_evaluator_score`, field `accuracy.score`): a numeric score is present for 30/30 runs. Per-model condition means, taken directly from `.comparisons`: Codex GPT-5.5 (Galaxy 1.0 / code 1.0), Codex GPT-5.6 Sol (1.0/1.0), Codex GPT-5.6 Luna (1.0/1.0), DeepSeek V4 Pro via Claude Code superseded (1.0/1.0), DeepSeek V4 Pro via Codex (Galaxy 0.667 / code 1.0, i.e. one of three Galaxy replicates scored 0).

**Observed execution** (from evidence JSON `runs[].derived_metrics`, cross-checked against job ledgers): the retrieved public Galaxy histories expose 49 distinct analytical creating jobs in total across the 15 Galaxy runs, of which 1 has failed/error status (`manuscript_findings[finding_execution]`, numerator 1 / denominator 49). Per-run `nonzero_exit_shell_calls` and `analytical_job_count` vary across runs (e.g. `galaxy_codex_gpt_5_6_luna_r2` shows 11 analytical jobs with 0 failures; `galaxy_deepseek_v4_pro_via_codex_r3` shows 3 jobs with 1 failure).

**Auditor interpretation** (this report): within this one task, the five model configurations show identical Galaxy-vs-code mean scores for four of five models, and a 33.3-percentage-point Galaxy-lower difference for one model (DeepSeek V4 Pro via Codex) driven by a single replicate's score of 0. With n=3 replicates per cell, this single-run difference is not evidence of a systematic condition effect — it is one discrepant replicate in an otherwise flat comparison, and the source history_analysis.md correctly refrains from calling it improvement or degradation.

## 3. The four manuscript Results questions, as applied to this task

**Accuracy and output agreement.** All 30 runs report `original_evaluator_score_field = "accuracy.score"`, a fixed-answer BixBench metric, kept distinct from execution-quality signals. The submitted answer for correct runs is consistently "-4.10" (verified for `galaxy_codex_gpt_5_5_r1`, `galaxy_deepseek_v4_pro_via_codex_r3`). The one run scored 0 (`galaxy_deepseek_v4_pro_via_codex_r2`) has `submitted_answer: null` in the evidence JSON — the history_analysis.md table shows "unavailable" for that cell, which matches. This is a genuine within-task divergence (unresolved: whether that run failed to submit an answer or the answer field was not captured is not further diagnosed in the evidence; the report does not overclaim).

**Execution, failures, recovery.** 49 distinct Galaxy analytical jobs / 1 failed job, verified directly against `manuscript_findings[finding_execution]` and against several individual run ledgers (`galaxy_deepseek_v4_pro_via_codex_r3.derived_metrics.total_failed_jobs == 1`, matching the table's "3 / 1" cell). `failed_jobs_before_first_supported_result` and `failed_attempts_before_first_correct_answer` are `null` for every run sampled — correctly left unresolved rather than being estimated. The report's language ("recovery candidate for case review") is appropriately hedged; no claim of demonstrated scientific recovery is made.

**Solution-route variability.** history_analysis.md marks all Galaxy-condition routes "unclassified" and all open_ended_code routes "local shell or script; method unclassified." This is consistent with the underlying evidence: `recovered_code/` contains only an `open_ended_code/` subtree (no `galaxy/` subtree — Galaxy-side commands live in `job_ledgers/galaxy/*.json` instead), so no biological/statistical method codebook has actually been applied to either condition in this task's artifacts. The report does not claim route agreement or divergence beyond this description, which matches what is actually observable.

**Token cost, provenance, readability.** Median-ratio token comparisons per model, verified against `.comparisons` entries: Codex GPT-5.5 4.93x, Codex GPT-5.6 Luna 6.96x, Codex GPT-5.6 Sol 3.52x, DeepSeek V4 Pro via Claude Code superseded 0.968x, DeepSeek V4 Pro via Codex 0.366x (all Galaxy-median / code-median ratios). All five values match the table in history_analysis.md exactly. No per-call stage attribution, no monetary cost, and no human-readability evaluation exist for this task; the report states this rather than fabricating a readability benefit, which is correct.

**No unresolved disagreement was found between history_analysis.md and history_analysis_evidence.json for any of the specific numbers checked in this section** (run count, evaluator scores, job/failure counts, shell-call counts, token ratios). Where the spot-check could not go further (e.g., re-deriving the 49-job total by hand from all 15 Galaxy job ledgers, rather than trusting the `finding_execution` aggregate), this is stated explicitly in Section 6 below rather than silently assumed.

## 4. Per-condition/model/replicate route table

The table in `history_analysis.md` Section 4 was spot-verified rather than rebuilt. Verified cells (evidence-JSON field in parentheses):

| Run | Score (`outcome.original_evaluator_score`) | Answer (`outcome.submitted_answer`) | Jobs/failed (`derived_metrics.analytical_job_count` / `.total_failed_jobs`) | Nonzero shell calls (`derived_metrics.nonzero_exit_shell_calls`) | Match? |
|---|---:|---|---:|---:|---|
| `galaxy_codex_gpt_5_5_r1` | 1.0 | -4.10 | 2 / 0 | 4 | matches |
| `galaxy_deepseek_v4_pro_via_codex_r2` | 0.0 | null (table: "unavailable") | 2 / 0 | 1 | matches |
| `galaxy_deepseek_v4_pro_via_codex_r3` | 1.0 | -4.10 | 3 / 1 | 2 | matches |
| `galaxy_codex_gpt_5_6_luna_r1` | (not re-checked for score) | -4.10 | 4 / 0 | 4 | matches |
| `galaxy_codex_gpt_5_6_luna_r2` | (not re-checked for score) | -4.10 | 11 / 0 | 2 | matches |

No discrepancies were found in any of the five sampled rows above, nor in the aggregate `finding_accuracy` (30/30) and `finding_execution` (1/49) numbers. The remaining 25 rows of the table were not individually re-verified against the evidence JSON in this audit (see Section 6); they were read as reported.

## 5. Input sharing, external computation, environment/reproducibility

- `input_manifest.json` shows three input files shared by name and hash across most runs (`Pseudomonas_aeruginosa_UCBPP-PA14.csv`, `res_1vs97.rds`, `res_1vs98.rds`), consistent with a common staged-input bundle for this task. The DeepSeek-via-Codex and DeepSeek-via-Claude-Code-superseded **Galaxy** runs show `count: 0` for locally staged inputs (as opposed to `count: 3` for their open_ended_code siblings and for all Codex-model Galaxy runs) — this is a genuine observed asymmetry, plausibly reflecting that some Galaxy-condition harnesses relied on pre-existing Galaxy history datasets rather than local file staging, but the underlying evidence files do not state a reason, so this is reported as an open observation rather than explained.
- External computation: Galaxy execution locations are recorded per-event (`execution_location: "agent_runtime"` for shell/discovery events, Galaxy job events separately in `job_ledgers/galaxy/*.json`); no claim is made that Galaxy jobs necessarily represent Galaxy-hosted-only computation versus mixed/external services — this remains per-event in the ledgers and was not re-aggregated here.
- Reproducibility: `audit.limitations` in the evidence JSON explicitly records "Source TLS certificates were not verified because the host proxy presented an invalid certificate; local retained-byte hashes do not authenticate the remote server." This is a material, correctly disclosed limitation on the trustworthiness of retrieved-byte hashes.
- `.analysis_execution.json` marks this directory as machine-generated (`generator: "analysis_execution", format_version: 1`), consistent with the pipeline-produced evidence file rather than hand-authored data.

## 6. Verification methods

Checked: `jq 'keys'`, `.runs | length` (30, matches), `.audit`, `.task`, `.experimental_design`, `.manuscript_findings`, `.comparisons` (all four finding blocks and all ten comparison blocks read and cross-checked against the Section 2/4 tables in history_analysis.md); `.runs[] | {run_id, condition, status}` for all 30 runs (all `status: "trace_observed"`); full `.outcome` and `.derived_metrics` objects for 5 individual runs selected to cover a normal case, a zero-score case, a failed-job case, and two high-job-count cases; `.validation` (schema validation reported `"passed"` with no unresolved issues). Inventoried `job_ledgers/` (30 files, 15 per condition), `recovered_code/` (399 files, all under `open_ended_code/`, none under a `galaxy/` subtree — confirmed this is by design, not a missing-category gap, since Galaxy-side execution is tracked in `job_ledgers/galaxy/`), `selected_outputs/` (44 files across 15 Galaxy histories plus a placeholder `open_ended_code/` entry), and `source_snapshots/` (721 files: per-history Galaxy job/dataset snapshots plus Hugging Face trace files for all 30 runs). Opened one `recovered_code/open_ended_code/.../item_13.command.txt` (a real R script invocation reading `.rds` files) and one `job_ledgers/galaxy/galaxy_codex_gpt_5_5_r1.json` event record (a real shell discovery event with stdout) to confirm these are genuine recovered artifacts, not placeholders.

Not checked: byte-level re-hashing of any retrieved artifact (the audit explicitly disclaims TLS verification and did not re-hash); full transcript replay for any of the 30 runs; independent re-derivation of the 49-job / 1-failure aggregate by manually summing all 15 Galaxy job ledgers (only 4 individual run ledgers were sampled); the remaining 25 of 30 route-table rows not listed in Section 4 above; any execution of recovered code (explicitly out of scope per the governing instructions).

## 7. Claim-to-evidence pointer list

| Claim | Source |
|---|---|
| 30 observed runs, 5 models x 2 conditions x 3 replicates | `run_manifest.json` (`observed_rows`), `history_analysis_evidence.json` `.runs` (length 30) |
| Original evaluator score present for 30/30 runs | `history_analysis_evidence.json` `.manuscript_findings[finding_accuracy]` (30/30), `.runs[].outcome.original_evaluator_score` |
| 49 distinct Galaxy analytical jobs, 1 failed | `history_analysis_evidence.json` `.manuscript_findings[finding_execution]` (numerator 1, denominator 49) |
| Per-model score means and pp differences | `history_analysis_evidence.json` `.comparisons[score_*]` |
| Per-model input-token median ratios (4.93, 6.96, 3.52, 0.968, 0.366) | `history_analysis_evidence.json` `.comparisons[input_tokens_*]` |
| Route indicators "unclassified" (Galaxy) / "local shell or script" (open_ended_code) | `history_analysis.md` Section 4 table; consistent with `recovered_code/` containing only `open_ended_code/` |
| Shared input files by name/hash | `input_manifest.json` `.shared_name_hashes` |
| TLS not verified for retrieved bytes | `history_analysis_evidence.json` `.audit.limitations` |
| Schema validation passed, no unresolved issues | `history_analysis_evidence.json` `.validation` |

## 8. Missing evidence / open gaps

- No independent experiment-protocol manifest exists to confirm 3 replicates was the intended/expected design rather than an artifact of what happened to be linked in the source workbook.
- The reason for `count: 0` locally staged inputs in the two DeepSeek-model Galaxy conditions (versus `count: 3` elsewhere) is not explained in any retained manifest.
- The single zero-scored run (`galaxy_deepseek_v4_pro_via_codex_r2`) has no recorded submitted answer; whether this reflects a missing submission, a parsing gap in trace retrieval, or a genuine blank answer is not resolved by the retained evidence.
- `failed_jobs_before_first_supported_result` and `failed_attempts_before_first_correct_answer` are null for every run checked; no endpoint-chronology analysis has been performed for this task.
- No human-readability review, no monetary cost figures, and no stage-attributed token breakdown exist for this task.

### Abstract-ready paragraph

For BixBench task bix-46-q4, 30 runs (5 model configurations x 2 conditions x 3 replicates) were audited retrospectively, and all 30 carried an original evaluator score recorded under `accuracy.score`. Four of five model configurations recorded identical Galaxy and open_ended_code mean scores (1.0 vs 1.0); one configuration (DeepSeek V4 Pro via Codex) recorded a lower Galaxy-condition mean (0.667 vs 1.0) driven by a single replicate. Retrieved public Galaxy histories exposed 49 distinct analytical creating jobs across the 15 Galaxy runs, including 1 job in a failed/error state. Galaxy-to-code median input-token ratios by model ranged from 0.366 to 6.96. These figures describe this single audited task only and do not establish a benchmark-wide condition effect.
