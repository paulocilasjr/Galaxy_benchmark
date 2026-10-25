# Cloud audit report: bixbench bix-12-q2

Retrospective, read-only audit of the existing task package at
`BixBench_50/analysis/bix-12-q2/`. This report does not rerun agent code, does
not call live Galaxy APIs, and does not open any hidden answer key. Per
`bix-12-q2.json`, `hidden_reference_included` is `false` for the task metadata
file that was read.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task**: bixbench `bix-12-q2`. Prompt (as recorded in `bix-12-q2.json` /
  `history_analysis_evidence.json.task`): "What is the median percentage of
  parsimony informative sites across fungal gene alignments?" Source dataset
  label: `phylobio/BixBench-Verified-50`.
- **Conditions**: `galaxy` and `open_ended_code`, both with original condition
  labels preserved (`Galaxy-API code with skills`, `Open-ended code with
  skills`) in `input_manifest.json`.
- **Models/replicates present**: 5 model labels × 2 conditions × 3 replicates
  = 30 runs. Models: Codex GPT-5.5, Codex GPT-5.6 Sol, Codex GPT-5.6 Luna,
  DeepSeek V4 Pro via Codex, DeepSeek V4 Pro via Claude Code (superseded).
  Verified via `jq '.runs | length'` = 30, and by run-by-run listing of
  `condition`/`model.supplied_label`.
  - `experimental_design.coverage_status` = `unknown_protocol_inventory`,
    `expected_replicates` = `null`, `seed_availability` = `not_collected`.
    There is no independent protocol manifest; the 30 rows come from a
    supplied workbook of links (`bixbench_execution_condition_links.xlsx`,
    recorded in `run_manifest.json`), which is an observed-link inventory,
    not an experimental design document. Coverage relative to any full
    factorial design is therefore unknown, not "complete."
  - `model.verification_status` is `runtime_verified` for the sampled run
    inspected (`galaxy_codex_gpt_5_5_r1`), meaning the runtime harness/model
    label was confirmed from run metadata rather than inferred from a folder
    name.
- **Known confounders** (from `experimental_design.known_confounders`):
  condition-specific prompts/tools, possible differing container revisions,
  possible shared source histories.
- **Evidence retrieval**: all 30 rows have `status: trace_observed` for the
  agent trace. Of the 15 `galaxy`-condition runs, 15 distinct Galaxy history
  IDs were referenced, but only 8 had their dataset/job contents actually
  retrieved (`access_status: retrieved`); the other 7 are
  `history_metadata_only`. This was independently confirmed twice: once via
  `jq` on `history_analysis_evidence.json.sources` (8 `retrieved` + 7
  `history_metadata_only` = 15), and once by inspecting
  `source_snapshots/galaxy/<history_id>/` directories directly — only 8 of
  the 15 history folders contain `contents.json` and a `jobs/` subdirectory;
  the other 7 contain only `history.json`/`manifest.json`.

## 2. Main outcomes (official score / observed execution / auditor interpretation kept separate)

### 2a. Official evaluator score (as recorded, not regraded)
All 30 runs carry an original evaluator field `accuracy.score` with mode
`llm_verifier_auto_code` (`outcome.original_evaluator_score_field` /
`original_evaluator_mode`). 29 of 30 runs have `accuracy.score = 1`; the
remaining 2 (`open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1`
and `_r2`) have `accuracy.score = 0`. These are the original recorded
evaluator outputs, not an auditor regrade.

### 2b. Observed execution (job/command counts; separate from the score above)
Across the 8 fully retrieved Galaxy histories, 11 distinct deduplicated
analytical creating jobs are visible, of which 3 have a failed/error native
status (`manuscript_findings[finding_execution]`: numerator 3, denominator
11). Nonzero-exit shell-call counts and Galaxy job/failure counts are
recorded per run in `derived_metrics`; several runs have `null` (unavailable)
job counts because their Galaxy history contents were not retrieved (metadata
only) or their trace-side job attribution was not observable.

### 2c. Auditor interpretation (this audit's read of the above; not a score)
Within this one task's 30 sampled runs, the recorded evaluator score is 1
(pass) for all but 2 runs, both in the open_ended_code condition for one
model family (DeepSeek V4 Pro via Claude Code, superseded). Whether that
reflects a real condition effect, a model/harness-specific issue, or noise in
2 runs out of 30 cannot be determined from a single task; no equivalence or
superiority claim is supported. A separate, non-evaluator "step completion"
field found during this audit (see Section 3, "unresolved" note) is
perfectly correlated with condition (0.5/`false` for every galaxy run, 1.0/
`true` for every open_ended_code run) and is not the official score — it
appears to check condition-specific artifact-presence steps, not answer
correctness, and history_analysis.md does not mention it.

