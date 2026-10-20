# Cloud analysis report: bixbench bix-12-q5

Independent read-only audit of the existing task-audit package at
`BixBench_50/analysis/bix-12-q5/`. This report does not replace
`history_analysis.md`; it records what an independent spot-check of
`history_analysis_evidence.json` and the evidence subdirectories confirmed,
could not confirm, or found inconsistent. No agent code was rerun, no Galaxy
API calls were made, and no hidden reference/answer-key file was opened. All
counts below were recomputed by the auditor directly from
`history_analysis_evidence.json` with `jq`, from the four top-level JSON
manifests, and from a directory inventory; none were copied from
`history_analysis.md` prose without separate verification.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task**: bixbench `bix-12-q5`. Prompt (from `bix-12-q5.json` and
  `history_analysis_evidence.json:.task.prompt`, identical in both): "What is
  the maximum number of parsimony informative sites in any animal gene
  alignment?" Allowed task metadata reference:
  `experiments/BixBench/task_5.json` (`bix-12-q5.json`); `hidden_reference_included: false`.
  No hidden answer key was present in this directory or opened by this audit.
- **Design source**: `run_manifest.json` is a workbook-derived link inventory
  (`inventory_source`: `bixbench_execution_condition_links.xlsx`), not an
  independent protocol manifest. `experimental_design.coverage_status` in the
  evidence JSON is explicitly `"unknown_protocol_inventory"` and
  `expected_replicates` is `null`. Expected coverage is therefore unknown by
  design, not by omission.
- **Rows/runs**: 30 observed rows in `run_manifest.json`, and 30 run records in
  `history_analysis_evidence.json.runs` (`jq '.runs | length'` → 30). All 30
  have `status: "trace_observed"` (verified by `group_by` on `.runs[].status`).
- **Conditions**: `galaxy` and `open_ended_code`, preserved as original labels;
  `run_manifest.json` additionally carries human-readable condition labels
  ("Galaxy-API code with skills" / "Open-ended code with skills"). These two
  condition populations are kept separate throughout this report and are never
  pooled into one "accuracy" figure.
- **Models/replicates**: 5 model labels x 2 conditions x 3 replicates = 30 rows:
  `codex_gpt_5_5`, `codex_gpt_5_6_sol`, `codex_gpt_5_6_luna`,
  `deepseek_v4_pro_via_codex`, `deepseek_v4_pro_via_claude_code_superseded`.
  Model identity is the supplied label; `experimental_design.matching_rule`
  states matching is "Same task and supplied model label; replicate numbers
  are labels, not matched seeds." `seed_availability` is `"not_collected"`.
- **Galaxy public-history retrieval**: 18 of the 30 rows are `galaxy` condition
  and carry a `galaxy_url`; `open_ended_code` rows carry `galaxy_url: null`.
  Public Galaxy dataset/job data was actually retrieved for 9 of those 18
  Galaxy runs (the runs with non-null `derived_metrics.analytical_job_count`,
  see Section 2); the remaining 9 Galaxy rows are marked `"unavailable"` for
  job/failure counts in the route table. This matches the "9 distinct
  histories represented by dataset records" statement in
  `history_analysis.md` Section 1.
- **Known confounders** (`experimental_design.known_confounders`):
  condition-specific prompts/tools, possible container-revision differences,
  possible shared source histories.
- **What is unknown**: expected replicate count/protocol, seeds, whether
  replicate numbers correspond to matched runs across conditions, and full
  Galaxy job/failure data for 9 of the 18 Galaxy runs.

## 2. Main outcomes (kept in three separate subsections, per audit requirement)

### 2a. Official evaluator score (as recorded by the original evaluator, not the auditor)

- Every one of the 30 runs carries `outcome.original_evaluator_score_field =
  "accuracy.score"` and a non-null `outcome.original_evaluator_score`
  (verified directly, `jq -r '.runs[] | [.run_id, .outcome.original_evaluator_score_field, .outcome.original_evaluator_score, .outcome.submitted_answer]'`).
  28/30 runs scored `1.0`; 2/30 runs (both
  `open_ended_code_deepseek_v4_pro_via_claude_code_superseded`, replicates 1
  and 3) scored `0.0` with submitted answer `35` instead of `29`.
  `manuscript_findings[0]` (`finding_accuracy`) reports numerator 30,
  denominator 30, estimate 1.0 — that estimate is "runs with an observed
  evaluator score available," not "runs scored correct"; it should not be
  read as a 100% accuracy figure. This is a scope/labeling nuance worth
  flagging explicitly: `history_analysis.md` avoids this confusion by never
  quoting `finding_accuracy`'s numeric estimate as an accuracy percentage, but
  a careless reader of the raw evidence JSON could conflate "score coverage"
  with "score value." No inconsistency was found — this is a clarity note, not
  a discrepancy.
