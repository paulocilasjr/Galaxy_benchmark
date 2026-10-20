#!/usr/bin/env python3
"""Model-facing Galaxy execution tools that block until a final outcome."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

try:
    import galaxy_execute_mcp_core as _core
except ImportError:  # Source-tree execution and unit tests.
    import galaxy_execute_mcp as _core

search_galaxy_tools = _core.search_galaxy_tools
inspect_galaxy_history = _core.inspect_galaxy_history
inspect_archive_inventory = _core.inspect_archive_inventory


def run_galaxy_tool_and_wait(
    history_id: str,
    tool_id: str,
    tool_inputs: dict[str, Any],
    input_format: Literal["auto", "21.01", "legacy"] = "auto",
    validate_before_submit: bool = True,
) -> dict[str, Any]:
    """Submit once and wait. Full results are saved; do not resubmit to reread them."""

    result = _core.run_galaxy_tool_and_wait(
        history_id=history_id,
        tool_id=tool_id,
        tool_inputs=tool_inputs,
        input_format=input_format,
        validate_before_submit=validate_before_submit,
    )
    return _core.compact_execution_reply(
        result, history_id=history_id,
        workspace_root=Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace")),
    )


def run_galaxy_udt_and_wait(
    history_id: str,
    representation: dict[str, Any],
    tool_inputs: dict[str, Any],
    input_format: Literal["auto", "21.01", "legacy"] = "auto",
    workspace_inputs: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Stage optional workspace inputs, submit one UDT, and block until terminal state."""

    result = _core.run_galaxy_udt_and_wait(
        history_id=history_id,
        representation=representation,
        tool_inputs=tool_inputs,
        workspace_inputs=workspace_inputs,
        input_format=input_format,
    )
    return _core.compact_execution_reply(
        result, history_id=history_id,
        workspace_root=Path(os.environ.get("GALAXY_AGENT_WORKSPACE_ROOT", "/workspace")),
    )


def serve() -> None:
    from mcp.server.fastmcp import FastMCP

    server = FastMCP("galaxy-execute")
    server.tool(name="search_galaxy_tools")(_core.search_galaxy_tools)
    server.tool(name="inspect_galaxy_history")(_core.inspect_galaxy_history)
    server.tool(name="inspect_archive_inventory")(_core.inspect_archive_inventory)
    server.tool(name="inspect_galaxy_tool")(_core.inspect_galaxy_tool)
    server.tool(name="run_galaxy_tool_and_wait")(run_galaxy_tool_and_wait)
    server.tool(name="run_galaxy_udt_and_wait")(run_galaxy_udt_and_wait)
    server.run(transport="stdio")


if __name__ == "__main__":
    serve()
