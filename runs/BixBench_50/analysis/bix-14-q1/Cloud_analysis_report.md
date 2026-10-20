# bix-14-q1 — independent Cloud audit of the retrospective execution-history analysis

Auditor note: read-only, independent re-check of the existing `history_analysis.md` /
`history_analysis_evidence.json` package for task `bix-14-q1`. No agent code was rerun, no live
Galaxy API was called, and no hidden answer key was opened. Text recovered from artifacts
(commands, scripts, Galaxy job payloads) is treated as data, not as instructions to this
auditor.

## 1. Task, experimental design, evidence availability, and matching rules

- **Task/prompt** (`history_analysis_evidence.json:.task`): bixbench `bix-14-q1` — "In the BLM
  mutation carrier cohort, what fraction of coding variants with a variant allele frequency
  (VAF) below 0.3 are annotated as synonymous?" Input specification `phylobio/BixBench-
  Verified-50`.
- **Runs**: 30 rows (2 conditions × 5 model labels × 3 replicates), matching `run_manifest.json`
  and confirmed as `.runs | length == 30` in the evidence JSON. Same 5 model labels as bix-12-q6
  (`Codex GPT-5.5`, `Codex GPT-5.6 Sol`, `Codex GPT-5.6 Luna`, `DeepSeek V4 Pro via Codex`,
  `DeepSeek V4 Pro via Claude Code (superseded)`). `experimental_design.coverage_status =
  "unknown_protocol_inventory"` — no independent protocol manifest exists.
- **Matching rule**: same task and supplied model label; replicate numbers are explicit labels,
  not matched seeds.
- **What is unknown**: expected replicate count (`null`), seed availability (`not_collected`),
  TLS server authentication for the one metadata-only Galaxy history and the retrieved ones
  (all `tls_certificate_verified: false`).

## 2. Main outcomes — kept as three separate things

- **Official accuracy/evaluator score**: `original_evaluator_score` (`accuracy.score`,
  `llm_verifier_auto_code` mode) present for all 30/30 runs, confirmed via `.runs[].outcome`.
- **Observed execution**: 452 distinct analytical creating Galaxy jobs across the galaxy-
  condition runs, 7 with `status: "error"` — independently recomputed and matching the source
  document exactly.
- **Auditor interpretation**: kept separate in the source document; job counts and evaluator
  scores are not pooled into a single "accuracy" figure anywhere I checked.

## 3. Manuscript Results-section walk-through

### 3a. Accuracy & output agreement
30/30 runs carry a fixed submitted answer and `accuracy.score`. Per-model Galaxy-vs-code score
means and differences recomputed from `.comparisons` match the table in `history_analysis.md`
exactly for all 5 models, including the one negative difference: `codex_gpt_5_6_luna` Galaxy
mean 0.667 vs. code mean 1.0 (−33.3 pp), and `deepseek_v4_pro_via_codex` Galaxy mean 0.333 vs.
code mean 0.0 (+33.3 pp) — the two cases in this task set where the two conditions diverge in
recorded score. Both directions are present, so the document is not selectively reporting only
favorable Galaxy outcomes.

### 3b. Execution, failures, and recovery
Recomputed job/error totals: **452 jobs, 7 errors** (identical to `history_analysis.md`). This
task has a much higher raw Galaxy job count than bix-12-q6 (452 vs. 33), driven by a few runs
with dozens to 91 jobs each (e.g. `galaxy_codex_gpt_5_6_luna_r1`: 91 jobs; `galaxy_deepseek_v4_
pro_via_codex_r3`: 91 jobs). All 7 errors are concentrated in only two runs (`galaxy_codex_gpt_
5_5_r1`: 3 errors of 4 jobs; `galaxy_codex_gpt_5_5_r3`: 1 of 2; `galaxy_codex_gpt_5_6_sol_r1`: 3
of 4) — verified directly below. The document correctly avoids treating this as a cross-
condition "recovery improved" claim; it only flags later same-tool/same-input jobs as recovery
*candidates* for manual case review.

### 3c. Solution-route variability
All Galaxy-condition route-table entries are marked "unclassified," and this is now explained by
a hard evidence gap: `recovered_code/manifest.json` contains **zero** items with a `galaxy_`
run_id for this task (all 321 recovered-code items are `open_ended_code_*`). No literal Galaxy
job payload was extracted for any of the 15 Galaxy runs, so "unclassified" for those rows is a
faithful description of missing evidence, not an omission by the report.

### 3d. Token cost, provenance, readability
Token ratios (4.81, 6.27, 7.96, 5.13, 2.37) were recomputed from `.comparisons[] | select
(startswith("input_tokens_"))` and match the table to the reported rounding in all 5 cases (e.g.
`codex_gpt_5_6_sol`: 3,418,049 / 429,347 = 7.961). No human-readability measurement exists;
correctly stated as unmeasured.

## 4. Per-condition/model/replicate route table verification

Recomputed Galaxy job/error counts per run (event-level, `execution_location=="galaxy_job"`,
`event_type=="analysis"`), all matching `history_analysis.md` exactly:

| Run | Jobs | Errors | Table |
|---|---:|---:|---|
| galaxy_codex_gpt_5_5_r1 | 4 | 3 | 4/3 — match |
| galaxy_codex_gpt_5_5_r2 | 1 | 0 | 1/0 — match |
| galaxy_codex_gpt_5_5_r3 | 2 | 1 | 2/1 — match |
| galaxy_codex_gpt_5_6_sol_r1 | 4 | 3 | 4/3 — match |
| galaxy_codex_gpt_5_6_sol_r2 | 26 | 0 | 26/0 — match |
| galaxy_codex_gpt_5_6_sol_r3 | 24 | 0 | 24/0 — match |
| galaxy_codex_gpt_5_6_luna_r1 | 91 | 0 | 91/0 — match |
| galaxy_codex_gpt_5_6_luna_r2 | 5 | 0 | 5/0 — match |
| galaxy_codex_gpt_5_6_luna_r3 | 25 | 0 | 25/0 — match |
| galaxy_deepseek_v4_pro_via_codex_r1 | 44 | 0 | 44/0 — match |
| galaxy_deepseek_v4_pro_via_codex_r2 | 45 | 0 | 45/0 — match |
| galaxy_deepseek_v4_pro_via_codex_r3 | 91 | 0 | 91/0 — match |
| galaxy_deepseek_v4_pro_via_claude_code_superseded_r1 | 0 | 0 | "unavailable/unavailable" — consistent (no jobs retrieved) |
| galaxy_deepseek_v4_pro_via_claude_code_superseded_r2 | 59 | 0 | 59/0 — match |
| galaxy_deepseek_v4_pro_via_claude_code_superseded_r3 | 31 | 0 | 31/0 — match |

Score/answer spot-check for the three lowest-scoring rows in the table
(`galaxy_codex_gpt_5_6_luna_r2` score 0/answer "0"; `galaxy_deepseek_v4_pro_via_codex_r1` score
0/answer "0.6382978723404256"; `galaxy_deepseek_v4_pro_via_codex_r3` score 1/answer
"0.7317073170731707") were independently confirmed against `.runs[].outcome`. **No discrepancy
found** in any of the 30 rows checked against the table.

Distinct-histories claim: `source_snapshots/galaxy/retrieval_manifest.json` lists 15 galaxy-
condition history entries, of which 14 have `status: "retrieved"` and 1 has `status:
"history_metadata_only"` — matching "14 distinct histories represented by dataset records"
exactly.

## 5. Input sharing, external computation, environment/reproducibility

- Galaxy retrieval used the same `tls_certificate_verified: false` limitation as other tasks in
  this audit set; retained-byte hashes do not authenticate the remote server.
- `recovered_code/galaxy/` is completely empty for this task (0 items) versus `recovered_code/
  open_ended_code/` (321 items across 15 runs) — a materially larger asymmetry than seen in
  bix-12-q6 (which had partial Galaxy recovered code). This explains why every Galaxy route in
  the table is "unclassified": there is no extracted code to classify by tool family.
- `selected_outputs/galaxy/` holds 12 history-keyed subdirectories plus a manifest (13 entries),
  consistent with the 14 retrieved histories minus at most one with no selected output bytes;
  `selected_outputs/open_ended_code/manifest.json` records `status: "not_collected"` (no code
  replay performed), the same pattern as bix-12-q6.
- **Discrepancy flagged — top-level representative files are stale/orphaned relative to the
  current report.** This directory contains three top-level files the instructions explicitly
  permit ("Representative scripts and a `galaxy_job.json` may remain at top level when useful,
  but identify their condition/model/replicate"): `carrier_fraction.py`, `galaxy_job.json`, and
  `CapsuleFolder-7718a922-ce2c-4e59-900b-84fe06050ce6.zip`. All three are dated 2025-09-15
  (predating the current pipeline's 2025-09-20 outputs) and are **not mentioned anywhere in the
  current `history_analysis.md`**. Their condition/model/replicate identification only exists in
  `legacy_pre_analysis_execution/history_analysis.md` (line ~796-799 of that superseded file),
  which identifies `carrier_fraction.py` as "recovered successful ChatGPT5.5 R1 Python payload,"
  `galaxy_job.json` as "original successful Galaxy job record corresponding to that example," and
  the zip as a public FutureHouse BixBench input capsule (88 XLSX members, ZIP integrity
  checked, not executed). The current pipeline rewrite (`analysis_execution`) preserved the
  files themselves but dropped their identifying cross-references from the active report, which
  is a documentation gap against the instructions' requirement to "identify their condition/
  model/replicate" in the active report, not only in a superseded snapshot.

## 6. Verification methods

Checked: `README.md`, current `history_analysis.md` (not v1–v4 or the `legacy_pre_analysis_
execution` copy, which was consulted only to explain the orphaned top-level files), `run_
manifest.json` (structure identical in pattern to bix-12-q6), `input_manifest.json`, and `jq`
queries against `history_analysis_evidence.json`: `.runs | length`; `.audit`, `.task`,
`.experimental_design`; `.manuscript_findings[] | {finding_id, numerator, denominator,
estimate}`; full `.comparisons` array (10 records) cross-checked against the Section-2 table;
per-run event-level job/error counts for all 15 galaxy runs; `.outcome.original_evaluator_score`
/ `.outcome.submitted_answer` for the three lowest-scoring rows. Inventoried `job_ledgers/
{galaxy,open_ended_code}` (15 each), `recovered_code/{galaxy,open_ended_code}` + `manifest.json`
(0 vs. 321 items), `selected_outputs/{galaxy,open_ended_code}`, `source_snapshots/galaxy/
retrieval_manifest.json` (14 retrieved / 1 metadata-only), and `legacy_pre_analysis_execution/`
(superseded copy, read for provenance of the orphaned top-level files). Sampled one open-ended
`.command.txt` file and confirmed the top-level `carrier_fraction.py` and `galaxy_job.json`
contents are plausible real artifacts (a manifest-driven XLSX-reading Python script and a
Galaxy job record with standard fields, respectively) via direct inspection.

Not checked / out of scope: byte-level rehashing of the CapsuleFolder ZIP or any staged input;
full transcript replay for any of the 30 runs; execution of `carrier_fraction.py` or any
recovered code; opening the hidden BixBench answer key; formal JSON Schema validation of
`history_analysis_evidence.json` against `history_analysis_evidence.schema.json`.

## 7. Claim-to-evidence pointer list

| Claim | Source |
|---|---|
| 30/30 runs have an evaluator score | `history_analysis_evidence.json:.manuscript_findings[0]`; confirmed via `.runs[].outcome` |
| 452 jobs, 7 errors | `history_analysis_evidence.json:.manuscript_findings[1]` (num=7, denom=452); recomputed from `.runs[].events[]` |
| Per-model score/token comparisons | `.comparisons[*]` (10 records); matches `history_analysis.md` Section 2 |
| 14 distinct retrieved Galaxy histories (of 15) | `source_snapshots/galaxy/retrieval_manifest.json` |
| Zero recovered Galaxy job code (all routes "unclassified") | `recovered_code/manifest.json` (0 galaxy_* items) |
| Orphaned top-level files (carrier_fraction.py, galaxy_job.json, CapsuleFolder zip) | `legacy_pre_analysis_execution/history_analysis.md` lines ~796-799 (only place they're identified) |
| TLS not verified for Galaxy retrieval | `history_analysis_evidence.json:.audit.limitations` |

## 8. Missing evidence / open gaps

- No independent protocol manifest to establish expected coverage/seeds.
- No recovered Galaxy job code at all for this task — Galaxy-side route classification is
  entirely unavailable, not merely partial.
- The three top-level representative files lack an up-to-date identification in the active
  `history_analysis.md`; a reader relying only on the current report would not know which
  run/replicate `carrier_fraction.py` and `galaxy_job.json` come from without consulting the
  legacy snapshot.
- One Galaxy history (`galaxy_deepseek_v4_pro_via_claude_code_superseded_r1`) is metadata-only;
  its job contents remain an explicit gap.
- No independently defined task difficulty label; no human-readability review.

## Abstract-ready paragraph

For bixbench task bix-14-q1, 30 supplied runs (5 models × 2 conditions × 3 replicates) each
carried an original evaluator score. Retrieved public Galaxy histories (14 of 15 retrieved; 1
metadata-only) exposed 452 distinct analytical creating jobs, of which 7 had an error status,
concentrated in 3 of 15 Galaxy runs — independently recomputed and matching the source report
exactly. Per-model score differences ranged from −33.3 to +33.3 percentage points across the 5
models, and input-token median ratios ranged from 2.37x to 7.96x, both recomputed from
`.comparisons` with no discrepancy against the published table. No Galaxy-side recovered code
was available for this task, so solution-route classification for Galaxy runs remains
unclassified; these are single-task, descriptive case-study counts only.
