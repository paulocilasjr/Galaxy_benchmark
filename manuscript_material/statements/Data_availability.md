# Data availability

All agent run traces, evaluator records and Galaxy history snapshots analysed in this study are publicly available from the Hugging Face dataset goeckslab/galaxy-agent-benchmark-run-traces (https://huggingface.co/datasets/goeckslab/galaxy-agent-benchmark-run-traces; revision main, retrieved 20–23 September 2026). Every retrieved file is recorded with its original SHA-256 hash in the per-task snapshot manifests of the analysis repository. [Authors: before submission, replace "revision main" with a fixed commit hash or a DOI-minted release, so that the archive cannot change after publication.]

Source Data are provided with this paper for Figs. 1–5 and Extended Data Figs. 1–5 (one Excel workbook per figure, one sheet per panel).

Supplementary Tables 1–67 and Supplementary Data 1–3 contain:
- the per-run summaries of all 4,240 runs;
- all 7,389 failed Galaxy MCP calls, with their failure class, error text and arguments;
- 2,085 detected parameter substitutions;
- the adjudication ledger for all 254 audited failures.

Reference answers of the benchmark tasks are omitted from the Supplementary Data to limit benchmark contamination; they remain available in the evaluator records of the source archive.

Benchmarks:
- BixBench-Verified-50 [ref];
- CompBioBench [ref];
- the Intergalactic Workflow Commission (IWC) collection of curated Galaxy workflows (https://iwc.galaxyproject.org) [ref].

All Galaxy jobs ran on the public usegalaxy.org server.

The independent mitogenome comparison used the *Agrius convolvuli* mitochondrial genome, accession OZ203683.1 (INSDC).
