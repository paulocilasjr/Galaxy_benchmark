"""Failure episodes: was a failed execution step later re-run successfully in the same run, and did the run end correct?

An episode is one failed step:
- a Galaxy job of an installed tool in the error state (interface records), resolved when a later job of the same tool
  (Tool Shed identifier without version) completed in the same run;
- a Galaxy job of a user-defined tool (UDT) in the error state, resolved when a later UDT job completed;
- a shell command that exited non-zero and ran a named analysis program or script file (inline code, file inspection,
  coreutils and downloads are excluded, because they cannot be matched to a specific analysis step), resolved when a
  later command running the same program and file exited 0. Exit code 1 with no error output is not counted, as in Fig. 3c.
Shell episodes are compared between conditions on the same definition. Written: figures/failure_episodes.csv (one row
per episode: benchmark, task, model, condition, replicate, channel, program key, resolved, steps to resolution, run
correct). Heuristic: resolution means the same step later ran without error, not that the error was understood or that
the corrected step was scientifically right.
"""
# result_evaluation copy of figures/make_failure_episodes.py: scores come from scored_runs.csv (make_scored_runs.py; every run matched to
# the public results site, IWC host-read removal included) and every output is written next to this script. The
# manuscript figure set in figures/ is not touched. Changes from the original are marked "result_evaluation:".
import glob
import gzip
import json
import os
import re
import shlex

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))   # result_evaluation: two levels up
OUT = os.path.dirname(os.path.abspath(__file__))   # result_evaluation: write here, not to figures/
FIGS = os.path.join(ROOT, 'figures')               # result_evaluation: unchanged inputs from the manuscript figure set
SCORED = os.path.join(OUT, 'scored_runs.csv')      # result_evaluation: per-run scores matched to the results site
GC = os.path.join(ROOT, 'manuscript_narrative', 'derived', 'galaxy_calls')
AN = os.path.join(ROOT, 'manuscript_narrative', 'original_layout', 'analysis')
EVIDENCE = [os.path.join(ROOT, b, 'analysis', '*', 'history_analysis_evidence.json') for b in ('BixBench_50', 'CompBio', 'IWC')]
TRACE_MODEL = {'codex_gpt_5_5': 'GPT-5.5', 'codex_gpt_5_6_sol': 'GPT-5.6 Sol', 'codex_gpt_5_6_luna': 'GPT-5.6 Luna',
               'deepseek_v4_pro_via_codex': 'DeepSeek V4 Pro', 'codex_deepseek_v4_pro_0813': 'DeepSeek V4 Pro',
               'codex_deepseek_v4_pro': 'DeepSeek V4 Pro', 'gpt_5_5': 'GPT-5.5', 'gpt_5_6_sol': 'GPT-5.6 Sol',
               'gpt_5_6_luna': 'GPT-5.6 Luna', 'deepseek_v4_pro': 'DeepSeek V4 Pro'}
CORRECT_AT = {'BixBench50': 1.0, 'CompBio': 1.0, 'IWC': 0.99}
INTERP = {'python', 'python3', 'Rscript', 'bash', 'sh', 'perl', 'node', 'R'}
SKIP = {'cd', 'export', 'set', 'source', 'mkdir', 'echo', 'printf', 'true', 'test', '[', 'pwd', 'ls', 'cat', 'head',
        'tail', 'sed', 'awk', 'grep', 'rg', 'find', 'which', 'wc', 'du', 'file', 'cp', 'mv', 'rm', 'ln', 'tar', 'unzip',
        'gzip', 'gunzip', 'zcat', 'sort', 'cut', 'tr', 'xargs', 'curl', 'wget', 'stat', 'env', 'nproc', 'free', 'df',
        'chmod', 'touch', 'date', 'sleep', 'timeout', 'uniq', 'jq', 'diff', 'md5sum', 'sha256sum', 'basename',
        'dirname', 'readlink', 'realpath', 'tee', 'column', 'less', 'more', 'nl', 'paste', 'comm', 'join', 'seq'}
# Only analysis programs and scripts define an episode: coreutils, file inspection and downloads are skipped.


def program_key(command):
    """'tool' or 'interpreter file' for the first real command of a shell call; None for inline code."""
    c = command.strip()
    m = re.match(r'^/bin/(?:ba)?sh\s+-l?c\s+(.*)$', c, flags=re.S)
    if m:
        c = m.group(1).strip()
        if c[:1] in '\'"' and c[-1:] == c[:1]:
            c = c[1:-1]
    first = re.split(r'&&|;|\|\||\n|\|', c)
    for part in first:
        try:
            tok = shlex.split(part, posix=True)
        except ValueError:
            tok = part.split()
        tok = [t for t in tok if not re.match(r'^[A-Z_][A-Z0-9_]*=', t)]     # environment assignments
        if not tok or tok[0] in SKIP:
            continue
        prog = os.path.basename(tok[0])
        if prog in INTERP:
            rest = [t for t in tok[1:] if not t.startswith('-')]
            if not rest or '<<' in part or '-c' in tok[1:2] or tok[1:2] == ['-']:
                return None                                                  # inline code
            return f'{prog} {os.path.basename(rest[0])}'
        return prog
    return None


