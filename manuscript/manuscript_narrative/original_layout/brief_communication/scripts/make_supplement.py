#!/usr/bin/env python3
"""Supplementary Figures and Tables of the Brief Communication, written for scripts/build_docx.js.

Supplementary Figs. 1-3 and 5-11 are the archive's figures (figures/*.png, copied at 300 dpi to
figures/supplementary/) with their legends (figures/*_legend.md), renumbered in order of citation; Supplementary Fig. 4
is drawn by make_figures.supp_consensus. Supplementary Tables 1-6 are built from data/, numbers.json, the archive's
figure source data, figures/supp_table_design.csv and analysis/integrity_audit/violations.csv.
Writes supplementary/si_content.json, supplementary/Supplementary_Tables.xlsx (one sheet per table) and
supplementary/Supplementary_Data_1.xlsx (the source data of the Supplementary Figures, one sheet per figure).
Usage: python scripts/make_supplement.py
"""
import json
import os
import re

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
BC = os.path.dirname(HERE)
ARCHIVE = os.path.abspath(os.path.join(BC, '..', '..', '..', '..'))
FIG, DATA = os.path.join(ARCHIVE, 'figures'), os.path.join(BC, 'data')
SUPP_FIG = os.path.join(BC, 'figures', 'supplementary')
OUT = os.path.join(BC, 'supplementary')

# Supplementary Figure number -> archive figure, in order of citation in the main text and Methods
FIGURES = [(1, 'fig2'), (2, 'ed_fig2'), (3, 'ed_fig6'), (4, None), (5, 'fig5'), (6, 'ed_fig5'), (7, 'fig3'),
           (8, 'ed_fig3'), (9, 'fig4'), (10, 'ed_fig4'), (11, 'ed_fig7')]
MAIN_MAP = {int(k[3:]): n for n, k in FIGURES if k and k.startswith('fig')}
ED_MAP = {int(k[6:]): n for n, k in FIGURES if k and k.startswith('ed_fig')}
ARCHIVE_FILES = {'`accuracy_sensitivities.csv`': 'accuracy_sensitivities.csv in the run archive',
                 '`figures/annotations/`': 'figures/annotations/ of the run archive',
                 '`udt_methods.csv`': 'figures/udt_methods.csv in the run archive'}
BENCH = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC-derived tasks'}
COND = {'galaxy': 'Galaxy', 'custom_code': 'Custom code', 'open_ended_code': 'Custom code'}
MODELS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro']


def remap(text):
    """Renumber archive figure cross-references to Supplementary Figures (Extended Data first, then main figures)."""
    def figs(nums, table, letters=''):
        ns = [table[int(x)] for x in re.findall(r'\d+', nums)]
        if len(ns) == 1:
            return f'§SF {ns[0]}{letters}'
        return f'§SFS {", ".join(map(str, ns[:-1]))} and {ns[-1]}{letters}'
    text = re.sub(r'Extended Data Figs?\.? (\d+(?:(?:,| and) \d+)*)([a-z](?:,[a-z])*)?',
                  lambda m: figs(m.group(1), ED_MAP, m.group(2) or ''), text)
    text = re.sub(r'\bFigs?\. (\d+(?:(?:,| and) \d+)*)([a-z](?:,[a-z])*)?',
                  lambda m: figs(m.group(1), MAIN_MAP, m.group(2) or ''), text)
    assert not re.search(r'(?<!§SF )\bFig', text.replace('§SFS ', '').replace('§SF ', '')), text
    text = text.replace('§SFS ', 'Supplementary Figs. ').replace('§SF ', 'Supplementary Fig. ')
    text = text.replace('Source Data', 'Supplementary Data 1')
    for k, v in ARCHIVE_FILES.items():
        text = text.replace(k, v)
    assert '`' not in text, text
    return text


def legend(key):
    lines = open(os.path.join(FIG, f'{key}_legend.md')).read().strip().split('\n')
    title = re.match(r'\*\*(?:Extended Data )?Fig\. \d+ \\\| (.*)\*\*$', lines[0]).group(1)
    body = [remap(x.strip()) for x in lines[1:] if x.strip()]
    return title, body


def consensus_legend():
    title = 'Accuracy of single runs, a majority of three and at least one correct run of three, by model.'
    body = [
        'A replicate group is the three replicates of one task, model and condition. For each benchmark, model and '
        'condition: single run (filled circles), the share of runs correct; majority of 3 (triangles), the share of '
        'groups with at least two correct runs, which assumes that correct answers agree; at least 1 of 3 correct '
        '(squares, value printed), the share of groups with a correct run, the accuracy that a validation step that '
        'always selected a correct replicate would reach. Shading spans the three values. For each model, Galaxy '
        '(blue, upper row) and custom code (lower row); "All four models" pools the models.',
        'A run is correct when accepted (BixBench-Verified-50), when it agrees with the answer key (CompBioBench) or at '
        'output agreement ≥ 0.99 (IWC-derived tasks). *n* = 50, 100 and 10 replicate groups per model and condition on '
        'BixBench-Verified-50, CompBioBench and the IWC-derived tasks. None of these strategies was run; the values are '
        'computed from the existing runs (Supplementary Table 1). Source data are in Supplementary Data 1.',
    ]
    return title, body


