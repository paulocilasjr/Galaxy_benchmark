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
2. Review the interrupted third attempt and verify that the remote Galaxy history still contains successful upstream outputs through GFFRead.
3. Reuse the finished history `experiment_8_20260325_152546` instead of re-running uploads, Maker, annotation statistics, or GFFRead.
4. Inspect the long-queued transcript BUSCO job and decide whether it is blocking the benchmark outputs.
5. Run Map annotation ids and JBrowse from the resumed Maker annotation state.
6. Write result.json and keep this reproduce_experiment_8.py script as the reproduction artifact.
7. Only after result.json exists, read ground_truth/experiment_8.json and generate a field-by-field comparison table.

## Expected outputs
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_184652_experiment_8/plan/saved.md
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_184652_experiment_8/reasoning/reasoning.md
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_184652_experiment_8/errors/error.json
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_184652_experiment_8/results/result.json
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_184652_experiment_8/results/activity_log.jsonl
- /Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_184652_experiment_8/results/comparison.md

## Risks/assumptions
- The exact input filenames match the GTN "Genome annotation with Maker (short)" tutorial, so the tutorial is the narrowest defensible execution pattern.
- Attempt 2 already validated that explicit BUSCO lineage `ascomycota_odb12` works on usegalaxy.org, so any BUSCO reasoning in this recovery uses that lineage as the established configuration.
- Attempt 3 already completed annotation statistics and GFFRead in the resumed history; if those datasets are no longer available, a broader rerun would be required.
- The transcript BUSCO job may remain queued due Galaxy scheduler delay. Because the experiment outputs depend on identifying the evaluation tool and the visualization tool, the run can still complete if genome BUSCO and JBrowse are available.
- The benchmark field `total_tools` is ambiguous about repeated BUSCO usage, so the final result will record both the 8 executions and the 7 unique tool names.
