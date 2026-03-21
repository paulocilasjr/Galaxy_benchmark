#!/usr/bin/env python3
import json
import re
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path

import requests
from bioblend.galaxy import GalaxyInstance
from bioblend.galaxy.dataset_collections import (
    CollectionDescription,
    CollectionElement,
    HistoryDatasetElement,
)


BASE_URL = "https://usegalaxy.org"
PUBLISHED_WORKFLOW_ID = "50c22b81c8fb9cae"
PUBLISHED_WORKFLOW_NAME = "RNA-Seq Analysis: Paired-End Read Processing and Quantification (release v1.3)"
RUN_DIR = Path(__file__).resolve().parents[1]
PLAN_PATH = RUN_DIR / "plan" / "saved.md"
REASONING_PATH = RUN_DIR / "reasoning" / "reasoning.md"
ERROR_PATH = RUN_DIR / "errors" / "error.json"
ACTIVITY_PATH = RUN_DIR / "results" / "activity_log.jsonl"
STATE_PATH = RUN_DIR / "results" / "execution_state.json"
HISTORY_CONTENTS_PATH = RUN_DIR / "results" / "history_contents.json"
WORKFLOW_EXPORT_PATH = RUN_DIR / "results" / "workflow_export.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def append_activity(step: str, category: str, action: str, status: str, details: dict) -> None:
    row = {
        "timestamp": utc_now(),
        "step": step,
        "category": category,
        "action": action,
        "status": status,
        "details": details,
    }
    with ACTIVITY_PATH.open("a", encoding="ascii") as handle:
        handle.write(json.dumps(row) + "\n")


def append_reasoning(step: str, decision: str, why: str, next_action: str) -> None:
    entry = (
        f"\n- Timestamp: {utc_now()}\n"
        f"  - Step reference: {step}\n"
        f"  - Decision made: {decision}\n"
        f"  - Why this decision was made: {why}\n"
        f"  - Next action: {next_action}\n"
    )
    with REASONING_PATH.open("a", encoding="ascii") as handle:
        handle.write(entry)


def load_error_doc() -> dict:
    return json.loads(ERROR_PATH.read_text(encoding="ascii"))


def save_error_doc(doc: dict) -> None:
    doc["updated_at"] = utc_now()
    ERROR_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="ascii")


def add_error(step: str, message: str, category: str, context: dict, resolution: str = "") -> str:
    doc = load_error_doc()
    error_id = f"err-{len(doc['errors']) + 1:04d}"
    doc["errors"].append(
        {
            "id": error_id,
            "timestamp": utc_now(),
            "step": step,
            "phase": "execution",
            "severity": "error",
            "category": category,
            "status": "open",
            "message": message,
            "job_id": context.get("job_id"),
            "invocation_id": context.get("invocation_id"),
            "action_taken": "Execution stopped and failure evidence was captured.",
            "resolution": resolution,
            "retry_count": 0,
            "context": context,
            "additional_data": {},
        }
    )
    doc["summary"]["total_errors"] = len(doc["errors"])
    doc["summary"]["open_errors"] = sum(1 for err in doc["errors"] if err["status"] == "open")
    doc["summary"]["resolved_errors"] = sum(1 for err in doc["errors"] if err["status"] == "resolved")
    doc["run_status"] = "running"
    save_error_doc(doc)
    return error_id


def resolve_error(error_id: str, resolution: str) -> None:
    doc = load_error_doc()
    for err in doc["errors"]:
        if err["id"] == error_id:
            err["status"] = "resolved"
            err["resolution"] = resolution
            break
    doc["summary"]["total_errors"] = len(doc["errors"])
    doc["summary"]["open_errors"] = sum(1 for err in doc["errors"] if err["status"] == "open")
    doc["summary"]["resolved_errors"] = sum(1 for err in doc["errors"] if err["status"] == "resolved")
    save_error_doc(doc)


def finalize_status(status: str) -> None:
    doc = load_error_doc()
    doc["run_status"] = status
    doc["summary"]["total_errors"] = len(doc["errors"])
    doc["summary"]["open_errors"] = sum(1 for err in doc["errors"] if err["status"] == "open")
    doc["summary"]["resolved_errors"] = sum(1 for err in doc["errors"] if err["status"] == "resolved")
    save_error_doc(doc)


