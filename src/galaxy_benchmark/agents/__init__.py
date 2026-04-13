"""Agent adapters for the benchmark workbench."""

from .base import AgentAdapter, AgentExecution
from .builtin import BUILTIN_AGENTS, EchoAgentAdapter, HeuristicAgentAdapter

__all__ = [
    "AgentAdapter",
    "AgentExecution",
    "BUILTIN_AGENTS",
    "EchoAgentAdapter",
    "HeuristicAgentAdapter",
]
