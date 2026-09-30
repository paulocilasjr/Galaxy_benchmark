"""Assemble every figure panel's data from the archived evidence into source_data/figure_data.json.

Run from the repository root:  python manuscript_material/scripts/build_data.py
Inputs (all in this repository):
  BixBench50_CompBio_analysis/analysis.json           archived tables (B1-X20), per-run summaries, token pairs
  CompBio/compBio_overview_audit.json                 archived CompBioBench aggregate score vectors
  analysis_reports/galaxy_improvement_20260924/...    failure ledger, per-run MCP failure taxonomy,
                                                      replicate-divergence mechanisms, independent checks
  manuscript_material/source_data/derived/run_summaries.jsonl.gz   per-run trace summaries (extract.py output)
  <benchmark>/analysis/<task>/source_snapshots/...   raw agent traces and evaluator files (scanned once)
No agent code is executed and no Galaxy server is contacted.
"""
import collections
import gzip
import json
import os
import re
import statistics as st

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'manuscript_material', 'source_data', 'figure_data.json')
V2 = os.path.join(ROOT, 'analysis_reports', 'galaxy_improvement_20260924', 'v2_trace_friction')

A = json.load(open(os.path.join(ROOT, 'BixBench50_CompBio_analysis', 'analysis.json')))
T = A['tables']
RUNS = A['runs']
SUMS = [json.loads(l) for l in gzip.open(os.path.join(ROOT, 'manuscript_material', 'source_data', 'derived', 'run_summaries.jsonl.gz'), 'rt')]
SUM = {(s['benchmark'], s['task'], s['run_id']): s for s in SUMS}

CFG = {  # archive model key -> display label (fixed order used in every figure)
    'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
    'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
    'codex_deepseek_v4_pro': 'DeepSeek V4 Pro',
    'deepseek_v4_pro_via_claude_code_superseded': 'DeepSeek V4 Pro (Claude Code, superseded)',
    'codex_gpt_6_astra': 'GPT-6 Astra',
}
ORDER = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro', 'DeepSeek V4 Pro (Claude Code, superseded)']
BENCH = ['BixBench50', 'CompBio', 'IWC']
NUM = r'-?[\d,]*\.?\d+(?:e-?\d+)?'


def frac(cell):
    """'134/150 (89.3%)' -> (134, 150)."""
    m = re.match(r'\s*([\d,]+)\s*/\s*([\d,]+)', cell)
    return (int(m.group(1).replace(',', '')), int(m.group(2).replace(',', ''))) if m else (None, None)


def est_ci(cell):
    """'2.00 [0.00, 5.30]' (optionally 'n; ...') -> (est, lo, hi)."""
    m = re.search(rf'({NUM})\s*\[\s*({NUM}),\s*({NUM})\s*\]', cell)
    return tuple(float(x) for x in m.groups()) if m else (None, None, None)


def first_num(cell):
    m = re.search(NUM, cell)
    return float(m.group(0).replace(',', '')) if m else None


def label(row0):
    return re.sub(r'\]\(.*?\)', '', row0).strip('[] ')


def rows(tid):
    return T[tid]['rows']


D = {'_provenance': 'Built by manuscript_material/scripts/build_data.py from archived evidence; see module docstring.'}

# ---------------------------------------------------------------- Figure 1c / ED Fig. 1: inventory
inv = {}
for b in BENCH:
    rr = [r for r in RUNS if r['benchmark'] == b]
    ss = [s for s in SUMS if s['benchmark'] == b]
    g = [s for s in ss if s['condition'] == 'galaxy']
    inv[b] = dict(runs=len(rr), traces=sum(1 for s in ss if s.get('trace')), galaxy_runs=len(g),
                  code_runs=len(ss) - len(g), mcp_calls=sum(s.get('n_mcp') or 0 for s in g),
                  mcp_failed=sum(s.get('n_mcp_fail') or 0 for s in g), tasks=len({r['task'] for r in rr}))
jobs = collections.Counter(j['benchmark'] for j in A['jobs'])
job_err = collections.Counter(j['benchmark'] for j in A['jobs'] if j['status'] == 'error')
for b in BENCH:
    inv[b]['nonfetch_jobs'] = jobs[b]
    inv[b]['error_jobs'] = job_err[b]
det = {'BixBench50': frac(rows('B4')[0][1]), 'CompBio': frac(rows('C3')[0][1]), 'IWC': frac(rows('I7')[0][1])}
for b in BENCH:
    inv[b]['detailed_histories'] = det[b]
D['inventory'] = inv

# ---------------------------------------------------------------- Figure 2a: BixBench acceptance (B1)
D['fig2a'] = [dict(config=r[0], galaxy=frac(r[1]), code=frac(r[2]), diff=est_ci(r[3])) for r in rows('B1')]

# ---------------------------------------------------------------- Figure 2b: CompBio aggregate vectors (C1 source)
cb = json.load(open(os.path.join(ROOT, 'CompBio', 'compBio_overview_audit.json')))
D['fig2b'] = [dict(config=CFG[v['model']], condition=v['condition'], replicate=v['replicate'], score=v['score'],
                   official=v['score_type'].startswith('official'), vector_available=v.get('answers_compared', 0) > 0,
                   hash_matches=v.get('hash_matches')) for v in cb['score_vectors']]

