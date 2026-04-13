from __future__ import annotations

import json
import math
import shutil
import sys
from collections import defaultdict
from dataclasses import asdict
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Iterable, Mapping

from .contracts import normalize_evaluator_payload


DATASET_MANIFEST_PATH = Path("docs") / "dataset_governance_manifest.json"
PUBLICATION_RESULTS_PATH = Path("docs") / "publication_results_bundle.json"
PUBLICATION_RESULTS_SUMMARY_PATH = Path("docs") / "publication_results_summary.md"
PUBLICATION_RESULTS_SOURCE_PATH = Path("docs") / "publication_results_source.json"
OUTPUTS_DIR = Path("outputs")
OUTPUTS_ALLOWED_FILES = {".gitkeep", "README.md"}
PUBLIC_RELEASE_STAGES = {"public_release_candidate", "published"}
DATASET_SOURCE_KINDS = {"local_file", "remote_url"}
RIGHTS_REVIEW_STATUSES = {
    "benchmark_authored",
    "maintainer_reviewed_public_release",
    "source_governed_fetch_only",
}
RELEASE_INCLUSION_VALUES = {"public_release_mirror", "source_fetch_only", "metadata_only"}
PLACEHOLDER_SUBSTRINGS = {
    "verify upstream",
    "resolve and record",
    "before external",
    "placeholder",
    "todo",
    "tbd",
}


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _contains_placeholder(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    lowered = value.lower()
    return any(token in lowered for token in PLACEHOLDER_SUBSTRINGS)


def _normalise_path(path: str | Path) -> str:
    return Path(path).as_posix()


def _relative_to_root(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def load_dataset_manifest_payload(root_dir: str | Path) -> dict[str, Any]:
    path = Path(root_dir) / DATASET_MANIFEST_PATH
    payload = _load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Dataset manifest must be an object: {path}")
    return payload


def load_dataset_manifest(root_dir: str | Path) -> dict[str, dict[str, Any]]:
    payload = load_dataset_manifest_payload(root_dir)
    items = payload.get("datasets", [])
    manifest: dict[str, dict[str, Any]] = {}
    if not isinstance(items, list):
        raise ValueError("Dataset manifest datasets must be a list")
    for item in items:
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        if isinstance(source, str):
            manifest[source] = item
    return manifest


def load_publication_results_bundle(root_dir: str | Path) -> dict[str, Any]:
    path = Path(root_dir) / PUBLICATION_RESULTS_PATH
    payload = _load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Publication results bundle must be an object: {path}")
    return payload


def load_publication_results_source(root_dir: str | Path) -> dict[str, Any]:
    path = Path(root_dir) / PUBLICATION_RESULTS_SOURCE_PATH
    payload = _load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"Publication results source must be an object: {path}")
    return payload


def iter_public_experiment_payloads(root_dir: str | Path) -> Iterable[tuple[str, str, dict[str, Any]]]:
    root = Path(root_dir)
    for level in ("low_context", "medium_context", "high_context"):
        for path in sorted((root / "experiments" / level).glob("experiment_*.json")):
            payload = _load_json(path)
            experiment_id, body = next(iter(payload.items()))
            if isinstance(body, dict):
                yield level, experiment_id, body


def expected_benchmark_instances(root_dir: str | Path) -> list[tuple[str, str]]:
    return [(experiment_id, level) for level, experiment_id, _ in iter_public_experiment_payloads(root_dir)]


def unique_experiment_inputs(root_dir: str | Path) -> list[str]:
    sources: set[str] = set()
    for _, _, payload in iter_public_experiment_payloads(root_dir):
        dataset = payload.get("Inputs_Path", {}).get("dataset", [])
        if isinstance(dataset, str):
            dataset = [dataset]
        for item in dataset:
            if isinstance(item, str):
                sources.add(item)
    return sorted(sources)


def audit_public_task_alignment(root_dir: str | Path) -> list[str]:
    issues: list[str] = []
    root = Path(root_dir)
    for ground_truth_path in sorted((root / "ground_truth").glob("experiment_*.json")):
        ground_truth = _load_json(ground_truth_path)
        if not isinstance(ground_truth, dict):
            issues.append(f"{ground_truth_path.stem}: ground truth must be a JSON object")
            continue
        variants = ground_truth.get("public_task_variants", {})
        if not isinstance(variants, dict):
            issues.append(f"{ground_truth_path.stem}: public_task_variants must be an object")
            continue
        for level in ("low_context", "medium_context", "high_context"):
            experiment_path = root / "experiments" / level / ground_truth_path.name
            experiment_payload = _load_json(experiment_path)
            _, public_payload = next(iter(experiment_payload.items()))
            expected_payload = variants.get(level)
            if public_payload != expected_payload:
                issues.append(
                    f"{ground_truth_path.stem}:{level} public_task_variants does not match experiments/{level}/{ground_truth_path.name}"
                )
    return issues


def audit_expected_result_fields(root_dir: str | Path) -> list[str]:
    issues: list[str] = []
    root = Path(root_dir)
    for path in sorted((root / "ground_truth").glob("experiment_*.json")):
        payload = _load_json(path)
        normalized = normalize_evaluator_payload(payload if isinstance(payload, dict) else None)
        expected = normalized.get("expected_result_fields", [])
        if not expected:
            issues.append(f"{path.stem}: normalized evaluator contract has no expected_result_fields")
            continue
        names = {item.get("name") for item in expected if isinstance(item, dict)}
        for required in (
            "galaxy_execution.final_entity_type",
            "galaxy_execution.final_entity_name",
            "galaxy_execution.history_input_mode",
        ):
            if required not in names:
                issues.append(f"{path.stem}: normalized evaluator contract is missing {required}")
    return issues


def audit_outputs_directory(root_dir: str | Path) -> list[str]:
    issues: list[str] = []
    outputs_dir = Path(root_dir) / OUTPUTS_DIR
    if not outputs_dir.exists():
        issues.append("outputs/: missing directory")
        return issues
    for path in sorted(outputs_dir.rglob("*")):
        relative = path.relative_to(outputs_dir).as_posix()
        if path.is_dir():
            issues.append(f"outputs/: release-safe authoring tree should not contain tracked run directories ({relative})")
            continue
        if relative not in OUTPUTS_ALLOWED_FILES:
            issues.append(f"outputs/: unexpected tracked artifact present ({relative})")
    return issues


def audit_dataset_manifest(root_dir: str | Path) -> list[str]:
    issues: list[str] = []
    root = Path(root_dir)
    payload = load_dataset_manifest_payload(root)
    release_stage = payload.get("generated_for_release")
    if release_stage not in PUBLIC_RELEASE_STAGES:
        issues.append(
            "dataset manifest generated_for_release must be one of: public_release_candidate, published"
        )
    items = payload.get("datasets", [])
    if not isinstance(items, list) or not items:
        issues.append("dataset manifest datasets must be a non-empty list")
        return issues
    manifest = load_dataset_manifest(root)
    for source in unique_experiment_inputs(root):
        item = manifest.get(source)
        if item is None:
            issues.append(f"dataset manifest is missing source: {source}")
            continue
        required_keys = {
            "source",
            "source_kind",
            "experiments",
            "license_name",
            "rights_review_status",
            "release_inclusion",
            "citation",
            "access_date",
            "persistence_policy",
        }
        missing = sorted(key for key in required_keys if key not in item)
        if missing:
            issues.append(f"dataset manifest entry {source} is missing keys: {', '.join(missing)}")
            continue
        if item["source_kind"] not in DATASET_SOURCE_KINDS:
            issues.append(f"dataset manifest entry {source} has unsupported source_kind {item['source_kind']!r}")
        if item["rights_review_status"] not in RIGHTS_REVIEW_STATUSES:
            issues.append(
                f"dataset manifest entry {source} has unsupported rights_review_status {item['rights_review_status']!r}"
            )
        if item["release_inclusion"] not in RELEASE_INCLUSION_VALUES:
            issues.append(
                f"dataset manifest entry {source} has unsupported release_inclusion {item['release_inclusion']!r}"
            )
        for key in (
            "license_name",
            "rights_review_status",
            "release_inclusion",
            "citation",
            "access_date",
            "persistence_policy",
        ):
            if _contains_placeholder(item.get(key)):
                issues.append(f"dataset manifest entry {source} contains placeholder text in {key}")
        if not isinstance(item.get("experiments"), list) or not item["experiments"]:
            issues.append(f"dataset manifest entry {source} must list one or more experiments")
        if source.startswith("dataset/"):
            path = root / source
            if not path.exists():
                issues.append(f"dataset manifest entry points to missing local file: {source}")
                continue
            if item.get("release_inclusion") != "public_release_mirror":
                issues.append(f"local dataset manifest entry {source} must use release_inclusion=public_release_mirror")
            if item.get("source_kind") != "local_file":
                issues.append(f"local dataset manifest entry {source} must use source_kind=local_file")
            if item.get("size_bytes") != path.stat().st_size:
                issues.append(f"dataset manifest entry has incorrect size_bytes for {source}")
            if item.get("sha256") != _hash_file(path):
                issues.append(f"dataset manifest entry has incorrect sha256 for {source}")
            mirror_location = item.get("mirror_location")
            if not isinstance(mirror_location, str) or mirror_location != source:
                issues.append(f"dataset manifest entry {source} must mirror to its repository path")
        else:
            if item.get("source_kind") != "remote_url":
                issues.append(f"remote dataset manifest entry {source} must use source_kind=remote_url")
            if item.get("release_inclusion") not in {"source_fetch_only", "metadata_only"}:
                issues.append(
                    f"remote dataset manifest entry {source} must use release_inclusion source_fetch_only or metadata_only"
                )
            if item.get("rights_review_status") != "source_governed_fetch_only":
                issues.append(
                    f"remote dataset manifest entry {source} must use rights_review_status=source_governed_fetch_only"
                )
            if item.get("mirror_location") not in (None, "") and not isinstance(item.get("mirror_location"), str):
                issues.append(f"remote dataset manifest entry {source} has invalid mirror_location")
            if not isinstance(item.get("source_doi"), str):
                issues.append(f"remote dataset manifest entry {source} must include source_doi")
    return issues


def audit_publication_results(root_dir: str | Path) -> list[str]:
    issues: list[str] = []
    root = Path(root_dir)
    path = root / PUBLICATION_RESULTS_PATH
    if not path.exists():
        return [f"missing publication results bundle: {PUBLICATION_RESULTS_PATH.as_posix()}"]
    summary_path = root / PUBLICATION_RESULTS_SUMMARY_PATH
    if not summary_path.exists():
        issues.append(f"missing publication results summary: {PUBLICATION_RESULTS_SUMMARY_PATH.as_posix()}")
    source_path = root / PUBLICATION_RESULTS_SOURCE_PATH
    if not source_path.exists():
        issues.append(f"missing publication results source: {PUBLICATION_RESULTS_SOURCE_PATH.as_posix()}")
    payload = load_publication_results_bundle(root)
    required_top_level = {
        "format_version",
        "benchmark_version",
        "generated_on",
        "release_stage",
        "benchmark_summary",
        "coverage_summary",
        "coverage_by_instance",
        "baseline_inventory",
        "reporting_summary",
    }
    missing = sorted(key for key in required_top_level if key not in payload)
    if missing:
        issues.append(f"publication results bundle is missing keys: {', '.join(missing)}")
        return issues
    if payload["release_stage"] not in PUBLIC_RELEASE_STAGES:
        issues.append("publication results bundle release_stage must be public_release_candidate or published")
    coverage = payload.get("coverage_by_instance")
    if not isinstance(coverage, list):
        issues.append("publication results bundle coverage_by_instance must be a list")
        return issues
    expected_instances = set(expected_benchmark_instances(root))
    observed_instances: set[tuple[str, str]] = set()
    for entry in coverage:
        if not isinstance(entry, dict):
            issues.append("publication results bundle coverage_by_instance entries must be objects")
            continue
        experiment_id = entry.get("experiment_id")
        level = entry.get("level")
        if not isinstance(experiment_id, str) or not isinstance(level, str):
            issues.append("publication results bundle coverage entries must include experiment_id and level")
            continue
        observed_instances.add((experiment_id, level))
        run_status = entry.get("run_status")
        if run_status not in {"scored", "missing", "excluded"}:
            issues.append(
                f"publication results bundle coverage entry {experiment_id}:{level} has unsupported run_status {run_status!r}"
            )
        if run_status == "scored":
            scores = entry.get("score_summary")
            if not isinstance(scores, dict):
                issues.append(f"publication results bundle scored entry {experiment_id}:{level} is missing score_summary")
                continue
            for score_name in (
                "scientific_solution_score",
                "standard_analysis_score",
                "galaxy_execution_score",
            ):
                score = scores.get(score_name)
                if not isinstance(score, dict) or "value" not in score:
                    issues.append(
                        f"publication results bundle scored entry {experiment_id}:{level} is missing {score_name}"
                    )
    if observed_instances != expected_instances:
        missing_instances = sorted(expected_instances - observed_instances)
        extra_instances = sorted(observed_instances - expected_instances)
        if missing_instances:
            issues.append(
                "publication results bundle is missing benchmark instances: "
                + ", ".join(f"{experiment_id}:{level}" for experiment_id, level in missing_instances)
            )
        if extra_instances:
            issues.append(
                "publication results bundle contains unknown benchmark instances: "
                + ", ".join(f"{experiment_id}:{level}" for experiment_id, level in extra_instances)
            )
    baseline_inventory = payload.get("baseline_inventory")
    if not isinstance(baseline_inventory, list) or not baseline_inventory:
        issues.append("publication results bundle baseline_inventory must be a non-empty list")
    if payload.get("release_stage") == "published":
        incomplete = [
            f"{entry.get('experiment_id')}:{entry.get('level')}"
            for entry in coverage
            if isinstance(entry, dict) and entry.get("run_status") != "scored"
        ]
        if incomplete:
            issues.append(
                "published publication results bundle must score every benchmark instance; incomplete entries: "
                + ", ".join(incomplete)
            )
    return issues


def build_release_audit(root_dir: str | Path) -> dict[str, list[str]]:
    return {
        "public_task_alignment": audit_public_task_alignment(root_dir),
        "expected_result_fields": audit_expected_result_fields(root_dir),
        "dataset_manifest": audit_dataset_manifest(root_dir),
        "outputs_directory": audit_outputs_directory(root_dir),
        "publication_results": audit_publication_results(root_dir),
    }


def _z_value_for_confidence(confidence: float) -> float:
    return {
        0.90: 1.645,
        0.95: 1.96,
        0.99: 2.576,
    }.get(confidence, 1.96)


def summarize_numeric_values(values: Iterable[float], *, confidence: float = 0.95) -> dict[str, float | int | None]:
    series = [float(value) for value in values]
    if not series:
        raise ValueError("summarize_numeric_values requires at least one value")
    count = len(series)
    avg = mean(series)
    minimum = min(series)
    maximum = max(series)
    std = 0.0 if count == 1 else stdev(series)
    sem = 0.0 if count == 1 else std / math.sqrt(count)
    z = _z_value_for_confidence(confidence)
    margin = z * sem
    return {
        "n": count,
        "mean": avg,
        "stddev": std,
        "min": minimum,
        "max": maximum,
        "ci_low": avg - margin,
        "ci_high": avg + margin,
    }


def _extract_score_value(record: Mapping[str, Any], score_name: str) -> float | None:
    if score_name == "performance_score":
        value = record.get("performance_score")
        return None if value is None else float(value)
    summary = record.get("score_summary")
    if not isinstance(summary, Mapping):
        return None
    score = summary.get(score_name)
    if not isinstance(score, Mapping):
        return None
    value = score.get("value")
    return None if value is None else float(value)


def build_reliability_report(
    run_records: Iterable[Mapping[str, Any]],
    *,
    confidence: float = 0.95,
) -> dict[str, Any]:
    score_names = (
        "performance_score",
        "scientific_solution_score",
        "standard_analysis_score",
        "galaxy_execution_score",
    )
    grouped: dict[tuple[str, str, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    overall: dict[str, list[float]] = defaultdict(list)

    for record in run_records:
        task_id = str(record.get("task_id"))
        prompt_level = str(record.get("prompt_level"))
        environment = str(record.get("environment"))
        key = (task_id, prompt_level, environment)
        for score_name in score_names:
            value = _extract_score_value(record, score_name)
            if value is None:
                continue
            grouped[key][score_name].append(value)
            overall[score_name].append(value)

    by_group = []
    for (task_id, prompt_level, environment), scores in sorted(grouped.items()):
        by_group.append(
            {
                "task_id": task_id,
                "prompt_level": prompt_level,
                "environment": environment,
                "scores": {
                    score_name: summarize_numeric_values(values, confidence=confidence)
                    for score_name, values in sorted(scores.items())
                },
            }
        )

    return {
        "confidence_level": confidence,
        "overall": {
            score_name: summarize_numeric_values(values, confidence=confidence)
            for score_name, values in sorted(overall.items())
            if values
        },
        "by_task_prompt_environment": by_group,
    }


def collect_scored_run_snapshots(
    root_dir: str | Path,
    *,
    run_dirs: Iterable[str | Path] | None = None,
) -> list[dict[str, Any]]:
    root = Path(root_dir)
    candidates = [
        Path(path).resolve()
        for path in (
            run_dirs
            if run_dirs is not None
            else sorted(path.parent.parent for path in (root / "outputs").glob("*/results/result.json"))
        )
    ]
    if not candidates:
        source_path = root / PUBLICATION_RESULTS_SOURCE_PATH
        if source_path.exists():
            payload = load_publication_results_source(root)
            source_runs = payload.get("scored_runs", [])
            return [item for item in source_runs if isinstance(item, dict)]
        return []
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    from tools import benchmark_scorer

    snapshots: list[dict[str, Any]] = []
    for run_dir in candidates:
        experiment_id = benchmark_scorer.infer_experiment_id(run_dir, None)
        inferred_level = benchmark_scorer.infer_level(run_dir, None)
        bundle = benchmark_scorer.build_bundle(run_dir, experiment_id, inferred_level)
        normalized_result = benchmark_scorer.normalize_result(bundle)
        entries = []
        entries.extend(benchmark_scorer.build_scientific_comparisons(normalized_result, bundle))
        entries.extend(benchmark_scorer.build_standard_comparisons(normalized_result, bundle))
        entries.extend(benchmark_scorer.build_galaxy_comparisons(normalized_result, bundle))
        score_summaries = {
            "scientific_solution_score": benchmark_scorer.summarize_score(
                "scientific_solution_score",
                [entry for entry in entries if entry.score_name == "scientific_solution_score"],
                bundle,
            ),
            "standard_analysis_score": benchmark_scorer.summarize_score(
                "standard_analysis_score",
                [entry for entry in entries if entry.score_name == "standard_analysis_score"],
                bundle,
            ),
            "galaxy_execution_score": benchmark_scorer.summarize_score(
                "galaxy_execution_score",
                [entry for entry in entries if entry.score_name == "galaxy_execution_score"],
                bundle,
            ),
        }
        snapshots.append(
            {
                "run_dir": _relative_to_root(run_dir, root),
                "experiment_id": experiment_id,
                "level": bundle.level or "low_context",
                "level_inference": "explicit" if bundle.level else "fallback_low_context",
                "environment": "galaxy",
                "execution_mode": "legacy_live_output_snapshot",
                "publication_eligible": True,
                "normalized_result": normalized_result,
                "score_summary": {name: asdict(value) for name, value in score_summaries.items()},
                "normalization_notes": bundle.normalization_notes,
            }
        )
    return snapshots


def _group_publication_scores(scored_runs: Iterable[Mapping[str, Any]]) -> dict[str, list[float]]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for run in scored_runs:
        score_summary = run.get("score_summary")
        if not isinstance(score_summary, Mapping):
            continue
        for score_name in (
            "scientific_solution_score",
            "standard_analysis_score",
            "galaxy_execution_score",
        ):
            score = score_summary.get(score_name)
            if not isinstance(score, Mapping) or score.get("value") is None:
                continue
            grouped[score_name].append(float(score["value"]))
    return grouped


def build_publication_results_bundle(
    root_dir: str | Path,
    *,
    benchmark_version: str,
    release_stage: str,
    scored_runs: Iterable[Mapping[str, Any]],
) -> dict[str, Any]:
    root = Path(root_dir)
    if release_stage not in PUBLIC_RELEASE_STAGES:
        raise ValueError("release_stage must be public_release_candidate or published")
    expected = expected_benchmark_instances(root)
    grouped_runs: dict[tuple[str, str], list[Mapping[str, Any]]] = defaultdict(list)
    for run in scored_runs:
        experiment_id = run.get("experiment_id")
        level = run.get("level")
        if isinstance(experiment_id, str) and isinstance(level, str):
            grouped_runs[(experiment_id, level)].append(run)
    coverage_by_instance = []
    scored_instances = 0
    for experiment_id, level in expected:
        runs = grouped_runs.get((experiment_id, level), [])
        if runs:
            representative = runs[-1]
            coverage_by_instance.append(
                {
                    "experiment_id": experiment_id,
                    "level": level,
                    "run_status": "scored",
                    "run_count": len(runs),
                    "environment": representative.get("environment", "galaxy"),
                    "execution_mode": representative.get("execution_mode", "legacy_live_output_snapshot"),
                    "level_inference": representative.get("level_inference", "explicit"),
                    "score_summary": representative.get("score_summary"),
                    "run_dirs": [run.get("run_dir") for run in runs],
                }
            )
            scored_instances += 1
        else:
            coverage_by_instance.append(
                {
                    "experiment_id": experiment_id,
                    "level": level,
                    "run_status": "missing",
                    "run_count": 0,
                    "environment": None,
                    "execution_mode": None,
                    "level_inference": None,
                    "score_summary": None,
                    "run_dirs": [],
                }
            )
    grouped_scores = _group_publication_scores(scored_runs)
    reporting_summary = {
        score_name: summarize_numeric_values(values)
        for score_name, values in sorted(grouped_scores.items())
        if values
    }
    by_level = defaultdict(lambda: {"total_instances": 0, "scored_instances": 0})
    for entry in coverage_by_instance:
        bucket = by_level[entry["level"]]
        bucket["total_instances"] += 1
        if entry["run_status"] == "scored":
            bucket["scored_instances"] += 1
    return {
        "format_version": "galaxy_benchmark_publication_results_v1",
        "benchmark_id": "galaxy_benchmark",
        "benchmark_version": benchmark_version,
        "generated_on": datetime.now(UTC).date().isoformat(),
        "release_stage": release_stage,
        "benchmark_summary": {
            "task_groups": len({experiment_id for experiment_id, _ in expected}),
            "benchmark_instances": len(expected),
            "platform": "Galaxy",
            "result_scope": "authoring_repo_snapshot_without_field-level_ground_truth",
            "artifact_retention_policy": "publication summaries may reference historical run identifiers even when the underlying outputs/ directories are not shipped in the repository",
        },
        "coverage_summary": {
            "scored_instances": scored_instances,
            "missing_instances": len(expected) - scored_instances,
            "by_level": dict(sorted(by_level.items())),
        },
        "coverage_by_instance": coverage_by_instance,
        "baseline_inventory": [
            {
                "baseline_id": "transparent_heuristic_baseline",
                "status": "protocol_defined",
                "description": "Transparent benchmark-specific heuristic or rules baseline for paper tables.",
            },
            {
                "baseline_id": "strong_general_agent_baseline",
                "status": "protocol_defined",
                "description": "Strong general-purpose agent baseline executed under the canonical Galaxy protocol.",
            },
            {
                "baseline_id": "primary_system_under_study",
                "status": "release_specific",
                "description": "Primary agent or executor configuration evaluated in the publication.",
            },
        ],
        "reporting_summary": reporting_summary,
    }


def build_publication_results_markdown(bundle: Mapping[str, Any]) -> str:
    coverage = bundle.get("coverage_summary", {})
    reporting = bundle.get("reporting_summary", {})
    lines = [
        "# Publication Results Summary",
        "",
        "This file is a release-facing summary artifact that intentionally excludes field-level ground-truth tables.",
        "It may cite historical run identifiers even when the underlying `outputs/` directories are no longer shipped in the repository.",
        "",
        "## Coverage",
        "",
        f"- Benchmark instances: {bundle.get('benchmark_summary', {}).get('benchmark_instances', 0)}",
        f"- Scored instances: {coverage.get('scored_instances', 0)}",
        f"- Missing instances: {coverage.get('missing_instances', 0)}",
        "",
        "## Aggregate Scores",
        "",
        "| Score | N | Mean | Stddev | 95% CI |",
        "|---|---:|---:|---:|---:|",
    ]
    if reporting:
        for score_name, summary in sorted(reporting.items()):
            if not isinstance(summary, Mapping):
                continue
            ci = f"{float(summary['ci_low']):.3f} to {float(summary['ci_high']):.3f}"
            lines.append(
                f"| {score_name} | {int(summary['n'])} | {float(summary['mean']):.3f} | {float(summary['stddev']):.3f} | {ci} |"
            )
    else:
        lines.append("| no_scored_runs | 0 | n/a | n/a | n/a |")
    lines.extend(
        [
            "",
            "## Baseline Inventory",
            "",
            "| Baseline | Status | Description |",
            "|---|---|---|",
        ]
    )
    for baseline in bundle.get("baseline_inventory", []):
        if not isinstance(baseline, Mapping):
            continue
        lines.append(
            f"| {baseline.get('baseline_id', '')} | {baseline.get('status', '')} | {baseline.get('description', '')} |"
        )
    lines.append("")
    return "\n".join(lines)


def _copy_path(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def build_release_packages(root_dir: str | Path, output_dir: str | Path) -> dict[str, str]:
    root = Path(root_dir)
    output = Path(output_dir)
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    public_blind = output / "galaxy_benchmark_public_blind"
    publication_companion = output / "galaxy_benchmark_publication_companion"
    hidden_scoring = output / "galaxy_benchmark_hidden_scoring"
    for package_dir in (public_blind, publication_companion, hidden_scoring):
        package_dir.mkdir(parents=True, exist_ok=True)

    public_paths = [
        Path("README.md"),
        Path("SKILL.md"),
        Path("AGENTS.md"),
        Path("LICENSE"),
        Path("CITATION.cff"),
        Path("pyproject.toml"),
        Path("Makefile"),
        Path("Dockerfile"),
        Path("src"),
        Path("dataset"),
        Path("experiments"),
        Path("outputs"),
    ]
    publication_paths = [
        Path("README.md"),
        Path("docs"),
        Path("CITATION.cff"),
    ]
    hidden_paths = [
        Path("ground_truth"),
        Path("tools/benchmark_scorer.py"),
        Path("README.md"),
        Path("docs/formal_score_model.md"),
    ]
    for path in public_paths:
        src = root / path
        if not src.exists():
            continue
        if path == Path("docs"):
            continue
        _copy_path(src, public_blind / path)
    for tool_name in (
        "audit_benchmark_assets.py",
        "build_publication_results_bundle.py",
        "build_reliability_report.py",
        "build_release_packages.py",
    ):
        src = root / "tools" / tool_name
        if src.exists():
            _copy_path(src, public_blind / "tools" / tool_name)
    docs_public = public_blind / "docs"
    docs_public.mkdir(parents=True, exist_ok=True)
    for doc_path in sorted((root / "docs").glob("*")):
        if doc_path.name in {
            PUBLICATION_RESULTS_PATH.name,
            PUBLICATION_RESULTS_SUMMARY_PATH.name,
            PUBLICATION_RESULTS_SOURCE_PATH.name,
        }:
            continue
        _copy_path(doc_path, docs_public / doc_path.name)
    for path in publication_paths:
        src = root / path
        if not src.exists():
            continue
        if path == Path("docs"):
            _copy_path(src / PUBLICATION_RESULTS_PATH.name, publication_companion / "docs" / PUBLICATION_RESULTS_PATH.name)
            _copy_path(
                src / PUBLICATION_RESULTS_SUMMARY_PATH.name,
                publication_companion / "docs" / PUBLICATION_RESULTS_SUMMARY_PATH.name,
            )
            _copy_path(src / "benchmark_card.md", publication_companion / "docs" / "benchmark_card.md")
            _copy_path(
                src / "dataset_governance_manifest.json",
                publication_companion / "docs" / "dataset_governance_manifest.json",
            )
            _copy_path(
                src / PUBLICATION_RESULTS_SOURCE_PATH.name,
                publication_companion / "docs" / PUBLICATION_RESULTS_SOURCE_PATH.name,
            )
            _copy_path(src / "publication_release.md", publication_companion / "docs" / "publication_release.md")
            continue
        _copy_path(src, publication_companion / path)
    for path in hidden_paths:
        src = root / path
        if not src.exists():
            continue
        _copy_path(src, hidden_scoring / path)
    manifest = {
        "public_blind": _normalise_path(public_blind),
        "publication_companion": _normalise_path(publication_companion),
        "hidden_scoring": _normalise_path(hidden_scoring),
    }
    (output / "release_package_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest
