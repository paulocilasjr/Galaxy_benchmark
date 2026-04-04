"""Structured event logging ports."""

from __future__ import annotations

from typing import Protocol

from galaxy_benchmark.domain.models import ExecutionEvent


class EventLogPort(Protocol):
    """Contract for append-only execution and knowledge event logs."""

    def append_event(self, event: ExecutionEvent) -> None: ...

    def append_text(self, category: str, message: str) -> None: ...
