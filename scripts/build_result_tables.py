"""Retrospective tables from archived evidence; no execution, retrieval or regrading.

Requires NumPy. Run from any directory. Outputs Result_table.md and a separate
cross-benchmark audit package. Existing task evidence is read-only.
"""
from collections import Counter, defaultdict
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import platform
import re
import statistics as st
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "BixBench50_CompBio_analysis"
SEED, RESAMPLES = 20260922, 20000
CONDITIONS = ("galaxy", "open_ended_code")
COMMON = ("codex_gpt_5_5", "codex_gpt_5_6_sol", "codex_gpt_5_6_luna")
DEEP_B = "deepseek_v4_pro_via_codex"
DEEP_C = "codex_deepseek_v4_pro_0813"
OLD = "deepseek_v4_pro_via_claude_code_superseded"
ASTRA = "codex_gpt_6_astra"
MODELS = {"BixBench50": (*COMMON, DEEP_B, OLD), "CompBio": (*COMMON, DEEP_C)}
FOLDERS = {"BixBench50": "BixBench_50", "CompBio": "CompBio"}
LABELS = dict(zip(COMMON, ("GPT-5.5", "GPT-5.6 Sol", "GPT-5.6 Luna")))
LABELS.update({DEEP_B: "DeepSeek V4 Pro (Codex)", DEEP_C: "DeepSeek V4 Pro 0813 (Codex)",
               OLD: "DeepSeek V4 Pro (Claude Code, superseded)", ASTRA: "GPT-6 Astra (unpaired)"})
ENV = {"galaxy": "Galaxy", "open_ended_code": "Open-ended code"}
spec = importlib.util.spec_from_file_location("bix_paths", ROOT / "BixBench_50/solution_path_consistency_analysis.py")
paths = importlib.util.module_from_spec(spec)
spec.loader.exec_module(paths)
deep_spec = importlib.util.spec_from_file_location("result_table_deep_analysis", ROOT / "scripts/result_table_deep_analysis.py")
deep = importlib.util.module_from_spec(deep_spec)
deep_spec.loader.exec_module(deep)


def reader_labels(text):
    """Expand display labels only; preserve identifiers and Claude Code's name."""
    text = re.sub(r'\bG\b', 'Galaxy', text)
    text = re.sub(r'(?<!Claude )\bCode\b', 'open-ended code', text)
    text = re.sub(r'\bCI\b', 'confidence interval', text)
    text = re.sub(r'\bpp\b', 'percentage points', text)
    return re.sub(r'\bNA\b', 'Unavailable', text)


def read(path):
    return json.loads((ROOT / path).read_text())


def sha(path):
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def summary(values):
    values = list(values)
    if not values:
        return {"n": 0, "median": None, "mean": None, "q1": None, "q3": None}
    return dict(n=len(values), median=float(np.median(values)), mean=float(np.mean(values)),
                q1=float(np.quantile(values, .25)), q3=float(np.quantile(values, .75)),
                min=float(min(values)), max=float(max(values)))


def bootstrap(rows, value, key, statistic="mean"):
    """Resample entire clusters; retained rows, including models, stay together."""
    groups = defaultdict(list)
    for r in rows:
        if r[value] is not None:
            groups[r["cluster"]].append(r[value])
    groups = [groups[k] for k in sorted(groups)]
    assert len(groups) > 1, (key, len(groups))
    a = np.full((len(groups), max(map(len, groups))), np.nan)
    for i, g in enumerate(groups):
        a[i, :len(g)] = g
    rng = np.random.default_rng([SEED, int(hashlib.sha256(key.encode()).hexdigest()[:8], 16)])
    fn = np.nanmean if statistic == "mean" else np.nanmedian
    draws = []
    for start in range(0, RESAMPLES, 250):
        selected = rng.integers(len(groups), size=(min(250, RESAMPLES-start), len(groups)))
        draws.extend(fn(a[selected].reshape(len(selected), -1), axis=1))
    draws = np.array(draws)
    assert np.isfinite(draws).all()
    return {"estimate": float(fn(a)), "ci95": np.quantile(draws, [.025, .975]).tolist(),
            "clusters": len(groups), "n": sum(map(len, groups))}, draws


def fmt(value, digits=2):
    return "NA" if value is None else f"{value:,.{digits}f}"


def ci(result, digits=2):
    return f"{fmt(result['estimate'], digits)} [{fmt(result['ci95'][0], digits)}, {fmt(result['ci95'][1], digits)}]"


def frac(n, d):
    return f"{int(n):,}/{int(d):,} ({100*n/d:.1f}%)" if d else "NA"


def iqr(s, digits=2):
    return f"{fmt(s['median'], digits)} ({fmt(s['q1'], digits)}-{fmt(s['q3'], digits)})"


def task_link(benchmark, task):
    return f"[{task}]({FOLDERS[benchmark]}/analysis/{task}/history_analysis.md)"


