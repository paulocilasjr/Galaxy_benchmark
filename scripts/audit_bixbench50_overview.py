"""Recompute the overview from archived evidence without rerunning agent analyses."""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import random
import statistics


CONDITIONS = ("galaxy", "open_ended_code")


def quantile(values, probability):
    values = sorted(values)
    position = (len(values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def describe(values):
    return {
        "n": len(values),
        "median": statistics.median(values),
        "mean": statistics.mean(values),
        "q1": quantile(values, 0.25),
        "q3": quantile(values, 0.75),
        "min": min(values),
        "max": max(values),
    }


def model_slug(run):
    return run["run_id"].removeprefix(run["condition"] + "_").rsplit("_r", 1)[0]


def accepted(runs):
    return {
        c: {
            "accepted": int(sum(r["outcome"]["original_evaluator_score"] for r in runs if r["condition"] == c)),
            "n": sum(r["condition"] == c for r in runs),
        }
        for c in CONDITIONS
    }


def audit(root, resamples):
    reports = sorted((root / "BixBench_50/analysis").glob("*/history_analysis.md"))
    assert len(reports) == 50, f"Expected 50 task reports, found {len(reports)}"
    records, tasks, hashes = [], [], []
    all_jobs, all_histories = {}, set()
    job_conflicts = []
    groups = defaultdict(list)
    verifier_groups = defaultdict(list)
    raw_modes = Counter()
    recovery_runs = recovery_episodes = 0
    for report in reports:
        evidence_path = report.with_name("history_analysis_evidence.json")
        evidence = json.loads(evidence_path.read_text())
        runs = evidence["runs"]
        assert len(runs) == 30
        task_id = evidence["task"]["task_id"]
        definition = json.loads((report.parent / (task_id + ".json")).read_text())
        metadata_path = root / definition["allowed_task_metadata"]
        metadata = json.loads(metadata_path.read_text())
        assert metadata["question_id"] == task_id
        markdown = report.read_text()
        rows = {}
        for line in markdown.splitlines():
            if line.startswith("| `galaxy_") or line.startswith("| `open_ended_code_"):
                cells = [cell.strip() for cell in line.strip("|").split("|")]
                assert len(cells) == 7, (task_id, cells)
                rows[cells[0].strip("`")] = cells
        assert len(rows) == 30
        local_jobs, local_histories = {}, set()
        for run in runs:
            outcome = run["outcome"]
            score = outcome["original_evaluator_score"]
            assert score in (0, 1) and outcome["original_evaluator_score_field"] == "accuracy.score"
            cells = rows[run["run_id"]]
            assert float(cells[2].split(" / ")[1]) == score
            assert cells[4] == (run["solution_route"]["classification"] or "unclassified")
            artifacts = {a["original_name"]: a for a in run["artifacts"] if a.get("local_path")}
            evaluation = json.loads((report.parent / artifacts["evaluation.json"]["local_path"]).read_text())
            usage = json.loads((report.parent / artifacts["usage.json"]["local_path"]).read_text())
            assert evaluation["accuracy"]["score"] == score
            assert evaluation["step_completion"] == outcome["step_completion"]
            assert usage["totals"]["input_tokens"] == run["usage"]["provider_reported_input_tokens"]
            assert run["usage"]["provider_reported_input_tokens"] > 0
            mode = evaluation["accuracy"].get("source_mode", evaluation["accuracy"].get("mode"))
            raw_modes[str(evaluation["accuracy"].get("mode"))] += 1
            if mode:
                verifier_groups[mode].append(run)
            server = run["environment"].get("galaxy_server")
            for artifact in run["artifacts"]:
                if artifact.get("history_id"):
                    local_histories.add((server, artifact["history_id"]))
            for event in run["events"]:
                if event["execution_location"] != "galaxy_job" or event["event_type"] != "analysis":
                    continue
                key = (server, event["native_job_id"])
                if key in all_jobs and any(all_jobs[key].get(k) != event.get(k) for k in ("status", "tool")):
                    job_conflicts.append(list(key))
                local_jobs[key] = event
                all_jobs[key] = event
            recovery_runs += bool(run["recovery_episodes"])
            recovery_episodes += len(run["recovery_episodes"])
        counts = Counter((model_slug(r), r["condition"], r["replicate_id"]) for r in runs)
        assert len(counts) == 30 and set(counts.values()) == {1}
        assert set(r["replicate_id"] for r in runs) == {1, 2, 3}
        token_comparisons = []
        for slug in sorted({model_slug(r) for r in runs}):
            median_tokens = {
                c: statistics.median(r["usage"]["provider_reported_input_tokens"] for r in runs if model_slug(r) == slug and r["condition"] == c)
                for c in CONDITIONS
            }
            ratio = median_tokens["galaxy"] / median_tokens["open_ended_code"]
            saved = next(c for c in evidence["comparisons"] if c["comparison_id"] == "input_tokens_" + slug)
            assert math.isclose(ratio, saved["estimate"], rel_tol=1e-12)
            token_comparisons.append({"model": slug, "ratio": ratio})
        summary = {
            "task": task_id,
            "capsule": metadata["capsule_uuid"],
            "accuracy": accepted(runs),
            "jobs": len(local_jobs),
            "error_jobs": sum(e["status"] == "error" for e in local_jobs.values()),
            "histories": len(local_histories),
            "token_ratios": token_comparisons,
        }
        assert f"**{len(local_jobs)} distinct analytical creating jobs**" in markdown
        tasks.append(summary)
        records.extend(runs)
        groups[metadata["capsule_uuid"]].append(summary)
        all_histories.update(local_histories)
        hashes.append({
            "task": task_id,
            "report_sha256": hashlib.sha256(report.read_bytes()).hexdigest(),
            "evidence_sha256": hashlib.sha256(evidence_path.read_bytes()).hexdigest(),
            "metadata_sha256": hashlib.sha256(metadata_path.read_bytes()).hexdigest(),
        })

    models = {}
    for slug in sorted({model_slug(r) for r in records}):
        runs = [r for r in records if model_slug(r) == slug]
        ratios = [c["ratio"] for t in tasks for c in t["token_ratios"] if c["model"] == slug]
        models[slug] = {"accuracy": accepted(runs), "token_ratio": describe(ratios), "routes": {}}
        for c in CONDITIONS:
            subset = [r for r in runs if r["condition"] == c]
            family_counts = Counter(tag for r in subset for tag in (r["solution_route"]["classification"] or "unclassified").split(", "))
            models[slug]["routes"][c] = dict(family_counts)
            models[slug].setdefault("tokens", {})[c] = describe([r["usage"]["provider_reported_input_tokens"] for r in subset])
    differences = [t["accuracy"]["galaxy"]["accepted"] - t["accuracy"]["open_ended_code"]["accepted"] for t in tasks]
    model_task_differences = [
        sum(r["outcome"]["original_evaluator_score"] * (1 if r["condition"] == "galaxy" else -1) for r in records if r["task_id"] == t["task"] and model_slug(r) == slug)
        for t in tasks for slug in models
    ]

    # Resample source capsules as blocks, preserving both conditions and all runs.
    # Weight by the number of retained questions to preserve the original estimand.
    blocks = [(sum(t["accuracy"]["galaxy"]["accepted"] - t["accuracy"]["open_ended_code"]["accepted"] for t in ts), 15 * len(ts)) for ts in groups.values()]
    rng = random.Random(20260920)
    bootstrap = []
    for _ in range(resamples):
        selected = rng.choices(blocks, k=len(blocks))
        bootstrap.append(100 * sum(x[0] for x in selected) / sum(x[1] for x in selected))
    ratios = [c["ratio"] for t in tasks for c in t["token_ratios"]]
    task_ratios = [statistics.median(c["ratio"] for c in t["token_ratios"]) for t in tasks]
    return {
        "scope": {"tasks": len(tasks), "runs": len(records), "capsules": len(groups), "histories_with_datasets": len(all_histories)},
        "accuracy": accepted(records),
        "task_comparisons": dict(Counter("galaxy_higher" if d > 0 else "code_higher" if d < 0 else "tie" for d in differences)),
        "model_task_comparisons": dict(Counter("galaxy_higher" if d > 0 else "code_higher" if d < 0 else "tie" for d in model_task_differences)),
        "tasks_with_any_accepted": {c: sum(t["accuracy"][c]["accepted"] > 0 for t in tasks) for c in CONDITIONS},
        "tasks_with_all_accepted": {c: sum(t["accuracy"][c]["accepted"] == 15 for t in tasks) for c in CONDITIONS},
        "tasks_with_none_accepted": {c: [t["task"] for t in tasks if t["accuracy"][c]["accepted"] == 0] for c in CONDITIONS},
        "exploratory_cluster_bootstrap": {
            "unit": "source capsule", "clusters": len(blocks), "resamples": resamples, "seed": 20260920,
            "method": "percentile, linear quantiles; question-weighted pooled Galaxy minus code acceptance",
            "difference_pp": 100 * sum(differences) / 750,
            "interval_95_pp": [quantile(bootstrap, 0.025), quantile(bootstrap, 0.975)],
            "limitations": "Post hoc; assumes independence across capsules, which may share biological data. Does not establish causal effects, equivalence, or generalization beyond the selected corpus.",
        },
        "models": models,
        "source_verifier_groups_observed_only": {k: accepted(v) for k, v in verifier_groups.items()},
        "raw_evaluator_modes": dict(raw_modes),
        "jobs": {"unique": len(all_jobs), "states": dict(Counter(e["status"] for e in all_jobs.values())), "tools": dict(Counter(e["tool"] for e in all_jobs.values())), "conflicts": job_conflicts},
        "recovery_candidates": {"runs": recovery_runs, "episodes": recovery_episodes},
        "history_coverage": dict(Counter(r["evidence_completeness"]["public_history_contents"] for r in records if r["condition"] == "galaxy")),
        "step_checks": {c: dict(Counter(x["id"] + ":" + str(x["passed"]) for r in records if r["condition"] == c for x in r["outcome"]["step_completion"].get("steps", []))) for c in CONDITIONS},
        "missing_submitted_answers": [{"task": r["task_id"], "run": r["run_id"], "score": r["outcome"]["original_evaluator_score"]} for r in records if r["outcome"]["submitted_answer"] is None],
        "token_ratios": describe(ratios),
        "task_level_pearson": {"n": 50, "token_ratio_vs_jobs": statistics.correlation(task_ratios, [t["jobs"] for t in tasks]), "token_ratio_vs_errors": statistics.correlation(task_ratios, [t["error_jobs"] for t in tasks])},
        "tasks": tasks,
        "source_hashes": hashes,
        "validation": "All 1500 markdown scores and route labels match evidence JSON; scores and step checks match archived evaluation.json; input tokens match archived usage.json; all 250 ratios recomputed from unrounded condition medians.",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--resamples", type=int, default=100000)
    args = parser.parse_args()
    result = audit(Path(__file__).resolve().parents[1], args.resamples)
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(encoded)
        print(json.dumps({k: result[k] for k in ("scope", "accuracy", "exploratory_cluster_bootstrap", "token_ratios", "validation")}, indent=2))
    else:
        print(encoded, end="")
