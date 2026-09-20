"""Validate schema, local links, source bytes, IDs, and derived comparisons."""
from __future__ import annotations

import json
import re
import statistics
from pathlib import Path

from collect import digest, write_json


def validate(output: Path, *, mark_passed: bool = True) -> dict:
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("Install analysis_execution/requirements.txt to validate JSON Schema 2.0") from exc
    path = output / "history_analysis_evidence.json"
    evidence = json.loads(path.read_text())
    schema_path = output / "history_analysis_evidence.schema.json"
    schema = json.loads(schema_path.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
    jsonschema.Draft202012Validator(schema).validate(evidence)
    assert evidence["validation"]["schema"]["sha256"] == digest(schema_path.read_bytes())
    sources = {s["source_id"] for s in evidence["sources"]}
    runs = {r["run_id"] for r in evidence["runs"]}
    events = {e["event_id"] for r in evidence["runs"] for e in r["events"]}
    artifacts = {a["artifact_id"] for r in evidence["runs"] for a in r["artifacts"]}
    assert len(sources) == len(evidence["sources"]), "duplicate source ID"
    assert len(runs) == len(evidence["runs"]), "duplicate run ID"
    assert len(events) == sum(len(r["events"]) for r in evidence["runs"]), "duplicate event ID"
    assert len(artifacts) == sum(len(r["artifacts"]) for r in evidence["runs"]), "duplicate artifact ID"
    for run in evidence["runs"]:
        assert set(run["source_ids"]) <= sources
        own_events = {e["event_id"] for e in run["events"]}
        own_artifacts = {a["artifact_id"] for a in run["artifacts"]}
        for event in run["events"]:
            assert set(event.get("parent_event_ids", [])) <= own_events
            assert set(event.get("input_artifact_ids", [])) <= own_artifacts
            assert set(event.get("output_artifact_ids", [])) <= own_artifacts
            for ref in event["evidence_refs"]:
                assert ref.partition(":")[0] in sources
        for artifact in run["artifacts"]:
            if artifact.get("producing_event_id"):
                assert artifact["producing_event_id"] in own_events
            if artifact.get("local_path"):
                local = output / artifact["local_path"]
                assert local.is_file(), local
                assert local.stat().st_size == artifact["observed_size"], local
                assert digest(local.read_bytes()) == artifact["sha256"], local
        for episode in run["recovery_episodes"]:
            assert set(episode["failed_event_ids"] + episode["recovery_event_ids"]) <= own_events
    for finding in evidence["manuscript_findings"]:
        assert set(finding["eligible_run_ids"]) <= runs
        for ref in finding["evidence_refs"] + finding["contradictory_evidence_refs"]:
            assert ref in sources | runs | events | artifacts or ref.partition(":")[0] in sources
        if finding["numerator"] is not None and finding["denominator"]:
            assert finding["estimate"] == finding["numerator"] / finding["denominator"]
    for comp in evidence["comparisons"]:
        assert set(comp["included_run_ids"] + comp["excluded_run_ids"]) <= runs
        if comp["comparison_id"].startswith("input_tokens_") and comp["status"] == "descriptive_only":
            assert comp["estimate"] == comp["galaxy_median"] / comp["code_median"]
    run_manifest = json.loads((output / "run_manifest.json").read_text())
    assert {x["run_id"] for x in run_manifest["observed_rows"]} == runs
    hf_manifests = output / "source_snapshots/huggingface_traces/manifests"
    for manifest_path in hf_manifests.glob("*.json"):
        manifest = json.loads(manifest_path.read_text())
        for file in manifest.get("files", []):
            if file.get("status") == "retained":
                local = output / file["local_path"]
                assert local.stat().st_size == file["retained_bytes"]
                assert digest(local.read_bytes()) == file["retained_sha256"]
                assert file.get("reported_size_matches_download", True), local
    galaxy_dir = output / "source_snapshots/galaxy"
    for manifest_path in galaxy_dir.glob("*/manifest.json"):
        manifest = json.loads(manifest_path.read_text())
        for item in manifest.get("jobs", []):
            assert digest((output / item["path"]).read_bytes()) == item["sha256"]
        for item in manifest.get("outputs", []):
            local = output / item["path"]
            assert local.stat().st_size == item["retained_bytes"]
            assert digest(local.read_bytes()) == item["retained_sha256"]
            assert item.get("reported_size_matches_download", True), local
    secret_patterns = [rb"hf_[A-Za-z0-9]{20,}", rb"sk-[A-Za-z0-9_-]{20,}",
                       rb"GALAXY_API_KEY\s*[=:]\s*[A-Za-z0-9._-]{20,}",
                       rb"Bearer\s+[A-Za-z0-9._-]{20,}", rb"/Users/[^/\s\"']+"]
    for folder in (output / "source_snapshots/huggingface_traces/files", output / "source_snapshots/galaxy", output / "recovered_code"):
        for file in folder.rglob("*"):
            if file.is_file() and file.stat().st_size <= 10_000_000:
                raw = file.read_bytes()
                if file.suffix == ".gz":
                    import gzip
                    raw = gzip.decompress(raw)
                assert not any(re.search(pattern, raw) for pattern in secret_patterns), file
    for filename in ("README.md", "history_analysis.md"):
        markdown = output / filename
        if not markdown.exists():
            continue
        for target in re.findall(r"\]\(([^)]+)\)", markdown.read_text()):
            if target.startswith(("https://", "http://", "#")):
                continue
            assert (output / target).exists(), (markdown, target)
    if mark_passed:
        evidence["validation"]["schema"]["validation_status"] = "passed"
        evidence["validation"]["reference_integrity"] = "passed"
        evidence["validation"]["hash_size_and_count_checks"] = "passed"
        write_json(path, evidence)
    return evidence


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    validate(args.directory.resolve())
    print("Validation passed")
