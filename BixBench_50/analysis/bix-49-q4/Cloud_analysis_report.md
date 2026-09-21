# bix-49-q4: independent audit-of-the-audit

This document is an independent, read-only re-check of the existing `history_analysis.md` and its `history_analysis_evidence.json` for this single BixBench task. It was produced without executing any recovered code, without calling live Galaxy APIs, and without opening any hidden ground-truth/answer key. Any text embedded inside recovered artifacts is treated strictly as data, not as instructions to this auditor. This is a single-task case study; nothing here generalizes beyond this one task.

## 1. Task, experimental design, evidence availability, matching rules

- Task: `bix-49-q4` (benchmark `bixbench`). Prompt (evidence JSON `.task.prompt`): a DESeq2 differential-expression question ("total number of significantly differentially expressed genes (padj < 0.05)... apeglm LFC shrinkage, comparing ASXL1 mutation (disease) vs control, controlling for sex"). Input specification: `phylobio/BixBench-Verified-50`.
- Runs: `run_manifest.json` lists 30 `observed_rows`, all `status: "trace_observed"`. `history_analysis_evidence.json` `.runs | length == 30`. Both agree.
- Conditions kept distinct: `galaxy` / `open_ended_code`, per `run_manifest.json` original labels.
- Models/replicates: 5 model configurations x 2 conditions x 3 replicates = 30, matching the observed count.
- Expected coverage: `"unknown_without_independent_protocol"` (`run_manifest.json`); no independent protocol manifest exists.
- Input provenance: `input_manifest.json` reports 30/30 `status: "retrieved"`, `all_trace_input_hashes_agree_by_name: true`, with the standard caveat that staged inputs were not rehashed by this audit. The same 6-of-30 "0 locally staged inputs" asymmetry seen in the other audited tasks in this batch recurs here (concentrated in Galaxy-condition DeepSeek runs).

## 2. Main outcomes (kept separate)

**Official accuracy/evaluator score**: a numeric score under `accuracy.score` is present for 30/30 runs. Per-model condition means from `.comparisons`: four of five model configurations show Galaxy mean = code mean = 1.0 (0 pp). One configuration, DeepSeek V4 Pro via Claude Code (superseded), shows Galaxy mean 1.0 vs code mean 0.333 — a 66.7 percentage-point Galaxy-higher difference, verified directly against `.comparisons[score_deepseek_v4_pro_via_claude_code_superseded]` (`galaxy_mean: 1.0`, `code_mean: 0.3333...`, `estimate: 66.667`).

**Observed execution**: the retrieved public Galaxy histories expose 203 distinct analytical creating jobs across the 15 Galaxy runs, of which 31 have failed/error status (`manuscript_findings[finding_execution]`, numerator 31 / denominator 203 — the highest failure count and failure rate of the tasks audited in this batch, ~15%). Job counts range widely per run, from 1 job (e.g. `galaxy_codex_gpt_5_5_r2`) to 52 jobs with 11 failures (`galaxy_codex_gpt_5_6_luna_r3`).

**Auditor interpretation** (this report): the two open_ended_code replicates that scored 0 for the DeepSeek-via-Claude-Code-superseded configuration both submitted the answer "2100," while the one open_ended_code replicate that scored 1 submitted "2118" — and separately, several Galaxy runs across different model configurations submitted "2106" and also scored 1. This indicates the original evaluator accepted more than one numeric value as correct for this task (plausibly reflecting run-to-run stochastic variation in DESeq2/apeglm output that falls within an evaluator tolerance), while "2100" fell outside whatever tolerance or exact-match rule was applied. This is a within-task observation about evaluator behavior; the retained evidence does not include the evaluator's tolerance specification, so this is reported as an unresolved observation, not a finding about scoring correctness.

## 3. The four manuscript Results questions, as applied to this task

