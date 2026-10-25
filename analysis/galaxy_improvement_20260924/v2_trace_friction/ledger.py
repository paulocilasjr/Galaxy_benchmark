"""Assign primary/secondary root causes to every failing BixBench run and IWC run < 0.5; emit counts + grouped ledger."""
import collections
import json

S = [json.loads(l) for l in open('run_summaries.jsonl')]
SHORT = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'Sol', 'codex_gpt_5_6_luna': 'Luna',
         'deepseek_v4_pro_via_codex': 'DS-Codex', 'deepseek_v4_pro_via_claude_code_superseded': 'DS-ClaudeCode',
         'codex_deepseek_v4_pro': 'DS-Codex'}


def lab(s):
    return f"{'G' if s['condition'] == 'galaxy' else 'C'} {SHORT[s['model']]} r{s['replicate']}"


def missing(s):
    return s['answer'] in (None, '', 'None')


# (predicate, primary, secondary, decision point, confidence)
R = {
 'bix-12-q2': [(lambda s: True, 'KNOWLEDGE', '-', 'Counted gap characters as character states when scoring parsimony-informative sites', 'high')],
 'bix-12-q4': [(lambda s: s['answer'].startswith('1162'), 'RIGOR', '-', 'Kept only alignments with exactly four sequences (22/241 animal, 211/255 fungal); re-derived U on the same restricted set and treated agreement as validation', 'high'),
               (lambda s: True, 'RIGOR', 'KNOWLEDGE', 'Parsimony-informative percentages computed on a different population or state definition', 'moderate')],
 'bix-12-q5': [(lambda s: True, 'KNOWLEDGE', '-', 'Gap characters counted as states (maximum 35 instead of 29)', 'high')],
 'bix-12-q6': [(lambda s: True, 'KNOWLEDGE', 'RIGOR', 'State definition (gaps) and population differ from the reference counting', 'high')],
 'bix-14-q1': [(lambda s: s['answer'] == '0', 'RIGOR', '-', 'Filter chain yielded zero qualifying variants and the zero was submitted without questioning it', 'moderate'),
               (lambda s: True, 'RIGOR', 'SPEC', 'Different carrier-cohort / coding-variant / VAF definition gives 30/47 = 0.638', 'moderate')],
 'bix-16-q1': [(lambda s: s['answer'] == 'USP54', 'RIGOR', '-', '`sort -k3,3n` on scientific-notation coefficients selected rho = -9.4e-5 as "strongest"', 'high'),
               (lambda s: s['answer'] == 'COX17', 'RIGOR', 'PLATFORM', 'UDT container lacked SciPy; hand-written rank correlation returned implausible values (top rho -0.238 vs expected ~-0.52) and was accepted', 'high'),
               (lambda s: True, 'KNOWLEDGE', 'RIGOR', 'Correlated expression with raw Chronos gene effect instead of essentiality (-effect); CCND1 is most negative only on the raw scale', 'high')],
 'bix-16-q3': [(lambda s: True, 'RIGOR', '-', 'Unresolved: threshold/direction choice gave 0 genes', 'unresolved')],
 'bix-16-q4': [(lambda s: True, 'RIGOR', '-', 'Unresolved: different test family or multiple-testing denominator', 'unresolved')],
 'bix-22-q1': [(lambda s: True, 'RIGOR', '-', 'Unresolved: normalization / cell-type interpretation', 'unresolved')],
 'bix-24-q2': [(lambda s: True, 'RIGOR', 'SPEC', 'Direction call from GO enrichment of up- vs down-regulated sets inverted (contrast orientation)', 'moderate')],
 'bix-26-q5': [(lambda s: missing(s), 'HARNESS', 'RIGOR', 'No answer: 68.8 M input tokens, 206 shell calls, ended in literature / benchmark-source searches', 'high'),
               (lambda s: True, 'SPEC', 'RIGOR', 'Enrichment universe, KEGG ID mapping and BH family unstated; Galaxy kegg_ora converges on 2, code clusterProfiler variants on 1; no run reported the sensitivity', 'moderate')],
 'bix-27-q5': [(lambda s: missing(s), 'HARNESS', 'PLATFORM', 'No answer: turn ended while web-searching legacy Galaxy PCA wrapper source to learn its output semantics', 'high'),
               (lambda s: True, 'RIGOR', 'SPEC', 'Unresolved PCA input scope (56.47 vs 55.97)', 'unresolved')],
 'bix-28-q3': [(lambda s: True, 'PLATFORM', 'RIGOR', 'phykit_metrics non-verbose long_branch_score returned the sample variance (146.3023) of the four per-taxon scores; agent had the four values (median -30.455) and did not check the range', 'high')],
 'bix-30-q3': [(lambda s: True, 'SPEC', '-', 'Reproduced the published analysis (Student t-test, paper exclusions, mean-Ct normalization: miR-21 Bonferroni p_adj = 0.034); reference matches Welch on unnormalized data', 'high')],
 'bix-31-q2': [(lambda s: s['condition'] == 'galaxy', 'PLATFORM', 'RIGOR', 'UDT jobs never dispatched (handler/exit_code null); fell back to the R DESeq2+apeglm wrapper instead of the named pydeseq2 default shrinkage', 'high'),
               (lambda s: s['run_id'].endswith('claude_code_superseded_r3'), 'RIGOR', '-', 'Subsampled the sample population to reduce memory, changing the estimate', 'high'),
               (lambda s: True, 'RIGOR', 'SPEC', 'Estimator/filter settings differ from pydeseq2 defaults', 'moderate')],
 'bix-32-q2': [(lambda s: s['answer'] == '3', 'RIGOR', '-', 'Enriched the intersection of DE genes instead of intersecting pathways from three separate ORAs', 'high'),
               (lambda s: True, 'RIGOR', 'SPEC', 'Different enrichment operation/universe gives 2 same-direction pathways', 'moderate')],
 'bix-34-q5': [(lambda s: missing(s), 'HARNESS', 'PLATFORM', 'No answer: budget ended mid-UDT after PhyKIT CLI output parsing returned 0/96 trees', 'high'),
               (lambda s: True, 'RIGOR', 'KNOWLEDGE', 'Wrong aggregation unit / population / distance metric (.mldist instead of patristic)', 'high')],
 'bix-35-q1': [(lambda s: True, 'PLATFORM', 'RIGOR', 'Conditional binding: flat keys silently ran default total_tree_length; retry with __current_case__:0 ran it again with the mismatch guard blind; identical outputs accepted as confirmation', 'high')],
 'bix-35-q2': [(lambda s: True, 'RIGOR', '-', 'Different gene population for the rank test', 'moderate')],
 'bix-43-q2': [(lambda s: missing(s), 'HARNESS', 'RIGOR', 'No answer: turn ended during web searches that included the BixBench dataset viewer', 'high'),
               (lambda s: s['answer'].startswith('5.831005'), 'EVALUATOR', '-', 'Rounded-numeric verifier rejected 5.831 which the tolerance verifier accepted in other runs', 'high'),
               (lambda s: abs(float(s['answer']) - 5.81) > 0.1, 'RIGOR', 'SPEC', 'DEG set / enrichment input far from reference (odds ratio off by >0.1)', 'mixed'),
               (lambda s: True, 'SPEC', 'RIGOR', 'Near-miss DEG set (pre-filter semantics, contrast, pydeseq2 version) under a 0.5% tolerance; mechanism not isolated', 'mixed')],
 'bix-43-q4': [(lambda s: True, 'RIGOR', 'SPEC', 'DEG-set / pathway-denominator difference (9/49, 8/47)', 'mixed')],
 'bix-45-q1': [(lambda s: s['answer'].startswith('4.0286'), 'RIGOR', 'SPEC', 'Restricted to orthologs shared by both groups (241/241), changing the population', 'moderate'),
               (lambda s: s['condition'] == 'galaxy', 'SPEC', 'PLATFORM', 'Reference encodes PhyKIT 2.0.3-era RCV; Galaxy wrapper (like current PhyKIT) gives 1.5198e-56; wrapper version not surfaced, and a pinned-version route needed a UDT', 'high'),
               (lambda s: True, 'SPEC', 'RIGOR', 'Used current PhyKIT without checking version sensitivity (successful code runs matched the version to the input archive date)', 'high')],
 'bix-46-q4': [(lambda s: True, 'HARNESS', '-', 'No answer: turn ended during web search for the published log2FC value', 'high')],
 'bix-49-q4': [(lambda s: True, 'RIGOR', 'SPEC', 'Unresolved estimator difference (2100 vs 2106/2118, both accepted elsewhere)', 'unresolved')],
 'bix-51-q8': [(lambda s: True, 'RIGOR', 'KNOWLEDGE', 'Defined the response outcome as treatment arm (41 treated vs 39 controls) instead of PR vs SD/PD', 'high')],
 'bix-52-q2': [(lambda s: True, 'RIGOR', '-', 'Unresolved join / denominator scope', 'unresolved')],
 'bix-52-q7': [(lambda s: missing(s), 'HARNESS', '-', 'No answer: stopped after resolving an input filename mismatch', 'high'),
               (lambda s: s['answer'] == '539', 'RIGOR', '-', 'Reported the complement (retained rows) instead of removed rows', 'high'),
               (lambda s: True, 'RIGOR', '-', 'Off-by-one: header row counted (19160)', 'high')],
 'bix-53-q2': [(lambda s: True, 'EVALUATOR', '-', '"increase" (often with counts 1479->1931) rejected against "increases the number of DE genes"', 'high')],
 'bix-53-q5': [(lambda s: True, 'CONTRACT', 'EVALUATOR', 'Answered 10.0% where a fraction (0.1) was requested; same value', 'high')],
 'bix-54-q7': [(lambda s: True, 'SPEC', 'RIGOR', 'Reference requires excluding pure-strain-98 rows, documented only in the original capsule; both accepted runs retrieved benchmark source material', 'high')],
 'bix-55-q1': [(lambda s: True, 'RIGOR', 'SPEC', 'BUSCO version/pipeline or completeness-intersection difference', 'mixed')],
 'bix-61-q2': [(lambda s: True, 'RIGOR', '-', 'Re-trimmed the raw subsample FASTQs with Trimmomatic instead of mapping the supplied trimmed reads', 'high')],
 'bix-61-q5': [(lambda s: True, 'SPEC', 'RIGOR', 'All runs computed Ts/Tv on the supplied raw GATK callset (48,234/18,865 = 2.557); reference presumably filtered; no run tested filter sensitivity', 'high')],
}

