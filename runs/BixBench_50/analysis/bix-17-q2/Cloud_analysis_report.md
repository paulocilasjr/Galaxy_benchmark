# bix-17-q2: independent audit-of-audit report

Auditor role: this document is a second-pass, read-only review of the existing
`history_analysis.md` / `history_analysis_evidence.json` package for one BixBench
task. It does not rerun agent code, call live Galaxy APIs, open hidden references,
or replay transcripts. All counts below were recomputed from the files present in
this directory using `jq`, `find`, and direct file reads; none were copied from
prose without independent recalculation.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task**: `bix-17-q2.json` gives the prompt: "Among patients classified as BLM
  mutation carriers, what is the median number of somatic CHIP variants — defined
  as variants with a Variant Allele Frequency (VAF) < 0.3? Prior to analysis,
  exclude all variants that are Intronic, Intergenic, in UTR regions, or have
  Reference zygosity." `hidden_reference_included: false`; the allowed task
  metadata reference is `experiments/BixBench/task_11.json` with a recorded
  SHA-256. This matches `task.prompt` and `task.prompt_version` in
  `history_analysis_evidence.json` exactly (both files agree; verified by direct
  comparison).
- **Runs**: `run_manifest.json` lists **30 observed rows** (`observed_rows`
  array, one entry per run) drawn from an external workbook
  (`/Users/4475918/Downloads/bixbench_execution_condition_links.xlsx`). This
  equals `jq '.runs | length' history_analysis_evidence.json` = **30**. Both
  agree.
- **Conditions and models**: two condition labels are preserved — `galaxy`
  ("Galaxy-API code with skills") and `open_ended_code` ("Open-ended code with
  skills") — each with 5 model labels × 3 replicates = 15 runs per condition,
  30 total: `codex_gpt_5_5`, `codex_gpt_5_6_sol`, `codex_gpt_5_6_luna`,
  `deepseek_v4_pro_via_codex`, `deepseek_v4_pro_via_claude_code_superseded`.
  `experimental_design.coverage_status` is explicitly
  `"unknown_protocol_inventory"` and `expected_replicates: null` — the
  workbook is an observed-link inventory, not an independent protocol
  manifest, so expected coverage is correctly left unknown rather than assumed
  to be complete. `experimental_design.seed_availability` is
  `"not_collected"`; replicate numbers are documented as labels, not matched
  seeds.
- **Known confounders** recorded in `experimental_design.known_confounders`:
  condition-specific prompts/tools, possible container-revision differences,
  and possible shared source histories.
- **Evidence completeness**: `jq -r '.runs[].evidence_completeness.public_history_contents'`
  across all 30 runs gives 15 `not_applicable` (the 15 open-ended-code runs, for
  which Galaxy history contents do not apply), 14 `retrieved`, and 1
  `history_metadata_only`. The one incomplete case is
  `galaxy_deepseek_v4_pro_via_codex_r1`: its Galaxy history
  (`bbd44e69cb8906b582fa225952de0f26`) has no corresponding directory under
  `selected_outputs/galaxy/` or `source_snapshots/galaxy/` (confirmed by listing
  both directories — 14 history-ID directories are present, not 15), consistent
  with the evidence JSON's `history_metadata_only` flag for that run. This
  matches history_analysis.md's statement of "14 distinct histories represented
  by dataset records" out of 15 galaxy run rows.

## 2. Main outcomes

### 2a. Official evaluator score (as recorded, not reinterpreted)
- `jq -r '.runs[].outcome.original_evaluator_score'` returns **30/30 values of
  1.0**, field name `accuracy.score`, mode `str_verifier_auto_numeric`, for
  every run in both conditions.
- `jq -r '.runs[].outcome.submitted_answer'` returns the literal string `"2"`
  for all 30 runs.
- This is a single fixed-answer, binary-style numeric field per BixBench
  convention; it is not pooled with any other benchmark's metric in this
  report.

### 2b. Observed execution facts (counts, not scored)
- Retrieved public Galaxy histories expose **248 distinct analytical creating
  jobs** across the 15 galaxy-condition runs, with **21** carrying a
  failed/error status. Both numbers were independently recomputed in this
  audit directly from `job_ledgers/galaxy/*.json` (summing
  `event_type=="analysis"` + `execution_location=="galaxy_job"` events, one
  event per native job) and matched exactly: 248 total, 21 failed, with no
  double counting by native job ID.
- Per-run job/failure counts recomputed the same way match the
  `history_analysis.md` route table row-for-row for all 15 galaxy runs
  (e.g., `galaxy_codex_gpt_5_6_luna_r2` = 79/4; `galaxy_deepseek_v4_pro_via_codex_r2`
  = 29/0; `galaxy_deepseek_v4_pro_via_claude_code_superseded_r2` = 44/0).
- "Nonzero shell calls" per run (recomputed as shell-tool events with a
  non-null, non-zero exit code) match the `history_analysis.md` table for
  **all 30 rows** with no discrepancies.
- **Notable observed fact not surfaced in `history_analysis.md`**: every one
  of the 15 galaxy-condition runs carries an
  `outcome.step_completion` record with `score: 0.5`, `passed: false`, and the
  single failing sub-step `fresh_galaxy_history_recorded`. Every one of the 15
  open-ended-code runs carries `step_completion.score: 1.0`, `passed: true`,
  with no failing sub-steps. This field is distinct from
  `original_evaluator_score` (`accuracy.score`, 1.0 for all 30 runs) and is
  not mentioned anywhere in the current `history_analysis.md`. The evidence
  JSON does not define what originally produced this step-completion record
  or what "fresh_galaxy_history_recorded" checks operationally (e.g., whether
  it verifies a newly created vs. reused/copied Galaxy history for that run).
  This audit reports the value as observed; it draws no conclusion about
  cause.

### 2c. Auditor interpretation (bounded)
- Within this single task, the fixed-answer evaluator score is uniform (1.0)
  across both conditions and all five model configurations — a case-study
  observation, not a benchmark-wide accuracy claim, and not evidence of
  "equivalence" under the instructions' defined evidence standard (no
  prespecified margin was set).
