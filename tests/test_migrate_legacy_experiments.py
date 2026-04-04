from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_migration_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "migrate_legacy_experiments.py"
    spec = importlib.util.spec_from_file_location("migrate_legacy_experiments", script_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def write_legacy_pair(
    tmp_path: Path,
    *,
    experiment_id: str,
    experiment_payload: dict[str, object],
    ground_truth_payload: dict[str, object],
):
    experiments_dir = tmp_path / "experiments"
    ground_truth_dir = tmp_path / "ground_truth"
    experiments_dir.mkdir(parents=True, exist_ok=True)
    ground_truth_dir.mkdir(parents=True, exist_ok=True)

    experiment_path = experiments_dir / f"{experiment_id}.json"
    ground_truth_path = ground_truth_dir / f"{experiment_id}.json"
    experiment_path.write_text(json.dumps(experiment_payload, indent=2) + "\n")
    ground_truth_path.write_text(json.dumps(ground_truth_payload, indent=2) + "\n")
    return experiment_path, ground_truth_path


def test_snake_case_normalizes_legacy_field_names():
    module = load_migration_module()

    assert module.snake_case("roc-auc") == "roc_auc"
    assert module.snake_case("ROC-AUC") == "roc_auc"
    assert module.snake_case("total__steps") == "total_steps"
    assert module.snake_case("QC_step_detail") == "qc_step_detail"


def test_build_canonical_outputs_for_experiment_1(tmp_path: Path):
    module = load_migration_module()
    experiment_path, ground_truth_path = write_legacy_pair(
        tmp_path,
        experiment_id="experiment_1",
        experiment_payload={
            "title": "machine learning model",
            "level": 1,
            "prompt": {
                "task": "Create a new history in Galaxy and upload the datasets. Train a machine learning model to predict the response variable based on the given training dataset and evaluate its performance on the test dataset.",
                "dataset": [
                    {
                        "name": "Chowell_train_Response.tsv",
                        "path": "dataset/experiment_1/Chowell_train_Response.tsv",
                    },
                    {
                        "name": "Chowell_test_Response.tsv",
                        "path": "dataset/experiment_1/Chowell_test_Response.tsv",
                    },
                ],
                "galaxy_instance": "https://usegalaxy.org/",
                "tool": {"name": "Tabular Learner"},
            },
            "experiment_outputs": {
                "tool_name": "the tool used in galaxy",
                "target": "look in the parameters of the report for the target and its value",
                "roc-auc": "look in the test summary for the ROC-AUC value",
            },
        },
        ground_truth_payload={
            "tool_name": "Tabular Learner",
            "target": "Response",
            "roc-auc": 0.76,
        },
    )
    pair = module.LegacyPair(experiment_path=experiment_path, ground_truth_path=ground_truth_path)
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
    assert task["input_assets"][0]["path_or_url"] == "benchmark/datasets/local/core_tabular_001/Chowell_train_Response.tsv"
    assert task["metadata"]["benchmark_hypotheses"] == ["H1", "H2"]
    assert ground_truth["expected_fields"]["roc_auc"] == 0.76
    assert ground_truth["metadata"]["field_aliases"] == {"roc_auc": "roc-auc"}


def test_build_canonical_task_infers_missing_inputs_and_clean_dataset_paths(tmp_path: Path) -> None:
    module = load_migration_module()
    experiment_path, ground_truth_path = write_legacy_pair(
        tmp_path,
        experiment_id="experiment_8",
        experiment_payload={
            "title": "Genome annotation",
            "level": 8,
            "prompt": {
                "task": (
                    "I need to perform a genome annotation of the samples I got and evaluate the quality "
                    "of the annotation. All files are in the benchmark/datasets/local/experiment_8 directory."
                ),
                "history_name": "annotation_history",
            },
            "experiment_outputs": {
                "tool_name_1": "Retrieve what was tool used for evaluation of the annotation quality.",
                "tool_name_2": "Retrieve what was tool used for visualization of the results",
                "total_tools": "Count the number of tools used in the pipeline.",
            },
        },
        ground_truth_payload={
            "tool_name_1": "BUSCO",
            "tool_name_2": "JBrowse",
            "total_tools": 12,
        },
    )
    pair = module.LegacyPair(experiment_path=experiment_path, ground_truth_path=ground_truth_path)
    legacy_experiment = json.loads(pair.experiment_path.read_text())

    task = module.build_canonical_task(pair, legacy_experiment)

    assert task["task_id"] == "core_genome_annotation_001"
    assert task["task_family"] == "workflow_retrieval_and_execution"
    assert task["task_subfamily"] == "genome_annotation_and_qc"
    assert len(task["input_assets"]) == 5
    assert task["input_assets"][0]["path_or_url"] == (
        "benchmark/datasets/local/core_genome_annotation_001/S_pombe_chrIII_genome.fasta"
    )
    assert "benchmark/datasets/local/core_genome_annotation_001 directory" in task["description"]
    assert task["expected_outputs"][0]["field"] == "annotation_quality_tool"


def test_migration_writes_clean_flattened_fixtures(tmp_path: Path):
    module = load_migration_module()
    write_legacy_pair(
        tmp_path,
        experiment_id="experiment_1",
        experiment_payload={
            "title": "machine learning model",
            "level": 1,
            "prompt": {
                "task": "Create a new history in Galaxy and upload the datasets.",
                "dataset": [
                    {
                        "name": "Chowell_train_Response.tsv",
                        "path": "dataset/experiment_1/Chowell_train_Response.tsv",
                    },
                ],
                "tool": {"name": "Tabular Learner"},
            },
            "experiment_outputs": {
                "tool_name": "the tool used in galaxy",
                "roc-auc": "look in the test summary for the ROC-AUC value",
            },
        },
        ground_truth_payload={
            "tool_name": "Tabular Learner",
            "roc-auc": 0.76,
        },
    )

    manifest = module.migrate_legacy_experiments(tmp_path, tmp_path)

    canonical_task = tmp_path / "benchmark" / "tasks" / "core_tabular_001.json"
    canonical_gt = tmp_path / "benchmark" / "ground_truth" / "core_tabular_001.json"
    manifest_path = tmp_path / "benchmark" / "migration_manifest.json"

    canonical_payload = json.loads(canonical_task.read_text())
    canonical_gt_payload = json.loads(canonical_gt.read_text())
    written_manifest = json.loads(manifest_path.read_text())

    assert canonical_payload["metadata"]["benchmark_hypotheses"] == ["H1", "H2"]
    assert canonical_payload["input_assets"][0]["path_or_url"] == (
        "benchmark/datasets/local/core_tabular_001/Chowell_train_Response.tsv"
    )
    assert canonical_gt_payload["expected_fields"]["roc_auc"] == 0.76
    assert canonical_gt_payload["metadata"]["field_aliases"] == {"roc_auc": "roc-auc"}
    assert manifest["task_count"] == 1
    assert written_manifest["task_count"] == 1
    assert written_manifest["tasks"][0]["task_id"] == "core_tabular_001"
    assert written_manifest["tasks"][0]["canonical_task_path"] == "benchmark/tasks/core_tabular_001.json"
