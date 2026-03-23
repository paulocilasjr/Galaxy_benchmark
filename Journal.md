# Experiment 1

## What was found

- The earliest archived run for experiment 1 completed tool execution, but post-processing could not parse ROC-AUC because the extraction logic expected plain-text patterns while the metric was inside a zipped HTML report.
- The initial `result.json` therefore recorded `roc-auc` as `unknown`, even though the report artifact contained the metric.
- A versioned correction artifact later extracted ROC-AUC `0.76` from the HTML member inside the zip and matched ground truth.
- A later independent rerun completed without recorded execution errors, which indicates the main archived problem was output parsing fragility rather than Galaxy tool failure.

## Lesson learned

- Successful Galaxy execution is not enough if the metric-extraction path does not understand the actual output container format.
- Benchmark immutability is useful here: a corrected extraction should be written as a new artifact, not by overwriting the original result.

## How to prevent this

- Inspect output file types before parsing and support zipped HTML or other structured report formats directly.
- Prefer structured metric sources over loose regex on generic output text.
- Add a post-parse validation step that treats `unknown` for required metrics as an extraction failure that must be resolved before finalization.

# Experiment 2

## What was found

- No runtime or Galaxy execution errors were recorded in the archived experiment 2 run; all five Image Learner attempts completed successfully.
- The run still produced a benchmark mismatch: every attempt reported ROC-AUC `1.0000`, while the ground truth expected `0.93`.
- The likely source of the mismatch is metric extraction: the reported ROC-AUC was not the expected test ROC-AUC. It was most likely extracted from train metrics, and less likely from validation metrics, instead of from the benchmark-required test split.
- The archived trace also shows that the run used `selected_HAM10000_img_metadata_aug.csv` and grouped by `lesion_id` to mitigate leakage from augmented variants.

## Lesson learned

- A clean execution can still be benchmark-wrong.
- Repeated perfect metrics across multiple attempts should trigger metric-split verification even when no tool errors occur.
- For learner outputs that expose train, validation, and test metrics, the extraction step must explicitly bind to the benchmark-required split instead of relying on a generic ROC-AUC field.

## How to prevent this

- Validate the exact dataset provenance and split semantics against the benchmark expectation before launching multiple tuning attempts.
- Make the metric extractor explicitly select the test ROC-AUC field and record the exact metric path used in the artifact trail.
- Add a sanity check after the first successful baseline run; if the metric is suspiciously high, audit whether the value came from train, validation, or test before continuing.
- Record explicitly whether augmented examples are included and how grouping or split controls are enforced.

# Experiment 3

## What was found

- The first archived run failed before training because remote upload used a bad fetch endpoint and returned `404` with `No route for /api/api/tools/fetch`.
- The next archived run used a corrected remote-upload path, all three Zenodo datasets uploaded successfully, and the Multimodal Learner completed all five model attempts.
- The failure source was client-side upload construction, not unavailable remote files or instability in the Multimodal Learner itself.

## Lesson learned

- Transport-layer upload failures should be separated from dataset-availability failures.
- One successful smoke-test upload is enough to prove the remote source is reachable and the API path is correct before the main benchmark run proceeds.

## How to prevent this

- Use one validated Galaxy upload mechanism consistently for remote URLs.
- Add a preflight upload test for one representative remote file before starting the full run.
- Log the exact API path used for remote import so route-construction bugs are easy to diagnose.

# Experiment 4

## What was found

- The archived ATACseq run was temporarily classified as blocked when two final `deeptools_bigwig_average` jobs stayed in `running` with unchanged update timestamps for more than 10 minutes.
- The same run later completed successfully, and the blocker record was resolved afterward.
- The problem source was premature stall classification during a slow or stale Galaxy backend phase, not a permanent workflow failure.

## Lesson learned

- A stalled-looking history is not always a terminal blocker.
- Polling heuristics based only on unchanged job timestamps can be too aggressive for long-running late-stage aggregation jobs.

## How to prevent this

- Treat this pattern as a suspected stall first rather than an immediate terminal blocker.
- Re-check the history after a longer grace period before final blocker classification, especially when there are no error or paused datasets.
- Use tool-aware stall thresholds for heavy late-stage jobs instead of a single universal timeout.

# Experiment 5

## What was found

- Attempt 1 failed because the workflow invocation payload did not bind the required non-optional workflow input `Generate additional QC reports`.
- That payload-shape issue was corrected in attempt 2 by moving runtime parameter values into the workflow `inputs` map and addressing inputs with `inputs_by=name`.
- Attempts 2 and 3 were then accepted by Galaxy but never populated any workflow steps or jobs; both invocations remained in `state=new` with zero populated steps, even after a materially different retry that added the optional Cufflinks mask GTF.
- The archived run was therefore blocked by Galaxy workflow population rather than by credentials or broken data URLs.
- A smaller post-processing issue also appeared later: the first generated reproduction script needed a syntax fix before comparison.

