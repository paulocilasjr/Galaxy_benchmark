# History Revisit Report

- Timestamp: 2026-03-14T00:23:01Z
- History ID: `bbd44e69cb8906b56d7f0eb03f73cac5`
- Visible items: 29
- Hidden items: 128

## Invocation Snapshot
- `2494e85fc3e1f32f`: state=new workflow_id=8ce598eace0f2556 updated=2026-03-13T23:55:44.812729
- `a3d009c366bdfeeb`: state=ready workflow_id=0ac927bc4473993b updated=2026-03-14T00:14:56.695963
- `14d3a69611449895`: state=ready workflow_id=547ff3800b846d56 updated=2026-03-14T00:14:57.439737
- `488a07439e164b3a`: state=ready workflow_id=45b5203e68d49b5a updated=2026-03-14T00:14:57.133748
- `e5d32642b37f4c12`: state=ready workflow_id=b676a16e99fa0884 updated=2026-03-14T00:14:56.949811
- `b82e8bae1107c6df`: state=new workflow_id=8ce598eace0f2556 updated=2026-03-14T00:21:42.202692
- `77266417f49509bd`: state=scheduled workflow_id=0ac927bc4473993b updated=2026-03-14T00:21:41.492798
- `7a8a68abefb37d8f`: state=scheduled workflow_id=547ff3800b846d56 updated=2026-03-14T00:14:50.235881
- `efce3477099ce339`: state=scheduled workflow_id=45b5203e68d49b5a updated=2026-03-14T00:14:49.381657
- `a4245fa442769799`: state=ready workflow_id=b676a16e99fa0884 updated=2026-03-14T00:14:51.898697

## Finished Visible Analysis Outputs

| HID | Name | Format | Result Summary |
|---|---|---|---|
| 21 | Mapped Reads | bam | 1 BAM in collection; 43.6 MB |
| 63 | Mapped Reads | bam | 1 BAM in collection; 43.6 MB; duplicate finished mapped-read result set |
| 90 | Both Strands Coverage | bigwig | 1 bigWig; 892.5 KB |
| 99 | uniquely mapped stranded coverage | bigwig | 2 bigWigs: forward 507.3 KB, reverse 490.2 KB |
| 107 | Gene abundance estimates from StringTie | tabular | 7,128 lines x 9 columns; headers Gene ID/Gene Name/Reference/Strand/Start/End/Coverage/FPKM/TPM |
| 110 | Genes Expression from Cufflinks | tabular | 7,128 lines x 13 columns; FPKM table with FPKM_status column |
| 111 | Transcripts Expression from Cufflinks | tabular | 7,128 lines x 13 columns; transcript-level FPKM table |
| 123 | FeatureCounts Summary Table | tabular | 15 lines x 2 columns; Assigned=74234, Unassigned_Unmapped=0 |
| 132 | Gene abundance estimates from StringTie | tabular | Duplicate finished StringTie gene-abundance result set |
| 135 | Genes Expression from Cufflinks | tabular | Duplicate finished Cufflinks gene-expression result set |
| 136 | Transcripts Expression from Cufflinks | tabular | Duplicate finished Cufflinks transcript-expression result set |
| 148 | FeatureCounts Summary Table | tabular | Duplicate finished featureCounts summary result set; Assigned=74234 |
| 150 | HTS count like output | tabular | 7,072 lines x 2 columns; first rows include YDR387C=2 and YDL094C=1 |

## Finished Visible Preparatory Items

| HID | Name | Format | Notes |
|---|---|---|---|
| 1 | SRR5085167_forward.fastqsanger.gz | fastqsanger.gz | Input FASTQ, ok |
| 2 | SRR5085167_reverse.fastqsanger.gz | fastqsanger.gz | Input FASTQ, ok |
| 3 | Saccharomyces_cerevisiae.R64-1-1.113.gtf | gtf | Annotation input, ok |
| 4 | SRR5085167_paired_reads | list:paired | Input collection, ok |
| 5 | cufflinks_chrM_mask.gtf | gtf | Optional mask input added during retry, ok |
| 45 | Extract element identifiers on dataset 31 and collection 23 | txt | Contains SRR5085167 |
| 87 | Extract element identifiers on dataset 73 and collection 65 | txt | Contains SRR5085167 |
| 120 | Create text file | txt | FeatureCounts_was_not_used placeholder table |
| 121 | Text transformation on dataset 120 | tabular | Placeholder table rendered as 2-column tabular |
| 145 | Create text file | txt | Duplicate FeatureCounts_was_not_used placeholder table |
| 146 | Text transformation on dataset 145 | tabular | Duplicate placeholder table rendered as 2-column tabular |

## Visible Items Not Finished Yet

| HID | Name | Format | State |
|---|---|---|---|
| 156 | FastQC on collection 8: Webpage | list | new |
| 157 | FastQC on collection 8: RawData | list | new |

## Hidden Completed Intermediates

- There are many hidden `ok` intermediates, including flattened read collections, fastp outputs, STAR bedGraph coverage files, assembled transcripts, hidden tabular copies of StringTie/Cufflinks outputs, and hidden featureCounts/count-table intermediates.
- Notable hidden completed artifacts include BAMs at HIDs 29 and 71, bigWig datasets at HIDs 91, 100, 101, assembled-transcript GTFs at HIDs 108, 117, 133, 142, and hidden featureCounts summary tables at HIDs 124 and 149.
