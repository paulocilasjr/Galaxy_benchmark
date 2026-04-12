#!/usr/bin/env python3
"""Regression coverage for the benchmark scorer."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools import benchmark_scorer as scorer


def score_run(run_name: str, level: str | None = None):
    run_dir = scorer.ROOT_DIR / "outputs" / run_name
    experiment_id = scorer.infer_experiment_id(run_dir, None)
    bundle = scorer.build_bundle(run_dir, experiment_id, level)
    normalized_result = scorer.normalize_result(bundle)

    entries = []
    entries.extend(scorer.build_scientific_comparisons(normalized_result, bundle))
    entries.extend(scorer.build_standard_comparisons(normalized_result, bundle))
    entries.extend(scorer.build_galaxy_comparisons(normalized_result, bundle))

    score_summaries = {
        "scientific_solution_score": scorer.summarize_score(
            "scientific_solution_score",
            [entry for entry in entries if entry.score_name == "scientific_solution_score"],
            bundle,
        ),
        "standard_analysis_score": scorer.summarize_score(
            "standard_analysis_score",
            [entry for entry in entries if entry.score_name == "standard_analysis_score"],
            bundle,
        ),
        "galaxy_execution_score": scorer.summarize_score(
            "galaxy_execution_score",
            [entry for entry in entries if entry.score_name == "galaxy_execution_score"],
            bundle,
        ),
    }
    return normalized_result, entries, score_summaries


class BenchmarkScorerRegressionTest(unittest.TestCase):
    def test_experiment_1_normalizes_legacy_metric_object(self) -> None:
        normalized, _, summaries = score_run("20260304_162800_experiment_1")
        self.assertEqual(normalized["scientific_answer"]["primary_metric"]["name"], "ROC-AUC")
        self.assertEqual(normalized["scientific_answer"]["primary_metric"]["split"], "test")
        self.assertEqual(normalized["scientific_answer"]["primary_metric"]["value"], 0.87)
        self.assertEqual(summaries["scientific_solution_score"].value, 1.0)
        self.assertLess(summaries["galaxy_execution_score"].value, 0.85)

    def test_experiment_4_parses_descriptive_step_count_and_input_type(self) -> None:
        normalized, entries, summaries = score_run("20260312_220316_experiment_4")
        self.assertEqual(normalized["galaxy_execution"]["workflow_tool_step_count"], 27)
        workflow_input_entry = next(
            entry for entry in entries if entry.field_path == "scientific_answer.workflow_input_type"
        )
        self.assertEqual(workflow_input_entry.match_status, "match")
        self.assertEqual(summaries["galaxy_execution_score"].value, 1.0)

    def test_experiment_6_high_context_scores_cleanly(self) -> None:
        _, _, summaries = score_run("20260319_222516_experiment_6", level="high_context")
        self.assertEqual(summaries["scientific_solution_score"].value, 1.0)
        self.assertEqual(summaries["standard_analysis_score"].value, 1.0)
        self.assertEqual(summaries["galaxy_execution_score"].value, 1.0)

    def test_experiment_8_uses_completed_tool_count_and_maker_entity(self) -> None:
        normalized, _, summaries = score_run("20260325_184652_experiment_8", level="high_context")
        self.assertEqual(normalized["galaxy_execution"]["total_tool_executions"], 7)
        self.assertIn("maker", normalized["galaxy_execution"]["final_entity_name"].lower())
        self.assertEqual(summaries["galaxy_execution_score"].value, 1.0)

    def test_experiment_5_medium_context_standard_score_is_active(self) -> None:
        _, _, summaries = score_run("20260313_193404_experiment_5", level="medium_context")
        self.assertEqual(summaries["standard_analysis_score"].value, 1.0)
        self.assertEqual(summaries["standard_analysis_score"].status, "pass")


if __name__ == "__main__":
    unittest.main()
