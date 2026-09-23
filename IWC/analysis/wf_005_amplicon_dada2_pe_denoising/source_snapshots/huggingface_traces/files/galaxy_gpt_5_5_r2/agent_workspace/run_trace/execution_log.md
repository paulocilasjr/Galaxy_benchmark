Galaxy history: bbd44e69cb8906b5e71bb32a88efbecb

Steps:
- Imported the assigned list:paired FASTQ collection with `qiime2 tools import-fastq`.
  - Job: bbd44e69cb8906b5f0ce08b942094ea8
  - Output: f9cad7b01a472135facfec10f3d8140c
- Denoised paired-end reads with `qiime2 dada2 denoise-paired`.
  - Job: bbd44e69cb8906b5dc2e81695728671c
  - Parameters: trim_left_f=0, trim_left_r=0, trunc_len_f=0, trunc_len_r=0, max_ee_f=2, max_ee_r=2, min_overlap=12, max_merge_mismatch=0, chimera_method=consensus, pooling_method=independent, retain_all_samples=true
  - Outputs: table f9cad7b01a47213517d9b8633f496488, representative sequences f9cad7b01a472135f0b94a2d10c1972e
- Exported the DADA2 feature table artifact as BIOMV210Format.
  - Job: bbd44e69cb8906b52b94b4cd6cabe74b
  - Output: f9cad7b01a472135f5b2c711d070970d
- Converted exported BIOM to classic TSV with `biom_convert`.
  - Job: bbd44e69cb8906b536b5a57cb3a1d7a0
  - Output: f9cad7b01a4721356ac87ec13020546c
- Joined raw counts to representative ASV sequences and wrote `final_answer/asv_abundance.tsv`.

Validation:
- Final table: 306 ASV rows, 17 sample columns plus `sequence`.
- Sample columns match the 17 supplied collection identifiers.
- Sequences are unique uppercase nucleotide strings.
- Counts are nonnegative integers.
