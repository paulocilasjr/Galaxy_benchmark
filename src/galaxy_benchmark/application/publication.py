from __future__ import annotations

import json
import math
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
from statistics import mean, stdev
from typing import Any, Iterable, Mapping

from .contracts import normalize_evaluator_payload


DATASET_MANIFEST_PATH = Path("docs") / "dataset_governance_manifest.json"


def load_dataset_manifest(root_dir: str | Path) -> dict[str, dict[str, Any]]:
    path = Path(root_dir) / DATASET_MANIFEST_PATH
    payload = json.loads(path.read_text(encoding="utf-8"))
    items = payload.get("datasets", []) if isinstance(payload, dict) else []
    manifest: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            continue
        source = item.get("source")
        if isinstance(source, str):
            manifest[source] = item
    return manifest


def iter_public_experiment_payloads(root_dir: str | Path) -> Iterable[tuple[str, str, dict[str, Any]]]:
    root = Path(root_dir)
    for level in ("low_context", "medium_context", "high_context"):
        for path in sorted((root / "experiments" / level).glob("experiment_*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            experiment_id, body = next(iter(payload.items()))
            yield level, experiment_id, body


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


def _hash_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def audit_public_task_alignment(root_dir: str | Path) -> list[str]:
    issues: list[str] = []
    root = Path(root_dir)
    for ground_truth_path in sorted((root / "ground_truth").glob("experiment_*.json")):
        ground_truth = json.loads(ground_truth_path.read_text(encoding="utf-8"))
        variants = ground_truth.get("public_task_variants", {})
        for level in ("low_context", "medium_context", "high_context"):
            experiment_path = root / "experiments" / level / ground_truth_path.name
            experiment_payload = json.loads(experiment_path.read_text(encoding="utf-8"))
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
        payload = json.loads(path.read_text(encoding="utf-8"))
        normalized = normalize_evaluator_payload(payload)
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


def audit_dataset_manifest(root_dir: str | Path) -> list[str]:
    issues: list[str] = []
    root = Path(root_dir)
    manifest = load_dataset_manifest(root)
    for source in unique_experiment_inputs(root):
        item = manifest.get(source)
        if item is None:
            issues.append(f"dataset manifest is missing source: {source}")
            continue
        required_keys = {
            "source",
            "source_kind",
            "license",
            "citation",
            "access_date",
            "persistence_policy",
        }
        missing = sorted(key for key in required_keys if key not in item)
        if missing:
            issues.append(f"dataset manifest entry {source} is missing keys: {', '.join(missing)}")
        if source.startswith("dataset/"):
            path = root / source
            if not path.exists():
                issues.append(f"dataset manifest entry points to missing local file: {source}")
                continue
            if item.get("size_bytes") != path.stat().st_size:
                issues.append(f"dataset manifest entry has incorrect size_bytes for {source}")
            if item.get("sha256") != _hash_file(path):
                issues.append(f"dataset manifest entry has incorrect sha256 for {source}")
    return issues


def build_release_audit(root_dir: str | Path) -> dict[str, list[str]]:
    return {
        "public_task_alignment": audit_public_task_alignment(root_dir),
        "expected_result_fields": audit_expected_result_fields(root_dir),
        "dataset_manifest": audit_dataset_manifest(root_dir),
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