- The uniform `fresh_galaxy_history_recorded: false` pattern across all 15
  galaxy runs, next to a uniform `passed: true` across all 15 open-ended
  runs, is consistent with a structural difference in how each condition's
  runs were checked or executed, but the audit cannot determine, from the
  evidence retained, whether this reflects a genuine history-reuse pattern in
  the underlying Galaxy runs, an artifact of the step-completion checker
  itself, or an unrelated scoring-harness quirk. This is flagged as an open
  question in Section 8, not resolved here.
- A byte-level cross-check found that the retained Galaxy output artifact
  `f9cad7b01a4721351562028b63085cc7.dat` in history
  `bbd44e69cb8906b519a476f3040e85cf` (`selected_outputs/galaxy/.../manifest.json`)
  has `retained_sha256` = `53c234e5e8472b6ac51c1ae1cab3fe06fad053beb8ebfd8977b010655bfdd3c3`,
  identical to `outcome.submitted_answer_sha256` recorded for
  `galaxy_codex_gpt_5_5_r1`. This supports (does not itself prove, since equal
  hashes only confirm byte identity, not causal authorship) that the
  submitted answer for that run corresponds to a byte-identical artifact
  retained from that run's Galaxy history.

## 3. Walkthrough of the four manuscript Results questions

### Accuracy and output agreement (Section 4)
`history_analysis.md` states the score field/value is preserved per run and
that BixBench's `accuracy.score` evaluates a fixed submitted answer. Verified:
all 30 `outcome.original_evaluator_score` values are 1.0, all 30
`outcome.submitted_answer` values are the string "2". The per-model comparison
table (0 percentage-point Galaxy-minus-code difference for all five model
groups) was recomputed directly from `comparisons[]` in the evidence JSON and
matches `history_analysis.md`'s table exactly (galaxy_mean = code_mean = 1.0
for all five `score_*` comparison records). **No disagreement found.** This
audit adds, as new context not previously reported, the `step_completion`
step-level field described in 2b/2c above, which is a separate, non-accuracy
compliance signal.

