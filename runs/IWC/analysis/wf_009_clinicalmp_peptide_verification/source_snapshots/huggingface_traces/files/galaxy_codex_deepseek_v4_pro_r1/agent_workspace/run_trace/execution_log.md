# Execution log

1. Inspected assigned Galaxy history `bbd44e69cb8906b50d6580d0cd360a9b`.
2. Merged Human UniProt+Isoforms FASTA and cRAP FASTA with FASTA Merge Files and Filter Unique Sequences.
3. Ran PepQuery2 novel peptide/protein validation separately on all four assigned MGF datasets:
   - fixed Carbamidomethylation (C), TMT 11-plex (K and peptide N-term)
   - variable Oxidation (M)
   - trypsin, 2 missed cleavages, 10 ppm precursor, 0.6 Da fragment, charges 2-6, CID/HCD
4. Extracted PSM rank outputs and selected rows where `confident == Yes`.
5. Joined the verified peptide sequences to the supplied SGPS and MaxQuant peptide reports and wrote peptide/protein pairs.
6. Wrote `final_answer/verified_peptides.tsv`.
