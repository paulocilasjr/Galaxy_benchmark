# Comparison Report

| Field | Agent Result | Ground Truth | Match Status | Notes |
|---|---|---|---|---|
| analysis_type | RNA-Seq | RNA-seq | mismatch | Semantic match; capitalization differs. |
| artifact | bigwig | MultiQC HTML Report (dataset:html, state=ok) | mismatch | Agent selected a representative coverage artifact from workflow metadata; ground truth expected the MultiQC HTML output artifact. |
| workflow steps | 16 | 16 | match | Agent counted tool/subworkflow nodes only, excluding input and parameter nodes. |
