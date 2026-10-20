#!/usr/bin/env python3
"""Six integrated manuscript figures from frozen archive-only analysis tables."""
from pathlib import Path
import json
import sys
import textwrap

import numpy as np
import pandas as pd
from matplotlib.colors import LogNorm
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Patch

PAPER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAPER.parent))
import narrative_common as nc
from narrative_common import plt, style

AN = PAPER / 'analysis'
FIG = PAPER / 'figures'
(FIG / 'previews').mkdir(exist_ok=True, parents=True)
BENCH = ['BixBench50', 'CompBio', 'IWC']
BL = {'BixBench50':'BixBench-Verified-50', 'CompBio':'CompBioBench', 'IWC':'IWC'}
PREFIX = {'BixBench50':'bix', 'CompBio':'cb', 'IWC':'iwc'}
CFG = list(nc.CODEX4)
ENVS = ['open_ended_code', 'galaxy']
SHORT = {'GPT-5.5':'5.5','GPT-5.6 Sol':'Sol','GPT-5.6 Luna':'Luna','DeepSeek V4 Pro':'DeepSeek'}
POOLED = 'All four primary configurations'
GROUPS = ['Agent analysis', 'Benchmark, reference or provenance', 'Galaxy platform or wrapper', 'Other']
GROUP_LABEL = {'Agent analysis':'Agent analysis', 'Benchmark, reference or provenance':'Benchmark, reference or provenance',
               'Galaxy platform or wrapper':'Galaxy platform or wrapper', 'Other':'Other'}
# Cause groups are not execution arms, so they avoid the arm colours (vermillion = code, blue = Galaxy).
GROUP_COLOR = {'Agent analysis':style.NEUTRAL_DARK, 'Benchmark, reference or provenance':style.OI_GREEN,
               'Galaxy platform or wrapper':style.OI_PURPLE, 'Other':style.NEUTRAL_LIGHT}
TAGS = ['Verification only', 'Verification and domain', 'Domain only', 'Neither tag']
TAG_COLOR = {'Verification only':style.NEUTRAL_DARK, 'Verification and domain':style.NEUTRAL_MID,
             'Domain only':style.OI_YELLOW, 'Neither tag':style.NEUTRAL_LIGHT}
DARK_FILLS = {style.NEUTRAL_DARK, style.OI_GREEN, style.OI_PURPLE, style.GALAXY}
NUM, PROV, TABLES = {}, {}, {}


def load(name):
    return pd.read_csv(AN / name)


def number(key, value, source):
    NUM[key] = str(value)
    PROV[key] = source


def signed(v, digits=1):
    return nc.fmt(v, digits, True)


def ci(r, digits=1):
    return f'{signed(r.difference,digits)} ({nc.fmt(r.ci95_low,digits)} to {nc.fmt(r.ci95_high,digits)})'


def ratio_ci(est, lo, hi, digits=2):
    return f'{nc.fmt(est,digits)} ({nc.fmt(lo,digits)} to {nc.fmt(hi,digits)})'


def count(v):
    return f'{int(round(v)):,}'


def table(name, frame):
    TABLES[name] = frame.copy()


def title(ax, letter, text):
    ax.set_title(f'{letter}   {text}', loc='left', fontsize=6.5, fontweight='bold', pad=7)


def save(fig, name, caption):
    style.enforce_min_font(fig)
    fig.savefig(FIG / f'{name}.pdf', metadata={'Title':caption, 'Subject':'Archive-derived Analysis figure; prospective result panel explicitly pending'})
    fig.savefig(FIG / 'previews' / f'{name}.png', dpi=300)
    plt.close(fig)


def dot_ci(ax, x, lo, hi, y, env):
    ax.errorbar(x, y, xerr=[[max(0,x-lo)],[max(0,hi-x)]], color=style.ENV_COLOR[env],
                marker=style.ENV_MARKER[env], ms=3.6, lw=.65, capsize=0, mec='white', mew=.4)


def draw_box(ax, x,y,w,h,text,fill='white',edge=style.INK2, fs=6, ls='-'):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.006,rounding_size=.01',
                transform=ax.transAxes,fc=fill,ec=edge,lw=.65,ls=ls,clip_on=False))
    ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=fs,transform=ax.transAxes,linespacing=1.3)


def arrow(ax,x0,y0,x1,y1):
    ax.add_patch(FancyArrowPatch((x0,y0),(x1,y1),arrowstyle='-|>',mutation_scale=7,
                transform=ax.transAxes,color=style.INK2,lw=.7,clip_on=False))


def stacked_bars(ax, rows, order, colors, min_label=4.5):
    """100% stacked horizontal bars. rows: list of (label, {segment: count}); segments are labelled with counts."""
    for i, (_, values) in enumerate(rows):
        total = sum(values.get(k, 0) for k in order)
        left = 0
        for k in order:
            v = values.get(k, 0)
            if not v:
                continue
            w = 100 * v / total
            ax.barh(i, w, left=left, color=colors[k], height=.62, ec='white', lw=.4)
            if w >= min_label:
                ax.text(left + w/2, i, f'{int(v):,}', ha='center', va='center', fontsize=5.5,
                        color='white' if colors[k] in DARK_FILLS else style.INK)
            left += w
    ax.set_yticks(range(len(rows)), [r[0] for r in rows])
    ax.set_ylim(len(rows) - .5, -.5)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])