**Accuracy and output agreement.** All 30 runs report `original_evaluator_score_field = "accuracy.score"`. Submitted answers cluster around three numeric values — "2106", "2118" (both scoring 1 in the runs sampled), and "2100" (scoring 0 in the two runs sampled) — verified directly for 5 runs. This is a genuine instance of output disagreement across otherwise-scored-correct runs, and it is visible in the underlying evidence rather than smoothed over by the report, which retains the raw per-run answer strings.

**Execution, failures, recovery.** 203 distinct Galaxy analytical jobs / 31 failed, verified against `manuscript_findings[finding_execution]` and against 2 individually sampled high-failure runs: `galaxy_codex_gpt_5_6_luna_r3` (52 jobs / 11 failed, nonzero shell calls 4 — matches table exactly) and `galaxy_deepseek_v4_pro_via_claude_code_superseded_r3` (10 jobs / 8 failed, 0 nonzero shell calls — matches table exactly). Notably, this last run recorded 8 failed jobs out of only 10 total yet still produced the answer "2118" that scored 1 — an example the report correctly does not call "successful recovery," since no `failed_jobs_before_first_supported_result` chronology is populated to establish whether the 8 failures preceded or were incidental to the eventually-submitted answer.

**Solution-route variability.** As in bix-47-q3, most Galaxy runs are marked "unclassified," with one exception: `galaxy_codex_gpt_5_6_luna_r2` is flagged "Datamash." Open_ended_code runs remain uniformly "local shell or script; method unclassified," consistent with `recovered_code/` containing only an `open_ended_code/` subtree (565 files) and no `galaxy/` subtree.

**Token cost, provenance, readability.** Per-model median-ratio token comparisons, verified against `.comparisons`: Codex GPT-5.5 1.10x (evidence 1.104), Codex GPT-5.6 Luna 9.03x (9.026), Codex GPT-5.6 Sol 2.20x (2.201), DeepSeek V4 Pro via Claude Code superseded 2.58x (2.578), DeepSeek V4 Pro via Codex 0.531x (0.5313). All five match the table exactly within stated rounding. This task shows the only sub-1 ratio pair with a large absolute magnitude difference outside DeepSeek-via-Codex; no stage attribution or readability data exist.

**No unresolved disagreement was found** between history_analysis.md and history_analysis_evidence.json for any number checked. The one place where this audit adds interpretation beyond the source report is the cross-run answer-value observation ("2106"/"2118" scored 1, "2100" scored 0) described above — the source report states the raw table values but does not itself remark on the accepted-answer variability; this is noted here as an addition, not a correction.

## 4. Per-condition/model/replicate route table

Spot-verified rows (evidence-JSON field in parentheses):

| Run | Score | Answer | Jobs/failed | Nonzero shell calls | Match? |
|---|---:|---|---:|---:|---|
| `open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r1` | 1.0 | 2118 | null/null (table: unavailable/unavailable) | 0 | matches |
| `open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r2` | 0.0 | 2100 | null/null | 0 | matches |
| `open_ended_code_deepseek_v4_pro_via_claude_code_superseded_r3` | 0.0 | 2100 | null/null | 0 | matches |
| `galaxy_codex_gpt_5_6_luna_r3` | 1.0 | 2106 | 52 / 11 | 4 | matches |
| `galaxy_deepseek_v4_pro_via_claude_code_superseded_r3` | 1.0 | 2118 | 10 / 8 | 0 | matches |

The remaining 25 of 30 table rows were not individually re-verified in this audit; they were read as reported.

## 5. Input sharing, external computation, environment/reproducibility

- Same shared-input-by-name pattern and 6-of-30 zero-staged-input asymmetry as in the other tasks audited in this batch (`input_manifest.json`), unexplained in the retained manifests.
- Environment evidence: a sampled recovered command (`recovered_code/open_ended_code/open_ended_code_deepseek_v4_pro_via_codex_r3/item_51.command.txt`) shows a `micromamba install` invocation for `zlib`/`libxml2` via conda-forge — direct evidence of local environment/dependency management activity in the open_ended_code condition for this run, consistent with a bioinformatics R/DESeq2 workflow.
- Reproducibility: same TLS-verification caveat as the other audited tasks (`audit.limitations`).
- `.analysis_execution.json` marks this directory as machine-generated, consistent with the rest of the batch.