def load_data(b, c):
    capsule = {t["task"]: t["capsule"] for t in b["tasks"]}
    expected_hashes = {("BixBench50", t["task"]): t["evidence_sha256"] for t in b["source_hashes"]}
    expected_hashes.update({("CompBio", t["task"]): t["evidence_sha256"] for t in c["task_manifest"]})
    manifests, runs, cells, jobs = [], [], [], {}
    for benchmark, folder in FOLDERS.items():
        for path in sorted((ROOT / folder / "analysis").glob("*/history_analysis_evidence.json")):
            rel = str(path.relative_to(ROOT))
            d = read(rel)
            task = d["task"]["task_id"]
            assert sha(rel) == expected_hashes[benchmark, task], rel
            cluster = capsule[task] if benchmark == "BixBench50" else task
            manifests.append({"benchmark": benchmark, "task": task, "path": rel, "sha256": sha(rel),
                              "included_run_ids": [r["run_id"] for r in d["runs"]],
                              "finding_ids": [f["finding_id"] for f in d["manuscript_findings"]]})
            grouped = defaultdict(list)
            for r in d["runs"]:
                cond = r["condition"]
                model = r["run_id"].removeprefix(cond + "_").rsplit("_r", 1)[0]
                fingerprint = set()
                run_jobs = {}
                for e in r["events"]:
                    if e["execution_location"] == "galaxy_job":
                        tool = paths.galaxy_tool(e.get("tool"))
                        if tool:
                            fingerprint.add(tool)
                        if e["event_type"] == "analysis" and e.get("tool") != "__DATA_FETCH__":
                            job_key = (benchmark, r["environment"].get("galaxy_server"), e["native_job_id"])
                            ref = {"task": task, "run_id": r["run_id"], "event_id": e["event_id"], "evidence": rel}
                            if job_key in jobs:
                                assert (jobs[job_key]["tool"], jobs[job_key]["status"]) == (e["tool"], e["status"])
                                jobs[job_key]["refs"].append(ref)
                            else:
                                jobs[job_key] = {"benchmark": benchmark, "server": job_key[1], "native_job_id": job_key[2],
                                    "tool": e["tool"], "status": e["status"], "exit_code": e.get("exit_code"),
                                    "stderr": e.get("stderr_excerpt") or "", "stdout": e.get("stdout_excerpt") or "", "refs": [ref]}
                            run_jobs[job_key] = e
                    elif cond == "open_ended_code" and e.get("command"):
                        fingerprint.update("bio." if t.lower().rstrip(".") == "bio" else t.lower().rstrip(".")
                                           for t in paths.VOCAB.findall(e["command"]))
                ec = r["evidence_completeness"]
                observed = ec["public_history_contents"] == "retrieved" if cond == "galaxy" else ec["agent_transcript"] == "retrieved"
                errors = sum(e["status"] in ("error", "failed") for e in run_jobs.values())
                rr = {"benchmark": benchmark, "task": task, "cluster": cluster, "model": model, "condition": cond,
                      "run_id": r["run_id"], "replicate": r["replicate_id"], "evidence": rel,
                      "domain": d["task"].get("domain"), "model_metadata": r["model"],
                      "score": r["outcome"]["original_evaluator_score"], "answer": r["outcome"]["submitted_answer"],
                      "answer_sha256": r["outcome"].get("submitted_answer_sha256"),
                      "verifier": r["outcome"].get("original_evaluator_mode"),
                      "input_tokens": r["usage"].get("provider_reported_input_tokens"),
                      "output_tokens": r["usage"].get("provider_reported_output_tokens"),
                      "coverage": ec, "fingerprint": sorted(fingerprint), "path_observed": observed,
                      "jobs": len(run_jobs) if cond == "galaxy" and observed else None,
                      "errors": errors if cond == "galaxy" and observed else None,
                      "has_error": int(errors > 0) if cond == "galaxy" and observed else None,
                      "nonzero_shell": r["derived_metrics"].get("nonzero_exit_shell_calls") if ec["agent_transcript"] == "retrieved" else None,
                      "recovery_candidates": len(r["recovery_episodes"])}
                assert rr['score'] in (0, 1) if benchmark == 'BixBench50' else rr['score'] is None
                deep.enrich_run(d, r, rr)
                runs.append(rr)
                grouped[model, cond].append(rr)
            for (model, cond), rs in sorted(grouped.items()):
                complete = len(rs) == 3 and {r["replicate"] for r in rs} == {1, 2, 3}
                eligible = complete and all(r["path_observed"] and r["fingerprint"] for r in rs)
                fps = [set(r["fingerprint"]) for r in rs]
                scores = [r["score"] for r in rs]
                answers = [r["answer"] for r in rs]
                cells.append({"benchmark": benchmark, "task": task, "cluster": cluster, "condition": cond, "model": model,
                              "run_ids": [r["run_id"] for r in rs], "eligible": eligible,
                              "agreement": paths.agreement(fps) if eligible else "not_evaluable",
                              "jaccard": st.mean(paths.jaccard(x, y) for x, y in itertools.combinations(fps, 2)) if eligible else None,
                              "accepted": int(sum(scores)) if complete and all(s is not None for s in scores) else None,
                              "answer_distinct": len(set(answers)) if complete and all(a is not None for a in answers) else None,
                              "any_error": any(r["has_error"] for r in rs) if all(r["has_error"] is not None for r in rs) else None})
    assert len(manifests) == 150 and len(runs) == 4000
    assert len({(r['benchmark'], r['task'], r['run_id']) for r in runs}) == 4000
    return manifests, runs, cells, list(jobs.values())


def compute(b, c, runs, cells, jobs):
    results = {"accuracy": {}, "tokens": {}, "path_summaries": [], "cross_tokens": [], "cross_paths": [], "failure_rates": []}
    br = [r for r in runs if r["benchmark"] == "BixBench50"]
    bc = [x for x in cells if x["benchmark"] == "BixBench50"]
    for label, models in [(m, (m,)) for m in MODELS['BixBench50']] + [("all", MODELS['BixBench50']), ("codex_four", (*COMMON, DEEP_B)), ("shared_three", COMMON)]:
        sub = [x for x in bc if x['model'] in models]
        paired = defaultdict(dict)
        for x in sub:
            paired[x['task'], x['model']][x['condition']] = x
        differences = [{"cluster": pair['galaxy']['cluster'], "delta": 100*(pair['galaxy']['accepted']-pair['open_ended_code']['accepted'])/3}
                       for pair in paired.values()]
        result, _ = bootstrap(differences, 'delta', 'accuracy_'+label)
        result['conditions'] = {cond: {"accepted": int(sum(r['score'] for r in br if r['condition']==cond and r['model'] in models)),
                                      "n": sum(r['condition']==cond and r['model'] in models for r in br)} for cond in CONDITIONS}
        results['accuracy'][label] = result
    pair_records = []
    grouped = defaultdict(list)
    for r in runs:
        if r['model'] in MODELS[r['benchmark']]:
            grouped[r['benchmark'], r['task'], r['model']].append(r)
    for (benchmark, task, model), rs in sorted(grouped.items()):
        assert len(rs) == 6
        if any(r['input_tokens'] is None for r in rs):
            continue
        medians = {cond: st.median(r['input_tokens'] for r in rs if r['condition']==cond) for cond in CONDITIONS}
        assert medians['open_ended_code'] > 0
        pair_records.append({"benchmark": benchmark, "task": task, "model": model, "cluster": rs[0]['cluster'],
                             "ratio": medians['galaxy']/medians['open_ended_code'], "medians": medians,
                             "run_ids": [r['run_id'] for r in rs]})
    assert Counter(p['benchmark'] for p in pair_records) == {'BixBench50': 250, 'CompBio': 386}
    token_draws = {}
    for benchmark in FOLDERS:
        for label, models in [(m, (m,)) for m in MODELS[benchmark]] + [('all', MODELS[benchmark]), ('shared_three', COMMON)]:
            sub = [p for p in pair_records if p['benchmark']==benchmark and p['model'] in models]
            estimate, token_draws[benchmark, label] = bootstrap(sub, 'ratio', benchmark+'_tokens_'+label, 'median')
            results['tokens'][benchmark+'_'+label] = {**summary(p['ratio'] for p in sub), **estimate,
                "greater_than_one": sum(p['ratio']>1 for p in sub)}
        for cond in CONDITIONS:
            for label, models in [(m, (m,)) for m in MODELS[benchmark]] + [('all', MODELS[benchmark]), ('shared_three', COMMON)]:
                sub = [x for x in cells if x['benchmark']==benchmark and x['condition']==cond and x['model'] in models]
                ev = [x for x in sub if x['eligible']]
                results['path_summaries'].append({"benchmark": benchmark, "condition": cond, "model": label,
                    "total": len(sub), "evaluable": len(ev), "counts": dict(Counter(x['agreement'] for x in sub)),
                    "mean_jaccard": st.mean(x['jaccard'] for x in ev)})
    for label, models in [(m, (m,)) for m in COMMON] + [('shared_three', COMMON)]:
        estimates, draws = {}, {}
        for benchmark in FOLDERS:
            estimates[benchmark] = results['tokens'][benchmark+'_'+label]
            draws[benchmark] = token_draws[benchmark, label]
        effect = draws['CompBio']/draws['BixBench50']
        results['cross_tokens'].append({"model": label, **estimates,
            "ratio_of_medians": estimates['CompBio']['estimate']/estimates['BixBench50']['estimate'],
            "ci95": np.quantile(effect,[.025,.975]).tolist()})
    for cond in CONDITIONS:
        estimates, draws = {}, {}
        for benchmark in FOLDERS:
            sub = [x for x in cells if x['benchmark']==benchmark and x['condition']==cond and x['model'] in COMMON and x['eligible']]
            estimates[benchmark], draws[benchmark] = bootstrap(sub,'jaccard','cross_paths_'+benchmark+'_'+cond)
        results['cross_paths'].append({"condition": cond, **estimates,
            "difference": estimates['CompBio']['estimate']-estimates['BixBench50']['estimate'],
            "ci95": np.quantile(draws['CompBio']-draws['BixBench50'],[.025,.975]).tolist()})
    for benchmark in FOLDERS:
        sub = [r for r in runs if r['benchmark']==benchmark and r['condition']=='galaxy' and r['model'] in COMMON and r['has_error'] is not None]
        result, _ = bootstrap(sub,'has_error','error_rate_'+benchmark)
        results['failure_rates'].append({"benchmark": benchmark, **result, "with_error": sum(r['has_error'] for r in sub)})
    # Error-message indicators are overlapping, descriptive and not adjudicated causes.
    patterns = {
        'Dependency / executable': r'command not found|modulenotfounderror|importerror|no module named|cannot open shared object|error while loading shared libraries',
        'Type / numeric / attribute': r'typeerror|attributeerror|invalid numeric|could not convert|cannot convert|unsupported operand|ufunc',
        'File / path / access': r'filenotfounderror|no such file or directory|permission denied|could not open|cannot open file',
        'Argument / syntax / encoding': r'syntaxerror|unrecognized arguments|invalid option|invalid argument|invalid base64|incorrect padding',
        'Network / retrieval': r'httperror|urlerror|connectionerror|connection refused|connection reset|name resolution|unable to resolve host|http error|curl:|wget:',
        'Memory / resource': r'memoryerror|out of memory|oom.kill|cannot allocate memory|disk quota|no space left',
    }
    for job in jobs:
        text = job['stderr']+'\n'+job['stdout']
        job['has_error_text'] = bool(text.strip())
        job['error_indicators'] = [name for name, pattern in patterns.items() if re.search(pattern,text,re.I)] if job['status']=='error' else []
        family = job['tool'].split('/')[-2] if 'toolshed' in job['tool'] else job['tool']
        job['specific_error_signatures'] = [label for benchmark, tool, label, pattern, _ in deep.ERROR_RULES
            if job['benchmark']==benchmark and family==tool and job['status']=='error' and re.search(pattern,text,re.I|re.S)]
        # Source event references retain the full evidence; do not duplicate logs.
        del job['stderr'], job['stdout']
    results['error_codebook'] = patterns
    results['error_indicators'] = {benchmark: {name: sum(j['status']=='error' and name in j['error_indicators'] for j in jobs if j['benchmark']==benchmark)
                                                for name in patterns} for benchmark in FOLDERS}
    results['token_pairs'] = pair_records
    return results