## Lesson learned

- Workflow acceptance is not the same thing as workflow population.
- Correcting payload shape and diagnosing post-acceptance population stalls are different problems and need separate checks.

## How to prevent this

- Enumerate and bind every non-optional workflow parameter input explicitly before invocation.
- Add a hard population gate: if the invocation remains unpopulated for a short diagnostic window, stop and inspect the workflow/input contract immediately.
- After one payload correction and one materially different retry still yield `state=new` with zero steps, switch execution environment or workflow source instead of attempting a manual reimplementation.
- Run a syntax check on generated reproduction artifacts before considering result generation complete.

# Experiment 6

## What was found

- Experiment 6 ran successfully in Galaxy, but it used the older GTN workflow `Clustering 3k PBMC with Scanpy` (workflow version 5, 51 tool steps), not the newer parameterized workflow variant.
- The executed workflow used `Scanpy normalize` with `pp.normalize_total(target_sum=10000.0)`.
- The extracted dotplot genes were `IL7R, CCR7, CD8A, CD14, LYZ, MS4A1, CD79A, GNLY, NKG7, KLRB1, FCER1A, CST3, PPBP, FCGR3A`.
- This disagreed with the newer workflow/ground-truth expectation because the older workflow hardcodes marker genes, while the newer workflow derives them dynamically from ranked genes.
- A second issue appeared after execution: Galaxy history items used generic dataset names, so post-processing could not rely on expected tutorial-style output labels.

## Lesson learned

- Choosing the first workflow that looks like an exact tutorial match is not enough. It can still be an older lineage and produce different benchmark answers.
- The workflow-selection check must focus on the answer-bearing parts of the workflow, not only on the title or general description.

## How to prevent this

- Before execution, enumerate all compatible workflows and compare workflow name, authors, version/release, step count, and whether key outputs are hardcoded or derived dynamically.
- Prefer the newest compatible workflow in the same lineage instead of the first exact-name/tutorial match.
- Validate the specific steps that drive the benchmark result before running: normalization method, total tool-step count, and how the dotplot gene list is generated.
- After execution, map outputs from the actual Galaxy history dataset names rather than assuming workflow labels will be preserved in the history.

# Experiment 7

## What was found

- Experiment 7 did not complete successfully because the workflow repeatedly failed at `MMseqs2 Taxonomy Assignments` on `usegalaxy.org`.
- The source of the persistent workflow failure was the MMseqs2 taxonomy prefilter stage. Attempt 2 showed an explicit Slurm cgroup out-of-memory kill, and attempts 3 and 4 failed in the same step even after stronger memory-reduction overrides.
- The repeated failed outputs were `MMseqs2 Taxonomy Tabular` and `MMseqs2 Taxonomy Kraken`, and the repeated paused downstream outputs were the KrakenTools, Krona, and MultiQC taxonomy-dependent steps.
- A separate input-quality issue existed in the benchmark spec: `experiment_7.json` pointed to `./dataset/meta_genomic_R1.fastqsanger.gz` and `./dataset/meta_genomic_R2.fastqsanger.gz`, but the actual files were under `dataset/experiment_7/` with `meta_genomics_...` names.
- Two local orchestration bugs also caused avoidable problems during execution. The first runner polled the dataset collection incorrectly and stalled on an `unknown` state, and the next runner kept polling after Galaxy had already reached a terminal `error` state with paused descendants.

## Lesson learned

- When a failure stays pinned to one heavy Galaxy tool across multiple retries, the source is usually the execution environment or resource envelope, not the workflow graph itself.
- For benchmark runs, runner logic must treat Galaxy collection readiness and terminal failure states very carefully. Small polling mistakes can turn a real tool failure into a misleading timeout.
- Benchmark input declarations need validation before upload. A small path/name mismatch is easy to work around once, but it should not remain in the experiment definition.

## How to prevent this

- Add a preflight check that validates all experiment input paths against the repository before any Galaxy upload begins.
- Keep the collection polling fix: use HDCA `populated_state` and `populated` instead of relying on a generic collection `state` field.
- Keep the terminal-failure polling fix: if there are no active jobs and any datasets are in `error`, `paused`, or similar problem states, stop immediately and record the failure instead of waiting for timeout.
- Add a resource-risk preflight for heavy Galaxy tools such as MMseqs2 taxonomy. Check the available database, expected input size, and whether the target Galaxy instance is likely to have enough memory for that step.
- Prefer running this workflow on a Galaxy instance or queue with more memory for MMseqs2 taxonomy, or on an environment where the taxonomy database or job resources can be controlled.
- If the benchmark must stay on `usegalaxy.org`, avoid blind retries after the same MMseqs2 signature repeats. Only retry when there is a real mechanism change, such as a different execution environment or a justified workflow/tool substitution.
