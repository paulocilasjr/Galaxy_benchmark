# ADR 0004: Agent Abstraction

## Status

Proposed

## Context

The benchmark must compare different providers and agent styles without binding the core platform to a single model SDK.

## Decision

Expose agent execution through an `AgentPort` and keep provider-specific code in infrastructure adapters.

## Consequences

- OpenAI, Claude, scripted, and mock agents can share the same benchmark flow
- provider traces can be captured without leaking provider details into domain logic

