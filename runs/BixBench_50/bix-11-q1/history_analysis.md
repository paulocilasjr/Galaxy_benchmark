# BixBench bix-11-q1: Galaxy and open-ended-code execution histories

## 1. Task, design, evidence, and matching

The task asks for the fungi minus animals difference between median treeness values, as a decimal proportion. The allowed task metadata is [task_1.json](../../experiments/BixBench/task_1.json). This is a retrospective audit of the **24 run links supplied for this one selected task**: four model labels × two execution conditions × three replicate labels. It is a case study, not a sample of the full benchmark. The [run manifest](run_manifest.json) maps every supplied label to its source. There is no independent protocol manifest against which to establish expected-run coverage, matched seeds, or stopping rules; expected coverage is **unknown**.

The supplied labels were checked against `docker_invocation.json` in the original trace packages: `gpt-5.5`, `gpt-5.6-sol`, `gpt-5.6-luna`, and `deepseek-v4-pro`. Their reasoning settings were high, high, max, and high, respectively. The conditions are `galaxy_strict_skills` (Galaxy) and `anycode_nongalaxy_skills` (open-ended code). Within model, the code and Galaxy prompts are related but condition-specific; some model cohorts also have prompt-text differences or different container-image revisions. Replicate numbers do not demonstrate paired seeds. Accordingly, the condition differences below are descriptive associations within this selected task, not isolated effects of Galaxy access.

All **24 original trace packages** were retrieved from the supplied Hugging Face paths, including fixed answers, original `evaluation.json`, usage records, input manifests, commands, and tool-call transcripts. The original evaluator records, rather than hidden BixBench ground truth, are the scoring source. The auditor did not open hidden ground truth, submit a new Galaxy job, or replay recovered code. The 12 Galaxy labels link to **11 distinct public history IDs**: Sol replicates 2 and 3 point to the same history. Ten distinct histories yielded detailed contents, jobs, and small selected outputs. Luna replicate 2 yielded top-level history metadata, but its 8,801-dataset contents listing timed out; its original trace and evaluator remain available. See [source snapshots](source_snapshots/galaxy/retrieval_manifest.json), [Galaxy trace manifest](source_snapshots/huggingface_traces/manifest_galaxy.json), and [code trace manifest](source_snapshots/huggingface_traces/manifest.json).

## 2. Main outcomes

**Official fixed-answer accuracy.** The original run evaluator accepted **12/12 Galaxy** and **12/12 open-ended-code** answers (`accuracy.score = 1.0` in every retrieved `evaluation.json`). The observed difference is **0 percentage points** for this task. Each model × condition group had 3/3 accepted answers. With one selected task, no independent task-level confidence interval or equivalence claim is warranted. The Sol Galaxy r2/r3 history reuse further limits any assertion of three independent executions, although their trace packages and answer records are distinct.

**Recorded execution.** The ten detailed distinct Galaxy histories contain 27 deduplicated analytical creating jobs, one of which failed. They show installed PhyKIT, Galaxy-hosted custom Python, Datamash, and Summary Statistics routes. The original traces provide a fuller agent chronology for all 24 labels. Across the 12 Galaxy traces there are 268 completed shell calls, 16 nonzero shell exits, and 255 MCP calls; across the 12 code traces there are 220 completed shell calls and 10 nonzero shell exits. These are native call counts, **not** counts of independent scientific attempts or unique Galaxy jobs.

**Auditor interpretation of saved outputs.** All ten detailed distinct Galaxy histories support a fungi minus animals difference near **0.0501**. The custom GPT-5.5 Galaxy r3 output is `0.050139847768049167`; the approximately `0.00003985` precision difference from `0.0501` does not change the original evaluator's accepted-answer status. Some histories save only per-tree values or group medians; those difference calculations are explicitly auditor reconstructions, separate from submitted answers. Luna Galaxy r2's public outputs could not be independently inspected through the contents API.

