---
pretty_name: CompBioBench agent traces
license: mit
---

# CompBioBench agent traces

This dataset contains the final 100-answer vectors and primary agent event trace
for 21 completed CompBioBench replicates. It covers Anycode and Galaxy runs for
GPT-5.5, GPT-5.6 Sol, and DeepSeek V4 Pro, plus the completed Luna Anycode runs.
Luna Galaxy runs are not included because they are still in progress.

`replicates.tsv` lists each vector and labels its score as either an official
leaderboard result or a prediction. Each replicate directory contains the exact
`predictions.tsv`, item-level `provenance.tsv`, and one compressed event trace per
question. Galaxy provenance includes an unlisted history link when available.

Downloaded analysis outputs, benchmark inputs, runtime homes, and credentials are
excluded. Traces are sanitized for credentials, account names, and local host
paths. The leaderboard remains the authority for official accuracy.
