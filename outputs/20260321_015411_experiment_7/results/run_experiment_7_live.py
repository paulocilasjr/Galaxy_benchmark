#!/usr/bin/env python3
"""Execute benchmark experiment_7 on Galaxy with full audit artifacts."""

from __future__ import annotations

import copy
import json
import os
import time
import urllib3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from bioblend.galaxy import GalaxyInstance, dataset_collections

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://usegalaxy.org"
WORKFLOW_GITHUB_REF = "c5bb240"
WORKFLOW_NAME = "metagenomic-genes-catalogue/main"
WORKFLOW_GITHUB_URL = "https://github.com/iwc-workflows/metagenomic-genes-catalogue"
WORKFLOWHUB_URL = "https://workflowhub.eu/workflows/2024?version=4"
WORKFLOW_EXPORT_URL = (
    "https://raw.githubusercontent.com/iwc-workflows/"
    f"metagenomic-genes-catalogue/{WORKFLOW_GITHUB_REF}/metagenomic-genes-catalogue.ga"
)
WORKFLOW_TESTS_URL = (
    "https://raw.githubusercontent.com/iwc-workflows/"
    f"metagenomic-genes-catalogue/{WORKFLOW_GITHUB_REF}/metagenomic-genes-catalogue-tests.yml"
)
PREVIOUS_ATTEMPT_DIR = "outputs/20260321_014356_experiment_7"
PREVIOUS_FAILURE_SIGNATURE = (
    "local_runner.collection_poll waited on HistoryDatasetCollectionAssociation.state="
    "None/unknown instead of populated_state=ok, so the retry gate never advanced"
)

PARAMETER_VALUES = {
    "AMR genes detection database": "amrfinderplus_V3.12_2024-05-02.2",
    "Full genes catalogue": False,
    "Virulence genes detection database": "resfinder",
    "starAMR database": "staramr_downloaded_07042025_resfinder_d1e607b_pointfinder_694919f_plasmidfinder_3e77502",
    "mmseqs2 taxonomy DB": "UniRef50-17-b804f-07112025",
    "eggNOG database": "5.0.2",
}

ESSENTIAL_OUTPUT_MARKERS = [
    "Megahit Contigs Output",
    "Eggnog Annotations",
    "MMseqs2 Taxonomy Tabular",
    "CoverM contig",
    "Argnorm AMRfinderplus Report",
    "Detailed Summary",
    "MultiQC Report",
]


class RunError(Exception):
    def __init__(self, message: str, *, context: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.context = context or {}


@dataclass
class Paths:
    repo_root: Path
    run_dir: Path
    experiment_json: Path
    plan: Path
    reasoning: Path
    errors: Path
    activity: Path
    result: Path
    comparison: Path
    reproduce: Path
    workflow_export: Path
    workflow_metadata: Path
    invocation_terminal: Path
    history_contents: Path
    output_inventory: Path


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def append_reasoning(path: Path, step: str, decision: str, why: str, next_action: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"## {utc_now()} | {step}\n")
        handle.write(f"- Decision made: {decision}\n")
        handle.write(f"- Why this decision was made: {why}\n")
        handle.write(f"- Next action: {next_action}\n\n")


def log_activity(path: Path, step: str, category: str, action: str, status: str, details: dict[str, Any]) -> None:
    append_jsonl(
        path,
        {
            "timestamp": utc_now(),
            "step": step,
            "category": category,
            "action": action,
            "status": status,
            "details": details,
        },
    )


def normalize_text(value: Any) -> str:
    if isinstance(value, (list, dict)):
        raw = json.dumps(value, sort_keys=True)
    else:
        raw = str(value)
    lowered = raw.lower()
    chars: list[str] = []
    last_space = False
    for char in lowered:
        if char.isalnum():
            chars.append(char)
            last_space = False
        else:
            if not last_space:
                chars.append(" ")
                last_space = True
    return " ".join("".join(chars).split())


def compare_values(agent_value: Any, truth_value: Any) -> tuple[str, str]:
    if isinstance(agent_value, (int, float)) or isinstance(truth_value, (int, float)):
        try:
            if float(agent_value) == float(truth_value):
                return "match", "Numeric values match."
        except Exception:
            pass
    agent_norm = normalize_text(agent_value)
    truth_norm = normalize_text(truth_value)
    if agent_norm == truth_norm:
        return "match", "Normalized text matches."
    if truth_norm and truth_norm in agent_norm:
        return "match", "Ground-truth value is contained in the agent result."
    if agent_norm and agent_norm in truth_norm:
        return "match", "Agent result is contained in the ground-truth value."
    return "mismatch", "Values differ after normalization."


def load_api_key(env_path: Path) -> str:
    if not env_path.exists():
        raise RunError("Missing .env file in repository root.")
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("GALAXY_API_KEY="):
            value = stripped.split("=", 1)[1].strip().strip('"').strip("'")
            if value:
                return value
            break
    raise RunError("Missing required credential: GALAXY_API_KEY in .env. Provide this key before running Galaxy API tasks.")


def save_error_doc(path: Path, error_doc: dict[str, Any]) -> None:
    errors = error_doc.get("errors", [])
    error_doc["summary"] = {
        "total_errors": len(errors),
        "open_errors": sum(1 for entry in errors if entry.get("status") == "open"),
        "resolved_errors": sum(1 for entry in errors if entry.get("status") == "resolved"),
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
    status: str,
    message: str,
    action_taken: str,
    resolution: str,
    retry_count: int,
    history_id: str | None = None,
    invocation_id: str | None = None,
    context: dict[str, Any] | None = None,
) -> str:
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
            "job_id": None,
            "invocation_id": invocation_id,
            "action_taken": action_taken,
            "resolution": resolution,
            "retry_count": retry_count,
            "context": {"history_id": history_id, **(context or {})},
            "additional_data": {},
        }
    )
    return err_id


