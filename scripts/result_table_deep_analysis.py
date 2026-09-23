"""Additional retrospective questions for Result_table.md.

All metrics derive from preserved events. A requested user-defined tool is not
assumed to have run, and an agent's explanation is not a verified catalog gap.
"""
from collections import Counter, defaultdict
import gzip
import hashlib
import json
import re
import statistics as st

import numpy as np

SOFTWARE_PATTERNS = {
    'phykit': r'\bphykit\b',
    'deseq2': r'\b(?:deseq2|pydeseq2)\b',
    'gseapy': r'\bgseapy\b',
    'samtools': r'\bsamtools\b',
    'bcftools': r'\bbcftools\b',
    'bedtools': r'\bbedtools\b',
    'anndata': r'\banndata\b',
    'scanpy': r'\bscanpy\b',
    'datamash': r'\bdatamash\b',
    'bwa': r'\bbwa\b',
}

ERROR_RULES = [
    ('BixBench50', 'kegg_ora', 'Empty background after pathway intersection', r'universe has zero genes',
     'Gene identifiers/background did not overlap pathway mappings; validate namespace and background before enrichment.'),
    ('BixBench50', 'kegg_ora', 'Mapping table has too few columns', r'mapping row .*too few columns',
     'Input table schema did not match wrapper requirements; validate columns and delimiter.'),
    ('BixBench50', 'kegg_ora', 'Empty foreground after intersection', r'foreground has zero genes',
     'Selected gene set did not overlap the analysis universe/mappings; inspect upstream selection and identifiers.'),
    ('BixBench50', 'deseq2', 'Missing factor-list element', r'factor_list\[\[1\]\].*subscript out of bounds',
     'Factor configuration was absent or misbound; the message does not identify whether the agent, helper or wrapper caused it.'),
    ('BixBench50', 'deseq2', 'Duplicate row names or factor levels', r"duplicate 'row.names'|factor level .*duplicated",
     'Sample labels or factor encoding were not unique; validate the design table before submission.'),
    ('CompBio', 'CONVERTER_gz_to_uncompressed', 'Invalid gzip magic', r'gzip: invalid magic',
     'Bytes were not recognized as gzip by the converter; check declared datatype against bytes before conversion.'),
    ('CompBio', 'bcftools_norm', 'Unrecognized or unindexable input', r'unknown file type|cannot be usefully indexed',
     'Input format or compression/index compatibility failed; check the variant-file format and index prerequisites.'),
    ('CompBio', 'anndata_export', 'DataFrame construction failure', r'DataFrame constructor not properly called',
     'The exported matrix did not fit the expected table representation; inspect matrix presence/type and export mode.'),
    ('CompBio', 'deseq2', 'No residual degrees of freedom', r'same number of samples and coefficients',
     'Model design could not estimate dispersion; validate replication and design rank before fitting.'),
]


