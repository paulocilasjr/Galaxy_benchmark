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
