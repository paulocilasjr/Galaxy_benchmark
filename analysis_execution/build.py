"""Build task-neutral, evidence-linked audit artifacts from retained sources."""
from __future__ import annotations

import gzip
import hashlib
import json
import re
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from collect import digest, write_json
from workbook import RunLink, huggingface_source


def read_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def locate(folder: Path, name: str) -> Path | None:
    if not folder.exists():
        return None
    matches = sorted(folder.rglob(name), key=lambda p: (len(p.parts), str(p)))
    return matches[0] if matches else None


def _event_type(command: str, condition: str) -> str:
    low = command.lower()
    if any(x in low for x in ("--help", "command -v", "which ", "pip show", "rg --files")):
        return "discovery"
    if any(x in low for x in ("unzip -l", "unzip -t", "ls -la", "inputs_manifest.json")):
        return "input_preparation"
    if condition == "galaxy":
        return "orchestration"
    if any(x in low for x in ("python", "phykit", "rscript", "awk ", "bash ", "perl ")):
        return "analysis"
    return "orchestration"


def _trace_events(path: Path, run_id: str, source_id: str, condition: str):
    if not path:
        return []
    raw = gzip.decompress(path.read_bytes()).decode(errors="replace") if path.suffix == ".gz" else path.read_text(errors="replace")
    if path.name.startswith("claude_events"):
        return _claude_trace_events(raw, path, run_id, source_id, condition)
    events = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        if record.get("type") != "item.completed":
            continue
        item = record.get("item") or {}
        kind = item.get("type")
        if kind not in {"command_execution", "mcp_tool_call", "web_search"}:
            continue
        native = str(item.get("id") or f"line_{line_number}")
        command = item.get("command") if kind == "command_execution" else None
        tool = "shell" if kind == "command_execution" else item.get("tool") or kind
        event_type = _event_type(command or "", condition) if kind == "command_execution" else (
            "discovery" if kind == "web_search" or str(tool).startswith(("inspect_", "search_")) else "orchestration")
        events.append({"event_id": f"evt_trace_{run_id}_{native}_line_{line_number}", "sequence": len(events) + 1,
                       "source_line": line_number, "timestamp": None,
                       "timestamp_source": "JSONL order; no per-item timestamp",
                       "event_type": event_type,
                       "execution_location": "agent_runtime" if kind == "command_execution" else "external_service" if kind == "web_search" else "mixed" if str(tool).startswith("run_galaxy") else "agent_runtime",
                       "native_tool_call_id": native, "parent_event_ids": [], "input_artifact_ids": [], "output_artifact_ids": [],
                       "tool": tool, "command": command, "parameters": item.get("arguments"),
                       "is_mcp_call": kind == "mcp_tool_call",
                       "status": item.get("status") or "completed", "exit_code": item.get("exit_code"),
                       "stdout_excerpt": (item.get("aggregated_output") or "")[:1000] if kind == "command_execution" else None,
                       "stderr_excerpt": str(item.get("error"))[:1000] if item.get("error") else None,
                       "evidence_refs": [f"{source_id}:{path.name}#L{line_number}"],
                       "visibility_limits": "Full retained trace is authoritative; shell output excerpt is truncated"})
    return events


def _claude_trace_events(raw: str, path: Path, run_id: str, source_id: str, condition: str):
    records = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        records.append((line_number, record))
    results = {}
    for line_number, record in records:
        if record.get("type") != "user":
            continue
        content = (record.get("message") or {}).get("content", [])
        for block in content if isinstance(content, list) else []:
            if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("tool_use_id"):
                text = block.get("content")
                if isinstance(text, list):
                    text = "\n".join(x.get("text", "") for x in text if isinstance(x, dict))
                results[block["tool_use_id"]] = (line_number, str(text or ""), bool(block.get("is_error")))
    events = []
    for line_number, record in records:
        if record.get("type") != "assistant":
            continue
        content = (record.get("message") or {}).get("content", [])
        for block_index, block in enumerate(content if isinstance(content, list) else []):
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            native = str(block.get("id") or f"line_{line_number}")
            native_tool = str(block.get("name") or "unknown")
            params = block.get("input") or {}
            is_shell = native_tool == "Bash"
            command = params.get("command") if is_shell and isinstance(params, dict) else None
            is_mcp = native_tool.startswith("mcp__")
            tool = "shell" if is_shell else native_tool.rsplit("__", 1)[-1] if is_mcp else native_tool
            result = results.get(native)
            events.append({"event_id": f"evt_trace_{run_id}_{native}_line_{line_number}_block_{block_index}", "sequence": len(events) + 1,
                           "source_line": line_number, "timestamp": None,
                           "timestamp_source": "Claude JSONL order; no per-tool timestamp",
                           "event_type": _event_type(command or "", condition) if is_shell else "discovery" if tool.startswith(("inspect_", "search_")) else "orchestration",
                           "execution_location": "agent_runtime" if is_shell else "mixed" if is_mcp and tool.startswith("run_galaxy") else "agent_runtime",
                           "native_tool_call_id": native, "native_tool_name": native_tool,
                           "parent_event_ids": [], "input_artifact_ids": [], "output_artifact_ids": [],
                           "tool": tool, "command": command, "parameters": params, "is_mcp_call": is_mcp,
                           "status": "error" if result and result[2] else "completed" if result else "result_not_observed",
                           "exit_code": None, "stdout_excerpt": result[1][:1000] if result else None,
                           "stderr_excerpt": result[1][:1000] if result and result[2] else None,
                           "evidence_refs": [f"{source_id}:{path.name}#L{line_number}"] + ([f"{source_id}:{path.name}#L{result[0]}"] if result else []),
                           "visibility_limits": "Claude tool-use/result records; exit code not always structured; full retained trace is authoritative"})
    return events