def fig1():
    fig = plt.figure(figsize=(180*style.MM,145*style.MM))
    ax = fig.add_axes([.04,.60,.92,.31]); ax.axis('off'); title(ax,'a','Same task and model configuration, two assigned execution arms')
    draw_box(ax,.01,.24,.18,.49,'Biomedical task\n+ allowed inputs\n\nFour configurations\nThree replicate runs',style.LIGHT)
    draw_box(ax,.28,.57,.32,.35,'Open-ended code\nAgent installs software\nand writes analysis code',style.ENV_TINT[ENVS[0]],style.CODE)
    draw_box(ax,.28,.08,.32,.35,'Galaxy\nInstalled tools + agent-written UDTs\nJobs and analysis histories',style.ENV_TINT[ENVS[1]],style.GALAXY)
    draw_box(ax,.69,.25,.29,.47,'Submitted answer\n+ recorded analysis\n\nBenchmark-specific score\nReplicate consistency\nTokens and interface activity',style.LIGHT)
    for y in (.73,.25): arrow(ax,.19,.49,.28,y);arrow(ax,.60,y,.69,.49)
    axb=fig.add_axes([.04,.30,.92,.20]);axb.axis('off');title(axb,'b','Three endpoints remain separate')
    rows=[['Benchmark','Tasks','Runs per arm','Endpoint'],['BixBench-Verified-50','50','600','Original evaluator acceptance'],
          ['CompBioBench','100','1,200','Agreement with reconstructed key'],['IWC','9 of 10','108','Workflow-output agreement (0–1)']]
    xs=[.00,.39,.50,.66]
    for j,row in enumerate(rows):
        for x,s in zip(xs,row):axb.text(x,.84-j*.22,s,ha='left',va='top',fontsize=6,fontweight='bold' if j==0 else 'normal',transform=axb.transAxes)
    axb.axhline(.68,color=style.GRID,lw=.6)
    axc=fig.add_axes([.04,.03,.92,.19]);axc.axis('off');title(axc,'c','Analysis populations')
    draw_box(axc,.00,.52,.17,.40,'4,240\narchived runs',style.LIGHT)
    draw_box(axc,.27,.52,.30,.40,'3,840 assigned primary runs\n160 tasks × 4 configurations\n× 2 arms × 3 replicates',style.LIGHT)
    draw_box(axc,.67,.52,.32,.40,'3,816 endpoint runs\n159 tasks (nine IWC)',style.LIGHT)
    arrow(axc,.17,.72,.27,.72);arrow(axc,.57,.72,.67,.72)
    draw_box(axc,.04,.00,.36,.30,'Excluded: 100 unpaired Astra code runs;\n300 superseded-harness runs',ls='--',fs=5.6)
    draw_box(axc,.46,.00,.53,.30,'Excluded from endpoints: IWC host-removal task (24 runs),\nincomparable arm scores; retained in the interface audit',ls='--',fs=5.6)
    arrow(axc,.22,.72,.22,.31);arrow(axc,.62,.72,.62,.31)
    table('F1_design',pd.DataFrame([dict(benchmark=BL[b],primary_tasks=n,runs_per_arm=r,endpoint=e) for b,n,r,e in
          [('BixBench50',50,600,'Original evaluator acceptance'),('CompBio',100,1200,'Reconstructed-key agreement'),('IWC',9,108,'Workflow-output agreement (0-1)')]]))
    pr=load('accuracy_prompt_design.csv')
    for r in pr.itertuples():
        number(PREFIX[r.benchmark]+'_prompt_words_code',count(r.median_prompt_words_code),'Fig1 legend; accuracy_prompt_design.csv')
        number(PREFIX[r.benchmark]+'_prompt_words_galaxy',count(r.median_prompt_words_galaxy),'Fig1 legend; accuracy_prompt_design.csv')
    number('prompt_pairs',count(pr.prompt_pairs.sum()),'Fig1 legend; accuracy_prompt_design.csv, primary pairs')
    number('identical_prompt_pairs',int(pr.identical_prompt_pairs.sum()),'Fig1 legend; accuracy_prompt_design.csv')
    table('F1_prompts',pr)
    save(fig,'Fig1','Experimental setup and analysis populations')


def fig2():
    x=load('accuracy_benchmark_configuration.csv'); s=load('accuracy_sensitivities.csv')
    fig,axs=plt.subplots(2,3,figsize=(180*style.MM,155*style.MM))
    fig.subplots_adjust(left=.11,right=.97,top=.91,bottom=.12,wspace=.60,hspace=.64)
    for j,b in enumerate(BENCH):
        ax=axs[0,j]; title(ax,chr(97+j),BL[b])
        for i,c in enumerate(CFG+['Pooled']):
            r=x[(x.benchmark==b)&(x.cfg==c)].iloc[0]
            for k,e in enumerate(ENVS):dot_ci(ax,r[e],r[e+'_ci95_low'],r[e+'_ci95_high'],i+(k-.5)*.16,e)
        ax.set_yticks(range(5),[SHORT.get(c,c) for c in CFG+['Pooled']]);ax.invert_yaxis();style.grid_x(ax)
        ax.set_xlabel('Accepted runs (%)' if b=='BixBench50' else ('Key agreement (%)' if b=='CompBio' else 'Output agreement (0–1)'))
        ax.set_xlim((65,101) if b!='IWC' else (.68,1.025));ax.set_ylim(4.55,-.5)
        p=x[(x.benchmark==b)&(x.cfg=='Pooled')].iloc[0]
        prefix=PREFIX[b];nd=1 if b!='IWC' else 3
        number(prefix+'_code',nc.fmt(p.open_ended_code,nd),'Fig2; accuracy_benchmark_configuration.csv, Pooled')
        number(prefix+'_galaxy',nc.fmt(p.galaxy,nd),'Fig2; accuracy_benchmark_configuration.csv, Pooled')
        number(prefix+'_diff',ci(p,nd),'Fig2; accuracy_benchmark_configuration.csv, Pooled')
        aa=axs[1,j];title(aa,chr(100+j),'Sensitivity of the arm difference')
        groups=[('Primary',p)]
        for r in s[s.benchmark==b].itertuples():
            labels={'BixBench_exclude_benchmark_side_C1_C2_C3_C6':'Exclude 15\naudited tasks',
              'CompBio_exclude_outcome_named_cells':'Exclude 66\nflagged cells',
              'IWC_exclude_tasks_with_zero_run':'Exclude zero-score\ntasks',
              'IWC_exclude_ATAC_agent_calibrated_routes':'Exclude calibrated\nATAC',
              'IWC_budget_matched_pairs':'Equal-budget pairs'}
            label=labels.get(r.population,r.population.replace('_',' '))
            groups.append((label,r))
            number('sens_'+r.population,ci(r,nd),'Fig2; accuracy_sensitivities.csv, '+r.population)
        for i,(label,r) in enumerate(groups):
            aa.errorbar(r.difference,i,xerr=[[r.difference-r.ci95_low],[r.ci95_high-r.difference]],marker='o' if i==0 else 'D',ms=3.3,
                        mfc=style.INK if i==0 else 'white',mec=style.INK,color=style.INK,lw=.7)
        aa.set_yticks(range(len(groups)),[g[0] for g in groups]);aa.invert_yaxis();aa.axvline(0,color=style.NEUTRAL_MID,lw=.6,ls='--');style.grid_x(aa)
        aa.set_xlabel('Galaxy − code (points)' if b!='IWC' else 'Galaxy − code (agreement)')
        aa.set_ylim(len(groups)-.5,-.5)
    best=[]
    for b in BENCH:
        for e in ENVS:
            q=x[(x.benchmark==b)&x.cfg.isin(CFG)].sort_values(e,ascending=False).iloc[0]
            best.append(dict(benchmark=b,env=e,cfg=q.cfg,score=q[e]))
            number(f'{PREFIX[b]}_best_{e}',nc.fmt(q[e],1) if b!='IWC' else nc.fmt(q[e],3),'Fig2; accuracy_benchmark_configuration.csv, highest configuration ('+q.cfg+')')
    fig.legend(handles=style.env_handles(),loc='lower center',ncol=2,bbox_to_anchor=(.5,.015),fontsize=6)
    table('F2_scores',x);table('F2_sensitivity',s)
    save(fig,'Fig2','Observed performance and sensitivity by benchmark')