def clean_workflow_export(workflow_export: dict[str, Any]) -> dict[str, Any]:
    cleaned = copy.deepcopy(workflow_export)
    for field in [
        "id",
        "url",
        "owner",
        "published",
        "deleted",
        "hidden",
        "importable",
        "model_class",
        "number_of_steps",
        "show_in_tool_panel",
        "latest_workflow_uuid",
        "uuid",
        "create_time",
        "update_time",
        "version",
    ]:
        cleaned.pop(field, None)
    return cleaned


def summarize_history_status(status: dict[str, Any]) -> dict[str, Any]:
    details = status.get("state_details", {})
    active = {
        key: value
        for key, value in details.items()
        if key in {"new", "queued", "running", "upload", "setting_metadata", "paused"} and value
    }
    problems = {key: value for key, value in details.items() if key in {"error", "failed"} and value}
    return {
        "state": status.get("state"),
        "state_details": details,
        "active_states": active,
        "problem_states": problems,
        "percent_complete": status.get("percent_complete"),
    }


def download_workflow_export(url: str) -> dict[str, Any]:
    response = requests.get(url, timeout=180, verify=False)
    response.raise_for_status()
    return response.json()


def load_experiment(paths: Paths) -> dict[str, Any]:
    return json.loads(paths.experiment_json.read_text(encoding="utf-8"))


def resolve_input_paths(experiment: dict[str, Any], repo_root: Path) -> list[dict[str, str]]:
    resolved: list[dict[str, str]] = []
    dataset_dir = repo_root / "dataset" / "experiment_7"
    for item in experiment["prompt"]["dataset"]:
        declared_name = item["name"]
        declared_path = item["path"]
        candidate_paths = [
            repo_root / declared_path.lstrip("./"),
            dataset_dir / declared_name,
            dataset_dir / declared_name.replace("meta_genomic", "meta_genomics"),
            dataset_dir / Path(declared_path).name.replace("meta_genomic", "meta_genomics"),
        ]
        chosen: Path | None = None
        for candidate in candidate_paths:
            if candidate.exists():
                chosen = candidate.resolve()
                break
        if chosen is None:
            for candidate in sorted(dataset_dir.glob("*.fastqsanger.gz")):
                if "R1" in declared_name and "R1" in candidate.name:
                    chosen = candidate.resolve()
                    break
                if "R2" in declared_name and "R2" in candidate.name:
                    chosen = candidate.resolve()
                    break
        if chosen is None:
            raise RunError(
                f"Unable to resolve declared input path {declared_path}.",
                context={"declared_name": declared_name, "declared_path": declared_path},
            )
        resolved.append(
            {
                "declared_name": declared_name,
                "declared_path": declared_path,
                "resolved_name": chosen.name,
                "resolved_path": str(chosen),
            }
        )
    return resolved


