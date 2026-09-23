# Execution log

- Assigned Galaxy history: `bbd44e69cb8906b52dbafe55c82e5487`
- Input collection: `Short-reads` (`ecf12fb1e5686762`, `list:paired`)
- Aligner: BWA-MEM 0.7.19+galaxy1 using Galaxy built-in hg38 index
- Galaxy alignment input: paired forward/reverse FASTQ datasets from assigned history
- Galaxy BAM output dataset: `f9cad7b01a4721353cc3a72ed67b1822`
- Standard paired-end validity filter: BWA-MEM SAM flag `0x2` (proper pair)
- Proper-pair read-name list: `f9cad7b01a47213511870b974084a5b1`
- Retained reads: filtered original FASTQ files to exclude proper-pair read names,
  keeping forward and reverse synchronized by read name
- Read counts: 78,090 input pairs; 57,193 proper pairs; 20,897 retained pairs
- Final deliverables written under `final_answer/`
