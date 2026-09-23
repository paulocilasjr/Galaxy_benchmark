# Short-read QC/trimming execution log

## Objective
Perform paired-end quality control/trimming with:
- adapter removal via mate-overlap analysis only
- no supplied adapter sequence or separate adapter autodetection
- low-quality base threshold: Phred < 20
- discard a pair if either mate has >40% low-quality bases, >5 Ns, or post-adapter length < 15
- no other trimming or base correction

## Input
- Assigned Galaxy history: `bbd44e69cb8906b5ea315934818e3d1e`
- Input collection: `Raw reads` (`list:paired`, HDCA `ac35edac99e04ac3`)

## Galaxy work
1. Created a direct paired collection from the provided forward/reverse datasets:
   - HDCA: `22aaaa86bd59e985`, type `paired`
   - forward: `f9cad7b01a472135b1b95063e43eb774`
   - reverse: `f9cad7b01a4721355a54e0662f5b4230`
2. Ran fastp (`toolshed.g2.bx.psu.edu/repos/iuc/fastp/fastp/1.3.6+galaxy0`) with:
   - `single_paired_selector=paired_collection`
   - `detect_adapter_for_pe=true`
   - no adapter sequence supplied
   - `qualified_quality_phred=20`
   - `unqualified_percent_limit=40`
   - `n_base_limit=5`
   - `length_required=15`
   - polyG tail trimming disabled (`-G`)
   - polyX trimming, per-read quality cutting, and base correction disabled
3. Successful Galaxy job: `bbd44e69cb8906b55c86cdbbd98e0159`
   - Output paired collection: `2618c4bc488a6ccc`
   - forward dataset: `f9cad7b01a472135a15c8123d8c9a64a`
   - reverse dataset: `f9cad7b01a47213586c3786bc3726f90`

## Final deliverables
- `final_answer/trimmed_forward.fastqsanger.gz`
- `final_answer/trimmed_reverse.fastqsanger.gz`

## Verification
- Both gzip files pass `gzip -t`.
- Both mates contain 276,615 records.
- Base read identifiers (after stripping `/1` and `/2`) match exactly in order.
- Post-filter checks:
  - forward: N>5 = 0, length<15 = 0, lowQ>40% = 0
  - reverse: N>5 = 0, length<15 = 0, lowQ>40% = 0
- fastp JSON report confirms Q20/Q30 rates improved after filtering.

## Final file hashes
- trimmed_forward.fastqsanger.gz: `70a762d4a4ffdc55675673d16197d150`
- trimmed_reverse.fastqsanger.gz: `8af0f4bb420c835f154c0e7cdc3b4cf6`
