# BixBench: third token-optimization round, October 2026

This supplementary batch contains GPT-5.6 Sol Galaxy-API code runs on the same
50 BixBench Verified-50 tasks, with three replicates (150 selected runs).
It does not replace any previous experiment or trace directory.

Each trace includes the original final answer in
`agent_workspace/codex_output/answer.txt`, prompts, evaluation, usage and model
events. `native_api_usage.json` contains deduplicated provider usage records.
Cached input is included in input tokens; do not add it again.

Full nested tool requests, schemas, replies, job details and parameter checks
are preserved in `galaxy_execution_records.tar.gz`. Extract with
`tar -xzf galaxy_execution_records.tar.gz`; `execution_records_index.json`
lists every sanitized member and its hash. Original scientific input datasets,
downloaded result files, runtime homes and credentials are not uploaded.
Credentials and host-specific paths are redacted; no original source run is
changed. The protocol directory records the MCP implementation, eight skills
and the waiting-only AGENTS instructions used by these workers.

Galaxy used 52.50M, 60.45M and 50.09M input-plus-output tokens; accuracies were
46/50, 46/50 and 45/50. The mean was 54.35M, or 1.53 times the 35.51M-token
Open-ended code baseline. The Open-ended comparison reuses the existing
GPT-5.6 Sol three-replicate records for the same 50 tasks, rather than a new run.
Previous website Galaxy averaged 122.41M tokens (3.45 times Open-ended code).
The earlier local MCP-only selected trial used 85.93M in one replicate (2.42x).
Website CLI was 0.146.0; the local batches used 0.156.0. This package reports
observed batch comparisons, not separate causal effects for individual changes.

Working histories are accessible by link and are not published in Galaxy's
public history list. Existing HF repository visibility is unchanged.
