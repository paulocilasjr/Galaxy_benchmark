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

## Reproduction

From the repository root:

```sh
python3 IWC/build_iwc_overview.py
python3 IWC/solution_path_consistency_analysis.py
python3 analysis_execution/validate.py IWC/analysis/wf_001_short_read_qc_trim
```

The source collection used the read-only `analysis_execution` procedure with the supplied workbook. No agent code was rerun, no Galaxy jobs were submitted, and hidden ground truth was not opened. The source manifests record the environment's TLS limitation and all retained-byte hashes.
