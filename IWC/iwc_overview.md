# IWC overview

This directory contains a retrospective, read-only evidence archive for the supplied IWC execution-link workbook. It preserves task-scoped traces, Galaxy history metadata and jobs, selected text outputs, recovered commands, and validated evidence JSON for later analysis.

## Inventory

The workbook contains **240 runs** across **10 tasks**, **4 models**, two execution conditions, and replicate labels 1, 2, 3. Each task has 24 observed rows.

| Model | Runs |
|---|---:|
| Codex + DeepSeek V4 Pro | 60 |
| GPT-5.5 | 60 |
| GPT-5.6 Luna | 60 |
| GPT-5.6 Sol | 60 |

| Condition | Runs |
|---|---:|
| galaxy | 120 |
| open_ended_code | 120 |

## Evidence

The archive contains **1352 distinct analytical creating jobs**. Source retrieval statuses, per-run links, hashes, outputs, skipped binary outputs, and metadata-only histories are recorded in [iwc_recovery_summary.json](iwc_recovery_summary.json). The full machine-readable aggregate index is [iwc_overview_audit.json](iwc_overview_audit.json).

No benchmark answer was regraded, no agent code was executed, and no hidden ground truth was opened.
