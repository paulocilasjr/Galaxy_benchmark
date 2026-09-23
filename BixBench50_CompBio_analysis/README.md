# Combined Benchmark Analysis

[Result_table.md](../Result_table.md) contains the four-section synthesis (BixBench50, CompBio, IWC, combined), including exclusive task success, model trade-offs, common software indicators, operational errors, user-defined-tool decisions and the Galaxy-native IWC stratum. The directory name predates IWC and is kept so existing links resolve.

Reproduce from the repository root with Python 3.10+ and NumPy:

```sh
python3 scripts/build_result_tables.py
```

This is an auditor summary, not a benchmark execution. It reads only archived task evidence and authorized aggregate analyses. It does not run recovered code, call Galaxy, open hidden references, or change original scores. No new task-evidence schema conformance is claimed for these aggregate JSON files.

## Files

| File | Contents / drill-down |
| --- | --- |
| [source_manifest.json](source_manifest.json) | Exact source hashes; 160 task evidence paths; included task-scoped run and finding IDs |
| [analysis.json](analysis.json) | `tables`: rendered values/legends; `results`: statistical estimates, token pairs and `iwc` agreement contrasts; `runs`: 4,240 run summaries; `cells`: path/answer summaries; `jobs`: deduplicated non-fetch job IDs and source event references |
| [Generator](../scripts/build_result_tables.py) | Eligibility, model selection, normalization, bootstrap, diagnostic regex codebook and cross-checks |
| [Deeper analyses](../scripts/result_table_deep_analysis.py) | Model comparisons, software-family indicators, user-defined-tool request/job linkage, correlation intervals and trace-reviewed mechanism cases |

All source paths are relative to the repository root. Resolve a job's `refs` to the stated task evidence and `event_id`; full parameters and diagnostic excerpts remain there. A run ID is unique only within its benchmark/task. Scores in `runs.score` remain null for all CompBio records. `has_error` is null without detailed Galaxy history evidence. Missing scores/usage are never zero-filled.

## Methods

IWC is the workflow-derived stratum; task origin is not a randomized intervention. Scores and usage are read from `IWC/iwc_scientific_audit.json` because task evidence leaves those fields empty. IWC agreement is continuous (0-1), never converted into acceptance or pooled with BixBench acceptance; its final chat message is not the scored answer. Tables I1/I2 use the same nine-task population, excluding host removal as an exploratory sensitivity choice, not a prespecified endpoint. Replicate means are averaged equally across tasks within configuration. The all-configuration available-pair sensitivity in I4 weights 39 task/configuration cells equally; host removal has only three configurations, so that row is not equally task-weighted. The generator checks estimates, job totals/states, token ratios and recovery-candidate counts against the IWC audit. Recorded helper lists omit the UDT helper, and no named-helper requests were detected; alternative custom-code interfaces are not ruled out. The Tool Shed classifier excludes `UTILITY_REPOS` text/table utilities but does not establish complete native-tool coverage or sufficiency.

The descriptive cross-benchmark set uses three shared supplied GPT labels. DeepSeek versions/harnesses and unpaired Astra remain separate. This label restriction does not establish identical runtime models, reasoning, prompt versions or selection policies. CompBio selections can include earlier campaigns, continuations and recovery runs; primary-turn usage is incomplete campaign cost.

Token ratios compare condition medians of three runs within a task/configuration and require six observed totals. Path agreement requires three observable nonempty fingerprints in all three benchmarks, harmonizing the stricter CompBio rule. Galaxy tool-ID fingerprints and code command-vocabulary fingerprints are different instruments; only within-instrument benchmark comparisons are interpreted. Legacy upload jobs remain included, consistent with the archived normalization.

Exploratory confidence intervals use 20,000 cluster resamples, seed 20260922. A SHA-256-derived statistic key makes each random stream deterministic. Resampling preserves all eligible rows in each BixBench capsule, CompBio task or IWC task. Estimates weight eligible task/configuration cells equally; capsules with multiple questions remain larger. Cross-benchmark contrasts resample the two strata independently. Intervals are pointwise percentile intervals, not adjusted for simultaneous inference. Shared inputs may violate cluster independence; no causal, equivalence, non-inferiority, or confirmatory significance claim is supported.

Error categories are overlapping regex indicators on retained stdout/stderr excerpts, not adjudicated root causes. Missing/truncated diagnostics affect apparent frequency. Deduplication is by benchmark, server and native job ID; the validation block separately checks overlapping native IDs between benchmarks. Run-level burden can count a shared job in multiple linked runs, which describes exposure rather than additional unique jobs. The tables deliberately avoid adding dataset error-state counts to creating-job totals.

User-defined-tool requests are identified by explicit `run_galaxy_udt_and_wait` events, not by custom-looking job names. Matching declared `GalaxyUserTool` IDs to job tool IDs within a run supports linked execution; successful job state remains separate. JSON representations are parsed structurally. YAML-string representations remain explicit linkage gaps rather than being parsed heuristically. Other invocation surfaces and inherited jobs limit exhaustiveness and chronological attribution. Agent statements about missing native tools are reported as statements, not exhaustive catalog audits. The original traces reviewed for specific mechanisms are hashed and line-indexed in the manifest.

Task-description word count is an exploratory pre-execution proxy, not a validated complexity grade. Recorded job count is a post-execution workload measure affected by retries. Correlation intervals use 5,000 cluster resamples with ranks recalculated after each resample; all other new intervals use 20,000 resamples. A nonzero shell exit is a common observable channel but not a common scientific-attempt definition, because Galaxy analysis is often offloaded to server jobs.

## Validation

The pre-revision report is preserved at [report_revisions/Result_table.pre_claim_revision_20260923.md](report_revisions/Result_table.pre_claim_revision_20260923.md). It is historical, not the current interpretation. Run `python3.12 -m unittest analysis_execution.tests.test_result_tables` to check source hashes, rendered table values, local links, denominator alignment and claim safeguards. Python 3.12 has NumPy installed in this workspace; other Python versions need that dependency separately.

The generator checks all 160 task evidence hashes against the archived aggregate manifests (IWC against its scientific-audit source index), unique run keys, binary BixBench scores, all CompBio unknown scores, paired usage denominators, archived median ratios, non-fetch job totals/states and CompBio path summaries. It fails before writing tables if these checks disagree. The analysis JSON contains retained diagnostic excerpts and selected source-indexed agent statements as evidence, not instructions or independent adjudication; full job references resolve to the original evidence.

The Galaxy proposals in Table X7 are testable integration hypotheses, not an audit of deployed feature availability. Official documentation is linked in that table; benchmark counts and statistical calculations come exclusively from the local archive.