- These are the official per-run `accuracy.score` values as retained from the
  original evaluator record (e.g. `evaluation.json` referenced by
  `outcome.original_evaluator_record`); this audit did not regrade any answer.

### 2b. Observed execution (job/command counts, failures — auditor-tallied from retained ledgers, not evaluator output)

- Summing `derived_metrics.analytical_job_count` across the 9 Galaxy runs
  with non-null job data: 3+2+1+1+5+2+1+1+2 = **18** distinct analytical
  creating jobs. Summing `derived_metrics.total_failed_jobs` over the same
  9 runs: 2+1+0+0+3+1+0+0+1 = **8** failed jobs. Both totals match
  `history_analysis.md`'s Section 2 statement ("18 distinct analytical
  creating jobs, including 8 failed jobs") and `manuscript_findings[1]`
  (`finding_execution`: numerator 8, denominator 18, estimate 0.444...).
  Confirmed consistent — no discrepancy.
- These job/failure counts are Galaxy-specific (native creating-job counts,
  deduplicated per the evidence JSON's own accounting) and are not a
  cross-condition "scientific attempt" count. Open-ended-code shell-call
  counts (`derived_metrics.nonzero_exit_shell_calls`) are recorded per run
  where available but are a different unit and are not summed into the
  Galaxy job total.

### 2c. Auditor interpretation

- The near-uniform `accuracy.score = 1` across both conditions for 4 of 5
  models, with one model (`deepseek_v4_pro_via_claude_code_superseded`)
  showing a 2/3 open_ended_code failure rate against 3/3 Galaxy success, is a
  single-task, single-model observation. It does not establish that Galaxy is
  more reliable than open-ended code for this model or in general: only one
  model out of five diverges, replicate counts are small (n=3 per cell), and
  no prespecified equivalence/superiority margin is defined anywhere in the
  evidence package. The pattern is reported descriptively, consistent with
  `history_analysis.md`'s own framing ("no task-level confidence interval or
  equivalence conclusion is calculated from this one task").
- The 8/18 (44%) Galaxy job failure rate is nontrivial but is drawn only from
  the 9 Galaxy runs with retrievable public-history data; it cannot be
  extrapolated to the other 9 Galaxy runs whose job data is `"unavailable"`,
  nor to open-ended-code executions (which have no comparable Galaxy-job
  concept).

## 3. Manuscript Results-section questions, applied to this task

### 3.1 Accuracy and output agreement by execution condition

Evidence shows (per-model, per-condition means from
`history_analysis_evidence.json.comparisons`, independently recomputed and
cross-checked against the run-level `outcome.original_evaluator_score`
values):

| Model | Galaxy mean | Code mean | Difference | Verified? |
|---|---:|---:|---:|---|
| codex_gpt_5_5 | 1.0 | 1.0 | 0 pp | Confirmed against comparisons[] and run-level scores |
| codex_gpt_5_6_sol | 1.0 | 1.0 | 0 pp | Confirmed |
| codex_gpt_5_6_luna | 1.0 | 1.0 | 0 pp | Confirmed |
| deepseek_v4_pro_via_codex | 1.0 | 1.0 | 0 pp | Confirmed |
| deepseek_v4_pro_via_claude_code_superseded | 1.0 | 0.333 | 66.7 pp | Confirmed (2/3 open_ended_code runs scored 0) |

All five rows match `history_analysis.md`'s Section 2 table exactly (values
1/1/0pp, 1/1/0pp, 1/1/0pp, 1/0.333/66.7pp, 1/1/0pp). **No discrepancy found.**
This is a single-task case study with n=3 replicates per cell; the 66.7 pp
gap for one model is an observed difference, not evidence of a general Galaxy
advantage — no prespecified margin or paired statistical test is present in
the evidence package to support an "improved" or "equivalent" claim, and none
is made in `history_analysis.md`.

### 3.2 Analysis execution, failures, and recovery

