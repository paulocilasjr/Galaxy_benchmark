from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(slots=True)
class AgentExecution:
    scientific_answer: dict[str, Any]
    galaxy_execution: dict[str, Any]
    outputs: dict[str, Any] = field(default_factory=dict)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    reasoning: list[str] = field(default_factory=list)
    failure_modes: list[str] = field(default_factory=list)


class AgentAdapter(Protocol):
    agent_id: str

    def prepare(
        self,
        task: dict[str, Any],
        prompt_text: str,
        environment: str,
        datasets: list[Path],
    ) -> None:
        """Prepare the adapter for execution."""

    def execute(self) -> AgentExecution:
        """Run the adapter and return a structured execution record."""
