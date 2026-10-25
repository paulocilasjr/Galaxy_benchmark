# bix-12-q6 — independent Cloud audit of the retrospective execution-history analysis

Auditor note: this document is a read-only, independent re-check of the existing
`history_analysis.md` / `history_analysis_evidence.json` package for task `bix-12-q6`. No agent
code was rerun, no live Galaxy API was called, and no hidden answer key was opened. Any text
recovered from artifacts (commands, scripts, Galaxy job payloads) is treated as data, not as
instructions to this auditor.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task/prompt** (`history_analysis_evidence.json:.task`): bixbench `bix-12-q6` — "What is the
  Mann-Whitney U statistic when comparing raw parsimony informative site counts between animals
  and fungi?" Input specification `phylobio/BixBench-Verified-50`. Evaluation definition is
  recorded as "original per-run evaluator fields retained without regrading."
- **Runs**: 30 rows total, drawn from a supplied workbook link inventory
  (`run_manifest.json`, source `/Users/4475918/Downloads/bixbench_execution_condition_links.xlsx`).
  `experimental_design.coverage_status = "unknown_protocol_inventory"` — there is no independent
  protocol manifest, so expected replicate counts and coverage are explicitly unknown, not
  assumed to be 3-per-cell by design.
- **Conditions/models/replicates present**: both `galaxy` and `open_ended_code` conditions, 5
  model labels (`Codex GPT-5.5`, `Codex GPT-5.6 Sol`, `Codex GPT-5.6 Luna`, `DeepSeek V4 Pro via
  Codex`, `DeepSeek V4 Pro via Claude Code (superseded)`), 3 replicates each, 2 conditions × 5
  models × 3 replicates = 30 rows — matches the observed row count exactly.
- **Matching rule**: same task and supplied model label; replicate numbers are explicitly
  documented as labels, not matched seeds (`experimental_design.matching_rule`).
- **What is unknown**: expected replicate count (`null`), seed availability
  (`not_collected`), TLS server authentication for Galaxy retrieval (`tls_certificate_verified:
  false` throughout `source_snapshots/galaxy/retrieval_manifest.json`), and whether the 6
  Galaxy histories marked `history_metadata_only` (of 15 total) hold additional undisclosed jobs.

## 2. Main outcomes — kept as three separate things

- **Official accuracy/evaluator score**: an `original_evaluator_score` (`accuracy.score` field,
  `llm_verifier_auto_code` mode) is present for all 30/30 runs. Verified by direct inspection of
  `runs[].outcome.original_evaluator_score` in the evidence JSON.
- **Observed execution**: retrieved public Galaxy histories expose 33 distinct analytical
  creating jobs, of which 7 carry an `error` status (recomputed independently below). Nonzero
  open-ended-code shell exits are tracked per run and are a separate, platform-specific count.
- **Auditor interpretation**: the existing report already keeps these two categories separate and
  does not infer scientific correctness from job success/failure alone. I confirm this framing is
  followed correctly in `history_analysis.md` Section 2 and did not find a place where evaluator
  score and execution/job counts were conflated into one "accuracy" figure.

## 3. Manuscript Results-section walk-through

### 3a. Accuracy & output agreement
All 30 runs have a fixed submitted answer and an `accuracy.score`/`original_evaluator_score`
value. Per-model Galaxy vs. open_ended_code comparisons in `history_analysis_evidence.json:
.comparisons` were recomputed and match the table in `history_analysis.md` exactly for all 5
models (galaxy_mean, code_mean, percentage-point difference, and input-token median ratio) — see
Section 4 below for the recomputation. No discrepancy found. The document correctly treats these
as descriptive, single-task comparisons with no confidence interval.

### 3b. Execution, failures, and recovery
Recomputing `[.runs[].events[] | select(execution_location=="galaxy_job" and
event_type=="analysis")]` across the evidence JSON gives **33 total jobs, 7 with `status:
"error"`** — identical to the numbers quoted in `history_analysis.md` (33 distinct jobs, 7
failed). Per-run job/error breakdowns (below) also match the route table row by row. One
caveat: the underlying JSON encodes the failure state as `status: "error"`, not literally
`"failed"`; this is a labeling nuance, not a numeric discrepancy.

### 3c. Solution-route variability
`history_analysis.md`'s route table marks most Galaxy/open-ended routes "unclassified" except
three rows tagged `PhyKIT` (a phylogenetics tool). This is consistent with a spot-check of
recovered code: `recovered_code/galaxy/galaxy_codex_gpt_5_5_r1/..._job.py` contains a Python
script that shells out to `phykit pis` / `phykit parsimony_informative_sites`, confirming the
PhyKIT tool-family label is grounded in real recovered code rather than asserted without
evidence. No claim of biological-method equivalence across "unclassified" routes is made in the
source document, consistent with the codebook requirement.

