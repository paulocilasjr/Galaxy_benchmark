#!/usr/bin/env python3
import json
import sys
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
    resolve_error,
    summarize_history_status,
    wait_for_history_terminal,
)


HISTORY_ID = "bbd44e69cb8906b56d7f0eb03f73cac5"
WORKFLOW_ID = "d75906df7c345830"
PAIRED_COLLECTION_ID = "37468deefebdd014"
GTF_DATASET_ID = "f9cad7b01a472135c19c15d27fbc3c3f"
STATE_PATH = RUN_DIR / "results" / "execution_state.attempt_2.json"
HISTORY_CONTENTS_PATH = RUN_DIR / "results" / "history_contents.attempt_2.json"


def main() -> int:
    api_key = load_api_key()
    gi = GalaxyInstance(url=BASE_URL, key=api_key)

    append_activity(
        "failure_evidence_review",
        "check",
        "Review the failed attempt 1 invocation response before retrying",
        "completed",
        {
            "attempt": 1,
            "error_signature": "HTTP 400 missing non-optional input step Generate additional QC reports",
            "evidence": "Galaxy returned `Workflow cannot be run because input step ... is not optional and no input provided.`",
        },
    )
    append_reasoning(
        "failure-02",
        "Interpret the first failure as a workflow payload-shape error rather than a data or tool error.",
        "The failure occurred before any workflow job was scheduled, and Galaxy named a missing non-optional parameter input step. This points to an API binding problem, not to invalid FASTQs, annotation incompatibility, or compute-side job failure.",
        "Revise the retry to supply parameter_input values via the workflow `inputs` map instead of `params`.",
    )

    append_activity(
        "payload_revision",
        "revise",
        "Create attempt 2 retry logic with parameter_input values bound in the workflow inputs map",
        "completed",
        {
            "attempt": 2,
            "changed_items": [
                "Move workflow runtime parameter values from `params` to `inputs`.",
                "Address workflow inputs by step label using `inputs_by=name`.",
                "Reuse the existing history, uploaded datasets, and paired collection because attempt 1 failed before job launch.",
            ],
            "reason": "Galaxy rejected attempt 1 because the non-optional parameter input `Generate additional QC reports` was not considered provided.",
            "new_artifact_path": str(Path(__file__).resolve()),
        },
    )
    append_reasoning(
        "revise-01",
        "Retry with a label-addressed workflow input map that includes both data inputs and parameter inputs.",
        "Galaxy's workflow invocation model records parameter_input steps as workflow inputs. Using `inputs_by=name` with raw values is the narrowest change that addresses the exact failure signature while preserving the already prepared datasets and collection.",
        "Submit attempt 2 and poll the history to terminal state.",
    )

    workflow_inputs = {
        "Collection paired FASTQ files": {"id": PAIRED_COLLECTION_ID, "src": "hdca"},
        "GTF file of annotation": {"id": GTF_DATASET_ID, "src": "hda"},
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
        "workflow_retry",
        "retry",
        "Retry workflow invocation with corrected parameter-input mapping",
        "started",
        {
            "attempt": 2,
            "history_id": HISTORY_ID,
            "workflow_id": WORKFLOW_ID,
            "inputs_by": "name",
        },
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
        "workflow_retry",
        "execute",
        "Submit attempt 2 workflow invocation",
        "submitted",
        {
            "attempt": 2,
            "history_id": HISTORY_ID,
            "workflow_id": WORKFLOW_ID,
            "invocation_id": invocation_id,
        },
    )

    history_status, final_invocation, final_summary = wait_for_history_terminal(gi, HISTORY_ID, invocation_id)
    append_activity(
        "workflow_retry",
        "execute",
        "Complete attempt 2 workflow invocation",
        "completed",
        {
            "attempt": 2,
            "history_id": HISTORY_ID,
            "workflow_id": WORKFLOW_ID,
            "invocation_id": invocation_id,
            "history_status": summarize_history_status(history_status),
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
        "err-0001",
        "Attempt 2 supplied runtime parameter_input values in the workflow inputs map with `inputs_by=name`, which satisfied Galaxy's required non-optional input-step binding.",
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
            step="live_execution_attempt_2",
            message=str(exc),
            category="tool",
            context={"traceback": tb},
        )
        append_reasoning(
            "failure-03",
            f"Stop attempt 2 after {type(exc).__name__}: {exc}",
            "The revised invocation still failed, so a different mechanism or input interpretation would be required before another retry.",
            "Inspect the new failure evidence and decide whether a materially different third attempt is justified.",
        )
        append_activity(
            "workflow_retry",
            "check",
            "Capture terminal attempt 2 failure evidence",
            "failed",
            {"attempt": 2, "error_id": error_id, "error_type": type(exc).__name__, "message": str(exc)},
        )
        finalize_status("failed")
        print(tb, file=sys.stderr)
        raise
