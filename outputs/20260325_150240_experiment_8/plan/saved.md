# experiment_8

## Experiment name
- experiment_8

## Initial objective
- I need to perform a genome annotation of the samples I got and evaluate the quality of the annotation. The inputs that I have are FASTA files for genome, protein and some auxiliary datasets to perfrom the analysis. All files are in the dataset/experiment_8 directory. Run the tools in Galaxy necessary to achieve the two goals setted.

## Inputs and datasets
- S_pombe_chrIII_genome.fasta: dataset/experiment_8/S_pombe_chrIII_genome.fasta (Genome sequence for annotation, QC, transcript extraction, and visualization.)
- S_pombe_trinity_assembly.fasta: dataset/experiment_8/S_pombe_trinity_assembly.fasta (Transcript evidence for Maker.)
- Swissprot_no_S_pombe.fasta: dataset/experiment_8/Swissprot_no_S_pombe.fasta (Protein evidence for Maker.)
- augustus_training.tar.gz.augustus: dataset/experiment_8/augustus_training.tar.gz.augustus (Custom Augustus training bundle for Maker.)
- snap_training.snaphmm: dataset/experiment_8/snap_training.snaphmm (SNAP training model for Maker.)

## Planned steps
1. Validate the Galaxy API credential in the repository .env file.
2. Recreate the tool-discovery evidence that links this dataset bundle to the GTN Maker short tutorial and the installed usegalaxy.org tool IDs.
3. Create a fresh Galaxy history on usegalaxy.org for this benchmark run.
4. Upload the genome, transcript evidence, protein evidence, custom Augustus model, and SNAP model from dataset/experiment_8.
5. Run Fasta Statistics and BUSCO on the genome as the tutorial-aligned pre-annotation QC steps.
6. Run Maker with transcript evidence, protein evidence, the custom Augustus model, the SNAP model, and repeat masking disabled as specified by the matching tutorial.
7. Run Genome annotation statistics, GFFread, BUSCO on the predicted transcripts, Map annotation ids, and JBrowse in sequence.
8. Write result.json and keep this reproduce_experiment_8.py script as the reproduction artifact.
9. Only after result.json exists, read ground_truth/experiment_8.json and generate a field-by-field comparison table.

## Expected outputs
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_150240_experiment_8/plan/saved.md
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_150240_experiment_8/reasoning/reasoning.md
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_150240_experiment_8/errors/error.json
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_150240_experiment_8/results/result.json
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_150240_experiment_8/results/activity_log.jsonl
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_150240_experiment_8/results/comparison.md

## Risks/assumptions
- The exact input filenames match the GTN "Genome annotation with Maker (short)" tutorial, so the tutorial is the narrowest defensible execution pattern.
- BUSCO is installed on usegalaxy.org at a newer version than the tutorial, so lineage selection is mapped to the current auto-lineage eukaryote option instead of the older static Fungi selector.
- The benchmark field `total_tools` is ambiguous about repeated BUSCO usage, so the final result will record both the 8 executions and the 7 unique tool names.