def pct(x, d=1):
    return f'{100 * x:.{d}f}'


def signed(x, d=1):
    return f'{float(x):.{d}f}'.replace('-', '−')


def ci(v, lo, hi, d=1):
    return f'{signed(v, d)} ({signed(lo, d)} to {signed(hi, d)})'


def table1():
    q = pd.read_csv(os.path.join(DATA, 'replicate_consensus.csv'))
    rows = []
    for r in q.itertuples():
        rows.append(['IWC-derived tasks' if r.benchmark == 'IWC' else r.benchmark, r.track.capitalize(), r.runs,
                     r.replicate_groups,
                     pct(r.single_run_accuracy), pct(r.majority_of_3_accuracy),
                     'n.a.' if pd.isna(r.answer_majority_of_3_accuracy) else pct(r.answer_majority_of_3_accuracy),
                     pct(r.any_of_3_accuracy), pct(r.majority_of_12_accuracy),
                     f'{pct(r.groups_3_of_3)} / {pct(r.groups_2_of_3)} / {pct(r.groups_1_of_3)} / '
                     f'{pct(r.groups_0_of_3)}', r.incorrect_runs, r.incorrect_in_all_wrong_groups])
    return dict(
        n=1, title='Replicate agreement and consensus estimates.',
        legend='A replicate group is the three replicates of one task, model and condition (four models pooled). '
               'Single run, share of runs correct. Majority of 3, share of groups with at least two correct runs '
               '(assumes that correct answers agree). Answer vote of 3, share of groups in which an answer submitted by '
               'at least two replicates, compared as normalized text, was correct (n.a. for the IWC-derived tasks, '
               'whose outputs are files). At least 1 of 3, share of groups with a correct run. Majority of 12, share '
               'of tasks in which more than half of the 12 runs in the condition were correct (ties counted as incorrect). Groups 3/2/1/0 of 3, share of groups with that '
               'many correct runs. Incorrect runs in all-wrong groups, incorrect runs whose two sibling replicates were '
               'also incorrect. A run is correct when accepted, when it agrees with the answer key or at output '
               'agreement ≥ 0.99 (IWC-derived tasks). None of these strategies was run.',
        header=['Benchmark', 'Condition', 'Runs', 'Replicate groups', 'Single run (%)', 'Majority of 3 (%)',
                'Answer vote of 3 (%)', 'At least 1 of 3 (%)', 'Majority of 12 (%)', 'Groups 3/2/1/0 of 3 (%)',
                'Incorrect runs', 'Incorrect runs in all-wrong groups'],
        rows=rows)


def table2():
    t = pd.read_csv(os.path.join(DATA, 'token_ratios_main_runs.csv'))
    order = {m: i for i, m in enumerate(MODELS + ['All models'])}
    bo = {'BixBench-Verified-50': 0, 'CompBioBench': 1, 'IWC': 2}
    t = t.sort_values(['benchmark', 'model'], key=lambda s: s.map(order if s.name == 'model' else bo))
    rows = [['IWC-derived tasks' if r.benchmark == 'IWC' else r.benchmark, r.model,
             f'{r.custom_code_total_tokens / 1e6:,.1f}', f'{r.galaxy_total_tokens / 1e6:,.1f}', f'{r.ratio:.2f}']
            for r in t.itertuples()]
    return dict(
        n=2, title='Tokens used in the main runs, by benchmark and model.',
        legend='Total tokens (input, including cached context, plus output; millions) over all main runs of each '
               'benchmark, model and condition, as published on the results site, and their ratio (Galaxy ÷ custom '
               'code). CompBioBench totals include the 53 Galaxy runs that reviewed reruns replaced; 14 CompBioBench '
               'runs have no usage record. Ratios are not monetary costs.',
        header=['Benchmark', 'Model', 'Custom code (M tokens)', 'Galaxy (M tokens)', 'Galaxy ÷ custom code'],
        rows=rows)


