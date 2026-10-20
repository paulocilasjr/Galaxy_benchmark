# Galaxy execution log

- History: `run-c274594b644446d29dcba8543302cc93` (`bbd44e69cb8906b579fdd0cd503df96e`), using the original paired collection.
- Preprocessing: fastp 0.23.4 (`bbd44e69cb8906b563e79c82d94fbe80`), paired-end overlap adapter detection, `-q 20 -u 70 -l 15`; output HIDs `f9cad7b01a472135157247a2941ac56d`, `f9cad7b01a472135906248bf81595e19`.
- Alignment: Bowtie2 2.3.4.3 (`bbd44e69cb8906b5440cc4496c22ac09`), built-in hg19 index, paired-end `--no-mixed --no-discordant`; sorted BAM HID `f9cad7b01a472135199676db5d645b73`.
- Alignment filtering: samtools view 1.22 (`bbd44e69cb8906b58a8d6916464bca72`), proper-pair flag, MAPQ 30, and expression excluding `chrM`/`MT`; BAM HID `f9cad7b01a4721357493403b71103d56`.
- Duplicate removal: Picard MarkDuplicates 3.1.1.0 (`bbd44e69cb8906b57df953f2c3d45a25`), `REMOVE_DUPLICATES=true`; BAM HID `f9cad7b01a472135f0c19012d2a6a052`.
- Peak calling: MACS2 callpeak 2.2.9.1 (`bbd44e69cb8906b5a00322f96fcef0b9`), `BAMPE`, hg19 effective genome size `2700000000`, no control, narrow peaks, q-value `0.05`; BED HID `f9cad7b01a4721351fbd12adf2cd4c6d`.
- Export: Galaxy Cut selected columns 1–3 (HID `f9cad7b01a472135bc1d4ac6d1f12f85`); Galaxy AWK range extraction exported all 38,549 records in 78 contiguous blocks. Local validation found 38,549 lines, exactly three tab-separated columns per line, and zero invalid intervals.
