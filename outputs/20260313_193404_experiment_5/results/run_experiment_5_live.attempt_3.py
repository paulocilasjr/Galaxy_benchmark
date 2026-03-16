#!/usr/bin/env python3
import json
import sys
import time
import traceback
from pathlib import Path

from bioblend.galaxy import GalaxyInstance

from run_experiment_5_live import (
    BASE_URL,
    RUN_DIR,
    add_error,
    append_activity,
    append_reasoning,
    finalize_status,
    load_api_key,
    load_error_doc,
    resolve_error,
    save_error_doc,
    wait_for_dataset,
)


HISTORY_ID = "bbd44e69cb8906b56d7f0eb03f73cac5"
WORKFLOW_ID = "d75906df7c345830"
PAIRED_COLLECTION_ID = "37468deefebdd014"
GTF_DATASET_ID = "f9cad7b01a472135c19c15d27fbc3c3f"
STALLED_INVOCATION_ID = "a4245fa442769799"
MASK_FILE_PATH = RUN_DIR / "results" / "cufflinks_chrM_mask.gtf"
STATE_PATH = RUN_DIR / "results" / "execution_state.attempt_3.json"
HISTORY_CONTENTS_PATH = RUN_DIR / "results" / "history_contents.attempt_3.json"


def set_run_status_running() -> None:
    doc = load_error_doc()
    doc["run_status"] = "running"
    save_error_doc(doc)


def ensure_stall_error() -> str:
    message = (
        "Accepted workflow invocation remained in state `new` with zero populated steps and no scheduled jobs "
        "for more than 60 seconds."
    )
    doc = load_error_doc()
    for err in doc["errors"]:
        if err["message"] == message:
            return err["id"]
    return add_error(
        step="attempt_2_monitoring",
        message=message,
        category="workflow",
        context={
            "invocation_id": STALLED_INVOCATION_ID,
            "history_id": HISTORY_ID,
            "observed_state": "new",
            "populated_steps": 0,
            "jobs_summary": {},
        },
    )


def wait_for_population(
    gi: GalaxyInstance,
    invocation_id: str,
    timeout_seconds: int = 180,
    poll_seconds: int = 20,
) -> tuple[dict, dict]:
    elapsed = 0
    while True:
        invocation = gi.invocations.show_invocation(invocation_id)
        summary = gi.invocations.get_invocation_summary(invocation_id)
        snapshot = {
            "invocation_id": invocation_id,
            "invocation_state": invocation.get("state"),
            "steps": len(invocation.get("steps", [])),
            "jobs_summary": summary.get("states", {}),
            "populated_state": summary.get("populated_state"),
            "elapsed_seconds": elapsed,
        }
        append_activity(
            "workflow_population_poll",
            "check",
            "Poll workflow invocation population status",
            "observed",
            snapshot,
        )
        if summary.get("populated_state") not in {"new", "ready"} and len(invocation.get("steps", [])) > 0:
            return invocation, summary
        if elapsed >= timeout_seconds:
            raise RuntimeError(
                "Workflow invocation remained unpopulated after "
                f"{timeout_seconds} seconds: state={invocation.get('state')} "
                f"populated_state={summary.get('populated_state')} steps={len(invocation.get('steps', []))}"
            )
        time.sleep(poll_seconds)
        elapsed += poll_seconds


def wait_for_completion(
    gi: GalaxyInstance,
    invocation_id: str,
    history_id: str,
    poll_seconds: int = 60,
) -> tuple[dict, dict, dict]:
    time.sleep(25)
    while True:
        invocation = gi.invocations.show_invocation(invocation_id)
        summary = gi.invocations.get_invocation_summary(invocation_id)
        history_status = gi.histories.get_status(history_id)
        job_states = summary.get("states", {})
        active_jobs = sum(job_states.get(key, 0) for key in ["new", "waiting", "queued", "running"])
        problem_jobs = sum(job_states.get(key, 0) for key in ["error", "failed", "paused", "deleted"])
        history_details = history_status.get("state_details", {})
        append_activity(
            "workflow_completion_poll",
            "check",
            "Poll workflow completion status after population",
            "observed",
            {
                "invocation_id": invocation_id,
                "invocation_state": invocation.get("state"),
                "populated_state": summary.get("populated_state"),
                "job_states": job_states,
                "history_status": history_status,
            },
        )
        if summary.get("populated_state") in {"failed", "cancelled"} or invocation.get("state") in {"failed", "cancelled"}:
            raise RuntimeError(
                f"Workflow invocation reached terminal failure state {invocation.get('state')} "
                f"with populated_state={summary.get('populated_state')} and jobs={job_states}"
            )
        if (
            summary.get("populated_state") == "ok"
            and len(invocation.get("steps", [])) > 0
            and active_jobs == 0
        ):
            if problem_jobs > 0 or sum(history_details.get(k, 0) for k in ["error", "failed", "paused"]) > 0:
                raise RuntimeError(
                    f"Workflow completed with job or history errors. jobs={job_states} history={history_details}"
                )
            return history_status, invocation, summary
        time.sleep(poll_seconds)