def fig3():
    r=load('accuracy_repeatability.csv');u=load('accuracy_udt_usage.csv');assoc=load('accuracy_udt_accuracy_association.csv')
    ov=load('accuracy_persistent_failure_overlap.csv')
    fig=plt.figure(figsize=(180*style.MM,165*style.MM))
    for j,b in enumerate(BENCH[:2]):
        ax=fig.add_axes([.14+j*.46,.66,.30,.24]);title(ax,chr(97+j),BL[b]+': all three correct')
        y=r[(r.benchmark==b)&(r.measure=='all_three_correct')]
        for i,c in enumerate(CFG):
            q=y[y.cfg==c].iloc[0];ax.errorbar(q.difference,i,xerr=[[q.difference-q.ci95_low],[q.ci95_high-q.difference]],
                            color=style.INK,marker='o',ms=3.6,lw=.7)
        ax.set_yticks(range(4),[SHORT[c] for c in CFG]);ax.invert_yaxis();ax.axvline(0,color=style.NEUTRAL_MID,ls='--',lw=.6)
        ax.set_xlabel('Galaxy − code (points)');style.grid_x(ax);ax.set_xlim(-17,23)
        p=y[y.cfg=='Pooled'].iloc[0]
        prefix=PREFIX[b]
        number(prefix+'_three_code',nc.fmt(p.open_ended_code,1),'Fig3; accuracy_repeatability.csv, all_three_correct, Pooled')
        number(prefix+'_three_galaxy',nc.fmt(p.galaxy,1),'Fig3; accuracy_repeatability.csv, all_three_correct, Pooled')
        o=ov[ov.benchmark==b].iloc[0]
        for key in ['three_rejected_sets_code','three_rejected_sets_galaxy','three_rejected_sets_both','three_rejected_tasks_code',
                    'three_rejected_tasks_galaxy','three_rejected_tasks_both','mixed_sets_code','mixed_sets_galaxy']:
            number(f'{prefix}_{key}',int(o[key]),'Fig3/Fig4; accuracy_persistent_failure_overlap.csv, '+key)
    ax=fig.add_axes([.20,.40,.64,.17]);title(ax,'c','Pooled discordance is lower; precision varies')
    pp=r[(r.cfg=='Pooled')&(r.measure=='discordant')]
    for i,b in enumerate(BENCH):
        q=pp[pp.benchmark==b].iloc[0];ax.errorbar(q.ratio,i,xerr=[[q.ratio-q.ratio_ci95_low],[q.ratio_ci95_high-q.ratio]],marker='o',ms=4,color=style.INK,lw=.7)
        number(b+'_discordance_ratio',f'{nc.fmt(q.ratio,2)} ({nc.fmt(q.ratio_ci95_low,2)} to {nc.fmt(q.ratio_ci95_high,2)})','Fig3; accuracy_repeatability.csv, discordant, Pooled')
        number(b+'_discordance_code',nc.fmt(q.open_ended_code,1),'Fig3; accuracy_repeatability.csv, discordant, Pooled')
        number(b+'_discordance_galaxy',nc.fmt(q.galaxy,1),'Fig3; accuracy_repeatability.csv, discordant, Pooled')
    ax.set_yticks(range(3),[BL[b] for b in BENCH]);ax.invert_yaxis();ax.axvline(1,color=style.NEUTRAL_MID,ls='--',lw=.6)
    ax.set_xlabel('Discordant-set ratio (Galaxy / code)');ax.set_xlim(0,2);style.grid_x(ax)
    for j,b in enumerate(BENCH[:2]):
        ax=fig.add_axes([.14+j*.46,.10,.30,.19]);title(ax,chr(100+j),BL[b]+': UDT use')
        q=u[(u.benchmark==b)&u.cfg.isin(CFG)].set_index('cfg').loc[CFG]
        for i,c in enumerate(CFG):
            z=q.loc[c];ax.barh(i-.15,100*z.observed_attempting_runs/z.runs,height=.28,color=style.NEUTRAL_MID)
            ax.barh(i+.15,100*z.observed_completed_ok_runs/z.runs,height=.28,color=style.GALAXY)
        ax.set_yticks(range(4),[SHORT[c] for c in CFG]);ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xlabel('Share of assigned Galaxy runs (%)');style.grid_x(ax)
        z=u[(u.benchmark==b)&(u.cfg=='Pooled')].iloc[0]
        prefix=PREFIX[b]
        for key,col in [('udt_attempt','observed_attempting_runs'),('udt_jobok','observed_completed_ok_runs'),('udt_returnok','observed_returned_ok_runs')]:
            number(prefix+'_'+key,int(z[col]),'Fig3; accuracy_udt_usage.csv, Pooled')
        a=assoc[(assoc.benchmark==b)&(assoc.cfg=='Pooled')].set_index('trajectory')
        for key,traj in [('udt_ok','At least one completed ok UDT job'),('udt_nook','Job record; no completed ok job observed'),('no_udt','No UDT request observed')]:
            if traj in a.index:
                number(f'{prefix}_{key}_acc',nc.fmt(100*a.loc[traj,'score_mean'],1),'Fig3 text; accuracy_udt_accuracy_association.csv, Pooled, '+traj)
                number(f'{prefix}_{key}_runs',count(a.loc[traj,'runs']),'Fig3 text; accuracy_udt_accuracy_association.csv, Pooled, '+traj)
    fig.legend(handles=[Patch(fc=style.NEUTRAL_MID,label='Observed UDT attempt'),Patch(fc=style.GALAXY,label='At least one recorded ok UDT job')],loc='lower center',ncol=2,bbox_to_anchor=(.5,.01),fontsize=5.7)
    table('F3_repeatability',r);table('F3_UDT_usage',u);table('F3_UDT_association',assoc)
    save(fig,'Fig3','Repeatability and agent-written code inside Galaxy')


