# Comparison Report

## 2026-03-12T22:41:15Z | Blocker Snapshot Comparison

| Field | Agent Result | Ground Truth | Match Status | Notes |
|---|---|---|---|---|
| input | Workflow expects list:paired FASTQ input; this was provided as fastqsanger.gz forward/reverse files assembled into a list:paired collection. | collection or a list of datasets | mismatch | blocked run snapshot differs from target terminal output |
| last artifact | cutadapt_trimmed_sequences_plot_3_Obs_Exp (dataset:tabular, state=ok); run blocked before terminal completion. | bigwig | mismatch | blocked run snapshot differs from target terminal output |
| workflow steps | Workflow 'ATACseq (release v1.0)' has 27 tool steps excluding 4 input steps. | 27 | mismatch | blocked run snapshot differs from target terminal output |

## 2026-03-12T22:59:49Z | Final Completed Run Comparison

| Field | Agent Result | Ground Truth | Match Status | Notes |
|---|---|---|---|---|
| input | Workflow input requires a list:paired collection of FASTQ datasets; uploaded forward/reverse files were provided as fastqsanger.gz and assembled into list:paired(sample1: forward, reverse). | collection or a list of datasets | mismatch | semantic comparison required |
| last artifact | cutadapt_trimmed_sequences_plot_3_Obs_Exp (dataset:tabular, state=ok) | bigwig | mismatch | semantic comparison required |
| workflow steps | Workflow 'ATACseq (release v1.0)' contains 27 tool steps excluding 4 input steps; expected tool-step count for this release is 27 (match). | 27 | mismatch | semantic comparison required |
