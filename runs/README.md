# Immutable Run Artifacts

Each benchmark run should be written into a unique timestamped directory under `runs/`.

## Expected Contents

- `manifest.json`
- `input/`
- `plan/`
- `trace/`
- `reasoning/`
- `errors/`
- `results/`
- `artifacts/`

## Rules

- run directories are immutable once created
- logs are append-only
- corrections must create new versioned artifacts
- secrets must never be written into run artifacts

## Purpose

This directory is the evidence store for benchmark execution, not a working directory.

