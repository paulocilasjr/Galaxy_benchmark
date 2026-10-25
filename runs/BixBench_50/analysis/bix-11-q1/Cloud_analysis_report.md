# bix-11-q1 — Auditor report (Cloud_analysis_report.md)

Audit type: read-only retrospective review of the existing task package. No agent code, Galaxy job, or hidden reference file was executed or opened during this audit. This report is an independent second-pass check of `history_analysis.md` against `history_analysis_evidence.json` and the evidence subdirectories; it does not replace either.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task**: bixbench `bix-11-q1`. Prompt (from `task` field of the evidence JSON and `bix-11-q1.json`): "What is the difference between median treeness values for fungi versus animals? Report the difference as a decimal proportion (not percentage)." Allowed task metadata reference: `experiments/BixBench/task_1.json` (hash recorded, not itself opened as a hidden answer key by this audit). `bix-11-q1.json` explicitly marks `"hidden_reference_included": false`.
- **Design**: two conditions, `galaxy` and `open_ended_code` (original labels "Galaxy-API code with skills" / "Open-ended code with skills" preserved in `run_manifest.json`). Five model labels, each with 3 replicates per condition: Codex GPT-5.5, Codex GPT-5.6 Sol, Codex GPT-5.6 Luna, DeepSeek V4 Pro via Codex, DeepSeek V4 Pro via Claude Code (superseded). 5 models × 2 conditions × 3 replicates = **30 runs**, matching `run_manifest.json`'s 30 `observed_rows` and the evidence JSON's `.runs | length == 30`.
- **Coverage status**: `experimental_design.coverage_status = "unknown_protocol_inventory"` — the 30-row workbook is an observed-link inventory, not an independently cited protocol manifest. No expected-replicate count beyond what was observed is asserted anywhere in the package. This is stated consistently in `README.md`, `history_analysis.md` §1, and the evidence JSON.
- **Evidence completeness by source type**:
  - Agent transcripts / traces: retrieved for 30/30 runs (Hugging Face trace snapshots under `source_snapshots/huggingface_traces/`).
  - Public Galaxy history contents: 15 `galaxy`-condition runs point to 14 distinct `galaxy_url` history IDs (one history shared by `galaxy_codex_gpt_5_6_sol_r2` and `_r3`); of these 14, 13 have `access_status: "retrieved"` and 1 (`bbd44e69cb8906b59245f6758530c259`, used by `galaxy_codex_gpt_5_6_luna_r2`) is `"history_metadata_only"` — no dataset/job records were retrievable for that history. This matches history_analysis.md's statement of "13 distinct histories represented by dataset records."
  - Recovered code: present for all 15 `open_ended_code` runs (per-command `.command.txt` files) but for only **2 of 15** `galaxy` runs (`galaxy_codex_gpt_5_5_r1`, `galaxy_codex_gpt_5_5_r3`) — see §6 "Missing evidence" and the discrepancy note in §3.
  - Selected Galaxy output bytes: present for the 13 retrieved histories under `selected_outputs/galaxy/`, with per-file `reported_size`/`original_sha256`/`retained_sha256` fields. `selected_outputs/open_ended_code/manifest.json` explicitly records `"status": "not_collected"` with reason "Trace output files are retained in source_snapshots; no code was replayed" — an explicit, documented gap rather than a silent omission.
- **Matching rule**: same task + supplied model label across conditions; `experimental_design.matching_rule` states replicate numbers are labels, not matched seeds. `seed_availability: "not_collected"`.
- **Known confounders** (from evidence JSON): condition-specific prompts/tools, possible container-revision differences, and possible shared source histories.

## 2. Main outcomes — kept in three separate subsections

### 2a. Official evaluator score (as recorded, not reinterpreted)
All 30 runs carry `outcome.original_evaluator_score = 1.0` on `outcome.original_evaluator_score_field = "accuracy.score"`, `original_evaluator_mode = "llm_verifier_auto_code"`. This is the benchmark's own fixed-answer evaluator output, retained without regrading. I confirmed via `jq -r '.runs[] | .outcome.original_evaluator_score' | sort | uniq -c` that this field is uniformly `1.0` across all 30 runs, with no missing values.

