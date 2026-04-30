# Resume Plan: Attempt 2

## What Changed

The Galaxy upload jobs previously marked as blocked were rechecked on 2026-04-29 and found to have completed successfully on 2026-04-28. The retry will resume from the completed expanded family VCF dataset in the original Galaxy history rather than re-uploading or discarding the experiment.

## Resume Inputs

- Completed Galaxy family VCF dataset: `f9cad7b01a47213534c258eaf2258516` in history `bbd44e69cb8906b510e78c9363f4d6e4`.
- Local ClinVar reference remains preserved at `traces/local/inputs/clinvar_20250521.vcf.gz`; it will be uploaded to Galaxy as the clinical reference input for the resumed analysis.
- Ground truth remains `ground_truth/BioAgent/task_3.json`, only for evaluation.

## Galaxy Steps

1. Snapshot the now-completed family VCF dataset and upload job.
2. Upload the ClinVar reference to the same Galaxy history.
3. Run Galaxy `Filter1` on the completed family VCF to select rows where NA12879, NA12885, and NA12886 are homozygous alternate and annotation contains `CFTR`, `HIGH`, and `stop_gained`.
4. Run a Galaxy text/VCF selection step for the ClinVar record matching chromosome 7, position 117227832, variant ID 7115, G>T.
5. Download original Galaxy outputs unchanged.
6. Derive a prompt-shaped CSV only from the preserved Galaxy outputs, then update result/evaluation artifacts.

## Risk

The ClinVar upload may enter the same delayed `__DATA_FETCH__` queue. If it does, keep polling under the run policy and preserve the queue evidence rather than declaring immediate failure.
