"""Core benchmark entities and value objects."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from galaxy_benchmark.domain.enums import (
    AccessMode,
    AgentType,
    ArtifactType,
    BenchmarkPillar,
    EventCategory,
    FailureCategory,
    KnowledgeCondition,
    PromptFormat,
    PromptTier,
    RunStatus,
    Severity,
    SourceType,
    TaskFamily,
)


class InputAsset(BaseModel):
    """A typed reference to an input used by a benchmark task."""

    model_config = ConfigDict(extra="forbid")

    name: str
    source_type: SourceType
    path_or_url: str
    format: str
    role: str
    checksum: str | None = None
    optional: bool = False


class ExpectedOutputField(BaseModel):
    """A normalized output field expected from a run."""

    model_config = ConfigDict(extra="forbid")

    field: str
    value_type: str
    description: str
    source_key: str | None = None
    legacy_field: str | None = None
    source: str | None = None


class KnowledgeRequirement(BaseModel):
    """Knowledge sources or conditions required by a task."""

    model_config = ConfigDict(extra="forbid")

    conditions: list[KnowledgeCondition] = Field(default_factory=list)
    sources: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class SuccessCriteria(BaseModel):
    """Success conditions for the task outcome."""

    model_config = ConfigDict(extra="forbid")

    required_fields: list[str] = Field(default_factory=list)
    metric_thresholds: dict[str, float] = Field(default_factory=dict)
    artifact_requirements: list[str] = Field(default_factory=list)


class ProcessConstraints(BaseModel):
    """Process-level rules that executions must obey."""

    model_config = ConfigDict(extra="forbid")

    must_log_trace: bool = True
    must_not_read_ground_truth_before_result: bool = True
    write_boundary_roots: list[str] = Field(default_factory=lambda: ["runs"])
    notes: list[str] = Field(default_factory=list)


class TaskDefinition(BaseModel):
    """Structured execution expectations for a benchmark task."""

    model_config = ConfigDict(extra="forbid")

    goal: str
    required_actions: list[str] = Field(default_factory=list)
    tool_hints: list[str] = Field(default_factory=list)
    target_outputs: list[ExpectedOutputField] = Field(default_factory=list)


class BenchmarkTask(BaseModel):
    """Canonical benchmark task definition."""

    model_config = ConfigDict(extra="forbid")

    task_id: str
    suite_id: str
    title: str
    description: str
    task_family: TaskFamily
    task_subfamily: str | None = None
    benchmark_pillars: list[BenchmarkPillar] = Field(default_factory=list)
    difficulty_level: int = Field(ge=1)
    galaxy_instance: str
    input_assets: list[InputAsset] = Field(default_factory=list)
    expected_outputs: list[ExpectedOutputField] = Field(default_factory=list)
    knowledge_requirements: KnowledgeRequirement = Field(default_factory=KnowledgeRequirement)
    tool_hints: list[str] = Field(default_factory=list)
    workflow_hints: list[str] = Field(default_factory=list)
    success_criteria: SuccessCriteria = Field(default_factory=SuccessCriteria)
    process_constraints: ProcessConstraints = Field(default_factory=ProcessConstraints)
    failure_scenarios: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    task_definition: TaskDefinition | None = None

    @field_validator("suite_id", "task_id")
    @classmethod
    def _must_be_snake_case_like(cls, value: str) -> str:
        return value.strip().lower().replace("-", "_")

    def normalized_output_field_names(self) -> list[str]:
        return [field.field for field in self.expected_outputs]


class GroundTruth(BaseModel):
    """Normalized ground-truth definition for comparison and scoring."""

    model_config = ConfigDict(extra="forbid")

    task_id: str
    expected_artifacts: list[str] = Field(default_factory=list)
    expected_fields: dict[str, Any] = Field(default_factory=dict)
    acceptable_alternatives: dict[str, list[Any]] = Field(default_factory=dict)
    process_expectations: list[str] = Field(default_factory=list)
    failure_expectations: list[str] = Field(default_factory=list)
    scoring_hints: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptVariant(BaseModel):
    """A deterministic prompt variant for a task."""

    model_config = ConfigDict(extra="forbid")

    variant_id: str
    task_id: str
    tier: PromptTier
    format: PromptFormat
    content: str
    semantic_equivalence_group: str = "default"
    notes: list[str] = Field(default_factory=list)


class Budget(BaseModel):
    """Budget envelope for a run."""

    model_config = ConfigDict(extra="forbid")

    max_steps: int = 100
    max_runtime_seconds: int = 7200
    max_retries: int = 3
    max_cost_usd: float | None = None


class TimeoutPolicy(BaseModel):
    """Timeouts for launch and polling."""

    model_config = ConfigDict(extra="forbid")

    initial_status_check_seconds: int = 20
    polling_interval_seconds: int = 60
    terminal_timeout_seconds: int = 7200


class RunConfiguration(BaseModel):
    """Execution configuration for a single benchmark trial."""

    model_config = ConfigDict(extra="forbid")

    run_id: str
    task_id: str
    agent_id: str
    agent_type: AgentType | None = None
    provider: str | None = None
    model_name: str | None = None
    access_mode: AccessMode
    knowledge_condition: KnowledgeCondition
    mcp_enabled: bool = False
    prompt_variant_id: str
    prompt_tier: PromptTier | None = None
    prompt_format: PromptFormat | None = None
    repeat_index: int = 1
    seed: int | None = None
    budget: Budget = Field(default_factory=Budget)
    timeouts: TimeoutPolicy = Field(default_factory=TimeoutPolicy)
    capture_level: str = "full"


class ExecutionEvent(BaseModel):
    """Structured event emitted during a run."""

    model_config = ConfigDict(extra="forbid")

    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    step: str
    category: EventCategory
    action: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)


class ExecutionTrace(BaseModel):
    """Aggregate view of execution events for a run."""

    model_config = ConfigDict(extra="forbid")

    events: list[ExecutionEvent] = Field(default_factory=list)
    selected_tools: list[str] = Field(default_factory=list)
    selected_workflows: list[str] = Field(default_factory=list)
    retries: int = 0
    external_knowledge_accesses: list[str] = Field(default_factory=list)


class ScoreCard(BaseModel):
    """Outcome, process, and robustness scoring."""

    model_config = ConfigDict(extra="forbid")

    outcome_score: float = Field(ge=0.0, le=1.0)
    process_score: float = Field(ge=0.0, le=1.0)
    robustness_score: float = Field(ge=0.0, le=1.0)
    total_score: float = Field(ge=0.0, le=1.0)
    component_weights: dict[str, float] = Field(
        default_factory=lambda: {"outcome": 0.5, "process": 0.3, "robustness": 0.2},
    )
    subscores: dict[str, float] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def _sync_total(self) -> "ScoreCard":
        weights = self.component_weights
        expected_total = round(
            (self.outcome_score * weights["outcome"])
            + (self.process_score * weights["process"])
            + (self.robustness_score * weights["robustness"]),
            4,
        )
        if abs(self.total_score - expected_total) > 0.0001:
            self.total_score = expected_total
        return self


class FailureEvidence(BaseModel):
    """Evidence linked to a failure."""

    model_config = ConfigDict(extra="forbid")

    message: str
    step: str
    job_id: str | None = None
    invocation_id: str | None = None
    exit_code: int | None = None
    artifact_paths: list[str] = Field(default_factory=list)


class FailureRecord(BaseModel):
    """A classified failure event."""

    model_config = ConfigDict(extra="forbid")

    failure_id: str
    task_id: str
    run_id: str
    category: FailureCategory
    subcategory: str
    severity: Severity
    signature: str
    evidence: list[FailureEvidence] = Field(default_factory=list)
    root_cause: str
    recoverable: bool
    recovered: bool = False
    notes: list[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    """Bundle of result fields, score, and failures for a run."""

    model_config = ConfigDict(extra="forbid")

    task_id: str
    run_id: str
    status: RunStatus
    extracted_outputs: dict[str, Any] = Field(default_factory=dict)
    scorecard: ScoreCard | None = None
    failures: list[FailureRecord] = Field(default_factory=list)
    artifacts: dict[ArtifactType, list[str]] = Field(default_factory=dict)


class EnvironmentSnapshot(BaseModel):
    """Redacted environment metadata captured with a run."""

    model_config = ConfigDict(extra="forbid")

    captured_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    python_version: str
    platform: str
    environment: dict[str, str] = Field(default_factory=dict)


class RunPaths(BaseModel):
    """Resolved artifact paths for an immutable run directory."""

    model_config = ConfigDict(extra="forbid")

    root: Path
    manifest: Path
    input_dir: Path
    plan_dir: Path
    trace_dir: Path
    reasoning_dir: Path
    errors_dir: Path
    results_dir: Path
    artifacts_dir: Path


class RunManifest(BaseModel):
    """Manifest stored at the run root."""

    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)

    run_id: str
    task_id: str
    agent_id: str
    agent_type: AgentType | None = None
    provider: str | None = None
    model_name: str | None = None
    access_mode: AccessMode
    knowledge_condition: KnowledgeCondition
    mcp_enabled: bool = False
    prompt_variant_id: str
    prompt_tier: PromptTier | None = None
    prompt_format: PromptFormat | None = None
    repeat_index: int
    seed: int | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    artifact_root: Path
