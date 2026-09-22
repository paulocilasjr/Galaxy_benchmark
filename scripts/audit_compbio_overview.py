"""Reproduce CompBio overview, Results tables and their evidence manifest offline."""
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import random
import re
import statistics
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "CompBio"
META = BASE / "source_snapshots/aggregate_metadata"
sys.path.insert(0, str(BASE))
import solution_path_consistency_analysis as paths
sys.path.insert(0, str(ROOT / "analysis_execution"))
from workbook import load_inventory
from validate import validate

CONDITIONS = paths.CONDITIONS
MODELS = paths.MODELS
LABEL = paths.LABEL
SITE_MODELS = {"gpt55": MODELS[0], "sol": MODELS[1], "luna": MODELS[2], "deepseek": MODELS[3]}


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def quantile(values, p):
    values = sorted(values)
    if not values:
        return None
    i = (len(values)-1)*p
    return values[math.floor(i)] + (values[math.ceil(i)]-values[math.floor(i)])*(i-math.floor(i))


def describe(values):
    values = [v for v in values if v is not None]
    return {"n": len(values), "median": statistics.median(values) if values else None,
            "q1": quantile(values, .25), "q3": quantile(values, .75),
            "min": min(values) if values else None, "max": max(values) if values else None}


def table(title, headers, rows, note=""):
    def escape(v):
        if isinstance(v, str) and v in CONDITIONS:
            v = {"galaxy": "Galaxy", "open_ended_code": "Open-ended code"}[v]
        return str(v).replace("|", "\\|").replace("\n", " ")
    return "\n".join([f"**{title}**", "", "| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"] +
                     ["| " + " | ".join(escape(v) for v in row) + " |" for row in rows] + ["", note, ""])


def fmt(value, digits=2):
    return "Unavailable" if value is None else f"{value:.{digits}f}"


def history_state_summary(history):
    state_ids = history.get("state_ids")
    counts = {state: len(ids) for state, ids in state_ids.items()} if state_ids is not None else None
    unique_ids = {item for ids in state_ids.values() for item in ids} if state_ids is not None else None
    details = history.get("state_details") or {}
    return {
        "state_id_counts": counts,
        "elements_without_state_id": history["count"] - len(unique_ids)
        if history.get("count") is not None and unique_ids is not None else None,
        "state_count_disagreements": {
            state: {"state_details": details[state], "state_ids_count": count}
            for state, count in (counts or {}).items() if state in details and details[state] != count
        },
    }


def top_tools_with_ties(counts, limit=3):
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    if not ranked:
        return []
    cutoff = ranked[min(limit, len(ranked)) - 1][1]
    return [(tool, count) for tool, count in ranked if count >= cutoff]


