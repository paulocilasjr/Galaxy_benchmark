# Plan for comparative-genomics diamond/inflation rerun

- Experiment name: comparative-genomics
- Public task prompt:
  - `Reconstruct phylogeny and identify COGs across four Micrococcus genomes; filter clusters present in all genomes, coding-only, with high-confidence annotations.`
  - `Output CSV columns: cluster_number,consensus_annotation. Run the analysis inside the Galaxy environment.`
- Objective: rerun the Galaxy comparative-genomics step with lower inflation but a faster search engine so the job is more likely to complete while still reducing orthogroup fragmentation.
- Attempt identity:
  - try label: `try_3_diamond_inflation_1.2`
  - predecessor: `outputs/20260413_201917_bioagent_comparative-genomics_rerun_blast`
  - key change from predecessor: keep `inflation=1.2` but revert `search_program` from `blast` to `diamond` after the blast attempt stalled
- Inputs and datasets:
  - prior Galaxy history: `bbd44e69cb8906b58f94567c3eb106f4`
  - Prokka protein FASTAs from the four successful genomes: hids 20, 32, 44, 56
  - prior successful OrthoFinder rerun artifacts: `outputs/20260413_200056_bioagent_comparative-genomics_rerun/results/orthofinder_hogs/`
  - failed blast/inflation rerun: `outputs/20260413_201917_bioagent_comparative-genomics_rerun_blast/`
  - truth-guidance available post hoc from `ground_truth/BioAgent/task_2.json`
- Ordered plan:
  1. Reuse the same four Galaxy `Prokka` FAA outputs in a fresh `OrthoFinder` run.
  2. Set `search_program=diamond`.
  3. Set `inflation=1.2`.
  4. Download the new orthogroup outputs and compare OG/HOG-level mappings against the missing truth labels and the prior rerun score.
  5. Write a new result bundle and score summary.
- Expected outputs:
  - fresh Galaxy `OrthoFinder` outputs
  - rerun `results/result.json`
  - rerun comparison against task-2 truth
- Risks/assumptions:
  - Lower inflation may improve recall but could also merge distinct functions.
  - The search change is chosen for completion reliability after the blast attempt stalled in the Galaxy queue.
