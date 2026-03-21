# History Revisit Report (Latest)

- Timestamp: 2026-03-14T00:23:56Z
- Visible finished analysis outputs currently include mapped BAMs, bigWig coverage, StringTie and Cufflinks tabular outputs, featureCounts summaries, HTS-like counts, the final Counts Table, and the MultiQC HTML/stats pair.
- Visible unfinished items are limited to FastQC collections HIDs 156 and 157.

## Finished Visible Analysis Outputs

| HID | Name | Format | Result Summary |
|---|---|---|---|
| 21 | Mapped Reads | bam collection | 1 BAM, 43.6 MB |
| 63 | Mapped Reads | bam collection | Duplicate finished BAM result set, 43.6 MB |
| 90 | Both Strands Coverage | bigwig collection | 1 bigWig, 892.5 KB |
| 99 | uniquely mapped stranded coverage | bigwig collection | 2 bigWigs: forward 507.3 KB, reverse 490.2 KB |
| 107 | Gene abundance estimates from StringTie | tabular collection | 7,128 x 9; includes Coverage, FPKM, TPM |
| 110 | Genes Expression from Cufflinks | tabular collection | 7,128 x 13; gene-level FPKM table |
| 111 | Transcripts Expression from Cufflinks | tabular collection | 7,128 x 13; transcript-level FPKM table |
| 123 | FeatureCounts Summary Table | tabular collection | Assigned=74234, Unassigned_Unmapped=0 |
| 132 | Gene abundance estimates from StringTie | tabular collection | Duplicate finished StringTie result set |
| 135 | Genes Expression from Cufflinks | tabular collection | Duplicate finished gene-level Cufflinks result set |
| 136 | Transcripts Expression from Cufflinks | tabular collection | Duplicate finished transcript-level Cufflinks result set |
| 148 | FeatureCounts Summary Table | tabular collection | Duplicate finished featureCounts summary; Assigned=74234 |
| 150 | HTS count like output | tabular collection | 7,072 x 2; first counts include YDR387C=2, YDL094C=1 |
| 152 | Counts Table | tabular collection | 7,128 x 2; first counts include YDR387C=2, YDL094C=1 |
| 154 | MultiQC ... Webpage | html | 2.2 MB HTML report |
| 155 | MultiQC ... Stats | tabular | 3 x 17; includes featurecounts-assigned and STAR mapping metrics |

## Visible Unfinished Items

| HID | Name | State |
|---|---|---|
| 156 | FastQC on collection 8: Webpage | new |
| 157 | FastQC on collection 8: RawData | new |
