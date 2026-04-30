# Initial Plan

## Objective

Identify the recessive causal variant for cystic fibrosis in the simulated CEPH family sequencing dataset for affected siblings NA12885, NA12886, and NA12879, using Galaxy execution evidence. Produce a final CSV with columns:

chromosome, position, variant_id, reference, alternate, gene_name, gene_id, annotation, impact, transcript_id, hgvs_c, hgvs_p, clinical_significance, diseases, review_status, rs_id.

## Input Datasets

- Variant dataset URL from `experiments/BioAgent/task_3/description.json`: `https://osf.io/download/68b20df289a6df6718780c40/`
- Reference/annotation URL from `experiments/BioAgent/task_3/description.json`: `https://osf.io/download/68345adb08d1077918ab8378/`
- Ground truth metadata for evaluation: `ground_truth/BioAgent/task_3.json`

## Intended Galaxy Path

1. Create a fresh Galaxy history for this run.
2. Upload the two task inputs to Galaxy by URL so Galaxy preserves the source data in history.
3. Inspect the uploaded dataset metadata and content enough to determine the file types and available fields.
4. Run Galaxy-compatible filtering/query operations to isolate variants that are recessive in the three affected siblings.
5. If the uploaded data already contains annotations needed by the prompt, use Galaxy tabular manipulation tools to filter and select the required fields.
6. If annotation is split between the variant dataset and reference file, use Galaxy join/filter operations to combine them before selecting the causal candidate.
7. Download the original Galaxy output(s) used for evaluation unchanged into `results/original_galaxy_outputs/`.
8. Create a separate Galaxy-derived transformed CSV only if the original Galaxy output is tool-native and not already prompt-shaped.

## Intended Tool Choices

- Galaxy upload by URL for both input artifacts.
- Galaxy tabular inspection and manipulation tools when available: select/filter/query, join, cut, sort, and/or similar data-table operations.
- Galaxy metadata/provenance APIs for history, dataset, and job snapshots.

## Expected Result Files

- Original Galaxy output file(s) preserving the candidate causal variant evidence.
- A prompt-shaped CSV, if a transformation from original Galaxy output is needed.
- Structured result, run record, manifests, evaluation comparison, and metric summary artifacts.

## Anticipated Risks

- Input URLs may resolve to archives or files whose names/formats are not evident until download/upload.
- Galaxy public server tool availability may differ from expected tabular or annotation tools.
- The reference artifact may already encode expected annotations, making annotation joins unnecessary but requiring careful provenance.
- If Galaxy cannot complete a specialized genetics operation, the run must preserve the failure evidence and stop or retry with a changed mechanism rather than blind retries.