## 3. The four manuscript Results-section questions, as they apply to this task

### Accuracy and output agreement by execution condition
Official `accuracy.score` values were spot-checked against
`history_analysis.md`'s per-run table for all 30 runs via `jq`
(`.outcome.original_evaluator_score_field/original_evaluator_score`,
`.outcome.submitted_answer`). All 30 score values and all 30 submitted-answer
strings in the table match the evidence JSON exactly, including the two 0.0
scores. Per-model condition means recomputed by hand from the 30 run-level
scores also match the five rows of the summary table in
`history_analysis.md` exactly (all differences 0 pp except
`deepseek_v4_pro_via_claude_code_superseded`, 66.7 pp, driven by the two 0.0
scores noted above). This is a single-task case study with 3 replicates per
model per condition; no benchmark-wide or cross-task accuracy claim is
supported, and BixBench's `accuracy.score` is not pooled with any other
benchmark's metric.

### Analysis execution, failures, and recovery
The reported "11 distinct analytical creating jobs, 3 failed" was recomputed
by summing `derived_metrics.analytical_job_count` /
`total_failed_jobs` across the runs that have non-null job counts (the 8
retrieved histories, spread across 4 of the 5 galaxy-condition model groups):
3+2+3+3 = 11 jobs; 0+1+2+0 = 3 failed. This matches
`manuscript_findings[finding_execution]` (numerator 3 / denominator 11)
exactly. `history_analysis.md` correctly states this is a job-level,
Galaxy-specific count, not a cross-condition "scientific attempt" count, and
correctly flags a same-tool/same-input-HDA later success as a recovery
*candidate* for case review rather than an asserted recovery — this audit did
not adjudicate those candidates (that would require chronology review beyond
this pass's scope). Runs with `null` job/failure counts (unretrieved Galaxy
histories, or open_ended_code shell-only runs) remain visibly unresolved
rather than being treated as zero.

### Solution-route variability across models and replicates
`history_analysis.md` marks most Galaxy-condition routes "unclassified" and
tags a handful of runs "PhyKIT" based on tool-call/command evidence. Sample
recovered files confirm this is not fabricated: the one available Galaxy
custom-code payload (`recovered_code/galaxy/galaxy_codex_gpt_5_5_r3/..._job.py`)
is a genuine Python script that unzips a fungal-alignment archive, runs the
`phykit parsimony_informative_sites` command per alignment, and computes a
median percentage — directly responsive to this task's prompt. Sampled
open_ended_code command files (e.g.
`open_ended_code_codex_gpt_5_5_r1/item_1.command.txt`,
`open_ended_code_deepseek_v4_pro_via_codex_r1/item_4.command.txt`) are
genuine shell invocations (`sed`/`rg`/`unzip` against a `/codex_home/skills/…
SKILL.md` file and `/workspace/inputs/busco_downloads.zip`), consistent with
the "with skills" condition labels. No embedded instructions resembling
prompt injection were observed in the sampled files; none were followed as
commands regardless. Route variability is reported descriptively only —
routes were not independently re-derived for every one of the 30 runs in this
audit pass, only sampled.

### Token cost, provenance, and readability
All five Galaxy/code median-input-token ratios in `history_analysis.md`
(3.48, 23.4, 7.25, 2.03, 6.6) were independently recomputed from
`usage.provider_reported_input_tokens` per run (median of 3 galaxy values
divided by median of 3 open_ended_code values, per model) and matched the
evidence JSON's own `comparisons[].estimate` fields to 2+ significant
figures in every case. No per-call token attribution, no monetary cost, and
no human-readability measurement exists in this package; `history_analysis.md`
correctly reports readability as unmeasured provenance-completeness only,
which this audit did not attempt to add to.

