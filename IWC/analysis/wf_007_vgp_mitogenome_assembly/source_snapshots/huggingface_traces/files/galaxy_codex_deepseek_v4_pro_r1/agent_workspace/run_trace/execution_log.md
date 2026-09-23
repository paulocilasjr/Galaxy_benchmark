# MitoHiFi assembly execution log

Assigned Galaxy history: bbd44e69cb8906b5fe1462249f83d30e

## Steps

1. Located the MitoHiFi tool (3.2.3+galaxy2) in the assigned Galaxy history.
2. Ran the MitoHiFi "find_reference" operation for `Agrius convolvuli`,
   mitochondrion, to obtain a close-related mitogenome reference.
3. Ran MitoHiFi in PacBio HiFi read mode with:
   - Input collection: Collection of Pacbio Data (`ea30dfc48f0c60f7`)
   - Reference FASTA/GenBank outputs from step 2
   - Organism: animal
   - Genetic code: 5 (invertebrate mitochondrial code)
4. Downloaded the final mitogenome FASTA output and verified it contains
   exactly one non-empty sequence record (length 15449 bp).
5. Gzip-compressed the sequence to `final_answer/mitogenome.fasta.gz`.

## Result

- Output: `final_answer/mitogenome.fasta.gz`
- Records: 1
- Sequence length: 15449 bp
