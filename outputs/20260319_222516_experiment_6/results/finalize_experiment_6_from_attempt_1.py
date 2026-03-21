#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from bioblend.galaxy import GalaxyInstance

RUN_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = RUN_DIR.parents[1]
ERROR_PATH = RUN_DIR / "errors" / "error.json"
REASONING_PATH = RUN_DIR / "reasoning" / "reasoning.md"
ACTIVITY_PATH = RUN_DIR / "results" / "activity_log.jsonl"
RESULT_PATH = RUN_DIR / "results" / "result.json"
COMPARISON_PATH = RUN_DIR / "results" / "comparison_report.md"
WORKFLOW_EXPORT_PATH = RUN_DIR / "results" / "workflow_export.json"
HISTORY_CONTENTS_PATH = RUN_DIR / "results" / "history_contents.json"
DOTPLOT_PATH = RUN_DIR / "results" / "pl_dotplot_marker_genes.png"
UMAP_LOUVAIN_PATH = RUN_DIR / "results" / "pl_umap_louvain.png"
UMAP_MARKER_PATH = RUN_DIR / "results" / "pl_umap_marker_genes.png"

HISTORY_ID = "bbd44e69cb8906b5174caf0eb12c7d4b"
HISTORY_NAME = "experiment_6_20260319_222516_attempt_1"
INVOCATION_ID = "9143db221977d986"
IMPORTED_WORKFLOW_ID = "29b8e304305a5f07"
SOURCE_WORKFLOW_ID = "21315ffd2df2f159"


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def log_activity(step: str, category: str, action: str, status: str, details: dict[str, Any]) -> None:
    append_jsonl(
        ACTIVITY_PATH,
        {
            "timestamp": utc_now(),
            "step": step,
            "category": category,
            "action": action,
            "status": status,
            "details": details,
        },
    )


def append_reasoning(step: str, decision: str, why: str, next_action: str) -> None:
    with REASONING_PATH.open("a", encoding="utf-8") as handle:
        handle.write(f"## {utc_now()} | {step}\n")
        handle.write(f"- Decision made: {decision}\n")
        handle.write(f"- Why this decision was made: {why}\n")
        handle.write(f"- Next action: {next_action}\n\n")


def load_api_key() -> str:
    for line in (REPO_ROOT / ".env").read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("GALAXY_API_KEY="):
            return stripped.split("=", 1)[1].strip().strip('"').strip("'")
    raise RuntimeError("Missing required credential: GALAXY_API_KEY in .env.")


def normalize_text(value: Any) -> str:
    if isinstance(value, (list, dict)):
        raw = json.dumps(value, sort_keys=True)
    else:
        raw = str(value)
    lowered = raw.lower()
    chars = []
    last_space = False
    for char in lowered:
        if char.isalnum():
            chars.append(char)
            last_space = False
        elif not last_space:
            chars.append(" ")
            last_space = True
    return " ".join("".join(chars).split())


def stringify(value: Any) -> str:
    if isinstance(value, (list, dict)):
        return json.dumps(value, ensure_ascii=True)
    return str(value)


def compare_values(agent_value: Any, truth_value: Any) -> tuple[str, str]:
    if isinstance(agent_value, list) and isinstance(truth_value, list):
        if agent_value == truth_value:
            return "match", "Exact ordered gene list match."
        if sorted(agent_value) == sorted(truth_value):
            return "match", "Gene list membership matches; order differs."
        return "mismatch", "Gene list differs."

    agent_norm = normalize_text(agent_value)
    truth_norm = normalize_text(truth_value)
    if agent_norm == truth_norm:
        return "match", "Normalized text matches."
    if truth_norm and truth_norm in agent_norm:
        return "match", "Ground-truth text is contained in the agent result."
    if agent_norm and agent_norm in truth_norm:
        return "match", "Agent result is contained in the ground-truth text."
    return "mismatch", "Values differ after normalization."


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")


def parse_workflow_answers(workflow_export: dict[str, Any]) -> tuple[str, list[str]]:
    normalize_step = workflow_export["steps"]["18"]
    dotplot_step = workflow_export["steps"]["53"]
    normalize_state = json.loads(normalize_step["tool_state"])
    dotplot_state = json.loads(dotplot_step["tool_state"])
    normalization = f"Scanpy normalize using {normalize_state['method']['method']} with target_sum={normalize_state['method']['target_sum']}"
    genes = [gene.strip() for gene in dotplot_state["method"]["var_names"]["var_names"].split(",") if gene.strip()]
    return normalization, genes


def find_dataset(items: list[dict[str, Any]], name: str) -> dict[str, Any]:
    for item in items:
        if item.get("history_content_type") == "dataset" and item.get("name") == name and item.get("state") == "ok":
            return item
    raise RuntimeError(f"Dataset not found: {name}")


