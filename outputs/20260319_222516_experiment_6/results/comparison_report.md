# Comparison Report

| Field | Agent Result | Ground Truth | Match Status | Notes |
|---|---|---|---|---|
| data_normalization | Scanpy normalize using pp.normalize_total with target_sum=10000.0 | None | mismatch | Values differ after normalization. |
| total_tool_steps | 51 | 45 | mismatch | Values differ after normalization. |
| list_of_genes | ["IL7R", "CCR7", "CD8A", "CD14", "LYZ", "MS4A1", "CD79A", "GNLY", "NKG7", "KLRB1", "FCER1A", "CST3", "PPBP", "FCGR3A"] | ["LDHB", "DUSP4", "CCL5", "LST1", "NKG7", "HLA-DPA1", "FCGR3A"] | mismatch | Gene list differs. |
