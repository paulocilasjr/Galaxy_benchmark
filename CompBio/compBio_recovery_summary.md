# CompBio evidence recovery

Recovered task prompts from nested task metadata and 2486 primary-turn usage records from retained traces. Prior evidence/reports remain under each task's `versions/pre_compbio_synthesis/`.

Additional read-only retrieval retained 21 prediction vectors and provenance tables, five collection indexes, the dated campaign registry and the Astra submission/vector. 9 advertised vector hashes disagree with downloaded bytes; 3 Luna Galaxy vectors are absent from the replicate archive. All available parsed vector answers match the archived task answers.

**Score-source conflicts**

| Campaign | replicates.tsv | Dated site metadata |
| --- | --- | --- |
| sol-galaxy-r1 | 92 (predicted leaderboard) | 93 (official_labelled) |
| sol-galaxy-r3 | 92 (predicted leaderboard) | 91 (official_labelled) |



**Unresolved vector hashes**

| Campaign / model | Downloaded vector | Hash status |
| --- | --- | --- |
| galaxy-gpt55 | source_snapshots/aggregate_metadata/compbiobench/replicates/galaxy-gpt55/predictions.tsv | match |
| galaxy-gpt55-r2 | source_snapshots/aggregate_metadata/compbiobench/replicates/galaxy-gpt55-r2/predictions.tsv | mismatch |
| galaxy-gpt55-r3 | source_snapshots/aggregate_metadata/compbiobench/replicates/galaxy-gpt55-r3/predictions.tsv | mismatch |
| gpt55-anycode-jul30 | source_snapshots/aggregate_metadata/compbiobench/replicates/gpt55-anycode-jul30/predictions.tsv | match |
| gpt55-anycode-r1 | source_snapshots/aggregate_metadata/compbiobench/replicates/gpt55-anycode-r1/predictions.tsv | mismatch |
| gpt55-anycode-r2 | source_snapshots/aggregate_metadata/compbiobench/replicates/gpt55-anycode-r2/predictions.tsv | mismatch |
| sol-galaxy-r1 | source_snapshots/aggregate_metadata/compbiobench/replicates/sol-galaxy-r1/predictions.tsv | match |
| sol-galaxy-r2 | source_snapshots/aggregate_metadata/compbiobench/replicates/sol-galaxy-r2/predictions.tsv | mismatch |
| sol-galaxy-r3 | source_snapshots/aggregate_metadata/compbiobench/replicates/sol-galaxy-r3/predictions.tsv | mismatch |
| sol-anycode-r1 | source_snapshots/aggregate_metadata/compbiobench/replicates/sol-anycode-r1/predictions.tsv | match |
| sol-anycode-r2 | source_snapshots/aggregate_metadata/compbiobench/replicates/sol-anycode-r2/predictions.tsv | match |
| sol-anycode-r3 | source_snapshots/aggregate_metadata/compbiobench/replicates/sol-anycode-r3/predictions.tsv | match |
| codex-ds-v4pro-galaxy-r1 | source_snapshots/aggregate_metadata/compbiobench/replicates/codex-ds-v4pro-galaxy-r1/predictions.tsv | mismatch |
| codex-ds-v4pro-galaxy-r2 | source_snapshots/aggregate_metadata/compbiobench/replicates/codex-ds-v4pro-galaxy-r2/predictions.tsv | match |
| codex-ds-v4pro-galaxy-r3 | source_snapshots/aggregate_metadata/compbiobench/replicates/codex-ds-v4pro-galaxy-r3/predictions.tsv | match |
| codex-ds-v4pro-anycode-r1 | source_snapshots/aggregate_metadata/compbiobench/replicates/codex-ds-v4pro-anycode-r1/predictions.tsv | match |
| codex-ds-v4pro-anycode-r2 | source_snapshots/aggregate_metadata/compbiobench/replicates/codex-ds-v4pro-anycode-r2/predictions.tsv | mismatch |
| codex-ds-v4pro-anycode-r3 | source_snapshots/aggregate_metadata/compbiobench/replicates/codex-ds-v4pro-anycode-r3/predictions.tsv | mismatch |
| luna-galaxy-r1 | Absent | unavailable |
| luna-galaxy-r2 | Absent | unavailable |
| luna-galaxy-r3 | Absent | unavailable |
| luna-anycode-r1 | source_snapshots/aggregate_metadata/compbiobench/replicates/luna-anycode-r1/predictions.tsv | match |
| luna-anycode-r2 | source_snapshots/aggregate_metadata/compbiobench/replicates/luna-anycode-r2/predictions.tsv | match |
| luna-anycode-r3 | source_snapshots/aggregate_metadata/compbiobench/replicates/luna-anycode-r3/predictions.tsv | match |
| codex_gpt_6_astra | source_snapshots/aggregate_metadata/compbiobench/run_traces_compbiobench_codex_gpt6_astra/predictions.tsv | match |




No item-level correctness was recovered. Format-validation logs are not evaluator scores. The older README claims only 21 completed replicates and omits Luna Galaxy; newer indexes and workbook enumerate 24 paired-condition replicates plus Astra. Both descriptions are preserved; the workbook/index inventory governs this audit.

Reproduce with `python3 scripts/audit_compbio_overview.py --validate` from the repository root. [Numerical audit](compBio_overview_audit.json), [path analysis](solution_path_consistency_analysis.py), [path results](solution_path_consistency_results.json), [source recovery](compBio_recovery_summary.md), [source manifest](source_snapshots/aggregate_metadata/manifest.json), and [task packages](analysis/) retain the evidence.
