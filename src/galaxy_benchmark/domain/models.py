from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import Complexity, Environment, PromptLevel, RunStatus


@dataclass(slots=True)
class TaskSpec:
    task_id: str
    title: str
    domain: str
    description: str
    complexity: Complexity
    datasets: list[dict[str, Any]]
    ground_truth: dict[str, Any]
    acceptable_solutions: list[dict[str, Any]]
    requires_iteration: bool
    evaluation_spec: dict[str, Any]
    iteration_budget: int | None = None
    tags: list[str] = field(default_factory=list)


@dataclass(slots=True)
class PromptSpec:
    prompt_id: str
    task_id: str
    specificity_level: PromptLevel
    text: str


@dataclass(slots=True)
class RunRecord:
    run_id: str
    task_id: str
    prompt_level: PromptLevel
    environment: Environment
    agent_id: str
    input_prompt: str
    status: RunStatus
    component_scores: dict[str, float]
    performance_score: float
    outputs: dict[str, Any] | None = None
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] | None = None
    timing: dict[str, Any] | None = None
    failure_modes: list[str] = field(default_factory=list)
    score_summary: dict[str, Any] | None = None
    execution_mode: str = "unspecified"
    benchmark_validity: dict[str, Any] | None = None
    execution_context: dict[str, Any] | None = None


@dataclass(slots=True)
class BenchmarkReport:
    benchmark_id: str
    agents: list[str]
    task_count: int
    environments: list[str]
    metrics: dict[str, Any]
    per_agent: list[dict[str, Any]] = field(default_factory=list)
    per_task: list[dict[str, Any]] = field(default_factory=list)
