"""BixBench-compatible fingerprint analysis with explicit CompBio missingness.

Uses the identical BixBench vocabulary, Galaxy normalization and Jaccard rules.
Primary estimates require three observable, nonempty fingerprints. The legacy
BixBench inclusion rule is also reported as a labelled sensitivity analysis.
Unknown outcome scores are never converted into rejection.
"""
from collections import Counter, defaultdict
import importlib.util
import itertools
import json
from pathlib import Path
import statistics

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("bixbench_paths", HERE.parent / "BixBench_50/solution_path_consistency_analysis.py")
bix = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bix)
MODELS = ["codex_gpt_5_5", "codex_gpt_5_6_sol", "codex_gpt_5_6_luna", "codex_deepseek_v4_pro_0813"]
LABEL = dict(zip(MODELS, ["GPT-5.5 (Codex)", "GPT-5.6 Sol (Codex)", "GPT-5.6 Luna (Codex)", "DeepSeek V4 Pro 0813 (Codex)"]))
LABEL["codex_gpt_6_astra"] = "GPT-6 Astra (Codex; unpaired)"
CONDITIONS = ("galaxy", "open_ended_code")


def model(run):
    return run["run_id"].removeprefix(run["condition"] + "_").rsplit("_r", 1)[0]


def mean(xs):
    xs = list(xs)
    return statistics.mean(xs) if xs else None


def load_cells():
    grouped = defaultdict(list)
    for path in sorted((HERE / "analysis").glob("*/history_analysis_evidence.json")):
        data = json.loads(path.read_text())
        for run in data["runs"]:
            fingerprint = set()
            for event in run["events"]:
                if run["condition"] == "galaxy" and event["execution_location"] == "galaxy_job":
                    tool = bix.galaxy_tool(event.get("tool"))
                    if tool:
                        fingerprint.add(tool)
                elif run["condition"] == "open_ended_code" and event.get("command"):
                    fingerprint.update("bio." if t.lower().rstrip(".") == "bio" else t.lower().rstrip(".") for t in bix.VOCAB.findall(event["command"]))
            visible = (run["evidence_completeness"]["public_history_contents"] == "retrieved" if run["condition"] == "galaxy"
                       else run["evidence_completeness"]["agent_transcript"] == "retrieved")
            grouped[data["task"]["task_id"], run["condition"], model(run)].append((run, fingerprint, visible))
    cells = []
    for (task, condition, slug), records in sorted(grouped.items()):
        runs, fps, visible = zip(*records)
        complete = len(runs) == 3 and {r["replicate_id"] for r in runs} == {1, 2, 3}
        eligible = complete and all(visible) and all(fps)
        pairs = [bix.jaccard(a, b) for a, b in itertools.combinations(fps, 2)]
        legacy = bix.agreement(fps) if complete else "insufficient_replicates"
        cells.append({"task": task, "condition": condition, "model": slug, "run_ids": [r["run_id"] for r in runs],
            "n_runs": len(runs), "fingerprints": [sorted(f) for f in fps], "eligible": eligible,
            "exclusion": None if eligible else "insufficient_replicates" if not complete else "missing_or_empty_fingerprint",
            "agreement": legacy if eligible else "not_evaluable", "legacy_agreement": legacy,
            "mean_jaccard": mean(pairs) if eligible else None,
            "legacy_mean_jaccard": mean(j for j in pairs if j is not None) if complete else None,
            "mean_fingerprint_size": mean(map(len, fps)),
            "median_events": statistics.median(len(r["events"]) for r in runs),
            "median_jobs": statistics.median(r["derived_metrics"]["analytical_job_count"] for r in runs) if all(r["derived_metrics"]["analytical_job_count"] is not None for r in runs) else None,
            "any_failed_job": any(r["derived_metrics"]["total_failed_jobs"] > 0 for r in runs) if all(r["derived_metrics"]["total_failed_jobs"] is not None for r in runs) else None,
            "accepted": sum(r["outcome"]["original_evaluator_score"] == 1 for r in runs) if all(r["outcome"]["original_evaluator_score"] is not None for r in runs) else None,
            "distinct_submitted_answers": len({r["outcome"]["submitted_answer"] for r in runs}),
            "evidence_path": f"analysis/{task}/history_analysis_evidence.json"})
    return cells