# ---------------------------------------------------------------- Figure 2c: IWC nine-task means (I1)
D['fig2c'] = []
for r in rows('I1'):
    D['fig2c'].append(dict(config=r[0].replace(' (Codex, IWC)', ''), galaxy_mean=first_num(r[1].split(';')[1]),
                           code_mean=first_num(r[2].split(';')[1]), diff=est_ci(r[4])))

# ---------------------------------------------------------------- Figure 2d: IWC per-task scores, every replicate
TASKNAME = {
    'wf_001_short_read_qc_trim': 'Short-read QC', 'wf_002_rnaseq_de_visualization': 'RNA-seq DE',
    'wf_003_host_contamination_removal': 'Host-read removal', 'wf_005_amplicon_dada2_pe_denoising': 'Amplicon denoising',
    'wf_006_atacseq_chromatin_accessibility': 'ATAC-seq peaks', 'wf_007_vgp_mitogenome_assembly': 'Mitogenome assembly',
    'wf_008_amr_gene_detection': 'AMR detection', 'wf_009_clinicalmp_peptide_verification': 'Peptide verification',
    'wf_010_pseudobulk_scrna_de': 'Pseudobulk DE', 'wf_011_bioproject_metadata_sequence_retrieval': 'BioProject retrieval'}
D['fig2d'] = [dict(task=r['task'], task_label=TASKNAME[r['task']], condition=r['condition'], config=CFG[r['model']],
                   replicate=r['replicate'], score=r['score']) for r in RUNS if r['benchmark'] == 'IWC']
D['fig2d_means'] = {label(r[0]): dict(galaxy=first_num(r[2]), code=first_num(r[3])) for r in rows('I3')}

# ---------------------------------------------------------------- Figure 2e: root causes (ledger)
led = json.load(open(os.path.join(V2, 'ledger.json')))
bix = [x for x in led if x['b'] == 'BixBench']
D['fig2e'] = {c: dict(n=sum(1 for x in bix if x['cond'] == c),
                      primary=collections.Counter(x['p'] for x in bix if x['cond'] == c),
                      secondary=collections.Counter(x['s'] for x in bix if x['cond'] == c and x['s'] != '-'),
                      platform_any=sum(1 for x in bix if x['cond'] == c and 'PLATFORM' in (x['p'], x['s'])))
              for c in ['galaxy', 'open_ended_code']}
D['fig2e_confidence'] = collections.Counter(x['c'] for x in bix)

# ---------------------------------------------------------------- Figure 3a (X14), 3b (X19 + B9/C8/I10), 3c (X12), 3d (X18)
D['fig3a'] = [dict(operation=r[0], values=[frac(c) for c in r[1:4]]) for r in rows('X14')]
D['fig3b_toolshed'] = {r[0]: frac(r[6]) for r in rows('X19')}
D['fig3b_top'] = {b: [dict(tool=r[0], jobs=int(r[1].replace(',', '')), errors=int(r[2].replace(',', ''))) for r in rows(t)]
                  for b, t in [('BixBench50', 'B9'), ('CompBio', 'C8'), ('IWC', 'I10')]}
D['fig3c'] = [dict(benchmark=r[0], config=r[1], requesting=frac(r[2]), linked=frac(r[4]),
                   linked_success=int(r[6]) if r[6].isdigit() else None) for r in rows('X12')]
D['fig3d'] = [dict(benchmark=r[0], family=r[1], diagnostic=r[2], n=frac(r[3])) for r in rows('X18')]

# ---------------------------------------------------------------- Figure 4a (X9, X12), 4b (B5/C5/I8)
D['fig4a_families'] = [dict(family=r[0], values=[frac(c) for c in r[1:7]]) for r in rows('X9')]
D['fig4b'] = {}
for b, t in [('BixBench50', 'B5'), ('CompBio', 'C5'), ('IWC', 'I8')]:
    D['fig4b'][b] = [dict(config=r[1].replace(' (Codex, IWC)', '').replace(' 0813 (Codex)', '').replace(' (Codex)', ''),
                          jaccard=float(r[6])) for r in rows(t) if r[0] == 'Galaxy']
D['fig4b_code'] = {b: [dict(config=r[1], jaccard=float(r[6])) for r in rows(t) if r[0] == 'Open-ended code']
                   for b, t in [('BixBench50', 'B5'), ('CompBio', 'C5'), ('IWC', 'I8')]}

# ---------------------------------------------------------------- Figure 4a-c: replicate sets (split, unanimous)
def cells(bench):
    c = collections.defaultdict(list)
    for r in RUNS:
        if r['benchmark'] == bench and r['model'] != 'codex_gpt_6_astra':
            c[(r['condition'], CFG[r['model']], r['task'])].append(r)
    return c


mixed = collections.defaultdict(lambda: collections.Counter())
comp = collections.defaultdict(lambda: collections.Counter())
for (cond, cfg, task), rs in cells('BixBench50').items():
    k = sum(r['score'] == 1 for r in rs)
    state = 'all' if k == 3 else ('none' if k == 0 else 'mixed')
    comp[('BixBench50', cond, cfg)][state] += 1
    if state == 'mixed':
        mixed[('BixBench50', cond)][cfg] += 1
