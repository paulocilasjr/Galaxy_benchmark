"""Add original agent, evaluator, and usage evidence to the public-history audit.

This script reads preserved, redacted trace files. It never executes agent code,
opens a hidden answer key, or contacts an external service.
"""
import gzip
import hashlib
import json
import pathlib
import re
import statistics
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parent
HF = ROOT / "source_snapshots/huggingface_traces"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def locate(folder, name):
    matches = list(folder.rglob(name))
    return matches[0] if matches else None


def read_json(folder, name):
    path = locate(folder, name)
    return json.loads(path.read_text()) if path else {}


def read_events(folder):
    path = locate(folder, "codex_events.jsonl") or locate(folder, "codex_events.jsonl.gz")
    if not path:
        return None, []
    raw = gzip.decompress(path.read_bytes()).decode(errors="replace") if path.suffix == ".gz" else path.read_text(errors="replace")
    records = []
    for line_number, line in enumerate(raw.splitlines(), 1):
        if not line.lstrip().startswith("{"):
            continue
        try:
            records.append((line_number, json.loads(line)))
        except json.JSONDecodeError:
            continue
    return path, records


def classify_command(command, condition):
    low = command.lower()
    if any(x in low for x in ("sed -n '1,220p' /codex_home/skills", "rg --files", "command -v", "pip show", "--help", "which phykit")):
        return "discovery"
    if any(x in low for x in ("unzip -l", "unzip -z1", "unzip -t", "find inputs", "ls -la", "inputs_manifest.json")) and "calculate_treeness" not in low:
        return "input_preparation"
    if condition == "galaxy":
        return "orchestration"
    if any(x in low for x in ("python", "phykit", "rscript", "awk", "compute_treeness")):
        return "analysis"
    return "orchestration"


def unique_source(source_list, source):
    if not any(x["source_id"] == source["source_id"] for x in source_list):
        source_list.append(source)


