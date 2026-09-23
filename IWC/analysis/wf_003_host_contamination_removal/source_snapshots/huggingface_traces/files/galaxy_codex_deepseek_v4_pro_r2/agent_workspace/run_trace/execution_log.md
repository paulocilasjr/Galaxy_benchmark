# Host contamination removal run

Assigned Galaxy history: `bbd44e69cb8906b57db3a694a176f92a`.

Input collection:
- Outer collection: `list:paired` (`Short-reads`, `c4193068596995d3`)
- Inner paired collection: `bbd44e69cb8906b5f106bf831188a89f`

Steps:
1. Re-zipped the inner forward/reverse HDA elements into a top-level paired collection
   using the Galaxy collection operation `__ZIP_COLLECTION__`.
2. Ran Bowtie2 (`toolshed.g2.bx.psu.edu/repos/devteam/bowtie2/bowtie2/2.5.5+galaxy0`)
   against the built-in `hg38` Bowtie2 index with the new paired collection and default
   paired-end criteria. Enabled the wrapper's "write unaligned reads" option, which
   invokes `--un-conc` and writes the mate pairs that fail to align concordantly.
3. Exported the resulting forward/reverse mates as
   `final_answer/filtered_forward.fastqsanger.gz` and
   `final_answer/filtered_reverse.fastqsanger.gz`.

Verification:
- Both output files are valid gzip-compressed FASTQ.
- Both contain 72,867 reads.
- Forward/reverse read names match in order (0 mismatches).

Output collection:
- `4e02d70cfd0f5f5f` (`Bowtie2 on collection 17: unaligned read pairs`)
