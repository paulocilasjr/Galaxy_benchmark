"""Migration use case for legacy benchmark definitions."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from galaxy_benchmark.domain.enums import BenchmarkPillar, KnowledgeCondition, SourceType, TaskFamily
from galaxy_benchmark.domain.exceptions import LegacyMigrationError
from galaxy_benchmark.domain.models import (
    BenchmarkTask,
    ExpectedOutputField,
    GroundTruth,
    InputAsset,
    KnowledgeRequirement,
    ProcessConstraints,
    SuccessCriteria,
    TaskDefinition,
)

LEGACY_TASK_SPECS: dict[str, dict[str, Any]] = {
    "experiment_1": {
        "task_id": "core_tabular_001",
        "suite_id": "core",
        "task_family": TaskFamily.SINGLE_TOOL_EXECUTION,
        "task_subfamily": "tabular_ml",
        "benchmark_pillars": [
            BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY,
            BenchmarkPillar.PROMPT_ROBUSTNESS_AND_TRUST,
        ],
        "knowledge_conditions": [KnowledgeCondition.NONE],
        "workflow_hints": [],
    },
    "experiment_2": {
        "task_id": "core_image_ml_001",
        "suite_id": "core",
        "task_family": TaskFamily.OPTIMIZATION_AND_PARAMETER_SEARCH,
        "task_subfamily": "image_ml",
        "benchmark_pillars": [
            BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY,
            BenchmarkPillar.PROMPT_ROBUSTNESS_AND_TRUST,
        ],
        "knowledge_conditions": [KnowledgeCondition.NONE],
        "workflow_hints": [],
    },
    "experiment_3": {
        "task_id": "core_multimodal_survival_001",
        "suite_id": "core",
        "task_family": TaskFamily.OPTIMIZATION_AND_PARAMETER_SEARCH,
        "task_subfamily": "multimodal_ml",
        "benchmark_pillars": [
            BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY,
            BenchmarkPillar.PROMPT_ROBUSTNESS_AND_TRUST,
        ],
        "knowledge_conditions": [KnowledgeCondition.NONE],
        "workflow_hints": [],
    },
    "experiment_4": {
        "task_id": "iwc_atac_seq_001",
        "suite_id": "iwc",
        "task_family": TaskFamily.WORKFLOW_RETRIEVAL_AND_EXECUTION,
        "task_subfamily": "iwc_grounded_atac_seq",
        "benchmark_pillars": [
            BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY,
            BenchmarkPillar.ECOSYSTEM_KNOWLEDGE_USE,
        ],
        "knowledge_conditions": [KnowledgeCondition.IWC_ONLY],
        "workflow_hints": ["ATAC-seq Analysis: Chromatin Accessibility Profiling"],
    },
    "experiment_5": {
        "task_id": "gtn_rna_seq_001",
        "suite_id": "gtn",
        "task_family": TaskFamily.TUTORIAL_GROUNDED_EXECUTION,
        "task_subfamily": "paired_end_rna_seq",
        "benchmark_pillars": [
            BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY,
            BenchmarkPillar.ECOSYSTEM_KNOWLEDGE_USE,
        ],
        "knowledge_conditions": [KnowledgeCondition.GTN_ONLY],
        "workflow_hints": ["Complete RNA-Seq analysis for paired-end data"],
    },
    "experiment_6": {
        "task_id": "gtn_single_cell_rna_seq_001",
        "suite_id": "gtn",
        "task_family": TaskFamily.TUTORIAL_GROUNDED_EXECUTION,
        "task_subfamily": "single_cell_rna_seq",
        "benchmark_pillars": [
            BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY,
            BenchmarkPillar.ECOSYSTEM_KNOWLEDGE_USE,
        ],
        "knowledge_conditions": [KnowledgeCondition.GTN_ONLY],
        "workflow_hints": ["single-cell RNA-seq analysis"],
    },
    "experiment_7": {
        "task_id": "core_metagenomics_resistome_001",
        "suite_id": "core",
        "task_family": TaskFamily.WORKFLOW_RETRIEVAL_AND_EXECUTION,
        "task_subfamily": "metagenomics_resistome",
        "benchmark_pillars": [
            BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY,
            BenchmarkPillar.PROMPT_ROBUSTNESS_AND_TRUST,
        ],
        "knowledge_conditions": [KnowledgeCondition.NONE],
        "workflow_hints": ["metagenomics pipeline"],
    },
    "experiment_8": {
        "task_id": "core_genome_annotation_001",
        "suite_id": "core",
        "task_family": TaskFamily.WORKFLOW_RETRIEVAL_AND_EXECUTION,
        "task_subfamily": "genome_annotation_and_qc",
        "benchmark_pillars": [
            BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY,
            BenchmarkPillar.PROMPT_ROBUSTNESS_AND_TRUST,
        ],
        "knowledge_conditions": [KnowledgeCondition.NONE],
        "workflow_hints": ["genome annotation", "annotation quality evaluation"],
    },
    "experiment_9": {
        "task_id": "legacy_paper_reproduction_001",
        "suite_id": "legacy",
        "task_family": TaskFamily.PROVENANCE_AND_REPRODUCIBILITY,
        "task_subfamily": "published_work_reproduction",
        "benchmark_pillars": [
            BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY,
            BenchmarkPillar.PROMPT_ROBUSTNESS_AND_TRUST,
        ],
        "knowledge_conditions": [KnowledgeCondition.NONE],
        "workflow_hints": ["published work reproduction"],
    },
}

OUTPUT_ALIASES = {
    "roc-auc": "roc_auc",
    "ROC-AUC": "roc_auc",
    "last artifact": "last_artifact_format",
    "workflow steps": "workflow_step_count",
    "artifact": "artifact_name",
    "data_normalization": "normalization_tool",
    "data_normalization_tool": "normalization_tool",
    "list_of_genes": "marker_genes",
    "total__steps": "workflow_step_count",
    "total_tool_steps": "workflow_step_count",
    "total_tools": "workflow_step_count",
    "tool_name_1": "functional_annotation_tool",
    "tool_name_2": "assembly_tool",
    "input": "input_format",
    "analysis_result": "matching_gene_count",
    "QC_step_detail": "qc_filter_parameter",
}

EXPERIMENT_SPECIFIC_OUTPUTS = {
    "experiment_8": {
        "tool_name_1": "annotation_quality_tool",
        "tool_name_2": "visualization_tool",
    },
    "experiment_9": {
        "tool_name_1": "gene_count_tool",
    },
}

INFERRED_INPUTS = {
    "experiment_8": [
        ("S_pombe_chrIII_genome.fasta", "benchmark/datasets/local/core_genome_annotation_001/S_pombe_chrIII_genome.fasta", "fasta", "genome"),
        ("S_pombe_trinity_assembly.fasta", "benchmark/datasets/local/core_genome_annotation_001/S_pombe_trinity_assembly.fasta", "fasta", "assembly"),
        ("Swissprot_no_S_pombe.fasta", "benchmark/datasets/local/core_genome_annotation_001/Swissprot_no_S_pombe.fasta", "fasta", "protein_reference"),
        ("snap_training.snaphmm", "benchmark/datasets/local/core_genome_annotation_001/snap_training.snaphmm", "snaphmm", "snap_model"),
        ("augustus_training.tar.gz.augustus", "benchmark/datasets/local/core_genome_annotation_001/augustus_training.tar.gz.augustus", "augustus", "augustus_model"),
    ],
    "experiment_9": [
        ("anton_2025.pdf", "benchmark/datasets/local/legacy_paper_reproduction_001/anton_2025.pdf", "pdf", "paper"),
    ],
}

LOCAL_DATASET_DIRS = {
    "experiment_1": "core_tabular_001",
    "experiment_4": "iwc_atac_seq_001",
    "experiment_7": "core_metagenomics_resistome_001",
    "experiment_8": "core_genome_annotation_001",
    "experiment_9": "legacy_paper_reproduction_001",
}


def normalize_output_field_name(name: str, *, experiment_name: str | None = None) -> str:
    """Normalize legacy output field names into canonical snake_case keys."""

    if experiment_name and experiment_name in EXPERIMENT_SPECIFIC_OUTPUTS:
        if name in EXPERIMENT_SPECIFIC_OUTPUTS[experiment_name]:
            return EXPERIMENT_SPECIFIC_OUTPUTS[experiment_name][name]
    if name in OUTPUT_ALIASES:
        return OUTPUT_ALIASES[name]
    normalized = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    return normalized


def infer_value_type(value: Any) -> str:
    """Infer a portable JSON-ish value type label."""

    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def _extract_thresholds(must_have: list[str]) -> dict[str, float]:
    thresholds: dict[str, float] = {}
    for entry in must_have:
        match = re.search(r"ROC-AUC of at least ([0-9.]+)", entry, re.IGNORECASE)
        if match:
            thresholds["roc_auc"] = float(match.group(1))
    return thresholds


def _source_type_for_path(path_or_url: str) -> SourceType:
    return SourceType.URL if path_or_url.startswith("http") else SourceType.LOCAL


def _format_for_path(path_or_url: str) -> str:
    name = Path(path_or_url).name.lower()
    if name.endswith(".fastqsanger.gz"):
        return "fastqsanger.gz"
    if ".tar.gz" in name:
        return "tar.gz"
    parts = name.split(".")
    return parts[-1] if len(parts) > 1 else "unknown"


def _role_from_name(name: str) -> str:
    lowered = name.lower()
    if "train" in lowered:
        return "train_dataset"
    if "test" in lowered:
        return "test_dataset"
    if "forward" in lowered or "_r1" in lowered:
        return "forward_reads"
    if "reverse" in lowered or "_r2" in lowered:
        return "reverse_reads"
    if "barcode" in lowered:
        return "barcode_table"
    if "gene" in lowered:
        return "gene_table"
    if "matrix" in lowered:
        return "count_matrix"
    if "image" in lowered or lowered.endswith(".zip"):
        return "image_bundle"
    return "input"


def _normalize_dataset_path(experiment_name: str, path_or_url: str) -> str:
    normalized = path_or_url.lstrip("./")
    if normalized.startswith("dataset/"):
        parts = normalized.split("/", 2)
        if len(parts) >= 3 and experiment_name in LOCAL_DATASET_DIRS:
            normalized = f"benchmark/datasets/local/{LOCAL_DATASET_DIRS[experiment_name]}/{parts[2]}"
        else:
            normalized = normalized.replace("dataset/", "benchmark/datasets/local/", 1)
    if experiment_name == "experiment_7":
        normalized = normalized.replace("meta_genomic_R1.fastqsanger.gz", "meta_genomics_R1.fastqsanger.gz")
        normalized = normalized.replace("meta_genomic_R2.fastqsanger.gz", "meta_genomics_R2.fastqsanger.gz")
    return normalized


def _canonicalize_text_references(experiment_name: str, text: str) -> str:
    normalized = text.replace("dataset/", "benchmark/datasets/local/")
    task_dir = LOCAL_DATASET_DIRS.get(experiment_name)
    if task_dir:
        normalized = normalized.replace(f"benchmark/datasets/local/{experiment_name}", f"benchmark/datasets/local/{task_dir}")
    return normalized


class LegacyExperimentMigrator:
    """Convert legacy experiment definitions into canonical tasks and ground truths."""

    def migrate_experiment(self, experiment_name: str, payload: dict[str, Any]) -> BenchmarkTask:
        try:
            spec = LEGACY_TASK_SPECS[experiment_name]
        except KeyError as exc:
            raise LegacyMigrationError(f"Unsupported legacy experiment: {experiment_name}") from exc

        prompt = payload.get("prompt", {})
        output_template = payload.get("experiment_outputs", {})
        must_have = payload.get("must_have", [])
        ground_truth_gate = "Ground truth must only be read after result and reproduction artifacts exist."

        input_assets = self._build_input_assets(experiment_name, prompt)
        expected_outputs = [
            ExpectedOutputField(
                field=normalize_output_field_name(key, experiment_name=experiment_name),
                value_type="unknown",
                description=description,
                source_key=key,
            )
            for key, description in output_template.items()
        ]
        tool_hints = self._build_tool_hints(prompt)
        knowledge_notes = []
        if experiment_name == "experiment_4":
            knowledge_notes.append("IWC workflow retrieval is part of the task definition.")
        if experiment_name in {"experiment_5", "experiment_6"}:
            knowledge_notes.append("Galaxy training material is expected to guide workflow selection.")

        task_definition = TaskDefinition(
            goal=_canonicalize_text_references(experiment_name, prompt.get("task", payload.get("title", ""))),
            required_actions=self._required_actions_for_task(experiment_name),
            tool_hints=tool_hints,
            target_outputs=expected_outputs,
        )
        success_criteria = SuccessCriteria(
            required_fields=[field.field for field in expected_outputs],
            metric_thresholds=_extract_thresholds(must_have),
        )
        task = BenchmarkTask(
            task_id=spec["task_id"],
            suite_id=spec["suite_id"],
            title=payload.get("title", experiment_name).strip(),
            description=_canonicalize_text_references(experiment_name, prompt.get("task", payload.get("title", ""))),
            task_family=spec["task_family"],
            task_subfamily=spec["task_subfamily"],
            benchmark_pillars=spec["benchmark_pillars"],
            difficulty_level=int(payload.get("level", 1)),
            galaxy_instance=prompt.get("galaxy_instance", "https://usegalaxy.org/"),
            input_assets=input_assets,
            expected_outputs=expected_outputs,
            knowledge_requirements=KnowledgeRequirement(
                conditions=spec["knowledge_conditions"],
                sources=[
                    "gtn" if condition == KnowledgeCondition.GTN_ONLY else "iwc"
                    for condition in spec["knowledge_conditions"]
                    if condition != KnowledgeCondition.NONE
                ],
                notes=knowledge_notes,
            ),
            tool_hints=tool_hints,
            workflow_hints=spec["workflow_hints"],
            success_criteria=success_criteria,
            process_constraints=ProcessConstraints(
                notes=[ground_truth_gate],
            ),
            metadata={
                "benchmark_hypotheses": self._hypotheses_for_task(spec["benchmark_pillars"]),
            },
            task_definition=task_definition,
        )
        return task

    def migrate_ground_truth(
        self,
        experiment_name: str,
        task_id: str,
        payload: dict[str, Any],
    ) -> GroundTruth:
        expected_fields = {
            normalize_output_field_name(key, experiment_name=experiment_name): value
            for key, value in payload.items()
        }
        return GroundTruth(
            task_id=task_id,
            expected_fields=expected_fields,
            process_expectations=self._process_expectations_for_task(experiment_name),
            failure_expectations=self._failure_expectations_for_task(experiment_name),
            scoring_hints={"compare_fields": list(expected_fields.keys())},
        )

    def migrate_directory(
        self,
        experiments_dir: Path,
        ground_truth_dir: Path,
    ) -> list[tuple[BenchmarkTask, GroundTruth]]:
        migrated: list[tuple[BenchmarkTask, GroundTruth]] = []
        for experiment_path in sorted(experiments_dir.glob("experiment_*.json")):
            experiment_name = experiment_path.stem
            experiment_payload = json.loads(experiment_path.read_text())
            ground_truth_path = ground_truth_dir / f"{experiment_name}.json"
            ground_truth_payload = json.loads(ground_truth_path.read_text())
            task = self.migrate_experiment(experiment_name, experiment_payload)
            ground_truth = self.migrate_ground_truth(experiment_name, task.task_id, ground_truth_payload)
            task.expected_outputs = [
                field.model_copy(
                    update={
                        "value_type": infer_value_type(ground_truth.expected_fields.get(field.field, "")),
                    }
                )
                for field in task.expected_outputs
            ]
            migrated.append((task, ground_truth))
        return migrated

    def _build_input_assets(self, experiment_name: str, prompt: dict[str, Any]) -> list[InputAsset]:
        if experiment_name in INFERRED_INPUTS:
            return [
                InputAsset(
                    name=name,
                    source_type=_source_type_for_path(path_or_url),
                    path_or_url=path_or_url,
                    format=file_format,
                    role=role,
                )
                for name, path_or_url, file_format, role in INFERRED_INPUTS[experiment_name]
            ]

        dataset_entries = prompt.get("dataset", [])
        assets: list[InputAsset] = []
        for dataset in dataset_entries:
            raw_path = dataset["path"]
            path_or_url = _normalize_dataset_path(experiment_name, raw_path)
            assets.append(
                InputAsset(
                    name=dataset["name"],
                    source_type=_source_type_for_path(path_or_url),
                    path_or_url=path_or_url,
                    format=_format_for_path(path_or_url),
                    role=_role_from_name(dataset["name"]),
                )
            )
        return assets

    def _build_tool_hints(self, prompt: dict[str, Any]) -> list[str]:
        tool = prompt.get("tool")
        if isinstance(tool, dict):
            if "name" in tool:
                return [tool["name"]]
            return []
        if isinstance(tool, str):
            return [tool]
        return []

    def _required_actions_for_task(self, experiment_name: str) -> list[str]:
        common = ["create_history", "upload_inputs", "execute", "inspect_outputs"]
        if experiment_name in {"experiment_4", "experiment_5", "experiment_6"}:
            return ["retrieve_workflow_or_knowledge", *common]
        if experiment_name in {"experiment_2", "experiment_3"}:
            return [*common, "revise_parameters", "repeat_runs"]
        return common

    def _process_expectations_for_task(self, experiment_name: str) -> list[str]:
        expectations = [
            "do not read ground truth before result generation",
            "capture provenance and append-only activity logs",
        ]
        if experiment_name in {"experiment_4", "experiment_5", "experiment_6"}:
            expectations.append("consult the intended Galaxy knowledge source before execution")
        if experiment_name in {"experiment_2", "experiment_3"}:
            expectations.append("justify every parameter or architecture revision")
        return expectations

    def _failure_expectations_for_task(self, experiment_name: str) -> list[str]:
        family_specific = {
            "experiment_2": ["unsafe parameter sweeps without evidence-backed revision"],
            "experiment_3": ["unsafe parameter sweeps without evidence-backed revision"],
            "experiment_4": ["workflow retrieved from IWC but bound to inputs incorrectly"],
            "experiment_5": ["tutorial retrieved but not adapted to provided datasets"],
            "experiment_6": ["tutorial retrieved but not adapted to provided datasets"],
            "experiment_9": ["results reported without a reproducible provenance trail"],
        }
        return family_specific.get(experiment_name, [])

    @staticmethod
    def _hypotheses_for_task(pillars: list[BenchmarkPillar]) -> list[str]:
        hypotheses = ["H2"] if BenchmarkPillar.PROMPT_ROBUSTNESS_AND_TRUST in pillars else []
        if BenchmarkPillar.PLATFORM_OPERATION_CAPABILITY in pillars:
            hypotheses.insert(0, "H1")
        if BenchmarkPillar.ECOSYSTEM_KNOWLEDGE_USE in pillars:
            hypotheses.append("H3")
        return hypotheses