def fig4():
    cen=load('rigor_census_categories.csv');tags=load('rigor_tag_overlap.csv');per=load('rigor_persistence.csv')
    tr=load('accuracy_cross_arm_error_transitions.csv');cases=load('rigor_cases.csv');rr=json.loads((AN/'rigor_results.json').read_text())
    fig=plt.figure(figsize=(180*style.MM,170*style.MM))
    # a. Cause groups in every task with a rejected primary run.
    ax=fig.add_axes([.25,.805,.27,.115]);title(ax,'a','Primary cause, every task with a rejected run')
    rows=[]
    for b,label in [('BixBench-Verified-50','BixBench-Verified-50'),('CompBioBench','CompBioBench'),('Both binary benchmarks','Both')]:
        q=cen[cen.benchmark==b].groupby('cause_group').tasks.sum()
        rows.append((f'{label} (n = {int(q.sum())})',q.to_dict()))
    stacked_bars(ax,rows,GROUPS,GROUP_COLOR);ax.set_xlabel('Tasks (%)')
    ax.legend(handles=[Patch(fc=GROUP_COLOR[g],label=GROUP_LABEL[g]) for g in GROUPS],ncol=2,fontsize=5.3,loc='upper left',bbox_to_anchor=(-.62,-.42))
    # b. Verification and domain-knowledge tags.
    ax=fig.add_axes([.75,.805,.22,.115]);title(ax,'b','Verification and domain tags')
    rows=[]
    for scope,label in [('Census: tasks with a rejected primary run','All failing tasks'),('Census: agent-analysis tasks','Agent analysis')]:
        q=tags[tags.scope==scope].set_index('tag_combination').task_cases
        rows.append((f'{label} (n = {int(q.sum())})',q.to_dict()))
    stacked_bars(ax,rows,TAGS,TAG_COLOR);ax.set_xlabel('Tasks (%)')
    ax.legend(handles=[Patch(fc=TAG_COLOR[t],label=t) for t in TAGS],ncol=2,fontsize=5.3,loc='upper left',bbox_to_anchor=(-.75,-.42))
    # c. Persistent (a set rejected 3/3) versus sporadic failures.
    ax=fig.add_axes([.25,.53,.27,.10]);title(ax,'c','Persistent versus sporadic failures')
    rows=[]
    for p,label in [('persistent (a set rejected 3/3)','Persistent: 3/3 rejected'),('sporadic (1-2 rejected per set)','Sporadic: 1–2 rejected')]:
        q=per[per.persistence==p].set_index('cause_group').tasks
        rows.append((f'{label} (n = {int(q.sum())})',q.to_dict()))
    stacked_bars(ax,rows,GROUPS,GROUP_COLOR);ax.set_xlabel('Tasks (%)')
    # d. The same task x configuration in both arms: rejected attempts out of three.
    for j,b in enumerate(['BixBench50','CompBio']):
        ax=fig.add_axes([.64+j*.19,.465,.13,.165])
        q=tr[tr.benchmark==b].pivot(index='code_rejected',columns='galaxy_rejected',values='sets').reindex(index=range(4),columns=range(4)).fillna(0)
        ax.imshow(q.values+0.5,cmap='Greys',norm=LogNorm(vmin=.5,vmax=400),aspect='equal')
        for i in range(4):
            for k in range(4):
                v=int(q.values[i,k]);ax.text(k,i,str(v),ha='center',va='center',fontsize=5.5,color='white' if v>=40 else style.INK)
        ax.set_xticks(range(4));ax.set_yticks(range(4));ax.set_xlabel('Galaxy rejected (of 3)');ax.set_ylabel('Code rejected (of 3)')
        ax.tick_params(length=0)
        for s in ax.spines.values():s.set_visible(False)
        ax.set_title(f'{"BixBench" if b=="BixBench50" else "CompBioBench"} ({int(q.values.sum())} pairs)',fontsize=6,fontweight='bold',pad=4)
    fig.text(.585,.675,'d   Rejected attempts, same task × configuration in both arms',fontsize=6.5,fontweight='bold')
    # e. Trace evidence.
    ax=fig.add_axes([.04,.03,.92,.33]);ax.axis('off');title(ax,'e','Recorded decisions identify concrete validation checks')
    headers=['Task','Recorded problem','Useful check']
    rows=[['bix-52-q2','Digits-only filter drops W and Z','Assert identifiers and row counts'],
          ['variant-status-q1','Pileup allele supported at read ends','Audit allele support by read position'],
          ['exogenous-mix-reads-q1','Fit and score on the same reference reads','Hold out or cross-fit read groups'],
          ['IWC mitogenome','Circularity or self-mapping used as identity','Test independent organellar identity'],
          ['histone-chip-q1','Negative candidate test not acted on','Reject candidate or broaden hypotheses']]
    xs=[.00,.29,.67]
    for x,h in zip(xs,headers):ax.text(x,.88,h,va='top',fontsize=5.8,fontweight='bold',transform=ax.transAxes)
    for i,row in enumerate(rows):
        for x,t in zip(xs,row):ax.text(x,.70-i*.15,textwrap.fill(t,40),va='top',fontsize=5.4,transform=ax.transAxes,linespacing=1.2)
    ax.plot([0,1],[.80,.80],color=style.GRID,lw=.6,transform=ax.transAxes)
    for key,col in [('audit_cases','audit_task_cases'),('census_tasks','census_tasks'),('census_verification','census_verification_tag'),
                    ('census_domain','census_domain_tag'),('census_both','census_both_tags'),('census_domain_only','census_domain_only'),
                    ('census_c5','census_C5'),('census_c5_verification','census_C5_verification_tag'),('census_c5_domain_only','census_C5_domain_only'),
                    ('census_rejected_runs','census_rejected_primary_runs'),('persistent_tasks','persistent_tasks'),('sporadic_tasks','sporadic_tasks'),
                    ('persistent_verification','persistent_verification_tag'),('sporadic_verification','sporadic_verification_tag')]:
        number(key,rr[col],'Fig4; rigor_results.json, '+col)
    n=rr['census_tasks']
    for key,num in [('census_verification',rr['census_verification_tag']),('census_domain_only',rr['census_domain_only'])]:
        number(key+'_pct',nc.fmt(100*num/n,1),'Fig4; rigor_results.json, '+key+' / census_tasks')
    number('census_c5_verification_pct',nc.fmt(100*rr['census_C5_verification_tag']/rr['census_C5'],1),'Fig4; rigor_results.json')
    for b,label in [('BixBench-Verified-50','bix'),('CompBioBench','cb')]:
        number(f'census_{label}',rr['census_tasks_by_benchmark'][b],'Fig4; rigor_results.json, census_tasks_by_benchmark')
        g=cen[cen.benchmark==b].groupby('cause_group').tasks.sum()
        for grp,key in [('Agent analysis','agent'),('Benchmark, reference or provenance','benchmark'),('Galaxy platform or wrapper','galaxy')]:
            number(f'census_{label}_{key}',int(g.get(grp,0)),'Fig4a; rigor_census_categories.csv, '+b)
    for g,key in [('Agent analysis','agent'),('Benchmark, reference or provenance','benchmark'),('Galaxy platform or wrapper','galaxy')]:
        v=rr['census_cause_groups'].get(g,0)
        number(f'census_{key}',v,'Fig4; rigor_results.json, census_cause_groups')
        number(f'census_{key}_pct',nc.fmt(100*v/n,1),'Fig4; rigor_results.json, census_cause_groups / census_tasks')
        runs=rr['census_rejected_primary_runs_by_group'][g]
        number(f'census_{key}_runs',runs,'Fig4; rigor_results.json, census_rejected_primary_runs_by_group')
        number(f'census_{key}_runs_pct',nc.fmt(100*runs/rr['census_rejected_primary_runs'],1),'Fig4; rigor_results.json')
        number(f'persistent_{key}',rr['persistent_cause_groups'].get(g,0),'Fig4; rigor_results.json, persistent_cause_groups')
        number(f'sporadic_{key}',rr['sporadic_cause_groups'].get(g,0),'Fig4; rigor_results.json, sporadic_cause_groups')
    table('F4_census',cen);table('F4_tags',tags);table('F4_persistence',per);table('F4_transitions',tr)
    table('F4_overlap',load('accuracy_persistent_failure_overlap.csv'));table('F4_cases',cases)
    save(fig,'Fig4','Causes of failure in every failing task and recorded validation evidence')