def analyze():
    cells = load_cells()
    summary, drivers = [], {}
    for cond in CONDITIONS:
        for slug in MODELS + ["ALL"]:
            sub = [c for c in cells if c["condition"] == cond and c["model"] in MODELS and (slug == "ALL" or c["model"] == slug)]
            ev = [c for c in sub if c["eligible"]]
            counts = Counter(c["agreement"] for c in sub)
            legacy = [c for c in sub if c["legacy_mean_jaccard"] is not None]
            summary.append({"condition": cond, "model": slug, "cells": len(sub), **dict(counts),
                            "evaluable_cells": len(ev), "pct_identical": 100 * counts["identical"] / len(ev) if ev else None,
                            "mean_jaccard": mean(c["mean_jaccard"] for c in ev),
                            "legacy_evaluable_cells": len(legacy),
                            "legacy_mean_jaccard": mean(c["legacy_mean_jaccard"] for c in legacy),
                            "legacy_identical": sum(c["legacy_agreement"] == "identical" for c in legacy)})
        ev = [c for c in cells if c["condition"] == cond and c["eligible"]]
        task_means = {t: mean(c["mean_jaccard"] for c in ev if c["task"] == t) for t in sorted({c["task"] for c in ev})}
        configuration_means = {m: mean(c["mean_jaccard"] for c in ev if c["model"] == m) for m in MODELS}
        correlations = {}
        for variable in ("median_events", "median_jobs", "mean_fingerprint_size"):
            usable = [c for c in ev if c[variable] is not None]
            correlations[variable] = {"n": len(usable), "spearman_rho": bix.spearman([c[variable] for c in usable], [c["mean_jaccard"] for c in usable])}
        failure_groups = {str(flag): {"n": sum(c["any_failed_job"] is flag for c in ev),
                         "mean_jaccard": mean(c["mean_jaccard"] for c in ev if c["any_failed_job"] is flag)} for flag in (True, False, None)}
        sizes = sorted(c["mean_fingerprint_size"] for c in ev)
        cutoffs = [sizes[len(sizes)//3], sizes[2*len(sizes)//3]] if sizes else []
        strata = []
        for lo, hi in ((None, cutoffs[0]), (cutoffs[0], cutoffs[1]), (cutoffs[1], None)) if cutoffs else []:
            sub = [c for c in ev if (lo is None or c["mean_fingerprint_size"] > lo) and (hi is None or c["mean_fingerprint_size"] <= hi)]
            strata.append({"lower_exclusive": lo, "upper_inclusive": hi, "groups": {str(flag): {"n": sum(c["any_failed_job"] is flag for c in sub), "mean_jaccard": mean(c["mean_jaccard"] for c in sub if c["any_failed_job"] is flag)} for flag in (True, False)}})
        drivers[cond] = {"task_means": task_means, "configuration_means": configuration_means,
                          "task_mean_sd": statistics.pstdev(task_means.values()) if task_means else None,
                          "configuration_mean_sd": statistics.pstdev(v for v in configuration_means.values() if v is not None),
                          "correlations": correlations, "failure_groups": failure_groups, "fingerprint_size_strata": strata,
                          "acceptance_association": "not_assessable_without_item_scores"}
    common = sorted(set(drivers["galaxy"]["task_means"]) & set(drivers["open_ended_code"]["task_means"]))
    out = {"method": "Same BixBench closed vocabulary and version-stripping. Primary analysis requires all three nonempty observed fingerprints. Different instruments across conditions; tools are not adjudicated scientific methods.",
           "by_condition_and_model": summary, "drivers": drivers, "cells": cells,
           "cross_condition_task_correlation": {"n": len(common), "spearman_rho": bix.spearman([drivers["galaxy"]["task_means"][t] for t in common], [drivers["open_ended_code"]["task_means"][t] for t in common])},
           "provenance": {"evidence_files": len({c["task"] for c in cells}), "runs_loaded": sum(c["n_runs"] for c in cells), "triplicate_cells": sum(c["n_runs"] == 3 for c in cells), "single_run_cells": sum(c["n_runs"] == 1 for c in cells)}}
    (HERE / "solution_path_consistency_results.json").write_text(json.dumps(out, indent=2) + "\n")
    return out


if __name__ == "__main__":
    print(json.dumps(analyze()["provenance"]))
