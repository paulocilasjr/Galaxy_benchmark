from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .base import AgentExecution


def _find_candidate_target(headers: list[str]) -> str | None:
    preferred = (
        "response",
        "label",
        "target",
        "class",
        "outcome",
        "status",
        "condition",
    )
    normalized = {header.lower(): header for header in headers}
    for candidate in preferred:
        if candidate in normalized:
            return normalized[candidate]
    for header in headers:
        if ":" in header and header.split(":")[-1].strip().lower() in preferred:
            return header
    return headers[-1] if headers else None


def _tsv_headers(path: Path) -> list[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter="\t")
        return next(reader, [])


@dataclass(slots=True)
class EchoAgentAdapter:
    agent_id: str = "echo_agent_v1"
    task: dict[str, Any] | None = None
    prompt_text: str = ""
    environment: str = ""
    datasets: list[Path] = field(default_factory=list)

    def prepare(
        self,
        task: dict[str, Any],
        prompt_text: str,
        environment: str,
        datasets: list[Path],
    ) -> None:
        self.task = task
        self.prompt_text = prompt_text
        self.environment = environment
        self.datasets = datasets

    def execute(self) -> AgentExecution:
        dataset_names = [path.name for path in self.datasets]
        return AgentExecution(
            scientific_answer={
                "summary": f"Echo agent received task {self.task.get('task_id', 'unknown')}.",
                "datasets_seen": dataset_names,
            },
            galaxy_execution={
                "final_entity_type": "mixed" if self.environment != "open" else "tool",
                "final_entity_name": "Echo Agent Simulation",
                "history_input_mode": "local_upload",
                "adaptation_summary": "stopped_with_documented_blocker",
            },
            outputs={"summary": "No scientific execution performed; this is a dry-run adapter."},
            trace=[
                {
                    "step": 1,
                    "action": "echo_prompt",
                    "value": self.prompt_text,
                }
            ],
            reasoning=[
                "Echo agent does not solve the task.",
                "It exists to validate the workbench execution path and artifact generation.",
            ],
            failure_modes=["no_execution_backend"],
        )


@dataclass(slots=True)
class HeuristicAgentAdapter:
    agent_id: str = "heuristic_agent_v1"
    task: dict[str, Any] | None = None
    prompt_text: str = ""
    environment: str = ""
    datasets: list[Path] = field(default_factory=list)

    def prepare(
        self,
        task: dict[str, Any],
        prompt_text: str,
        environment: str,
        datasets: list[Path],
    ) -> None:
        self.task = task
        self.prompt_text = prompt_text
        self.environment = environment
        self.datasets = datasets

    def execute(self) -> AgentExecution:
        headers: list[str] = []
        table_paths = [path for path in self.datasets if path.suffix.lower() in {".tsv", ".csv"}]
        if table_paths:
            headers = _tsv_headers(table_paths[0])
        target = _find_candidate_target(headers)

        scientific_answer: dict[str, Any]
        reasoning: list[str]
        trace: list[dict[str, Any]]
        failure_modes: list[str]
        if target:
            scientific_answer = {
                "target": target,
                "primary_metric": {
                    "name": "ROC-AUC",
                    "split": "test" if "test" in self.prompt_text.lower() else "held_out",
                    "value": 0.5,
                },
                "notes": "Heuristic baseline inferred the apparent target column from dataset headers.",
            }
            reasoning = [
                f"Inferred target column `{target}` from tabular headers.",
                "Returned a conservative placeholder metric because no true model execution backend is configured.",
            ]
            trace = [
                {"step": 1, "action": "inspect_headers", "value": headers},
                {"step": 2, "action": "infer_target", "value": target},
                {"step": 3, "action": "emit_placeholder_metric", "value": 0.5},
            ]
            failure_modes = ["placeholder_metric_without_model_execution"]
            adaptation_summary = "stopped_with_documented_blocker"
        else:
            scientific_answer = {
                "notes": "Unable to infer a supported target or metric from the provided datasets.",
            }
            reasoning = [
                "No supported heuristic path was available for this task family.",
                "The adapter stopped rather than inventing a scientific result.",
            ]
            trace = [{"step": 1, "action": "inspect_datasets", "value": [p.name for p in self.datasets]}]
            failure_modes = ["unsupported_task_family"]
            adaptation_summary = "stopped_with_documented_blocker"

        entity_name = "Galaxy Heuristic Simulation" if self.environment != "open" else "Local Heuristic Simulation"
        if "tabular" in str(self.task.get("task_family", "")).lower():
            entity_name = "Tabular Learner" if self.environment != "open" else "Tabular Classification Baseline"

        return AgentExecution(
            scientific_answer=scientific_answer,
            galaxy_execution={
                "final_entity_type": "tool",
                "final_entity_name": entity_name,
                "history_input_mode": "local_upload",
                "adaptation_summary": adaptation_summary,
            },
            outputs={"inspected_headers": headers, "dataset_count": len(self.datasets)},
            trace=trace,
            reasoning=reasoning,
            failure_modes=failure_modes,
        )


BUILTIN_AGENTS: dict[str, type[EchoAgentAdapter] | type[HeuristicAgentAdapter]] = {
    "echo": EchoAgentAdapter,
    "heuristic": HeuristicAgentAdapter,
}
