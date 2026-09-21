# bix-11-q2: Cloud audit report

This report is an independent, read-only verification pass over the existing
`bix-11-q2` audit package. It does not replace `history_analysis.md`; it
records what was spot-checked against `history_analysis_evidence.json` and
the evidence subdirectories, and states explicitly where checks succeeded,
were inconclusive, or could not be performed. No agent code was rerun, no
Galaxy API calls were made, and no hidden-reference file was opened.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task**: bixbench `bix-11-q2`. Prompt (from `bix-11-q2.json` and
  `history_analysis_evidence.json:.task.prompt`): "What percentage of fungal
  genes have treeness values above 0.06?" Source dataset:
  `phylobio/BixBench-Verified-50`. `hidden_reference_included: false` in
  `bix-11-q2.json`; no ground-truth/answer-key file was opened during this
  audit.
- **Runs**: 30 workbook-listed rows, all with `status: "trace_observed"`
  (verified: `jq '[.runs[].status] | group_by(.)'` returns a single group of
  30). Two conditions — `galaxy` (15 runs) and `open_ended_code` (15 runs) —
  across 5 model labels (`Codex GPT-5.5`, `Codex GPT-5.6 Sol`, `Codex GPT-5.6
  Luna`, `DeepSeek V4 Pro via Codex`, `DeepSeek V4 Pro via Claude Code
  (superseded)`), each with 3 labelled replicates.
- **Coverage**: `experimental_design.coverage_status =
  "unknown_protocol_inventory"`; `expected_replicates: null`;
  `seed_availability: "not_collected"`. There is no independent protocol
  manifest, so the 30 rows are the observed-link inventory, not a verified
  complete/expected set. Replicate numbers are labels, not evidence of
  matched seeds (per `matching_rule` in the evidence JSON and per the
  governing instructions).
- **Known confounders** (from `experimental_design.known_confounders`):
  condition-specific prompts/tools, possible container-revision differences,
  possible shared source histories.
- **What's unknown**: whether 30 rows represent full or partial coverage of
  intended replicates; original seeds; whether any non-workbook runs exist
  for this task; stopping rules; retry policy.

## 2. Main outcomes (kept separate per the governing instructions)

### 2a. Official evaluator score (as recorded, not reinterpreted)
- All 30 runs carry `outcome.original_evaluator_score = 1.0` on
  `original_evaluator_score_field = "accuracy.score"`,
  `original_evaluator_mode = "llm_verifier_auto_code"`. Verified by
  inspecting `outcome` for `galaxy_codex_gpt_5_5_r1` and
  `galaxy_codex_gpt_5_5_r3` directly; `history_analysis.md`'s per-run table
  reports `accuracy.score / 1` for all 30 rows, consistent with these two
  spot-checks and with the aggregate mean of 1.0 in every `comparisons[]`
  score entry (`galaxy_mean`/`code_mean` = 1.0 for all five models).
- A second, separate score dimension exists in the evidence that
  **`history_analysis.md`'s tables and prose do not mention**:
  `outcome.step_completion` (e.g. `{"score": 0.5, "passed": false, "steps":
  [{"id": "fresh_galaxy_history_recorded", "passed": false}, {"id":
  "final_deliverable_written", "passed": true}]}`). This is an
  auditor/pipeline-defined process-compliance check, not the official
  BixBench evaluator score, and it is not the same as `accuracy.score`. It
  is not wrong for `history_analysis.md` to omit it from the "official score"
  narrative (mixing it in would violate the instruction to keep evaluator
  score, execution, and interpretation separate), but it is evidence present
  in the JSON that the current report does not surface anywhere. Its
  recurring `fresh_galaxy_history_recorded: false` value is explained in
  Section 3 below (all Galaxy runs copied a seed history rather than
  starting from an empty one).

### 2b. Observed execution (counts only, no correctness judgment)
- Retrieved public Galaxy histories: 15 for the `galaxy` condition (one per
  run; `jq` over `run_manifest.json` shows 15 distinct, non-repeated
  `galaxy_url` values — no history is shared across rows for this task).
- Of those 15, 13 have retrievable job/dataset snapshots
  (`source_snapshots/galaxy/<history_id>/jobs/` non-empty); 2 do not
  (`bbd44e69cb8906b5caa4460da0417599`,
  `bbd44e69cb8906b5cdf69d89c84ad4d8` — both `galaxy_codex_gpt_5_6_luna`
  replicates 2 and 3 — have zero files under `jobs/`). This matches
  `sources[]` in the evidence JSON, where exactly 2 of 45 source records
  carry `access_status: "history_metadata_only"` and the other 43 are
  `"retrieved"`. This is fully consistent with README's "13 distinct
  histories represented by dataset records."