norm = lambda a: (a or '').strip().lower().replace(' ', '')
cbr = [r for r in RUNS if r['benchmark'] == 'CompBio']
modal, support = {}, {}
for t in {r['task'] for r in cbr}:
    cnt = collections.Counter(norm(r['answer']) for r in cbr if r['task'] == t)
    modal[t], support[t] = cnt.most_common(1)[0]
for (cond, cfg, task), rs in cells('CompBio').items():
    if support[task] < 20:
        continue
    k = sum(norm(r['answer']) == modal[task] for r in rs)
    comp[('CompBio', cond, cfg)]['cells'] += 1
    comp[('CompBio', cond, cfg)]['all' if k == len(rs) else ('none' if k == 0 else 'mixed')] += 1
    if 0 < k < len(rs):
        mixed[('CompBio', cond)][cfg] += 1
for (cond, cfg, task), rs in cells('IWC').items():
    sc = [r['score'] for r in rs]
    if None in sc:
        continue
    comp[('IWC', cond, cfg)]['cells'] += 1
    if max(sc) - min(sc) > 0.05:
        mixed[('IWC', cond)][cfg] += 1
D['fig4c'] = {f'{b}|{c}': dict(mixed[(b, c)]) for b in BENCH for c in ['galaxy', 'open_ended_code']}
D['fig4c_cells'] = {f'{b}|{c}|{cfg}': dict(v) for (b, c, cfg), v in comp.items()}
D['compbio_strong_tasks'] = sum(1 for t in support if support[t] >= 20)

# ---------------------------------------------------------------- Figure 4d: divergence mechanisms
src = open(os.path.join(V2, 'variability.py')).read()
ns = {}
exec(compile(src.split('\ndef main')[0].replace("S = [json.loads(l) for l in open('run_summaries.jsonl')]", 'S = []'), 'variability', 'exec'), ns)
D['fig4d'] = {'galaxy': collections.Counter(ns['G'].values()), 'open_ended_code': collections.Counter(ns['C'].values()),
              'labels': ns['MECH']}

# ---------------------------------------------------------------- Figure 5a (token pairs), 5c (B15)
D['fig5a'] = [dict(benchmark=p['benchmark'], config=CFG[p['model']], ratio=p['ratio']) for p in A['results']['token_pairs']]
D['fig5a_summary'] = {'BixBench50': est_ci(rows('B7')[-1][3]), 'CompBio': est_ci(rows('C6')[-1][3]), 'IWC': est_ci(rows('I9')[-1][3])}
D['fig5c'] = [dict(env=r[0], config=r[1], acc_diff=est_ci(r[2]), token_ratio=est_ci(r[3])) for r in rows('B15')]

# ---------------------------------------------------------------- ED Fig. 2a (X3), 4b (X11), 5a (X2)
D['ed2a'] = [dict(instrument=r[0], values=[est_ci(c) for c in r[1:4]], contrasts=[est_ci(c) for c in r[4:6]],
                  n=[int(c.split(';')[0]) for c in r[1:4]]) for r in rows('X3')]
D['ed4b'] = [dict(benchmark=r[0], env=r[1], exposure=r[2], response=r[3], n=int(r[4]), rho=est_ci(r[5])) for r in rows('X11')]
D['ed5a'] = [dict(config=r[0], values=[est_ci(c) for c in r[1:4]], contrasts=[est_ci(c) for c in r[4:6]]) for r in rows('X2')]

# ---------------------------------------------------------------- ED Fig. 2b/2c: bix-45-q1 and bix-43-q2 per run
def evaluation(bench_dir, task, run_id):
    base = os.path.join(ROOT, bench_dir, 'analysis', task, 'source_snapshots', 'huggingface_traces', 'files', run_id)
    p = os.path.join(base, 'evaluation.json')
    return json.load(open(p)) if os.path.exists(p) else {}


for key, task in [('ed2b', 'bix-45-q1'), ('ed2c', 'bix-43-q2')]:
    out = []
    for r in RUNS:
        if r['benchmark'] == 'BixBench50' and r['task'] == task:
            acc = evaluation('BixBench_50', task, r['run_id']).get('accuracy', {})
            try:
                val = float(r['answer'])
            except (TypeError, ValueError):
                val = None
            out.append(dict(condition=r['condition'], config=CFG[r['model']], replicate=r['replicate'], value=val,
                            accepted=r['score'] == 1, mode=acc.get('mode'), expected=acc.get('expected_value'),
                            tolerance=acc.get('tolerance')))
    D[key] = out

# ---------------------------------------------------------------- ED Fig. 2d: IWC adjudications
chk = json.load(open(os.path.join(ROOT, 'analysis_reports', 'galaxy_improvement_20260924', 'independent_checks.json')))
D['ed2d_mito'] = [dict(run=m['run'], f1=m['f1'], length=m['length'],
                       condition='galaxy' if m['run'].startswith('galaxy') else 'open_ended_code') for m in chk['mitogenome_comparison']]
host = {}
for rid in ['galaxy_gpt_5_6_luna_r1', 'galaxy_gpt_5_6_luna_r3', 'galaxy_gpt_5_6_sol_r1', 'galaxy_gpt_5_6_luna_r2']:
    e = evaluation('IWC', 'wf_003_host_contamination_removal', rid)
    det_ = e.get('details', {})
    host[rid] = dict(score=e.get('reference_accuracy'), route=(e.get('route') or {}).get('route_id'),
                     candidate_retained=det_.get('retained_read_ids', {}).get('candidate_total'),
                     reference_retained=det_.get('retained_read_ids', {}).get('reference_total'),
                     matched=det_.get('retained_read_ids', {}).get('matched'))
