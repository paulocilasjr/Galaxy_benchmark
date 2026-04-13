from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from galaxy_benchmark.agents.base import AgentAdapter
from galaxy_benchmark.application.contracts import prompt_level_from_specificity
from galaxy_benchmark.application.scoring import run_performance
from galaxy_benchmark.domain.enums import Environment as EnvironmentEnum
from galaxy_benchmark.domain.enums import PromptLevel, RunStatus
from galaxy_benchmark.domain.models import RunRecord
from galaxy_benchmark.environments.base import EnvironmentRunner


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=False)


def _write_text(path: Path, content: str) -> None:
    path.write_text(content, encoding="utf-8")


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _append_jsonl(path: Path, entry: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")


def _required_field_payload(required_fields: list[str], payload: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for field_path in required_fields:
        cursor_in: Any = payload
        keys = field_path.split(".")
        for key in keys:
            if not isinstance(cursor_in, dict):
                cursor_in = None
                break
            cursor_in = cursor_in.get(key)
        cursor_out = result
        for key in keys[:-1]:
            cursor_out = cursor_out.setdefault(key, {})
        cursor_out[keys[-1]] = cursor_in
    return result


def _build_plan_text(task: dict[str, Any], environment_name: str, datasets: list[Path]) -> str:
    lines = [
        f"# Plan for {task['task_id']}",
        "",
            f"- Objective: {task['user_prompt']}",
        f"- Environment: {environment_name}",
        f"- Datasets: {', '.join(path.name for path in datasets)}",
        "- Ordered plan:",
        "  1. Inspect the task contract and datasets.",
        "  2. Prepare the selected environment runner and agent adapter.",
        "  3. Execute the task and capture structured outputs.",
        "  4. Write reproducible artifacts and run record.",
        "  5. Score against hidden assets when available.",
    ]
    return "\n".join(lines) + "\n"


def _build_reasoning_text(entries: list[str]) -> str:
    timestamp = _now_iso()
    body = [f"- {timestamp}: {entry}" for entry in entries] or [f"- {timestamp}: No reasoning entries recorded."]
    return "# Reasoning Log\n\n" + "\n".join(body) + "\n"


def _component_scores(environment_result: dict[str, Any], execution_mode: str) -> dict[str, float]:
    if environment_result["status"] == "success":
        return {
            "correctness": 0.8,
            "execution": 1.0,
            "scientific_validity": 0.7,
            "reproducibility": 1.0,
            "interpretation": 0.8,
        }
    return {
        "correctness": 0.4,
        "execution": 0.8 if execution_mode != "open" else 0.6,
        "scientific_validity": 0.3,
        "reproducibility": 1.0,
        "interpretation": 0.6,
    }


def _collect_execution_context(
    task: dict[str, Any],
    environment: EnvironmentRunner,
    environment_result: dict[str, Any],
) -> dict[str, Any]:
    execution_environment = task.get("execution_environment", {})
    trace = environment_result.get("trace", []) if isinstance(environment_result, dict) else []
    history_ids = []
    invocation_ids = []
    tool_ids = []
    tool_versions = []
    workflow_ids = []
    workflow_names = []
    workflow_revisions = []
    queue_blockers = []
    for entry in trace if isinstance(trace, list) else []:
        if not isinstance(entry, dict):
            continue
        details = entry.get("details")
        candidates = [entry]
        if isinstance(details, dict):
            candidates.append(details)
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            for key, bucket in (
                ("history_id", history_ids),
                ("invocation_id", invocation_ids),
                ("tool_id", tool_ids),
                ("tool_version", tool_versions),
                ("workflow_id", workflow_ids),
                ("workflow_name", workflow_names),
                ("workflow_revision", workflow_revisions),
            ):
                value = candidate.get(key)
                if value not in (None, "") and value not in bucket:
                    bucket.append(value)
        for failure in ("queue_blocker", "scheduler_blocker"):
            blocker = entry.get(failure)
            if blocker and blocker not in queue_blockers:
                queue_blockers.append(blocker)
    timing = environment_result.get("timing", {}) if isinstance(environment_result, dict) else {}
    return {
        "platform": execution_environment.get("platform", "Galaxy" if environment.environment_name != "open" else "Open"),
        "environment_name": environment.environment_name,
        "galaxy_instance": execution_environment.get("galaxy_instance"),
        "execution_rule": execution_environment.get("execution_rule"),
        "run_started_at": timing.get("started_at"),
        "run_finished_at": timing.get("finished_at"),
        "history_ids": history_ids,
        "invocation_ids": invocation_ids,
        "workflow_ids": workflow_ids,
        "workflow_names": workflow_names,
        "workflow_revisions": workflow_revisions,
        "tool_ids": tool_ids,
        "tool_versions": tool_versions,
        "queue_blockers": queue_blockers,
    }


def _benchmark_validity(environment: EnvironmentRunner) -> dict[str, Any]:
    if environment.environment_name == "galaxy":
        return {
            "publication_eligible": False,
            "blind_package_eligible": False,
            "benchmark_alignment": "galaxy-aligned but simulated harness execution",
            "reasons": [
                "This run was produced by the internal workbench using a simulated environment runner.",
                "Publication-grade benchmark claims require a live Galaxy execution trace rather than a stubbed harness run.",
            ],
        }
    return {
        "publication_eligible": False,
        "blind_package_eligible": False,
        "benchmark_alignment": "internal non-canonical harness execution",
        "reasons": [
            f"Environment `{environment.environment_name}` is retained for internal diagnostics and is not a canonical benchmark mode.",
        ],
    }


class BenchmarkWorkbench:
    def __init__(self, root_dir: str | Path) -> None:
        self.root_dir = Path(root_dir)

    def create_run_dir(self, experiment_id: str, level: str, output_root: str | Path | None = None) -> Path:
        base = Path(output_root) if output_root else self.root_dir / "outputs"
        run_dir = base / f"{_timestamp()}_{level}_{experiment_id}"
        _ensure_dir(run_dir)
        for child in ("plan", "reasoning", "errors", "results"):
            _ensure_dir(run_dir / child)
        return run_dir

    def execute_task(
        self,
        *,
        task: dict[str, Any],
        environment: EnvironmentRunner,
        agent: AgentAdapter,
        output_root: str | Path | None = None,
    ) -> Path:
        experiment_id = task["task_id"]
        level = task["level"]
        run_dir = self.create_run_dir(experiment_id, level, output_root=output_root)
        datasets = [self.root_dir / item["path"] for item in task.get("inputs", {}).get("datasets", [])]

        error_path = run_dir / "errors" / "error.json"
        activity_path = run_dir / "results" / "activity_log.jsonl"
        plan_path = run_dir / "plan" / "saved.md"
        reasoning_path = run_dir / "reasoning" / "reasoning.md"
        result_path = run_dir / "results" / "result.json"
        reproduce_path = run_dir / "results" / f"reproduce_{experiment_id}.py"
        run_record_path = run_dir / "results" / "run_record.json"

        _write_json(
            error_path,
            {
                "experiment_name": experiment_id,
                "run_status": "running",
                "started_at": _now_iso(),
                "updated_at": _now_iso(),
                "summary": {"total_errors": 0, "open_errors": 0, "resolved_errors": 0},
                "errors": [],
            },
        )
        _write_text(plan_path, _build_plan_text(task, environment.environment_name, datasets))
        _append_jsonl(
            activity_path,
            {
                "timestamp": _now_iso(),
                "step": "plan",
                "category": "plan",
                "action": "initialize_run",
                "status": "completed",
                "details": {"environment": environment.environment_name, "agent": getattr(agent, "agent_id", "unknown")},
            },
        )

        environment_result = environment.execute(task, task["user_prompt"], datasets, agent, run_dir)
        required = task["required_result_format"]
        result_payload = {
            "scientific_answer": _required_field_payload(
                required["scientific_answer"]["required_fields"],
                environment_result.outputs.get("scientific_answer", {}),
            ),
            "galaxy_execution": _required_field_payload(
                required["galaxy_execution"]["required_fields"],
                environment_result.outputs.get("galaxy_execution", {}),
            ),
        }
        _write_json(result_path, result_payload)
        _write_text(
            reproduce_path,
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    '"""Reproduction stub for benchmark run."""',
                    "",
                    f"print('Reproduce {experiment_id} in {environment.environment_name} with agent {getattr(agent, 'agent_id', 'unknown')}')",
                ]
            )
            + "\n",
        )

        if environment.environment_name == "galaxy":
            _write_json(
                run_dir / "results" / "galaxy_execution_stub.json",
                {"mode": "simulated", "galaxy_instance": task.get("execution_environment", {}).get("galaxy_instance")},
            )
        if environment.environment_name == "galaxy_skills":
            _write_json(run_dir / "results" / "skills_manifest.json", {"skills": ["procedural_guidance"]})

        reasoning_entries = [
            f"Loaded task {experiment_id} at level {level}.",
            f"Prepared {len(datasets)} dataset reference(s).",
            *environment_result.reasoning,
        ]
        _write_text(reasoning_path, _build_reasoning_text(reasoning_entries))

        for entry in environment_result.trace:
            _append_jsonl(
                activity_path,
                {
                    "timestamp": _now_iso(),
                    "step": entry.get("step", "execute"),
                    "category": "execute",
                    "action": entry.get("action", "environment_step"),
                    "status": "completed",
                    "details": entry,
                },
            )

        final_status = "completed" if environment_result.status == "success" else "completed_with_errors"
        _write_json(
            error_path,
            {
                "experiment_name": experiment_id,
                "run_status": final_status,
                "started_at": _now_iso(),
                "updated_at": _now_iso(),
                "summary": {
                    "total_errors": len(environment_result.failure_modes),
                    "open_errors": 0,
                    "resolved_errors": 0,
                },
                "errors": [
                    {"type": mode, "message": mode, "context": {"environment": environment.environment_name}}
                    for mode in environment_result.failure_modes
                ],
            },
        )

        component_scores = _component_scores(asdict(environment_result), environment.environment_name)
        performance_score = run_performance(component_scores)
        score_summary = self._score_if_available(run_dir, experiment_id, task["level"])
        execution_context = _collect_execution_context(task, environment, asdict(environment_result))
        run_record = RunRecord(
            run_id=run_dir.name,
            task_id=experiment_id,
            prompt_level=PromptLevel(prompt_level_from_specificity(task["level"])),
            environment=EnvironmentEnum(environment.environment_name),
            agent_id=getattr(agent, "agent_id", "unknown"),
            input_prompt=task["user_prompt"],
            status=RunStatus.SUCCESS if environment_result.status == "success" else RunStatus.PARTIAL,
            component_scores=component_scores,
            performance_score=performance_score,
            outputs=environment_result.outputs,
            artifacts=environment_result.artifacts,
            trace=environment_result.trace,
            timing=environment_result.timing,
            failure_modes=environment_result.failure_modes,
            score_summary=score_summary,
            execution_mode="simulated_harness",
            benchmark_validity=_benchmark_validity(environment),
            execution_context=execution_context,
        )
        _write_json(run_record_path, asdict(run_record))
        return run_dir

    def execute_matrix(
        self,
        *,
        tasks: list[dict[str, Any]],
        environments: list[EnvironmentRunner],
        agent_factory: callable,
        output_root: str | Path | None = None,
    ) -> list[Path]:
        run_dirs: list[Path] = []
        for task in tasks:
            for environment in environments:
                run_dirs.append(
                    self.execute_task(
                        task=task,
                        environment=environment,
                        agent=agent_factory(),
                        output_root=output_root,
                    )
                )
        return run_dirs

    def _score_if_available(self, run_dir: Path, experiment_id: str, level: str) -> dict[str, Any] | None:
        ground_truth_path = self.root_dir / "ground_truth" / f"{experiment_id}.json"
        if not ground_truth_path.exists():
            return None
        if str(self.root_dir) not in sys.path:
            sys.path.insert(0, str(self.root_dir))
        from tools import benchmark_scorer

        def score_value_to_dict(score_value: Any) -> dict[str, Any]:
            return {
                "value": score_value.value,
                "status": score_value.status,
                "applicability": score_value.applicability,
                "basis": score_value.basis,
                "matched_fields": score_value.matched_fields,
                "applicable_fields": score_value.applicable_fields,
                "notes": score_value.notes,
            }

        bundle = benchmark_scorer.build_bundle(run_dir, experiment_id, level)
        normalized_result = benchmark_scorer.normalize_result(bundle)
        entries = []
        entries.extend(benchmark_scorer.build_scientific_comparisons(normalized_result, bundle))
        entries.extend(benchmark_scorer.build_standard_comparisons(normalized_result, bundle))
        entries.extend(benchmark_scorer.build_galaxy_comparisons(normalized_result, bundle))
        summaries = {
            "scientific_solution_score": score_value_to_dict(
                benchmark_scorer.summarize_score(
                    "scientific_solution_score",
                    [entry for entry in entries if entry.score_name == "scientific_solution_score"],
                    bundle,
                )
            ),
            "standard_analysis_score": score_value_to_dict(
                benchmark_scorer.summarize_score(
                    "standard_analysis_score",
                    [entry for entry in entries if entry.score_name == "standard_analysis_score"],
                    bundle,
                )
            ),
            "galaxy_execution_score": score_value_to_dict(
                benchmark_scorer.summarize_score(
                    "galaxy_execution_score",
                    [entry for entry in entries if entry.score_name == "galaxy_execution_score"],
                    bundle,
                )
            ),
        }
        _write_json(run_dir / "results" / "score_summary.json", summaries)
        return summaries