def report(b, c, runs, cells, jobs, results):
    doc, tables = [], {}

    def put(text):
        doc.append(reader_labels(text).strip()+'\n')

    def table(label, title, headers, rows, legend):
        title, legend = reader_labels(title), reader_labels(legend)
        headers = [reader_labels(h) for h in headers]
        rows = [[reader_labels(str(v)) for v in row] for row in rows]
        assert all(len(row)==len(headers) for row in rows), label
        tables[label] = {"title": title, "headers": headers, "rows": rows, "legend": legend}
        def clean(v):
            return str(v).replace('|', '&#124;').replace('\n', ' ')
        put(f"### Table {label}. {title}\n\n"+'| '+' | '.join(headers)+' |\n'+
            '| '+' | '.join(['---']*len(headers))+' |\n'+
            '\n'.join('| '+' | '.join(map(clean,row))+' |' for row in rows)+'\n\n'+legend)

    def subset(benchmark, condition=None, model=None):
        return [r for r in runs if r['benchmark']==benchmark and (condition is None or r['condition']==condition)
                and (r['model'] in MODELS[benchmark] if model is None else r['model']==model)]

    def path_rows(benchmark):
        return [[ENV[s['condition']], LABELS.get(s['model'],'All configurations'), f"{s['evaluable']}/{s['total']}",
                 s['counts'].get('identical',0),s['counts'].get('two_of_three',0),s['counts'].get('all_distinct',0),
                 fmt(s['mean_jaccard'],3)] for s in results['path_summaries'] if s['benchmark']==benchmark and s['model']!='shared_three']

    def execution_rows(benchmark):
        rr = subset(benchmark,'galaxy'); jj = [j for j in jobs if j['benchmark']==benchmark]
        ev = [r for r in rr if r['errors'] is not None]
        states = Counter(j['status'] for j in jj)
        return [['Detailed Galaxy histories, run-linked',frac(len(ev),len(rr))],
                ['Metadata-only / unavailable run-linked histories',f"{sum(r['coverage']['public_history_contents']=='history_metadata_only' for r in rr)} / {sum(r['coverage']['public_history_contents']=='unavailable' for r in rr)}"],
                ['Distinct non-fetch creating jobs',f"{len(jj):,}"],
                ['Job states: ok / error / deleted / paused',' / '.join(f"{states[k]:,}" for k in ['ok','error','deleted','paused'])],
                ['Error jobs / non-fetch jobs',frac(states['error'],len(jj))],
                ['Runs with >=1 error job / detailed runs',frac(sum(r['has_error'] for r in ev),len(ev))],
                ['Error jobs/run: median (Q1-Q3); range',iqr(summary(r['errors'] for r in ev),1)+f"; 0-{max(r['errors'] for r in ev)}"],
                ['Candidate recovery episodes / runs containing one',f"{sum(r['recovery_candidates'] for r in rr)} / {sum(r['recovery_candidates']>0 for r in rr)}"],
                ['Adjudicated recovery rate; failures before correct answer','NA; NA'],
                ['Certified Galaxy-only completion','NA']]

    def token_rows(benchmark):
        rows=[]
        for model in (*MODELS[benchmark],'all'):
            t=results['tokens'][benchmark+'_'+model]
            g=subset(benchmark,'galaxy',None if model=='all' else model)
            o=subset(benchmark,'open_ended_code',None if model=='all' else model)
            g=[r['input_tokens'] for r in g if r['input_tokens'] is not None]
            o=[r['input_tokens'] for r in o if r['input_tokens'] is not None]
            rows.append([LABELS.get(model,'All configurations'),t['n'],iqr(t),ci(t),
                         f"{fmt(st.median(g),1)} / {fmt(st.median(o),1)}",frac(t['greater_than_one'],t['n'])])
        return rows

    def tool_rows(benchmark):
        jj=[j for j in jobs if j['benchmark']==benchmark]
        counts=Counter(j['tool'] for j in jj)
        errors=Counter(j['tool'] for j in jj if j['status']=='error')
        top=sorted(counts,key=lambda t:(-counts[t],t))[:6]
        return [[tool.split('/')[-2]+'/'+tool.split('/')[-1] if 'toolshed' in tool else tool,
                 counts[tool],errors[tool]] for tool in top]

    uncertainty = ("Unless a table specifies otherwise, new intervals are exploratory 95% percentile cluster-bootstrap intervals (20,000 resamples; seed 20260922, "
        "with deterministic statistic-specific streams). BixBench resamples eligible source capsules (up to 33); CompBio resamples eligible tasks (up to 100), "
        "retaining configurations and replicate bundles. Estimates weight eligible task/configuration cells equally; capsule sizes remain unequal. "
        "Cross-benchmark draws are independent and stratified by benchmark. Intervals assume independent clusters, an assumption not established "
        "for shared biological inputs. They are pointwise, not multiplicity-adjusted simultaneous intervals. No confirmatory significance, equivalence, "
        "non-inferiority or causal claim is made; an interval spanning zero (differences) or one (ratios) is inconclusive.")
    path_legend = ("One cell = task x configuration x environment with three replicate labels. This report harmonizes BOTH benchmarks: "
        "all three fingerprints must be observed and nonempty. Identical / two identical / all distinct partition evaluable cells. "
        "Jaccard = intersection/union, averaged over the three replicate pairs and then over eligible cells. "
        "Galaxy uses version-stripped job tool IDs (excluding data fetch, retaining legacy upload); code uses the archived closed command vocabulary. "
        "These instruments cannot rank scientific consistency across environments; order, most parameters and biological validity are unmeasured. "
        "BixBench counts differ from its legacy report because that report also admitted partly missing/empty fingerprints.")
    token_legend = ("Ratio = median input tokens of three Galaxy runs / median of three code runs for the same task and configuration; "
        "all six totals must be available. Q1-Q3 are quartile endpoints. Absolute medians use every available run in that row and are "
        "not the numerator/denominator of the paired median ratio. Cached input is already included. Output/reasoning are not added. "
        "Usage covers archived primary turns, not full campaign, compute or monetary cost. Failed runs are retained; missing usage is never zero.")
    put("# Benchmark Results Tables\n\nRetrospective synthesis of the archived BixBench-50 and CompBioBench analyses. "
        "`BixBench50` below maps to the repository's `BixBench_50/` directory. "
        "The central questions are whether accepted answers are reliable, what execution records reveal about errors, "
        "and which measurable changes could improve Galaxy for agents and users.\n\n"
        "**Readout:** Galaxy means the Galaxy application programming interface condition; open-ended code means the agent's own runtime. "
        "Intervals are 95% confidence intervals unless specified. Q1 and Q3 are the first and third quartiles. Unavailable never means zero. "
        "All GPT-5 configurations use the supplied Codex labels. Replicate numbers are not matched seeds. "
        "CompBio vectors are final campaign selections, including continuations/recoveries; they do not measure first-attempt performance.\n\n"
        "[Reproduce and inspect](BixBench50_CompBio_analysis/README.md) | "
        "[Calculations and table values](BixBench50_CompBio_analysis/analysis.json) | "
        "[Task/run/finding source manifest](BixBench50_CompBio_analysis/source_manifest.json).")
    put("**Question guide:** exclusive task success and its cause (B11-B13); model capacity, reliability and cost (B14-B15, C9); "
        "common software and environmental friction (X9-X10); recurring diagnostics and task specification/workload (X5-X6, X11, X18); "
        "user-defined tool necessity versus choice (X12-X15); different routes to the same answer and evidence for the motivating observations (X16-X17). "
        "Tables report observations unless explicitly labelled as inference or a proposed intervention.")
    put("## 1) Bixbench50 analysis\n\n**Finding:** high observed acceptance is compatible with Galaxy execution, "
        "but the environment difference is uncertain and sensitive to the superseded harness. "
        "The archive contains 50 questions in 33 capsules, five configurations, two environments and three replicates (1,500 scored runs).")
    rows=[]
    for model in (*MODELS['BixBench50'],'all','codex_four'):
        a=results['accuracy'][model]; g=a['conditions']['galaxy'];o=a['conditions']['open_ended_code']
        rows.append([LABELS.get(model,{'all':'All five','codex_four':'Four Codex configurations'}[model] if model not in LABELS else model),
                     frac(g['accepted'],g['n']),frac(o['accepted'],o['n']),ci(a)])
    table('B1','Original-evaluator acceptance and paired environment difference',
          ['Configuration','Galaxy accepted','Code accepted','G - Code, pp [95% CI]'], rows,
          "Original binary evaluator scores are retained, including six scored missing answers (five G, one Code). "
          "No regrading was performed. The superseded Claude Code configuration contributes 16 of the 24 extra accepted G runs; "
          "excluding it leaves eight. The original 100,000-resample audit interval was -1.41 to +7.91 pp; the fresh calculation above uses the common settings below.\n\n"+uncertainty)
    rows=[]
    for model in MODELS['BixBench50']:
        for cond in CONDITIONS:
            xs=[x for x in cells if x['benchmark']=='BixBench50' and x['model']==model and x['condition']==cond]
            counts=Counter(x['accepted'] for x in xs)
            rows.append([LABELS[model],ENV[cond],counts[3],counts[1]+counts[2],counts[0],frac(50-counts[0],50)])
    table('B2','Repeatability of accepted answers', ['Configuration','Environment','3/3 accepted','1-2/3 accepted','0/3 accepted','At least one accepted'],rows,
          "Each row contains 50 task cells; the middle three categories are mutually exclusive. At least one is an overlapping endpoint, "
          "not single-run accuracy. These are replicate-labelled archived runs, not best-of-three adaptive attempts.")
    rows=[]
    for task,question in [('bix-30-q3','Multiple-testing miRNA ratio'),('bix-43-q2','gseapy enrichment odds ratio'),('bix-45-q1','RCV Mann-Whitney p-value'),('bix-53-q2','Differential expression after replicate exclusion'),('bix-61-q5','Transition/transversion ratio')]:
        t=next(t for t in b['tasks'] if t['task']==task)
        rows.append([task_link('BixBench50',task),question,f"{t['accuracy']['galaxy']['accepted']}/15",f"{t['accuracy']['open_ended_code']['accepted']}/15",f"{t['error_jobs']}/{t['jobs']}"])
    table('B3','Largest acceptance discordances and tasks rejected throughout',
          ['Task','Question','G accepted','Code accepted','G error/non-fetch jobs'],rows,
          "Selection rule: absolute acceptance difference >=5/15 or zero acceptance in both environments; all five qualifying tasks are shown. "
          "Task-linked jobs are deduplicated within task. Operationally successful jobs do not establish a correct answer: "
          "RCV and transition/transversion results were rejected despite no recorded job errors. "
          "RCV means relative composition variability. "
          "The source reports implicate threshold choices, upstream gene sets and RCV input construction; those mechanisms are not independently adjudicated here.")
    table('B4','Galaxy execution, missing evidence and recovery candidates',['Measure','Observed'],execution_rows('BixBench50'),
          "Jobs are deduplicated by server/native job ID and exclude data-fetch jobs, but include preparation and legacy upload. "
          "Histories may contain inherited/later state. A candidate is later same-tool/input success, not verified recovery of a scientific objective. "
          "31/32 collection-limited runs had accepted answers. The original fresh-history check is false for all 750 G runs, "
          "despite retrieved history evidence; Galaxy-only completion remains unresolved.")
    table('B5','Observable triplicate path agreement under the harmonized rule',
          ['Environment','Configuration','Eligible/total','Identical','Two identical','All distinct','Mean Jaccard'],path_rows('BixBench50'),path_legend)
    rows=[]
    for cond in CONDITIONS:
        for score in [3,1,0]:
            xs=[x for x in cells if x['benchmark']=='BixBench50' and x['condition']==cond and x['eligible'] and
                (x['accepted'] in [1,2] if score==1 else x['accepted']==score)]
            rows.append([ENV[cond],{3:'All three',1:'One or two',0:'None'}[score],len(xs),len({x['task'] for x in xs}),
                         frac(sum(x['agreement']=='identical' for x in xs),len(xs)),fmt(st.mean(x['jaccard'] for x in xs),3)])
    table('B6','Does a consistent recorded path imply acceptance?',
          ['Environment','Accepted replicates','Eligible cells','Tasks','Identical fingerprints','Mean Jaccard'],rows,
          "Descriptive association conditional on observable nonempty paths. Cells share tasks; failure-prone task composition can drive the pattern. "
          "Agreement is neither correctness nor causal evidence that varied methods help. The retained rows allow inspection of both accepted and rejected consistent paths.")
    table('B7','Input-token burden by configuration',
          ['Configuration','Paired cells','Ratio median (Q1-Q3)','Ratio [95% CI]','Median input G / Code','Pairs with G > Code'],token_rows('BixBench50'),token_legend)
    modes=defaultdict(list)
    for r in subset('BixBench50'):
        modes[r['verifier']].append(r)
    rows=[[str(mode),frac(sum(r['score']==1 for r in rs),len(rs)),sum(r['condition']=='galaxy' for r in rs),sum(r['condition']=='open_ended_code' for r in rs)] for mode,rs in sorted(modes.items(),key=lambda x:str(x[0]))]
    table('B8','Evaluator-mode composition and acceptance',['Recorded verifier','Accepted/all','G runs','Code runs'],rows,
          "Modes are observational and task/configuration-dependent; these are not randomized verifier comparisons. "
          "The source audit reports byte-identical answers with different scores under different modes. Rounded-numeric scoring occurs "
          "only in the two DeepSeek configurations. These evaluator effects limit interpreting rejection as a demonstrated analytical mistake.")
    table('B9','Most frequently recorded Galaxy operations',['Recorded tool / version','Non-fetch jobs','Error jobs'],tool_rows('BixBench50'),
          "Top six tool IDs by job count (ties sorted by full ID), among 5,042 deduplicated non-fetch jobs. "
          "Spreadsheet conversion, column selection and filtering accompany KEGG over-representation and PhyKIT metrics. "
          "KEGG is the Kyoto Encyclopedia of Genes and Genomes. "
          "Counts include preparation and inherited/later history state; operation frequency is not success attribution. "
          "Full IDs and event references are in the analysis JSON.")
    rows=[]
    for cond in CONDITIONS:
        other=next(x for x in CONDITIONS if x!=cond)
        tasks=b['tasks']
        rows.append([ENV[cond],frac(sum(t['accuracy'][cond]['accepted']>0 for t in tasks),50),
                     frac(sum(t['accuracy'][cond]['accepted']==15 for t in tasks),50),
                     sum(t['accuracy'][cond]['accepted']>0 and t['accuracy'][other]['accepted']==0 for t in tasks),
                     b['model_task_comparisons']['galaxy_higher' if cond=='galaxy' else 'code_higher']])
    table('B10','Task coverage versus within-configuration advantage',
          ['Environment','Tasks with any accepted run','All 15 runs accepted','Tasks accepted only here','Task/configuration pairs with more accepted runs'],rows,
          "Task coverage pools five configurations and three replicates (15 runs/task/environment), whereas the last column compares "
          "three-replicate counts within each of 250 matched task/configuration pairs. There are 198 tied pairs, "
          "and two tasks with no accepted answer in either environment. These endpoints do not describe the reliability of a single run.")
    deep.render(SimpleNamespace(**globals()),'BixBench50',table,runs,cells,jobs,results)
    put("## 2) CompBio analysis\n\n**Finding:** the archive supports execution, answer-text consistency and token analyses, "
        "but does not support task-level accuracy or correct-answer recovery rates. It includes 2,400 records in four paired configurations "
        "over 100 tasks, plus 100 unpaired GPT-6 Astra records. All 2,500 item-level evaluator scores are unavailable.")
    rows=[]
    for model in (*MODELS['CompBio'],ASTRA):
        row=[LABELS[model]]
        for cond in CONDITIONS:
            vs=[v for v in c['score_vectors'] if v['model']==model and v['condition']==cond]
            parts=[]
            for v in sorted(vs,key=lambda v:v['replicate']):
                flag='O' if v['score_type']=='official_labelled' else 'P'
                flag += '; hash mismatch' if v['hash_matches'] is False else '; vector absent' if v['hash_matches'] is None else ''
                parts.append(f"{v['replicate']}: {v['score']}/100 ({flag})")
            row.append('; '.join(parts) if parts else 'Not represented')
        rows.append(row)
    table('C1','Source-reported answer-vector scores, with provenance status',['Configuration','Galaxy','Code'],rows,
          "O = archive-labelled official, not an independently verified leaderboard receipt; P = predicted. "
          "15 vectors are O and 10 P; 13 advertised hashes match retained bytes, nine mismatch and three vectors are absent. "
          "All parsed answers match for the 22 available vectors. Sol G r1/r3 were previously 92/100 P; dated metadata changes them "
          "to 93/100 O and 91/100 O. Neither version is silently discarded. No pooled accuracy, uncertainty interval, or "
          "task-level all/some/none-correct inference is computed from this mixture. "
          "Source: [aggregate audit](CompBio/compBio_overview_audit.json), `score_vectors` and `score_conflicts`.")
    rows=[]
    for model in MODELS['CompBio']:
        for cond in CONDITIONS:
            rs=subset('CompBio',cond,model);xs=[x for x in cells if x['benchmark']=='CompBio' and x['model']==model and x['condition']==cond]
            counts=Counter(x['answer_distinct'] for x in xs)
            rows.append([LABELS[model],ENV[cond],frac(sum(r['input_tokens'] is not None for r in rs),len(rs)),
                         counts[1],counts[2],counts[3]])
    table('C2','Usage completeness and repeated-answer consistency',
          ['Configuration','Environment','Usage coverage','1 distinct answer','2 distinct','3 distinct'],rows,
          "Usage denominators are 300 runs/row; answer counts partition 100 triplicate task cells/row. "
          "Answers use archived submitted text with outer whitespace removed, not raw-file hashes. "
          "Text identity does not establish semantic equivalence or correctness. Among all 12 answers/task/environment, "
          "62/100 G tasks and 58/100 Code tasks have one distinct answer; answer sets differ across environments in 43/100 tasks.")
    table('C3','Galaxy execution and recovery evidence',['Measure','Observed'],execution_rows('CompBio'),
          "The archive contains 22,067 distinct creating jobs: 5,381 data-fetch and 16,686 non-fetch (including 372 upload1 jobs). "
          "Non-fetch jobs are not independent scientific attempts. Nonzero shell exits occur in 676/1,188 available G transcripts "
          "and 882/1,200 Code transcripts; probes/searches can return nonzero, so these are not comparative scientific-failure rates. "
          "The two metadata-only histories contain 196 error-state datasets in state_ids but zero in state_details, plus 17 "
          "unaccounted elements. Those dataset states are not added to creating-job totals.")
    domains=defaultdict(list)
    for t in c['tasks']:
        domains[t['domain']].append(t)
    rows=[]
    for domain,ts in sorted(domains.items(),key=lambda x:(-len(x[1]),x[0])):
        ids={t['task'] for t in ts}; rr=[r for r in subset('CompBio','galaxy') if r['task'] in ids and r['errors'] is not None]
        ratios=[p['ratio'] for p in results['token_pairs'] if p['benchmark']=='CompBio' and p['task'] in ids]
        rows.append([domain,len(ts),f"{sum(len(t['answers']['galaxy'])==1 for t in ts)} / {sum(len(t['answers']['open_ended_code'])==1 for t in ts)}",
                     frac(sum(r['has_error'] for r in rr),len(rr)),iqr(summary(ratios)),len(ratios)])
    table('C4','Biological domain, answer convergence and operational burden',
          ['Recorded domain','Tasks','Single-answer tasks G / Code','G runs with error','Token ratio median (Q1-Q3)','Token pairs'],rows,
          "Domains come from task metadata; these are not difficulty strata. All four paired configurations are included. "
          "Single-answer counts use 12 submitted answers per task/environment. Error denominators include only detailed G runs. "
          "Ratios require all six usage records; small domains are descriptive case groups, not evidence of domain superiority.")
    table('C5','Observable triplicate path agreement',
          ['Environment','Configuration','Eligible/total','Identical','Two identical','All distinct','Mean Jaccard'],path_rows('CompBio'),path_legend)
    table('C6','Input-token burden by configuration',
          ['Configuration','Paired cells','Ratio median (Q1-Q3)','Ratio [95% CI]','Median input G / Code','Pairs with G > Code'],token_rows('CompBio'),
          token_legend+" Fourteen of 400 pairs are excluded (3 GPT-5.5, 10 Luna, 1 DeepSeek). "
          "The runtime-and-reasoning-verified sensitivity contains only 99 DeepSeek pairs (median 3.53), so it changes the configuration population. "
          "Astra usage is available in 100/100 unpaired Code runs (median input 314,244.5); no G ratio is possible.")
    table('C7','Adjudicated examples: correction versus changed objective',
          ['Task / run','Failure','Later operation','Supported conclusion'],[
          [task_link('CompBio','bedtools-chromhmm-q1')+'; DeepSeek G r2','round(c1/c5*100): string columns',
           'round(float(c1)/float(c5)*100); job ok','Operational type correction; biological denominator and answer correctness not validated'],
          [task_link('CompBio','perturb-seq-align-q1')+'; DeepSeek G r3','AnnData chunk_X: sparse-matrix attribute error',
           'Successful var metadata query','Same tool/input, different operation; not recovery of chunk_X']],
          "Purposive positive and contradictory examples, not a random sample of 213 candidates. "
          "Exact event IDs, parameter changes, timestamps and excerpts are preserved in `case_reviews` in the "
          "[CompBio audit](CompBio/compBio_overview_audit.json). No recovery success percentage is inferred from these two cases.")
    table('C8','Most frequently recorded Galaxy operations',['Recorded tool / version','Non-fetch jobs','Error jobs'],tool_rows('CompBio'),
          "Top six tool IDs by job count among 16,686 deduplicated non-fetch jobs. AnnData inspection and bedtools intersection "
          "appear alongside filtering, column selection, Datamash and legacy upload. This is evidence of operation availability/use, "
          "not correctness, independent analyses or exclusive use of installed domain tools. Full IDs and event references are in the analysis JSON.")
    deep.render(SimpleNamespace(**globals()),'CompBio',table,runs,cells,jobs,results)
    put("## 3) BixBench50 + CompBio analysis\n\n**Finding:** input-token overhead appears in both archives, while evidence completeness "
        "and operational burden vary substantially. Shared evidence supports prioritizing observability and validated input/operation contracts. "
        "It does not establish a cross-benchmark accuracy benefit or that provenance benefits outweigh resource cost.")
    table('X1','What can be combined fairly?', ['Endpoint / population','BixBench50','CompBio','Combined interpretation'],[
          ['Archived inventory','50 tasks; 1,500 runs','100 tasks; 2,500 runs','150 task packages; 4,000 records, not 4,000 independent observations'],
          ['Shared supplied GPT labels (primary cross-benchmark set)','3 configurations; 900 runs','3 configurations; 1,800 runs','2,700 records; exact runtime/reasoning matching not established'],
          ['DeepSeek','V4 Pro / Codex; superseded Claude Code separate','V4 Pro 0813 / Codex','Version equivalence unverified; excluded from primary cross-benchmark effects'],
          ['Task-level accepted answers','1,500 binary scores','0/2,500 item scores','No combined accuracy, correct-per-token or correctness/recovery estimate'],
          ['Paired input-token ratios','250/250 all-configuration pairs','386/400 all-configuration pairs','Comparable formula; report benchmark strata and shared-label comparisons'],
          ['Path agreement','Recomputed strict observed/nonempty eligibility','Same strict eligibility','Compare benchmarks within each instrument; no G-versus-Code consistency ranking'],
          ['Run-linked operational errors','Detailed histories in 714/750 G records','Detailed histories in 1,198/1,200 G records','Available-case burden; collection and task composition confound contrasts'],
          ['Full cost / human review time','Unavailable / unmeasured','Unavailable / unmeasured','Neither monetary efficiency nor faster human review is established']],
          "The historical CompBio source composes final vectors from multiple campaigns, unlike a prospectively fixed independent replicate design. "
          "Prompt additions, harnesses, tools, model verification, domain mix and campaign selection remain confounders. "
          "No cross-benchmark pooled accuracy denominator is constructed.")
    rows=[]
    for x in results['cross_tokens']:
        effect={'estimate':x['ratio_of_medians'],'ci95':x['ci95']}
        rows.append([LABELS.get(x['model'],'All three shared configurations'),
                     f"{x['BixBench50']['n']}; {ci(x['BixBench50'])}",f"{x['CompBio']['n']}; {ci(x['CompBio'])}",ci(effect)])
    table('X2','Does relative input-token overhead generalize across benchmarks?',
          ['Shared supplied configuration','Bix pairs; median G/Code [CI]','CompBio pairs; median G/Code [CI]','CompBio/Bix median-ratio contrast [CI]'],rows,
          "The last column divides the two benchmark-specific medians of within-task ratios; it is not an absolute-token ratio. "
          "A value above one means greater relative overhead in CompBio. Benchmark strata are resampled separately, "
          "preserving tasks/configurations within clusters. Selection differs and these are observational comparisons. "+uncertainty)
    rows=[]
    for x in results['cross_paths']:
        rows.append([ENV[x['condition']],f"{x['BixBench50']['n']}; {ci(x['BixBench50'],3)}",
                     f"{x['CompBio']['n']}; {ci(x['CompBio'],3)}",ci({'estimate':x['difference'],'ci95':x['ci95']},3)])
    table('X3','Does the same path instrument reproduce its agreement across benchmarks?',
          ['Instrument / environment','Bix eligible cells; mean [CI]','CompBio eligible cells; mean [CI]','CompBio - Bix [CI]'],rows,
          "Primary population: three shared GPT labels; all three run fingerprints observed and nonempty. "
          "This holds the extraction rule and included supplied labels fixed; eligible configuration proportions can still differ. "
          "It does not control biological task complexity, command-vocabulary coverage, "
          "custom-wrapper identity or campaign selection. Lower agreement describes more variable recorded toolsets/command indicators, "
          "not worse science. Instrument values must not be directly compared across the two rows.")
    rows=[]
    for x in results['failure_rates']:
        e={'estimate':100*x['estimate'],'ci95':[100*v for v in x['ci95']]}
        rows.append([x['benchmark'],frac(x['with_error'],x['n']),ci(e,1),x['clusters']])
    table('X4','Run-level operational burden with the shared configuration mix',
          ['Benchmark','G runs with >=1 non-fetch error / detailed runs','Percentage [95% CI]','Resampling clusters'],rows,
          "Three shared GPT labels only; missing detailed histories are excluded explicitly. Each run contributes one binary indicator, "
          "preventing runs with many jobs from dominating this estimate. Histories may contain inherited/later state; this is recorded burden, "
          "not a causal benchmark/platform failure probability. No code-condition counterpart uses an equivalent job instrument.")
    errors={benchmark:[j for j in jobs if j['benchmark']==benchmark and j['status']=='error'] for benchmark in FOLDERS}
    rows=[]
    for name in results['error_codebook']:
        rows.append([name,*[frac(results['error_indicators'][bm][name],len(errors[bm])) for bm in FOLDERS]])
    rows.extend([
        ['Error jobs with any retained stdout/stderr',*[frac(sum(j['has_error_text'] for j in errors[bm]),len(errors[bm])) for bm in FOLDERS]],
        ['Error jobs without retained stdout/stderr',*[frac(sum(not j['has_error_text'] for j in errors[bm]),len(errors[bm])) for bm in FOLDERS]],
        ['Text present but no rule matched',*[frac(sum(j['has_error_text'] and not j['error_indicators'] for j in errors[bm]),len(errors[bm])) for bm in FOLDERS]],
        ['Error state with recorded exit code zero',*[frac(sum(j['exit_code']==0 for j in errors[bm]),len(errors[bm])) for bm in FOLDERS]],
    ])
    table('X5','Which operational error messages are observable?',
          ['Exploratory indicator / observability','Bix error jobs (n=552)','CompBio error jobs (n=3,097)'],rows,
          "All benchmark-specific paired configurations, not just shared GPT labels. Deduplicated non-fetch error jobs; "
          "case-insensitive regex matches on retained stderr/stdout excerpts, with overlapping categories. "
          "The exact codebook and every source event reference are in the analysis JSON. "
          "These are message indicators, not independently adjudicated root causes; missing/truncated logs suppress detection, "
          "and absent text does not mean no diagnostic existed on the server. No significance test compares these unequally observed taxonomies. "
          "Exit code zero does not override the recorded Galaxy error state.")
    rows=[]
    for benchmark in FOLDERS:
        jj=[j for j in jobs if j['benchmark']==benchmark]
        counts=Counter(j['tool'] for j in jj);fails=Counter(j['tool'] for j in jj if j['status']=='error')
        top=sorted(fails,key=lambda t:(-fails[t],t))[:5]
        for tool in top:
            short=tool.split('/')[-2]+'/'+tool.split('/')[-1] if 'toolshed' in tool else tool
            rows.append([benchmark,short,frac(fails[tool],counts[tool])])
    table('X6','Where recorded error jobs concentrate', ['Benchmark','Recorded tool / version','Error / all jobs for tool'],rows,
          "Top five tool IDs ranked by error-job count within each benchmark (ties ordered by full ID); "
          "all non-fetch jobs and all configurations. These are triage targets, not tool-quality rankings: exposure, parameters, "
          "input quality, custom wrappers and task mix differ. In particular, udt-render-probe-v1 identifies a diagnostic probe; "
          "its error states cannot be assumed to be failed biomedical analyses. Full tool IDs and creating-job references are retained in `jobs` in the analysis JSON.")
    table('X7','Galaxy improvements suggested by the observed evidence',
          ['Priority / owner','Evidence and limitation','Proposed capability or integration','Prospective success measure'],[
          ['1. Galaxy API + agent client: complete audit capture',
           'B4/C3: 32 Bix and 2 CompBio metadata-only histories; CompBio state summaries disagree',
           'Paginate/resume history collection; reconcile dataset/job states; export run-scoped graph with inherited-job flags and immutable submission/evaluator receipts',
           'Missing-job rate, state disagreements, receipt/hash linkage, blinded audit reconstruction errors'],
          ['1. Tool wrappers + agent client: typed preflight',
           'C7: string division corrected; X5: numeric/type and dependency indicators',
           'Expose column types, sparse/dense matrix capabilities, required executable/version and typed argument checks before launch',
           'Avoidable error jobs per task and accepted-answer rate in a paired ablation; track false rejections'],
          ['1. Agent client + Galaxy: objective-aware recovery',
           '93 Bix and 213 CompBio candidates; chunk_X to var is a counterexample',
           'Attach objective IDs and output postconditions to attempts; show input/parameter diffs and require same-objective validation before marking recovery',
           'Adjudicated recovery precision, unresolved objectives, attempts/tokens before a supported result'],
          ['2. Workflow authors + evaluators: scientific input contracts',
           'B3: rejected RCV and transition/transversion answers despite successful jobs',
           'Persist cohort/callset, reference release, coordinates, filter thresholds and denominator; validate final result against the declared contract',
           'Scientifically wrong completed runs, parameter/reference mismatches and correct alternatives retained'],
          ['2. Galaxy API + agent client: compact state and usage ledger',
           'B7/C6/X2: median token ratios above one; stage attribution is unavailable',
           'Cache tool schemas, fetch state deltas, batch status queries and attach provider request usage to stages with a mixed/unattributed category',
           'Input/output/cache tokens and latency per task, with acceptance and evidence completeness held to prespecified targets'],
          ['2. Galaxy reports + user interface: evidence-linked result review',
           'B6/C2: consistency does not imply correctness; no human review study',
           'Show answer, supporting datasets, tool/parameter versions, unresolved errors and score provenance in one reviewable report',
           'Blinded randomized review time, reconstruction accuracy and reviewer agreement under equal information access']],
          "Priorities are analyst proposals, not measured intervention effects or claims that these features are wholly absent. "
          "Galaxy already documents [history API and exports](https://docs.galaxyproject.org/en/release_26.1/_modules/galaxy/webapps/galaxy/api/histories.html), "
          "[error troubleshooting](https://training.galaxyproject.org/training-material/faqs/galaxy/analysis_troubleshooting.html), "
          "[datatype handling](https://training.galaxyproject.org/training-material/faqs/galaxy/datatypes_understanding_datatypes.html) and "
          "[workflow reports](https://training.galaxyproject.org/training-material/faqs/galaxy/workflows_report_view.html). "
          "The proposed work is to assess and extend these capabilities at the agent interface. "
          "Collection limits belong to this audit's collector and are not established Galaxy server limits. "
          "Documentation checked 2026-09-22; no deployed-server feature audit was performed.")
    table('X8','Claim strength, remaining questions and evidence needed',
          ['Question','Supported answer / strength','Evidence','What would resolve the gap?'],[
          ['Does Galaxy improve accuracy?', 'Bix difference is small/uncertain and harness-sensitive; CompBio unassessable',
           'B1-B3; finding_accuracy in source manifest', 'Fixed prospective design, compatible prompts/runtime settings, item evaluator receipts and predefined equivalence/superiority estimand'],
          ['Is overhead common?', 'Higher median input-token ratios in both archives; robust descriptive result for observed primary turns',
           'B7/C6/X2; token_pairs and finding_cost_readability', 'All campaigns/subagents, cache accounting, per-call stage usage and compute/storage costs'],
          ['Are consistent paths or answers valid?', 'Consistency is observable; validity is a separate endpoint',
           'B6/C2/C5/X3; cells and finding_variability', 'CompBio item scores; common adjudicated biological-method codebook and intermediate outputs'],
          ['Can error causes and recovery be quantified?', 'Job burden and message indicators yes; comparative scientific recovery rate no',
           'B4/C3/C7/X4-X6; jobs and finding_execution', 'Complete diagnostics, common-stage attempt mapping, objective-linked endpoints and random adjudication of candidates/noncandidates'],
          ['Does Galaxy make human review easier?', 'Inspectable provenance exists; improved review performance is unmeasured',
           'Source task packages; X7', 'Randomized blinded reconstruction study with equal evidence access and reviewer agreement'],
          ['Do results generalize by difficulty?', 'No independent difficulty annotation or controlled prompt-version comparison',
           'HISTORY_ANALYSIS_INSTRUCTIONS.md; task metadata', 'Prospectively defined task-complexity strata and independent benchmark replication']],
          "All 150 task evidence paths, hashes, included run IDs and original finding IDs are linked in the "
          "[source manifest](BixBench50_CompBio_analysis/source_manifest.json). Table-specific display values and calculated "
          "statistics, run/cell denominators, job references and exclusion rules are in the "
          "[analysis JSON](BixBench50_CompBio_analysis/analysis.json). Source task evidence is unchanged; no hidden references, "
          "recovered agent code, new Galaxy runs or new correctness judgements were used.")
    deep.render(SimpleNamespace(**globals()),'combined',table,runs,cells,jobs,results)
    return '\n'.join(doc), tables