- Summing `derived_metrics.analytical_job_count` across the 15 Galaxy runs
  (nulls excluded, i.e. excluding the two histories with no job data) gives
  **29**; summing `derived_metrics.total_failed_jobs` over the same set
  gives **2**. Both match `history_analysis.md`'s "29 distinct analytical
  creating jobs, including 2 failed jobs" and the `finding_execution`
  finding record (`numerator: 2, denominator: 29`).
- `recovery_episodes` is an empty array for all 30 runs, with no exceptions
  (verified by `jq '[.runs[] | select(.recovery_episodes | length > 0)]'` →
  `[]`). No run in this evidence package has a formally recorded recovery
  episode, despite 2 recorded job failures.

### 2c. Auditor interpretation (this audit's own reading, clearly separated)
- The absence of any populated `recovery_episodes` record, combined with a
  narrative sentence in `history_analysis.md` about a "recovery candidate,"
  is a soft gap: the claim of a same-tool/same-input retry is not backed by
  a structured `recovery_episodes` entry anywhere in the evidence JSON (see
  Section 3 for the specific spot-check).
- The two histories with `history_metadata_only` status structurally
  understate Galaxy-side job/failure counts for `galaxy_codex_gpt_5_6_luna`
  replicates 2 and 3: their true job and failure counts are unknown, not
  zero, and both `history_analysis.md` and this report correctly render them
  as "unavailable" rather than folding them into the 29/2 totals.
- This is a single-task case study across 5 model labels; none of the above
  supports a benchmark-wide or condition-superiority claim.

## 3. The four manuscript Results questions, applied to this task

### 3.1 Accuracy and output agreement by execution condition
`history_analysis.md`'s comparison table reports, per model, Galaxy/code
mean `accuracy.score` and a Galaxy/code difference of 0 percentage points
for all five models, plus a "Galaxy/code median input-token ratio." I
recomputed each of the five ratios directly from
`comparisons[]` in the evidence JSON:

| Model | galaxy_mean | code_mean | pp diff | galaxy_median tokens | code_median tokens | ratio (galaxy/code) | matches report? |
|---|---:|---:|---:|---:|---:|---:|---|
| codex_gpt_5_5 | 1.0 | 1.0 | 0 | 1,404,112 | 264,767 | 5.3032 | yes (5.3) |
| codex_gpt_5_6_luna | 1.0 | 1.0 | 0 | 9,889,509 | 608,736 | 16.2460 | yes (16.2) |
| codex_gpt_5_6_sol | 1.0 | 1.0 | 0 | 1,141,622 | 342,864 | 3.3297 | yes (3.33) |
| deepseek_v4_pro_via_claude_code_superseded | 1.0 | 1.0 | 0 | 1,047,622 | 2,455,757 | 0.4266 | yes (0.427) |
| deepseek_v4_pro_via_codex | 1.0 | 1.0 | 0 | 2,722,465 | 1,490,020 | 1.8271 | yes (1.83) |

All five score means, all five percentage-point differences, and all five
token ratios in `history_analysis.md`'s Section 2 table match the evidence
JSON exactly (to reported precision). Every `outcome.original_evaluator_score`
value observed while sampling individual runs was `1.0` on `accuracy.score`,
consistent with the reported means. `accuracy.score` here evaluates a fixed
submitted answer per the BixBench evaluation contract; it is not pooled with
any other benchmark's endpoint, and this task provides no IWC-style output
agreement metric to keep separate. What remains unresolved: whether
`accuracy.score = 1.0` for all 30 runs means all submitted answers were
judged correct, partially correct, or matched under some tolerance — the
evaluator mode is `llm_verifier_auto_code`, and its internal decision logic
was not (and could not properly be) re-examined without treating a
regrading exercise as this audit's job, which it is not.

