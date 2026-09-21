# bix-35-q1: Auditor verification report (Cloud analysis)

This report is an independent read-through and spot-check of the existing `history_analysis.md` for
task `bix-35-q1`, following `HISTORY_ANALYSIS_INSTRUCTIONS.md` Section 9. It does not rerun agent
code, call live Galaxy APIs, or open hidden ground-truth files. Nothing here supersedes
`history_analysis.md`, `run_manifest.json`, or `input_manifest.json`; this document records what was
independently verified against `history_analysis_evidence.json` and the on-disk evidence directories.

## 1. Task, experimental design, evidence availability, and matching rules

- Task prompt (from `history_analysis_evidence.json` `.task.prompt`, matching `history_analysis.md` §1):
  "Calculate the evolutionary rate for the BUSCO gene 156083at2759 using PhyKIT's evoluionary_rate
  function. What is the gene's evolutionary rate in animals?" Benchmark `bixbench`, input specification
  `phylobio/BixBench-Verified-50`.
- 30 workbook-linked rows are audited (`run_manifest.json` lists 30 `observed_rows`; the evidence JSON
  `.runs` array also has length 30 — confirmed by `jq '.runs | length'`).
- Conditions present: `galaxy` and `open_ended_code` (15 runs each), across 5 model labels ("Codex
  GPT-5.5", "Codex GPT-5.6 Sol", "Codex GPT-5.6 Luna", "DeepSeek V4 Pro via Codex", "DeepSeek V4 Pro via
  Claude Code (superseded)"), 3 replicates per model/condition combination = 30 runs. All 30 have
  `status: trace_observed` in both `run_manifest.json` and the evidence JSON.
- `.experimental_design.coverage_status` is `"unknown_protocol_inventory"` — no independent protocol
  manifest was supplied, so expected replicate counts and matched-seed status are unknown by design, not
  by omission. `expected_replicates: null`, `seed_availability: "not_collected"`.
- Known confounders recorded in the evidence JSON: condition-specific prompts/tools, possible container
  revision differences, possible shared source histories.
- Evidence availability is asymmetric by condition (detailed in Section 4/6 below): Galaxy runs have
  per-run job ledgers and source-snapshot Galaxy history data; open-ended-code runs have per-run
  recovered shell/Python commands. Each condition's distinctive evidence category is well populated;
  the *other* condition's version of that category is largely `unavailable`, which is expected given
  what each condition actually produces, not a gap in retrieval on its own.

## 2. Main outcomes (kept separate as required)

**Official evaluator score (separate fact).** `history_analysis.md` states 30/30 runs carry an original
numeric evaluator score. Confirmed: all 30 `runs[].outcome.original_evaluator_score_field` equal
`"accuracy.score"` with a numeric value present for every run (spot-checked via `jq` over the full run
list — no `null` scores observed). 29 of 30 runs score `1.0`; exactly one run,
`galaxy_deepseek_v4_pro_via_claude_code_superseded_r1`, scores `0.0`.

**Observed execution (separate fact).** `history_analysis.md` states 31 distinct analytical creating
jobs across the retrieved Galaxy histories, with 0 failed jobs. Confirmed via
`finding_execution.numerator/denominator` = `0/31` in `manuscript_findings`, and independently
re-derived by summing `derived_metrics.analytical_job_count` over the 15 `galaxy`-condition runs
(1+1+1+3+3+3+3+2+5+2+1+1+2+2+1 = 31), with `total_failed_jobs` = 0 for every one of those runs. The two
counting paths agree exactly.

**Auditor interpretation (this report, not a fact from the evidence).** Within this single task, both
conditions recorded a numeric score for every run and the model-level score means are identical between
Galaxy and open_ended_code for 4 of 5 models (all 1.0), with one model
(`deepseek_v4_pro_via_claude_code_superseded`) showing a lower Galaxy-side mean (0.667 vs 1.0) driven by
the single `0.0`-scored replicate above. This is a within-task, descriptive pattern only; it does not
establish a general condition effect and is not extrapolated beyond this task.

## 3. Manuscript Results-section walkthrough for this task

### §4 Accuracy and output agreement by execution condition

All 30 runs report `accuracy.score` as the evaluator field, so the "same original field on both sides"
requirement for a difference calculation is met for every model pairing here. `history_analysis.md`'s
per-model table (score means, percentage-point differences) reproduces exactly from
`.comparisons[]` in the evidence JSON:

| Model | Galaxy mean | Code mean | Diff (pp) | history_analysis.md | Match |
|---|---:|---:|---:|---|---|
| codex_gpt_5_5 | 1.0 | 1.0 | 0.0 | 0 pp | yes |
| codex_gpt_5_6_luna | 1.0 | 1.0 | 0.0 | 0 pp | yes |
| codex_gpt_5_6_sol | 1.0 | 1.0 | 0.0 | 0 pp | yes |
| deepseek_v4_pro_via_claude_code_superseded | 0.667 | 1.0 | -33.3 | -33.3 pp | yes |
| deepseek_v4_pro_via_codex | 1.0 | 1.0 | 0.0 | 0 pp | yes |

No disagreement found. This is a single-task case study; no benchmark-wide accuracy claim is supported.

### §5 Analysis execution, failures, and recovery

`history_analysis.md` §3 states: "A later successful Galaxy job with the same tool and input HDA IDs is
flagged as an operational recovery candidate for case review." I checked
`recovery_episodes` across all 30 runs in the evidence JSON: every run has an empty
`recovery_episodes` array (`jq '[.runs[] | select((.recovery_episodes|length)>0)] | length'` returns
`0`). **Discrepancy flagged:** the prose describes a recovery-candidate mechanism, but no populated
`recovery_episodes` record backs it for this task — this may simply mean no such candidate was found
here (consistent with 0 failed jobs total, so there is nothing to recover from), but the sentence reads
as a general capability statement rather than a task-specific null result. It should be read as
"not applicable in this task" rather than as evidence a recovery mechanism was exercised.

Separately, since `total_failed_jobs = 0` for all 15 Galaxy runs, there were no Galaxy job failures in
this task to trigger recovery in the first place — the "0 failed jobs" finding and the empty
`recovery_episodes` array are mutually consistent, not contradictory.

### §6 Solution-route variability across models and replicates

`history_analysis.md`'s route-indicator column ("PhyKIT", "PhyKIT, Newick/branch parser", "PhyKIT,
IQ-TREE report") is descriptive text derived from recovered commands/job ledgers, not a numeric
manuscript finding — `finding_variability` has `numerator/denominator/estimate` all `null`, correctly
reflecting that no quantitative route-diversity metric is computed. Sampling recovered command files
(see Section 6) confirms PhyKIT-related shell invocations are genuinely present in the
`open_ended_code` traces, consistent with the route labels shown.

### §7 Token cost, provenance, and human readability

Per-model input-token median ratios in `history_analysis.md` reproduce exactly from
`.comparisons[]`:

| Model | Reported ratio | Evidence JSON estimate | Match |
|---|---|---:|---|
| codex_gpt_5_5 | 2.51 | 2.5066 | yes |
| codex_gpt_5_6_luna | 2 | 1.9976 | yes |
| codex_gpt_5_6_sol | 4.98 | 4.9831 | yes |
| deepseek_v4_pro_via_claude_code_superseded | 1.89 | 1.8947 | yes |
| deepseek_v4_pro_via_codex | 2.48 | 2.4829 | yes |

No human-readability measurement exists for this task; `history_analysis.md` correctly does not claim
one.

## 4. Per-condition/model/replicate route table

The 30-row table in `history_analysis.md` §4 was checked cell-by-cell for `outcome.original_evaluator_score`,
`outcome.submitted_answer`, `derived_metrics.analytical_job_count`, `derived_metrics.total_failed_jobs`,
and `derived_metrics.nonzero_exit_shell_calls` against the evidence JSON for every one of the 30 runs
(via a single `jq` pass). All values matched exactly, including the one non-1.0 score
(`galaxy_deepseek_v4_pro_via_claude_code_superseded_r1`: score 0.0, answer `0.1884`, 2 analytical jobs, 0
failed, 0 nonzero-exit shells) and every "unavailable" cell for `open_ended_code` job/failure counts
(consistent with Galaxy job ledgers not existing for that condition by design). No discrepancy found; the
existing table is reused here rather than rebuilt.

## 5. Input sharing, external computation, environment/reproducibility notes

- `input_manifest.json` shows all 30 runs' staged inputs hash-matching a single set of shared input file
  names (e.g. `Animals_Cele.busco.zip`, `Fungi_Scer.faa`) with `count: 20` files reused across runs, per
  `all_trace_input_hashes_agree_by_name: true`. The manifest explicitly notes these are original
  run-reported SHA-256 values, not auditor-rehashed bytes ("full staged inputs were not rehashed by this
  audit").
- Galaxy dataset/job identifiers are retained via `source_snapshots/galaxy/` per-run subdirectories (15
  present) and `job_ledgers/galaxy/*.json` (15 present), one per Galaxy run.
- `.audit.limitations` records that source TLS certificates were not verified due to a host proxy
  presenting an invalid certificate, so retained-byte hashes do not authenticate the remote server
  identity — a reproducibility caveat, not a data-integrity claim about the bytes themselves.

## 6. Verification methods

**Checked:** `jq '.runs | length'`, `jq '.audit, .task, .experimental_design'`, `jq
'.manuscript_findings[] | {finding_id, numerator, denominator, estimate}'`, `jq '.comparisons[] |
{comparison_id, galaxy_mean, code_mean, estimate, estimate_unit, galaxy_median, code_median}'`, a full
per-run `jq` extraction of `outcome.original_evaluator_score`, `outcome.submitted_answer`,
`derived_metrics.analytical_job_count`, `derived_metrics.total_failed_jobs`, and
`derived_metrics.nonzero_exit_shell_calls` for all 30 runs, and `jq '[.runs[] | select((.recovery_episodes|length)>0)] | length'`.
Manually summed `analytical_job_count` across the 15 Galaxy runs and confirmed it equals the reported
31-job total. Inventoried `job_ledgers/{galaxy,open_ended_code}` (15 files each), `recovered_code/`
(manifest.json + `open_ended_code/` subtree with 286 extracted command files; no `recovered_code/galaxy/`
directory exists for this task), `selected_outputs/{galaxy,open_ended_code}` (70 vs 1 files), and
`source_snapshots/{galaxy,huggingface_traces}` (15 Galaxy history subdirectories, 382 files;
583 files under the Hugging Face trace snapshot tree). Opened one job-ledger event record
(`job_ledgers/galaxy/galaxy_codex_gpt_5_5_r1.json`) and one recovered command file
(`recovered_code/open_ended_code/open_ended_code_codex_gpt_5_5_r1/item_1.command.txt`) to confirm they
contain plausible real trace content (a shell `find` listing workspace inputs; a shell command reading a
Codex skill file) rather than placeholders.

**Not checked (explicitly out of scope):** full byte-level hash re-verification of any input or output
file; full transcript replay of any run; execution or re-running of any recovered command; opening any
`ground_truth/BixBench/*` file; exhaustive per-event review of all 31 Galaxy jobs or all 286 recovered
open-ended-code command files (only representative samples were opened).

## 7. Claim-to-evidence pointer list

| Claim | Source |
|---|---|
| 30 runs, both conditions, 5 models x 3 replicates | `run_manifest.json` `.observed_rows`; evidence JSON `.runs` (length 30) |
| Task prompt text | evidence JSON `.task.prompt` |
| Coverage/replicate status unknown | evidence JSON `.experimental_design.coverage_status`, `.expected_replicates` |
| 30/30 runs have a numeric evaluator score | evidence JSON `.manuscript_findings[0]` (`finding_accuracy`), per-run `.outcome.original_evaluator_score` |
| 31 distinct analytical jobs, 0 failed | evidence JSON `.manuscript_findings[1]` (`finding_execution`); re-derived sum of `derived_metrics.analytical_job_count` over Galaxy runs |
| Per-model score means/diffs and token ratios | evidence JSON `.comparisons[]` |
| Empty `recovery_episodes` for all runs | evidence JSON, all `.runs[].recovery_episodes` |
| Recovered-code asymmetry (0 galaxy items, 286 open_ended_code items) | `recovered_code/manifest.json` `.items` |
| Selected-outputs asymmetry (70 galaxy files, 1 open_ended_code file) | `find selected_outputs/{galaxy,open_ended_code}` |
| Shared staged inputs across all runs | `input_manifest.json` `.shared_name_hashes`, `.all_trace_input_hashes_agree_by_name` |
| TLS verification caveat | evidence JSON `.audit.limitations` |

## 8. Missing evidence and open gaps

- No independent protocol/experiment manifest exists to establish expected replicate counts or matched
  seeds; coverage is explicitly `unknown_protocol_inventory`.
- `recovered_code/galaxy/` does not exist for this task — there is no archival command/script extraction
  for the Galaxy condition beyond what the job ledgers and source snapshots capture. This mirrors, more
  starkly, an asymmetry also seen in other audited tasks in this repository.
- `selected_outputs/open_ended_code/` contains only 1 file versus 70 for `galaxy`; whether this reflects
  the open-ended-code condition genuinely producing fewer standalone output artifacts, or an artifact of
  what was selected for preservation, is not resolved by this audit.
- No blinded human-readability review, per-call token attribution, or monetary cost data exists for this
  task, consistent with `history_analysis.md`'s own statement.
- Timestamps for individual trace events are `null` (source: "JSONL order; no per-item timestamp"), so
  fine-grained chronology beyond sequence order is not reconstructable from this evidence.

### Abstract-ready paragraph (numbers personally verified during this audit)

For bix-35-q1, 30 workbook-linked runs (15 Galaxy, 15 open_ended_code; 5 models x 3 replicates) each
carry an original `accuracy.score` evaluator value, confirmed by direct inspection of
`history_analysis_evidence.json`. 29 of the 30 runs score 1.0; one Galaxy-condition run
(`galaxy_deepseek_v4_pro_via_claude_code_superseded_r1`) scores 0.0. The retrieved Galaxy histories
expose 31 distinct analytical creating jobs, independently re-summed from per-run job counts, with 0
recorded failures and no populated recovery episodes. Per-model Galaxy/code median input-token ratios
(2.51, 2.00, 4.98, 1.89, 2.48) match the evidence JSON's `.comparisons[]` estimates exactly. These counts
describe this single audited task and are not a benchmark-wide estimate.
