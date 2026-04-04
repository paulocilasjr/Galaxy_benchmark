"""Scoring services for benchmark trials."""

from __future__ import annotations

from typing import Any

from galaxy_benchmark.domain.models import GroundTruth, ScoreCard


class OutcomeScorer:
    """Score final outputs against normalized ground truth."""

    def score(self, actual_fields: dict[str, Any], ground_truth: GroundTruth) -> tuple[float, dict[str, float]]:
        expected = ground_truth.expected_fields
        if not expected:
            return 0.0, {}
        field_matches = 0
        for key, expected_value in expected.items():
            actual_value = actual_fields.get(key)
            matched = float(actual_value == expected_value)
            if isinstance(expected_value, float) and isinstance(actual_value, (int, float)):
                matched = float(round(float(actual_value), 4) == round(expected_value, 4))
            field_matches += int(bool(matched))
        field_match_score = field_matches / len(expected)

        artifact_correctness = float(actual_fields.get("__artifact_correctness", field_match_score))
        answer_report_correctness = float(actual_fields.get("__answer_report_correctness", field_match_score))
        metric_target_achieved = float(actual_fields.get("__metric_target_achieved", field_match_score))
        completion_under_budget = float(actual_fields.get("__completion_under_budget", 1.0))

        subscores = {
            "outcome_final_artifact_correctness": artifact_correctness,
            "outcome_answer_report_correctness": answer_report_correctness,
            "outcome_metric_target_achieved": metric_target_achieved,
            "outcome_completion_under_budget": completion_under_budget,
            "outcome_field_match_score": field_match_score,
        }
        total = (
            (artifact_correctness * 0.25)
            + (answer_report_correctness * 0.10)
            + (metric_target_achieved * 0.10)
            + (completion_under_budget * 0.05)
        ) / 0.50
        return total, subscores


class ProcessScorer:
    """Score process quality using trace evidence."""

    def score(self, details: dict[str, Any]) -> tuple[float, dict[str, float]]:
        checks = {
            "process_workflow_or_tool_selection_correctness": float(
                details.get("workflow_or_tool_selection_correctness", 0.0),
            ),
            "process_parameter_correctness": float(details.get("parameter_correctness", 0.0)),
            "process_dependency_handling_and_polling": float(
                details.get("dependency_handling_and_polling", 0.0),
            ),
            "process_provenance_completeness": float(details.get("provenance_completeness", 0.0)),
        }
        total = (
            (checks["process_workflow_or_tool_selection_correctness"] * 0.10)
            + (checks["process_parameter_correctness"] * 0.10)
            + (checks["process_dependency_handling_and_polling"] * 0.05)
            + (checks["process_provenance_completeness"] * 0.05)
        ) / 0.30
        return total, checks


class RobustnessScorer:
    """Score stability across repeated conditions."""

    def score(self, details: dict[str, Any] | list[bool]) -> tuple[float, dict[str, float]]:
        if isinstance(details, list):
            repeat_consistency = sum(1 for repeat in details if repeat) / len(details) if details else 0.0
            detail_map = {
                "average_prompt_tier_score": repeat_consistency,
                "worst_case_prompt_tier_score": repeat_consistency,
                "repeat_consistency": repeat_consistency,
                "recovery_after_initial_failure": repeat_consistency,
            }
        else:
            detail_map = {
                "average_prompt_tier_score": float(details.get("average_prompt_tier_score", 0.0)),
                "worst_case_prompt_tier_score": float(details.get("worst_case_prompt_tier_score", 0.0)),
                "repeat_consistency": float(details.get("repeat_consistency", 0.0)),
                "recovery_after_initial_failure": float(details.get("recovery_after_initial_failure", 0.0)),
            }
        total = (
            (detail_map["average_prompt_tier_score"] * 0.08)
            + (detail_map["worst_case_prompt_tier_score"] * 0.04)
            + (detail_map["repeat_consistency"] * 0.04)
            + (detail_map["recovery_after_initial_failure"] * 0.04)
        ) / 0.20
        return total, {f"robustness_{key}": value for key, value in detail_map.items()}


class ScoreAggregator:
    """Combine subgroup scorers into a scorecard."""

    def build(
        self,
        *,
        outcome: tuple[float, dict[str, float]],
        process: tuple[float, dict[str, float]],
        robustness: tuple[float, dict[str, float]],
        notes: list[str] | None = None,
    ) -> ScoreCard:
        outcome_score, outcome_subscores = outcome
        process_score, process_subscores = process
        robustness_score, robustness_subscores = robustness
        return ScoreCard(
            outcome_score=outcome_score,
            process_score=process_score,
            robustness_score=robustness_score,
            total_score=0.0,
            subscores={
                **outcome_subscores,
                **process_subscores,
                **robustness_subscores,
            },
            notes=notes or [],
        )
