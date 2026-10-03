# Integrated manuscript in the original narrative layout

This package combines the user and workbench perspectives into one Analysis draft. The text and six main figures follow the requested sequence:

1. A paired benchmark of biomedical agents in Galaxy and open-ended code: design and analysis populations (Fig. 1).
2. Galaxy matches open-ended code: performance by benchmark (Fig. 2), repeatability and user-defined-tool use (Fig. 3).
3. Failures reflect insufficient verification more than missing knowledge: a census of every failing task, persistent versus sporadic failures and traced cases (Fig. 4).
4. Galaxy's token overhead is concentrated in addressable interface costs: model trade-offs and token ratios (Fig. 5), interface costs and failure modes, and the pending intervention study (Fig. 6).

`manuscript.md` is the editable source; numbers in `{{…}}` are filled from `numbers.json`, whose provenance is in `numbers_provenance.json`. `Galaxy_agents_original_layout_manuscript.docx` contains the manuscript and embedded figures. `figures/` contains vector PDFs and PNG previews. `Source_Data.xlsx` contains figure summaries, observations and a column dictionary; analysis tables and notes are in `analysis/`, scripts in `scripts/`. No private CompBioBench reference answer is disclosed.

`RESPONSES_TO_COMMENTS.md` answers the paragraph-level questions. `STYLE_AND_SCOPE.md` maps each requested assertion to the supported statement and lists outstanding work. `package_validation.json` records automated checks and pending author fields; `visual_validation.json` records the inspected renders. Passing local checks does not make the manuscript submission-ready.

## Placeholder status

**The token-reduction intervention is a placeholder until its results are confirmed and finalized.** The final paragraph of Results section 4 and Fig. 6f are labelled RESULTS PENDING, and `TOKEN_REDUCTION_PLACEHOLDER.md` records the planned design, the archived reference point (GPT-5.5 BixBench Galaxy/code ratio of total input, 2.82) and what is needed to replace the placeholder. No reduction percentage is reported.

## Rebuilding

Run `sh manuscript_narrative/original_layout/build_all.sh` from the repository root. Set `PYTHON` to an interpreter with the packages pinned in the parent `requirements.txt` (Python 3.12), `NODE_BINARY` to Node 24, and `NODE_PATH` to a `node_modules` containing `docx` 9.6.1 and `@oai/artifact-tool` 2.8.71 (the Codex runtime bundles both, together with a matching Node binary). The build reads only existing archive evidence and regenerates the analysis, figures, workbook, numbers and DOCX, then validates them. It contacts no Galaxy server and runs no benchmark agent. Exact installed versions and input hashes are recorded in `release_manifest.json`.

The package relies on the parent `narrative_common.py`, `references.json`, `author_metadata.json`, `requirements.txt` and `build_docx.js`. The four primary Codex configurations are included; Astra (no Galaxy arm) and the superseded harness are excluded from primary comparisons; IWC endpoints use the nine tasks with comparable scores.
