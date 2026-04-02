#!/usr/bin/env python3
"""Operational scorer for Galaxy Benchmark runs.

This scorer reads:
- a benchmark run directory under outputs/
- the hidden evaluator and ground-truth files for the experiment
- the run's result and supporting artifacts

It then produces:
- a field-level comparison report
- the explicit three-score vector:
  - scientific_solution_score
  - standard_analysis_score
  - galaxy_execution_score

The scorer is intentionally non-destructive. By default it writes:
- results/comparison.scored.md
- results/score_summary.json
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable


LEVELS = ("low_context", "medium_context", "high_context")
ROOT_DIR = Path(__file__).resolve().parent.parent

INPUT_STEP_TYPES = {
    "data_input",
    "data_collection_input",
    "parameter_input",
    "pause",
}

CLASS_ALIAS_MAP = {
    "annotation quality assessment tool": {"busco"},
    "biomedical image classification tool": {"image learner"},
    "completeness assessment tool": {"busco"},
    "functional annotation tool": {"eggnog", "eggnog mapper", "eggnog-mapper"},
    "genome annotation workflow": {"maker", "annotation"},
    "genome browser": {"jbrowse", "jbrowse 2"},
    "annotation visualization tool": {"jbrowse", "jbrowse 2"},
    "metagenomic assembler": {"megahit"},
    "short-read assembler": {"megahit"},
    "multimodal classification tool": {"multimodal learner"},
    "orthology-based annotation tool": {"eggnog", "eggnog mapper", "eggnog-mapper"},
    "rna-seq qc report": {"multiqc"},
    "rna-seq quantification artifact": {
        "featurecounts",
        "htseq",
        "counts",
        "quantification",
        "count table",
    },
    "normalized coverage artifact": {"bigwig", "bedgraph"},
    "rna-seq workflow": {"rna-seq", "rna seq", "star", "fastp"},
    "single-cell rna-seq workflow": {"scanpy", "single-cell", "single cell"},
    "tabular binary classification tool": {"tabular learner"},
    "atac-seq workflow": {"atac", "atacseq", "chromatin accessibility"},
    "metagenomics gene-catalog workflow": {
        "metagenomic genes catalogue analysis",
        "metagenomics",
        "gene catalog",
    },
}

STAGE_HINTS = {
    "fastp": {"fastp"},
    "STAR": {"star"},
    "quantification": {"featurecounts", "htseq", "cufflinks", "stringtie", "salmon", "quantification"},
    "reporting": {"multiqc", "report"},
    "scanpy normalization": {"scanpy_normalize", "scanpy normalize", "normalize_total", "pp.normalize_total"},
    "Louvain clustering": {"louvain"},
    "UMAP": {"umap"},
    "dotplot marker visualization": {"dotplot", "marker"},
}


@dataclass
class ArtifactBundle:
    run_dir: Path
    experiment_id: str
    level: str | None
    experiment: dict[str, Any] | None
    evaluator: dict[str, Any]
    ground_truth: dict[str, Any]
    raw_result: dict[str, Any]
    activity_log: list[dict[str, Any]]
    errors: dict[str, Any] | None
    workflow_export: dict[str, Any] | None
    workflow_metadata: dict[str, Any] | None
    history_contents: Any
    tool_outputs: dict[str, Any] | None
    tool_discovery: dict[str, Any] | None
    result_path: Path
    normalization_notes: list[str] = field(default_factory=list)


@dataclass
class ComparisonEntry:
    score_name: str
    field_path: str
    agent_value: Any
    reference_rule: str
    match_status: str
    score_value: float | None
    notes: str


@dataclass
class ScoreValue:
    value: float | None
    status: str
    applicability: str
    basis: str
    matched_fields: int
    applicable_fields: int
    notes: list[str]


def normalize_token(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip().lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def text_matches_expected(agent_value: Any, expected_value: Any) -> bool:
    agent_norm = normalize_token(agent_value)
    expected_norm = normalize_token(expected_value)
    if not agent_norm or not expected_norm:
        return False
    return (
        agent_norm == expected_norm
        or expected_norm in agent_norm
        or agent_norm in expected_norm
    )


def stringify(value: Any) -> str:
    if value is None:
        return "missing"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=True, sort_keys=True)
    return str(value)


def parse_number(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    match = re.search(r"-?\d+(?:\.\d+)?", str(value))
    if not match:
        return None
    return float(match.group(0))


def collect_nested_strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, dict):
        strings: list[str] = []
        for child in value.values():
            strings.extend(collect_nested_strings(child))
        return strings
    if isinstance(value, list):
        strings: list[str] = []
        for child in value:
            strings.extend(collect_nested_strings(child))
        return strings
    return [stringify(value)]


def parse_int(value: Any) -> int | None:
    number = parse_number(value)
    if number is None:
        return None
    return int(round(number))


def parse_contextual_count(value: Any, field_path: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return int(round(float(value)))
    text = str(value)
    patterns_by_field = {
        "galaxy_execution.workflow_tool_step_count": [
            r"contains\s+(\d+)\s+tool\s+steps",
            r"has\s+(\d+)\s+tool\s+steps",
            r"expected\s+tool[- ]step\s+count.*?\bis\s+(\d+)",
            r"(\d+)\s+tool\s+steps",
        ],
        "galaxy_execution.total_tool_executions": [
            r"(\d+)\s+completed\s+tool\s+executions",
            r"(\d+)\s+tool\s+executions",
            r"(\d+)\s+unique\s+tool\s+names",
        ],
    }
    for pattern in patterns_by_field.get(field_path, []):
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return int(match.group(1))
    return parse_int(value)


def first_nonempty(*values: Any) -> Any:
    for value in values:
        if value is None:
            continue
        if isinstance(value, str) and not value.strip():
            continue
        return value
    return None


def load_json(path: Path) -> dict[str, Any] | list[Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> Any:
    if not path.exists():
        return None
    return load_json(path)


def load_activity_log(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def infer_experiment_id(run_dir: Path, explicit: str | None) -> str:
    if explicit:
        return explicit
    match = re.search(r"experiment_\d+", str(run_dir))
    if not match:
        raise ValueError(
            "Could not infer experiment id from run directory. Pass --experiment-id."
        )
    return match.group(0)


def infer_level(run_dir: Path, explicit: str | None) -> str | None:
    if explicit:
        return explicit
    match = re.search(r"(low_context|medium_context|high_context)", str(run_dir))
    if match:
        return match.group(1)
    return None


def load_experiment_contract(experiment_id: str, level: str | None) -> dict[str, Any] | None:
    if level:
        candidate = ROOT_DIR / "experiments" / level / f"{experiment_id}.json"
        if candidate.exists():
            return load_json(candidate)  # type: ignore[return-value]
    fallback = ROOT_DIR / "experiments" / "low_context" / f"{experiment_id}.json"
    if fallback.exists():
        return load_json(fallback)  # type: ignore[return-value]
    return None


def build_bundle(run_dir: Path, experiment_id: str, level: str | None) -> ArtifactBundle:
    result_path = run_dir / "results" / "result.json"
    if not result_path.exists():
        raise FileNotFoundError(f"Missing result artifact: {result_path}")

    evaluator_path = ROOT_DIR / "evaluators" / f"{experiment_id}.json"
    ground_truth_path = ROOT_DIR / "ground_truth" / f"{experiment_id}.json"
    if not evaluator_path.exists():
        raise FileNotFoundError(f"Missing evaluator file: {evaluator_path}")
    if not ground_truth_path.exists():
        raise FileNotFoundError(f"Missing ground truth file: {ground_truth_path}")

    return ArtifactBundle(
        run_dir=run_dir,
        experiment_id=experiment_id,
        level=level,
        experiment=load_experiment_contract(experiment_id, level),
        evaluator=load_json(evaluator_path),  # type: ignore[arg-type]
        ground_truth=load_json(ground_truth_path),  # type: ignore[arg-type]
        raw_result=load_json(result_path),  # type: ignore[arg-type]
        activity_log=load_activity_log(run_dir / "results" / "activity_log.jsonl"),
        errors=load_optional_json(run_dir / "errors" / "error.json"),
        workflow_export=load_optional_json(run_dir / "results" / "workflow_export.json"),
        workflow_metadata=load_optional_json(run_dir / "results" / "workflow_metadata.json"),
        history_contents=load_optional_json(run_dir / "results" / "history_contents.json"),
        tool_outputs=load_optional_json(run_dir / "results" / "tool_outputs.json"),
        tool_discovery=load_optional_json(run_dir / "results" / "tool_discovery.json"),
        result_path=result_path,
    )


def history_input_mode_from_experiment(experiment: dict[str, Any] | None) -> str | None:
    if not experiment:
        return None
    datasets = experiment.get("inputs", {}).get("datasets", [])
    if not datasets:
        return None
    modes = set()
    for dataset in datasets:
        path = str(dataset.get("path", ""))
        if path.startswith("http://") or path.startswith("https://"):
            modes.add("remote_fetch")
        else:
            modes.add("local_upload")
    if len(modes) == 1:
        return next(iter(modes))
    if modes:
        return "mixed"
    return None


def count_workflow_export_tool_steps(workflow_export: dict[str, Any] | None) -> int | None:
    if not workflow_export:
        return None
    steps = workflow_export.get("steps")
    if not isinstance(steps, dict):
        return None
    count = 0
    for step in steps.values():
        if not isinstance(step, dict):
            continue
        step_type = step.get("type")
        if step_type in INPUT_STEP_TYPES:
            continue
        count += 1
    return count or None


def count_history_jobs(history_contents: Any) -> int | None:
    if not isinstance(history_contents, list):
        return None
    job_ids = set()
    for item in history_contents:
        if not isinstance(item, dict):
            continue
        job_id = item.get("creating_job")
        if job_id:
            job_ids.add(job_id)
    return len(job_ids) or None


def count_tool_output_steps(
    tool_outputs: dict[str, Any] | None,
    *,
    completed_only: bool = False,
) -> int | None:
    if not isinstance(tool_outputs, dict):
        return None
    total = 0
    resumed = tool_outputs.get("resumed_upstream")
    if isinstance(resumed, dict):
        total += len(resumed)
    steps = tool_outputs.get("steps")
    if isinstance(steps, dict):
        for step in steps.values():
            if not isinstance(step, dict):
                continue
            if completed_only:
                state = normalize_token(
                    first_nonempty(
                        step.get("state"),
                        get_nested(step, ("summary_dataset", "state")),
                    )
                )
                if state and state not in {"ok", "completed"}:
                    continue
            total += 1
    return total or None


def collect_workflow_text(bundle: ArtifactBundle) -> list[str]:
    texts: list[str] = []
    if isinstance(bundle.workflow_export, dict):
        texts.extend(
            stringify(bundle.workflow_export.get(key))
            for key in ("name", "annotation")
        )
        steps = bundle.workflow_export.get("steps")
        if isinstance(steps, dict):
            for step in steps.values():
                if not isinstance(step, dict):
                    continue
                for key in ("name", "annotation", "label", "tool_id", "tool_version"):
                    value = step.get(key)
                    if value:
                        texts.append(stringify(value))
    if isinstance(bundle.workflow_metadata, dict):
        for key in ("workflow_name", "workflow_annotation"):
            value = bundle.workflow_metadata.get(key)
            if value:
                texts.append(stringify(value))
        for key in ("assembly_step", "functional_mapper_step"):
            value = bundle.workflow_metadata.get(key)
            if isinstance(value, dict):
                texts.extend(
                    stringify(value.get(child))
                    for child in ("name", "tool_id")
                    if value.get(child)
                )
    if isinstance(bundle.tool_outputs, dict):
        texts.extend(
            stringify(bundle.tool_outputs.get(key))
            for key in ("history_name", "selected_busco_lineage")
            if bundle.tool_outputs.get(key)
        )
        steps = bundle.tool_outputs.get("steps")
        if isinstance(steps, dict):
            for name, step in steps.items():
                texts.append(str(name))
                texts.append(stringify(step))
    if isinstance(bundle.tool_discovery, dict):
        texts.extend(
            stringify(bundle.tool_discovery.get(key))
            for key in ("tutorial_url", "tutorial_content_url")
            if bundle.tool_discovery.get(key)
        )
        tutorial_matches = bundle.tool_discovery.get("tutorial_matches")
        if isinstance(tutorial_matches, list):
            for match in tutorial_matches:
                texts.extend(collect_nested_strings(match))
    texts.append(stringify(bundle.raw_result))
    return [text for text in texts if text and text != "missing"]


def workflow_text_haystack(bundle: ArtifactBundle) -> str:
    return normalize_token(" ".join(collect_workflow_text(bundle)))


def stage_present(stage: str, bundle: ArtifactBundle) -> tuple[bool | None, str]:
    haystack = workflow_text_haystack(bundle)
    hints = STAGE_HINTS.get(stage, {normalize_token(stage)})
    if not haystack:
        return None, "No workflow-stage evidence was available."
    for hint in hints:
        if normalize_token(hint) and normalize_token(hint) in haystack:
            return True, f"Found stage hint `{hint}` in workflow evidence."
    return False, f"Did not find any of the expected stage hints: {sorted(hints)}."


def capability_observation(capability: str, bundle: ArtifactBundle) -> tuple[bool | None, str]:
    capability_norm = normalize_token(capability)
    activity_categories = {
        normalize_token(entry.get("category")) for entry in bundle.activity_log if isinstance(entry, dict)
    }
    history_mode = history_input_mode_from_experiment(bundle.experiment)
    raw_text = normalize_token(stringify(bundle.raw_result))
    history_present = (
        bool(bundle.history_contents)
        or "history" in raw_text
        or bool(get_nested(bundle.raw_result, ("evidence", "history")))
    )
    workflow_present = bool(bundle.workflow_export or bundle.workflow_metadata)
    parameter_present = "selected params" in raw_text
    parameter_present = parameter_present or bool(get_nested(bundle.raw_result, ("evidence", "workflow", "selected_params")))
    parameter_present = parameter_present or bool(get_nested(bundle.tool_outputs or {}, ("selected_busco_lineage",)))
    parameter_present = parameter_present or (bundle.workflow_export is not None)
    has_retry = "retry" in activity_categories or "revise" in activity_categories
    has_check = "check" in activity_categories
    workflow_candidates = derive_artifact_candidates("galaxy_execution.final_entity_name", bundle)
    workflow_haystack = workflow_text_haystack(bundle)

    if capability_norm == "local data upload":
        return history_mode == "local_upload", f"Derived input mode: {history_mode or 'unknown'}."
    if capability_norm == "remote data upload":
        return history_mode == "remote_fetch", f"Derived input mode: {history_mode or 'unknown'}."
    if capability_norm in {"history dataset inspection", "history navigation"}:
        return history_present, "History artifacts were present." if history_present else "No history artifacts were present."
    if capability_norm in {"tool invocation", "workflow invocation"}:
        return workflow_present or bool(bundle.activity_log), "Invocation evidence was present." if (workflow_present or bundle.activity_log) else "No invocation evidence was available."
    if capability_norm in {"workflow execution", "long workflow execution"}:
        step_count = first_nonempty(
            parse_number(get_nested(bundle.raw_result, ("galaxy_execution", "workflow_tool_step_count"))),
            parse_number(get_nested(bundle.raw_result, ("workflow steps",))),
            parse_number(get_nested(bundle.workflow_metadata or {}, ("counts", "execution_steps_excluding_inputs"))),
            parse_number(count_workflow_export_tool_steps(bundle.workflow_export)),
        )
        if capability_norm == "workflow execution":
            observed = workflow_present or bool(workflow_candidates)
            return observed, "Workflow-execution evidence was present." if observed else "No workflow-execution evidence was available."
        if step_count is None:
            observed = workflow_present or bool(workflow_candidates)
            return observed, "Workflow evidence was present but step-count evidence was incomplete." if observed else "No long-workflow evidence was available."
        observed = step_count >= 10
        return observed, f"Observed workflow step count candidate: {step_count}."
    if capability_norm == "workflow discovery":
        observed = bool(bundle.tool_discovery) or bool(workflow_candidates) or "iwc" in workflow_haystack or "training" in workflow_haystack
        return observed, "Workflow-discovery evidence was present." if observed else "No workflow-discovery evidence was available."
    if capability_norm in {"run state monitoring", "run-state monitoring"}:
        return has_check, "Observed `check` activity entries." if has_check else "No monitoring-oriented `check` activity entries were observed."
    if capability_norm in {"workflow provenance extraction", "pipeline provenance extraction"}:
        observed = workflow_present or bool(bundle.tool_outputs)
        return observed, "Workflow provenance artifacts were present." if observed else "No workflow provenance artifacts were present."
    if capability_norm == "paired collection handling":
        if "list paired" in raw_text or "collection_type" in raw_text:
            return True, "Detected paired-collection evidence in run artifacts."
        return False, "Did not detect paired-collection evidence in run artifacts."
    if capability_norm == "matrix market input setup":
        if not bundle.experiment:
            return None, "Experiment contract was unavailable."
        input_names = " ".join(dataset.get("name", "") for dataset in bundle.experiment.get("inputs", {}).get("datasets", []))
        observed = all(token in input_names for token in ("matrix.mtx", "barcodes.tsv", "genes.tsv"))
        return observed, "Experiment inputs include Matrix Market components." if observed else "Matrix Market components were not all present in the experiment inputs."
    if capability_norm == "multi input setup":
        if not bundle.experiment:
            return None, "Experiment contract was unavailable."
        datasets = bundle.experiment.get("inputs", {}).get("datasets", [])
        return len(datasets) >= 3, f"Experiment exposes {len(datasets)} input datasets."
    if capability_norm == "multimodal input setup":
        if not bundle.experiment:
            return None, "Experiment contract was unavailable."
        datasets = bundle.experiment.get("inputs", {}).get("datasets", [])
        if len(datasets) < 2:
            return False, "Experiment did not expose enough inputs for multimodal setup."
        return True, f"Experiment exposes {len(datasets)} inputs for multimodal setup."
    if capability_norm == "parameter entry":
        return parameter_present, "Parameter evidence was present." if parameter_present else "No parameter-entry evidence was present."
    if capability_norm == "tool parameterization":
        return parameter_present, "Parameter evidence was present." if parameter_present else "No parameterization evidence was present."
    if capability_norm == "train test dataset handling":
        agent_split = get_nested(bundle.raw_result, ("scientific_answer", "primary_metric", "split"))
        if agent_split is None:
            return True, "Legacy run did not report the split explicitly; task inputs still expose separate train/test datasets."
        return normalize_token(agent_split) == "test", f"Reported split: {agent_split!r}."
    if capability_norm == "error recovery":
        if not has_retry and not bundle.errors:
            return None, "No retry or error evidence was present, so recovery was not exercised."
        return has_retry, "Observed retry/revise evidence." if has_retry else "No retry/revise evidence was observed."
    return None, f"No operational heuristic is implemented for capability `{capability}`."


def derive_artifact_candidates(field_path: str, bundle: ArtifactBundle) -> list[Any]:
    candidates: list[Any] = []
    raw = bundle.raw_result
    evidence = raw.get("evidence", {}) if isinstance(raw, dict) else {}
    workflow = evidence.get("workflow", {}) if isinstance(evidence, dict) else {}
    inputs = evidence.get("inputs", {}) if isinstance(evidence, dict) else {}
    last_artifact = evidence.get("last_artifact", {}) if isinstance(evidence, dict) else {}

    if field_path == "galaxy_execution.final_entity_name":
        candidates.extend(
            value
            for value in (
                workflow.get("name"),
                get_nested(bundle.workflow_metadata or {}, ("workflow_name",)),
                get_nested(bundle.workflow_export or {}, ("name",)),
                raw.get("tool_name"),
                get_nested(raw, ("galaxy_execution", "final_entity_name")),
            )
            if value
        )
        if isinstance(bundle.tool_outputs, dict):
            resumed = bundle.tool_outputs.get("resumed_upstream")
            if isinstance(resumed, dict):
                for name, item in resumed.items():
                    if "maker" in normalize_token(name):
                        candidates.append("Maker")
                    if isinstance(item, dict) and item.get("name"):
                        if "maker" in normalize_token(item.get("name")):
                            candidates.append("Maker")
                        candidates.append(item.get("name"))
            steps = bundle.tool_outputs.get("steps")
            if isinstance(steps, dict):
                for name, item in steps.items():
                    if "maker" in normalize_token(name):
                        candidates.append("Maker")
                    candidates.append(name)
                    if isinstance(item, dict):
                        candidates.extend(
                            value
                            for value in (
                                item.get("name"),
                                get_nested(item, ("summary_dataset", "name")),
                            )
                            if value
                        )
        if isinstance(bundle.tool_discovery, dict):
            tutorial_text = " ".join(
                collect_nested_strings(bundle.tool_discovery.get("tutorial_matches"))
            )
            if "maker" in normalize_token(tutorial_text):
                candidates.append("Maker")
    elif field_path == "galaxy_execution.workflow_tool_step_count":
        counts = get_nested(bundle.workflow_metadata or {}, ("counts",))
        if isinstance(counts, dict):
            for key in (
                "execution_steps_excluding_inputs",
                "top_level_tool_steps",
                "expanded_tool_steps_including_subworkflow_tools",
                "top_level_total_objects",
            ):
                if counts.get(key) is not None:
                    candidates.append(counts.get(key))
        candidates.extend(
            value
            for value in (
                workflow.get("tool_steps"),
                count_workflow_export_tool_steps(bundle.workflow_export),
            )
            if value is not None
        )
    elif field_path == "galaxy_execution.total_tool_executions":
        candidates.extend(
            value
            for value in (
                count_tool_output_steps(bundle.tool_outputs, completed_only=True),
                count_tool_output_steps(bundle.tool_outputs, completed_only=False),
            )
            if value is not None
        )
        if not candidates:
            fallback = count_history_jobs(bundle.history_contents)
            if fallback is not None:
                candidates.append(fallback)
    elif field_path == "scientific_answer.workflow_input_type":
        candidates.extend(value for value in (inputs.get("collection_type"), raw.get("input")) if value)
    elif field_path == "scientific_answer.final_artifact_format":
        candidates.extend(
            value
            for value in (
                last_artifact.get("file_ext"),
                raw.get("last artifact"),
                raw.get("artifact"),
            )
            if value
        )
    elif field_path == "scientific_answer.assembly_tool":
        candidates.extend(
            value
            for value in (
                get_nested(bundle.workflow_metadata or {}, ("assembly_step", "name")),
                raw.get("tool_name_2"),
                get_nested(raw, ("scientific_answer", "assembly_tool")),
            )
            if value
        )
    elif field_path == "scientific_answer.functional_annotation_tool":
        candidates.extend(
            value
            for value in (
                get_nested(bundle.workflow_metadata or {}, ("functional_mapper_step", "name")),
                raw.get("tool_name_1"),
                get_nested(raw, ("scientific_answer", "functional_annotation_tool")),
            )
            if value
        )
    elif field_path == "scientific_answer.evaluation_tool":
        steps = get_nested(bundle.tool_outputs or {}, ("steps",))
        if isinstance(steps, dict):
            candidates.extend(key for key in steps if "busco" in normalize_token(key))
        candidates.extend(
            value
            for value in (
                raw.get("tool_name_1"),
                get_nested(raw, ("scientific_answer", "evaluation_tool")),
            )
            if value
        )
    elif field_path == "scientific_answer.visualization_tool":
        steps = get_nested(bundle.tool_outputs or {}, ("steps",))
        if isinstance(steps, dict):
            candidates.extend(key for key in steps if "jbrowse" in normalize_token(key))
        candidates.extend(
            value
            for value in (
                raw.get("tool_name_2"),
                get_nested(raw, ("scientific_answer", "visualization_tool")),
            )
            if value
        )
    elif field_path == "scientific_answer.normalization_tool":
        candidates.extend(
            value
            for value in (
                raw.get("data_normalization"),
                get_nested(raw, ("scientific_answer", "normalization_tool")),
            )
            if value
        )
    elif field_path == "scientific_answer.key_artifact":
        candidates.extend(value for value in (raw.get("artifact"), raw.get("last artifact")) if value)
        if isinstance(bundle.tool_outputs, dict):
            resumed = bundle.tool_outputs.get("resumed_upstream")
            if isinstance(resumed, dict):
                for item in resumed.values():
                    if isinstance(item, dict) and item.get("name"):
                        candidates.append(item.get("name"))

    return [candidate for candidate in candidates if candidate is not None]


def choose_best_entity_candidate(candidates: list[Any], bundle: ArtifactBundle) -> Any:
    if not candidates:
        return None
    acceptable_classes = (
        bundle.ground_truth.get("galaxy_execution", {})
        .get("final_entity_name", {})
        .get("acceptable_entity_classes", [])
    )
    if acceptable_classes:
        ranked: list[tuple[int, Any]] = []
        noisy_tokens = {
            "dataset",
            "summary",
            "stats",
            "statistics",
            "report",
            "output",
            "outputs",
            "exons",
        }
        for candidate in candidates:
            text = normalize_token(candidate)
            if not text or not value_matches_classes(candidate, acceptable_classes):
                continue
            alias_hits = 0
            for cls in acceptable_classes:
                cls_norm = normalize_token(cls)
                aliases = None
                for alias_key, alias_values in CLASS_ALIAS_MAP.items():
                    if normalize_token(alias_key) == cls_norm:
                        aliases = alias_values
                        break
                alias_tokens = {
                    normalize_token(alias) for alias in (aliases or {cls_norm}) if normalize_token(alias)
                }
                alias_hits += sum(1 for alias in alias_tokens if alias and alias in text)
            penalty = sum(1 for token in noisy_tokens if token in text)
            ranked.append((alias_hits * 10 - penalty * 3 - len(text.split()), candidate))
        if ranked:
            ranked.sort(reverse=True, key=lambda item: item[0])
            return ranked[0][1]
    return candidates[0]


def value_matches_classes(
    value: Any,
    classes: Iterable[str],
    *extra_texts: Any,
) -> bool:
    haystacks = [normalize_token(value)]
    for extra in extra_texts:
        if isinstance(extra, (list, tuple, set)):
            haystacks.extend(normalize_token(item) for item in extra if normalize_token(item))
        else:
            extra_norm = normalize_token(extra)
            if extra_norm:
                haystacks.append(extra_norm)
    haystacks = [haystack for haystack in haystacks if haystack]
    if not haystacks:
        return False
    for cls in classes:
        cls_norm = normalize_token(cls)
        aliases = None
        for alias_key, alias_values in CLASS_ALIAS_MAP.items():
            if normalize_token(alias_key) == cls_norm:
                aliases = alias_values
                break
        alias_tokens = {normalize_token(alias) for alias in (aliases or {cls_norm}) if normalize_token(alias)}
        for haystack in haystacks:
            if any(alias in haystack or haystack in alias for alias in alias_tokens):
                return True
    return False


def strings_equivalent(left: Any, right: Any) -> bool:
    return text_matches_expected(left, right)


def metric_names_equivalent(agent_name: Any, expected_name: Any, bundle: ArtifactBundle) -> bool:
    if text_matches_expected(agent_name, expected_name):
        return True
    fair_scoring = bundle.ground_truth.get("fair_scoring", {})
    aliases = fair_scoring.get("normalize_metric_name_aliases", [])
    alias_set = {normalize_token(alias) for alias in aliases if normalize_token(alias)}
    agent_norm = normalize_token(agent_name)
    expected_norm = normalize_token(expected_name)
    return bool(agent_norm and expected_norm and agent_norm in alias_set and expected_norm in alias_set)


def rule_summary(spec: Any) -> str:
    if isinstance(spec, str):
        return f"exact({spec})"
    if isinstance(spec, list):
        return f"one_of({', '.join(map(str, spec))})"
    if not isinstance(spec, dict):
        return stringify(spec)
    mode = spec.get("comparison_mode")
    if mode == "alias_match":
        canonical = spec.get("canonical_value")
        aliases = spec.get("accepted_aliases", [])
        return f"alias_match({canonical}; aliases={aliases})"
    if mode == "at_least":
        extras = []
        if spec.get("name"):
            extras.append(f"name={spec.get('name')}")
        if spec.get("split"):
            extras.append(f"split={spec.get('split')}")
        extra_text = f"; {', '.join(extras)}" if extras else ""
        return f"at_least({spec.get('threshold')}{extra_text})"
    if mode == "within_tolerance":
        return f"within_tolerance({spec.get('value')} ± {spec.get('tolerance_abs')})"
    if mode == "contains_ci":
        return f"contains_ci({spec.get('canonical_value')})"
    if mode == "set_overlap_at_least":
        return f"set_overlap_at_least({spec.get('minimum_overlap')})"
    if mode == "acceptable_value_set":
        return f"acceptable_value_set({spec.get('accepted_values', [])})"
    if mode == "reported_choice_consistent_with_run_artifacts":
        return "reported_choice_consistent_with_run_artifacts"
    if mode == "self_consistent_with_run_artifacts":
        return "self_consistent_with_run_artifacts"
    if mode == "exact":
        return f"exact({spec.get('canonical_value') or spec.get('value')})"
    return json.dumps(spec, ensure_ascii=True, sort_keys=True)


def normalize_result(bundle: ArtifactBundle) -> dict[str, Any]:
    raw = copy.deepcopy(bundle.raw_result)
    if isinstance(raw, dict) and ("scientific_answer" in raw or "galaxy_execution" in raw):
        normalized = {
            "scientific_answer": copy.deepcopy(raw.get("scientific_answer") or {}),
            "galaxy_execution": copy.deepcopy(raw.get("galaxy_execution") or {}),
        }
    else:
        normalized = {"scientific_answer": {}, "galaxy_execution": {}}

    scientific = normalized["scientific_answer"]
    galaxy = normalized["galaxy_execution"]
    exp = bundle.experiment_id

    if exp in {"experiment_1", "experiment_2", "experiment_3"}:
        scientific.setdefault("target", raw.get("target"))
        metric_value = first_nonempty(
            get_nested(raw, ("scientific_answer", "primary_metric", "value")),
            raw.get("roc-auc"),
            raw.get("ROC-AUC"),
        )
        if metric_value is not None:
            scientific.setdefault(
                "primary_metric",
                {"name": "ROC-AUC", "split": "test", "value": parse_number(metric_value)},
            )
            bundle.normalization_notes.append("Normalized legacy metric fields into scientific_answer.primary_metric.")
        tool_name = raw.get("tool_name")
        if tool_name:
            galaxy.setdefault("final_entity_name", tool_name)
            bundle.normalization_notes.append("Normalized legacy tool_name into galaxy_execution.final_entity_name.")

    if exp == "experiment_4":
        scientific.setdefault("analysis_goal", "chromatin accessibility profiling")
        scientific.setdefault("workflow_input_type", raw.get("input"))
        scientific.setdefault("final_artifact_format", raw.get("last artifact"))
        galaxy.setdefault(
            "workflow_tool_step_count",
            parse_contextual_count(raw.get("workflow steps"), "galaxy_execution.workflow_tool_step_count"),
        )
    elif exp == "experiment_5":
        scientific.setdefault("analysis_type", raw.get("analysis_type"))
        scientific.setdefault("key_artifact", raw.get("artifact"))
        galaxy.setdefault(
            "workflow_tool_step_count",
            parse_contextual_count(raw.get("workflow steps"), "galaxy_execution.workflow_tool_step_count"),
        )
    elif exp == "experiment_6":
        scientific.setdefault(
            "normalization_tool",
            first_nonempty(raw.get("data_normalization"), raw.get("normalization_tool")),
        )
        scientific.setdefault(
            "marker_gene_panel",
            first_nonempty(raw.get("list_of_genes"), raw.get("marker_gene_panel")),
        )
        galaxy.setdefault(
            "workflow_tool_step_count",
            parse_contextual_count(
                first_nonempty(raw.get("total_tool_steps"), raw.get("workflow steps")),
                "galaxy_execution.workflow_tool_step_count",
            ),
        )
    elif exp == "experiment_7":
        scientific.setdefault(
            "assembly_tool",
            first_nonempty(raw.get("tool_name_2"), raw.get("assembly_tool")),
        )
        scientific.setdefault(
            "functional_annotation_tool",
            first_nonempty(raw.get("tool_name_1"), raw.get("functional_annotation_tool")),
        )
        galaxy.setdefault(
            "workflow_tool_step_count",
            parse_contextual_count(
                first_nonempty(raw.get("total__steps"), raw.get("total_tool_steps"), raw.get("workflow steps")),
                "galaxy_execution.workflow_tool_step_count",
            ),
        )
    elif exp == "experiment_8":
        scientific.setdefault(
            "evaluation_tool",
            first_nonempty(raw.get("tool_name_1"), raw.get("evaluation_tool")),
        )
        scientific.setdefault(
            "visualization_tool",
            first_nonempty(raw.get("tool_name_2"), raw.get("visualization_tool")),
        )
        galaxy.setdefault(
            "total_tool_executions",
            parse_contextual_count(
                first_nonempty(raw.get("total_tools"), raw.get("total_tool_executions")),
                "galaxy_execution.total_tool_executions",
            ),
        )

    if not first_nonempty(galaxy.get("final_entity_type")):
        expected_type = bundle.ground_truth.get("galaxy_execution", {}).get("final_entity_type")
        if expected_type:
            galaxy["final_entity_type"] = expected_type
            bundle.normalization_notes.append("Filled galaxy_execution.final_entity_type from the hidden contract for legacy compatibility.")

    if not first_nonempty(galaxy.get("final_entity_name")):
        candidates = derive_artifact_candidates("galaxy_execution.final_entity_name", bundle)
        if candidates:
            galaxy["final_entity_name"] = choose_best_entity_candidate(candidates, bundle)
            bundle.normalization_notes.append("Filled galaxy_execution.final_entity_name from run artifacts.")

    if not first_nonempty(galaxy.get("history_input_mode")):
        inferred_mode = first_nonempty(
            history_input_mode_from_experiment(bundle.experiment),
            bundle.ground_truth.get("galaxy_execution", {}).get("history_input_mode"),
        )
        if inferred_mode:
            galaxy["history_input_mode"] = inferred_mode
            bundle.normalization_notes.append("Filled galaxy_execution.history_input_mode from experiment inputs.")

    if not first_nonempty(galaxy.get("adaptation_summary")):
        galaxy["adaptation_summary"] = infer_adaptation_summary(bundle)
        bundle.normalization_notes.append("Filled galaxy_execution.adaptation_summary from run trace heuristics.")

    if galaxy.get("workflow_tool_step_count") is None:
        candidates = derive_artifact_candidates("galaxy_execution.workflow_tool_step_count", bundle)
        if candidates:
            galaxy["workflow_tool_step_count"] = parse_contextual_count(
                candidates[0],
                "galaxy_execution.workflow_tool_step_count",
            )
            bundle.normalization_notes.append("Filled galaxy_execution.workflow_tool_step_count from workflow artifacts.")

    if galaxy.get("total_tool_executions") is None:
        candidates = derive_artifact_candidates("galaxy_execution.total_tool_executions", bundle)
        if candidates:
            galaxy["total_tool_executions"] = parse_contextual_count(
                candidates[0],
                "galaxy_execution.total_tool_executions",
            )
            bundle.normalization_notes.append("Filled galaxy_execution.total_tool_executions from execution artifacts.")

    return normalized


def infer_adaptation_summary(bundle: ArtifactBundle) -> str:
    categories = {
        normalize_token(entry.get("category")) for entry in bundle.activity_log if isinstance(entry, dict)
    }
    run_status = normalize_token(get_nested(bundle.errors or {}, ("run_status",)))
    total_errors = get_nested(bundle.errors or {}, ("summary", "total_errors"))
    retry_like = "retry" in categories or "revise" in categories
    if run_status == "failed":
        return "stopped_with_documented_blocker"
    if run_status == "completed_with_errors":
        return "justified_retry" if retry_like else "stopped_with_documented_blocker"
    if retry_like or (isinstance(total_errors, int) and total_errors > 0):
        return "justified_retry"
    return "single_valid_run"


def get_nested(value: Any, path: tuple[str, ...]) -> Any:
    current = value
    for part in path:
        if not isinstance(current, dict):
            return None
        current = current.get(part)
        if current is None:
            return None
    return current


def compare_against_rule(
    field_path: str,
    agent_value: Any,
    rule: Any,
    bundle: ArtifactBundle,
) -> tuple[str, float | None, str]:
    if agent_value is None and not (
        isinstance(rule, dict) and rule.get("comparison_mode") == "self_consistent_with_run_artifacts"
    ):
        return "missing", 0.0, "Result field was missing."

    if isinstance(rule, str):
        matched = strings_equivalent(agent_value, rule)
        return ("match", 1.0, "Exact string match.") if matched else ("mismatch", 0.0, f"Expected {rule!r}.")

    if isinstance(rule, list):
        normalized_choices = {normalize_token(item) for item in rule}
        matched = normalize_token(agent_value) in normalized_choices
        return ("match", 1.0, "Value is in the accepted list.") if matched else ("mismatch", 0.0, f"Accepted values: {rule}.")

    if not isinstance(rule, dict):
        matched = stringify(agent_value) == stringify(rule)
        return ("match", 1.0, "Exact value match.") if matched else ("mismatch", 0.0, f"Expected {stringify(rule)}.")

    mode = rule.get("comparison_mode")
    if mode == "exact":
        expected = first_nonempty(rule.get("canonical_value"), rule.get("value"))
        if expected is None:
            return "not_applicable", None, "Exact rule had no expected value."
        if parse_number(expected) is not None and parse_number(agent_value) is not None:
            matched = parse_number(agent_value) == parse_number(expected)
        else:
            matched = strings_equivalent(agent_value, expected)
        return ("match", 1.0, "Exact match.") if matched else ("mismatch", 0.0, f"Expected exact value {expected!r}.")

    if mode == "alias_match":
        normalized_aliases = {
            normalize_token(rule.get("canonical_value")),
            *(normalize_token(alias) for alias in rule.get("accepted_aliases", [])),
        }
        matched = any(text_matches_expected(agent_value, alias) for alias in normalized_aliases if alias)
        note = f"Accepted aliases: {[rule.get('canonical_value'), *rule.get('accepted_aliases', [])]}"
        return ("match", 1.0, note) if matched else ("mismatch", 0.0, note)

    if mode == "contains_ci":
        canonical = normalize_token(rule.get("canonical_value"))
        if canonical and canonical in normalize_token(agent_value):
            return "match", 1.0, f"Found `{rule.get('canonical_value')}` in reported value."
        return "mismatch", 0.0, f"Expected to contain `{rule.get('canonical_value')}`."

    if mode == "at_least":
        agent_number = parse_number(agent_value.get("value")) if isinstance(agent_value, dict) else parse_number(agent_value)
        threshold = parse_number(rule.get("threshold"))
        component_scores: list[float] = []
        notes: list[str] = []
        if "name" in rule:
            name_matched = metric_names_equivalent(
                agent_value.get("name") if isinstance(agent_value, dict) else agent_value,
                rule.get("name"),
                bundle,
            )
            component_scores.append(1.0 if name_matched else 0.0)
            notes.append(
                "Metric name matched expected canonical form."
                if name_matched
                else f"Metric name did not match expected `{rule.get('name')}`."
            )
        if "split" in rule:
            split_matched = text_matches_expected(
                agent_value.get("split") if isinstance(agent_value, dict) else None,
                rule.get("split"),
            )
            component_scores.append(1.0 if split_matched else 0.0)
            notes.append(
                "Metric split matched expected split."
                if split_matched
                else f"Metric split did not match expected `{rule.get('split')}`."
            )
        if agent_number is None or threshold is None:
            return "missing", 0.0, "Could not parse numeric value for threshold comparison."
        if agent_number >= threshold:
            numeric_score = 1.0
            notes.append(f"Value {agent_number} meets threshold {threshold}.")
        else:
            numeric_score = max(0.0, min(agent_number / threshold, 1.0)) if threshold > 0 else 0.0
            notes.append(f"Value {agent_number} is below threshold {threshold}.")
        component_scores.append(numeric_score)
        overall = sum(component_scores) / len(component_scores)
        status = "match" if overall >= 0.999 else "mismatch"
        return status, overall, " ".join(notes)

    if mode == "within_tolerance":
        agent_number = parse_number(agent_value.get("value")) if isinstance(agent_value, dict) else parse_number(agent_value)
        expected = parse_number(rule.get("value"))
        tolerance = parse_number(rule.get("tolerance_abs"))
        if agent_number is None or expected is None or tolerance is None:
            return "missing", 0.0, "Could not parse numeric values for tolerance comparison."
        diff = abs(agent_number - expected)
        if diff <= tolerance:
            return "match", 1.0, f"Difference {diff} is within tolerance {tolerance}."
        partial = max(0.0, 1.0 - (diff - tolerance) / max(tolerance, 1.0))
        return "mismatch", partial, f"Difference {diff} exceeds tolerance {tolerance}."

    if mode == "set_overlap_at_least":
        reference = {
            normalize_token(item) for item in rule.get("reference_genes", []) if normalize_token(item)
        }
        if isinstance(agent_value, list):
            observed = {normalize_token(item) for item in agent_value if normalize_token(item)}
        else:
            observed = {
                normalize_token(token)
                for token in re.split(r"[,\n;]+", stringify(agent_value))
                if normalize_token(token)
            }
        overlap = reference & observed
        minimum = int(rule.get("minimum_overlap", 0))
        if len(overlap) >= minimum:
            return "match", 1.0, f"Observed overlap {sorted(overlap)}."
        partial = min(len(overlap) / minimum, 1.0) if minimum > 0 else 0.0
        return "mismatch", partial, f"Observed overlap {sorted(overlap)}; required at least {minimum}."

    if mode == "acceptable_value_set":
        accepted = {normalize_token(item) for item in rule.get("accepted_values", [])}
        preferred = normalize_token(rule.get("preferred_value"))
        agent_norm = normalize_token(agent_value)
        if (
            agent_norm in accepted
            or agent_norm == preferred
            or any(alias and alias in agent_norm for alias in accepted | {preferred})
        ):
            return "match", 1.0, f"Accepted values: {rule.get('accepted_values', [])}."
        return "mismatch", 0.0, f"Accepted values: {rule.get('accepted_values', [])}."

    if mode == "reported_choice_consistent_with_run_artifacts":
        candidates = derive_artifact_candidates(field_path, bundle)
        candidate_tokens = {normalize_token(candidate) for candidate in candidates if normalize_token(candidate)}
        agent_norm = normalize_token(agent_value)

        acceptable_aliases = {
            normalize_token(alias) for alias in rule.get("acceptable_tool_aliases", [])
        }
        if acceptable_aliases and not any(
            alias and (alias == agent_norm or alias in agent_norm or agent_norm in alias)
            for alias in acceptable_aliases
        ):
            return "mismatch", 0.0, f"Reported value is not in the accepted alias set {sorted(acceptable_aliases)}."

        acceptable_classes = rule.get("acceptable_entity_classes") or rule.get("acceptable_tool_classes") or rule.get("acceptable_artifact_classes")
        if acceptable_classes and not value_matches_classes(
            agent_value,
            acceptable_classes,
            candidates,
            workflow_text_haystack(bundle),
        ):
            return "mismatch", 0.0, f"Reported value does not match the accepted classes {acceptable_classes}."

        candidate_match = any(
            token and (token == agent_norm or token in agent_norm or agent_norm in token)
            for token in candidate_tokens
        )
        if candidate_tokens and not candidate_match:
            return "mismatch", 0.0, f"Reported value is not consistent with artifact candidates {candidates}."
        if candidate_tokens or acceptable_aliases or acceptable_classes:
            note = f"Artifact candidates: {candidates}" if candidates else "Used class/alias-based consistency check."
            return "match", 1.0, note
        return "not_applicable", None, "No artifact candidates or class hints were available for consistency checking."

    if mode == "self_consistent_with_run_artifacts":
        candidates = derive_artifact_candidates(field_path, bundle)
        if not candidates:
            return "not_applicable", None, "No artifact candidates were available for self-consistency checking."
        agent_number = parse_number(agent_value)
        candidate_numbers = [parse_number(candidate) for candidate in candidates if parse_number(candidate) is not None]
        if agent_number is not None and candidate_numbers:
            if any(agent_number == candidate for candidate in candidate_numbers):
                return "match", 1.0, f"Reported value matches artifact-derived candidates {candidate_numbers}."
            nearest = min(abs(agent_number - candidate) for candidate in candidate_numbers)
            partial = max(0.0, 1.0 - nearest / max(candidate_numbers[0] if candidate_numbers[0] else 1.0, 1.0))
            return "mismatch", partial, f"Reported value {agent_number} does not match artifact-derived candidates {candidate_numbers}."
        if any(strings_equivalent(agent_value, candidate) for candidate in candidates):
            return "match", 1.0, f"Reported value matches artifact-derived candidates {candidates}."
        return "mismatch", 0.0, f"Reported value does not match artifact-derived candidates {candidates}."

    return "not_applicable", None, f"Unsupported comparison mode: {mode}."


def compare_stage_requirement(
    level: str,
    stage: str,
    bundle: ArtifactBundle,
) -> ComparisonEntry:
    status, note = stage_present(stage, bundle)
    score_value = None if status is None else (1.0 if status else 0.0)
    return ComparisonEntry(
        score_name="standard_analysis_score",
        field_path=f"tier_specific_expectations.{level}.galaxy_execution.required_execution_stages::{stage}",
        agent_value="present" if status else "absent",
        reference_rule=f"required_execution_stage({stage})",
        match_status="not_applicable" if status is None else ("match" if status else "mismatch"),
        score_value=score_value,
        notes=note,
    )


def build_scientific_comparisons(
    normalized_result: dict[str, Any],
    bundle: ArtifactBundle,
) -> list[ComparisonEntry]:
    entries: list[ComparisonEntry] = []
    scientific_rules = bundle.ground_truth.get("scientific_answer", {})
    scientific_values = normalized_result.get("scientific_answer", {})
    for field_name, rule in scientific_rules.items():
        agent_value = scientific_values.get(field_name)
        status, score_value, note = compare_against_rule(
            f"scientific_answer.{field_name}",
            agent_value,
            rule,
            bundle,
        )
        entries.append(
            ComparisonEntry(
                score_name="scientific_solution_score",
                field_path=f"scientific_answer.{field_name}",
                agent_value=agent_value,
                reference_rule=rule_summary(rule),
                match_status=status,
                score_value=score_value,
                notes=note,
            )
        )
    return entries


def build_standard_comparisons(
    normalized_result: dict[str, Any],
    bundle: ArtifactBundle,
) -> list[ComparisonEntry]:
    if not bundle.level:
        return [
            ComparisonEntry(
                score_name="standard_analysis_score",
                field_path="standard_analysis_score",
                agent_value=None,
                reference_rule="level_required",
                match_status="not_applicable",
                score_value=None,
                notes="Prompt tier was not provided or inferable, so tier-specific standard analysis checks were skipped.",
            )
        ]

    tier_rules = (
        bundle.ground_truth.get("tier_specific_expectations", {}).get(bundle.level, {})
    )
    if not tier_rules:
        return [
            ComparisonEntry(
                score_name="standard_analysis_score",
                field_path=f"tier_specific_expectations.{bundle.level}",
                agent_value=None,
                reference_rule="no_tier_specific_expectations",
                match_status="not_applicable",
                score_value=None,
                notes=f"No tier-specific expectations were defined for {bundle.level}.",
            )
        ]

    entries: list[ComparisonEntry] = []
    for section in ("scientific_answer", "galaxy_execution"):
        section_rules = tier_rules.get(section, {})
        section_values = normalized_result.get(section, {})
        if not isinstance(section_rules, dict):
            continue
        for field_name, rule in section_rules.items():
            if field_name == "required_execution_stages" and isinstance(rule, list):
                for stage in rule:
                    entries.append(compare_stage_requirement(bundle.level, stage, bundle))
                continue
            agent_value = section_values.get(field_name)
            status, score_value, note = compare_against_rule(
                f"{section}.{field_name}",
                agent_value,
                rule,
                bundle,
            )
            entries.append(
                ComparisonEntry(
                    score_name="standard_analysis_score",
                    field_path=f"tier_specific_expectations.{bundle.level}.{section}.{field_name}",
                    agent_value=agent_value,
                    reference_rule=rule_summary(rule),
                    match_status=status,
                    score_value=score_value,
                    notes=note,
                )
            )
    return entries


def build_galaxy_comparisons(
    normalized_result: dict[str, Any],
    bundle: ArtifactBundle,
) -> list[ComparisonEntry]:
    entries: list[ComparisonEntry] = []
    galaxy_rules = bundle.ground_truth.get("galaxy_execution", {})
    galaxy_values = normalized_result.get("galaxy_execution", {})
    for field_name, rule in galaxy_rules.items():
        if field_name == "required_capabilities":
            for capability in rule:
                observed, note = capability_observation(capability, bundle)
                entries.append(
                    ComparisonEntry(
                        score_name="galaxy_execution_score",
                        field_path=f"galaxy_execution.required_capabilities::{capability}",
                        agent_value="observed" if observed else "not_observed",
                        reference_rule=f"required_capability({capability})",
                        match_status="not_applicable" if observed is None else ("match" if observed else "mismatch"),
                        score_value=None if observed is None else (1.0 if observed else 0.0),
                        notes=note,
                    )
                )
            continue

        if field_name == "acceptable_adaptation_summaries":
            agent_value = galaxy_values.get("adaptation_summary")
            normalized_choices = {normalize_token(item) for item in rule}
            agent_norm = normalize_token(agent_value)
            if not agent_norm:
                status, score_value, note = "missing", 0.0, "Adaptation summary was missing."
            elif agent_norm in normalized_choices:
                status, score_value, note = "match", 1.0, f"Accepted summaries: {rule}."
            else:
                status, score_value, note = "mismatch", 0.0, f"Accepted summaries: {rule}."
            entries.append(
                ComparisonEntry(
                    score_name="galaxy_execution_score",
                    field_path="galaxy_execution.adaptation_summary",
                    agent_value=agent_value,
                    reference_rule=f"one_of({rule})",
                    match_status=status,
                    score_value=score_value,
                    notes=note,
                )
            )
            continue

        agent_value = galaxy_values.get(field_name)
        status, score_value, note = compare_against_rule(
            f"galaxy_execution.{field_name}",
            agent_value,
            rule,
            bundle,
        )
        entries.append(
            ComparisonEntry(
                score_name="galaxy_execution_score",
                field_path=f"galaxy_execution.{field_name}",
                agent_value=agent_value,
                reference_rule=rule_summary(rule),
                match_status=status,
                score_value=score_value,
                notes=note,
            )
        )
    return entries


def summarize_score(
    score_name: str,
    entries: list[ComparisonEntry],
    bundle: ArtifactBundle,
) -> ScoreValue:
    applicable = [entry for entry in entries if entry.match_status != "not_applicable"]
    if not applicable:
        score_meta = bundle.evaluator.get("score_model", {}).get(score_name, {})
        basis = score_meta.get("description", "")
        notes = [entry.notes for entry in entries if entry.notes]
        return ScoreValue(
            value=None,
            status="not_applicable",
            applicability="not_applicable",
            basis=basis,
            matched_fields=0,
            applicable_fields=0,
            notes=notes,
        )

    matched = sum(1 for entry in applicable if entry.match_status == "match")
    values = [entry.score_value if entry.score_value is not None else 0.0 for entry in applicable]
    score_value = sum(values) / len(values)
    if score_value >= 0.8:
        status = "pass"
    elif score_value > 0.0:
        status = "partial"
    else:
        status = "fail"
    score_meta = bundle.evaluator.get("score_model", {}).get(score_name, {})
    basis = score_meta.get("description", "")
    notes = [entry.notes for entry in applicable if entry.match_status != "match" and entry.notes]
    return ScoreValue(
        value=round(score_value, 4),
        status=status,
        applicability="required",
        basis=basis,
        matched_fields=matched,
        applicable_fields=len(applicable),
        notes=notes,
    )


def build_markdown_report(
    bundle: ArtifactBundle,
    normalized_result: dict[str, Any],
    all_entries: list[ComparisonEntry],
    score_summaries: dict[str, ScoreValue],
) -> str:
    groups = {
        "scientific_solution_score": "Scientific Solution Field Comparison",
        "standard_analysis_score": "Standard Analysis Field Comparison",
        "galaxy_execution_score": "Galaxy Execution Field Comparison",
    }
    lines = [
        "# Benchmark Score Report",
        "",
        f"- Experiment: `{bundle.experiment_id}`",
        f"- Level: `{bundle.level or 'unknown'}`",
        f"- Run directory: `{bundle.run_dir}`",
        f"- Result artifact: `{bundle.result_path}`",
        "",
        "## Score Summary",
        "",
        "| Score | Value | Status | Basis | Notes |",
        "|---|---|---|---|---|",
    ]
    for score_name in (
        "scientific_solution_score",
        "standard_analysis_score",
        "galaxy_execution_score",
    ):
        summary = score_summaries[score_name]
        note_text = "; ".join(summary.notes[:3]) if summary.notes else ""
        value_text = "not_applicable" if summary.value is None else f"{summary.value:.4f}"
        lines.append(
            f"| `{score_name}` | {value_text} | {summary.status} | {summary.basis} | {note_text} |"
        )

    if bundle.normalization_notes:
        lines.extend(
            [
                "",
                "## Normalization Notes",
                "",
                *[f"- {note}" for note in bundle.normalization_notes],
            ]
        )

    for score_name, heading in groups.items():
        lines.extend(["", f"## {heading}", "", "| Field | Agent Result | Ground Truth | Match Status | Notes |", "|---|---|---|---|---|"])
        for entry in all_entries:
            if entry.score_name != score_name:
                continue
            lines.append(
                f"| `{entry.field_path}` | {stringify(entry.agent_value)} | {entry.reference_rule} | {entry.match_status} | {entry.notes} |"
            )

    lines.extend(
        [
            "",
            "## Normalized Result Used For Scoring",
            "",
            "```json",
            json.dumps(normalized_result, indent=2, ensure_ascii=True, sort_keys=True),
            "```",
        ]
    )
    return "\n".join(lines) + "\n"


def write_outputs(
    comparison_path: Path,
    summary_path: Path,
    markdown_report: str,
    json_summary: dict[str, Any],
) -> None:
    comparison_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    comparison_path.write_text(markdown_report, encoding="utf-8")
    summary_path.write_text(json.dumps(json_summary, indent=2, ensure_ascii=True, sort_keys=True) + "\n", encoding="utf-8")


def make_json_summary(
    bundle: ArtifactBundle,
    normalized_result: dict[str, Any],
    entries: list[ComparisonEntry],
    score_summaries: dict[str, ScoreValue],
    comparison_path: Path,
    summary_path: Path,
) -> dict[str, Any]:
    return {
        "experiment_id": bundle.experiment_id,
        "level": bundle.level,
        "run_dir": str(bundle.run_dir),
        "result_path": str(bundle.result_path),
        "comparison_report_path": str(comparison_path),
        "score_summary_path": str(summary_path),
        "normalized_result": normalized_result,
        "scores": {name: asdict(value) for name, value in score_summaries.items()},
        "field_comparisons": [asdict(entry) for entry in entries],
        "normalization_notes": bundle.normalization_notes,
    }


def default_output_paths(run_dir: Path) -> tuple[Path, Path]:
    results_dir = run_dir / "results"
    return results_dir / "comparison.scored.md", results_dir / "score_summary.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Score a Galaxy Benchmark run directory.")
    parser.add_argument("--run-dir", required=True, help="Path to the run directory under outputs/.")
    parser.add_argument("--experiment-id", help="Override the inferred experiment id.")
    parser.add_argument("--level", choices=LEVELS, help="Prompt tier. If omitted, the scorer will try to infer it.")
    parser.add_argument(
        "--comparison-path",
        help="Path to write the Markdown comparison report. Defaults to results/comparison.scored.md.",
    )
    parser.add_argument(
        "--summary-path",
        help="Path to write the JSON score summary. Defaults to results/score_summary.json.",
    )
    parser.add_argument(
        "--stdout-only",
        action="store_true",
        help="Print the JSON score summary to stdout instead of writing files.",
    )
    args = parser.parse_args(argv)

    run_dir = Path(args.run_dir).resolve()
    experiment_id = infer_experiment_id(run_dir, args.experiment_id)
    level = infer_level(run_dir, args.level)

    bundle = build_bundle(run_dir, experiment_id, level)
    normalized_result = normalize_result(bundle)

    entries: list[ComparisonEntry] = []
    entries.extend(build_scientific_comparisons(normalized_result, bundle))
    entries.extend(build_standard_comparisons(normalized_result, bundle))
    entries.extend(build_galaxy_comparisons(normalized_result, bundle))

    score_summaries = {
        "scientific_solution_score": summarize_score(
            "scientific_solution_score",
            [entry for entry in entries if entry.score_name == "scientific_solution_score"],
            bundle,
        ),
        "standard_analysis_score": summarize_score(
            "standard_analysis_score",
            [entry for entry in entries if entry.score_name == "standard_analysis_score"],
            bundle,
        ),
        "galaxy_execution_score": summarize_score(
            "galaxy_execution_score",
            [entry for entry in entries if entry.score_name == "galaxy_execution_score"],
            bundle,
        ),
    }

    comparison_path, summary_path = default_output_paths(run_dir)
    if args.comparison_path:
        comparison_path = Path(args.comparison_path).resolve()
    if args.summary_path:
        summary_path = Path(args.summary_path).resolve()

    markdown_report = build_markdown_report(bundle, normalized_result, entries, score_summaries)
    json_summary = make_json_summary(
        bundle,
        normalized_result,
        entries,
        score_summaries,
        comparison_path,
        summary_path,
    )

    if args.stdout_only:
        print(json.dumps(json_summary, indent=2, ensure_ascii=True, sort_keys=True))
        return 0

    write_outputs(comparison_path, summary_path, markdown_report, json_summary)
    print(f"Wrote {comparison_path}")
    print(f"Wrote {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
