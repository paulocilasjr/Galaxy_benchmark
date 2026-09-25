"""Render the retrospective report and individual evidence dossiers."""
import collections
import json
import re
from pathlib import Path
from adjudications import classify

HERE = Path(__file__).resolve().parent
BASE = HERE.parents[1]
RUNS = json.loads((HERE / 'run_index.json').read_text())
PACKETS = json.loads((HERE / 'failure_evidence.json').read_text())
INDEX = {(r['task'], r['run_id']): r for r in RUNS}


def cell(x):
    return str(x).replace('|', '&#124;').replace('\n', ' ').replace('<', '&lt;')


def link(label, path, line=None):
    p = Path(path)
    if not p.is_absolute():
        p = BASE / p
    assert p.exists(), p
    dest = str(p) + (f':{line}' if line is not None and p.suffix != '.gz' else '')
    return f'[{label}](<{dest}>)'


def trace_link(match):
    task, run, line, label = match.groups()
    r = INDEX[(task, run)]
    path = r['trace_paths'][0]
    return link(label, path, int(line)) + f' (L{line}; decompressed line numbering)'


def table(headers, rows):
    return '\n'.join(['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |'] +
                     ['| ' + ' | '.join(cell(v) for v in row) + ' |' for row in rows])


def bix_table():
    models = ['Codex GPT-5.5', 'Codex GPT-5.6 Sol', 'Codex GPT-5.6 Luna',
              'DeepSeek V4 Pro via Codex', 'DeepSeek V4 Pro via Claude Code (superseded)']
    rows = []
    for m in models:
        row = [m]
        for c in ['galaxy', 'open_ended_code']:
            all_m = [r for r in RUNS if r['benchmark']=='BixBench_50' and r['model']==m and r['condition']==c]
            for rep in [1,2,3]:
                a = [r for r in all_m if r['replicate']==rep]
                good = sum(r['score']==1 for r in a)
                row.append(f'{good}/{len(a)-good}')
            row.append(f"{sum(r['score']==1 for r in all_m)}/{sum(r['score']==0 for r in all_m)}")
        rows.append(row)
    return table(['Model/harness','Galaxy r1','G r2','G r3','G total','Code r1','C r2','C r3','C total'], rows)


def compbio_table():
    audit = json.loads((BASE/'CompBio/compBio_overview_audit.json').read_text())
    vs = audit['score_vectors']
    models = [('codex_gpt_5_5','GPT-5.5'),('codex_gpt_5_6_sol','GPT-5.6 Sol'),('codex_gpt_5_6_luna','GPT-5.6 Luna'),
              ('codex_deepseek_v4_pro_0813','DeepSeek V4 Pro (Codex)'),('codex_gpt_6_astra','GPT-6 Astra')]
    rows=[]
    for model,label in models:
        row=[label]
        for c in ['galaxy','open_ended_code']:
            for rep in ['r1','r2','r3']:
                a=[v for v in vs if v['model']==model and v['condition']==c and v['replicate']==rep]
                if not a:row.append('—');continue
                v=a[0];mark='O' if v['score_type']=='official_labelled' else 'P'
                status='!' if v['hash_matches'] is False else '?' if v['hash_matches'] is None else ''
                row.append(f"{v['score']} {mark}{status}")
        rows.append(row)
    return table(['Model','Galaxy r1','G r2','G r3','Code r1','C r2','C r3'],rows)


def iwc_table():
    models=['GPT-5.5','GPT-5.6 Sol','GPT-5.6 Luna','Codex + DeepSeek V4 Pro'];rows=[]
    for m in models:
        for c in ['galaxy','open_ended_code']:
            row=[m,'Galaxy' if c=='galaxy' else 'Custom code']
            for rep in [1,2,3]:
                a=[r for r in RUNS if r['benchmark']=='IWC' and r['model']==m and r['condition']==c and r['replicate']==rep]
                pos=sum(r['score'] is not None and r['score']>0 for r in a);zero=sum(r['score']==0 for r in a);null=sum(r['score'] is None for r in a)
                mean=sum(r['score'] for r in a if r['score'] is not None)/(len(a)-null)
                row.append(f'{pos}/{zero}/{null}; {mean:.4f}')
            rows.append(row)
    return table(['Model','Track','r1: +/0/NA; mean','r2: +/0/NA; mean','r3: +/0/NA; mean'],rows)