def fig5():
    front=load('token_model_pareto_common_tasks.csv');front=front[front.token_kind=='input_tokens']
    ratios=load('token_paired_arm_ratios.csv');ratios=ratios[ratios.task_scope=='primary_endpoint']
    totals=load('token_arm_total_ratios.csv');totals=totals[totals.task_scope=='primary_endpoint']
    sibling=load('token_outcome_sibling_summary.csv');sibling=sibling[sibling.cfg=='All four primary configurations']
    fig=plt.figure(figsize=(180*style.MM,170*style.MM))
    offsets={('CompBio','open_ended_code','GPT-5.5'):(-14,-12),('CompBio','open_ended_code','GPT-5.6 Sol'):(5,9),
             ('CompBio','open_ended_code','GPT-5.6 Luna'):(-17,12),('CompBio','open_ended_code','DeepSeek V4 Pro'):(8,-10),
             ('CompBio','galaxy','GPT-5.6 Luna'):(8,18),('CompBio','galaxy','DeepSeek V4 Pro'):(10,-16),
             ('BixBench50','open_ended_code','GPT-5.5'):(6,7),('BixBench50','open_ended_code','GPT-5.6 Sol'):(-14,-11),
             ('IWC','galaxy','DeepSeek V4 Pro'):(-38,3),('IWC','galaxy','GPT-5.6 Luna'):(2,-11),('IWC','galaxy','GPT-5.6 Sol'):(4,-10),
             ('IWC','galaxy','GPT-5.5'):(-15,-11),('BixBench50','galaxy','DeepSeek V4 Pro'):(-36,-9)}
    for k,e in enumerate(ENVS):
        for j,b in enumerate(BENCH):
            ax=fig.add_axes([.085+j*.315,.735-k*.265,.235,.195]);title(ax,chr(97+k*3+j),BL[b]+': '+('code' if k==0 else 'Galaxy'))
            q=front[(front.benchmark==b)&(front.env==e)]
            for i,c in enumerate(CFG):
                r=q[q.cfg==c].iloc[0];scale=100 if b!='IWC' else 1;x=r.median_tokens/1e6;y=r.mean_endpoint*scale
                ax.errorbar(x,y,xerr=[[x-r.token_ci95_low/1e6],[r.token_ci95_high/1e6-x]],
                    yerr=[[y-r.endpoint_ci95_low*scale],[r.endpoint_ci95_high*scale-y]],
                    marker=style.ENV_MARKER[e],ms=4.2,mfc=style.ENV_COLOR[e] if r.point_pareto_efficient else 'white',
                    mec=style.ENV_COLOR[e],color=style.ENV_COLOR[e],lw=.5,alpha=.8)
                off=offsets.get((b,e,c),(3,5 if c!='GPT-5.6 Sol' else -8))
                ax.annotate(SHORT[c],(x,y),xytext=off,textcoords='offset points',fontsize=5,
                            arrowprops={'arrowstyle':'-','lw':.35,'color':style.INK2} if (b,e,c) in offsets and abs(off[0])+abs(off[1])>16 else None)
            ax.set_xscale('log');ax.set_xlim(.10,35);ax.set_xticks([.1,1,10],['0.1','1','10']);ax.set_xticks([],minor=True)
            ax.set_xlabel('Median input tokens per run (millions)');ax.set_ylabel('Key/evaluator acceptance (%)' if b!='IWC' else 'Output agreement (0–1)')
            ax.set_ylim((65,101) if b!='IWC' else (.68,1.025));style.grid_x(ax)
    frontier=front.groupby('cfg').point_pareto_efficient.sum();frontier_mean=front.groupby('cfg').point_pareto_efficient_mean_tokens.sum()
    for c in CFG:
        number(f'frontier_{SHORT[c].lower()}',int(frontier[c]),'Fig5a-f; token_model_pareto_common_tasks.csv, point_pareto_efficient, six views')
        number(f'frontier_mean_{SHORT[c].lower()}',int(frontier_mean[c]),'Fig5 sensitivity; point_pareto_efficient_mean_tokens, six views')
    # g. Aggregate Galaxy/code input by configuration (ratio of totals), with uncached input and the median cell ratio.
    ax=fig.add_axes([.17,.05,.37,.30]);title(ax,'g','Galaxy/code input-token ratio by configuration')
    rows,labels=[],[]
    pos=0
    for b in BENCH:
        labels.append((pos,BL[b],True));pos+=1
        for c in [POOLED]+CFG:
            rows.append((pos,b,c));labels.append((pos,'Pooled' if c==POOLED else SHORT[c],False));pos+=1
    for p,b,c in rows:
        t=totals[(totals.benchmark==b)&(totals.cfg==c)].set_index('token_kind')
        m=ratios[(ratios.benchmark==b)&(ratios.cfg==c)&(ratios.token_kind=='input_tokens')].iloc[0]
        a,u=t.loc['input_tokens'],t.loc['uncached_input_tokens']
        ax.errorbar(a.ratio_of_totals,p-.17,xerr=[[a.ratio_of_totals-a.ci95_low],[a.ci95_high-a.ratio_of_totals]],marker='o',ms=3.2 if c!=POOLED else 3.8,
                    color=style.INK,lw=.6,mfc=style.INK)
        ax.errorbar(u.ratio_of_totals,p+.17,xerr=[[u.ratio_of_totals-u.ci95_low],[u.ci95_high-u.ratio_of_totals]],marker='D',ms=2.8,
                    color=style.NEUTRAL_MID,lw=.6,mfc='white',mec=style.INK2)
        ax.plot(m.median_ratio,p-.17,marker='|',ms=5,color=style.OI_ORANGE,mew=1.1,ls='')
    ax.set_yticks([l[0] for l in labels],[l[1] for l in labels])
    for tick,(_,_,bold) in zip(ax.get_yticklabels(),labels):
        if bold:tick.set_fontweight('bold')
    ax.set_ylim(pos-.5,-.5);ax.set_xscale('log');ax.set_xlim(.18,16)
    ax.set_xticks([.25,.5,1,2,4,8],['0.25','0.5','1','2','4','8']);ax.set_xticks([],minor=True)
    ax.axvline(1,color=style.NEUTRAL_MID,ls='--',lw=.6);style.grid_x(ax);ax.tick_params(axis='y',length=0)
    ax.set_xlabel('Galaxy / code input tokens (log scale)')
    ax.legend(handles=[Line2D([],[],marker='o',color=style.INK,ls='',ms=3.4,label='Total input (primary)'),
                       Line2D([],[],marker='D',mfc='white',mec=style.INK2,color=style.NEUTRAL_MID,ls='',ms=2.8,label='Total uncached input'),
                       Line2D([],[],marker='|',color=style.OI_ORANGE,ls='',ms=5,mew=1.1,label='Median within-cell ratio')],
              ncol=1,fontsize=5,loc='upper left',bbox_to_anchor=(0.0,1.0),handletextpad=.6)
    for b in BENCH:
        t=totals[(totals.benchmark==b)&(totals.cfg==POOLED)].set_index('token_kind')
        for kind,suffix in [('input_tokens','total_ratio'),('uncached_input_tokens','total_uncached')]:
            r=t.loc[kind];number(f'{PREFIX[b]}_{suffix}',ratio_ci(r.ratio_of_totals,r.ci95_low,r.ci95_high),'Fig5g; token_arm_total_ratios.csv, primary_endpoint, pooled, '+kind)
            number(f'{PREFIX[b]}_{suffix}_point',nc.fmt(r.ratio_of_totals,1),'Fig5g; token_arm_total_ratios.csv, pooled point estimate, '+kind)
        number(f'{PREFIX[b]}_token_cells',int(t.loc['input_tokens'].complete_cells),'Fig5g; token_arm_total_ratios.csv, complete_cells')
        for c in CFG:
            r=totals[(totals.benchmark==b)&(totals.cfg==c)&(totals.token_kind=='input_tokens')].iloc[0]
            number(f'{PREFIX[b]}_{SHORT[c].lower()}_total',ratio_ci(r.ratio_of_totals,r.ci95_low,r.ci95_high),'Fig5g; token_arm_total_ratios.csv, '+c)
            number(f'{PREFIX[b]}_{SHORT[c].lower()}_total_point',nc.fmt(r.ratio_of_totals,2),'Fig5g; token_arm_total_ratios.csv, '+c)
        m=ratios[(ratios.benchmark==b)&(ratios.cfg==POOLED)].set_index('token_kind')
        for kind,suffix in [('input_tokens','total'),('uncached_input_tokens','uncached')]:
            r=m.loc[kind];number(f'{PREFIX[b]}_tokens_{suffix}',ratio_ci(r.median_ratio,r.ci95_low,r.ci95_high),'Fig5g; token_paired_arm_ratios.csv, primary_endpoint, '+kind)
    above=totals[(totals.token_kind=='input_tokens')&totals.cfg.isin(CFG)]
    number('total_ratio_cells_above_one',int(above.greater_than_one_point.sum()),'Fig5g; token_arm_total_ratios.csv, configuration rows above one')
    unc=totals[(totals.token_kind=='uncached_input_tokens')&totals.cfg.isin(CFG)]
    number('uncached_ratio_cells_above_one',int(unc.greater_than_one_point.sum()),'Fig5g; token_arm_total_ratios.csv, uncached configuration rows above one')
    iw=load('token_iwc_task_inputs.csv').set_index(['task','env'])
    for task,key in [('wf_006_atacseq_chromatin_accessibility','atac'),('wf_007_vgp_mitogenome_assembly','mito')]:
        for e,suffix in [('open_ended_code','code'),('galaxy','galaxy')]:
            number(f'iwc_{key}_{suffix}_mean',nc.fmt(iw.loc[(task,e),'mean_input_tokens']/1e6,1),'Fig5 text; token_iwc_task_inputs.csv, mean_input_tokens (millions)')
    # h. Rejected versus accepted sibling attempts.
    ax=fig.add_axes([.74,.05,.23,.30]);title(ax,'h','Rejected versus accepted siblings')
    for i,(b,e) in enumerate([(b,e) for b in BENCH[:2] for e in ENVS]):
        r=sibling[(sibling.benchmark==b)&(sibling.env==e)].iloc[0]
        dot_ci(ax,r.median_rejected_over_accepted_tokens,r.ci95_low,r.ci95_high,i,e)
    ax.set_yticks(range(4),['Bix: code','Bix: Galaxy','CompBio: code','CompBio: Galaxy']);ax.invert_yaxis();ax.axvline(1,color=style.NEUTRAL_MID,ls='--',lw=.6)
    ax.set_xlim(.4,1.8);ax.set_xlabel('Rejected / accepted sibling input');style.grid_x(ax)
    table('F5_model_tradeoffs',front);table('F5_arm_totals',totals);table('F5_arm_ratios',ratios);table('F5_outcome',sibling)
    table('F5_IWC_tasks',load('token_iwc_task_inputs.csv'))
    save(fig,'Fig5','Benchmark-specific model trade-offs and token overhead')


