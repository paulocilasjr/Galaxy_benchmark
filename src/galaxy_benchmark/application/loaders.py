from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from galaxy_benchmark.domain.enums import Complexity, Environment, PromptLevel, RunStatus
from galaxy_benchmark.domain.models import PromptSpec, RunRecord, TaskSpec

from .validation import validate_prompt_payload, validate_run_payload, validate_task_payload


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def dump_json(payload: Any, path: str | Path) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_task_spec(path: str | Path) -> TaskSpec:
    payload = load_json(path)
    validate_task_payload(payload)
    return TaskSpec(
        task_id=payload["task_id"],
        title=payload["title"],
        domain=payload["domain"],
        description=payload["description"],
        complexity=Complexity(payload["complexity"]),
        datasets=payload["datasets"],
        ground_truth=payload["ground_truth"],
        acceptable_solutions=payload["acceptable_solutions"],
        requires_iteration=payload["requires_iteration"],
        iteration_budget=payload.get("iteration_budget"),
        evaluation_spec=payload["evaluation_spec"],
        tags=payload.get("tags", []),
    )


def load_prompt_spec(path: str | Path) -> PromptSpec:
    payload = load_json(path)
    validate_prompt_payload(payload)
    return PromptSpec(
        prompt_id=payload["prompt_id"],
        task_id=payload["task_id"],
        specificity_level=PromptLevel(payload["specificity_level"]),
        text=payload["text"],
    )


def load_run_record(path: str | Path) -> RunRecord:
    payload = load_json(path)
    validate_run_payload(payload)
    return RunRecord(
        run_id=payload["run_id"],
        task_id=payload["task_id"],
        prompt_level=PromptLevel(payload["prompt_level"]),
        environment=Environment(payload["environment"]),
        agent_id=payload["agent_id"],
        input_prompt=payload["input_prompt"],
        status=RunStatus(payload["status"]),
        component_scores=payload["component_scores"],
        performance_score=float(payload["performance_score"]),
        outputs=payload.get("outputs"),
        artifacts=payload.get("artifacts", []),
        trace=payload.get("trace"),
        timing=payload.get("timing"),
        failure_modes=payload.get("failure_modes", []),
        score_summary=payload.get("score_summary"),
    )


def as_json_dict(model: TaskSpec | PromptSpec | RunRecord) -> dict[str, Any]:
    payload = asdict(model)
    for key in ("complexity", "specificity_level", "prompt_level", "environment", "status"):
        if key in payload and hasattr(payload[key], "value"):
            payload[key] = payload[key].value
    return payload
