# BixBench bix-11-q1: execution-history case study

## 1. Task, design, evidence, and matching

The prompt asks: “What is the difference between median treeness values for fungi versus animals? Report the difference as a decimal proportion (not percentage).” The allowed input metadata is [task_1.json](../../experiments/BixBench/task_1.json). This is a BixBench fixed-answer task: official performance is the binary evaluation of the submitted answer, not a score for an intermediate Galaxy table. The evaluator-only reference was not opened in this audit.

The sampling frame is the **24 links supplied for this one selected task**, not all BixBench runs. The supplied labels cover four models, three replicate labels, and two conditions (`galaxy_strict_skills` and `anycode_nongalaxy_skills`). No original experiment manifest, prompt additions, seed allocation, exact runtime model IDs, stopping rules, budgets, or evaluator outputs were retrieved. Therefore expected protocol coverage is unknown. Model names in this report are user-supplied labels, not verified runtime identities. Replicate numbers do not establish paired seeds. The conditions also have different prompt variants, so a condition effect cannot be isolated from prompt or harness effects.

The public Galaxy API yielded full contents and creating-job snapshots for **10 distinct histories**, plus top-level metadata for an eleventh. The Luna replicate-2 history reports **8,801 contents**; both the unpaginated and a five-item paginated contents request timed out. The GPT-5.6 Sol replicate-2 and replicate-3 links are the **same history ID**, so they cannot substantiate two independent Galaxy executions. The 12 Hugging Face open-ended-code links point into a repository whose API returned **HTTP 401**. No code-condition transcript, submitted answer, token record, or evaluator result was retrieved. See [run_manifest.json](run_manifest.json) and the source records in [history_analysis_evidence.json](history_analysis_evidence.json).

## 2. Main outcomes

| Model supplied by user | Galaxy r1 | Galaxy r2 | Galaxy r3 | Open-ended code r1–r3 |
|---|---|---|---|---|
| Codex GPT-5.5 | Explicit output 0.0501 | Reconstructed from saved tree values: 0.0501 | Explicit custom output 0.050139847768049167 | Traces inaccessible |
| Codex GPT-5.6 Sol | Reconstructed: 0.0501 | Reconstructed: 0.0501 | **Same history as r2** | Traces inaccessible |
| Codex GPT-5.6 Luna | Reconstructed: 0.0501 | Only history metadata retrieved | Reconstructed: 0.0501 after Datamash correction | Traces inaccessible |
| DeepSeek V4 Pro via Codex | Reconstructed: 0.0501 | Reconstructed: 0.0501 | Reconstructed: 0.0501 | Traces inaccessible |

“Reconstructed” means an **auditor** calculated the two group medians from downloaded Galaxy per-tree value files. It is not a claim about the agent's submitted answer. Among **10 detailed distinct histories**, all yield a fungi minus animals difference within 0.00005 of 0.0501. The custom parser in GPT-5.5 replicate 3 retains more precision than the standard PhyKIT output; the difference from 0.0501 is about 0.00003985. These values are visible execution artifacts, not official BixBench accuracy. **Available official scores: 0 of 24 linked run labels.** No condition accuracy difference, task reliability category, or confidence interval is defensible.

## 3. Results questions

### Accuracy and output agreement

The saved Galaxy outputs converge on approximately 0.0501 for this case, with the precision difference noted above. Ten distinct histories have enough accessible output to support that observation; one history is metadata-only. The official submitted answers and evaluator outcomes are unavailable, so neither a Galaxy success rate nor an open-ended-code success rate can be reported. The `10/10` figure describes **available Galaxy output agreement**, not answer accuracy and not a benchmark-wide estimate. There is one task, no independent task sample for a task-level interval, and a duplicated Sol history link. See findings `galaxy-output-convergence` and `accuracy-unavailable` in the [evidence JSON](history_analysis_evidence.json).

### Execution, failures, and recovery

Across the **10 detailed distinct Galaxy histories**, there are **27 distinct analytical creating jobs** and **one recorded failed analytical job**. Shared `__DATA_FETCH__` jobs are excluded, and multi-output jobs are counted once. The remaining history has unknown job count. The ten visible histories contain both installed PhyKIT metrics jobs and custom code hosted in Galaxy. This establishes Galaxy-hosted computation for the recorded jobs; activity outside Galaxy is unknown without agent transcripts. No external analytical service is evident in the retained job commands. Reading remote inputs and using a tool installed on Galaxy are separate from external analytical computation.