FAIL_LABEL = {
    'A1 tool-schema needs history context':'Tool schema needed history context',
    'A2 tool ID not found / guessed':'Tool ID not found or guessed',
    'A3 nested-parameter key structure':'Nested parameter structure',
    'A4 parameter value / datatype validation':'Parameter value or datatype',
    'A5 ID handling (wrong/foreign/truncated IDs)':'Wrong or foreign dataset/history ID',
    'A6 UDT representation schema':'UDT definition schema',
    'A7 upload / datatype registry':'Upload or datatype registry',
    'A8 server / transport / rate-limit':'Server, transport or rate limit',
    'B1 UDT container missing dependency':'UDT container missing dependency',
    'B2 job error with no diagnostic':'Job error without diagnostic',
    'B3 tool runtime error (stderr)':'Tool runtime error with stderr',
    'B4 input format / compression / index':'Input format, compression or index',
    'B5 memory / resource':'Memory or resource',
    'X additional transport or tool exceptions (previously uncounted)':'Other transport or tool exception',
    'Z unclassified':'Unclassified'}
STAGE_COLOR = {'Request rejected before a job ran':style.NEUTRAL_MID,'Job failed during execution':style.NEUTRAL_DARK,'Other exception':style.NEUTRAL_LIGHT}
UDT_ORDER = ['Returned ok','Job error with diagnostic text','Job error without diagnostic text','Other non-ok return']
UDT_COLOR = {'Returned ok':style.GALAXY,'Job error with diagnostic text':style.NEUTRAL_MID,
             'Job error without diagnostic text':style.NEUTRAL_DARK,'Other non-ok return':style.NEUTRAL_LIGHT}