def _read_task(benchmark: str, task_id: str, repo_root: Path, trace_folders: list[Path]):
    if benchmark == "bixbench":
        for path in sorted((repo_root / "experiments/BixBench").glob("task_*.json")):
            obj = read_json(path)
            if obj.get("question_id") == task_id:
                return {"prompt": obj.get("prompt_task"), "allowed_task_metadata": str(path.relative_to(repo_root)),
                        "allowed_task_metadata_sha256": digest(path.read_bytes()), "source_dataset": obj.get("source_dataset")}
    for folder in trace_folders:
        path = locate(folder, "task.json")
        obj = read_json(path) if path else {}
        if obj:
            return {"prompt": obj.get("prompt_task") or obj.get("prompt") or obj.get("question"),
                    "allowed_task_metadata": None, "allowed_task_metadata_sha256": digest(path.read_bytes()),
                    "source_dataset": obj.get("source_dataset")}
    return {"prompt": None, "allowed_task_metadata": None, "allowed_task_metadata_sha256": None, "source_dataset": None}


def _solution_route(run: dict) -> dict:
    jobs = [e for e in run["events"] if e["execution_location"] == "galaxy_job" and e["event_type"] == "analysis"]
    calls = [e for e in run["events"] if e.get("command") and e["execution_location"] == "agent_runtime"]
    texts = "\n".join(e["command"] for e in calls).lower()
    tools = sorted({e.get("tool") for e in jobs if e.get("tool")})
    families = []
    for label, pattern in (("PhyKIT", "phykit"), ("Datamash", "datamash"),
                           ("Summary Statistics", "summary_statistics"), ("Galaxy custom code", "__udt__")):
        if pattern in " ".join(tools).lower():
            families.append(label)
    if run["condition"] == "open_ended_code":
        for label, pattern in (("PhyKIT", "phykit"), ("Biopython", "bio.phylo"),
                               ("IQ-TREE report", "iq-tree"), ("Newick/branch parser", "newick")):
            if pattern in texts:
                families.append(label)
        if calls and not families:
            families.append("local shell or script; method unclassified")
    return {"classification": ", ".join(dict.fromkeys(families)) or None,
            "tool_ids": tools, "observed_command_indicators": list(dict.fromkeys(families)),
            "biological_method": None, "parameters": "See retained job and command events",
            "validation": "Original evaluator and any recorded agent checks are separate",
            "route_codebook": "Tool family and observed command indicators; method requires case-specific interpretation"}


def _native_hda_ids(value) -> list[str]:
    if isinstance(value, dict):
        found = [str(value["id"])] if value.get("src") in {"hda", "ldda"} and value.get("id") else []
        for child in value.values():
            found.extend(_native_hda_ids(child))
        return list(dict.fromkeys(found))
    if isinstance(value, list):
        return list(dict.fromkeys(x for child in value for x in _native_hda_ids(child)))
    return []


