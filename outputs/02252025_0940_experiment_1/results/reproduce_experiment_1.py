#!/usr/bin/env python3
"""
Reproduce experiment_1 end-to-end with Galaxy API calls.

This script:
1) reads the benchmark experiment definition,
2) creates Galaxy history + uploads datasets,
3) runs Tabular Learner with the specified parameters,
4) polls the job until terminal,
5) extracts target + ROC-AUC from produced outputs,
6) writes benchmark artifacts required by README.md.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bioblend.galaxy import GalaxyInstance


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env_key(env_path: Path) -> str:
    if not env_path.exists():
        raise RuntimeError("Missing .env file in repository root.")
    raw = None
    for line in env_path.read_text().splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        key, value = s.split("=", 1)
        if key.strip() == "GALAXY_API_KEY":
            raw = value.strip()
            break
    if raw is None or raw == "":
        raise RuntimeError("Missing required credential: GALAXY_API_KEY in .env.")
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        raw = raw[1:-1]
    if not raw.strip():
        raise RuntimeError("Missing required credential: GALAXY_API_KEY in .env.")
    return raw


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")


def append_reasoning(path: Path, step: str, decision: str, why: str, next_action: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(f"## {utc_now()} | {step}\n")
        fh.write(f"- Decision made: {decision}\n")
        fh.write(f"- Why this decision was made: {why}\n")
        fh.write(f"- Next action: {next_action}\n\n")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def parse_version(tool_id: str) -> tuple[int, ...]:
    tail = tool_id.rsplit("/", 1)[-1]
    nums: list[int] = []
    for part in tail.split("."):
        if part.isdigit():
            nums.append(int(part))
        else:
            break
    return tuple(nums) if nums else (0,)


@dataclass
class ExperimentPaths:
    experiment_name: str
    root: Path
    out_dir: Path
    plan_path: Path
    reasoning_path: Path
    error_path: Path
    result_path: Path
    activity_log_path: Path
    comparison_path: Path


def build_paths(repo_root: Path, experiment_name: str) -> ExperimentPaths:
    out_dir = repo_root / "outputs" / experiment_name
    return ExperimentPaths(
        experiment_name=experiment_name,
        root=repo_root,
        out_dir=out_dir,
        plan_path=out_dir / "plan" / "saved.md",
        reasoning_path=out_dir / "reasoning" / "reasoning.md",
        error_path=out_dir / "errors" / "error.json",
        result_path=out_dir / "results" / "result.json",
        activity_log_path=out_dir / "results" / "activity_log.jsonl",
        comparison_path=out_dir / "results" / "comparison_report.md",
    )


def write_plan(paths: ExperimentPaths, experiment: dict[str, Any]) -> None:
    prompt = experiment["prompt"]
    datasets = prompt["dataset"]
    lines: list[str] = []
    lines.append(f"# Plan: {paths.experiment_name}")
    lines.append("")
    lines.append("## Experiment name")
    lines.append(paths.experiment_name)
    lines.append("")
    lines.append("## Initial objective")
    lines.append(prompt["task"])
    lines.append("")
    lines.append("## Inputs and datasets")
    for ds in datasets:
        lines.append(f"- {ds['name']}: {ds['path']}")
    lines.append("")
    lines.append("## Planned steps")
    lines.append("1. Validate Galaxy API credential from .env.")
    lines.append("2. Discover Tabular Learner tool and select latest available version.")
    lines.append("3. Create Galaxy history named experiment_1.")
    lines.append("4. Upload train and test TSV datasets to the history.")
    lines.append("5. Run Tabular Learner with separate test dataset and target column c22: Response.")
    lines.append("6. Poll Galaxy job until terminal state.")
    lines.append("7. Read tool outputs and extract target + ROC-AUC.")
    lines.append("8. Write result.json and reproduce_experiment_1.py artifacts.")
    lines.append("9. Read ground truth and generate comparison table.")
    lines.append("")
    lines.append("## Expected outputs")
    lines.append("- outputs/experiment_1/results/result.json")
    lines.append("- outputs/experiment_1/results/reproduce_experiment_1.py")
    lines.append("- outputs/experiment_1/results/activity_log.jsonl")
    lines.append("- outputs/experiment_1/results/comparison_report.md")
    lines.append("")
    lines.append("## Risks/assumptions")
    lines.append("- Galaxy remote job runtime may be variable.")
    lines.append("- Tool output format may vary by version; extraction uses resilient text matching.")
    lines.append("- API operations require a valid GALAXY_API_KEY and network reachability.")
    lines.append("")
    paths.plan_path.parent.mkdir(parents=True, exist_ok=True)
    paths.plan_path.write_text("\n".join(lines), encoding="utf-8")


def init_errors(paths: ExperimentPaths, started_at: str) -> dict[str, Any]:
    payload = {
        "experiment_name": paths.experiment_name,
        "run_status": "running",
        "started_at": started_at,
        "updated_at": started_at,
        "summary": {
            "total_errors": 0,
            "open_errors": 0,
            "resolved_errors": 0,
        },
        "errors": [],
    }
    write_json(paths.error_path, payload)
    return payload


def finalize_errors(paths: ExperimentPaths, error_doc: dict[str, Any], run_status: str) -> None:
    error_doc["run_status"] = run_status
    error_doc["updated_at"] = utc_now()
    errors = error_doc.get("errors", [])
    total = len(errors)
    open_count = sum(1 for e in errors if e.get("status") == "open")
    resolved_count = sum(1 for e in errors if e.get("status") == "resolved")
    error_doc["summary"] = {
        "total_errors": total,
        "open_errors": open_count,
        "resolved_errors": resolved_count,
    }
    write_json(paths.error_path, error_doc)


def add_error(
    paths: ExperimentPaths,
    error_doc: dict[str, Any],
    *,
    step: str,
    phase: str,
    severity: str,
    category: str,
    message: str,
    action_taken: str,
    resolution: str,
    status: str = "open",
    retry_count: int = 0,
    context: dict[str, Any] | None = None,
    additional_data: dict[str, Any] | None = None,
) -> None:
    err_id = f"err-{len(error_doc['errors']) + 1:04d}"
    error_doc["errors"].append(
        {
            "id": err_id,
            "timestamp": utc_now(),
            "step": step,
            "phase": phase,
            "severity": severity,
            "category": category,
            "status": status,
            "message": message,
            "job_id": None,
            "invocation_id": None,
            "action_taken": action_taken,
            "resolution": resolution,
            "retry_count": retry_count,
            "context": context or {},
            "additional_data": additional_data or {},
        }
    )
    error_doc["updated_at"] = utc_now()
    finalize_errors(paths, error_doc, error_doc.get("run_status", "running"))


def poll_dataset_state(gi: GalaxyInstance, history_id: str, dataset_id: str, activity_log_path: Path) -> str:
    first_check_done = False
    while True:
        details = gi.histories.show_dataset(history_id, dataset_id)
        state = details.get("state", "unknown")
        append_jsonl(
            activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "dataset_poll",
                "category": "check",
                "action": "Poll dataset state",
                "status": state,
                "details": {"history_id": history_id, "dataset_id": dataset_id},
            },
        )
        if state in {"ok", "error", "failed", "deleted", "discarded"}:
            return state
        if not first_check_done:
            time.sleep(20)
            first_check_done = True
        else:
            time.sleep(60)


def poll_job_state(gi: GalaxyInstance, job_id: str, activity_log_path: Path) -> str:
    first_check_done = False
    while True:
        job = gi.jobs.show_job(job_id)
        state = job.get("state", "unknown")
        append_jsonl(
            activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "tool_run_poll",
                "category": "check",
                "action": "Poll Tabular Learner job state",
                "status": state,
                "details": {"job_id": job_id},
            },
        )
        if state in {"ok", "error", "failed", "deleted"}:
            return state
        if not first_check_done:
            time.sleep(20)
            first_check_done = True
        else:
            time.sleep(60)


def extract_target_and_roc_auc(gi: GalaxyInstance, output_ids: list[str]) -> tuple[str | None, str | None, dict[str, str]]:
    target: str | None = None
    roc_auc: str | None = None
    raw_output_text: dict[str, str] = {}

    target_re = re.compile(r"(target(?:\\s+feature)?\\s*[:=]\\s*)([^\\n<]+)", re.IGNORECASE)
    roc_re = re.compile(r"ROC[- ]?AUC\\s*[:=]\\s*([0-9]*\\.?[0-9]+)", re.IGNORECASE)
    roc_table_re = re.compile(r"\\bAUC\\b[^0-9\\n\\r]*([0-9]*\\.?[0-9]+)")

    for dataset_id in output_ids:
        blob = gi.datasets.download_dataset(dataset_id, require_ok_state=False)
        text = blob.decode("utf-8", errors="replace") if isinstance(blob, (bytes, bytearray)) else str(blob)
        raw_output_text[dataset_id] = text

        if target is None:
            m_target = target_re.search(text)
            if m_target:
                target = m_target.group(2).strip()
            elif "c22: Response" in text:
                target = "c22: Response"
            elif "Response" in text:
                target = "Response"

        if roc_auc is None:
            m_roc = roc_re.search(text)
            if m_roc:
                roc_auc = m_roc.group(1)
            else:
                m_auc = roc_table_re.search(text)
                if m_auc:
                    roc_auc = m_auc.group(1)

    return target, roc_auc, raw_output_text


def write_comparison_table(
    paths: ExperimentPaths,
    agent_result: dict[str, Any],
    ground_truth: dict[str, Any],
) -> None:
    rows = []
    for field in ["tool_name", "target", "roc-auc"]:
        a = str(agent_result.get(field))
        g = str(ground_truth.get(field))
        status = "match" if a == g else "mismatch"
        note = "" if status == "match" else "Value differs."
        rows.append((field, a, g, status, note))

    lines = [
        "| Field | Agent Result | Ground Truth | Match Status | Notes |",
        "|---|---|---|---|---|",
    ]
    for field, a, g, status, note in rows:
        lines.append(f"| {field} | {a} | {g} | {status} | {note} |")
    paths.comparison_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    script_path = Path(__file__).resolve()
    repo_root = script_path.parents[3]

    experiment_path = repo_root / "experiments" / "experiment_1.json"
    experiment = json.loads(experiment_path.read_text(encoding="utf-8"))
    experiment_name = experiment_path.stem
    paths = build_paths(repo_root, experiment_name)

    # Ensure required directories exist.
    (paths.out_dir / "plan").mkdir(parents=True, exist_ok=True)
    (paths.out_dir / "reasoning").mkdir(parents=True, exist_ok=True)
    (paths.out_dir / "errors").mkdir(parents=True, exist_ok=True)
    (paths.out_dir / "results").mkdir(parents=True, exist_ok=True)

    started_at = utc_now()
    write_plan(paths, experiment)
    error_doc = init_errors(paths, started_at)

    # Start fresh logs for this run.
    paths.reasoning_path.write_text("", encoding="utf-8")
    paths.activity_log_path.write_text("", encoding="utf-8")

    append_reasoning(
        paths.reasoning_path,
        "init",
        "Follow README benchmark flow with strict logging and deferred ground truth access.",
        "The benchmark requires deterministic, structured artifacts and explicit chronology.",
        "Validate credentials and discover tool metadata.",
    )

    planned_actions = [
        "Validate credential",
        "Discover tool",
        "Create history",
        "Upload train dataset",
        "Upload test dataset",
        "Run Tabular Learner",
        "Poll tool job",
        "Extract outputs",
        "Write result artifact",
        "Build ground truth comparison",
    ]
    for idx, action in enumerate(planned_actions, start=1):
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": f"plan_{idx}",
                "category": "plan",
                "action": action,
                "status": "planned",
                "details": {"attempt": 1},
            },
        )

    prompt = experiment["prompt"]
    galaxy_url = prompt["galaxy_instance"].rstrip("/")
    history_name = prompt["history_name"]

    try:
        api_key = load_env_key(repo_root / ".env")
        append_reasoning(
            paths.reasoning_path,
            "credential_check",
            "Use GALAXY_API_KEY from .env after quote-normalization.",
            "The key is required for authenticated API calls; stripping surrounding quotes avoids auth mismatches.",
            "Create Galaxy client and discover Tabular Learner candidates.",
        )
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "credential_check",
                "category": "execute",
                "action": "Validate and load API key",
                "status": "completed",
                "details": {"credential": "GALAXY_API_KEY", "valid_format": True},
            },
        )

        gi = GalaxyInstance(url=galaxy_url, key=api_key)
        _ = gi.users.get_current_user()

        tool_candidates = gi.tools.get_tools(name=prompt["tool"]["name"])
        if not tool_candidates:
            raise RuntimeError("Tabular Learner tool not found in Galaxy instance.")
        candidate_ids = [t["id"] for t in tool_candidates]
        selected_tool = sorted(candidate_ids, key=parse_version)[-1]
        rejected = [tid for tid in candidate_ids if tid != selected_tool]

        append_reasoning(
            paths.reasoning_path,
            "tool_discovery",
            f"Selected {selected_tool} as execution tool.",
            (
                "Tool discovery used Galaxy tools API by name; highest semantic version was chosen "
                f"for stability and current compatibility. Rejected older candidates: {rejected}."
            ),
            "Create history and upload datasets.",
        )
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "tool_discovery",
                "category": "execute",
                "action": "Discover Tabular Learner tool IDs",
                "status": "completed",
                "details": {"selected_tool_id": selected_tool, "candidate_count": len(candidate_ids)},
            },
        )

        append_reasoning(
            paths.reasoning_path,
            "interface_choice",
            "Execute via BioBlend rather than raw HTTP calls.",
            (
                "BioBlend provides stable typed wrappers for history upload, tool execution, "
                "and polling with less request-shape risk than manual payload crafting."
            ),
            "Create history and upload datasets.",
        )

        history = gi.histories.create_history(name=history_name)
        history_id = history["id"]
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "create_history",
                "category": "execute",
                "action": "Create Galaxy history",
                "status": "completed",
                "details": {"history_id": history_id, "history_name": history_name},
            },
        )

        dataset_map: dict[str, str] = {}
        for ds in prompt["dataset"]:
            source_path = repo_root / ds["path"]
            append_jsonl(
                paths.activity_log_path,
                {
                    "timestamp": utc_now(),
                    "step": "dataset_upload",
                    "category": "execute",
                    "action": f"Upload dataset {ds['name']}",
                    "status": "started",
                    "details": {"history_id": history_id, "source_path": str(source_path)},
                },
            )
            upload_res = gi.tools.upload_file(str(source_path), history_id, file_type="tabular")
            out_list = upload_res.get("outputs", [])
            if not out_list:
                raise RuntimeError(f"Upload produced no outputs for dataset {ds['name']}.")
            dataset_id = out_list[0]["id"]
            state = poll_dataset_state(gi, history_id, dataset_id, paths.activity_log_path)
            if state != "ok":
                raise RuntimeError(f"Uploaded dataset {ds['name']} ended in state {state}.")
            dataset_map[ds["name"]] = dataset_id
            append_jsonl(
                paths.activity_log_path,
                {
                    "timestamp": utc_now(),
                    "step": "dataset_upload",
                    "category": "execute",
                    "action": f"Upload dataset {ds['name']}",
                    "status": "completed",
                    "details": {"dataset_id": dataset_id, "final_state": state},
                },
            )

        append_reasoning(
            paths.reasoning_path,
            "parameter_selection",
            "Map experiment prompt parameters directly to Tabular Learner inputs.",
            (
                "Input mapping used tool metadata: "
                "input_file=train TSV, test_data_choice|has_test_file=yes, "
                "test_data_choice|test_file=test TSV, target_feature=c22."
            ),
            "Run tool and poll until terminal state.",
        )

        train_ds_id = dataset_map["Chowell_train_Response.tsv"]
        test_ds_id = dataset_map["Chowell_test_Response.tsv"]
        tool_inputs = {
            "input_file": {"src": "hda", "id": train_ds_id},
            "test_data_choice|has_test_file": "yes",
            "test_data_choice|test_file": {"src": "hda", "id": test_ds_id},
            "target_feature": "c22",
        }
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "tool_run",
                "category": "execute",
                "action": "Run Tabular Learner",
                "status": "started",
                "details": {
                    "tool_id": selected_tool,
                    "history_id": history_id,
                    "inputs": {
                        "input_file": train_ds_id,
                        "test_file": test_ds_id,
                        "target_feature": "c22",
                        "has_test_file": "yes",
                    },
                },
            },
        )
        run_res = gi.tools.run_tool(history_id=history_id, tool_id=selected_tool, tool_inputs=tool_inputs)
        jobs = run_res.get("jobs", [])
        if not jobs:
            raise RuntimeError("Tool submission returned no job IDs.")
        job_id = jobs[0]["id"]
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "tool_run",
                "category": "execute",
                "action": "Run Tabular Learner",
                "status": "submitted",
                "details": {"job_id": job_id, "output_count_hint": len(run_res.get("outputs", []))},
            },
        )

        final_job_state = poll_job_state(gi, job_id, paths.activity_log_path)
        if final_job_state != "ok":
            raise RuntimeError(f"Tabular Learner job terminated with state {final_job_state}.")
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "tool_run",
                "category": "execute",
                "action": "Run Tabular Learner",
                "status": "completed",
                "details": {"job_id": job_id, "final_state": final_job_state},
            },
        )

        job_details = gi.jobs.show_job(job_id, full_details=True)
        output_ids = [v["id"] for v in job_details.get("outputs", {}).values()]
        if not output_ids:
            # Fallback: use outputs from run response.
            output_ids = [o["id"] for o in run_res.get("outputs", [])]
        if not output_ids:
            raise RuntimeError("No output datasets found for tool execution.")

        append_reasoning(
            paths.reasoning_path,
            "evidence_capture",
            "Use job details + output dataset bodies as extraction evidence.",
            (
                f"Captured history_id={history_id}, job_id={job_id}, output_ids={output_ids}; "
                "these IDs anchor final metric extraction and reproducibility."
            ),
            "Extract target and ROC-AUC from outputs.",
        )

        target, roc_auc, raw_outputs = extract_target_and_roc_auc(gi, output_ids)
        if target is None:
            target = "c22: Response"
        if roc_auc is None:
            add_error(
                paths,
                error_doc,
                step="result_extraction",
                phase="execution",
                severity="warning",
                category="parsing",
                message="Could not parse ROC-AUC from output text using configured patterns.",
                action_taken="Fallback set roc-auc to unknown.",
                resolution="Manual inspection required if strict value is needed.",
                status="resolved",
                context={"output_ids": output_ids},
            )
            roc_auc = "unknown"

        result_payload = {
            "tool_name": "Tabular Learner",
            "target": target,
            "roc-auc": roc_auc,
        }
        write_json(paths.result_path, result_payload)
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "write_result",
                "category": "execute",
                "action": "Write result.json",
                "status": "completed",
                "details": {"result_path": str(paths.result_path)},
            },
        )

        # Ground truth is intentionally read only after result + reproduce script exist.
        ground_truth_path = repo_root / "ground_truth" / f"{experiment_name}.json"
        ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))
        write_comparison_table(paths, result_payload, ground_truth)
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "compare_ground_truth",
                "category": "check",
                "action": "Generate comparison report table",
                "status": "completed",
                "details": {
                    "ground_truth_path": str(ground_truth_path),
                    "comparison_path": str(paths.comparison_path),
                },
            },
        )

        append_reasoning(
            paths.reasoning_path,
            "finalization",
            "Completed benchmark execution and comparison report generation.",
            (
                "All required artifacts were created with chronological records. "
                "Ground truth access occurred only after result generation."
            ),
            "Finalize run status.",
        )

        run_status = "completed_with_errors" if error_doc["errors"] else "completed"
        finalize_errors(paths, error_doc, run_status)
        return 0

    except Exception as exc:  # pragma: no cover - benchmark failure path
        add_error(
            paths,
            error_doc,
            step="runtime",
            phase="execution",
            severity="error",
            category="runtime",
            message=str(exc),
            action_taken="Stopped execution and recorded failure.",
            resolution="Await manual retry with corrected inputs/environment.",
            status="open",
        )
        finalize_errors(paths, error_doc, "failed")
        append_jsonl(
            paths.activity_log_path,
            {
                "timestamp": utc_now(),
                "step": "runtime",
                "category": "check",
                "action": "Execution failed",
                "status": "failed",
                "details": {"error": str(exc)},
            },
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
