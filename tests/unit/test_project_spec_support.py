from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark.application.loaders import load_prompt_spec, load_run_record, load_task_spec
from galaxy_benchmark.application.reporting import benchmark_report_as_dict, build_benchmark_report
from galaxy_benchmark.application.scoring import (
    adaptability,
    aggregate_prompt_scores,
    run_performance,
    task_robustness,
    user_level_confidence,
)
from galaxy_benchmark.application.validation import ValidationError, validate_run_payload

class ProjectSpecSupportTest(unittest.TestCase):
    def test_example_task_prompt_and_run_load(self) -> None:
        task = load_task_spec(ROOT_DIR / "project_spec" / "examples" / "task.example.json")
        self.assertEqual(task.task_id, "de_rnaseq_001")

        with tempfile.TemporaryDirectory() as temp_dir:
            prompt_path = Path(temp_dir) / "prompt.json"
            prompt_path.write_text(
                json.dumps(
                    {
                        "prompt_id": "example_specific",
                        "task_id": "de_rnaseq_001",
                        "specificity_level": "specific",
                        "text": "Perform differential expression and return fold change and p-values.",
                    }
                ),
                encoding="utf-8",
            )
            prompt = load_prompt_spec(prompt_path)
            self.assertEqual(prompt.specificity_level.value, "specific")

        run = load_run_record(ROOT_DIR / "project_spec" / "examples" / "run.example.json")
        self.assertEqual(run.environment.value, "galaxy")
        self.assertAlmostEqual(run.performance_score, 0.923)
        self.assertEqual(run.execution_mode, "live_galaxy")
        self.assertTrue(run.benchmark_validity["publication_eligible"])
        self.assertEqual(run.execution_context["platform"], "Galaxy")

    def test_scoring_formulas_match_spec(self) -> None:
        component_scores = {
            "correctness": 0.95,
            "execution": 1.0,
            "scientific_validity": 0.9,
            "reproducibility": 0.95,
            "interpretation": 0.8,
        }
        self.assertAlmostEqual(run_performance(component_scores), 0.935)
        prompt_scores = {"vague": 0.8, "specific": 0.9, "very_specific": 1.0}
        self.assertAlmostEqual(aggregate_prompt_scores(prompt_scores), 0.901)
        self.assertAlmostEqual(task_robustness(prompt_scores), 0.8966666666666666)
        self.assertAlmostEqual(
            adaptability(
                {"vague": 0.7, "specific": 0.75, "very_specific": 0.8},
                {"vague": 0.8, "specific": 0.85, "very_specific": 0.9},
            ),
            0.1,
        )
        self.assertAlmostEqual(user_level_confidence([0.8, 0.6, 0.95], 0.7), 2 / 3)

    def test_report_generation_aggregates_environments(self) -> None:
        runs = [
            {
                "run_id": "r1",
                "task_id": "t1",
                "prompt_level": "vague",
                "environment": "open",
                "agent_id": "agentA",
                "input_prompt": "a",
                "status": "success",
                "component_scores": {},
                "performance_score": 0.5,
            },
            {
                "run_id": "r2",
                "task_id": "t1",
                "prompt_level": "specific",
                "environment": "open",
                "agent_id": "agentA",
                "input_prompt": "a",
                "status": "success",
                "component_scores": {},
                "performance_score": 0.6,
            },
            {
                "run_id": "r3",
                "task_id": "t1",
                "prompt_level": "very_specific",
                "environment": "open",
                "agent_id": "agentA",
                "input_prompt": "a",
                "status": "success",
                "component_scores": {},
                "performance_score": 0.7,
            },
            {
                "run_id": "r4",
                "task_id": "t1",
                "prompt_level": "vague",
                "environment": "galaxy",
                "agent_id": "agentA",
                "input_prompt": "a",
                "status": "success",
                "component_scores": {},
                "performance_score": 0.7,
            },
            {
                "run_id": "r5",
                "task_id": "t1",
                "prompt_level": "specific",
                "environment": "galaxy",
                "agent_id": "agentA",
                "input_prompt": "a",
                "status": "success",
                "component_scores": {},
                "performance_score": 0.8,
            },
            {
                "run_id": "r6",
                "task_id": "t1",
                "prompt_level": "very_specific",
                "environment": "galaxy",
                "agent_id": "agentA",
                "input_prompt": "a",
                "status": "success",
                "component_scores": {},
                "performance_score": 0.9,
            },
        ]
        report = build_benchmark_report("bench1", runs)
        payload = benchmark_report_as_dict(report)
        self.assertEqual(payload["task_count"], 1)
        self.assertAlmostEqual(payload["metrics"]["overall_performance"]["open"], 0.601)
        self.assertAlmostEqual(payload["metrics"]["overall_performance"]["galaxy"], 0.801)
        self.assertAlmostEqual(payload["metrics"]["adaptability"]["galaxy_minus_open"], 0.2)
        self.assertEqual(payload["metrics"]["overall_score_vector"], {})

    def test_report_generation_preserves_three_score_vector_when_available(self) -> None:
        runs = [
            {
                "run_id": "r1",
                "task_id": "t1",
                "prompt_level": "vague",
                "environment": "galaxy",
                "agent_id": "agentA",
                "input_prompt": "a",
                "status": "success",
                "component_scores": {
                    "correctness": 1.0,
                    "execution": 1.0,
                    "scientific_validity": 1.0,
                    "reproducibility": 1.0,
                    "interpretation": 1.0,
                },
                "performance_score": 1.0,
                "score_summary": {
                    "scientific_solution_score": {"value": 0.9},
                    "standard_analysis_score": {"value": 0.8},
                    "galaxy_execution_score": {"value": 0.7},
                },
            }
        ]
        report = build_benchmark_report("bench2", runs)
        payload = benchmark_report_as_dict(report)
        self.assertAlmostEqual(
            payload["metrics"]["overall_score_vector"]["scientific_solution_score"]["galaxy"],
            0.9,
        )
        self.assertAlmostEqual(
            payload["metrics"]["overall_score_vector"]["standard_analysis_score"]["galaxy"],
            0.8,
        )
        self.assertAlmostEqual(
            payload["metrics"]["overall_score_vector"]["galaxy_execution_score"]["galaxy"],
            0.7,
        )

    def test_validation_rejects_invalid_run(self) -> None:
        with self.assertRaises(ValidationError):
            validate_run_payload(
                {
                    "run_id": "x",
                    "task_id": "t1",
                    "prompt_level": "bad_level",
                    "environment": "galaxy",
                    "agent_id": "a",
                    "input_prompt": "test",
                    "status": "success",
                    "component_scores": {
                        "correctness": 1.0,
                        "execution": 1.0,
                        "scientific_validity": 1.0,
                        "reproducibility": 1.0,
                        "interpretation": 1.0,
                    },
                    "performance_score": 1.0,
                }
            )


if __name__ == "__main__":
    unittest.main()
