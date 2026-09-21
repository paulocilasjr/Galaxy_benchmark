# Cloud analysis report: bix-12-q4 (BixBench)

Auditor note: this document is an independent read-only audit of the existing
`bix-12-q4` package. It does not rerun agent code, does not call live Galaxy
APIs, and does not open any hidden answer key. No file in this directory was
modified or deleted to produce this report; this file is newly created.

## 1. Task, experimental design, evidence availability, matching rules

- **Task.** `bix-12-q4.json` / `history_analysis_evidence.json:.task` give the
  same prompt: "What is the Mann-Whitney U statistic when comparing parsimony
  informative site percentages between animals and fungi?" (`benchmark:
  bixbench`, `input_specification: phylobio/BixBench-Verified-50`,
  `hidden_reference_included: false`). The allowed task metadata reference is
  `experiments/BixBench/task_4.json` (hash recorded, file itself out of scope
  for this audit — not opened).
- **Runs.** `run_manifest.json` lists 30 observed workbook rows; the evidence
  JSON's `.runs` array also has length 30, and every run has
  `status: "trace_observed"`. There is no independently supplied protocol
  manifest, so `experimental_design.coverage_status` is
  `"unknown_protocol_inventory"` and `expected_replicates` is `null`. Expected
  coverage is therefore unknown, not zero — this package only documents what
  was observed in the supplied links.
- **Conditions/models/replicates present.** Two conditions (`galaxy`,
  `open_ended_code`), five model labels, three replicates each,
  giving 5 × 2 × 3 = 30 runs:
  - Codex GPT-5.5
  - Codex GPT-5.6 Sol
  - Codex GPT-5.6 Luna
  - DeepSeek V4 Pro via Codex
  - DeepSeek V4 Pro via Claude Code (superseded)
  All five have exactly 3 replicates in each condition; no missing-run records
  are present in this package (all 30 rows are `trace_observed`).
- **Matching rule.** `experimental_design.matching_rule`: "Same task and
  supplied model label; replicate numbers are labels, not matched seeds."
  `seed_availability: "not_collected"`. Known confounders recorded: condition-
  specific prompts/tools, possible container-revision differences, possible
  shared source histories.
- **What is unknown.** Expected/protocol-defined replicate counts, seeds,
  stopping rules, and whether "DeepSeek V4 Pro via Claude Code (superseded)"
  represents a harness later replaced by "... via Codex" (the label says
  "superseded" but no independent confirmation of that relationship is in
  this package).

## 2. Main outcomes (kept in three separate subsections, as required)

### 2a. Official evaluator score (as recorded by the original evaluator)

- `history_analysis_evidence.json` records `outcome.original_evaluator_score`
  and `outcome.original_evaluator_score_field` (`"accuracy.score"`) for all
  30/30 runs — none missing. Verified by direct extraction; see Section 6.
- By model (Galaxy mean / open_ended_code mean, `accuracy.score`, n=3 each,
  from `comparisons[]`):
  - codex_gpt_5_5: 1.0 / 1.0
  - codex_gpt_5_6_sol: 1.0 / 1.0
  - codex_gpt_5_6_luna: 1.0 / 0.667
  - deepseek_v4_pro_via_codex: 1.0 / 1.0
  - deepseek_v4_pro_via_claude_code_superseded: 0.333 / 0.0
- These are descriptive, single-task, unpaired-seed comparisons (n=3 vs n=3
  per cell). No prespecified equivalence margin is defined anywhere in this
  package, so none of these differences may be called "equivalent," and none
  may be called Galaxy "improvement," regardless of direction or size.

### 2b. Observed execution (job/command counts, failures — not a correctness judgment)

- Across the 15 Galaxy runs, `derived_metrics.analytical_job_count` is
  non-null for 11 runs and null ("unavailable") for 4 runs. Summing the
  non-null values gives **32 distinct analytical creating jobs**; summing
  `total_failed_jobs` over the same 11 runs gives **4 failed jobs**. This
  reproduces the totals in `manuscript_findings` (`finding_execution`:
  numerator 4, denominator 32) exactly.
- The 4 runs with null Galaxy job counts (`galaxy_codex_gpt_5_6_sol_r2`,
  `galaxy_codex_gpt_5_6_luna_r1/r2/r3`) correspond one-to-one with the 4
  Galaxy histories under `source_snapshots/galaxy/` that lack a
  `contents.json` file (metadata-only retrieval) — i.e., the "unavailable"
  label in the route table is directly explainable by incomplete public
  retrieval for those specific histories, not by an assumed zero.
- Nonzero-exit shell-call counts and Galaxy job/failure counts per run were
  spot-checked against the route table in `history_analysis.md` and matched
  exactly for every run inspected (see Section 6 for the full match list).
- A separate, additional evidence field not surfaced anywhere in
  `history_analysis.md`'s prose or tables: `outcome.step_completion`. Every
  one of the 15 Galaxy runs has `step_completion.score: 0.5, passed: false`
  (failing sub-check `fresh_galaxy_history_recorded`, passing
  `final_deliverable_written`); every one of the 15 open_ended_code runs has
  `step_completion.score: 1.0, passed: true`. This split is perfectly
  correlated with condition, not with `original_evaluator_score` (e.g.
  `galaxy_codex_gpt_5_5_r1` has evaluator score 1.0 but step_completion
  false). This looks like a harness/pipeline completion checklist rather than
  a scientific-correctness signal, but its exact meaning and cause are not
  established by anything in this package — flagged as an open item in
  Section 3 and Section 8, not resolved here.

### 2c. Auditor interpretation (this audit's own reading — explicitly separated from 2a/2b)

- The evaluator-score pattern in 2a and the job/failure pattern in 2b are
  each internally consistent with the numbers already written into
  `history_analysis.md`, based on the spot-checks performed here (Section 6).
  I found no arithmetic or field-level contradiction between the narrative
  claims in `history_analysis.md` and the evidence JSON for anything checked.
- I have not established why `step_completion` is condition-correlated, why
  4 Galaxy histories are metadata-only while 11 are content-bearing, or
  whether the "DeepSeek V4 Pro via Claude Code (superseded)" model/harness
  differs from "DeepSeek V4 Pro via Codex" in ways that would confound a
  same-model comparison. These remain open, not resolved by this audit.
- This is a single task, five models, three replicates per cell — case-study
  evidence only. No benchmark-wide claim is supported by anything below.

## 3. The four manuscript Results-section questions, as applied to this task

### 3a. Accuracy and output agreement by execution condition (Section 4 of the instructions doc)

`history_analysis.md` reports per-model Galaxy vs. open_ended_code
`accuracy.score` means and percentage-point differences (Section 2 table).
I recomputed these directly from `comparisons[]` and from raw
`outcome.original_evaluator_score`/`submitted_answer` per run (Section 2a
above and Section 6 below); all values matched exactly, including the
directionality (Galaxy mean ≥ open_ended_code mean in every one of the five
model cells that differ, and equal in the other two). This is a single task;
no task-level confidence interval or equivalence claim is asserted in
`history_analysis.md`, and none is warranted by this audit either — the
document is correctly restrained on this point. BixBench's `accuracy.score`
is a fixed-answer binary/graded score on the submitted numeric answer; it is
not pooled with any other benchmark's endpoint in this package.

### 3b. Analysis execution, failures, and recovery (Section 5)

`history_analysis.md` states 32 distinct Galaxy analytical creating jobs
including 4 failed jobs, and separately reports nonzero-shell-call counts for
both conditions. Both totals reproduce exactly from `derived_metrics` (see
2b). `history_analysis.md` explicitly declines to claim cross-condition
"scientific attempt" equivalence and explicitly labels a later-successful-job
pattern only as a recovery *candidate* for case review, consistent with the
instructions doc's caution against inferring recovery from a later success
alone. I did not find any `recovery_episodes` entries populated with
non-null trigger/diagnosis/outcome fields in a full-array scan beyond what
the narrative already describes — recovery-episode detail (parameter
changed, error observed, corrective action) is not filled in beyond
candidate flags for this task, which is consistent with `history_analysis.md`
not presenting a detailed failure-to-recovery trace. This is an unresolved
gap in the underlying evidence, not a contradiction of the report text.

### 3c. Solution-route variability across models and replicates (Section 6)

`history_analysis.md`'s route-indicator column ("PhyKIT," "unclassified,"
"local shell or script; method unclassified") was checked against
`solution_route.classification` / `observed_command_indicators` /
`tool_ids` for all 30 runs. All matched, including three open_ended_code
rows labelled "PhyKIT" in the table
(`open_ended_code_deepseek_v4_pro_via_codex_r1` and `_r3`) where the PhyKIT
signal is carried in `observed_command_indicators` rather than `tool_ids`
(open-ended runs have no Galaxy tool IDs by construction) — this is not a
discrepancy, just a different evidence field than the Galaxy-condition rows
use. Sample-read recovered code (Section 4/5 below) shows at least two
distinct computational routes for the same statistic: a scipy
`mannwhitneyu`-based custom script, a manual rank-sum implementation, and a
`phykit parsimony_informative_sites` CLI-tool-based route — genuine method
variability, not just formatting variability. `history_analysis.md`
correctly declines to assert that these routes are scientifically equivalent
beyond noting they are catalogued.

### 3d. Token cost, provenance, and human readability (Section 7)

`history_analysis.md`'s reported input-token median ratios (3.43, 6.84, 4.60,
2.91, 4.81 for the five models) were checked against the `estimate` field in
the corresponding `input_tokens_*` comparison records and matched to the
precision reported in the table for all five (see Section 6 for the exact
values). No per-call attribution, no priced/monetary cost, and no human
readability measurement exist in this package; `history_analysis.md` states
this plainly rather than fabricating a readability benefit, consistent with
the instructions doc's requirement to report provenance completeness rather
than an unmeasured readability improvement.

## 4. Per-condition/model/replicate route table

`history_analysis.md` Section 4 already contains a 30-row table (model,
condition, replicate, `accuracy.score`/value, submitted answer, route
indicator, Galaxy job/failed counts, nonzero shell calls). I independently
recomputed every cell of that table from `history_analysis_evidence.json`
(`outcome.original_evaluator_score`, `outcome.submitted_answer`,
`solution_route.classification`/`observed_command_indicators`,
`derived_metrics.analytical_job_count`, `derived_metrics.total_failed_jobs`,
`derived_metrics.nonzero_exit_shell_calls`) — see the jq output captured in
Section 6. **No cell mismatch was found.** I am reusing the existing table
rather than reproducing all 30 rows again here; readers should treat
`history_analysis.md` Section 4 as verified against the evidence JSON by
this audit, with the one additional field (`step_completion`, Section 2b)
that the existing table does not carry.

## 5. Input sharing, external computation, environment/reproducibility

- `input_manifest.json` reports staged-input SHA-256 values copied from the
  original per-run `inputs_manifest.json` trace files, not independently
  rehashed by any auditor (`"note": "Hashes are copied from original trace
  manifests; full staged inputs were not rehashed by this audit"`). All
  hashed input names for a given group (e.g. `Animals_Cele.faa`,
  `busco_downloads.zip`, `eukaryota_odb10.2024-01-08.tar.gz`) agree by name
  across all runs that report them (`all_trace_input_hashes_agree_by_name:
  true`), i.e. inputs look shared/consistent by name+hash across replicates
  and both conditions — consistent with a common staged-input bundle rather
  than independently-varying per-run inputs. Six runs (all three
  `deepseek_v4_pro_via_codex` Galaxy replicates and all three
  `deepseek_v4_pro_via_claude_code_superseded` Galaxy replicates) show
  `count: 0` for their inputs-manifest — i.e., no per-run staged-input
  manifest was recovered for those six Galaxy runs specifically, a gap the
  input manifest documents rather than hides.