def fig6():
    op=load('token_operation_volume.csv');op=op[op.population=='four_primary_configurations'].copy()
    allop=op[op.benchmark=='All benchmarks'].sort_values('calls',ascending=False)
    fr=load('token_interface_friction.csv')
    short={'run_galaxy_tool_and_wait':'Installed tool + wait','search_galaxy_tools':'Tool search','inspect_galaxy_tool':'Tool inspection',
           'run_galaxy_udt_and_wait':'UDT + wait','peek_galaxy_dataset':'Dataset peek','inspect_galaxy_history':'History inspection',
           'stage_workspace_file':'File staging','wait_for_galaxy_jobs':'Job wait','inspect_archive_inventory':'Archive inventory'}
    fig=plt.figure(figsize=(180*style.MM,170*style.MM))
    ax=fig.add_axes([.17,.72,.30,.22]);title(ax,'a','Galaxy interface calls by operation')
    ax.barh(range(len(allop)),allop.calls,color=style.NEUTRAL_LIGHT,height=.68)
    ax.barh(range(len(allop)),allop.failed_calls,color=style.NEUTRAL_DARK,height=.68)
    ax.set_yticks(range(len(allop)),[short[o] for o in allop.operation]);ax.invert_yaxis();ax.set_xlabel('Interface calls');ax.set_xlim(0,22000)
    ax.set_xticks([0,5000,10000,15000,20000],['0','5,000','10,000','15,000','20,000'])
    for i,r in enumerate(allop.itertuples()):ax.text(r.calls+300,i,f'{r.failed_percent:.1f}%',va='center',fontsize=5)
    ax.legend(handles=[Patch(fc=style.NEUTRAL_LIGHT,label='All calls'),Patch(fc=style.NEUTRAL_DARK,label='Failed (% labelled)')],ncol=2,fontsize=5.2,loc='lower left',bbox_to_anchor=(-.08,-.30))
    ax=fig.add_axes([.68,.72,.29,.22]);title(ax,'b','Tool discovery')
    disc_rows=[]
    disc_colors=[style.NEUTRAL_LIGHT,style.NEUTRAL_MID,style.NEUTRAL_DARK]
    for i,b in enumerate(BENCH):
        q=op[(op.benchmark==b)&op.operation.isin(['search_galaxy_tools','inspect_galaxy_tool'])]
        calls=q.call_share_percent.sum();chars=q.character_share_percent.sum()
        nr=fr[(fr.benchmark==b)&(fr.measure=='Inspected tools never run in the same run')].iloc[0]
        for k,v in enumerate([calls,chars,nr.percent]):
            ax.barh(i+(k-1)*.25,v,height=.23,color=disc_colors[k])
            ax.text(v+1.5,i+(k-1)*.25,f'{v:.0f}',va='center',fontsize=5)
        disc_rows.append(dict(benchmark=BL[b],discovery_call_share_percent=calls,discovery_character_share_percent=chars,
                         inspected_never_run_percent=nr.percent))
        number(PREFIX[b]+'_discovery_chars',nc.fmt(chars,1),'Fig6b; token_operation_volume.csv, search + inspect tool, character_share_percent')
        number(PREFIX[b]+'_discovery_calls',nc.fmt(calls,1),'Fig6b; token_operation_volume.csv, search + inspect tool, call_share_percent')
        number(PREFIX[b]+'_never_run_pct',nc.fmt(nr.percent,1),'Fig6b; token_interface_friction.csv, inspected tools never run')
        number(PREFIX[b]+'_never_run',f'{int(nr["count"]):,} of {int(nr.denominator):,}','Fig6b; token_interface_friction.csv')
        number(PREFIX[b]+'_median_searches',int(fr[(fr.benchmark==b)&(fr.measure=='Median tool searches per run')].iloc[0]['count']),'Fig6 text; token_interface_friction.csv')
    ax.set_yticks(range(3),['BixBench','CompBio','IWC']);ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xlabel('Percent');style.grid_x(ax)
    ax.legend(handles=[Patch(fc=disc_colors[0],label='Search + inspection, share of calls'),Patch(fc=disc_colors[1],label='Search + inspection, share of returned text'),
                       Patch(fc=disc_colors[2],label='Inspected tools never run in that run')],fontsize=5.2,loc='lower left',bbox_to_anchor=(-.30,-.46))
    # c. Failure classes of failed Galaxy calls, primary configurations, all benchmarks.
    fc=load('token_failure_classes.csv');fc=fc[fc.population=='four_primary_configurations']
    cls=fc.groupby(['failure_stage','failure_class']).calls.sum().reset_index()
    order={'Request rejected before a job ran':0,'Job failed during execution':1,'Other exception':2}
    cls['o']=cls.failure_stage.map(order);cls=cls.sort_values(['o','calls'],ascending=[True,False])
    ax=fig.add_axes([.27,.235,.24,.335]);title(ax,'c','Why failed Galaxy calls failed')
    ax.barh(range(len(cls)),cls.calls,color=[STAGE_COLOR[s] for s in cls.failure_stage],height=.7)
    ax.set_yticks(range(len(cls)),[FAIL_LABEL[c] for c in cls.failure_class]);ax.invert_yaxis()
    for i,v in enumerate(cls.calls):ax.text(v+25,i,f'{int(v):,}',va='center',fontsize=5)
    ax.set_xlim(0,2000);ax.set_xticks([0,500,1000,1500,2000],['0','500','1,000','1,500','2,000']);ax.set_xlabel('Failed calls');style.grid_x(ax)
    ax.legend(handles=[Patch(fc=STAGE_COLOR[s],label=s) for s in order],fontsize=5.2,loc='upper right',bbox_to_anchor=(1.0,.80),ncol=1)
    total=int(cls.calls.sum())
    number('primary_failed_calls',f'{total:,}','Fig6c; token_failure_classes.csv, four_primary_configurations')
    for stage,key in [('Request rejected before a job ran','fail_request'),('Job failed during execution','fail_execution')]:
        v=int(cls[cls.failure_stage==stage].calls.sum());number(key,f'{v:,}','Fig6c; token_failure_classes.csv');number(key+'_pct',nc.fmt(100*v/total,1),'Fig6c')
    for c,key in [('A1 tool-schema needs history context','fail_a1'),('A2 tool ID not found / guessed','fail_a2'),('A4 parameter value / datatype validation','fail_a4'),
                  ('B2 job error with no diagnostic','fail_b2'),('B3 tool runtime error (stderr)','fail_b3'),('A5 ID handling (wrong/foreign/truncated IDs)','fail_a5')]:
        number(key,f'{int(cls[cls.failure_class==c].calls.sum()):,}','Fig6c; token_failure_classes.csv, '+c)
    # d. UDT call outcomes.
    bd=load('token_udt_call_breakdown.csv')
    ax=fig.add_axes([.72,.49,.25,.08]);title(ax,'d','UDT call outcomes')
    rows=[]
    for b in ['BixBench50','CompBio']:
        q=bd[bd.benchmark==b].set_index('call_outcome').calls
        rows.append((f'{"BixBench" if b=="BixBench50" else "CompBio"} (n = {int(q.sum()):,})',q.to_dict()))
    stacked_bars(ax,rows,UDT_ORDER,UDT_COLOR,min_label=6);ax.set_xlabel('UDT calls (%)')
    ax.legend(handles=[Patch(fc=UDT_COLOR[k],label=k) for k in UDT_ORDER],ncol=2,fontsize=5.1,loc='upper left',bbox_to_anchor=(-.45,-.62))
    cb=bd[bd.benchmark=='CompBio'].set_index('call_outcome')
    number('cb_udt_nodiag',f'{int(cb.loc["Job error without diagnostic text","calls"]):,}','Fig6d; token_udt_call_breakdown.csv')
    number('cb_udt_nodiag_pct',nc.fmt(cb.loc['Job error without diagnostic text','percent'],1),'Fig6d; token_udt_call_breakdown.csv')
    number('cb_udt_ok_pct',nc.fmt(cb.loc['Returned ok','percent'],1),'Fig6d; token_udt_call_breakdown.csv')
    bx=bd[bd.benchmark=='BixBench50'].set_index('call_outcome')
    number('bix_udt_ok_pct',nc.fmt(bx.loc['Returned ok','percent'],1),'Fig6d; token_udt_call_breakdown.csv')
    # e. Responses to failures without diagnostics.
    ax=fig.add_axes([.72,.235,.25,.105]);title(ax,'e','Failures without diagnostics')
    items=[('UDT job failures before execution without diagnostic text','UDT failures: no diagnostic,\nbefore execution','udt_prexec_nodiag'),
           ('Identical resubmission after a failed job without diagnostic text','Identical resubmission after\na no-diagnostic failure','resubmit'),
           ('Identical resubmissions that failed again','Identical resubmission\nfailed again','resubmit_failed')]
    probe=fr[(fr.benchmark=='CompBio')&(fr.measure=='Runs with probe or preflight-named calls')].iloc[0]
    for i,(measure,label,key) in enumerate(items):
        r=fr[fr.measure==measure].iloc[0]
        ax.barh(i,r.percent,color=style.NEUTRAL_DARK,height=.6)
        ax.text(r.percent+1.5,i,f'{int(r["count"]):,}/{int(r.denominator):,}',va='center',fontsize=5)
        number(key,f'{int(r["count"]):,}','Fig6e; token_interface_friction.csv, '+measure)
        number(key+'_n',f'{int(r.denominator):,}','Fig6e; token_interface_friction.csv, '+measure)
        number(key+'_pct',nc.fmt(r.percent,1),'Fig6e; token_interface_friction.csv, '+measure)
    ax.set_yticks(range(3),[x[1] for x in items]);ax.invert_yaxis();ax.set_xlim(0,100);ax.set_xlabel('Percent');style.grid_x(ax)
    number('cb_probe_runs',f'{int(probe["count"]):,}','Fig6 text; token_interface_friction.csv, probe runs')
    number('cb_probe_runs_n',f'{int(probe.denominator):,}','Fig6 text; token_interface_friction.csv')
    number('cb_probe_runs_pct',nc.fmt(probe.percent,1),'Fig6 text; token_interface_friction.csv')
    # f. Prospective study placeholder.
    ax=fig.add_axes([.04,.02,.92,.13]);ax.axis('off');title(ax,'f','Token-reduction intervention: results placeholder')
    gpt=load('token_arm_total_ratios.csv')
    gpt=gpt[(gpt.task_scope=='primary_endpoint')&(gpt.benchmark=='BixBench50')&(gpt.cfg=='GPT-5.5')&(gpt.token_kind=='input_tokens')].iloc[0]
    draw_box(ax,.01,.04,.97,.74,'RESULTS PENDING — placeholder until intervention results are confirmed and finalized\n\n'
       'Planned BixBench-Verified-50 comparison: frozen baseline, prompt/skill changes, MCP/execution changes and both (2 × 2),\n'
       f'with a contemporaneous code arm. Archived reference point: GPT-5.5 Galaxy/code total input = {nc.fmt(gpt.ratio_of_totals,2)}×. '
       'No reduction is reported here.',style.LIGHT,style.INK2,fs=6.0)
    number('primary_interface_calls',f'{int(allop.calls.sum()):,}','Fig6a; token_operation_volume.csv, four_primary_configurations, All benchmarks')
    u=allop[allop.operation=='run_galaxy_udt_and_wait'].iloc[0]
    number('udt_call_count',f'{int(u.calls):,}','Fig6a; token_operation_volume.csv, UDT, All benchmarks')
    number('udt_call_ok',nc.fmt(u.returned_ok_percent,1),'Fig6a; token_operation_volume.csv, UDT, returned_ok_percent')
    number('udt_call_failed',nc.fmt(u.failed_percent,1),'Fig6a; token_operation_volume.csv, UDT, failed_percent')
    number('tool_search_calls',f'{int(allop[allop.operation=="search_galaxy_tools"].calls.iloc[0]):,}','Fig6a; token_operation_volume.csv, search')
    number('tool_inspect_calls',f'{int(allop[allop.operation=="inspect_galaxy_tool"].calls.iloc[0]):,}','Fig6a; token_operation_volume.csv, inspect tool')
    number('gpt55_bix_total',ratio_ci(gpt.ratio_of_totals,gpt.ci95_low,gpt.ci95_high),'Fig6f; token_arm_total_ratios.csv, BixBench50 GPT-5.5 input_tokens')
    number('gpt55_bix_total_point',nc.fmt(gpt.ratio_of_totals,2),'Fig6f; token_arm_total_ratios.csv, BixBench50 GPT-5.5 input_tokens')
    act=load('token_actions_association.csv').set_index('benchmark')
    for b in BENCH:number(PREFIX[b]+'_actions_rho',nc.fmt(act.loc[b,'rho'],2),'Fig6 text; token_actions_association.csv, Spearman rho')
    interventions=[('Tool ID not found or guessed; inspected tools never run','Relevance-ranked search with type/operation filters; reusable inventories',
                    'Correct tool retrieval; versions retained'),
                   ('Tool schema needed history context; parameter value errors','History-scoped schemas; return only parameters relevant to the request',
                    'Requested and resolved parameters compared'),
                   ('UDT failures without diagnostics; identical resubmissions','Dependency and dispatch preflight; actionable failure payloads; resumable waits',
                    'First-attempt completion and diagnostics reported'),
                   ('Repeated large responses','Full records saved with hashes; bounded summaries returned to the model',
                    'Details retrievable on demand')]
    table('F6_operations',op);table('F6_discovery',pd.DataFrame(disc_rows));table('F6_failure_classes',fc);table('F6_udt_outcomes',bd)
    table('F6_friction',fr)
    table('F6_interventions',pd.DataFrame([dict(cost_mechanism=a,intervention_to_test=b,quality_guardrail=c,status='Proposed; reduction result pending') for a,b,c in interventions]))
    save(fig,'Fig6','Interface costs, failure modes and a pending token-reduction study')


