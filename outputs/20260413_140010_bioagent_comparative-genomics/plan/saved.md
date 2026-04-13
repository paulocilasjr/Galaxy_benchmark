# Plan for comparative-genomics

- Experiment name: comparative-genomics
- Initial objective: Reconstruct phylogeny and identify orthologous gene clusters across four Micrococcus genomes, then report coding clusters present in all genomes with high-confidence consensus annotations.
- Inputs and datasets:
  - dataset URL: https://osf.io/download/68b20d89324caca584780a19/
  - reference URL: https://osf.io/download/688634a1c0fb9e14f4f27c3d/
- Ordered plan:
  1. Inspect the BioAgent task metadata and initialize the run artifacts.
  2. Fetch and inspect the public input archive to determine exact file formats and suitable Galaxy tools.
  3. Create a dedicated Galaxy history and import the required inputs.
  4. Run the comparative-genomics workflow/toolchain in Galaxy, monitor jobs, and adapt only if failure evidence justifies a change.
  5. Extract the final cluster table, derive the required CSV, and write a reproducible result bundle.
  6. After `results/result.json` and `results/reproduce_comparative-genomics.py` are complete, read hidden scoring assets and generate the comparison report.
- Expected outputs:
  - `results/result.json`
  - `results/reproduce_comparative-genomics.py`
  - `results/activity_log.jsonl`
  - comparison report and score summary
- Risks/assumptions:
  - The BioAgent import uses OSF-hosted archives rather than local `dataset/` files.
  - The Galaxy instance may not have every comparative-genomics tool expected by the original benchmark, so tool discovery may require a valid substitute.
  - The large actinobacterial reference archive may need remote import instead of local staging.