The one clear operational recovery is **Luna replicate 3**. A Datamash job requested median of column 4 and failed because the first value was the text `treeness`. A later Datamash job on the **same input HDA** changed the median column to 5 and succeeded, producing animals `0` and fungi `0.0501`. The failed and successful jobs are preserved in the [job ledger](job_ledgers/galaxy/galaxy_luna_r3.json). This supports a parameter correction and operational recovery. It does not establish a correct fixed submitted answer. No failed-attempts-before-correct-answer measure is available. The other nine detailed histories have no recorded failed analytical jobs in their current snapshots; that does not establish an error-free agent session.

### Solution-route variability

The common biological target is per-tree treeness followed by separate animal and fungal medians and their difference. Eight detailed histories expose PhyKIT per-tree values for both groups; GPT-5.5 replicate 1 uses an additional custom Galaxy-hosted script that invokes PhyKIT commands and writes the difference; GPT-5.5 replicate 3 uses a custom Newick parser to calculate treeness directly. DeepSeek replicate 1 uses Galaxy Summary Statistics on the two PhyKIT value tables. Sol replicate 2/3 and Luna replicate 3 use Datamash grouped medians. Some histories stop at per-tree metrics; the final subtraction is only an auditor reconstruction in those cases. See each run's tool IDs, parameters, and output artifacts in the [evidence JSON](history_analysis_evidence.json).

The PhyKIT summaries in the accessible histories report **100 processed animal treefiles and 249 fungal treefiles**, with zero failed selected files. They also report larger archive totals (1,564 animal and 2,514 fungal files); the workflow selected near-universally single-copy orthologous treefiles, so the denominators are the processed sets, not all archive members. One Luna replicate-3 preliminary combined run had 349 rows with a blank group and could not itself provide separate medians; its later grouped output did. The custom Newick parser's 0.050139847768049167 and PhyKIT's 0.0501 show a precision/method difference that should remain visible. The task has no independently supplied difficulty category, and one task cannot establish model-level route variability generally.

### Token cost, provenance, and readability

Provider-reported input, output, cached-input, reasoning tokens, and monetary cost were not retrieved for either condition. Token ratios, correct results per token, and explanations based on retries cannot be calculated. Public Galaxy job and dataset records make tool IDs, input associations, parameters, output states, and one error inspectable; this is a provenance observation. No blinded human review or time-to-reconstruct study was supplied, so improved human readability is **not measured**. See finding `cost-readability-unavailable`.

## 4. Per-model and replicate routes

| Galaxy run | Recorded route and rationale | Analysis jobs; failed | Final visible artifact or limit |
|---|---|---:|---|
| GPT-5.5 r1 | PhyKIT probe, then custom Galaxy script invoking PhyKIT over ZIP treefiles and computing medians | 2; 0 | Explicit difference 0.0501 plus group details |
| GPT-5.5 r2 | PhyKIT metrics separately for animal and fungal ZIPs | 2; 0 | Per-tree values; auditor difference 0.0501 |
| GPT-5.5 r3 | Custom Galaxy script parsing Newick branch lengths and taking medians | 1; 0 | Explicit difference 0.050139847768049167 |
| Sol r1 | PhyKIT metrics on both groups | 2; 0 | Per-tree values; auditor difference 0.0501 |
| Sol r2/r3 | PhyKIT on combined and separate ZIP inputs; Datamash grouped median in one shared history | 4; 0 **combined** | Group medians 0 and 0.0501; two replicate labels share evidence |
| Luna r1 | PhyKIT probe and separate group metrics | 3; 0 | Per-tree values; auditor difference 0.0501 |
| Luna r2 | Public history metadata only | Unknown | 8,801 reported contents; detailed API timed out |
| Luna r3 | PhyKIT preliminary and corrected grouping; Datamash column 4 failed, column 5 succeeded | 6; 1 | Group medians 0 and 0.0501 |
| DeepSeek r1 | PhyKIT metrics and Galaxy Summary Statistics for each group | 4; 0 | Summary medians 0 and 0.0501 |
| DeepSeek r2 | One PhyKIT metrics job on both ZIPs | 1; 0 | Per-tree values; auditor difference 0.0501 |
| DeepSeek r3 | PhyKIT probe and combined metrics | 2; 0 | Per-tree values; auditor difference 0.0501 |

The [recovered-code manifest](recovered_code/manifest.json) links the two custom Python payloads to their Galaxy job command lines and SHA-256 hashes. These are archival copies; neither payload was run in this audit. All twelve open-ended-code routes remain unknown because the supplied trace source was inaccessible.

## 5. Inputs, external computation, and reproducibility

The two key source ZIP names, `scogs_animals.zip` and `scogs_fungi.zip`, each resolve to **one underlying Galaxy dataset ID and one original creating job** across the ten detailed histories. Their repeated history associations are object reuse, not ten independent uploads. The original fetch jobs predate the July and August history creation times. Their source checksums and association IDs are recorded in [input_manifest.json](input_manifest.json) and each run's artifacts. The Sol shared history contains later added input associations as well as earlier analytical outputs; a current snapshot cannot allocate all of them to one purported replicate.