def object_value(value):
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        try:
            result = json.loads(value)
            return result if isinstance(result, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def enrich_run(evidence, original, row):
    events = original['events']
    calls = [e for e in events if e['execution_location'] != 'galaxy_job']
    requests = [e for e in calls if e.get('tool') == 'run_galaxy_udt_and_wait']
    representations = [object_value(object_value(e.get('parameters')).get('representation')) for e in requests]
    ids = {r['id'] for r in representations if r.get('class') == 'GalaxyUserTool' and r.get('id')}
    jobs = [e for e in events if e['execution_location'] == 'galaxy_job' and e.get('tool') in ids]
    observed = row['coverage']['agent_transcript'] == 'retrieved'
    shell_events = [e for e in calls if e.get('tool') == 'shell']
    known_exits = [e['exit_code'] for e in shell_events if isinstance(e.get('exit_code'), int)]
    row.update({
        'prompt_words': len(re.findall(r'\b\w+\b', evidence['task']['prompt'])),
        'prompt_sha256': next((a.get('sha256') for a in original['artifacts'] if a.get('original_name') == 'prompt.txt'), None),
        'shell_calls': original['derived_metrics'].get('completed_shell_calls') if observed else None,
        'has_nonzero_shell': int(any(x != 0 for x in known_exits)) if observed and known_exits else None,
        'shell_events_with_exit_code': len(known_exits),
        'shell_events_without_exit_code': len(shell_events)-len(known_exits),
        'interface_calls': dict(Counter(e.get('tool') for e in calls)),
        'udt_request_count': len(requests) if observed else None,
        'udt_requested': bool(requests) if observed else None,
        'udt_ids': sorted(ids),
        'udt_unparsed_representations': sum(not rep for rep in representations),
        'udt_matched_job_ids': sorted({e['native_job_id'] for e in jobs}),
        'udt_matched_success_ids': sorted({e['native_job_id'] for e in jobs if e['status'] == 'ok'}),
        'udt_request_event_ids': [e['event_id'] for e in requests],
        'galaxy_full_tool_ids': sorted({e['tool'] for e in events if e['execution_location'] == 'galaxy_job' and e['tool'] != '__DATA_FETCH__'}),
        'software_command_indicators': [name for name,pattern in SOFTWARE_PATTERNS.items()
            if any(e.get('command') and re.search(pattern,e['command'],re.I) for e in calls)],
    })


def collect_case_sources(builder):
    cases = [
        ('BixBench50', 'bix-11-q1', 'galaxy_codex_gpt_5_5_r1', [18, 40, 49, 52, 63]),
        ('BixBench50', 'bix-11-q1', 'galaxy_codex_gpt_5_5_r3', [35, 49]),
        ('BixBench50', 'bix-45-q1', 'open_ended_code_codex_gpt_5_6_sol_r1', [29, 52]),
        ('BixBench50', 'bix-45-q1', 'galaxy_codex_gpt_5_6_sol_r1', [28, 32, 53]),
        ('CompBio', 'borzoi-basic-q1', 'galaxy_codex_gpt_5_5_r1', [17, 74]),
        ('CompBio', 'odd-one-out-q1', 'galaxy_codex_gpt_5_5_r1', [29, 30, 38, 44]),
    ]
    records = []
    for benchmark, task, rid, lines in cases:
        base = builder.ROOT / builder.FOLDERS[benchmark] / 'analysis' / task
        evidence = json.loads((base / 'history_analysis_evidence.json').read_text())
        run = next(r for r in evidence['runs'] if r['run_id'] == rid)
        artifact = next(a for a in run['artifacts'] if a.get('original_name') in ('codex_events.jsonl', 'codex_events.jsonl.gz'))
        path = base / artifact['local_path']
        with gzip.open(path, 'rt') if path.suffix == '.gz' else path.open() as f:
            contents = f.read().splitlines()
        messages = []
        for number in lines:
            item = json.loads(contents[number-1]).get('item', {})
            assert item.get('type') == 'agent_message', (task, rid, number)
            messages.append({'line': number, 'text': item.get('text'), 'evidence_type': 'agent_report_not_independent_adjudication'})
        numerical_checks = []
        if task == 'bix-45-q1' and rid == 'open_ended_code_codex_gpt_5_6_sol_r1':
            for line, expected in [(24, '1.5197572608715265e-56'), (33, '7.6967608298013025e-54'), (45, '7.6967608298013025e-54')]:
                event = next(e for e in run['events'] if e.get('source_line') == line)
                assert expected in event['stdout_excerpt']
                numerical_checks.append({'event_id': event['event_id'], 'source_line': line,
                                         'task_pvalue': expected, 'stdout_excerpt': event['stdout_excerpt']})
        records.append({'benchmark': benchmark, 'task': task, 'run_id': rid,
                        'source': str(path.relative_to(builder.ROOT)), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                        'messages': messages, 'numerical_checks': numerical_checks})
    return records


def correlation_interval(builder, rows, x, y, key):
    groups = defaultdict(list)
    for r in rows:
        groups[r['cluster']].append(r)
    groups = list(groups.values())
    def rho(rs):
        return builder.paths.spearman([r[x] for r in rs], [r[y] for r in rs])
    rng = np.random.default_rng([builder.SEED, int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)])
    draws = []
    for _ in range(5000):
        sample = [r for i in rng.integers(len(groups), size=len(groups)) for r in groups[i]]
        value = rho(sample)
        if value is not None:
            draws.append(value)
    return {'estimate': rho(rows), 'ci95': np.quantile(draws, [.025, .975]).tolist(),
            'n': len(rows), 'clusters': len(groups), 'resamples': 5000, 'valid_resamples': len(draws)}


