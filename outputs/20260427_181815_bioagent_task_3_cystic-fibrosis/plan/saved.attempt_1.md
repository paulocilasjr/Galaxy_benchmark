# Retry Plan: Attempt 1

## What Changed

The first execution attempt uploaded the expanded `ex1.eff.vcf` file directly. Galaxy created a queued dataset with zero recorded file size and did not progress through repeated one-minute checks. The retry changes the upload mechanism, not the scientific criteria.

## Retry Objective

Run the same cystic-fibrosis causal-variant analysis in Galaxy, but upload the gzip-compressed VCF (`traces/local/inputs/ex1.eff.vcf.gz`) derived from the task archive. Galaxy should decompress/ingest it as tabular text before the same filter expression is applied.

## Inputs

- `traces/local/inputs/ex1.eff.vcf.gz`, gzip-compressed copy of the task VCF extracted from the OSF `data.tar.gz`.
- `traces/local/inputs/clinvar_20250521.vcf.gz`, ClinVar reference from the task input URL.
- `traces/local/extracted_inputs/data/family_description.txt`, used to confirm affected and unaffected sample IDs.

## Galaxy Steps

1. Create a fresh history for the retry.
2. Upload the compressed family VCF as a tabular dataset.
3. Upload the compressed ClinVar VCF as text.
4. Run Galaxy `Filter1` using the same criteria: NA12879, NA12885, and NA12886 are homozygous alternate, with CFTR, HIGH, and stop_gained in the annotation field.
5. Run Galaxy `Grep1` against the ClinVar reference for the selected causal variant's clinical record.
6. Download both original Galaxy outputs unchanged.
7. Derive the prompt-shaped CSV only from those downloaded Galaxy outputs.

## Risk And Stop Rule

If Galaxy does not decompress or ingest the compressed VCF as tabular/text, record the failure and stop or use a materially different Galaxy-supported extraction path. Do not repeat the same stalled expanded-file upload.
