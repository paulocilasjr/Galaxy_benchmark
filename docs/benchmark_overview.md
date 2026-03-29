# Benchmark Overview

## Identity

`GalaxyAgentBench` evaluates agents in Galaxy across three benchmark pillars:

- platform-operation capability
- prompt robustness and trust
- ecosystem knowledge use

## Core Claim

The benchmark measures whether an agent can use Galaxy the way a competent scientist would:

- select the right tool or workflow
- bind inputs correctly
- choose and justify parameters
- poll and recover correctly
- use GTN, IWC, and Galaxy metadata when appropriate
- leave a reproducible provenance trail

## Why Galaxy

Galaxy is a strong benchmark environment because it combines:

- histories and dataset state
- reusable workflows
- tool metadata and parameter structure
- first-class provenance
- community knowledge systems such as GTN and IWC

## What Gets Measured

- outcome correctness
- process correctness
- robustness across prompt, access, and repeated-run conditions
- explicit failure mode attribution

## Repository Layers

- `benchmark/tasks/`: typed tasks and legacy migrated fixtures
- `benchmark/ground_truth/`: outcome gold, process gold, and failure expectations
- `benchmark/prompts/`: templates and generated variants
- `benchmark/suites/`: suite manifests and v1 planning structure
- `runs/`: immutable execution outputs
- `docs/`: benchmark framing, methodology, and ADRs
