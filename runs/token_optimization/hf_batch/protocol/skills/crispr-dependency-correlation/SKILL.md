---
name: crispr-dependency-correlation
description: Use only for CRISPR/RNAi dependency, essentiality, fitness, or gene-effect analyses where score direction or expression-dependency association changes a ranking, sign, or threshold. Do not use for generic screen-output correlations without dependency-score semantics.
---

# CRISPR Dependency Correlation

Resolve the score coordinate before computing, ranking, or thresholding a
dependency association.

## Score Semantics

- Determine the score definition from the task, field documentation, and data
  source. A column name alone is insufficient.
- DepMap/Chronos gene-effect values usually become more negative as dependency
  increases, with values near zero indicating little effect. Preserve that raw
  coordinate when the task asks for gene effect.
- Essentiality or dependency strength is a biological, positive-going
  coordinate unless the task explicitly defines it as a raw field. When that
  quantity is requested from a documented negative-going gene-effect field,
  use `dependency_strength = -gene_effect`. Thus a requested negative
  correlation with essentiality is evaluated after this transform.
- Do not negate a score that is already documented as positive-going. The
  transform requires both biological-strength wording and evidence that the
  supplied field is negative-going; either condition alone is insufficient.
- Apply any transform before correlations, rankings, signs, or thresholds are
  interpreted. Negating one variable negates its correlation coefficient.

## Matrix Alignment

- Make samples, models, or cell lines the shared observation axis and align
  them by stable identifiers rather than position.
- Use the intended feature pairing. Same-gene expression versus dependency is
  the default only when the task asks for a same-gene association; preserve
  cross-gene regulator-target requests.
- Resolve duplicate feature symbols deliberately. Prefer stable feature IDs or
  exact source labels until an aggregation rule is justified.
- Compute each feature correlation on its valid paired observations when
  pairwise-complete handling is intended. Do not drop an entire feature because
  one model is missing.
- For Spearman correlation, rank after alignment, filtering, and score-coordinate
  selection.

## Ranking And Counts

Interpret positive, negative, strongest, and threshold wording in the selected
coordinate. Use signed correlation unless the task explicitly asks for absolute
magnitude. Count or rank only after missing-value handling and coordinate choice
are fixed, and report the requested raw-score or biological-strength result
without silently switching between them.