def _recovery_candidates(run: dict) -> list[dict]:
    """Record same-tool/input operational retries; do not infer scientific correctness."""
    jobs = sorted((e for e in run["events"] if e["execution_location"] == "galaxy_job" and e["event_type"] == "analysis"),
                  key=lambda e: (e.get("timestamp") or "", e["event_id"]))
    episodes = []
    for failed in jobs:
        if failed.get("status") not in {"error", "failed"}:
            continue
        inputs = failed.get("native_input_hda_ids") or []
        if not inputs:
            continue
        repaired = next((later for later in jobs if (later.get("timestamp") or "") > (failed.get("timestamp") or "")
                         and later.get("status") == "ok" and later.get("tool") == failed.get("tool")
                         and later.get("native_input_hda_ids") == inputs), None)
        if repaired:
            episodes.append({"episode_id": f"recovery_{run['run_id']}_{failed['native_job_id']}",
                             "trigger": "Recorded Galaxy job failure",
                             "failure_type": "execution_or_parameter_failure_unclassified",
                             "failed_event_ids": [failed["event_id"]],
                             "diagnosis_evidence": failed["evidence_refs"],
                             "corrective_action": "A later job used the same tool and input HDA IDs; compare parameters in event records",
                             "recovery_event_ids": [repaired["event_id"]],
                             "same_goal_linkage": "Same Galaxy tool and input HDA IDs; scientific objective requires case review",
                             "eventual_outcome": "Operational success of later job; answer correctness kept separate",
                             "classification_status": "candidate_requires_case_review"})
    return episodes


def _extract_code(output: Path, run: dict, trace_sid: str) -> list[dict]:
    extracted = []
    for e in run["events"]:
        cmd = e.get("command")
        if not cmd:
            continue
        native = re.sub(r"[^a-zA-Z0-9_-]", "_", str(e.get("native_tool_call_id")))
        if run["condition"] == "open_ended_code":
            path = output / "recovered_code/open_ended_code" / run["run_id"] / f"{native}.command.txt"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(cmd + "\n")
            extracted.append({"run_id": run["run_id"], "event_id": e["event_id"],
                              "path": str(path.relative_to(output)), "sha256": digest(path.read_bytes()),
                              "source_id": trace_sid, "source_line": e.get("source_line"),
                              "reported_exit_code": e.get("exit_code"), "extraction": "Original completed command text; not replayed"})
    for e in run["events"]:
        if e["execution_location"] != "galaxy_job":
            continue
        command = e.get("command") or ""
        match = re.search(r"cat\s*>\s*([^\s]+\.py)\s*<<['\"]?([A-Za-z_]+)['\"]?\n(.*?)\n\2(?:\n|$)", command, re.S)
        if not match:
            continue
        native = re.sub(r"[^a-zA-Z0-9_-]", "_", str(e.get("native_job_id")))
        path = output / "recovered_code/galaxy" / run["run_id"] / f"{native}_{Path(match.group(1)).name}"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(match.group(3) + "\n")
        extracted.append({"run_id": run["run_id"], "event_id": e["event_id"],
                          "path": str(path.relative_to(output)), "sha256": digest(path.read_bytes()),
                          "source_id": e["evidence_refs"][0].split(":", 1)[0],
                          "extraction": "Literal Galaxy command heredoc body; not replayed"})
    return extracted


def _input_manifest(output: Path, runs: list[dict]) -> dict:
    by_run = {}
    names = defaultdict(set)
    for run in runs:
        folder = output / "source_snapshots/huggingface_traces/files" / run["run_id"]
        path = locate(folder, "inputs_manifest.json")
        if not path:
            by_run[run["run_id"]] = {"status": "not_collected"}
            continue
        obj = read_json(path)
        items = obj.get("inputs", [])
        by_run[run["run_id"]] = {"status": "retrieved", "path": str(path.relative_to(output)),
                                 "sha256": digest(path.read_bytes()), "count": len(items)}
        for item in items:
            if item.get("name") and item.get("sha256"):
                names[item["name"]].add(item["sha256"])
    return {"runs": by_run,
            "shared_name_hashes": {name: sorted(hashes) for name, hashes in sorted(names.items())},
            "all_trace_input_hashes_agree_by_name": all(len(h) == 1 for h in names.values()) if names else None,
            "note": "Hashes are copied from original trace manifests; full staged inputs were not rehashed by this audit"}