| Runtime model | Galaxy accepted / 3 | Code accepted / 3 | Galaxy submitted answers, r1–r3 | Code submitted answers, r1–r3 |
|---|---:|---:|---|---|
| GPT-5.5 | 3 | 3 | 0.050099999999999999; 0.0501; 0.050139847768049167 | 0.05013984776804917 in all three |
| GPT-5.6 Sol | 3 | 3 | 0.0501 in all three | 0.05013984776804917; same; 0.0501398477680492 |
| GPT-5.6 Luna | 3 | 3 | 0.0501 in all three | 0.05013984776804917; 0.05014; 0.05014 |
| DeepSeek V4 Pro | 3 | 3 | 0.0501; 0.05; 0.0501 | 0.0501; 0.05014; 0.05014 |

The original evaluator reports `llm_verifier_auto_code`, source mode `llm_verifier`, and numeric tolerance `0.0005`. The current repository `SKILL.md` describes a different verifier procedure; this audit preserves the **original run evaluator** and does not rescore the answers with current rules. Its `step_completion.score` is 0.5 for all Galaxy runs and 1.0 for all code runs, but the tested steps differ: Galaxy marks `fresh_galaxy_history_recorded=false` and `final_deliverable_written=true`; code marks `agent_run_completed=true` and `final_deliverable_written=true`. These scores cannot be subtracted as a common execution-quality measure. Public linked histories and trace-referenced jobs exist despite the Galaxy history-record step failing in the original evaluator.

## 3. Results questions

### Accuracy and output agreement by execution condition

The descriptive single-run accuracy is 100% in each condition, and all eight model × condition groups are **all correct among their three submitted answers** under the original evaluator. There is no observed “some but not all” or “none” group among these supplied packages. These are 24 answer evaluations for one task, not 24 independent tasks. No task bootstrap, confidence interval, noninferiority analysis, or model-general performance inference is defensible. The Galaxy output agreement in ten public histories provides independent provenance for many accepted answers, while the Luna r2 public contents gap and shared Sol history remain visible limits. Different decimal precision and routes all received accepted-answer scores; the evidence does not show which route caused success.

### Analysis execution, failures, and recovery

For this audit, **Galaxy-hosted analysis** means an analytical job executed on usegalaxy.org. A stronger claim that *all* analysis occurred in Galaxy would require full event-level exclusion of local calculation and external services. The traces include local inspection and, in some runs, arithmetic summaries of Galaxy-derived values. They do not demonstrate use of an external analytical service. Reading remote input files or documentation is distinct from outsourcing computation. Thus the histories establish Galaxy-hosted scientific metric jobs in the ten detailed histories, while “Galaxy only” is not a supported blanket label for all 12 runs.

The detailed histories contain **27 unique analytical creating jobs, 1 failed**; shared `__DATA_FETCH__` jobs are excluded and multiple outputs of one job are counted once. Luna Galaxy r2's public job total is unknown. The original Galaxy traces contain 80 `run_galaxy_tool_and_wait` calls and 3 `run_galaxy_udt_and_wait` calls, with discovery, inspection, polling, and other MCP calls making up the rest of the 255. Calls can repeat, refer to other histories, or correspond to multiple outputs, so they do not replace the public job ledger. The 16 Galaxy and 10 code nonzero shell exits likewise include nonanalytical command failures. A cross-condition “failed scientific attempts before correct answer” statistic is **not assessable** from these heterogeneous native events without a defensible common attempt mapping.

One directly traceable Galaxy recovery occurred in **Luna r3**: Datamash median column 4 failed on the text `treeness`; changing to column 5 on the same input HDA succeeded, yielding animals `0` and fungi `0.0501`. This is an operational parameter correction, followed by an accepted final answer. In **Sol code r1**, a missing Biopython import prompted installation and a subsequent tree calculation. In **DeepSeek code r1**, PhyKIT rejected `-t`, then accepted the tree path positionally. These are same-goal tool/dependency recoveries. DeepSeek code r2 also shows a failed `pip --user` invocation followed by installation, but a nonzero shell exit by itself is not counted as a distinct scientific attempt. There is no basis here to say Galaxy improved recovery relative to code; both conditions show successful recoveries in selected traces. See [job ledgers](job_ledgers/galaxy) and the event/recovery IDs in [evidence JSON](history_analysis_evidence.json).

### Solution-route variability across models and replicates

