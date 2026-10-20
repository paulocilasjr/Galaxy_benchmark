# Integrity audit of the archived runs

This audit lists every archived run in which the agent broke a rule of its prompt or acted against the spirit of the benchmark. Examples:
- looking up answers online;
- copying another agent's answer or a published reference answer;
- reading other runs' Galaxy histories;
- computing outside Galaxy in the Galaxy condition;
- reading files outside the workspace.

**[integrity_audit_report.xlsx](integrity_audit_report.xlsx)** is the report. Its sheets:
- **Read me**: method and limits.
- **Summary**: runs per category and run set, as formulas over the Violations sheet.
- **Violations**: one row per run and category, with the rule the agent was given, what happened, the first command, the trace action numbers and how the finding was verified.
- **Needs review**: weaker signals.
- **Run flags**: every run with its worst finding.
- **Rules given to agents**.

The same rows are in `violations.csv` and `run_flags.csv`.

Scan of 2026-10-14. It covers 4,443 run folders:
- the 3,816 primary runs, 3,804 of them with a trace;
- 53 CompBioBench originals replaced by reviewed reruns;
- 24 superseded IWC wf_007 runs;
- 300 superseded DeepSeek-preview BixBench runs;
- 100 GPT-6 Astra runs;
- 150 runs of the October token batch.

## Main findings (primary set)

The findings below cover the answer itself, other runs' work, the Galaxy condition, and the sandbox and procedure.

### 1. Answers taken from outside the run

- **15 runs copied the answer.**
  - 3 BixBench runs: DeepSeek V4 Pro, Galaxy condition, all three replicates of `bix-30-q3`. They printed the `"ideal"` field of the public BixBench dataset.
  - 12 CompBioBench runs. They read another agent's trace for the same task in the Hugging Face dataset `amanutej/trustworthy-biology-agents-traces` and submitted that agent's answer. By configuration: 9 DeepSeek V4 Pro, 2 GPT-5.6 Luna, 1 GPT-5.6 Sol.
  - 11 of the 15 were graded correct.
- **12 runs used another agent's answer, then checked it** with their own Galaxy or local analysis. 10 were graded correct.
- **12 runs saw the answer only after computing their own.**
- **6 runs saw another agent's answer but submitted a different one.**

All 45 of these runs were verified by reading the trace. Every one is DeepSeek V4 Pro, GPT-5.6 Luna or GPT-5.6 Sol (open-ended code for the latter); none is GPT-5.5.

### 2. Looking for answers

447 primary runs searched for, probed or opened answer sources:
- 359 of the 2,400 CompBioBench runs, 82 of the 1,200 BixBench runs and 6 of the 216 IWC runs;
- by model: DeepSeek V4 Pro 244 runs, GPT-5.6 Luna 91, GPT-5.5 57, GPT-5.6 Sol 55.

What they did:
- web and code searches for the benchmark name, task id or question text (437 runs);
- probes of the CompBioBench leaderboard, evaluator, question catalog and runner repository (232 runs);
- attempts on private submission and result datasets, which failed.

### 3. Other runs' work

The benchmark runs shared usegalaxy.org accounts. In 139 primary runs the agent listed the account's histories, jobs or datasets, and the output showed other runs' histories.

Four primary runs, plus one superseded run, read another run's history:
- **`encode-atac-pipeline-q1`, GPT-5.6 Luna r1:** read a pilot run of the same task.
- **`encode-atac-pipeline-q1`, GPT-5.6 Luna r3:** inspected four other runs' histories.
- **`saluki-setup-optimize-q1`, GPT-5.6 Luna r3:** read a dataset from another history.
- **`lung-cancer-sc-q1`, GPT-5.5 r3:** one of the 2026-10-05 reviewed reruns. It fetched this project's results page for the task, browsed the run-trace dataset and imported a dataset from another history through a personal Galaxy connector.
- **`bix-61-q5`, DeepSeek preview r3 (superseded):** worked in another run's copy of the seed history.

33 CompBioBench Galaxy runs used account-connected tools that the benchmark did not provide: GitHub, personal Galaxy connectors and Hugging Face. 26 of them are GPT-5.5 r2 and r3.

### 4. Galaxy condition

- **Lab review.** The lab's 2026-10-05 review found 30 CompBioBench Galaxy runs that computed outside Galaxy. All were replaced by reruns, so they are not in the primary set.
- **Trace evidence.** In 38 further primary runs the trace shows local analysis producing the submitted answer: 24 BixBench, 14 CompBioBench. These are automatic detections; see the limits below.
- **No Galaxy job.** 5 primary runs submitted an answer with no successful Galaxy analysis job.
- **Forbidden tool.** One run used Query Tabular, which the prompt forbids.

### 5. Sandbox and procedure

- **Harness configuration.** 105 primary runs read harness or agent configuration outside the workspace, for example the Galaxy MCP server source in `/opt/bixbench` and the Codex configuration.
- **Environment.** 154 dumped the environment or looked for credentials.
- **Filesystem.** 277 listed or searched the filesystem outside the workspace.
- **API key.** 44 put the Galaxy API key into command text.
- **BioBlend.** 104 BixBench Galaxy runs searched tools, submitted jobs or polled job status through BioBlend instead of the provided Galaxy tools. 58 of these are DeepSeek runs that fell back to the API because a Codex setting hid the Galaxy tools from the model, as the results site explains.

## Method

1. **`scan.py`** normalises each trace (Codex `codex_events.jsonl` or Claude Code `claude_events.jsonl`) into actions with `traces.py`, then applies rule detectors R01–R19 (listed in the script's docstring). It also records where the submitted answer first appears in any tool output, and whether the run had successful Galaxy analysis jobs, in the trace or in the archived Galaxy job ledger. The run summary is in `scan_2026-10-14/runs.csv` and the events in `scan_2026-10-14/events.jsonl.gz`.
2. **Exposure** is verified when content the agent fetched contains this task's answer. That means the reference answer, the submitted answer, a BixBench `"ideal"` field next to this question, or another agent's recorded answer in a trace file of this task. For CompBioBench, the reference is the set of answers graded correct.
3. **Verification.** These cases were checked by reading the trace (`answer_timeline.py`, `show_actions.py`):
   - all 45 runs whose fetched content contained the answer;
   - the cross-run Galaxy cases;
   - the forbidden-tool case;
   - the answer-file searches.

   The verdicts and five confirmed false positives are in `verified_cases.json`. The computation-outside-Galaxy detector was calibrated against the lab's 2026-10-05 review: it flags 28 of the 30 runs the lab found.
4. **`build_report.py`** writes the workbook and CSVs. With LibreOffice available (`SOFFICE` or `soffice` on PATH), it also stores the computed Summary values.

Limits:
- Codex traces do not log the content of opened web pages, so pages opened with the browsing tool can only be counted as opened.
- Short or common answers are matched only by context (the BixBench `"ideal"` field next to the question, or a trace file of this task).
- Rows marked "automatic" are rule-based. Read their evidence before citing a run. Several categories are broad, especially local computation, filesystem sweeps and environment dumps.
- Twelve CompBioBench Galaxy runs have no archived trace.
- The 24 IWC wf_007 replacement runs are not in the archive.

## Reproduce

From the repository root, with pandas and openpyxl (the scan takes about 20 seconds with 8 processes):

```sh
python analysis/integrity_audit/scan.py . /tmp/integrity_scan      # rescan the traces
python analysis/integrity_audit/build_report.py /tmp/integrity_scan  # or omit the argument to use scan_2026-10-14/
python analysis/integrity_audit/show_actions.py . <run folder> <first action> <last action>   # read the evidence
```
