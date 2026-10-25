#!/usr/bin/env python3
"""Summarize replicate-level solution-path fingerprints for IWC evidence.

This is an auditor-derived descriptive index. It reads archived evidence only,
executes no recovered code, and makes no claim that fingerprints are
scientifically equivalent across execution conditions.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import itertools
import json
from pathlib import Path
import re
import statistics

HERE = Path(__file__).resolve().parent
CONDITIONS = ("galaxy", "open_ended_code")
VOCAB = re.compile(
    r"\b(fastqc|fastp|multiqc|cutadapt|trimmomatic|bowtie2|bwa|samtools|bcftools|bedtools|"
    r"dada2|qiime2|star|hisat2|featurecounts|salmon|kallisto|blast|diamond|hmmer|mafft|"
    r"minimap2|gatk|picard|pandas|numpy|scipy|sklearn|statsmodels|matplotlib|seaborn|"
    r"scanpy|anndata|biopython|bioconda|rscript|python3?|awk|sed|grep|sort|uniq|jq|"
    r"curl|wget|samtools|gffread|vcftools|plink|deseq2|edger|limma|snakemake|nextflow)\b", re.I)


def load_runs():
    records = []
    for path in sorted((HERE / "analysis").glob("*/history_analysis_evidence.json")):
        evidence = json.loads(path.read_text())
        for run in evidence["runs"]:
            fingerprint = set()
            for event in run["events"]:
                if run["condition"] == "galaxy" and event.get("execution_location") == "galaxy_job":
                    tool = event.get("tool")
                    if tool and tool != "__DATA_FETCH__":
                        fingerprint.add(re.sub(r"\d+$", "", tool).strip())
                if run["condition"] == "open_ended_code":
                    fingerprint.update(token.lower() for token in VOCAB.findall(event.get("command") or ""))
            records.append({
                "task": run["task_id"],
                "run_id": run["run_id"],
                "model": run["model"]["supplied_label"],
                "condition": run["condition"],
                "replicate": run["replicate_id"],
                "fingerprint": sorted(fingerprint),
                "fingerprint_size": len(fingerprint),
                "events": len(run["events"]),
                "analytical_jobs": run["derived_metrics"].get("analytical_job_count"),
                "failed_jobs": run["derived_metrics"].get("total_failed_jobs"),
                "evidence_path": str(path.relative_to(HERE)),
            })
    return records


def jaccard(left, right):
    left, right = set(left), set(right)
    return len(left & right) / len(left | right) if left | right else None


def agreement(fingerprints):
    values = [tuple(value) for value in fingerprints]
    if all(not value for value in values):
        return "no_signal"
    return {1: "identical", 2: "two_of_three", 3: "all_distinct"}[len(set(values))]


def analyze():
    records = load_runs()
    grouped = defaultdict(list)
    for record in records:
        grouped[(record["task"], record["condition"], record["model"])].append(record)
    cells = []
    for (task, condition, model), members in sorted(grouped.items()):
        members.sort(key=lambda record: record["replicate"])
        pairs = [jaccard(a["fingerprint"], b["fingerprint"]) for a, b in itertools.combinations(members, 2)]
        pairs = [value for value in pairs if value is not None]
        complete = len(members) == 3 and {member["replicate"] for member in members} == {1, 2, 3}
        cells.append({
            "task": task,
            "condition": condition,
            "model": model,
            "run_ids": [member["run_id"] for member in members],
            "complete_triplicate": complete,
            "fingerprints": [member["fingerprint"] for member in members],
            "agreement": agreement([member["fingerprint"] for member in members]) if complete else "incomplete",
            "mean_jaccard": statistics.mean(pairs) if pairs else None,
            "mean_fingerprint_size": statistics.mean(member["fingerprint_size"] for member in members),
            "median_events": statistics.median(member["events"] for member in members),
            "median_analytical_jobs": statistics.median(member["analytical_jobs"] for member in members if member["analytical_jobs"] is not None) if any(member["analytical_jobs"] is not None for member in members) else None,
            "any_failed_job": any((member["failed_jobs"] or 0) > 0 for member in members),
            "evidence_path": members[0]["evidence_path"],
        })

    summaries = []
    for condition in CONDITIONS:
        for model in sorted({cell["model"] for cell in cells}):
            subset = [cell for cell in cells if cell["condition"] == condition and cell["model"] == model]
            evaluable = [cell for cell in subset if cell["complete_triplicate"] and cell["mean_jaccard"] is not None]
            summaries.append({
                "condition": condition,
                "model": model,
                "cells": len(subset),
                "evaluable_cells": len(evaluable),
                "agreement_counts": dict(Counter(cell["agreement"] for cell in subset)),
                "mean_jaccard": statistics.mean(cell["mean_jaccard"] for cell in evaluable) if evaluable else None,
                "identical_pct": 100 * sum(cell["agreement"] == "identical" for cell in evaluable) / len(evaluable) if evaluable else None,
            })
    output = {
        "method": "Condition-specific replicate fingerprints from structured Galaxy tool IDs or a fixed open-code vocabulary. Fingerprints document observed routes and are not scientific equivalence measures.",
        "provenance": {"runs_loaded": len(records), "cells": len(cells), "tasks": len({record["task"] for record in records})},
        "by_condition_and_model": summaries,
        "cells": cells,
    }
    (HERE / "solution_path_consistency_results.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    return output


if __name__ == "__main__":
    result = analyze()
    print(json.dumps(result["provenance"]))