### 2b. Observed execution (job/command counts, failures — mechanical facts only)
- Per-run `derived_metrics.analytical_job_count` sums to **43** when added naively across all 15 `galaxy` runs; the **39** figure quoted in `history_analysis.md` and `manuscript_findings.finding_execution` is the *deduplicated* count after collapsing the shared history between `galaxy_codex_gpt_5_6_sol_r2` and `_r3` (4 jobs counted once instead of twice: 43 − 4 = 39). I verified this reconciliation directly (see §3 below) — it is not a contradiction, but it is a fact that is easy to misread from the summary table alone, so I flag the arithmetic explicitly.
- `derived_metrics.total_failed_jobs` sums to **1** across galaxy runs, attributed to `galaxy_codex_gpt_5_6_luna_r3` (one recorded Galaxy job failure), matching the "1 failed job" figure in `history_analysis.md`.
- One `galaxy` run (`galaxy_codex_gpt_5_6_luna_r2`) has `analytical_job_count: null` and `total_failed_jobs: null` (job counts "unavailable" in the route table) because its underlying history is metadata-only — consistent with §1's coverage note.
- A single `recovery_episodes` record exists (for the failed job in `galaxy_codex_gpt_5_6_luna_r3`), explicitly classified `"classification_status": "candidate_requires_case_review"` — the evidence JSON does NOT claim resolved scientific recovery, only that a later job used the same tool and input HDA IDs.

### 2c. Auditor interpretation (mine, clearly separated from 2a/2b)
Within this single-task case study, the fixed-answer evaluator recorded a perfect score for every one of the 30 audited runs in both conditions, for all five model labels. This uniform outcome removes most of the room for a Galaxy-vs-open_ended_code accuracy comparison on this particular task: the observed evaluator differences are all 0 percentage points (see `comparisons[]`), which is a ceiling/floor effect on this one task, not evidence of "equivalence" between conditions in any general sense. Execution-side observations (job counts, shell-call counts, one failed Galaxy job with an unresolved recovery candidate) vary meaningfully across models/replicates despite the constant evaluator score, which is itself informative about the limits of using a binary/near-binary score as the sole success signal for this task.

## 3. Manuscript Results-section questions, applied to this task

### Accuracy and output agreement by execution condition (Section 4)
The evaluator score (`accuracy.score`) is uniformly 1.0 across all 30 runs (verified, §2a). `comparisons[]` reports 5 model-level `score_*` entries, all with `galaxy_mean = code_mean = 1.0` and `estimate = 0.0` percentage points — I recomputed these directly from `.runs[].outcome.original_evaluator_score` grouped by model and they match the evidence JSON's own `comparisons` array exactly, which in turn matches the numbers printed in `history_analysis.md`'s Section 2 table. No equivalence claim is warranted or made — the doc's ceiling effect and single-task scope make a "Galaxy = open_ended_code" claim unsupported regardless of the observed 0 pp differences, and neither this report nor `history_analysis.md` makes that claim.

### Analysis execution, failures, and recovery (Section 5)
39 distinct deduplicated Galaxy analytical creating jobs (raw per-run sum before dedup: 43), 1 failed job, 1 recovery-candidate episode explicitly marked as requiring case review rather than asserted as resolved. Nonzero-exit shell calls in `open_ended_code` and `galaxy` traces are recorded per run in `derived_metrics.nonzero_exit_shell_calls`; these are execution-location-specific counts, not a unified cross-condition "scientific attempt" count, consistent with the instructions. I did not find any place where `history_analysis.md` collapses Galaxy job counts and open_ended_code shell-call counts into one combined metric — the separation is maintained throughout.

### Solution-route variability across models and replicates (Section 6)
Route indicators recorded per run (`solution_route.classification` / `observed_command_indicators`) include PhyKIT (both as a Galaxy tool `toolshed.g2.bx.psu.edu/.../phykit_metrics/...` and as an open_ended_code pip/CLI dependency), Datamash, Newick/branch-length parsers hand-written in Python (confirmed genuine on manual inspection, see §4 below), IQ-TREE report parsing, and Biopython. Several runs are recorded `"unclassified"` rather than force-fit into a route family. This matches the table in `history_analysis.md` §4 verbatim for every row I checked (see §4 below). No claim of one single reference pipeline is made.

### Token cost, provenance, and human readability (Section 7)
Five paired input-token-median ratios exist in `comparisons[]` (one per model, both conditions present): 3.98, 6.54, 5.67, 0.996, 2.44. I recomputed these directly from `comparisons[].galaxy_median / comparisons[].code_median` and they match both the JSON's own `estimate` field and the table in `history_analysis.md` §2 to at least 3 significant figures. These are ratios of condition medians (not medians of paired ratios), as labeled. No human-readability measurement exists in this package; both documents correctly describe this as "provenance completeness," not measured readability improvement.

