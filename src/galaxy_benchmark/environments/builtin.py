from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from galaxy_benchmark.agents.base import AgentAdapter

from .base import EnvironmentRunResult


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(slots=True)
class OpenEnvironmentRunner:
    environment_name: str = "open"

    def execute(
        self,
        task: dict[str, Any],
        prompt_text: str,
        datasets: list[Path],
        agent: AgentAdapter,
        run_dir: Path,
    ) -> EnvironmentRunResult:
        agent.prepare(task, prompt_text, self.environment_name, datasets)
        execution = agent.execute()
        trace = [{"step": 0, "action": "environment_setup", "value": "open"}] + execution.trace
        return EnvironmentRunResult(
            status="partial" if execution.failure_modes else "success",
            outputs={
                "scientific_answer": execution.scientific_answer,
                "galaxy_execution": execution.galaxy_execution,
                **execution.outputs,
            },
            artifacts=execution.artifacts,
            trace=trace,
            timing={"started_at": _now_iso(), "finished_at": _now_iso()},
            failure_modes=execution.failure_modes,
            resource_usage={"environment": "open"},
        )


@dataclass(slots=True)
class GalaxyEnvironmentRunner:
    environment_name: str = "galaxy"

    def execute(
        self,
        task: dict[str, Any],
        prompt_text: str,
        datasets: list[Path],
        agent: AgentAdapter,
        run_dir: Path,
    ) -> EnvironmentRunResult:
        agent.prepare(task, prompt_text, self.environment_name, datasets)
        execution = agent.execute()
        trace = [
            {
                "step": 0,
                "action": "environment_setup",
                "value": "galaxy",
                "instance": task.get("execution_environment", {}).get("galaxy_instance"),
            },
            {
                "step": 0,
                "action": "execution_rule",
                "value": task.get("execution_environment", {}).get("execution_rule"),
            },
        ] + execution.trace
        artifacts = list(execution.artifacts)
        artifacts.append({"path": str(run_dir / "results" / "galaxy_execution_stub.json"), "type": "provenance"})
        return EnvironmentRunResult(
            status="partial" if execution.failure_modes else "success",
            outputs={
                "scientific_answer": execution.scientific_answer,
                "galaxy_execution": execution.galaxy_execution,
                **execution.outputs,
            },
            artifacts=artifacts,
            trace=trace,
            timing={"started_at": _now_iso(), "finished_at": _now_iso()},
            failure_modes=execution.failure_modes,
            resource_usage={"environment": "galaxy"},
        )


@dataclass(slots=True)
class GalaxySkillsEnvironmentRunner:
    environment_name: str = "galaxy_skills"

    def execute(
        self,
        task: dict[str, Any],
        prompt_text: str,
        datasets: list[Path],
        agent: AgentAdapter,
        run_dir: Path,
    ) -> EnvironmentRunResult:
        agent.prepare(task, prompt_text, self.environment_name, datasets)
        execution = agent.execute()
        trace = [
            {
                "step": 0,
                "action": "environment_setup",
                "value": "galaxy_skills",
                "instance": task.get("execution_environment", {}).get("galaxy_instance"),
            },
            {
                "step": 0,
                "action": "skills_support",
                "value": "Galaxy procedural skills enabled",
            },
        ] + execution.trace
        artifacts = list(execution.artifacts)
        artifacts.append({"path": str(run_dir / "results" / "skills_manifest.json"), "type": "skills"})
        return EnvironmentRunResult(
            status="partial" if execution.failure_modes else "success",
            outputs={
                "scientific_answer": execution.scientific_answer,
                "galaxy_execution": execution.galaxy_execution,
                "skills_used": ["procedural_guidance"],
                **execution.outputs,
            },
            artifacts=artifacts,
            trace=trace,
            timing={"started_at": _now_iso(), "finished_at": _now_iso()},
            failure_modes=execution.failure_modes,
            resource_usage={"environment": "galaxy_skills"},
        )


BUILTIN_ENVIRONMENTS: dict[str, type[OpenEnvironmentRunner] | type[GalaxyEnvironmentRunner] | type[GalaxySkillsEnvironmentRunner]] = {
    "open": OpenEnvironmentRunner,
    "galaxy": GalaxyEnvironmentRunner,
    "galaxy_skills": GalaxySkillsEnvironmentRunner,
}