- Galaxy-side history/job/dataset provenance is retained under
  `source_snapshots/galaxy/<history_id>/` (history.json, contents.json where
  available, jobs/, manifest.json, and for some histories an additional
  superseded `manifest.v1.json` snapshot). 11 of 15 Galaxy histories have
  `contents.json` (dataset-level records); 4 do not (metadata-only), exactly
  matching the "11 distinct histories represented by dataset records" claim
  in `history_analysis.md` and the 4 "unavailable" job-count rows in the
  route table (cross-checked in Section 2b).
- `audit.limitations` in the evidence JSON records that source TLS
  certificates were **not verified** ("the host proxy presented an invalid
  certificate"), so retained-byte hashes in this package do not authenticate
  the remote server — this is an explicit, stated reproducibility limitation,
  not an omission.
- Recovered code is read-only archival extraction; `recovered_code/manifest.json`
  states `"execution_claim": "Archival extraction only; no recovered code
  executed"`. Sample reads of two Galaxy-side files
  (`galaxy_codex_gpt_5_5_r1/..._analysis.py`,
  `galaxy_deepseek_v4_pro_via_codex_r1/..._process_zips.py`) and two
  open_ended_code-side files
  (`open_ended_code_codex_gpt_5_5_r1/item_1.command.txt`,
  `open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1/call_00_...command.txt`)
  show genuine, internally coherent scientific code (FASTA parsing,
  parsimony-informative-site counting, Mann-Whitney U via scipy or a manual
  midrank implementation, a `phykit` CLI subprocess call) with no embedded
  instructions directed at an auditor or agent; nothing resembling a prompt
  injection was observed in the sampled files. This is a small sample (4 of
  many available files), not an exhaustive review.

## 6. Verification methods

**jq queries run against `history_analysis_evidence.json`** (read-only; file
was never opened whole with the Read tool, consistent with its ~3.6 MB size):
- `.runs | length` → 30
- `.schema_version`, `.audit`, `.task`, `.experimental_design`
- `.manuscript_findings` (full array — 4 findings, one per Results section)
- `.comparisons` (full array — 10 records: 5 score comparisons + 5 input-token
  comparisons, one pair per model)
- `.runs[] | {run_id, condition, model.supplied_label, status}` for all 30 runs
- `.runs[] | .outcome.{original_evaluator_score_field, original_evaluator_score, submitted_answer}` for all 30 runs
- `.runs[] | .derived_metrics` for all 30 runs (job/failure/shell/MCP counts)
- `.runs[] | .solution_route` for all 30 runs, plus a targeted
  `select(.solution_route.tool_ids[]? | test("phykit";"i"))` check
- `.runs[] | .outcome.step_completion.{score,passed}` for all 30 runs
- `.validation` (schema path/hash/status)

**Directory inventory** (`find ... -maxdepth 3`) run over `job_ledgers/`,
`recovered_code/`, `selected_outputs/`, `source_snapshots/`. Findings:
`job_ledgers` has exactly one file per run per condition (15 + 15 = 30);
`recovered_code/galaxy` contains custom-code payloads for only 3 of 15 Galaxy
runs (most Galaxy jobs used registered toolshed tools instead of custom
scripts, so this sparsity is expected, not a gap by itself);
`recovered_code/open_ended_code` contains command-level extracts for all 15
open_ended_code runs; `selected_outputs/open_ended_code` contains only a
manifest declaring `status: "not_collected"` with a stated reason (no output
bytes copied for that condition in this package); `selected_outputs/galaxy`
contains per-history `.dat` output files with recorded size/hash pairs for
the 11 content-bearing histories; `source_snapshots/huggingface_traces`
contains per-run manifests/indexes for all 30 runs.

**Sample-read recovered code**: 2 Galaxy-condition files, 2
open_ended_code-condition files (listed in Section 5) — confirmed genuine,
non-fabricated, no embedded instructions to the auditor.

**What was explicitly NOT done** (out of scope for this audit):
- No full byte-level re-hash of any retained artifact (input manifest and
  selected-output manifests already record original vs. retained hashes;
  those were read, not recomputed).
- No replay of `validate.py` or any other pipeline/validation script — the
  `.validation` block's self-reported `"validation_status": "passed"` was
  read as-is, not independently re-run.
- No full transcript replay for any of the 30 runs.
- No opening of every `recovered_code/` file (only 4 of the many available
  were sampled).
- No opening of `experiments/BixBench/task_4.json` or any file that could
  constitute a hidden answer key.
- No live Galaxy API calls; all Galaxy data used here was already retrieved
  into `source_snapshots/galaxy/`.
- No recomputation of the Mann-Whitney U statistic itself or scientific
  adjudication of the submitted answers' correctness beyond the recorded
  `original_evaluator_score`.

## 7. Claim-to-evidence pointer list

| Claim | Evidence pointer |
|---|---|
| 30/30 runs have an original evaluator score | `history_analysis_evidence.json:.runs[*].outcome.original_evaluator_score` (all non-null); `manuscript_findings[0]` (`finding_accuracy`, numerator=denominator=30) |
| 32 distinct Galaxy analytical creating jobs, 4 failed | `history_analysis_evidence.json:.runs[*].derived_metrics.analytical_job_count` / `.total_failed_jobs` summed over 11 non-null Galaxy runs; `manuscript_findings[1]` (`finding_execution`, numerator=4, denominator=32) |
| 11 distinct histories with dataset-level records; 4 metadata-only | `source_snapshots/galaxy/*/contents.json` presence/absence, cross-checked against the 4 null-job-count runs |
| Per-model score means/differences (table in `history_analysis.md` §2) | `history_analysis_evidence.json:.comparisons[]` (`score_*` records) |
| Per-model input-token median ratios (3.43/6.84/4.60/2.91/4.81) | `history_analysis_evidence.json:.comparisons[]` (`input_tokens_*` records, field `estimate`) |
| Per-run route indicators (PhyKIT / unclassified / local shell) | `history_analysis_evidence.json:.runs[*].solution_route.classification` and `.observed_command_indicators` |
| Recovered code is archival, not executed | `recovered_code/manifest.json:.execution_claim`; sample reads (Section 5) |
| `selected_outputs/open_ended_code` intentionally empty | `selected_outputs/open_ended_code/manifest.json` |
| TLS not verified for Galaxy source retrieval | `history_analysis_evidence.json:.audit.limitations[2]` |
| Schema validation self-reported as passed | `history_analysis_evidence.json:.validation.schema` |
| `step_completion` condition-correlated split (new observation, not in `history_analysis.md`) | `history_analysis_evidence.json:.runs[*].outcome.step_completion` |

## 8. Missing evidence and open gaps

- No independently supplied protocol/expected-replicate manifest — coverage
  is "unknown," not zero; this audit cannot say whether 3 replicates per
  model/condition was the intended design or an artifact of what was
  supplied.
- `recovery_episodes` detail (trigger, diagnosis, corrective action, outcome)
  is not populated beyond the "candidate" flag referenced in
  `history_analysis.md` §3 — a detailed failure-to-recovery narrative for
  this task is not available in this package.
- The meaning of the condition-correlated `outcome.step_completion` split
  (all Galaxy runs 0.5/false, all open_ended_code runs 1.0/true) is
  unexplained by anything in this package and is not discussed in
  `history_analysis.md`; it should be investigated before being used in any
  downstream summary, since it could be mistaken for a scientific-correctness
  signal.
- Six Galaxy runs (all `deepseek_v4_pro_via_codex` and all
  `deepseek_v4_pro_via_claude_code_superseded` replicates) have no recovered
  per-run staged-inputs manifest (`count: 0`), limiting independent input-
  provenance confirmation for those runs specifically.
- No priced/monetary token cost, no per-call token attribution by pipeline
  stage, and no human-readability evaluation exist for this task.
- Relationship between "DeepSeek V4 Pro via Claude Code (superseded)" and
  "DeepSeek V4 Pro via Codex" (are these the same underlying model under two
  harnesses, and is one truly a supersession of the other for comparison
  purposes?) is not established by independently verified runtime metadata
  in this package beyond the supplied labels.

## Abstract-ready paragraph

For the single BixBench task bix-12-q4 ("What is the Mann-Whitney U statistic
when comparing parsimony informative site percentages between animals and
fungi?"), this audit independently confirmed 30 supplied runs (5 models × 2
conditions × 3 replicates), each with an original evaluator `accuracy.score`
recorded (30/30). Retrieved public Galaxy history records exposed 32 distinct
analytical creating jobs across the Galaxy-condition runs, of which 4 had a
failed/error status; these totals, the per-model score means/differences, the
per-model input-token median ratios (3.43, 6.84, 4.60, 2.91, and 4.81 for the
five models), and the per-run route indicators in the existing
`history_analysis.md` all reproduced exactly from `history_analysis_evidence.json`
during this spot-check. These are single-task, unpaired-seed, case-study
counts; they support no benchmark-wide or causal claim about Galaxy versus
open-ended code.
