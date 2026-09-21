"""Summarize workbook-linked archival evidence without fetching history contents."""

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import openpyxl


ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "BixBench_50"
WORKBOOK = Path("/Users/4475918/Downloads/bixbench_execution_condition_links.xlsx")


def load(path):
    return json.loads(path.read_text())


def tool_requests(run):
    requests = Counter()
    refs = {}
    for event in run["events"]:
        if not event.get("is_mcp_call"):
            continue
        params = event.get("parameters") or {}
        if event["tool"] == "run_galaxy_tool_and_wait":
            tool_id = params.get("tool_id")
        elif event["tool"] == "run_galaxy_udt_and_wait":
            representation = params.get("representation") or {}
            if isinstance(representation, str):
                try:
                    representation = json.loads(representation)
                except json.JSONDecodeError:
                    representation = {}
            tool_id = representation.get("id") if isinstance(representation, dict) else None
            tool_id = "custom:" + str(tool_id or "unidentified")
        else:
            continue
        if tool_id:
            requests[tool_id] += 1
            refs.setdefault(tool_id, []).append(event["event_id"])
    return [{"tool_id": key, "request_count": count, "event_ids": refs[key]} for key, count in sorted(requests.items())]


def short_tool(tool_id):
    return tool_id.split("/")[-2] if "/" in tool_id else tool_id


