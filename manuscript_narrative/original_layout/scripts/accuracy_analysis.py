#!/usr/bin/env python3
"""Archive-only accuracy, repeatability, and UDT analysis for original_layout.

No scientific execution, remote service, benchmark answer, or private key is read.
Grades use narrative_common.graded_runs(); IWC uses the nine interpretable tasks.
All bootstrap contrasts resample shared source capsules (BixBench) or tasks, keeping
the paired arms, configurations and replicates together. Intervals are descriptive,
not equivalence tests, and are not adjusted for multiple configuration comparisons.
"""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
NARR = HERE.parent
sys.path.insert(0, str(NARR))
import narrative_common as nc

OUT = HERE / 'analysis'
OUT.mkdir(parents=True, exist_ok=True)
KEY = ['benchmark', 'task', 'cfg', 'env', 'replicate']
BENCH = ['BixBench50', 'CompBio', 'IWC']
ENVS = ['open_ended_code', 'galaxy']


def write(name, frame):
    frame.to_csv(OUT / f'accuracy_{name}.csv', index=False)


def json_clean(obj):
    if isinstance(obj, dict):
        return {k:json_clean(v) for k,v in obj.items()}
    if isinstance(obj, list):
        return [json_clean(v) for v in obj]
    if isinstance(obj, (float,np.floating)) and not np.isfinite(obj):
        return None
    if isinstance(obj,np.generic):
        return obj.item()
    return obj


def interval(df, value, scale=1.):
    """Paired-arm ratio-of-sums contrast and separate arm cluster intervals."""
    arr = nc.paired_cluster_arrays(df, value)
    delta, lo, hi = nc.boot_diff(*arr, scale=scale)
    out = dict(difference=delta, ci95_low=lo, ci95_high=hi,
               clusters=int(df.cluster.nunique()))
    for i, env in enumerate(ENVS):
        a, b, c = nc.boot_ratio_of_sums(arr[2*i], arr[2*i+1])
        out[env] = a*scale
        out[env+'_ci95_low'] = b*scale
        out[env+'_ci95_high'] = c*scale
        out[env+'_n'] = int(arr[2*i+1].sum())
    return out


