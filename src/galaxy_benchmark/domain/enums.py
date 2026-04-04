"""Canonical enums for benchmark definitions and runs."""

from __future__ import annotations

from enum import StrEnum


class BenchmarkPillar(StrEnum):
    PLATFORM_OPERATION_CAPABILITY = "platform_operation_capability"
    PROMPT_ROBUSTNESS_AND_TRUST = "prompt_robustness_and_trust"
    ECOSYSTEM_KNOWLEDGE_USE = "ecosystem_knowledge_use"


class TaskFamily(StrEnum):
    BASIC_GALAXY_OPERATIONS = "basic_galaxy_operations"
    SINGLE_TOOL_EXECUTION = "single_tool_execution"
    WORKFLOW_RETRIEVAL_AND_EXECUTION = "workflow_retrieval_and_execution"
    TUTORIAL_GROUNDED_EXECUTION = "tutorial_grounded_execution"
    OPTIMIZATION_AND_PARAMETER_SEARCH = "optimization_and_parameter_search"
    FAILURE_RECOVERY = "failure_recovery"
    PROVENANCE_AND_REPRODUCIBILITY = "provenance_and_reproducibility"


class PromptTier(StrEnum):
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"


class PromptFormat(StrEnum):
    BRIEF = "brief"


class AgentType(StrEnum):
    EXTERNAL_GENERAL_AGENT = "external_general_agent"
    EXTERNAL_GENERAL_AGENT_WITH_WRAPPER = "external_general_agent_with_wrapper"
    INTERNAL_GALAXY_CONNECTED_AGENT = "internal_galaxy_connected_agent"
    INTERNAL_GALAXY_CONNECTED_AGENT_WITH_MCP = "internal_galaxy_connected_agent_with_mcp"
    SCRIPTED_BASELINE = "scripted_baseline"
    MOCK_TEST_AGENT = "mock_test_agent"


class AccessMode(StrEnum):
    API = "api"
    BROWSER = "browser"
    MCP = "mcp"
    HYBRID = "hybrid"
    MOCK = "mock"


class KnowledgeCondition(StrEnum):
    NONE = "none"
    GTN_ONLY = "gtn_only"
    IWC_ONLY = "iwc_only"
    GTN_AND_IWC = "gtn_and_iwc"
    RAW_WEB = "raw_web"
    MCP_EXPOSED = "mcp_exposed"


class ArtifactType(StrEnum):
    TASK_SNAPSHOT = "task_snapshot"
    PROMPT_VARIANT = "prompt_variant"
    RUN_CONFIGURATION = "run_configuration"
    ENVIRONMENT_SNAPSHOT = "environment_snapshot"
    RESULT = "result"
    SCORE = "score"
    FAILURE_ANALYSIS = "failure_analysis"
    COMPARISON = "comparison"
    REPRODUCTION = "reproduction"
    TRACE = "trace"
    REPORT = "report"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_ERRORS = "completed_with_errors"
    FAILED = "failed"


class EventCategory(StrEnum):
    PLAN = "plan"
    EXECUTE = "execute"
    CHECK = "check"
    RETRY = "retry"
    REVISE = "revise"
    KNOWLEDGE = "knowledge"


class FailureCategory(StrEnum):
    TASK_UNDERSTANDING = "task_understanding"
    WORKFLOW_DISCOVERY = "workflow_discovery"
    TOOL_DISCOVERY = "tool_discovery"
    INPUT_MAPPING = "input_mapping"
    PARAMETER_GROUNDING = "parameter_grounding"
    EXECUTION_CONTROL = "execution_control"
    POLLING_OR_WAITING = "polling_or_waiting"
    OUTPUT_INTERPRETATION = "output_interpretation"
    PROVENANCE_FAILURE = "provenance_failure"
    KNOWLEDGE_RETRIEVAL_FAILURE = "knowledge_retrieval_failure"
    KNOWLEDGE_ADAPTATION_FAILURE = "knowledge_adaptation_failure"
    UNNECESSARY_AUTONOMY = "unnecessary_autonomy"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"
    HALLUCINATED_ACTION = "hallucinated_action"
    UNSAFE_DEFAULTING = "unsafe_defaulting"
    INCOMPLETE_RECOVERY = "incomplete_recovery"
    UNKNOWN = "unknown"


class SourceType(StrEnum):
    LOCAL = "local"
    URL = "url"
    GALAXY_DATASET = "galaxy_dataset"
    GENERATED = "generated"


class Severity(StrEnum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