D['ed2d_host'] = host

# ---------------------------------------------------------------- ED Fig. 3b: MCP failure taxonomy by benchmark
prf = json.load(open(os.path.join(V2, 'per_run_friction.json')))
tax = collections.defaultdict(collections.Counter)
for k, v in prf.items():
    tax[k.split('|')[0]].update(v)
D['ed3b'] = {b: dict(tax[b]) for b in BENCH}

# ---------------------------------------------------------------- one pass over Codex-harness Galaxy traces
def opener(p):
    return gzip.open(p, 'rt', errors='replace') if p.endswith('.gz') else open(p, errors='replace')


def result_struct(it):
    r = it.get('result') or {}
    sc = r.get('structured_content') if isinstance(r, dict) else None
    if isinstance(sc, dict):
        return sc
    try:
        return json.loads(r['content'][0]['text'])
    except Exception:
        return {}


BYPASS = {'copy_history': r'copy_history|/copy\b', 'download': r'download_dataset|/display\?|datasets/[^/\s]+/display|/download',
          'tool_schema': r'show_tool\(|/build\b', 'job_polling': r'show_job\(|jobs/[0-9a-f]{16}|wait_for_job',
          'raw_submission': r'\.run_tool\(|requests\.post\([^)]*api/tools|-X\s*POST[^\n]{0,200}api/tools|urlopen\([^)]*api/tools[^)]*data='}
PROBE = re.compile(r'probe|preflight|render|smoke|diagnos|sanity', re.I)
scan = dict(runtool_status=collections.defaultdict(collections.Counter), mismatch_tools=collections.defaultdict(collections.Counter),
            mismatch_kind=collections.Counter(), mismatch_examples=[], udt_status=collections.Counter(),
            failed_phase=collections.Counter(), after_notext=collections.Counter(), probe=collections.Counter(),
            bypass=collections.defaultdict(collections.Counter), codex_runs=collections.Counter(),
            inspected=collections.Counter(), inspected_never_run=collections.Counter(), searches=collections.defaultdict(list),
            api_shell=collections.Counter(), api_shell_core=collections.Counter(), all_shell=collections.Counter(),
            core_library=collections.defaultdict(list), core_library_read_only=collections.defaultdict(list))
CORE_IMPORT = re.compile(r'import\s+galaxy_execute_mcp_core|from\s+galaxy_execute_mcp_core|galaxy_execute_mcp_core\.\w+\(')
for s in SUMS:
    if s['condition'] != 'galaxy' or not s.get('trace') or 'claude' in s['trace']:
        continue
    b = s['benchmark']
    scan['codex_runs'][b] += 1
    calls, hits, inspected, ran, nsearch, probe_hit, core_hit, core_read = [], set(), set(), set(), 0, 0, False, False
    for line in opener(s['trace']):
        if '"item.completed"' not in line:
            continue
        try:
            it = json.loads(line)['item']
        except Exception:
            continue
        if it.get('type') == 'command_execution':
            cmd = it.get('command', '')
            scan['all_shell'][b] += 1
            if CORE_IMPORT.search(cmd):  # the Galaxy interface's own library imported into a shell script
                core_hit = True
            elif 'galaxy_execute_mcp_core' in cmd:
                core_read = True
            if re.search(r'bioblend|GalaxyInstance|usegalaxy\.org/api|/api/(histories|datasets|jobs|tools)', cmd):
                scan['api_shell_core'][b] += 1  # definition used in the improvement report (shell_galaxy.py)
            if re.search(r'bioblend|GalaxyInstance|/api/', cmd):
                scan['api_shell'][b] += 1
                for k, rx in BYPASS.items():
                    if re.search(rx, cmd):
                        hits.add(k)
            continue
        if it.get('type') != 'mcp_tool_call':
            continue
        tool, args = it.get('tool') or '', it.get('arguments') or {}
        if tool == 'search_galaxy_tools':
            nsearch += 1
        elif tool == 'inspect_galaxy_tool' and args.get('tool_id'):
            inspected.add(args['tool_id'])
        elif tool == 'run_galaxy_tool_and_wait' and args.get('tool_id'):
            ran.add(args['tool_id'])
        if not (tool.startswith('run_galaxy') or tool == 'wait_for_galaxy_jobs'):
            continue
        sc = result_struct(it)
        status = sc.get('status')
        if tool.startswith('run_galaxy'):
            scan['runtool_status'][b][str(status)] += 1
        if tool == 'run_galaxy_udt_and_wait':
            scan['udt_status'][str(status)] += 1
            rep = args.get('representation') if isinstance(args.get('representation'), dict) else {}
            if PROBE.search(str(rep.get('id', ''))):
                probe_hit += 1
        if status in ('parameter_mismatch', 'validation_parameter_mismatch'):
            pp = sc.get('parameter_provenance') or {}
            mms, miss = list(pp.get('mismatches') or []), list(pp.get('missing_paths') or [])
            for j in pp.get('jobs') or []:
                mms += j.get('mismatches') or []
                miss += j.get('missing_paths') or []
            scan['mismatch_kind'][(b, status, 'substituted' if mms else 'dropped')] += 1
            tid = args.get('tool_id') or ('UDT' if 'udt' in tool else '?')
            short = tid.split('/')[-2] if tid.count('/') >= 2 else tid
            scan['mismatch_tools'][short][status] += 1
            for m in mms[:1]:
                if len(scan['mismatch_examples']) < 3000:
                    scan['mismatch_examples'].append((b, s['task'], short, m.get('path'), str(m.get('expected')), str(m.get('resolved'))))
        if status == 'failed':
            for j in sc.get('jobs') or []:
                if j.get('state') == 'error':
                    ph = (j.get('failure_diagnostic') or {}).get('phase')
                    kind = 'udt' if 'udt' in tool else ('wait' if tool == 'wait_for_galaxy_jobs' else 'tool')
                    scan['failed_phase'][(kind, ph, 'stderr' if j.get('failure') else 'no_text')] += 1
        calls.append((status, json.dumps(args.get('tool_inputs') or args.get('representation'), sort_keys=True), sc))
    for i, (status, payload, sc) in enumerate(calls[:-1]):
        jobs_ = sc.get('jobs') or []
        if status == 'failed' and jobs_ and all(not j.get('failure') for j in jobs_ if j.get('state') == 'error'):
            nstatus, npayload, _ = calls[i + 1]
            scan['after_notext'][('identical' if npayload == payload else 'modified', 'failed' if nstatus == 'failed' else 'other')] += 1
    for k in hits:
        scan['bypass'][b][k] += 1
    if probe_hit:
        scan['probe'][(b, 'runs')] += 1
        scan['probe'][(b, 'calls')] += probe_hit
    scan['inspected'][b] += len(inspected)
    scan['inspected_never_run'][b] += len(inspected - ran)
    scan['searches'][b].append(nsearch)

    if core_hit:
        scan['core_library'][(b, CFG[s['model']])].append(f"{s['task']}|{s['run_id']}")
    elif core_read:
        scan['core_library_read_only'][(b, CFG[s['model']])].append(f"{s['task']}|{s['run_id']}")

