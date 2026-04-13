from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
from typing import Any, Iterable, Mapping

from galaxy_benchmark.domain.enums import Environment
from galaxy_benchmark.domain.models import BenchmarkReport

from .scoring import (
    DEFAULT_PROMPT_WEIGHTS,
    aggregate_by_environment,
    environment_pair_adaptability,
    score_value_from_summary,
    task_robustness,
    user_level_confidence_by_environment,
    weighted_mean_available,
)


def _normalize_run_dict(record: Mapping[str, Any]) -> dict[str, Any]:
    normalized = dict(record)
    for key in ("prompt_level", "environment", "status"):
        value = normalized.get(key)
        if hasattr(value, "value"):
            normalized[key] = value.value
    return normalized


def _is_publication_eligible(record: Mapping[str, Any]) -> bool:
    validity = record.get("benchmark_validity")
    if not isinstance(validity, Mapping):
        return True
    eligible = validity.get("publication_eligible")
    return True if eligible is None else bool(eligible)


def build_benchmark_report(
    benchmark_id: str,
    run_records: Iterable[Mapping[str, Any]],
    *,
    confidence_threshold: float = 0.70,
) -> BenchmarkReport:
    normalized_runs = [_normalize_run_dict(record) for record in run_records]
    publication_eligible_runs = [record for record in normalized_runs if _is_publication_eligible(record)]
    task_prompt_environment: dict[str, dict[str, dict[str, float]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    agent_ids: set[str] = set()
    environments: set[str] = set()

    for record in normalized_runs:
        task_id = str(record["task_id"])
        environment = str(record["environment"])
        prompt_level = str(record["prompt_level"])
        task_prompt_environment[task_id][environment][prompt_level] = float(record["performance_score"])
        agent_ids.add(str(record["agent_id"]))
        environments.add(environment)

    per_task = []
    task_env_scores: dict[str, dict[str, float]] = {}
    task_robustness_scores: dict[str, dict[str, float]] = {}
    score_vectors: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    for record in normalized_runs:
        task_id = str(record["task_id"])
        environment = str(record["environment"])
        score_summary = record.get("score_summary")
        if isinstance(score_summary, dict):
            for score_name in (
                "scientific_solution_score",
                "standard_analysis_score",
                "galaxy_execution_score",
            ):
                value = score_value_from_summary(score_summary, score_name)
                if value is not None:
                    score_vectors[score_name][task_id][environment] = value
    for task_id, env_scores in sorted(task_prompt_environment.items()):
        env_performance = {
            environment: weighted_mean_available(prompt_scores, DEFAULT_PROMPT_WEIGHTS)
            for environment, prompt_scores in env_scores.items()
        }
        env_robustness = {
            environment: task_robustness(prompt_scores)
            for environment, prompt_scores in env_scores.items()
        }
        task_env_scores[task_id] = env_performance
        task_robustness_scores[task_id] = env_robustness
        per_task.append(
            {
                "task_id": task_id,
                "environment_performance": env_performance,
                "environment_robustness": env_robustness,
                "prompt_breakdown": env_scores,
            }
        )

    overall_performance = aggregate_by_environment(task_env_scores)
    overall_robustness = aggregate_by_environment(task_robustness_scores)
    overall_score_vector = {
        score_name: aggregate_by_environment(task_scores)
        for score_name, task_scores in sorted(score_vectors.items())
    }
    galaxy_minus_open = aggregate_by_environment(
        {
            task_id: {"galaxy_minus_open": value}
            for task_id, value in environment_pair_adaptability(
                normalized_runs,
                Environment.OPEN.value,
                Environment.GALAXY.value,
            ).items()
        }
    ).get("galaxy_minus_open", 0.0)
    skills_minus_galaxy = aggregate_by_environment(
        {
            task_id: {"skills_minus_galaxy": value}
            for task_id, value in environment_pair_adaptability(
                normalized_runs,
                Environment.GALAXY.value,
                Environment.GALAXY_SKILLS.value,
            ).items()
        }
    ).get("skills_minus_galaxy", 0.0)

    per_agent = []
    for agent_id in sorted(agent_ids):
        agent_runs = [record for record in normalized_runs if str(record["agent_id"]) == agent_id]
        per_agent.append(
            {
                "agent_id": agent_id,
                "run_count": len(agent_runs),
                "user_level_confidence": user_level_confidence_by_environment(
                    agent_runs,
                    confidence_threshold,
                ),
            }
        )

    return BenchmarkReport(
        benchmark_id=benchmark_id,
        agents=sorted(agent_ids),
        task_count=len(task_prompt_environment),
        environments=sorted(environments),
        metrics={
            "overall_performance": overall_performance,
            "overall_robustness": overall_robustness,
            "overall_score_vector": overall_score_vector,
            "run_partitioning": {
                "total_runs": len(normalized_runs),
                "publication_eligible_runs": len(publication_eligible_runs),
                "excluded_runs": len(normalized_runs) - len(publication_eligible_runs),
            },
            "adaptability": {
                "galaxy_minus_open": galaxy_minus_open,
                "skills_minus_galaxy": skills_minus_galaxy,
            },
            "user_level_confidence": user_level_confidence_by_environment(
                normalized_runs,
                confidence_threshold,
            ),
        },
        per_agent=per_agent,
        per_task=per_task,
    )


def benchmark_report_as_dict(report: BenchmarkReport) -> dict[str, Any]:
    return asdict(report)
