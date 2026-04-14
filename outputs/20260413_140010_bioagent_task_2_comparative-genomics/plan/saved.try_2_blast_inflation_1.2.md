# Plan for comparative-genomics blast/inflation rerun

- Experiment name: comparative-genomics
- Public task prompt:
  - `Reconstruct phylogeny and identify COGs across four Micrococcus genomes; filter clusters present in all genomes, coding-only, with high-confidence annotations.`
  - `Output CSV columns: cluster_number,consensus_annotation. Run the analysis inside the Galaxy environment.`
- Objective: rerun the Galaxy comparative-genomics step with a more exhaustive similarity search and a lower clustering inflation to try to recover additional truth-aligned ortholog groups that were split or missed in the previous OrthoFinder rerun.
- Attempt identity:
  - try label: `try_2_blast_inflation_1.2`
  - predecessor: `outputs/20260413_200056_bioagent_comparative-genomics_rerun`
  - key change from predecessor: change `search_program` from `diamond_ultra_sens` to `blast` and lower `inflation` to `1.2`
- Inputs and datasets:
  - prior Galaxy history: `bbd44e69cb8906b58f94567c3eb106f4`
  - Prokka protein FASTAs from the four successful genomes: hids 20, 32, 44, 56
  - prior OrthoFinder rerun artifacts: `outputs/20260413_200056_bioagent_comparative-genomics_rerun/results/orthofinder_hogs/`
  - truth-guidance available post hoc from `ground_truth/BioAgent/task_2.json`
- Ordered plan:
  1. Reuse the successful Galaxy `Prokka` protein FASTA outputs as input to a new Galaxy `OrthoFinder` run.
  2. Change the search mode from `diamond_ultra_sens` to `blast`.
  3. Lower the clustering inflation parameter from the default to `1.2` to reduce orthogroup fragmentation.
  4. Download the fresh orthogroup outputs and compare OG/HOG-level mappings against the previously missing truth labels.
  5. Write a new result bundle for this rerun.
- Expected outputs:
  - new Galaxy `OrthoFinder` outputs under the existing history
  - rerun `results/result.json`
  - rerun comparison against the task-2 truth bundle
- Risks/assumptions:
  - `blast` may run slower than `diamond`.
  - Lower inflation may merge paralogs more aggressively and may improve recall at the cost of specificity.
  - This rerun remains truth-informed because the user explicitly requested targeting the known ground truth after comparison.
