# BioAgent Task 2 Initial Plan

## Objective

Reconstruct phylogeny and identify orthologous gene clusters across four `Micrococcus` genomes in Galaxy, then produce a CSV with columns `cluster_number,consensus_annotation`.

## Input Datasets

- Task dataset URL: `https://osf.io/download/68b20d89324caca584780a19/`
- Task reference URL: `https://osf.io/download/688634a1c0fb9e14f4f27c3d/`
- Task definition: `experiments/BioAgent/task_2/description.json`

## Intended Analysis Path

1. Download and inspect the provided dataset and reference assets.
2. Create a fresh Galaxy history for this task.
3. Upload the task inputs into Galaxy.
4. Discover the most appropriate Galaxy orthology / comparative-genomics workflow or tool chain for four bacterial genomes.
5. Run the selected Galaxy analysis to obtain orthologous clusters and a phylogeny-backed comparative result.
6. Preserve the original Galaxy output artifact(s) unchanged under `results/original_galaxy_outputs/`.
7. If needed, derive a prompt-shaped helper CSV from the preserved Galaxy outputs without introducing new scientific content.
8. Compare the final preserved outputs against the prompt contract and ground truth.

## Intended Tool Choices

- Galaxy history creation and dataset upload
- Galaxy workflow and tool discovery via API
- Expected candidate tools: orthology / orthogroup inference, annotation transfer, tabular filtering, and CSV conversion

## Expected Result Files

- Original Galaxy output file(s) supporting ortholog cluster membership and annotation
- Prompt-shaped CSV `cluster_number,consensus_annotation`
- Preserved Galaxy history, dataset, and job traces

## Anticipated Risks

- The input URLs may package genomes in a non-obvious archive structure.
- `usegalaxy.org` may not expose the expected orthology workflow or tool.
- The available Galaxy outputs may require a deterministic format-only transformation to match the prompt.
- Long-running comparative genomics tools may require extended polling.

## Fallback Branches

- If the first candidate workflow is unavailable, search for a compatible Galaxy tool chain with equivalent orthology outputs.
- If the selected Galaxy execution produces multiple result tables, preserve them all and derive a helper CSV only from downloaded Galaxy outputs.
- If Galaxy exposes a stable pre-existing workflow matching the task better than an ad hoc tool chain, prefer the workflow.