## 6. Verification methods

Checked: `jq 'keys'`, `.runs | length` (30, matches), `.task`, `.manuscript_findings` (all four blocks), `.comparisons` (all ten blocks, cross-checked against Section 2's five score rows and five token-ratio rows — all matched); full `.outcome` and `.derived_metrics` for 5 individually selected runs chosen to cover the discrepant-score model, the highest-failure Galaxy run, and a second high-failure run; `.validation` (`"passed"`, no unresolved issues). Inventoried `job_ledgers/` (30 files), `recovered_code/` (565 files, entirely under `open_ended_code/`), `selected_outputs/` (26 files), and `source_snapshots/` (1075 files). Opened one recovered command file (a `micromamba install` invocation) to confirm genuine recovered content.

Not checked: byte-level re-hashing of any artifact; full transcript replay; independent re-derivation of the 203-job/31-failure aggregate from all 15 Galaxy job ledgers (only 2 were individually sampled); the remaining 25 of 30 route-table rows; the original evaluator's tolerance/matching rule that apparently accepts both "2106" and "2118" as correct (not documented in any retained file); execution of any recovered code.

## 7. Claim-to-evidence pointer list

| Claim | Source |
|---|---|
| 30 observed runs, 5 models x 2 conditions x 3 replicates | `run_manifest.json`; `history_analysis_evidence.json` `.runs` (length 30) |
| Original evaluator score present for 30/30 runs | `.manuscript_findings[finding_accuracy]` |
| 203 distinct Galaxy analytical jobs, 31 failed | `.manuscript_findings[finding_execution]` (31/203) |
| DeepSeek-via-Claude-Code-superseded: Galaxy 1.0 vs code 0.333 (66.7 pp) | `.comparisons[score_deepseek_v4_pro_via_claude_code_superseded]` |
| Per-model input-token median ratios (1.10, 9.03, 2.20, 2.58, 0.531) | `.comparisons[input_tokens_*]` |
| Accepted-answer variability ("2106"/"2118" score 1; "2100" scores 0) | `.runs[].outcome.submitted_answer` and `.original_evaluator_score` for the 5 sampled runs |
| 6 of 30 runs with 0 locally staged inputs | `input_manifest.json` |
| TLS not verified for retrieved bytes | `.audit.limitations` |
| Schema validation passed | `.validation` |

## 8. Missing evidence / open gaps

- No independent experiment-protocol manifest to confirm 3-replicate design intent.
- The original evaluator's exact tolerance rule for accepting "2106"/"2118" but not "2100" is not documented in any retained file; this is an open gap in the evaluation specification, not merely a missing count.
- No recovery-chronology data (`failed_jobs_before_first_supported_result`) exists despite this task showing the highest failure count of the batch (31 jobs, up to 8/10 failed in one run).
- No human-readability review, no monetary cost figures, and no stage-attributed token breakdown exist for this task.
- Reason for the 6-run zero-staged-input asymmetry remains unresolved.

### Abstract-ready paragraph

For BixBench task bix-49-q4, 30 runs (5 model configurations x 2 conditions x 3 replicates) were audited retrospectively, and all 30 carried an original evaluator score under `accuracy.score`. Four of five model configurations recorded identical Galaxy and open_ended_code mean scores (1.0 vs 1.0); one configuration (DeepSeek V4 Pro via Claude Code, superseded) recorded a higher Galaxy-condition mean (1.0 vs 0.333), reflecting two code-condition replicates that submitted a numeric answer the evaluator scored as incorrect. Retrieved public Galaxy histories exposed 203 distinct analytical creating jobs across the 15 Galaxy runs, including 31 jobs in a failed/error state, the highest recorded failure count among the tasks in this batch. Galaxy-to-code median input-token ratios by model ranged from 0.531 to 9.03. These figures describe this single audited task only and do not establish a benchmark-wide condition effect.
