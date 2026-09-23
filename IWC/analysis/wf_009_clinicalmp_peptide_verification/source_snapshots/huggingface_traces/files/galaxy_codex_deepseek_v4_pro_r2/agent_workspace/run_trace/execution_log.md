# Execution log

## Scope
- Used only the assigned Galaxy history `bbd44e69cb8906b580220d0ad0456f9b`.
- Inputs were already present in that history.

## Galaxy steps
1. Merged Human UniProt+Isoforms FASTA and cRAP FASTA with
   `FASTA Merge Files and Filter Unique Sequences`.
   Output: `f9cad7b01a4721354ca92a3f24cdc19c`.
2. Extracted peptide and protein columns from SGPS and MaxQuant reports:
   - SGPS Cut: `f9cad7b01a472135ae3b4ad5d7e11b35`
   - MaxQuant Cut: `f9cad7b01a472135ca9f4a27f0af04f4`
   - Removed headers and concatenated them into
     `f9cad7b01a4721359deca5c396fcd378`.
3. Ran PepQuery2 in novel peptide validation mode over the MGF collection
   using the supplied tolerances, digestion rules, charge range, and
   modifications. The resulting `psm_rank.txt` collection was
   `4ba2af70ab3dfc43`.
4. Collapsed the PSM rank collection into
   `f9cad7b01a472135047827ac5061baba`.
5. Filtered rows where `c20=='Yes'`, removed the header, and cut peptide
   column. Verified peptide list:
   `f9cad7b01a472135e64bbc8c685ba0fc`.
6. Joined verified peptides to the concatenated peptide-protein report with
   Query Tabular. Joined output:
   `f9cad7b01a472135db2fe5246aab1e25`.

## Final deliverable
- `final_answer/verified_peptides.tsv` was written from the joined Galaxy
  output after replacing the Query Tabular header prefix `#` with the exact
  required header.