def build(validate_packages=False):
    inventory = load_inventory(BASE / "compbiobench_execution_condition_links.xlsx")
    expected = {(x.task, x.run_id): x for x in inventory}
    records, manifests, tasks, jobs, conflicts = {}, [], [], {}, []
    capped, recoveries, histories = [], [], set()
    for p in sorted((BASE / "analysis").glob("*/history_analysis_evidence.json")):
        e = validate(p.parent, mark_passed=False) if validate_packages else read(p)
        task = e["task"]["task_id"]
        assert len(e["runs"]) == 25
        manifests.append({"task": task, "evidence_path": str(p.relative_to(BASE)), "evidence_sha256": sha(p),
                          "report_path": str(p.with_name('history_analysis.md').relative_to(BASE)), "report_sha256": sha(p.with_name('history_analysis.md')),
                          "included_run_ids": [r["run_id"] for r in e["runs"]], "finding_ids": [f["finding_id"] for f in e["manuscript_findings"]]})
        for r in e["runs"]:
            key = task, r["run_id"]
            assert key not in records and key in expected
            link = expected[key]
            assert (r["condition"], r["replicate_id"], r["model"]["supplied_label"]) == (link.condition, link.replicate, link.model)
            trace_source = next(s for s in e["sources"] if s["source_id"] == "src_trace_" + r["run_id"])
            assert trace_source["location"] == link.trace_url
            records[key] = r
            for ev in r["events"]:
                if ev["execution_location"] != "galaxy_job":
                    continue
                jk = r["environment"]["galaxy_server"], ev["native_job_id"]
                if jk in jobs and (jobs[jk]["status"], jobs[jk]["tool"]) != (ev["status"], ev["tool"]):
                    conflicts.append(jk)
                jobs[jk] = ev
            for episode in r["recovery_episodes"]:
                recoveries.append({"task": task, "run_id": r["run_id"], **episode})
        for s in e["sources"]:
            if not s["source_id"].startswith("src_galaxy_"):
                continue
            histories.add(s["location"])
            if s["access_status"] == "history_metadata_only":
                h = read(p.parent / s["local_snapshot"] / "history.json")
                capped.append({"task": task, "source_id": s["source_id"], "count": h.get("count"), "states": h.get("state_details"),
                               **history_state_summary(h),
                               "path": str((p.parent / s["local_snapshot"] / "history.json").relative_to(BASE))})
        by_cond = {c: [r for r in e["runs"] if r["condition"] == c and paths.model(r) in MODELS] for c in CONDITIONS}
        tasks.append({"task": task, "domain": e["task"].get("domain"), "prompt": e["task"]["prompt"],
                      "answers": {c: dict(Counter(r["outcome"]["submitted_answer"] for r in rs)) for c, rs in by_cond.items()},
                      "tools": dict(Counter(v["tool"] for r in by_cond["galaxy"] for v in r["events"] if v["execution_location"] == "galaxy_job" and v["event_type"] == "analysis")),
                      "evidence_path": str(p.relative_to(BASE))})
    assert set(records) == set(expected) and len(records) == 2500
    assert len(tasks) == 100 and not conflicts
    runs = list(records.values())
    cases = []
    for task, rid, failed_id, later_id, interpretation in [
        ('bedtools-chromhmm-q1','galaxy_codex_deepseek_v4_pro_0813_r2','bbd44e69cb8906b5c39271b5fbfb4cf5','bbd44e69cb8906b55252779ccd350d58',
         'Explicit float conversion repaired the same column calculation; operational correction supported, answer correctness unavailable.'),
        ('perturb-seq-align-q1','galaxy_codex_deepseek_v4_pro_0813_r3','bbd44e69cb8906b5fd717ea8a10ddbc6','bbd44e69cb8906b5086075ff0eb0610c',
         'chunk_X inspection failed; later var inspection succeeded. Different operations: not confirmation of recovery of the original objective.')]:
        events = {v.get('native_job_id'): v for v in records[task,rid]['events'] if v.get('native_job_id')}
        failed, later = events[failed_id], events[later_id]
        assert failed['status']=='error' and later['status']=='ok' and failed['timestamp']<later['timestamp']
        assert failed['native_input_hda_ids']==later['native_input_hda_ids']
        cases.append({'task':task,'run_id':rid,'failed_event':failed,'later_event':later,'interpretation':interpretation})
    primary = [r for r in runs if paths.model(r) in MODELS]
    group = defaultdict(list)
    for r in runs:
        group[r["task_id"], paths.model(r), r["condition"]].append(r)
    token_pairs, token_excluded = [], []
    for task in sorted(t["task"] for t in tasks):
        for model in MODELS:
            members = {c: group[task, model, c] for c in CONDITIONS}
            assert all(len(v) == 3 and {r['replicate_id'] for r in v} == {1,2,3} for v in members.values())
            vals = {c: [r["usage"]["provider_reported_input_tokens"] for r in rs] for c, rs in members.items()}
            entry = {"task": task, "model": model, "included_run_ids": [r["run_id"] for rs in members.values() for r in rs]}
            if all(isinstance(v, (int,float)) and v >= 0 for vs in vals.values() for v in vs) and statistics.median(vals['open_ended_code']) > 0:
                medians = {c: statistics.median(v) for c,v in vals.items()}
                ids = {r['model']['verified_runtime_id'] for rs in members.values() for r in rs}
                settings = {r['model']['reasoning_setting'] for rs in members.values() for r in rs}
                token_pairs.append({**entry, "medians": medians, "ratio": medians['galaxy']/medians['open_ended_code'],
                                    "all_runtime_ids_verified_same": len(ids) == 1 and None not in ids,
                                    "all_reasoning_settings_verified_same": len(settings) == 1 and None not in settings})
            else:
                token_excluded.append({**entry,"reason":"At least one missing usage total or zero code median"})
    rng = random.Random(20260921)
    by_task = defaultdict(list)
    for p in token_pairs:
        by_task[p['task']].append(p['ratio'])
    task_names = sorted(by_task)
    boot = [statistics.median(v for t in rng.choices(task_names,k=len(task_names)) for v in by_task[t]) for _ in range(10000)]
    numerical = {
        "inventory": {"tasks":len(tasks),"runs":len(runs),"paired_runs":len(primary),"unpaired_astra_runs":len(runs)-len(primary),
                      "workbook_path":"compbiobench_execution_condition_links.xlsx","workbook_sha256":sha(BASE/'compbiobench_execution_condition_links.xlsx'),
                      "expected_protocol_coverage":"unknown; supplied workbook rows all matched", "paired_task_model_cells":400,
                      "per_item_scores_available":sum(r['outcome']['original_evaluator_score'] is not None for r in runs)},
        "task_manifest":manifests,"tasks":tasks,"token_pairs":token_pairs,"token_excluded":token_excluded,
        "tokens": {"pooled":describe(p['ratio'] for p in token_pairs),
                   "bootstrap":{"unit":"task, keeping eligible configuration bundles", "seed":20260921,"resamples":10000,"percentile95":[quantile(boot,.025),quantile(boot,.975)],"status":"exploratory; independence across tasks not established"},
                   "by_model":{m:describe(p['ratio'] for p in token_pairs if p['model']==m) for m in MODELS},
                   "runtime_verified_sensitivity":describe(p['ratio'] for p in token_pairs if p['all_runtime_ids_verified_same']),
                   "runtime_and_reasoning_verified_sensitivity":describe(p['ratio'] for p in token_pairs if p['all_runtime_ids_verified_same'] and p['all_reasoning_settings_verified_same'])},
        "execution":{"unique_histories":len(histories),"all_creating_jobs":len(jobs),"job_conflicts":conflicts,
                     "all_job_states":dict(Counter(v['status'] for v in jobs.values())),
                     "nonfetch_jobs":sum(v['tool']!='__DATA_FETCH__' for v in jobs.values()),
                     "nonfetch_states":dict(Counter(v['status'] for v in jobs.values() if v['tool']!='__DATA_FETCH__')),
                     "data_fetch_jobs":sum(v['tool']=='__DATA_FETCH__' for v in jobs.values()),
                     "legacy_upload_jobs":sum(v['tool']=='upload1' for v in jobs.values()),
                     "tools":dict(Counter(v['tool'] for v in jobs.values() if v['tool']!='__DATA_FETCH__').most_common()),
                     "job_refs":[{"server":k[0],"native_job_id":k[1],"event_id":v['event_id']} for k,v in jobs.items()],
                     "capped_histories":capped,"recovery_candidates":recoveries,
                     "recovery_runs":len({(r['task'],r['run_id']) for r in recoveries})},
        "run_summaries":[],"coverage":{},"score_vectors":[],"score_conflicts":[]}
    numerical['case_reviews'] = cases
    numerical['token_distributions'] = [{
        'model':m,'condition':c,'listed_runs':len(sub),
        'input_tokens':describe(r['usage']['provider_reported_input_tokens'] for r in sub),
        'output_tokens':describe(r['usage']['provider_reported_output_tokens'] for r in sub),
        'runs_without_usage':[{'task':r['task_id'],'run_id':r['run_id']} for r in sub if r['usage']['provider_reported_input_tokens'] is None],
        'correct_only_summary':None,'correct_only_missingness':'No item-level evaluator scores'}
        for m in MODELS+['codex_gpt_6_astra'] for c in CONDITIONS
        if (sub := [r for r in runs if paths.model(r)==m and r['condition']==c])]
    for r in runs:
        numerical['run_summaries'].append({"task":r['task_id'],"run_id":r['run_id'],"condition":r['condition'],"model":paths.model(r),
            "runtime_model":r['model']['verified_runtime_id'],"reasoning":r['model']['reasoning_setting'],
            "usage":r['usage'],"transcript":r['evidence_completeness']['agent_transcript'],
            "history":r['evidence_completeness']['public_history_contents'],
            "metrics":r['derived_metrics'],"prompt_sha256":r['prompt_sha256'],"answer_sha256":r['outcome']['submitted_answer_sha256']})
    for c in CONDITIONS:
        sub=[r for r in primary if r['condition']==c]
        numerical['coverage'][c]={"runs":len(sub),"usage":sum(r['usage']['provider_reported_input_tokens'] is not None for r in sub),
            "transcripts":sum(r['evidence_completeness']['agent_transcript']=='retrieved' for r in sub),
            "history_status":dict(Counter(r['evidence_completeness']['public_history_contents'] for r in sub)),
            "runs_with_job_failure":sum((r['derived_metrics']['total_failed_jobs'] or 0)>0 for r in sub),
            "job_failure_coverage":sum(r['derived_metrics']['total_failed_jobs'] is not None for r in sub),
            "runs_with_nonzero_shell":sum(r['derived_metrics']['nonzero_exit_shell_calls']>0 for r in sub),
            "failed_jobs_distribution":describe(r['derived_metrics']['total_failed_jobs'] for r in sub),
            "nonzero_shell_distribution":describe(r['derived_metrics']['nonzero_exit_shell_calls'] for r in sub if r['evidence_completeness']['agent_transcript']=='retrieved')}
    site=read(META/'paper_site_runs.json')
    old={r['campaign_id']:r for r in csv.DictReader((META/'compbiobench/replicates.tsv').open(),delimiter='\t')}
    for m in site['models']:
        for cond,v in m['conditions'].items():
            for rep in v['replicates']:
                c='galaxy' if cond=='galaxy' else 'open_ended_code'
                rid=c+'_'+SITE_MODELS[m['id']]+'_'+rep['id']
                path=META/'compbiobench/replicates'/rep['campaign_id']/'predictions.tsv'
                rows=list(csv.DictReader(path.open(),delimiter='\t')) if path.exists() else []
                mismatches=[a['question_id'] for a in rows if records[a['question_id'],rid]['outcome']['submitted_answer']!=a['answer']]
                kind='official_labelled' if 'official_score' in rep else 'predicted'
                score=rep.get('official_score',rep.get('predicted_score'))
                entry={"model":SITE_MODELS[m['id']],"condition":c,"replicate":rep['id'],"campaign_id":rep['campaign_id'],
                       "score":score,"score_type":kind,"denominator":100,"source":"source_snapshots/aggregate_metadata/paper_site_runs.json",
                       "source_pointer":f"models/{site['models'].index(m)}/conditions/{cond}/replicates/{v['replicates'].index(rep)}",
                       "advertised_sha256":rep['vector_sha256'],"observed_sha256":sha(path) if path.exists() else None,
                       "vector_path":str(path.relative_to(BASE)) if path.exists() else None,
                       "hash_matches":sha(path)==rep['vector_sha256'] if path.exists() else None,"answers_compared":len(rows),"answer_mismatch_tasks":mismatches,
                       "source_campaigns":rep['roots'],"included_run_ids":[rid],"included_task_ids":sorted(r['question_id'] for r in rows)}
                prior=old.get(rep['campaign_id'])
                if prior and (float(prior['score'])!=score or ('official' in prior['score_type'])!=(kind=='official_labelled')):
                    numerical['score_conflicts'].append({"campaign":rep['campaign_id'],"older_score":prior['score'],"older_type":prior['score_type'],"site_score":score,"site_type":kind})
                numerical['score_vectors'].append(entry)
    astra_path=META/'compbiobench/run_traces_compbiobench_codex_gpt6_astra'
    astra=read(astra_path/'submission.json'); ap=astra_path/'predictions.tsv'
    ar=list(csv.DictReader(ap.open(),delimiter='\t'))
    numerical['score_vectors'].append({"model":"codex_gpt_6_astra","condition":"open_ended_code","replicate":"r1",
        "score":astra['official_score'],"score_type":"official_labelled","denominator":astra['total'],"source":str((astra_path/'submission.json').relative_to(BASE)),
        "advertised_sha256":astra['sha256'],"observed_sha256":sha(ap),"hash_matches":sha(ap)==astra['sha256'],"vector_path":str(ap.relative_to(BASE)),
        "answers_compared":len(ar),"answer_mismatch_tasks":[a['question_id'] for a in ar if a['answer']!=records[a['question_id'],'open_ended_code_codex_gpt_6_astra_r1']['outcome']['submitted_answer']]})
    assert not any(x['answer_mismatch_tasks'] for x in numerical['score_vectors'])
    numerical['solution_paths']=paths.analyze()
    numerical['source_manifest']=read(META/'manifest.json')
    for source in numerical['source_manifest']['sources']:
        assert sha(BASE/source['path'])==source['sha256']
    numerical['validation']={"workbook_rows":"2500/2500 matched without duplicates","source_hashes":"passed",
                             "per_task_full_validation":"passed" if validate_packages else "not run this invocation",
                             "unknown_scores_remain_null":all(r['outcome']['original_evaluator_score'] is None for r in runs)}
    numerical['software']={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),BASE/'solution_path_consistency_analysis.py',ROOT/'BixBench_50/solution_path_consistency_analysis.py',ROOT/'scripts/enrich_compbio_evidence.py']}
    return numerical