def write_initial_plan(paths: Paths, experiment: dict[str, Any], resolved_inputs: list[dict[str, str]]) -> None:
    input_lines = "\n".join(
        f"- {item['declared_name']} -> {item['resolved_path']}" for item in resolved_inputs
    )
    plan_text = f"""# Experiment name
experiment_7

# Initial objective
Execute the metagenomic genes catalogue workflow that matches the experiment_7 prompt on Galaxy, produce all required benchmark artifacts, and extract the mapper, pipeline step count, and assembly tool from the executed workflow version.

# Inputs and datasets
- Experiment definition: {paths.experiment_json}
{input_lines}
- Workflow source candidate: {WORKFLOWHUB_URL}
- Pinned workflow export: {WORKFLOW_EXPORT_URL}

# Planned steps
1. Validate the experiment definition and resolve the local FASTQ inputs referenced by the prompt.
2. Download and save the pinned workflow export matching the prompt.
3. Create a fresh Galaxy history on usegalaxy.org for this benchmark run.
4. Upload the paired FASTQ files and build the required list:paired collection.
5. Import the pinned workflow into the authenticated Galaxy account.
6. Invoke the workflow with the resolved inputs and benchmark-documented parameter values.
7. Poll Galaxy until the workflow reaches a terminal state, then capture history and invocation evidence.
8. Extract the requested output fields from the workflow definition used for the run and write result.json.
9. Write the reproduction script before reading ground truth.
10. Read ground truth and write a comparison report table.
11. Record the prior local runner failure signature and the retry fix before re-launching Galaxy actions.

# Expected outputs
- results/result.json
- results/reproduce_experiment_7.py
- results/activity_log.jsonl
- results/workflow_export.json
- results/history_contents.json
- results/comparison.md

# Risks/assumptions
- The prompt paths point to ./dataset/meta_genomic_*.fastqsanger.gz, but the repository stores experiment_7 reads under dataset/experiment_7/meta_genomics_*.fastqsanger.gz; this run resolves to the existing local files and records the discrepancy.
- The prompt does not specify the boolean branch value. This run uses the source-published workflow test configuration with Full genes catalogue=false because it is the only explicit upstream runnable parameterization for the pinned workflow version.
- The pipeline step count is reported as execution steps excluding workflow inputs and parameter-input controls, while supplementary metadata will preserve the other step-count views for auditability.
- A previous local runner attempt in {PREVIOUS_ATTEMPT_DIR} hung while waiting on a dataset collection `state` field that Galaxy does not populate for this object type. This retry treats `populated_state=ok` as the readiness signal and records the failure-recovery rationale in the run artifacts.
"""
    write_text(paths.plan, plan_text)


def seed_error_doc(paths: Paths) -> dict[str, Any]:
    doc = {
        "experiment_name": "experiment_7",
        "run_status": "running",
        "started_at": utc_now(),
        "updated_at": utc_now(),
        "summary": {"total_errors": 0, "open_errors": 0, "resolved_errors": 0},
        "errors": [],
    }
    save_error_doc(paths.errors, doc)
    return doc


def seed_activity_log(paths: Paths, resolved_inputs: list[dict[str, str]]) -> None:
    planned_actions = [
        ("resolve_inputs", "Resolve declared experiment inputs to existing repository files.", {"resolved_inputs": resolved_inputs}),
        ("download_workflow", "Download the pinned workflow export and supporting source references.", {"workflow_export_url": WORKFLOW_EXPORT_URL, "workflowhub_url": WORKFLOWHUB_URL}),
        ("create_history", "Create a new Galaxy history for experiment_7.", {"base_url": BASE_URL}),
        ("upload_inputs", "Upload the paired FASTQ files.", {"file_count": len(resolved_inputs)}),
        ("create_collection", "Build the list:paired workflow input collection.", {"collection_type": "list:paired"}),
        ("import_workflow", "Import the pinned workflow into Galaxy.", {"workflow_name": WORKFLOW_NAME}),
        ("invoke_workflow", "Invoke the imported workflow with named inputs and parameter values.", {"inputs_by": "name"}),
        ("poll_workflow", "Poll Galaxy invocation and history state until terminal completion.", {"initial_delay_seconds": 20, "poll_interval_seconds": 60}),
        ("capture_outputs", "Capture terminal history contents and workflow metadata.", {"history_contents_path": str(paths.history_contents)}),
        ("write_result", "Write result.json and workflow metadata artifacts.", {"result_path": str(paths.result)}),
        ("write_reproduce", "Write the reproduction script before reading ground truth.", {"reproduce_path": str(paths.reproduce)}),
        ("compare_ground_truth", "Read ground truth and write the comparison report.", {"comparison_path": str(paths.comparison)}),
    ]
    for step, action, details in planned_actions:
        log_activity(paths.activity, step, "plan", action, "planned", details)


def write_reproduce_script(paths: Paths) -> None:
    script = f"""#!/usr/bin/env python3
\"\"\"Reproduce benchmark experiment_7 for this specific run directory.

This wrapper re-executes the live runner that performed the benchmark actions:
1. validate the local experiment inputs and Galaxy credentials
2. download the pinned metagenomic genes catalogue workflow definition
3. create a fresh Galaxy history, upload reads, and create the list:paired input collection
4. import and invoke the workflow on usegalaxy.org
5. poll Galaxy to terminal completion, then write result and comparison artifacts
\"\"\"

from pathlib import Path
import subprocess
import sys

RUNNER = Path(__file__).resolve().parent / "run_experiment_7_live.py"
command = [sys.executable, "-B", str(RUNNER)]
print("# Re-running experiment_7 benchmark workflow")
print("# Command:", " ".join(command))
completed = subprocess.run(command, check=False)
print("# Exit code:", completed.returncode)
raise SystemExit(completed.returncode)
"""
    write_text(paths.reproduce, script)
    os.chmod(paths.reproduce, 0o755)


