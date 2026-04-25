# BioAgent Task 2 Attempt 2 Plan

## Why attempt 1 failed

- `Roary` rejected the RefSeq `genomic.gff` inputs because they lacked the trailing FASTA sequence that Roary requires.
- Galaxy stderr recommended reannotating the FASTA files with `Prokka`.

## Attempt 2 objective

Retry the same four-genome comparative-genomics analysis with a corrected annotation path:

- `GCF_002008305.4`
- `GCF_003691675.1`
- `GCF_005280335.1`
- `GCF_020097155.1`

## Attempt 2 workflow

1. Extract the four selected genome FASTAs from the already-downloaded task dataset archive under `traces/local/`.
2. Upload the four FASTAs into a fresh Galaxy history.
3. Run `Prokka` on each uploaded genome to generate Roary-compatible GFF outputs with embedded sequence context.
4. Build a Galaxy list collection from the four Prokka GFFs.
5. Run `Roary` on that GFF collection with `core_diff=100.0`.
6. Run `FastTree` on Roary's core gene alignment.
7. Preserve the original Galaxy outputs unchanged and derive the prompt-shaped helper CSV from Roary's CSV output only.

## Why this is a material fix

- The failing mechanism changes from incompatible RefSeq GFF inputs to Galaxy-generated Prokka GFF outputs explicitly designed to satisfy Roary's parser.
- The retry uses the same task genomes and same core pangenome / phylogeny analysis goal, but changes the annotation mechanism at the point the failure occurred.
