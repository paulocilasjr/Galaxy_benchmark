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
- migration is completed before assets land on this branch
- execution logic moves behind ports and use cases

## Branch State

- this rebuild branch contains only canonical benchmark assets
- original experiment and result folders are not carried forward
- `benchmark/datasets/local/` holds the benchmark-local datasets used by the canonical tasks

## Migration Stages

1. extract source benchmark definitions outside the rebuild branch
2. convert legacy experiments into canonical task snapshots
3. normalize output field names and schemas
4. align migrated tasks to the benchmark pillars and task-family taxonomy
5. write flat canonical tasks and ground truths
6. validate benchmark assets and generate prompt variants from the canonical model

## Canonical Naming

The migration should normalize field names such as `roc-auc` and `ROC-AUC` to `roc_auc` in canonical schemas and reports.
