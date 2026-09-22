"""Recover CompBio metadata and usage from retained bytes; never grade answers."""
import gzip
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "analysis_execution"))
from build import locate, make_comparisons, make_findings, read_json
from collect import digest, write_json
from report import render
from validate import validate


def trace_usage(path):
    """A single completed-turn record is unambiguous; multiple totals stay unknown."""
    if not path:
        return {}, [], "trace_absent", {}
    raw = gzip.decompress(path.read_bytes()).decode() if path.suffix == ".gz" else path.read_text()
    terminal, types, malformed = [], {}, 0
    for line, text in enumerate(raw.splitlines(), 1):
        try:
            item = json.loads(text)
        except json.JSONDecodeError:
            malformed += 1
            continue
        kind = item.get("type", "unknown")
        types[kind] = types.get(kind, 0) + 1
        if kind == "turn.completed" and isinstance(item.get("usage"), dict):
            terminal.append((line, item["usage"]))
    if len(terminal) == 1 and not malformed:
        return terminal[0][1], [terminal[0][0]], None, types
    return {}, [x[0] for x in terminal], "ambiguous_multiple_turn_totals" if len(terminal) > 1 else "no_complete_usage_record", types


def enrich(folder):
    evidence_path = folder / "history_analysis_evidence.json"
    evidence = read_json(evidence_path)
    backup = folder / "versions/pre_compbio_synthesis"
    backup.mkdir(parents=True, exist_ok=True)
    for name in ("README.md", "history_analysis.md", "history_analysis_evidence.json", folder.name + ".json"):
        if not (backup / name).exists():
            shutil.copy2(folder / name, backup / name)
    metadata = None
    metadata_path = None
    for run in evidence["runs"]:
        source = folder / "source_snapshots/huggingface_traces/files" / run["run_id"]
        task_path = locate(source, "task.json")
        task = read_json(task_path) if task_path else {}
        if task.get("metadata", {}).get("question") and metadata is None:
            metadata = task["metadata"]
            metadata_path = task_path
        trace = locate(source, "codex_events.jsonl") or locate(source, "codex_events.jsonl.gz")
        totals, lines, missing, types = trace_usage(trace)
        if totals:
            run["usage"].update({"provider_reported_input_tokens": totals.get("input_tokens"),
                                 "provider_reported_output_tokens": totals.get("output_tokens"),
                                 "provider_reported_cached_input_tokens": totals.get("cached_input_tokens"),
                                 "provider_reported_reasoning_tokens": totals.get("reasoning_output_tokens"),
                                 "source_id": "src_trace_" + run["run_id"], "missingness": None})
        else:
            run["usage"]["missingness"] = missing
        run["usage"].update({"extraction": "Single turn.completed provider usage record; no cumulative snapshots summed",
                             "source_path": str(trace.relative_to(folder)) if trace else None, "source_lines": lines,
                             "aggregation_scope": "Archived primary agent turn only; earlier campaigns and separate subagents not established"})
        run["evidence_completeness"]["usage"] = "retrieved" if totals else "not_collected"
        run["derived_metrics"]["trace_record_types"] = types
        inv_path = locate(source, "docker_invocation.json") or locate(source, "conda_invocation.json")
        invocation = read_json(inv_path) if inv_path else {}
        if invocation.get("model"):
            run["model"].update({"verified_runtime_id": invocation["model"], "version": invocation["model"],
                                  "harness": inv_path.name.removesuffix("_invocation.json"),
                                  "reasoning_setting": invocation.get("reasoning_effort"), "verification_status": "runtime_verified",
                                  "source_path": str(inv_path.relative_to(folder))})
        run["budgets"]["time"] = {"timeout_minutes": task.get("timeout_minutes"), "timeout_seconds": invocation.get("timeout_seconds")}
        run["timestamps"]["prepared_at"] = task.get("created_at")
        run["outcome"]["evaluation_limitation"] = "evaluation.stdout.txt is submission-format validation, not per-task correctness. Aggregate leaderboard claims are reported separately."
        for path, role in ((task_path, "agent_trace"), (inv_path, "agent_trace")):
            if path and not any(a.get("local_path") == str(path.relative_to(folder)) for a in run["artifacts"]):
                run["artifacts"].append({"artifact_id": f"art_{run['run_id']}_{path.name.replace('.', '_')}", "role": role,
                    "condition": run["condition"], "run_id": run["run_id"], "original_name": path.name,
                    "local_path": str(path.relative_to(folder)), "format": "json", "observed_size": path.stat().st_size,
                    "sha256": digest(path.read_bytes()), "producing_event_id": None, "derivation_parent_ids": [], "status": "retained"})
    if metadata:
        evidence["task"].update({"prompt": metadata["question"], "prompt_version": digest(metadata_path.read_bytes()),
                                 "input_specification": metadata.get("requested_file_paths"),
                                 "metadata_source": str(metadata_path.relative_to(folder)),
                                 "domain": metadata.get("domain"), "question_style": metadata.get("question_style"),
                                 "evaluation_definition": "Prompt requests exact-string final answers; per-item evaluator outcomes unavailable. Aggregate official-labelled and predicted scores are kept separate in CompBio overview."})
        task_ref = read_json(folder / (folder.name + ".json"))
        task_ref.update({"prompt": metadata["question"], "allowed_task_metadata": str(metadata_path.relative_to(ROOT)),
                         "allowed_task_metadata_sha256": digest(metadata_path.read_bytes())})
        write_json(folder / (folder.name + ".json"), task_ref)
    evidence["audit"]["supplemental_extraction"] = "scripts/enrich_compbio_evidence.py; original report/evidence in versions/pre_compbio_synthesis"
    evidence["comparisons"] = make_comparisons(evidence["runs"])
    evidence["manuscript_findings"] = make_findings(evidence["runs"], evidence["comparisons"])
    write_json(evidence_path, evidence)
    render(folder, evidence)
    p = folder / "history_analysis.md"
    p.write_text(p.read_text().replace("Per-run `usage.json`", "Per-run provider usage records (including `turn.completed` trace lines)").replace("No per-call usage, dated prices", "No stage-attributed usage, dated prices") +
                 "\n## CompBio source recovery\n\nThe task prompt was recovered from `task.json:metadata.question`; token totals from a single provider `turn.completed` usage record where present. Exact source paths and lines are in the evidence JSON. Multiple terminal totals remain unknown rather than being summed. `evaluation.stdout.txt` reports vector format validation, not answer correctness. Official-labelled aggregate scores and predictions are documented separately in `CompBio/compBio_overview.md`. Earlier source campaigns, absent primary traces and unmeasured review effort remain limitations.\n")
    validate(folder, mark_passed=False)
    return sum(r["usage"]["provider_reported_input_tokens"] is not None for r in evidence["runs"])


if __name__ == "__main__":
    total = 0
    for i, folder in enumerate(sorted((ROOT / "CompBio/analysis").iterdir()), 1):
        if not (folder / "history_analysis_evidence.json").exists():
            continue
        total += enrich(folder)
        if i % 10 == 0:
            print(f"Validated {i} task packages; {total} recovered usage records", flush=True)
