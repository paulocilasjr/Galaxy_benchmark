# IWC retrospective execution archive

This directory contains the locally retained evidence for the IWC execution-condition workbook. It is organized like the `CompBio` and `BixBench_50` archives: one validated package per task under `analysis/`, plus aggregate overview, recovery, results, and solution-path artifacts.

## Contents

- `iwc_execution_condition_links.xlsx`: supplied run-link inventory, preserved unchanged.
- `analysis/<task>/`: source snapshots, run inventories, recovered code, selected outputs, job ledgers, evidence JSON, and task report.
- `iwc_overview_audit.json`: machine-readable inventory and aggregate index for every run.
- `iwc_overview.md`: concise overview of coverage and evidence.
- `iwc_recovery_summary.json` and `iwc_recovery_summary.md`: retrieval status, jobs, outputs, and explicit limitations.
- `result_section_iwc.md`: results-evidence draft for later scientific analysis.
- `solution_path_consistency_analysis.py` and `solution_path_consistency_results.json`: descriptive replicate-route fingerprints.
- `audit_iwc_results.py` and `iwc_scientific_audit.json`: the scientific audit (per-run scores, token use, budgets and run roots). This is the IWC evidence that `BixBench50_CompBio_analysis/analysis.json`, `manuscript_material/` and `manuscript_narrative/` use.
- `iwc_sensitivity_analysis.py` and `iwc_sensitivity_results.json`: shape, leave-one-task-out and catastrophic-run sensitivity analyses of the output-agreement endpoint, read from `iwc_scientific_audit.json`.

## Reproduction

From the repository root, the manuscript evidence is rebuilt with:

```sh
python3 IWC/audit_iwc_results.py
python3 IWC/iwc_sensitivity_analysis.py
python3 analysis_execution/validate.py IWC/analysis/wf_001_short_read_qc_trim
```

`IWC/build_iwc_overview.py` is the earlier overview generator. It still rebuilds `iwc_overview.md`, `iwc_recovery_summary.*` and `result_section_iwc.md`, but those files predate the scientific audit and are not used by the manuscripts; prefer `iwc_scientific_audit.json` for any number. `IWC/solution_path_consistency_analysis.py` rebuilds the route fingerprints.

Two caveats apply to the output-agreement score. For `wf_006_atacseq_chromatin_accessibility`, some route references were calibrated from agent runs, and each run's evaluation record flags this. The RNA-seq composite does not include the set of significant genes. `manuscript_narrative/` reports both as sensitivity analyses and score components.

The source collection used the read-only `analysis_execution` procedure with the supplied workbook. No agent code was rerun, no Galaxy jobs were submitted, and hidden ground truth was not opened. The source manifests record the environment's TLS limitation and all retained-byte hashes.