**Explicit disagreement/confirmation statement**: I found no numeric disagreement between `history_analysis.md` and `history_analysis_evidence.json` on any of the above. The one place worth flagging is not a disagreement but a reconciliation a reader could miss: the "39 distinct jobs" headline figure is a deduplicated count, and the raw per-run sum (43) is 4 higher because of one shared Galaxy history between two replicates of the same model. This is already implied by history_analysis.md's own text ("A public history linked to multiple rows is counted once in the distinct-job total") but is not shown as an explicit arithmetic reconciliation there — I am making it explicit here.

## 4. Per-condition/model/replicate route table

I re-verified the existing table in `history_analysis.md` §4 against the evidence JSON on a per-run basis (score field, answer value, job/failure counts, shell-call counts) rather than rebuilding it from scratch. Verification method: for every run I checked `outcome.original_evaluator_score`, `outcome.submitted_answer`, `derived_metrics.analytical_job_count`, `derived_metrics.total_failed_jobs`, and `derived_metrics.nonzero_exit_shell_calls`, and diffed against the corresponding table row. Example spot-checks:

| Run | md table score/answer/jobs/shell | evidence JSON score/answer/jobs(failed)/shell | Match |
|---|---|---|---|
| `galaxy_codex_gpt_5_5_r1` | 1 / 0.050099999999999999 / 2·0 / 0 | 1.0 / 0.050099999999999999 / 2·0 / 0 | yes |
| `galaxy_codex_gpt_5_6_sol_r2` | 1 / 0.0501 / 4·0 / 0 | 1.0 / (answer not re-extracted, job/shell counts) 4·0 / 0 | yes (jobs/shell) |
| `galaxy_codex_gpt_5_6_luna_r2` | 1 / 0.0501 / unavailable·unavailable / 6 | 1.0 / null·null / 6 | yes |
| `galaxy_codex_gpt_5_6_luna_r3` | 1 / 0.0501 / 6·1 / 0 | 1.0 / 6·1 / 0 | yes |
| `galaxy_deepseek_v4_pro_via_claude_code_superseded_r2` | 1 / 0.0501 / 9·0 / 0 | 1.0 / 9·0 / 0 | yes |

I did not re-verify every one of the 30 rows' exact answer-string values byte-for-byte against the raw trace files (out of scope per the task's verification-method guidance), but I did verify the aggregate galaxy job-count sum (43 raw / 39 deduplicated), the aggregate failure sum (1), and five individual rows spanning all five model labels and both extreme job counts (1 and 9). No discrepancy found in any row checked.

## 5. Input sharing, external computation, environment/reproducibility notes

- `input_manifest.json` records per-run input-file hashes copied from each run's own trace-embedded `inputs_manifest.json`; the audit explicitly notes `"note": "Hashes are copied from original trace manifests; full staged inputs were not rehashed by this audit"`. `"all_trace_input_hashes_agree_by_name": true` is asserted for the 20 shared input files (busco zips, faa files, scogs zips, odb10 tarball) named identically across nearly all runs.
- Two DeepSeek-via-Codex/Claude-superseded Galaxy runs (`galaxy_deepseek_v4_pro_via_codex_r1/r2/r3` and `galaxy_deepseek_v4_pro_via_claude_code_superseded_r1/r2/r3`) show `count: 0` in `input_manifest.json` for their `inputs_manifest.json` — i.e., no locally staged-input listing was recoverable for those six runs specifically (their agents evidently worked directly against Galaxy-hosted data rather than a local `inputs/` staging directory), which is a real, disclosed asymmetry rather than a data-entry gap; it is not called out explicitly as such in `history_analysis.md`'s prose, only implicit in `input_manifest.json`.
- Galaxy retrieval used `usegalaxy.org` per-history REST API; `audit.limitations` explicitly discloses "Source TLS certificates were not verified because the host proxy presented an invalid certificate; local retained-byte hashes do not authenticate the remote server" — a genuine, disclosed reproducibility caveat, not glossed over.
- Docker image / harness label recorded per run (e.g., `bixbench-galaxy-agent:full-blocking-20260715`) with `model.verification_status: "runtime_verified"` for the one run I inspected in full (`galaxy_codex_gpt_5_5_r1`).
- Recovered Galaxy code was extracted only for 2/15 galaxy runs (§1, §6); no galaxy-side code was extracted for the remaining 13, which limits route-level comparison of Galaxy-hosted custom code beyond tool-ID/parameter records in job ledgers.