The route codebook separates the biological/statistical operation (per-tree treeness, group medians, fungi minus animals) from where and how it was implemented. In Galaxy, most detailed runs used installed **PhyKIT** for treeness. GPT-5.5 r1 additionally used a Galaxy-hosted custom script invoking PhyKIT; GPT-5.5 r3 used a custom Galaxy-hosted Newick/branch-length parser. Sol's shared r2/r3 history and Luna r3 used Datamash aggregation; DeepSeek r1 used Summary Statistics. In open-ended code, GPT-5.5 and Luna mainly used local Newick parsers, Sol used Biopython (r1), IQ-TREE report extraction (r2), and a Decimal Newick parser (r3), while DeepSeek used local PhyKIT across all three. IQ-TREE reports served as cross-checks in several other code runs. The [recovered-code manifest](recovered_code/manifest.json) records command strings and Galaxy-hosted payload hashes; these were archived, not executed by the auditor.

The accessible PhyKIT summaries report **100 processed animal treefiles and 249 fungal treefiles**, each with zero failed selected files. Their archive totals of 1,564 and 2,514 are not the denominators for this analysis. The different decimal precision is compatible with method/rounding differences, and all submitted values passed the original evaluator. No task difficulty category was independently supplied, so variability by difficulty cannot be assessed. Three replicates of one question do not support model-wide route-diversity claims.

### Token cost, provenance, and human readability

The original usage records report the following **provider input-token totals**. Each comparison is the **ratio of the Galaxy median to the code median within a model** over the three supplied runs; it is not a median of paired replicate ratios. All 24 runs are included because all have usage and accepted answers. Cached input is a subset of input, and reasoning output may be included in output; those categories were not added to totals.

| Runtime model | Code median input | Galaxy median input | Ratio of medians | Code median output | Galaxy median output |
|---|---:|---:|---:|---:|---:|
| GPT-5.5 | 293,680 | 1,168,645 | 3.98 | 5,312 | 8,493 |
| GPT-5.6 Sol | 276,694 | 1,568,679 | 5.67 | 5,189 | 8,020 |
| GPT-5.6 Luna | 725,139 | 4,743,276 | 6.54 | 11,368 | 21,055 |
| DeepSeek V4 Pro | 1,432,925 | 3,498,944 | 2.44 | 15,233 | 24,838 |

Luna Galaxy r2 reports **45,580,283 input tokens**, a large within-group outlier; its 8,801-dataset history may be relevant context, but the available totals cannot attribute token use to that history size, retries, tool discovery, or repeated context. The traces preserve tool calls, yet no per-call provider usage allows a defensible stage-by-stage token allocation. Prices, compute/storage charges, and external-service costs were not supplied, so monetary or total execution cost is unavailable. Since accuracy is uniformly accepted in this case, it provides no outcome variation with which to estimate a token–accuracy association. Galaxy histories expose structured tool IDs, parameters, links, states, and errors, which is **provenance inspectability**. No blinded human review, reconstruction time, or error-rate study was performed, so improved human readability is unmeasured.

## 4. Per-condition, model, and replicate routes

The table describes the **final scientific route visible in the original traces or public jobs**; a trace can include exploratory commands. `Accepted` refers only to the original evaluator's fixed-answer score. The Galaxy job counts are for ten detailed **distinct** histories; the Sol r2/r3 count belongs to one shared history. A blank public-job count for Luna r2 means unknown, not zero.

