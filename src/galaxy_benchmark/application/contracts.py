from __future__ import annotations

from pathlib import Path
from typing import Any


DEFAULT_RESULT_FORMAT = {
    "format_name": "galaxy_benchmark_result_v2",
    "scientific_answer": {"required_fields": []},
    "galaxy_execution": {
        "required_fields": [
            "final_entity_type",
            "final_entity_name",
            "history_input_mode",
            "adaptation_summary",
        ]
    },
}

RULE_ONLY_GALAXY_FIELDS = {
    "acceptable_adaptation_summaries",
    "required_capabilities",
    "required_execution_stages",
}


def prompt_level_from_specificity(level: str) -> str:
    return {
        "low_context": "vague",
        "medium_context": "specific",
        "high_context": "very_specific",
    }[level]


def _field_description(field_path: str) -> str:
    return f"Auto-derived expected result field for `{field_path}`."


def _append_expected_field(
    entries: list[dict[str, str]],
    seen: set[str],
    field_path: str,
    *,
    description: str | None = None,
) -> None:
    if field_path in seen:
        return
    entries.append({"name": field_path, "description": description or _field_description(field_path)})
    seen.add(field_path)


def _has_child_field(field_path: str, seen: set[str]) -> bool:
    prefix = f"{field_path}."
    return any(item.startswith(prefix) for item in seen)


def normalize_evaluator_payload(ground_truth_payload: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(ground_truth_payload, dict):
        return {}

    evaluator = ground_truth_payload.get("evaluation_spec", {})
    if not isinstance(evaluator, dict):
        evaluator = {}
    normalized = dict(evaluator)

    raw_expected = evaluator.get("expected_result_fields", [])
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    if isinstance(raw_expected, list):
        for item in raw_expected:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            if not isinstance(name, str):
                continue
            _append_expected_field(
                entries,
                seen,
                name,
                description=item.get("description") if isinstance(item.get("description"), str) else None,
            )

    scientific_answer = ground_truth_payload.get("scientific_answer", {})
    if isinstance(scientific_answer, dict):
        for key, value in scientific_answer.items():
            field_path = f"scientific_answer.{key}"
            if field_path in seen or _has_child_field(field_path, seen):
                continue
            _append_expected_field(entries, seen, field_path)

    galaxy_execution = ground_truth_payload.get("galaxy_execution", {})
    if isinstance(galaxy_execution, dict):
        for key, value in galaxy_execution.items():
            if key in RULE_ONLY_GALAXY_FIELDS:
                continue
            field_path = f"galaxy_execution.{key}"
            if field_path in seen or _has_child_field(field_path, seen):
                continue
            _append_expected_field(entries, seen, field_path)

    tier_specific = ground_truth_payload.get("tier_specific_expectations", {})
    if isinstance(tier_specific, dict):
        high_context = tier_specific.get("high_context", {})
        if isinstance(high_context, dict):
            for section in ("scientific_answer", "galaxy_execution"):
                section_payload = high_context.get(section, {})
                if not isinstance(section_payload, dict):
                    continue
                for key, value in section_payload.items():
                    if section == "galaxy_execution" and key in RULE_ONLY_GALAXY_FIELDS:
                        continue
                    field_path = f"{section}.{key}"
                    if field_path in seen or _has_child_field(field_path, seen):
                        continue
                    _append_expected_field(entries, seen, field_path)

    normalized["expected_result_fields"] = entries
    normalized["auto_derived_expected_result_fields"] = [
        item["name"]
        for item in entries
        if item.get("description", "").startswith("Auto-derived expected result field")
    ]
    return normalized


def _legacy_task_payload(raw_payload: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    if len(raw_payload) != 1:
        raise ValueError("Legacy experiment payload must contain exactly one top-level experiment key")
    experiment_id, payload = next(iter(raw_payload.items()))
    if not isinstance(payload, dict):
        raise ValueError("Legacy experiment payload body must be an object")
    return experiment_id, payload


def normalize_experiment_payload(
    raw_payload: dict[str, Any],
    *,
    level: str,
    ground_truth_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if "task_id" in raw_payload:
        payload = dict(raw_payload)
        payload.setdefault("level", level)
        payload.setdefault("required_result_format", DEFAULT_RESULT_FORMAT)
        return payload

    experiment_id, legacy = _legacy_task_payload(raw_payload)
    evaluator = normalize_evaluator_payload(ground_truth_payload)
    benchmark_axes = ground_truth_payload.get("benchmark_axes", {}) if isinstance(ground_truth_payload, dict) else {}

    raw_datasets = legacy.get("Inputs_Path", {}).get("dataset", [])
    if isinstance(raw_datasets, str):
        raw_datasets = [raw_datasets]

    datasets = []
    for path in raw_datasets:
        datasets.append({"name": Path(path).name, "path": path})

    scientific_required_fields: list[str] = []
    galaxy_required_fields = list(DEFAULT_RESULT_FORMAT["galaxy_execution"]["required_fields"])
    expected_result_fields = evaluator.get("expected_result_fields", [])
    if isinstance(expected_result_fields, list):
        for field in expected_result_fields:
            name = field.get("name") if isinstance(field, dict) else None
            if isinstance(name, str):
                if name.startswith("scientific_answer."):
                    scientific_required_fields.append(name.removeprefix("scientific_answer."))
                if name.startswith("galaxy_execution."):
                    field_name = name.removeprefix("galaxy_execution.")
                    if "." not in field_name and field_name not in galaxy_required_fields:
                        galaxy_required_fields.append(field_name)

    required_result_format = {
        "format_name": "galaxy_benchmark_result_v2",
        "scientific_answer": {"required_fields": sorted(dict.fromkeys(scientific_required_fields))},
        "galaxy_execution": {"required_fields": galaxy_required_fields},
    }

    task_family = evaluator.get("canonical_task_interpretation", {}).get("task_family")
    if not task_family:
        task_family = experiment_id

    focus_capabilities = evaluator.get("benchmark_metadata", {}).get("capabilities_under_test", [])
    return {
        "format_version": "galaxy_benchmark_task_input_v2_legacy_compatible",
        "task_id": experiment_id,
        "task_group_id": f"{experiment_id}_prompt_tiers",
        "level": level,
        "task_family": task_family,
        "benchmark_axes": {
            "scientist_level_band": benchmark_axes.get("scientist_level_band", "unknown"),
            "galaxy_complexity_band": benchmark_axes.get("galaxy_complexity_band", "unknown"),
            "focus_capabilities": focus_capabilities if isinstance(focus_capabilities, list) else [],
        },
        "required_result_format": required_result_format,
        "execution_environment": {
            "platform": "Galaxy",
            "galaxy_instance": "https://usegalaxy.org/",
            "execution_rule": "After you form a plan for the analysis, execute that plan in Galaxy.",
        },
        "inputs": {"datasets": datasets},
        "user_prompt": legacy.get("Prompt", ""),
        "legacy_source": {"Task": legacy.get("Task", ""), "Inputs_Path": legacy.get("Inputs_Path", {})},
    }
