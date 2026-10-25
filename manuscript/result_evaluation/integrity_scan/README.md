# Answer-source scan (preliminary)

The case studies for Fig. 3 found agents that looked up published benchmark answers:
- custom-code runs on `conservation-lookup-q1` copied answers from the Hugging Face dataset `amanutej/trustworthy-biology-agents-traces`;
- DeepSeek V4 Pro Galaxy runs on `bix-30-q3` printed the BixBench `"ideal"` answer from `futurehouse/BixBench` before answering.

`scan_answer_sources.py` reads the agent trace of every scored run in `figures/scored_runs.csv` and flags:
- **`source`:** the trace mentions a published-answer source (`futurehouse/BixBench`, `trustworthy-biology-agents-traces`, `compbiobench-results`, `compbiobench-submissions`, `compbiobench-leaderboard`);
- **`ideal`:** the trace contains a printed BixBench `"ideal": "…"` answer field.

The output is `answer_source_scan.csv`, one row per run.
This is a pattern scan, not an audit.
A `source` flag can mean only that the run queried the source; for example, the CompBioBench leaderboard returns only metadata.
Each flagged run still needs a check of whether it obtained an answer, and whether that answer was the one it submitted.

Runs without an archived trace are listed with `trace = missing`:
- 12 CompBioBench Galaxy runs;
- the 24 IWC `wf_007` runs, which the results site replaced on 2026-10-12 with reruns the archive does not hold (`runs/IWC/replacement_wf007_20261012/`).

When a run folder keeps more than one trace, every attempt is scanned.