def table3():
    d = pd.read_csv(os.path.join(FIG, 'supp_table_design.csv')).fillna('')
    cols = [f'{"IWC-derived tasks" if r.Benchmark == "IWC" else r.Benchmark}, '
            f'{r.Condition if r.Condition == "Galaxy" else r.Condition.lower()}'
            for r in d.itertuples()]
    fields = [c for c in d.columns if c not in ('Benchmark', 'Condition')]
    rows = [[f] + [str(v) for v in d[f]] for f in fields]
    return dict(
        n=3, title='Design and run selection by benchmark and condition.',
        legend='Archived runs, all runs in the archive; primary runs, the four model configurations compared here; '
               'scored runs, primary runs with a benchmark score. Prompts differ between conditions for every task, '
               'model and replicate (0 identical prompt files of 2,070 pairs), and Galaxy prompts add the execution '
               'policy. Values come from the read-only design extraction of the run archive.',
        header=['Field'] + cols, rows=rows, transposed=True)


def table4():
    f = pd.read_csv(os.path.join(FIG, 'fig2_source_data.csv'))
    a = f[(f.panel == 'a') & f.replicate.isna()].set_index(['benchmark', 'model', 'condition'])
    b = f[(f.panel == 'b') & (f.measure == 'mean_score_difference_points')].set_index(['benchmark', 'model'])
    rows = []
    for bm in ('BixBench50', 'CompBio', 'IWC'):
        for m in MODELS + ['all four']:
            cells = []
            for env in ('custom_code', 'galaxy'):
                if m == 'all four':
                    cells.append('')
                    continue
                x = a.loc[(bm, m, env)]
                cells.append(ci(x.value, x.ci95_low, x.ci95_high))
            d = b.loc[(bm, m)]
            p = f'{d.p:.3f}' + (f' ({d.p_holm:.2f})' if m != 'all four' else '')
            rows.append([BENCH[bm], 'All four (pooled)' if m == 'all four' else m, *cells,
                         ci(d.value, d.ci95_low, d.ci95_high), p])
    return dict(
        n=4, title='Accuracy by benchmark, model and condition.',
        legend='Runs accepted (BixBench-Verified-50; 150 runs per model and condition), runs agreeing with the answer '
               'key (CompBioBench; 300 runs) and mean output agreement × 100 (IWC-derived tasks; 30 runs), with 95% '
               'cluster-bootstrap intervals (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). '
               'Difference, Galaxy minus custom code (percentage points). *P*, paired cluster sign-flip test (200,000 '
               'random sign vectors; exact for the IWC-derived tasks); in parentheses, Holm-adjusted across the 12 '
               'model comparisons. Pooled condition values are given in the main text.',
        header=['Benchmark', 'Model', 'Custom code (95% CI)', 'Galaxy (95% CI)', 'Difference (95% CI)',
                '*P* (Holm-adjusted)'],
        rows=rows)


def table5():
    n = json.load(open(os.path.join(BC, 'numbers.json')))
    st = n['token_stages']['value']
    ch = n['token_change']['value']
    meta = [('July 2026', 'GPT-5.5', 'Round 1: shorter skill text and prompt guidance', '150'),
            ('July 2026', 'GPT-5.5', 'Round 2: one call submits a job, waits and checks the resolved inputs and '
             'parameters; automatic record keeping; live tool search', '150'),
            ('October 2026', 'GPT-5.6 Sol', 'Round 2 (archived main runs)', '150'),
            ('October 2026', 'GPT-5.6 Sol', 'Round 3: replies capped at 4 KiB per output and 8 KiB per reply, '
             'unchanged notices, parameter templates, fewer false parameter warnings, UDT pre-submission checks', '50'),
            ('October 2026', 'GPT-5.6 Sol', 'Round 3 plus instructions to wait 5–30 min before rechecking a job',
             '150')]
    rows = []
    for (when, model, what, runs), s in zip(meta, st):
        r = float(s['ratio_of_tokens_per_50_task_run'])
        ratio = f'{r:.2f}' if pd.isna(s.get('ratio_lo')) else f'{r:.2f} ({s["ratio_lo"]:.2f}–{s["ratio_hi"]:.2f})'
        corr = f'{float(s["galaxy_correct"]):.1f}' if 'galaxy_correct' in s else 'n.a.'
        rows.append([when, model, what, runs, f'{float(s["code_tokens_m"]):.1f}', f'{float(s["galaxy_tokens_m"]):.1f}',
                     ratio, corr])
    j, o = ch['July'], ch['October']
    return dict(
        n=5, title='Interface rounds on BixBench-Verified-50.',
        legend='Tokens (input, including cached context, plus output; millions) per complete 50-task run, averaged over '
               'replicates; ratio, Galaxy ÷ custom code, with 95% cluster-bootstrap intervals; Galaxy correct, share of '
               'Galaxy runs accepted. The July comparison reran both conditions; the October stages share the archived '
               'custom-code runs of GPT-5.6 Sol. Round 3 without longer waits was run once over the 50 tasks (50 runs; '
               f'no interval). Change in Galaxy tokens, paired by task: July, {signed(j["pct"])}% (95% CI '
               f'{signed(j["lo"])} to {signed(j["hi"])}%); October, from the archived runs to round 3 plus longer '
               f'waits, {signed(o["pct"])}% ({signed(o["lo"])} to {signed(o["hi"])}%). The rounds changed several '
               'features at once and the Codex command-line interface changed for round 3 (0.156.0 versus 0.146.0), so '
               'the stages are not a controlled ablation.',
        header=['Comparison', 'Model', 'Interface', 'Galaxy runs', 'Custom code (M tokens)', 'Galaxy (M tokens)',
                'Ratio (95% CI)', 'Galaxy correct (%)'],
        rows=rows)