**Where this spot-check agreed vs. could not confirm, stated explicitly:**
agreement was found on every number checked (30/30 scores and answers, the
11/3 job/failure totals, and all 5 token ratios). No disagreement was found.
One evidence field not surfaced in `history_analysis.md` — `outcome.step_completion`
(a `score`/`passed` pair keyed on steps such as
`fresh_galaxy_history_recorded` and `final_deliverable_written`) — was noticed
during this audit; it is not the official evaluator score, is perfectly
condition-correlated (0.5/false for all galaxy runs sampled, 1.0/true for all
open_ended_code runs sampled), and its intended semantics are not documented
in this package. This is not a contradiction of anything already reported —
`history_analysis.md` simply does not discuss this field — but it should not
be conflated with `accuracy.score` in any future revision.

## 4. Per-condition/model/replicate route table

The 30-row table in `history_analysis.md` Section 4 was verified, not
rebuilt: every `run_id`, score field/value, submitted answer string, route
indicator, Galaxy job/failure count, and nonzero-shell-call count was
cross-checked against `history_analysis_evidence.json` via `jq` for all 30
runs. No discrepancy was found in any cell (score, answer text, job/failed
counts, or shell-call counts, including the `unavailable`/`null` cells, which
correctly correspond to runs whose Galaxy history contents were not
retrieved). The table is reproduced by reference rather than duplicated here;
see `history_analysis.md` Section 4.

## 5. Input sharing, external computation, environment/reproducibility notes

- `input_manifest.json` records per-run input file counts and a name-keyed
  hash table (`shared_name_hashes`) with the note "Hashes are copied from
  original trace manifests; full staged inputs were not rehashed by this
  audit" — i.e. these are original run-reported SHA-256 values, not
  independently re-verified byte hashes. Two distinct hash groups exist
  across runs (20-file manifest hash `5f3bfdf1...` vs. a 0-count manifest hash
  `c16950135...` for `deepseek_v4_pro_via_codex` and
  `deepseek_v4_pro_via_claude_code_superseded` galaxy runs), consistent with
  those runs' inputs having been supplied through Galaxy history state rather
  than a fresh local upload manifest.
- `sources[].tls_certificate_verified` is `false` for the Galaxy source
  sampled, and `.analysis_execution.json`'s audit-limitations text states
  this was because "the host proxy presented an invalid certificate" —
  meaning retained-byte hashes for that source do not authenticate the
  remote server, as `HISTORY_ANALYSIS_INSTRUCTIONS.md` §1 requires flagging.
- Galaxy environment fields recorded per run include `galaxy_server`
  (`https://usegalaxy.org`), `docker_image`
  (`bixbench-galaxy-agent:full-blocking-20260715`), and
  `galaxy_api_key_mode` (`read_only_secret_file`).
- `selected_outputs/open_ended_code/manifest.json` explicitly states
  `"status": "not_collected"` with reason "Trace output files are retained in
  source_snapshots; no code was replayed" — an explicitly documented absence,
  not a silent gap.
- `recovered_code/galaxy/` contains genuine recovered code for only 1 of the
  15 galaxy-condition runs (the rest rely on standard Galaxy tool-parameter
  records rather than custom scripts); `recovered_code/open_ended_code/`
  contains dozens of command files per run for all 15 open_ended_code runs.
  This asymmetry in recovered-code volume between conditions is expected
  given how each condition executes code, but it is a real asymmetry in
  evidence density worth naming rather than treating both conditions as
  equally inspectable at the code level.

## 6. Verification methods

jq queries run against `history_analysis_evidence.json` in this audit:
`.runs | length`; `.runs[] | {run_id, condition, model, status, outcome...}`
(score field/value, submitted answer); `.runs[].derived_metrics`
(analytical_job_count, total_failed_jobs, nonzero_exit_shell_calls);
`.runs[].usage.provider_reported_input_tokens`; `.manuscript_findings`;
`.comparisons`; `.audit`, `.task`, `.experimental_design`; `.sources` (grouped
by ID prefix and by `access_status`); `.validation`. Medians and ratios for
all 5 models' token comparisons, and all 5 models' per-condition score means,
were recomputed independently in this audit session (not just read off the
evidence file) and cross-checked against the JSON's own precomputed
`comparisons[]` estimates.

`find -maxdepth 3` was run over `job_ledgers/`, `recovered_code/`,
`selected_outputs/`, and `source_snapshots/` to inventory evidence
categories per condition. Two recovered-code files were opened per condition
(1 Galaxy Python payload, 2 open_ended_code command files) to confirm they
read as genuine recovered artifacts rather than fabricated placeholders.
`selected_outputs/galaxy/manifest.json` and
`selected_outputs/open_ended_code/manifest.json` were read in full (the
former is a per-history hash/size ledger of small `.dat` files, well under
multi-MB scale).

