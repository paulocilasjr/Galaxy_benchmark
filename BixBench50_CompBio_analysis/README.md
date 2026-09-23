# Combined Benchmark Analysis

[Result_table.md](../Result_table.md) contains the three-section synthesis, including exclusive task success, model trade-offs, common software indicators, operational errors and user-defined-tool decisions.

Reproduce from the repository root with Python 3.10+ and NumPy:

```sh
python3 scripts/build_result_tables.py
```

This is an auditor summary, not a benchmark execution. It reads only archived task evidence and authorized aggregate analyses. It does not run recovered code, call Galaxy, open hidden references, or change original scores. No new task-evidence schema conformance is claimed for these aggregate JSON files.

## Files

| File | Contents / drill-down |
| --- | --- |
| [source_manifest.json](source_manifest.json) | Exact source hashes; 150 task evidence paths; included task-scoped run and finding IDs |
| [analysis.json](analysis.json) | `tables`: rendered values/legends; `results`: statistical estimates and token pairs; `runs`: 4,000 run summaries; `cells`: path/answer summaries; `jobs`: deduplicated non-fetch job IDs and source event references |
| [Generator](../scripts/build_result_tables.py) | Eligibility, model selection, normalization, bootstrap, diagnostic regex codebook and cross-checks |
| [Deeper analyses](../scripts/result_table_deep_analysis.py) | Model comparisons, software-family indicators, user-defined-tool request/job linkage, correlation intervals and trace-reviewed mechanism cases |

All source paths are relative to the repository root. Resolve a job's `refs` to the stated task evidence and `event_id`; full parameters and diagnostic excerpts remain there. A run ID is unique only within its benchmark/task. Scores in `runs.score` remain null for all CompBio records. `has_error` is null without detailed Galaxy history evidence. Missing scores/usage are never zero-filled.

## Methods

The primary cross-benchmark set uses three shared supplied GPT labels. DeepSeek versions/harnesses and unpaired Astra remain separate. This label restriction does not establish identical runtime models, reasoning, prompt versions or selection policies. CompBio selections can include earlier campaigns, continuations and recovery runs; primary-turn usage is incomplete campaign cost.

Token ratios compare condition medians of three runs within a task/configuration and require six observed totals. Path agreement requires three observable nonempty fingerprints in both benchmarks, harmonizing the stricter CompBio rule. Galaxy tool-ID fingerprints and code command-vocabulary fingerprints are different instruments; only within-instrument benchmark comparisons are interpreted. Legacy upload jobs remain included, consistent with the archived normalization.

Exploratory confidence intervals use 20,000 cluster resamples, seed 20260922. A SHA-256-derived statistic key makes each random stream deterministic. Resampling preserves all eligible rows in each BixBench capsule or CompBio task. Estimates weight eligible task/configuration cells equally; capsules with multiple questions remain larger. Cross-benchmark contrasts resample the two strata independently. Intervals are pointwise percentile intervals, not adjusted for simultaneous inference. Shared inputs may violate cluster independence; no causal, equivalence, non-inferiority, or confirmatory significance claim is supported.

Error categories are overlapping regex indicators on retained stdout/stderr excerpts, not adjudicated root causes. Missing/truncated diagnostics affect apparent frequency. Deduplication is by benchmark, server and native job ID; the validation block separately checks overlapping native IDs between benchmarks. Run-level burden can count a shared job in multiple linked runs, which describes exposure rather than additional unique jobs. The tables deliberately avoid adding dataset error-state counts to creating-job totals.

User-defined-tool requests are identified by explicit `run_galaxy_udt_and_wait` events, not by custom-looking job names. Matching declared `GalaxyUserTool` IDs to job tool IDs within a run supports linked execution; successful job state remains separate. JSON representations are parsed structurally. YAML-string representations remain explicit linkage gaps rather than being parsed heuristically. Other invocation surfaces and inherited jobs limit exhaustiveness and chronological attribution. Agent statements about missing native tools are reported as statements, not exhaustive catalog audits. The original traces reviewed for specific mechanisms are hashed and line-indexed in the manifest.

Task-description word count is an exploratory pre-execution proxy, not a validated complexity grade. Recorded job count is a post-execution workload measure affected by retries. Correlation intervals use 5,000 cluster resamples with ranks recalculated after each resample; all other new intervals use 20,000 resamples. A nonzero shell exit is a common observable channel but not a common scientific-attempt definition, because Galaxy analysis is often offloaded to server jobs.

## Validation

The generator checks all 150 task evidence hashes against the archived aggregate manifests, unique run keys, binary BixBench scores, all CompBio unknown scores, paired usage denominators, archived median ratios, non-fetch job totals/states and CompBio path summaries. It fails before writing tables if these checks disagree. Output contains no copied stderr or agent instructions; job references point back to original evidence.

The Galaxy proposals in Table X7 are testable integration hypotheses, not an audit of deployed feature availability. Official documentation is linked in that table; benchmark counts and statistical calculations come exclusively from the local archive.