ser = lambda c: {('|'.join(map(str, k)) if isinstance(k, tuple) else str(k)): v for k, v in c.items()}
D['scan'] = dict(
    codex_galaxy_runs=dict(scan['codex_runs']),
    runtool_status={b: dict(v) for b, v in scan['runtool_status'].items()},
    mismatch_kind=ser(scan['mismatch_kind']),
    mismatch_tools={k: dict(v) for k, v in scan['mismatch_tools'].items()},
    mismatch_examples=scan['mismatch_examples'],
    udt_status=dict(scan['udt_status']),
    failed_phase=ser(scan['failed_phase']),
    after_notext=ser(scan['after_notext']),
    probe=ser(scan['probe']),
    bypass={b: dict(v) for b, v in scan['bypass'].items()},
    api_shell=dict(scan['api_shell']), api_shell_core=dict(scan['api_shell_core']), all_shell=dict(scan['all_shell']),
    inspected=dict(scan['inspected']), inspected_never_run=dict(scan['inspected_never_run']),
    searches={b: dict(median=st.median(v), max=max(v)) for b, v in scan['searches'].items()},
    core_library={f'{b}|{c}': v for (b, c), v in scan['core_library'].items()},
    core_library_read_only={f'{b}|{c}': v for (b, c), v in scan['core_library_read_only'].items()},
)

# ---------------------------------------------------------------- Figure 5b: per-run discovery shares
share = collections.defaultdict(lambda: {'calls': [], 'chars': []})
for s in SUMS:
    if s['condition'] != 'galaxy' or not s.get('trace') or 'claude' in s['trace']:
        continue
    cc, ch = s.get('class_calls') or {}, s.get('class_chars') or {}
    mc = sum(v for k, v in cc.items() if k != 'shell')
    mch = sum(v for k, v in ch.items() if k != 'shell')
    if mc:
        share[s['benchmark']]['calls'].append(cc.get('discovery', 0) / mc)
    if mch:
        share[s['benchmark']]['chars'].append(ch.get('discovery', 0) / mch)
D['fig5b'] = {b: v for b, v in share.items()}
D['fig5b_class_totals'] = {b: {k: dict(calls=sum((s.get('class_calls') or {}).get(k, 0) for s in SUMS if s['benchmark'] == b and s['condition'] == 'galaxy'),
                                       chars=sum((s.get('class_chars') or {}).get(k, 0) for s in SUMS if s['benchmark'] == b and s['condition'] == 'galaxy'))
                               for k in ['discovery', 'inspection', 'execution', 'other']} for b in BENCH}

# ---------------------------------------------------------------- skill uptake (Addendum V2/V3)
DOMAIN = {'crispr-dependency-correlation', 'expression-matrix-pca', 'model-fitting-setup-validation',
          'phylogenetics-tree-metrics', 'transcriptomics', 'variant-callset-ratio'}