def write_reports(a):
    ex=a['execution']; cov=a['coverage']; sp=a['solution_paths']; tok=a['tokens']; score=a['score_vectors']
    usage=sum(r['usage']['provider_reported_input_tokens'] is not None for r in a['run_summaries'])
    errors=ex['nonfetch_states'].get('error',0)+ex['nonfetch_states'].get('failed',0)
    intro=("We retrospectively examined 2,500 workbook-linked CompBioBench run records for 100 tasks. "
           "The paired descriptive population comprises four configurations (GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro 0813 through Codex), "
           "two environments and three replicate labels: 2,400 records, 1,200 per environment and 800 triplicate cells. "
           "The remaining 100 GPT-6 Astra records comprise one open-ended-code run per task and are reported separately. "
           "All workbook rows match the retained task, model label, environment, replicate and trace URL. "
           "An independent selection and stopping protocol was unavailable. Replicate labels do not establish independent executions or matched seeds: "
           "the supplied campaign metadata assembles final vectors from initial, continuation and recovery campaigns. "
           "These are final archived selections, not measured first-attempt success rates. Runtime metadata, prompt hashes and source roots are retained per run. "
           "Submitted answers, original evaluator outcomes, operational states and auditor interpretations remain distinct.")
    n_off=sum(s['score_type']=='official_labelled' for s in score); n_pred=len(score)-n_off
    n_hash=sum(s['hash_matches'] is True for s in score); bad_hash=sum(s['hash_matches'] is False for s in score); absent=sum(s['hash_matches'] is None for s in score)
    conflicts_by_campaign = {s['campaign']: s for s in a['score_conflicts']}
    rows=[]
    for m in MODELS+['codex_gpt_6_astra']:
        cells=[]
        for c in CONDITIONS:
            sub=[s for s in score if s['model']==m and s['condition']==c]
            entries=[]
            for s in sub:
                annotations=['O' if s['score_type']=='official_labelled' else 'P']
                if s['hash_matches'] is False:
                    annotations.append('hash mismatch')
                elif s['hash_matches'] is None:
                    annotations.append('vector unavailable')
                prior=conflicts_by_campaign.get(s.get('campaign_id'))
                if prior:
                    prior_type='O' if 'official' in prior['older_type'] else 'P'
                    annotations.append(f"previously {prior['older_score']}/100 {prior_type}")
                entries.append(f"{s['replicate']}: {s['score']}/100 ({'; '.join(annotations)})")
            cells.append('; '.join(entries) or 'Not represented')
        rows.append([LABEL[m],*cells])
    tables={1:table('Table 1. Source-reported answer-vector scores', ['Configuration','Galaxy','Open-ended code'],rows,
        'O = archive-labelled official leaderboard score; P = prediction. Labels are preserved, not independently regraded or promoted to item-level official outcomes. Scores refer to 100-answer vectors. '
        f'Hash mismatch means retained vector bytes disagree with the advertised SHA-256 ({bad_hash} entries); vector unavailable means no vector bytes were retrieved and zero answers were compared ({absent} Luna Galaxy entries). '
        f'The other {n_hash} hashes match. Parsed answers agree for all {len(score)-absent} available vectors. '
        'Previous Sol scores are from `replicates.tsv`; displayed scores are from the dated `paper_site_runs.json`. No pooled official comparison is calculated from this mixture.')}
    sol_revisions=' and '.join(
        f"from {conflicts_by_campaign[s['campaign_id']]['older_score']} to {s['score']}/100 for {s['replicate']}"
        for s in score if s['model']=='codex_gpt_5_6_sol' and s['condition']=='galaxy' and s.get('campaign_id') in conflicts_by_campaign)
    accuracy=(f"Per-task original evaluator scores are unavailable for all 2,500 records. The archived `evaluation.stdout.txt` files report submission-format validation, "
              f"not scientific correctness. Additional source retrieval recovered 25 aggregate score labels: {n_off} official-labelled and {n_pred} predicted (Table 1). "
              f"Of the advertised vector hashes, {n_hash} match retained bytes, {bad_hash} do not, and {absent} have no corresponding downloaded vector. "
              "For every available vector, all parsed answers match the per-run submitted answers. This establishes content agreement with those files, "
              "but does not resolve disagreement with the advertised submission hash. Two Sol Galaxy entries change from predictions in `replicates.tsv` "
              f"to official-labelled scores in the dated `paper_site_runs.json`, with numerical revisions {sol_revisions}; "
              "both versions are retained in the conflict ledger and shown in Table 1. "
              "The dated site metadata is displayed with explicit attribution, not treated as an independently verified leaderboard receipt. "
              "GPT-6 Astra has an archive-labelled 93/100 score for its single open-ended vector and no Galaxy counterpart. "
              "Task-level accuracy differences, all/some/none accepted counts, accuracy bootstrap intervals, outcome-versus-route associations and accepted results per token "
              "cannot be recovered from aggregate totals. No missing score is treated as failure, no predicted score substitutes for an official result, "
              "and no equivalence, non-inferiority or superiority claim follows from these records.")
    trows=[]
    for c in CONDITIONS:
        counts=[len(t['answers'][c]) for t in a['tasks']]
        trows.append([c,100,1200,fmt(statistics.median(counts),1),sum(n==1 for n in counts),'Unavailable'])
    tables[2]=table('Table 2. Task coverage and submitted-answer convergence',['Environment','Tasks','Runs','Median distinct answers/task','Tasks with one answer','Tasks with accepted answers'],trows,
        'Four paired configurations only: 12 answers per task and environment. Answer identity uses archived text with outer whitespace stripped, without numeric rounding. `run_summaries.answer_sha256` hashes raw answer-file bytes, whereas Tables 2-3 compare `outcome.submitted_answer`, already stripped during evidence construction; grouping by those hashes can therefore give different counts. It is not correctness or semantic agreement; BixBench six-significant-figure normalization is inappropriate for heterogeneous CompBio lists, identifiers and coordinates.')
    tables[3]=table('Table 3. Triplicate answer consistency, distinct from acceptance',['Environment','Configuration','One distinct answer','Two','Three','Scored triplicate cells'],[
        [c,LABEL[m],*[sum(x['distinct_submitted_answers']==n for x in sp['cells'] if x['condition']==c and x['model']==m) for n in (1,2,3)],0]
        for c in CONDITIONS for m in MODELS], 'Each row contains 100 task cells. The BixBench all/some/none accepted analysis remains unavailable; these counts describe answer text only.')
    tables[4]=table('Table 4. Most frequent retained Galaxy creating-job tool IDs',['Tool ID (recorded version)','Distinct jobs'],list(ex['tools'].items())[:12],
        'Deduplicated by Galaxy server and native job ID across all histories. Excludes `__DATA_FETCH__`; includes 372 legacy `upload1` jobs as a table row. Preparation jobs are included, so these are not counts of independent scientific analyses.')
    case_names=['1000G-retrieve-genotype-q1','annotate-variant-regulatory-overlap-q1','perturb-seq-align-q1','deg-simple-q1','reverse-search-gwas-q1','sample-swap-atac-q1']
    tables[5]=table('Table 5. Task-specific execution examples',['Task','Domain','Distinct answers G / code','Recorded Galaxy operations (top 3, including ties; counts)','Official item outcomes'],[
        [f"[{t['task']}](analysis/{t['task']}/history_analysis.md)",t['domain'],f"{len(t['answers']['galaxy'])} / {len(t['answers']['open_ended_code'])}",'; '.join(f'{k} ({v})' for k,v in top_tools_with_ties(t['tools'])),'Unavailable']
        for name in case_names for t in a['tasks'] if t['task']==name],
        'Illustrative tasks selected by domain and evidence availability, not by inferred success. Counts are recorded analysis-type Galaxy job events across the 12 paired-configuration runs for each task. All tools tied at the third-entry count are included, ordered alphabetically within ties. Tool presence and completed jobs do not demonstrate an accepted final answer. Complete tool IDs, parameters, failures and submitted answers are linked in each task package.')
    state_rows=[['Unique linked Galaxy histories',ex['unique_histories']],['Galaxy runs with detailed contents',cov['galaxy']['history_status'].get('retrieved',0)],
                ['Metadata-only histories',len(ex['capped_histories'])],['All distinct creating jobs',ex['all_creating_jobs']],['Data-fetch jobs',ex['data_fetch_jobs']],
                ['Legacy upload1 jobs within non-fetch category',ex['legacy_upload_jobs']],['Non-fetch creating jobs',ex['nonfetch_jobs']]]
    state_rows += [[f'Non-fetch job state: {k}',v] for k,v in sorted(ex['nonfetch_states'].items())]
    state_rows += [['Recovery candidates',len(ex['recovery_candidates'])],['Runs containing a recovery candidate',ex['recovery_runs']]]
    tables[6]=table('Table 6. Execution availability, states and operational recovery candidates',['Measure','Count'],state_rows,
        'Current snapshots can include inherited or later state. Failed jobs are not failures before a correct answer; that endpoint is unobserved. Same-tool, same-input later success identifies a candidate operational recovery, not an adjudicated scientific correction.')
    execution=(f"Detailed Galaxy contents were retained for {cov['galaxy']['history_status'].get('retrieved',0)}/1,200 runs; "
               f"{len(ex['capped_histories'])} histories have metadata only. Across the snapshots, {ex['all_creating_jobs']:,} distinct creating jobs include "
               f"{ex['data_fetch_jobs']:,} data-fetch jobs and {ex['nonfetch_jobs']:,} non-fetch jobs. The latter include {errors:,} failed/error jobs "
               f"({100*errors/ex['nonfetch_jobs']:.1f}%; Table 6). "
               f"At least one failed non-fetch job appears in {cov['galaxy']['runs_with_job_failure']}/{cov['galaxy']['job_failure_coverage']} evaluable Galaxy runs. "
               f"At least one nonzero shell exit appears in {cov['galaxy']['runs_with_nonzero_shell']}/{cov['galaxy']['transcripts']} available Galaxy-condition transcripts "
               f"and {cov['open_ended_code']['runs_with_nonzero_shell']}/{cov['open_ended_code']['transcripts']} open-ended-code transcripts. "
               "These are counts of runs with a recorded shell exit, not counts of failed Galaxy jobs; a shell exit may represent a probe or search rather than a failed analysis. "
               f"The retained records flag {len(ex['recovery_candidates'])} candidate same-tool/input failure-to-success sequences across {ex['recovery_runs']} Galaxy runs. "
               "They support investigation of recovery, not a comparative recovery benefit. The tool inventory combines installed tools with task-specific identifiers; "
               "custom identifiers alone cannot distinguish a standard domain tool from a user-defined wrapper. No run is certified Galaxy-only without an adjudicated "
               "event-level computation-location audit. Inherited input preparation, calls to external services, and local orchestration must be distinguished from substantive analysis. "
               "The full error/parameter records and candidate event IDs remain available in the numerical audit and task ledgers.")
    execution += ("\n\nA concrete parameter correction is visible in `bedtools-chromhmm-q1`, DeepSeek Galaxy replicate 2. "
                  "The column-making expression `round(c1/c5*100)` failed because both columns were strings. "
                  "A later job on the same input used `round(float(c1)/float(c5)*100)`, reached `ok`, and reported that it computed "
                  "the new column for all input lines. This supports an operational correction, without establishing correctness of the chosen biological denominator. "
                  "A contradictory example shows why automated recovery counts need review: in `perturb-seq-align-q1`, DeepSeek Galaxy replicate 3, "
                  "AnnData `chunk_X` failed with a sparse-matrix attribute error, while the later successful job requested `var` metadata. "
                  "It used the same tool and input but performed a different operation, so success did not demonstrate recovery of the original objective. "
                  "Both failed/later event pairs, exact parameters, timestamps and output excerpts are retained in `case_reviews` in the numerical audit.")
    nonidentical=sum(set(t['answers']['galaxy'])!=set(t['answers']['open_ended_code']) for t in a['tasks'])
    tables[7]=table('Table 7. Environment comparisons and unavailable accuracy endpoints',['Measure','Result'],[
        ['Task-level answer sets differ between environments',f'{nonidentical}/100'],['Task-level answer sets identical',f'{100-nonidentical}/100'],
        ['Tasks with Galaxy-only accepted answers','Not assessable'],['Strict discordance (3 accepted versus 0)','Not assessable'],
        ['Cross-configuration consistency of accuracy advantage','Not assessable'],['Verifier-mode effects','Not assessable']],
        'Different submitted answers need not differ scientifically or in evaluation. Aggregate vector scores cannot locate discordant tasks.')
    indicators=['bedtools','samtools','bcftools','anndata','scanpy','numpy','pandas','scipy']
    routes=[]
    for c in CONDITIONS:
        for m in MODELS:
            fingerprints=[fp for cell in sp['cells'] if cell['condition']==c and cell['model']==m for fp in cell['fingerprints']]
            routes.append([c,LABEL[m],*[sum(any(token in f.lower() for f in fp) for fp in fingerprints) for token in indicators]])
    tables[8]=table('Table 8. Selected CompBio tool and library indicators',['Environment','Configuration',*indicators],routes,
        'Non-exclusive numbers of runs out of 300 per row. Galaxy indicators are substring matches on structured job tool IDs; open-ended-code indicators use the unchanged BixBench closed command vocabulary. Absence of an indicator is not absence of the scientific method. Custom wrappers may conceal library use, and missing/empty fingerprints are excluded from primary agreement estimates.')
    tables[9]=table('Table 9. Triplicate solution-path agreement',['Environment','Configuration','Identical','Two identical','All distinct','Not evaluable','Identical %','Mean Jaccard'],[
        [r['condition'],LABEL.get(r['model'],'All configurations'),r.get('identical',0),r.get('two_of_three',0),r.get('all_distinct',0),r.get('not_evaluable',0),fmt(r['pct_identical'],1),fmt(r['mean_jaccard'],3)] for r in sp['by_condition_and_model']],
        'Same fingerprint vocabulary and normalization as BixBench. Jaccard is the number of shared fingerprint elements divided by the number in their union; Mean Jaccard averages the three replicate-pair similarities per cell, then averages across eligible cells. Primary estimates require three observable nonempty fingerprints. Empty or missing records are not agreement. The numerical output also records the legacy BixBench inclusion-rule sensitivity. Astra has only one replicate and its 100 cells are explicitly excluded. Fingerprints ignore order and most parameters, so agreement is not workflow equivalence; magnitudes across environments use different instruments.')
    driver_rows=[]
    for key,label in [('task_mean_sd','Task mean Jaccard standard deviation'),('configuration_mean_sd','Configuration mean Jaccard standard deviation')]:
        driver_rows.append([label,*[fmt(sp['drivers'][c][key],3) for c in CONDITIONS]])
    for variable in ('median_events','median_jobs','mean_fingerprint_size'):
        driver_rows.append([f'Spearman correlation: {variable}',*[f"{fmt(sp['drivers'][c]['correlations'][variable]['spearman_rho'],3)} (n={sp['drivers'][c]['correlations'][variable]['n']})" for c in CONDITIONS]])
    for flag,label in [('True','Cells with a recorded failed Galaxy job'),('False','Cells without a recorded failed Galaxy job')]:
        v=sp['drivers']['galaxy']['failure_groups'][flag]
        driver_rows.append([label,f"{fmt(v['mean_jaccard'],3)} (n={v['n']})",'Not applicable'])
    driver_rows.append(['Association with answer acceptance','Not assessable','Not assessable'])
    cross=sp['cross_condition_task_correlation']
    tables[10]=table('Table 10. Descriptive associations with path variability',['Measure','Galaxy','Open-ended code'],driver_rows,
        f"Across the {cross['n']} tasks with an evaluable task mean in both environments, Spearman rho between task mean Jaccard values was {fmt(cross['spearman_rho'],3)}. "
        'Task means average eligible configuration cells; the contributing configurations can differ between environments. The two failure-group rows report mean Jaccard, not correlations. Cells share tasks and are not independent observations. Task difficulty is not inferred from failures or token use. Fingerprint-size-stratified failure associations are retained in the JSON; none establishes causality.')
    g=next(r for r in sp['by_condition_and_model'] if r['condition']=='galaxy' and r['model']=='ALL')
    o=next(r for r in sp['by_condition_and_model'] if r['condition']=='open_ended_code' and r['model']=='ALL')
    variability=(f"Among {g['evaluable_cells']} evaluable Galaxy triplicate cells, {g.get('identical',0)} had identical recorded toolsets "
                 f"({fmt(g['pct_identical'],1)}%); mean pairwise Jaccard agreement was {fmt(g['mean_jaccard'],3)}. "
                 f"The corresponding open-ended-code counts were {o.get('identical',0)}/{o['evaluable_cells']} "
                 f"({fmt(o['pct_identical'],1)}%) and {fmt(o['mean_jaccard'],3)} (Table 9). "
                 "Galaxy fingerprints come from structured version-stripped tool identifiers, while code fingerprints come from vocabulary matches in commands. "
                 "These instruments differ in resolution and visibility, precluding a direct ranking of scientific solution consistency between environments. "
                 "The closed vocabulary is intentionally unchanged from BixBench for side-by-side evaluation, but can omit CompBio-specific software. "
                 "Tables 8-10 therefore describe observed indicators and configuration differences within an environment, not adjudicated biological methods. "
                 f"Task mean agreement was weakly correlated across environments (Spearman rho = {fmt(cross['spearman_rho'],3)}, n = {cross['n']} tasks; Table 10). "
                 "These indicators show little cross-environment correspondence in task rankings; they do not establish that task identity has no effect on path variability. "
                 "Submitted-answer consistency is reported independently in Tables 2-3. Without item-level scores, convergent answers cannot be called correct, "
                 "and divergent paths cannot be counted as valid alternative solutions. No independent difficulty strata or controlled prompt-version comparison were available.")
    rows=[[LABEL[m],tok['by_model'][m]['n'],fmt(tok['by_model'][m]['median']),f"{fmt(tok['by_model'][m]['q1'])}-{fmt(tok['by_model'][m]['q3'])}"] for m in MODELS]
    rows.append(['All paired configurations',tok['pooled']['n'],fmt(tok['pooled']['median']),f"{fmt(tok['pooled']['q1'])}-{fmt(tok['pooled']['q3'])}"])
    tables[11]=table('Table 11. Galaxy/open-ended-code input-token ratios',['Configuration','Eligible task comparisons','Median ratio','IQR'],rows,
        'Each ratio divides the median of three Galaxy input totals by the median of three open-ended-code totals for the same task and supplied configuration. IQR columns report the first and third quartiles (Q1-Q3), rather than their difference. All six totals must be available; excluded pairs are listed in the audit. This is a median of task/configuration ratios, not a ratio of pooled totals or matched-seed runs. Cached input is already included and is not added again; output and reasoning fields remain separate.')
    lo,hi=tok['bootstrap']['percentile95']
    cost=(f"Provider-reported primary-turn usage was recovered for {usage}/2,500 runs. Complete usage in both environments permitted "
          f"{tok['pooled']['n']}/400 task-by-configuration comparisons. Their median Galaxy/open-ended-code input-token ratio was "
          f"{fmt(tok['pooled']['median'])} (IQR {fmt(tok['pooled']['q1'])}-{fmt(tok['pooled']['q3'])}; range "
          f"{fmt(tok['pooled']['min'])}-{fmt(tok['pooled']['max'])}; Table 11). An exploratory task-block bootstrap gave a 95% percentile interval "
          f"of {fmt(lo)}-{fmt(hi)} (10,000 resamples, seed 20260921). This interval treats task bundles as independent; shared inputs and campaign selection "
          "may violate that assumption. Complete-case selection can also omit costly interrupted runs. "
          "The totals cover the archived primary turn, not all earlier campaigns or separately logged subagents, and thus do not measure the full cost of obtaining the final vectors. "
          "Missing or ambiguous terminal records remain null. Runtime-verified and runtime-plus-reasoning-verified subsets are retained as sensitivity summaries. "
          "Execution failures and token distributions are retained for all observable runs, but correct-only summaries cannot be computed without item scores. "
          "No per-call accounting permits attribution to retries, discovery, analysis or orchestration: 100% of these totals remains stage-unattributed. "
          "Dollar costs, review time, reconstruction errors and reviewer agreement were not measured. Structured histories and command traces support inspection; "
          "they do not demonstrate faster review or that provenance benefits outweigh token cost.")
    dist_rows=[[LABEL[d['model']],d['condition'],f"{d['input_tokens']['n']}/{d['listed_runs']}",
                fmt(d['input_tokens']['median'],1),f"{fmt(d['input_tokens']['q1'])}-{fmt(d['input_tokens']['q3'])}",
                fmt(d['output_tokens']['median'],1)] for d in a['token_distributions']]
    distribution_table=table('Supplementary Table S1. Absolute provider-token distributions',
                            ['Configuration','Environment','Usage coverage','Median input','Input IQR','Median output'],dist_rows,
                            'All observable final selected runs, including those with operational errors. Medians retain one decimal place and linearly interpolated quartiles retain two, preserving fractional summary values from integer token counts. Input IQR reports Q1-Q3. Missing usage is excluded explicitly, never zero. The unpaired Astra population is separate. Correct-only and full multi-campaign costs are unavailable.')
    capped_descriptions=[]
    for h in ex['capped_histories']:
        counts=h['state_id_counts']
        capped_descriptions.append(
            f"For `{h['task']}`, the [{h['count']}-element snapshot]({h['path']}) lists "
            f"{counts['ok']} `ok` and {counts['error']} `error` elements in `state_ids`, "
            f"leaving {h['elements_without_state_id']} elements unaccounted for by those state-ID lists.")
    capped_errors=sum(h['state_id_counts']['error'] for h in ex['capped_histories'])
    capped_unaccounted=sum(h['elements_without_state_id'] for h in ex['capped_histories'])
    capped_detail_errors=sum(h['states']['error'] for h in ex['capped_histories'])
    capped_note=(' '.join(capped_descriptions) +
                 f" Together these metadata-only histories record {capped_errors} error-state elements and {capped_unaccounted} elements without a listed state ID. "
                 f"The snapshots' `state_details` fields report {capped_detail_errors} errors in total, contradicting their `state_ids`; both representations and their discrepancy are retained in the audit. "
                 "These are dataset-state observations, not deduplicated creating-job counts or answer outcomes, and are not added to Table 6 job totals. "
                 "Detailed contents remain excluded under the collection limit. Capping does not establish experiment failure, but it does not erase the recorded error states.\n\n")
    methods=("## Methods, provenance and limitations\n\n"
             "The workbook defines the observed inventory, not an independent expected-run protocol. Matching uses task and supplied configuration; "
             "condition-specific prompt additions, runtime reasoning settings and campaign roots remain visible confounders. No individual replicate is paired by seed. "
             "Counts use all listed runs unless an explicit complete-case criterion is stated. Jobs are deduplicated by server/native job ID; data-fetch jobs are separate. "
             "Inputs are not assumed independent merely because they have distinct uploads or histories. Run-level input manifests and dataset IDs support inspection, "
             "but complete input-version equivalence and ownership within the original run time window have not been established. "
             "No recovered agent code was executed, no hidden reference was opened, no new benchmark was run, and no submitted answer was regraded.\n\n"
             "Prior task reports and evidence are retained exactly under `analysis/<task>/versions/pre_compbio_synthesis/`. "
             "The existing schema and full source hash/reference checks validate the updated packages. The aggregate JSON references all 100 evidence hashes, "
             "included run IDs, finding IDs, source files and software hashes. Initial trace/history collection did not verify TLS certificates; "
             "the supplemental metadata fetch verified the certificate chain and hostname with strict CA-extension checking disabled for the host proxy. "
             "Neither byte hashes nor successful schema validation resolve score-source disagreements.\n\n"
             f"{capped_note}"
             "Exact per-task official evaluator outputs, versioned scoring definitions and submission receipts matching advertised vector hashes are needed for "
             "BixBench-equivalent accuracy, reliability and outcome-versus-route tables. Missing primary traces/usage, independent campaign-selection records, "
             "and event-level location/recovery adjudication are needed to quantify complete computational cost and exclusively Galaxy-derived solutions. "
             "A blinded review study is required for readability claims. These missing results are explicitly unavailable rather than replaced by plausible answers.\n")
    claims=table('Claim-to-evidence map',['Finding ID','Supported claim','Evidence'],[
        ['compbio_inventory','100 tasks; 2,500 supplied rows; 2,400 paired records','compBio_overview_audit.json: inventory, task_manifest'],
        ['compbio_accuracy','Aggregate score claims retained; no item-level accuracy','score_vectors, score_conflicts; downloaded metadata manifests'],
        ['compbio_execution','Observed deduplicated job states and recovery candidates','execution.job_refs; each task finding_execution'],
        ['compbio_variability','Instrument-specific fingerprint agreement','solution_path_consistency_results.json: cells and drivers'],
        ['compbio_cost','Complete-case ratios of primary-turn provider input totals','token_pairs, token_excluded, tokens; run_summaries.usage source lines']],
        'Every task evidence path and SHA-256 is enumerated in task_manifest. Run IDs are scoped by task; job references include server. Aggregate calculations never place multiple tasks into a singular task evidence record.')
    abstract=(f"We audited 2,500 CompBioBench records spanning 100 tasks, including 2,400 records across four paired model configurations and 100 unpaired GPT-6 Astra records. "
              f"The archive supplied no item-level evaluator scores; {n_off} aggregate scores were labelled official and {n_pred} predicted. "
              f"Galaxy snapshots exposed {ex['nonfetch_jobs']:,} distinct non-fetch creating jobs, including {errors:,} failures. "
              f"Input-token totals were recovered for {usage} records; the median Galaxy/open-ended-code ratio was {fmt(tok['pooled']['median'])} across "
              f"{tok['pooled']['n']} complete task-by-configuration comparisons. These retrospectively selected records support execution and provenance comparisons, "
              "while missing item outcomes and incomplete campaign accounting limit accuracy, recovery and total-cost conclusions.")
    sources=("Reproduce with `python3 scripts/audit_compbio_overview.py --validate` from the repository root. "
             "[Numerical audit](compBio_overview_audit.json), [path analysis](solution_path_consistency_analysis.py), "
             "[path results](solution_path_consistency_results.json), [source recovery](compBio_recovery_summary.md), "
             "[source manifest](source_snapshots/aggregate_metadata/manifest.json), and [task packages](analysis/) retain the evidence.\n")
    sections=[('Accuracy and output agreement by execution condition',accuracy,[1,2,3]),
              ('Analysis execution, failures and recovery',execution,[4,5,6,7]),
              ('Solution-path variability across tasks and configurations',variability,[8,9,10]),
              ('Token cost, provenance and human readability',cost,[11])]
    full=['# RESULTS','',intro,'']
    for heading,body,nums in sections:
        full += ['## '+heading,'',body,'']+[tables[n] for n in nums]
    full += [methods,claims,'## Abstract-ready paragraph','',abstract,'',sources]
    full.insert(-7,distribution_table)
    (BASE/'result_section_compbio.md').write_text('\n'.join(full))
    overview=['# RESULTS','',intro,'']
    for (heading,body,_),n in zip(sections,[1,6,9,11]):
        overview += ['## '+heading,'',body,'',tables[n]]
    overview += [methods,claims,'## Abstract-ready paragraph','',abstract,'',sources]
    (BASE/'compBio_overview.md').write_text('\n'.join(overview))
    recovery=['# CompBio evidence recovery','',
              f'Recovered task prompts from nested task metadata and {usage} primary-turn usage records from retained traces. Prior evidence/reports remain under each task\'s `versions/pre_compbio_synthesis/`.',
              '',f'Additional read-only retrieval retained 21 prediction vectors and provenance tables, five collection indexes, the dated campaign registry and the Astra submission/vector. {bad_hash} advertised vector hashes disagree with downloaded bytes; {absent} Luna Galaxy vectors are absent from the replicate archive. All available parsed vector answers match the archived task answers.',
              '',table('Score-source conflicts',['Campaign','replicates.tsv','Dated site metadata'],[[s['campaign'],f"{s['older_score']} ({s['older_type']})",f"{s['site_score']} ({s['site_type']})"] for s in a['score_conflicts']]),
              table('Unresolved vector hashes',['Campaign / model','Downloaded vector','Hash status'],[[s.get('campaign_id',s['model']),s.get('vector_path') or 'Absent','match' if s['hash_matches'] else 'mismatch' if s['hash_matches'] is False else 'unavailable'] for s in score]),
              '', 'No item-level correctness was recovered. Format-validation logs are not evaluator scores. The older README claims only 21 completed replicates and omits Luna Galaxy; newer indexes and workbook enumerate 24 paired-condition replicates plus Astra. Both descriptions are preserved; the workbook/index inventory governs this audit.',
              '',sources]
    (BASE/'compBio_recovery_summary.md').write_text('\n'.join(recovery))
    (BASE/'compBio_recovery_summary.json').write_text(json.dumps({k:a[k] for k in ('score_vectors','score_conflicts','coverage','source_manifest')},indent=2)+'\n')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--validate',action='store_true')
    args=parser.parse_args()
    a=build(args.validate)
    write_reports(a)
    (BASE/'compBio_overview_audit.json').write_text(json.dumps(a,indent=2)+'\n')
    for name in ('compBio_overview.md','result_section_compbio.md','compBio_recovery_summary.md'):
        for target in re.findall(r'\]\(([^)]+)\)',(BASE/name).read_text()):
            assert target.startswith(('http://','https://','#')) or (BASE/target).exists(), (name,target)
    print(json.dumps({"inventory":a['inventory'],"tokens":a['tokens'],"validation":a['validation']},indent=2))


if __name__=='__main__':
    main()
