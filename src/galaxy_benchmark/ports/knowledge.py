"""Knowledge source ports."""

from __future__ import annotations

from typing import Protocol


class KnowledgeSourcePort(Protocol):
    """Search and retrieve benchmark-relevant knowledge records."""

    def search(self, query: str, *, task_family: str | None = None) -> list[dict]: ...

    def retrieve(self, identifier: str) -> dict: ...