def compute(builder, runs, cells, jobs):
    out = {'model_comparisons': [], 'shell_comparisons': [], 'udt': [], 'complexity': [], 'specific_error_codebook': ERROR_RULES,
           'software_indicator_codebook': SOFTWARE_PATTERNS, 'case_sources': collect_case_sources(builder)}
    grouped = defaultdict(list)
    for r in runs:
        if r['model'] in builder.MODELS[r['benchmark']]:
            grouped[r['benchmark'], r['task'], r['model'], r['condition']].append(r)
    for condition in builder.CONDITIONS:
        for model in builder.MODELS['BixBench50'][1:]:
            rows, error_rows = [], []
            for (benchmark, task, m, c), rs in grouped.items():
                if benchmark != 'BixBench50' or m != model or c != condition:
                    continue
                ref = grouped[benchmark, task, builder.COMMON[0], condition]
                rows.append({'task': task, 'cluster': rs[0]['cluster'],
                             'accuracy_difference': 100*(st.mean(r['score'] for r in rs)-st.mean(r['score'] for r in ref)),
                             'token_ratio': st.median(r['input_tokens'] for r in rs)/st.median(r['input_tokens'] for r in ref),
                             'run_ids': [r['run_id'] for r in rs+ref]})
                if condition=='galaxy' and all(r['has_error'] is not None for r in rs+ref):
                    error_rows.append({'task':task,'cluster':rs[0]['cluster'],
                        'difference':100*(st.mean(r['has_error'] for r in rs)-st.mean(r['has_error'] for r in ref)),
                        'run_ids':[r['run_id'] for r in rs+ref]})
            accuracy, _ = builder.bootstrap(rows, 'accuracy_difference', 'model_accuracy_'+condition+model)
            tokens, _ = builder.bootstrap(rows, 'token_ratio', 'model_cost_'+condition+model, 'median')
            errors = builder.bootstrap(error_rows,'difference','model_errors_'+model)[0] if error_rows else None
            out['model_comparisons'].append({'condition': condition, 'model': model, 'accuracy': accuracy, 'tokens': tokens,
                                             'job_error_difference':errors,'error_pairs':error_rows,'pairs': rows})
    for benchmark in builder.FOLDERS:
        pairs = []
        for (b, task, m, condition), rs in grouped.items():
            if b != benchmark or condition != 'galaxy':
                continue
            other = grouped[b, task, m, 'open_ended_code']
            if any(r['has_nonzero_shell'] is None for r in rs+other):
                continue
            g, o = sum(r['has_nonzero_shell'] for r in rs), sum(r['has_nonzero_shell'] for r in other)
            pairs.append({'cluster': rs[0]['cluster'], 'task': task, 'model': m, 'galaxy': g, 'open_ended_code': o,
                          'difference': 100*(g-o)/3, 'run_ids': [r['run_id'] for r in rs+other]})
        estimate, _ = builder.bootstrap(pairs, 'difference', 'shell_comparison_'+benchmark)
        out['shell_comparisons'].append({'benchmark': benchmark, 'estimate': estimate, 'pairs': pairs})
        for model in (*builder.MODELS[benchmark], 'all'):
            rs = [r for r in runs if r['benchmark']==benchmark and r['condition']=='galaxy' and
                  r['model'] in builder.MODELS[benchmark] and (model=='all' or r['model']==model)]
            by_cell = defaultdict(list)
            for r in rs:
                by_cell[r['task'],r['model']].append(r)
            complete = [v for v in by_cell.values() if len(v)==3 and all(r['udt_requested'] is not None for r in v)]
            varied = [v for v in complete if sum(r['udt_requested'] for r in v) in (1, 2)]
            same_prompt = [v for v in varied if all(r['prompt_sha256'] for r in v) and len({r['prompt_sha256'] for r in v})==1]
            same_runtime = [v for v in same_prompt if all(r['model_metadata'].get('verified_runtime_id') and
                            r['model_metadata'].get('reasoning_setting') for r in v) and
                            len({(r['model_metadata']['verified_runtime_id'],r['model_metadata']['reasoning_setting']) for r in v})==1]
            out['udt'].append({'benchmark':benchmark,'model':model,'listed_runs':len(rs),
                'transcripts':sum(r['udt_requested'] is not None for r in rs),
                'request_runs':sum(r['udt_requested'] is True for r in rs),
                'request_tasks':sorted({r['task'] for r in rs if r['udt_requested']}),
                'requests':sum(r['udt_request_count'] or 0 for r in rs),
                'job_linked_runs':sum(bool(r['udt_matched_job_ids']) for r in rs),
                'job_linked_tasks':sorted({r['task'] for r in rs if r['udt_matched_job_ids']}),
                'success_linked_runs':sum(bool(r['udt_matched_success_ids']) for r in rs),
                'unparsed_representations':sum(r['udt_unparsed_representations'] for r in rs),
                'complete_cells':len(complete),'zero_request_cells':sum(not any(r['udt_requested'] for r in v) for v in complete),
                'all_request_cells':sum(all(r['udt_requested'] for r in v) for v in complete),
                'variable_request_cells':len(varied),'variable_same_prompt':len(same_prompt),
                'variable_same_prompt_runtime_reasoning':len(same_runtime),
                'variable_cells':[{'task':v[0]['task'],'model':v[0]['model'],'run_ids':[r['run_id'] for r in v]} for v in varied]})
        # Task specification size is pre-execution, but is not a validated difficulty measure.
        for condition in builder.CONDITIONS:
            by_task = defaultdict(list)
            for r in runs:
                if r['benchmark']==benchmark and r['model'] in builder.COMMON and r['condition']==condition:
                    by_task[r['task']].append(r)
            complete=[]
            for task,rs in by_task.items():
                field = 'has_error' if condition=='galaxy' else 'has_nonzero_shell'
                if len(rs)!=9 or any(r[field] is None for r in rs):
                    continue
                complete.append({'task':task,'cluster':rs[0]['cluster'],'prompt_words':rs[0]['prompt_words'],
                                 'marker_rate':st.mean(r[field] for r in rs),
                                 'median_jobs':st.median(r['jobs'] for r in rs) if condition=='galaxy' else None,
                                 'job_error_fraction':sum(r['errors'] for r in rs)/sum(r['jobs'] for r in rs)
                                    if condition=='galaxy' and sum(r['jobs'] for r in rs)>0 else None})
            out['complexity'].append({'benchmark':benchmark,'condition':condition,'exposure':'Prompt word count',
                'response':'Runs with Galaxy job error' if condition=='galaxy' else 'Runs with nonzero shell exit',
                'statistics':correlation_interval(builder,complete,'prompt_words','marker_rate','length_'+benchmark+condition),'tasks':complete})
            if condition=='galaxy':
                valid=[r for r in complete if r['job_error_fraction'] is not None]
                out['complexity'].append({'benchmark':benchmark,'condition':condition,'exposure':'Median recorded non-fetch jobs/run',
                    'response':'Error jobs / recorded jobs','statistics':correlation_interval(builder,valid,'median_jobs','job_error_fraction','workload_'+benchmark),'tasks':valid})
    return out


