"""Build a retrospective audit from public snapshots; never run agent code."""
import hashlib
import json
import pathlib
import re
import csv
import statistics
from collections import Counter
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent
REPO = ROOT.parents[1]
SNAP = ROOT / "source_snapshots" / "galaxy"
LABELS = {"gpt55": "Codex GPT-5.5", "sol": "Codex GPT-5.6 Sol", "luna": "Codex GPT-5.6 Luna", "deepseek": "DeepSeek V4 Pro via Codex"}
HF_ROOTS = {"gpt55": "run_traces_tokens_cut_jul14", "sol": "run_traces_july31_codex_gpt56_sol", "luna": "run_traces_july31_codex_gpt56_luna", "deepseek": "run_traces_august15_codex_deepseek_v4pro"}


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def redact(value):
    if isinstance(value, dict):
        return {k: ("[redacted]" if k in {"user_email", "user_id", "username", "username_and_slug"} else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


def finding(fid, section, question, claim, ids, refs, *, unit="run", num=None, den=None, status="observed", missing=None, limits=None):
    return {"finding_id": fid, "section": section, "question": question, "claim": claim, "scope": "case_study", "unit_of_analysis": unit, "eligible_run_ids": ids, "evidence_refs": refs, "contradictory_evidence_refs": [], "numerator": num, "denominator": den, "estimate": None if num is None or den in (None, 0) else num / den, "uncertainty": None, "missingness": missing, "limitations": limits or [], "interpretation_status": status}


def main():
    now = datetime.now(timezone.utc).isoformat()
    task_path = REPO / "experiments/BixBench/task_1.json"
    task = json.loads(task_path.read_text())
    # Preserve public source responses only after removing unnecessary account IDs.
    for path in SNAP.rglob("*.json"):
        obj = json.loads(path.read_text())
        dump(path, redact(obj))
    sources, runs, inventory, inputs, recovered = [], [], [], {}, []
    output_manifest_path = ROOT / "selected_outputs/galaxy/manifest.json"
    output_manifest = json.loads(output_manifest_path.read_text()) if output_manifest_path.exists() else {"outputs": [], "errors": []}
    output_by_hda = {x["hda_id"]: x for x in output_manifest["outputs"]}
    first_twenty_ids = []
    for model_key in LABELS:
        for rep in (1, 2, 3):
            label = f"{model_key}_r{rep}"
            folder_label = "sol_r2_r3" if label in {"sol_r2", "sol_r3"} else label
            folder = SNAP / folder_label
            h = json.loads((folder / "history.json").read_text())
            detailed = (folder / "contents.json").exists()
            ds = json.loads((folder / "contents.json").read_text()) if detailed else []
            jobs = [json.loads(p.read_text()) for p in (folder / "jobs").glob("*.json")]
            jobs.sort(key=lambda x: (x.get("create_time") or "", x["id"]))
            hda_to_job = {d["id"]: d.get("creating_job") for d in ds if d.get("history_content_type") == "dataset"}
            def native_input_ids(value):
                if isinstance(value, dict):
                    found = [value["id"]] if value.get("src") in {"hda", "ldda"} and value.get("id") else []
                    for child in value.values():
                        found.extend(native_input_ids(child))
                    return found
                if isinstance(value, list):
                    return [item for child in value for item in native_input_ids(child)]
                return []
            input_hdas_by_job = {j["id"]: list(dict.fromkeys(x for x in native_input_ids(j.get("inputs", {})) if x in hda_to_job)) for j in jobs}
            hid = h["id"]
            rid = f"galaxy_{label}"
            sid = f"src_galaxy_{folder_label}"
            if not any(x["source_id"] == sid for x in sources):
                sources.append({"source_id": sid, "location": f"https://usegalaxy.org/histories/view?id={hid}", "local_snapshot": str(folder.relative_to(ROOT)), "retrieval_time_utc": json.loads((SNAP / "retrieval_manifest.json").read_text())["retrieved_at_utc"], "access_status": "public_api_retrieved" if detailed else "history_metadata_only_contents_timeout", "redactions": ["Galaxy account ID, username and email removed from retained JSON; original source bytes not retained"], "sha256_history_snapshot": sha(folder / "history.json"), "sha256_contents_snapshot": sha(folder / "contents.json") if detailed else None, "evidence_completeness": "Current history and creating-job snapshot; original agent transcript and submission not available" if detailed else "Only top-level history metadata; 8801 reported contents; contents and jobs not retrieved"})
            events, artifacts = [], []
            for n, j in enumerate(jobs, 1):
                jid = j["id"]
                is_fetch = j.get("tool_id") == "__DATA_FETCH__"
                input_hdas = input_hdas_by_job[jid]
                parent_jobs = list(dict.fromkeys(hda_to_job[x] for x in input_hdas if hda_to_job.get(x) and hda_to_job[x] != jid))
                events.append({"event_id": f"evt_{label}_{jid}", "sequence": n, "timestamp": j.get("create_time"), "timestamp_source": "Galaxy job create_time", "event_type": "input_acquisition" if is_fetch else "analysis", "execution_location": "galaxy_job", "native_job_id": jid, "parent_event_ids": [f"evt_{label}_{x}" for x in parent_jobs], "input_artifact_ids": [f"art_{label}_{x}" for x in input_hdas], "output_artifact_ids": [f"art_{label}_{d['id']}" for d in ds if d.get("creating_job") == jid], "tool": j.get("tool_id"), "tool_version": j.get("command_version") or (j.get("tool_id") or "").split("/")[-1], "parameters": j.get("params"), "status": j.get("state"), "exit_code": j.get("exit_code"), "stdout": j.get("stdout") or j.get("tool_stdout"), "stderr": j.get("stderr") or j.get("tool_stderr"), "evidence_refs": [f"{sid}:jobs/{jid}.json"], "visibility_limits": "Job snapshot is not the agent transcript", "attributable_to_run": not is_fetch and j.get("history_id") == hid})
                if not is_fetch:
                    cmd = j.get("command_line") or ""
                    match = re.search(r"cat\s*>\s*([^\s]+\.py)\s*<<['\"]?([A-Za-z_]+)['\"]?\n(.*?)\n\2(?:\n|$)", cmd, re.S)
                    if match:
                        code = match.group(3) + "\n"
                        dest = ROOT / "recovered_code/galaxy" / folder_label / f"{jid}_{pathlib.Path(match.group(1)).name}"
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        dest.write_text(code)
                        if not any(x["path"] == str(dest.relative_to(ROOT)) for x in recovered):
                            recovered.append({"run_ids": [rid], "job_id": jid, "path": str(dest.relative_to(ROOT)), "sha256": sha(dest), "source": f"{sid}:jobs/{jid}.json#command_line", "extraction": "Literal Python heredoc body; not executed or validated"})
            for d in ds:
                if d.get("history_content_type") != "dataset":
                    continue
                aid = f"art_{label}_{d['id']}"
                o = output_by_hda.get(d["id"])
                artifacts.append({"artifact_id": aid, "role": "shared_input" if d.get("hid", 0) <= 20 else ("error_output" if d.get("state") == "error" else "analytical_output"), "condition": "galaxy", "run_id": rid, "original_name": d.get("name"), "local_path": o["path"] if o else None, "source_url": o["source_url"] if o else "https://usegalaxy.org" + d.get("download_url", ""), "format": d.get("extension"), "observed_size": o["bytes"] if o else d.get("file_size"), "sha256": o["sha256"] if o else None, "source_reported_hashes": d.get("hashes", []), "producing_event_id": f"evt_{label}_{d['creating_job']}" if d.get("creating_job") else None, "derivation_parent_ids": [f"art_{label}_{x}" for x in input_hdas_by_job.get(d.get("creating_job"), [])], "status": d.get("state"), "history_id": hid, "hda_id": d["id"], "dataset_id": d.get("dataset_id"), "uuid": d.get("uuid"), "creating_job": d.get("creating_job"), "hid": d.get("hid"), "deleted": d.get("deleted"), "purged": d.get("purged")})
            if not first_twenty_ids:
                first_twenty_ids = [{"name": d.get("name"), "hda_id": d["id"], "dataset_id": d.get("dataset_id"), "uuid": d.get("uuid"), "source_reported_hashes": d.get("hashes", [])} for d in ds if d.get("hid", 0) <= 20 and d.get("history_content_type") == "dataset"]
            analytic = [j for j in jobs if j.get("tool_id") != "__DATA_FETCH__" and j.get("history_id") == hid]
            failures = [j for j in analytic if j.get("state") in {"error", "failed", "deleted"} or j.get("exit_code") not in (None, 0)]
            tool_ids = list(dict.fromkeys(j["tool_id"] for j in analytic))
            route = "installed PhyKIT metrics" if tool_ids and all("phykit_metrics" in t for t in tool_ids) else ("custom Galaxy-hosted code" if any("phykit_metrics" not in t for t in tool_ids) else "unclassified")
            if any("phykit_metrics" in t for t in tool_ids) and route == "custom Galaxy-hosted code":
                route = "installed PhyKIT metrics plus custom Galaxy-hosted code"
            run = {"run_id": rid, "benchmark": "BixBench", "task_id": "bix-11-q1", "prompt_variant": "galaxy_strict_skills", "iteration_setting": None, "condition": "galaxy", "model": {"supplied_label": LABELS[model_key], "verified_runtime_id": None, "version": None, "harness": "Codex (supplied label); runtime metadata unavailable", "reasoning_setting": None, "verification_status": "user_supplied_only"}, "replicate_id": rep, "seed": None, "status": "history_metadata_only" if not detailed else ("history_observed_duplicate_link" if label == "sol_r3" else "history_observed"), "source_ids": [sid], "timestamps": {"history_create_time": h.get("create_time"), "history_update_time": h.get("update_time"), "agent_start": None, "submission": None}, "budgets": {"time": None, "tokens": None, "retry_policy": None}, "input_provenance": {"observed_hda_count_hid_1_to_20": sum(1 for d in ds if d.get("hid", 0) <= 20 and d.get("history_content_type") == "dataset") if detailed else None, "shared_import_ownership": "Creating fetch jobs predate these histories; independent agent uploads not established" if detailed else "unknown"}, "environment": {"server": "https://usegalaxy.org", "galaxy_version": next((j.get("galaxy_version") for j in analytic if j.get("galaxy_version")), None), "local_analysis_observed": None, "external_analytical_service_observed": None}, "evidence_completeness": {"history_and_job_snapshot": "retrieved" if detailed else "not_observable_contents_timeout", "analytical_output_bytes": "selected small datasets retrieved; see manifest" if detailed else "not_collected", "agent_transcript": "not_collected", "submitted_answer": "not_collected", "official_evaluation": "not_collected", "tokens": "not_collected"}, "limitations": ["A current history snapshot does not establish original agent chronology or actions outside Galaxy"] + (["Same history ID supplied for Sol replicates 2 and 3; independent replication cannot be verified"] if label in {"sol_r2", "sol_r3"} else []) + (["8801 reported contents; contents API timed out even with 5-item pagination"] if not detailed else []), "events": events, "artifacts": artifacts, "solution_route": {"codebook": {"biological_method": "Per-tree treeness then group median difference when evidenced", "tool_family": route, "external_resource_version": None, "validation": "not observable from history alone"}, "tool_ids": tool_ids, "classification": route if detailed else None}, "outcome": {"submitted_answer": None, "submission_time": None, "official_bixbench_answer_score": None, "official_evaluator_version": None, "execution_completion": ("all observed analytical jobs succeeded" if not failures else "observed errors") if detailed else None, "prompt_compliance": None, "auditor_scientific_interpretation": None, "result_status": "history_output_observed; submitted answer unavailable" if detailed else "not_assessable"}, "recovery_episodes": [], "usage": {"provider_reported_input_tokens": None, "provider_reported_output_tokens": None, "provider_reported_cached_input_tokens": None, "provider_reported_reasoning_tokens": None, "missingness": "not_collected"}, "derived_metrics": {"analytical_job_count": len(analytic) if detailed else None, "total_failed_jobs": len(failures) if detailed else None, "failed_jobs_before_first_supported_result": None, "failed_attempts_before_first_correct_answer": None, "distinct_tool_ids": len(tool_ids) if detailed else None, "endpoint_censoring": "submission and correctness endpoint unavailable"}}
            if label == "luna_r3":
                failed = next((j for j in analytic if j.get("state") == "error" and "datamash_ops" in j.get("tool_id", "")), None)
                repaired = next((j for j in analytic if j.get("state") == "ok" and "datamash_ops" in j.get("tool_id", "")), None)
                if failed and repaired:
                    run["recovery_episodes"].append({"episode_id": "recovery_luna_r3_datamash", "trigger": "Datamash rejected text 'treeness' as numeric input", "failure_type": "analytical_error", "failed_event_ids": [f"evt_{label}_{failed['id']}"], "diagnosis_evidence": [f"{sid}:jobs/{failed['id']}.json#stderr"], "corrective_action": "Changed median column from 4 to 5 on the same input HDA", "recovery_event_ids": [f"evt_{label}_{repaired['id']}"], "same_goal_linkage": "Both jobs group by column 1 and compute a median from the same input", "eventual_outcome": "Operationally resolved; correct fixed answer not established"})
            selected = [(d, output_by_hda.get(d["id"])) for d in ds if d.get("id") in output_by_hda]
            interpretation = None
            if label in {"gpt55_r1", "gpt55_r3"}:
                direct = next(((d, o) for d, o in selected if d.get("hid") == 22), None)
                if direct:
                    try:
                        value = float((ROOT / direct[1]["path"]).read_text().strip())
                        interpretation = {"fungi_minus_animals": value, "basis": "explicit Galaxy analytical output", "evidence_refs": [f"art_{label}_{direct[0]['id']}"]}
                    except ValueError:
                        pass
            if interpretation is None:
                groups, refs, seen_metric_rows = {}, [], set()
                duplicate_metric_rows = 0
                for d, o in selected:
                    try:
                        with (ROOT / o["path"]).open() as stream:
                            rows = list(csv.DictReader(stream, delimiter="\t"))
                        if not rows or not {"group", "value"}.issubset(rows[0]):
                            continue
                        seen = False
                        for row in rows:
                            group = (row.get("group") or "").strip().lower()
                            if group in {"animals", "fungi"}:
                                key = (group, row.get("file_id"), row.get("file_name"), row.get("metric"), row.get("value"))
                                if key in seen_metric_rows:
                                    duplicate_metric_rows += 1
                                    continue
                                seen_metric_rows.add(key)
                                groups.setdefault(group, []).append(float(row["value"]))
                                seen = True
                        if seen:
                            refs.append(f"art_{label}_{d['id']}")
                    except (ValueError, UnicodeDecodeError, OSError):
                        pass
                if all(groups.get(g) for g in ("animals", "fungi")):
                    am, fm = statistics.median(groups["animals"]), statistics.median(groups["fungi"])
                    interpretation = {"fungi_minus_animals": fm - am, "animal_median": am, "fungal_median": fm, "basis": "auditor median from saved Galaxy per-tree values", "observed_unique_value_rows": {g: len(groups[g]) for g in ("animals", "fungi")}, "duplicate_repeated_output_rows_dropped": duplicate_metric_rows, "evidence_refs": refs}
            run["outcome"]["auditor_scientific_interpretation"] = interpretation
            if interpretation:
                run["outcome"]["result_status"] = "explicit Galaxy output; submission unavailable" if interpretation["basis"].startswith("explicit") else "reconstructable from Galaxy output; submission unavailable"
            runs.append(run)
            dump(ROOT / "job_ledgers/galaxy" / f"{rid}.json", {"run_id": rid, "history_id": hid, "events": events})
            inventory.append({"run_id": rid, "condition": "galaxy", "model_label": LABELS[model_key], "replicate_id": rep, "source_id": sid, "status": run["status"]})
            # Each code-side source is a distinct user-supplied trace URL. Public API currently returns 401.
            code_rid = f"open_ended_code_{label}"
            code_sid = f"src_code_{label}"
            code_url = f"https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces/tree/main/bixbench/{HF_ROOTS[model_key]}/bix_11_q1/anycode_nongalaxy_skills/replicate_{rep}"
            sources.append({"source_id": code_sid, "location": code_url, "retrieval_time_utc": now, "access_status": "HTTP_401_unauthorized", "access_status_snapshot": "source_snapshots/huggingface_response.json", "sha256_access_response": sha(ROOT / "source_snapshots/huggingface_response.json"), "redactions": [], "evidence_completeness": "No transcript, outputs, usage or evaluator record retrieved"})
            code_run = {"run_id": code_rid, "benchmark": "BixBench", "task_id": "bix-11-q1", "prompt_variant": "anycode_nongalaxy_skills", "iteration_setting": None, "condition": "open_ended_code", "model": {"supplied_label": LABELS[model_key], "verified_runtime_id": None, "version": None, "harness": "Codex (supplied label); runtime metadata unavailable", "reasoning_setting": None, "verification_status": "user_supplied_only"}, "replicate_id": rep, "seed": None, "status": "source_inaccessible", "source_ids": [code_sid], "timestamps": {"agent_start": None, "submission": None}, "budgets": {"time": None, "tokens": None, "retry_policy": None}, "input_provenance": {"status": "not_collected"}, "environment": {"status": "not_collected"}, "evidence_completeness": {"events": "not_collected", "artifacts": "not_collected", "submitted_answer": "not_collected", "official_evaluation": "not_collected", "tokens": "not_collected"}, "limitations": ["Hugging Face trace source returned HTTP 401; no run-level conclusions possible"], "events": [], "artifacts": [], "solution_route": {"classification": None, "missingness": "not_collected"}, "outcome": {"submitted_answer": None, "official_bixbench_answer_score": None, "execution_completion": None, "prompt_compliance": None, "auditor_scientific_interpretation": None, "result_status": "not_assessable"}, "recovery_episodes": [], "usage": {"provider_reported_input_tokens": None, "provider_reported_output_tokens": None, "provider_reported_cached_input_tokens": None, "provider_reported_reasoning_tokens": None, "missingness": "not_collected"}, "derived_metrics": {"analytical_job_count": None, "total_failed_jobs": None, "failed_jobs_before_first_supported_result": None, "failed_attempts_before_first_correct_answer": None, "endpoint_censoring": "all events and outcomes unavailable"}}
            runs.append(code_run)
            inventory.append({"run_id": code_rid, "condition": "open_ended_code", "model_label": LABELS[model_key], "replicate_id": rep, "source_id": code_sid, "status": "source_inaccessible"})
    for item in recovered:
        if item["job_id"]:
            folder = item["path"].split("/")[2]
            if folder == "sol_r2_r3":
                item["run_ids"] = ["galaxy_sol_r2", "galaxy_sol_r3"]
    dump(ROOT / "recovered_code/manifest.json", {"galaxy_extractions": recovered, "open_ended_code": {"status": "not_collected", "reason": "HF trace source HTTP 401"}, "execution_claim": "No extracted code was run by this audit"})
    dump(ROOT / "run_manifest.json", {"task_id": "bix-11-q1", "inventory_basis": "24 model/condition/replicate links supplied by user; no experiment protocol or manifest retrieved", "expected_coverage": "unknown", "observed_source_links": len(inventory), "unique_galaxy_history_ids": len({s["location"] for s in sources if s["source_id"].startswith("src_galaxy")}), "runs": inventory, "matching_rule": "Task/model/replicate labels only; seeds and harness equivalence unverified; no replicate-level paired estimate"})
    dump(ROOT / "input_manifest.json", {"task_metadata_source": str(task_path.relative_to(REPO)), "capsule_uuid": task.get("capsule_uuid"), "allowed_input_names": [pathlib.Path(x).name for x in task.get("all_dataset_files", [])], "representative_galaxy_hid_1_to_20": first_twenty_ids, "version_and_checksum_status": "Galaxy reports hashes for some input associations; local source files not read or hashed", "shared_input_caveat": "Equal names do not prove identity; compare dataset IDs/UUIDs in evidence"})
    galaxy_runs = [r for r in runs if r["condition"] == "galaxy"]
    unique_h = len({r["source_ids"][0] for r in galaxy_runs})
    unique_jobs = len({e["native_job_id"] for r in galaxy_runs for e in r["events"] if e["event_type"] == "analysis"})
    failed_jobs = len({e["native_job_id"] for r in galaxy_runs for e in r["events"] if e["event_type"] == "analysis" and e["status"] != "ok"})
    interpreted_by_source = {}
    for r in galaxy_runs:
        if r["outcome"]["auditor_scientific_interpretation"]:
            interpreted_by_source.setdefault(r["source_ids"][0], r)
    interpreted = list(interpreted_by_source.values())
    near_00501 = [r for r in interpreted if abs(r["outcome"]["auditor_scientific_interpretation"]["fungi_minus_animals"] - 0.0501) < 0.00005]
    findings = [
        finding("accuracy-unavailable", "accuracy", "How do official answer scores compare by condition?", None, [r["run_id"] for r in runs], [], status="not_assessable", missing="No official result for supplied runs; code traces inaccessible; Galaxy submissions unavailable", limits=["A saved intermediate value is not a fixed submitted answer"]),
        finding("galaxy-output-convergence", "accuracy", "What do saved Galaxy outputs support?", f"{len(near_00501)} of {len(interpreted)} detailed distinct histories support a fungi minus animals median difference near 0.0501; one custom output retains higher precision.", [r["run_id"] for r in interpreted], [ref for r in interpreted for ref in r["outcome"]["auditor_scientific_interpretation"]["evidence_refs"]], num=len(near_00501), den=len(interpreted), limits=["Auditor interpretation, not submitted-answer accuracy", "No benchmark-wide inference from a single task"]),
        finding("galaxy-history-coverage", "execution", "What Galaxy computation is visible?", f"{unique_h} distinct public histories are visible for 12 supplied Galaxy labels; {unique_jobs} distinct analytical creating jobs appear in their current snapshots.", [r["run_id"] for r in galaxy_runs], [r["source_ids"][0] for r in galaxy_runs], num=unique_h, den=12, limits=["Sol replicates 2 and 3 share one history", "Creating jobs from shared input imports excluded"]),
        finding("galaxy-observed-failures", "execution", "How many Galaxy analytical jobs failed?", f"{failed_jobs} of {unique_jobs} distinct analytical jobs have a non-ok terminal state in the retrieved snapshots.", [r["run_id"] for r in galaxy_runs], [e["event_id"] for r in galaxy_runs for e in r["events"] if e["event_type"] == "analysis" and e["status"] != "ok"], unit="event", num=failed_jobs, den=unique_jobs, limits=["Does not measure scientific correctness or recovery"]),
        finding("routes-observed", "variability", "Do visible Galaxy routes vary?", "Installed PhyKIT metrics and custom Galaxy-hosted scripts both appear among the linked histories.", [r["run_id"] for r in galaxy_runs], [r["source_ids"][0] for r in galaxy_runs], limits=["Open-ended-code routes unavailable", "Route names alone do not establish method equivalence"]),
        finding("cost-readability-unavailable", "cost_readability", "How do token use and human readability compare?", None, [r["run_id"] for r in runs], [], status="not_assessable", missing="No provider token records or blinded human review records retrieved", limits=["History structure is provenance evidence, not a measured readability gain"]),
    ]
    schema_path = ROOT / "history_analysis_evidence.schema.json"
    evidence = {"schema_version": "2.0", "audit": {"audit_id": "bix-11-q1-public-history-2026-09-20", "timestamp_utc": now, "auditor": "Codex", "software_versions": {"python": __import__("sys").version.split()[0]}, "scope": "Retrospective read-only public Galaxy audit and inaccessible HF trace inventory", "source_snapshot": "source_snapshots/galaxy", "limitations": ["No hidden ground truth accessed", "No original agent transcript or official evaluation retrieved for linked runs", "Public history snapshots may include later edits"]}, "task": {"benchmark": "BixBench", "task_id": "bix-11-q1", "prompt": task["prompt_task"], "prompt_version": None, "prompt_sha256": hashlib.sha256(task["prompt_task"].encode()).hexdigest(), "input_specification": "experiments/BixBench/task_1.json; see input_manifest.json", "evaluation_definition": "BixBench binary score of fixed submitted answer; evaluator-only reference after submission gate; see SKILL.md section 8"}, "experimental_design": {"conditions": ["galaxy", "open_ended_code"], "model_labels": list(LABELS.values()), "coverage_status": "unknown_protocol_inventory", "supplied_replicate_labels": [1, 2, 3], "budgets": None, "matching_rule": "Task/model/replicate labels only; no seed pairing verified", "known_confounders": ["Condition prompt variants differ", "Runtime model IDs and harness settings unverified", "Sol replicate labels 2 and 3 share one history"]}, "sources": sources, "runs": runs, "comparisons": [{"comparison_id": "galaxy-vs-code", "status": "not_assessable", "included_run_ids": [], "excluded_run_ids": [r["run_id"] for r in runs], "reason": "Code traces HTTP 401 and official outcomes unavailable", "estimate": None, "uncertainty": None}], "manuscript_findings": findings, "validation": {"schema": {"path": "history_analysis_evidence.schema.json", "dialect": "https://json-schema.org/draft/2020-12/schema", "sha256": sha(schema_path), "validation_status": "pending"}, "reference_integrity": "pending", "counts": {"run_records": len(runs), "galaxy_run_labels": len(galaxy_runs), "distinct_galaxy_histories": unique_h, "distinct_analytical_jobs": unique_jobs, "failed_analytical_jobs": failed_jobs, "retrieved_selected_outputs": len(output_manifest["outputs"])}, "unresolved_issues": ["HF trace source HTTP 401", "Official answer/evaluator artifacts not retrieved", "Sol r2/r3 same history", "Protocol inventory and budgets unavailable"]}}
    dump(ROOT / "history_analysis_evidence.json", evidence)
    print(json.dumps(evidence["validation"]["counts"], indent=2))


if __name__ == "__main__":
    main()