Confirmed: 18 distinct Galaxy analytical creating jobs, 8 failed, drawn from
9 of the 18 Galaxy runs with retrievable job ledgers (Section 2b above).
`recovery_episodes` arrays were spot-checked on several runs (e.g.
`galaxy_codex_gpt_5_5_r1`) and are empty (`[]`); this audit did not find any
run with a populated `recovery_episodes` array. `history_analysis.md`
describes recovery only as an unresolved "candidate for case review," not as
a demonstrated recovery episode, which is consistent with the empty arrays
observed. Unresolved: `failed_jobs_before_first_supported_result` and
`failed_attempts_before_first_correct_answer` are `null` for every run
sampled — the endpoint-specific recovery metrics called for by
Section 5 of the methodology are not populated in this evidence package, and
`history_analysis.md` does not claim otherwise.

### 3.3 Solution-route variability across models and replicates

`solution_route.classification` is `null` for the sampled run
(`galaxy_codex_gpt_5_5_r1`), with `tool_ids` populated
(`animal-pis-max-20260716` variants) and `biological_method: null`. The route
table in `history_analysis.md` Section 4 labels most routes "unclassified"
and marks a few "PhyKIT" — consistent with an explicit codebook not yet being
applied beyond tool-name detection. Two recovered_code samples were read
directly (see Section 6) and both are genuine, task-relevant scripts/commands
(a Python PhyKIT-wrapper script computing parsimony-informative sites from a
zipped alignment collection, and shell commands listing zip contents /
reading a skill file) — not fabricated placeholders. Route variability
across the 30 runs is not independently re-derived here beyond confirming the
underlying `tool_ids`/command evidence exists; this audit did not build a new
codebook.

### 3.4 Token cost, provenance, and readability

All five token-ratio comparisons in `history_analysis_evidence.json.comparisons`
were recomputed by hand from the stored `galaxy_median`/`code_median` values
and matched `history_analysis.md`'s Section 2 table:

| Model | galaxy_median | code_median | ratio (evidence JSON) | ratio (history_analysis.md) |
|---|---:|---:|---:|---:|
| codex_gpt_5_5 | 1,604,452 | 199,622 | 8.037 | 8.04 |
| codex_gpt_5_6_luna | 10,400,271 | 540,131 | 19.255 | 19.3 |
| codex_gpt_5_6_sol | 3,463,348 | 610,004 | 5.678 | 5.68 |
| deepseek_v4_pro_via_claude_code_superseded | 1,887,928 | 405,491 | 4.656 | 4.66 |
| deepseek_v4_pro_via_codex | 1,313,328 | 1,267,834 | 1.036 | 1.04 |

**No discrepancy found** — all five ratios in `history_analysis.md` are the
ratio of condition medians (not a median-of-paired-ratios), exactly as the
comparisons array's `estimate_unit` field states. `comparisons[].limitation`
correctly notes provider input-token totals include cached input with no
stage-level attribution; no per-call attribution or human-readability
measurement exists in this package, and `history_analysis.md` does not claim
either.

## 4. Per-condition/model/replicate route table

The 30-row route table in `history_analysis.md` Section 4 (columns: run,
runtime model ID, score field/value, answer, route indicators, Galaxy
analytical jobs/failed, nonzero shell calls) was checked row-by-row against
`history_analysis_evidence.json` fields `outcome.original_evaluator_score_field`,
`outcome.original_evaluator_score`, `outcome.submitted_answer`,
`derived_metrics.analytical_job_count`, `derived_metrics.total_failed_jobs`,
and `derived_metrics.nonzero_exit_shell_calls`.

**Result: every one of the 30 rows matched exactly**, including the two
score=0/answer=35 rows
(`open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1` and `_r3`),
the job/failed pairs for the 9 Galaxy runs with data (3/2, 2/1, 1/0, 1/0,
unavailable/unavailable, 5/3, unavailable x3, 2/1, unavailable, 1/0,
unavailable, 1/0, 2/1), and all "unavailable" markers for the 9 Galaxy runs
without job data and all 15 open_ended_code runs (which have no Galaxy-job
concept). No discrepancy was found; the table in `history_analysis.md` is
reproducible directly from the evidence JSON.

## 5. Input sharing, external computation, environment/reproducibility notes