### Execution, failures, and recovery (Section 5)
`history_analysis.md` states 248 distinct analytical creating jobs and 21
failed jobs, both independently recomputed above and confirmed exact. The
per-run breakdown in the route table (job/failed counts, nonzero shell calls)
was independently recomputed from `job_ledgers/galaxy/*.json` and
`job_ledgers/open_ended_code/*.json` for **all 30 runs** and matched with **no
discrepancies**. "Galaxy only" is not asserted anywhere in the reviewed
document, consistent with the instructions' requirement that the term only be
used under its defined evidence standard; this audit likewise does not assert
it. `history_analysis.md` correctly marks Galaxy analytical job/failure counts
"unavailable" (not "0") for `galaxy_deepseek_v4_pro_via_codex_r1`; this audit
confirmed that run's `evidence_completeness.public_history_contents` is
`history_metadata_only` (not `retrieved`), so "unavailable" is the correct
label and a naive zero-count from an empty job-ledger events array would have
been a mislabeling. No recovery-episode array content was independently
re-derived beyond confirming its presence; `recovery_episodes` fields exist
per run but were not exhaustively cross-tabulated in this pass (see Section 6).

### Solution-route variability (Section 6)
`history_analysis.md`'s route table marks most galaxy runs "unclassified" and
identifies two runs using "Datamash" and one using "Summary Statistics" as
named tool indicators; all `open_ended_code` runs are marked "local shell or
script; method unclassified." This audit did not re-derive a route codebook
independently (out of scope for this pass — see Section 6/methods below) but
confirms via `recovered_code/manifest.json` and sampled files
(`recovered_code/galaxy/galaxy_codex_gpt_5_5_r2/..._analysis.py`,
`recovered_code/open_ended_code/open_ended_code_codex_gpt_5_5_r1/item_1.command.txt`)
that recovered artifacts genuinely look like archival copies of executable
analysis code and shell commands, not placeholders. **No disagreement found**
with the variability claims made, but they remain largely "unclassified" by
the existing report's own admission, and this audit did not independently
resolve that gap.

### Token cost, provenance, and readability (Section 7)
All five `input_tokens_*` comparison records in `comparisons[]` were
recomputed and matched `history_analysis.md`'s reported ratios exactly:
codex_gpt_5_5 = 3.4716789779930157 (reported "3.47"), codex_gpt_5_6_luna =
13.436728424822647 ("13.4"), codex_gpt_5_6_sol = 8.948440704768185 ("8.95"),
deepseek_v4_pro_via_claude_code_superseded = 5.081429323729764 ("5.08"),
deepseek_v4_pro_via_codex = 10.076204842924597 ("10.1"). **No disagreement
found.** Each ratio is explicitly the ratio of condition medians (not the
median of paired ratios), as required by the instructions; the `usage` block
per run documents cached-input and reasoning-token subset relationships and
does not sum them separately. No per-call attribution or human-readability
measurement is present in either document; both correctly describe this as
unmeasured rather than inferred.

## 4. Per-condition/model/replicate route table

The 30-row table in `history_analysis.md` (Section 4 of that document) was
spot-checked cell-by-cell for job/failure counts and nonzero-shell-call counts
against `job_ledgers/{galaxy,open_ended_code}/*.json`, and for score/answer
values against `history_analysis_evidence.json` `.runs[].outcome`. All 30 rows
matched with **no numeric discrepancies**. That table is reused here by
reference rather than reproduced, per the task instructions, since verification
found it accurate:

- Score field/value: `accuracy.score` / 1 for all 30 rows — confirmed.
- Answer: "2" for all 30 rows — confirmed.
- Galaxy analytical jobs/failed and nonzero shell calls — confirmed per row
  for all 30 rows (see Section 3, "Execution" above for aggregate figures).
