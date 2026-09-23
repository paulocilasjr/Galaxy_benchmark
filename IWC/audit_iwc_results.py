#!/usr/bin/env python3
"""Recalculate manuscript evidence without replaying or changing archived runs.

This is a supplemental aggregate, not a migration of the legacy task evidence.
Run from any directory with Python 3. Reports remain editorial documents.
"""

from collections import Counter, defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import random
import statistics as stats
import sys

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent))
from analysis_execution.workbook import load_inventory

HOST = "wf_003_host_contamination_removal"
SEED = 20260923
RESAMPLES = 10000
CONDITIONS = ("galaxy", "open_ended_code")


def read(path):
    return json.loads(path.read_text())


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def quantile(values, q):
    values = sorted(values)
    position = (len(values) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(values) - 1)
    return values[lower] + (values[upper] - values[lower]) * (position - lower)


def distribution(values):
    values = list(values)
    if not values:
        return {"n": 0}
    return dict(n=len(values), mean=stats.mean(values), median=stats.median(values),
                q1=quantile(values, .25), q3=quantile(values, .75),
                minimum=min(values), maximum=max(values))


def bootstrap(differences):
    rng = random.Random(SEED)
    values = list(differences)
    samples = [stats.mean(rng.choices(values, k=len(values))) for _ in range(RESAMPLES)]
    return {"estimate": stats.mean(values), "ci95": [quantile(samples, .025), quantile(samples, .975)],
            "tasks": len(values), "task_differences": values}


def route_name(method):
    # Normalize spelling only, retaining aligner generations and method families.
    if not method:
        return None
    aliases = {"bowtie 2": "bowtie2", "edger quasi-likelihood": "edger"}
    return " + ".join(aliases.get(str(method[k]).lower(), str(method[k]).lower())
                      for k in sorted(method))