def skills_read(trace):
    got = set()
    for line in opener(trace):
        if 'SKILL.md' not in line and '"Skill"' not in line:
            continue
        try:
            e = json.loads(line)
        except Exception:
            continue
        it = e.get('item') or {}
        if it.get('type') == 'command_execution' and re.search(r'\b(sed|cat|head|less|awk|nl|tail)\b', it.get('command', '')):
            got |= set(re.findall(r'skills/([a-z0-9-]+)/SKILL\.md', it['command']))
        msg = e.get('message') or {}
        for blk in msg.get('content') or [] if isinstance(msg.get('content'), list) else []:
            if blk.get('type') == 'tool_use':
                inp = blk.get('input') or {}
                if blk.get('name') == 'Skill':
                    got.add(inp.get('skill', ''))
                elif blk.get('name') in ('Read', 'Bash'):
                    got |= set(re.findall(r'skills/([a-z0-9-]+)/SKILL\.md', json.dumps(inp)))
    return got


BX = [s for s in SUMS if s['benchmark'] == 'BixBench50' and s.get('trace')]
READ = {(s['task'], s['run_id']): skills_read(s['trace']) for s in BX}
REL = {}
for t in {s['task'] for s in BX}:
    c = collections.Counter(k for s in BX if s['task'] == t and s['score'] == 1 for k in READ[(t, s['run_id'])] if k in DOMAIN)
    REL[t] = c.most_common(1)[0][0] if c else None
up = collections.defaultdict(lambda: [0, 0])
for s in BX:
    if REL[s['task']]:
        u = up[(CFG[s['model']], s['condition'])]
        u[1] += 1
        u[0] += REL[s['task']] in READ[(s['task'], s['run_id'])]
D['skill_uptake'] = {f'{k[0]}|{k[1]}': v for k, v in up.items()}
D['skill_relevant_tasks'] = sum(1 for v in REL.values() if v)

# =====================================================================================================
# Panels introduced for the restructured Results (execution condition -> model configuration -> replicate
# agreement -> trace-level analysis). Every value below is recomputed from the archive, not typed in.
# =====================================================================================================

# ---- IWC medians and means per model configuration, nine matched tasks and all ten tasks (Fig. 2a, Fig. 3a)
iwc = collections.defaultdict(list)
for p in D['fig2d']:
    if p['score'] is not None:
        iwc[(p['config'], p['condition'], p['task_label'] != 'Host-read removal')].append(p['score'])
D['iwc_levels'] = {f'{c}|{e}': dict(nine_median=st.median(iwc[(c, e, True)]), nine_mean=st.mean(iwc[(c, e, True)]),
                                    ten_median=st.median(iwc[(c, e, True)] + iwc[(c, e, False)]),
                                    ten_mean=st.mean(iwc[(c, e, True)] + iwc[(c, e, False)]),
                                    ten_n=len(iwc[(c, e, True)] + iwc[(c, e, False)]))
                   for c in ORDER[:4] for e in ('galaxy', 'open_ended_code')}
D['iwc_replicate_means_ten'] = {}
rep10 = collections.defaultdict(list)
for p in D['fig2d']:
    if p['score'] is not None:
        rep10[(p['config'], p['condition'], p['replicate'])].append(p['score'])
D['iwc_replicate_means_ten'] = {f'{c}|{e}|{r}': st.mean(v) for (c, e, r), v in rep10.items()}

# ---- IWC sensitivity of the condition difference (I4): leave-one-task-out and zero-scored-run removal (Extended Data Fig. 3)
def _num(x):
    m = re.findall(NUM, x)
    return [float(v) for v in m]


D['iwc_sensitivity'] = []
for r in rows('I4'):
    lo, hi = _num(r[2])[:2]
    D['iwc_sensitivity'].append(dict(config=r[0].replace(' (Codex, IWC)', ''), nine=_num(r[1])[0], loto_low=lo, loto_high=hi,
                                     sign_stable=r[3].strip().startswith('Yes'), no_zero=_num(r[4])[0], no_zero_removed=int(_num(r[4])[1]),
                                     with_host=_num(r[5])[0]))

# ---- BixBench run-level and unanimous accuracy per model configuration and condition (Fig. 4b,e)
acc = collections.defaultdict(lambda: [0, 0])
for r in RUNS:
    if r['benchmark'] == 'BixBench50':
        a = acc[(CFG[r['model']], r['condition'])]
        a[0] += r['score'] == 1
        a[1] += 1
D['bix_accuracy'] = {f'{c}|{e}': dict(correct=v[0], runs=v[1], run_level=100 * v[0] / v[1],
                                      unanimous=100 * D['fig4c_cells'][f'BixBench50|{e}|{c}']['all'] / 50,
                                      all=D['fig4c_cells'][f'BixBench50|{e}|{c}']['all'],
                                      split=D['fig4c_cells'][f'BixBench50|{e}|{c}'].get('mixed', 0),
                                      none=D['fig4c_cells'][f'BixBench50|{e}|{c}']['none'])
                     for (c, e), v in acc.items()}

# ---- CompBio answer consistency: distinct answers per replicate set (C2) and across all 12 runs (Fig. 4c)
cbr_p = [r for r in RUNS if r['benchmark'] == 'CompBio' and r['model'] != 'codex_gpt_6_astra']
distinct = collections.defaultdict(collections.Counter)
by_set = collections.defaultdict(set)
for r in cbr_p:
    by_set[(CFG[r['model']], r['condition'], r['task'])].add(norm(r['answer']))
for (c, e, t), s in by_set.items():
    distinct[f'{c}|{e}'][len(s)] += 1
