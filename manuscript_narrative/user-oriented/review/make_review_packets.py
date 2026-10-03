"""Expert-review packets for Supplementary Note 1, section 4 (blinded expert review and audit verification).

Run from the repository root with the narrative environment:
    python manuscript_narrative/user-oriented/review/make_review_packets.py [--out DIR] [--concordant-per-stratum N]

What it writes
- In this repository (no answers, safe to keep here):
    review/sampling_design.csv   every replicate set in the primary population, its stratum, inclusion probability and
                                 whether it was selected;
    review/audit_sample.csv      audited task cases selected for human verification and why;
    review/packet_manifest.json  SHA-256 of every packet file written outside the repository.
- Outside this repository (default: <repository parent>/Galaxy_benchmark_review_packets/user_oriented/):
    reviewer/T##/task.md, reviewer/T##/runs.md, reviewer/T##/rating_form.csv   blinded run packets, one folder per task;
    reviewer/audit/C##.md, reviewer/audit/audit_rating_form.csv                  audit-verification packets;
    coordinator/run_key.csv, coordinator/audit_key.csv, coordinator/README.md    the keys that undo the blinding.

Why the packets are written outside the repository: a packet holds each run's submitted answer, and the sampling design
says which sets were all correct. Together they reveal benchmark reference answers, including the private CompBioBench
key. Agents are run from this repository, so nothing that reveals references may be stored here.

Blinding: runs are shown in a random order under random identifiers, with the same layout for both arms. Each analysis
step is the executed command line (Galaxy job command or shell command) with directory paths reduced to file names and
platform words masked. Provenance structure can still reveal the arm, so reviewers record an arm guess.
Not included anywhere: evaluator scores, references, grades, arm labels, model names, run identifiers.
"""
import argparse
import csv
import hashlib
import json
import os
import random
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
NARR = HERE.parents[1]
ROOT = NARR.parent
sys.path.insert(0, str(NARR))
import narrative_common as nc  # noqa: E402
from style import CONFIGS  # noqa: E402

SEED = 20261002
BENCH_DIR = {'BixBench50': 'BixBench_50', 'CompBio': 'CompBio', 'IWC': 'IWC'}
BENCH_LABEL = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
IWC_EXCLUDED = 'wf_003_host_contamination_removal'
MAX_STEPS = 80
MAX_CMD = 500
MAX_OUT = 300
MASK = re.compile(r'(?i)[\w.\-]*(?:galaxy|toolshed|bioblend|planemo|codex|claude|deepseek|shed_tools|cvmfs|jetstream)[\w.\-]*'
                  r'|[\w.\-]*gpt[-_]?\d[\w.\-]*|[\w.\-]*histor(?:y|ies)[\w.\-]*|(?<![A-Za-z0-9])hda(?![A-Za-z0-9])')
PATH = re.compile(r"(?<![\w.])/(?:[^\s'\"/]+/)+([^\s'\"/]*)")
HEXID = re.compile(r'\b[0-9a-f]{16,40}\b')


# ---------------------------------------------------------------------------------------------------- sampling
def sampling_frame():
    """Replicate sets of the primary population: four Codex configurations, nine IWC tasks."""
    s = nc.replicate_sets()
    s = s[s.cfg.isin(CONFIGS) & (s.task != IWC_EXCLUDED)].copy()

    def stratum(r):
        if r['cat'] == 'split':
            return 'discordant'
        if r.benchmark == 'IWC':
            return 'concordant_high' if r['mean'] >= 0.95 else 'concordant_low'
        return 'concordant_all_correct' if r['cat'] == '3/3' else 'concordant_none_correct'
    s['stratum'] = s.apply(stratum, axis=1)
    return s.reset_index(drop=True)


