# Execution summary

- Galaxy history: `bbd44e69cb8906b563d8d1d83ed36c59` (`run-e5523d7c58d3432788f26aa7cd5791c1`)
- Reference: pinned UCSC `hg38.fa.gz`; verified MD5 `1c9dcaddfa41027f17cd8f7a82c7293b`; staged as Galaxy dataset `f9cad7b01a472135e125e17023118eed`.
- Aligner: BWA-MEM 0.7.19 (`bwa_mem/0.7.19+galaxy1`), standard paired Illumina mode, no read trimming or custom alignment parameters. Alignment job `bbd44e69cb8906b502d87085b65121db` completed `ok` with matched parameter and dataset provenance.
- Retention rule: discard pairs marked by BWA-MEM as proper pairs (SAM flag `0x2`); retain all other primary pairs. Secondary and supplementary alignment records were excluded only to avoid duplicate FASTQ reconstruction.
- To preserve original FASTQ text, retained QNAMEs were applied to each original mate with Galaxy Filter sequences by ID, followed by Galaxy's datatype-preserving gzip converter. Final Galaxy datasets: forward `f9cad7b01a4721352ae7ba8c3a3d096e`; reverse `f9cad7b01a472135589f0387aefa3139`.
- Verification: 20,896 records per mate; valid gzip and four-line FASTQ structure; 0 mate-ID mismatches; 0 full-record mismatches; 0 order mismatches. SHA-256: forward `c523b87c853cc49ade54f32e5b58212f222c77ecb5d3153c7c1895edc3e7cf9c`; reverse `909c1929bdbe50b7645e66c77038191b0a034d22964f737a29a828f9284e0079`.
- Discarded branches: Bowtie2 wrapper attempts failed before command rendering; preliminary Samtools FASTQ reconstructions were superseded because they did not preserve complete original headers. None were exported as final deliverables.
