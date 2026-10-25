# AMR determinant detection log

- Galaxy history: bbd44e69cb8906b5001a78319510f528 (run-4bd48da6988c4249ab64719a2de11084)
- Decompressed input fasta.gz to fasta using Galaxy CONVERTER_gz_to_uncompressed.
- Ran starAMR search 0.12.3+galaxy0 with:
  - ResFinder database: d1e607b (via staramr_downloaded_07042025_resfinder_d1e607b_pointfinder_694919f_plasmidfinder_3e77502)
  - PointFinder database: 694919f
  - PointFinder organism: Escherichia coli (escherichia_coli)
  - Percent identity threshold: 90.0
  - ResFinder percent length overlap: 60.0
  - PointFinder percent length overlap: 95.0
- Parsed ResFinder and PointFinder reports; excluded PlasmidFinder and MLST results.
- Wrote final_answer/resistance_determinants.tsv.