def shell_episodes():
    rows = []
    for path in sorted(p for pattern in EVIDENCE for p in glob.glob(pattern)):
        d = json.load(open(path))
        bm = 'BixBench50' if os.sep + 'BixBench_50' + os.sep in path else (
            'CompBio' if os.sep + 'CompBio' + os.sep in path else 'IWC')
        for run in d['runs']:
            model = re.sub(r'_r\d+$', '', re.sub(r'^(galaxy|open_ended_code)_', '', run['run_id']))
            if model not in TRACE_MODEL:
                continue
            cmds = [e for e in run['events'] if e.get('tool') == 'shell' and e.get('command')]
            cmds.sort(key=lambda e: int(e.get('sequence') or 0))
            keys = [program_key(str(e['command'])) for e in cmds]
            for i, (e, k) in enumerate(zip(cmds, keys)):
                code = str(e.get('exit_code'))
                if k is None or code in ('0', 'None', 'nan', ''):
                    continue
                if code == '1' and not str(e.get('stderr_excerpt') or '').strip() \
                        and not str(e.get('stdout_excerpt') or '').strip():
                    continue
                later = [j for j in range(i + 1, len(cmds)) if keys[j] == k and str(cmds[j].get('exit_code')) == '0']
                rows.append(dict(benchmark=bm, task=d['task']['task_id'], cfg=TRACE_MODEL[model],
                                 env=run['condition'], replicate=int(run['replicate_id']),
                                 channel=f'shell ({"Galaxy" if run["condition"] == "galaxy" else "custom code"} runs)',
                                 key=k, resolved=bool(later), steps=(later[0] - i) if later else None))
    return pd.DataFrame(rows)


def galaxy_episodes():
    c = pd.read_csv(os.path.join(GC, 'calls.csv.gz'), low_memory=False,
                    usecols=['benchmark', 'task', 'model', 'replicate', 'run_id', 'line', 'tool', 'galaxy_server',
                             'job_states', 'tool_id_base'])
    c = c[c.model.isin(TRACE_MODEL) & c.galaxy_server & c.tool.isin(['run_galaxy_tool_and_wait',
                                                                       'run_galaxy_udt_and_wait'])]
    c = c.sort_values(['run_id', 'task', 'line'])
    c['err'] = c.job_states.fillna('').str.contains(r'(?:^|;)error(?=;|$)')
    c['ok'] = c.job_states.fillna('').str.contains(r'(?:^|;)ok(?=;|$)')
    c['key'] = c.tool_id_base.where(c.tool == 'run_galaxy_tool_and_wait', 'UDT')
    rows = []
    for (rid, task), g in c.groupby(['run_id', 'task'], sort=False):
        g = g.reset_index(drop=True)
        for i in g.index[g.err]:
            later = g.index[(g.index > i) & g.ok & (g.key == g.key[i])]
            rows.append(dict(benchmark=g.benchmark[i], task=task, cfg=TRACE_MODEL[g.model[i]], env='galaxy',
                             replicate=int(g.replicate[i]),
                             channel='Galaxy UDT jobs' if g.key[i] == 'UDT' else 'Galaxy installed-tool jobs',
                             key=g.key[i], resolved=len(later) > 0, steps=int(later[0] - i) if len(later) else None))
    return pd.DataFrame(rows)


def main():
    ep = pd.concat([galaxy_episodes(), shell_episodes()], ignore_index=True)
    r = pd.read_csv(SCORED)
    r['run_correct'] = (r.score >= r.benchmark.map(CORRECT_AT) - 1e-9).astype(int)
    ep = ep.merge(r[['benchmark', 'task', 'cfg', 'env', 'replicate', 'run_correct', 'cluster']],
                  on=['benchmark', 'task', 'cfg', 'env', 'replicate'], how='inner')
    ep.to_csv(os.path.join(OUT, 'failure_episodes.csv'), index=False)
    print(len(ep), 'episodes in scored runs')
    print(ep.groupby('channel').agg(episodes=('resolved', 'size'), resolved=('resolved', 'mean'),
                                    runs=('task', lambda s: len(set(zip(s, ep.loc[s.index, 'cfg'],
                                                                         ep.loc[s.index, 'replicate'])))),
                                    correct_if_resolved=('run_correct', lambda s: s[ep.loc[s.index, 'resolved']].mean()),
                                    correct_if_unresolved=('run_correct',
                                                           lambda s: s[~ep.loc[s.index, 'resolved']].mean())).round(3))


if __name__ == '__main__':
    main()
