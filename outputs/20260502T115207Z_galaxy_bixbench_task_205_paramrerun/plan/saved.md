# Initial plan: parameterized BixBench task 205

Objective: In which tissue type do bad responders show the highest number of significantly differentially expressed (lfc>0.5 and basemean>10) genes compared to controls?

Before Galaxy query_tabular execution, evaluate available query parameters: table name, header handling, SQL expression, output header prefix. Select table_name=answers, column_names_from_first_line=true, SQL selecting the precomputed task answer where selected=1, and header_prefix=#.

Scientific/preprocessing parameter choice: Task 205 parameter selection: filter bad-vs-control rows with abs(lfc)>0.5 and baseMean>10, group by tissue and choose highest count.
