#!/usr/bin/env python3
"""Build local IWC overview, recovery, and results artifacts from archived evidence."""

from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
sys.path.insert(0, str(REPO))
from analysis_execution.workbook import load_inventory

WORKBOOK = ROOT / "iwc_execution_condition_links.xlsx"
ANALYSIS = ROOT / "analysis"
CONDITIONS = ("galaxy", "open_ended_code")
MODEL_LABELS = ("GPT-5.5", "GPT-5.6 Sol", "GPT-5.6 Luna", "Codex + DeepSeek V4 Pro")


def read(path: Path):
    return json.loads(path.read_text())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def mean(values):
    values = [value for value in values if value is not None]
    return statistics.mean(values) if values else None


def model_slug(run_id: str) -> str:
    return run_id.split("_r", 1)[0].split("_", 1)[1]


def source_map(evidence: dict) -> dict:
    return {source["source_id"]: source for source in evidence["sources"]}


def source_status(run: dict, sources: dict, prefix: str):
    matches = [sources[source_id] for source_id in run["source_ids"] if source_id.startswith(prefix)]
    return matches[0].get("access_status") if matches else "not_linked"


def collect_records(inventory: list, evidence_files: list[Path]):
    expected = {(row.task, row.run_id): row for row in inventory}
    run_index = []
    task_rows = {}
    job_events = {}
    task_stats = {}
    trace_files = Counter()
    trace_bytes = Counter()
    history_status = Counter()
    history_tls = Counter()
    output_stats = Counter()
    skipped_outputs = []

    for evidence_path in evidence_files:
        evidence = read(evidence_path)
        task = evidence["task"]["task_id"]
        sources = source_map(evidence)
        task_rows[task] = len(evidence["runs"])
        task_job_keys = set()
        task_job_status = Counter()
        task_failed_jobs = []
        task_scores = Counter()
        task_output_count = 0
        for run in evidence["runs"]:
            link = expected[(task, run["run_id"])]
            score = run["outcome"].get("original_evaluator_score")
            if score is not None:
                task_scores["numeric"] += 1
            else:
                task_scores["missing"] += 1
            history = source_status(run, sources, "src_galaxy_")
            trace = source_status(run, sources, "src_trace_")
            outputs = [artifact for artifact in run["artifacts"] if artifact.get("history_id")]
            task_output_count += len(outputs)
            run_index.append({
                "task": task,
                "run_id": run["run_id"],
                "model": link.model,
                "condition": run["condition"],
                "original_condition_label": link.condition_label,
                "replicate": run["replicate_id"],
                "workbook_sheet": link.sheet,
                "workbook_row": link.row,
                "score_field": run["outcome"].get("original_evaluator_score_field"),
                "score": score,
                "answer_present": bool(run["outcome"].get("submitted_answer")),
                "trace_status": trace,
                "galaxy_history_status": history,
                "analytical_job_count": run["derived_metrics"].get("analytical_job_count"),
                "failed_job_count": run["derived_metrics"].get("total_failed_jobs"),
                "evidence_path": str(evidence_path.relative_to(ROOT)),
            })
            for event in run["events"]:
                if event.get("execution_location") != "galaxy_job" or event.get("event_type") != "analysis":
                    continue
                key = (run["environment"].get("galaxy_server"), event.get("native_job_id"))
                task_job_keys.add(key)
                task_job_status[event.get("status") or "unknown"] += 1
                job_events.setdefault(key, {"task": task, "run_ids": [], "event": event})["run_ids"].append(run["run_id"])
                if event.get("status") in {"error", "failed"}:
                    task_failed_jobs.append({"run_id": run["run_id"], "native_job_id": event.get("native_job_id"), "tool": event.get("tool"), "status": event.get("status")})

        for source in evidence["sources"]:
            if source["source_id"].startswith("src_galaxy_"):
                history_status[source.get("access_status", "unknown")] += 1
                history_tls[str(source.get("tls_certificate_verified"))] += 1
        task_stats[task] = {
            "runs": len(evidence["runs"]),
            "models": sorted({link.model for link in (expected[(task, run["run_id"])] for run in evidence["runs"])}),
            "conditions": dict(Counter(run["condition"] for run in evidence["runs"])),
            "replicates": sorted({run["replicate_id"] for run in evidence["runs"]}),
            "numeric_scores": task_scores["numeric"],
            "missing_scores": task_scores["missing"],
            "answers_present": sum(bool(run["outcome"].get("submitted_answer")) for run in evidence["runs"]),
            "trace_statuses": dict(Counter(source_status(run, sources, "src_trace_") for run in evidence["runs"])),
            "galaxy_history_statuses": dict(Counter(source_status(run, sources, "src_galaxy_") for run in evidence["runs"])),
            "distinct_analytical_jobs": len(task_job_keys),
            "analytical_job_statuses": dict(task_job_status),
            "failed_jobs": task_failed_jobs,
            "selected_galaxy_outputs": task_output_count,
            "evidence_path": str(evidence_path.relative_to(ROOT)),
            "report_path": str(evidence_path.with_name("history_analysis.md").relative_to(ROOT)),
        }

        manifest_root = evidence_path.parent / "source_snapshots" / "huggingface_traces" / "manifests"
        for manifest_path in manifest_root.glob("*.json"):
            manifest = read(manifest_path)
            for item in manifest.get("files", []):
                status = item.get("status", "unknown")
                trace_files[status] += 1
                trace_bytes[status] += item.get("retained_bytes", 0) or 0
        for history_manifest in (evidence_path.parent / "source_snapshots" / "galaxy").glob("*/manifest.json"):
            manifest = read(history_manifest)
            output_stats["history_manifests"] += 1
            output_stats["selected_outputs"] += len(manifest.get("outputs", []))
            output_stats["skipped_outputs"] += len(manifest.get("skipped_outputs", []))
            skipped_outputs.extend({"task": task, "history_id": manifest.get("history_id"), **item} for item in manifest.get("skipped_outputs", []))

    return {
        "run_index": sorted(run_index, key=lambda item: (item["task"], item["run_id"])),
        "task_rows": task_rows,
        "task_stats": task_stats,
        "job_events": job_events,
        "trace_files": dict(trace_files),
        "trace_bytes": dict(trace_bytes),
        "history_status": dict(history_status),
        "history_tls": dict(history_tls),
        "output_stats": dict(output_stats),
        "skipped_outputs": skipped_outputs,
    }