def clean(value):
    if isinstance(value,dict):return {k:clean(v) for k,v in value.items()}
    if isinstance(value,list):return [clean(v) for v in value]
    if isinstance(value,(np.floating,float)) and not np.isfinite(value):return None
    if isinstance(value,np.generic):return value.item()
    return value


def export_tables():
    # Full observations make the plotted summaries auditable without exposing answers.
    table('Scored_runs',load('accuracy_primary_runs.csv'))
    table('Replicate_sets',load('accuracy_replicate_sets.csv'))
    tr=load('token_run_observations.csv');tr=tr[tr.model_primary & tr.primary_endpoint]
    table('Token_runs',tr[['benchmark','task','cfg','env','replicate','cluster','endpoint_score','input_tokens','cached','uncached_input_tokens','output_tokens']])
    table('Token_cells',load('token_cell_eligibility_and_ratios.csv').query("task_scope == 'primary_endpoint'"))
    table('Audit_tasks',load('rigor_task_cases.csv'))
    table('Trace_locators',load('rigor_evidence.csv'))
    docs=[]
    for name,frame in TABLES.items():
        for col in frame.columns:
            from column_dictionary import describe
            d=describe(col,name)
            docs.append([name,col,d])
    payload={'title':'Source Data for the integrated Galaxy manuscript','scope':'Four primary configurations, benchmark-specific endpoints; audit tags are task-level AI-assisted annotations covering every failing binary-benchmark task. No CompBioBench submitted/reference answers. Prospective reductions pending.',
       'tables':{n:{'columns':list(x.columns),'rows':clean(x.to_numpy().tolist())} for n,x in TABLES.items()},'dictionary':docs}
    (PAPER/'source_data'/'figure_source_data.json').write_text(json.dumps(payload,indent=1,ensure_ascii=False,allow_nan=False)+'\n')


def main():
    for fun in [fig1,fig2,fig3,fig4,fig5,fig6]:fun();print(fun.__name__+' done',flush=True)
    (PAPER/'numbers.json').write_text(json.dumps(NUM,indent=2,ensure_ascii=False)+'\n')
    (PAPER/'numbers_provenance.json').write_text(json.dumps(PROV,indent=2,ensure_ascii=False)+'\n')
    export_tables()


if __name__=='__main__':main()