The retained snapshots include history metadata, all returned dataset entries including errors, and creating jobs with commands, parameters, inputs, outputs, and stderr. The [selected output manifest](selected_outputs/galaxy/manifest.json) contains **56 downloaded small analytical outputs**, with byte counts and SHA-256 hashes; all downloaded sizes matched Galaxy metadata. Account identifiers were redacted from retained JSON. We did not save secret-bearing originals. The three transient output download failures were retried and resolved. The oversized Luna history and inaccessible Hugging Face traces remain reproducibility limits.

## 6. Methods and safeguards

Galaxy reads used `GET /api/histories/{id}`, `/contents?details=all`, and `/api/jobs/{job_id}?full=true` at `usegalaxy.org`; no job submission occurred. Dataset association ID, not display number, is the artifact key. Jobs were deduplicated by native creating-job ID within the Galaxy server. Input fetches were separated from analysis jobs; outputs of one job were not counted as independent attempts. Where a complete per-tree `group`/`value` table was downloaded, the auditor took Python `statistics.median` separately by group and subtracted animals from fungi. Repeated outputs in the Sol shared history do not change those medians and are not counted as independent histories. This auditor calculation is separate from the original agent chronology and from official scoring.

No cross-condition matching estimate, bootstrap, equivalence test, cost attribution, or human review was possible. The run inventory is based on the links supplied here; no independent protocol establishes its completeness. All numeric claims above can be recalculated from [history_analysis_evidence.json](history_analysis_evidence.json) and the retained outputs.

## 7. Claim-to-evidence map

| Proposed manuscript sentence | Finding ID | Primary records |
|---|---|---|
| Ten distinct detailed Galaxy histories support a difference near 0.0501 in saved outputs. | `galaxy-output-convergence` | Per-run artifact IDs and SHA-256 hashes in evidence JSON; selected output files |
| Twelve supplied Galaxy labels resolve to eleven public history IDs. | `galaxy-history-coverage` | Source IDs and `run_manifest.json` |
| Twenty-seven distinct analytical jobs include one failed Datamash job, later corrected on the same input. | `galaxy-observed-failures` | Job ledgers and `recovery_luna_r3_datamash` |
| Both installed PhyKIT and custom Galaxy-hosted scripts were used. | `routes-observed` | Job tool IDs and recovered-code manifest |
| An official condition accuracy or token-cost comparison cannot be estimated from these supplied sources. | `accuracy-unavailable`, `cost-readability-unavailable` | Source access statuses and null official/usage fields |

## 8. Missing evidence and next data

To assess official accuracy, obtain each fixed submitted answer, submission time, evaluator output, and original scoring version without changing those answers. To compare conditions, obtain the twelve open-ended-code traces and verify prompt additions, model runtime IDs, seeds, budgets, and replicate independence. To finish Luna replicate 2, retrieve a bounded, successful contents/job snapshot for the 8,801-dataset history or an original run-specific trace that identifies its relevant objects. Provider usage records and a prespecified blinded review protocol are needed for token and readability questions. No unknown metric is encoded as zero.

### Abstract-ready paragraph

In a selected BixBench treeness task, 12 supplied Galaxy replicate labels mapped to 11 distinct public histories. Ten histories yielded detailed outputs; all ten supported a fungi minus animals median treeness difference near 0.0501. Their snapshots contained 27 distinct analytical jobs, including one failed Datamash job followed by a successful column correction. Official submitted-answer scores and open-ended-code traces were unavailable, so this case cannot estimate a condition accuracy or cost difference.

### Results draft

We audited 24 supplied links for one BixBench question: four model labels, three replicate labels, and Galaxy versus open-ended-code conditions. Twelve Galaxy labels resolved to 11 distinct history IDs because GPT-5.6 Sol replicates 2 and 3 shared a link. Of these, 10 histories returned detailed contents and creating-job metadata; the remaining history reported 8,801 datasets but its contents endpoint timed out. The detailed histories contained 27 distinct analytical jobs after excluding shared input fetches. One job failed when Datamash treated a text treeness header as a numeric value; a later job on the same input changed the median column from 4 to 5 and succeeded. Saved Galaxy outputs from all 10 detailed histories supported a fungi minus animals median difference within 0.00005 of 0.0501, including one custom-script output of 0.050139847768049167. These are output-level observations, not official answer scores. The twelve supplied open-ended-code trace links returned HTTP 401, and no submitted answers, evaluator records, token usage, or human review data were retrieved. Consequently, this case supports a description of Galaxy execution routes and one operational recovery, but no claim of comparative accuracy, cost, or readability.