def main() -> int:
    set_run_status_running()
    stall_error_id = ensure_stall_error()

    api_key = load_api_key()
    gi = GalaxyInstance(url=BASE_URL, key=api_key)

    append_activity(
        "stalled_invocation_review",
        "check",
        "Review attempt 2 evidence before a materially different retry",
        "completed",
        {
            "attempt": 2,
            "stalled_invocation_id": STALLED_INVOCATION_ID,
            "observed_signature": "Invocation stayed new with zero steps and empty jobs_summary",
            "evidence_window_seconds": 60,
        },
    )
    append_reasoning(
        "failure-04",
        "Treat the attempt 2 invocation as a stalled workflow-population failure.",
        "Galaxy stored all input bindings but never populated any workflow steps, which means the second attempt did not advance into job scheduling. The workflow includes an optional Cufflinks mask input that is explicitly described as a mitochondrial exclusion GTF, and leaving it blank while enabling Cufflinks may be blocking population.",
        "Provide a concrete mitochondrial mask GTF and retry with a stricter population-completion gate.",
    )

    append_activity(
        "attempt_3_revision",
        "revise",
        "Prepare attempt 3 with explicit Cufflinks mask input and corrected completion gating",
        "completed",
        {
            "attempt": 3,
            "changed_items": [
                "Add `results/cufflinks_chrM_mask.gtf` as the optional Cufflinks exclusion input.",
                "Upload the mask dataset to Galaxy and bind it to workflow input `GTF with regions to exclude from FPKM normalization with Cufflinks`.",
                "Require the invocation to populate steps before treating workflow execution as started.",
            ],
            "reason": "Attempt 2 stalled after accepted submission without populating any workflow steps.",
            "new_artifact_path": str(Path(__file__).resolve()),
        },
    )

    mask_text = MASK_FILE_PATH.read_text(encoding="ascii")
    append_activity(
        "mask_upload",
        "execute",
        "Upload the mitochondrial mask GTF for Cufflinks exclusion",
        "started",
        {"history_id": HISTORY_ID, "artifact_path": str(MASK_FILE_PATH.resolve())},
    )
    upload = gi.tools.paste_content(
        mask_text,
        HISTORY_ID,
        file_type="gtf",
        dbkey="sacCer3",
        file_name="cufflinks_chrM_mask.gtf",
    )
    mask_dataset_id = upload["outputs"][0]["id"]
    append_activity(
        "mask_upload",
        "execute",
        "Upload the mitochondrial mask GTF for Cufflinks exclusion",
        "submitted",
        {"history_id": HISTORY_ID, "dataset_id": mask_dataset_id},
    )
    mask_dataset = wait_for_dataset(gi, mask_dataset_id, "cufflinks_chrM_mask.gtf")
    append_activity(
        "mask_upload",
        "execute",
        "Upload the mitochondrial mask GTF for Cufflinks exclusion",
        "completed",
        {"history_id": HISTORY_ID, "dataset_id": mask_dataset_id, "state": mask_dataset.get("state")},
    )

    workflow_inputs = {
        "Collection paired FASTQ files": {"id": PAIRED_COLLECTION_ID, "src": "hdca"},
        "GTF file of annotation": {"id": GTF_DATASET_ID, "src": "hda"},
        "GTF with regions to exclude from FPKM normalization with Cufflinks": {
            "id": mask_dataset_id,
            "src": "hda",
        },
        "Forward adapter": "",
        "Reverse adapter": "",
        "Generate additional QC reports": False,
        "Reference genome": "sacCer3",
        "Strandedness": "unstranded",
        "Use featureCounts for generating count tables": True,
        "Compute Cufflinks FPKM": True,
        "Compute StringTie FPKM": True,
    }

    append_activity(
        "workflow_retry_attempt_3",
        "retry",
        "Retry workflow invocation with explicit Cufflinks mask input",
        "started",
        {"attempt": 3, "history_id": HISTORY_ID, "workflow_id": WORKFLOW_ID, "inputs_by": "name"},
    )
    invocation = gi.workflows.invoke_workflow(
        WORKFLOW_ID,
        history_id=HISTORY_ID,
        inputs=workflow_inputs,
        inputs_by="name",
        allow_tool_state_corrections=True,
        import_inputs_to_history=False,
        use_cached_job=False,
    )
    invocation_id = invocation["id"]
    append_activity(
        "workflow_retry_attempt_3",
        "execute",
        "Submit attempt 3 workflow invocation",
        "submitted",
        {"attempt": 3, "history_id": HISTORY_ID, "workflow_id": WORKFLOW_ID, "invocation_id": invocation_id},
    )

    populated_invocation, populated_summary = wait_for_population(gi, invocation_id)
    append_activity(
        "workflow_retry_attempt_3",
        "execute",
        "Confirm attempt 3 invocation populated workflow steps",
        "completed",
        {
            "attempt": 3,
            "invocation_id": invocation_id,
            "invocation_state": populated_invocation.get("state"),
            "populated_state": populated_summary.get("populated_state"),
            "steps": len(populated_invocation.get("steps", [])),
        },
    )

    history_status, final_invocation, final_summary = wait_for_completion(gi, invocation_id, HISTORY_ID)
    append_activity(
        "workflow_retry_attempt_3",
        "execute",
        "Complete attempt 3 workflow invocation",
        "completed",
        {
            "attempt": 3,
            "history_id": HISTORY_ID,
            "workflow_id": WORKFLOW_ID,
            "invocation_id": invocation_id,
            "history_status": history_status,
            "invocation_state": final_invocation.get("state"),
            "jobs_summary": final_summary.get("states", {}),
        },
    )

    history_contents = gi.histories.show_history(HISTORY_ID, contents=True, visible=None, details="all")
    HISTORY_CONTENTS_PATH.write_text(json.dumps(history_contents, indent=2) + "\n", encoding="utf-8")
    state_doc = {
        "base_url": BASE_URL,
        "history": {"id": HISTORY_ID},
        "workflow": {"imported_workflow_id": WORKFLOW_ID},
        "invocation": {
            "id": invocation_id,
            "state": final_invocation.get("state"),
            "jobs_summary": final_summary.get("states", {}),
            "populated_state": final_summary.get("populated_state"),
        },
        "inputs": {
            "paired_collection_id": PAIRED_COLLECTION_ID,
            "annotation_dataset_id": GTF_DATASET_ID,
            "cufflinks_mask_dataset_id": mask_dataset_id,
            "reference_genome": "sacCer3",
            "strandedness": "unstranded",
            "featurecounts_enabled": True,
            "cufflinks_enabled": True,
            "stringtie_enabled": True,
            "additional_qc_enabled": False,
        },
    }
    STATE_PATH.write_text(json.dumps(state_doc, indent=2) + "\n", encoding="ascii")

    resolve_error(
        stall_error_id,
        "Attempt 3 supplied the optional Cufflinks mitochondrial mask input and used a strict population gate before monitoring job completion.",
    )
    finalize_status("completed_with_errors")
    print(json.dumps(state_doc, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - benchmark recovery path
        tb = traceback.format_exc()
        error_id = add_error(
            step="live_execution_attempt_3",
            message=str(exc),
            category="workflow",
            context={"traceback": tb},
        )
        append_reasoning(
            "failure-05",
            f"Stop attempt 3 after {type(exc).__name__}: {exc}",
            "The third attempt introduced both a new optional workflow input and a corrected scheduler gate. If it still fails, the next action must change the execution mechanism rather than repeating the same workflow invocation pattern.",
            "Inspect the new failure evidence and decide whether manual tool-chain execution is required.",
        )
        append_activity(
            "workflow_retry_attempt_3",
            "check",
            "Capture terminal attempt 3 failure evidence",
            "failed",
            {"attempt": 3, "error_id": error_id, "error_type": type(exc).__name__, "message": str(exc)},
        )
        finalize_status("failed")
        print(tb, file=sys.stderr)
        raise
