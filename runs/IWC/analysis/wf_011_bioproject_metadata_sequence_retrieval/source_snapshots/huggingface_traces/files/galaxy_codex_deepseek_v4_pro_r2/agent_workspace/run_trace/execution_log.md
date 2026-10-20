# Execution log

Assigned Galaxy history: `bbd44e69cb8906b50e497d0913ab228f`

## Metadata retrieval
- Used Galaxy `pysradb search` (v2.5.1) against SRA for:
  - `PRJNA1354216`: 8 public runs, all `SINGLE`
  - `PRJNA1339024`: 12 public runs, all `PAIRED`
- Retrieved all required run metadata fields from the Galaxy outputs.

## Read retrieval
- Uploaded the 20 run accessions as `all_run_accessions.txt` to the assigned history.
- Ran Galaxy `Faster Download and Extract Reads in FASTQ` (`fasterq-dump`
  v3.1.1+galaxy1) with:
  - input: the uploaded accession list
  - split mode: `--split-3`
  - `skip_technical`: true
- Downloaded the resulting Galaxy FASTQ datasets without decompression or
  reformatting to `final_answer/reads/`.

## Validation
- All 28 FASTQ gzip files passed `gzip -t`.
- Paired forward/reverse files have equal read counts and match the run spot
  counts from SRA metadata.
- Single-end read counts match SRA metadata spot counts.
- `run_manifest.tsv` has exactly 20 rows and matches the 20 rows in the two
  metadata tables.