| Model / replicate | Galaxy route and final artifact | Code route and final artifact | Notable correction |
|---|---|---|---|
| GPT-5.5 r1 | PhyKIT probe, then custom Galaxy script invoking PhyKIT; explicit 0.0501; 2 jobs | Local Newick/branch-length parser; 0.05013984776804917 | None established |
| GPT-5.5 r2 | PhyKIT on groups; per-tree values, auditor difference 0.0501; 2 jobs | Local Newick parser, IQ-TREE check; 0.05013984776804917 | None established |
| GPT-5.5 r3 | Galaxy-hosted custom Newick parser; explicit 0.050139847768049167; 1 job | Local Newick parser, IQ-TREE check; 0.05013984776804917 | None established |
| Sol r1 | PhyKIT on groups; per-tree values, auditor difference 0.0501; 2 jobs | Biopython tree calculation; 0.05013984776804917 | Code dependency install after import failure |
| Sol r2 | PhyKIT and Datamash in shared history; group medians 0 and 0.0501 | Local IQ-TREE report extraction; 0.05013984776804917 | None established |
| Sol r3 | Same public history as Sol r2; distinct trace and accepted answer | Local Decimal Newick parser; 0.0501398477680492 | Shared history limits independent Galaxy provenance |
| Luna r1 | PhyKIT probe and group metrics; auditor difference 0.0501; 3 jobs | Local Newick parser, IQ-TREE check; 0.05013984776804917 | None established |
| Luna r2 | Trace records Galaxy tools and accepted 0.0501; public 8,801-dataset contents unavailable | Local Newick parser, IQ-TREE check; 0.05014 | Public job/output inventory unavailable |
| Luna r3 | PhyKIT plus Datamash; medians 0 and 0.0501; 6 jobs, 1 failed | Local Newick parser; 0.05014 | Galaxy Datamash column 4 → 5 |
| DeepSeek r1 | PhyKIT plus Summary Statistics; medians 0 and 0.0501; 4 jobs | Local PhyKIT; 0.0501 | Code PhyKIT `-t` → positional path |
| DeepSeek r2 | PhyKIT; auditor difference 0.0501; 1 job | Local PhyKIT; 0.05014 | Code package-install syntax repaired |
| DeepSeek r3 | PhyKIT; auditor difference 0.0501; 2 jobs | Local PhyKIT with parser cross-checks; 0.05014 | None established |

The Sol r2/r3 shared history has **4 analytical creating jobs total**, counted once. Per-run events, parameters, exact answer bytes, and source references are in the [evidence JSON](history_analysis_evidence.json). The table is a summary, not a substitute for the chronology.

## 5. Inputs, external computation, and reproducibility

Each original trace package has an `inputs_manifest.json` listing **20 staged input files**; names and SHA-256 values agree across all 24 packages. The auditor compared those manifests but did not download and rehash all large source files. In the ten detailed Galaxy histories, `scogs_animals.zip` and `scogs_fungi.zip` each resolve to one underlying Galaxy dataset ID and one original creating job across copied associations. This is object reuse, not 20 independent acquisitions. Their upstream fetches predate the July/August histories. The [input manifest](input_manifest.json) records names, object IDs, checksums when available, and provenance limits.

The original code condition used local shell/Python and packages seen in the traces; Galaxy used installed tool versions and job parameters recorded in the public job snapshots. Some code runs inspected IQ-TREE reports, and some traces included package installations. The public Galaxy records do not prove that every local agent action was merely orchestration or arithmetic, and no remote analytical service appears in the retained records. Prompt variants, container revisions, shared input state, and the Sol duplicate history limit causal condition interpretation.

The audit retained **56 small Galaxy output files** with verified byte sizes and SHA-256 hashes, original trace packages as redacted derivatives, public history/job snapshots, command extracts, and per-run ledgers. Source manifests record original and retained hashes where available. Redaction removed unnecessary local account paths and credential-like strings; no secret-bearing originals were placed in this package. The Luna r2 public contents timeout and lack of independently verified bytes for all 20 staged input files remain explicit gaps. The report's previous exact version is preserved as [history_analysis.v1.md](history_analysis.v1.md).

## 6. Methods and safeguards

Galaxy metadata came from read-only `GET /api/histories/{id}`, `/contents?details=all`, and `/api/jobs/{job_id}?full=true` requests. The history association ID is the dataset key, rather than its display number. Analytical jobs were deduplicated by native creating-job ID within the same server, multi-output jobs were counted once, and shared `__DATA_FETCH__` jobs were excluded. A current history is a snapshot, so the run's own transcript has priority for chronology and attribution. Where a complete group/value table was available, the auditor took `statistics.median` separately for animals and fungi and subtracted animals from fungi; this is an **auditor calculation**, never substituted for the fixed answer.

The original evaluator's answer score is reported exactly as recorded. Run-level accuracy uses each trace package once; history-level job counts use each distinct history once. No seed matching is claimed. Token medians use the three reported totals per model and condition; ratios divide those two medians. No stage attribution, task bootstrap, equivalence margin, monetary conversion, or human readability experiment was introduced. Recovered commands and code were not executed. [JSON Schema 2.0](history_analysis_evidence.schema.json) and [validation script](validate_audit.py) check the evidence structure, references, source hashes, output sizes, and counts.

