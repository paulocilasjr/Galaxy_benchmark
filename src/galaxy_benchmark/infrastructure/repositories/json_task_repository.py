"""JSON-backed task repository."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from galaxy_benchmark.domain.enums import KnowledgeCondition, TaskFamily
from galaxy_benchmark.domain.models import BenchmarkTask, GroundTruth


class JsonTaskRepository:
    """Load canonical tasks and ground truths from JSON files."""

    def load_task(self, path: str | Path) -> BenchmarkTask:
        file_path = Path(path)
        payload = json.loads(file_path.read_text())
        return BenchmarkTask.model_validate(self._normalize_task_payload(payload))

    def load_ground_truth(self, path: str | Path) -> GroundTruth:
        file_path = Path(path)
        payload = json.loads(file_path.read_text())
        return GroundTruth.model_validate(self._normalize_ground_truth_payload(payload))

    def list_tasks(self, directory: str | Path) -> list[BenchmarkTask]:
        return [self.load_task(path) for path in sorted(Path(directory).glob("*.json"))]

    def save_task(self, task: BenchmarkTask, path: str | Path) -> Path:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(task.model_dump(mode="json"), indent=2) + "\n")
        return file_path

    def save_ground_truth(self, ground_truth: GroundTruth, path: str | Path) -> Path:
        file_path = Path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(json.dumps(ground_truth.model_dump(mode="json"), indent=2) + "\n")
        return file_path

    def _normalize_task_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        normalized = dict(payload)
        task_family = normalized.get("task_family")
        legacy_family_map = {
            "workflow_execution": TaskFamily.WORKFLOW_RETRIEVAL_AND_EXECUTION.value,
            "knowledge_guided_analysis": TaskFamily.TUTORIAL_GROUNDED_EXECUTION.value,
            "branching_pipeline_execution": TaskFamily.WORKFLOW_RETRIEVAL_AND_EXECUTION.value,
            "multi_tool_pipeline": TaskFamily.WORKFLOW_RETRIEVAL_AND_EXECUTION.value,
            "literature_grounded_reproduction": TaskFamily.PROVENANCE_AND_REPRODUCIBILITY.value,
        }
        if task_family in legacy_family_map:
            normalized["task_family"] = legacy_family_map[task_family]
        if not normalized.get("galaxy_instance"):
            normalized["galaxy_instance"] = "https://usegalaxy.org/"

        knowledge_requirements = normalized.get("knowledge_requirements", {})
        if isinstance(knowledge_requirements, list):
            conditions = []
            sources = []
            for item in knowledge_requirements:
                if item == "iwc":
                    conditions.append(KnowledgeCondition.IWC_ONLY.value)
                    sources.append("iwc")
                elif item == "gtn":
                    conditions.append(KnowledgeCondition.GTN_ONLY.value)
                    sources.append("gtn")
            normalized["knowledge_requirements"] = {
                "conditions": conditions or [KnowledgeCondition.NONE.value],
                "sources": sources,
                "notes": [],
            }

        process_constraints = normalized.get("process_constraints", {})
        if isinstance(process_constraints, dict):
            legacy_must_have = process_constraints.pop("legacy_must_have", [])
            notes = process_constraints.get("notes", [])
            if legacy_must_have:
                notes = [*notes, f"Legacy must_have requirements: {legacy_must_have!r}"]
            process_constraints["notes"] = notes
            process_constraints.setdefault("write_boundary_roots", ["runs"])
            normalized["process_constraints"] = process_constraints

        success_criteria = normalized.get("success_criteria", {})
        if isinstance(success_criteria, dict) and isinstance(success_criteria.get("metric_thresholds"), list):
            threshold_map = {}
            for item in success_criteria["metric_thresholds"]:
                metric = item.get("metric")
                value = item.get("value")
                if metric and isinstance(value, (int, float)):
                    threshold_map[str(metric)] = float(value)
            success_criteria["metric_thresholds"] = threshold_map
            normalized["success_criteria"] = success_criteria

        expected_outputs = []
        for item in normalized.get("expected_outputs", []):
            expected_outputs.append(
                {
                    "field": item["field"],
                    "value_type": item.get("value_type", "unknown"),
                    "description": item.get("description", ""),
                    "source_key": item.get("source_key") or item.get("legacy_field") or item["field"],
                    "legacy_field": item.get("legacy_field"),
                    "source": item.get("source"),
                }
            )
        normalized["expected_outputs"] = expected_outputs

        input_assets = []
        for asset in normalized.get("input_assets", []):
            asset_copy = dict(asset)
            asset_copy["format"] = asset_copy.get("format") or "unknown"
            input_assets.append(asset_copy)
        normalized["input_assets"] = input_assets
        return normalized

    def _normalize_ground_truth_payload(self, payload: dict[str, Any]) -> dict[str, Any]:
        if "expected_fields" in payload:
            return payload
        metadata = {
            "legacy_experiment_name": payload.get("legacy_experiment_name"),
            "legacy_field_names": payload.get("legacy_field_names", {}),
            "source": payload.get("source", {}),
        }
        return {
            "task_id": payload["task_id"],
            "expected_artifacts": payload.get("expected_artifacts", []),
            "expected_fields": payload.get("normalized_fields", {}),
            "acceptable_alternatives": payload.get("acceptable_alternatives", {}),
            "process_expectations": payload.get("process_expectations", []),
            "failure_expectations": payload.get("failure_expectations", []),
            "scoring_hints": payload.get(
                "scoring_hints",
                {"compare_fields": list(payload.get("normalized_fields", {}).keys())},
            ),
            "metadata": metadata,
        }
