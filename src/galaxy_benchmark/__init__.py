"""Galaxy Benchmark support package."""

__version__ = "0.1.0"

from .application.reporting import build_benchmark_report
from .application.orchestrator import BenchmarkWorkbench
from .application.publication import build_reliability_report, build_release_audit
from .application.scoring import (
    adaptability,
    aggregate_by_environment,
    aggregate_prompt_scores,
    run_performance,
    task_robustness,
    user_level_confidence,
)
from .application.validation import validate_prompt_payload, validate_run_payload, validate_task_payload

__all__ = [
    "adaptability",
    "aggregate_by_environment",
    "aggregate_prompt_scores",
    "BenchmarkWorkbench",
    "build_benchmark_report",
    "build_reliability_report",
    "build_release_audit",
    "run_performance",
    "task_robustness",
    "user_level_confidence",
    "validate_prompt_payload",
    "validate_run_payload",
    "validate_task_payload",
]
