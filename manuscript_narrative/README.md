# Narrative manuscripts

This folder holds two retrospective Nature Methods Analysis drafts built from the same archive of 4,240 agent runs (BixBench-Verified-50, CompBioBench, IWC). Each paper asks its own question and has its own figures, Source Data and supplementary material. The 2 October 2026 reassessment corrects additional classification and voting issues. Archive-based corrections are implemented; independent reference validation, human review, new runs and intervention/transfer evidence remain open. Protocols specify future work and are not results.

| Folder | Manuscript | Question |
|---|---|---|
| `user-oriented/` | *Execution environments shape the reliability of biomedical AI agents* (`Galaxy_agents_user_oriented_manuscript.docx`) | For a user, does the assigned execution arm (open-ended code or Galaxy) change benchmark accuracy, the repeatability of scored outcomes, the evidence left for review and the cost of a run? |
| `galaxy-oriented/` | *Measuring agent readiness in scientific workbenches through Galaxy* (`Galaxy_agents_workbench_oriented_manuscript.docx`) | What must a workbench expose so that an agent's intended analysis is faithfully executed, diagnosably recoverable and attributable? |

Each paper folder contains:

- `manuscript.md`: the editable source. Numbers appear as `{{key}}` and are filled from `numbers.json` when the .docx is built.
- `numbers.json` and `numbers_provenance.json`: the build-time estimates and counts, and the figure function that computed them.
- The .docx: abstract, main text, references, legends, Methods, Methods references, Extended Data legends, statements and embedded figures.
- `figures/`: `Fig1–6` and `ED_Fig1–4` (user) or `ED_Fig1–3` (Galaxy) as vector PDFs (180 mm wide, editable text) with 300-dpi PNG previews.
- `source_data/`: one workbook per figure, with a README sheet, one sheet per panel and a column dictionary.
- `supplementary/`:
  - `Supplementary_Tables.xlsx` (Tables 1–5, including the provenance of every number);
  - Supplementary Note 1, a protocol for prospective validation (user) or for interventions and conformance tests (Galaxy), as .md and .docx;
  - `Reporting_Summary_notes.md`, draft answers for the Nature Portfolio form.
- `scripts/make_figures.py`: figures, Source Data and numbers.

Shared files:

- `narrative_common.py`: data access, cluster bootstrap, figure and Source Data helpers. It reuses `manuscript_material/scripts/style.py`.
- `references.json`: cited as `[@key]`. Entries were checked against Crossref, PubMed, arXiv or bioRxiv on 2 October 2026 (`references_verification.json`).
- `build_docx.js` and `scripts/make_supplement.py`.
- `journal_requirements.md`: Nature Methods rules for Analysis articles, quoted from the journal's pages.
- `derived/`: read-only extractions from the archive. `galaxy_calls/` is the per-call table of Galaxy-interface activity; `design/` records the design differences between arms.

## Rebuilding

From the repository root:

```bash
python3.12 -m venv .venv-narrative && .venv-narrative/bin/pip install -r manuscript_narrative/requirements.txt
(cd manuscript_narrative && npm install)
PYTHON=.venv-narrative/bin/python sh manuscript_narrative/build_all.sh
```

`build_all.sh` regenerates every figure, Source Data workbook, `numbers.json`, the Supplementary Tables and the four .docx files. It takes about 30 s. The tables under `derived/` are archived outputs. Their extraction scripts (`derived/galaxy_calls/extract_calls.py`, `derived/design/extract_design.py`) need the raw run snapshots and are not re-run by the build.

## Data and conventions