def build():
    sources = {}

    def source(path):
        relative = str(path.relative_to(ROOT))
        if relative not in sources:
            sources[relative] = {"sha256": digest(path), "bytes": path.stat().st_size}
        return relative

    workbook = ROOT / "iwc_execution_condition_links.xlsx"
    inventory = load_inventory(workbook)
    links = {(row.task, row.run_id): row for row in inventory}
    runs, jobs, histories, recoveries, integrity_errors = [], {}, [], [], []
    file_status, trace_bytes = Counter(), Counter()
    checked_files = 0
    for ep in sorted((ROOT / "analysis").glob("*/history_analysis_evidence.json")):
        evidence = read(ep)
        task = evidence["task"]["task_id"]
        evidence_ref = source(ep)
        for old in evidence["runs"]:
            run_id = old["run_id"]
            row = links[task, run_id]
            base = ep.parent / "source_snapshots/huggingface_traces/files" / run_id
            evaluation = read(base / "evaluation.json")
            record = read(base / "run_record.json")
            workspace = base / "agent_workspace"
            invocation_path = workspace / "run_trace/codex_invocation.json"
            invocation = read(invocation_path)
            trace = workspace / "run_trace/codex_events.jsonl"
            # One retained plain trace is partial; its compressed counterpart has
            # the terminal event. Never add the two representations together.
            if trace.with_suffix(".jsonl.gz").exists():
                trace = trace.with_suffix(".jsonl.gz")
            usage, malformed = [], []
            opener = gzip.open if trace.suffix == ".gz" else open
            with opener(trace, "rt") as stream:
                for line_number, line in enumerate(stream, 1):
                    try:
                        event = json.loads(line)
                    except ValueError:
                        malformed.append(line_number)
                        continue
                    if event.get("type") == "turn.completed":
                        usage.append({"line": line_number, **event["usage"]})
            assert len(usage) == 1, (task, run_id, "ambiguous terminal usage")
            method_path = workspace / "final_answer/method.json"
            method = read(method_path) if method_path.exists() else None
            score = evaluation["reference_accuracy"]
            previous = record.get("acc")
            conflict = (score is None) != (previous is None)
            if score is not None and previous is not None:
                conflict = abs(score - previous) > 1e-9
            run_jobs = []
            for event in old["events"]:
                if event.get("execution_location") != "galaxy_job":
                    continue
                key = old["environment"]["galaxy_server"] + "/jobs/" + event["native_job_id"]
                if key not in jobs:
                    jobs[key] = {"task": task, "run_refs": [], "event_id": event["event_id"],
                                 "tool": event["tool"], "status": event.get("status"),
                                 "acquisition": event["tool"] in {"__DATA_FETCH__", "upload1"},
                                 "evidence": evidence_ref}
                jobs[key]["run_refs"].append(task + "/" + run_id)
                run_jobs.append(key)
            run_jobs = sorted(set(run_jobs))
            failed = [key for key in run_jobs if jobs[key]["status"] in {"error", "failed"}]
            for recovery in old["recovery_episodes"]:
                recoveries.append({"task": task, "run_id": run_id, "evidence": evidence_ref, **recovery})
            final_files = []
            for name in evaluation.get("final_answer_files", []):
                path = workspace / name
                final_files.append({"path": str(path.relative_to(ROOT)), "retained": path.exists()})
            runs.append({
                "id": task + "/" + run_id, "task": task, "run_id": run_id,
                "model": row.model, "condition": old["condition"], "replicate": old["replicate_id"],
                "workbook_sheet": row.sheet, "workbook_row": row.row,
                "original_condition": record.get("condition"), "runtime": invocation["runtime"],
                "started_at_utc": invocation["started_at_utc"],
                "wall_timeout_seconds": invocation["wall_clock_timeout_seconds"],
                "input_tree_sha256": invocation.get("workspace_contract", {}).get("input_tree_sha256"),
                "skills_revision": invocation.get("skills_bundle", {}).get("revision"),
                "skills_bundle_sha256": invocation.get("skills_bundle", {}).get("sha256"),
                "prompt_sha256": digest(workspace / "prompt.txt"),
                "harness_status": record.get("status"), "score": score,
                "run_record_acc": previous, "score_conflict_gt_1e_9": conflict,
                "evaluation_version": evaluation["evaluation_version"], "metric": evaluation["metric"],
                "evaluation_error": evaluation.get("error"), "evaluator_route": evaluation.get("route"),
                "declared_method": method, "declared_route_normalized": route_name(method),
                "final_answer_files": final_files, "usage": usage[0], "malformed_trace_lines": malformed,
                "job_refs": run_jobs, "failed_job_refs": failed,
                "shell_calls": old["derived_metrics"].get("completed_shell_calls"),
                "nonzero_shell_calls": old["derived_metrics"].get("nonzero_exit_shell_calls"),
                "sources": {"evaluation": source(base / "evaluation.json"), "record": source(base / "run_record.json"),
                            "invocation": source(invocation_path), "trace": source(trace),
                            "prompt": source(workspace / "prompt.txt"), "evidence": evidence_ref,
                            "method": source(method_path) if method else None},
            })
        for mp in sorted((ep.parent / "source_snapshots/huggingface_traces/manifests").glob("*.json")):
            manifest = read(mp)
            source(mp)
            for item in manifest["files"]:
                file_status[item["status"]] += 1
                trace_bytes[item["status"]] += item.get("retained_bytes", 0)
                if item.get("local_path") and item.get("retained_sha256"):
                    path = ep.parent / item["local_path"]
                    checked_files += 1
                    if not path.exists() or path.stat().st_size != item["retained_bytes"] or digest(path) != item["retained_sha256"]:
                        integrity_errors.append(str(path.relative_to(ROOT)))
        for mp in sorted((ep.parent / "source_snapshots/galaxy").glob("*/manifest.json")):
            manifest = read(mp)
            histories.append({"task": task, "source": source(mp), **manifest})
            for item in manifest.get("outputs", []):
                path = ep.parent / item["path"]
                checked_files += 1
                if not path.exists() or path.stat().st_size != item["retained_bytes"] or digest(path) != item["retained_sha256"]:
                    integrity_errors.append(str(path.relative_to(ROOT)))
            for item in manifest.get("jobs", []):
                path = ep.parent / item["path"]
                checked_files += 1
                if not path.exists() or digest(path) != item["sha256"]:
                    integrity_errors.append(str(path.relative_to(ROOT)))
    assert len(runs) == len(links) == len({r["id"] for r in runs}) == 240
    assert not integrity_errors, integrity_errors
    tasks = sorted({r["task"] for r in runs})
    models = sorted({r["model"] for r in runs})
    cells = defaultdict(list)
    for run in runs:
        cells[run["task"], run["model"], run["condition"]].append(run)
    assert len(cells) == 80 and all(len(v) == 3 for v in cells.values())
    comparisons = {}
    for name, eligible in (("common_nine_tasks", [t for t in tasks if t != HOST]), ("available_pairs", tasks)):
        comparisons[name] = {}
        for model in models:
            pairs = []
            for task in eligible:
                sides = [cells[task, model, condition] for condition in CONDITIONS]
                if not all(all(r["score"] is not None for r in side) for side in sides):
                    continue
                means = [stats.mean(r["score"] for r in side) for side in sides]
                pairs.append({"task": task, "galaxy": means[0], "open_ended_code": means[1],
                              "difference": means[0] - means[1], "run_ids": [r["id"] for side in sides for r in side]})
            comparisons[name][model] = {"pairs": pairs, "galaxy": stats.mean(p["galaxy"] for p in pairs),
                                       "open_ended_code": stats.mean(p["open_ended_code"] for p in pairs),
                                       **bootstrap(p["difference"] for p in pairs)}
    task_results = {}
    token_results = {}
    operational = {}
    for task in tasks:
        task_results[task] = {c: distribution(r["score"] for r in runs if r["task"] == task and r["condition"] == c and r["score"] is not None) for c in CONDITIONS}
    for model in models:
        token_results[model] = {}
        for c in CONDITIONS:
            selected = [r for r in runs if r["model"] == model and r["condition"] == c]
            token_results[model][c] = {field: distribution(r["usage"][field] for r in selected) for field in ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens")}
            token_results[model][c]["run_ids"] = [r["id"] for r in selected]
        for field in ("input_tokens", "output_tokens"):
            ratios = [stats.median(r["usage"][field] for r in cells[t, model, "galaxy"]) / stats.median(r["usage"][field] for r in cells[t, model, "open_ended_code"]) for t in tasks]
            token_results[model][field + "_task_median_ratios"] = {"tasks": tasks, "ratios": ratios, **distribution(ratios)}
    for c in CONDITIONS:
        selected = [r for r in runs if r["condition"] == c]
        observed = [r for r in selected if r["job_refs"]]
        operational[c] = {"runs": len(selected), "runs_with_observed_jobs": len(observed),
                          "runs_with_job_failures": sum(bool(r["failed_job_refs"]) for r in observed) if observed else None,
                          "failed_jobs_per_observed_run": distribution(len(r["failed_job_refs"]) for r in observed),
                          "runs_with_nonzero_shell_calls": sum(bool(r["nonzero_shell_calls"]) for r in selected),
                          "nonzero_shell_calls_per_run": distribution(r["nonzero_shell_calls"] for r in selected if r["nonzero_shell_calls"] is not None)}
    route_cells = []
    for (task, model, condition), selected in sorted(cells.items()):
        routes = [r["declared_route_normalized"] for r in selected]
        if any(routes):
            route_cells.append({"task": task, "model": model, "condition": condition,
                                "complete": all(routes), "distinct_routes": len(set(routes) - {None}),
                                "runs": [{k: r[k] for k in ("id", "replicate", "declared_method", "declared_route_normalized", "score", "usage", "failed_job_refs")} for r in selected]})
    output = {
        "format": "iwc-manuscript-supplement-v1", "audit_id": "iwc-local-scientific-audit-20260923",
        "workbook": source(workbook), "script": source(Path(__file__)),
        "scope": "Observed workbook runs only; no replay, hidden-reference access, regrading or source mutation",
        "methods": {"score": "evaluation.json/reference_accuracy; preserve run_record.acc separately",
                    "uncertainty": "paired task percentile bootstrap retaining all replicate bundles", "seed": SEED, "resamples": RESAMPLES,
                    "primary_sensitivity": "nine common tasks excluding unresolved host-removal route adjudication; exploratory, not prespecified",
                    "quantiles": "linear interpolation at (n-1)*q", "usage": "single terminal turn.completed event per run; no addition of cached or reasoning subsets",
                    "job_scope": "visible creating jobs, not validated run-owned actions; server/job ID deduplication",
                    "acquisition": "__DATA_FETCH__ and upload1; all other jobs are other creating jobs, not uniformly scientific attempts",
                    "route_codebook": "final_answer/method.json declarations only; lowercase, bowtie 2 -> bowtie2, edgeR quasi-likelihood -> edgeR; no inference from shell utility vocabulary"},
        "inventory": {"observed_runs": len(runs), "tasks": tasks, "models": models, "expected_protocol_coverage": None},
        "sources": dict(sorted(sources.items())), "runs": runs, "comparisons": comparisons, "task_results": task_results,
        "token_results": token_results, "operational": operational, "route_cells": route_cells,
        "jobs": jobs, "recovery_candidates": recoveries, "histories": histories,
        "archive": {"trace_file_statuses": dict(file_status), "trace_bytes": dict(trace_bytes),
                    "selected_galaxy_output_files": sum(len(h.get("outputs", [])) for h in histories),
                    "explicitly_skipped_galaxy_outputs": sum(len(h.get("skipped_outputs", [])) for h in histories)},
        "validation": {"retained_files_checked_against_collection_manifests": checked_files,
                       "integrity_errors": integrity_errors, "unique_runs": True, "balanced_observed_cells": True,
                       "terminal_usage_events_per_run": 1, "schema_note": "Supplemental format, not a claim of task-evidence schema 2.0 conformance"},
        "finding_run_sets": {
            "IWC-F1": [r["id"] for r in runs],
            "IWC-F2": [r["id"] for r in runs if r["task"] != HOST],
            "IWC-F3": [r["id"] for r in runs if r["score_conflict_gt_1e_9"]],
            "IWC-F4": [r["id"] for r in runs if r["condition"] == "galaxy"],
            "IWC-F5": [r["id"] for r in runs if r["declared_method"]],
            "IWC-F6": [r["id"] for r in runs],
            "IWC-F7": [r["id"] for r in runs if r["score"] == 0],
        },
    }
    target = ROOT / "iwc_scientific_audit.json"
    target.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"output": target.name, "runs": len(runs), "sources": len(sources), **output["validation"]}, indent=2))


if __name__ == "__main__":
    build()