def render(builder, benchmark, table, runs, cells, jobs, results):
    deep=results['deep']; fmt, frac, ci=builder.fmt,builder.frac,builder.ci
    labels,env=builder.LABELS,builder.ENV
    def rs(b, condition=None, model=None):
        return [r for r in runs if r['benchmark']==b and r['model'] in builder.MODELS[b] and
                (condition is None or r['condition']==condition) and (model is None or r['model']==model)]
    if benchmark=='BixBench50':
        tasks=defaultdict(dict)
        for task in sorted({r['task'] for r in rs(benchmark)}):
            for cond in builder.CONDITIONS:
                tasks[task][cond]=sum(r['score'] for r in rs(benchmark,cond) if r['task']==task)
        exclusive={cond:[t for t,v in tasks.items() if v[cond]>0 and v[next(x for x in builder.CONDITIONS if x!=cond)]==0] for cond in builder.CONDITIONS}
        rows=[]
        for cond in builder.CONDITIONS:
            if not exclusive[cond]:
                rows.append([env[cond],'None','0/50 tasks','No task met the specified exclusive-success rule'])
            for task in exclusive[cond]:
                rows.append([env[cond],builder.task_link(benchmark,task),
                             f"Galaxy {int(tasks[task]['galaxy'])}/15; open-ended code {int(tasks[task]['open_ended_code'])}/15",
                             'Version-dependent relative composition variability; see B13'])
        table('B11','Model capacity: tasks accepted in only one execution condition',
              ['Exclusive condition','Task','Observed acceptance','Explanation supported by the archive'],rows,
              'Exact rule: at least one accepted replicate across the five configurations in one condition and zero across all 15 runs in the other. '
              'Galaxy-only: zero tasks. Open-ended-code-only: one task, bix-45-q1. This is a task-level set comparison, not a test of superiority. '
              'Relative composition variability is the alignment statistic requested in the task. Model-specific counts are shown next.')
        rows=[]
        for m in builder.MODELS[benchmark]:
            values=[sum(r['score'] for r in rs(benchmark,cond,m) if r['task']=='bix-45-q1') for cond in builder.CONDITIONS]
            rows.append([labels[m],f'{int(values[0])}/3',f'{int(values[1])}/3'])
        table('B12','Model dependence of the exclusive open-ended-code success',['Configuration','Galaxy accepted','Open-ended code accepted'],rows,
              'Single-task description: all 15 Galaxy answers were rejected, although all 45 retained non-fetch Galaxy jobs had state ok. '
              'An environment-wide missing execution capability is therefore not established. No benchmark-wide interval is estimated from one task.')
        table('B13','Why bix-45-q1 differs: a version contrast retained within one original run',
              ['Recorded analysis / source','Alignments: animal / fungal','Mann-Whitney statistic','Task p-value','Original final-answer status'],[
              ['Open-ended code, Sol replicate 1, current PhyKIT calculation; event source line 24','241 / 255','5,483.5','1.5197572608715265e-56','Matches the rejected Galaxy value'],
              ['Same run, PhyKIT 2.0.3 reconstruction; event source line 33','241 / 255','6,115','7.6967608298013025e-54','Matches the accepted submitted value'],
              ['Same run, direct PhyKIT 2.0.3 check; event source line 45','241 / 255','6,115','7.6967608298013025e-54','Saved output confirms reconstruction agreement'],
              ['Galaxy, Sol replicate 1; PhyKIT metrics and rank-test wrappers','241 / 255','Not extracted here','1.5197572608715265e-56','Rejected']],
              'These p-values are outputs of the biomedical task, not tests of an environment effect. The recorded checks use rounded per-alignment values '
              'and two-sided asymptotic/automatic Mann-Whitney tests with continuity correction. The agent attributed the change to version-dependent '
              'gap/ambiguous-residue handling; the archived numerical contrast supports a version explanation for this run. '
              'It does not prove the intended reference release, adjudicate biological validity, or explain every rejected run. '
              'Source: [task evidence](BixBench_50/analysis/bix-45-q1/history_analysis_evidence.json), '
              '`open_ended_code_codex_gpt_5_6_sol_r1`, source lines 24, 33 and 45; trace messages and hashes are in `results.deep.case_sources`. '
              'No calculation was replayed. The within-run version contrast narrows the possible explanation beyond a generic input-assembly difference.')
        performance_panel(builder,benchmark,table,runs,cells,'B14')
        rows=[[env[x['condition']],labels[x['model']],ci(x['accuracy']),ci(x['tokens']),
               f"{ci(x['job_error_difference'])}; {len(x['error_pairs'])} tasks" if x['job_error_difference'] else 'Not applicable']
              for x in deep['model_comparisons']]
        table('B15','Model trade-off: acceptance difference and token use relative to GPT-5.5',
              ['Environment','Compared configuration','Acceptance difference (percentage points) [95% interval]',
               'Input-token ratio to GPT-5.5 [95% interval]','Galaxy error-run difference (percentage points) [95% interval]; paired tasks'],rows,
              'Reference is GPT-5.5 within the same environment and the same 50 tasks. Accuracy differences average all three replicates; '
              'token ratios divide task medians of three replicates and are then summarized by the median ratio. '
              'Error-run differences use the subset of tasks with all six detailed Galaxy runs and compare proportions with at least one error; '
              'the error column can therefore have a different task population from the other columns. '
              'Intervals use 20,000 paired capsule bootstrap resamples, seed 20260922. They are exploratory and pointwise. '
              'A difference interval containing zero does not establish equal performance or non-inferiority. '
              'Within Galaxy, Sol and Luna consumed more input tokens than GPT-5.5 without a resolved acceptance advantage; '
              'both DeepSeek configurations consumed more and had lower observed acceptance. These are selected-corpus associations, not general model rankings. '
              'Absolute pooled medians in B14 and median paired ratios here can order models differently because they are different estimands.')
        paired=defaultdict(dict)
        for cell in cells:
            if cell['benchmark']=='BixBench50':
                paired[cell['task'],cell['model']][cell['condition']]=cell['accepted']
        rows=[]
        for (task,model),counts in sorted(paired.items()):
            if bool(counts['galaxy'])==bool(counts['open_ended_code']):
                continue
            interpretation = ('Version contrast documented in B13' if task=='bix-45-q1' else
                              'Threshold / upstream gene-set differences discussed in B3' if task in ['bix-30-q3','bix-43-q2'] else
                              'Direction reverses between DeepSeek harnesses; mechanism unadjudicated' if task=='bix-26-q5' else
                              'Observed configuration-specific difference; mechanism unadjudicated')
            rows.append([builder.task_link('BixBench50',task),labels[model],f"{counts['galaxy']}/3",f"{counts['open_ended_code']}/3",interpretation])
        table('B16','Configuration-specific exclusive task successes hidden by pooling models',
              ['Task','Configuration','Galaxy accepted','Open-ended code accepted','Supported interpretation'],rows,
              'Same rule as B11, but now applied within a task and configuration: one or more accepted replicates versus none. '
              'All 13 qualifying pairs are shown: nine Galaxy-exclusive pairs and four open-ended-code-exclusive pairs out of 250. '
              'These do not contradict B11 because another configuration can succeed in the other environment. '
              'A one-of-three result is weak repeatability, not a stable platform advantage. Cells share tasks and cannot be treated as independent observations '
              'in a simple binomial test. Rows without an audited mechanism remain unresolved rather than being attributed to missing tools or model knowledge.')
    elif benchmark=='CompBio':
        performance_panel(builder,benchmark,table,runs,cells,'C9')
        task='odd-one-out-q1';rows=[]
        for m in builder.MODELS[benchmark]:
            for cond in builder.CONDITIONS:
                selected=[r for r in rs(benchmark,cond,m) if r['task']==task]
                answers=Counter(r['answer'] for r in selected)
                errs=[r for r in selected if r['has_error'] is not None]
                rows.append([labels[m],env[cond],'; '.join(f'{a}: {n}/3' for a,n in sorted(answers.items())),
                             frac(sum(r['has_error'] for r in errs),len(errs)) if errs else 'Not applicable','Unavailable'])
        table('C10','Outlier case: what can actually be said about biomedical knowledge?',
              ['Configuration','Environment','Submitted outlier index: replicate count','Runs with Galaxy job errors','Accepted answers'],rows,
              'The task asks which of ten tagAlign files comes from a different assay. Missing item scores prevent saying that most agents were wrong '
              'or assigning a biomedical-knowledge error rate. In GPT-5.5 Galaxy replicate 1, the trace records an unsuccessful external checksum lookup, '
              'then binned coverage correlations, chromosome distribution, strand correlation and transcription-start-site enrichment; it explicitly considers '
              'cell-line copy-number differences as an alternative explanation. These are documented diagnostic choices, not proof that the final index 9 is correct. '
              'Source: [task evidence](CompBio/analysis/odd-one-out-q1/history_analysis_evidence.json); trace lines 29, 30, 38 and 44 in `results.deep.case_sources`. '
              'Operational errors and uncertain scientific interpretation must remain separate.')
    else:
        cross_tables(builder,table,runs,cells,jobs,deep)


