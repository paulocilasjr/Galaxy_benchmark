---
name: variant-callset-ratio
description: Use for Ts/Tv, SNP/indel, genotype-specific rates, mutation counts, or filtered variant summaries when the requested callset stage, sample/genotype scope, filters, variant type, and site-versus-allele unit can change the result.
---

# Variant Callset Ratios

Resolve the requested data object before computing a ratio. A correct statistic
from a different callset, sample scope, or counting unit is a different result.

## Callset Scope

Determine from the task, metadata, and VCF provenance:

- the target sample, cohort, organism, and reference build;
- whether the requested object is the supplied VCF, a named filtered stage, or
  the output of a specified calling/filtering procedure;
- raw, intermediate, filtered, or analysis-ready status;
- sample and genotype inclusion rules;
- PASS, quality, depth, allele-frequency, or other requested filters; and
- site, allele, genotype, or event as the counting unit.

An explicit request for a particular VCF or table selects that object. A request
for a downstream filtered or pipeline-defined callset requires that stage. When
several stages are available but the task names only a sample-level statistic,
use provenance and the described method to identify the intended stage; a
filename such as `raw` or the mere presence of reads, BAM, or a reference does
not by itself require re-calling.

Calling the same reads with a different caller creates a different callset. Do
not introduce a caller, ploidy model, or filtering chain that is not requested
or supported by provenance merely because it is convenient. If a necessary
stage must be generated, preserve the named method and target sample/genotype
scope.

Organism ploidy and sample composition are part of genotype scope. For a
haploid clonal isolate, diploid heterozygous calls can indicate a caller-ploidy
mismatch, mixed population, contamination, mapping ambiguity, or another data
issue; they are not ordinary fixed isolate variants. First determine whether
the task asks for the supplied VCF, an isolate consensus, or within-sample
variation. When a new consensus callset is actually required, use a caller and
ploidy model appropriate to the organism. Filtering a diploid callset to
homozygous-alternate records is a different operation and must not be presented
as equivalent to haploid re-calling.

## Ts/Tv And Other Ratios

- For Ts/Tv, count only single-nucleotide substitutions unless the task states
  otherwise. Transitions are A<->G and C<->T; the other single-base changes are
  transversions.
- Decide whether a multiallelic record contributes one site or separate alleles.
- For sample-specific results, exclude reference, missing, and no-call genotypes
  and apply the requested genotype scope.
- For SNP/indel or related ratios, define both classes under the same record,
  allele, and filter conventions.
- Tie numerator and denominator to the same callset stage, sample set, filter
  chain, variant type, and counting unit.

## Validation

Check retained counts after material filters and confirm that variants belong to
the requested sample or cohort. Treat an empty result as unresolved until
coverage, reference compatibility, filter behavior, and job status support a
true zero. Never mix a site-level numerator with an allele-level denominator or
include indels, symbolic alleles, or missing genotypes in an SNV-only ratio.