- `input_manifest.json` shows most runs (26/30) sharing an identical
  `inputs_manifest.json` SHA-256 (`5f3bfdf1a19a...`, count 20 files), while 6
  runs (all three replicates each of `galaxy_deepseek_v4_pro_via_codex` and
  `galaxy_deepseek_v4_pro_via_claude_code_superseded`) share a second hash
  (`c1695013...`, count 0). The manifest explicitly states "Hashes are copied
  from original trace manifests; full staged inputs were not rehashed by this
  audit" and `all_trace_input_hashes_agree_by_name: true`. This audit did not
  independently re-hash any staged input file; it only confirms the manifest
  is internally consistent and self-declares its verification scope.
- `sources` in the evidence JSON (45 entries) record `tls_certificate_verified:
  false` for the sampled Galaxy and HuggingFace sources, and the top-level
  `audit.limitations` explicitly states retained-byte hashes therefore do not
  authenticate the remote server. This is a genuine reproducibility caveat
  already surfaced by the package, not a new finding.
- Redactions are recorded per source (e.g. local filesystem path patterns for
  trace sources, "account fields" for Galaxy sources) — consistent with the
  methodology's credential-redaction requirement.
- Galaxy computation vs. external computation vs. local shell computation is
  not separately re-derived by this audit beyond what
  `history_analysis.md` Section 3 states (execution-location fields exist per
  event but were not exhaustively tabulated here).

## 6. Verification methods

jq queries executed directly against `history_analysis_evidence.json`
(3.0 MB; never opened whole with the Read tool):
`.schema_version`; `.runs | length`; `.audit`; `.task`; `.experimental_design`;
`.manuscript_findings[] | {finding_id, section, question, numerator,
denominator, estimate, interpretation_status}`;
`.runs[] | {run_id, condition, model: .model.supplied_label, status}`;
`[.runs[].status] | group_by(.) | map({status: .[0], count: length})`;
`.runs[].outcome` (sampled on run 0 to discover field names, then
`.runs[] | .outcome.{original_evaluator_score_field, original_evaluator_score,
submitted_answer}` across all 30 runs); `.comparisons` (all entries, full
dump); `.runs[].derived_metrics` (sampled on run 0, then tabulated
`analytical_job_count`, `total_failed_jobs`, `nonzero_exit_shell_calls` across
all 30 runs); `.runs[0].solution_route`; `.runs[0].recovery_episodes`;
`.validation`; `.sources | length` and `.sources[0:2]`;
`.manuscript_findings[] | {finding_id, eligible_run_ids: length,
evidence_refs: length, limitations}`.

Directory inventory (`find -maxdepth 2/3/4`) covered `job_ledgers/galaxy`
(15 files), `job_ledgers/open_ended_code` (15 files), `recovered_code/galaxy`
(2 of 15 possible run subdirectories populated: `galaxy_codex_gpt_5_5_r1` and
`_r3`, containing 3 files total), `recovered_code/open_ended_code` (16 run
subdirectories, ~236 files), `selected_outputs/galaxy` (9 history-ID
subdirectories + manifest, matching the 9 Galaxy runs with retrieved job
data), `selected_outputs/open_ended_code` (manifest only, explicitly
`status: "not_collected"` with a stated reason — not a silent gap), and
`source_snapshots/{galaxy,huggingface_traces}` (10 Galaxy history snapshot
directories + retrieval manifest, plus HuggingFace trace files/manifests/
indexes for all 30 runs).

Two `recovered_code` files were opened and read directly to confirm they are
genuine recovered artifacts, not fabricated: `recovered_code/galaxy/
galaxy_codex_gpt_5_5_r1/bbd44e69cb8906b540a1554f03622432_job.py` (a Python
script parsing FASTA alignments from a zip archive and invoking
`phykit pis`) and `recovered_code/open_ended_code/
open_ended_code_codex_gpt_5_5_r1/item_1.command.txt` and `item_9.command.txt`
(shell commands reading a Galaxy skill file and listing zip contents). A
grep for embedded-instruction language ("ignore previous instructions",
"disregard", "system prompt") across `recovered_code/` returned no matches.

**Explicitly not checked in this audit**: byte-level re-hashing of any staged
input or output file; full transcript replay of any run; opening every file
in `recovered_code/` (236+ files in `open_ended_code` alone) or every
`job_ledgers` entry beyond the one sampled in full; the `history_analysis_evidence.schema.json`
file was not used to re-run schema validation (the evidence JSON's own
`.validation.schema.validation_status: "passed"` was taken as the reported
status, not independently re-verified); no Galaxy API call was made and no
hidden reference/answer-key file was opened.

## 7. Claim-to-evidence pointer list