def performance_panel(builder,benchmark,table,runs,cells,label):
    rows=[]
    for model in builder.MODELS[benchmark]:
        for cond in builder.CONDITIONS:
            rs=[r for r in runs if r['benchmark']==benchmark and r['model']==model and r['condition']==cond]
            cs=[c for c in cells if c['benchmark']==benchmark and c['model']==model and c['condition']==cond]
            scored=all(r['score'] is not None for r in rs)
            consistent=sum(c['accepted']==3 for c in cs) if scored else sum(c['answer_distinct']==1 for c in cs)
            errors=[r for r in rs if r['has_error'] is not None]
            shells=[r for r in rs if r['has_nonzero_shell'] is not None]
            tokens=[r['input_tokens'] for r in rs if r['input_tokens'] is not None]
            rows.append([builder.LABELS[model],builder.ENV[cond],
                         builder.frac(sum(r['score'] for r in rs),len(rs)) if scored else 'Unavailable',
                         builder.frac(consistent,len(cs)),
                         builder.frac(sum(r['has_error'] for r in errors),len(errors)) if errors else 'Not applicable',
                         builder.frac(sum(r['has_nonzero_shell'] for r in shells),len(shells)),
                         f"{builder.fmt(st.median(tokens)/1e6,3)}; {len(tokens)}/{len(rs)}"])
    table(label,'Model comparison: capacity, consistency, operational burden and cost',
          ['Configuration','Environment','Accepted runs','Tasks with all accepted' if benchmark=='BixBench50' else 'Tasks with identical answer text',
           'Runs with Galaxy job error','Runs with nonzero shell exit','Median input tokens (millions); coverage'],rows,
          'Each task contributes three runs/configuration/environment. Accepted-answer reliability is used for BixBench; '
          'CompBio can only report answer-text consistency, never correctness. Galaxy job errors and nonzero shell exits are different instruments. '
          'A shell exit may be a probe or failed search; Galaxy analysis is often offloaded to server jobs, so fewer shell exits do not establish easier execution. '
          'Shell denominators require at least one numeric recorded exit code: the superseded Claude Code traces contain no numeric exit codes and are unavailable, not zero failures. '
          'Tokens describe archived primary turns, not full execution cost. Missing data are excluded with explicit denominators; all observed outcomes are included.')


