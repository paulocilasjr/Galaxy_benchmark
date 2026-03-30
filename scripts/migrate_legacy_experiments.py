#!/usr/bin/env python3
"""Migrate legacy Galaxy benchmark experiments into clean canonical fixtures."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LEGACY_SUITE_ID = "legacy"

PILLAR_OPERATION = "platform_operation_capability"
PILLAR_PROMPT = "prompt_robustness_and_trust"
PILLAR_KNOWLEDGE = "ecosystem_knowledge_use"

TASK_BLUEPRINTS: dict[str, dict[str, Any]] = {
    "experiment_1": {
        "task_id": "core_tabular_001",
        "suite_id": "core",
        "task_family": "single_tool_execution",
        "task_subfamily": "tabular_ml",
        "benchmark_pillars": [PILLAR_OPERATION, PILLAR_PROMPT],
        "knowledge_requirements": [],
        "workflow_hints": [],
    },
    "experiment_2": {
        "task_id": "core_image_ml_001",
        "suite_id": "core",
        "task_family": "optimization_and_parameter_search",
        "task_subfamily": "image_ml",
        "benchmark_pillars": [PILLAR_OPERATION, PILLAR_PROMPT],
        "knowledge_requirements": [],
        "workflow_hints": [],
    },
    "experiment_3": {
        "task_id": "core_multimodal_survival_001",
        "suite_id": "core",
        "task_family": "optimization_and_parameter_search",
        "task_subfamily": "multimodal_ml",
        "benchmark_pillars": [PILLAR_OPERATION, PILLAR_PROMPT],
        "knowledge_requirements": [],
        "workflow_hints": [],
    },
    "experiment_4": {
        "task_id": "iwc_atac_seq_001",
        "suite_id": "iwc",
        "task_family": "workflow_retrieval_and_execution",
        "task_subfamily": "iwc_grounded_atac_seq",
        "benchmark_pillars": [PILLAR_OPERATION, PILLAR_KNOWLEDGE],
        "knowledge_requirements": ["iwc"],
        "workflow_hints": ["ATAC-seq Analysis: Chromatin Accessibility Profiling"],
    },
    "experiment_5": {
        "task_id": "gtn_rna_seq_001",
        "suite_id": "gtn",
        "task_family": "tutorial_grounded_execution",
        "task_subfamily": "paired_end_rna_seq",
        "benchmark_pillars": [PILLAR_OPERATION, PILLAR_KNOWLEDGE],
        "knowledge_requirements": ["gtn"],
        "workflow_hints": ["Complete RNA-Seq analysis for paired-end data"],
    },
    "experiment_6": {
        "task_id": "gtn_single_cell_rna_seq_001",
        "suite_id": "gtn",
        "task_family": "tutorial_grounded_execution",
        "task_subfamily": "single_cell_rna_seq",
        "benchmark_pillars": [PILLAR_OPERATION, PILLAR_KNOWLEDGE],
        "knowledge_requirements": ["gtn"],
        "workflow_hints": ["single-cell RNA-seq analysis"],
    },
    "experiment_7": {
        "task_id": "core_metagenomics_resistome_001",
        "suite_id": "core",
        "task_family": "workflow_retrieval_and_execution",
        "task_subfamily": "metagenomics_resistome",
        "benchmark_pillars": [PILLAR_OPERATION, PILLAR_PROMPT],
        "knowledge_requirements": [],
        "workflow_hints": ["metagenomics pipeline"],
    },
    "experiment_8": {
        "task_id": "core_genome_annotation_001",
        "suite_id": "core",
        "task_family": "workflow_retrieval_and_execution",
        "task_subfamily": "genome_annotation_and_qc",
        "benchmark_pillars": [PILLAR_OPERATION, PILLAR_PROMPT],
        "knowledge_requirements": [],
        "workflow_hints": ["genome annotation", "annotation quality evaluation"],
    },
    "experiment_9": {
        "task_id": "legacy_paper_reproduction_001",
        "suite_id": "legacy",
        "task_family": "provenance_and_reproducibility",
        "task_subfamily": "published_work_reproduction",
        "benchmark_pillars": [PILLAR_OPERATION, PILLAR_PROMPT],
        "knowledge_requirements": [],
        "workflow_hints": ["published work reproduction"],
    },
}

INFERRED_INPUTS: dict[str, list[tuple[str, str, str, str]]] = {
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

PROCESS_EXPECTATIONS: dict[str, list[str]] = {
    "default": [
        "do not read ground truth before result generation",
        "capture provenance and append-only activity logs",
    ],
    "knowledge": [
        "consult the intended Galaxy knowledge source before execution",
    ],
    "optimization": [
        "justify every parameter or architecture revision",
    ],
}

FAILURE_EXPECTATIONS: dict[str, list[str]] = {
    "experiment_2": ["unsafe parameter sweeps without evidence-backed revision"],
    "experiment_3": ["unsafe parameter sweeps without evidence-backed revision"],
    "experiment_4": ["workflow retrieved from IWC but bound to inputs incorrectly"],
    "experiment_5": ["tutorial retrieved but not adapted to provided datasets"],
    "experiment_6": ["tutorial retrieved but not adapted to provided datasets"],
    "experiment_9": ["results reported without a reproducible provenance trail"],
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


@dataclass(frozen=True)
class LegacyPair:
    experiment_path: Path
    ground_truth_path: Path


def snake_case(value: str) -> str:
    """Normalize a legacy name into deterministic snake_case."""

    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    value = re.sub(r"[^A-Za-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value.lower()


def infer_source_type(path_or_url: str) -> str:
    lowered = path_or_url.lower()
    if lowered.startswith("http://") or lowered.startswith("https://"):
        return "url"
    return "local"


def infer_format(path_or_url: str) -> str | None:
    lowered = path_or_url.lower()
    if lowered.endswith(".fastqsanger.gz"):
        return "fastqsanger_gz"
    if lowered.endswith(".fastq.gz"):
        return "fastq_gz"
    if lowered.endswith(".tar.gz"):
        return "tar_gz"
    if lowered.endswith(".tgz"):
        return "tgz"
    suffixes = Path(lowered).suffixes
    if not suffixes:
        return None
    if len(suffixes) >= 2 and suffixes[-2:] == [".json", ""]:
        return "json"
    if len(suffixes) >= 2 and suffixes[-2] == ".fastqsanger" and suffixes[-1] == ".gz":
        return "fastqsanger_gz"
    if len(suffixes) >= 2:
        return "".join(suffixes[-2:]).lstrip(".").replace(".", "_")
    return suffixes[-1].lstrip(".")


def infer_role(dataset_name: str, index: int, total: int) -> str:
    name = dataset_name.lower()
    if "train" in name:
        return "training_dataset"
    if "test" in name:
        return "test_dataset"
    if "forward" in name or name.endswith("_r1.fastqsanger.gz") or "_r1" in name:
        return "read_1"
    if "reverse" in name or name.endswith("_r2.fastqsanger.gz") or "_r2" in name:
        return "read_2"
    if "barcode" in name:
        return "barcodes"
    if "gene" in name and "matrix" not in name:
        return "gene_annotation"
    if "matrix" in name:
        return "count_matrix"
    if "metadata" in name:
        return "metadata_table"
    if "image" in name or name.endswith(".zip"):
        return "image_archive"
    if total == 1:
        return "primary_dataset"
    return f"input_dataset_{index + 1}"


def normalize_dataset_path(experiment_id: str, path_or_url: str) -> str:
    normalized = path_or_url.lstrip("./")
    if normalized.startswith("dataset/"):
        parts = normalized.split("/", 2)
        if len(parts) >= 3 and experiment_id in LOCAL_DATASET_DIRS:
            normalized = f"benchmark/datasets/local/{LOCAL_DATASET_DIRS[experiment_id]}/{parts[2]}"
        else:
            normalized = normalized.replace("dataset/", "benchmark/datasets/local/", 1)
    if experiment_id == "experiment_7":
        normalized = normalized.replace("meta_genomic_R1.fastqsanger.gz", "meta_genomics_R1.fastqsanger.gz")
        normalized = normalized.replace("meta_genomic_R2.fastqsanger.gz", "meta_genomics_R2.fastqsanger.gz")
    return normalized


def canonicalize_text_references(experiment_id: str, text: str) -> str:
    normalized = text.replace("dataset/", "benchmark/datasets/local/")
    task_dir = LOCAL_DATASET_DIRS.get(experiment_id)
    if task_dir:
        normalized = normalized.replace(f"benchmark/datasets/local/{experiment_id}", f"benchmark/datasets/local/{task_dir}")
    return normalized


def normalize_output_name(key: str, experiment_id: str | None = None) -> str:
    if experiment_id and experiment_id in EXPERIMENT_SPECIFIC_OUTPUTS:
        if key in EXPERIMENT_SPECIFIC_OUTPUTS[experiment_id]:
            return EXPERIMENT_SPECIFIC_OUTPUTS[experiment_id][key]
    if key in OUTPUT_ALIASES:
        return OUTPUT_ALIASES[key]
    return snake_case(key)


def normalize_mapping(mapping: dict[str, Any], experiment_id: str | None = None) -> tuple[dict[str, Any], dict[str, str]]:
    normalized: dict[str, Any] = {}
    aliases: dict[str, str] = {}
    for key, value in mapping.items():
        normalized_key = normalize_output_name(key, experiment_id)
        normalized[normalized_key] = value
        if normalized_key != key:
            aliases[normalized_key] = key
    return normalized, aliases


def metric_thresholds(must_have: list[str] | None) -> list[dict[str, Any]]:
    if not must_have:
        return []
    thresholds: list[dict[str, Any]] = []
    for entry in must_have:
        lower = entry.lower()
        match = re.search(r"at least\s+([0-9]*\.?[0-9]+)", lower)
        if not match:
            continue
        metric = "roc_auc" if "roc-auc" in lower or "roc auc" in lower else "threshold"
        thresholds.append(
            {
                "metric": metric,
                "operator": ">=",
                "value": float(match.group(1)),
                "source_text": entry,
            }
        )
    return thresholds


def build_input_assets(experiment_id: str, prompt: dict[str, Any]) -> list[dict[str, Any]]:
    if experiment_id in INFERRED_INPUTS:
        return [
            {
                "name": name,
                "source_type": infer_source_type(path_or_url),
                "path_or_url": path_or_url,
                "format": file_format,
                "role": role,
                "checksum": None,
                "optional": False,
            }
            for name, path_or_url, file_format, role in INFERRED_INPUTS[experiment_id]
        ]

    datasets = prompt.get("dataset") or []
    assets: list[dict[str, Any]] = []
    for index, dataset in enumerate(datasets):
        path_or_url = normalize_dataset_path(experiment_id, dataset["path"])
        name = dataset["name"]
        assets.append(
            {
                "name": name,
                "source_type": infer_source_type(path_or_url),
                "path_or_url": path_or_url,
                "format": infer_format(path_or_url),
                "role": infer_role(name, index, len(datasets)),
                "checksum": None,
                "optional": False,
            }
        )
    return assets


def build_expected_outputs(experiment_outputs: dict[str, Any], experiment_id: str) -> list[dict[str, Any]]:
    normalized, aliases = normalize_mapping(experiment_outputs, experiment_id)
    outputs: list[dict[str, Any]] = []
    for field, description in normalized.items():
        outputs.append(
            {
                "field": field,
                "legacy_field": aliases.get(field, field),
                "description": description,
                "source": "experiment_outputs",
            }
        )
    return outputs


def build_canonical_task(pair: LegacyPair, legacy: dict[str, Any]) -> dict[str, Any]:
    experiment_id = pair.experiment_path.stem
    prompt = legacy.get("prompt") or {}
    blueprint = TASK_BLUEPRINTS[experiment_id]

    tool = prompt.get("tool")
    tool_hints: list[str] = []
    workflow_hints = list(blueprint.get("workflow_hints", []))
    if isinstance(tool, dict):
        name = tool.get("name")
        if name:
            tool_hints.append(name)
    elif isinstance(tool, str) and tool.strip():
        workflow_hints.append(tool.strip())

    required_outputs = [item["field"] for item in build_expected_outputs(legacy.get("experiment_outputs") or {}, experiment_id)]
    threshold_list = metric_thresholds(legacy.get("must_have"))
    process_constraints = {
        "must_log_trace": True,
        "must_not_read_ground_truth_before_result": True,
        "legacy_must_have": legacy.get("must_have") or [],
    }

    metadata = {
        "benchmark_hypotheses": hypotheses_for_pillars(blueprint["benchmark_pillars"]),
    }

    return {
        "task_id": blueprint["task_id"],
        "suite_id": blueprint["suite_id"],
        "title": legacy.get("title"),
        "description": canonicalize_text_references(experiment_id, prompt.get("task")),
        "task_family": blueprint["task_family"],
        "task_subfamily": blueprint["task_subfamily"],
        "benchmark_pillars": blueprint["benchmark_pillars"],
        "difficulty_level": legacy.get("level"),
        "galaxy_instance": prompt.get("galaxy_instance") or "https://usegalaxy.org/",
        "input_assets": build_input_assets(experiment_id, prompt),
        "expected_outputs": build_expected_outputs(legacy.get("experiment_outputs") or {}, experiment_id),
        "knowledge_requirements": blueprint["knowledge_requirements"],
        "tool_hints": tool_hints,
        "workflow_hints": workflow_hints,
        "success_criteria": {
            "required_fields": required_outputs,
            "metric_thresholds": threshold_list,
            "artifact_requirements": [],
        },
        "process_constraints": process_constraints,
        "failure_scenarios": [],
        "metadata": metadata,
    }


def build_canonical_ground_truth(pair: LegacyPair, ground_truth: dict[str, Any]) -> dict[str, Any]:
    experiment_id = pair.experiment_path.stem
    normalized, aliases = normalize_mapping(ground_truth, experiment_id)
    blueprint = TASK_BLUEPRINTS[experiment_id]
    process_expectations = list(PROCESS_EXPECTATIONS["default"])
    if experiment_id in {"experiment_4", "experiment_5", "experiment_6"}:
        process_expectations.extend(PROCESS_EXPECTATIONS["knowledge"])
    if experiment_id in {"experiment_2", "experiment_3"}:
        process_expectations.extend(PROCESS_EXPECTATIONS["optimization"])
    return {
        "task_id": blueprint["task_id"],
        "expected_artifacts": [],
        "expected_fields": normalized,
        "acceptable_alternatives": {},
        "process_expectations": process_expectations,
        "failure_expectations": FAILURE_EXPECTATIONS.get(experiment_id, []),
        "scoring_hints": {
            "compare_fields": sorted(normalized.keys()),
        },
        "metadata": {
            "field_aliases": aliases,
        },
    }


def hypotheses_for_pillars(pillars: list[str]) -> list[str]:
    hypotheses = ["H2"] if PILLAR_PROMPT in pillars else []
    if PILLAR_OPERATION in pillars:
        hypotheses.insert(0, "H1")
    if PILLAR_KNOWLEDGE in pillars:
        hypotheses.append("H3")
    return hypotheses


def collect_legacy_pairs(source_root: Path) -> list[LegacyPair]:
    experiment_dir = source_root / "experiments"
    ground_truth_dir = source_root / "ground_truth"
    pairs: list[LegacyPair] = []
    for experiment_path in sorted(experiment_dir.glob("experiment_*.json")):
        ground_truth_path = ground_truth_dir / experiment_path.name
        if not ground_truth_path.exists():
            raise FileNotFoundError(f"Missing ground truth for {experiment_path.name}: {ground_truth_path}")
        pairs.append(LegacyPair(experiment_path=experiment_path, ground_truth_path=ground_truth_path))
    return pairs


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: Any) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def migrate_legacy_experiments(source_root: Path, output_root: Path) -> dict[str, Any]:
    pairs = collect_legacy_pairs(source_root)

    benchmark_root = output_root / "benchmark"
    manifest_items: list[dict[str, Any]] = []

    for pair in pairs:
        legacy_experiment = json.loads(pair.experiment_path.read_text(encoding="utf-8"))
        legacy_ground_truth = json.loads(pair.ground_truth_path.read_text(encoding="utf-8"))
        canonical_task = build_canonical_task(pair, legacy_experiment)
        canonical_gt = build_canonical_ground_truth(pair, legacy_ground_truth)
        canonical_task_path = benchmark_root / "tasks" / f"{canonical_task['task_id']}.json"
        canonical_gt_path = benchmark_root / "ground_truth" / f"{canonical_task['task_id']}.json"

        write_json(canonical_task_path, canonical_task)
        write_json(canonical_gt_path, canonical_gt)

        manifest_items.append(
            {
                "task_id": canonical_task["task_id"],
                "suite_id": canonical_task["suite_id"],
                "canonical_task_path": str(canonical_task_path.relative_to(output_root)),
                "canonical_ground_truth_path": str(canonical_gt_path.relative_to(output_root)),
                "task_family": canonical_task["task_family"],
                "task_subfamily": canonical_task["task_subfamily"],
                "benchmark_pillars": canonical_task["benchmark_pillars"],
            }
        )

    manifest = {
        "suite_id": LEGACY_SUITE_ID,
        "source_root": str(source_root),
        "output_root": str(output_root),
        "task_count": len(manifest_items),
        "tasks": manifest_items,
    }
    write_json(benchmark_root / "migration_manifest.json", manifest)
    return manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Legacy repository root that contains experiments/ and ground_truth/.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Root directory where benchmark/ will be written.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    migrate_legacy_experiments(args.source_root, args.output_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
