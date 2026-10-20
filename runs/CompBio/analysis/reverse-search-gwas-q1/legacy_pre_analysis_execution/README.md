# Reverse-search GWAS q1 audit

Start with [history_analysis.md](history_analysis.md). This mirrors the earlier BixBench analysis packages, with additional per-job ledgers for the larger histories.

- `reverse-search-gwas-q1.json`: original task prompt and input reference.
- `reverse.search.gwas.q1.tsv.gz`: local-only original benchmark source archive (151 MB), excluded from Git; `input_manifest.json` records its download URL and integrity hashes.
- `history_analysis.md`: model/replicate routes, inferred rationale, outcomes, code differences, input sharing and evidence limits.
- `history_analysis_evidence.json`: machine-readable dataset/job and output evidence.
- `verify_gwas_source.py`, `galaxy_job.json`: representative successful Sol replicate 2 source verification and its Galaxy job.
- `recovered_code/`: uploaded scripts, recorded custom commands, manifests and retrieved public job records.
- `job_ledgers/`: complete per-replicate job ledgers.
- `selected_outputs/`: selected inspected outputs; dataset links and hashes are in the evidence JSON.

Replicate numbering follows the supplied links in groups of three: GPT-5.5, GPT-5.6 Sol, Codex + DeepSeek-v4-pro-0813, Codex GPT-5.6 Luna. Model identity is user-supplied, not independently authenticated by Galaxy.

This is a read-only retrospective audit; no new analysis jobs or recovered scripts were executed. Large reference datasets are not all mirrored. The 151 MB input is ignored by Git. On another computer, download it from the URL in `input_manifest.json` and verify its SHA-256 checksum if the local source archive is needed.