IWC = {
 ('wf_007_vgp_mitogenome_assembly', 'galaxy_gpt_5_5_r1'): ('KNOWLEDGE', 'PLATFORM', 'Selected a 14,449-bp high-depth circular contig as the mitogenome from length/depth alone; no gene-content or identity check (0 shared 31-mers with OZ203683.1)', 'high'),
 ('wf_007_vgp_mitogenome_assembly', 'open_ended_code_gpt_5_5_r1'): ('RIGOR', 'PLATFORM', 'Agent noted the 16.3-kb candidate lacked support outside the anchor, then finalized it anyway', 'high'),
 ('wf_007_vgp_mitogenome_assembly', 'open_ended_code_codex_deepseek_v4_pro_r2'): ('KNOWLEDGE', 'RIGOR', 'Seed-dependent polishing and self-alignment used as validation of a wrong contig', 'high'),
 ('wf_005_amplicon_dada2_pe_denoising', 'open_ended_code_gpt_5_5_r1'): ('CONTRACT', '-', 'Sample IDs taken from lowercased directory slugs instead of the collection manifest identifiers', 'high'),
 ('wf_005_amplicon_dada2_pe_denoising', 'open_ended_code_gpt_5_5_r3'): ('CONTRACT', 'PLATFORM', 'Validated sample IDs against directory names (the wrong authority); R setup friction forced VSEARCH route', 'high'),
 ('wf_010_pseudobulk_scrna_de', 'open_ended_code_codex_deepseek_v4_pro_r3'): ('RIGOR', '-', 'Hand-written BH used forward cumulative max instead of reverse cumulative min; 1,065/1,429 FDRs wrong', 'high'),
 ('wf_003_host_contamination_removal', 'galaxy_gpt_5_6_luna_r1'): ('EVALUATOR', 'SPEC', 'BWA-MEM output (20,899 retained pairs) scored against the Bowtie2 route (72,867); matches the BWA route (20,896)', 'high'),
 ('wf_003_host_contamination_removal', 'galaxy_gpt_5_6_luna_r3'): ('EVALUATOR', 'SPEC', 'Same route-registration artifact as r1', 'high'),
}


