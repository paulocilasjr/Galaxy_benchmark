# Annotate variant regulatory overlap q1

Start with [history_analysis.md](history_analysis.md).

- [Task metadata](annotate-variant-regulatory-overlap-q1.json): original prompt and text-specified variant.
- [History analysis](history_analysis.md): all 12 replicates, tools and inferred rationale, outcomes, errors, coordinate handling, code differences, resource provenance and external-computation limits.
- [Evidence](history_analysis_evidence.json): dataset/job records and downloaded artifact hashes.
- [Input manifest](input_manifest.json): variant and large external registry references; no common input archive is supplied by this task.
- [Representative code](ccre_query.py) and [Galaxy job](galaxy_job.json): successful ChatGPT-5.5 replicate 2 API-query tool.
- [Recovered code](recovered_code/README.md), `selected_outputs/` and `job_ledgers/`: scripts, commands, small outputs and full per-replicate records.

The histories agree at the reported locus on EH38E1957012 (pELS / Proximal enhancer), with different strengths of execution and release provenance. This is a retrospective audit, not a fresh benchmark execution or hidden-ground-truth score. Large reference files are linked rather than added to Git.
