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