FOCUS = {
 ('bix-12-q4','open_ended_code_codex_gpt_5_6_luna_r1'):[70,72],
 ('bix-16-q1','galaxy_codex_gpt_5_6_luna_r2'):[58],
 ('bix-28-q3','galaxy_codex_gpt_5_6_sol_r1'):[44,47,49],
 ('bix-35-q1','galaxy_deepseek_v4_pro_via_claude_code_superseded_r1'):[6618],
 ('wf_007_vgp_mitogenome_assembly','galaxy_gpt_5_5_r1'):[70,75,82,89,127],
 ('wf_007_vgp_mitogenome_assembly','open_ended_code_gpt_5_5_r1'):[354,447,456],
 ('wf_007_vgp_mitogenome_assembly','open_ended_code_codex_deepseek_v4_pro_r2'):[161,163,171,179,183],
 ('wf_010_pseudobulk_scrna_de','open_ended_code_codex_deepseek_v4_pro_r3'):[60,63],
 ('wf_005_amplicon_dada2_pe_denoising','open_ended_code_gpt_5_5_r1'):[37],
 ('wf_005_amplicon_dada2_pe_denoising','open_ended_code_gpt_5_5_r3'):[91],
}

KEYWORDS={
 'bix-12':['Counter','mannwhitney','counts','phykit','informative'],
 'bix-14':['synonymous','coding_so','fraction','VAF'],
 'bix-16':['spearman','correl','sort ','rho','significant'],
 'bix-22':['pearson','correl','CD14','CD4'],
 'bix-24':['enrich','metabol','upreg','downreg'],
 'bix-26':['background','foreground','pathway','split(','adjust'],
 'bix-27':['prcomp','svd','PCA','variance','duplicat'],
 'bix-28':['long_branch','median'],
 'bix-30':['t.test','ttest','p.adjust','significant','Ct'],
 'bix-31':['FAM138A','Deseq','deseq','filter'],
 'bix-32':['enrich','intersection','pathway'],
 'bix-34':['distance','median','mldist','shared'],
 'bix-35':['evolutionary','total_tree','mannwhitney','median'],
 'bix-43':['odds','background','Reactome','Contingency'],
 'bix-45':['rcv','mannwhitney','2.0.3','wilcox'],
 'bix-49':['Deseq','deseq','significant'],
 'bix-51':['Logistic','logit','coefficient'],
 'bix-52':['density','retained','19159','19160','539','wc -l'],
 'bix-53':['increase','1931','1479','significant'],
 'bix-54':['StrainNumber','spline','optimize','maximize'],
 'bix-55':['BUSCO','busco','Complete','intersection'],
 'bix-61':['TSTV','transversion','transition','depth','bcftools'],
}


def relevant_calls(p):
    events=p['calls'];chosen={}
    for line in FOCUS.get((p['task'],p['run_id']),[]):
        near=[e for e in events if abs(e['source_line']-line)<=1]
        if near:chosen[near[0]['event_id']]=near[0]
    keys=next((v for k,v in KEYWORDS.items() if p['task'].startswith(k)),[])
    rated=[]
    for e in events:
        s=' '.join(str(e.get(k) or '') for k in ['command','parameters','stdout_excerpt','stderr_excerpt'])
        # Exclude routine schema browsing from evidence snippets unless explicitly selected.
        if 'tool_response.json' in s or 'build_response.json' in s:continue
        score=sum(k.lower() in s.lower() for k in keys)
        if score: rated.append((score,e['source_line'],e))
    for _,_,e in sorted(rated,key=lambda x:(x[0],x[1]),reverse=True)[:3]:chosen.setdefault(e['event_id'],e)
    if not chosen:
        for e in events[-2:]:chosen[e['event_id']]=e
    return sorted(chosen.values(),key=lambda e:e['source_line'])


def excerpt(s, maxlen=3200):
    s=str(s or '')
    if len(s)>maxlen:s=s[:maxlen]+'\n[Excerpt truncated here; complete normalized/raw call is linked.]'
    return s.replace('```','` ` `')