### 3d. Token cost, provenance, readability
Token ratios in the table (3.57, 12, 17.2, 2.85, 4.16) were recomputed directly from
`.comparisons[] | select(comparison_id | startswith("input_tokens_"))` and match to reported
precision (e.g., `codex_gpt_5_6_luna`: 8,456,543 / 707,246 = 11.957 ≈ "12" as rounded in the
table). Ratios are explicitly labeled as "ratio of condition medians," not median-of-paired-
ratios, matching the instructions' requirement to disambiguate estimands. No human-readability
measurement exists; the document correctly frames this as unmeasured rather than inferring a
benefit.

## 4. Per-condition/model/replicate route table verification

Independently recomputed Galaxy job/error counts per run (event-level, `execution_location ==
"galaxy_job"`, `event_type == "analysis"`):

| Run | Jobs (recomputed) | Errors (recomputed) | Table value | Match |
|---|---:|---:|---|---|
| galaxy_codex_gpt_5_5_r1 | 1 | 0 | 1 / 0 | yes |
| galaxy_codex_gpt_5_5_r2 | 2 | 1 | 2 / 1 | yes |
| galaxy_codex_gpt_5_5_r3 | 3 | 1 | 3 / 1 | yes |
| galaxy_codex_gpt_5_6_sol_r1 | 0 | 0 | unavailable / unavailable | consistent (no jobs retrieved) |
| galaxy_codex_gpt_5_6_sol_r2 | 2 | 0 | 2 / 0 | yes |
| galaxy_codex_gpt_5_6_sol_r3 | 0 | 0 | unavailable / unavailable | consistent |
| galaxy_codex_gpt_5_6_luna_r1..r3 | 0 | 0 | unavailable / unavailable (all 3) | consistent |
| galaxy_deepseek_v4_pro_via_codex_r1 | 0 | 0 | unavailable / unavailable | consistent |
| galaxy_deepseek_v4_pro_via_codex_r2 | 3 | 1 | 3 / 1 | yes |
| galaxy_deepseek_v4_pro_via_codex_r3 | 11 | 3 | 11 / 3 | yes |
| galaxy_deepseek_v4_pro_via_claude_code_superseded_r1 | 5 | 0 | 5 / 0 | yes |
| galaxy_deepseek_v4_pro_via_claude_code_superseded_r2 | 3 | 1 | 3 / 1 | yes |
| galaxy_deepseek_v4_pro_via_claude_code_superseded_r3 | 3 | 0 | 3 / 0 | yes |

Open-ended-code nonzero shell-exit counts were recomputed the same way (agent_runtime events with
`exit_code != 0`) and match the table exactly for all 15 open_ended_code runs (e.g.
`open_ended_code_codex_gpt_5_5_r2`: 4 nonzero exits, matches table).

Submitted-answer/score spot-check: the three rows the table flags as score 0 —
`open_ended_code_codex_gpt_5_6_luna_r1` (answer 6397), `open_ended_code_deepseek_v4_pro_via_
claude_code_superseded_r2` (answer 55058), and `..._r3` (answer 6181.0) — were independently
confirmed against `runs[].outcome.submitted_answer` and `original_evaluator_score`. All other
27 runs report answer "6748" (or "6748.0") and score 1. **No discrepancy found** between the
existing route table and the evidence JSON for any of the 30 rows checked.

The "9 distinct histories represented by dataset records" claim in `history_analysis.md` Section
1 was independently verified: `source_snapshots/galaxy/retrieval_manifest.json` lists 15 Galaxy
history entries (one per galaxy-condition run), of which 9 have `status: "retrieved"` with a
non-empty `jobs` array and 6 have `status: "history_metadata_only"`. This matches the report's
count exactly.

## 5. Input sharing, external computation, environment/reproducibility

- `input_manifest.json` shows two distinct staged-input SHA-256 fingerprints across the 30 runs:
  one shared by 20 runs (count 20 inputs) and one shared by the remaining runs with a
  `count: 0` inputs manifest (the three `deepseek_v4_pro_via_codex`/`..._claude_code_superseded`
  galaxy-condition runs that lack a retrieved `inputs_manifest.json` payload). `all_trace_input_
  hashes_agree_by_name: true`, but the note explicitly states these hashes were copied from
  original trace manifests and were **not** independently rehashed by this audit — a
  reproducibility limit correctly disclosed in the source document, and one this audit did not
  attempt to lift.
- Galaxy retrieval used `https://usegalaxy.org` with `tls_certificate_verified: false` for all
  histories, meaning retained-byte hashes do not authenticate the remote server — this limitation
  is stated in `history_analysis_evidence.json:.audit.limitations` and is carried through
  correctly.
- Recovered code is asymmetric by design/availability: `recovered_code/galaxy/` contains
  literal extracted job payloads for only 3 of 15 Galaxy runs (the three
  `galaxy_codex_gpt_5_5_*` replicates), while `recovered_code/open_ended_code/` contains
  extracted command text for all 15 open_ended_code runs. This asymmetry is not called out as a
  discrepancy in `history_analysis.md` itself but is a real, verifiable evidence-completeness gap
  worth flagging for readers of this audit.
