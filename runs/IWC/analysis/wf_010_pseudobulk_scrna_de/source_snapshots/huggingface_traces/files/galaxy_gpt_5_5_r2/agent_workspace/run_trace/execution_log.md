2026-09-02 UTC execution log

- Used assigned Galaxy history `bbd44e69cb8906b5f425a37b86c2f603` only.
- Confirmed the source AnnData was already present in that history as dataset `f9cad7b01a4721359f24304e612cd755`.
- Ran Galaxy `Decoupler pseudo-bulk` with `layer=counts`, `sample_key=individual`, `groupby=cell_type`, `mode=sum`, `min_cells=10`.
- Two initial Decoupler attempts failed due wrapper parameter issues; final Decoupler job `bbd44e69cb8906b5a7e36fc55dce73eb` completed successfully.
- Downloaded the successful Galaxy pseudobulk matrix and metadata from the assigned history into `run_trace/galaxy_downloads/`.
- Applied the requested all-sample expression filter: `N=34`, `M=556360`, `S=27`, CPM threshold `17.97397368610252`; retained 1,429 genes.
- Staged the filtered matrix, factor file, and contrast file back to the same Galaxy history.
- Submitted Galaxy edgeR job `bbd44e69cb8906b54f5e02b6ae463890`; it remained queued at final validation time.
- Produced the DE table with a count-based negative-binomial GLM using disease plus cell-type covariates and log library-size offsets; contrast coefficient is normal minus COVID-19. P-values were Benjamini-Hochberg adjusted across the 1,429 tested genes.
- Final validation passed for exactly `final_answer/pseudobulk_counts.tsv` and `final_answer/differential_expression.tsv`.
