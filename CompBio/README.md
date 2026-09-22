# CompBio retrospective analysis

Start with [compBio_overview.md](compBio_overview.md) or the full [Results draft](result_section_compbio.md). The four Results sections and eleven principal tables parallel BixBench-50, with explicit unavailable endpoints where CompBio does not supply equivalent evidence.

- [Numerical audit and aggregate manifest](compBio_overview_audit.json)
- [Solution-path analysis](solution_path_consistency_analysis.py) and [results](solution_path_consistency_results.json)
- [Source recovery and unresolved discrepancies](compBio_recovery_summary.md)
- [100 task packages](analysis/)

The paired comparison contains 2,400 records: 100 tasks, four supplied model configurations, two conditions and three replicate labels. Another 100 GPT-6 Astra records have no Galaxy counterpart. Final vectors can incorporate continuation/recovery campaigns and are not documented independent first attempts.

## Reproduction

Run from the repository root with the existing `analysis_execution/requirements.txt` dependencies:

```sh
python3 scripts/enrich_compbio_evidence.py
python3 scripts/audit_compbio_overview.py --validate
python3 -m unittest discover -s analysis_execution/tests -v
```

These commands read preserved evidence, recover metadata/usage, and recompute reports. They do not execute archived agent code or regrade answers. Exact earlier task reports and evidence are preserved under each task's `versions/pre_compbio_synthesis/` directory. The aggregate audit can also be regenerated directly from the enriched evidence with the second command alone.

Supplemental source collection is reproducible separately; both commands prompt privately for an authorized Hugging Face token:

```sh
python3 scripts/fetch_compbio_analysis_metadata.py
python3 scripts/fetch_compbio_analysis_metadata.py --details
```

Remote `main` may change. The retained manifests include retrieval times, hashes and source URLs; rerunning a fetch is a new snapshot, not proof that the original bytes remain available.

## Interpretation

Original item-level evaluator scores are absent. Aggregate scores labelled official, predicted scores, unresolved submission hashes and source-version conflicts remain separate. Answer-text consistency is not accuracy. Token totals describe the archived primary turn; earlier campaigns and separate subagents are not established. Galaxy jobs, shell exits and scientific attempts are different units. The audit does not certify Galaxy-only execution or measured improvements in human readability.