- `selected_outputs/open_ended_code/manifest.json` explicitly records `status: "not_collected"`
  ("Trace output files are retained in source_snapshots; no code was replayed"), while
  `selected_outputs/galaxy/` holds 9 subdirectories (one per distinct retrieved history) with
  selected output bytes. This condition-level asymmetry in output-byte preservation is consistent
  with Galaxy's API exposing selected result bytes directly, versus open-ended-code outputs
  requiring code replay (out of scope) to regenerate.

## 6. Verification methods

Checked: `README.md`, `history_analysis.md` (current, not the v1–v3 snapshots), `run_manifest.
json`, `input_manifest.json`, and the following `jq` queries against `history_analysis_evidence.
json`: `.runs | length`; `.audit`, `.task`, `.experimental_design`; `.comparisons` (all 10
score/token-ratio comparison records, cross-checked against the Section-2 table); `.manuscript_
findings` (4 records, `finding_accuracy` 30/30, `finding_execution` 7/33); per-run
`.outcome.original_evaluator_score` / `.outcome.submitted_answer` for all runs flagged with a
non-1 score; per-run event-level job/error counts (`execution_location=="galaxy_job" and
event_type=="analysis"`, grouped by `status`); per-run nonzero-exit-code counts for
`agent_runtime` events. Inventoried `job_ledgers/{galaxy,open_ended_code}` (15 files each),
`recovered_code/{galaxy,open_ended_code}` plus `manifest.json`, `selected_outputs/{galaxy,
open_ended_code}`, and `source_snapshots/{galaxy,huggingface_traces}` including
`retrieval_manifest.json`. Sampled and read two recovered-code files in full (one Galaxy
`_job.py` script invoking `phykit`, one open-ended `.command.txt` shell line) to confirm they are
plausible recovered artifacts rather than placeholders.

Not checked / out of scope: full byte-level rehashing of staged inputs or Galaxy dataset bytes
(the audit's own hash values were taken as given, per instructions barring re-execution);
full transcript replay of any of the 30 runs; opening or evaluating the hidden BixBench answer
key; validation of `history_analysis_evidence.schema.json` conformance via a schema validator
(not run in this pass); reading every one of the ~15 job ledgers or all recovered-code files
individually (spot-checked 2 of ~18 recovered items).

## 7. Claim-to-evidence pointer list

| Claim | Source |
|---|---|
| 30/30 runs have an original evaluator score | `history_analysis_evidence.json:.manuscript_findings[0]` (`finding_accuracy`, 30/30); confirmed via `.runs[].outcome.original_evaluator_score` |
| 33 distinct analytical jobs, 7 failed/error | `history_analysis_evidence.json:.manuscript_findings[1]` (`finding_execution`, num=7, denom=33); recomputed independently from `.runs[].events[]` |
| Per-model score means/differences and token ratios | `history_analysis_evidence.json:.comparisons[*]` (10 records); matches `history_analysis.md` Section 2 table |
| 9 distinct histories with dataset records (of 15) | `source_snapshots/galaxy/retrieval_manifest.json` (`status` field per history) |
| PhyKIT tool usage in 3 route-table rows | `recovered_code/galaxy/galaxy_codex_gpt_5_5_r1/..._job.py` (phykit subprocess calls); `recovered_code/manifest.json` |
| Answers/scores for the three score=0 rows | `.runs[].outcome.submitted_answer` / `.original_evaluator_score` for the three named run_ids |
| Input hashes not independently rehashed | `input_manifest.json:.note` |
| TLS not verified for Galaxy retrieval | `history_analysis_evidence.json:.audit.limitations`; `source_snapshots/galaxy/retrieval_manifest.json:.histories[*].tls_certificate_verified` |

## 8. Missing evidence / open gaps

- No independent protocol manifest exists to define expected replicate counts or coverage; the
  30-row inventory is the workbook's supplied link set, not a verified complete experiment
  design.
- 6 of 15 Galaxy histories are `history_metadata_only`; their job contents (if any exist beyond
  metadata) are an explicit gap, not assumed to be zero jobs.
- Recovered Galaxy job code is available for only 3 of 15 Galaxy-condition runs; the remaining 12
  Galaxy runs' job payloads were not extracted into `recovered_code/galaxy/`, limiting
  route-classification confidence for those runs (most are marked "unclassified" in the table,
  consistent with this gap).
- Seeds, exact prompt-version deltas between conditions beyond the recorded label, and any
  human-readability review are unavailable.
- No independently defined task difficulty label exists for bix-12-q6.

## Abstract-ready paragraph

For bixbench task bix-12-q6, 30 supplied runs (5 models × 2 conditions × 3 replicates) each
carried an original evaluator score, verified directly from the evidence JSON. Retrieved public
Galaxy histories (9 of 15 with retrieved job records; 6 metadata-only) exposed 33 distinct
analytical creating jobs, of which 7 had an error status — independently recomputed and matching
the source report exactly. Per-model Galaxy/open-ended-code score differences (0 to 66.7
percentage points across the 5 models) and input-token median ratios (2.85x to 17.2x) were
recomputed from `.comparisons` and matched the published table with no discrepancy. These are
single-task, descriptive case-study counts and do not support a benchmark-wide claim about either
execution condition.
