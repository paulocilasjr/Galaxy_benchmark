"""Conservative retrospective annotations, separate from original scores."""

TASK_NOTES = {
 'bix-12-q2': ('Domain/statistical definition', 'Gap characters were counted as states in parsimony-informative sites; Counter(column) includes repeated gaps. A working counter is insufficient without the biological state definition.', 'high'),
 'bix-12-q4': ('Population/metric mismatch', 'The U statistic depends on the alignment population and treatment of gaps. Shared-ortholog restriction, four-sequence filtering, and metric differences occur in these traces; the exact cause is not established for every replicate.', 'mixed'),
 'bix-12-q5': ('Domain/statistical definition', 'Counting repeated gaps as character states inflated the maximum informative-site count to 35; accepted runs return 29 under gap exclusion.', 'high'),
 'bix-12-q6': ('Population/state definition', 'Gap-inclusive informative-site fractions or a shared-ortholog subset change the U statistic. Complementary U orientation is an additional issue in the 55058 submission.', 'high'),
 'bix-14-q1': ('Cohort/variant definition', 'Five answers use 30/47: six splice-region records enter the coding denominator, versus 30/(30+11) under the accepted synonymous/missense scope. Splice-region annotation alone does not establish a coding-base change. The zero-answer run has a separate cohort/filter problem.', 'moderate'),
 'bix-16-q1': ('Unresolved data/reference mismatch', 'A different top correlation is not disproved by gene-name consensus. Sample alignment, feature mapping, coefficient ordering, and the scored reference must be reconciled. USP54 has a directly demonstrated scientific-notation sorting error; other candidates remain unadjudicated.', 'unresolved'),
 'bix-16-q3': ('Unresolved data/reference mismatch', 'The trace reports a maximum positive rho of 0.523398 and therefore zero genes above 0.6. The threshold calculation follows those coefficients; sample matching/reference differences, not threshold disregard, remain unresolved.', 'unresolved'),
 'bix-16-q4': ('Unresolved statistical/reference mismatch', 'The submitted significant-percentage values differ from the saved evaluator. Reconstruct the matched samples, p-values, tested family, and denominator before assigning a statistical defect.', 'unresolved'),
 'bix-22-q1': ('Unresolved normalization/interpretation', 'The run calculated expression-versus-length Pearson correlations and selected CD4; the evaluator expects CD14. The precise upstream divergence is not established by the archived score or a familiar marker name.', 'unresolved'),
 'bix-24-q2': ('Contrast/interpretation mismatch', 'The upregulation conclusion depends on the treatment/control contrast and selection of metabolic GO terms. Galaxy Luna r3 computed both directions but based its conclusion on CBD-versus-DMSO terms; other contrasts show strong downregulated metabolism. The reference contrast requires reconciliation.', 'moderate'),
 'bix-26-q5': ('Enrichment-universe/reference ambiguity', 'Foreground sizes, mapping coverage, background, pathway-size bounds, and the BH test family vary. Completed ORA and an adjusted-p threshold do not establish equivalence to the scored universe. No universal arithmetic error is established.', 'moderate'),
 'bix-27-q5': ('Unresolved PCA input scope', 'Runs obtain approximately 56.47% or 56.02% for different raw/duplicate-sample handling, versus approximately 55.97% accepted. Repeated SVD/prcomp agreement validates a selected matrix, not which columns the question intended.', 'unresolved'),
 'bix-28-q3': ('Tool-output semantics + rigor', 'The verbose tool returned four negative values; their median is -30.45505. Nonverbose mode returned 146.3023, which the agent accepted despite the contradiction. The precise wrapper/upstream parser defect is not isolated.', 'high'),
 'bix-30-q3': ('Statistical specification/reference ambiguity', 'One-versus-zero significant results depend on normalization, missing Ct handling, and test specification. Multiple computed sensitivity results do not identify a unique reference method. No blanket BH error is established.', 'unresolved'),
 'bix-31-q2': ('Estimator/filter compatibility', 'DESeq2/PyDESeq2 settings and filtering change the FAM138A estimate. At least one run changed the gene population to avoid memory pressure; provenance is insufficient to assign that mechanism to all six rejections.', 'mixed'),
 'bix-32-q2': ('Enrichment operation/universe mismatch', 'Some runs compare separately enriched pathway sets; one first intersects 59 DE genes and enriches that intersection, a different estimand. Background/library differences remain unresolved for the other rejections.', 'mixed'),
 'bix-34-q5': ('Wrong aggregation/population/metric', 'The three submitted custom-code answers respectively pool per-tip distances, restrict to shared trees, or use ML distance matrices rather than the requested per-tree patristic-distance summaries. One Galaxy run has no answer.', 'high'),
 'bix-35-q1': ('Tool parameter/output semantics + rigor', 'Both total-tree-length and evolutionary-rate requests returned 0.1884. The agent itself calculated total length/4 approximately 0.04709 but trusted the inconsistent tool output. Wrong operation binding or wrapper semantics needs repair.', 'high'),
 'bix-35-q2': ('Population mismatch', 'Restricting to shared orthologs/available tree subsets changes the Mann–Whitney population. Runs use 96/96 or 19/19 subsets rather than the reference population. The smaller sample is a different analysis.', 'moderate'),
 'bix-43-q2': ('Mixed evaluator/statistical compatibility', 'The same 5.831005 value passes a tolerance-based evaluator and fails a two-decimal evaluator. Other values also differ scientifically/numerically; their DE/background choices are not all independently adjudicated.', 'mixed'),
 'bix-43-q4': ('Gene-set denominator/reference mismatch', 'Overlap counts of 9 or pathway sizes of 47 differ from the reference. One run inferred size 47 from odds-ratio algebra using an assumed background, which cannot establish the full Reactome pathway membership.', 'mixed'),
 'bix-45-q1': ('Software-version/reference compatibility', 'RCV values differ between PhyKIT implementations. Modern calculation gives U=5483.5 and p=1.5197572608715265e-56; old 2.0.3 gives U=6115 and the accepted p=7.69676083e-54. Shared-only inputs give another rejected p. Scientific invalidity of all rejected implementations is not established.', 'moderate'),
 'bix-46-q4': ('Missing submission', 'No fixed submitted answer is preserved. Trace evidence cannot establish an independently correct final result; the ultimate termination/budget cause is unresolved.', 'unresolved'),
 'bix-49-q4': ('Estimator/evaluator compatibility', 'Both rejected older-harness runs report 2100 after PyDESeq2 analysis and repaired input/API errors. Other accepted values differ slightly too. Version/filter/acceptance-policy differences require matched replay; no uncorrected parsing defect is established.', 'unresolved'),
 'bix-51-q8': ('Statistical estimator defaults', 'The cross-check used LogisticRegression(solver="liblinear"), with regularization defaults, rather than establishing equivalence to the requested unpenalized logistic coefficient. Reproducing the regularized value does not validate the reference estimand.', 'moderate'),
 'bix-52-q2': ('Unresolved join/denominator scope', 'The final density table contains 18 chromosome rows and a mean of 9.5074614e-8. That confirms the submitted arithmetic on that table, not chromosome completeness or the intended mean denominator.', 'unresolved'),
 'bix-52-q7': ('Counting/answer-target error', '19160 is one above the accepted data-row count 19159; 539 is 19698-19159, the complementary removed count. One run has no submission. Inspect header policy and whether retained or removed genes are requested.', 'high'),
 'bix-53-q2': ('Evaluator semantic false rejection', 'All 30 answers state an increase, matching the expected direction. The saved label-token/string check rejects equivalent wording. Direction is independently adjudicated; exact DE counts are not revalidated here.', 'high'),
 'bix-53-q5': ('Unit normalization/evaluator', '10.0% is numerically 0.1. The verifier compared the parsed 10.0 with expected 0.1. Scientific fraction equivalence is established; requested output-unit compliance is a separate issue.', 'high'),
 'bix-54-q7': ('Model-input scope/reference ambiguity', 'Including both pure endpoints gives about 178984; mixtures alone about 180771; including pure 287 but excluding pure 98 gives the accepted approximately 184372. Optimizer convergence does not decide the row-inclusion contract.', 'moderate'),
 'bix-55-q1': ('BUSCO/version/pipeline compatibility', 'Two reruns yield 100 complete orthologs versus reference 101; another standalone HMM approach yields 64 and is not the full BUSCO completeness pipeline. Version and lineage snapshot matter.', 'mixed'),
 'bix-61-q2': ('Unresolved upstream mapping/input difference', 'The trace divides 95174581 by 4641652, correctly obtaining 20.50446 on the emitted NC_000913.3 positions. That arithmetic alone cannot reconcile the expected 12.1283; no denominator bug is established.', 'unresolved'),
 'bix-61-q5': ('Unresolved callset/reference-stage mismatch', 'All 30 runs return 2.56 while the reference is 2.68. Independent arithmetic confirms reported Ts/Tv counts around 2.557; the underlying fixed VCF was not preserved in the selected artifacts needed for a new recount. Unanimity is not ground truth.', 'unresolved'),
}


