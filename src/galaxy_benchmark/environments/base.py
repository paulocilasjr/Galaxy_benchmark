from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

from galaxy_benchmark.agents.base import AgentAdapter


@dataclass(slots=True)
class EnvironmentRunResult:
    status: str
    outputs: dict[str, Any]
    reasoning: list[str] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    timing: dict[str, Any] | None = None
    failure_modes: list[str] = field(default_factory=list)
    resource_usage: dict[str, Any] | None = None


class EnvironmentRunner(Protocol):
    environment_name: str

    def execute(
        self,
        task: dict[str, Any],
        prompt_text: str,
        datasets: list[Path],
        agent: AgentAdapter,
        run_dir: Path,
    ) -> EnvironmentRunResult:
        """Execute one task instance in the target environment."""
