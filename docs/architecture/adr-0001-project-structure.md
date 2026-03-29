# ADR 0001: Project Structure

## Status

Proposed

## Context

The current repository is organized around legacy benchmark inputs and run outputs. The rebuild needs a structure that supports reusable benchmark logic, typed models, and clean separation between domain, application, ports, infrastructure, and interfaces.

## Decision

Adopt a Hexagonal / Clean Architecture layout with a canonical `benchmark/` namespace for tasks, prompts, and ground truth, and keep `runs/` as the immutable output area for each trial.

## Consequences

- domain logic remains independent of Galaxy SDKs and CLI concerns
- adapters can be replaced without changing core benchmark policy
- legacy benchmark files can be migrated instead of rewritten

