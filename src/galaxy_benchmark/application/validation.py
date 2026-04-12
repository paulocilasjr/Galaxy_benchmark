from __future__ import annotations

from typing import Any, Mapping


class ValidationError(ValueError):
    """Raised when a payload does not satisfy the benchmark contract."""


def _require_object(payload: Any, *, schema_name: str) -> Mapping[str, Any]:
    if not isinstance(payload, dict):
        raise ValidationError(f"{schema_name} must be a JSON object")
    return payload


def _require_keys(payload: Mapping[str, Any], required: set[str], *, schema_name: str) -> None:
    missing = sorted(required - set(payload))
    if missing:
        raise ValidationError(f"{schema_name} is missing required fields: {', '.join(missing)}")


def _reject_extra_keys(payload: Mapping[str, Any], allowed: set[str], *, schema_name: str) -> None:
    extra = sorted(set(payload) - allowed)
    if extra:
        raise ValidationError(f"{schema_name} contains unsupported fields: {', '.join(extra)}")


def validate_task_payload(payload: Any) -> None:
    data = _require_object(payload, schema_name="Task payload")
    allowed = {
        "task_id",
        "title",
        "domain",
        "description",
        "complexity",
        "datasets",
        "ground_truth",
        "acceptable_solutions",
        "requires_iteration",
        "iteration_budget",
        "evaluation_spec",
        "tags",
    }
    required = {
        "task_id",
        "title",
        "domain",
        "description",
        "complexity",
        "datasets",
        "ground_truth",
        "acceptable_solutions",
        "requires_iteration",
        "evaluation_spec",
    }
    _require_keys(data, required, schema_name="Task payload")
    _reject_extra_keys(data, allowed, schema_name="Task payload")
    if data["complexity"] not in {"simple", "complex", "very_complex"}:
        raise ValidationError("Task payload complexity must be one of: simple, complex, very_complex")
    if not isinstance(data["datasets"], list):
        raise ValidationError("Task payload datasets must be a list")
    for index, dataset in enumerate(data["datasets"]):
        if not isinstance(dataset, dict):
            raise ValidationError(f"Task payload dataset {index} must be an object")
        _require_keys(dataset, {"name", "path", "format"}, schema_name=f"Task dataset {index}")
    if not isinstance(data["ground_truth"], dict):
        raise ValidationError("Task payload ground_truth must be an object")
    if not isinstance(data["acceptable_solutions"], list):
        raise ValidationError("Task payload acceptable_solutions must be a list")
    if not isinstance(data["requires_iteration"], bool):
        raise ValidationError("Task payload requires_iteration must be a boolean")
    if data.get("iteration_budget") is not None:
        if not isinstance(data["iteration_budget"], int) or data["iteration_budget"] < 1:
            raise ValidationError("Task payload iteration_budget must be null or an integer >= 1")
    if not isinstance(data["evaluation_spec"], dict):
        raise ValidationError("Task payload evaluation_spec must be an object")
    if "tags" in data and not isinstance(data["tags"], list):
        raise ValidationError("Task payload tags must be a list when present")


def validate_prompt_payload(payload: Any) -> None:
    data = _require_object(payload, schema_name="Prompt payload")
    allowed = {"prompt_id", "task_id", "specificity_level", "text"}
    required = set(allowed)
    _require_keys(data, required, schema_name="Prompt payload")
    _reject_extra_keys(data, allowed, schema_name="Prompt payload")
    if data["specificity_level"] not in {"vague", "specific", "very_specific"}:
        raise ValidationError(
            "Prompt payload specificity_level must be one of: vague, specific, very_specific"
        )
    if not isinstance(data["text"], str) or not data["text"].strip():
        raise ValidationError("Prompt payload text must be a non-empty string")


def validate_run_payload(payload: Any) -> None:
    data = _require_object(payload, schema_name="Run payload")
    allowed = {
        "run_id",
        "task_id",
        "prompt_level",
        "environment",
        "agent_id",
        "input_prompt",
        "outputs",
        "artifacts",
        "trace",
        "status",
        "timing",
        "failure_modes",
        "component_scores",
        "performance_score",
        "score_summary",
    }
    required = {
        "run_id",
        "task_id",
        "prompt_level",
        "environment",
        "agent_id",
        "input_prompt",
        "status",
        "component_scores",
        "performance_score",
    }
    _require_keys(data, required, schema_name="Run payload")
    _reject_extra_keys(data, allowed, schema_name="Run payload")
    if data["prompt_level"] not in {"vague", "specific", "very_specific"}:
        raise ValidationError("Run payload prompt_level must be one of: vague, specific, very_specific")
    if data["environment"] not in {"open", "galaxy", "galaxy_skills"}:
        raise ValidationError("Run payload environment must be one of: open, galaxy, galaxy_skills")
    if data["status"] not in {"success", "partial", "failed", "timeout"}:
        raise ValidationError("Run payload status must be one of: success, partial, failed, timeout")
    if data.get("outputs") is not None and not isinstance(data["outputs"], dict):
        raise ValidationError("Run payload outputs must be an object or null")
    if "artifacts" in data and not isinstance(data["artifacts"], list):
        raise ValidationError("Run payload artifacts must be a list when present")
    if data.get("trace") is not None and not isinstance(data["trace"], list):
        raise ValidationError("Run payload trace must be a list or null")
    if data.get("timing") is not None and not isinstance(data["timing"], dict):
        raise ValidationError("Run payload timing must be an object or null")
    if "failure_modes" in data and not isinstance(data["failure_modes"], list):
        raise ValidationError("Run payload failure_modes must be a list when present")
    if data.get("score_summary") is not None and not isinstance(data["score_summary"], dict):
        raise ValidationError("Run payload score_summary must be an object or null")
    component_scores = data["component_scores"]
    if not isinstance(component_scores, dict):
        raise ValidationError("Run payload component_scores must be an object")
    required_scores = {
        "correctness",
        "execution",
        "scientific_validity",
        "reproducibility",
        "interpretation",
    }
    _require_keys(component_scores, required_scores, schema_name="Run payload component_scores")
    for key in required_scores:
        value = component_scores[key]
        if not isinstance(value, (int, float)) or not 0 <= float(value) <= 1:
            raise ValidationError(f"Run payload component_scores.{key} must be a number in [0, 1]")
    performance = data["performance_score"]
    if not isinstance(performance, (int, float)) or not 0 <= float(performance) <= 1:
        raise ValidationError("Run payload performance_score must be a number in [0, 1]")
