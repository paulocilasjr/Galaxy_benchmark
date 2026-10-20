# Execution log

- Assigned Galaxy history: `bbd44e69cb8906b597036621dd2efd02` (`run-89f9f3e4d46b475a948b8df9f0c2d17b`).
- Input collection: `PE fastq input` (`b5968833e514367a`), `list:paired`, one paired element `SRR891269`.
- Planned workflow: fastp paired-overlap adapter/quality/length filtering; Bowtie2 paired-end alignment to built-in `hg19`; retain proper-pair MAPQ >= 30 non-mitochondrial alignments; remove PCR duplicates; MACS2 callpeak in `BAMPE` mode with q-value 0.05 and no control.
- Accepted trimming job: fastp job `bbd44e69cb8906b58f575c5f42e934a8` on the inner paired collection element, output collection `d4ac05671e3db150`; 111,613,648 reads passed filtering.
- Accepted alignment job: Bowtie2 job `bbd44e69cb8906b5d035a892c41ba360`, output BAM `f9cad7b01a47213595ecf0cde87042b8`; overall alignment rate 99.42%.
- Accepted filtering branch: samtools proper-pair/MAPQ>=30 BAM `f9cad7b01a472135e12e097d584c016c`; bamtools non-mitochondrial BAM `f9cad7b01a472135e9c64867abb517ff`.
- Accepted duplicate-removal job: Picard MarkDuplicates job `bbd44e69cb8906b515445e34b605d1d0`, duplicate-removed BAM `f9cad7b01a4721355c243455c0b8527e`; 16,353,729 read pairs examined, 25.28% duplication.
- Accepted peak calling job: MACS2 job `bbd44e69cb8906b59a0e658239aa39d6`, narrowPeak dataset `f9cad7b01a472135f74222f480e1ff05`; 33,488 regions.
- Final deliverables written: `final_answer/peaks.bed` and `final_answer/method.json`.
