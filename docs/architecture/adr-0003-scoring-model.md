# ADR 0003: Scoring Model

## Status

Proposed

## Context

The benchmark needs to evaluate not only final correctness but also process quality and robustness.

## Decision

Use a three-part scoring model: outcome, process, and robustness, with a deterministic aggregator.

## Consequences

- correctness and execution quality can be analyzed separately
- repeated runs can be compared across prompt tiers and access modes
- scoring remains side-effect free and reproducible

