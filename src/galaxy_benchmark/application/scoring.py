from __future__ import annotations

from collections import defaultdict
from statistics import mean
from typing import Iterable, Mapping

from galaxy_benchmark.domain.enums import Environment, PromptLevel


DEFAULT_COMPONENT_WEIGHTS: dict[str, float] = {
    "correctness": 0.35,
    "execution": 0.20,
    "scientific_validity": 0.20,
    "reproducibility": 0.15,
    "interpretation": 0.10,
}

DEFAULT_PROMPT_WEIGHTS: dict[str, float] = {
    PromptLevel.VAGUE.value: 0.33,
    PromptLevel.SPECIFIC.value: 0.33,
    PromptLevel.VERY_SPECIFIC.value: 0.34,
}

PRACTICAL_SUPPORT_PROMPT_WEIGHTS: dict[str, float] = {
    PromptLevel.VAGUE.value: 0.40,
    PromptLevel.SPECIFIC.value: 0.35,
    PromptLevel.VERY_SPECIFIC.value: 0.25,
}

USER_LEVEL_BY_PROMPT: dict[str, str] = {
    PromptLevel.VAGUE.value: "novice",
    PromptLevel.SPECIFIC.value: "intermediate",
    PromptLevel.VERY_SPECIFIC.value: "expert",
}


def _weighted_sum(values: Mapping[str, float], weights: Mapping[str, float]) -> float:
    missing = [key for key in weights if key not in values]
    if missing:
        raise KeyError(f"Missing weighted values for keys: {', '.join(sorted(missing))}")
    return sum(float(values[key]) * float(weights[key]) for key in weights)


def weighted_mean_available(values: Mapping[str, float], weights: Mapping[str, float]) -> float:
    present = {key: float(weights[key]) for key in weights if key in values}
    if not present:
        raise KeyError("No overlapping weighted values were provided")
    total_weight = sum(present.values())
    return sum(float(values[key]) * weight for key, weight in present.items()) / total_weight


def score_value_from_summary(score_summary: Mapping[str, object], score_name: str) -> float | None:
    score = score_summary.get(score_name)
    if not isinstance(score, Mapping):
        return None
    value = score.get("value")
    if value is None:
        return None
    return float(value)


def run_performance(
    component_scores: Mapping[str, float],
    weights: Mapping[str, float] | None = None,
) -> float:
    return _weighted_sum(component_scores, weights or DEFAULT_COMPONENT_WEIGHTS)


def aggregate_prompt_scores(
    prompt_scores: Mapping[str, float],
    prompt_weights: Mapping[str, float] | None = None,
) -> float:
    return _weighted_sum(prompt_scores, prompt_weights or DEFAULT_PROMPT_WEIGHTS)


def task_robustness(
    prompt_scores: Mapping[str, float],
    *,
    alpha: float = 1.0,
    beta: float = 0.5,
) -> float:
    vals = [float(value) for value in prompt_scores.values()]
    prompt_mean = mean(vals)
    prompt_var = sum((value - prompt_mean) ** 2 for value in vals) / len(vals)
    return alpha * prompt_mean - beta * prompt_var


def adaptability(
    scores_a: Mapping[str, float],
    scores_b: Mapping[str, float],
    prompt_weights: Mapping[str, float] | None = None,
) -> float:
    weights = prompt_weights or DEFAULT_PROMPT_WEIGHTS
    overlapping = {
        prompt: float(scores_b[prompt]) - float(scores_a[prompt])
        for prompt in weights
        if prompt in scores_a and prompt in scores_b
    }
    return weighted_mean_available(overlapping, weights)


def user_level_confidence(task_prompt_scores: Iterable[float], threshold: float) -> float:
    scores = [float(score) for score in task_prompt_scores]
    if not scores:
        raise ValueError("task_prompt_scores must contain at least one score")
    passed = sum(1 for score in scores if score >= threshold)
    return passed / len(scores)


def aggregate_by_environment(
    task_scores_by_environment: Mapping[str, Mapping[str, float]],
    task_weights: Mapping[str, float] | None = None,
) -> dict[str, float]:
    task_ids = sorted(task_scores_by_environment)
    if not task_ids:
        return {}
    weights = task_weights or {task_id: 1.0 / len(task_ids) for task_id in task_ids}
    totals: dict[str, float] = defaultdict(float)
    for task_id, env_scores in task_scores_by_environment.items():
        for environment, value in env_scores.items():
            totals[environment] += float(value) * float(weights[task_id])
    return dict(totals)


def user_level_confidence_by_environment(
    run_records: Iterable[Mapping[str, object]],
    threshold: float,
) -> dict[str, float]:
    grouped: dict[str, list[float]] = defaultdict(list)
    for record in run_records:
        prompt_level = str(record["prompt_level"])
        environment = str(record["environment"])
        grouped[f"{USER_LEVEL_BY_PROMPT[prompt_level]}_{environment}"].append(
            float(record["performance_score"])
        )
    return {
        key: user_level_confidence(scores, threshold)
        for key, scores in sorted(grouped.items())
    }


def environment_pair_adaptability(
    run_records: Iterable[Mapping[str, object]],
    from_environment: Environment | str,
    to_environment: Environment | str,
    prompt_weights: Mapping[str, float] | None = None,
) -> dict[str, float]:
    source = str(from_environment)
    target = str(to_environment)
    per_task: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    for record in run_records:
        per_task[str(record["task_id"])][str(record["environment"])][str(record["prompt_level"])] = float(
            record["performance_score"]
        )
    result: dict[str, float] = {}
    for task_id, env_map in per_task.items():
        if source in env_map and target in env_map:
            result[task_id] = adaptability(
                env_map[source],
                env_map[target],
                prompt_weights=prompt_weights,
            )
    return result