- Route indicators ("unclassified", "Datamash", "Summary Statistics", "local
  shell or script; method unclassified") were not independently re-derived
  under a formal codebook in this pass; they are reused as originally
  reported.

## 5. Input sharing, external computation, environment, and reproducibility

- `input_manifest.json` shows 26 of the 30 runs sharing an identical
  `inputs_manifest.json` SHA-256 (`28748437b5bba7f4d1455454439fd47401e320d3fc21c1b5436b26af2724847e`,
  count 88 inputs each), while the 3 `galaxy_deepseek_v4_pro_via_codex` runs
  and the 3 `galaxy_deepseek_v4_pro_via_claude_code_superseded` runs each
  record a different shared hash
  (`c16950135b08147b2d283b8ea8ef785b8af3a51669374f769fecaa07aaaa81bf`, count 0).
  This 0-count/alternate-hash pattern is documented in the file itself (it is
  not a fabricated null) and is consistent with those six galaxy runs using a
  different (or no locally staged) input-manifest recording path than the
  other 24 runs; `history_analysis.md` does not call this out explicitly, but
  it does not contradict anything stated there either, since that document
  only asserts "input names and reported SHA-256 values are compared," which
  remains true.
- `input_manifest.json` explicitly states: "Hashes are copied from original
  trace manifests; full staged inputs were not rehashed by this audit" and
  `"all_trace_input_hashes_agree_by_name": true` — this audit did not
  independently rehash the 88 named `.xlsx` input files either; it is
  reusing the same non-rehashed provenance chain.
- Galaxy environment metadata recorded per run (`runs[].environment`)
  includes `galaxy_server: https://usegalaxy.org`, a docker image tag
  (`bixbench-galaxy-agent:no-static-udt-resolver-20260714`), and
  `galaxy_api_key_mode: read_only_secret_file` — consistent with a read-only
  credential-gated retrieval process, matching the README's claim that "This
  pipeline did not execute agent code, submit Galaxy jobs, or open hidden
  references."
- `audit.limitations` in the evidence JSON explicitly states TLS certificates
  were not verified for retrieved sources because "the host proxy presented
  an invalid certificate," so retained-byte hashes do not authenticate the
  remote server. This is a real, disclosed reproducibility limitation, not an
  omission.

## 6. Verification methods (what was and was not checked)

**Checked in this audit pass:**
- `jq '.runs | length'`, `.audit`, `.task`, `.experimental_design`,
  `.comparisons`, `.manuscript_findings`, and targeted `.runs[]` /
  `.outcome` / `.evidence_completeness` / `.environment` / `.usage` queries
  against `history_analysis_evidence.json`.
- Independent recomputation of distinct Galaxy job counts and failed-job
  counts directly from `job_ledgers/galaxy/*.json` (15 files), aggregated and
  per-run, and cross-checked against both `history_analysis.md`'s table and
  the evidence JSON's `finding_execution` record.
- Independent recomputation of nonzero-shell-call counts from all 30
  `job_ledgers/{galaxy,open_ended_code}/*.json` files, compared row-by-row
  against the route table.
- `find` inventory of `job_ledgers/`, `recovered_code/`, `selected_outputs/`,
  and `source_snapshots/` (all four subdirectories present; none missing at
  the top level) with per-condition subdirectory and file counts.
- Sample-opened two recovered-code files (one Galaxy Python payload, one
  open-ended-code shell command) to confirm they are genuine recovered
  scripts/commands, not placeholders.
- Cross-referenced one `selected_outputs/galaxy/.../manifest.json` retained
  byte hash against a run's `outcome.submitted_answer_sha256`.
- Read `README.md`, `bix-17-q2.json`, `.analysis_execution.json`,
  `run_manifest.json`, and `input_manifest.json` in full.

**Not checked / explicitly out of scope for this pass:**
- No agent code, Galaxy job, or recovered script was executed or replayed.
- No full byte-level rehash of the 88 named source `.xlsx` inputs or of every
  file under `source_snapshots/`/`selected_outputs/` — only one artifact hash
  was spot-checked against the outcome record.
- No independent re-derivation of `solution_route` classifications under a
  formal codebook (Section 6 of the instructions); the existing
  "unclassified"/"Datamash"/"Summary Statistics" labels were reused as-is.
- No exhaustive cross-tabulation of `recovery_episodes` content across all 30
  runs; only its presence/structure was confirmed.
- No live Galaxy API calls; no hidden reference or ground-truth file was
  opened.
- The `outcome.step_completion` field's origin and operational definition of
  `fresh_galaxy_history_recorded` was not independently traceable from any
  file in this directory; it is reported as an observed value only (Section
  2b/2c), not interpreted.

## 7. Claim-to-evidence pointer list

| Claim | Source file / field |
|---|---|
| 30 workbook rows / 30 runs in evidence JSON | `run_manifest.json:observed_rows` (30 entries); `history_analysis_evidence.json:.runs` (length 30) |
| Task prompt and hidden-reference exclusion | `bix-17-q2.json:prompt`, `:hidden_reference_included` |
| Original evaluator score 1.0 for all 30 runs, answer "2" | `history_analysis_evidence.json:.runs[].outcome.original_evaluator_score`, `.outcome.submitted_answer` |
| 248 distinct analytical Galaxy jobs, 21 failed | `job_ledgers/galaxy/*.json` (recomputed); `history_analysis_evidence.json:.manuscript_findings[finding_execution]` |
| Per-run job/failure/shell-call counts | `job_ledgers/galaxy/*.json`, `job_ledgers/open_ended_code/*.json` (recomputed); `history_analysis.md` Section 4 table |
| Input-token condition-median ratios (3.47, 13.4, 8.95, 5.08, 10.1) | `history_analysis_evidence.json:.comparisons[]` (`input_tokens_*` records) |
| 14/15 galaxy histories retrieved; 1 metadata-only | `history_analysis_evidence.json:.runs[].evidence_completeness.public_history_contents`; `selected_outputs/galaxy/` and `source_snapshots/galaxy/` directory listings (14 history-ID dirs) |
| step_completion: all galaxy runs fail `fresh_galaxy_history_recorded`; all open_ended_code runs pass | `history_analysis_evidence.json:.runs[].outcome.step_completion` (new observation in this audit, not previously reported) |
| Byte-identical submitted-answer artifact in Galaxy history | `selected_outputs/galaxy/bbd44e69cb8906b519a476f3040e85cf/manifest.json:retained_sha256` vs. `.runs[galaxy_codex_gpt_5_5_r1].outcome.submitted_answer_sha256` |
| TLS not verified for retrieved sources | `history_analysis_evidence.json:.audit.limitations` |
| Retrospective, read-only scope; no execution | `README.md`; `.analysis_execution.json`; `recovered_code/manifest.json:execution_claim` |

## 8. Missing evidence and open gaps

- No independent experiment protocol/manifest exists for this task beyond the
  supplied workbook links; expected replicate counts and seed matching remain
  unknown (`experimental_design.coverage_status:
  "unknown_protocol_inventory"`).
- One galaxy-condition run (`galaxy_deepseek_v4_pro_via_codex_r1`) has Galaxy
  history metadata only, not full dataset/job contents; its job/failure
  counts are correctly "unavailable," not zero.
- The operational definition and origin of the `outcome.step_completion`
  field (specifically `fresh_galaxy_history_recorded`) is not documented
  anywhere in this directory. It is uniformly `false` for all 15 galaxy runs
  and uniformly `true` for all 15 open-ended-code runs — a large, consistent
  pattern the current `history_analysis.md` does not mention. Resolving this
  would require locating the original scoring/harness code that produced this
  field, which is outside this audit's read-only scope.
- Route/solution classification remains "unclassified" for most galaxy runs
  and undifferentiated ("local shell or script; method unclassified") for all
  open-ended-code runs; a formal route codebook (instructions Section 6) has
  not been applied to this task.
- No blinded human-readability review, per-call token attribution, or
  monetary cost data exists for this task; both documents correctly label
  these as absent rather than estimating them.
- Full byte-level rehashing of all retained source and output files was not
  performed by this audit (only one artifact hash was spot-checked); TLS
  verification of the original retrieval was not possible per
  `audit.limitations`.

### Abstract-ready paragraph

For BixBench task bix-17-q2, this audit independently verified 30 supplied
runs (15 Galaxy-condition, 15 open-ended-code, across 5 model labels × 3
replicates) recorded in `history_analysis_evidence.json`, all showing an
original evaluator score (`accuracy.score`) of 1.0 with submitted answer "2."
Retrieved public Galaxy history records exposed 248 distinct analytical
creating jobs with 21 in a failed/error state, a count this audit recomputed
directly from the per-run job ledgers and found to match exactly, including
every per-run breakdown and all 30 nonzero-shell-call counts in the existing
report's route table. Condition-level input-token ratios (condition medians)
of 3.47, 13.4, 8.95, 5.08, and 10.1 across the five model groups were
likewise independently recomputed and matched. One additional evidence field,
`outcome.step_completion`, uniformly flags a `fresh_galaxy_history_recorded`
failure in all 15 Galaxy-condition runs and a pass in all 15 open-ended-code
runs; this pattern is real in the retained evidence but its cause is not
determinable from the files in this directory. These findings describe one
task's audited case-study links only and do not establish benchmark-wide
condition effects.