def table6():
    v = pd.read_csv(os.path.join(ARCHIVE, 'analysis', 'integrity_audit', 'violations.csv'))
    p = v[v.run_set == 'primary']
    key = ['benchmark', 'task', 'model', 'condition', 'replicate']
    order = ['Answer integrity', 'Reuse of other runs', 'Galaxy condition', 'Procedure', 'Sandbox and credentials']
    rows = []
    for g in order:
        sub = p[p.group == g]
        for cat, c in sub.groupby('category', sort=False):
            u = c.drop_duplicates(key)
            verified = (c.verification.str.startswith('verified')).all()
            rows.append([g, cat, c.severity.iloc[0], len(u), (u.benchmark == 'BixBench50').sum(),
                         (u.benchmark == 'CompBio').sum(), (u.benchmark == 'IWC').sum(),
                         (u.condition == 'galaxy').sum(), 'trace read' if verified else 'automatic'])
    sev = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    rows.sort(key=lambda r: (order.index(r[0]), sev[r[2]], -r[3]))
    rows = [[*r[:3], *map(int, r[3:8]), r[8]] for r in rows]
    return dict(
        n=6, title='Integrity audit of the primary runs.',
        legend='Rule breaks and departures from the spirit of the benchmark detected by 19 rule detectors in the 3,816 '
               'archived primary runs (3,804 with a trace; the 24 replacement runs of the mitochondrial genome '
               'assembly task are not archived), as distinct runs per category; a run can appear in several '
               'categories. Verification: trace read, every run in the category checked by reading its trace; '
               'automatic, rule-based detections whose evidence should be read before citing a run. The audit also '
               'scanned 627 superseded, replaced, extra-configuration and token-batch runs, which are not counted '
               'here. Source: '
               'analysis/integrity_audit/ of the run archive (scan of 14 October 2026). See Supplementary Note 1.',
        header=['Group', 'Category', 'Severity', 'Runs', 'BixBench-Verified-50', 'CompBioBench', 'IWC-derived',
                'Galaxy condition', 'Verification'],
        rows=rows)


def source_data(path):
    with pd.ExcelWriter(path) as xw:
        for n, key in FIGURES:
            if key is None:
                d = pd.read_csv(os.path.join(SUPP_FIG, 'SuppFig4_consensus_by_model.csv'))
            else:
                d = pd.read_csv(os.path.join(FIG, f'{key}_source_data.csv'), low_memory=False)
            d.to_excel(xw, sheet_name=f'Supplementary Fig. {n}', index=False)


def main():
    os.makedirs(OUT, exist_ok=True)
    figs = []
    for n, key in FIGURES:
        title, body = consensus_legend() if key is None else legend(key)
        png = [f for f in os.listdir(SUPP_FIG) if f.startswith(f'SuppFig{n}_') and f.endswith('.png')]
        assert len(png) == 1, (n, png)
        figs.append(dict(n=n, archive=key, file=os.path.join('figures', 'supplementary', png[0]), title=title,
                         body=body))
    tables = [table1(), table2(), table3(), table4(), table5(), table6()]
    with pd.ExcelWriter(os.path.join(OUT, 'Supplementary_Tables.xlsx')) as xw:
        for t in tables:
            hdr = [h.replace('*', '') for h in t['header']]
            pd.DataFrame(t['rows'], columns=hdr).to_excel(xw, sheet_name=f'Supplementary Table {t["n"]}',
                                                          index=False, startrow=2)
            ws = xw.sheets[f'Supplementary Table {t["n"]}']
            ws['A1'] = f'Supplementary Table {t["n"]} | {t["title"]}'
            ws['A2'] = t['legend'].replace('*', '')
    source_data(os.path.join(OUT, 'Supplementary_Data_1.xlsx'))
    json.dump(dict(figures=figs, tables=tables), open(os.path.join(OUT, 'si_content.json'), 'w'), indent=1,
              default=int)
    for f in figs:
        print(f'Supplementary Fig. {f["n"]}: {f["title"]}')
    for t in tables:
        print(f'Supplementary Table {t["n"]}: {t["title"]} ({len(t["rows"])} rows)')


if __name__ == '__main__':
    main()
