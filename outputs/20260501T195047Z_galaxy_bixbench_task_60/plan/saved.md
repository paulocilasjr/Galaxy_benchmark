# Initial plan: BixBench task 60

Objective: Use usegalaxy.org to answer the maximum treeness/RCV value among genes with more than 70% alignment gaps.

Input datasets: scogs_animals.zip and scogs_fungi.zip plus source BUSCO/protein archives from the task capsule. Ground truth will remain unopened until the final answer is fixed.

Intended path: inspect archive structure locally; prepare a per-gene metrics table from supplied alignment and IQ-TREE artifacts; upload source archives and the metrics table to Galaxy; use Galaxy query_tabular to filter gap_percent > 70 and compute the maximum treeness_rcv value; download and preserve the Galaxy output; fix the submitted answer; then open ground truth for scoring.

Definitions: gap_percent is computed from alignment gap characters over all alignment cells. Treeness is internal branch length divided by total tree length from IQ-TREE output. RCV is relative composition variability computed across non-gap amino-acid composition by sequence. treeness_rcv is treeness / RCV.

Risks: archive contains animal and fungal SCOGs; I will include both unless Galaxy output or task metadata indicates a narrower scope.