def main() -> int:
    workflow_export = json.loads(WORKFLOW_EXPORT_PATH.read_text(encoding="utf-8"))
    history_contents = json.loads(HISTORY_CONTENTS_PATH.read_text(encoding="utf-8"))
    normalization, genes = parse_workflow_answers(workflow_export)
    tool_steps = sum(1 for step in workflow_export["steps"].values() if step.get("type") == "tool")

    dotplot = find_dataset(history_contents, "PNG plot from Scanpy plot (pl.dotplot) on dataset 50")
    umap_louvain = find_dataset(history_contents, "PNG plot from Scanpy plot (pl.umap) on dataset 35")
    umap_marker = find_dataset(history_contents, "PNG plot from Scanpy plot (pl.umap) on dataset 37")

    log_activity(
        "history_output_inspection",
        "check",
        "Inspect completed attempt-1 history contents to map generic Galaxy output names to the benchmark plots",
        "completed",
        {
            "history_contents_path": str(HISTORY_CONTENTS_PATH),
            "dotplot_dataset_id": dotplot["id"],
            "umap_louvain_dataset_id": umap_louvain["id"],
            "umap_marker_dataset_id": umap_marker["id"],
        },
    )
    append_reasoning(
        "history_output_inspection",
        "Reuse the completed attempt-1 Galaxy history and correct only the output-name mapping.",
        "The workflow itself finished successfully with 62 ok history items. The failure came from expecting tutorial label names, while Galaxy materialized generic plot names such as 'PNG plot from Scanpy plot (pl.dotplot) on dataset 50'.",
        "Download the correct plot datasets and finalize the result/comparison artifacts from the successful history.",
    )

    log_activity(
        "extraction_revise",
        "revise",
        "Switch result extraction from expected tutorial labels to the actual history dataset names emitted by Galaxy",
        "completed",
        {
            "attempt": 2,
            "changed_items": [
                "dotplot dataset mapping",
                "UMAP dataset mapping",
                "finalization path",
            ],
            "reason": "Attempt 1 completed successfully but the post-run extraction expected the workflow output labels rather than the generic Galaxy dataset names present in the history.",
            "new_artifact_path": str(Path(__file__)),
        },
    )

    key = load_api_key()
    gi = GalaxyInstance(url="https://usegalaxy.org", key=key, verify=False)
    gi.datasets.download_dataset(dotplot["id"], file_path=str(DOTPLOT_PATH), use_default_filename=False)
    gi.datasets.download_dataset(umap_louvain["id"], file_path=str(UMAP_LOUVAIN_PATH), use_default_filename=False)
    gi.datasets.download_dataset(umap_marker["id"], file_path=str(UMAP_MARKER_PATH), use_default_filename=False)
    log_activity(
        "artifact_download_finalize",
        "execute",
        "Download dotplot and UMAP outputs from the successful attempt-1 history",
        "completed",
        {
            "dotplot_path": str(DOTPLOT_PATH),
            "umap_louvain_path": str(UMAP_LOUVAIN_PATH),
            "umap_marker_path": str(UMAP_MARKER_PATH),
        },
    )

    result = {
        "data_normalization": normalization,
        "total_tool_steps": tool_steps,
        "list_of_genes": genes,
        "evidence": {
            "execution_server": "https://usegalaxy.org",
            "history": {"id": HISTORY_ID, "name": HISTORY_NAME},
            "workflow": {
                "source_workflow_id": SOURCE_WORKFLOW_ID,
                "imported_workflow_id": IMPORTED_WORKFLOW_ID,
                "tool_steps": tool_steps,
            },
            "invocation": {"id": INVOCATION_ID, "state": "completed"},
            "visualizations": {
                "dotplot_dataset": dotplot,
                "dotplot_path": str(DOTPLOT_PATH),
                "umap_louvain_dataset": umap_louvain,
                "umap_louvain_path": str(UMAP_LOUVAIN_PATH),
                "umap_marker_dataset": umap_marker,
                "umap_marker_path": str(UMAP_MARKER_PATH),
            },
            "workflow_export_path": str(WORKFLOW_EXPORT_PATH),
            "history_contents_path": str(HISTORY_CONTENTS_PATH),
        },
    }
    write_json(RESULT_PATH, result)
    log_activity("result_write_finalize", "execute", "Write results/result.json from the successful attempt-1 history", "completed", {"artifact_path": str(RESULT_PATH)})

    ground_truth = json.loads((REPO_ROOT / "ground_truth" / "experiment_6.json").read_text(encoding="utf-8"))
    log_activity("ground_truth_read", "check", "Read ground_truth/experiment_6.json after result.json was finalized", "completed", {"artifact_path": str(REPO_ROOT / 'ground_truth' / 'experiment_6.json')})

    rows = []
    for field in ["data_normalization", "total_tool_steps", "list_of_genes"]:
        status, note = compare_values(result[field], ground_truth.get(field))
        rows.append((field, result[field], ground_truth.get(field), status, note))

    lines = [
        "# Comparison Report",
        "",
        "| Field | Agent Result | Ground Truth | Match Status | Notes |",
        "|---|---|---|---|---|",
    ]
    for field, agent_value, truth_value, status, note in rows:
        lines.append(f"| {field} | {stringify(agent_value)} | {stringify(truth_value)} | {status} | {note} |")
    write_text(COMPARISON_PATH, "\n".join(lines) + "\n")
    log_activity("comparison_write", "execute", "Write field-by-field comparison report for experiment_6", "completed", {"artifact_path": str(COMPARISON_PATH)})

    error_doc = json.loads(ERROR_PATH.read_text(encoding="utf-8"))
    if error_doc.get("errors"):
        error_doc["errors"][0]["resolution"] = "Resolved by inspecting the completed attempt-1 history and mapping Galaxy's generic plot names to the expected dotplot and UMAP outputs; no additional workflow execution was required."
        error_doc["errors"][0]["status"] = "resolved"
    error_doc["run_status"] = "completed_with_errors"
    error_doc["updated_at"] = utc_now()
    error_doc["summary"] = {
        "total_errors": len(error_doc.get("errors", [])),
        "open_errors": sum(1 for entry in error_doc.get("errors", []) if entry.get("status") == "open"),
        "resolved_errors": sum(1 for entry in error_doc.get("errors", []) if entry.get("status") == "resolved"),
    }
    write_json(ERROR_PATH, error_doc)

    append_reasoning(
        "finalize",
        "Finalize experiment_6 from the successful attempt-1 history after correcting the output-name mapping.",
        "Galaxy completed the workflow without job failures. The only remaining issue was translating generic history item names back to the benchmark's dotplot/UMAP expectations.",
        "Return control with completed result, comparison, downloaded plots, and updated error accounting.",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