D['compbio_distinct'] = {k: dict(v) for k, v in distinct.items()}
D['compbio_single_answer_all12'] = {e: sum(1 for t in {r['task'] for r in cbr_p}
                                           if len({norm(r['answer']) for r in cbr_p if r['task'] == t and r['condition'] == e}) == 1)
                                    for e in ('galaxy', 'open_ended_code')}

# ---- CompBio reported benchmark scores per model configuration (Fig. 2d, Fig. 3a)
cbs = collections.defaultdict(list)
for p in D['fig2b']:
    cbs[f"{p['config']}|{p['condition']}"].append(p['score'])
D['compbio_scores'] = {k: dict(mean=st.mean(v), replicates=v) for k, v in cbs.items()}

# ---- input-token usage per run, by benchmark, model configuration and condition (Fig. 3c)
tok = collections.defaultdict(list)
for s in SUMS:
    if s.get('input_tokens') and s['model'] != 'codex_gpt_6_astra':
        tok[(s['benchmark'], CFG[s['model']], s['condition'])].append(s['input_tokens'])
D['input_tokens'] = {f'{b}|{c}|{e}': dict(median=st.median(v), n=len(v), q1=float(sorted(v)[len(v) // 4]), q3=float(sorted(v)[(3 * len(v)) // 4]))
                     for (b, c, e), v in tok.items()}
D['input_tokens_runs'] = {f'{b}|{c}|{e}': v for (b, c, e), v in tok.items() if e == 'galaxy'}

# ---- the interface's core library scripted from the shell: BixBench accuracy of those runs (Extended Data Fig. 4)
core = D['scan']['core_library']
D['core_library_accuracy'] = {}
for c in ORDER[:4]:
    ids = set(core.get(f'BixBench50|{c}', []))
    read = set(D['scan']['core_library_read_only'].get(f'BixBench50|{c}', []))
    runs_c = [s for s in SUMS if s['benchmark'] == 'BixBench50' and s['condition'] == 'galaxy' and CFG[s['model']] == c]
    key = lambda s: f"{s['task']}|{s['run_id']}"
    D['core_library_accuracy'][c] = dict(runs=len(runs_c), scripted=len(ids), read_only=len(read),
                                         scripted_correct=sum(1 for s in runs_c if key(s) in ids and s['score'] == 1),
                                         other_correct=sum(1 for s in runs_c if key(s) not in ids and s['score'] == 1))

# ---- divergence mechanisms by model configuration (Extended Data Fig. 5)
inv_sh = {v: k for k, v in ns['SH'].items()} if 'SH' in ns else {}
div_cfg = collections.defaultdict(collections.Counter)
for env, table in (('galaxy', ns['G']), ('open_ended_code', ns['C'])):
    for key, mech in table.items():
        cfg = CFG.get(inv_sh.get(key[1], key[1]), key[1])
        div_cfg[f'{env}|{cfg}'][mech] += 1
D['divergence_by_config'] = {k: dict(v) for k, v in div_cfg.items()}

# ---- task-level audit (Fig. 5a, Extended Data Fig. 8): parsed from individual_error_analysis.md in the repository root
IEA = os.path.join(ROOT, 'individual_error_analysis.md')
cases = []
section = None
for line in open(IEA):
    m = re.match(r'^### (BixBench-50|CompBioBench|IWC workflows) index', line)
    if m:
        section = {'BixBench-50': 'BixBench50', 'CompBioBench': 'CompBio', 'IWC workflows': 'IWC'}[m.group(1)]
        continue
    if line.startswith('## ') and not line.startswith('## Index'):
        section = None
    if section and line.startswith('| [') :
        cells_ = [c.strip() for c in line.strip().strip('|').split('|')]
        task = re.match(r'\[([^\]]+)\]', cells_[0]).group(1)
        cases.append(dict(benchmark=section, task=task, galaxy=cells_[1], code=cells_[2], category=cells_[3], finding=cells_[4],
                          tags=[t.strip() for t in cells_[5].split(',') if t.strip()]))
assert len(cases) == 93, len(cases)
D['task_cases'] = cases
CATS = {}
for line in open(IEA):
    m = re.match(r'^\| (C\d)\. (.+?) \|', line)
    if m:
        CATS[m.group(1)] = m.group(2)
D['task_case_categories'] = CATS

# ---- integrity problems (Extended Data Fig. 8): run-level lists transcribed from the task entries of individual_error_analysis.md
D['integrity'] = dict(
    local_fallback_correct=[  # correct Galaxy-condition CompBioBench answers whose decisive computation ran in the local shell
        ('atac-tn5-shift-q1', 'GPT-5.5', 2), ('atac-tn5-shift-q1', 'GPT-5.5', 3), ('borzoi-rnaseq-q1', 'GPT-5.5', 3),
        ('borzoi-rnaseq-q1', 'DeepSeek V4 Pro', 1), ('extract-rna-secondary-structure-q1', 'GPT-5.5', 2),
        ('extract-rna-secondary-structure-q1', 'GPT-5.5', 3), ('extract-rna-secondary-structure-q1', 'GPT-5.6 Luna', 1),
        ('huggingface-entropy-q1', 'GPT-5.5', 2), ('huggingface-entropy-q1', 'GPT-5.5', 3), ('saluki-setup-optimize-q1', 'GPT-5.5', 3),
        ('saluki-setup-optimize-q1', 'DeepSeek V4 Pro', 2), ('tissue-fibroblast-q1', 'GPT-5.5', 3), ('tissue-fibroblast-q1', 'GPT-5.6 Luna', 1),
        ('finding-geo-q1', 'GPT-5.5', 2), ('hic-differential-loop-q1', 'GPT-5.5', 1)],
    local_fallback_incorrect=[('encode-atac-pipeline-q1', 'GPT-5.5', 2), ('encode-atac-pipeline-q1', 'GPT-5.5', 3), ('overexpress-tf-q1', 'GPT-5.5', 2)],
    cross_run=[('encode-atac-pipeline-q1', 'GPT-5.6 Luna', 1, 'copied 13636 from the answer file of an earlier pilot history (incorrect)'),
               ('saluki-setup-optimize-q1', 'GPT-5.6 Luna', 3, 'read the outputs of two other runs through the jobs API (correct)')],
    # auditor classification of the 26 tasks tagged benchmark-answer-retrieval
    retrieval={'Benchmark answer, key or another agent\'s answer obtained': [
                   'bix-12-q6', 'bix-26-q5', 'bix-30-q3', 'bix-54-q7', '1000G-retrieve-genotype-q1', 'atac-doublet-q1', 'contaminated-rna-q2',
                   'hic-differential-loop-q1', 'reverse-search-gwas-q1', 'tissue-fibroblast-q1'],
               'Source paper, dataset or workflow settings that fix the answer': [
                   'protein-shape-q1', 'characterize-response-q1', 'covid-patient-q1', 'wf_007_vgp_mitogenome_assembly',
                   'wf_009_clinicalmp_peptide_verification'],
               'Attempted; nothing usable obtained': [
                   'bix-16-q3', 'bix-32-q2', 'bix-53-q5', 'atac-tn5-shift-q1', 'deg-simple-q2', 'gene-pair-ordering-fraction-q1', 'histone-chip-q1',
                   'lung-cancer-sc-q1', 'phase-chain-q1', 'saluki-setup-optimize-q1', 'variant-status-q1']})
_tagged = {c['task'] for c in cases if 'benchmark-answer-retrieval' in c['tags']}
_listed = {t for v in D['integrity']['retrieval'].values() for t in v}
assert _tagged == _listed, (_tagged ^ _listed)

# ---- bix-35-q1: metric actually executed by every PhyKIT job in every Galaxy-condition run (Fig. 5b, Extended Data Fig. 7)
b35 = []
tdir = os.path.join(ROOT, 'BixBench_50', 'analysis', 'bix-35-q1')
ev = json.load(open(os.path.join(tdir, 'history_analysis_evidence.json')))
for r in ev['runs']:
    if r['condition'] != 'galaxy':
        continue
    hist = [x.replace('src_galaxy_', '') for x in r['source_ids'] if x.startswith('src_galaxy_')]
    jobs_ = []
    for h in hist:
        for jf in sorted(os.listdir(os.path.join(tdir, 'source_snapshots', 'galaxy', h, 'jobs'))) if os.path.isdir(os.path.join(tdir, 'source_snapshots', 'galaxy', h, 'jobs')) else []:
            j = json.load(open(os.path.join(tdir, 'source_snapshots', 'galaxy', h, 'jobs', jf)))
            if 'phykit_metrics' in (j.get('tool_id') or ''):
                m = re.search(r"--metric '([^']+)'", j.get('command_line') or '')
                jobs_.append(dict(job=j['id'], state=j['state'], metric=m.group(1) if m else None, created=j.get('create_time')))
    rr = [x for x in RUNS if x['benchmark'] == 'BixBench50' and x['task'] == 'bix-35-q1' and x['run_id'] == r['run_id']][0]
    b35.append(dict(run=r['run_id'], config=CFG[rr['model']], replicate=rr['replicate'], answer=rr['answer'], correct=rr['score'] == 1,
                    jobs=sorted(jobs_, key=lambda j: j['created'] or '')))
D['bix35'] = b35

# ---- contaminated-rna-q1: what each Galaxy-condition run's classification database could contain (Fig. 5c)
cr = [x for x in RUNS if x['benchmark'] == 'CompBio' and x['task'] == 'contaminated-rna-q1']
D['contaminated_rna_q1'] = dict(
    runs=[dict(config=CFG[x['model']], condition=x['condition'], replicate=x['replicate'], answer=x['answer'],
               correct=(x['answer'] or '').strip().lower() == 'hydra vulgaris') for x in cr],
    failures={'GPT-5.5|3': 'core_nt job finished with empty classification datasets; fell back to standard-16',
              'GPT-5.6 Luna|2': 'core_nt job ran for hours on one thread and was cancelled; fell back to standard-16',
              'GPT-5.6 Luna|1': 'core_nt job and nucleotide BLAST reached the four-hour wall-time limit; fell back to a mitochondrion-only BLAST'},
    hydra_reads=8793, ebv_reads=195, total_reads=96053)

json.dump(D, open(OUT, 'w'), indent=1, default=lambda o: dict(o) if isinstance(o, collections.Counter) else str(o))
print('wrote', OUT, os.path.getsize(OUT) // 1024, 'KB')
