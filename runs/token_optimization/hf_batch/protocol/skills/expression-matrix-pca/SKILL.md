---
name: expression-matrix-pca
description: Use for PCA and explained-variance summaries on expression-like matrices when observation identity, sample/feature orientation, transform state, duplicate handling, centering/scaling, missingness, or variance extraction can change the result.
---

# Expression Matrix PCA

Define the observation unit, fitted matrix, preprocessing, and requested PCA
quantity before accepting a result.

**Required pre-fit gate:** When primary labels repeat and companion metadata is
available, inspect every metadata row in every repeated-ID group for an
explicit secondary identity and conflicts in plausible invariant attributes
before deciding the fitted observations or computing PCA. Matching counts or
multiplicities cannot substitute for this inspection. A numeric sample-level
result produced without completing this gate is invalid.

## Resolve Observation Identity

A matrix row or column is a measurement record, not automatically an
independent sample. When a task requests samples as PCA rows, each fitted row
must have a defensible sample identity.

1. Identify the observation and feature axes from labels, metadata, and
   provenance. Expression tables often store genes as rows and samples as
   columns even though PCA libraries expect observations as rows.
2. Materialize original observation labels before a transpose or a library can
   auto-rename them. Compare total and unique labels.
3. When companion sample metadata is supplied, use it to validate observation
   identity and inclusion even if its variables are not PCA features.
4. When primary labels repeat, complete the required pre-fit gate above before
   choosing retention, aggregation, or exclusion.

Use the following decision order for repeated primary labels:

- Retain distinct observations when an explicit key such as visit, tissue,
  library, aliquot, lane, timepoint, treatment, or cell barcode defines the
  observation unit requested by the task.
- If provenance establishes technical replicates of one biological sample,
  combine them using a scale-appropriate rule. Raw count partitions are
  usually summed; continuous or normalized measurements are usually averaged
  feature-wise.
- If provenance defines the primary ID as the analysis unit and repeated
  measurements are exchangeable observations of that unit, combine them only
  with an aggregation rule justified for the scale and estimand.
- If records sharing a primary ID disagree on stable attributes and no
  secondary key maps each matrix record to a valid observation, treat the
  complete repeated group as an unresolved identity collision. For a sample-
  or subject-level PCA, retention requires affirmative identity provenance: do
  not fit those records as independent observations and do not average them.
  If the requested analysis can proceed on the resolved observations, exclude
  every occurrence of the collided primary ID. If removing the group would
  invalidate the estimand or analysis set, leave the setup unresolved.

Matching matrix and metadata multiplicities, distinct expression values,
automatic suffixes, or instructions to use the supplied matrix do not by
themselves establish a secondary observation identity. Conversely, conflicts
in invariant attributes such as sex or germline genotype can disprove a
technical-replicate interpretation. Do not keep the first record, average
biologically incompatible records, or invent occurrence keys to hide an
unresolved collision.

Metadata used to validate identity and inclusion does not become a PCA feature.
An expression-only PCA therefore cannot ignore an identity collision exposed
by companion metadata. Likewise, wording that identifies the supplied
expression matrix as the data source does not define each matrix record as a
valid independent sample. Once a repeated group is classified as an unresolved
collision, only records with resolved identity are eligible for a numeric
sample-level fit; exclude the complete collided group when the remaining data
support that fit, or leave the analysis unresolved.

## Construct The Fitted Matrix

- Fit PCA with the requested observations as rows and features as columns.
  Preserve labels through transpose and reshape operations, and match metadata
  by identifiers rather than position.
- Establish whether values are raw counts, normalized abundance,
  log-transformed values, residuals, or batch-corrected values. Do not repeat a
  transform or correction already represented in the input.
- Apply the transform requested by the task. If ordinary PCA is requested on
  otherwise untransformed counts, use a scientifically justified count-aware
  normalization and transform.
- Resolve observation identity and any scale-appropriate replicate aggregation
  before applying a nonlinear transform unless the named method specifies a
  different order.
- Center features unless the method states otherwise. Scale only when requested
  or scientifically justified; scaling changes covariance-style PCA into
  correlation-style PCA.
- Apply an explicit missing-value policy and remove zero-variance features
  after the final transform.

## Extract Explained Variance

- PC scores are observation coordinates and loadings are feature weights;
  neither is percent variance explained.
- Use the implementation's explained-variance ratio when available. Otherwise,
  divide the component eigenvalue by total variance across the complete fitted
  feature space.
- Do not normalize by only the retained or truncated components and call that
  total explained variance.
- Convert a fraction to percent only when the requested output is a percentage.

## Acceptance Check

Before accepting a result, verify:

- the requested observation unit and the original and fitted matrix axes;
- total and unique primary labels, any secondary key, and the final observation
  count;
- comparison of all metadata records in repeated groups on plausible stable
  attributes;
- the evidence supporting retention, aggregation, exclusion, or unresolved
  status for repeated labels;
- transform state, centering, scaling, missingness, and zero-variance handling;
- the requested component count; and
- the explained-variance field, denominator, and units.

Reject a PCA result when observation identity, fitted orientation, transform
state, or the total-variance denominator remains implicit. Also reject a fit
that retains repeated primary labels as separate sample rows without an
explicit secondary identity or independent provenance.