def draw_sample(frame, per_stratum):
    rng = np.random.default_rng(SEED)
    out = []
    for (b, e, st), x in frame.groupby(['benchmark', 'env', 'stratum']):
        x = x.sort_values(['task', 'cfg']).copy()
        n = len(x) if st == 'discordant' else min(per_stratum, len(x))
        pick = set(rng.choice(len(x), size=n, replace=False)) if n < len(x) else set(range(len(x)))
        x['stratum_sets'] = len(x)
        x['selected_sets'] = n
        x['inclusion_probability'] = n / len(x)
        x['selected'] = [i in pick for i in range(len(x))]
        out.append(x)
    return pd.concat(out, ignore_index=True)


def audit_sample():
    tc = pd.DataFrame(nc.fd()['task_cases'])
    rng = random.Random(SEED)
    n = round(0.2 * len(tc))
    random_pick = set(rng.sample(sorted(tc.task), n))
    galaxy = set(tc[(tc.category == 'C4') | tc.tags.apply(lambda v: 'galaxy-platform-defect' in v)].task)
    tc['random_20pct'] = tc.task.isin(random_pick)
    tc['galaxy_attributed'] = tc.task.isin(galaxy)
    tc['selected'] = tc.random_20pct | tc.galaxy_attributed
    tc['inclusion_probability'] = np.where(tc.galaxy_attributed, 1.0, n / len(tc))
    return tc


# ---------------------------------------------------------------------------------------------------- evidence
def run_cfg(run):
    """Model configuration from the run identifier (<condition>_<model key>_r<replicate>)."""
    key = re.sub(r'_r\d+$', '', re.sub(r'^(galaxy|open_ended_code)_', '', run['run_id']))
    return nc.CFG.get(key) or nc.CFG.get('codex_' + key) or key


def evidence(benchmark, task):
    p = ROOT / BENCH_DIR[benchmark] / 'analysis' / task / 'history_analysis_evidence.json'
    return json.load(open(p))


def task_statement(benchmark, task, ev):
    prompt = (ev.get('task') or {}).get('prompt')
    if prompt:
        return prompt.strip()
    # IWC keeps no task-level question; both arms' prompts are identical before their run-condition block
    for r in ev['runs']:
        for a in r.get('artifacts') or []:
            if a.get('original_name') == 'prompt.txt' and a.get('local_path'):
                p = ROOT / BENCH_DIR[benchmark] / 'analysis' / task / a['local_path']
                if p.exists():
                    return p.read_text().split('Run condition constraints:')[0].strip()
    return '(task statement not retained in the archive)'


