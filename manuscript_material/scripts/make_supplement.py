"""Supplementary Tables, Supplementary Data and the Supplementary Information PDF.

Run from the repository root after build_data.py:  python manuscript_material/scripts/make_supplement.py
Outputs (manuscript_material/supplementary/):
  Supplementary_Tables.xlsx          archive tables renumbered in order of first citation, plus new audit tables
  Supplementary_Table_crosswalk.csv  Supplementary Table number <-> archive ID <-> where the draft cites it
  Supplementary_Data_1..3.xlsx       per-run summaries, failed MCP calls, detected parameter substitutions
  Supplementary_Information.pdf      Supplementary Notes 1-9 and legends for every table and data file
Nothing is regraded, no agent code is executed and no Galaxy server is contacted.
"""
import collections
import csv
import gzip
import json
import os
import re
import statistics as st

import pandas as pd
from openpyxl import Workbook
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'manuscript_material')
SUP = os.path.join(OUT, 'supplementary')
V2 = os.path.join(ROOT, 'analysis_reports', 'galaxy_improvement_20260924', 'v2_trace_friction')
os.makedirs(SUP, exist_ok=True)

A = json.load(open(os.path.join(ROOT, 'BixBench50_CompBio_analysis', 'analysis.json')))
T = A['tables']
D = json.load(open(os.path.join(OUT, 'source_data', 'figure_data.json')))
LEDGER = json.load(open(os.path.join(V2, 'ledger.json')))
SUMS = [json.loads(l) for l in gzip.open(os.path.join(OUT, 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt')]
BENCH = ['BixBench50', 'CompBio', 'IWC']
BLABEL = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
CFG = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
       'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
       'codex_deepseek_v4_pro': 'DeepSeek V4 Pro',
       'deepseek_v4_pro_via_claude_code_superseded': 'DeepSeek V4 Pro (Claude Code, superseded)',
       'codex_gpt_6_astra': 'GPT-6 Astra'}
ENV = {'open_ended_code': 'Open-ended code', 'galaxy': 'Galaxy'}  # reference condition first everywhere
ENV_ORDER = {'open_ended_code': 0, 'galaxy': 1, 'Open-ended code': 0, 'Galaxy': 1}
CAUSE_NAME = {'SPEC': 'Task under-specified or reference ambiguous', 'RIGOR': 'Statistical or reasoning error',
              'EVALUATOR': 'Evaluator rejected a correct answer', 'KNOWLEDGE': 'Missing domain knowledge',
              'PLATFORM': 'Platform or tool defect', 'HARNESS': 'No answer submitted', 'CONTRACT': 'Output format violated'}
RUN_CFG = {'GPT-5.5': 'GPT-5.5', 'Sol': 'GPT-5.6 Sol', 'Luna': 'GPT-5.6 Luna', 'DS-Codex': 'DeepSeek V4 Pro',
           'DS-ClaudeCode': 'DeepSeek V4 Pro (Claude Code harness, superseded)'}


def load_block(path, start, end):
    """Load constants and functions from an audit script without running its data loaders."""
    src = open(path).read()
    a = src.index(start)
    ns = {'re': re, 'collections': collections, 'json': json}
    exec(src[a:src.index(end, a)], ns)
    return ns


TAXO = load_block(os.path.join(V2, 'taxonomy.py'), 'RULES = [', 'def main')
VAR = load_block(os.path.join(V2, 'variability.py'), 'SH = {', 'def main')
SECRET = re.compile(r'(?i)(api[_-]?key|x-api-key|authorization|password|secret|bearer)(["\'\s:=]+)([^\s"\',}]+)')


def clean(s, limit=2000):
    """Strip Markdown, redact anything shaped like a credential and cap the length for Excel."""
    s = '' if s is None else str(s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', lambda m: f'{m.group(1)} ({m.group(2)})' if m.group(2).startswith('http') else m.group(1), s)
    s = s.replace('**', '').replace('`', '')
    s = SECRET.sub(lambda m: m.group(1) + m.group(2) + '[REDACTED]', s)
    s = ILLEGAL_CHARACTERS_RE.sub('', s)
    return s if len(s) <= limit else s[:limit - 1] + '…'


# =====================================================================================================
# New tables produced by this audit
# =====================================================================================================
def t_ledger():
    rows = []
    for x in sorted(LEDGER, key=lambda x: (x['b'], x['task'], ENV_ORDER[x['cond']], x['run'])):
        _, cfg, rep_ = x['run'].split(' ')
        rows.append({'Benchmark': 'BixBench-Verified-50' if x['b'] == 'BixBench' else 'IWC', 'Task': x['task'],
                     'Environment': ENV[x['cond']], 'Configuration': RUN_CFG[cfg], 'Replicate': int(rep_[1:]),
                     'Submitted answer or score': clean(x['ans'], 300), 'Decision point that determined the outcome': clean(x['d']),
                     'Primary cause': CAUSE_NAME[x['p']], 'Secondary cause': CAUSE_NAME.get(x['s'], ''), 'Confidence': x['c']})
    return [('', pd.DataFrame(rows))]


def t_proxy():
    runs = [r for r in A['runs'] if r['benchmark'] == 'CompBio']
    norm = lambda a: (a or '').strip().lower().replace(' ', '')
    tasks = sorted({r['task'] for r in runs})
    modal = {t: collections.Counter(norm(r['answer']) for r in runs if r['task'] == t).most_common(1)[0] for t in tasks}
    per_task = []
    dev = collections.Counter()
    for t in tasks:
        ans, n = modal[t]
        strong = n >= 20
        g = sum(1 for r in runs if r['task'] == t and r['condition'] == 'galaxy' and norm(r['answer']) != ans) if strong else None
        c = sum(1 for r in runs if r['task'] == t and r['condition'] == 'open_ended_code' and r['model'] != 'codex_gpt_6_astra'
                and norm(r['answer']) != ans) if strong else None
        if strong:
            dev['galaxy'] += g
            dev['code'] += c
        per_task.append({'Task': t, 'Runs giving the most common answer (of 25)': n, 'Strong consensus (20 or more of 25)': 'yes' if strong else 'no',
                         'Open-ended-code runs deviating (of 12; GPT-6 Astra excluded)': c, 'Galaxy runs deviating (of 12)': g})
    by = collections.defaultdict(dict)
    for r in runs:
        by[(r['model'], r['condition'], r['replicate'])][r['task']] = norm(r['answer'])
    cb = json.load(open(os.path.join(ROOT, 'CompBio', 'compBio_overview_audit.json')))['score_vectors']
    vec = []
    for v in cb:
        if not v.get('answers_compared'):
            continue
        key = (v['model'], v['condition'], int(v['replicate'][1:]))
        vec.append({'Configuration': CFG.get(v['model'], v['model']), 'Environment': ENV[v['condition']], 'Replicate': int(v['replicate'][1:]),
                    'Archived vector score (of 100)': v['score'], 'Score provenance': v['score_type'],
                    'Answers matching cross-run consensus (of 100)': sum(1 for t, a in by[key].items() if a == modal[t][0])})
    vdf = pd.DataFrame(vec).sort_values('Environment', key=lambda c: c.map(ENV_ORDER), kind='stable')
    err = vdf['Answers matching cross-run consensus (of 100)'] - vdf['Archived vector score (of 100)']
    summary = pd.DataFrame([{'Vectors with retained answers': len(vdf), 'Mean absolute error': round(err.abs().mean(), 2),
                             'Mean bias (proxy − archived)': round(err.mean(), 2),
                             'Strong-consensus tasks': sum(1 for t in tasks if modal[t][1] >= 20),
                             'Galaxy deviations on strong-consensus tasks': dev['galaxy'],
                             'Open-ended-code deviations on strong-consensus tasks': dev['code']}])
    summary = summary[['Vectors with retained answers', 'Mean absolute error', 'Mean bias (proxy − archived)', 'Strong-consensus tasks',
                       'Open-ended-code deviations on strong-consensus tasks', 'Galaxy deviations on strong-consensus tasks']]
    return [('a | Validation summary', summary), ('b | Proxy against each archived vector', vdf), ('c | Consensus support per task', pd.DataFrame(per_task))]


def t_udt():
    s = D['scan']
    us = s['udt_status']
    lab = {'ok': 'ok', 'failed': 'Job failed', 'udt_creation_failed': 'Tool creation failed', 'None': 'No status returned'}
    a = pd.DataFrame([{'Status returned': lab.get(k, k), 'UDT calls': v, 'Share (%)': round(100 * v / sum(us.values()), 1)}
                      for k, v in sorted(us.items(), key=lambda kv: -kv[1])])
    ph = {'udt': 'User-defined tool', 'tool': 'Installed wrapper', 'wait': 'Job wait call'}
    pn = {'pre_execution_or_command_rendering': 'Before execution or during command rendering', 'command_runtime': 'Command runtime'}
    b = pd.DataFrame([{'Execution route': ph.get(k.split('|')[0], k.split('|')[0]), 'Failure phase': pn.get(k.split('|')[1], k.split('|')[1]),
                       'Diagnostic text returned': 'stderr or message' if k.split('|')[2] == 'stderr' else 'none',
                       'Failed jobs': v} for k, v in sorted(s['failed_phase'].items(), key=lambda kv: -kv[1])])
    an = s['after_notext']
    c = pd.DataFrame([{'Next tool-run call after a failure with no diagnostic text': ('Identical payload resubmitted' if k.startswith('identical') else 'Modified payload'),
                       'Outcome of that call': 'Failed again' if k.endswith('failed') else 'Other outcome', 'Calls': v}
                      for k, v in sorted(an.items())])
    pr = s['probe']
    d = pd.DataFrame([{'Benchmark': BLABEL[bm], 'Runs with probe UDTs': pr.get(f'{bm}|runs', 0), 'Probe UDT calls': pr.get(f'{bm}|calls', 0)}
                      for bm in ('BixBench50', 'CompBio')])
    return [('a | Status returned by UDT calls', a), ('b | Failed jobs by route, phase and diagnostic', b),
            ('c | What agents did after a diagnostic-free failure', c), ('d | Probe UDTs written to bisect template rendering', d)]


TAX_DEF = {
    'A1': ('Tool description needs a history', 'Tool inspection returned "History unavailable" because no history identifier was supplied.'),
    'A2': ('Tool identifier not found', 'A tool identifier that does not resolve on the server (usually guessed or truncated).'),
    'A3': ('Conditional option structure', 'Nested conditional/repeat parameters submitted with a key structure the server rejects.'),
    'A4': ('Parameter value or data type', 'A value, option, format or collection type rejected by tool-state validation.'),
    'A5': ('Dataset or history identifier', 'Wrong, foreign, truncated or undecodable dataset/history identifiers, or histories not owned by the user.'),
    'A6': ('User-defined tool definition', 'User-defined tool representation rejected at creation (schema, pattern, discriminator or extra fields).'),
    'A7': ('Upload or file type', 'Unknown extension or failed upload/fetch.'),
    'A8': ('Server, connection or rate limit', 'HTML error pages, uncaught server exceptions, transport closure, time-outs, rate limits.'),
    'B1': ('User-defined tool: software missing', 'Package or executable absent from the container chosen for a user-defined tool.'),
    'B2': ('Job failed, no error message', 'A created job ended in error and no error message was returned to the agent.'),
    'B3': ('Job failed with error message', 'A created job failed while running and returned an error message or traceback.'),
    'B4': ('File format, compression or index', 'Input not parseable in the declared format, compression mismatch or missing index.'),
    'B5': ('Memory or compute limit', 'Memory exhaustion or killed process.'),
    'Z': ('Unclassified', 'Failure text matched no rule; retained for completeness.'),
}


def t_taxonomy():
    inv = D['inventory']
    rules = {name.split()[0]: rx for name, rx in TAXO['RULES']}
    ex = {}
    for s in SUMS:
        if s['condition'] != 'galaxy':
            continue
        for er in s.get('errors') or []:
            code = TAXO['classify'](er).split()[0]
            if code not in ex and (er.get('err') or '').strip():
                ex[code] = clean(er['err'], 220)
    rows = []
    for code, (name, definition) in TAX_DEF.items():
        cnt = {b: sum(v for k, v in D['ed3b'][b].items() if k.split()[0] == code) for b in BENCH}
        row = {'Class': code, 'Name': name, 'Stage': 'Before a job exists' if code.startswith('A') else ('After job creation' if code.startswith('B') else '—'),
               'Definition': definition}
        for b in BENCH:
            row[f'{BLABEL[b]} calls'] = cnt[b]
        row['Total calls'] = sum(cnt.values())
        for b in BENCH:
            row[f'{BLABEL[b]} per 1,000 MCP calls'] = round(1000 * cnt[b] / inv[b]['mcp_calls'], 2)
        row['Detection rule (regular expression, first match wins)'] = rules.get(code, 'no rule matched')
        row['Example error text'] = ex.get(code, '')
        rows.append(row)
    df = pd.DataFrame(rows)
    tot = {'Class': 'All', 'Name': 'All failed calls', 'Stage': '', 'Definition': ''}
    for b in BENCH:
        tot[f'{BLABEL[b]} calls'] = int(df[f'{BLABEL[b]} calls'].sum())
    tot['Total calls'] = int(df['Total calls'].sum())
    denom = {'Class': 'Denominator', 'Name': 'Galaxy MCP calls', 'Stage': '', 'Definition': ''}
    for b in BENCH:
        denom[f'{BLABEL[b]} calls'] = inv[b]['mcp_calls']
    denom['Total calls'] = sum(inv[b]['mcp_calls'] for b in BENCH)
    df = pd.concat([df, pd.DataFrame([tot, denom])], ignore_index=True)
    sel = lambda p: df[df['Class'].str.fullmatch(p)]
    stage = pd.DataFrame([{'Stage': st_, **{BLABEL[b]: int(sel(p)[f'{BLABEL[b]} calls'].sum()) for b in BENCH}, 'Total': int(sel(p)['Total calls'].sum())}
                          for st_, p in [('Before a job exists (A1–A8)', r'A\d'), ('After job creation (B1–B5)', r'B\d'), ('Unclassified', 'Z')]])
    return [('a | Stage totals', stage), ('b | Classes, definitions, counts and detection rules', df)]


def t_substitution():
    s = D['scan']
    rows = []
    for b in BENCH:
        stt = s['runtool_status'][b]
        tot = sum(stt.values())
        blk, exe = stt.get('validation_parameter_mismatch', 0), stt.get('parameter_mismatch', 0)
        mk = s['mismatch_kind']
        rows.append({'Benchmark': BLABEL[b], 'Tool-run calls (Codex harness)': tot, 'Executed as requested (ok)': stt.get('ok', 0),
                     'Would substitute or drop values; blocked before submission': blk,
                     'Executed with substituted or dropped values': exe, 'Any requested-vs-resolved difference': blk + exe,
                     'Share of tool-run calls (%)': round(100 * (blk + exe) / tot, 1),
                     'Blocked: explicit value substitution': mk.get(f'{b}|validation_parameter_mismatch|substituted', 0),
                     'Blocked: requested path missing': mk.get(f'{b}|validation_parameter_mismatch|dropped', 0),
                     'Executed: explicit value substitution': mk.get(f'{b}|parameter_mismatch|substituted', 0),
                     'Executed: requested path missing': mk.get(f'{b}|parameter_mismatch|dropped', 0)})
    a = pd.DataFrame(rows)
    tools = sorted(s['mismatch_tools'].items(), key=lambda kv: -sum(kv[1].values()))
    b_ = pd.DataFrame([{'Tool (short identifier)': t, 'Blocked before submission': v.get('validation_parameter_mismatch', 0),
                        'Executed with altered values': v.get('parameter_mismatch', 0), 'Total': sum(v.values())} for t, v in tools])
    ex = [('Datamash', 'operations|0|op_name', 'max', 'count'), ('Datamash', 'operations|0|op_column', '6', '1'),
          ('PhyKIT metrics', 'operation|selector', 'treeness', 'total_tree_length'), ('STAR-Fusion', 'genomeDir', 'hg38', 'apiMel4 (honey bee)'),
          ('STAR-Fusion', 'singlePaired|sPaired', 'paired', 'single'), ('Unzip', 'extract_options|target', 'all_regex', 'all'),
          ('DESeq2', 'factorLevel', 'DMSO', 'FactorLevel')]
    c = pd.DataFrame(ex, columns=['Tool', 'Parameter path', 'Requested value', 'Value in resolved Galaxy state'])
    return [('a | By benchmark', a), ('b | By tool', b_), ('c | Examples shown in Fig. 3e', c)]


def t_mixed():
    rows = []
    for key, v in D['fig4c_cells'].items():
        b, env, cfg = key.split('|')
        rows.append({'Benchmark': BLABEL[b], 'Environment': ENV[env], 'Configuration': cfg,
                     'All 3 replicates succeeded': v.get('all'), 'Non-unanimous triplicates': v.get('mixed', 0), 'All 3 replicates failed': v.get('none')})
    order = {c: i for i, c in enumerate(['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro', 'DeepSeek V4 Pro (Claude Code, superseded)'])}
    bord = {BLABEL[b]: i for i, b in enumerate(BENCH)}
    df = pd.DataFrame(rows).sort_values(['Benchmark', 'Environment', 'Configuration'],
                                        key=lambda c: c.map(order) if c.name == 'Configuration' else (c.map(ENV_ORDER) if c.name == 'Environment' else c.map(bord)))
    tot = df.groupby(['Benchmark', 'Environment'], sort=False)['Non-unanimous triplicates'].sum().reset_index()
    defs = pd.DataFrame([
        {'Benchmark': 'BixBench-Verified-50', 'Triplicates per configuration': 50,
         'Non-unanimous when': '1 or 2 of 3 replicates were accepted by the original evaluator',
         'All succeeded / all failed': '3 of 3 accepted / 0 of 3 accepted'},
        {'Benchmark': 'CompBioBench', 'Triplicates per configuration': D['compbio_strong_tasks'],
         'Non-unanimous when': '1 or 2 of 3 replicates matched the answer given by at least 20 of 25 runs (consensus proxy; Supplementary Note 7)',
         'All succeeded / all failed': '3 of 3 match / 0 of 3 match'},
        {'Benchmark': 'IWC', 'Triplicates per configuration': '9–10 (tasks scored for that configuration)',
         'Non-unanimous when': 'the three agreement scores differed by more than 0.05', 'All succeeded / all failed': 'not defined for a continuous endpoint'}])
    return [('a | Definitions', defs), ('b | Totals', tot), ('c | By configuration', df)]


def t_divergence():
    sh = VAR['SH']
    inv = {v: k for k, v in sh.items()}
    runs = {(s['task'], s['model'], s['condition'], s['replicate']): s for s in SUMS if s['benchmark'] == 'BixBench50'}
    rows = []
    for env, table in (('open_ended_code', VAR['C']), ('galaxy', VAR['G'])):
        for (task, cfg, rep), mech in sorted(table.items()):
            s = runs.get((task, inv[cfg], env, rep), {})
            rows.append({'Environment': ENV[env], 'Task': task, 'Configuration': CFG[inv[cfg]], 'Replicate': rep,
                         'What separated this replicate from its accepted siblings': MECH_NAME[mech], 'Submitted answer': clean(s.get('answer'), 200)})
    df = pd.DataFrame(rows)
    summ = df.groupby(['What separated this replicate from its accepted siblings', 'Environment']).size().unstack(fill_value=0).reset_index()
    summ = summ[['What separated this replicate from its accepted siblings'] + list(ENV.values())]
    for e in ENV.values():
        summ[f'{e} (%)'] = (100 * summ[e] / summ[e].sum()).round(1)
    return [('a | Summary', summ), ('b | Every rejected replicate in a non-unanimous triplicate', df)]


def t_discovery():
    s = D['scan']
    x14 = {r[0]: r[1:] for r in T['X14']['rows']}
    rows = []
    for k, b in enumerate(BENCH):
        sh = D['fig5b'][b]
        n = s['codex_galaxy_runs'][b]
        by = s['bypass'].get(b, {})
        a2 = sum(v for kk, v in D['ed3b'][b].items() if kk.startswith('A2'))
        rows.append({'Benchmark': BLABEL[b], 'Galaxy runs with primary traces (Codex harness)': n,
                     'Median share of MCP calls spent on tool search and inspection (%)': round(100 * st.median(sh['calls']), 1),
                     'Median share of returned characters from tool search and inspection (%)': round(100 * st.median(sh['chars']), 1),
                     'Tool identifiers inspected (summed over runs)': s['inspected'][b],
                     'Inspected but never executed': s['inspected_never_run'][b],
                     'Searches per run, median': s['searches'][b]['median'], 'Searches per run, maximum': s['searches'][b]['max'],
                     'Unresolvable tool identifiers (A2 failures)': a2,
                     'Galaxy API calls among Galaxy-track shell commands (%)': round(100 * s['api_shell_core'][b] / s['all_shell'][b], 1),
                     'Runs copying the seed history via BioBlend/REST': by.get('copy_history', 0) if b == 'BixBench50' else 'not applicable',
                     'Runs downloading outputs via BioBlend/REST': by.get('download', 0),
                     'Runs fetching tool schemas via BioBlend/REST': by.get('tool_schema', 0),
                     'Runs polling job status via BioBlend/REST': by.get('job_polling', 0),
                     'Runs submitting jobs via raw API': by.get('raw_submission', 0)})
    return [('', pd.DataFrame(rows).set_index('Benchmark').T.reset_index().rename(columns={'index': 'Measure'}))]


MECH_NAME = {'V1': 'Galaxy interface trap (silent default, output semantics or job not dispatched)',
             'V3': 'Different software version installed', 'V4': 'Domain convention or definition applied differently',
             'V5': 'Hand-written method instead of the library method (script, or user-defined tool in Galaxy)',
             'V6': 'Error in the final step (sorting, counting, units)', 'V7': 'No answer submitted',
             'V8': 'Answer retrieved from benchmark source files'}

NEW = {
    'NEW-ledger': ('Failure ledger: every rejected BixBench run and every IWC run scoring below 0.5', t_ledger,
                   'One row per run (246 BixBench rejections: 111 Galaxy, 135 open-ended code; 8 IWC runs below 0.5). Run labels give '
                   'environment (G, Galaxy; C, open-ended code), configuration (DS-Codex, DeepSeek V4 Pro via Codex; DS-ClaudeCode, DeepSeek V4 Pro via '
                   'the superseded Claude Code harness) and replicate. Causes: SPEC, task under-specified or reference depends on an unstated choice; '
                   'RIGOR, statistical or reasoning error (weak evidence accepted, thresholds or invariants ignored, wrong denominator); EVALUATOR, '
                   'grader rejected an equivalent answer or score records conflict; KNOWLEDGE, domain-knowledge gap; PLATFORM, Galaxy, MCP or tooling '
                   'defect (for code runs, local tooling); HARNESS, no answer written; CONTRACT, output-format or identifier violation. Confidence '
                   'levels are defined in Supplementary Note 6. Source: trace-by-trace adjudication (Supplementary Note 6).'),
    'NEW-proxy': ('CompBioBench cross-run consensus proxy and its validation against archived aggregate scores', t_proxy,
                  'CompBioBench retains aggregate score vectors but no item-level grades. For each task the modal normalized answer across its 25 runs '
                  'was taken as the consensus; tasks with at least 20 of 25 concordant runs are "strong consensus". The proxy is validated by '
                  'counting, for each archived vector with retained answers, how many of its 100 answers match the consensus (a). Deviations are '
                  'probable, not adjudicated, failures. Source: CompBio/compBio_overview_audit.json and archived answers.'),
    'NEW-udt': ('Reliability of the user-defined tool route', t_udt,
                'Counts are from Codex-harness Galaxy traces (1,908 runs), which return a structured status for every tool-run call. Failure phase '
                'and diagnostic availability come from the failure_diagnostic block of each failed job. A "no diagnostic" failure returns neither '
                'stderr nor a message. Probe UDTs are user-defined tools whose identifier names a probe, preflight, render, smoke, diagnostic or '
                'sanity check.'),
    'NEW-taxonomy': ('Classification of every failed Galaxy MCP call (A1–A8 before a job exists; B1–B5 after job creation)', t_taxonomy,
                     'All Galaxy-environment runs with primary traces, both harnesses. Rules are applied in the listed order to the error text plus '
                     'status of each failed call; the first match assigns the class. Rates use all Galaxy MCP calls in the benchmark as denominator. '
                     'Example strings are verbatim, truncated and screened for credentials.'),
    'NEW-substitution': ('Requested-versus-resolved parameter differences in tool-run calls', t_substitution,
                         'The benchmark MCP layer compares the parameters an agent requested with the tool state Galaxy resolved and reports '
                         'validation_parameter_mismatch (the harness blocked submission) or parameter_mismatch (the job executed). "Explicit value '
                         'substitution" means a requested value was replaced; "requested path missing" means a requested parameter path is absent '
                         'from the resolved state. Codex-harness traces only. Short tool identifiers are the Tool Shed repository names.'),
    'NEW-mixed': ('Non-unanimous triplicates by benchmark, environment and configuration', t_mixed,
                  'A triplicate is one task run three times with one configuration in one environment (called a "mixed cell" in the draft text '
                  'when non-unanimous). CompBioBench triplicates use the 82 strong-consensus tasks. '
                  'IWC cells are variable when the range of the three agreement scores exceeds 0.05. The superseded Claude Code configuration was '
                  'run on BixBench only.'),
    'NEW-divergence': ('What separated each rejected replicate from its accepted siblings in non-unanimous BixBench-Verified-50 triplicates',
                       t_divergence,
                       'Every rejected replicate in a non-unanimous BixBench-Verified-50 triplicate (45 open-ended-code replicates in 33 triplicates; '
                       '36 Galaxy replicates in 28 triplicates) was '
                       'compared call by call with the accepted replicate(s) of the same cell. The mechanism names what differed between the '
                       'replicates, not why the answer was wrong (for that, see the failure ledger). Definitions in Supplementary Note 8.'),
    'NEW-discovery': ('Control-plane burden and use of BioBlend or raw REST outside the MCP interface', t_discovery,
                      'Codex-harness Galaxy traces. Tool search and inspection = search_galaxy_tools and inspect_galaxy_tool calls. Returned '
                      'characters are the lengths of the tool results returned to the agent, used as a proxy for context consumed because token '
                      'totals cannot be attributed to individual calls. Inspected-but-never-executed counts distinct tool identifiers per run that '
                      'were inspected but not submitted through run_galaxy_tool_and_wait, summed over runs. Shell commands are counted as Galaxy '
                      'API calls when they use BioBlend or GalaxyInstance or call the Galaxy histories, datasets, jobs or tools API; bypass '
                      'operations are matched among commands referencing BioBlend, GalaxyInstance or any /api/ path. The seed history is '
                      'supplied only in BixBench.'),
}

# Order of first citation in the draft Results; NEW-* are tables introduced by this audit.
ORDER = [
    ('X1', 'Design paragraph: benchmarks analysed as separate strata'),
    ('B1', 'Section 1: BixBench acceptance (Fig. 2a)'), ('B10', 'Section 1: task coverage'), ('B11', 'Section 1: tasks solved in one condition only'),
    ('C1', 'Section 1: CompBioBench aggregate vectors (Fig. 2b)'), ('NEW-proxy', 'Section 1: consensus proxy, MAE 2.6 (Extended Data Fig. 1c,d)'),
    ('I1', 'Section 1: IWC agreement (Fig. 2c)'), ('I2', 'Section 1: IWC replicate dispersion'), ('I3', 'Section 1: IWC per task (Fig. 2d)'),
    ('X3', 'Section 1: cross-benchmark tool-set similarity (Extended Data Fig. 2a)'), ('X19', 'Section 1: non-utility Tool Shed share'),
    ('I4', 'Section 1: IWC difference rests on few runs'), ('I6', 'Section 1: IWC score provenance'),
    ('NEW-ledger', 'Section 1: "Supplementary failure ledger" (Fig. 2e)'),
    ('B12', 'Section 1: bix-45-q1 model dependence (Extended Data Fig. 2b)'), ('B13', 'Section 1: bix-45-q1 version contrast (Extended Data Fig. 2b)'),
    ('B8', 'Section 1: verifier modes, bix-43-q2 (Extended Data Fig. 2c)'), ('I5', 'Section 1: IWC runs below 0.5 (Extended Data Fig. 2d)'),
    ('C4', 'Section 2: biological domains'), ('X14', 'Section 2: workbench operations (Fig. 3a)'),
    ('B9', 'Section 2: top BixBench operations (Fig. 3b)'), ('C8', 'Section 2: top CompBioBench operations (Fig. 3b)'),
    ('I10', 'Section 2: top IWC operations (Fig. 3b)'), ('X12', 'Section 2: UDT requests and linked execution (Fig. 3c)'),
    ('X13', 'Section 2: UDT choice across replicates'), ('X15', 'Section 2: why UDTs were chosen'), ('I11', 'Section 2: IWC helper exposure'),
    ('NEW-udt', 'Section 2: UDT reliability (Extended Data Fig. 3a)'), ('B4', 'Section 2: BixBench execution evidence'),
    ('C3', 'Section 2: CompBioBench execution evidence'), ('I7', 'Section 2: IWC execution evidence'),
    ('X18', 'Section 2: recurring diagnostics (Fig. 3d)'), ('X5', 'Section 2: observable error messages (stderr retention)'),
    ('NEW-taxonomy', 'Section 2: A1–A8/B1–B5 taxonomy (Extended Data Fig. 3b); currently cited as X5'),
    ('X10', 'Section 2: shell-exit marker'), ('C7', 'Section 2: adjudicated recovery examples'),
    ('NEW-substitution', 'Section 2: silent parameter substitution (Fig. 3e; Extended Data Fig. 3c)'),
    ('X7', 'Section 2: engineering targets (Extended Data Fig. 3d)'),
    ('X9', 'Section 3: software families (Fig. 4a)'), ('I12', 'Section 3: IWC declared routes'),
    ('B5', 'Section 3: BixBench path agreement (Fig. 4b)'), ('C5', 'Section 3: CompBioBench path agreement (Fig. 4b)'),
    ('I8', 'Section 3: IWC path agreement (Fig. 4b)'), ('NEW-mixed', 'Section 3: mixed cells, i.e. non-unanimous triplicates (Fig. 4c; Extended Data Fig. 4a)'),
    ('X11', 'Section 3: prompt size and workload (Extended Data Fig. 4b)'), ('X16', 'Section 3: different paths, identical answers'),
    ('B6', 'Section 3: consistent path vs acceptance'), ('NEW-divergence', 'Section 3: divergence mechanisms (Fig. 4d)'),
    ('B7', 'Section 4: BixBench token ratio (Fig. 5a)'), ('C6', 'Section 4: CompBioBench token ratio'), ('I9', 'Section 4: IWC token ratio'),
    ('X2', 'Section 4: shared-configuration overhead (Extended Data Fig. 5a)'),
    ('NEW-discovery', 'Section 4: discovery burden and bypass (Fig. 5b; Extended Data Fig. 5b)'),
    ('B15', 'Section 4: token use vs acceptance (Fig. 5c)'), ('I13', 'Section 4: IWC configuration outcomes'),
]
UNCITED = [('B2', 'Suggest Section 3 (repeatability), beside B5'), ('B3', 'Suggest Section 1 (four near-universal failures; bix-45-q1, bix-30-q3)'),
           ('B14', 'Suggest Section 4 (Luna trajectory length)'), ('B16', 'Suggest Section 1 (coverage sentence)'),
           ('C2', 'Suggest Section 1 or 4 (usage completeness)'), ('C9', 'Suggest Section 3 or 4 (CompBioBench configuration outcomes)'),
           ('C10', 'Suggest Methods/limitations (biomedical-knowledge outlier)'), ('X4', 'Suggest Section 4 (run-level burden)'),
           ('X6', 'Suggest Section 2 (where error jobs concentrate)'), ('X8', 'Suggest Discussion (claim strength)'),
           ('X17', 'Suggest Discussion (six motivating observations)'), ('X20', 'Suggest design paragraph, beside X1')]


def xref(text):
    """Rewrite archive table identifiers inside legends (e.g. 'I3', 'B4/C3/I7') as Supplementary Table numbers."""
    return re.sub(r'\b([BCIX]\d{1,2})\b', lambda m: f'Supplementary Table {TABLE_NO[m.group(1)]}' if m.group(1) in TABLE_NO else m.group(1), text)


# =====================================================================================================
# Excel writing
# =====================================================================================================
HEAD = PatternFill('solid', fgColor='E8EEF6')
THIN = Side(style='thin', color='B8B8B8')


def write_sheet(wb, name, number, title, archive_id, blocks, legend):
    ws = wb.create_sheet(name)
    ws['A1'] = f'Supplementary Table {number} | {title}'
    ws['A1'].font = Font(bold=True, size=12)
    ws['A2'] = f'Archive ID: {archive_id}' if not archive_id.startswith('NEW') else 'New table produced by the trace-level audit'
    ws['A2'].font = Font(italic=True, size=9, color='555555')
    r = 4
    widths = collections.defaultdict(int)
    for sub, df in blocks:
        if sub:
            ws.cell(r, 1, sub).font = Font(bold=True, size=10)
            r += 1
        for j, h in enumerate(df.columns, 1):
            c = ws.cell(r, j, clean(h, 300))
            c.font, c.fill, c.border = Font(bold=True, size=9), HEAD, Border(bottom=THIN)
            c.alignment = Alignment(wrap_text=True, vertical='top')
            widths[j] = max(widths[j], min(40, len(str(h)) // 2 + 4))
        r += 1
        for row in df.itertuples(index=False):
            for j, v in enumerate(row, 1):
                v = None if (isinstance(v, float) and pd.isna(v)) else v
                c = ws.cell(r, j, clean(v) if isinstance(v, str) else v)
                c.font = Font(size=9)
                c.alignment = Alignment(wrap_text=True, vertical='top')
                widths[j] = max(widths[j], min(60, len(str(v)) + 2))
            r += 1
        r += 1
    ws.cell(r, 1, 'Notes').font = Font(bold=True, size=9)
    for para in [p for p in clean(legend, 30000).split('\n') if p.strip()]:
        r += 1
        c = ws.cell(r, 1, para)
        c.font = Font(size=9)
        c.alignment = Alignment(wrap_text=True, vertical='top')
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=max(6, min(len(widths), 10)))
        ws.row_dimensions[r].height = max(15, 12 * (len(para) // 140 + 1))
    for j, w in widths.items():
        ws.column_dimensions[get_column_letter(j)].width = max(10, w)
    ws.freeze_panes = 'A5' if not blocks[0][0] else None


def expand_names(x):
    """Spell out benchmark short names used in the archive tables."""
    x = re.sub(r'\bBixBench50\b|\bBix\b', 'BixBench-Verified-50', x)
    return re.sub(r'\bCompBio\b(?!Bench)', 'CompBioBench', x)


def code_first(headers, rows):
    """Put open-ended code before Galaxy wherever an archive table pairs them (reference condition first)."""
    headers, rows = list(headers), [list(r) for r in rows]
    i = 0
    while i < len(headers) - 1:  # adjacent 'Galaxy ...' / 'open-ended code ...' column pairs
        if headers[i].lower().startswith('galaxy') and headers[i + 1].lower().startswith('open-ended code'):
            headers[i], headers[i + 1] = headers[i + 1], headers[i]
            for r in rows:
                r[i], r[i + 1] = r[i + 1], r[i]
            i += 2
        else:
            i += 1
    for j, h in enumerate(headers):  # single columns reported as 'Galaxy / open-ended code'
        if 'Galaxy / open-ended code' in h and all(len(str(r[j]).split(' / ')) == 2 for r in rows):
            headers[j] = h.replace('Galaxy / open-ended code', 'open-ended code / Galaxy')
            for r in rows:
                a, b = str(r[j]).split(' / ')
                r[j] = f'{b} / {a}'
    env = next((j for j, h in enumerate(headers) if h.strip().lower() == 'environment'), None)
    rank = lambda v: 0 if str(v).strip().lower().startswith('open-ended') else (1 if str(v).strip().lower().startswith('galaxy') else None)
    if env is not None:  # within rows sharing the identifying columns before 'Environment', list open-ended code first
        out, i = [], 0
        while i < len(rows):
            j = i
            while j < len(rows) and rows[j][:env] == rows[i][:env]:
                j += 1
            block = rows[i:j]
            if all(rank(r[env]) is not None for r in block):
                block = sorted(block, key=lambda r: rank(r[env]))
            out += block
            i = j
        rows = out
    return headers, rows


def archive_blocks(tid):
    t = T[tid]
    headers, rows = code_first([expand_names(clean(h)) for h in t['headers']], [[expand_names(clean(x)) for x in row] for row in t['rows']])
    headers = [h[:1].upper() + h[1:] for h in headers]
    return [('', pd.DataFrame(rows, columns=headers))]


GLOSSARY = [
    ('Open-ended code', 'Reference condition: the agent works in an unrestricted shell and can install and run any software.'),
    ('Galaxy-mediated condition', 'The agent runs its analysis through the Galaxy server (usegalaxy.org) via a Model Context Protocol interface.'),
    ('Galaxy interface call (MCP call)', 'One call from the agent to the Galaxy interface, for example a tool search, a tool inspection or a job submission.'),
    ('User-defined tool (UDT)', 'Agent-written code packaged and run as a Galaxy tool, used when no installed tool fits or an installed tool fails.'),
    ('Installed tool (wrapper)', 'A tool installed on the Galaxy server from the Galaxy Tool Shed.'),
    ('Domain-analysis tool (non-utility Tool Shed job)', 'An installed tool that performs a biological or statistical analysis, as opposed to a file or table utility.'),
    ('Configuration', 'One language model with one agent harness (for example GPT-5.6 Sol under the Codex harness).'),
    ('Replicate', 'One of three independent runs of the same task with the same configuration and environment (not seed-matched).'),
    ('Triplicate (cell)', 'The three replicates of one task, one configuration and one environment.'),
    ('Non-unanimous triplicate (mixed cell)', 'A triplicate in which only 1 or 2 of the 3 replicates succeeded (definitions per benchmark in the non-unanimous-triplicate table).'),
    ('Consensus proxy', 'For CompBioBench, which keeps no per-question grades: the most common answer across the 25 runs of a task; tasks where at least '
                        '20 runs agree are "strong consensus", and deviating answers are probable failures.'),
    ('Jaccard index', 'Size of the intersection divided by the size of the union of two tool sets; 0 = no tool in common, 1 = identical tool sets.'),
    ('Source capsule', 'The BixBench unit of shared input data; several tasks can share one capsule. Used as the bootstrap resampling unit.'),
    ('Input tokens', 'Text units sent to the language model, including cached input; a measure of how much the model had to read.'),
    ('Requested-versus-resolved difference (parameter mismatch)', 'A difference between the parameter values the agent requested and the '
     'tool state Galaxy resolved from them.'),
    ('Evaluator', 'The benchmark component that accepts or rejects a BixBench answer (tolerance or rounded-numeric verifier modes).'),
    ('Primary and secondary cause', 'The adjudicated main and contributing reasons for a rejected run (categories defined in Supplementary Note 6).'),
    ('Percentage points', 'Absolute difference between two percentages.'),
    ('95% confidence interval', 'Exploratory 95% percentile cluster-bootstrap interval (Supplementary Note 9).')]


def build_tables():
    wb = Workbook()
    idx = wb.active
    idx.title = 'Index'
    entries = [(tid, cite, 'cited') for tid, cite in ORDER] + [(tid, cite, 'not cited in current draft') for tid, cite in UNCITED]
    cross = []
    legends = []
    for n, (tid, cite, status) in enumerate(entries, 1):
        if tid.startswith('NEW'):
            title, fn, legend = NEW[tid]
            blocks = fn()
        else:
            title, legend = clean(T[tid]['title']), xref(T[tid]['legend'])
            blocks = archive_blocks(tid)
        write_sheet(wb, f'Supplementary Table {n}', n, title, tid, blocks, legend)
        nrows = sum(len(df) for _, df in blocks)
        cross.append({'Supplementary Table': n, 'Archive ID': tid if not tid.startswith('NEW') else 'new (this audit)',
                      'Internal key': tid, 'Title': title, 'Rows': nrows, 'First cited (draft Results)': cite, 'Status': status})
        legends.append((n, title, legend, tid))
    heads = list(cross[0].keys())
    idx['A1'] = 'Supplementary Tables: index and crosswalk to archive table identifiers'
    idx['A1'].font = Font(bold=True, size=12)
    idx['A2'] = ('Tables are numbered in order of first citation in the draft Results. Tables marked "not cited" should be cited at the '
                 'suggested location or removed before submission; renumber by editing ORDER in scripts/make_supplement.py.')
    idx['A2'].alignment = Alignment(wrap_text=True)
    idx.merge_cells('A2:G2')
    idx.row_dimensions[2].height = 30
    for j, h in enumerate(heads, 1):
        c = idx.cell(4, j, h)
        c.font, c.fill = Font(bold=True, size=9), HEAD
    for i, row in enumerate(cross, 5):
        for j, h in enumerate(heads, 1):
            c = idx.cell(i, j, row[h])
            c.font = Font(size=9, color='9C3D00' if row['Status'] != 'cited' else '000000')
            c.alignment = Alignment(wrap_text=True, vertical='top')
    for j, w in enumerate([10, 12, 16, 60, 7, 60, 22], 1):
        idx.column_dimensions[get_column_letter(j)].width = w
    idx.freeze_panes = 'A5'
    gl = wb.create_sheet('Glossary', 1)
    gl['A1'] = 'Glossary of terms used in the tables'
    gl['A1'].font = Font(bold=True, size=12)
    for j, h in enumerate(['Term', 'Meaning'], 1):
        c = gl.cell(3, j, h)
        c.font, c.fill = Font(bold=True, size=9), HEAD
    for i, (term, meaning) in enumerate(GLOSSARY, 4):
        gl.cell(i, 1, term).font = Font(bold=True, size=9)
        c = gl.cell(i, 2, meaning)
        c.font, c.alignment = Font(size=9), Alignment(wrap_text=True, vertical='top')
    gl.column_dimensions['A'].width = 38
    gl.column_dimensions['B'].width = 110
    wb.save(os.path.join(SUP, 'Supplementary_Tables.xlsx'))
    with open(os.path.join(SUP, 'Supplementary_Table_crosswalk.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=heads)
        w.writeheader()
        w.writerows(cross)
    return cross, legends


# =====================================================================================================
# Supplementary Data
# =====================================================================================================
def write_data(fname, title, legend, df):
    wb = Workbook()
    ws = wb.active
    ws.title = 'README'
    ws['A1'] = title
    ws['A1'].font = Font(bold=True, size=12)
    for i, para in enumerate(legend.split('\n'), 3):
        ws.cell(i, 1, para).alignment = Alignment(wrap_text=True, vertical='top')
    ws.column_dimensions['A'].width = 150
    ws2 = wb.create_sheet('data')
    for j, h in enumerate(df.columns, 1):
        c = ws2.cell(1, j, h)
        c.font, c.fill = Font(bold=True, size=9), HEAD
        ws2.column_dimensions[get_column_letter(j)].width = max(10, min(45, len(h) + 2))
    for i, row in enumerate(df.itertuples(index=False), 2):
        for j, v in enumerate(row, 1):
            v = None if (isinstance(v, float) and pd.isna(v)) else v
            ws2.cell(i, j, clean(v) if isinstance(v, str) else v)
    ws2.freeze_panes = 'A2'
    ws2.auto_filter.ref = ws2.dimensions
    wb.save(os.path.join(SUP, fname))


def build_data():
    fr = json.load(open(os.path.join(V2, 'per_run_friction.json')))
    rows = []
    for s in sorted(SUMS, key=lambda s: (BENCH.index(s['benchmark']), s['task'], ENV_ORDER[s['condition']], s['model'], s['replicate'])):
        cc = s.get('class_calls') or {}
        f = fr.get(f"{s['benchmark']}|{s['task']}|{s['run_id']}", {}) if s['condition'] == 'galaxy' else {}
        row = {'benchmark': BLABEL[s['benchmark']], 'task': s['task'], 'run_id': s['run_id'], 'configuration': CFG.get(s['model'], s['model']),
               'environment': ENV[s['condition']], 'replicate': s['replicate'], 'archived_score': s.get('score'),
               'submitted_answer': clean(s.get('answer'), 500), 'evaluator_mode': s.get('eval_mode') or s.get('verifier'),
               'input_tokens': s.get('input_tokens'), 'output_tokens': s.get('output_tokens'),
               'primary_trace_present': bool(s.get('trace')), 'shell_commands': s.get('n_shell'), 'shell_nonzero_exits': s.get('n_shell_nonzero'),
               'web_calls': s.get('n_web'), 'galaxy_mcp_calls': s.get('n_mcp') if s['condition'] == 'galaxy' else None,
               'galaxy_mcp_failed_calls': s.get('n_mcp_fail') if s['condition'] == 'galaxy' else None,
               'mcp_discovery_calls': cc.get('discovery') if s['condition'] == 'galaxy' else None,
               'mcp_history_inspection_calls': cc.get('inspection') if s['condition'] == 'galaxy' else None,
               'mcp_execution_calls': cc.get('execution') if s['condition'] == 'galaxy' else None}
        for code in TAX_DEF:
            row[f'failed_calls_{code}'] = sum(v for k, v in f.items() if k.split()[0] == code) if s['condition'] == 'galaxy' else None
        rows.append(row)
    write_data('Supplementary_Data_1_run_summaries.xlsx', 'Supplementary Data 1 | Per-run summary of all 4,240 archived runs',
               'One row per archived run. archived_score is the score as archived (BixBench: binary evaluator acceptance; CompBioBench: no item-level '
               'grade is archived, so the field is empty; IWC: 0-1 agreement with the workflow reference output). No score was regraded.\n'
               'Operational counts come from the primary agent trace (Codex JSONL or Claude Code stream-JSON). Galaxy MCP columns are empty for '
               'open-ended-code runs. mcp_discovery_calls = tool search and tool inspection; mcp_history_inspection_calls = history and archive '
               'inspection; mcp_execution_calls = tool, UDT and job-wait calls. failed_calls_A1..Z use the classes in Supplementary Table '
               f'{TABLE_NO["NEW-taxonomy"]}.\nReference answers are deliberately omitted to limit benchmark contamination; they are available in the '
               'source archive evaluator records.', pd.DataFrame(rows))
    calls = []
    for s in SUMS:
        if s['condition'] != 'galaxy':
            continue
        for er in s.get('errors') or []:
            calls.append({'benchmark': BLABEL[s['benchmark']], 'task': s['task'], 'run_id': s['run_id'], 'configuration': CFG.get(s['model'], s['model']),
                          'trace_line': er.get('line'), 'mcp_tool': er.get('tool'), 'status': er.get('status'),
                          'failure_class': TAXO['classify'](er), 'error_text': clean(er.get('err'), 1500), 'arguments': clean(er.get('args'), 1500)})
    write_data('Supplementary_Data_2_failed_MCP_calls.xlsx', f'Supplementary Data 2 | All {len(calls):,} failed Galaxy MCP calls with class, error and arguments',
               'One row per failed Galaxy MCP call in Galaxy-environment runs with a primary trace (both harnesses). trace_line is the line in the '
               'decompressed primary event log (<benchmark>/analysis/<task>/source_snapshots/huggingface_traces/files/<run_id>/). failure_class '
               f'follows Supplementary Table {TABLE_NO["NEW-taxonomy"]}. error_text and arguments are verbatim, truncated to 1,500 characters and '
               'screened for credential-like strings.', pd.DataFrame(calls))
    ex = pd.DataFrame(D['scan']['mismatch_examples'], columns=['benchmark', 'task', 'tool', 'parameter_path', 'requested_value', 'resolved_value'])
    ex['benchmark'] = ex['benchmark'].map(BLABEL)
    write_data('Supplementary_Data_3_parameter_substitutions.xlsx',
               f'Supplementary Data 3 | {len(ex):,} detected parameter substitutions (first substituted value per tool-run call)',
               'For every Codex-harness tool-run call whose parameter provenance reported an explicit value substitution (statuses '
               'validation_parameter_mismatch or parameter_mismatch), the first substituted parameter path with its requested and resolved values. '
               'Calls in which a requested path was only missing from the resolved state are counted in Supplementary Table '
               f'{TABLE_NO["NEW-substitution"]} but have no resolved value to list.', ex)
    return len(calls), len(ex)


# =====================================================================================================
# Supplementary Information PDF
# =====================================================================================================
def build_pdf(legends, n_calls, n_subst):
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    ss = getSampleStyleSheet()
    body = ParagraphStyle('b', parent=ss['BodyText'], fontName='Helvetica', fontSize=9, leading=12.2, alignment=TA_LEFT, spaceAfter=5)
    h1 = ParagraphStyle('h1', parent=ss['Heading1'], fontName='Helvetica-Bold', fontSize=14, leading=17, spaceAfter=8)
    h2 = ParagraphStyle('h2', parent=ss['Heading2'], fontName='Helvetica-Bold', fontSize=11, leading=14, spaceBefore=10, spaceAfter=5)
    small = ParagraphStyle('s', parent=body, fontSize=7.5, leading=9.5, spaceAfter=0)
    smallb = ParagraphStyle('sb', parent=small, fontName='Helvetica-Bold')
    inv = D['inventory']
    fe = D['fig2e']

    def P(t, s=body):
        return Paragraph(t, s)

    def table(data, widths):
        rows = [[P(str(c), smallb if i == 0 else small) for c in r] for i, r in enumerate(data)]
        t = Table(rows, colWidths=[w * mm for w in widths], repeatRows=1)
        t.setStyle(TableStyle([('LINEABOVE', (0, 0), (-1, 0), 0.6, colors.black), ('LINEBELOW', (0, 0), (-1, 0), 0.4, colors.black),
                               ('LINEBELOW', (0, -1), (-1, -1), 0.6, colors.black), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                               ('TOPPADDING', (0, 0), (-1, -1), 2), ('BOTTOMPADDING', (0, 0), (-1, -1), 2)]))
        return t

    S = []
    S += [P('Supplementary Information', h1),
          P('<b>[Manuscript title]</b>'), P('[Authors]'), Spacer(1, 6),
          P('This file contains Supplementary Notes 1–9, legends for Supplementary Tables 1–' + str(len(legends)) +
            ' (provided as Supplementary_Tables.xlsx) and legends for Supplementary Data 1–3 (provided as separate Excel files).'),
          Spacer(1, 6), P('<b>Contents</b>')]
    notes = ['Evidence archive and scope', 'Trace extraction, call classes and interface bypass', 'Classification of failed Galaxy MCP calls',
             'Requested-versus-resolved parameter differences', 'User-defined tool reliability measures', 'Failure adjudication protocol',
             'CompBioBench consensus proxy', 'Replicate variability: non-unanimous triplicates and divergence mechanisms', 'Statistical analysis and limitations']
    for i, n in enumerate(notes, 1):
        S.append(P(f'Supplementary Note {i}. {n}', small))
    S.append(P('Supplementary Table legends; Supplementary Data legends', small))
    S.append(PageBreak())

    # ---- Note 1
    S += [P('Supplementary Note 1. Evidence archive and scope', h2),
          P(f'The analysis is retrospective and read-only. It uses 4,240 archived runs: BixBench-Verified-50 (50 tasks; {inv["BixBench50"]["runs"]:,} runs, '
            'five configurations × two environments × three replicates), CompBioBench (100 tasks; 2,400 paired runs from four configurations plus 100 '
            'code-only GPT-6 Astra runs) and IWC (10 tasks; 240 runs, four configurations). Of these, '
            f'{sum(inv[b]["traces"] for b in BENCH):,} retain a primary agent event log (Codex JSONL, or Claude Code stream-JSON for the superseded '
            'DeepSeek harness); the 12 missing traces are CompBioBench runs. Galaxy job records comprise '
            f'{sum(inv[b]["nonfetch_jobs"] for b in BENCH):,} non-fetch jobs ({inv["BixBench50"]["nonfetch_jobs"]:,} BixBench, '
            f'{inv["CompBio"]["nonfetch_jobs"]:,} CompBioBench, {inv["IWC"]["nonfetch_jobs"]:,} IWC), deduplicated by server and job identifier; '
            'data-fetch jobs are excluded. Detailed history snapshots exist for '
            f'{inv["BixBench50"]["detailed_histories"][0]}/{inv["BixBench50"]["detailed_histories"][1]}, '
            f'{inv["CompBio"]["detailed_histories"][0]:,}/{inv["CompBio"]["detailed_histories"][1]:,} and '
            f'{inv["IWC"]["detailed_histories"][0]}/{inv["IWC"]["detailed_histories"][1]} Galaxy runs; they were taken after the runs completed.'),
          P('Archive integrity was checked before analysis: 160 source-evidence hashes were verified, all 4,240 run identifiers are unique, and the '
            'archived accuracy, job-state and token medians were reproduced from the raw records. No score was regraded; the original evaluator '
            'outcome of every run is retained, including scored missing answers. No agent code was executed and no Galaxy server was contacted. '
            'BixBench reference values were read only from the evaluator records of completed runs.'),
          P('The three benchmarks retain different endpoints — binary evaluator acceptance (BixBench), archived aggregate score vectors without item-level '
            'grades (CompBioBench) and continuous 0–1 agreement with workflow reference outputs (IWC) — and are analysed as separate strata throughout. '
            'Extended Data Fig. 1a summarizes the archive and Extended Data Fig. 1b the audit pipeline.')]
    # ---- Note 2
    s = D['scan']
    S += [P('Supplementary Note 2. Trace extraction, call classes and interface bypass', h2),
          P('Every primary event log was parsed. For each Galaxy MCP call we recovered the tool name, arguments, structured status, error text, '
            'failure summary, validation errors and parameter provenance. Calls were grouped as <i>discovery</i> (search_galaxy_tools, '
            'inspect_galaxy_tool), <i>history inspection</i> (history and archive inspection), <i>execution</i> (run_galaxy_tool_and_wait, '
            'run_galaxy_udt_and_wait, job waits) and shell commands. Token totals are recorded per run and cannot be attributed to individual calls, so '
            'the number of characters each call returned to the agent is used as a proxy for context consumed (Fig. 5b).'),
          P('Shell commands in Galaxy-environment runs were counted as Galaxy API calls when they used BioBlend or GalaxyInstance or called the '
            'Galaxy histories, datasets, jobs or tools API. Commands referencing BioBlend, GalaxyInstance or any /api/ path were matched against '
            'five operations: seed-history copy (copy_history, /copy), dataset download (download_dataset, '
            '/display, /download), tool-schema fetch (show_tool, /build), job polling (show_job, /jobs/{id}, wait_for_job) and raw job submission '
            '(run_tool, or a POST to /api/tools through requests, curl or urllib). Bypass, substitution and UDT statistics use Codex-harness traces '
            f'({sum(s["codex_galaxy_runs"].values()):,} Galaxy runs: {s["codex_galaxy_runs"]["BixBench50"]} BixBench, '
            f'{s["codex_galaxy_runs"]["CompBio"]:,} CompBioBench, {s["codex_galaxy_runs"]["IWC"]} IWC), because the Claude Code harness renders tool '
            'results in a different structure. The seed history is provided, and its copy required by the harness policy, only in BixBench.')]
    # ---- Note 3
    tax_rows = [['Class', 'Name', 'Definition']] + [[k, v[0], v[1]] for k, v in TAX_DEF.items()]
    tot = {b: sum(D['ed3b'][b].values()) for b in BENCH}
    pre = sum(v for b in BENCH for k, v in D['ed3b'][b].items() if k.startswith('A'))
    post = sum(v for b in BENCH for k, v in D['ed3b'][b].items() if k.startswith('B'))
    unc = sum(v for b in BENCH for k, v in D['ed3b'][b].items() if k.startswith('Z'))
    S += [P('Supplementary Note 3. Classification of failed Galaxy MCP calls', h2),
          P(f'Of {sum(inv[b]["mcp_calls"] for b in BENCH):,} Galaxy MCP calls, {sum(tot.values()):,} returned a failure status. Each failed call was '
            'assigned one class by applying ordered regular-expression rules to its error text and status (first match wins; rules in Supplementary '
            f'Table {TABLE_NO["NEW-taxonomy"]}). Classes A1–A8 are failures before any job existed ({pre:,} calls); B1–B5 are failures of a created '
            f'job ({post:,}); {unc} calls matched no rule and are reported as unclassified. Rule order resolves overlaps; for example, a missing '
            'history context is assigned A1 even when the message also contains a validation keyword. Classes were designed to be actionable: '
            'each maps onto an interface change (Extended Data Fig. 3d).'),
          table(tax_rows, [12, 45, 113])]
    # ---- Note 4
    S += [P('Supplementary Note 4. Requested-versus-resolved parameter differences', h2),
          P('The benchmark MCP layer compares the parameter values an agent requested with the tool state Galaxy resolved from them, and returns the '
            'difference as parameter provenance. Two statuses carry a difference: <i>validation_parameter_mismatch</i>, for which the harness '
            'blocked submission, and <i>parameter_mismatch</i>, for which the job executed. Within each, a call is an <i>explicit substitution</i> '
            'when a requested value was replaced (for example max → count) and a <i>missing path</i> when a requested parameter path is absent from '
            'the resolved state, typically because the value was placed under a conditional branch or repeat key that Galaxy did not select. '
            f'Detected differences occurred in 4,352 tool-run calls: 3,436 blocked and 916 executed (Fig. 3e; Supplementary Table '
            f'{TABLE_NO["NEW-substitution"]}). Supplementary Data 3 lists the first substituted value of each call with an explicit substitution '
            f'({n_subst:,} calls). These are differences between request and resolved state; whether a given difference changed a scientific result '
            'was established only for the adjudicated cases in the failure ledger.')]
    # ---- Note 5
    S += [P('Supplementary Note 5. User-defined tool reliability measures', h2),
          P('Every run_galaxy_udt_and_wait call returns a structured status (ok, failed, udt_creation_failed or none). For failed jobs, the '
            'failure_diagnostic block records the phase (before execution or during command rendering, versus command runtime) and whether stderr '
            'or a message was returned. A diagnostic-free failure was followed to the next tool-run call of the same run, which was classed as an '
            'identical resubmission when its tool inputs or UDT representation were byte-identical after key sorting, and otherwise as modified. '
            'Probe UDTs were identified by identifiers containing probe, preflight, render, smoke, diagnos(tic) or sanity. Of the calls that '
            'followed a diagnostic-free failure, 784 resubmitted an identical payload and 615 of those failed again (Extended Data Fig. 3a; '
            f'Supplementary Table {TABLE_NO["NEW-udt"]}).')]
    # ---- Note 6
    cat_rows = [['Category', 'Definition', 'Open-ended code, primary / secondary (n = 135)', 'Galaxy, primary / secondary (n = 111)']]
    cdef = {'SPEC': 'Task under-specified, or the reference depends on a choice the question does not state',
            'RIGOR': 'Statistical or reasoning error: weak evidence accepted, thresholds or invariants ignored, wrong denominator',
            'EVALUATOR': 'Grader rejected an equivalent answer, or score records conflict',
            'KNOWLEDGE': 'Domain-knowledge gap', 'PLATFORM': 'Galaxy, MCP or tooling defect (for code runs: local environment tooling)',
            'HARNESS': 'No answer written (turn ended or budget exhausted)', 'CONTRACT': 'Output-format or identifier violation'}
    for k, v in cdef.items():
        cat_rows.append([CAUSE_NAME[k], v, f'{fe["open_ended_code"]["primary"].get(k, 0)} / {fe["open_ended_code"]["secondary"].get(k, 0)}',
                         f'{fe["galaxy"]["primary"].get(k, 0)} / {fe["galaxy"]["secondary"].get(k, 0)}'])
    S += [P('Supplementary Note 6. Failure adjudication protocol', h2),
          P('Every rejected BixBench run (246: 135 open-ended code, 111 Galaxy) and every IWC run scoring below 0.5 (8) was read call by call. For '
            'each, we identified the decision point: the step at which the evidence the agent acted on diverged from what the reference required, '
            'and whether that evidence was sufficient. Rejected runs were contrasted with accepted runs of the same task, using the same '
            'configuration where one succeeded. Final answers were checked against independent evidence where possible (for example, '
            'reconstructing a statistic from the retained inputs, recomputing Benjamini–Hochberg adjustments, or comparing assembled contigs '
            'with the public <i>Agrius convolvuli</i> mitogenome OZ203683.1 by canonical 31-mers) rather than against the agent\'s own conclusion.'),
          P('Each run received one primary and at most one secondary root-cause category. Galaxy is counted as <i>implicated</i> when a platform or tool defect is '
            f'primary or secondary: {fe["open_ended_code"]["platform_any"]} of 135 open-ended-code rejections and {fe["galaxy"]["platform_any"]} of 111 '
            'Galaxy rejections.'),
          table(cat_rows, [40, 70, 30, 30]), Spacer(1, 5),
          P('Confidence was assigned per run: <b>high</b> (159), the decisive step is visible in the trace and confirmed by reproduction, '
            'independent reference comparison or contrast with an accepted sibling; <b>moderate</b> (55), the decisive step is identified but only '
            'partly verified; <b>mixed</b> (20), several contributing causes are present and the primary assignment is a judgement; '
            '<b>unresolved</b> (12), no decisive step could be isolated and the category is the best-supported explanation. Mixed and unresolved '
            'assignments (32 of 246) are not proofs. The ledger (Supplementary Table ' + str(TABLE_NO['NEW-ledger']) + ') records the decision point '
            'for every run. For IWC, two Galaxy host-removal records scored 0.273 were re-examined: the submitted BWA-MEM output retained 20,899 read '
            'pairs, matching the BWA-route reference (20,896) rather than the Bowtie2-route reference (72,867) against which it was scored; the IWC '
            'archive itself performs no adjudication of these score-conflicted records (Extended Data Fig. 2d).')]
    # ---- Note 7
    S += [P('Supplementary Note 7. CompBioBench consensus proxy', h2),
          P('CompBioBench archives 22 aggregate score vectors but no item-level grades or references, so task-level correctness cannot be observed. '
            'Answers were normalized (lower case, whitespace removed) and the modal answer across the 25 runs of each task was taken as the '
            'consensus. Applied to the 22 vectors with retained answers, the number of answers matching the consensus reproduces the archived totals '
            'with a mean absolute error of 2.6 of 100 and a mean bias of +2.0 (Extended Data Fig. 1c). On the 82 tasks with at least 20 of 25 '
            'concordant runs, a deviating answer is treated as a <i>probable</i> failure; this yields 33 Galaxy and 40 open-ended-code deviations '
            '(GPT-6 Astra excluded). The 18 contested tasks are not used. Re-fitting individual answers to the totals was rejected because it '
            'over-fits (22 constraints, 100 unknowns). The proxy is labelled as such wherever it appears and supports no task-level accuracy claim.')]
    # ---- Note 8
    S += [P('Supplementary Note 8. Replicate variability: non-unanimous triplicates and divergence mechanisms', h2),
          P('A triplicate (cell) is one task run three times with one configuration in one environment. A triplicate is <i>non-unanimous</i> '
            '(a "mixed cell" in the draft text) when 1 or 2 of 3 BixBench replicates '
            'were accepted, when 1 or 2 of 3 CompBioBench replicates match a strong consensus answer (82 tasks), or when the within-cell range of IWC '
            'agreement scores exceeds 0.05. For every rejected replicate in a non-unanimous BixBench triplicate, the trace was compared with the accepted '
            'sibling(s) to identify what separated them. Mechanisms: <b>platform trap</b>, an optional interface path taken by this replicate only '
            'produced a silent default, a different output semantics or an undispatched job; <b>package-version drift</b>, the replicate installed '
            'a different software version from its accepted sibling; <b>convention or definition</b>, a domain convention or variable definition '
            'applied differently; <b>self-implemented method</b>, a hand-written script (or, in Galaxy, a UDT) diverged from the library method; '
            '<b>final-step slip</b>, a sort, count, complement or unit error after an otherwise correct analysis; <b>no answer</b>; and '
            '<b>benchmark-source lookup</b>, the only accepted replicate retrieved benchmark source data. Mechanisms describe what differed between '
            'replicates and are distinct from root causes (Note 6). Replicates are not seed-matched, so variability means run-to-run divergence under '
            'the same prompt, model and harness.')]
    # ---- Note 9
    S += [P('Supplementary Note 9. Statistical analysis and limitations', h2),
          P('Unless stated otherwise, intervals are exploratory 95% percentile cluster-bootstrap intervals with 20,000 resamples (seed 20260922; '
            'NumPy linear quantiles; statistic-specific SHA-256 streams). Resampling units are source capsules for BixBench (up to 33), tasks for '
            'CompBioBench (up to 100) and tasks for IWC; configurations and replicate bundles are retained within each cluster, and cross-benchmark '
            'draws are independent and stratified by benchmark. Intervals assume independent clusters, which is not established for shared biological '
            'inputs, and are pointwise rather than multiplicity-adjusted. No confirmatory significance, equivalence, non-inferiority or causal claim '
            'is made; an interval spanning zero (differences) or one (ratios) is inconclusive. Token ratios divide the median input tokens of the '
            'three Galaxy runs by the median of the three code runs for the same task and configuration (all six totals required; cached input '
            'included; output and reasoning tokens not added), and are summarized by their median. Spearman correlations between prompt word '
            'count or recorded workload and failure markers are across tasks, use the three shared GPT configurations (nine observed runs '
            'required per task and environment) and 5,000 capsule or task bootstrap resamples with ties reranked within each resample.'),
          P('<b>Limitations.</b> Benchmarks differ in task selection, prompts, execution budgets, exposed interfaces and endpoints, so cross-benchmark '
            'contrasts are descriptive. The IWC estimates rest on nine or ten task clusters. The superseded Claude Code harness ran BixBench only. '
            'Galaxy histories were snapshotted after the runs. Adjudication was performed by trace review, and 32 of 246 assignments are mixed or '
            'unresolved. Candidate recovery episodes were not adjudicated, and the code condition has no equivalent job-level detector. Shell exits '
            'are an operational marker, not a scientific failure rate. Human review time, reconstruction accuracy and monetary cost were not measured.')]
    S.append(PageBreak())
    # ---- Table legends
    S.append(P('Supplementary Table legends', h2))
    S.append(P('All tables are provided in Supplementary_Tables.xlsx, one sheet per table, with an index sheet mapping each table to its archive '
               'identifier and first citation.', body))
    for n, title, legend, tid in legends:
        leg = clean(legend, 4000).replace('\n\n', ' ').replace('\n', ' ')
        leg = re.sub(r'Unless a table specifies otherwise, new intervals are exploratory.*', 'Intervals as in Supplementary Note 9.', leg)
        src = f' Archive table {tid}.' if not tid.startswith('NEW') else ''
        ttl = clean(title) if clean(title).endswith(('?', '.')) else clean(title) + '.'
        S.append(P(f'<b>Supplementary Table {n} | {ttl}</b> {leg}{src}', small))
        S.append(Spacer(1, 4))
    S.append(P('Supplementary Data legends', h2))
    S += [P('<b>Supplementary Data 1 | Per-run summary of all 4,240 archived runs.</b> One row per run with benchmark, task, configuration, '
            'environment, replicate, archived score, submitted answer, evaluator mode, token usage, shell and MCP call counts and failed-call counts '
            'by class. Reference answers are omitted to limit benchmark contamination.', small), Spacer(1, 4),
          P(f'<b>Supplementary Data 2 | All {n_calls:,} failed Galaxy MCP calls.</b> One row per failed call with run, trace line, MCP tool, status, '
            'failure class, verbatim error text and arguments (truncated to 1,500 characters; screened for credentials).', small), Spacer(1, 4),
          P(f'<b>Supplementary Data 3 | {n_subst:,} detected parameter substitutions.</b> For each Codex-harness tool-run call with an explicit '
            'requested-versus-resolved substitution, the first substituted parameter path with requested and resolved values.', small)]

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 7.5)
        canvas.drawRightString(A4[0] - 18 * mm, 10 * mm, f'Supplementary Information — page {doc.page}')
        canvas.restoreState()

    doc = SimpleDocTemplate(os.path.join(SUP, 'Supplementary_Information.pdf'), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm, title='Supplementary Information', author='[Authors]')
    doc.build(S, onFirstPage=footer, onLaterPages=footer)


TABLE_NO = {tid: n for n, (tid, _) in enumerate(ORDER + UNCITED, 1)}

if __name__ == '__main__':
    cross, legends = build_tables()
    n_calls, n_subst = build_data()
    build_pdf(legends, n_calls, n_subst)
    print(f'{len(cross)} Supplementary Tables ({sum(1 for c in cross if c["Status"] == "cited")} cited); '
          f'Supplementary Data: {n_calls} failed calls, {n_subst} substitutions')
