# Per-call Galaxy interface activity (agent fidelity)

Per-call table of MCP tool calls in Galaxy-condition runs, built from archived agent traces. The extraction is read-only: it reads `manuscript_material/source_data/derived/run_summaries.jsonl.gz` and the trace files that table points to. It does not read `ground_truth/`, run agent code or contact any server.

Reproduce (Python 3.12 + pandas):

```
python extract_calls.py   # writes calls.csv.gz, salvaged_calls.csv.gz, run_coverage.csv, _coverage_meta.json
python summarize.py       # writes summary.json, tool_mismatch_rates.csv
```

The event parsing and the legacy failure classifier are copied from `analysis_reports/galaxy_improvement_20260924/v2_trace_friction/extract.py`. The legacy classifier is kept as `extract_class`, so call and failure counts match `run_summaries` exactly.

## Files

| file | content |
|---|---|
| `calls.csv.gz` | One row per MCP tool call (69,812 rows). |
| `salvaged_calls.csv.gz` | 4 MCP calls recovered from corrupted trace lines. They are left out of `calls.csv.gz` so its totals still match `run_summaries`. Same columns. |
| `summary.json` | Results per benchmark: status counts, provenance, reconciliation, non-Galaxy failures, outage signatures and per-tool mismatch rates. |
| `tool_mismatch_rates.csv` | Mismatch rate per tool for each benchmark (version-stripped `tool_id` with at least 20 `run_galaxy_tool_and_wait` calls). |
| `run_coverage.csv` | One row per parsed run: parsed vs expected `n_mcp`/`n_mcp_fail`, salvage counts and trace diagnostics. |
| `_coverage_meta.json` | Intermediate file: Galaxy run counts and the 12 runs that have no trace. |

## Coverage

- `run_summaries` lists 2,070 Galaxy-condition runs. 2,058 of them have a primary trace, and all 2,058 were parsed with no file errors. The 12 runs with no trace are all CompBio (10 `codex_gpt_5_6_luna`, 2 `codex_gpt_5_5`); they are listed in `summary.json -> coverage.runs_without_trace`.
- Codex logs: 1,908 runs (1,431 `codex_events.jsonl` + 477 `codex_events.jsonl.gz`). Claude Code logs (`claude_events.jsonl[.gz]`, model `deepseek_v4_pro_via_claude_code_superseded`, BixBench50 only): 150 runs (137 gz + 13 plain).
- Runs by benchmark: BixBench50 750 (600 Codex + 150 Claude Code), CompBio 1,188, IWC 120.
- Reconciliation is exact for every run. Per benchmark, `n_mcp` is 17,550 / 48,297 / 3,965 = 69,812, and legacy failures are 1,900 / 5,116 / 373 = 7,389. No run has a count mismatch.

## Parsing rules

- **Codex**: one call = one `item.completed` event whose `item.type == "mcp_tool_call"`. `item.started` is ignored. `line` is the physical line number in the decompressed file (read with `newline='\n'`, so it matches `sed -n Np`). The fields used are `server`, `tool`, `arguments`, `status` (completed/failed) and `error` (`{message}`) on the item. The payload is `result.structured_content`; if that is absent, the parser falls back to the JSON-parsed `result.content[].text`.
- **Claude Code**: one call = one assistant `tool_use` block named `mcp__<server>__<tool>`. It is paired by `tool_use_id` with the user `tool_result`. `line` is the `tool_use` line, as in extract.py, and `result_line` is the result line. The payload is the JSON-parsed result text (Claude Code does not log `structured_content`). `call_status = failed` when `is_error` is true. Every call had a result.
- Lines that are not valid JSON are skipped, as extract.py does.

## Namespaces

Galaxy interface servers: `bixbench_galaxy_execute`, `bixbench_galaxy_wait` (BixBench50); `galaxy_execute`, `galaxy_wait` (CompBio); `iwc_galaxy_execute`, `iwc_galaxy_wait` (IWC). Galaxy interface tools: `run_galaxy_tool_and_wait`, `run_galaxy_udt_and_wait`, `search_galaxy_tools`, `inspect_galaxy_tool`, `inspect_galaxy_history`, `wait_for_galaxy_jobs`, `inspect_archive_inventory`, `peek_galaxy_dataset`, `stage_workspace_file`.

Non-Galaxy MCP activity (307 calls):

- Codex built-ins `list_mcp_resources` and `list_mcp_resource_templates`. Codex logs these under server `codex`, or under the server named in the arguments, including the Galaxy servers (35 calls).
- `codex_apps` connectors (`github.*`, `hugging_face.*`; 51 calls, CompBio only).
- Two server names that do not exist, used by agents: `galaxy` (1 call) and `iwc-galaxy-execute` (2 calls).

