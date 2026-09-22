---
pretty_name: BixBench July 6 Codex run traces
license: mit
---

# BixBench July 6 Codex Run Traces

This dataset contains sanitized run traces for the July 6 Codex
BixBench-Verified-50 experiment used by the repository website.

The package contains the 600 official item-grouped traces referenced by
`bixbench/run_traces_july6_codex/index.json`:

- `anycode_nongalaxy_skills`: 150 traces
- `anycode_without_skills`: 150 traces
- `galaxy_strict_skills`: 150 traces
- `galaxy_strict_without_skills`: 150 traces

Included files are limited to prompts, task metadata, final answers,
evaluation and usage records, Codex event logs, skill inventories, and Galaxy
job/history/UDT evidence. Input datasets, downloaded output datasets, local
Codex home state, private verifier/source rows, and API-key files are excluded.
Potential token/API-key fields in copied text files are redacted.

Package summary:

- files copied: 24389
- copied bytes: 375973982
- redacted files: 5876
- skipped data files: 87084
- skipped secret/local files: 0