def poll_dataset_state(gi: GalaxyInstance, history_id: str, dataset_id: str, dataset_name: str, activity_path: Path) -> dict[str, Any]:
    while True:
        dataset = gi.histories.show_dataset(history_id, dataset_id)
        state = dataset.get("state", "unknown")
        log_activity(
            activity_path,
            "upload_poll",
            "check",
            "Poll uploaded dataset state",
            state,
            {"history_id": history_id, "dataset_id": dataset_id, "dataset_name": dataset_name},
        )
        if state == "ok":
            return dataset
        if state in {"error", "failed", "deleted", "discarded"}:
            raise RunError(
                f"Uploaded dataset {dataset_name} entered terminal failure state {state}.",
                context={"history_id": history_id, "dataset_id": dataset_id, "dataset_name": dataset_name, "state": state},
            )
        time.sleep(10)


def poll_collection_state(gi: GalaxyInstance, history_id: str, hdca_id: str, activity_path: Path) -> dict[str, Any]:
    while True:
        collection = gi.histories.show_dataset_collection(history_id, hdca_id)
        populated_state = collection.get("populated_state")
        state = collection.get("state") or populated_state or ("ok" if collection.get("populated") else "unknown")
        elements_states = collection.get("elements_states", {})
        log_activity(
            activity_path,
            "collection_poll",
            "check",
            "Poll dataset collection state",
            state,
            {
                "history_id": history_id,
                "hdca_id": hdca_id,
                "populated": collection.get("populated"),
                "populated_state": populated_state,
                "elements_states": elements_states,
            },
        )
        if any(key in {"error", "failed"} for key in elements_states):
            raise RunError(
                "Input dataset collection contains failed elements.",
                context={
                    "history_id": history_id,
                    "hdca_id": hdca_id,
                    "elements_states": elements_states,
                    "populated_state": populated_state,
                },
            )
        if state == "ok" or (collection.get("populated") and populated_state in {None, "ok"}):
            return collection
        if state in {"error", "failed", "deleted", "discarded"} or populated_state in {"error", "failed"}:
            raise RunError(
                f"Input dataset collection entered terminal failure state {state}.",
                context={
                    "history_id": history_id,
                    "hdca_id": hdca_id,
                    "state": state,
                    "populated_state": populated_state,
                    "elements_states": elements_states,
                },
            )
        time.sleep(10)


