| Field | Agent Result | Ground Truth | Match Status | Notes |
|---|---|---|---|---|
| scientific_answer.chromosome | 7 | 7 | match |  |
| scientific_answer.position | 117227832 | 117227832 | match |  |
| scientific_answer.variant_id | 7115 | 7115 | match |  |
| scientific_answer.reference | G | G | match |  |
| scientific_answer.alternate | T | T | match |  |
| scientific_answer.gene_name | CFTR | CFTR | match |  |
| scientific_answer.gene_id | ENSG00000001626 | ENSG00000001626 | match |  |
| scientific_answer.annotation | stop_gained | stop_gained | match |  |
| scientific_answer.impact | HIGH | HIGH | match |  |
| scientific_answer.transcript_id | ENST00000003084 | ENST00000003084 | match |  |
| scientific_answer.hgvs_c | c.1624G>T | c.1624G>T | match |  |
| scientific_answer.hgvs_p | p.Gly542* | p.Gly542* | match |  |
| scientific_answer.clinical_significance | Pathogenic | Pathogenic | match |  |
| scientific_answer.diseases | Cystic_fibrosis|Congenital_bilateral_aplasia_of_vas_deferens_from_CFTR_mutation|Hereditary_pancreatitis|Bronchiectasis_with_or_without_elevated_sweat_chloride_1|CFTR-related_disorder|not_provided | Hereditary_pancreatitis; Congenital_bilateral_aplasia_of_vas_deferens_from_CFTR_mutation; Bronchiectasis_with_or_without_elevated_sweat_chloride_1; Cystic_fibrosis; not_provided; CFTR-related_disorder | mismatch | Delimiter/order mismatch |
| scientific_answer.review_status | practice_guideline | practice_guideline | match |  |
| scientific_answer.rs_id | 113993959 | 113993959 | match |  |

| Score | Value | Status | Basis | Notes |
|---|---|---|---|---|
| scientific_solution_score | 0.9375 | pass | scientific_answer exact field comparison | 15/16 exact fields on first blind pass. |
| standard_analysis_score | 0.9375 | pass | requested CSV schema adherence | Only diseases serialization differed. |
| galaxy_execution_score | not_applicable | not_applicable | hidden bundle lacks Galaxy-execution rubric | Scientific truth only. |