def main():
    g = nc.graded_runs()
    g = g[g.cfg.isin(nc.CODEX4)].copy()
    assert len(g) == 3816
    assert not g.duplicated(KEY).any()
    meta = []
    for r in nc.analysis()['runs']:
        if nc.CFG[r['model']] not in nc.CODEX4:
            continue
        meta.append(dict(benchmark=r['benchmark'], task=r['task'],
                         cfg=nc.CFG[r['model']], env=r['condition'],
                         replicate=r['replicate'], run_id=r['run_id'],
                         udt_requested_archive=bool(r.get('udt_requested'))))
    meta = pd.DataFrame(meta)
    g = g.merge(meta, on=KEY, how='left', validate='one_to_one')
    bad_cells, bad_run_count = nc.compbio_outcome_named_cells()
    bad = set(zip(bad_cells.task, bad_cells.cfg))
    bench_side = {t for (b,t), c in nc.audit_categories().items()
                  if b == 'BixBench50' and c in ('C1','C2','C3','C6')}
    zero_tasks = set(g[(g.benchmark == 'IWC') & g.score.eq(0)].task)
    g['bix_benchmark_side_task'] = g.benchmark.eq('BixBench50') & g.task.isin(bench_side)
    g['compbio_outcome_named_cell'] = [b == 'CompBio' and (t,c) in bad for b,t,c in zip(g.benchmark,g.task,g.cfg)]
    g['iwc_zero_task'] = g.benchmark.eq('IWC') & g.task.isin(zero_tasks)
    g['iwc_atac_task'] = g.benchmark.eq('IWC') & g.task.eq('wf_006_atacseq_chromatin_accessibility')
    d = json.load(open(NARR / 'derived/design/design_metadata.json'))
    bud = pd.DataFrame(d['q4_budgets']['iwc_per_run']['rows'])
    bud['cfg'] = bud.model.map(nc.CFG)
    w = bud.pivot_table(index=['task','cfg','replicate'], columns='condition', values='budget_h').reset_index()
    w['budget_matched'] = w.galaxy.eq(w.open_ended_code)
    g = g.merge(w[['task','cfg','replicate','budget_matched']], on=['task','cfg','replicate'], how='left', validate='many_to_one')
    write('primary_runs', g)

    estimates = []
    for b in BENCH:
        for cfg in nc.CODEX4 + ['Pooled']:
            y = g[g.benchmark.eq(b) & (g.cfg.isin(nc.CODEX4) if cfg == 'Pooled' else g.cfg.eq(cfg))]
            estimates.append(dict(benchmark=b,cfg=cfg,scale=100 if b != 'IWC' else 1,
                                  endpoint='Original evaluator acceptance (%)' if b == 'BixBench50' else
                                  ('Reconstructed-key agreement (%)' if b == 'CompBio' else 'Mean output agreement (0-1)'),
                                  **interval(y,'score',100 if b != 'IWC' else 1)))
    est = pd.DataFrame(estimates)
    write('benchmark_configuration', est)

    ranks = []
    for b in BENCH:
        for env in ENVS:
            z = est[est.benchmark.eq(b) & est.cfg.ne('Pooled')].copy()
            z['rank'] = z[env].rank(ascending=False,method='min')
            ranks.extend(dict(benchmark=b,env=env,cfg=r.cfg,score=getattr(r,env),rank=int(r.rank)) for r in z.itertuples())
    rank = pd.DataFrame(ranks)
    write('descriptive_model_ranks',rank)

    ss = nc.replicate_sets()
    ss = ss[ss.cfg.isin(nc.CODEX4)].copy()
    ss['n_correct'] = [int(sum(v == 1 for v in x)) if b != 'IWC' else np.nan for b,x in zip(ss.benchmark,ss.scores)]
    ss['n_errors'] = np.where(ss.benchmark.ne('IWC'),3-ss.n_correct,np.nan)
    ss['all_three_correct'] = np.where(ss.benchmark.ne('IWC'),ss.n_correct.eq(3).astype(int),np.nan)
    ss['discordant'] = ss.cat.eq('split').astype(int)
    ss['within_set_range'] = ss.scores.map(lambda x: float(max(x)-min(x)))
    ss['within_set_sd'] = ss.scores.map(lambda x: float(np.std(x,ddof=1)))
    ss['scores'] = ss.scores.map(lambda x: ';'.join(str(v) for v in x))
    write('replicate_sets',ss)
    repeat = []
    errors = []
    for b in BENCH:
        for cfg in nc.CODEX4+['Pooled']:
            y = ss[ss.benchmark.eq(b) & (ss.cfg.isin(nc.CODEX4) if cfg == 'Pooled' else ss.cfg.eq(cfg))]
            fields=['discordant'] + (['all_three_correct'] if b != 'IWC' else ['within_set_range','within_set_sd'])
            for field in fields:
                vals=interval(y,field,100 if field in ('discordant','all_three_correct') else 1)
                if field == 'discordant':
                    arr=nc.paired_cluster_arrays(y,field)
                    if arr[0].sum()>0 and arr[2].sum()>0:
                        ratio,lo,hi=nc.boot_rel(*arr)
                    elif arr[0].sum()>0:
                        ratio=lo=hi=0.
                    else:
                        ratio=lo=hi=np.nan
                    vals.update(ratio=ratio,ratio_ci95_low=lo,ratio_ci95_high=hi)
                repeat.append(dict(benchmark=b,cfg=cfg,measure=field,**vals))
            if b != 'IWC':
                for env in ENVS:
                    q=y[y.env.eq(env)]
                    for k in range(4):
                        errors.append(dict(benchmark=b,cfg=cfg,env=env,n_errors=k,sets=int(q.n_errors.eq(k).sum()),denominator=len(q),percent=100*q.n_errors.eq(k).mean()))
    rep=pd.DataFrame(repeat)
    write('repeatability',rep)
    write('error_count_distribution',pd.DataFrame(errors))

    # The same task x configuration is attempted three times in each arm. Sets rejected 3/3 recur across arms,
    # so the arm difference in repeatability lies in the mixed (one or two rejected) sets.
    transitions=[];overlap=[]
    for b in BENCH[:2]:
        y=ss[ss.benchmark.eq(b)].pivot_table(index=['task','cfg'],columns='env',values='n_errors')
        tab=y.groupby(['open_ended_code','galaxy']).size()
        for i in range(4):
            for j in range(4):
                transitions.append(dict(benchmark=b,code_rejected=i,galaxy_rejected=j,sets=int(tab.get((float(i),float(j)),0)),denominator=len(y)))
        code3,gal3=y.open_ended_code.eq(3),y.galaxy.eq(3)
        tasks=lambda m:set(y[m].reset_index().task)
        overlap.append(dict(benchmark=b,paired_sets=len(y),
            three_rejected_sets_code=int(code3.sum()),three_rejected_sets_galaxy=int(gal3.sum()),three_rejected_sets_both=int((code3&gal3).sum()),
            three_rejected_tasks_code=len(tasks(code3)),three_rejected_tasks_galaxy=len(tasks(gal3)),
            three_rejected_tasks_both=len(tasks(code3)&tasks(gal3)),
            mixed_sets_code=int(y.open_ended_code.isin([1,2]).sum()),mixed_sets_galaxy=int(y.galaxy.isin([1,2]).sum())))
    write('cross_arm_error_transitions',pd.DataFrame(transitions))
    write('persistent_failure_overlap',pd.DataFrame(overlap))

    # Prompt files differ between arms by design: Galaxy prompts add execution policy. Primary pairs only.
    dr=nc.design_runs();dr=dr[dr.cfg.isin(nc.CODEX4)]
    pairs=dr.pivot_table(index=['benchmark','task','cfg','replicate'],columns='condition',values='prompt_file_sha256',aggfunc='first').dropna()
    words=dr.groupby(['benchmark','condition']).prompt_file_words.median().unstack()
    prompts=[dict(benchmark=b,prompt_pairs=int((pairs.reset_index().benchmark==b).sum()),
                  identical_prompt_pairs=int((pairs.galaxy==pairs.open_ended_code)[pairs.reset_index().benchmark.eq(b).values].sum()),
                  median_prompt_words_code=float(words.loc[b,'open_ended_code']),median_prompt_words_galaxy=float(words.loc[b,'galaxy']))
             for b in BENCH]
    write('prompt_design',pd.DataFrame(prompts))

    sens=[]
    populations={
        'BixBench_exclude_benchmark_side_C1_C2_C3_C6':g[g.benchmark.eq('BixBench50') & ~g.bix_benchmark_side_task],
        'CompBio_exclude_outcome_named_cells':g[g.benchmark.eq('CompBio') & ~g.compbio_outcome_named_cell],
        'IWC_exclude_tasks_with_zero_run':g[g.benchmark.eq('IWC') & ~g.iwc_zero_task],
        'IWC_exclude_ATAC_agent_calibrated_routes':g[g.benchmark.eq('IWC') & ~g.iwc_atac_task],
        'IWC_budget_matched_pairs':g[g.benchmark.eq('IWC') & g.budget_matched.eq(True)],
    }
    for label,y in populations.items():
        b=y.benchmark.iloc[0]
        sens.append(dict(population=label,benchmark=b,tasks=y.task.nunique(),runs=len(y),**interval(y,'score',100 if b!='IWC' else 1)))
    write('sensitivities',pd.DataFrame(sens))

    # Interface attempts, server submissions and completed jobs are different endpoints.
    calls=nc.galaxy_calls()
    calls=calls[calls.galaxy_server.eq(True) & calls.cfg.isin(nc.CODEX4) & calls.tool.eq('run_galaxy_udt_and_wait')].copy()
    calls['udt_submitted_record']=calls.submitted.fillna(False).astype(str).str.lower().eq('true')
    calls['udt_job_record']=calls.n_jobs.fillna(0).gt(0)
    calls['udt_ok_job_record']=calls.job_states.fillna('').str.split(';').map(lambda xs:'ok' in xs)
    calls['udt_error_job_record']=calls.job_states.fillna('').str.split(';').map(lambda xs: bool(set(xs)&{'error','failed'}))
    calls['udt_returned_ok']=calls.result_status.eq('ok') & calls.call_status.eq('completed')
    safe=['benchmark','task','run_id','cfg','replicate','line','result_status','call_status','submitted','n_jobs','job_states','udt_submitted_record','udt_job_record','udt_ok_job_record','udt_error_job_record','udt_returned_ok']
    write('udt_call_observations',calls[safe])
    grp=calls.groupby(['benchmark','task','run_id','cfg','replicate']).agg(
        udt_calls_observed=('line','size'),udt_submitted_calls=('udt_submitted_record','sum'),
        udt_job_record_calls=('udt_job_record','sum'),udt_ok_job_calls=('udt_ok_job_record','sum'),
        udt_error_job_calls=('udt_error_job_record','sum'),udt_returned_ok_calls=('udt_returned_ok','sum'))
    u=g[g.env.eq('galaxy')].merge(grp.reset_index(),on=['benchmark','task','run_id','cfg','replicate'],how='left',validate='one_to_one')
    sums=nc.summaries()
    u=u.merge(sums[KEY+['has_trace']],on=KEY,how='left',validate='one_to_one')
    for col in grp.columns:
        u[col]=u[col].fillna(0).astype(int)
    u['udt_attempt_observed']=u.udt_calls_observed.gt(0)
    u['udt_submitted_observed']=u.udt_submitted_calls.gt(0)
    u['udt_job_observed']=u.udt_job_record_calls.gt(0)
    u['udt_completed_ok_observed']=u.udt_ok_job_calls.gt(0)
    u['udt_returned_ok_observed']=u.udt_returned_ok_calls.gt(0)
    u['udt_trajectory']=np.select(
        [u.udt_completed_ok_observed,u.udt_job_observed,u.udt_attempt_observed,u.udt_requested_archive,~u.has_trace.fillna(False)],
        ['At least one completed ok UDT job','Job record; no completed ok job observed','UDT attempt; no job record observed','Archived request; no parsed call observed','Trace unavailable'],
        default='No UDT request observed')
    write('udt_run_observations',u)
    udt=[]
    associations=[]
    for b in BENCH:
        for cfg in nc.CODEX4+['Pooled']:
            y=u[u.benchmark.eq(b) & (u.cfg.isin(nc.CODEX4) if cfg=='Pooled' else u.cfg.eq(cfg))]
            udt.append(dict(benchmark=b,cfg=cfg,runs=len(y),traces=int(y.has_trace.sum()),
                archived_requesting_runs=int(y.udt_requested_archive.sum()),
                observed_attempting_runs=int(y.udt_attempt_observed.sum()),
                observed_submitted_runs=int(y.udt_submitted_observed.sum()),
                observed_job_record_runs=int(y.udt_job_observed.sum()),
                observed_completed_ok_runs=int(y.udt_completed_ok_observed.sum()),
                observed_returned_ok_runs=int(y.udt_returned_ok_observed.sum()),
                udt_calls=int(y.udt_calls_observed.sum()),
                submitted_calls=int(y.udt_submitted_calls.sum()),job_record_calls=int(y.udt_job_record_calls.sum()),
                completed_ok_job_calls=int(y.udt_ok_job_calls.sum()),returned_ok_calls=int(y.udt_returned_ok_calls.sum())))
            for trajectory,q in y.groupby('udt_trajectory'):
                associations.append(dict(benchmark=b,cfg=cfg,trajectory=trajectory,runs=len(q),
                    score_mean=float(q.score.mean()),correct_runs=int(q.score.eq(1).sum()) if b!='IWC' else None,
                    interpretation='Descriptive selection association; UDT use and success are post-assignment variables.'))
    write('udt_usage',pd.DataFrame(udt))
    write('udt_accuracy_association',pd.DataFrame(associations))

    vs=nc.vote_sets();vs=vs[vs.cfg.isin(nc.CODEX4)]
    write('answer_vote_sensitivity',vs)
    result={
        'population':{'primary_configurations':nc.CODEX4,'graded_primary_runs':len(g),'binary_tasks':150,'iwc_primary_tasks':9,'all_archived_primary_runs':3840,'excluded_iwc_task':nc.IWC_NINE_EXCLUDED},
        'statistical_contract':{'n_boot':nc.N_BOOT,'seed':nc.B_SEED,'cluster':'BixBench source capsule; CompBio and IWC task','interval':'95% paired percentile cluster bootstrap','multiplicity':'No multiplicity adjustment; descriptive configuration comparisons','endpoint_warning':'IWC agreement is continuous and must not be pooled with binary correctness','causal_warning':'Assigned arms differ in prompts, budgets, campaigns and execution environments; these are not isolated Galaxy effects'},
        'pooled_accuracy':est[est.cfg.eq('Pooled')].to_dict('records'),
        'configuration_accuracy':est[est.cfg.ne('Pooled')].to_dict('records'),
        'descriptive_ranks':rank.to_dict('records'),
        'repeatability':rep.to_dict('records'),
        'sensitivity':sens,
        'bix_excluded_tasks':sorted(bench_side),'compbio_outcome_named_runs':bad_run_count,'compbio_excluded_cells':len(bad),
        'iwc_zero_tasks':sorted(zero_tasks),
        'udt_usage':udt,
        'persistent_failure_overlap':overlap,
        'prompt_design':prompts,
        'answer_identity_warning':'All-three-correct is evaluator-outcome repeatability, not exact-answer stability. Retrospective normalized identity at ten or three significant digits is a separate measure, with no percent unit conversion.',
        'udt_warning':'An attempted UDT is agent-authored code inside the Galaxy arm. Submission/job metadata does not establish a completed computation. No observed call or job is not proof of no attempt or execution when traces are missing.',
        'claims':{
            'similar_accuracy':'Small pooled binary score differences with intervals spanning zero; similarity does not establish equivalence/noninferiority.',
            'no_one_model_fits_all':'Descriptively supported by benchmark-specific rank reversals, not a formally established universal interaction.',
            'galaxy_stability_all_models':'All-three-correct rate increased in every one of eight binary benchmark x configuration cells; discordance did not decrease in all cells. Individual intervals are broad and this does not establish an advantage in all models.',
            'persistent_versus_sporadic':'Sets rejected in all three attempts mostly recur in the other arm for the same task x configuration; the arm difference lies in mixed-outcome sets.',
            'udt_accuracy':'Selection-associated, not causal; successful UDT execution and correctness must be kept separate.'},
        'inputs':[{'path':str(p.relative_to(Path(nc.ROOT))),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [Path(nc.path('BixBench50_CompBio_analysis','analysis.json')),Path(nc.path('manuscript_material','on_demand','Source_Data_OD_Fig4.xlsx')),NARR/'derived/galaxy_calls/calls.csv.gz',NARR/'derived/design/per_run_design_metadata.csv']],
    }
    (OUT/'accuracy_results.json').write_text(json.dumps(json_clean(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps({'runs':len(g),'replicate_sets':len(ss),'pooled':result['pooled_accuracy'],'udt':pd.DataFrame(udt).query("cfg == 'Pooled'").to_dict('records')},indent=2))


if __name__=='__main__':
    main()
