#!/usr/bin/env python3
"""Reproduce the task-level error-audit evidence for original-layout section 3.

Reads archived audit annotations and selected trace lines only. It neither opens
ground_truth/private reference keys nor reruns scientific analyses. The audit is a
census of tasks with at least one rejected (BixBench) or key-deviating (CompBio) run
in any archived configuration, plus the IWC low-agreement workflows; the script
checks that every task with a rejected primary run was audited. Counts are task-level
AI-assisted annotations, not independently adjudicated labels.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'manuscript_narrative/original_layout/analysis'
sys.path.insert(0, str(ROOT / 'manuscript_narrative'))
import narrative_common as nc  # noqa: E402
BENCH = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
CAT = {
    'C1': 'Equivalent answer representation',
    'C2': 'Scoring/evaluator artifact',
    'C3': 'Reference depends on an unstated choice',
    'C4': 'Galaxy platform/wrapper/server',
    'C5': 'Agent analysis error (broad composite)',
    'C6': 'Execution provenance/answer exposure',
    'C7': 'Score conceals changed scientific conclusion',
    'C8': 'Completion failure',
}
MODELS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro (Codex)']
# Cause groups used for the census figure; benchmark-side follows the BixBench sensitivity analysis.
GROUP = {'C5': 'Agent analysis', 'C1': 'Benchmark, reference or provenance', 'C2': 'Benchmark, reference or provenance',
         'C3': 'Benchmark, reference or provenance', 'C6': 'Benchmark, reference or provenance',
         'C4': 'Galaxy platform or wrapper', 'C7': 'Other', 'C8': 'Other'}
SELECTION = {'BixBench-Verified-50': 'census: task with at least one rejected run in any archived configuration',
             'CompBioBench': 'census: task with at least one run deviating from the reconstructed key in any archived configuration',
             'IWC': 'IWC workflow with a low-agreement run, or near-perfect agreement concealing a changed result'}


def dump_csv(name, rows):
    if not rows:
        return
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def sha256(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def trace_path(benchmark, task, run, gz=False):
    suffix = '.gz' if gz else ''
    return f'{benchmark}/analysis/{task}/source_snapshots/huggingface_traces/files/{run}/agent_workspace/run_trace/codex_events.jsonl{suffix}'


# These cases are intentionally chosen for positive recorded decision evidence.
# CompBioBench reference answers are omitted; no final answer values are exported.
CASES = [
    dict(case_id='R1', benchmark='BixBench-Verified-50', task='bix-52-q2',
         mechanism='A header filter also dropped valid chromosome identifiers',
         recorded_evidence='A digits-only regex precedes an inner join; the run explicitly accepts 18 rows although its input has 20 chromosome groups.',
         validation_opportunity='Assert preservation of eligible chromosome identifiers and row counts across the join.',
         contrasting_run='Luna Galaxy r1 explicitly asserts 20 rows and retains W and Z.',
         observed_mechanism_runs=1, task_primary_runs=24,
         count_definition='One scored-incorrect primary run with traced row loss; not a validation-absence rate.',
         caveat='Tool binding matched the request; scientific correctness depends on the requested filter.',
         audit_task='bix-52-q2'),
    dict(case_id='R2', benchmark='CompBioBench', task='variant-status-q1',
         mechanism='Read-end artifacts were interpreted as a biological allele',
         recorded_evidence='Wrong-run exemplars report the pileup-based genotype; correct Sol runs record a read-position hypothesis and a Galaxy UDT that removes the apparent alternate signal.',
         validation_opportunity='Inspect allele support by read cycle and alignment end, rather than base quality alone.',
         contrasting_run='Sol Galaxy r2/r3 execute a read-position audit inside Galaxy.',
         observed_mechanism_runs=20, task_primary_runs=24,
         count_definition='Twenty primary wrong calls attributed to the artifact by the targeted audit; this does not certify that all 20 omitted every validation step.',
         caveat='Domain judgment and validation rigor overlap; successful diagnostic use by Sol does not test the knowledge of other configurations.',
         audit_task='variant-status-q1'),
    dict(case_id='R3', benchmark='CompBioBench', task='exogenous-mix-reads-q1',
         mechanism='In-sample classification replaced held-out validation',
         recorded_evidence='GPT-5.5 code r1 first fits a held-out classifier, then replaces it with training-set estimates; GPT-5.5 Galaxy r1 fits and scores its estimators on the same reference reads.',
         validation_opportunity='Use grouped held-out or cross-fitted estimates and challenge perfect training separation.',
         contrasting_run='Sol Galaxy r2 explicitly prevents identical reads from leaking between training and validation folds.',
         observed_mechanism_runs=2, task_primary_runs=24,
         count_definition='Two runs with in-sample leakage in the audit: one code and one Galaxy. A third wrong run follows a UDT outage and a different route.',
         caveat='The leakage mechanism is observed across both arms; the third wrong run is not counted as the same mechanism.',
         audit_task='exogenous-mix-reads-q1'),
    dict(case_id='R4', benchmark='IWC', task='wf_007_vgp_mitogenome_assembly',
         mechanism='Structural plausibility or self-mapping was treated as sequence identity',
         recorded_evidence='A Galaxy run explicitly selects a circular, high-depth contig; a code run explicitly validates a seed by mapping reads back to that same seed. The three zero-score outputs share no canonical 31-mers with the workflow reference.',
         validation_opportunity='Test mitochondrial gene content or independent organellar identity, alongside structure, coverage and read support.',
         contrasting_run='Successful Galaxy runs use the MitoHiFi reference-finding and assembly route.',
         observed_mechanism_runs=3, task_primary_runs=24,
         count_definition='Three zero-agreement candidates, one Galaxy and two code, attributed to non-mitochondrial candidate selection in the targeted audit.',
         caveat='The input-only policy conflicted with external-reference requirements. Some recorded validation was performed but did not establish molecular identity.',
         audit_task='wf_007_vgp_mitogenome_assembly'),
    dict(case_id='R5', benchmark='CompBioBench', task='histone-chip-q1',
         mechanism='A direct cross-check contradicted the candidate identity but was not acted on',
         recorded_evidence='DeepSeek Galaxy r1 calls ENCODE peak-set overlap a direct identity check; its returned Jaccard values are approximately 0.0011 and 0.0006, yet it retains one of those candidates.',
         validation_opportunity='Treat negative candidate tests as reasons to broaden hypotheses and examine independent read-level evidence.',
         contrasting_run='GPT-5.5 Galaxy r1 computes read-level promoter, gene-body and repeat enrichment with UDT jobs.',
         observed_mechanism_runs=1, task_primary_runs=24,
         count_definition='One direct ignored-cross-check example among two wrong DeepSeek Galaxy runs. The second has no reasoning transcript and is not counted as positive ignored-check evidence.',
         caveat='The audit also assigns domain-knowledge error. Weak overlap is evidence against the chosen candidate, not an independently definitive histone identity test.',
         audit_task='histone-chip-q1'),
]

# Each tuple is (case, purpose, source, decompressed line, strings to confirm).
EVIDENCE = [
    ('R1', 'wrong filter', trace_path('BixBench_50', 'bix-52-q2', 'galaxy_codex_gpt_5_6_luna_r3'), 89, ['^[0-9]+']),
    ('R1', 'accepted depleted denominator', trace_path('BixBench_50', 'bix-52-q2', 'galaxy_codex_gpt_5_6_luna_r3'), 135, ['18 eligible chromosomes']),
    ('R1', 'contrasting row-count assertion', trace_path('BixBench_50', 'bix-52-q2', 'galaxy_codex_gpt_5_6_luna_r1'), 195, ['assert len(rows) == 20']),
    ('R2', 'wrong-run pileup then answer', trace_path('CompBio', 'variant-status-q1', 'open_ended_code_codex_gpt_5_6_sol_r1', True), 11, ['samtools mpileup']),
    ('R2', 'correct diagnostic hypothesis', trace_path('CompBio', 'variant-status-q1', 'galaxy_codex_gpt_5_6_sol_r2'), 25, ['cluster at read positions 1']),
    ('R2', 'Galaxy diagnostic UDT', trace_path('CompBio', 'variant-status-q1', 'galaxy_codex_gpt_5_6_sol_r2'), 40, ['run_galaxy_udt_and_wait', 'counts_min_distance_from_end_2']),
    ('R3', 'held-out model before replacement', trace_path('CompBio', 'exogenous-mix-reads-q1', 'open_ended_code_codex_gpt_5_5_r1', True), 26, ['holdout kmer classifier', 'train[cls]=arr[:split]']),
    ('R3', 'training-set model after replacement', trace_path('CompBio', 'exogenous-mix-reads-q1', 'open_ended_code_codex_gpt_5_5_r1', True), 30, ["seqs[cls]", "P={cls:Counter(cat(s)"]),
    ('R3', 'Galaxy in-sample diagnostic', trace_path('CompBio', 'exogenous-mix-reads-q1', 'galaxy_codex_gpt_5_5_r1'), 20, ['klf4-exogenous-mixture-diagnostics-v1']),
    ('R3', 'contrasting grouped validation', trace_path('CompBio', 'exogenous-mix-reads-q1', 'galaxy_codex_gpt_5_6_sol_r2'), 32, ['prevents identical reads from leaking']),
    ('R4', 'explicit input-policy conflict', trace_path('IWC', 'wf_007_vgp_mitogenome_assembly', 'galaxy_gpt_5_5_r1'), 32, ['use only the provided inputs']),
    ('R4', 'explicit candidate criteria', trace_path('IWC', 'wf_007_vgp_mitogenome_assembly', 'galaxy_gpt_5_5_r1'), 82, ['circular', '14,449']),
    ('R4', 'explicit circular validation', trace_path('IWC', 'wf_007_vgp_mitogenome_assembly', 'open_ended_code_codex_deepseek_v4_pro_r2', True), 193, ['map back with full coverage', '18.3x']),
    ('R5', 'claimed direct identity check', trace_path('CompBio', 'histone-chip-q1', 'galaxy_codex_deepseek_v4_pro_0813_r1', True), 294, ['direct identity check']),
    ('R5', 'returned negative cross-check', trace_path('CompBio', 'histone-chip-q1', 'galaxy_codex_deepseek_v4_pro_0813_r1', True), 396, ['0.001077']),
    ('R5', 'returned negative cross-check', trace_path('CompBio', 'histone-chip-q1', 'galaxy_codex_deepseek_v4_pro_0813_r1', True), 436, ['0.000619181']),
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    audit_p = ROOT / 'individual_error_analysis.md'
    fd_p = ROOT / 'manuscript_material/source_data/figure_data.json'
    audit = audit_p.read_text()
    cases = json.loads(fd_p.read_text())['task_cases']
    assert len(cases) == 93
    counts = Counter(r['category'] for r in cases)
    assert dict(counts) == {'C2': 4, 'C3': 20, 'C6': 1, 'C5': 52, 'C4': 8, 'C8': 1, 'C1': 6, 'C7': 1}
    # Replicate sets of the four primary configurations (written by accuracy_analysis.py).
    sets = pd.read_csv(OUT / 'accuracy_replicate_sets.csv')
    binary = sets[sets.benchmark.isin(['BixBench50', 'CompBio'])]
    task_max = binary.groupby(['benchmark', 'task']).n_errors.max()
    task_wrong = binary.groupby(['benchmark', 'task']).n_errors.sum()
    failing = {(BENCH[b], t) for (b, t), m in task_max.items() if m > 0}
    audited = {(BENCH[r['benchmark']], r['task']) for r in cases}
    assert failing <= audited, f'Tasks with rejected primary runs missing from the audit: {sorted(failing - audited)}'
    # BixBench grades are archived for every configuration, so the census rule can be checked directly.
    arch = nc.runs()
    bix_any = set(arch[(arch.benchmark == 'BixBench50') & arch.score.eq(0)].task)
    assert bix_any == {t for (b, t) in audited if b == 'BixBench-Verified-50'}, 'BixBench audit is not the census of failing tasks'

    rows = []
    for r in cases:
        b = BENCH[r['benchmark']]
        key = (r['benchmark'], r['task'])
        fail = (b, r['task']) in failing
        mx = int(task_max[key]) if key in task_max.index else None
        rows.append(dict(benchmark=b, task=r['task'], primary_category=r['category'],
                         primary_category_label=CAT[r['category']], cause_group=GROUP[r['category']], tags=';'.join(r['tags']),
                         insufficient_verification_tag='insufficient-verification' in r['tags'],
                         domain_knowledge_tag='domain-knowledge-error' in r['tags'],
                         primary_failing_task=fail,
                         max_rejected_in_primary_set=mx if b != 'IWC' else None,
                         rejected_primary_runs=int(task_wrong[key]) if key in task_wrong.index else None,
                         persistence=('IWC continuous endpoint' if b == 'IWC' else
                                      'persistent (a set rejected 3/3)' if mx == 3 else
                                      'sporadic (1-2 rejected per set)' if fail else 'no primary rejection'),
                         audit_source='individual_error_analysis.md', selection=SELECTION[b]))
    dump_csv('rigor_task_cases.csv', rows)
    category_rows = []
    tag_rows = []
    for b in list(BENCH.values()) + ['All audited cases']:
        subset = rows if b == 'All audited cases' else [r for r in rows if r['benchmark'] == b]
        for cat in CAT:
            n = sum(r['primary_category'] == cat for r in subset)
            category_rows.append(dict(benchmark=b, category=cat, label=CAT[cat], task_cases=n, denominator_cases=len(subset), percent=100*n/len(subset), unit='audited task case'))
        tags = Counter(t for r in subset for t in r['tags'].split(';'))
        for tag, n in sorted(tags.items()):
            tag_rows.append(dict(benchmark=b, tag=tag, task_cases=n, denominator_cases=len(subset), percent=100*n/len(subset), exclusive=False, unit='audited task case'))
    dump_csv('rigor_category_counts.csv', category_rows)
    dump_csv('rigor_tag_counts.csv', tag_rows)

    def tag_cell(r):
        v, d = r['insufficient_verification_tag'], r['domain_knowledge_tag']
        return 'Verification and domain' if v and d else 'Verification only' if v else 'Domain only' if d else 'Neither tag'

    census = [r for r in rows if r['primary_failing_task']]
    scopes = {'All audited cases': rows, 'C5 agent-analysis cases': [r for r in rows if r['primary_category'] == 'C5'],
              'Census: tasks with a rejected primary run': census,
              'Census: agent-analysis tasks': [r for r in census if r['primary_category'] == 'C5']}
    overlap = []
    for scope, subset in scopes.items():
        for verification in [False, True]:
            for domain in [False, True]:
                overlap.append(dict(scope=scope, insufficient_verification_tag=verification, domain_knowledge_tag=domain,
                                    tag_combination=tag_cell(dict(insufficient_verification_tag=verification, domain_knowledge_tag=domain)),
                                    task_cases=sum(r['insufficient_verification_tag'] == verification and r['domain_knowledge_tag'] == domain for r in subset), denominator_cases=len(subset)))
    dump_csv('rigor_tag_overlap.csv', overlap)

    # Census of binary-benchmark tasks with at least one rejected primary run.
    census_rows = []
    for scope in ['BixBench-Verified-50', 'CompBioBench', 'Both binary benchmarks']:
        subset = census if scope.startswith('Both') else [r for r in census if r['benchmark'] == scope]
        wrong = sum(r['rejected_primary_runs'] for r in subset)
        for cat in CAT:
            q = [r for r in subset if r['primary_category'] == cat]
            census_rows.append(dict(benchmark=scope, cause_group=GROUP[cat], category=cat, label=CAT[cat],
                                    tasks=len(q), denominator_tasks=len(subset), percent=100*len(q)/len(subset),
                                    rejected_primary_runs=sum(r['rejected_primary_runs'] for r in q), denominator_runs=wrong,
                                    verification_tagged_tasks=sum(r['insufficient_verification_tag'] for r in q),
                                    unit='task with at least one rejected primary run'))
    dump_csv('rigor_census_categories.csv', census_rows)
    persistence_rows = []
    for persistence in ['persistent (a set rejected 3/3)', 'sporadic (1-2 rejected per set)']:
        subset = [r for r in census if r['persistence'] == persistence]
        for group in dict.fromkeys(GROUP.values()):
            q = [r for r in subset if r['cause_group'] == group]
            persistence_rows.append(dict(persistence=persistence, cause_group=group, tasks=len(q), denominator_tasks=len(subset),
                                         percent=100*len(q)/len(subset),
                                         verification_tagged_tasks=sum(r['insufficient_verification_tag'] for r in q),
                                         unit='task with at least one rejected primary run'))
    dump_csv('rigor_persistence.csv', persistence_rows)

    lines = audit.splitlines()
    selected = []
    for c in CASES:
        row = dict(c)
        heading = next((i+1, l) for i, l in enumerate(lines) if l.startswith('### '+c['audit_task']+' —'))
        # The original heading can itself contain a private reconstructed answer.
        # Keep an item locator, never its answer-bearing wording.
        row.update(audit_source='individual_error_analysis.md', audit_heading_locator='### '+c['audit_task'], audit_heading_line=heading[0])
        selected.append(row)
    dump_csv('rigor_cases.csv', selected)
    evidence_rows = []
    inputs = [audit_p, fd_p]
    for case, purpose, source, n, terms in EVIDENCE:
        p = ROOT / source
        opener = gzip.open if source.endswith('.gz') else open
        with opener(p, 'rt') as f:
            line = next(l for i, l in enumerate(f, 1) if i == n)
        # Unescape JSON content to check actual snippets, not its serialized form.
        content = json.dumps(json.loads(line), ensure_ascii=False)
        for term in terms:
            assert term.replace('\\', '') in content.replace('\\', ''), (case, source, n, term)
        evidence_rows.append(dict(case_id=case, purpose=purpose, source_file=source, decompressed_line=n,
                                  line_sha256=hashlib.sha256(line.encode()).hexdigest(), expected_evidence_found=True,
                                  evidence_role='positive recorded action/decision; no absence-of-transcript inference'))
        inputs.append(p)
    dump_csv('rigor_evidence.csv', evidence_rows)

    # This older workbook's endpoint is labelled as an acceptance proxy, never
    # scientific repair. It contains shell failures within Galaxy-assigned runs.
    recovery_p = ROOT / 'manuscript_material/on_demand/Source_Data_OD_Fig5.xlsx'
    errors = pd.read_excel(recovery_p, sheet_name='abc_every_error')
    runs = pd.read_excel(recovery_p, sheet_name='abc_runs')
    errors = errors[errors.model_configuration.isin(MODELS)]
    runs = runs[runs.model_configuration.isin(MODELS)]
    bench_normalize = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench'}
    errors['benchmark'] = errors.benchmark.replace(bench_normalize)
    runs['benchmark'] = runs.benchmark.replace(bench_normalize)
    recovery_rows = []
    channel_rows = []
    for (b, e), g in errors.groupby(['benchmark', 'execution_condition']):
        rr = runs[(runs.benchmark == b) & (runs.execution_condition == e)]
        accepted = int(g.run_ended_correct.sum())
        recovery_rows.append(dict(benchmark=b, assigned_arm=e, eligible_runs=len(rr), observed_error_events=len(g),
                                  errors_in_accepted_runs=accepted, acceptance_proxy_percent=100*accepted/len(g),
                                  endpoint='Error event belongs to a run that later passed its benchmark threshold',
                                  same_step_repair_measured=False, scientific_recovery_measured=False))
        for channel, gg in g.groupby('channel'):
            channel_rows.append(dict(benchmark=b, assigned_arm=e, channel=channel, observed_error_events=len(gg),
                                     errors_in_accepted_runs=int(gg.run_ended_correct.sum())))
    dump_csv('rigor_recovery_proxy.csv', recovery_rows)
    dump_csv('rigor_recovery_channels.csv', channel_rows)
    inputs.append(recovery_p)
    def census_count(pred, subset=census):
        return sum(bool(pred(r)) for r in subset)
    census_c5 = [r for r in census if r['primary_category'] == 'C5']
    persistent = [r for r in census if r['persistence'].startswith('persistent')]
    sporadic = [r for r in census if r['persistence'].startswith('sporadic')]
    findings = {
        'unit': 'retrospective audited task case; tags non-exclusive',
        'audit_selection_rule': SELECTION,
        'census_check': 'Every BixBench/CompBio task with a rejected primary run is audited; the BixBench audit equals the set of tasks with a rejected run in any archived configuration.',
        'census_tasks': len(census),
        'census_tasks_by_benchmark': Counter(r['benchmark'] for r in census),
        'census_verification_tag': census_count(lambda r: r['insufficient_verification_tag']),
        'census_domain_tag': census_count(lambda r: r['domain_knowledge_tag']),
        'census_both_tags': census_count(lambda r: r['insufficient_verification_tag'] and r['domain_knowledge_tag']),
        'census_domain_only': census_count(lambda r: r['domain_knowledge_tag'] and not r['insufficient_verification_tag']),
        'census_cause_groups': Counter(r['cause_group'] for r in census),
        'census_C5': len(census_c5),
        'census_C5_verification_tag': census_count(lambda r: r['insufficient_verification_tag'], census_c5),
        'census_C5_domain_only': census_count(lambda r: r['domain_knowledge_tag'] and not r['insufficient_verification_tag'], census_c5),
        'census_rejected_primary_runs': sum(r['rejected_primary_runs'] for r in census),
        'census_rejected_primary_runs_by_group': {g: sum(r['rejected_primary_runs'] for r in census if r['cause_group'] == g) for g in dict.fromkeys(GROUP.values())},
        'census_rejected_runs_in_verification_tagged_tasks': sum(r['rejected_primary_runs'] for r in census if r['insufficient_verification_tag']),
        'persistent_tasks': len(persistent),
        'persistent_cause_groups': Counter(r['cause_group'] for r in persistent),
        'persistent_verification_tag': census_count(lambda r: r['insufficient_verification_tag'], persistent),
        'sporadic_tasks': len(sporadic),
        'sporadic_cause_groups': Counter(r['cause_group'] for r in sporadic),
        'sporadic_verification_tag': census_count(lambda r: r['insufficient_verification_tag'], sporadic),
        'audit_task_cases': len(rows),
        'total_archive_tasks': 160,
        'audit_case_counts_by_benchmark': Counter(r['benchmark'] for r in rows),
        'primary_category_counts': counts,
        'insufficient_verification_tag_cases': sum(r['insufficient_verification_tag'] for r in rows),
        'domain_knowledge_tag_cases': sum(r['domain_knowledge_tag'] for r in rows),
        'both_verification_and_domain_tag_cases': sum(r['insufficient_verification_tag'] and r['domain_knowledge_tag'] for r in rows),
        'verification_tag_in_C5_cases': sum(r['insufficient_verification_tag'] and r['primary_category'] == 'C5' for r in rows),
        'C5_cases': counts['C5'],
        'annotation_status': 'AI-assisted retrospective audit; independent blinded expert adjudication has not been performed',
        'population_prevalence_estimated': 'Task-level census of failing binary-benchmark tasks; not a run-level prevalence and not independently adjudicated',
        'biological_knowledge_independently_tested': False,
        'galaxy_knowledge_independently_tested': False,
        'absence_of_validation_inferred_from_missing_transcript': False,
        'comparative_same_goal_error_recovery_measured': False,
        'selected_case_count': len(selected),
        'selected_trace_line_checks_passed': len(evidence_rows),
        'selected_cases': selected,
        'recovery_acceptance_proxy': recovery_rows,
        'replicate_pattern_interpretation': {
            'one_or_two_wrong': 'Observed within-cell outcome variability; mostly agent-analysis tasks, and nearly all Galaxy platform/wrapper tasks fall here.',
            'three_wrong': 'Observed repeated rejection; enriched for benchmark, reference or provenance categories relative to sporadic failures. The count alone does not assign a cause.',
            'scored_wrong_not_scientifically_wrong': 'Reference and evaluator defects must be separated from agent failure.'},
        'source_sha256': {str(p.relative_to(ROOT)): sha256(p) for p in sorted(set(inputs))},
        'no_new_agent_or_Galaxy_runs': True,
        'private_reference_answers_exported': False,
    }
    (OUT / 'rigor_results.json').write_text(json.dumps(findings, indent=2)+'\n')
    print(f'Rigor evidence: {len(rows)} task cases; census {len(census)} failing binary tasks, '
          f'{findings["census_verification_tag"]} verification-tagged; {len(evidence_rows)} selected trace checks passed.')


if __name__ == '__main__':
    main()
