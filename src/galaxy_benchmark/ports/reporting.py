"""Reporting and export ports."""

from __future__ import annotations

from typing import Protocol

from galaxy_benchmark.domain.models import EvaluationResult, ScoreCard


class ReportingPort(Protocol):
    """Contract for report generation and export surfaces."""

    def render_run_report(self, evaluation: EvaluationResult) -> str: ...

    def render_score_summary(self, scorecard: ScoreCard) -> str: ...
