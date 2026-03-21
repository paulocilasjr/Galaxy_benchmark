Experiment name: experiment_5
Initial objective: Execute the paired-end RNA-seq analysis experiment in Galaxy with full traceability and capture the analysis type, an expected output artifact, and the workflow step count.
Inputs and datasets:
- SRR5085167_forward.fastqsanger.gz from https://zenodo.org/records/13987631/files/SRR5085167_forward.fastqsanger.gz
- SRR5085167_reverse.fastqsanger.gz from https://zenodo.org/records/13987631/files/SRR5085167_reverse.fastqsanger.gz
Planned steps:
1. Read benchmark instructions and experiment definition.
2. Validate Galaxy credential availability and infer the Galaxy instance for experiment_5.
3. Discover the matching paired-end RNA-seq workflow/tool chain and confirm input requirements.
4. Create or identify the Galaxy history, upload inputs, and launch the workflow/tool chain.
5. Poll Galaxy until terminal state and inspect output artifacts.
6. Write result.json and a reproducibility script.
7. Read ground truth only after result generation and produce a comparison report.
Expected outputs:
- analysis_type
- artifact
- workflow steps
- comparison report
Risks/assumptions:
- experiment_5 omits galaxy_instance; assume https://usegalaxy.org/ unless discovery proves another instance is required.
- public workflow/tool availability may differ from prompt wording and may require workflow discovery before execution.
- large RNA-seq jobs may fail or take extended time; failures must follow the recovery protocol.
