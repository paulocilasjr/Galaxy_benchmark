---
name: transcriptomics
description: Use for RNA-seq or miRNA differential expression, design and contrast semantics, shrinkage, target-gene extraction, gene annotation, ORA, GSEA, and pathway enrichment. Do not use for simple summaries or correlations over an already prepared expression matrix.
---

# Transcriptomics

Preserve the requested method, contrast, identifiers, enrichment source, and
statistical population. These are parts of the estimand, not interchangeable
output formats.

## Differential Expression

- Match count-matrix sample IDs to metadata before fitting. Confirm the design
  formula, covariates, reference and target levels, and contrast direction.
- Use raw counts for count-model methods unless the named method specifies a
  different input. Do not treat normalized or transformed abundance as counts.
- Use the matched experimental control. Do not replace a vehicle, batch-matched,
  or paired control with another baseline unless the task defines that contrast.
- Preserve sample and gene identifiers through reshaping. Resolve duplicate IDs
  rather than silently collapsing them.
- Do not add a manual gene prefilter merely to reduce the table unless the task
  or named method defines it. In DESeq2, prefiltering changes the population
  available to independent filtering and multiple-testing adjustment.
- Apply a filter only after the statistic it references exists. For example, a
  shrunken-effect filter cannot be applied to an unshrunk coefficient.
- Match the measurement scale to the method. Continuous Ct, intensity, or
  normalized abundance does not automatically satisfy count-model assumptions.

For DESeq2, `results(alpha=...)` sets the target used to optimize independent
filtering; it is not merely a final `padj` display cutoff and can change adjusted
p-values and which rows are `NA`. For a fresh analysis, match `alpha` to the
intended FDR threshold. When reproducing a documented result table, preserve
its documented `results()` settings or defaults, then apply any requested row
filter to that table. Treat unspecified source settings as method ambiguity if
the alternatives change the requested quantity.

Separate significance testing from LFC shrinkage. In current DESeq2 workflows,
`lfcShrink()` replaces effect-size and uncertainty columns while preserving the
`pvalue` and `padj` values supplied by `results()`, unless options such as an LFC
threshold or s-values explicitly change the inferential target. If the requested
quantity only counts adjusted-p-value rows, preserve the fitted model and
`results()` configuration; do not create a second significance route solely to
apply a named shrinkage estimator.

When extracting a count from a result table, determine header presence and
column meaning from the file plus dataset schema or metadata. Some tabular
outputs store column names only in metadata. Do not discard the first data row
by unconditionally treating it as a header.

## Target-Gene Results

For a requested gene value, use the same fitted model, contrast, covariates,
reference level, coefficient, and shrinkage method named by the task. Inspect
fitted result names when software sanitizes factor labels. A target fitted value
is not removed merely because a later foreground or significance filter excludes
that gene, unless the task asks specifically for a filtered result.

## Enrichment Setup

Define before ORA or GSEA:

- foreground or ranked-list rule, including direction and thresholds;
- eligible universe/background for ORA;
- organism, identifier type, mapping source, pathway library and version;
- test, adjustment method, adjustment family, and significance threshold; and
- requested output field, sorting key, top-N rule, and stable pathway identifier.

Use one homogeneous identifier namespace for each enrichment run. After
mapping, do not mix mapped identifiers with unmapped source identifiers in the
same foreground or universe. Either drop and count unmapped identifiers, or use
the source namespace uniformly when the selected library and tool document that
they support it. Apply the same mapping policy to foreground and background.

Foreground and universe are different populations. A DE significance or effect
threshold may define the foreground while the universe remains all mapped genes
eligible after upstream experiment-level filtering. Do not narrow the universe
with a foreground-only threshold unless the named method requires it.

Use the multiple-testing family defined by the named implementation. For a
clusterProfiler-style ORA, correction is applied to the tested result terms
remaining after mapping and gene-set-size filtering; do not silently add
zero-hit pathways to that family. Do not compare adjusted values produced from
different families as if they were equivalent.

When the task asks for pathways enriched in the same direction across
contrasts, run the requested enrichment separately for each contrast and sign
with a shared eligible universe and method settings, then intersect significant
stable pathway IDs within each sign. Intersecting DE genes first answers a
different question. Do this directional branching only when the requested
quantity is direction-specific pathway enrichment.

For a top-term question, sort by the named tool's requested or documented
ordering, select the requested rank window with explicit tie handling, and only
then apply the term-name, ID, or category test. Do not replace a top-N quantity
with a count over all significant terms.

## Odds Ratios And Source Stability

- Define the ORA contingency table from foreground membership and the eligible
  universe before accepting an odds ratio.
- Library snapshots and services can differ in membership, mapping, background,
  hypothesis family, and odds-ratio definition. Use the source and version
  requested by the task; results from another service are not automatically
  equivalent.
- Prefer stable pathway IDs for intersections and comparisons. Use names only
  when IDs are unavailable and the match is unambiguous.

Before finalizing, verify the actual contrast, target field or foreground,
universe, mapping, library, adjustment family, and final extraction rule.
