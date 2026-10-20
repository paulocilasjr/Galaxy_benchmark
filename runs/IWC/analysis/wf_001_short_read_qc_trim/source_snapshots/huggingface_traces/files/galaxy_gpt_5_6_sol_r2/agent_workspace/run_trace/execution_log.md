# Execution log

- Assigned Galaxy history: `bbd44e69cb8906b5714c5cd0ef86f866` (`run-538946b498ef4a1e8382f05849ca501b`)
- Input: `Raw reads`, collection ID `3b26f06545a541ba`, type `list:paired`.
- Selected Galaxy tool: fastp `1.3.6+galaxy0`.
- Requested processing: paired overlap adapter trimming enabled; adapter sequences unset; paired-end adapter-sequence autodetection disabled.
- Pair filters: low-quality threshold Phred 20; reject when low-quality bases exceed 40%; reject when N count exceeds 5; reject when post-adapter-trim length is below 15 bp.
- Explicitly disabled/not enabled: fixed front/tail trimming, quality-window trimming, poly-G trimming, poly-X trimming, low-complexity filtering, UMI processing, read merging, and overlap base correction.
- The initial API-format test resolved to single-end defaults and was rejected from use. A correctly resolved map-over-`list:paired` submission then failed before command rendering. To avoid that Galaxy mapping issue, a direct `paired` collection (`410d99e0701820da`) was assembled in the assigned history from the same forward/reverse collection elements; no datasets from another history were accessed or copied.
- Accepted Galaxy job: `bbd44e69cb8906b5219b5729fc387219` (state `ok`, exit code 0). Parameter provenance matched all 34 checked values. Output collection: `a830494a08e88fa4`.
- Accepted output datasets: forward `f9cad7b01a472135961e6c916934da6c`; reverse `f9cad7b01a4721350dad4992aef72794`.
- Galaxy report: 377,961 input pairs; 277,113 retained pairs; 89,226 reads overlap-adapter-trimmed (2,091,846 bases); post-filter Q20 was 99.0689% for read 1 and 98.4801% for read 2.
- Export validation: both gzip streams passed integrity checks; each contains 277,113 valid FASTQ records; mate IDs are synchronized with zero mismatches; observed lengths are 31--101 bp; no output mate has more than 5 Ns or more than 40% bases below Phred 20.
- SHA-256: forward `acff6ece4bcc20a9a6816e8d72f5e66cd284f1bb70b8db6940cf83a0f677fee2`; reverse `099c3e62a1226c0108318ac99e4eb770dae9660f74b156b7c75d7dce409e857c`.
