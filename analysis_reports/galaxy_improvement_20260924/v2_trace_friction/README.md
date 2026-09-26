# Trace-level friction and root-cause analysis (v2)

Supports `../../../Galaxy_improvement_report.md`. Reads archived traces only; runs no agent code and contacts no Galaxy server.

Run from this directory, in order:

1. `python3 extract.py` — parses every primary trace listed in `BixBench50_CompBio_analysis/analysis.json`; writes `run_summaries.jsonl` (one record per run, including each failed Galaxy MCP call) and compact per-run call logs under `logs/` (~180 MB, not retained here).
2. `python3 taxonomy.py` — classifies failed Galaxy MCP calls (A1–A8 pre-submission, B1–B5 post-submission); writes `cat_tool.json`, `per_run_friction.json`, `friction_examples.json`.
3. `python3 ledger.py` — primary/secondary root cause for all 246 rejected BixBench runs and the 8 IWC runs scoring < 0.5; writes `ledger.json`, `ledger_table.md`.
4. `python3 variability.py` — replicate-variability mixed cells and divergence mechanisms (report addendum).
5. Mechanism scripts (each prints its tables): `a1_mech.py` (history-context schema failures), `mismatch.py` and `mm_sub.py` (requested-vs-resolved parameter mismatches), `b2.py` (failed-job diagnostic phases, resubmission behaviour, UDT statuses), `a5_origin.py` (invalid-ID origins), `discovery.py` (tool-discovery burden), `shell_galaxy.py` (BioBlend/raw-API shell usage).

`ledger.py` encodes adjudications derived from the trace review described in the report; the predicates are explicit so each assignment can be audited.
