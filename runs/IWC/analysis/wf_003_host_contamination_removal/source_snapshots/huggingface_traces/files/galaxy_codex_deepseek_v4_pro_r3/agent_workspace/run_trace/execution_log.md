# Execution log

## Task

Filters paired-end short reads against the hg38 human reference and retains
read pairs not classified as valid paired-end (concordant) alignments.

## Galaxy history

- `bbd44e69cb8906b5e3824bf4369367c7` (assigned history)
- Input collection: `Short-reads` (`list:paired`)
- Created paired collection `Short-reads-pair` in the same history from the
  supplied forward and reverse datasets so Bowtie2 could consume it as a
  paired collection.

## Tool and parameters

- Tool: Bowtie2 (`toolshed.g2.bx.psu.edu/repos/devteam/bowtie2/bowtie2/2.5.5+galaxy0`)
- Reference: Galaxy built-in `hg38` Bowtie2 index
- Input mode: paired-end collection
- Paired-end options: defaults (`--fr`, `-I 0`, `-X 500`)
- Output unaligned read pairs: enabled (`--un-conc-gz`)
- Output aligned read pairs: disabled
- Analysis mode: default setting only
- Mapping statistics: saved

The `--un-conc` output retains the original mate-pair records for pairs that
Bowtie2 did not classify as concordant paired-end alignments under its default
paired-end criteria.

## Bowtie2 mapping statistics

- 78,090 read pairs in total
- 72,867 pairs aligned concordantly 0 times and were retained
- 4,711 pairs aligned concordantly exactly once (removed)
- 512 pairs aligned concordantly >1 times (removed)
- Overall alignment rate: 46.43%

## Outputs

- `final_answer/filtered_forward.fastqsanger.gz`
- `final_answer/filtered_reverse.fastqsanger.gz`

Both files contain 72,867 FASTQ records, pass `gzip -t`, and their read
identifiers are in the same order after removing the `/1` and `/2` mate
suffixes.
