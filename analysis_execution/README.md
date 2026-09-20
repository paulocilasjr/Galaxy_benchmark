# Spreadsheet-driven execution-history audits

`run.py` builds a separate retrospective audit package for every benchmark/task in an XLSX run-link table. It reads the links, retrieves original Hugging Face trace packages and read-only public Galaxy history evidence, then writes a task-scoped report and validated machine-readable evidence. It never submits analysis jobs, executes recovered commands, or opens hidden ground truth.

## Input table

Use one row per observed run. The supplied BixBench workbook has a `BixBench links` sheet with `benchmark`, `task`, `task_page`, `model`, `condition`, `replicate`, `run_trace`, and `galaxy_history` columns. The `README` sheet is ignored as source metadata, not treated as instructions. The parser also accepts the earlier seven-column example with an extra blank cell before the task. It reads both cell text and Excel hyperlink targets, so plain URLs, clickable links, and Markdown-style links work.

| benchmark | task | model | condition | replicate | link1 | link2 |
|---|---|---|---|---|---|---|
| bixbench | bix-6-q4 | Codex GPT-5.5 | galaxy-api | replicate 1 | Galaxy history URL | Hugging Face trace directory URL |
| bixbench | bix-6-q4 | Codex GPT-5.5 | open-coded | replicate 1 | Hugging Face trace directory URL | blank |

Supported benchmark labels: `BixBench-Verified-50`/`bixbench`, `compbio`/`compbiobench`, and `iwc`. `Galaxy-API code with skills`/`galaxy-api`/`galaxy_strict_skills` map to Galaxy; `Open-ended code with skills`/`open-coded`/`anycode` map to open-ended code. Original labels are retained. The task ID must appear in each trace directory path. Duplicate benchmark/task/model/condition/replicate rows are rejected. A history may be linked from more than one run; its native jobs are counted once in task-level totals.

## Run

Install the only nonstandard validation dependency:

```sh
python3 -m pip install -r analysis_execution/requirements.txt
```

The repository `SKILL.md` requires a nonempty `GALAXY_API_KEY` in the repository `.env` before **any** Galaxy API access, including read-only retrieval. The key is read without printing or saving its value. For restricted Hugging Face traces, provide a token in `HF_TOKEN` or enter it at a hidden prompt. The token is never written into the audit package.

TLS certificate verification is on by default. If the host's proxy presents an invalid certificate, `--insecure-tls` permits retrieval and marks every source manifest `tls_certificate_verified: false`; use it only in that environment. Retained hashes verify local bytes, not the remote server's identity.

```sh
python3 analysis_execution/run.py runs.xlsx --dry-run
python3 analysis_execution/run.py runs.xlsx --task bix-6-q4 --prompt-hf-token
python3 analysis_execution/run.py runs.xlsx --resume
```

Without `--task`, all table rows are processed by benchmark/task. Defaults are `BixBench_50/analysis/<task>/`, `CompBio/analysis/<task>/`, and `IWC/analysis/<task>/`. Use `--output-root` to change the root when selecting a single benchmark. `--resume` is required for a rerun of an existing package; it retries partial/unavailable sources, preserves the previous report and evidence as versioned snapshots, and rebuilds the result from retained sources. For a preexisting task directory produced by another workflow, `--adopt-existing` first archives every file the pipeline would replace under `legacy_pre_analysis_execution/`; unrelated files stay in place. `--offline` rebuilds from preexisting source manifests without network access or the Galaxy credential gate.

## Output contract

Each task directory contains:

```text
README.md
<task>.json
run_manifest.json
input_manifest.json
history_analysis_evidence.json
history_analysis_evidence.schema.json
history_analysis.md
source_snapshots/galaxy/<history-id>/
source_snapshots/huggingface_traces/{manifests,indexes,files}/
selected_outputs/{galaxy,open_ended_code}/
recovered_code/{galaxy,open_ended_code}/
job_ledgers/{galaxy,open_ended_code}/
```

The report follows the eight sections and two closing writing products in `HISTORY_ANALYSIS_INSTRUCTIONS.md`. It reports only task-neutral quantities it can derive: original evaluator fields, native job/call counts, route indicators, input-token medians, and explicit gaps. A failed Galaxy job followed by success with the same tool and input HDA IDs is flagged as an operational recovery **candidate**. It does **not** infer a task-specific biological result, scientific recovery, an IWC/BixBench/CompBio score equivalence, or a human readability gain from generic log patterns. Those require case-specific scientific review and may be added as a versioned interpretation after the generated audit is fixed.

Trace files larger than 10 MB and Galaxy output datasets larger than 100 KB are linked by default; adjust with `--max-trace-mb` and `--max-output-kb`. To keep a 50-task batch bounded, histories with more than 300 reported contents retain history metadata and original agent traces but defer public contents/job export; raise `--max-history-contents` in a later focused rerun to collect them. Original and retained hashes are recorded for downloaded trace/output bytes, while secret-bearing/account-path text is redacted in retained derivatives. Binary Galaxy outputs, which cannot be inspected by the text redactor, are explicitly listed in `skipped_outputs` without storing their bytes. Missing, partial, and metadata-only sources remain explicit. The validation step checks the JSON Schema, ID references, local byte hashes/sizes, and retained-text secret patterns. Network or access failures produce a partial, clearly labelled report rather than invented data.

## Check

```sh
python3 -m unittest discover -s analysis_execution/tests -v
python3 analysis_execution/validate.py BixBench_50/analysis/bix-6-q4
```

The offline integration test constructs a small XLSX with the shifted sample layout and checks the generated directory, both conditions, a Galaxy job, token ratio, recovered command, and Schema 2.0 validation. It does not require network access or credentials.
