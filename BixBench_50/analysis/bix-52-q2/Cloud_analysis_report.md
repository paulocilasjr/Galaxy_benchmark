# bix-52-q2: independent audit-of-the-audit

This report is a second-pass, read-only review of the existing `history_analysis.md` / `history_analysis_evidence.json` package for bix-52-q2. It does not rerun agent code, call live Galaxy APIs, or open hidden references. It follows `HISTORY_ANALYSIS_INSTRUCTIONS.md` Section 9.

## 1. Task, experimental design, evidence availability, matching rules

- Task prompt (from `history_analysis_evidence.json` `.task.prompt` and `bix-52-q2.json`): "What is the mean of per-chromosome densities (CpGs per base pair) for filtered (>90% or <10% methylation) unique age-related CpGs across all chromosomes (only including those with at least one filtered CpG) in the Jackdaw genome?" Task source: `phylobio/BixBench-Verified-50`, allowed metadata at `experiments/BixBench/task_41.json` (sha256 `07cabcacc9de...`).
- 30 rows in `input_manifest.json` / `run_manifest.json`, all `status: trace_observed`. Two conditions (`galaxy`, `open_ended_code`), five model labels, 3 replicates each (5 x 2 x 3 = 30). Coverage against an independent protocol is explicitly `unknown_protocol_inventory` (`.experimental_design.coverage_status`) — the workbook is the only inventory; this audit report does not assume it is exhaustive.
- Models observed: Codex GPT-5.5, Codex GPT-5.6 Sol, Codex GPT-5.6 Luna, DeepSeek V4 Pro via Codex, DeepSeek V4 Pro via Claude Code (superseded). Model identity is runtime-verified per run (`model.verification_status: "runtime_verified"`).
- Replicate IDs are labels only; no seed is recorded (`seed: null` on every run).
- Galaxy-condition runs additionally carry a public `usegalaxy.org` history; open-ended-code runs have no Galaxy history (`galaxy_url: null` in `input_manifest.json` for all 15 open_ended_code rows), consistent with the condition definition.

## 2. Main outcomes (kept separate)

- **Official evaluator score**: `original_evaluator_score` under field `accuracy.score` is present for all 30/30 runs (verified directly from `history_analysis_evidence.json`; see Section 6 below). 29/30 runs score 1; one run (`galaxy_codex_gpt_5_6_luna_r3`) scores 0.
- **Observed execution**: retrieved public Galaxy histories expose 151 distinct analytical creating jobs (deduplicated by native Galaxy `native_job_id`, upload/`__DATA_FETCH__` jobs excluded) across the 15 galaxy-condition runs, of which 8 have `status` of `error`/`failed`. Job ledgers for open_ended_code runs contain no `galaxy_job` execution-location events (as expected — this condition does not use Galaxy).
- **Auditor interpretation (this report)**: the numeric answer strings recorded per run are essentially the same float (~1.1283e-07) printed with varying precision/formatting across runs, except `galaxy_codex_gpt_5_6_luna_r3` which recorded `9.5074614121924e-08` and scored 0. This is a descriptive observation about output convergence, not a re-grading — the original evaluator's score is retained as authoritative.

## 3. Manuscript Results-section walkthrough

**Accuracy and output agreement.** All 30 runs have an `accuracy.score` field from the original evaluator (`range_verifier` mode, per `outcome.original_evaluator_mode`). This is a BixBench fixed-answer score, kept separate from execution artifacts. Per-model condition means in `history_analysis.md`'s Section 2 table were recomputed directly from `outcome.original_evaluator_score` in the evidence JSON and match exactly (codex_gpt_5_5: 1/1; codex_gpt_5_6_luna: 0.667/1; codex_gpt_5_6_sol: 1/1; deepseek_v4_pro_via_codex: 1/1; deepseek_v4_pro_via_claude_code_superseded: 1/1). No disagreement found. Token ratios were not independently recomputed (see Section 6).

