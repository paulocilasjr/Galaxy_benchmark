---
name: phylogenetics-tree-metrics
description: Use for tree, alignment, or phylogenetic-summary tasks involving branch lengths, patristic distances, long-branch scores, informative sites, composition variability, evolutionary rates, per-file aggregation, or group comparisons.
---

# Phylogenetics Tree Metrics

Match the requested metric to its biological input object and observation unit.

## Input And Metric

- Branch-length sums, patristic distances, and long-branch metrics require
  phylogenetic trees with the relevant branch lengths and rooting assumptions.
- Informative-site, composition-variability, alignment-length, and gap metrics
  require multiple sequence alignments. A FASTA suffix alone does not prove the
  sequences are aligned.
- Sequence distance, patristic distance, total tree length, and evolutionary
  rate are different quantities. Use the requested definition and denominator.
- Preserve taxon labels and document how missing taxa, missing branch lengths,
  failed files, and invalid archive members are handled.

## Collections And Aggregation

- Select archive members by the required object type and preserve their group
  labels.
- Compute the biological metric per tree, alignment, or file before group-level
  aggregation.
- When a tool returns one row per taxon or taxon pair, reduce those rows to the
  requested per-file summary before comparing files or groups.
- Do not pool all pairwise or per-taxon rows across files when the independent
  observation unit is the file.
- Apply the same inclusion and failure policy to every group and verify selected,
  processed, skipped, and failed counts.

## Statistical Comparisons

- Define the independent observation unit, group order, alternative hypothesis,
  tie handling, exact/asymptotic/permutation method, and continuity correction.
- A Mann-Whitney U value depends on implementation and input order. Report the
  statistic produced by the named implementation with the specified first
  sample; use the smaller-U convention only when that method or task defines it.
- Keep test statistics and p-values distinct. A reconstructed p-value is valid
  only when the alternative and implementation settings match.

Before accepting a group comparison, verify that every reported value was
derived from the same requested per-file metric and aggregation rule.