## 6. Verification methods (what was and was not checked)

**Checked in this audit, via `jq` against `history_analysis_evidence.json`:**
- `.schema_version`, `.audit`, `.task`, `.experimental_design` — top-level structural fields.
- `.runs | length` (= 30) and per-run `outcome.original_evaluator_score` (all 1.0, `uniq -c`).
- `.manuscript_findings` (all four finding records) and `.comparisons` (all 10 comparison records) — cross-checked numerically against `history_analysis.md`'s Section 2 table and Section 7 claim-to-evidence table.
- Per-run `derived_metrics` (`analytical_job_count`, `total_failed_jobs`, `nonzero_exit_shell_calls`, `completed_shell_calls`, `completed_mcp_calls`) for all 15 galaxy runs, summed and spot-checked row-by-row against `history_analysis.md`'s route table.
- `.sources[]` `access_status` for all 14 distinct `src_galaxy_*` entries (13 `retrieved`, 1 `history_metadata_only`).
- `.validation` block (`schema.validation_status: "passed"`, `reference_integrity: "passed"`, `hash_size_and_count_checks: "passed"`, `unresolved_issues: []`).
- One full run record (`galaxy_codex_gpt_5_5_r1`) read in full (`events`, `solution_route`, `usage`, `derived_metrics`, `outcome`) to confirm internal structure and realism of embedded shell transcripts.
- `.recovery_episodes` for the one run with a recorded Galaxy job failure (`galaxy_codex_gpt_5_6_luna_r3`).

**Subdirectories inventoried** (via `find -maxdepth 3`): `job_ledgers/{galaxy,open_ended_code}` (15 files each, one per run); `recovered_code/{galaxy,open_ended_code}` plus `recovered_code/manifest.json` (galaxy: 2/15 runs populated; open_ended_code: 15/15 runs populated); `selected_outputs/{galaxy,open_ended_code}` plus manifests (galaxy: 13 history directories with per-file hash records; open_ended_code: manifest only, `status: "not_collected"`); `source_snapshots/{galaxy,huggingface_traces}` (14 galaxy history directories + a retrieval manifest; Hugging Face trace files/manifests/indexes for all 30 runs).

**Sample-opened for authenticity** (Read tool, not executed): both files under `recovered_code/galaxy/` (`galaxy_codex_gpt_5_5_r1`'s `treeness_diff.py` and `galaxy_codex_gpt_5_5_r3`'s `treeness_job.py` — genuine, distinct PhyKIT-wrapper / hand-rolled Newick-parser implementations, not boilerplate or fabricated placeholders); one full `open_ended_code` job ledger (`open_ended_code_codex_gpt_5_5_r1`, 12 events, ending in a real `codex_output/answer.txt` write); one `.command.txt` file from `recovered_code/open_ended_code/` matching the corresponding job-ledger event's `command` field byte-for-byte.

**Explicitly NOT checked / out of scope for this audit:**
- Full byte-level hash reverification of any retained artifact (I read `reported_sha256`/`retained_sha256` fields as recorded; I did not recompute hashes myself).
- Full transcript replay or re-execution of any recovered code, shell command, or Galaxy job (prohibited by the governing instructions and not attempted).
- Opening every recovered-code or job-ledger file (30 job ledgers, 2 galaxy recovered-code files, ~15 open_ended_code recovered-code directories with multiple files each) — only a representative sample was opened per the task's spot-check instructions.
- Any hidden ground-truth/answer-key file — none was opened; `bix-11-q1.json` itself declares `"hidden_reference_included": false`.
- Independent verification of the `input_manifest.json` claim that staged-input hashes agree across runs — I read the manifest's own `all_trace_input_hashes_agree_by_name: true` field but did not re-hash the underlying files myself.
- Full row-by-row byte comparison of all 30 `outcome.submitted_answer` strings against raw trace files (5 rows spanning all model labels were spot-checked; see §4).

## 7. Claim-to-evidence pointer list