`galaxy_namespace` is true when the server is a Galaxy server. `galaxy_server` is true when the server is a Galaxy server and the tool is not a Codex built-in.

## Columns (`calls.csv.gz`)

| column | meaning |
|---|---|
| benchmark, task, run_id, model, replicate | Run identity, from run_summaries. |
| trace_format | `codex` or `claude_code`. |
| line, result_line | Line of the call in the decompressed trace, and line of its result (same as `line` for Codex). |
| server, tool | MCP server namespace and tool name. |
| galaxy_namespace, galaxy_server | See Namespaces. |
| call_index_in_run | 0-based order of the call among the run's `galaxy_server` calls. Null for non-Galaxy calls. |
| prior_same_tool_calls | Number of earlier Galaxy calls in the run with the same `tool` and the same `tool_id_full` (null matches null; for example `search_galaxy_tools` counts earlier searches). 0 means a first attempt. |
| prior_same_tool_calls_base | Same count, keyed on `tool_id_base`, so a retry under a different version still counts as a retry. |
| call_status | Transport-level outcome: `completed` or `failed` (Codex `item.status`; Claude `is_error`). |
| client_rejected | Claude Code returned `<tool_use_error>` (unknown tool name, or arguments that failed schema validation). The call never reached Galaxy. |
| result_status | `status` field of the structured result (for example `ok`, `validation_parameter_mismatch`, `parameter_mismatch`, `provenance_mismatch`, `failed`, `validation_failed`, `submission_failed`, `udt_creation_failed`). Null when the result has no JSON payload or no status (`inspect_galaxy_history` and `inspect_archive_inventory` return no status). |
| submitted, validation_status | From the structured result. |
| prov_status | `parameter_provenance.status`: `matched`, `mismatch`, `no_explicit_non_dataset_parameters` or `not_comparable`. |
| prov_stage | `validation` when mismatches come from the pre-submission check (top-level `mismatches`/`missing_paths`), `post_run` when they come from per-job comparison (`parameter_provenance.jobs[]`). |
| checked_parameter_count | `parameter_provenance.checked_parameter_count`. |
| n_mismatches, n_substituted, n_missing_paths | Requested-vs-resolved mismatches, summed over jobs for post-run checks. `n_substituted` counts mismatches whose `resolved` value is not null (Galaxy used a different value); the rest resolved to null. `n_missing_paths` counts requested paths absent from the resolved state. |
| mismatch_paths | Sorted, `;`-joined mismatch paths (capped at 400 characters). |
| dataset_prov_status | `provenance.status` for dataset inputs (intended vs resolved HDAs). This is separate from parameter provenance; `result_status = provenance_mismatch` can come from either. |
| tool_id_full, tool_id_base, tool_version | Requested `tool_id` from the arguments, falling back to the result's `tool_id`. For Tool Shed IDs (`.../repos/owner/repo/tool/version`), `tool_id_base` drops the version segment. Built-in IDs (for example `Cut1`) are unchanged. Malformed or hallucinated IDs are kept as given. For UDT calls, the tool id is `representation.id` (or the job's `tool_id`), with no version split. |
| udt | Call is `run_galaxy_udt_and_wait`. |
| n_jobs, job_ids, job_states, any_job_error | From the result's `jobs[]` list. States are `;`-joined. `any_job_error` means some job is in state `error` or `failed`. |
| job_failure_phases, job_exit_codes | `jobs[].failure_diagnostic.phase` and `.exit_code`. |
| has_error_text, error_excerpt | First 240 characters (whitespace normalised) of the error and diagnostic text, joined with ` \| ` in this order: transport error message; `error`; `errors` (validation); job `failure`/stderr (first 2); `phase=...` when a failed job has no message; `failure_summary`; `history_error`; `failed_input`. For non-JSON results, the result text when the call failed or the text starts with `Error`, `<tool_use_error>` or `MCP server`. |
| outage_sig_in_result | Error or result text matches `no destinations are available\|no execution destination\|training_tag_small_rule` (case-insensitive). |
| outage_sig_linked | One of this call's job ids or output dataset ids appears in a shell-output line (Codex `command_execution`, Claude `Bash` result) that carries the signature. If that line has no ids, ids from the shell command itself are used. |
| run_outage_sig | The signature appears anywhere in the run's trace. |
| chars_returned | Length of the text returned to the agent (the error message when there is no result). |
| elapsed_seconds | From the structured result. |
| extract_class, extract_fail | Legacy classification from extract.py (`ok`/`fail`/`job_error`/`start_timeout`). `extract_fail` (class is not `ok`) sums to run_summaries `n_mcp_fail`. |