def main():
    b=read('BixBench_50/bixBench50_overview_audit.json')
    c=read('CompBio/compBio_overview_audit.json')
    manifest,runs,cells,jobs=load_data(b,c)
    results=compute(b,c,runs,cells,jobs)
    results['deep']=deep.compute(SimpleNamespace(**globals()),runs,cells,jobs)
    # Cross-check archived aggregates before generating publication tables.
    for benchmark,audit in [('BixBench50',b),('CompBio',c)]:
        jj=[j for j in jobs if j['benchmark']==benchmark]
        expected=audit['jobs']['unique'] if benchmark=='BixBench50' else audit['execution']['nonfetch_jobs']
        assert len(jj)==expected,(benchmark,len(jj),expected)
        expected_states=audit['jobs']['states'] if benchmark=='BixBench50' else audit['execution']['nonfetch_states']
        assert dict(Counter(j['status'] for j in jj))==expected_states
        expected_ratio=audit['token_ratios']['median'] if benchmark=='BixBench50' else audit['tokens']['pooled']['median']
        assert abs(results['tokens'][benchmark+'_all']['median']-expected_ratio)<1e-10
    for cond in CONDITIONS:
        assert results['accuracy']['all']['conditions'][cond]==b['accuracy'][cond]
    assert all(r['score'] is None for r in runs if r['benchmark']=='CompBio')
    for row in c['solution_paths']['by_condition_and_model']:
        own=next(s for s in results['path_summaries'] if s['benchmark']=='CompBio' and s['condition']==row['condition'] and s['model']==('all' if row['model']=='ALL' else row['model']))
        assert own['evaluable']==row['evaluable_cells']
        assert abs(own['mean_jaccard']-row['mean_jaccard'])<1e-12
    text,tables=report(b,c,runs,cells,jobs,results)
    source_paths=['HISTORY_ANALYSIS_INSTRUCTIONS.md','scripts/build_result_tables.py','scripts/result_table_deep_analysis.py',
                  'BixBench_50/bixBench50_overview_audit.json','CompBio/compBio_overview_audit.json',
                  'BixBench_50/solution_path_consistency_analysis.py',
                  'BixBench_50/result_section_bixbench50.md','CompBio/result_section_compbio.md']
    OUT.mkdir(exist_ok=True)
    source_manifest={"format": "cross-benchmark-aggregate-manifest-v1", "not_task_evidence_schema": True,
                     "sources": [{"path":p,"sha256":sha(p)} for p in source_paths],"tasks":manifest,
                     "reviewed_trace_sources": [{"path":x['source'],"sha256":x['sha256'],"lines":[m['line'] for m in x['messages']]}
                                                for x in results['deep']['case_sources']]}
    shared_jobs=({(j['server'],j['native_job_id']) for j in jobs if j['benchmark']=='BixBench50'} &
                 {(j['server'],j['native_job_id']) for j in jobs if j['benchmark']=='CompBio'})
    data={"format":"cross-benchmark-analysis-v1", "software":{"python":platform.python_version(),"numpy":np.__version__},
          "bootstrap":{"resamples":RESAMPLES,"seed":SEED,"method":"percentile; NumPy linear quantiles; statistic-key SHA256 stream",
                       "units":{"BixBench50":"capsule","CompBio":"task"},"status":"exploratory pointwise intervals"},
          "common_configurations":list(COMMON),"results":results,"tables":tables,"runs":runs,"cells":cells,"jobs":jobs,
          "validation":{"source_evidence_hashes_checked":len(manifest),"run_ids_unique":len(runs),
                        "archived_accuracy_jobs_token_medians_reproduced":True,"compbio_path_summaries_reproduced":True,
                        "cross_benchmark_shared_native_jobs":len(shared_jobs),"compbio_item_scores_remain_null":True}}
    (OUT/'source_manifest.json').write_text(json.dumps(source_manifest,indent=2,ensure_ascii=True)+'\n')
    (OUT/'analysis.json').write_text(json.dumps(data,indent=2,ensure_ascii=True,allow_nan=False)+'\n')
    (ROOT/'Result_table.md').write_text(text)
    print(json.dumps({"tables":len(tables),"runs":len(runs),"task_packages":len(manifest),"shared_native_jobs":len(shared_jobs),
                      "report":"Result_table.md","analysis_bytes":(OUT/'analysis.json').stat().st_size},indent=2))


if __name__=='__main__':
    main()
