# Execution log
- History: bbd44e69cb8906b52d9bac9ef7920f7b
- Input: PE fastq input list:paired, SRR891269; created same-history paired collection c93858f87d9476d7 for tool compatibility.
- fastp: paired overlap adapter detection, Q20 low-quality threshold, 70 percent unqualified-base limit, min length 15; accepted output collection 5369696b6160f6c8.
- Bowtie2: hg19 built-in index, paired collection input, --no-mixed, --no-discordant, -X 2000; accepted BAM f9cad7b01a4721355bc816a01d77f025.
- Filtering: samtools view proper-pair flag, MAPQ >=30, exclude secondary/supplementary, BED of non-chrM hg19 contigs; accepted BAM f9cad7b01a47213538d03ce2ef4c04e1.
- Duplicate removal: Picard MarkDuplicates REMOVE_DUPLICATES=true; accepted BAM f9cad7b01a472135ddad88b1dbeae5d2.
- Query-name sort: Sambamba sort -n; accepted qname_sorted.bam f9cad7b01a472135b5e5f06fe36aa898.
- Peak calling: Genrich ATAC mode, no control, q <= 0.05, MAPQ 30; accepted peak dataset f9cad7b01a4721359f20c8557a3d0f1d.
- Final export: first three columns from Genrich output, no deduplication; 26,180 BED records.