def scrub(text, limit):
    if not text:
        return ''
    t = str(text)
    t = re.sub(r"^/bin/(ba)?sh -lc ", '', t.strip())
    t = PATH.sub(lambda m: m.group(1) or '.', t)
    t = HEXID.sub('<id>', t)
    t = MASK.sub('[masked]', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t if len(t) <= limit else t[:limit] + ' […]'


def tool_label(e):
    tool = str(e.get('tool') or '')
    if e.get('execution_location') == 'galaxy_job' or '/' in tool:
        parts = tool.rstrip('/').split('/')
        name = parts[-2] if len(parts) >= 2 and re.match(r'^[\d.]+', parts[-1]) else parts[-1]
        ver = re.sub(r'\+galaxy\d+$', '', parts[-1]) if len(parts) >= 2 and re.match(r'^[\d.]+', parts[-1]) else (e.get('tool_version') or '')
        return scrub(f'{name} {ver}'.strip(), 80)
    return 'command'


def run_steps(benchmark, task, run_id, arm):
    p = ROOT / BENCH_DIR[benchmark] / 'analysis' / task / 'job_ledgers' / arm / f'{run_id}.json'
    if not p.exists():
        return None
    ev = json.load(open(p))['events']
    steps = []
    for e in ev:
        if e.get('event_type') != 'analysis':
            continue
        cmd = e.get('command')
        if not cmd and e.get('parameters'):
            cmd = json.dumps({k: v for k, v in e['parameters'].items() if not str(k).startswith('__')})
        steps.append(dict(label=tool_label(e), command=scrub(cmd, MAX_CMD), status=str(e.get('status') or ''),
                          exit_code=e.get('exit_code'), output=scrub(e.get('stdout_excerpt'), MAX_OUT),
                          error=scrub(e.get('stderr_excerpt'), MAX_OUT)))
    return steps


def final_artifacts(run):
    names = []
    for a in run.get('artifacts') or []:
        if a.get('role') in ('final_answer', 'final_deliverable', 'selected_output') and a.get('original_name') != 'prompt.txt':
            names.append(f"{a.get('original_name')} ({a.get('observed_size', '?')} bytes; sha256 {str(a.get('sha256', ''))[:12]})")
    return names


# ---------------------------------------------------------------------------------------------------- writing
RUBRIC = """## How to rate each run (stage 1, no reference shown)

For every run, fill one row of `rating_form.csv`:

- `validity`: `valid`, `defensible_alternative`, `invalid` or `cannot_judge`. Judge the analysis and the answer against
  the task as stated, not against a benchmark reference.
- `followed_request`: `yes`, `partly` or `no`.
- `checkability`: `all`, `most`, `some` or `none` of the steps can be checked from this record.
- `minutes`: time you spent on this run.
- `arm_guess`: `A` (the agent wrote and ran its own code), `B` (the agent ran installed tools as managed jobs) or
  `unsure`, and `arm_confidence` from 1 (guess) to 5 (certain).
- `notes`: anything that drove your rating.

Commands show file names only; directory paths, identifiers and platform words are masked as `[masked]` or `<id>`.
Command output is truncated. Do not search for the benchmark or its answers. Stage 2, in which the coordinator shows
the benchmark reference where its release is permitted, is a separate form.
"""


def write_run_packets(sample, out):
    rng = random.Random(SEED + 1)
    sel = sample[sample.selected]
    tasks = sorted({(r.benchmark, r.task) for r in sel.itertuples()})
    rng.shuffle(tasks)
    run_ids = list(range(1, 10000))
    rng.shuffle(run_ids)
    key, written = [], []
    for ti, (b, t) in enumerate(tasks, start=1):
        tid = f'T{ti:02d}'
        ev = evidence(b, t)
        evr = {(r['condition'], run_cfg(r), int(r['replicate_id'])): r for r in ev['runs']}
        runs = []
        for r in sel[(sel.benchmark == b) & (sel.task == t)].itertuples():
            for rep in (1, 2, 3):
                er = evr.get((r.env, r.cfg, rep))
                runs.append((r, rep, er))
        rng.shuffle(runs)
        d = out / 'reviewer' / tid
        d.mkdir(parents=True, exist_ok=True)
        (d / 'task.md').write_text(f'# Task {tid}\n\n## Task as given to the agent\n\n{task_statement(b, t, ev)}\n\n{RUBRIC}')
        lines = [f'# Task {tid}: runs to review\n', f'{len(runs)} runs, in random order.\n']
        form = []
        for r, rep, er in runs:
            rid = f'R{run_ids.pop():04d}'
            if er is None:
                answer, steps, arts = '(run not found in the archive)', None, []
            else:
                answer = (er.get('outcome') or {}).get('submitted_answer') or '(no answer submitted)'
                steps = run_steps(b, t, er['run_id'], r.env)
                arts = final_artifacts(er)
            lines.append(f'\n## Run {rid}\n\n**Submitted answer**\n\n```\n{scrub(answer, 2000)}\n```\n')
            if arts:
                lines.append('**Deliverable files** (the coordinator supplies the files): ' + '; '.join(arts) + '\n')
            if steps is None:
                lines.append('\n*No execution trace was retained for this run.*\n')
            else:
                lines.append(f'\n**Analysis steps** ({len(steps)} recorded' + (f'; first {MAX_STEPS} shown' if len(steps) > MAX_STEPS else '') + ')\n')
                for k, s in enumerate(steps[:MAX_STEPS], start=1):
                    status = s['status'] + (f', exit {s["exit_code"]}' if s['exit_code'] not in (None, 0) else '')
                    lines.append(f'{k}. `{s["label"]}` ({status}): `{s["command"]}`')
                    if s['output']:
                        lines.append(f'   - output: `{s["output"]}`')
                    if s['error']:
                        lines.append(f'   - error: `{s["error"]}`')
            form.append(dict(task=tid, run=rid, reviewer='', validity='', followed_request='', checkability='', minutes='',
                             arm_guess='', arm_confidence='', notes=''))
            key.append(dict(task=tid, run=rid, benchmark=b, task_id=t, cfg=r.cfg, arm=r.env, replicate=rep,
                            run_id=er['run_id'] if er else '', stratum=r.stratum, inclusion_probability=r.inclusion_probability,
                            trace_retained=steps is not None))
        (d / 'runs.md').write_text('\n'.join(lines) + '\n')
        pd.DataFrame(form).to_csv(d / 'rating_form.csv', index=False)
        written += [d / 'task.md', d / 'runs.md', d / 'rating_form.csv']
    return pd.DataFrame(key), written


AUDIT_CODEBOOK = """## Primary-cause codebook

- C1: equivalent answer in another notation
- C2: scoring or evaluator artifact
- C3: the reference depends on a choice the task does not state (definition, software version, sample set, threshold)
- C4: Galaxy platform, wrapper or server
- C5: agent analysis error
- C6: other (harness failure, unresolved)

Also record whether the Galaxy platform, a wrapper or the server contributed (`galaxy_contributed`: yes/no/unclear).
"""


def write_audit_packets(tc, out):
    rng = random.Random(SEED + 2)
    sel = tc[tc.selected].sort_values('task').reset_index(drop=True)
    order = list(range(len(sel)))
    rng.shuffle(order)
    d = out / 'reviewer' / 'audit'
    d.mkdir(parents=True, exist_ok=True)
    key, form, written = [], [], []
    for ci, i in enumerate(order, start=1):
        c = sel.iloc[i]
        cid = f'C{ci:02d}'
        ev = evidence(c.benchmark, c.task)
        rows = []
        for r in sorted(ev['runs'], key=lambda r: r['run_id']):
            ans = (r.get('outcome') or {}).get('submitted_answer') or ''
            ledger = f"{BENCH_DIR[c.benchmark]}/analysis/{c.task}/job_ledgers/{r['condition']}/{r['run_id']}.json"
            rows.append(f"| {r['run_id']} | {str(ans)[:120].replace('|', '/').replace(chr(10), ' ')} | `{ledger}` |")
        withheld = c.benchmark == 'CompBio'
        text = [f'# Audit case {cid}: {BENCH_LABEL[c.benchmark]} task {c.task}\n',
                '## Task as given to the agents\n', task_statement(c.benchmark, c.task, ev), '',
                '## Outcome', f'Runs scored correct by the benchmark: Galaxy arm {c.galaxy}, open-ended code arm {c.code}.' if not withheld else
                'Per-run correctness and the reference are withheld until the CompBioBench maintainers permit their release '
                '(`manuscript_narrative/COMPBIO_REFERENCE_REQUEST.md`); the coordinator adds them in stage 2.', '',
                '## Runs, answers and evidence', 'Traces, job ledgers and Galaxy histories are in the project archive at the paths given.', '',
                '| run | submitted answer (first 120 characters) | job ledger |', '|---|---|---|', *rows, '',
                'Do not read `individual_error_analysis.md` or any manuscript text about this task before rating.', '', AUDIT_CODEBOOK]
        (d / f'{cid}.md').write_text('\n'.join(text) + '\n')
        written.append(d / f'{cid}.md')
        form.append(dict(case=cid, reviewer='', primary_cause='', galaxy_contributed='', confidence_1_to_5='', minutes='', notes=''))
        key.append(dict(case=cid, benchmark=c.benchmark, task=c.task, ai_primary_cause=c.category, ai_tags=';'.join(c.tags),
                        random_20pct=c.random_20pct, galaxy_attributed=c.galaxy_attributed, inclusion_probability=c.inclusion_probability,
                        outcome_withheld=withheld))
    pd.DataFrame(form).to_csv(d / 'audit_rating_form.csv', index=False)
    written.append(d / 'audit_rating_form.csv')
    return pd.DataFrame(key), written


COORD_README = """# Coordinator notes (do not share this folder with reviewers)

`run_key.csv` and `audit_key.csv` undo the blinding. Keep them away from reviewers until all stage-1 forms are returned.

1. Pilot: give each reviewer the runs flagged `pilot` in `run_key.csv` first. If reviewers' arm guesses are correct
   in more than 70% of pilot runs, revise the step format before the main review (Supplementary Note 1).
2. Assign two domain experts per task folder; they rate independently. A third expert resolves disagreements.
3. Stage 2: after stage-1 forms are returned, show the benchmark reference for BixBench-Verified-50 and IWC tasks and
   record `agrees_with_reference`, `defensible_but_different` or `invalid`. CompBioBench references and per-run
   correctness stay withheld until the maintainers permit their release.
4. Population estimates use inverse-probability weights from `inclusion_probability`; report the enriched-sample
   (unweighted) estimates separately.
5. Report Cohen's kappa for validity, agreement with the AI-assisted audit (`audit_key.csv`) and the arm-guess accuracy.
6. Deliverable files (IWC outputs) are listed by name and hash in the packets; supply them from the archive paths given
   by `run_id` in `run_key.csv`.
"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=str(ROOT.parent / 'Galaxy_benchmark_review_packets' / 'user_oriented'))
    ap.add_argument('--concordant-per-stratum', type=int, default=5)
    a = ap.parse_args()
    out = Path(a.out).resolve()
    if ROOT in out.parents or out == ROOT:
        sys.exit('Refusing to write packets inside the repository: they reveal benchmark references (see module docstring).')

    frame = sampling_frame()
    sample = draw_sample(frame, a.concordant_per_stratum)
    tc = audit_sample()
    (out / 'coordinator').mkdir(parents=True, exist_ok=True)
    run_key, w1 = write_run_packets(sample, out)
    pilot = run_key[run_key.stratum == 'discordant'].groupby('arm', group_keys=False).apply(
        lambda x: x.sample(n=min(10, len(x)), random_state=SEED))
    run_key['pilot'] = run_key.run.isin(pilot.run)
    run_key.to_csv(out / 'coordinator' / 'run_key.csv', index=False)
    audit_key, w2 = write_audit_packets(tc, out)
    audit_key.to_csv(out / 'coordinator' / 'audit_key.csv', index=False)
    (out / 'coordinator' / 'README.md').write_text(COORD_README)

    # repository-side records: no answers
    cols = ['benchmark', 'task', 'cfg', 'env', 'stratum', 'stratum_sets', 'selected_sets', 'inclusion_probability', 'selected']
    sample[cols].sort_values(cols[:4]).to_csv(HERE / 'sampling_design.csv', index=False)
    tc[['benchmark', 'task', 'random_20pct', 'galaxy_attributed', 'inclusion_probability', 'selected']].sort_values('task').to_csv(
        HERE / 'audit_sample.csv', index=False)
    files = w1 + w2 + [out / 'coordinator' / n for n in ('run_key.csv', 'audit_key.csv', 'README.md')]
    manifest = dict(seed=SEED, concordant_per_stratum=a.concordant_per_stratum, output_dir_name=out.name,
                    sets_selected=int(sample.selected.sum()), runs=len(run_key), tasks=int(run_key.task.nunique()),
                    runs_without_trace=int((~run_key.trace_retained).sum()), pilot_runs=int(run_key.pilot.sum()),
                    audit_cases=len(audit_key),
                    files={str(f.relative_to(out)): hashlib.sha256(f.read_bytes()).hexdigest() for f in files})
    json.dump(manifest, open(HERE / 'packet_manifest.json', 'w'), indent=1)
    print(json.dumps({k: v for k, v in manifest.items() if k != 'files'}, indent=1))
    print('packets written to', out)


if __name__ == '__main__':
    main()
