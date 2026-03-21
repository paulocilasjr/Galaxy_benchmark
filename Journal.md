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