def load_api_key() -> str:
    env_text = Path(".env").read_text(encoding="utf-8")
    match = re.search(r'^GALAXY_API_KEY="?([^"\n]+)"?$', env_text, re.MULTILINE)
    if not match or not match.group(1).strip():
        raise RuntimeError(
            "Missing required credential: GALAXY_API_KEY in .env. Provide this key before running Galaxy API tasks."
        )
    return match.group(1).strip()


def make_session(api_key: str) -> requests.Session:
    session = requests.Session()
    session.headers.update({"x-api-key": api_key})
    return session


def fetch_url(
    session: requests.Session,
    history_id: str,
    name: str,
    url: str,
    ext: str,
    dbkey: str | None = None,
) -> dict:
    element = {"src": "url", "url": url, "name": name, "ext": ext}
    if dbkey is not None:
        element["dbkey"] = dbkey
    payload = {
        "history_id": history_id,
        "targets": [{"destination": {"type": "hdas"}, "elements": [element]}],
    }
    response = session.post(f"{BASE_URL}/api/tools/fetch", json=payload, timeout=180)
    response.raise_for_status()
    return response.json()


def wait_for_dataset(
    gi: GalaxyInstance,
    dataset_id: str,
    dataset_name: str,
    initial_sleep: int = 20,
    poll_sleep: int = 20,
) -> dict:
    time.sleep(initial_sleep)
    while True:
        dataset = gi.datasets.show_dataset(dataset_id)
        state = dataset.get("state")
        append_activity(
            "dataset_poll",
            "check",
            f"Poll dataset state for {dataset_name}",
            "observed",
            {"dataset_id": dataset_id, "dataset_name": dataset_name, "state": state},
        )
        if state == "ok":
            return dataset
        if state in {"error", "failed", "discarded", "deleted"}:
            raise RuntimeError(f"Dataset {dataset_name} entered terminal failure state {state}.")
        time.sleep(poll_sleep)


def summarize_history_status(status: dict) -> dict:
    details = status.get("state_details", {})
    active_states = {
        key: value
        for key, value in details.items()
        if key in {"new", "queued", "running", "upload", "setting_metadata", "paused"} and value
    }
    terminal_problem_states = {
        key: value for key, value in details.items() if key in {"error", "failed", "paused"} and value
    }
    return {
        "state": status.get("state"),
        "state_details": details,
        "active_states": active_states,
        "terminal_problem_states": terminal_problem_states,
        "percent_complete": status.get("percent_complete"),
    }


def wait_for_history_terminal(
    gi: GalaxyInstance,
    history_id: str,
    invocation_id: str,
    first_sleep: int = 25,
    poll_sleep: int = 60,
) -> tuple[dict, dict, dict]:
    time.sleep(first_sleep)
    while True:
        history_status = gi.histories.get_status(history_id)
        invocation = gi.invocations.show_invocation(invocation_id)
        summary = gi.invocations.get_invocation_summary(invocation_id)
        snapshot = {
            "invocation_state": invocation.get("state"),
            "invocation_steps": len(invocation.get("steps", [])),
            "jobs_summary": summary.get("states", {}),
            "populated_state": summary.get("populated_state"),
            "history_status": summarize_history_status(history_status),
        }
        append_activity(
            "workflow_poll",
            "check",
            "Poll workflow invocation and history status",
            "observed",
            snapshot,
        )
        details = history_status.get("state_details", {})
        active = sum(details.get(key, 0) for key in ["new", "queued", "running", "upload", "setting_metadata"])
        paused = details.get("paused", 0)
        problems = details.get("error", 0) + details.get("failed", 0) + paused
        if active == 0:
            if problems > 0 or invocation.get("state") in {"failed", "cancelled"}:
                raise RuntimeError(
                    "Workflow reached a terminal failure state. "
                    f"invocation_state={invocation.get('state')} jobs_summary={summary.get('states', {})} "
                    f"history_state_details={details}"
                )
            return history_status, invocation, summary
        time.sleep(poll_sleep)