## Reconciliation and failure definitions

- `extract_fail` reproduces the 7,389 failed calls exactly (1,900 / 5,116 / 373).
- The legacy definition counts a call as failed if any of these hold: an error flag; an `error`, `failure_summary` or `errors` field; a status in a fixed fail set; or a job in state error/failed.
- The legacy definition counts these as **not failed**:
  - all 3,709 `validation_parameter_mismatch`, 930 `parameter_mismatch` and 168 `provenance_mismatch` tool runs;
  - 9 `workspace_staging_failed` UDTs;
  - 330 `dataset_not_ready` and 28 `history_mismatch` peeks;
  - 604 Codex calls with `item.status == "failed"` whose error came back as result text (`Error executing tool ...`, for example pydantic argument validation or missing workspace files) with `error: null`.
- `summary.json` reports `transport_failed_calls` (872), `transport_failed_not_counted_by_extract` (604) and `failed_calls_union` (7,993 = legacy failures plus transport failures).

## Key caveats

1. **`checked_parameter_count == 0` is not "unchecked".** Every `ok` tool run with a count of 0 has `prov_status = no_explicit_non_dataset_parameters`: the request had only dataset inputs (for example xlsx2tsv, csv_to_tabular, samtools_idxstats). No `ok` tool run has a null count.
2. **Post-run parameter mismatches never come back as `ok`.** They surface as `parameter_mismatch`, `provenance_mismatch` or `failed` (`post_run_submitted_and_result_ok = 0`). Validation-stage mismatches (`validation_parameter_mismatch`) were not submitted.
3. **Outage signatures do not appear in MCP results.** The strings "No destinations are available to fulfill request: training_tag_small_rule" are visible only in agent shell (BioBlend) output, agent messages and web searches, all in CompBio.
   - The interface reports these jobs as `failed` with `failure_diagnostic.phase = pre_execution_or_command_rendering`, `command_line_rendered = false`, no stderr, and `failure_summary = <job>=error`.
   - So `excerpt_matches_signature = 0` in every benchmark.
   - `summary.json -> failed_udt_outage_signature` gives proxies: calls linked through ids, calls in runs whose trace has the signature, and pre-execution-phase failures.
   - The pre-execution phase is not specific to the outage; it also covers UDT command-template errors.
   - ID linking is a lower bound: agents inspected only some failed datasets.
4. **Claude Code results** are parsed from text. One result exceeded Claude Code's output limit and was spilled to a file, so its status is null. 33 Claude calls in the Galaxy namespace were rejected client-side: 24 called `wait_for_galaxy_jobs` on the execute server, which does not expose it, and 9 had input-schema errors. They count as MCP calls and failures, consistent with extract.py.
5. **Trace defects.** 1,573 lines could not be parsed:
   - 1,526 come from the 150 `deepseek_v4_pro_via_codex` BixBench traces: 920 interleaved stderr lines ("Reading prompt from stdin...", `codex_core` ERROR logs and their continuation lines) and 606 `command_execution` records whose JSON was broken by secret redaction (`GALAXY_API_KEY=[REDACTED]"...`).
   - 25 IWC `command_execution` records (`env | rg galaxy|api`) were broken the same way by redaction.
   - The rest are Codex JSON records interleaved with or truncated by other records (bix-26-q3 `codex_gpt_5_5` r1–r3, plus 2 lines in a `codex_gpt_5_6_luna` run) and 1 Claude Code record.
   - Every unparsable line that contains `mcp_tool_call` (Codex; 22 lines, 13 of them stderr) or `mcp__` (Claude; none) was inspected. 4 complete MCP completion records were recovered from them (`salvaged_calls.csv.gz`, bix-26-q3 `codex_gpt_5_5` r1–r3). 4 truncated MCP completion fragments could not be recovered. Redaction did not break any MCP record.
   - 16 stderr records show MCP attempts that the Codex client rejected before dispatch (3 calls to a nonexistent tool `search_galaxy_tool`, 13 with unparsable arguments). They are not MCP items and are not in the table.
6. **Mismatch rates** (`tool_mismatch_rates.csv`) use all `run_galaxy_tool_and_wait` calls for the tool as the denominator. `rate_among_checked` uses only calls that returned a `parameter_provenance` block. `param_prov_mismatch` combines the validation and post-run stages; `dataset_prov_mismatch` and `any_prov_mismatch` are reported separately.
7. `prior_same_tool_calls` counts repeat calls; it does not prove intent to retry. An identical repeat can be a deliberate second analysis.
