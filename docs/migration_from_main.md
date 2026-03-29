# Migration From Main

## Intent

This document describes how the existing benchmark repository is migrated into the rebuilt platform without losing the current benchmark ideas or artifact conventions.

## What Is Preserved

- strict traceability
- immutable run directories
- structured run artifacts
- explicit failure recovery
- comparison against ground truth only after result generation

## What Changes

- canonical task definitions replace flat experiment files
- normalized field names replace mixed naming conventions
- legacy inputs become fixtures behind a migration layer
- execution logic moves behind ports and use cases

## Legacy Sources

- `benchmark/tasks/legacy/raw/*.json`
- `benchmark/ground_truth/legacy/raw/*.json`
- `benchmark/datasets/local/` for benchmark-local datasets migrated into the new layout

## Migration Stages

1. copy and preserve legacy fixtures
2. convert legacy experiments into canonical task snapshots
3. normalize output field names and schemas
4. align migrated tasks to the benchmark pillars and task-family taxonomy
5. validate migrated tasks and ground truths
6. generate docs, prompt variants, and run artifacts from the canonical model

## Canonical Naming

The migration should normalize field names such as `roc-auc` and `ROC-AUC` to `roc_auc` in canonical schemas and reports.
