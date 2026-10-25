# AMR determinant detection execution log

- Input: GCA_053668395.1_ASM5366839v1_genomic.fna.gz
- Galaxy history: bbd44e69cb8906b52e7c556e7bef196f
- Galaxy tool: staramr_search 0.12.3+galaxy0
- Database: staramr_downloaded_07042025_resfinder_d1e607b_pointfinder_694919f_plasmidfinder_3e77502
  - ResFinder release: d1e607b
  - PointFinder release: 694919f
- PointFinder organism: escherichia_coli
- Thresholds used:
  - Percent identity >= 90
  - ResFinder coverage >= 60
  - PointFinder coverage >= 95
- Final analysis job: bbd44e69cb8906b5405ccc406df7e57c
  - Excluded negative results, did not use the default AMR gene exclusion list.

## Detected determinants

Acquired resistance genes:

- aac(6')-Ib-cr
- aadA5
- blaCTX-M-15
- blaOXA-1
- catB3
- dfrA17
- mph(A)
- sul1
- tet(B)

Chromosomal point mutations:

- gyrA (D87N)
- gyrA (S83L)
- parC (S80I)
- parE (S458T)

Plasmid replicons and MLST results were ignored for the final deliverable.
