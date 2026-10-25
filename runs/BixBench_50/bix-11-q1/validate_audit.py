"""Validate schema, references, source hashes, output bytes, and core counts."""
import hashlib
import json
import pathlib
import sys

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = ROOT / "history_analysis_evidence.json"
    evidence = json.loads(p.read_text())
    schema_path = ROOT / "history_analysis_evidence.schema.json"
    schema = json.loads(schema_path.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["validation"]["schema"]["sha256"] == digest(schema_path)

    source_ids = [s["source_id"] for s in evidence["sources"]]
    run_ids = [r["run_id"] for r in evidence["runs"]]
    event_ids = [e["event_id"] for r in evidence["runs"] for e in r["events"]]
    artifact_ids = [a["artifact_id"] for r in evidence["runs"] for a in r["artifacts"]]
    for name, values in (("sources", source_ids), ("runs", run_ids), ("events", event_ids), ("artifacts", artifact_ids)):
        assert len(values) == len(set(values)), f"duplicate {name} ID"
    all_ids = set(source_ids + run_ids + event_ids + artifact_ids)
    for r in evidence["runs"]:
        assert set(r["source_ids"]) <= set(source_ids)
        own_events = {x["event_id"] for x in r["events"]}
        own_artifacts = {x["artifact_id"] for x in r["artifacts"]}
        for e in r["events"]:
            assert set(e.get("input_artifact_ids", [])) <= own_artifacts
            assert set(e.get("output_artifact_ids", [])) <= own_artifacts
            for ref in e["evidence_refs"]:
                sid, _, path = ref.partition(":")
                assert sid in source_ids and path
        for a in r["artifacts"]:
            if a["producing_event_id"]:
                assert a["producing_event_id"] in own_events
            if a["local_path"]:
                local = ROOT / a["local_path"]
                assert local.exists()
                assert a["observed_size"] == local.stat().st_size
                assert a["sha256"] == digest(local)
        for episode in r["recovery_episodes"]:
            assert set(episode["failed_event_ids"] + episode["recovery_event_ids"]) <= own_events
    for f in evidence["manuscript_findings"]:
        assert set(f["eligible_run_ids"]) <= set(run_ids)
        for ref in f["evidence_refs"] + f["contradictory_evidence_refs"]:
            assert ref in all_ids or ref.partition(":")[0] in source_ids, ref
        if f["numerator"] is not None and f["denominator"]:
            assert f["estimate"] == f["numerator"] / f["denominator"]
    for s in evidence["sources"]:
        if s.get("sha256_history_snapshot"):
            assert s["sha256_history_snapshot"] == digest(ROOT / s["local_snapshot"] / "history.json")
        if s.get("sha256_contents_snapshot"):
            assert s["sha256_contents_snapshot"] == digest(ROOT / s["local_snapshot"] / "contents.json")
        if s.get("sha256_access_response"):
            assert s["sha256_access_response"] == digest(ROOT / s["access_status_snapshot"])
    selected = json.loads((ROOT / "selected_outputs/galaxy/manifest.json").read_text())
    assert not selected["errors"]
    for item in selected["outputs"]:
        local = ROOT / item["path"]
        assert item["bytes"] == local.stat().st_size == item["expected_file_size"]
        assert item["sha256"] == digest(local)
    c = evidence["validation"]["counts"]
    assert c["run_records"] == len(run_ids) == 24
    assert c["galaxy_run_labels"] == sum(r["condition"] == "galaxy" for r in evidence["runs"]) == 12
    assert c["distinct_galaxy_histories"] == len({r["source_ids"][0] for r in evidence["runs"] if r["condition"] == "galaxy"}) == 11
    jobs = {e["native_job_id"] for r in evidence["runs"] for e in r["events"] if e["event_type"] == "analysis" and e["execution_location"] == "galaxy_job"}
    failed = {e["native_job_id"] for r in evidence["runs"] for e in r["events"] if e["event_type"] == "analysis" and e["execution_location"] == "galaxy_job" and e["status"] != "ok"}
    assert c["distinct_analytical_jobs"] == len(jobs) == 27
    assert c["failed_analytical_jobs"] == len(failed) == 1
    assert c["retrieved_selected_outputs"] == len(selected["outputs"]) == 56
    hf_root = ROOT / "source_snapshots/huggingface_traces"
    hf_manifests = [json.loads((hf_root / name).read_text()) for name in ("manifest.json", "manifest_galaxy.json")]
    assert all(len(m["runs"]) == 12 for m in hf_manifests)
    hf_files = [item for m in hf_manifests for run in m["runs"].values() for item in run["files"]]
    assert len(hf_files) == c["hf_trace_files"] == 408
    for item in hf_files:
        assert item["downloaded"]
        local = ROOT / item["local_path"]
        assert local.exists() and local.stat().st_size == item["retained_bytes"]
        assert digest(local) == item["retained_sha256"]
        if not item["redactions"]:
            assert item["sha256"] == item["retained_sha256"]
    assert c["official_evaluable_runs"] == len(evidence["runs"]) == 24
    assert c["official_correct_runs"] == sum(r["outcome"]["official_bixbench_answer_score"] == 1 for r in evidence["runs"]) == 24
    for comparison in evidence["comparisons"]:
        if comparison["comparison_id"].startswith("official_accuracy_"):
            assert comparison["code_correct"] == comparison["galaxy_correct"] == 3
            assert comparison["estimate"] == 0.0
        elif comparison["comparison_id"].startswith("input_token_ratio_"):
            code = [r["usage"]["provider_reported_input_tokens"] for r in evidence["runs"] if r["run_id"] in comparison["included_run_ids"] and r["condition"] == "open_ended_code"]
            galaxy = [r["usage"]["provider_reported_input_tokens"] for r in evidence["runs"] if r["run_id"] in comparison["included_run_ids"] and r["condition"] == "galaxy"]
            import statistics
            assert comparison["code_median"] == statistics.median(code)
            assert comparison["galaxy_median"] == statistics.median(galaxy)
            assert comparison["estimate"] == comparison["galaxy_median"] / comparison["code_median"]
    inputs = json.loads((ROOT / "input_manifest.json").read_text())
    assert inputs["trace_staged_input_run_count"] == 24
    assert inputs["all_trace_input_hashes_agree_by_name"]
    for source_file in (ROOT / "source_snapshots/galaxy").rglob("*.json"):
        obj = json.loads(source_file.read_text())
        def inspect(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key in {"user_email", "user_id", "username", "username_and_slug"}:
                        assert child == "[redacted]", source_file
                    else:
                        inspect(child)
            elif isinstance(value, list):
                for child in value:
                    inspect(child)
        inspect(obj)
    import re
    secret_patterns = [rb"hf_[A-Za-z0-9]{20,}", rb"sk-[A-Za-z0-9_-]{20,}", rb"GALAXY_API_KEY\s*[=:]\s*[A-Za-z0-9]{20,}", rb"Bearer\s+[A-Za-z0-9._-]{20,}", rb"/Users/[0-9]+/"]
    for source_file in (hf_root / "files").rglob("*"):
        if source_file.is_file():
            data = source_file.read_bytes()
            assert not any(re.search(pattern, data) for pattern in secret_patterns), source_file
    evidence["validation"]["schema"]["validation_status"] = "passed"
    evidence["validation"]["reference_integrity"] = "passed"
    evidence["validation"]["hash_size_and_count_checks"] = "passed"
    p.write_text(json.dumps(evidence, indent=2, ensure_ascii=False) + "\n")
    print("Validation passed: schema, IDs, references, hashes, sizes, counts, redactions")


if __name__ == "__main__":
    main()