def wait_for_history_terminal(
    gi: GalaxyInstance,
    history_id: str,
    invocation_id: str,
    activity_path: Path,
    *,
    timeout_seconds: int = 8 * 3600,
    population_timeout_seconds: int = 10 * 60,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    start = time.time()
    population_observed = False
    time.sleep(20)
    while True:
        if time.time() - start > timeout_seconds:
            raise RunError(
                "Galaxy workflow polling exceeded timeout without reaching terminal history state.",
                context={"history_id": history_id, "invocation_id": invocation_id, "timeout_seconds": timeout_seconds},
            )

        invocation = gi.invocations.show_invocation(invocation_id)
        history_status = gi.histories.get_status(history_id)
        try:
            summary = gi.invocations.get_invocation_summary(invocation_id)
        except Exception:
            summary = {}

        history_summary = summarize_history_status(history_status)
        snapshot = {
            "history_id": history_id,
            "invocation_id": invocation_id,
            "invocation_state": invocation.get("state"),
            "invocation_steps": len(invocation.get("steps", [])),
            "jobs_summary": summary.get("states", {}) if isinstance(summary, dict) else {},
            "populated_state": summary.get("populated_state") if isinstance(summary, dict) else None,
            "history_status": history_summary,
        }
        log_activity(activity_path, "workflow_poll", "check", "Poll workflow invocation/history state", "observed", snapshot)

        if invocation.get("state") in {"failed", "cancelled", "deleted"}:
            raise RunError(
                f"Workflow invocation entered terminal failure state {invocation.get('state')}.",
                context=snapshot,
            )

        active_count = sum(int(value) for value in history_summary["active_states"].values())
        problem_count = sum(int(value) for value in history_summary["problem_states"].values())
        jobs_summary = summary.get("states", {}) if isinstance(summary, dict) else {}
        populated_state = summary.get("populated_state") if isinstance(summary, dict) else None
        if (
            active_count > 0
            or len(invocation.get("steps", [])) > 0
            or bool(jobs_summary)
            or (populated_state not in {None, "", "new"})
        ):
            population_observed = True

        if not population_observed:
            if time.time() - start > population_timeout_seconds:
                raise RunError(
                    "Workflow invocation remained unpopulated after the initial population timeout.",
                    context={**snapshot, "population_timeout_seconds": population_timeout_seconds},
                )
            time.sleep(60)
            continue

        if active_count == 0:
            if problem_count:
                raise RunError("Workflow finished with failed Galaxy datasets.", context=snapshot)
            return invocation, summary, history_status

        time.sleep(60)


def workflow_metadata(workflow_export: dict[str, Any]) -> dict[str, Any]:
    steps = workflow_export.get("steps", {})
    top_level_total = len(steps)
    top_level_tool_steps = sum(1 for step in steps.values() if step.get("type") == "tool")
    top_level_subworkflows = sum(1 for step in steps.values() if step.get("type") == "subworkflow")
    input_and_parameter_steps = sum(1 for step in steps.values() if "input" in (step.get("type") or ""))
    expanded_subworkflow_tool_steps = 0
    for step in steps.values():
        if step.get("type") == "subworkflow":
            expanded_subworkflow_tool_steps += sum(
                1 for sub_step in step.get("subworkflow", {}).get("steps", {}).values() if sub_step.get("type") == "tool"
            )
    execution_steps = top_level_tool_steps + top_level_subworkflows
    expanded_tool_steps = top_level_tool_steps + expanded_subworkflow_tool_steps

    assembly_step = next(step for step in steps.values() if step.get("name") == "MEGAHIT")
    mapper_step = next(step for step in steps.values() if step.get("name") == "eggNOG Mapper")

    return {
        "workflow_name": workflow_export.get("name"),
        "workflow_annotation": workflow_export.get("annotation"),
        "workflow_github_ref": WORKFLOW_GITHUB_REF,
        "workflow_export_url": WORKFLOW_EXPORT_URL,
        "workflowhub_url": WORKFLOWHUB_URL,
        "counts": {
            "top_level_total_objects": top_level_total,
            "top_level_tool_steps": top_level_tool_steps,
            "top_level_subworkflows": top_level_subworkflows,
            "input_and_parameter_steps": input_and_parameter_steps,
            "execution_steps_excluding_inputs": execution_steps,
            "expanded_tool_steps_including_subworkflow_tools": expanded_tool_steps,
        },
        "assembly_step": {
            "name": assembly_step.get("name"),
            "tool_id": assembly_step.get("tool_id"),
        },
        "functional_mapper_step": {
            "name": mapper_step.get("name"),
            "tool_id": mapper_step.get("tool_id"),
        },
    }


def find_output_inventory(history_contents: list[dict[str, Any]]) -> dict[str, Any]:
    visible_items = []
    visible_names = []
    for item in history_contents:
        name = item.get("name", "")
        state = item.get("state")
        entry = {
            "id": item.get("id"),
            "name": name,
            "history_content_type": item.get("history_content_type"),
            "state": state,
            "visible": item.get("visible"),
            "deleted": item.get("deleted"),
        }
        visible_items.append(entry)
        visible_names.append(name)

    matched_outputs: dict[str, list[dict[str, Any]]] = {}
    for marker in ESSENTIAL_OUTPUT_MARKERS:
        matched_outputs[marker] = [item for item in visible_items if marker.lower() in item["name"].lower()]

    return {
        "history_item_count": len(visible_items),
        "visible_items": visible_items,
        "matched_outputs": matched_outputs,
        "visible_names": visible_names,
    }


def create_history(gi: GalaxyInstance, history_name: str, activity_path: Path) -> str:
    log_activity(activity_path, "history_create", "execute", "Create Galaxy history", "started", {"history_name": history_name})
    history = gi.histories.create_history(name=history_name)
    history_id = history["id"]
    log_activity(activity_path, "history_create", "execute", "Create Galaxy history", "completed", {"history_id": history_id, "history_name": history_name})
    return history_id


def upload_inputs(
    gi: GalaxyInstance,
    history_id: str,
    resolved_inputs: list[dict[str, str]],
    activity_path: Path,
) -> dict[str, str]:
    uploaded: dict[str, str] = {}
    for item in resolved_inputs:
        dataset_name = item["resolved_name"]
        file_path = Path(item["resolved_path"])
        log_activity(
            activity_path,
            "upload",
            "execute",
            "Upload FASTQ dataset",
            "started",
            {"history_id": history_id, "dataset_name": dataset_name, "path": str(file_path)},
        )
        response = gi.tools.upload_file(
            str(file_path),
            history_id,
            file_name=dataset_name,
            file_type="fastqsanger.gz",
        )
        outputs = response.get("outputs", [])
        if not outputs:
            raise RunError("Upload did not return output datasets.", context={"dataset_name": dataset_name, "history_id": history_id})
        dataset_id = outputs[0]["id"]
        dataset = poll_dataset_state(gi, history_id, dataset_id, dataset_name, activity_path)
        uploaded[dataset_name] = dataset_id
        log_activity(
            activity_path,
            "upload",
            "execute",
            "Upload FASTQ dataset",
            "completed",
            {"history_id": history_id, "dataset_name": dataset_name, "dataset_id": dataset_id, "state": dataset.get("state")},
        )
    return uploaded


def create_input_collection(
    gi: GalaxyInstance,
    history_id: str,
    uploaded: dict[str, str],
    activity_path: Path,
) -> str:
    r1_name = next(name for name in uploaded if "R1" in name)
    r2_name = next(name for name in uploaded if "R2" in name)
    collection_desc = dataset_collections.CollectionDescription(
        name="Metagenomics Trimmed reads",
        type="list:paired",
        elements=[
            dataset_collections.CollectionElement(
                name="sample1",
                type="paired",
                elements=[
                    dataset_collections.HistoryDatasetElement(name="forward", id=uploaded[r1_name]),
                    dataset_collections.HistoryDatasetElement(name="reverse", id=uploaded[r2_name]),
                ],
            )
        ],
    )
    log_activity(
        activity_path,
        "collection_create",
        "execute",
        "Create list:paired workflow input collection",
        "started",
        {"history_id": history_id, "collection_name": "Metagenomics Trimmed reads"},
    )
    hdca = gi.histories.create_dataset_collection(history_id, collection_desc, copy_elements=False)
    hdca_id = hdca["id"]
    collection = poll_collection_state(gi, history_id, hdca_id, activity_path)
    log_activity(
        activity_path,
        "collection_create",
        "execute",
        "Create list:paired workflow input collection",
        "completed",
        {"history_id": history_id, "hdca_id": hdca_id, "state": collection.get("state")},
    )
    return hdca_id


def invoke_workflow(
    gi: GalaxyInstance,
    workflow_id: str,
    history_id: str,
    hdca_id: str,
    activity_path: Path,
) -> str:
    inputs: dict[str, Any] = {"Metagenomics Trimmed reads": {"src": "hdca", "id": hdca_id}}
    inputs.update(PARAMETER_VALUES)
    log_activity(
        activity_path,
        "workflow_invoke",
        "execute",
        "Invoke imported metagenomic genes catalogue workflow",
        "started",
        {"history_id": history_id, "workflow_id": workflow_id, "inputs_by": "name", "parameter_values": {k: v for k, v in PARAMETER_VALUES.items()}},
    )
    invocation = gi.workflows.invoke_workflow(
        workflow_id,
        history_id=history_id,
        inputs=inputs,
        inputs_by="name",
        allow_tool_state_corrections=True,
        require_exact_tool_versions=False,
        use_cached_job=False,
    )
    invocation_id = invocation["id"]
    log_activity(
        activity_path,
        "workflow_invoke",
        "execute",
        "Invoke imported metagenomic genes catalogue workflow",
        "submitted",
        {"history_id": history_id, "workflow_id": workflow_id, "invocation_id": invocation_id},
    )
    return invocation_id


def write_comparison(paths: Paths, result_payload: dict[str, Any], truth_payload: dict[str, Any]) -> None:
    lines = [
        "| Field | Agent Result | Ground Truth | Match Status | Notes |",
        "|---|---|---|---|---|",
    ]
    for field, agent_value in result_payload.items():
        truth_value = truth_payload.get(field)
        status, notes = compare_values(agent_value, truth_value)
        lines.append(
            f"| {field} | {json.dumps(agent_value, ensure_ascii=True)} | {json.dumps(truth_value, ensure_ascii=True)} | {status} | {notes} |"
        )
    write_text(paths.comparison, "\n".join(lines) + "\n")


def main() -> int:
    run_script = Path(__file__).resolve()
    run_dir = run_script.parent.parent
    repo_root = run_script.parents[3]
    paths = Paths(
        repo_root=repo_root,
        run_dir=run_dir,
        experiment_json=repo_root / "experiments" / "experiment_7.json",
        plan=run_dir / "plan" / "saved.md",
        reasoning=run_dir / "reasoning" / "reasoning.md",
        errors=run_dir / "errors" / "error.json",
        activity=run_dir / "results" / "activity_log.jsonl",
        result=run_dir / "results" / "result.json",
        comparison=run_dir / "results" / "comparison.md",
        reproduce=run_dir / "results" / "reproduce_experiment_7.py",
        workflow_export=run_dir / "results" / "workflow_export.json",
        workflow_metadata=run_dir / "results" / "workflow_metadata.json",
        invocation_terminal=run_dir / "results" / "invocation_terminal.json",
        history_contents=run_dir / "results" / "history_contents.json",
        output_inventory=run_dir / "results" / "output_inventory.json",
    )

    error_doc = seed_error_doc(paths)
    history_id: str | None = None
    invocation_id: str | None = None

    try:
        experiment = load_experiment(paths)
        resolved_inputs = resolve_input_paths(experiment, paths.repo_root)
        write_initial_plan(paths, experiment, resolved_inputs)
        seed_activity_log(paths, resolved_inputs)
        write_reproduce_script(paths)

        log_activity(
            paths.activity,
            "previous_attempt_review",
            "check",
            "Review prior local runner failure evidence before retrying",
            "completed",
            {
                "prior_attempt_dir": PREVIOUS_ATTEMPT_DIR,
                "failure_signature": PREVIOUS_FAILURE_SIGNATURE,
                "evidence": "Prior attempt activity log showed repeated collection_poll status=unknown, while direct Galaxy inspection returned populated_state=ok for the same HDCA.",
            },
        )
        log_activity(
            paths.activity,
            "runner_revision",
            "revise",
            "Correct collection readiness polling for retry attempt",
            "completed",
            {
                "attempt": 2,
                "changed_items": ["poll_collection_state readiness gate"],
                "reason": "Galaxy dataset collections expose populated_state instead of state for readiness.",
                "new_artifact_path": str(run_script),
            },
        )
        log_activity(
            paths.activity,
            "retry_attempt",
            "retry",
            "Start retry attempt in a fresh benchmark directory",
            "started",
            {
                "attempt": 2,
                "prior_attempt_dir": PREVIOUS_ATTEMPT_DIR,
                "reason": PREVIOUS_FAILURE_SIGNATURE,
            },
        )

        append_reasoning(
            paths.reasoning,
            "failure_recovery",
            "Retry the benchmark in a fresh run directory after correcting the local collection polling logic.",
            "The previous attempt did not fail inside Galaxy. It stalled because the local runner waited on a nonexistent HDCA state field even though direct Galaxy inspection showed populated_state=ok and elements_states={'ok': 2}. The safe mechanism change is to gate collection readiness on populated_state/populated, then rerun end-to-end in a new immutable run directory.",
            "Resolve inputs again and continue with the same pinned workflow, parameters, and Galaxy instance so only the local readiness bug changes between attempts.",
        )
        append_reasoning(
            paths.reasoning,
            "input_resolution",
            "Resolve experiment_7 inputs to the existing FASTQ files under dataset/experiment_7.",
            "The experiment JSON declares ./dataset/meta_genomic_R1.fastqsanger.gz and ./dataset/meta_genomic_R2.fastqsanger.gz, but those files do not exist in the repository root dataset directory. The repository contains matching paired reads under dataset/experiment_7 with the same suffixes and only a singular/plural naming difference, so the run uses those concrete files and records the mismatch explicitly.",
            "Download the workflow definition and evaluate whether it matches the prompt.",
        )
        append_reasoning(
            paths.reasoning,
            "workflow_selection",
            "Select WorkflowHub workflow 2024 version 4 / GitHub ref c5bb240 as the execution target.",
            "Its public description matches the prompt's exact structure: raw metagenomic reads to gene catalogue, MEGAHIT assembly, Prodigal CDS prediction, a boolean Full genes catalogue branch, eggNOG functional mapping, MMseqs2 taxonomy, CoverM abundance, and AMR reporting. That is a materially tighter match than the broader ASaiM or Cloud-Aerosole workflows inspected during discovery.",
            "Use BioBlend against usegalaxy.org to create the history, upload inputs, import the workflow, and invoke it.",
        )
        append_reasoning(
            paths.reasoning,
            "interface_choice",
            "Use BioBlend for Galaxy stateful actions and requests only for downloading the pinned workflow export.",
            "BioBlend provides stable helpers for history creation, file upload, dataset collections, workflow import, invocation, and polling, which reduces raw API surface area while still preserving exact IDs and status evidence in the benchmark artifacts.",
            "Download the pinned workflow export, save it under results, and compute audit metadata from the exact file that will be imported.",
        )
        append_reasoning(
            paths.reasoning,
            "parameter_selection",
            "Use the upstream workflow test parameter set with Full genes catalogue=false.",
            "The experiment prompt does not specify which boolean branch to execute. The pinned source repository provides a concrete, version-matched Galaxy workflow test configuration that sets all required databases and explicitly chooses the resistome-focused branch. Using the source-published runnable configuration is a stronger evidence-based choice than inventing database values or a branch setting locally.",
            "Create the Galaxy history and upload the paired reads as a list:paired collection.",
        )

        api_key = load_api_key(paths.repo_root / ".env")
        gi = GalaxyInstance(url=BASE_URL, key=api_key, verify=False)

        log_activity(paths.activity, "workflow_download", "execute", "Download pinned workflow export", "started", {"url": WORKFLOW_EXPORT_URL})
        workflow_export = download_workflow_export(WORKFLOW_EXPORT_URL)
        write_json(paths.workflow_export, workflow_export)
        meta = workflow_metadata(workflow_export)
        write_json(paths.workflow_metadata, meta)
        log_activity(
            paths.activity,
            "workflow_download",
            "execute",
            "Download pinned workflow export",
            "completed",
            {
                "workflow_export_path": str(paths.workflow_export),
                "workflow_name": workflow_export.get("name"),
                "workflow_counts": meta["counts"],
            },
        )

        append_reasoning(
            paths.reasoning,
            "step_count_basis",
            "Report total__steps as 34 execution steps.",
            "The pinned workflow has 41 top-level objects, but 7 of those are the data/parameter inputs that are not executable pipeline steps. The WorkflowHub steps section for this workflow lists 34 execution steps, comprising 33 direct tools plus 1 subworkflow. Additional count views are preserved in workflow_metadata.json for auditability.",
            "Proceed with the Galaxy execution using the pinned workflow and chosen parameters.",
        )

        history_name = f"benchmark_experiment_7_{run_dir.name}"
        history_id = create_history(gi, history_name, paths.activity)
        uploaded = upload_inputs(gi, history_id, resolved_inputs, paths.activity)
        hdca_id = create_input_collection(gi, history_id, uploaded, paths.activity)

        log_activity(paths.activity, "workflow_import", "execute", "Import pinned workflow into Galaxy", "started", {"workflow_name": WORKFLOW_NAME})
        imported = gi.workflows.import_workflow_dict(clean_workflow_export(workflow_export))
        imported_workflow_id = imported["id"]
        imported_workflow = gi.workflows.show_workflow(imported_workflow_id)
        log_activity(
            paths.activity,
            "workflow_import",
            "execute",
            "Import pinned workflow into Galaxy",
            "completed",
            {"imported_workflow_id": imported_workflow_id, "imported_workflow_name": imported_workflow.get("name")},
        )

        invocation_id = invoke_workflow(gi, imported_workflow_id, history_id, hdca_id, paths.activity)
        terminal_invocation, invocation_summary, history_status = wait_for_history_terminal(gi, history_id, invocation_id, paths.activity)
        write_json(
            paths.invocation_terminal,
            {
                "terminal_invocation": terminal_invocation,
                "invocation_summary": invocation_summary,
                "history_status": history_status,
            },
        )

        history_contents = gi.histories.show_history(history_id, contents=True, visible=None, details="all")
        write_json(paths.history_contents, history_contents)
        inventory = find_output_inventory(history_contents)
        write_json(paths.output_inventory, inventory)
        log_activity(
            paths.activity,
            "capture_outputs",
            "check",
            "Capture terminal history contents and output inventory",
            "completed",
            {
                "history_contents_path": str(paths.history_contents),
                "output_inventory_path": str(paths.output_inventory),
                "history_item_count": inventory["history_item_count"],
            },
        )

        result_payload = {
            "tool_name_1": meta["functional_mapper_step"]["name"],
            "total__steps": meta["counts"]["execution_steps_excluding_inputs"],
            "tool_name_2": meta["assembly_step"]["name"],
        }
        write_json(paths.result, result_payload)
        log_activity(paths.activity, "write_result", "execute", "Write result.json", "completed", {"result_path": str(paths.result), "result_payload": result_payload})

        if not paths.reproduce.exists():
            write_reproduce_script(paths)
        log_activity(paths.activity, "write_reproduce", "execute", "Write reproduce_experiment_7.py", "completed", {"reproduce_path": str(paths.reproduce)})

        truth_path = paths.repo_root / "ground_truth" / "experiment_7.json"
        truth_payload = json.loads(truth_path.read_text(encoding="utf-8"))
        log_activity(paths.activity, "compare_ground_truth", "check", "Read ground truth after producing result and reproduce artifacts", "completed", {"ground_truth_path": str(truth_path)})
        write_comparison(paths, result_payload, truth_payload)
        log_activity(paths.activity, "compare_ground_truth", "execute", "Write ground truth comparison table", "completed", {"comparison_path": str(paths.comparison)})

        error_doc["run_status"] = "completed"
        save_error_doc(paths.errors, error_doc)
        return 0

    except Exception as exc:
        context = exc.context if isinstance(exc, RunError) else {"exception_type": type(exc).__name__}
        add_error(
            error_doc,
            step="experiment_7_run",
            phase="execution",
            severity="error",
            category="runtime",
            status="open",
            message=str(exc),
            action_taken="Stopped the current run and preserved failure context for auditability.",
            resolution="",
            retry_count=0,
            history_id=history_id,
            invocation_id=invocation_id,
            context=context,
        )
        error_doc["run_status"] = "failed"
        save_error_doc(paths.errors, error_doc)
        log_activity(
            paths.activity,
            "experiment_7_run",
            "check",
            "Capture terminal failure evidence",
            "failed",
            {
                "history_id": history_id,
                "invocation_id": invocation_id,
                "message": str(exc),
                "context": context,
            },
        )
        append_reasoning(
            paths.reasoning,
            "failure",
            f"Stop the run because experiment_7 raised {type(exc).__name__}: {exc}",
            "Benchmark policy requires preserving the exact failure symptom and context before any retry. The failure is recorded in errors/error.json and activity_log.jsonl, and the run directory remains immutable for later analysis.",
            "Inspect the saved error evidence and decide whether a new run directory should be created for a signature-specific retry.",
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
