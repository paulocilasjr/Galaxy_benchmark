# ADR 0005: Galaxy Access Modes

## Status

Proposed

## Context

The benchmark must compare multiple Galaxy access patterns, including API-driven, browser-based, MCP-enabled, and hybrid modes.

## Decision

Model Galaxy access as a port with multiple adapters rather than as a special case inside the benchmark runner.

## Consequences

- access modes are configurable per run
- polling, provenance, and result extraction remain consistent across implementations
- experimental access modes can be added without changing task schemas