def main():
    p = ROOT / "history_analysis_evidence.json"
    evidence = json.loads(p.read_text())
    manifests = {"open_ended_code": json.loads((HF / "manifest.json").read_text()), "galaxy": json.loads((HF / "manifest_galaxy.json").read_text())}
    all_runs = {r["run_id"]: r for r in evidence["runs"]}
    all_sources = {s["source_id"]: s for s in evidence["sources"]}
    recovered = json.loads((ROOT / "recovered_code/manifest.json").read_text())
    recovered["open_ended_code"] = {"status": "retrieved", "commands": [], "execution_claim": "Only transcript-reported completed commands are labelled executed; extracted command text was not replayed"}
    input_hashes = {}
    for condition, manifest in manifests.items():
        for label, entry in manifest["runs"].items():
            model_rep = label.removeprefix("galaxy_")
            rid = ("galaxy_" if condition == "galaxy" else "open_ended_code_") + model_rep
            run = all_runs[rid]
            folder = HF / "files" / label
            items = {pathlib.PurePosixPath(x["path"]).name: x for x in entry["files"] if x.get("downloaded")}
            assert all(x.get("downloaded") for x in entry["files"]), label
            assert {"evaluation.json", "usage.json", "result.json", "run_record.json", "docker_invocation.json", "prompt.txt", "inputs_manifest.json"} <= set(items), label
            sid = f"src_hf_{label}" if condition == "galaxy" else f"src_code_{label}"
            source = {"source_id": sid, "location": f"https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces/tree/main/{entry['prefix']}", "retrieval_time_utc": manifest["retrieved_at_utc"], "access_status": "authorized_trace_retrieved", "local_snapshot": f"source_snapshots/huggingface_traces/files/{label}", "file_count": len(entry["files"]), "index_path": entry["index_path"], "index_sha256": sha(ROOT / entry["index_path"]), "redactions": [x["redactions"] for x in entry["files"] if x.get("redactions")], "evidence_completeness": "Answer, evaluator, usage, prompt, runtime metadata and agent transcript retrieved"}
            if sid in all_sources:
                all_sources[sid].update(source)
                all_sources[sid].pop("access_status_snapshot", None)
                all_sources[sid].pop("sha256_access_response", None)
            else:
                evidence["sources"].append(source)
                all_sources[sid] = source
            if sid not in run["source_ids"]:
                run["source_ids"].append(sid)
            evaluation = read_json(folder, "evaluation.json")
            usage = read_json(folder, "usage.json")
            result = read_json(folder, "result.json")
            invocation = read_json(folder, "docker_invocation.json")
            run_record = read_json(folder, "run_record.json")
            attempt = read_json(folder, "attempt.json")
            prompt_path = locate(folder, "prompt.txt")
            answer_path = locate(folder, "answer.txt")
            assert prompt_path and answer_path
            answer = answer_path.read_text().strip()
            assert result["answer"]["text"].strip() == answer, rid
            run["model"].update({"verified_runtime_id": invocation.get("model"), "version": invocation.get("model"), "harness": invocation.get("image"), "reasoning_setting": invocation.get("reasoning_effort"), "service_tier": invocation.get("service_tier"), "verification_status": "runtime_verified"})
            run["iteration_setting"] = attempt.get("attempt")
            run["status"] = "trace_observed" if condition == "open_ended_code" else run["status"]
            run["timestamps"].update({"prepared_at_utc": run_record.get("prepared_at_utc"), "usage_written_at_utc": usage.get("written_at_utc")})
            run["environment"].update({"docker_image": invocation.get("image"), "workspace_mode": invocation.get("workspace_mode"), "galaxy_api_key_mode": invocation.get("galaxy_api_key_mode"), "galaxy_execute_mcp_enabled": invocation.get("galaxy_execute_mcp_enabled"), "service_tier": invocation.get("service_tier")})
            run["prompt_sha256"] = sha(prompt_path)
            inp = read_json(folder, "inputs_manifest.json")
            input_hashes[rid] = {x["name"]: x.get("sha256") for x in inp.get("inputs", [])}
            run["input_provenance"].update({"trace_input_manifest_sha256": sha(locate(folder, "inputs_manifest.json")), "staged_input_count": len(inp.get("inputs", [])), "source": "staged capsule data; see original trace manifest"})
            run["evidence_completeness"].update({"agent_transcript": "retrieved", "submitted_answer": "retrieved", "official_evaluation": "retrieved", "tokens": "retrieved"})
            run["limitations"] = [x for x in run["limitations"] if "HTTP 401" not in x and "no run-level conclusions" not in x]
            accuracy = evaluation["accuracy"]
            run["outcome"].update({"submitted_answer": answer, "submitted_answer_sha256": sha(answer_path), "submission_time": None, "official_bixbench_answer_score": accuracy.get("score"), "official_evaluator_version": accuracy.get("mode"), "official_score_details": {"original_field": "accuracy.score", "scale": "binary 0/1", "evaluation_target": "fixed submitted answer", "producer": "original run evaluator", "source_id": sid, "verifier_mode": accuracy.get("mode"), "source_mode": accuracy.get("source_mode"), "tolerance": accuracy.get("tolerance")}, "step_completion": {"original_field": "step_completion.score", "score": evaluation["step_completion"]["score"], "criteria": evaluation["step_completion"].get("steps"), "source_id": sid}, "result_status": "fixed submitted answer and original evaluator result observed"})
            run["usage"] = {"provider_reported_input_tokens": usage.get("totals", {}).get("input_tokens"), "provider_reported_output_tokens": usage.get("totals", {}).get("output_tokens"), "provider_reported_cached_input_tokens": usage.get("totals", {}).get("cached_input_tokens"), "provider_reported_reasoning_tokens": usage.get("totals", {}).get("reasoning_output_tokens"), "uncached_input_tokens": usage.get("totals", {}).get("uncached_input_tokens"), "source_id": sid, "source_file": "usage.json", "aggregation_scope": f"{usage.get('turn_completed_count')} completed turn(s); totals, not sum of snapshots", "accounting_note": "cached input is a subset of input; reasoning output is included in output", "estimated_cost_usd": usage.get("estimated_cost_usd"), "missingness": None}
            original_artifacts = run["artifacts"]
            for name, role in (("answer.txt", "final_answer"), ("evaluation.json", "evaluator_output"), ("usage.json", "usage_record"), ("prompt.txt", "agent_trace"), ("codex_events.jsonl", "agent_trace"), ("codex_events.jsonl.gz", "agent_trace"), ("inputs_manifest.json", "shared_input")):
                item = items.get(name)
                if not item:
                    continue
                original_artifacts.append({"artifact_id": f"art_trace_{rid}_{name.replace('.', '_')}", "role": role, "condition": condition, "run_id": rid, "original_name": name, "local_path": item["local_path"], "source_url": f"https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces/resolve/main/{item['path']}", "format": name.split(".")[-1], "observed_size": item.get("retained_bytes", item["bytes"]), "sha256": item.get("retained_sha256", item["sha256"]), "source_original_sha256": item["sha256"], "redactions": item.get("redactions", []), "producing_event_id": None, "derivation_parent_ids": [], "status": "retained"})
            event_path, records = read_events(folder)
            transcript_name = event_path.name if event_path else None
            trace_events = []
            for sequence, (line_number, record) in enumerate(records, 1):
                if record.get("type") != "item.completed":
                    continue
                item = record.get("item") or {}
                native_type = item.get("type")
                if native_type not in {"command_execution", "mcp_tool_call", "web_search"}:
                    continue
                native_id = item.get("id") or f"line_{line_number}"
                eid = f"evt_trace_{rid}_{native_id}"
                if native_type == "command_execution":
                    command = item.get("command") or ""
                    event_type = classify_command(command, condition)
                    location = "agent_runtime"
                    tool = "shell"
                    params = None
                    stdout = (item.get("aggregated_output") or "")[:1000]
                    stderr = None
                    exit_code = item.get("exit_code")
                elif native_type == "mcp_tool_call":
                    command = None
                    event_type = "discovery" if item.get("tool") in {"search_galaxy_tools", "inspect_galaxy_tool", "inspect_galaxy_history", "inspect_archive_inventory"} else "orchestration"
                    location = "mixed" if item.get("tool", "").startswith(("run_galaxy", "wait_for_galaxy")) else "agent_runtime"
                    tool = item.get("tool")
                    params = item.get("arguments")
                    stdout = None
                    stderr = str(item.get("error")) if item.get("error") not in (None, "None", "", False) else None
                    exit_code = None
                else:
                    command, params, stdout, stderr, exit_code = None, item.get("query"), None, None, None
                    event_type, location, tool = "discovery", "external_service", "web_search"
                trace_events.append({"event_id": eid, "sequence": sequence, "timestamp": None, "timestamp_source": "Original JSONL event order only; no per-item timestamps", "event_type": event_type, "execution_location": location, "native_tool_call_id": native_id, "parent_event_ids": [], "input_artifact_ids": [], "output_artifact_ids": [], "tool": tool, "command": command, "parameters": params, "status": item.get("status") or "completed", "exit_code": exit_code, "stdout_excerpt": stdout, "stderr_excerpt": stderr, "evidence_refs": [f"{sid}:{transcript_name}#L{line_number}"], "visibility_limits": "Output excerpt may be truncated; full retained trace is authoritative"})
                if condition == "open_ended_code" and native_type == "command_execution":
                    dest = ROOT / "recovered_code/open_ended_code" / model_rep / f"{native_id}.command.txt"
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_text(command + "\n")
                    recovered["open_ended_code"]["commands"].append({"run_id": rid, "event_id": eid, "path": str(dest.relative_to(ROOT)), "sha256": sha(dest), "source_id": sid, "source_line": line_number, "reported_exit_code": exit_code, "extraction": "Command string from completed original agent event; not replayed"})
            run["events"].extend(trace_events)
            commands = [x for x in trace_events if x["tool"] == "shell"]
            nonzero = [x for x in commands if x["exit_code"] not in (None, 0)]
            mcp = [x for x in trace_events if x["tool"] not in {"shell", "web_search"}]
            run["derived_metrics"].update({"completed_shell_calls": len(commands), "nonzero_exit_shell_calls": len(nonzero), "completed_mcp_calls": len(mcp), "native_trace_event_count": len(trace_events), "trace_call_counts_note": "Tool calls are not equated to scientific attempts or Galaxy jobs"})
            if condition == "open_ended_code":
                command_text = "\n".join(x["command"] or "" for x in commands)
                flags = {"installed_phykit": bool(re.search(r"pip\s+install.*phykit|pip3\s+install.*phykit", command_text, re.I)), "used_phykit": bool(re.search(r"phykit treeness|phykit.services.tree|calculate_treeness", command_text, re.I)), "used_biopython": bool(re.search(r"from Bio import Phylo|import Bio.Phylo", command_text)), "custom_newick_or_branch_parser": bool(re.search(r"class (?:Node|Parser)|def parse_(?:tree|subtree|newick)|internal.*total", command_text, re.I))}
                route = "PhyKIT local calculation" if flags["used_phykit"] else ("Biopython local calculation" if flags["used_biopython"] else "custom local Newick/branch-length calculation")
                # Classify the final computation, not an exploratory command earlier in the trace.
                if rid == "open_ended_code_sol_r2":
                    route = "local IQ-TREE report extraction"
                elif rid == "open_ended_code_sol_r3":
                    route = "custom local Decimal Newick/branch-length calculation"
                run["solution_route"] = {"classification": route, "observed_flags": flags, "biological_method": "per-tree treeness then median by group and fungi minus animals", "parameters": "See completed command events and retained transcript", "validation": "answer/evaluator records and transcript checks", "route_codebook": "tool family plus per-tree statistic and group aggregation; not just script bytes"}
                run["outcome"]["execution_completion"] = "agent_run_completed" if evaluation["step_completion"]["steps"][0]["passed"] else "not established"
                if rid == "open_ended_code_sol_r1":
                    run["recovery_episodes"].append({"episode_id": "recovery_code_sol_r1_biopython", "trigger": "Biopython import failed with ModuleNotFoundError", "failure_type": "execution_tool_dependency_failure", "failed_event_ids": [f"evt_trace_{rid}_item_6"], "diagnosis_evidence": [f"{sid}:{transcript_name}#item_6"], "corrective_action": "Installed Biopython, then reran a tree-based calculation", "recovery_event_ids": [f"evt_trace_{rid}_item_7", f"evt_trace_{rid}_item_8"], "same_goal_linkage": "The dependency was needed for the attempted tree parsing calculation", "eventual_outcome": "Operationally resolved; original evaluator accepted final answer"})
                if rid == "open_ended_code_deepseek_r1":
                    run["recovery_episodes"].append({"episode_id": "recovery_code_deepseek_r1_phykit_cli", "trigger": "PhyKIT treeness rejected the -t argument", "failure_type": "execution_tool_invalid_parameter", "failed_event_ids": [f"evt_trace_{rid}_item_18"], "diagnosis_evidence": [f"{sid}:{transcript_name}#item_18"], "corrective_action": "Passed the tree path positionally", "recovery_event_ids": [f"evt_trace_{rid}_item_19"], "same_goal_linkage": "Both commands computed PhyKIT treeness on the same sample treefiles", "eventual_outcome": "Operationally resolved; original evaluator accepted final answer"})
            else:
                run["solution_route"]["trace_mcp_tool_counts"] = dict(Counter(x["tool"] for x in mcp))
                run["limitations"] = [x for x in run["limitations"] if "agent transcript" not in x.lower()]
            save(ROOT / "job_ledgers" / condition / f"{rid}.json", {"run_id": rid, "source_id": sid, "trace_events": trace_events})
    save(ROOT / "recovered_code/manifest.json", recovered)
    shared_input_hashes = {name: sorted({per.get(name) for per in input_hashes.values() if per.get(name)}) for name in sorted({x for per in input_hashes.values() for x in per})}
    input_manifest_path = ROOT / "input_manifest.json"
    input_manifest = json.loads(input_manifest_path.read_text())
    input_manifest["trace_staged_input_checksums"] = shared_input_hashes
    input_manifest["trace_staged_input_run_count"] = len(input_hashes)
    input_manifest["all_trace_input_hashes_agree_by_name"] = all(len(v) == 1 for v in shared_input_hashes.values())
    input_manifest["version_and_checksum_status"] = "Original trace inputs_manifest.json files report sizes and SHA-256 hashes for all staged inputs; all 24 agree by name. Auditor did not download or independently hash the large source inputs."
    save(input_manifest_path, input_manifest)
    run_manifest_path = ROOT / "run_manifest.json"
    run_manifest = json.loads(run_manifest_path.read_text())
    for item in run_manifest["runs"]:
        if item["condition"] == "open_ended_code":
            item["status"] = "trace_observed"
    run_manifest["retrieved_trace_runs"] = 24
    run_manifest["authorized_trace_sources"] = ["source_snapshots/huggingface_traces/manifest.json", "source_snapshots/huggingface_traces/manifest_galaxy.json"]
    save(run_manifest_path, run_manifest)
    evidence["audit"]["scope"] = "Retrospective read-only audit of public Galaxy histories plus authenticated original run traces, evaluator results and usage"
    evidence["audit"]["limitations"] = ["No hidden ground-truth file opened", "No recovered code replayed", "Sol Galaxy replicates 2 and 3 share one history object", "Luna Galaxy replicate 2 history contents API timed out; original trace remains available"]
    evidence["experimental_design"]["model_configurations_verified"] = {r["run_id"]: {"runtime_id": r["model"]["verified_runtime_id"], "reasoning": r["model"]["reasoning_setting"], "harness_image": r["model"]["harness"]} for r in evidence["runs"]}
    evidence["experimental_design"]["known_confounders"] = ["Conditions have different explicit execution-policy prompts", "GPT-5.5 condition images differ by one day", "Sol Galaxy replicate labels 2 and 3 share a history object", "Replicate seeds not recorded", "One selected task; no task-level sample for inference"]
    evidence["task"]["evaluation_definition"] = "Original evaluator accuracy.score is binary fixed-answer correctness under llm_verifier_auto_code (tolerance 0.0005); step_completion.score has different condition-specific criteria. See original evaluation.json for each run. Repository SKILL.md describes a different current BixBench verifier; original run rules are retained here."
    comparisons = []
    for model in ("gpt55", "sol", "luna", "deepseek"):
        code = [all_runs[f"open_ended_code_{model}_r{i}"] for i in (1, 2, 3)]
        galaxy = [all_runs[f"galaxy_{model}_r{i}"] for i in (1, 2, 3)]
        cs = sum(r["outcome"]["official_bixbench_answer_score"] == 1 for r in code)
        gs = sum(r["outcome"]["official_bixbench_answer_score"] == 1 for r in galaxy)
        ids = [r["run_id"] for r in code + galaxy]
        comparisons.append({"comparison_id": f"official_accuracy_{model}", "status": "descriptive_only", "included_run_ids": ids, "excluded_run_ids": [], "unit": "submitted answer evaluation", "code_correct": cs, "code_evaluable": 3, "galaxy_correct": gs, "galaxy_evaluable": 3, "estimate": 100 * (gs / 3 - cs / 3), "estimate_unit": "percentage points Galaxy minus code", "uncertainty": None, "limitation": "Single task and replicate seeds unverified; Sol Galaxy histories not independent"})
        cm = statistics.median(r["usage"]["provider_reported_input_tokens"] for r in code)
        gm = statistics.median(r["usage"]["provider_reported_input_tokens"] for r in galaxy)
        comparisons.append({"comparison_id": f"input_token_ratio_{model}", "status": "descriptive_only", "included_run_ids": ids, "excluded_run_ids": [], "unit": "provider-reported input tokens including cached input", "code_median": cm, "galaxy_median": gm, "estimate": gm / cm, "estimate_unit": "ratio of condition medians", "uncertainty": None, "limitation": "Three runs per condition for one task; not a universal work unit across models"})
    evidence["comparisons"] = comparisons
    trace_sources = [s["source_id"] for s in evidence["sources"] if s["access_status"] == "authorized_trace_retrieved"]
    all_ids = [r["run_id"] for r in evidence["runs"]]
    accuracy_refs = [f"art_trace_{rid}_evaluation_json" for rid in all_ids]
    usage_refs = [f"art_trace_{rid}_usage_json" for rid in all_ids]
    evidence["manuscript_findings"] = [
        {"finding_id": "official-accuracy-24-runs", "section": "accuracy", "question": "How did fixed-answer accuracy compare in the supplied runs?", "claim": "The original evaluator accepted all 12 Galaxy and all 12 open-ended-code submitted answers for this one task (0 percentage-point observed difference).", "scope": "case_study", "unit_of_analysis": "run", "eligible_run_ids": all_ids, "evidence_refs": accuracy_refs, "contradictory_evidence_refs": [], "numerator": 24, "denominator": 24, "estimate": 1.0, "uncertainty": None, "missingness": None, "limitations": ["One selected task; no benchmark-wide confidence interval", "Sol Galaxy replicates 2/3 share history state", "Condition prompts differ"], "interpretation_status": "observed"},
        {"finding_id": "galaxy-output-convergence", "section": "accuracy", "question": "Do saved Galaxy analytical outputs support the accepted answer?", "claim": "Ten distinct detailed Galaxy histories support a difference near 0.0501; the Luna replicate-2 history contents remain unavailable, but its trace preserves a fixed accepted answer.", "scope": "case_study", "unit_of_analysis": "artifact", "eligible_run_ids": [r["run_id"] for r in evidence["runs"] if r["condition"] == "galaxy"], "evidence_refs": [ref for r in evidence["runs"] if r["condition"] == "galaxy" and r["outcome"].get("auditor_scientific_interpretation") for ref in r["outcome"]["auditor_scientific_interpretation"]["evidence_refs"]], "contradictory_evidence_refs": [], "numerator": 10, "denominator": 10, "estimate": 1.0, "uncertainty": None, "missingness": "One of 11 unique Galaxy history contents not retrieved", "limitations": ["Output agreement and submitted answer accuracy are separate", "Sol duplicate history counted once"], "interpretation_status": "observed"},
        {"finding_id": "execution-and-recovery", "section": "execution", "question": "What processing and recovery are visible?", "claim": "Ten detailed Galaxy histories show 27 distinct analytical jobs, one failed job, and a same-input Datamash column correction; original traces also record runtime commands and tool calls for all 24 runs.", "scope": "case_study", "unit_of_analysis": "event", "eligible_run_ids": all_ids, "evidence_refs": ["evt_luna_r3_bbd44e69cb8906b59f0c620c956f35a6", "evt_luna_r3_bbd44e69cb8906b598bb0cd5ea27abe3"] + trace_sources, "contradictory_evidence_refs": [], "numerator": 1, "denominator": 27, "estimate": 1 / 27, "uncertainty": None, "missingness": "Galaxy Luna r2 jobs not enumerated from contents API", "limitations": ["Job counts exclude inherited fetches and duplicated Sol history", "Raw command failures are not all scientific attempts"], "interpretation_status": "observed"},
        {"finding_id": "route-variation", "section": "variability", "question": "Which solution routes varied across conditions?", "claim": "The traces record installed PhyKIT, custom Galaxy-hosted code, local PhyKIT, Biopython, and local branch-length parsers across the supplied runs.", "scope": "case_study", "unit_of_analysis": "run", "eligible_run_ids": all_ids, "evidence_refs": trace_sources, "contradictory_evidence_refs": [], "numerator": None, "denominator": None, "estimate": None, "uncertainty": None, "missingness": None, "limitations": ["Method classification is descriptive and based on retained commands/job tool IDs", "One task cannot establish model-general diversity"], "interpretation_status": "observed"},
        {"finding_id": "input-token-cost", "section": "cost_readability", "question": "How did measured input-token usage differ?", "claim": "Galaxy input-token medians exceed code medians for each of the four models; ratios of condition medians range from 2.44 to 6.54 in this selected task.", "scope": "case_study", "unit_of_analysis": "run", "eligible_run_ids": all_ids, "evidence_refs": usage_refs, "contradictory_evidence_refs": [], "numerator": None, "denominator": None, "estimate": None, "uncertainty": None, "missingness": None, "limitations": ["One task with three runs per model/condition", "Input tokens include cached input; models have different accounting", "Luna Galaxy r2 is a 45.6-million-token outlier"], "interpretation_status": "observed"},
        {"finding_id": "readability-unmeasured", "section": "cost_readability", "question": "Did histories improve human readability?", "claim": None, "scope": "case_study", "unit_of_analysis": "run", "eligible_run_ids": all_ids, "evidence_refs": [], "contradictory_evidence_refs": [], "numerator": None, "denominator": None, "estimate": None, "uncertainty": None, "missingness": "No blinded reviewer/time-to-reconstruction study", "limitations": ["Provenance availability does not establish human readability"], "interpretation_status": "not_assessable"}
    ]
    evidence["validation"]["counts"].update({"authenticated_trace_runs": 24, "official_evaluable_runs": 24, "official_correct_runs": 24, "hf_trace_files": sum(len(x["files"]) for m in manifests.values() for x in m["runs"].values()), "staged_input_names": len(shared_input_hashes)})
    evidence["validation"]["unresolved_issues"] = ["Sol Galaxy replicates 2/3 share one history object", "Luna Galaxy r2 contents API timed out despite retained original transcript", "Original evaluator step-completion criterion differs by condition", "No human readability evaluation or prespecified equivalence margin"]
    evidence["validation"]["schema"]["sha256"] = sha(ROOT / "history_analysis_evidence.schema.json")
    evidence["validation"]["schema"]["validation_status"] = "pending"
    evidence["validation"]["reference_integrity"] = "pending"
    save(p, evidence)
    print("Augmented", len(evidence["runs"]), "runs with 24 original trace/evaluation/usage packages")


if __name__ == "__main__":
    main()
