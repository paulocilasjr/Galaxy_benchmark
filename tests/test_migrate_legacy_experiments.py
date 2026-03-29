from __future__ import annotations

import sys
import importlib.util
import json
from pathlib import Path


def load_migration_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "migrate_legacy_experiments.py"
    spec = importlib.util.spec_from_file_location("migrate_legacy_experiments", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_snake_case_normalizes_legacy_field_names():
    module = load_migration_module()

    assert module.snake_case("roc-auc") == "roc_auc"
    assert module.snake_case("ROC-AUC") == "roc_auc"
    assert module.snake_case("total__steps") == "total_steps"
    assert module.snake_case("QC_step_detail") == "qc_step_detail"


def test_build_canonical_outputs_for_experiment_1():
    module = load_migration_module()
    repo_root = Path(__file__).resolve().parents[1]
    pair = module.LegacyPair(
        experiment_path=repo_root / "benchmark" / "tasks" / "legacy" / "raw" / "experiment_1.json",
        ground_truth_path=repo_root / "benchmark" / "ground_truth" / "legacy" / "raw" / "experiment_1.json",
    )
    legacy_experiment = json.loads(pair.experiment_path.read_text())
    legacy_ground_truth = json.loads(pair.ground_truth_path.read_text())

    task = module.build_canonical_task(pair, legacy_experiment)
    ground_truth = module.build_canonical_ground_truth(pair, legacy_ground_truth)

    assert task["task_id"] == "core_tabular_001"
    assert task["suite_id"] == "core"
    assert task["task_family"] == "single_tool_execution"
    assert task["task_subfamily"] == "tabular_ml"
    assert task["benchmark_pillars"] == [
        "platform_operation_capability",
        "prompt_robustness_and_trust",
    ]
    assert task["tool_hints"] == ["Tabular Learner"]
    assert task["expected_outputs"][2]["field"] == "roc_auc"
    assert task["success_criteria"]["required_fields"] == ["tool_name", "target", "roc_auc"]
    assert task["input_assets"][0]["role"] == "training_dataset"
    assert ground_truth["normalized_fields"]["roc_auc"] == 0.76
    assert ground_truth["legacy_field_names"]["roc_auc"] == "roc-auc"


def test_build_canonical_task_infers_missing_inputs_and_blueprint_family() -> None:
    module = load_migration_module()
    repo_root = Path(__file__).resolve().parents[1]
    pair = module.LegacyPair(
        experiment_path=repo_root / "benchmark" / "tasks" / "legacy" / "raw" / "experiment_8.json",
        ground_truth_path=repo_root / "benchmark" / "ground_truth" / "legacy" / "raw" / "experiment_8.json",
    )
    legacy_experiment = json.loads(pair.experiment_path.read_text())

    task = module.build_canonical_task(pair, legacy_experiment)

    assert task["task_id"] == "core_genome_annotation_001"
    assert task["task_family"] == "workflow_retrieval_and_execution"
    assert task["task_subfamily"] == "genome_annotation_and_qc"
    assert len(task["input_assets"]) == 5
    assert task["expected_outputs"][0]["field"] == "annotation_quality_tool"


def test_migration_writes_raw_and_canonical_fixtures(tmp_path):
    module = load_migration_module()
    repo_root = Path(__file__).resolve().parents[1]

    manifest = module.migrate_legacy_experiments(repo_root, tmp_path)

    raw_task = tmp_path / "benchmark" / "tasks" / "legacy" / "raw" / "experiment_1.json"
    canonical_task = tmp_path / "benchmark" / "tasks" / "legacy" / "canonical" / "experiment_1.json"
    raw_gt = tmp_path / "benchmark" / "ground_truth" / "legacy" / "raw" / "experiment_1.json"
    canonical_gt = tmp_path / "benchmark" / "ground_truth" / "legacy" / "canonical" / "experiment_1.json"
    manifest_path = tmp_path / "benchmark" / "tasks" / "legacy" / "manifest.json"

    assert raw_task.read_text() == (
        repo_root / "benchmark" / "tasks" / "legacy" / "raw" / "experiment_1.json"
    ).read_text()
    assert raw_gt.read_text() == (
        repo_root / "benchmark" / "ground_truth" / "legacy" / "raw" / "experiment_1.json"
    ).read_text()

    canonical_payload = json.loads(canonical_task.read_text())
    canonical_gt_payload = json.loads(canonical_gt.read_text())

    assert canonical_payload["metadata"]["legacy_experiment_name"] == "experiment_1"
    assert canonical_payload["task_id"] == "core_tabular_001"
    assert canonical_payload["expected_outputs"][2]["field"] == "roc_auc"
    assert canonical_gt_payload["normalized_fields"]["roc_auc"] == 0.76
    assert canonical_gt_payload["task_id"] == "core_tabular_001"

    written_manifest = json.loads(manifest_path.read_text())
    assert manifest["task_count"] == 9
    assert written_manifest["task_count"] == 9
    assert written_manifest["tasks"][0]["task_id"] == "core_tabular_001"