def main() -> int:
    api_key = load_api_key()
    gi = GalaxyInstance(url=BASE_URL, key=api_key)
    session = make_session(api_key)

    append_reasoning(
        "execution-01",
        "Use BioBlend plus direct Galaxy fetch API requests for authenticated execution.",
        "BioBlend provides stable helpers for histories, workflows, invocations, and collections, while direct POSTs to /api/tools/fetch are the simplest way to import remote URLs without writing local input files.",
        "Create a fresh history and import the published RNA-seq workflow.",
    )

    run_stamp = RUN_DIR.name.split("_experiment_5")[0]
    history_name = f"experiment_5_{run_stamp}"
    append_activity(
        "history_create",
        "execute",
        "Create a fresh Galaxy history for experiment_5",
        "started",
        {"history_name": history_name},
    )
    history = gi.histories.create_history(name=history_name)
    history_id = history["id"]
    append_activity(
        "history_create",
        "execute",
        "Create a fresh Galaxy history for experiment_5",
        "completed",
        {"history_id": history_id, "history_name": history_name},
    )

    append_activity(
        "workflow_import",
        "execute",
        "Import the published IWC RNA-seq workflow into the authenticated Galaxy account",
        "started",
        {"published_workflow_id": PUBLISHED_WORKFLOW_ID},
    )
    imported_workflow = gi.workflows.import_shared_workflow(PUBLISHED_WORKFLOW_ID)
    workflow_id = imported_workflow["id"]
    append_activity(
        "workflow_import",
        "execute",
        "Import the published IWC RNA-seq workflow into the authenticated Galaxy account",
        "completed",
        {"workflow_id": workflow_id, "workflow_name": imported_workflow.get("name")},
    )

    workflow_export = requests.get(f"{BASE_URL}/api/workflows/{PUBLISHED_WORKFLOW_ID}/download", timeout=180).json()
    WORKFLOW_EXPORT_PATH.write_text(json.dumps(workflow_export, indent=2) + "\n", encoding="utf-8")

    inputs_to_fetch = [
        (
            "SRR5085167_forward.fastqsanger.gz",
            "https://zenodo.org/records/13987631/files/SRR5085167_forward.fastqsanger.gz",
            "fastqsanger.gz",
            None,
        ),
        (
            "SRR5085167_reverse.fastqsanger.gz",
            "https://zenodo.org/records/13987631/files/SRR5085167_reverse.fastqsanger.gz",
            "fastqsanger.gz",
            None,
        ),
        (
            "Saccharomyces_cerevisiae.R64-1-1.113.gtf",
            "https://zenodo.org/api/records/13987631/files/Saccharomyces_cerevisiae.R64-1-1.113.gtf/content",
            "gtf",
            "sacCer3",
        ),
    ]

    uploaded = {}
    for name, url, ext, dbkey in inputs_to_fetch:
        append_activity(
            "input_fetch",
            "execute",
            f"Fetch remote dataset {name} into Galaxy history",
            "started",
            {"history_id": history_id, "url": url, "ext": ext, "dbkey": dbkey},
        )
        response = fetch_url(session, history_id, name, url, ext=ext, dbkey=dbkey)
        output = response["outputs"][0]
        dataset_id = output["id"]
        append_activity(
            "input_fetch",
            "execute",
            f"Fetch remote dataset {name} into Galaxy history",
            "submitted",
            {"history_id": history_id, "dataset_id": dataset_id, "job_count": len(response.get("jobs", []))},
        )
        dataset = wait_for_dataset(gi, dataset_id, name)
        append_activity(
            "input_fetch",
            "execute",
            f"Fetch remote dataset {name} into Galaxy history",
            "completed",
            {"history_id": history_id, "dataset_id": dataset_id, "state": dataset.get("state")},
        )
        uploaded[name] = dataset_id

    append_reasoning(
        "execution-02",
        "Construct a one-element `list:paired` collection from the two FASTQ uploads.",
        "The workflow input contract requires a collection of type `list:paired`, not two independent datasets, so the forward and reverse reads must be wrapped into a paired collection before invocation.",
        "Create the collection and use it as workflow input step 0.",
    )
    pair_collection = CollectionElement(
        name="SRR5085167",
        type="paired",
        elements=[
            HistoryDatasetElement(name="forward", id=uploaded["SRR5085167_forward.fastqsanger.gz"]),
            HistoryDatasetElement(name="reverse", id=uploaded["SRR5085167_reverse.fastqsanger.gz"]),
        ],
    )
    collection_description = CollectionDescription(
        name="SRR5085167_paired_reads",
        type="list:paired",
        elements=[pair_collection],
    )
    append_activity(
        "collection_create",
        "execute",
        "Create the paired FASTQ dataset collection required by the workflow",
        "started",
        {"history_id": history_id, "collection_name": "SRR5085167_paired_reads"},
    )
    hdca = gi.histories.create_dataset_collection(history_id, collection_description, copy_elements=False)
    hdca_id = hdca["id"]
    append_activity(
        "collection_create",
        "execute",
        "Create the paired FASTQ dataset collection required by the workflow",
        "completed",
        {"history_id": history_id, "hdca_id": hdca_id, "collection_type": hdca.get("collection_type")},
    )

    workflow_inputs = {
        "0": {"id": hdca_id, "src": "hdca"},
        "5": {"id": uploaded["Saccharomyces_cerevisiae.R64-1-1.113.gtf"], "src": "hda"},
    }
    workflow_params = {
        "1": {"input": ""},
        "2": {"input": ""},
        "3": {"input": False},
        "4": {"input": "sacCer3"},
        "6": {"input": "unstranded"},
        "7": {"input": True},
        "8": {"input": True},
        "10": {"input": True},
    }

    append_activity(
        "workflow_invoke",
        "execute",
        "Invoke the imported RNA-seq workflow with the prepared inputs and runtime parameters",
        "started",
        {
            "workflow_id": workflow_id,
            "history_id": history_id,
            "input_steps": sorted(workflow_inputs.keys()),
            "parameter_steps": sorted(workflow_params.keys()),
        },
    )
    invocation = gi.workflows.invoke_workflow(
        workflow_id,
        history_id=history_id,
        inputs=workflow_inputs,
        params=workflow_params,
        allow_tool_state_corrections=True,
        import_inputs_to_history=False,
        use_cached_job=False,
    )
    invocation_id = invocation["id"]
    append_activity(
        "workflow_invoke",
        "execute",
        "Invoke the imported RNA-seq workflow with the prepared inputs and runtime parameters",
        "submitted",
        {"workflow_id": workflow_id, "history_id": history_id, "invocation_id": invocation_id},
    )

    history_status, final_invocation, final_summary = wait_for_history_terminal(gi, history_id, invocation_id)
    append_activity(
        "workflow_invoke",
        "execute",
        "Invoke the imported RNA-seq workflow with the prepared inputs and runtime parameters",
        "completed",
        {
            "workflow_id": workflow_id,
            "history_id": history_id,
            "invocation_id": invocation_id,
            "history_status": summarize_history_status(history_status),
            "invocation_state": final_invocation.get("state"),
            "jobs_summary": final_summary.get("states", {}),
        },
    )

    history_contents = gi.histories.show_history(history_id, contents=True, visible=None, details="all")
    HISTORY_CONTENTS_PATH.write_text(json.dumps(history_contents, indent=2) + "\n", encoding="utf-8")

    state_doc = {
        "base_url": BASE_URL,
        "history": {"id": history_id, "name": history_name},
        "workflow": {
            "published_workflow_id": PUBLISHED_WORKFLOW_ID,
            "published_workflow_name": PUBLISHED_WORKFLOW_NAME,
            "imported_workflow_id": workflow_id,
        },
        "invocation": {
            "id": invocation_id,
            "state": final_invocation.get("state"),
            "jobs_summary": final_summary.get("states", {}),
            "populated_state": final_summary.get("populated_state"),
        },
        "inputs": {
            "paired_collection_id": hdca_id,
            "forward_dataset_id": uploaded["SRR5085167_forward.fastqsanger.gz"],
            "reverse_dataset_id": uploaded["SRR5085167_reverse.fastqsanger.gz"],
            "annotation_dataset_id": uploaded["Saccharomyces_cerevisiae.R64-1-1.113.gtf"],
            "reference_genome": "sacCer3",
            "strandedness": "unstranded",
            "featurecounts_enabled": True,
            "cufflinks_enabled": True,
            "stringtie_enabled": True,
            "additional_qc_enabled": False,
        },
    }
    STATE_PATH.write_text(json.dumps(state_doc, indent=2) + "\n", encoding="ascii")
    finalize_status("completed")
    print(json.dumps(state_doc, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - benchmark recovery path
        tb = traceback.format_exc()
        error_id = add_error(
            step="live_execution",
            message=str(exc),
            category="tool",
            context={"traceback": tb},
        )
        append_reasoning(
            "failure-01",
            f"Stop the current attempt after execution failed with {type(exc).__name__}: {exc}",
            "The live execution script encountered a terminal error. The traceback was written to errors/error.json so the next step can be a signature-based diagnosis rather than a blind retry.",
            "Inspect the captured failure evidence and decide whether a targeted retry is justified.",
        )
        append_activity(
            "live_execution",
            "check",
            "Capture terminal execution failure evidence",
            "failed",
            {"error_id": error_id, "error_type": type(exc).__name__, "message": str(exc)},
        )
        finalize_status("failed")
        print(tb, file=sys.stderr)
        raise
