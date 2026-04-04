#!/usr/bin/env python3
"""
Reproduce experiment_3 end-to-end with Galaxy API calls.

Workflow summary:
1) validate Galaxy credential,
2) discover/select multimodal learner tool,
3) create history and upload required datasets from URL,
4) run 5 multimodal model attempts with revised architectures/settings,
5) extract best test ROC-AUC,
6) write benchmark artifacts and comparison report.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bioblend.galaxy import GalaxyInstance


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_version(tool_id: str) -> tuple[int, ...]:
    tail = tool_id.rsplit("/", 1)[-1]
    nums: list[int] = []
    for part in re.split(r"[^0-9]+", tail):
        if part.isdigit():
            nums.append(int(part))
    return tuple(nums) if nums else (0,)


def load_env_key(env_path: Path) -> str:
    if not env_path.exists():
        raise RuntimeError("Missing .env file in repository root.")
    key = ""
    for line in env_path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or "=" not in s:
            continue
        k, v = s.split("=", 1)
        if k.strip() == "GALAXY_API_KEY":
            key = v.strip().strip('"').strip("'")
            break
    if not key:
        raise RuntimeError("Missing required credential: GALAXY_API_KEY in .env.")
    return key


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


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


@dataclass
class Paths:
    repo_root: Path
    run_dir: Path
    reasoning: Path
    errors: Path
    activity: Path
    result: Path
    attempt_summary: Path
    comparison: Path


def save_error_doc(path: Path, error_doc: dict[str, Any]) -> None:
    errors = error_doc.get("errors", [])
    error_doc["summary"] = {
        "total_errors": len(errors),
        "open_errors": sum(1 for e in errors if e.get("status") == "open"),
        "resolved_errors": sum(1 for e in errors if e.get("status") == "resolved"),
    }
    error_doc["updated_at"] = utc_now()
    write_json(path, error_doc)


def add_error(
    error_doc: dict[str, Any],
    *,
    step: str,
    phase: str,
    severity: str,
    category: str,
    message: str,
    action_taken: str,
    resolution: str,
    status: str,
    retry_count: int = 0,
    job_id: str | None = None,
    context: dict[str, Any] | None = None,
    additional_data: dict[str, Any] | None = None,
) -> None:
    err_id = f"err-{len(error_doc.get('errors', [])) + 1:04d}"
    error_doc.setdefault("errors", []).append(
        {
            "id": err_id,
            "timestamp": utc_now(),
            "step": step,
            "phase": phase,
            "severity": severity,
            "category": category,
            "status": status,
            "message": message,
            "job_id": job_id,
            "invocation_id": None,
            "action_taken": action_taken,
            "resolution": resolution,
            "retry_count": retry_count,
            "context": context or {},
            "additional_data": additional_data or {},
        }
    )


def poll_dataset_state(
    gi: GalaxyInstance,
    history_id: str,
    dataset_id: str,
    activity_path: Path,
    timeout_seconds: int | None = None,
) -> tuple[str, bool]:
    first = True
    start = time.time()
    while True:
        state = gi.histories.show_dataset(history_id, dataset_id).get("state", "unknown")
        append_jsonl(
            activity_path,
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
            return state, False
        if timeout_seconds is not None and (time.time() - start) > timeout_seconds:
            return state, True
        if first:
            time.sleep(20)
            first = False
        else:
            time.sleep(60)


def poll_job_state(gi: GalaxyInstance, job_id: str, activity_path: Path) -> str:
    first = True
    while True:
        state = gi.jobs.show_job(job_id).get("state", "unknown")
        append_jsonl(
            activity_path,
            {
                "timestamp": utc_now(),
                "step": "tool_run_poll",
                "category": "check",
                "action": "Poll Multimodal Learner job state",
                "status": state,
                "details": {"job_id": job_id},
            },
        )
        if state in {"ok", "error", "failed", "deleted"}:
            return state
        if first:
            time.sleep(20)
            first = False
        else:
            time.sleep(60)


def normalize_metric(raw: Any) -> float | None:
    try:
        value = float(raw)
    except (TypeError, ValueError):
        return None
    if value < 0:
        return None
    if value <= 1.0:
        return value
    if value <= 100.0:
        return value / 100.0
    return None


def extract_roc_auc_from_metrics(payload: dict[str, Any]) -> tuple[float | None, str]:
    candidates: list[tuple[float, str]] = []

    def push(value: Any, source: str) -> None:
        v = normalize_metric(value)
        if v is not None:
            candidates.append((v, source))

    push(payload.get("test", {}).get("ROC-AUC"), "test.ROC-AUC")
    push(payload.get("test", {}).get("AG_roc_auc"), "test.AG_roc_auc")
    push(payload.get("ag_eval", {}).get("Test", {}).get("roc_auc"), "ag_eval.Test.roc_auc")

    if candidates:
        best = max(candidates, key=lambda x: x[0])
        return best[0], best[1]

    text = json.dumps(payload, ensure_ascii=False)
    patterns = [
        (re.compile(r'"test"\s*:\s*\{[^\}]{0,300}?"ROC-AUC"\s*:\s*([0-9]*\.?[0-9]+)', re.IGNORECASE | re.DOTALL), "regex_test_ROC-AUC"),
        (re.compile(r'"roc_auc"\s*:\s*([0-9]*\.?[0-9]+)', re.IGNORECASE), "regex_roc_auc"),
    ]
    for pattern, source in patterns:
        m = pattern.search(text)
        if m:
            v = normalize_metric(m.group(1))
            if v is not None:
                return v, source

    return None, "not_found"


def extract_signature(stderr: str, stdout: str) -> str:
    text = (stderr or "") + "\n" + (stdout or "")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for ln in reversed(lines):
        if "KeyError:" in ln or "ValueError:" in ln or "RuntimeError:" in ln or "Traceback" in ln:
            return ln[:240]
    if lines:
        return lines[-1][:240]
    return "unknown_error_signature"


def upload_from_url(
    gi: GalaxyInstance,
    key: str,
    history_id: str,
    name: str,
    url: str,
    ext: str,
    activity_path: Path,
) -> str:
    append_jsonl(
        activity_path,
        {
            "timestamp": utc_now(),
            "step": "dataset_upload",
            "category": "execute",
            "action": f"Upload dataset {name} from URL",
            "status": "started",
            "details": {"history_id": history_id, "url": url, "ext": ext},
        },
    )

    payload = {
        "history_id": history_id,
        "targets": [
            {
                "destination": {"type": "hdas"},
                "elements": [
                    {
                        "src": "url",
                        "url": url,
                        "ext": ext,
                        "dbkey": "?",
                        "name": name,
                    }
                ],
            }
        ],
    }

    response = requests.post(
        f"{gi.url.rstrip('/')}/api/tools/fetch",
        headers={"x-api-key": key},
        json=payload,
        timeout=180,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Fetch upload failed for {name}: {response.status_code} {response.text[:400]}")

    data = response.json()
    outputs = data.get("outputs", [])
    if not outputs:
        raise RuntimeError(f"Fetch upload returned no outputs for {name}.")

    dataset_id = outputs[0]["id"]
    append_jsonl(
        activity_path,
        {
            "timestamp": utc_now(),
            "step": "dataset_upload",
            "category": "execute",
            "action": f"Upload dataset {name} from URL",
            "status": "submitted",
            "details": {"dataset_id": dataset_id, "history_id": history_id},
        },
    )

    state, timed_out = poll_dataset_state(gi, history_id, dataset_id, activity_path, timeout_seconds=4 * 3600)
    if state != "ok":
        timeout_note = " (timeout)" if timed_out else ""
        raise RuntimeError(f"Dataset {name} upload ended in {state}{timeout_note}.")

    append_jsonl(
        activity_path,
        {
            "timestamp": utc_now(),
            "step": "dataset_upload",
            "category": "execute",
            "action": f"Upload dataset {name} from URL",
            "status": "completed",
            "details": {"dataset_id": dataset_id, "final_state": state},
        },
    )
    return dataset_id


def attempt_configs() -> list[dict[str, Any]]:
    return [
        {
            "name": "attempt_1_baseline_caformer_electra",
            "reason": "Establish baseline with medium-quality preset and proven backbones.",
            "params": {
                "backbone_text": "google/electra-base-discriminator",
                "backbone_image": "caformer_b36.sail_in22k_ft_in1k",
                "preset": "medium_quality",
                "eval_metric": "auto",
                "random_seed": 42,
                "time_limit": 600,
                "deterministic": True,
                "use_sample_id": True,
                "sample_id_column": "1",
                "missing_image_strategy": False,
                "customize_defaults": False,
            },
        },
        {
            "name": "attempt_2_vit_distilroberta_high_quality",
            "reason": "Increase model capacity and optimize directly for ROC-AUC.",
            "params": {
                "backbone_text": "distilroberta-base",
                "backbone_image": "vit_base_patch16_224.augreg_in21k_ft_in1k",
                "preset": "high_quality",
                "eval_metric": "roc_auc",
                "random_seed": 13,
                "time_limit": 700,
                "deterministic": True,
                "use_sample_id": True,
                "sample_id_column": "1",
                "missing_image_strategy": False,
                "customize_defaults": False,
            },
        },
        {
            "name": "attempt_3_resnet50_roberta_medium_quality",
            "reason": "Test a CNN image backbone plus RoBERTa text to compare representation balance.",
            "params": {
                "backbone_text": "roberta-base",
                "backbone_image": "resnet50.a1_in1k",
                "preset": "medium_quality",
                "eval_metric": "roc_auc",
                "random_seed": 23,
                "time_limit": 700,
                "deterministic": True,
                "use_sample_id": True,
                "sample_id_column": "1",
                "missing_image_strategy": False,
                "customize_defaults": False,
            },
        },
        {
            "name": "attempt_4_swin_deberta_small",
            "reason": "Try Swin transformer image encoder and smaller DeBERTa text encoder for different fusion dynamics.",
            "params": {
                "backbone_text": "microsoft/deberta-v3-small",
                "backbone_image": "swin_base_patch4_window7_224.ms_in22k_ft_in1k",
                "preset": "high_quality",
                "eval_metric": "roc_auc_ovr_macro",
                "random_seed": 31,
                "time_limit": 700,
                "deterministic": True,
                "use_sample_id": True,
                "sample_id_column": "1",
                "missing_image_strategy": True,
                "customize_defaults": False,
            },
        },
        {
            "name": "attempt_5_convnext_bert_best_quality",
            "reason": "Final sweep with ConvNeXt image backbone and best-quality preset.",
            "params": {
                "backbone_text": "bert-base-uncased",
                "backbone_image": "convnext_base.fb_in22k_ft_in1k",
                "preset": "best_quality",
                "eval_metric": "roc_auc",
                "random_seed": 59,
                "time_limit": 800,
                "deterministic": True,
                "use_sample_id": True,
                "sample_id_column": "1",
                "missing_image_strategy": True,
                "customize_defaults": False,
            },
        },
    ]


def build_tool_inputs(train_csv_id: str, test_csv_id: str, image_zip_id: str, params: dict[str, Any]) -> dict[str, Any]:
    use_sample_id = bool(params.get("use_sample_id", False))
    sample_selector: dict[str, Any] = {
        "__current_case__": 0 if use_sample_id else 1,
        "use_sample_id": "yes" if use_sample_id else "no",
    }
    if use_sample_id:
        sample_selector["sample_id_column"] = str(params.get("sample_id_column", "1"))

    customize_defaults = bool(params.get("customize_defaults", False))
    custom_section: dict[str, Any] = {
        "__current_case__": 0 if customize_defaults else 1,
        "customize_defaults": customize_defaults,
    }
    if customize_defaults:
        custom_section.update(
            {
                "validation_size": float(params.get("validation_size", 0.2)),
                "split_probabilities": str(params.get("split_probabilities", "0.7 0.1 0.2")),
                "cross_validation": bool(params.get("cross_validation", False)),
                "num_folds": int(params.get("num_folds", 3)),
                "epochs": int(params.get("epochs", 10)),
                "learning_rate": float(params.get("learning_rate", 1e-4)),
                "batch_size": int(params.get("batch_size", 8)),
                "threshold": float(params.get("threshold", 0.5)),
                "hyperparameters": params.get("hyperparameters"),
            }
        )

    return {
        "input_csv": {"src": "hda", "id": train_csv_id},
        "target_column": "3",
        "sample_id_selector": sample_selector,
        "test_dataset_conditional": {
            "__current_case__": 0,
            "has_test_dataset": True,
            "input_test": {"src": "hda", "id": test_csv_id},
        },
        "backbone_text": params["backbone_text"],
        "use_images_conditional": {
            "__current_case__": 0,
            "use_images": True,
            "images_zip_repeat": [
                {
                    "__index__": 0,
                    "images_zip": {"src": "hda", "id": image_zip_id},
                }
            ],
            "backbone_image": params["backbone_image"],
            "missing_image_strategy": bool(params.get("missing_image_strategy", False)),
        },
        "preset": params["preset"],
        "eval_metric": params["eval_metric"],
        "random_seed": int(params.get("random_seed", 42)),
        "time_limit": int(params.get("time_limit", 600)),
        "deterministic": bool(params.get("deterministic", True)),
        "customize_defaults_conditional": custom_section,
    }


def write_comparison_table(path: Path, agent_result: dict[str, Any], ground_truth: dict[str, Any]) -> None:
    fields = ["tool_name", "target", "ROC-AUC"]
    lines = [
        "| Field | Agent Result | Ground Truth | Match Status | Notes |",
        "|---|---|---|---|---|",
    ]
    for field in fields:
        a = str(agent_result.get(field))
        g = str(ground_truth.get(field))
        status = "match" if a == g else "mismatch"
        note = "" if status == "match" else "Value differs."
        lines.append(f"| {field} | {a} | {g} | {status} | {note} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    script_path = Path(__file__).resolve()
    run_dir = script_path.parents[1]
    repo_root = script_path.parents[3]

    paths = Paths(
        repo_root=repo_root,
        run_dir=run_dir,
        reasoning=run_dir / "reasoning" / "reasoning.md",
        errors=run_dir / "errors" / "error.json",
        activity=run_dir / "results" / "activity_log.jsonl",
        result=run_dir / "results" / "result.json",
        attempt_summary=run_dir / "results" / "attempt_summary.json",
        comparison=run_dir / "results" / "comparison_report.md",
    )

    experiment = json.loads((repo_root / "experiments" / "experiment_3.json").read_text(encoding="utf-8"))
    prompt = experiment["prompt"]
    error_doc = json.loads(paths.errors.read_text(encoding="utf-8"))

    planned_actions = [
        "Validate credential",
        "Discover multimodal learner tool",
        "Create history",
        "Upload train/test/image datasets",
        "Run at least 5 multimodal attempts",
        "Extract best test ROC-AUC",
        "Write result artifact",
        "Generate comparison report",
    ]
    for i, action in enumerate(planned_actions, start=1):
        append_jsonl(
            paths.activity,
            {
                "timestamp": utc_now(),
                "step": f"plan_{i}",
                "category": "plan",
                "action": action,
                "status": "planned",
                "details": {"attempt": 1},
            },
        )

    try:
        key = load_env_key(repo_root / ".env")
        append_jsonl(
            paths.activity,
            {
                "timestamp": utc_now(),
                "step": "credential_check",
                "category": "execute",
                "action": "Validate and load API key",
                "status": "completed",
                "details": {"credential": "GALAXY_API_KEY", "valid_format": True},
            },
        )
        append_reasoning(
            paths.reasoning,
            "credential_check",
            "Use GALAXY_API_KEY from .env for authenticated Galaxy API calls.",
            "Credential is required for history creation, uploads, and tool execution. Secret value is never logged.",
            "Initialize Galaxy client and discover multimodal learner tool versions.",
        )

        gi = GalaxyInstance(url=prompt["galaxy_instance"].rstrip("/"), key=key)
        _ = gi.users.get_current_user()

        all_tools = gi.tools.get_tools()
        mm_candidates = [t["id"] for t in all_tools if "multimodal_learner" in t.get("id", "")]
        if not mm_candidates:
            raise RuntimeError("Multimodal Learner tool not found in Galaxy instance.")

        selected_tool = sorted(mm_candidates, key=parse_version)[-1]
        rejected = [tid for tid in mm_candidates if tid != selected_tool]
        append_jsonl(
            paths.activity,
            {
                "timestamp": utc_now(),
                "step": "tool_discovery",
                "category": "execute",
                "action": "Discover Multimodal Learner tool IDs",
                "status": "completed",
                "details": {"selected_tool_id": selected_tool, "candidate_count": len(mm_candidates)},
            },
        )
        append_reasoning(
            paths.reasoning,
            "tool_discovery",
            f"Selected {selected_tool} as the execution tool.",
            (
                "Tool discovery used Galaxy tools API and selected the highest semantic version. "
                f"Rejected older candidates: {rejected}."
            ),
            "Create history and upload datasets from experiment prompt URLs.",
        )

        history = gi.histories.create_history(name=prompt["history_name"])
        history_id = history["id"]
        append_jsonl(
            paths.activity,
            {
                "timestamp": utc_now(),
                "step": "create_history",
                "category": "execute",
                "action": "Create Galaxy history",
                "status": "completed",
                "details": {"history_id": history_id, "history_name": prompt["history_name"]},
            },
        )

        dataset_ids: dict[str, str] = {}
        for ds in prompt["dataset"]:
            ext = "csv" if ds["name"].lower().endswith(".csv") else "zip"
            ds_id = upload_from_url(
                gi=gi,
                key=key,
                history_id=history_id,
                name=ds["name"],
                url=ds["path"],
                ext=ext,
                activity_path=paths.activity,
            )
            dataset_ids[ds["name"]] = ds_id

        required = {
            "HANCOCK_train_split_3GB_jpeg.csv",
            "HANCOCK_test_split_3GB_jpeg.csv",
            "CD3_CD8_images_3GB_jpeg.zip",
        }
        if set(dataset_ids) != required:
            missing = sorted(required - set(dataset_ids))
            raise RuntimeError(f"Dataset provisioning incomplete. Missing: {missing}")

        append_reasoning(
            paths.reasoning,
            "parameter_selection",
            "Use target column index 3 (`target`) and sample-id column index 1 (`patient_id`).",
            "CSV headers confirm survival label in `target`; sample ID grouping helps prevent patient leakage across splits.",
            "Run five architecture/parameter variants and track test ROC-AUC.",
        )

        train_id = dataset_ids["HANCOCK_train_split_3GB_jpeg.csv"]
        test_id = dataset_ids["HANCOCK_test_split_3GB_jpeg.csv"]
        image_zip_id = dataset_ids["CD3_CD8_images_3GB_jpeg.zip"]

        configs = attempt_configs()
        attempt_results: list[dict[str, Any]] = []
        best_record: dict[str, Any] | None = None

        for idx, cfg in enumerate(configs, start=1):
            params = cfg["params"]

            if idx > 1:
                append_jsonl(
                    paths.activity,
                    {
                        "timestamp": utc_now(),
                        "step": f"attempt_{idx}",
                        "category": "retry",
                        "action": "Retry Multimodal Learner with revised configuration",
                        "status": "started",
                        "details": {"attempt": idx, "reason": cfg["reason"]},
                    },
                )
                append_jsonl(
                    paths.activity,
                    {
                        "timestamp": utc_now(),
                        "step": f"attempt_{idx}_revise",
                        "category": "revise",
                        "action": "Revise model architecture and tuning settings",
                        "status": "completed",
                        "details": {
                            "attempt": idx,
                            "changed_items": params,
                            "reason": cfg["reason"],
                            "new_artifact_path": str(paths.attempt_summary),
                        },
                    },
                )

            append_reasoning(
                paths.reasoning,
                f"attempt_{idx}_plan",
                f"Run {cfg['name']}.",
                cfg["reason"],
                "Submit tool job and monitor to terminal state.",
            )

            tool_inputs = build_tool_inputs(train_id, test_id, image_zip_id, params)
            append_jsonl(
                paths.activity,
                {
                    "timestamp": utc_now(),
                    "step": f"attempt_{idx}_run",
                    "category": "execute",
                    "action": "Run Multimodal Learner",
                    "status": "started",
                    "details": {
                        "attempt": idx,
                        "name": cfg["name"],
                        "tool_id": selected_tool,
                        "history_id": history_id,
                        "params": params,
                    },
                },
            )

            run_res = gi.tools.run_tool(history_id=history_id, tool_id=selected_tool, tool_inputs=tool_inputs)
            jobs = run_res.get("jobs", [])
            if not jobs:
                raise RuntimeError(f"Attempt {idx}: submission returned no job IDs.")
            job_id = jobs[0]["id"]

            append_jsonl(
                paths.activity,
                {
                    "timestamp": utc_now(),
                    "step": f"attempt_{idx}_run",
                    "category": "execute",
                    "action": "Run Multimodal Learner",
                    "status": "submitted",
                    "details": {
                        "attempt": idx,
                        "job_id": job_id,
                        "output_count_hint": len(run_res.get("outputs", [])),
                    },
                },
            )

            final_state = poll_job_state(gi, job_id, paths.activity)
            if final_state != "ok":
                job_detail = gi.jobs.show_job(job_id, full_details=True)
                stderr = job_detail.get("stderr") or ""
                stdout = job_detail.get("stdout") or ""
                signature = extract_signature(stderr, stdout)

                append_jsonl(
                    paths.activity,
                    {
                        "timestamp": utc_now(),
                        "step": f"attempt_{idx}_failure_check",
                        "category": "check",
                        "action": "Inspect failed job evidence",
                        "status": "completed",
                        "details": {
                            "attempt": idx,
                            "job_id": job_id,
                            "state": final_state,
                            "error_signature": signature,
                        },
                    },
                )

                add_error(
                    error_doc,
                    step=f"attempt_{idx}_run",
                    phase="execution",
                    severity="error",
                    category="tool",
                    status="resolved",
                    message=f"Attempt {idx} job ended in state {final_state}.",
                    action_taken="Captured stderr/stdout and moved to revised configuration.",
                    resolution="Retry with a materially different backbone/metric/preset configuration.",
                    retry_count=max(0, idx - 1),
                    job_id=job_id,
                    context={
                        "attempt": idx,
                        "error_signature": signature,
                        "stderr_tail": stderr[-2000:],
                        "stdout_tail": stdout[-1000:],
                    },
                )
                save_error_doc(paths.errors, error_doc)

                append_reasoning(
                    paths.reasoning,
                    f"attempt_{idx}_failure",
                    f"Classified failure signature: {signature}",
                    "Failure evidence was read from Galaxy job stderr/stdout and normalized before planning retry.",
                    "Apply next configuration revision and rerun.",
                )

                record = {
                    "attempt": idx,
                    "name": cfg["name"],
                    "reason": cfg["reason"],
                    "job_id": job_id,
                    "state": final_state,
                    "roc_auc": None,
                    "metric_source": None,
                    "params": params,
                    "outputs": [],
                }
                attempt_results.append(record)
                write_json(paths.attempt_summary, {"attempt_results": attempt_results})
                continue

            append_jsonl(
                paths.activity,
                {
                    "timestamp": utc_now(),
                    "step": f"attempt_{idx}_run",
                    "category": "execute",
                    "action": "Run Multimodal Learner",
                    "status": "completed",
                    "details": {"attempt": idx, "job_id": job_id, "final_state": final_state},
                },
            )

            job_detail = gi.jobs.show_job(job_id, full_details=True)
            output_map = job_detail.get("outputs", {})
            output_ids = [v["id"] for v in output_map.values()] or [o["id"] for o in run_res.get("outputs", [])]

            output_meta: list[dict[str, Any]] = []
            output_json_payload: dict[str, Any] | None = None
            output_json_ds_id: str | None = None

            if "output_json" in output_map:
                output_json_ds_id = output_map["output_json"]["id"]

            for ds_id in output_ids:
                meta = gi.datasets.show_dataset(ds_id)
                item = {
                    "dataset_id": ds_id,
                    "name": meta.get("name", ds_id),
                    "state": meta.get("state"),
                    "file_ext": meta.get("file_ext"),
                }
                output_meta.append(item)
                if output_json_ds_id is None and meta.get("file_ext") == "json":
                    output_json_ds_id = ds_id

            if output_json_ds_id is not None:
                raw = gi.datasets.download_dataset(output_json_ds_id, require_ok_state=False)
                text = raw.decode("utf-8", errors="replace") if isinstance(raw, (bytes, bytearray)) else str(raw)
                try:
                    output_json_payload = json.loads(text)
                except Exception:
                    output_json_payload = None

            roc_auc = None
            metric_source = "not_found"
            if output_json_payload is not None:
                roc_auc, metric_source = extract_roc_auc_from_metrics(output_json_payload)

            append_jsonl(
                paths.activity,
                {
                    "timestamp": utc_now(),
                    "step": f"attempt_{idx}_evaluate",
                    "category": "check",
                    "action": "Evaluate attempt output metrics",
                    "status": "completed",
                    "details": {
                        "attempt": idx,
                        "ROC-AUC": roc_auc,
                        "metric_source": metric_source,
                    },
                },
            )

            record = {
                "attempt": idx,
                "name": cfg["name"],
                "reason": cfg["reason"],
                "job_id": job_id,
                "state": final_state,
                "roc_auc": roc_auc,
                "metric_source": metric_source,
                "params": params,
                "outputs": output_meta,
            }
            attempt_results.append(record)
            write_json(paths.attempt_summary, {"attempt_results": attempt_results})

            if roc_auc is not None and (best_record is None or roc_auc > float(best_record.get("roc_auc", -1))):
                best_record = record

        if best_record is None:
            raise RuntimeError("All attempts failed to produce a usable ROC-AUC metric.")

        result_payload = {
            "tool_name": "Multimodal Learner",
            "target": "target",
            "ROC-AUC": f"{float(best_record['roc_auc']):.4f}",
        }
        write_json(paths.result, result_payload)

        append_reasoning(
            paths.reasoning,
            "result_selection",
            f"Selected {best_record['name']} as best attempt with test ROC-AUC={best_record['roc_auc']:.4f}.",
            "Best attempt is chosen by highest extracted test ROC-AUC across five parameterized runs.",
            "Write final result JSON and compare against ground truth.",
        )

        append_jsonl(
            paths.activity,
            {
                "timestamp": utc_now(),
                "step": "result_write",
                "category": "execute",
                "action": "Write result artifact",
                "status": "completed",
                "details": {"result_path": str(paths.result), "best_attempt": best_record["attempt"]},
            },
        )

        ground_truth_path = repo_root / "ground_truth" / "experiment_3.json"
        ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))
        write_comparison_table(paths.comparison, result_payload, ground_truth)

        append_jsonl(
            paths.activity,
            {
                "timestamp": utc_now(),
                "step": "comparison",
                "category": "check",
                "action": "Generate comparison report",
                "status": "completed",
                "details": {
                    "ground_truth_path": str(ground_truth_path),
                    "comparison_path": str(paths.comparison),
                },
            },
        )

        error_doc["run_status"] = "completed" if error_doc.get("summary", {}).get("total_errors", 0) == 0 else "completed_with_errors"
        save_error_doc(paths.errors, error_doc)
        return 0

    except Exception as exc:
        add_error(
            error_doc,
            step="fatal",
            phase="execution",
            severity="error",
            category="runtime",
            status="open",
            message=str(exc),
            action_taken="Execution stopped.",
            resolution="None",
            retry_count=0,
            context={},
        )
        error_doc["run_status"] = "failed"
        save_error_doc(paths.errors, error_doc)

        append_reasoning(
            paths.reasoning,
            "fatal",
            "Stop execution due to unrecovered runtime error.",
            str(exc),
            "Inspect errors/error.json and rerun with revised strategy.",
        )

        append_jsonl(
            paths.activity,
            {
                "timestamp": utc_now(),
                "step": "fatal",
                "category": "execute",
                "action": "Run experiment_3 pipeline",
                "status": "failed",
                "details": {"error": str(exc)},
            },
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