def build_evidence(output: Path, links: list[RunLink], repo_root: Path, workbook_path: Path) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    sources, runs, run_inventory, recovered = [], [], [], []
    galaxy_seen = {}
    for link in links:
        rid = link.run_id
        trace_sid = f"src_trace_{rid}"
        galaxy_sid = None
        trace_folder = output / "source_snapshots/huggingface_traces/files" / rid
        trace_manifest = read_json(output / "source_snapshots/huggingface_traces/manifests" / f"{rid}.json")
        if link.trace_url:
            sources.append({"source_id": trace_sid, "location": link.trace_url,
                            "retrieval_time_utc": trace_manifest.get("retrieved_at_utc"),
                            "access_status": trace_manifest.get("status", "not_collected"),
                            "tls_certificate_verified": trace_manifest.get("tls_certificate_verified"),
                            "local_snapshot": str(trace_folder.relative_to(output)) if trace_folder.exists() else None,
                            "redactions": [x.get("redactions", []) for x in trace_manifest.get("files", []) if x.get("redactions")],
                            "evidence_completeness": "See file-level trace manifest"})
        galaxy = {}
        if link.galaxy_url:
            from workbook import galaxy_history_id
            hid = galaxy_history_id(link.galaxy_url)
            galaxy_sid = f"src_galaxy_{hid}"
            galaxy = read_json(output / "source_snapshots/galaxy" / hid / "manifest.json")
            if hid not in galaxy_seen:
                sources.append({"source_id": galaxy_sid, "location": link.galaxy_url,
                                "retrieval_time_utc": galaxy.get("retrieved_at_utc"),
                                "access_status": galaxy.get("status", "not_collected"),
                                "tls_certificate_verified": galaxy.get("tls_certificate_verified"),
                                "local_snapshot": f"source_snapshots/galaxy/{hid}" if galaxy else None,
                                "redactions": ["account fields in retained JSON"],
                                "evidence_completeness": "Read-only current history snapshot, not original agent chronology"})
                galaxy_seen[hid] = rid
        events, artifacts = [], []
        prompt_path = locate(trace_folder, "prompt.txt")
        answer_path = locate(trace_folder, "answer.txt")
        evaluation_path = locate(trace_folder, "evaluation.json")
        usage_path = locate(trace_folder, "usage.json")
        invocation_path = locate(trace_folder, "docker_invocation.json")
        trace_path = (locate(trace_folder, "codex_events.jsonl") or locate(trace_folder, "codex_events.jsonl.gz")
                      or locate(trace_folder, "claude_events.jsonl") or locate(trace_folder, "claude_events.jsonl.gz"))
        evaluation = read_json(evaluation_path) if evaluation_path else {}
        usage = read_json(usage_path) if usage_path else {}
        invocation = read_json(invocation_path) if invocation_path else {}
        for p, role in ((prompt_path, "agent_trace"), (answer_path, "final_answer"),
                        (evaluation_path, "evaluator_output"), (usage_path, "usage_record"),
                        (trace_path, "agent_trace")):
            if p:
                artifacts.append({"artifact_id": f"art_{rid}_{role}_{p.name.replace('.', '_')}",
                                  "role": role, "condition": link.condition, "run_id": rid,
                                  "original_name": p.name, "local_path": str(p.relative_to(output)),
                                  "format": p.suffix.lstrip("."), "observed_size": p.stat().st_size,
                                  "sha256": digest(p.read_bytes()), "producing_event_id": None,
                                  "derivation_parent_ids": [], "status": "retained"})
        events.extend(_trace_events(trace_path, rid, trace_sid, link.condition))
        if galaxy.get("contents_path"):
            contents = read_json(output / galaxy["contents_path"])
            hda_to_job = {str(d["id"]): d.get("creating_job") for d in contents if d.get("history_content_type") == "dataset"}
            job_paths = {x["id"]: output / x["path"] for x in galaxy.get("jobs", [])}
            for index, (jid, path) in enumerate(sorted(job_paths.items()), 1):
                job = read_json(path)
                is_fetch = job.get("tool_id") == "__DATA_FETCH__"
                input_hdas = [x for x in _native_hda_ids(job.get("inputs", {})) if x in hda_to_job]
                parent_jids = list(dict.fromkeys(hda_to_job[x] for x in input_hdas if hda_to_job[x] in job_paths and hda_to_job[x] != jid))
                events.append({"event_id": f"evt_galaxy_{rid}_{jid}", "sequence": index,
                               "timestamp": job.get("create_time"), "timestamp_source": "Galaxy job create_time",
                               "event_type": "input_acquisition" if is_fetch else "analysis", "execution_location": "galaxy_job",
                               "native_job_id": jid, "native_input_hda_ids": input_hdas,
                               "parent_event_ids": [f"evt_galaxy_{rid}_{x}" for x in parent_jids],
                               "input_artifact_ids": [f"art_galaxy_{rid}_{x}" for x in input_hdas],
                               "output_artifact_ids": [f"art_galaxy_{rid}_{d['id']}" for d in contents if d.get("creating_job") == jid],
                               "tool": job.get("tool_id"), "tool_version": job.get("command_version"),
                               "command": job.get("command_line"), "parameters": job.get("params"),
                               "status": job.get("state"), "exit_code": job.get("exit_code"),
                               "stdout_excerpt": (job.get("stdout") or job.get("tool_stdout") or "")[:1000],
                               "stderr_excerpt": (job.get("stderr") or job.get("tool_stderr") or "")[:1000],
                               "evidence_refs": [f"{galaxy_sid}:jobs/{jid}.json"],
                               "visibility_limits": "Current public job snapshot; ownership/time window requires original trace"})
            output_by_hda = {o["hda_id"]: o for o in galaxy.get("outputs", [])}
            for d in contents:
                if d.get("history_content_type") != "dataset":
                    continue
                o = output_by_hda.get(d["id"])
                artifacts.append({"artifact_id": f"art_galaxy_{rid}_{d['id']}",
                                  "role": "error_output" if d.get("state") == "error" else "shared_input" if d.get("creating_job") and read_json(job_paths.get(d["creating_job"], Path('/nonexistent'))).get("tool_id") == "__DATA_FETCH__" else "analytical_output",
                                  "condition": link.condition, "run_id": rid, "original_name": d.get("name"),
                                  "local_path": o.get("path") if o else None,
                                  "source_url": o.get("source_url") if o else None,
                                  "format": d.get("extension"), "observed_size": o.get("retained_bytes") if o else d.get("file_size"),
                                  "sha256": o.get("retained_sha256") if o else None,
                                  "producing_event_id": f"evt_galaxy_{rid}_{d['creating_job']}" if d.get("creating_job") in job_paths else None,
                                  "derivation_parent_ids": [f"art_galaxy_{rid}_{x}" for x in next((e["native_input_hda_ids"] for e in events if e.get("native_job_id") == d.get("creating_job")), [])], "status": d.get("state"),
                                  "history_id": galaxy.get("history_id"), "hda_id": d["id"],
                                  "dataset_id": d.get("dataset_id"), "uuid": d.get("uuid"),
                                  "creating_job": d.get("creating_job"), "deleted": d.get("deleted"), "purged": d.get("purged")})
        score_field = None
        score = None
        for candidate in ("accuracy", "output_agreement", "result_evaluation"):
            value = evaluation.get(candidate)
            if isinstance(value, dict) and isinstance(value.get("score"), (int, float)):
                score_field, score = candidate + ".score", value["score"]
                break
        answer = answer_path.read_text().strip() if answer_path else None
        totals = usage.get("totals") or {}
        run = {"run_id": rid, "benchmark": link.benchmark, "task_id": link.task,
               "prompt_variant": huggingface_source(link.trace_url)[2].split("/")[-2] if link.trace_url else None,
               "prompt_sha256": digest(prompt_path.read_bytes()) if prompt_path else None,
               "iteration_setting": read_json(locate(trace_folder, "attempt.json")).get("attempt") if locate(trace_folder, "attempt.json") else None,
               "condition": link.condition, "original_condition_label": link.condition_label,
               "model": {"supplied_label": link.model, "verified_runtime_id": invocation.get("model"),
                         "version": invocation.get("model"), "harness": invocation.get("image"),
                         "reasoning_setting": invocation.get("reasoning_effort") or invocation.get("effort"),
                         "verification_status": "runtime_verified" if invocation.get("model") else "user_supplied_only"},
               "replicate_id": link.replicate, "seed": None,
               "status": "trace_observed" if trace_path else "history_observed" if galaxy.get("contents_path") else "source_incomplete",
               "source_ids": [s for s in (trace_sid if link.trace_url else None, galaxy_sid) if s],
               "timestamps": {"submission": None, "history_create_time": read_json(output / galaxy["history_path"]).get("create_time") if galaxy.get("history_path") else None},
               "budgets": {"time": None, "tokens": None, "retry_policy": None},
               "input_provenance": {"trace_manifest": str(locate(trace_folder, "inputs_manifest.json").relative_to(output)) if locate(trace_folder, "inputs_manifest.json") else None},
               "environment": {"galaxy_server": "https://usegalaxy.org" if link.galaxy_url else None,
                               "docker_image": invocation.get("image"), "galaxy_api_key_mode": invocation.get("galaxy_api_key_mode")},
               "evidence_completeness": {"agent_transcript": "retrieved" if trace_path else "not_collected",
                                         "submitted_answer": "retrieved" if answer_path else "not_collected",
                                         "original_evaluation": "retrieved" if evaluation_path else "not_collected",
                                         "usage": "retrieved" if usage_path else "not_collected",
                                         "public_history_contents": galaxy.get("status") if link.galaxy_url else "not_applicable"},
               "limitations": ["Replicate seeds and independent task selection protocol not supplied"],
               "events": events, "artifacts": artifacts, "solution_route": {},
               "outcome": {"submitted_answer": answer,
                           "submitted_answer_sha256": digest(answer_path.read_bytes()) if answer_path else None,
                           "submission_time": None, "original_evaluator_score": score,
                           "original_evaluator_score_field": score_field,
                           "original_evaluator_mode": evaluation.get("accuracy", {}).get("mode") if isinstance(evaluation.get("accuracy"), dict) else None,
                           "original_evaluator_record": f"{trace_sid}:evaluation.json" if evaluation_path else None,
                           "step_completion": evaluation.get("step_completion"),
                           "execution_completion": "trace_observed" if trace_path else None,
                           "prompt_compliance": None, "auditor_scientific_interpretation": None,
                           "result_status": "fixed submitted answer and original evaluator observed" if answer_path and score is not None else "incomplete"},
               "recovery_episodes": [],
               "usage": {"provider_reported_input_tokens": totals.get("input_tokens"),
                         "provider_reported_output_tokens": totals.get("output_tokens"),
                         "provider_reported_cached_input_tokens": totals.get("cached_input_tokens"),
                         "provider_reported_reasoning_tokens": totals.get("reasoning_output_tokens"),
                         "source_id": trace_sid if usage_path else None,
                         "accounting_note": "Cached input is a subset of input; reasoning output may be included in output",
                         "missingness": None if usage_path else "not_collected"},
               "derived_metrics": {"completed_shell_calls": sum(e.get("tool") == "shell" for e in events),
                                   "nonzero_exit_shell_calls": sum(e.get("tool") == "shell" and e.get("exit_code") not in (None, 0) for e in events),
                                   "completed_mcp_calls": sum(bool(e.get("is_mcp_call")) for e in events),
                                   "analytical_job_count": sum(e["event_type"] == "analysis" and e["execution_location"] == "galaxy_job" for e in events) if galaxy.get("contents_path") else None,
                                   "total_failed_jobs": sum(e["event_type"] == "analysis" and e["execution_location"] == "galaxy_job" and e.get("status") in {"error", "failed"} for e in events) if galaxy.get("contents_path") else None,
                                   "failed_jobs_before_first_supported_result": None,
                                   "failed_attempts_before_first_correct_answer": None}}
        if link.galaxy_url and galaxy.get("history_id") in galaxy_seen and galaxy_seen[galaxy["history_id"]] != rid:
            run["limitations"].append(f"Public history also linked to {galaxy_seen[galaxy['history_id']]}; job inventory is shared")
        if link.galaxy_url and galaxy.get("status") == "history_metadata_only":
            run["limitations"].append("Public contents and jobs unavailable; trace evidence remains separate")
        run["solution_route"] = _solution_route(run)
        run["recovery_episodes"] = _recovery_candidates(run)
        recovered.extend(_extract_code(output, run, trace_sid))
        runs.append(run)
        run_inventory.append({"run_id": rid, "benchmark": link.benchmark, "task": link.task,
                              "model_label": link.model, "condition": link.condition, "condition_label": link.condition_label,
                              "replicate": link.replicate, "sheet": link.sheet, "row": link.row,
                              "galaxy_url": link.galaxy_url, "trace_url": link.trace_url,
                              "status": run["status"]})
        write_json(output / "job_ledgers" / link.condition / f"{rid}.json",
                   {"run_id": rid, "events": events, "note": "Native calls and jobs are not equated to scientific attempts"})
    task_meta = _read_task(links[0].benchmark, links[0].task, repo_root,
                           [output / "source_snapshots/huggingface_traces/files" / r.run_id for r in links])
    input_manifest = _input_manifest(output, runs)
    write_json(output / "input_manifest.json", input_manifest)
    write_json(output / "run_manifest.json", {"inventory_source": str(workbook_path),
                                               "inventory_source_sha256": digest(workbook_path.read_bytes()),
                                               "expected_coverage": "unknown_without_independent_protocol",
                                               "observed_rows": run_inventory})
    write_json(output / "recovered_code/manifest.json", {"execution_claim": "Archival extraction only; no recovered code executed",
                                                              "items": recovered,
                                                              "missingness": "Only recognizable command strings and Python heredocs extracted"})
    write_json(output / "selected_outputs/galaxy/manifest.json",
               {"histories": {hid: read_json(output / "source_snapshots/galaxy" / hid / "manifest.json").get("outputs", []) for hid in galaxy_seen},
                "selection_rule": "Accessible successful non-fetch datasets no larger than the configured byte cap"})
    task_ref = {"benchmark": links[0].benchmark, "task_id": links[0].task, **task_meta, "hidden_reference_included": False}
    write_json(output / f"{links[0].task}.json", task_ref)
    evidence = {"schema_version": "2.0",
                "audit": {"audit_id": f"{links[0].benchmark}-{links[0].task}-{now}", "timestamp_utc": now,
                          "auditor_software": "analysis_execution 1.0", "scope": "selected task links from supplied workbook",
                          "source_snapshot": str(workbook_path),
                          "limitations": ["Retrospective case; supplied links are not an independent protocol inventory", "Recovered code was not executed; hidden reference was not opened"]},
                "task": {"benchmark": links[0].benchmark, "task_id": links[0].task,
                         "prompt": task_meta.get("prompt"), "prompt_version": task_meta.get("allowed_task_metadata_sha256"),
                         "input_specification": task_meta.get("source_dataset"),
                         "evaluation_definition": "Original per-run evaluator fields retained without regrading; benchmark-specific scoring requires original specification"},
                "experimental_design": {"conditions": sorted({x.condition for x in links}),
                                        "coverage_status": "unknown_protocol_inventory",
                                        "matching_rule": "Same task and supplied model label; replicate numbers are labels, not matched seeds",
                                        "expected_replicates": None, "seed_availability": "not_collected",
                                        "known_confounders": ["Condition-specific prompts and tools", "Container revisions may differ", "Shared source histories may occur"]},
                "sources": sources, "runs": runs, "comparisons": [], "manuscript_findings": [],
                "validation": {"schema": {"path": "history_analysis_evidence.schema.json", "dialect": "https://json-schema.org/draft/2020-12/schema",
                                          "sha256": None, "validation_status": "pending"},
                               "reference_integrity": "pending", "hash_size_and_count_checks": "pending",
                               "unresolved_issues": []}}
    if any(s.get("tls_certificate_verified") is False for s in sources):
        evidence["audit"]["limitations"].append("Source TLS certificates were not verified because the host proxy presented an invalid certificate; local retained-byte hashes do not authenticate the remote server")
    evidence["comparisons"] = make_comparisons(runs)
    evidence["manuscript_findings"] = make_findings(runs, evidence["comparisons"])
    schema_path = output / "history_analysis_evidence.schema.json"
    evidence["validation"]["schema"]["sha256"] = digest(schema_path.read_bytes())
    write_json(output / "history_analysis_evidence.json", evidence)
    return evidence


