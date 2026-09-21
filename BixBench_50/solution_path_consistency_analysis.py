#!/usr/bin/env python3
"""Replicate-level solution-path consistency for BixBench-50.

Auditor-derived analysis. Reads only the archived per-task evidence packages
(analysis/<task>/history_analysis_evidence.json); executes no agent code, issues
no Galaxy API calls and opens no hidden reference answers.

Unit of analysis: a replicate cell = one (task, condition, model-harness
configuration) with its three replicate-labelled runs. 50 tasks x 2 conditions
x 5 configurations = 500 cells covering all 1,500 archived runs.

Solution-path fingerprint per run (auditor-defined, extraction rules below):
  Galaxy           set of Galaxy tool identifiers recorded on `galaxy_job`
                   events, version-stripped, excluding `__DATA_FETCH__`
                   (upload/fetch is kept separate from analytical processing).
  Open-ended code  set of analytical tool/library tokens matched by a fixed
                   vocabulary against the recorded shell/command text.

The two extraction instruments are NOT equivalent: Galaxy fingerprints come
from structured tool identifiers, open-ended-code fingerprints from free-text
command parsing against a closed vocabulary. Comparisons ACROSS conditions are
therefore instrument-confounded and are reported only to document that the two
agreement measures disagree in direction. Comparisons BETWEEN configurations
WITHIN a condition use the same instrument and are the interpretable contrast.

Outputs solution_path_consistency_results.json next to this script.
"""

import collections
import glob
import itertools
import json
import os
import re
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
EVIDENCE = sorted(glob.glob(os.path.join(HERE, "analysis", "*", "history_analysis_evidence.json")))

MODELS = [
    "codex_gpt_5_5",
    "codex_gpt_5_6_sol",
    "codex_gpt_5_6_luna",
    "deepseek_v4_pro_via_codex",
    "deepseek_v4_pro_via_claude_code_superseded",
]
LABEL = {
    "codex_gpt_5_5": "GPT-5.5",
    "codex_gpt_5_6_sol": "GPT-5.6 Sol",
    "codex_gpt_5_6_luna": "GPT-5.6 Luna",
    "deepseek_v4_pro_via_codex": "DeepSeek V4 Pro (Codex)",
    "deepseek_v4_pro_via_claude_code_superseded": "DeepSeek V4 Pro (Claude Code, superseded)",
}

# Closed vocabulary for open-ended-code command parsing.
VOCAB = re.compile(
    r"\b(phykit|iqtree|raxml|biopython|Bio\.|pandas|numpy|scipy|statsmodels|sklearn|seaborn|matplotlib|"
    r"deseq2|edgeR|limma|samtools|bcftools|bedtools|bwa|minimap2|vcftools|plink|gatk|picard|salmon|kallisto|"
    r"STAR|hisat2|featureCounts|htseq|fastqc|trimmomatic|cutadapt|multiqc|blast|diamond|hmmer|mafft|muscle|"
    r"trimal|clustal|datamash|awk|sed|grep|cut|sort|uniq|jq|csvtk|Rscript|python3?|mannwhitneyu|kruskal|ttest|"
    r"wilcox|glm|aic|kegg|gseapy|goatools|anndata|scanpy)\b",
    re.I,
)


def galaxy_tool(tool):
    """Version-stripped Galaxy tool name; None for data fetch/upload jobs."""
    if not tool or tool == "__DATA_FETCH__":
        return None
    if "toolshed" in tool:
        parts = tool.split("/")
        return parts[-2] if len(parts) >= 2 else tool
    return re.sub(r"\d+$", "", tool).strip()


def load_runs():
    runs = {}
    for path in EVIDENCE:
        with open(path) as fh:
            evidence = json.load(fh)
        task = (evidence.get("task") or {}).get("task_id") or os.path.basename(os.path.dirname(path))
        for run in evidence.get("runs", []):
            rid = run["run_id"]
            cond = "open_ended_code" if run["condition"] in ("open", "open_ended_code") else "galaxy"
            model = re.sub(r"_r\d+$", "", re.sub(r"^galaxy_|^open_ended_code_|^open_", "", rid))
            fingerprint, n_events, n_jobs, n_failed = set(), 0, 0, 0
            for event in run.get("events") or []:
                n_events += 1
                if event.get("execution_location") == "galaxy_job":
                    tool = galaxy_tool(event.get("tool"))
                    if tool:
                        n_jobs += 1
                        fingerprint.add(tool)
                    if (event.get("status") or "") in ("error", "failed"):
                        n_failed += 1
                command = event.get("command") or ""
                if command and cond == "open_ended_code":
                    for token in {t.lower().rstrip(".") for t in VOCAB.findall(command)}:
                        fingerprint.add("bio." if token == "bio" else token)
            usage = run.get("usage") or {}
            runs[rid, task] = dict(
                task=task,
                condition=cond,
                model=model,
                fingerprint=fingerprint,
                n_events=n_events,
                n_jobs=n_jobs,
                n_failed=n_failed,
                input_tokens=usage.get("input_tokens") if isinstance(usage, dict) else None,
                score=(run.get("outcome") or {}).get("original_evaluator_score"),
            )
    return runs


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else None


