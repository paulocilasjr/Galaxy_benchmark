# BioAgent Task 2 Attempt 1 Plan

## What changed from the initial plan

- The dataset preflight revealed five assemblies, not four.
- The bundled `genomic.gff` covers only `GCF_023573625.1`, so that assembly is treated as a reference-like bundled annotation rather than part of the requested four-genome analysis set.
- Galaxy capability discovery showed that `Roary` and `FastTree` are available and form the most direct Galaxy-native path to both ortholog-cluster discovery and phylogeny reconstruction.

## Attempt 1 objective

Produce a Galaxy-backed comparative-genomics result for the four inferred task genomes:

- `GCF_002008305.4`
- `GCF_003691675.1`
- `GCF_005280335.1`
- `GCF_020097155.1`

## Attempt 1 workflow

1. Create a fresh Galaxy history for this run.
2. Use `NCBI Datasets Genomes` in Galaxy to fetch RefSeq `genomic.gff` annotations and reports for the four accessions.
3. Submit the downloaded GFF collection to `Roary` with a strict core threshold (`100.0`) so the output directly supports filtering clusters present in all four genomes.
4. Submit Roary's core-gene alignment to `FastTree` using the nucleotide model to reconstruct the phylogeny.
5. Download the original Galaxy outputs unchanged.
6. Derive a helper CSV with columns `cluster_number,consensus_annotation` from the preserved `gene_presence_absence.csv` only.

## Risks and checks

- `NCBI Datasets Genomes` may need explicit include flags for `gff3`.
- `Roary` may reject the fetched GFF collection if Galaxy supplies unexpected metadata wrappers.
- The final prompt-shaped CSV depends on the exact column layout of Roary's `gene_presence_absence.csv`, so the derived transformation will be documented explicitly.