def make_comparisons(runs: list[dict]) -> list[dict]:
    groups = defaultdict(lambda: defaultdict(list))
    for r in runs:
        groups[r["model"]["supplied_label"]][r["condition"]].append(r)
    result = []
    for model, by_condition in sorted(groups.items()):
        name = re.sub(r"[^a-z0-9]+", "_", model.lower()).strip("_")
        code = by_condition.get("open_ended_code", [])
        galaxy = by_condition.get("galaxy", [])
        score_fields = {r["outcome"]["original_evaluator_score_field"] for r in code + galaxy if r["outcome"]["original_evaluator_score"] is not None}
        runtime_ids = {r["model"]["verified_runtime_id"] for r in code + galaxy}
        same_verified_model = len(runtime_ids) == 1 and None not in runtime_ids
        complete = bool(code and galaxy and same_verified_model and len(score_fields) == 1 and all(r["outcome"]["original_evaluator_score"] is not None for r in code + galaxy))
        if complete:
            gmean = statistics.mean(r["outcome"]["original_evaluator_score"] for r in galaxy)
            cmean = statistics.mean(r["outcome"]["original_evaluator_score"] for r in code)
        is_binary_accuracy = complete and all(r["benchmark"] == "bixbench" for r in code + galaxy) and score_fields == {"accuracy.score"} and all(r["outcome"]["original_evaluator_score"] in {0, 1} for r in code + galaxy)
        result.append({"comparison_id": f"score_{name}", "status": "descriptive_only" if complete else "not_assessable",
                       "included_run_ids": [r["run_id"] for r in galaxy + code if r["outcome"]["original_evaluator_score"] is not None],
                       "excluded_run_ids": [r["run_id"] for r in galaxy + code if r["outcome"]["original_evaluator_score"] is None],
                       "score_field": next(iter(score_fields)) if len(score_fields) == 1 else None,
                       "galaxy_n": len(galaxy), "code_n": len(code),
                       "galaxy_mean": gmean if complete else None, "code_mean": cmean if complete else None,
                       "estimate": (100 if is_binary_accuracy else 1) * (gmean - cmean) if complete else None,
                       "estimate_unit": "percentage points Galaxy minus code" if is_binary_accuracy else "score-scale difference Galaxy minus code" if complete else None,
                       "uncertainty": None,
                       "limitation": "One selected task; original scoring definitions and prompt differences must be checked before interpretation. Runtime model ID must match across conditions."})
        gtok = [r["usage"]["provider_reported_input_tokens"] for r in galaxy]
        ctok = [r["usage"]["provider_reported_input_tokens"] for r in code]
        token_complete = bool(gtok and ctok and same_verified_model and all(isinstance(x, (int, float)) and x >= 0 for x in gtok + ctok) and statistics.median(ctok) > 0)
        result.append({"comparison_id": f"input_tokens_{name}", "status": "descriptive_only" if token_complete else "not_assessable",
                       "included_run_ids": [r["run_id"] for r in galaxy + code if r["usage"]["provider_reported_input_tokens"] is not None],
                       "excluded_run_ids": [r["run_id"] for r in galaxy + code if r["usage"]["provider_reported_input_tokens"] is None],
                       "galaxy_n": len(gtok), "code_n": len(ctok),
                       "galaxy_median": statistics.median(gtok) if token_complete else None,
                       "code_median": statistics.median(ctok) if token_complete else None,
                       "estimate": statistics.median(gtok) / statistics.median(ctok) if token_complete else None,
                       "estimate_unit": "ratio of condition medians" if token_complete else None,
                       "uncertainty": None, "limitation": "Provider input-token totals include cached input; no stage-level attribution"})
    return result