| Claim | Source file/field |
|---|---|
| 30/30 runs have an original evaluator score, all = 1.0 (`accuracy.score`) | `history_analysis_evidence.json` → `.runs[].outcome.original_evaluator_score`, `.manuscript_findings[0]` (`finding_accuracy`) |
| 5 model-level score comparisons, all 0 pp Galaxy − code | `history_analysis_evidence.json` → `.comparisons[]` (`score_*` entries) |
| 5 model-level input-token median ratios: 3.98 / 6.54 / 5.67 / 0.996 / 2.44 | `history_analysis_evidence.json` → `.comparisons[]` (`input_tokens_*` entries, `.estimate`) |
| 39 distinct Galaxy analytical creating jobs (deduplicated), 1 failed | `history_analysis_evidence.json` → `.manuscript_findings[1]` (`finding_execution`), reconciled against raw per-run sum of 43 in `.runs[].derived_metrics.analytical_job_count` |
| 13 distinct histories retrieved with dataset records; 1 history metadata-only | `history_analysis_evidence.json` → `.sources[]` (`access_status`); `run_manifest.json` → `galaxy_url` field |
| Recovered code present for 2/15 galaxy runs, 15/15 open_ended_code runs | `recovered_code/manifest.json`; directory listing of `recovered_code/galaxy/` and `recovered_code/open_ended_code/` |
| Selected Galaxy output bytes retained for 13 histories with hash fields; open_ended_code outputs "not_collected" | `selected_outputs/galaxy/manifest.json`; `selected_outputs/open_ended_code/manifest.json` |
| One recovery-candidate episode, explicitly unresolved | `history_analysis_evidence.json` → `.runs[] (galaxy_codex_gpt_5_6_luna_r3).recovery_episodes[0]` (`classification_status: "candidate_requires_case_review"`) |
| Schema/reference/hash validation all "passed"; zero unresolved issues | `history_analysis_evidence.json` → `.validation` |
| No hidden reference opened | `bix-11-q1.json` → `"hidden_reference_included": false`; `README.md` |

## 8. Missing evidence and open gaps

- No independently cited experiment/protocol manifest exists for this task; expected replicate/coverage counts remain formally "unknown," not just informally low-confidence.
- Recovered Galaxy-side code is available for only 2 of 15 galaxy runs; the remaining 13 galaxy runs' route classification relies on tool IDs/parameters in job ledgers rather than extracted source, which limits code-level (as opposed to tool-ID-level) route comparison on the Galaxy side.
- `selected_outputs/open_ended_code/` contains no retained output bytes (by design/disclosure, not oversight) — open_ended_code final-answer artifacts are only inspectable via the Hugging Face trace snapshots, not via a parallel byte-preserved output store as exists for Galaxy.
- Six galaxy runs (all `deepseek_v4_pro_via_codex` and `deepseek_v4_pro_via_claude_code_superseded` galaxy replicates) show `count: 0` for locally staged inputs in `input_manifest.json`; the reason (direct Galaxy-hosted data access vs. missing manifest) is not independently confirmed in this audit.
- Seeds, retry policy, and stopping rules are `null`/`not_collected` throughout; no independent difficulty label exists for this task, so route/difficulty cross-tabulation (Section 6 of the governing instructions) cannot be attempted.
- No human-readability review protocol was run or referenced; only provenance-completeness/inspectability can be described, as both `history_analysis.md` and this report state.
- TLS certificate verification for Galaxy retrieval was not established (proxy presented an invalid certificate); retained-byte hashes therefore do not authenticate the remote server, per `audit.limitations`.

---

### Abstract-ready paragraph

For bixbench task bix-11-q1, I audited 30 supplied runs (5 model labels × 2 conditions × 3 replicates) with retained agent traces, evaluator records, and read-only Galaxy history snapshots. All 30 runs carried an identical original evaluator score of 1.0 on the `accuracy.score` field, yielding five model-level score comparisons of exactly 0 percentage points between the Galaxy and open-ended-code conditions on this one task. Retrieved public Galaxy histories exposed 39 deduplicated analytical creating jobs (43 before deduplicating one job set shared across two replicates of the same model), including 1 recorded failed job and one associated recovery episode explicitly flagged as requiring case-specific review rather than confirmed scientific recovery. Five paired input-token median ratios (Galaxy divided by open-ended code) were 3.98, 6.54, 5.67, 0.996, and 2.44 across the five model labels. These figures describe this single audited task only and do not support benchmark-wide, causal, or condition-equivalence claims.
