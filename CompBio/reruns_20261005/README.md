# CompBioBench Galaxy reruns (reviewed 2026-10-05)

53 CompBioBench Galaxy runs (task × model × replicate) were rerun by the lab after review, because key analyses ran outside Galaxy or tool timeouts needed verification. This folder records how they replaced the original runs in this archive.

**The rule:** only the 53 rerun runs get new results; every other run keeps its result exactly.

## Files

| File | Contents |
|---|---|
| `rerun_manifest.csv` | One row per rerun. Gives the reason, the original and rerun answers, the grade of each, and the rerun's Galaxy history and trace links (from `CompBioBench_Galaxy_Rerun_Impact_20261005.docx`; SHA-256 prefix in `source_report`). |
| `official_scores_20261005.csv` | Official accuracy of the 12 Galaxy replicates before and after the reruns, from the same report. |
| `apply_reruns.py` | The swap. It archives each original run, copies in the staged rerun, points the workbook row at the rerun, and rebuilds the 36 affected task packages offline. |
| `check_unchanged.py` | Compares every per-run table with the last commit before the swap (7ed8048c9). It fails if any record other than the 53 reruns changed. |
| `compbiobench_execution_condition_links.pre_rerun_20261005.xlsx` | The run-link workbook before the swap. |

Each affected task package keeps its original runs under `versions/pre_rerun_20261005/`. That folder holds the trace folders, manifests, Galaxy history snapshots, selected outputs, job ledgers and the task's previous evidence and report. `swapped_runs.json` lists the old and new trace and history for each run.

## How it was done

1. **Staging.** The reruns were collected with `analysis_execution/collect.py` (the repository's collector, same byte caps) into a staging folder outside the repository. HF_TOKEN and GALAXY_API_KEY came from the environment.
   - All 53 traces and histories were retrieved.
   - Every file's git object ID matches the Hugging Face commit pinned in the lab's rerun record (dff0bbae052068efeab4a37160c05e7e6714cb8c).
   - Every submitted answer and token total matches that record.
   - The record's own `trace_sha256` matches the retrieved trace for only 2 of 53 runs. It appears to hash a different copy, so the commit check is the integrity check used here.
2. **Swap.** `python CompBio/reruns_20261005/apply_reruns.py <staging folder>`. Rebuilding an unchanged task package offline reproduces its evidence exactly (only the audit timestamp differs).
3. **Rebuild.**
   1. `scripts/audit_compbio_overview.py`
   2. `scripts/build_result_tables.py`
   3. `v2_trace_friction/extract.py` (then gzip to `manuscript_material/source_data/derived/run_summaries.jsonl.gz`), followed by `taxonomy.py` and `ledger.py`
   4. `derived/galaxy_calls/extract_calls.py` and `summarize.py`
   5. `derived/design/`: `extract_design.py`, `prompt_phrases.py`, `build_design_metadata.py`, `build_md.py`, `wrap_json.py`, in that order
   6. `manuscript_material/scripts/build_data.py` and `fig_on_demand.py`
   7. `original_layout/scripts/accuracy_analysis.py` and `token_analysis.py`
   8. the scripts in `figures/`, in their build order
4. **Check.** `python CompBio/reruns_20261005/check_unchanged.py 7ed8048c9 <analysis tables>` passes. Only the 53 rerun records changed in:
   - the evidence, workbook and `analysis.json` (runs and jobs);
   - the run summaries and Galaxy calls;
   - the design metadata and the CompBio audit;
   - the per-run accuracy, token, action and UDT tables.

## Private inputs (kept outside this public repository)

The regrading in `fig_on_demand.py` and the UDT audit timelines read three files from the lab repository goeckslab/galaxy-agent-benchmark, through `COMPBIO_KEY_DIR`:

| File in `COMPBIO_KEY_DIR` | Source in the lab repository | SHA-256 prefix |
|---|---|---|
| `score_inferred_answers.tsv` | `compbiobench/results/score_inferred_answers.tsv` (unchanged) | 959dd3f2 |
| `compbiobench_results_score_predicted_answers.tsv` | `compbiobench/results/score_predicted_answers.tsv` (unchanged) | 57a6a92d |
| `paper_site_runs_lab.json` | `compbiobench/results/paper_site_runs.json` at commit 9914f4899411 | ff1f443b |

The new `paper_site_runs_lab.json` differs from the previously pinned version (055cfb18, commit bdc00429f559) only in the official scores and vector hashes of the Galaxy replicates whose answers the reruns changed. With it, the per-run grades reproduce all 24 official replicate scores.

The archived per-campaign answer vectors on Hugging Face predate the reruns. `scripts/audit_compbio_overview.py` therefore substitutes the rerun answers from `rerun_manifest.csv`, and the official scores from `official_scores_20261005.csv` for the 10 replicates that contain reruns. Where an archived vector matched its old hash, adding the rerun answers reproduces the new official hash exactly.

## Changes

- **Answers and grades:** 22 answers and 17 grades changed (8 runs to correct, 9 to incorrect).
- **UDT error audit (`manuscript_material/on_demand/udt_audit/`):** the 10 entries for replaced runs were set aside; `udt_error_audit_pre_rerun_20261005.jsonl` keeps the full previous file. The 14 incoming incorrect UDT runs were coded with the same codebook by two AI reviewers (batches `rerun_20261005_A` and `_B`).
- **Exposure scan:** under its existing rules, lung-cancer-sc-q1 (GPT-5.5 r3) counts as "attempted". Its trace shows that it fetched this project's results page for the task through the GitHub connector and reused other runs' published histories. The rule was not extended, so that other runs keep their tiers.

## How the reruns differ from the original condition

- **Same:** task prompt, model, reasoning effort, time limit and skill names. The effective prompt is identical apart from the history ID in 52 runs; the original Sol r3 contaminated-rna-q3 run was a continued turn.
- **Different:**
  - the agent container image;
  - the campaign (`compbio_galaxy_compliance_20260923_*`);
  - no rerun used web search (the original versions of these runs searched 1,336 times);
  - 30 reruns used Codex app connectors to Galaxy, GitHub or Hugging Face.

## Not yet updated

- **Task-level failure-cause audit (`individual_error_analysis.md`):** its entries for the affected tasks describe the replaced runs. reverse-encode-q1 and perturb-seq-align-q1 now have incorrect runs and no entry. `rigor_analysis.py` and the original-layout manuscript build stop on this.
- **Verification sample:** D075 (conservation-lookup-q1, DeepSeek r3) was coded on the replaced run. Its outcome stratum, incorrect, is unchanged.
