# IWC wf_007 runs replaced by the results site (2026-10-12)

On 2026-10-12 the results site replaced all 24 runs of `wf_007_vgp_mitogenome_assembly` (VGP mitochondrial genome assembly). Each was rerun on read set ERR12833637: 4 model configurations × 2 conditions × 3 replicates.
- **Site commit:** lab repository `goeckslab/galaxy-agent-benchmark`, commit `ff9c4f5` ("Publish wf007 ERR12833637 results, traces and token accounting").
- **When the new runs ran:** 2026-10-08 to 2026-10-11.
- **Where their traces are:** Hugging Face dataset `goeckslab/galaxy-agent-benchmark-run-traces`, under `iwc/run_traces_october2026_wf007_ERR12833637`, at revision `3cd47d3`.

This archive holds the traces, Galaxy histories and derived records of the **superseded** runs only. The replacement is a **values-only** update.

**Taken from the site for the 24 new runs:**
- the score the site shows (strand-independent 31-mer multiplicity F1);
- the token usage (input including cached, cached input, output, reasoning output).

**Not available for the new runs:** anything derived from a trace, namely tool calls, Galaxy jobs, execution errors, actions, interface replies, UDT definitions and run evidence. The new runs count as runs without a trace. The superseded runs' records are removed from every trace-derived table the figures read, so they are not attributed to the runs that replaced them.

## Files

| File | Contents |
|---|---|
| `runs.csv` | One row per run (24): model configuration, condition, replicate, the new run's identifiers, score and token usage, start and end times, and the superseded archive run and its score. |
| `sources.json` | The lab repository commit, the files read and their SHA-256, and where the new traces are. |
| `build_record.py` | Writes both files from the lab repository at the pinned commit (GitHub CLI with read access). The task's reference outputs, in the same folder of the lab repository, are not read. |

## Checks in `build_record.py`

- The commit's record of the superseded runs' usage (`raw_usage.json`, `previous`) equals the archive's per-run token table for all 24 runs. This confirms which archive run each new run replaces.
- The new runs' usage equals the commit's per-run token table (`wf007_token_usage.tsv`).
- One row per model configuration, condition and replicate.

`figures/make_scored_runs.py` also checks each new score against the value on the live site's wf_007 page (snapshot of 2026-10-12, `figures/site_snapshot/iwc_runs.json`). On that date the site differed from the previous snapshot (2026-10-07) only in these 24 runs.

## How the figures use it (`figures/replaced_runs.py`)

- **Scores.** `figures/scored_runs.csv` carries the new scores. For these runs, `run_id` names the new run, `archive_score` keeps the superseded run's score, and `score_source` records the replacement. `budget_matched` and `udt_requested_archive` are empty, because they were recorded only for the superseded runs.
- **Tokens.** `replace_tokens()` puts the new usage in place of the superseded runs' usage in the per-run token table and empties its trace-derived counts.
- **Trace-derived tables.** `drop_replaced()` and `replaced_evidence()` remove the superseded runs from:
  - the Galaxy call and coverage tables;
  - the execution-error and action workbooks;
  - the failure episodes and UDT methods;
  - the run evidence.
- **Failed Galaxy requests.** Fig. 3f drops the superseded runs' 43 failed requests (7,141 → 7,098); `superseded_failures()` gives their classes, for tables that hold only counts.
- **"Inspected tools never run".** `superseded_inspection()` takes the superseded runs' share (58 tools inspected, 19 never run) out of the IWC count of this measure. It counts the share with the same rule as `manuscript_material/scripts/build_data.py`, which reproduces the archive's IWC total (788 and 418).

The derived tables upstream of the figures are not rebuilt; they still describe the superseded runs. Those tables are `manuscript_narrative/`, `manuscript_material/` and the run summaries. Their full rebuild would need the new traces and Galaxy histories.

## Effect

Under the 0.99 output-agreement rule, 20 of the 24 superseded runs counted as correct, against 9 of the 24 new runs:
- **Galaxy:** 11 → 7;
- **custom code:** 9 → 2.

Many new runs score 0.986–0.989, just under the rule. Mean agreement rose from 0.869 to 0.948. wf_007 input tokens fell from 229.1M to 228.3M in total.
