"""Read-only retrospective indexing; never executes archived agent code."""
import csv
import gzip
import hashlib
import json
import os
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
ROOTS = ['BixBench_50', 'CompBio', 'IWC']

def main():
    inventory = {}
    with (OUT/'file_inventory.tsv').open('w') as f:
        w=csv.writer(f, delimiter='\t'); w.writerow(['path','bytes','sha256'])
        for root in ROOTS:
            n = size = 0
            for parent, dirs, files in os.walk(BASE/root):
                dirs.sort()
                for name in sorted(files):
                    p=Path(parent)/name
                    h=hashlib.sha256()
                    with p.open('rb') as src:
                        while b:=src.read(1048576): h.update(b)
                    s=p.stat().st_size; n+=1; size+=s
                    w.writerow([str(p.relative_to(BASE)),s,h.hexdigest()])
            inventory[root]={'files_read':n,'bytes_read':size}
            print(root,inventory[root],flush=True)
    rows=[]; tasks=[]; failures=[]; event_counts=Counter()
    iwc=json.loads((BASE/'IWC/iwc_scientific_audit.json').read_text())
    iwc_runs={r['id']:r for r in iwc['runs']}
    for root in ROOTS:
        for p in sorted((BASE/root/'analysis').glob('*/history_analysis_evidence.json')):
            d=json.loads(p.read_text()); task=d['task']['task_id']
            task_rows=[]
            for r in d['runs']:
                o=r['outcome']; score=o.get('original_evaluator_score')
                record={'benchmark':root,'task':task,'run_id':r['run_id'],'condition':r['condition'],
                        'model':r['model']['supplied_label'],'replicate':r['replicate_id'],
                        'score':score,'score_kind':'binary_acceptance' if root=='BixBench_50' else 'unavailable',
                        'answer':o.get('submitted_answer'),'evidence_path':str(p.relative_to(BASE)),
                        'usage':r['usage'],'metrics':r['derived_metrics'],'trace_paths':[],
                        'evaluator_paths':[],'event_types':{},'error_events':[],
                        'limitations':r['limitations']}
                if root=='IWC':
                    a=iwc_runs[task+'/'+r['run_id']]
                    record.update(score=a['score'],score_kind='continuous_agreement',
                                  run_record_score=a['run_record_acc'],score_conflict=a['score_conflict_gt_1e_9'],
                                  usage=a['usage'],evaluation_error=a['evaluation_error'])
                record['outcome_label']=('accepted' if score==1 else 'rejected') if root=='BixBench_50' else (
                    'unscored' if root=='CompBio' else 'unsupported_route' if record['score'] is None else
                    'zero_agreement' if record['score']==0 else 'positive_agreement')
                for a in r['artifacts']:
                    if a.get('original_name','').endswith(('jsonl','jsonl.gz')):
                        record['trace_paths'].append(str(p.parent/a['local_path']).replace(str(BASE)+'/', ''))
                    if a.get('role')=='evaluator_output':record['evaluator_paths'].append(str(p.parent/a['local_path']).replace(str(BASE)+'/', ''))
                ec=Counter()
                for e in r['events']:
                    ec[e['event_type']]+=1; event_counts[(root,e['event_type'])]+=1
                    if e.get('exit_code') not in (None,0) or e.get('status') in ('error','failed'):
                        record['error_events'].append({k:e.get(k) for k in ['event_id','sequence','source_line','event_type','tool','command','parameters','status','exit_code','stdout_excerpt','stderr_excerpt','evidence_refs']})
                record['event_types']=dict(ec)
                rows.append(record);task_rows.append(record)
                if record['outcome_label'] in ('rejected','zero_agreement'):failures.append(record)
            tasks.append({'benchmark':root,'task':task,'prompt':d['task'].get('prompt'),
                          'runs':len(task_rows),'answers':dict(Counter(str(r['answer']) for r in task_rows)),
                          'outcomes':dict(Counter(r['outcome_label'] for r in task_rows))})
    (OUT/'run_index.json').write_text(json.dumps(rows,indent=2)+'\n')
    (OUT/'task_index.json').write_text(json.dumps(tasks,indent=2)+'\n')
    (OUT/'coverage.json').write_text(json.dumps({'inventory':inventory,'tasks':len(tasks),'runs':len(rows),'failure_records':len(failures),'event_types':{str(k):v for k,v in event_counts.items()}},indent=2)+'\n')
    with (OUT/'run_outcomes.tsv').open('w') as f:
        keys=['benchmark','task','run_id','condition','model','replicate','score','score_kind','outcome_label','score_conflict','run_record_score','answer','evidence_path']
        w=csv.DictWriter(f,fieldnames=keys,delimiter='\t',extrasaction='ignore');w.writeheader();w.writerows(rows)
    print('Indexed',len(rows),'runs;',len(failures),'rejected/zero records',flush=True)

if __name__=='__main__':main()