| Claim | Source file/field |
|---|---|
| 30/30 runs have `trace_observed` status | `history_analysis_evidence.json:.runs[].status` |
| 30/30 runs have an original evaluator score (`accuracy.score`) | `history_analysis_evidence.json:.runs[].outcome.original_evaluator_score` |
| 28/30 runs scored 1.0; 2/30 scored 0.0 (both `open_ended_code_deepseek_v4_pro_via_claude_code_superseded` r1/r3) | `history_analysis_evidence.json:.runs[].outcome.{original_evaluator_score,submitted_answer}` |
| 18 distinct Galaxy analytical creating jobs; 8 failed | Sum of `history_analysis_evidence.json:.runs[].derived_metrics.{analytical_job_count,total_failed_jobs}` over the 9 runs with data; cross-checked against `.manuscript_findings[1]` (`finding_execution`) |
| 9 Galaxy runs have retrievable public-history job data; 9 do not | `history_analysis_evidence.json:.runs[].derived_metrics.analytical_job_count` (null vs. numeric) |
| Per-model score means/differences (0 pp x4, 66.7 pp x1) | `history_analysis_evidence.json:.comparisons[]` (`score_*` entries) |
| Per-model input-token median ratios (8.04, 19.3, 5.68, 4.66, 1.04) | `history_analysis_evidence.json:.comparisons[]` (`input_tokens_*` entries) |
| Route table (30 rows) in `history_analysis.md` Section 4 | `history_analysis_evidence.json:.runs[].{outcome,derived_metrics}` (row-by-row match confirmed) |
| Input hash groupings (26 runs one hash, 6 runs another) | `input_manifest.json:.runs[].sha256` |
| TLS not verified for retrieved sources; redactions applied | `history_analysis_evidence.json:.sources[].tls_certificate_verified`, `.redactions`; `.audit.limitations` |
| Recovered code/commands are genuine, task-relevant, non-fabricated (spot-check only) | `recovered_code/galaxy/galaxy_codex_gpt_5_5_r1/*.py`, `recovered_code/open_ended_code/open_ended_code_codex_gpt_5_5_r1/item_1.command.txt`, `item_9.command.txt` |
| No populated recovery episodes observed in sampled runs | `history_analysis_evidence.json:.runs[].recovery_episodes` (sampled) |

## 8. Missing evidence / open gaps for this task

- No independent experiment/protocol manifest exists to establish expected
  replicate counts, seeds, or stopping rules; coverage is labeled unknown by
  design.
- 9 of the 18 Galaxy runs have no retrievable public-history job/failure
  data (`"unavailable"` in the route table); the 18/8 job totals are drawn
  only from the other 9.
- `recovered_code/galaxy` contains code for only 2 of 15 Galaxy runs; the
  other 13 Galaxy runs have no recovered Galaxy-side script sampled or
  present in this subdirectory (job ledgers may still hold command text for
  some of these — not separately re-verified here).
- `selected_outputs/open_ended_code` contains no output artifacts by design
  (`status: "not_collected"`).
- `failed_jobs_before_first_supported_result` and
  `failed_attempts_before_first_correct_answer` are null for all sampled
  runs; no recovery-episode records were found populated in the runs sampled.
- No human-readability evaluation, per-call token attribution, or monetary
  cost data exists in this package.
- Byte-level re-hashing of large inputs/outputs and full transcript replay
  were not performed (out of scope per the retrospective-analysis mandate).

---

### Abstract-ready paragraph

For bixbench task bix-12-q5, this audit independently verified from
`history_analysis_evidence.json` that all 30 supplied workbook runs (5 model
labels x 2 conditions x 3 replicates) carry an observed original evaluator
`accuracy.score`: 28 of 30 runs scored 1.0 and 2 of 30 runs (both
`open_ended_code`, model `deepseek_v4_pro_via_claude_code_superseded`,
replicates 1 and 3) scored 0.0 with a submitted answer of 35 instead of 29.
Retrieved public Galaxy history records, available for 9 of the 18 Galaxy
condition runs, exposed 18 distinct analytical creating jobs of which 8 had a
failed/error status. Per-model input-token median ratios (Galaxy divided by
open-ended-code) ranged from 1.04 to 19.3 across the five models. All
per-run scores, job/failure counts, and token ratios in the existing
`history_analysis.md` were recomputed independently during this audit and
matched exactly; no discrepancy was found. These figures describe one
task's supplied links only and do not support a benchmark-wide or causal
Galaxy-versus-open-ended-code conclusion.