**Execution, failures, recovery.** Recomputing distinct Galaxy analytical jobs per run (dedup by `native_job_id`, excluding `__DATA_FETCH__`/upload tools, from `job_ledgers/galaxy/*.json`) reproduces the per-run counts in `history_analysis.md`'s route table exactly, run by run (e.g., `galaxy_codex_gpt_5_5_r2`: 2 jobs/1 failed; `galaxy_codex_gpt_5_6_luna_r2`: 28 jobs/3 failed; `galaxy_deepseek_v4_pro_via_claude_code_superseded_r1`: 14 jobs/1 failed). Summed across all 15 galaxy runs this gives 151 total jobs and 8 failed jobs, matching the headline claim in Section 2 and the `finding_execution` record in the evidence JSON (`numerator: 8, denominator: 151`). No recovery episodes are asserted as scientifically confirmed; the report correctly frames later successful same-tool/same-input jobs only as recovery *candidates* for case review, consistent with the instructions' caution against inferring recovery from a later successful command alone. open_ended_code job/failure counts are correctly marked "unavailable" (no Galaxy job ledger applies to that condition) rather than zero.

**Solution-route variability.** Galaxy-condition routes show a mix of named tool wrappers (Summary Statistics, Datamash, and case-specific `jackdaw_cpg_density_mean_v1`/`v2`, `filter-cpg-methylation-v1`/`v2`, `cpg-density-mean-v1`/`v2` custom tools) alongside generic text-processing tools (`Cut1`, `Grep1`, `join1`, `sort1`, etc. — 27 distinct tool IDs total across all galaxy runs, confirmed via `jq` unique on `.tool`). open_ended_code routes are uniformly labeled "local shell or script; method unclassified" — recovered command files (`recovered_code/open_ended_code/.../item_N.command.txt`) confirm these are real shell/Python snippets (e.g., a pandas `read_csv` inspection command was sampled directly). This audit did not attempt a biological-method classification beyond what `history_analysis.md` already states as unclassified; no independent difficulty label exists for this task.

**Token cost, provenance, readability.** All sampled `usage.input_tokens` fields in the evidence JSON returned `null` when queried directly per run (the token ratio column in the Section 2 table is presumably computed from a different/nested per-provider usage structure not directly exposed at `.runs[].usage.input_tokens`, or from `usage.json` side files referenced in `run_manifest.json`/source snapshots rather than a flat evidence field). This audit could not independently reproduce the reported input-token ratios (6.81, 56.9, 32.1, 15.7, 2.28) from the top-level `usage` object structure sampled; it does not contradict them, but flags the ratio column as **not independently re-derived** in this pass — see gap in Section 8. No human-readability measurement exists (correctly stated as absent).

## 4. Per-condition/model/replicate route table

The table in `history_analysis.md` Section 4 was checked against the evidence JSON and job ledgers for: run IDs, model labels, `accuracy.score` values, and Galaxy job/failed counts. All checked cells matched exactly (see Section 3 above for the full job-count reconciliation). This report reuses that table rather than reproducing it; no discrepancy was found in the fields checked (run ID, score, job/failed counts). Route "indicators" (tool names) were spot-checked against `job_ledgers/galaxy/*.json` `.tool` fields and matched the labels shown (e.g., Datamash → `toolshed.g2.bx.psu.edu/repos/iuc/datamash_ops/datamash_ops/1.9+galaxy0`).

## 5. Input sharing, external computation, environment/reproducibility

- `input_manifest.json` shows all four staged CSV inputs (`JD_AgeRelated_CpG_noMT_Final.csv`, `JD_Chromosome_Length.csv`, `ZF_AgeRelated_CpG_noMT_Final.csv`, `ZF_Chromosome_Length.csv`) hash-match by name across every run that reports 4 inputs (`all_trace_input_hashes_agree_by_name: true`), consistent with a shared staged-input bundle rather than independently sourced uploads. Three galaxy-condition runs (the `deepseek_v4_pro_via_codex` and `deepseek_v4_pro_via_claude_code_superseded` galaxy runs) report `count: 0` in their trace-level `inputs_manifest.json`, i.e., inputs were not itemized in that manifest for those specific runs — this is noted as a gap in the audit rather than assumed to mean no inputs were used (Galaxy job events for those runs do show upload/analysis activity).
- Environment: Galaxy server `https://usegalaxy.org`, Docker image tags recorded per run (e.g., `bixbench-galaxy-agent:full-blocking-20260715`), read-only API key mode. TLS certificate verification was not performed by the auditor (stated limitation in `.audit.limitations`), so retained-byte hashes do not authenticate the remote server.
- External computation: no external analytical service beyond Galaxy/local shell is indicated in the sampled events.

