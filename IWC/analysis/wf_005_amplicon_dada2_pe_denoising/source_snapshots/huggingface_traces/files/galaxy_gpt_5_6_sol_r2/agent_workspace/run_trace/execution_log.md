# Galaxy execution log

- Assigned history: `bbd44e69cb8906b5662bfb4c3f2290f4` (`run-d6a73ae07fac4103949432e70fdf700b`); no other history was used.
- Input: history collection `6b86e99cdbbceff8`, `list:paired`, 17 primer-free 2x250 bp samples.
- Imported the paired collection with QIIME 2 `tools import-fastq` 2026.1.0 (job `bbd44e69cb8906b559c06a6a58fc04e1`).
- Denoised with QIIME 2 DADA2 `denoise-paired` 2026.1.0 (job `bbd44e69cb8906b566fe96099fc61f29`): truncation 240/200 bp (forward/reverse), trim-left 0/0, maxEE 2/2, truncQ 2, minimum overlap 12, zero merge mismatches, independent inference, and consensus de novo chimera removal. All 17 samples were retained.
- DADA2 QC: 89.18-97.40% of reads passed filtering; 78.14-95.84% merged; 76.67-94.70% of input reads were retained as non-chimeric across samples.
- Exported the chimera-filtered feature table and representative sequences from the same DADA2 job, then deterministically replaced hashed feature IDs with their corresponding ASV sequences and restored the supplied input sample order.
- Final validation: 330 unique ASVs, 17 exact sample identifiers, 18 fields per row, uppercase A/C/G/T sequences only, nonnegative integer raw counts, no duplicate sequences, and every sample-column sum equals its Galaxy DADA2 non-chimeric read count. ASV lengths: 49 at 252 bp, 272 at 253 bp, and 9 at 254 bp.
- Deliverable SHA-256: `0eb6b0c1ec41ddb026a4ff5a8cd0beae083de21273dc5cecd2fcfdcdb650e97c`.