def agreement(fingerprints):
    sets = [frozenset(f) for f in fingerprints]
    if all(not s for s in sets):
        return "no_signal"
    return {1: "identical", 2: "two_of_three", 3: "all_distinct"}[len(set(sets))]


def rank(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return ranks


def spearman(xs, ys):
    if len(xs) < 4:
        return None
    rx, ry = rank(xs), rank(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else None


def build_cells(runs):
    grouped = collections.defaultdict(list)
    for value in runs.values():
        grouped[value["task"], value["condition"], value["model"]].append(value)
    cells = []
    for (task, cond, model), members in sorted(grouped.items()):
        if len(members) != 3:
            continue
        fps = [m["fingerprint"] for m in members]
        pairwise = [j for j in (jaccard(a, b) for a, b in itertools.combinations(fps, 2)) if j is not None]
        cells.append(
            dict(
                task=task,
                condition=cond,
                model=model,
                agreement=agreement(fps),
                mean_jaccard=statistics.mean(pairwise) if pairwise else None,
                mean_fingerprint_size=statistics.mean(len(f) for f in fps),
                accepted=sum(1 for m in members if m["score"] == 1.0),
                median_events=statistics.median(m["n_events"] for m in members),
                median_jobs=statistics.median(m["n_jobs"] for m in members),
                any_failed_job=any(m["n_failed"] > 0 for m in members),
            )
        )
    return cells


def summarize(cells):
    evaluable = [c for c in cells if c["agreement"] != "no_signal" and c["mean_jaccard"] is not None]
    out = {"by_condition_and_model": [], "drivers": {}}

    for cond in ("galaxy", "open_ended_code"):
        for model in MODELS + ["ALL"]:
            sub = [c for c in cells if c["condition"] == cond and (model == "ALL" or c["model"] == model)]
            ev = [c for c in sub if c["agreement"] != "no_signal"]
            counts = collections.Counter(c["agreement"] for c in sub)
            js = [c["mean_jaccard"] for c in ev if c["mean_jaccard"] is not None]
            out["by_condition_and_model"].append(
                dict(
                    condition=cond,
                    model=model,
                    label="All configurations" if model == "ALL" else LABEL[model],
                    identical=counts["identical"],
                    two_of_three=counts["two_of_three"],
                    all_distinct=counts["all_distinct"],
                    no_signal=counts["no_signal"],
                    evaluable_cells=len(ev),
                    pct_identical=round(100 * counts["identical"] / len(ev), 1) if ev else None,
                    mean_jaccard=round(statistics.mean(js), 3) if js else None,
                    median_events_per_run=statistics.median(c["median_events"] for c in ev) if ev else None,
                )
            )

    spread = {}
    for cond in ("galaxy", "open_ended_code"):
        sub = [c for c in evaluable if c["condition"] == cond]
        by_task, by_model = collections.defaultdict(list), collections.defaultdict(list)
        for c in sub:
            by_task[c["task"]].append(c["mean_jaccard"])
            by_model[c["model"]].append(c["mean_jaccard"])
        tm = [statistics.mean(v) for v in by_task.values()]
        mm = [statistics.mean(v) for v in by_model.values()]
        spread[cond] = dict(
            task_means_n=len(tm),
            task_means_sd=round(statistics.pstdev(tm), 3),
            task_means_range=[round(min(tm), 2), round(max(tm), 2)],
            model_means_n=len(mm),
            model_means_sd=round(statistics.pstdev(mm), 3),
            model_means_range=[round(min(mm), 2), round(max(mm), 2)],
        )
    out["drivers"]["spread_of_mean_jaccard"] = spread

    gt, ot = collections.defaultdict(list), collections.defaultdict(list)
    for c in evaluable:
        (gt if c["condition"] == "galaxy" else ot)[c["task"]].append(c["mean_jaccard"])
    common = sorted(set(gt) & set(ot))
    rho = spearman([statistics.mean(gt[t]) for t in common], [statistics.mean(ot[t]) for t in common])
    out["drivers"]["cross_condition_task_agreement"] = dict(
        spearman_rho=round(rho, 3) if rho is not None else None, n_tasks=len(common)
    )

    acceptance = {}
    for cond in ("galaxy", "open_ended_code"):
        strata = {}
        for label, pred in (("all_three", lambda a: a == 3), ("one_or_two", lambda a: 1 <= a <= 2), ("none", lambda a: a == 0)):
            sub = [c for c in evaluable if c["condition"] == cond and pred(c["accepted"])]
            if sub:
                strata[label] = dict(
                    cells=len(sub),
                    distinct_tasks=len({c["task"] for c in sub}),
                    mean_jaccard=round(statistics.mean(c["mean_jaccard"] for c in sub), 3),
                    pct_identical=round(100 * sum(1 for c in sub if c["agreement"] == "identical") / len(sub), 1),
                )
        acceptance[cond] = strata
    out["drivers"]["by_acceptance"] = acceptance

    workload = {}
    for cond in ("galaxy", "open_ended_code"):
        sub = [c for c in evaluable if c["condition"] == cond]
        entry = {}
        for var in ("median_events", "median_jobs", "mean_fingerprint_size"):
            pairs = [(c[var], c["mean_jaccard"]) for c in sub if c[var] is not None]
            rho = spearman([p[0] for p in pairs], [p[1] for p in pairs]) if len(pairs) >= 10 else None
            entry[var] = dict(spearman_rho=round(rho, 3) if rho is not None else None, n_cells=len(pairs))
        workload[cond] = entry
    out["drivers"]["workload_correlations"] = workload

    g = [c for c in evaluable if c["condition"] == "galaxy"]
    failed = [c for c in g if c["any_failed_job"]]
    clean = [c for c in g if not c["any_failed_job"]]
    sizes = sorted(c["mean_fingerprint_size"] for c in g)
    t1, t2 = sizes[len(sizes) // 3], sizes[2 * len(sizes) // 3]
    strata = []
    for lo, hi, lab in ((None, t1, "small"), (t1, t2, "mid"), (t2, None, "large")):
        sub = [c for c in g if (lo is None or c["mean_fingerprint_size"] > lo) and (hi is None or c["mean_fingerprint_size"] <= hi)]
        f = [c for c in sub if c["any_failed_job"]]
        n = [c for c in sub if not c["any_failed_job"]]
        strata.append(
            dict(
                size_tertile=lab,
                failed_cells=len(f),
                failed_mean_jaccard=round(statistics.mean(c["mean_jaccard"] for c in f), 3) if f else None,
                clean_cells=len(n),
                clean_mean_jaccard=round(statistics.mean(c["mean_jaccard"] for c in n), 3) if n else None,
            )
        )
    out["drivers"]["galaxy_failures"] = dict(
        with_failed_job=dict(cells=len(failed), mean_jaccard=round(statistics.mean(c["mean_jaccard"] for c in failed), 3)),
        without_failed_job=dict(cells=len(clean), mean_jaccard=round(statistics.mean(c["mean_jaccard"] for c in clean), 3)),
        stratified_by_fingerprint_size=strata,
    )

    # Acceptance gradient stratified by fingerprint size, to check that it is not a toolset-size artefact.
    acc_strata = []
    for lo, hi, lab in ((None, t1, "small"), (t1, t2, "mid"), (t2, None, "large")):
        sub = [c for c in g if (lo is None or c["mean_fingerprint_size"] > lo) and (hi is None or c["mean_fingerprint_size"] <= hi)]
        a3 = [c for c in sub if c["accepted"] == 3]
        a0 = [c for c in sub if c["accepted"] == 0]
        acc_strata.append(
            dict(
                size_tertile=lab,
                all_three_accepted_cells=len(a3),
                all_three_accepted_mean_jaccard=round(statistics.mean(c["mean_jaccard"] for c in a3), 3) if a3 else None,
                none_accepted_cells=len(a0),
                none_accepted_mean_jaccard=round(statistics.mean(c["mean_jaccard"] for c in a0), 3) if a0 else None,
            )
        )
    out["drivers"]["galaxy_acceptance_stratified_by_fingerprint_size"] = acc_strata
    out["drivers"]["fingerprint_size_tertile_cutoffs"] = [round(t1, 2), round(t2, 2)]
    return out


def main():
    runs = load_runs()
    cells = build_cells(runs)
    summary = summarize(cells)
    summary["provenance"] = dict(
        evidence_files=len(EVIDENCE),
        runs_loaded=len(runs),
        cells=len(cells),
        note="Auditor-derived measure. No agent code executed, no Galaxy API calls, no hidden references opened.",
    )
    summary["cells"] = cells
    dest = os.path.join(HERE, "solution_path_consistency_results.json")
    with open(dest, "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=False)
    print(f"evidence files: {len(EVIDENCE)}   runs: {len(runs)}   cells: {len(cells)}")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