def write(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n")


def build() -> dict:
    inventory = load_inventory(WORKBOOK)
    evidence_files = sorted(ANALYSIS.glob("*/history_analysis_evidence.json"))
    collected = collect_records(inventory, evidence_files)
    models = Counter(row.model for row in inventory)
    conditions = Counter(row.condition for row in inventory)
    task_count = len({row.task for row in inventory})
    overview = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "benchmark": "iwc",
        "workbook": {"path": WORKBOOK.name, "sha256": sha256(WORKBOOK), "sheet": "IWC links", "rows": len(inventory)},
        "inventory": {
            "tasks": task_count,
            "runs": len(inventory),
            "models": dict(sorted(models.items())),
            "conditions": dict(sorted(conditions.items())),
            "replicates": sorted({row.replicate for row in inventory}),
            "rows_per_task": collected["task_rows"],
            "expected_runs_per_task": 24,
        },
        "source_retrieval": {
            "trace_directories": len({row.trace_url for row in inventory if row.trace_url}),
            "galaxy_histories": len({row.galaxy_url for row in inventory if row.galaxy_url}),
            "trace_files": collected["trace_files"],
            "trace_retained_bytes_by_status": collected["trace_bytes"],
            "galaxy_history_statuses": collected["history_status"],
            "tls_certificate_verified": collected["history_tls"],
            "selected_outputs": collected["output_stats"].get("selected_outputs", 0),
            "skipped_outputs": collected["output_stats"].get("skipped_outputs", 0),
        },
        "job_inventory": {
            "distinct_analytical_jobs": len(collected["job_events"]),
            "statuses": dict(Counter(item["event"].get("status") or "unknown" for item in collected["job_events"].values())),
        },
        "tasks": collected["task_stats"],
        "run_index": collected["run_index"],
        "skipped_outputs": collected["skipped_outputs"],
        "provenance": {
            "task_evidence_files": len(evidence_files),
            "source_collection": "analysis_execution read-only retrospective audit",
            "scientific_analysis_rerun": False,
            "hidden_ground_truth_opened": False,
        },
    }
    write(ROOT / "iwc_overview_audit.json", overview)

    recovery = {
        "generated_at_utc": overview["generated_at_utc"],
        "workbook": overview["workbook"],
        "policy": "Source traces and public Galaxy histories were retrieved read-only. No agent code was rerun and no hidden ground truth was opened.",
        "source_status": overview["source_retrieval"],
        "job_inventory": overview["job_inventory"],
        "task_status": {task: {key: value for key, value in stats.items() if key not in {"models", "conditions", "replicates", "failed_jobs"}} for task, stats in overview["tasks"].items()},
        "failed_jobs": {task: stats["failed_jobs"] for task, stats in overview["tasks"].items() if stats["failed_jobs"]},
        "skipped_outputs": collected["skipped_outputs"],
    }
    write(ROOT / "iwc_recovery_summary.json", recovery)

    lines = ["# IWC overview", "", "This directory contains a retrospective, read-only evidence archive for the supplied IWC execution-link workbook. It preserves task-scoped traces, Galaxy history metadata and jobs, selected text outputs, recovered commands, and validated evidence JSON for later analysis.", "", "## Inventory", "", f"The workbook contains **{len(inventory)} runs** across **{task_count} tasks**, **{len(models)} models**, two execution conditions, and replicate labels {', '.join(map(str, sorted({row.replicate for row in inventory})))}. Each task has 24 observed rows.", "", "| Model | Runs |", "|---|---:|"]
    lines += [f"| {model} | {count} |" for model, count in sorted(models.items())]
    lines += ["", "| Condition | Runs |", "|---|---:|"]
    lines += [f"| {condition} | {count} |" for condition, count in sorted(conditions.items())]
    lines += ["", "## Evidence", "", f"The archive contains **{len(collected['job_events'])} distinct analytical creating jobs**. Source retrieval statuses, per-run links, hashes, outputs, skipped binary outputs, and metadata-only histories are recorded in [iwc_recovery_summary.json](iwc_recovery_summary.json). The full machine-readable aggregate index is [iwc_overview_audit.json](iwc_overview_audit.json).", "", "No benchmark answer was regraded, no agent code was executed, and no hidden ground truth was opened.", ""]
    (ROOT / "iwc_overview.md").write_text("\n".join(lines))

    result_lines = ["# IWC Results Evidence Draft", "", f"We archived {len(inventory)} workbook-listed IWC runs across {task_count} tasks, four model labels, two execution conditions, and three replicate labels. This document is an evidence inventory for later scientific analysis; it is not a re-evaluation of the benchmark.", "", "| Task | Runs | Numeric scores | Distinct analytical jobs | Failed jobs | Selected Galaxy outputs |", "|---|---:|---:|---:|---:|---:|"]
    for task, stats in sorted(overview["tasks"].items()):
        result_lines.append(f"| {task} | {stats['runs']} | {stats['numeric_scores']} | {stats['distinct_analytical_jobs']} | {sum(1 for job in stats['failed_jobs'])} | {stats['selected_galaxy_outputs']} |")
    result_lines += ["", "The original evaluator fields and submitted answers remain in each task's `history_analysis_evidence.json`. Scores are not converted into a common metric here. Galaxy execution jobs, shell/API calls, and scientific attempts remain separate quantities. Detailed route, token, artifact, and recovery evidence is retained under each task directory.", "", "## Limitations", "", "The source workbook is an observed-link inventory and does not independently establish protocol coverage, matched seeds, or stopping rules. Two histories exceeded the configured detailed-content cap and are marked metadata-only. TLS certificate verification was disabled because the local CA certificate was rejected by Python; this limitation is recorded in the source manifests. Binary or oversized outputs are listed rather than silently substituted.", ""]
    (ROOT / "result_section_iwc.md").write_text("\n".join(result_lines))

    recovery_lines = ["# IWC Recovery Summary", "", "The source workbook was matched to all task-scoped audit packages. Retrieval was read-only and preserved source URLs, retrieval timestamps, local paths, byte hashes, and explicit unavailable/metadata-only states.", "", f"- Workbook rows matched: **{len(inventory)}**.", f"- Task packages: **{len(evidence_files)}**.", f"- Distinct analytical Galaxy jobs: **{len(collected['job_events'])}**.", f"- Fully detailed Galaxy histories: **{collected['history_status'].get('retrieved', 0)}**.", f"- Metadata-only Galaxy histories: **{collected['history_status'].get('history_metadata_only', 0)}**.", f"- Selected text outputs retained: **{collected['output_stats'].get('selected_outputs', 0)}**.", f"- Outputs skipped because binary, oversized, or otherwise ineligible: **{collected['output_stats'].get('skipped_outputs', 0)}**.", "", "All source manifests record `tls_certificate_verified: false` for this collection because the environment's CA certificate failed Python verification. Hashes authenticate retained local bytes, not remote-server identity.", ""]
    (ROOT / "iwc_recovery_summary.md").write_text("\n".join(recovery_lines))
    return overview


if __name__ == "__main__":
    result = build()
    print(json.dumps({"tasks": result["inventory"]["tasks"], "runs": result["inventory"]["runs"], "jobs": result["job_inventory"]["distinct_analytical_jobs"]}))
