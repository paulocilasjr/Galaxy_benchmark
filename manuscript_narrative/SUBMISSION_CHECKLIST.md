# Submission decisions and remaining evidence

The two packages are retrospective Analysis drafts. Artifact validation does not establish scientific validity, independent replay or completed human review. No new scientific runs, Galaxy calls or external messages were performed during this reassessment.

## Answers to the requested decisions

**CompBioBench reference publication.** Maintainer approval is not confirmed. The official public dataset card identifies CC BY 4.0 licensing for questions, metadata and input files; it does not establish authorization to disclose private grader answers. See [the dataset card](https://huggingface.co/datasets/Genentech/compbiobench-data-v1/blob/main/README.md) and [the versioned dataset record](https://zenodo.org/records/19443186). Prior inclusion in a local audit is not a maintainer approval. The exact encode-atac-pipeline-q1 reference was removed from manuscript figures and Source Data. Preserve the mechanism using execution and benchmark-agreement categories. Do not restore the reference without a documented release decision. No maintainer was contacted.

**Author information and disclosures.** `author_metadata.json` lists the exact fields that need confirmed values. The builder substitutes supplied strings and leaves null fields highlighted. It does not invent authors, affiliations, funding, competing interests, release identifiers or completed review. Human verification remains explicitly pending. The archived UDT-audit README documents six Claude subagents and one reviewer per run; it does not establish human adjudication or an exact assistant-model snapshot. This reassessment used Codex desktop; exact served model identifiers were not independently recorded.

**Prospective work.** The supplementary protocols now include a third pinned-code arm, independent references, assigned-attempt replay denominators, weighted expert sampling, power targets, multiplicity, explicit registration gates and intervention mutation controls. Registration inputs and actual experiments remain unfinished. Protocols cannot close an empirical evidence gap.

**Visual review.** The four DOCX files can be rendered with the bundled document runtime, without installing desktop LibreOffice. The shared builder now constrains figures to the text width, uses black heading styles, removes the heading-only figure page and suppresses line numbering in the footer. Native figure PDFs remain 180 mm wide. Final render results are recorded in the reassessment report.

## Author and release gate

- Confirm authors, order, affiliations, corresponding author and contributions.
- Supply companion-manuscript wording or a real public citation; an unpublished companion does not receive an invented DOI.
- Disclose the shared archive and overlapping analyses to editors, supply the companion manuscript, and explain the independent contribution of each paper.
- Supply the actual archive identifier, repository URL and immutable release identifiers for this study. Benchmark input-data DOIs are not substitutes for the study release.
- Document human review: reviewer identities/roles, cases assessed, blinding, independence, confidence, disagreements and resolution. Do not mark the attestation complete until records exist.
- Provide AI tool/provider/model/version/date information for each phase when available; retain explicit unknowns.
- Confirm funding, acknowledgements, competing interests and responsibility statements.
- Establish evaluator-material access and reference-publication conditions. The public build reuses archived CompBioBench grades; it does not independently reproduce private-key grading.

Run `scripts/validate_package.py --submission` after supplying these facts. A failing submission gate is expected until confirmed fields and attestations are present. Default artifact validation can pass while submission remains pending.

## Scientific evidence gate

- Independently validate the reconstructed CompBioBench key and prepare IWC references without calibration from the evaluated agent runs.
- Perform independent clean-environment replay and human scientific/usability assessment.
- Freeze exact model/harness/interface versions, task/input/reference hashes, budgets, retry rules and analysis code for a prospective comparison.
- Choose held-out task counts and replication from a power calculation; justify any non-inferiority margin before observing new results.
- Execute intervention and conformance studies, including positive, negative and mutation controls.
- Use a second Galaxy deployment for installation robustness; implement the contract on another workbench before claiming platform transfer.

These requirements affect the strength of the claims. The current drafts support conditional archive findings and testable requirements; they do not establish Galaxy superiority or a validated portable contract.