### 3.2 Analysis execution, failures, and recovery
The retrieved Galaxy histories show 29 analytical creating jobs across 13
histories with job data (2 failed), matching Section 2 above. I additionally
opened the raw failing job event
(`galaxy_codex_gpt_5_6_luna_r1`, `native_job_id
bbd44e69cb8906b5a2f2b88750de9e3f`, tool `table_compute`, `status: "error"`,
`exit_code: 1`) and traced its stderr: a pandas `TypeError` inside a
`filtersumval` comparison against the value `"0.06"` — directly relevant to
this task's ">0.06 treeness" threshold. I then looked for the "later
successful job with the same tool and input HDA IDs" that
`history_analysis.md`'s execution paragraph describes as an "operational
recovery candidate." **I could not confirm this specific mechanic for this
run**: the next `table_compute` job in the same run (`native_job_id
bbd44e69cb8906b5a5638dfecd73cba7`, `status: "ok"`) used a *different* input
HDA (`f9cad7b01a47213521b2d92a1140ef1c`) than the failed job's input HDA
(`f9cad7b01a47213579d2ed7c486a2b96`). This looks more like a new analytical
attempt on a different artifact than a same-input retry of the failed
operation. `history_analysis.md`'s statement is phrased generally/cautiously
("flagged... as a candidate for case review," not asserted as confirmed
recovery), so this is not a contradiction of a specific claimed number, but
it is a place where my spot-check could not corroborate the implied
same-input-retry pattern, and no `recovery_episodes` record exists anywhere
in the evidence JSON to adjudicate it either way. This should be read as an
open item, not a resolved recovery.

Separately, `total_failed_jobs` and `analytical_job_count` are `null` (not
zero) for the two `history_metadata_only` runs, correctly excluded from the
29/2 totals — consistent with the instruction not to encode missing counts
as observed zeros.

### 3.3 Solution-route variability across models and replicates
`history_analysis.md`'s per-run route table lists tool-family indicators
(`PhyKIT`, `Newick/branch parser`, `IQ-TREE report`, `Biopython`,
`unclassified`). I opened two recovered/job-ledger records to check these
are archival, not fabricated:
- `open_ended_code_codex_gpt_5_5_r1/item_1.command.txt` — a real shell
  command reading a Skill file
  (`/codex_home/skills/phylogenetics-tree-metrics/SKILL.md`) and listing
  `/workspace`. Genuine agent shell output, consistent with "local shell or
  script."
