from __future__ import annotations

from pathlib import Path

from galaxy_benchmark.application.prompting.services import PromptVariantGenerator
from galaxy_benchmark.infrastructure.repositories.json_task_repository import JsonTaskRepository


def test_repository_loads_generated_canonical_task_fixture() -> None:
    repository = JsonTaskRepository()
    task = repository.load_task(
        Path("benchmark/tasks/core_tabular_001.json"),
    )

    assert task.task_id == "core_tabular_001"
    assert task.task_family.value == "single_tool_execution"
    assert task.benchmark_pillars[0].value == "platform_operation_capability"
    assert task.normalized_output_field_names() == ["tool_name", "target", "roc_auc"]
    assert task.input_assets[0].path_or_url == "benchmark/datasets/local/core_tabular_001/Chowell_train_Response.tsv"


def test_repository_loads_generated_ground_truth_fixture() -> None:
    repository = JsonTaskRepository()
    ground_truth = repository.load_ground_truth(
        Path("benchmark/ground_truth/core_tabular_001.json"),
    )

    assert ground_truth.task_id == "core_tabular_001"
    assert ground_truth.expected_fields["roc_auc"] == 0.76
    assert ground_truth.metadata == {}


def test_prompt_generator_produces_one_brief_variant_per_tier() -> None:
    repository = JsonTaskRepository()
    task = repository.load_task(Path("benchmark/tasks/core_tabular_001.json"))

    variants = PromptVariantGenerator().generate(task)

    assert len(variants) == 3
    variant_ids = {variant.variant_id for variant in variants}
    assert "core_tabular_001_novice_brief" in variant_ids
    assert "core_tabular_001_intermediate_brief" in variant_ids
    assert "core_tabular_001_expert_brief" in variant_ids
    assert variants[0].content.startswith("Task")
    assert "Attachments" in variants[0].content
    assert "Requirements" in variants[0].content
    assert "Return" in variants[0].content
