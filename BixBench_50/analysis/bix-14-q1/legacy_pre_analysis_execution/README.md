# bix-14-q1 history audit

Start with [history_analysis.md](history_analysis.md) for the four-model, twelve-history comparison.

- [Task metadata](bix-14-q1.json)
- [Structured provenance and validation](history_analysis_evidence.json)
- [Example recovered Python payload](carrier_fraction.py) and its [Galaxy job](galaxy_job.json)
- [All recovered custom code](recovered_code/manifest.json)
- [Public input capsule](CapsuleFolder-7718a922-ce2c-4e59-900b-84fe06050ce6.zip)

The explicit cohort result in four histories is 30/41 (73.17%). Other histories contain counts, a broader denominator, or incomplete cohort scope; see the report before comparing results. All original workbook uploads were shared from one source history. No new Galaxy analysis jobs were run for this audit.

Recovered code is archival evidence, including failed versions, not newly authored or tested production code. Shell files preserve Galaxy command paths that are not portable. Python bodies extracted from failed heredocs must be interpreted with their original shell commands. Do not infer original agent actions from the local checks performed during this audit.
