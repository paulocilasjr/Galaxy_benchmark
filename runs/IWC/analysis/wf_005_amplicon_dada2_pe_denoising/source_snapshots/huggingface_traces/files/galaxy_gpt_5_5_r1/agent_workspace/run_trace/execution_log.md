Galaxy history used: bbd44e69cb8906b5353fa6bb3d7670a5

Inputs:
- Existing Galaxy collection: c32be032e5a46e57, "Paired input data", collection_type list:paired, 17 samples.

QC/parameter basis:
- Reads were 250/251 nt paired-end MiSeq reads.
- Primer-free reads, so DADA2 trim_left_f=0 and trim_left_r=0.
- Mean quality remained high through the reads; DADA2 used trunc_len_f=0 and trunc_len_r=0 to retain full overlap.

Galaxy jobs:
- QIIME2 tools import-fastq: job bbd44e69cb8906b5d7d8cd39f66c018e, output HID 70, qza SampleData[PairedEndSequencesWithQuality].
- QIIME2 dada2 denoise-paired: job bbd44e69cb8906b5e6d67335060692f9, outputs HID 71 table.qza, HID 72 representative_sequences.qza, HID 73 denoising_stats.qza, HID 74 base_transition_stats.qza.
- QIIME2 tools export table: job bbd44e69cb8906b52ed1ee3f040508ca, output HID 75 BIOM.
- QIIME2 tools export representative sequences: job bbd44e69cb8906b58715214608709000, outputs HID 76 tabular/FASTA.
- BIOM Convert to TSV: job bbd44e69cb8906b511ed97ea1156e820, output HID 79 tabular count table.

DADA2 settings:
- trim_left_f=0, trim_left_r=0
- trunc_len_f=0, trunc_len_r=0
- max_ee_f=2.0, max_ee_r=2.0
- trunc_q=2
- min_overlap=12
- max_merge_mismatch=0
- pooling_method=independent
- chimera_method=consensus
- min_fold_parent_over_abundance=1.0
- allow_one_off=false
- n_reads_learn=1000000
- hashed_feature_ids=true
- retain_all_samples=true

Finalization:
- Joined Galaxy BIOM-derived counts to exported representative sequences.
- Wrote /workspace/final_answer/asv_abundance.tsv with 306 ASV rows, 17 sample columns, uppercase sequences, and integer raw counts.