## 7. Claim-to-evidence map

| Manuscript claim for this selected task | Finding ID | Primary records and limit |
|---|---|---|
| The original evaluator accepted all 12 Galaxy and all 12 code answers; observed difference 0 percentage points. | `official-accuracy-24-runs` | Original per-run `evaluation.json` in [trace manifests](source_snapshots/huggingface_traces); one task, no task-level interval |
| Ten detailed distinct Galaxy histories support an output difference near 0.0501. | `galaxy-output-convergence` | [Selected output bytes](selected_outputs/galaxy/manifest.json) and job/artifact IDs in evidence JSON; Luna r2 public contents unavailable |
| Ten detailed Galaxy histories contain 27 distinct analytical jobs and one failed Datamash job corrected on the same input. | `execution-and-recovery` | [Galaxy ledgers](job_ledgers/galaxy) and `recovery_luna_r3_datamash` in evidence JSON; native calls are not attempts |
| The runs used multiple routes: installed PhyKIT, custom Galaxy code, local PhyKIT, Biopython, IQ-TREE report extraction, and local parsers. | `route-variation` | Per-run events, routes, and [recovered-code manifest](recovered_code/manifest.json); descriptive one-task classification |
| Within each model, Galaxy's median input-token total exceeded code's by 2.44–6.54 times. | `input-token-cost` | Original `usage.json` and model-stratified comparisons in evidence JSON; ratio of medians, no causal attribution |
| Human readability improvement was not measured. | `readability-unmeasured` | No blinded review records or reviewer effort outcomes in the supplied sources |

## 8. Missing evidence and next data

An independent protocol manifest would establish expected-run coverage, seeds, stopping rules, budgets, and whether the two Sol labels were intended to have separate Galaxy histories. A bounded Luna r2 public job/output export would allow object-level verification of that run's history. Rehashing the full staged source inputs would strengthen byte-level input confirmation. Per-call provider usage, dated price sheets, and compute/storage records would be needed to allocate or monetize cost. A prespecified blinded reviewer study with equivalent access to both conditions would be needed to test readability. A multi-task, compatible matched sample would be needed for an accuracy interval or claim of equivalence or superiority. None of these unknowns is encoded as zero.

### Abstract-ready paragraph

In a selected BixBench treeness task, the original evaluator accepted all 12 Galaxy and all 12 open-ended-code submitted answers, an observed difference of 0 percentage points. Twelve Galaxy links mapped to 11 distinct public histories; ten detailed histories contained 27 distinct analytical jobs, including one failed Datamash job followed by a successful parameter correction. Within each of four models, Galaxy's median reported input-token total was 2.44–6.54 times the code median. These descriptive results concern one task and do not establish condition equivalence or a causal cost effect.

### Results draft

We audited the 24 supplied run packages for BixBench `bix-11-q1`, comprising four runtime model IDs, two conditions, and three replicate labels per model and condition. Under the original `llm_verifier_auto_code` evaluation, all 12 Galaxy and all 12 open-ended-code fixed answers were accepted (0 percentage-point observed difference). The Galaxy labels resolved to 11 public history IDs because Sol replicates 2 and 3 shared a history. Ten distinct histories exposed detailed contents and jobs, with 27 deduplicated analytical creating jobs and one failed job; Luna replicate 2's 8,801-dataset history exposed metadata but its contents request timed out. The failed job treated a text `treeness` field as a numeric median column; switching Datamash from column 4 to 5 on the same input succeeded. Saved outputs in all ten detailed histories supported a fungi minus animals median treeness difference near 0.0501. Original code traces also recorded dependency and CLI-argument recoveries. Provider-reported input-token medians were higher in Galaxy than code for each model, with ratios of condition medians from 2.44 to 6.54; the traces do not allocate these totals to retries or other stages. With one selected task, condition-specific prompts, no matched seeds, and one shared Galaxy history, these observations support an auditable case description rather than a benchmark-wide accuracy, equivalence, recovery advantage, or readability claim.