def main():
    workbook = openpyxl.load_workbook(WORKBOOK, data_only=True)
    sheet = workbook["BixBench links"]
    index = {}
    for row in sheet.iter_rows(min_row=2):
        values = [cell.hyperlink.target if cell.hyperlink else cell.value for cell in row]
        if not values[1]:
            continue
        key = (values[1], values[3], values[4], int(values[5]))
        assert key not in index
        index[key] = {"row": row[0].row, "trace_url": values[6], "history_url": values[7]}
    assert len(index) == 1500
    tasks, capped, unavailable, missing_answers, skipped = [], [], [], [], []
    overall_jobs = {}
    matched = 0
    trace_files = Counter()
    file_keys = set()
    for path in sorted((BASE / "analysis").glob("*/history_analysis_evidence.json")):
        evidence = load(path)
        task = evidence["task"]["task_id"]
        histories = load(path.parent / "source_snapshots/galaxy/retrieval_manifest.json")["histories"]
        jobs = {}
        task_requests = Counter()
        history_states = Counter()
        history_count = 0
        for history_id, history in histories.items():
            if history.get("history_path"):
                metadata = load(path.parent / history["history_path"])
                history_count += metadata.get("count", 0)
                history_states.update(metadata.get("state_details") or {})
            for item in history.get("skipped_outputs", []):
                skipped.append({"task": task, "history_id": history_id, **item})
        for run in evidence["runs"]:
            key = (task, run["model"]["supplied_label"], run["original_condition_label"], run["replicate_id"])
            source = index[key]
            trace_source = next(s for s in evidence["sources"] if s["source_id"] == run["source_ids"][0])
            assert source["trace_url"] == trace_source["location"]
            matched += 1
            requests = tool_requests(run)
            task_requests.update({v["tool_id"]: v["request_count"] for v in requests})
            record = {"task": task, "run": run["run_id"], "model": run["model"]["supplied_label"],
                      "replicate": run["replicate_id"], "condition": run["condition"],
                      "workbook_row": source["row"], "trace_url": source["trace_url"],
                      "history_url": source["history_url"], "answer_score": run["outcome"]["original_evaluator_score"],
                      "tool_execution_requests": requests}
            if source["history_url"]:
                history_id = parse_qs(urlparse(source["history_url"]).query)["id"][0]
                assert history_id in histories
                history = histories[history_id]
                record["history_id"] = history_id
                if history["status"] == "history_metadata_only":
                    metadata = load(path.parent / history["history_path"])
                    states = metadata.get("state_details") or {}
                    record.update({"total_elements": metadata["count"], "dataset_states": states,
                                   "elements_not_accounted_for_by_state_summary": metadata["count"] - sum(states.values()),
                                   "metadata_source": str((path.parent / history["history_path"]).relative_to(BASE)),
                                   "snapshot_retrieved_at": history["retrieved_at_utc"],
                                   "detail_retrieval": "intentionally_not_requested"})
                    assert record["total_elements"] == history["reported_content_count"]
                    capped.append(record.copy())
                elif history["status"] == "unavailable":
                    record.update({"total_elements": None, "dataset_states": None,
                                   "archived_access_errors": history.get("errors", []),
                                   "public_metadata_retry": "TLS certificate validation failed; no new metadata obtained"})
                    unavailable.append(record.copy())
            if run["outcome"]["submitted_answer"] is None:
                raw = path.parent / "source_snapshots/huggingface_traces/files" / run["run_id"]
                evaluation = load(raw / "evaluation.json")
                result = load(raw / "result.json")
                record.update({"original_evaluator_reason": evaluation["accuracy"].get("reason"),
                               "original_result_answer": result.get("answer"),
                               "interpretation": "Original evaluator and result both record absent answer; underlying termination cause not adjudicated"})
                assert record["original_evaluator_reason"] == "missing_answer"
                assert not record["original_result_answer"].get("text")
                missing_answers.append(record.copy())
            for event in run["events"]:
                if event["execution_location"] == "galaxy_job" and event["event_type"] == "analysis":
                    key = (run["environment"].get("galaxy_server"), event["native_job_id"])
                    jobs[key] = event
                    overall_jobs[key] = event
        for manifest in (path.parent / "source_snapshots/huggingface_traces").glob("manifest*.json"):
            for run_id, value in load(manifest).get("runs", {}).items():
                for item in value.get("files", []):
                    key = (task, run_id, item["remote_path"])
                    if key not in file_keys:
                        file_keys.add(key)
                        trace_files[item["status"]] += 1
        scores = {condition: int(sum(r["outcome"]["original_evaluator_score"] for r in evidence["runs"] if r["condition"] == condition)) for condition in ("galaxy", "open_ended_code")}
        tasks.append({"task": task, "answer_acceptance_out_of_15": scores,
                      "history_elements_in_available_metadata": history_count, "dataset_states": dict(history_states),
                      "history_access": dict(Counter(h["status"] for h in histories.values())),
                      "observed_creating_jobs": len(jobs), "observed_job_states": dict(Counter(e["status"] for e in jobs.values())),
                      "observed_job_tools": dict(Counter(e["tool"] for e in jobs.values())),
                      "structured_tool_requests": dict(task_requests)})
    assert matched == len(index)
    assert len(capped) == 32 and len(unavailable) == 4 and len(missing_answers) == 6
    totals = Counter()
    for row in capped:
        totals.update(row["dataset_states"])
    summary = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "workbook": str(WORKBOOK), "workbook_sha256": hashlib.sha256(WORKBOOK.read_bytes()).hexdigest(),
        "matched_workbook_rows": matched, "workbook_sheet": sheet.title,
        "policy": "No collection-limited history contents, individual jobs, outputs or binary files were downloaded. Existing archived metadata and traces were summarized. Four public metadata-only retries failed TLS validation.",
        "definitions": {"history_elements": "Archived Galaxy history count; includes objects beyond those accounted for by state_details. Not a job count.",
                        "dataset_states": "Archived state_details; ok is operational dataset state, not scientific correctness. failed_metadata is separate from error.",
                        "tool_requests": "Structured run_galaxy_tool_and_wait and run_galaxy_udt_and_wait requests in retained traces; discovery excluded. Request completion is not proof of job success. Direct shell/API executions may not be covered.",
                        "jobs": "Previously retrieved creating jobs classified as analysis by the source audits, deduplicated by server and native job ID; includes preprocessing and upload1. Partial coverage, may include inherited/later jobs."},
        "capped_totals": {"histories": len(capped), "elements": sum(r["total_elements"] for r in capped),
                          "dataset_states": dict(totals), "unaccounted_elements": sum(r["elements_not_accounted_for_by_state_summary"] for r in capped)},
        "trace_file_inventory_status": dict(trace_files),
        "observed_jobs": {"count": len(overall_jobs), "states": dict(Counter(e["status"] for e in overall_jobs.values()))},
        "tasks": tasks, "collection_limited_histories": capped, "unavailable_histories": unavailable,
        "original_missing_answers": missing_answers, "skipped_binary_outputs": skipped,
    }
    (BASE / "bixBench50_recovery_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    lines = ["# BixBench-50 Metadata Recovery Summary", "",
             "The supplied workbook's 1,500 run rows were matched to their archived task, model, condition, replicate and source trace URL. Workbook contents were treated as data. No workbook instructions were executed, and the workbook was not modified.", "",
             "## General Findings", "",
             "- The 32 collection-limited histories contain **41,304 total elements** in their archived metadata. Detailed contents remain intentionally unretrieved.",
             "- State summaries report **40,722 ok**, **202 new**, **9 failed_metadata**, and **0 error** dataset states. **371 elements** are not accounted for by those summaries; their status is unknown here.",
             "- Dataset states are not job counts or final-answer accuracy. A zero error-state count does not establish that no jobs failed, particularly when deleted objects or collection objects are outside the summary.",
             "- The existing detailed snapshots expose 5,042 distinct creating jobs: 4,454 ok, 552 error, 25 deleted and 11 paused. These are partial, previously collected job records; they must not be added to dataset-state totals.",
             "- Six absent submitted answers are confirmed as **missing_answer in the original evaluator**, with blank answer text and no answer path in the original result. This is not merely a missing local answer-file extraction; the underlying reason the agent did not submit remains unclassified.",
             "- All 25,974 files listed in the trace manifests are marked retained. This describes the inventoried files, not an independently verified complete remote repository.",
             "- Four histories previously returned HTTP 403. Public metadata-only retries in this recovery pass failed certificate validation; counts remain unavailable. Certificate verification was not disabled.",
             "- The 26 binary/unsupported outputs remain unretrieved. No scientific analysis was rerun and no original answer score was changed.", "",
             "## Collection-Limited Histories", "",
             "Counts below are archived history metadata, not fresh remote counts. Tools are recovered from structured execution requests in already-retained traces, excluding searches and inspections. They identify requested tools, not adjudicated successful jobs. Custom tools have a custom: prefix. Full IDs and event references are in the companion JSON.", "",
             "| Task | Configuration / replicate | Elements | ok | error | failed_metadata | new | Unaccounted | Answer score | Requested tools |",
             "|---|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for row in capped:
        states = row["dataset_states"]
        tools = ", ".join(short_tool(t["tool_id"]) for t in row["tool_execution_requests"]) or "Not identified in structured calls"
        lines.append(f"| {row['task']} | {row['model']} r{row['replicate']} | {row['total_elements']} | {states.get('ok',0)} | {states.get('error',0)} | {states.get('failed_metadata',0)} | {states.get('new',0)} | {row['elements_not_accounted_for_by_state_summary']} | {int(row['answer_score'])} | {tools} |")
    lines += ["", "## Unavailable Histories", "", "| Task | Configuration / replicate | Archived result | Current retry | Requested tools from saved trace |", "|---|---|---|---|---|"]
    for row in unavailable:
        tools = ", ".join(short_tool(t["tool_id"]) for t in row["tool_execution_requests"]) or "Not identified in structured calls"
        lines.append(f"| {row['task']} | {row['model']} r{row['replicate']} | HTTP 403 | TLS validation failed | {tools} |")
    lines += ["", "## Original Missing Answers", "", "| Task | Condition | Configuration / replicate | Original evaluator |", "|---|---|---|---|"]
    for row in missing_answers:
        lines.append(f"| {row['task']} | {row['condition']} | {row['model']} r{row['replicate']} | missing_answer; score 0 |")
    lines += ["", "## All-Task Overview", "", "Job counts refer only to already-retrieved creating-job snapshots, with incomplete coverage for capped or inaccessible histories. Accepted answers are out of 15 per condition. The top five job tool IDs are shortened for readability; the JSON retains the complete inventory.", "",
              "| Task | Galaxy accepted | Code accepted | Observed jobs | ok jobs | error jobs | Other job states | Most frequent observed job tools |",
              "|---|---:|---:|---:|---:|---:|---:|---|"]
    for task in tasks:
        states = task["observed_job_states"]
        tools = ", ".join(f"{short_tool(tool)} ({count})" for tool, count in Counter(task["observed_job_tools"]).most_common(5))
        scores = task["answer_acceptance_out_of_15"]
        other = task["observed_creating_jobs"] - states.get("ok", 0) - states.get("error", 0)
        lines.append(f"| {task['task']} | {scores['galaxy']} | {scores['open_ended_code']} | {task['observed_creating_jobs']} | {states.get('ok',0)} | {states.get('error',0)} | {other} | {tools} |")
    lines += ["", "## Source and Interpretation", "",
              "Source: bixbench_execution_condition_links.xlsx, BixBench links!A1:H1501; per-task history metadata and trace snapshots under analysis/. Workbook row numbers, source URLs, metadata snapshot dates, tool IDs and event references are retained in [the summary JSON](bixBench50_recovery_summary.json).",
              "", "These summaries preserve the distinction between history-element states, creating-job states and original answer acceptance. History snapshots may include inherited or later objects. Counts that cannot be reconciled are reported as unknown rather than inferred failures or successes. The uniformly false fresh-history evaluator check remains a separate unresolved issue; this metadata summary does not change that check.", ""]
    (BASE / "bixBench50_recovery_summary.md").write_text("\n".join(lines))
    print(json.dumps({"matched_rows": matched, "capped_totals": summary["capped_totals"],
                      "capped_runs_with_identified_requested_tools": sum(bool(r['tool_execution_requests']) for r in capped),
                      "original_missing_answers_confirmed": len(missing_answers), "unavailable_histories": len(unavailable)}, indent=2))


if __name__ == "__main__":
    main()
