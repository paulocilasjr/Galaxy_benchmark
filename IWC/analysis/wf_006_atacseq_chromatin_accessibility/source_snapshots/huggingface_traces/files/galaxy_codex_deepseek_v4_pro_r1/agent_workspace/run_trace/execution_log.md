# ATAC-seq workflow execution log

Assigned Galaxy history: `bbd44e69cb8906b541daa8b702aece3f`

1. Prepared the paired FASTQ input as a paired collection from the provided list:paired collection.
2. Ran `fastp` (1.3.6+galaxy0) with paired collection input, adapter auto-detection for paired-end/mate-overlap, qualified quality Phred 20, unqualified percent limit 70, and minimum read length 15.
3. Aligned filtered pairs with `Bowtie2` (2.5.5+galaxy0) against built-in hg19.
4. Coordinate-sorted with Picard `SortSam`, then removed PCR duplicates with Picard `MarkDuplicates` (`REMOVE_DUPLICATES true`).
5. Filtered with `Samtools view` to paired/proper-pair alignments with MAPQ >= 30 and excluded mitochondrial (`chrM`) records.
6. Called peaks with `MACS2 callpeak` using `BAMPE` format, effective genome size 2.7e9, no control, q-value cutoff 0.05.
7. Exported the narrowPeak output to `final_answer/peaks.bed` as the first three tab-separated columns only.

Final aligner: Bowtie2
Final peak caller: MACS2