- **Inputs.** Only archived evidence already in this repository: `BixBench50_CompBio_analysis/analysis.json`, `manuscript_material/source_data/figure_data.json` and `derived/run_summaries.jsonl.gz`, the on-demand Source Data in `manuscript_material/on_demand/`, `IWC/iwc_scientific_audit.json` and the per-run IWC evaluation records, the archived trace-friction ledger and `individual_error_analysis.md`. No agent code is run, no Galaxy server is contacted and nothing under `ground_truth/` is read.
- **CompBioBench grades.** Grades against the reconstructed key are read from `Source_Data_OD_Fig4.xlsx`. The key itself (54 score-inferred and 46 score-predicted items; private repository, commit `bdc00429f559`) is kept outside this repository so that agents run from here cannot read it. Regenerating grades needs authorized evaluator access. Explicit CompBioBench answers are withheld from manuscript figures and Source Data pending release authorization; public input-data licensing does not establish authorization for private grader answers.
- **Populations.** The primary paired population is the four Codex model configurations (3,840 runs; 3,816 in endpoint analyses, using nine IWC tasks). The superseded Claude Code harness (300 runs) is reported separately, and GPT-6 Astra (100 runs) is unpaired and excluded.
- **Statistics.** Intervals are 95% percentile cluster-bootstrap intervals with 20,000 resamples. Clusters are source capsules for BixBench-Verified-50 and tasks otherwise. Archived BixBench-Verified-50 and IWC accuracy intervals use seed 20260922; all new intervals use seed 20261002. Values are rounded half away from zero.
- **Majority vote.** Retrospective, outcome-blind grouping: rule A uses ten significant digits and rule B uses three; percentage units are retained. Select the earliest-replicate submitted answer in the majority group and reuse its archived grade. This is not independent regrading of a normalized answer. Member-grade disagreements and no-consensus cases are reported; the oracle is a reference statistic only.
- **Figures.** Colour and order follow `manuscript_material/`: open-ended code first, in vermillion squares; Galaxy in blue circles (Okabe–Ito).
- **Author input.** Confirmed values can be supplied in `author_metadata.json`; the DOCX builder substitutes them, while unconfirmed fields remain highlighted. Authorship, human review, release identifiers and disclosures cannot be inferred from the archive. `SUBMISSION_CHECKLIST.md` records the decisions that remain open.

## Validation and release status

See `REASSESSMENT_2026-10-02.md` for the post-revision review and `SUBMISSION_CHECKLIST.md` for remaining author, release and scientific decisions.

The build runs `scripts/validate_package.py`, checking number/citation resolution, independent call-count invariants, XML structure, figure sizes and Source Data documentation. It writes `package_validation.json` and `release_manifest.json` with SHA-256 input/artifact hashes and actual runtime versions. These checks establish artifact consistency, not biological correctness or scientific replay.

```sh
PYTHON=.venv-narrative/bin/python sh manuscript_narrative/build_all.sh
.venv-narrative/bin/python manuscript_narrative/scripts/validate_package.py --submission
```

The submission check intentionally fails while required author fields or attestations remain unresolved. DOCX pages must also be rendered and visually reviewed after layout changes; XML checks alone do not validate appearance. `NODE_BINARY` may select a Node executable, and `NODE_PATH` may select the documented bundled package directory.

## Review packets and conformance fixtures

- `user-oriented/review/`: generator for blinded expert-review and audit-verification packets (Supplementary Note 1, section 4). Packets reveal benchmark references, so they are written outside the repository (default `../Galaxy_benchmark_review_packets/user_oriented/`); only the answer-free sampling design and a hash manifest are kept here. No review has been performed.
- `galaxy-oriented/conformance/`: 33 conformance fixtures for requirements R1–R6, with a scorer and a mutation self-test that `build_all.sh` runs (Supplementary Note 1, section 3). The suite has not been run against any deployment.

## What is not done here

The review's steps 3 and 4 need new agent runs, human experts or a second Galaxy deployment. They are specified, not reported:

- `user-oriented/supplementary/Supplementary_Note_1_prospective_validation.md`: matched-arm rerun, independent replay and blinded expert review;
- `galaxy-oriented/supplementary/Supplementary_Note_1_interventions_and_conformance.md`: interventions, conformance suite and second deployment.