def classify(r):
    task, run, answer = r['task'], r['run_id'], r['answer']
    secondary = 'No secondary cause established; operational errors, if present, are listed separately.'
    if r['benchmark'] == 'IWC':
        if 'mitogenome' in task:
            if run == 'galaxy_gpt_5_5_r1':
                return ('Domain identity/evidence sufficiency', 'Chose circular 14449-bp high-depth ptg000099c without organellar identity evidence; public-reference canonical 31-mer overlap is zero.', 'high', 'Nested parameter binding/extraction friction occurred after candidate selection and did not cause its identity.')
            if run == 'open_ended_code_gpt_5_5_r1':
                return ('Rigor: known evidence deficit ignored', 'Finalized the 16279-bp candidate after explicitly recognizing that read support was concentrated at its anchor and inadequate elsewhere; public-reference overlap is zero.', 'high', 'Assembly/install/memory friction and a long execution tail; no exact fraction of tokens attributable to overhead is available.')
            return ('Domain identity/circular validation', 'Trimming/polishing the 15349-bp seed, filling Ns from it, and self-alignment validate the seed against itself, not mitochondrial identity or circular closure; public-reference overlap is zero.', 'high', 'N-count validation initially measured name/length fields; subsequently corrected without repairing candidate identity.')
        if 'amplicon' in task:
            return ('Identifier contract/harness integration', 'All 17 sample IDs in the submitted table use lowercase directory slugs, whereas the evaluator requires original mixed-case hFMT/mFMT/noFMT identifiers. Validating directory names is the wrong identity authority.', 'high', 'R/installation friction and fallback to VSEARCH in r3; DADA2 matching retries in r1. These do not explain the shared identifier error.')
        return ('Statistical algorithm error', 'Used forward maximum accumulation for BH correction. Independent recomputation disagrees in 1065/1429 rows by more than 1e-6. Range checks cannot validate the BH transformation.', 'high', 'NumPy/Dask and matrix-orientation errors were repaired; they are not the final algorithmic failure.')
    primary, note, confidence = TASK_NOTES[task]
    if answer is None:
        return ('Missing submission; cause unresolved', 'No answer artifact was fixed. This is a completion failure; do not infer a biological reasoning error or a timeout solely from score zero.', 'unresolved', 'See the complete call sequence for observed friction; termination cause is not established.')
    if task == 'bix-12-q4' and 'luna' in run:
        primary, note, confidence = 'Incorrect population restriction', 'L70 keeps only alignments with exactly four sequences (22 animal, 211 fungal). L72 observes 241/255 alignments. Pairwise-U and rank-sum agreement validate the same wrongly restricted population.', 'high'
    if task == 'bix-16-q1' and answer == 'USP54':
        primary, note, confidence = 'Numeric sorting + rigor', 'L58 uses sort -k3,3n on scientific notation and elevates rho=-9.411e-05 (p approximately 0.9975) to the strongest negative association. Parsed-float/general-numeric ordering and an extremum check would reject it.', 'high'
    if task == 'bix-28-q3':
        secondary = 'Agent accepted an impossible median despite having the four values; successful tool status was mistaken for a valid statistic.'
    if task == 'bix-35-q1':
        secondary = 'The agent explicitly noticed the factor-of-four contradiction and still submitted the inconsistent result.'
    if task == 'bix-43-q2' and answer == '5.831005059276599':
        primary, note, confidence = 'Evaluator policy inconsistency', 'This exact value is accepted in tolerance-based records but rejected by this rounded-numeric record. The score difference alone cannot be a reasoning difference.', 'high'
    if task == 'bix-31-q2' and 'claude_code' in run and 'open_ended' in run and run.endswith('r3'):
        primary, note, confidence = 'Statistical population altered for resources', 'Prefiltered genes to total counts >=50 (while retaining FAM138A), then fitted PyDESeq2 with changed outlier/filter settings. A memory workaround changed the fitted statistical population.', 'high'
        secondary = 'Memory pressure motivated the population change; estimator equivalence was not established.'
    if task == 'bix-32-q2' and 'claude_code' in run and 'open_ended' in run and run.endswith('r1'):
        primary, note, confidence = 'Wrong order of statistical operations', 'Intersected 59 DE genes first and enriched that set, instead of intersecting separately significant pathway sets. These operations are not interchangeable.', 'high'
    if task == 'bix-34-q5' and 'open_ended' in run:
        note = {'r1':'Pooled per-tip distances (303 animal/366 fungal from 94 trees) before the ratio; per-tree aggregation was lost.', 'r2':'Restricted to 96 shared trees, changing the population used for the ratio.', 'r3':'Used .mldist maximum-likelihood distances in place of distances along the inferred tree.'}[run[-2:]]
    if task == 'bix-52-q7':
        note = ('Submitted 539 removed genes (19698-19159), whereas the requested target and accepted result are 19159 retained genes.' if answer == '539' else 'Submitted 19160, one greater than 19159 retained data rows; header-versus-data counting must be reconciled.')
    if task == 'bix-14-q1' and answer == '0':
        primary, note, confidence = 'Cohort/filter selection gap', 'The late preview contains a single FLT3 missense record after filtering, insufficient to establish a cohort-wide synonymous fraction. The exact cohort-loss point is unresolved.', 'moderate'
    return primary, note, confidence, secondary