def make_findings(runs: list[dict], comparisons: list[dict]) -> list[dict]:
    ids = [r["run_id"] for r in runs]
    all_scored = [r for r in runs if r["outcome"]["original_evaluator_score"] is not None]
    galaxy_jobs = {(r["environment"]["galaxy_server"], e["native_job_id"]): e for r in runs for e in r["events"] if e["execution_location"] == "galaxy_job" and e["event_type"] == "analysis"}
    failed = [e for e in galaxy_jobs.values() if e.get("status") in {"error", "failed"}]
    findings = []
    specs = [
        ("accuracy", "What original evaluator scores are observable?", f"Original evaluator scores were retrieved for {len(all_scored)}/{len(runs)} supplied runs; condition differences are descriptive only." if all_scored else None,
         [r["run_id"] for r in all_scored], [r["outcome"]["original_evaluator_record"] for r in all_scored], len(all_scored), len(runs), "observed" if all_scored else "not_assessable"),
        ("execution", "What Galaxy processing and failures are visible?", f"{len(galaxy_jobs)} distinct public analytical creating jobs and {len(failed)} failed jobs are visible in retrieved histories." if galaxy_jobs else None,
         ids, [e["event_id"] for e in galaxy_jobs.values()], len(failed) if galaxy_jobs else None, len(galaxy_jobs) if galaxy_jobs else None, "observed" if galaxy_jobs else "not_assessable"),
        ("variability", "Which tool families occur across routes?", "Tool-family and command indicators are catalogued per run; biological equivalence requires task-specific review." if any(r["solution_route"]["classification"] for r in runs) else None,
         ids, [r["source_ids"][0] for r in runs if r["source_ids"]], None, None, "observed"),
        ("cost_readability", "What provider token totals and readability results exist?", "Input-token ratios of condition medians are reported only where both conditions have provider totals; human readability was not measured.",
         ids, [r["usage"]["source_id"] for r in runs if r["usage"]["source_id"]], None, None, "observed")]
    for section, question, claim, eligible, refs, num, den, status in specs:
        findings.append({"finding_id": f"finding_{section}", "section": section, "question": question,
                         "claim": claim, "scope": "case_study", "unit_of_analysis": "event" if section == "execution" else "run",
                         "eligible_run_ids": eligible, "evidence_refs": sorted(set(ref for ref in refs if ref)),
                         "contradictory_evidence_refs": [], "numerator": num, "denominator": den,
                         "estimate": num / den if num is not None and den else None,
                         "uncertainty": None, "missingness": None if refs else "not_collected",
                         "limitations": ["Selected task and supplied links only", "No independent task-level interval"],
                         "interpretation_status": status})
    return findings
