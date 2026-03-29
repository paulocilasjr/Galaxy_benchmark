# ADR 0002: Task Schema

## Status

Proposed

## Context

Legacy experiment files mix task description, dataset references, tool hints, and output expectations in one loose schema.

## Decision

Define a canonical typed task schema for the benchmark platform and treat legacy experiments as migration inputs only.

## Consequences

- tasks can be validated before execution
- prompt generation and scoring can rely on stable fields
- migration becomes explicit and testable