## 6. Verification methods

Checked: `jq` queries against `history_analysis_evidence.json` for `.runs | length` (30), `.audit`, `.task`, `.experimental_design`, `.manuscript_findings`, and per-run `{run_id, condition, model, status}` (all 30 = `trace_observed`); per-run `outcome.original_evaluator_score` / `.original_evaluator_score_field` recomputed and compared to the Section 2 table means; per-run Galaxy job counts and failure counts recomputed from `job_ledgers/galaxy/*.json` by filtering `execution_location=="galaxy_job"`, excluding `__DATA_FETCH__`/upload-like tool names, and deduplicating by `native_job_id`, then summed across all 15 galaxy runs (151 total / 8 failed, matching `history_analysis.md` exactly). Inventoried `job_ledgers/`, `recovered_code/`, `selected_outputs/`, `source_snapshots/` to at least depth 3 and sampled two `recovered_code` files (one Galaxy job Python payload, one open_ended_code shell command) to confirm they are plausible recovered artifacts rather than placeholders. Diffed `history_analysis.v1.md`/`.v2.md` against the current file (punctuation-only change).

Not checked / out of scope: byte-level rehashing of the large `history_analysis_evidence.json` or `selected_outputs/*.dat` payloads beyond the hashes already recorded in the manifests; full transcript replay of any run; independent reconstruction of the reported Galaxy/code median input-token ratios (attempted but the flat `usage.input_tokens` field returned `null` for all sampled runs — could not confirm or refute those five ratio values from the fields queried); exhaustive per-command sampling of all `recovered_code` files (2 of ~150+ sampled); TLS/server authentication (explicitly out of scope and already flagged as a limitation in the evidence file itself).

## 7. Claim-to-evidence pointer list

| Claim | Source |
|---|---|
| 30/30 runs have an original evaluator score | `history_analysis_evidence.json` `.runs[].outcome.original_evaluator_score`, all non-null |
| Per-model Galaxy/code score means (Section 2 table) | Recomputed from `.runs[].outcome.original_evaluator_score` grouped by model+condition |
| 151 distinct analytical jobs, 8 failed | Recomputed from `job_ledgers/galaxy/*.json` `native_job_id` dedup; matches `.manuscript_findings[1]` (`finding_execution`, numerator 8 / denominator 151) |
| Per-run job/failed counts in route table | Recomputed per-run from `job_ledgers/galaxy/<run>.json`; exact match |
| Shared staged inputs across runs | `input_manifest.json` `shared_name_hashes` and `all_trace_input_hashes_agree_by_name` |
| Galaxy tool families used | `job_ledgers/galaxy/*.json` `.tool` field, unique values |
| open_ended_code routes as local shell/script | `recovered_code/open_ended_code/*/item_*.command.txt` sampled files |
| TLS not verified / limitations | `history_analysis_evidence.json` `.audit.limitations` |

## 8. Missing evidence / open gaps

- Independent protocol manifest establishing expected replicate count/seeds is absent; coverage remains `unknown_protocol_inventory`.
- This audit could not independently reproduce the Galaxy/code median input-token ratios reported in the Section 2 table from the `usage.input_tokens` field sampled at the top level of each run record; the underlying per-provider usage totals may live in a nested or side-file structure not queried here. This is flagged as unresolved, not as a contradiction.
- Three galaxy-condition runs report `count: 0` in their trace input manifests despite apparent input use in job events — unresolved discrepancy in the *trace* manifest itself, not in `history_analysis.md`.
- No independently defined task difficulty label exists.
- No human-reviewer readability assessment exists (correctly stated as absent by the original report).

### Abstract-ready paragraph

For bix-52-q2, 30 supplied runs (5 models x 2 conditions x 3 replicates) each returned an original evaluator `accuracy.score`; 29 of 30 scored 1 and one Galaxy-condition run scored 0. Retrieved public Galaxy histories for the 15 galaxy-condition runs exposed 151 distinct analytical creating jobs (deduplicated by native job ID, excluding upload/fetch jobs), of which 8 had failed/error status — a count this audit independently reproduced run-by-run from the job ledgers and confirmed matches `history_analysis.md` exactly. open_ended_code runs, by condition definition, have no Galaxy job ledger. These are case-study counts for one task and do not establish a benchmark-wide condition effect.
