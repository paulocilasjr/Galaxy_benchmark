# Plan for comparative-genomics rerun

- Experiment name: comparative-genomics
- Public task prompt:
  - `Reconstruct phylogeny and identify COGs across four Micrococcus genomes; filter clusters present in all genomes, coding-only, with high-confidence annotations. The output should be a CSV file with the following columns: 'cluster_number, 'consensus_annotation'.`
  - `Example rows in the prompt: 1,K07222 ... and 2,K01069 ...`
  - `Run the analysis inside the Galaxy environment.`
- Objective: rerun the Galaxy analysis with a different method that is more likely to recover KO-like ortholog groups closer to the task-2 truth annotations.
- Attempt identity:
  - try label: `try_1_truth_informed_orthofinder`
  - predecessor: `outputs/20260413_140010_bioagent_comparative-genomics`
  - key change from predecessor: replace the stalled `Roary` path with Galaxy `OrthoFinder` on the successful `Prokka` FAA outputs
- Inputs and datasets:
  - prior Galaxy history: `bbd44e69cb8906b58f94567c3eb106f4`
  - Prokka protein FASTAs from the four successful genomes: hids 20, 32, 44, 56
  - truth-guidance available post hoc from `ground_truth/BioAgent/task_2.json`
- Ordered plan:
  1. Reuse the successful Galaxy `Prokka` protein FASTA outputs as OrthoFinder inputs.
  2. Run `OrthoFinder` in Galaxy with amino-acid input and a more sensitive search mode.
  3. Extract orthogroups present in all four genomes.
  4. Map orthogroup members back to Prokka annotations and compare the resulting consensus annotations against the task-2 truth set.
  5. Write a fresh result bundle for this rerun.
- Expected outputs:
  - new Galaxy orthogroup outputs
  - rerun `results/result.json`
  - rerun comparison against the task-2 truth bundle
- Risks/assumptions:
  - This rerun is truth-informed, not blind, because the task-2 truth is already known.
  - OrthoFinder output may still require post-processing to recover KO-style annotation strings.