def dossiers_and_table():
    doc=['# Individual rejected/zero-run evidence dossiers\n',
         'Each entry preserves the original verdict and a separate retrospective attribution. These excerpts are selected locators, not the complete trace. Full normalized call sequences are in `failure_evidence.json`; raw trace links retain original detail. Unresolved means that no specific causal scientific error has been established. Line numbers refer to the decompressed source.\n']
    rows=[];annotations=[]
    for n,p in enumerate(PACKETS,1):
        r=INDEX[(p['task'],p['run_id'])];primary,note,confidence,secondary=classify(r)
        ident=f'failure-{n:03d}';answer='[missing]' if p['answer'] is None else p['answer']
        dest=str(HERE/'failure_dossiers.md')+f'#{ident}'
        rows.append([p['task'],('Galaxy' if p['condition']=='galaxy' else 'Code')+' / '+p['model']+' / r'+str(p['replicate']),
                     cell(answer),primary,confidence,f'[F{n:03d}]({dest})'])
        annotations.append({'id':ident,'benchmark':p['benchmark'],'task':p['task'],'run_id':p['run_id'],
                            'primary':primary,'secondary':secondary,'assessment':note,'confidence':confidence,
                            'original_score':p['score'],'original_answer':p['answer']})
        doc.extend([f'<a id="{ident}"></a>\n',f'## F{n:03d}: {p["task"]} — {p["run_id"]}\n',
                    f'Original verdict: **{p["outcome_label"]}**, score {p["score"]}; answer: `{answer}`.\n',
                    f'**Primary:** {primary}. **Confidence:** {confidence}. {note}\n',
                    f'**Secondary:** {secondary}\n',
                    'Sources: '+', '.join([link('raw trace',x) for x in p['trace_paths']]+[link('evaluator',x) for x in p['evaluator_paths']]+[link('task evidence',p['evidence_path'])])+'.\n'])
        if p['evaluator_paths']:
            try:
                ev=json.loads((BASE/p['evaluator_paths'][0]).read_text())
                if 'accuracy' in ev:doc.extend(['Saved accuracy record:\n','```json\n'+json.dumps(ev['accuracy'],indent=2)+'\n```\n'])
            except (ValueError,UnicodeError):pass
        doc.append('Selected actual call/result evidence (the causal interpretation is stated above):\n')
        for e in relevant_calls(p):
            doc.append(f'**Source L{e["source_line"]}; {e.get("tool") or e["event_type"]}; status {e.get("status")}; exit {e.get("exit_code")}.**\n')
            args=e.get('command') or json.dumps(e.get('parameters'),indent=2)
            result=e.get('stdout_excerpt') or e.get('stderr_excerpt') or '[No text result preserved in normalized excerpt.]'
            doc.append('```text\n'+excerpt(args)+'\n\nRESULT:\n'+excerpt(result)+'\n```\n')
        doc.append('Recorded operational counts (not automatically causal): `'+json.dumps(r['metrics'],sort_keys=True)+'`.\n')
    (HERE/'failure_dossiers.md').write_text('\n'.join(doc))
    (HERE/'failure_adjudications.json').write_text(json.dumps(annotations,indent=2)+'\n')
    return table(['Task','Track / model / replicate','Submitted answer','Primary attribution','Confidence','Evidence'],rows)


def main():
    body=(HERE/'report_body.md').read_text()
    body=re.sub(r'\{\{trace:([^|}]+)\|([^|}]+)\|(\d+)\|([^}]+)\}\}',trace_link,body)
    body=body.replace('{{BIX_TABLE}}',bix_table()).replace('{{COMPBIO_TABLE}}',compbio_table()).replace('{{IWC_TABLE}}',iwc_table())
    body=body.replace('{{FAILURE_TABLE}}',dossiers_and_table())
    # Make repo-local evidence links directly clickable in the workspace client.
    body=re.sub(r'\[([^\]]+)\]\((analysis_reports/[^)]+|CompBio/[^)]+|IWC/[^)]+|BixBench_50/[^)]+)\)',
                lambda m:link(m[1],m[2]),body)
    assert '{{' not in body
    out=BASE/'Galaxy_improvement_report.md';out.write_text(body)
    assert len(PACKETS)==252
    assert sum(p['benchmark']=='BixBench_50' for p in PACKETS)==246
    assert sum(p['benchmark']=='IWC' for p in PACKETS)==6
    print(f'Wrote {out}: {len(body):,} characters; {len(PACKETS)} individual failure entries.')


if __name__=='__main__':main()
