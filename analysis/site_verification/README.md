# Archive against the public results site

`verify_against_site.py` fetches the three results pages and compares them with the archive. The pages are the IWC benchmark (`iwc/index.html` and its item pages), BixBench-Verified-50 (`index.html#bixbench`) and CompBioBench (`compbiobench/index.html` and its 100 item pages). The script also checks the token and UDT data files those pages link to. It writes `site_check.json`, one entry per check with the runs that differ. No answers are stored.

```sh
python analysis/site_verification/verify_against_site.py      # needs pandas; about one minute
```

## Result on 2026-10-14

Every score and answer the figures use matches the site.

| Check | Result |
|---|---|
| BixBench-Verified-50 per-run grades (1,500 runs) | identical to `figures/site_snapshot/` |
| IWC per-run values (240 runs, wf_007 replaced on 2026-10-12) | identical to `figures/site_snapshot/` |
| 6 July BixBench page (600 runs) | identical |
| CompBioBench official-leaderboard score of each replicate (24) | equal to the per-run grades in `figures/scored_runs.csv`; the single GPT-6 Astra replicate (93/100) is not part of the primary set |
| CompBioBench submitted answers (2,500 runs) | all equal to the archive |
| CompBioBench rerun labels (53) | equal to `runs/CompBio/reruns_20261005/rerun_manifest.csv` |
| Token-optimization batch (`summary.json`) | byte-identical to `runs/token_optimization/site_snapshot/` |
| BixBench input and output tokens (10 configurations) | equal at the displayed precision |
| IWC input and output tokens (24 replicates) | equal |

The site shows more than the archive holds in six places. None affects a score.

1. **CompBioBench per-item grades: by design.**
   - The item pages grade `annotate-variant-regulatory-overlap-q1` against the site's evidence-based reference. 9 runs are marked incorrect there but correct on the official leaderboard.
   - The figures use the leaderboard grades, as decided on 2026-10-07. The site's headline uses them too.
2. **CompBioBench token totals: 14 runs have no usage in the archive.**
   - 5 of 25 replicate totals differ: GPT-5.5 Galaxy r3 and GPT-5.6 Luna Galaxy r1–r3. 12 of the runs are the Galaxy runs whose traces were never archived. The site has usage for 12 of the 14 runs; DeepSeek open-ended code r1 is incomplete on the site too.
   - The cached Hugging Face token was rejected (HTTP 401), so it could not be checked whether those traces can now be downloaded.
3. **IWC cached-input tokens: one value missing.** In `token_run_observations.csv`, wf_010 GPT-5.6 Sol Galaxy r3 has no cached count. Its trace (`codex_events.jsonl.gz`) reports 35,633,920.
4. **BixBench cached-input tokens: three configurations differ.**
   - GPT-5.5 Galaxy: site 187.01M, archive 183.14M. The archive equals the runs' `usage.json`, so the site counts cached input differently.
   - DeepSeek via Claude Code (superseded): the archive has no cached counts at all.
5. **CompBioBench UDT use: 32 Galaxy runs are UDT runs on the site but not in the archive's UDT table.**
   - 10 of them have no archived trace.
   - The other 22, mostly DeepSeek, created UDTs through the raw Galaxy API, which the trace-based count does not see. The site counts from traces and Galaxy histories.
6. **BixBench UDT use: DeepSeek V4 Pro differs (site 18/150, archive 14/150).** The cause is the same as in item 5: the DeepSeek runs that fell back to the shell API.

Items 2 to 6 concern supplementary token and UDT tables, not the accuracy results. Fixing them means:
- recovering the 12 missing CompBioBench traces, which needs a valid Hugging Face token;
- adding the one IWC cached count;
- counting API-created UDTs.
