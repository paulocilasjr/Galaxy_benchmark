## 2026-03-19T22:20:08Z | plan
- Decision made: Adopt an artifact-first benchmark execution plan under the dedicated outputs run directory.
- Why this decision was made: README.md and SKILL.md require complete traceability, outputs-only writes, and a ground-truth gate after result generation.
- Next action: Validate credentials and record the workflow/server discovery evidence that determined the execution path.

## 2026-03-19T22:20:08Z | pre_run_discovery
- Decision made: Use the exact GTN workflow export from usegalaxy.eu, executed on usegalaxy.org after import.
- Why this decision was made: The exact workflow name 'Clustering 3k PBMC with Scanpy' is published on usegalaxy.eu and matches the GTN tutorial/Zenodo inputs. The current API key is valid on usegalaxy.org but not on usegalaxy.eu, so exporting the GTN workflow and importing it into usegalaxy.org preserves the workflow while keeping authenticated execution possible.
- Next action: Run attempt 1 with the imported GTN workflow, keeping a native usegalaxy.org published Scanpy workflow as the documented fallback if needed.

## 2026-03-19T22:24:14Z | workflow_selection_attempt_1
- Decision made: Attempt 1 selected workflow source gtn_export_import (21315ffd2df2f159).
- Why this decision was made: This is the exact GTN workflow backing the single-cell PBMC 3k training material and matches the experiment's three input files plus Louvain/UMAP/marker-gene outputs.
- Next action: Invoke the workflow with the three fetched Matrix Market inputs.

## 2026-03-19T22:24:17Z | attempt_failure_1
- Decision made: Attempt 1 failed with signature: RunError: Expected dataset 'pl_dotplot_marker_genes' was not found in terminal ok state.
- Why this decision was made: The failure evidence was captured from the exception context and Galaxy polling snapshot before any retry decision. Benchmark rules require a signature-specific fix rather than a blind retry.
- Next action: Switch workflow source for the next attempt if available; otherwise stop with a documented blocker.

