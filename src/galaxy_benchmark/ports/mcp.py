"""MCP integration port."""

from __future__ import annotations

from typing import Any, Protocol


class MCPPort(Protocol):
    """Contract for MCP-exposed tools and resources."""

    def list_resources(self) -> list[dict[str, Any]]: ...

    def invoke(self, name: str, payload: dict[str, Any]) -> dict[str, Any]: ...
