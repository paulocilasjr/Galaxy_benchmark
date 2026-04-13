from __future__ import annotations

import json
import tempfile
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from galaxy_benchmark.application.contracts import normalize_evaluator_payload
from galaxy_benchmark.application.publication import (
    build_reliability_report,
    build_release_audit,
    build_release_packages,
)
from galaxy_benchmark.application.registry import BenchmarkRegistry


class PublicationReadinessTest(unittest.TestCase):
    def test_release_audit_passes(self) -> None:
        audit = build_release_audit(ROOT_DIR)
        self.assertEqual(audit["public_task_alignment"], [])
        self.assertEqual(audit["expected_result_fields"], [])
        self.assertEqual(audit["dataset_manifest"], [])
        self.assertEqual(audit["outputs_directory"], [])
        self.assertEqual(audit["publication_results"], [])

    def test_normalized_evaluator_derives_missing_result_fields(self) -> None:
        ground_truth = json.loads((ROOT_DIR / "ground_truth" / "experiment_10.json").read_text(encoding="utf-8"))
        evaluator = normalize_evaluator_payload(ground_truth)
        names = {item["name"] for item in evaluator["expected_result_fields"]}
        self.assertIn("scientific_answer.baseline_alignment_rate_pct", names)
        self.assertIn("galaxy_execution.final_entity_type", names)
        self.assertIn("galaxy_execution.final_entity_name", names)
        self.assertIn("galaxy_execution.history_input_mode", names)
        self.assertIn("scientific_answer.baseline_alignment_rate_pct", evaluator["auto_derived_expected_result_fields"])

    def test_registry_normalizes_required_result_fields_for_legacy_experiments(self) -> None:
        registry = BenchmarkRegistry(ROOT_DIR)
        task = registry.load_experiment("experiment_11", "high_context")
        scientific_required = set(task["required_result_format"]["scientific_answer"]["required_fields"])
        self.assertIn("santana_tnswi1_r2", scientific_required)
        self.assertIn("wang_in_vivo_deg_count", scientific_required)
        self.assertIn("scf1_log2fc_wang_in_vitro", scientific_required)
        self.assertIn("id_mapping_method", scientific_required)
        galaxy_required = set(task["required_result_format"]["galaxy_execution"]["required_fields"])
        self.assertIn("final_entity_type", galaxy_required)
        self.assertIn("final_entity_name", galaxy_required)
        self.assertIn("history_input_mode", galaxy_required)
        self.assertIn("adaptation_summary", galaxy_required)

        replay_task = registry.load_experiment("experiment_10", "high_context")
        self.assertEqual(len(replay_task["inputs"]["datasets"]), 1)
        self.assertEqual(
            replay_task["inputs"]["datasets"][0]["path"],
            "dataset/experiment_10/manifest.tsv",
        )

    def test_reliability_report_computes_uncertainty(self) -> None:
        report = build_reliability_report(
            [
                {
                    "task_id": "experiment_1",
                    "prompt_level": "vague",
                    "environment": "galaxy",
                    "performance_score": 0.8,
                    "score_summary": {"scientific_solution_score": {"value": 0.7}},
                },
                {
                    "task_id": "experiment_1",
                    "prompt_level": "vague",
                    "environment": "galaxy",
                    "performance_score": 0.9,
                    "score_summary": {"scientific_solution_score": {"value": 0.8}},
                },
            ]
        )
        overall = report["overall"]["performance_score"]
        self.assertEqual(overall["n"], 2)
        self.assertAlmostEqual(overall["mean"], 0.85)
        self.assertGreater(overall["ci_high"], overall["ci_low"])

    def test_publication_results_bundle_covers_full_instance_matrix(self) -> None:
        bundle = json.loads((ROOT_DIR / "docs" / "publication_results_bundle.json").read_text(encoding="utf-8"))
        coverage = bundle["coverage_by_instance"]
        self.assertEqual(len(coverage), 33)
        self.assertTrue(any(entry["run_status"] == "scored" for entry in coverage))
        self.assertTrue(any(entry["run_status"] == "missing" for entry in coverage))

    def test_release_package_builder_separates_public_and_hidden_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            manifest = build_release_packages(ROOT_DIR, Path(temp_dir) / "release")
            public_root = Path(manifest["public_blind"])
            hidden_root = Path(manifest["hidden_scoring"])
            self.assertTrue((public_root / "experiments").exists())
            self.assertTrue((public_root / "dataset").exists())
            self.assertFalse((public_root / "ground_truth").exists())
            self.assertFalse((public_root / "docs" / "publication_results_bundle.json").exists())
            self.assertTrue((hidden_root / "ground_truth").exists())
            self.assertTrue((hidden_root / "tools" / "benchmark_scorer.py").exists())


if __name__ == "__main__":
    unittest.main()