- `open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1/call_00_...`
  — a real Python script parsing `.iqtree` report files with a regex on
  "Sum of internal branch lengths... % of tree length," dividing by 100, and
  counting genes above 0.06 — directly implementing the task's metric via a
  local/non-Galaxy route (an `IQ-TREE`/`Newick`-adjacent parser, matching the
  table's route indicator for that run).
- `job_ledgers/galaxy/galaxy_codex_gpt_5_5_r1.json` events show genuine
  Galaxy MCP tool calls (`search_galaxy_tools`, `run_galaxy_tool_and_wait`
  against `toolshed.g2.bx.psu.edu/repos/goeckslab/phykit_metrics/...`,
  `operation.selector: "treeness"`), consistent with the table's "PhyKIT"
  route indicator for Galaxy rows, and shows the agent copying a seed
  history via `bioblend` (`gi.histories.copy_history`) rather than starting
  from empty — see Section 5.

These spot-checks support that the route indicators in
`history_analysis.md` are grounded in real recovered text, not invented
labels. I did not re-derive the full route classification for all 30 runs;
I sampled 3 files (2 recovered-code, 1 job ledger) out of hundreds of
available artifacts. Difficulty is unclassified in this package, consistent
with `history_analysis.md`'s statement that no independent difficulty source
was supplied.

### 3.4 Token cost, provenance, and human readability
The four ratios recomputed in Section 3.1 all reproduce
`history_analysis.md`'s reported "Galaxy/code median input-token ratio"
column exactly. Each `comparisons[]` entry explicitly labels the estimate as
a "ratio of condition medians" (not a median of per-pair ratios), matching
the governing instructions' requirement to disambiguate these two
estimands, and matching `history_analysis.md`'s own caption language. No
per-call token attribution, no monetary costs, and no human-readability
protocol are present in this package; `history_analysis.md` correctly
states this rather than inferring a readability benefit.

## 4. Per-condition/model/replicate route table

`history_analysis.md` Section 4 already contains a 30-row table (model,
condition, replicate, `accuracy.score`/value, submitted answer, route
indicators, Galaxy analytical-job/failed counts, nonzero-shell-call counts).
I re-verified a sample of rows directly against `derived_metrics` and
`outcome.submitted_answer` in the evidence JSON rather than rebuilding the
table from scratch:

| Run | Report: jobs/failed | Evidence: `analytical_job_count`/`total_failed_jobs` | Report: nonzero shell | Evidence: `nonzero_exit_shell_calls` | Report: answer | Evidence: `submitted_answer` |
|---|---|---|---|---|---|---|
| `galaxy_codex_gpt_5_5_r1` | 1/0 | 1/0 | 0 | 0 | 35.34136546184739% | 35.34136546184739% |
| `galaxy_codex_gpt_5_5_r3` | 3/1 | 3/1 | 1 | 1 | 35.3413654618% | 35.3413654618% |
| `galaxy_codex_gpt_5_6_luna_r1` | 11/1 | 11/1 | 0 | 0 | 35.341365% | (not separately re-read; job/shell counts match) |
| `galaxy_codex_gpt_5_6_luna_r2` | unavailable/unavailable | null/null | 1 | 1 | 35.34% | consistent with `history_metadata_only` source |
| `galaxy_deepseek_v4_pro_via_codex_r1` | 2/0 | 2/0 | 4 | 4 | 35% | consistent |

No discrepancy found in this sample. I did not re-verify all 30 rows'
route-indicator text (e.g. "PhyKIT," "Newick/branch parser") cell-by-cell
against raw trace content beyond the 3 files sampled in Section 3.3; those
labels are plausible given the tool names visible in the underlying traces
but were not exhaustively re-derived.

## 5. Input sharing, external computation, environment/reproducibility

- `input_manifest.json` shows two distinct SHA-256 input-manifest hash
  groups: one shared by 20-input runs (`bb5b8d7a22...`, count 20) and one by
  0-input-manifest runs (`c16950135b...`, count 0) — the latter applies to
  all three `galaxy_deepseek_v4_pro_via_codex` and all three
  `galaxy_deepseek_v4_pro_via_claude_code_superseded` Galaxy replicates,
  meaning no `inputs_manifest.json` was staged/retrieved for those 6 runs
  specifically (their open-ended-code counterparts do have the 20-entry
  manifest). This is a gap, not a zero: `input_manifest.json` explicitly
  notes "Hashes are copied from original trace manifests; full staged
  inputs were not rehashed by this audit," and `all_trace_input_hashes_agree_by_name: true` for the runs that do have manifests.
- Every Galaxy run I inspected acquired its inputs by **copying a shared
  seed history** rather than by fresh independent upload: the
  `galaxy_codex_gpt_5_5_r1` job ledger shows the agent reading a
  `seed_history.json` recording `seed_history_id:
  bbd44e69cb8906b5a0ea2e5ab31d361f`, `seed_owner_username: alexch`, then
  calling `gi.histories.copy_history(seed, name=...)` to create its own
  working history. This directly explains the recurring
  `step_completion` result `"fresh_galaxy_history_recorded": false` noted
  in Section 2a: by the pipeline's own compliance check, none of these runs
  used a history that was not derived from the shared seed. This is
  consistent with the governing instructions' warning that "distinct
  uploads do not prove independent upstream acquisition" and that copied
  associations should not be treated as fresh uploads — the evidence here
  actively confirms shared-origin inputs rather than merely failing to rule
  it out.
- External computation: Galaxy analytical jobs ran via
  `toolshed.g2.bx.psu.edu` tool IDs (e.g. `goeckslab/phykit_metrics`) on
  `usegalaxy.org`; open-ended-code runs executed locally inside an agent
  workspace (`/workspace`, `/codex_home`) using shell/Python (IQ-TREE report
  parsing, Biopython). No case of a Galaxy job itself invoking a remote
  analytical service beyond the Galaxy instance was observed in the sampled
  events.
- `audit.limitations` in the evidence JSON records that "Source TLS
  certificates were not verified because the host proxy presented an
  invalid certificate; local retained-byte hashes do not authenticate the
  remote server" — a reproducibility caveat on all retrieved Galaxy/HF bytes
  for this task, applying package-wide, not just to a subset of runs.

## 6. Verification methods (what was and was not checked)

**jq queries executed** against `history_analysis_evidence.json`:
`.runs | length`; `.schema_version`; `.audit`; `.task`;
`.experimental_design`; `.comparisons` (full, plus per-comparison-id
selection for all 5 models' score and token-ratio entries);
`.manuscript_findings` (full); `.runs[] | {run_id, condition, model, status}`;
`.runs[0] | keys`; `.runs[0].outcome`; `.runs[] | select(run_id==...) |
{outcome, derived_metrics}` for `galaxy_codex_gpt_5_5_r1` and
`galaxy_codex_gpt_5_5_r3`; `.runs[] | select(condition=="galaxy") |
derived_metrics` (all 15, plus sum of `analytical_job_count` and
`total_failed_jobs`); `.runs[] | select(condition=="open_ended_code") |
derived_metrics` (checked all Galaxy-specific fields are null); `.runs[] |
select(recovery_episodes|length>0)` (empty); `.validation`; `.sources |
length` and grouped `.access_status`.

**Subdirectories inventoried** with `find -maxdepth 3`: `job_ledgers/`
(galaxy/ and open_ended_code/, 15 files each, one per run_id);
`recovered_code/` (only an `open_ended_code/` subtree exists — **no
`recovered_code/galaxy/` directory is present**; Galaxy-side command/tool-call
records live instead in `job_ledgers/galaxy/*.json` and
`source_snapshots/galaxy/<history_id>/jobs/`, which is a defensible design
choice given Galaxy has no local shell/script text of its own, but it means
the literal directory layout suggested in
`HISTORY_ANALYSIS_INSTRUCTIONS.md` Section 2 is not followed exactly for the
`galaxy` condition); `selected_outputs/` (`galaxy/` has 14 history-ID
subdirectories with `.dat` files; `open_ended_code/` has only a
`manifest.json` recording `status: "not_collected"` — no open-ended-code
output bytes were retained in `selected_outputs`, a category gap for that
condition); `source_snapshots/` (`galaxy/` with 15 history dirs, 13 of which
have non-empty `jobs/`; `huggingface_traces/files/` with 30 per-run
directories, one per run_id, plus `indexes/` and `manifests/`).

**Files opened directly** (sample-read, not exhaustive): `README.md`,
`history_analysis.md` (current version only — `.v1`–`.v4` snapshots were
identified but deliberately not treated as ground truth per instructions),
`run_manifest.json`, `input_manifest.json`, `bix-11-q2.json`,
`.analysis_execution.json`, `recovered_code/manifest.json`,
`selected_outputs/open_ended_code/manifest.json`,
`job_ledgers/galaxy/galaxy_codex_gpt_5_5_r1.json` (partial, first ~24
events), two `recovered_code/open_ended_code/*` command files, one raw
failing-job event inside `job_ledgers/galaxy/galaxy_codex_gpt_5_6_luna_r1.json`.

**Explicitly out of scope / not performed**: full byte-level hash
reverification of any artifact (I read recorded hashes; I did not recompute
SHA-256 over the underlying bytes); full transcript replay for any of the 30
runs; opening every one of the several hundred `recovered_code/*.command.txt`
files (a small sample was read per condition); re-deriving the route
classification for all 30 rows from raw trace content; executing or
re-running any recovered code, shell command, or Galaxy tool; opening any
hidden-answer-key file (none was located, and `bix-11-q2.json` explicitly
records `hidden_reference_included: false`); statistical inference beyond
what the single-task evidence supports.

## 7. Claim-to-evidence pointer list

| Claim | Evidence pointer |
|---|---|
| 30/30 runs have a `trace_observed` status and an original evaluator score | `history_analysis_evidence.json:.runs[].status` (all `"trace_observed"`); `.runs[*].outcome.original_evaluator_score` |
| `accuracy.score` mean = 1.0 for both conditions, all 5 models, 0 pp difference | `history_analysis_evidence.json:.comparisons[]` (`score_*` entries) |
| Token ratios 5.30 / 16.25 / 3.33 / 0.427 / 1.83 | `history_analysis_evidence.json:.comparisons[]` (`input_tokens_*` entries) |
| 29 distinct Galaxy analytical jobs, 2 failed | `history_analysis_evidence.json:.manuscript_findings[] (finding_execution)`; independently reproduced by summing `.runs[] | select(condition=="galaxy") | derived_metrics.analytical_job_count / total_failed_jobs` |
| 13 of 15 Galaxy histories have retrievable job data; 2 do not | `source_snapshots/galaxy/<history_id>/jobs/` file counts; `history_analysis_evidence.json:.sources[].access_status` (2 `history_metadata_only`) |
| Galaxy runs copy a shared seed history rather than starting fresh | `job_ledgers/galaxy/galaxy_codex_gpt_5_5_r1.json` events (`seed_history.json` read, `gi.histories.copy_history` call); `outcome.step_completion.steps[fresh_galaxy_history_recorded].passed == false` on sampled runs |
| Recovered open-ended-code commands are genuine, not fabricated | `recovered_code/open_ended_code/open_ended_code_codex_gpt_5_5_r1/item_1.command.txt`; `.../open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1/call_00_...command.txt` |
| A specific "same tool/input HDA" recovery candidate could not be confirmed for `galaxy_codex_gpt_5_6_luna_r1`'s failed job | `job_ledgers/galaxy/galaxy_codex_gpt_5_6_luna_r1.json`, `table_compute` events at sequence 21 (error, input HDA `...79d2ed7c486a2b96`) and sequence 23 (ok, input HDA `...21b2d92a1140ef1c`) — different input HDAs |
| No run in this package has a populated `recovery_episodes` record | `history_analysis_evidence.json:.runs[].recovery_episodes` (all `[]`) |
| `outcome.step_completion` is a distinct, non-official-evaluator score not surfaced in `history_analysis.md` | `history_analysis_evidence.json:.runs[*].outcome.step_completion` |
| `selected_outputs/open_ended_code` retains no output bytes for this condition | `selected_outputs/open_ended_code/manifest.json` (`status: "not_collected"`) |
| No `recovered_code/galaxy/` directory exists | `find recovered_code -maxdepth 2 -type d` |

## 8. Missing evidence / open gaps

- No independent experiment/protocol manifest exists to confirm 30 is the
  full intended run count for this task, or that 3 replicates per
  model/condition was the designed target rather than an artifact of
  workbook selection.
- `input_manifest.json` lacks a staged `inputs_manifest.json` for 6 of the
  15 Galaxy runs (`galaxy_deepseek_v4_pro_via_codex_*`,
  `galaxy_deepseek_v4_pro_via_claude_code_superseded_*`); their input
  provenance for this audit rests only on the shared-hash inference from
  their open-ended-code counterparts, not a directly retrieved manifest.
- 2 of 15 Galaxy histories (`galaxy_codex_gpt_5_6_luna_r2`,
  `_r3`) have no retrievable job/dataset data; their true job counts,
  failure counts, and tool usage are unknown, not zero.
- No `recovery_episodes` record exists for either of the 2 recorded Galaxy
  job failures in this task; whether either failure was followed by a
  same-objective corrective retry is unresolved from the evidence JSON
  structure (a raw-event trace exists and was partially examined, but a
  full same-goal-linkage determination was not attempted for all failures).
- `selected_outputs/open_ended_code` contains no retained output bytes
  (explicitly marked `not_collected`), so open-ended-code final artifacts
  for this task are only available via the HuggingFace trace snapshots, not
  as a separately curated output set.
- No token attribution by stage (discovery/input-acquisition/analysis/retry/
  reporting), no monetary costs, and no human-readability review exist for
  this task; `history_analysis.md` already states this rather than
  fabricating a benefit.
- The `step_completion` process-compliance dimension (e.g.
  `fresh_galaxy_history_recorded`) is present in every run's evidence record
  but is not discussed anywhere in `history_analysis.md`; whether this was
  an intentional scope decision or an oversight is not stated in the
  package.

### Abstract-ready paragraph

For the bixbench task bix-11-q2 ("What percentage of fungal genes have
treeness values above 0.06?"), this audit examined 30 recorded runs (15
Galaxy, 15 open-ended-code) spanning 5 model labels with 3 replicates each.
All 30 runs carried an original evaluator score of 1.0 on the
`accuracy.score` field, with a 0-percentage-point Galaxy-minus-code
difference recorded for every model in this single-task comparison.
Retrieved public Galaxy histories exposed 29 distinct analytical creating
jobs across 13 of 15 histories with retrievable job data (2 histories
returned no job records), including 2 recorded job failures. Galaxy/code
median-input-token ratios recomputed directly from the evidence JSON were
5.30, 16.25, 3.33, 0.43, and 1.83 for the five model labels, matching
`history_analysis.md`'s reported values exactly. No `recovery_episodes`
record was populated for either recorded failure, and a specific same-input
recovery pattern proposed in `history_analysis.md`'s narrative could not be
confirmed for the one failure inspected in detail; these counts describe a
single audited task and do not support a benchmark-wide or
condition-superiority conclusion.
