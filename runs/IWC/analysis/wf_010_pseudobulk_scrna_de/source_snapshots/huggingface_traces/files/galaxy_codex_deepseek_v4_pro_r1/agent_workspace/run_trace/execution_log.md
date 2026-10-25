# scRNA-seq pseudobulk DE execution log

- History: `bbd44e69cb8906b54c42120225aa0c29`
- Source AnnData inspected: 4903 cells x 19090 genes; raw counts layer `counts` used.
- Pseudobulk aggregation: 39 individual-cell_type groups, 34 retained (>=10 cells).
- Expression filter: N=34, median total count=556360, S=27, CPM threshold=17.9739736861, retained genes=1429.
- DE tool: edgeR 3.36.0+galaxy7 (single count matrix, factor file, formula `~disease+cell_type`).
- Contrast: `normal` in the wrapper's post-gsub design, equivalent to normal minus COVID-19.
- Successful edgeR Galaxy job: `bbd44e69cb8906b58eed8b7d483a4ac9`; result dataset `f9cad7b01a4721352eaade68df2ec4a7`.
- Outputs:
  - `/workspace/final_answer/pseudobulk_counts.tsv`
  - `/workspace/final_answer/differential_expression.tsv`
  - `/workspace/final_answer/method.json`
