"""Galaxy access port."""

from __future__ import annotations

from typing import Any, Protocol


class GalaxyPort(Protocol):
    """Contract for Galaxy operations behind adapters."""

    def create_history(self, history_name: str) -> str: ...

    def upload_file(self, history_id: str, path_or_url: str, name: str) -> str: ...

    def run_tool(self, history_id: str, tool_id: str, inputs: dict[str, Any]) -> dict[str, Any]: ...

    def run_workflow(
        self,
        history_id: str,
        workflow_id: str,
        inputs: dict[str, Any],
    ) -> dict[str, Any]: ...

    def poll(self, identifier: str) -> dict[str, Any]: ...