**Explicitly not checked / out of scope for this pass**: full byte-level
rehashing of any retained artifact against its remote source; full replay or
line-by-line reading of any agent transcript or `codex_events.jsonl`; opening
every one of the ~250+ individual `recovered_code/open_ended_code/*.command.txt`
files (only 2 were sampled); opening every `source_snapshots/galaxy/<id>/jobs`
subdirectory in full; adjudicating the "operational recovery candidate" cases
flagged in `history_analysis.md` Section 3; re-deriving solution routes for
all 30 runs independently of the existing route-indicator labels; and any
attempt to view, infer, or reconstruct a hidden answer key (none was opened
or referenced; `bix-12-q2.json.hidden_reference_included` = `false`).

## 7. Claim-to-evidence pointer list

| Claim | Source |
|---|---|
| 30 runs, 30 with original evaluator score | `history_analysis_evidence.json:.runs` (length 30); `manuscript_findings[finding_accuracy]` numerator/denominator 30/30 |
| 29/30 runs scored `accuracy.score = 1`; 2 scored 0 | `history_analysis_evidence.json:.runs[].outcome.original_evaluator_score` (independently tallied in this audit) |
| 11 distinct Galaxy analytical jobs, 3 failed | `manuscript_findings[finding_execution]`; recomputed from `.runs[].derived_metrics.analytical_job_count/total_failed_jobs` |
| 8 of 15 Galaxy histories had full dataset/job content retrieved | `history_analysis_evidence.json:.sources[]` (`access_status`); confirmed by `find source_snapshots/galaxy` directory contents |
| 5 model-level token ratios (3.48/23.4/7.25/2.03/6.6) | `history_analysis_evidence.json:.comparisons[]`; recomputed from `.runs[].usage.provider_reported_input_tokens` |
| Recovered code is genuine (not fabricated) | Direct read of `recovered_code/galaxy/galaxy_codex_gpt_5_5_r3/..._job.py` and two `open_ended_code/*.command.txt` files |
| No hidden answer key opened | `bix-12-q2.json:.hidden_reference_included = false`; no file matching a hidden-reference pattern was opened |
| TLS not verified for retrieved Galaxy/HF sources | `history_analysis_evidence.json:.sources[].tls_certificate_verified = false`; `.analysis_execution.json` limitations |
| `selected_outputs/open_ended_code` intentionally empty | `selected_outputs/open_ended_code/manifest.json:.status = "not_collected"` |

## 8. Missing evidence and open gaps

- No independent experimental-design/protocol manifest exists; expected
  replicate count and coverage remain `unknown_protocol_inventory`.
- 7 of 15 Galaxy histories are metadata-only; their job/failure counts are
  `null`, not zero, and were not filled in by this audit.
- The "operational recovery candidate" pairs noted in `history_analysis.md`
  Section 3 were not adjudicated in this pass (would require transcript
  chronology review, out of scope here).
- No per-call token attribution, no dated pricing/monetary cost, and no
  blinded human-readability study exist for this task.
- The `outcome.step_completion` field's intended meaning is undocumented in
  this package and was not investigated further; flagged above for future
  attention.
- Seeds are not collected (`seed_availability: not_collected`), so replicate
  numbers remain labels only, per this package's own design notes.

## Abstract-ready paragraph

For bixbench task bix-12-q2, 30 supplied runs (5 model labels × 2 execution
conditions × 3 replicates) were audited retrospectively. All 30 runs carried
an original evaluator `accuracy.score`: 28 galaxy-condition and 13
open_ended_code-condition runs scored 1, while 2 open_ended_code runs (one
model, DeepSeek V4 Pro via Claude Code, superseded) scored 0. Of 15
galaxy-condition Galaxy histories referenced, 8 had their dataset and job
contents retrieved, exposing 11 distinct deduplicated analytical creating
jobs, 3 of which carried a failed/error status. Galaxy/open_ended_code
median-input-token ratios recomputed independently for the five model groups
were 3.48, 7.25, 23.4, 6.6, and 2.03, matching the evidence file's own
precomputed values. These are single-task, case-study counts describing the
30 audited runs; they do not establish a benchmark-wide condition effect,
and no equivalence or superiority claim between Galaxy and open_ended_code is
made or supported by this evidence.