def cross_tables(builder,table,runs,cells,jobs,deep):
    frac,fmt,ci=builder.frac,builder.fmt,builder.ci
    families=list(SOFTWARE_PATTERNS)
    rows=[]
    for family in families:
        counts=[]
        for benchmark in builder.FOLDERS:
            for cond in builder.CONDITIONS:
                rs=[r for r in runs if r['benchmark']==benchmark and r['model'] in builder.COMMON and r['condition']==cond and r['path_observed']]
                def present(r):
                    return any(family in t.lower() for t in r['galaxy_full_tool_ids'] if 'toolshed' in t) if cond=='galaxy' else family in r['software_command_indicators']
                counts.append(frac(sum(present(r) for r in rs),len(rs)))
        rows.append(['DESeq2 / PyDESeq2' if family=='deseq2' else family,*counts])
    table('X9','Common software families: installed Galaxy wrappers versus code-command indicators',
          ['Software family','BixBench Galaxy','BixBench open-ended code','CompBio Galaxy','CompBio open-ended code'],rows,
          'Three shared GPT configurations. Galaxy counts runs whose retained jobs name a Tool Shed wrapper from the family; '
          'open-ended code uses a declared command-name codebook, including PyDESeq2 as a DESeq2-family implementation. '
          'This inventory codebook is separate from the unchanged path-fingerprint vocabulary; shared family labels do not imply equivalent implementations or versions. '
          'Denominators require detailed histories or retrieved transcripts, respectively. '
          'Indicators are nonexclusive and their visibility differs: libraries inside custom tools can be hidden, and a command mention is not a verified invocation. '
          'This answers which families are observable in both conditions; it is not a fair count of equivalent scientific operations or proof of absent software.')
    rows=[]
    for x in deep['shell_comparisons']:
        pairs=x['pairs'];n=3*len(pairs)
        rows.append([x['benchmark'],len(pairs),frac(sum(p['galaxy'] for p in pairs),n),
                     frac(sum(p['open_ended_code'] for p in pairs),n),ci(x['estimate'])])
    table('X10','Environment comparison using a shared, limited operational marker',
          ['Benchmark','Complete task/configuration pairs','Galaxy: runs with nonzero shell exit','Open-ended code: runs with nonzero shell exit','Galaxy minus open-ended code (percentage points) [95% interval]'],rows,
          'Each pair requires six transcripts with at least one numeric shell exit code per run. The superseded Claude Code configuration is excluded because its exit codes are unobserved. '
          'Intervals resample capsules/tasks with all eligible configuration bundles. '
          'Only the shell channel is compared: searches, probes and package checks can return nonzero, while Galaxy job failures can be returned as successful API calls. '
          'Thus this marker does not answer whether Galaxy has more scientific failures or is intrinsically harder. '
          'Higher Galaxy input-token use (B7/C6), server-job errors (B4/C3) and concrete wrapper-binding friction (X15) are distinct, supported forms of burden.')
    rows=[]
    for x in deep['complexity']:
        rows.append([x['benchmark'],builder.ENV[x['condition']],x['exposure'],x['response'],x['statistics']['n'],ci(x['statistics'],3)])
    table('X11','Task specification size and recorded workload versus operational failure markers',
          ['Benchmark','Environment','Exposure','Response','Complete tasks','Spearman correlation [95% interval]'],rows,
          'Three shared GPT configurations; nine observed runs are required per task/environment. Prompt word count is a pre-execution task-description-size proxy, '
          'not a validated difficulty score. Median job count is a post-execution workload measure; retries increase it, creating reverse causation. '
          'The job response divides recorded errors by recorded jobs to reduce the automatic opportunity effect of simply counting failures. '
          'Intervals use 5,000 capsule/task bootstrap resamples, seed 20260922, with ties reranked within each resample. '
          'These exploratory, unadjusted associations cannot establish that task complexity causes errors. Independent difficulty labels, budgets and attempt-level chronology are needed.')
    rows=[]
    for x in deep['udt']:
        n=50 if x['benchmark']=='BixBench50' else 100
        rows.append([x['benchmark'],builder.LABELS.get(x['model'],'All configurations'),
                     frac(x['request_runs'],x['transcripts']),frac(len(x['request_tasks']),n),
                     f"{x['job_linked_runs']}/{x['request_runs']}",len(x['job_linked_tasks']),x['success_linked_runs']])
    table('X12','User-defined tools: explicit requests, tasks reached and linked execution',
          ['Benchmark','Configuration','Requesting runs / retrieved transcripts','Tasks with request','Runs with linked job / requesting runs','Tasks with linked job','Runs with linked successful job'],rows,
          'An explicit request is a run_galaxy_udt_and_wait event. Linked execution requires a declared GalaxyUserTool identifier matching a retained Galaxy job tool ID '
          'in the same run; success requires job state ok. Matching IDs supports linkage but does not establish exact chronology or authorship for inherited jobs. '
          'Requests alone do not prove submission or execution; unobserved requests are unknown. Four YAML-string representations are not parsed and remain linkage gaps. '
          'Jobs invoked through other interfaces can be missed; these are lower-bound detections, not an exhaustive custom-tool inventory. '
          'The proposed 30-40% claim depends on its denominator: task coverage, run use and confirmed execution are not interchangeable. '
          'Official [user-defined tool documentation](https://galaxyproject.org/tools/user-defined-tools/) describes this capability and recommends existing published tools when suitable.')
    rows=[]
    for x in deep['udt']:
        rows.append([x['benchmark'],builder.LABELS.get(x['model'],'All configurations'),x['complete_cells'],
                     x['zero_request_cells'],x['variable_request_cells'],x['all_request_cells'],
                     f"{x['variable_same_prompt']} / {x['variable_same_prompt_runtime_reasoning']}"])
    table('X13','Are user-defined tool choices stable across repeat executions?',
          ['Benchmark','Configuration','Observable triplicate cells','No replicate requests','Some request','All request','Variable cells: same prompt / same prompt + runtime + reasoning'],rows,
          'One cell is one task/configuration; all three transcripts must be present. The three usage categories partition cells. '
          'Same prompt means identical archived prompt-file hashes; the stricter subset additionally requires a single verified runtime ID and reasoning setting. '
          'Variation is compatible with stochastic or context-dependent choice, not proof of randomness: input provenance, tool catalogs, prior state, '
          'campaign selection and services were not controlled. Missing runtime metadata is not treated as verified agreement.')
    features=[('search_galaxy_tools','Tool discovery'),('inspect_galaxy_tool','Parameter/schema inspection'),
              ('inspect_galaxy_history','History inspection'),('run_galaxy_tool_and_wait','Ordinary-tool submission requests'),
              ('run_galaxy_udt_and_wait','User-defined-tool submission requests'),('wait_for_galaxy_jobs','Explicit waiting/status requests')]
    rows=[]
    for event,description in features:
        values=[]
        for benchmark in builder.FOLDERS:
            rs=[r for r in runs if r['benchmark']==benchmark and r['condition']=='galaxy' and r['coverage']['agent_transcript']=='retrieved']
            values.append(frac(sum(r['interface_calls'].get(event,0)>0 for r in rs),len(rs)))
        rows.append([description,*values])
    table('X14','Workbench capabilities visibly exercised by agents',['Recorded interface operation','BixBench runs','CompBio runs'],rows,
          'All Galaxy configurations with retrieved transcripts; nonexclusive run-level counts of named calls. A completed helper call does not by itself prove '
          'job success or scientific validity. History creation/copying is not universally measured by these named helpers; it is documented in selected traces '
          'and must not be inferred for every run from a linked history. These counts support feature use, not improved human readability.')
    table('X15','Why choose a user-defined tool? Distinguishing capability gaps from interface friction',
          ['Case and configuration','Observed evidence','Classification / inference','What it does not establish'],[
          [builder.task_link('BixBench50','bix-11-q1')+'; GPT-5.5 Galaxy replicate 1',
           'Native PhyKIT found; transcript reports rejected parameter binding, then wrong resolved inputs, then a user-defined wrapper',
           'Agent-reported interface/parameter-binding workaround; package capability existed',
           'Not evidence that Galaxy lacked a treeness tool'],
          [builder.task_link('BixBench50','bix-11-q1')+'; GPT-5.5 Galaxy replicate 2',
           'Accepted answer, two retained PhyKIT jobs, no explicit user-defined-tool request',
           'Counterexample to task-wide necessity of a user-defined tool',
           'Does not show the same interface state or catalog across replicates'],
          [builder.task_link('BixBench50','bix-11-q1')+'; GPT-5.5 Galaxy replicate 3',
           'Native PhyKIT found; agent chooses a custom tool for archive handling, group medians and final difference',
           'Agent-reported composition/data-shape preference',
           'Not proof that native composition was impossible or that the decision was random'],
          [builder.task_link('CompBio','borzoi-basic-q1')+'; GPT-5.5 Galaxy replicate 1',
           'Agent states no ready-made TensorFlow parameter-counting wrapper was exposed, then requests a custom tool',
           'Agent-reported exposed-wrapper gap; unverified catalog absence',
           'No exhaustive contemporaneous catalog or alternative-workflow adjudication']],
          'Purposive mechanism cases, not percentages of all custom-tool use. `results.deep.case_sources` retains exact trace paths, hashes and line-numbered '
          'agent statements. The native-only treeness counterexample is verified from task evidence. '
          'To distinguish necessity from choice prospectively, snapshot catalog/search results, record rejected alternatives and parameter errors, '
          'then compare repeated matched tasks with a fixed tool catalog and an independently validated native workflow. '
          'The current archive cannot estimate the fraction used because no suitable Galaxy tool existed.')
    # Restrict to identical submitted text and observable path variation, avoiding a correctness shortcut.
    rows=[]
    for benchmark in builder.FOLDERS:
        for cond in builder.CONDITIONS:
            selected=[c for c in cells if c['benchmark']==benchmark and c['condition']==cond and c['eligible']]
            identical=[c for c in selected if c['answer_distinct']==1]
            varied=[c for c in identical if c['agreement']!='identical']
            rows.append([benchmark,builder.ENV[cond],len(selected),len(identical),len(varied),
                         sum(c['accepted']==3 for c in varied) if benchmark=='BixBench50' else 'Unavailable'])
    table('X16','Different recorded paths, identical submitted answers: does the observation hold?',
          ['Benchmark','Environment','Observable path cells','Identical-answer cells','Identical answer with varied paths','Of these, all answers accepted'],rows,
          'All benchmark-specific paired configurations; three observed nonempty fingerprints are required. Answer identity uses exact archived submitted text '
          'after outer whitespace removal; it does not merge numerically close strings. Path variation means tool-ID/command-token sets differ, '
          'not independently adjudicated biological algorithms. BixBench can confirm acceptance; CompBio cannot confirm validity. '
          'The counts support multiple observed execution routes to the same answer, with these measurement limits.')
    table('X17','Testing the five motivating observations',
          ['Proposed observation','Evidence-based verdict','Supporting tables / unresolved experiment'],[
          ['Agents can operate core Galaxy features','Supported for recorded discovery, inspection and submission requests; successful jobs separately observed','X14; B4/C3. Universal history creation and Galaxy-only execution still require event attribution'],
          ['Different approaches produce the same valid result','Supported for different recorded paths and identical accepted BixBench answers; biological method equivalence unadjudicated','X16; B6. CompBio item-level validity remains unavailable'],
          ['Custom tools fill missing Galaxy capabilities in 30-40% of tasks','Not supported as a task-rate or necessity claim; request/task/execution denominators differ','X12-X15. Native capability, parameter binding and workflow composition are distinct explanations'],
          ['Wrong outlier answers reflect missing knowledge and technical mistakes','Cannot quantify from this archive; item-level correctness and independent error adjudication are absent','C10. Observed diagnostic choices contradict a blanket claim that agents found no useful analysis'],
          ['Galaxy makes human validation easier','Plausible interface benefit; not measured in these benchmark records','X7. Randomized blinded reconstruction-time, error and agreement study required']],
          'These verdicts evaluate the motivating statements, not a prespecified hypothesis set. All statistical intervals are exploratory. '
          'Model capacity, workbench functionality, operational friction, scientific correctness and execution cost remain separate endpoints.')
    rows=[]
    for benchmark,family,signature,pattern,interpretation in ERROR_RULES:
        selected=[j for j in jobs if j['benchmark']==benchmark and j['status']=='error' and
                  (j['tool'].split('/')[-2] if 'toolshed' in j['tool'] else j['tool'])==family]
        matches=[j for j in selected if signature in j['specific_error_signatures']]
        rows.append([benchmark,family,signature,frac(len(matches),len(selected)),interpretation])
    table('X18','Specific recurring diagnostics and the mechanisms they suggest',
          ['Benchmark','Tool family','Retained diagnostic','Matching / family error jobs','Interpretation and actionable check'],rows,
          'Counts are deduplicated creating jobs; tool versions are pooled within the named family. The denominator contains every error job for that family, '
          'including missing/truncated diagnostics. Exact regex rules and matching job/source-event IDs are retained in the analysis JSON. '
          'These messages support input, datatype, identifier and design-validation hypotheses; they do not alone assign blame to the model, wrapper or platform. '
          'Multiple signatures may overlap. No claim is made that a tool always fails: the diagnostic probe with 57/57 error states in X6 is not a biomedical-analysis success endpoint.')
