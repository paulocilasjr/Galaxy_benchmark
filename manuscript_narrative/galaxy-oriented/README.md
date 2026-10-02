# Galaxy-oriented Analysis package

This retrospective Analysis asks what information and guarantees a scientific workbench must expose so that an agent's intended analysis can be executed, diagnosed and attributed. It describes archived interface deployments on usegalaxy.org in July–September 2026. It does not claim validated interventions, independent biological adjudication or portability to another platform.

## Decisions resolved in the re-evaluation

- **What is the contribution?** A trace-indexed operational baseline, parameter-check coverage and a set of testable execution requirements. The intervention protocol is a prospective supplement, not a completed experiment.
- **Is one adapter version established?** No. Interface commit coverage is incomplete; deployment, server, wrapper/container, harness and model layers must remain separate.
- **What counts as a failed call?** The existing exception/job-failure rule plus transport-level failures omitted by that rule, scoped to Galaxy tool namespaces. The 604 additional exceptions are not all adapter rejections: examples include Galaxy HTTP responses. Mismatch-only statuses are a separate endpoint.
- **Does ok establish semantic fidelity?** No. Parameter checks cover explicit requested non-dataset parameters. There are 1,140 ok calls with no such parameters to compare and three additional ok calls with non-comparable parameter provenance. Dataset identity, defaults, software version and output interpretation need separate assessment.
- **How are mismatch counts reconciled?** The six plotted outcome classes are exclusive. Independently recorded parameter mismatch flags identify 4,999 calls, including 251 with failed status; dataset-input mismatch flags identify 213 calls. Their union is 5,065. Source Data includes overlaps and call-level coverage.
- **Is recovery scientifically validated?** No. Later ok within a tool family and final benchmark acceptance are separate outcomes. Non-ok episodes include caught mismatches and timeouts; they do not establish a linked repair or retention of the same scientific goal. User-defined tools are grouped as one family.
- **Are absent diagnostics verified from complete payloads?** No. The current measure screens the extracted 240-character error excerpt. It is an indicator of diagnostic visibility and may miss later or differently formatted diagnostics.
- **Can a missing local-program indicator attest execution location?** No. Shell screening has false positives and false negatives. Galaxy API submission still creates Galaxy provenance, while bypassing adapter validation; API reads do not establish computation location.
- **Can a private reference answer be published?** Permission is not established in this package. The explicit CompBioBench ATAC reference answer has been removed from the main mechanism figure. The historical filename/extension failure remains supported without publishing that answer.

## Package and reproduction

`manuscript.md` is the editable source; `numbers.json` and `numbers_provenance.json` are generated. The main and Extended Data figures are vector PDFs, with PNG previews and per-figure Source Data workbooks. The Source Data contains plotted observations, cell eligibility, call-level parameter coverage and mismatch overlaps.

From the repository root, use the pinned environment documented in `../requirements.txt`:

```sh
python manuscript_narrative/galaxy-oriented/scripts/make_figures.py
```

The shared `../build_all.sh` also builds supplements and DOCX files. Full figure builds replace the generated number files; targeted builds merge only their generated keys.

Figure generation uses frozen derived records. Re-extracting the archive requires raw snapshots; regenerating reconstructed CompBioBench item grades requires evaluator material whose public release has not been established. This distinction must remain explicit in release documentation.

## Remaining evidence requirements

Independent domain review, full-payload diagnostic validation, same-goal failure/repair linkage, complete computation-location audit, systematic version-metadata coverage, interface-commit reconstruction, held-out intervention trials and cross-deployment or cross-platform replication are not established by this archive. Supplementary Note 1 specifies prospective work; it must not be cited as a result. Authorship, funding, competing interests, stable archive/code identifiers and evaluator-material permissions require author or maintainer facts.
