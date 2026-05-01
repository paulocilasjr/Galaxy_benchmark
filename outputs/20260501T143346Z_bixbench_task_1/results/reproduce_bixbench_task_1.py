#!/usr/bin/env python3
"""Replays the preserved Galaxy identifiers and local artifact paths for BixBench/task_1. Requires GALAXY_API_KEY in the environment for live Galaxy API inspection; does not rerun the analysis by default."""
import json, pathlib
run = pathlib.Path(__file__).resolve().parents[1]
print(json.dumps(json.loads((run / "results" / "run_record.json").read_text()), indent=2))
print("Preserved final answer:", json.loads((run / "results" / "result.json").read_text())["submitted_answer"])
print("Galaxy history id: bbd44e69cb8906b5edaa0d1bed3cda0c")
print("Primary preserved Galaxy outputs:")
for p in ["results/galaxy_deseq2_result_hid26.tsv", "results/galaxy_goseq_ranked_hid30.tsv", "results/galaxy_goseq_cat_genes_hid31.tsv"]:
    print("-", run / p)
