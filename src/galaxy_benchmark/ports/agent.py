"""Provider-agnostic agent port."""

from __future__ import annotations

from typing import Protocol

from galaxy_benchmark.domain.models import BenchmarkTask, ExecutionTrace, PromptVariant


class AgentPort(Protocol):
    """Contract for an agent that can execute a benchmark task."""

    def execute(
        self,
        *,
        task: BenchmarkTask,
        prompt: PromptVariant,
        accessible_tools: list[str],
        accessible_resources: list[str],
    ) -> ExecutionTrace: ...