def main():
    rows = []
    for s in S:
        if s['benchmark'] == 'BixBench50' and s['score'] == 0:
            for pred, p, sec, d, c in R[s['task']]:
                if pred(s):
                    rows.append(dict(b='BixBench', task=s['task'], run=lab(s), cond=s['condition'], ans=s['answer'], p=p, s=sec, d=d, c=c))
                    break
            else:
                raise SystemExit('unmatched ' + s['task'] + s['run_id'])
        if s['benchmark'] == 'IWC' and (s['task'], s['run_id']) in IWC:
            p, sec, d, c = IWC[(s['task'], s['run_id'])]
            rows.append(dict(b='IWC', task=s['task'], run=lab(s), cond=s['condition'], ans=f"score {s['score']:.3f}", p=p, s=sec, d=d, c=c))
    json.dump(rows, open('ledger.json', 'w'), indent=1)
    print('rows', len(rows), collections.Counter(r['b'] for r in rows))
    cats = ['PLATFORM', 'KNOWLEDGE', 'RIGOR', 'SPEC', 'EVALUATOR', 'CONTRACT', 'HARNESS']
    for b in ['BixBench', 'IWC']:
        for cond in ['galaxy', 'open_ended_code']:
            rr = [r for r in rows if r['b'] == b and r['cond'] == cond]
            pc = collections.Counter(r['p'] for r in rr)
            sc = collections.Counter(r['s'] for r in rr if r['s'] != '-')
            print(f"| {b} {cond} ({len(rr)}) | " + ' | '.join(f"{pc[c]} / {sc[c]}" for c in cats) + ' |')
    # grouped ledger
    out = ['| Task | Runs | Answer(s) | Decision point | Primary / secondary | Confidence |', '|---|---|---|---|---|---|']
    groups = collections.OrderedDict()
    for r in rows:
        k = (r['b'], r['task'], r['d'], r['p'], r['s'], r['c'])
        groups.setdefault(k, []).append(r)
    for (b, task, d, p, sec, c), rr in groups.items():
        answers = sorted({str(x['ans'])[:24] for x in rr})
        out.append(f"| {task} | {', '.join(x['run'] for x in rr)} | {'; '.join(answers)} | {d} | {p} / {sec} | {c} |")
    open('ledger_table.md', 'w').write('\n'.join(out))


if __name__ == '__main__':
    main()
