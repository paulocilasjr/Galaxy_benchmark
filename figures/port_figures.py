"""Write the manuscript repository's figure scripts from this archive's figure scripts (drawing code only).

For each figure, the generated figures/<folder>/make_figure.py in agent-galaxy-benchmark-manuscript holds the archive
script's drawing code (the functions that draw, and the helpers, constants and imports they use, copied unchanged)
and replays the panel data the archive script recorded (figures/panel_data/<script>.json, see panel_io.py). The
manuscript's analysis/export_galaxy_benchmark_tables.py copies that panel data and each figure's source data into its
data/figure_panels/. No estimate is recomputed in the manuscript repository.

Usage: python figures/port_figures.py <manuscript repository> <archive commit> [figure ...]
"""
import ast
import builtins
import os
import shutil
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ARCHIVE = 'paulocilasjr/Galaxy_benchmark'
# archive script, recorded figure name, manuscript folder, title, kind
FIGURES = [
    ('make_fig1_a.py', 'fig1_a', 'fig1_benchmark_overview', 'Study design and isolated execution pipeline', 'main'),
    ('make_fig2.py', 'fig2', 'fig2_performance',
     'Agents show similar observed benchmark performance in Galaxy and custom code', 'main'),
    ('make_fig3.py', 'fig3', 'fig3_structured_environment', 'Galaxy provides a structured environment for agent analyses',
     'main'),
    ('make_fig4.py', 'fig4', 'fig4_solution_variability',
     'Answer agreement and tool use vary across model configurations', 'main'),
    ('make_fig5.py', 'fig5', 'fig5_token_cost',
     'Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks', 'main'),
    ('make_fig2.py', 'ed_fig2', 'ed_fig2_failure_causes', 'Failure causes and sensitivity of the accuracy comparison',
     'supplementary'),
    ('make_fig3.py', 'ed_fig3', 'ed_fig3_execution_errors', 'Task status, execution errors and final correctness',
     'supplementary'),
    ('make_fig4.py', 'ed_fig4', 'ed_fig4_tools_and_answers',
     'Tool inventory, route similarity, answer matching, difficulty and UDT methods', 'supplementary'),
    ('make_fig5.py', 'ed_fig5', 'ed_fig5_token_use', 'Token use by model, outcome and action count', 'supplementary'),
    ('make_ed_validation.py', 'ed_fig6', 'ed_fig6_audit_checks',
     'Independent checks of the audits and of benchmark integrity', 'supplementary'),
    ('make_ed_validation.py', 'ed_fig7', 'ed_fig7_verification_recovery', 'Verification, recovery and selected cases',
     'supplementary'),
]
ARCHIVE_MODULES = {'style', 'panel_io', 'make_ed_validation', 'narrative_common', 'fig_on_demand', 'build', 'collect'}
PROVIDED = {'OUT', 'rng', 'style', 'plt', 'panel_io', 'HERE', 'DATA'}   # defined by the generated header


def names_in(node):
    out = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Name):
            out.add(n.id)
        elif isinstance(n, ast.Attribute):
            base = n
            while isinstance(base, ast.Attribute):
                base = base.value
            if isinstance(base, ast.Name):
                out.add(base.id)
    return out


def targets(stmt):
    out = set()
    nodes = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
    for t in nodes:
        for n in ast.walk(t):
            if isinstance(n, ast.Name):
                out.add(n.id)
    return out


def extract(path, roots):
    """Source of the top-level definitions needed by the functions in roots, in file order."""
    src = open(path).read()
    tree = ast.parse(src)
    defs, assigns, imports, other = {}, [], [], []
    for stmt in tree.body:
        if isinstance(stmt, (ast.FunctionDef, ast.ClassDef)):
            defs[stmt.name] = stmt
        elif isinstance(stmt, (ast.Assign, ast.AnnAssign)) and all(isinstance(t, (ast.Name, ast.Tuple)) for t in
                                                                   (stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target])):
            assigns.append(stmt)
        elif isinstance(stmt, (ast.Import, ast.ImportFrom)):
            imports.append(stmt)
        else:
            other.append(stmt)
    keep, todo = set(), list(roots)
    used = set()
    while todo:
        name = todo.pop()
        if name in keep:
            continue
        nodes = [defs[name]] if name in defs else [a for a in assigns if name in targets(a)]
        if not nodes:
            continue
        keep.add(name)
        for node in nodes:
            refs = names_in(node) - {name}
            used |= refs
            todo += [r for r in refs if r not in keep]
    # module-level statements that configure the style (rcParams, style.ENV_LABEL = ...)
    style_stmts = [s for s in other if isinstance(s, (ast.Expr, ast.Assign)) and names_in(s) & {'plt', 'style'}
                   and not names_in(s) & {'sys', 'ROOT'}]
    for s in style_stmts:
        used |= names_in(s)
    lines = src.splitlines()
    seg = lambda node: '\n'.join(lines[node.lineno - 1 - len(getattr(node, 'decorator_list', [])):node.end_lineno])
    body = [n for n in tree.body if (n in style_stmts) or
            (isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in keep) or
            (n in assigns and targets(n) & keep and not targets(n) & PROVIDED)]
    imps = []
    for imp in imports:
        mod = imp.module if isinstance(imp, ast.ImportFrom) else None
        aliases = [a for a in imp.names if (a.asname or a.name).split('.')[0] in used]
        if not aliases or (mod or aliases[0].name).split('.')[0] in ARCHIVE_MODULES:
            continue
        if isinstance(imp, ast.ImportFrom):
            imps.append(f'from {mod} import ' + ', '.join(a.name + (f' as {a.asname}' if a.asname else '') for a in aliases))
        else:
            imps.append('\n'.join(f'import {a.name}' + (f' as {a.asname}' if a.asname else '') for a in aliases))
    top_level = set(defs) | {t for a in assigns for t in targets(a)}
    missing = sorted((used & top_level) - keep - PROVIDED)
    return imps, [seg(n) for n in body], missing


HEADER = '''#!/usr/bin/env python3
"""{label}: {title}.

Drawing code copied unchanged from the run archive, {archive}@{commit}:figures/{script}; the panel data are the
values that script computed and passed to its drawing functions (data/figure_panels/{record}.json, written by the
archive's figures/panel_io.py and copied by analysis/export_galaxy_benchmark_tables.py). Nothing is recomputed here:
every number traces to the archive script at that commit. Writes, next to this script, {folder}.pdf, .png (600 dpi)
and .svg, and source_data.csv (the archive's {record}_source_data.csv).

Regenerate with: python figures/{folder}/make_figure.py
"""
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / 'data'
sys.path.insert(0, str(HERE.parent))
import figure_style as style  # noqa: E402  (the archive's style module; sets rcParams on import)
import panel_io  # noqa: E402
plt = style.plt
OUT = str(HERE)
'''

MAIN = '''

rng = np.random.default_rng(0)   # the archive script's jitter generator; replay restores its state before each call


def main():
    panel_io.replay(DATA / 'figure_panels' / '{script_record}.json', globals(), names=['{record}'])
    for ext in ('pdf', 'png', 'svg'):
        os.replace(HERE / f'{record}.{{ext}}', HERE / f'{folder}.{{ext}}')
    shutil.copyfile(DATA / 'figure_panels' / '{record}_source_data.csv', HERE / 'source_data.csv')


if __name__ == '__main__':
    main()
'''

FIG1_MAIN_NOTE = 'counts from data/figure_panels/fig1_a.json'


def port(target, commit, only=None):
    for script, record, folder, title, kind in FIGURES:
        if only and record not in only:
            continue
        path = os.path.join(HERE, script)
        script_record = {'make_ed_validation.py': 'ed_validation'}.get(script, record.replace('ed_', '') if
                                                                         script != 'make_fig1_a.py' else 'fig1_a')
        label = (f'Extended Data Fig. {record[6:]}' if record.startswith('ed_') else f'Figure {record[3]}')
        out_dir = os.path.join(target, 'figures', folder)
        os.makedirs(out_dir, exist_ok=True)
        head = HEADER.format(label=label, title=title, archive=ARCHIVE, commit=commit, script=script, record=record,
                             folder=folder)
        if script == 'make_fig1_a.py':
            src = open(path).read()
            tree = ast.parse(src)
            roots = [n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))
                     and n.name not in ('facts', 'main')]
            imps, body, missing = extract(path, roots + ['W', 'CONFIGS', 'N_COND', 'N_REP'])
            main_src = '\n'.join(src.splitlines()[[n for n in tree.body if getattr(n, 'name', '') == 'main'][0].lineno - 1:
                                                  [n for n in tree.body if getattr(n, 'name', '') == 'main'][0].end_lineno])
            start = main_src.index("    if os.environ.get('PANEL_DATA')")
            end = main_src.index('\n    n_tasks')
            main_src = main_src[:start].replace('    f = facts()\n', f"    f = json.load(open(DATA / 'figure_panels' / 'fig1_a.json'))['facts']   # {FIG1_MAIN_NOTE}\n") + main_src[end + 1:]
            tail = ('\n\n' + main_src + "\n    for ext in ('pdf', 'png', 'svg'):\n"
                    f"        os.replace(HERE / f'fig1_a.{{ext}}', HERE / f'{folder}.{{ext}}')\n"
                    "    import csv as _csv\n"
                    "    with open(HERE / 'source_data.csv', 'w', newline='') as fh:\n"
                    "        w = _csv.writer(fh)\n"
                    "        w.writerow(['quantity', 'value', 'source'])\n"
                    "        for k, v in f.items():\n"
                    f"            w.writerow([k, v, 'archive figures/make_fig1_a.py facts() at {commit}'])\n"
                    "\n\nif __name__ == '__main__':\n    main()\n")
            imps = sorted(set(imps) | {'import json', 'import numpy as np'})
        else:
            import json
            calls = json.load(open(os.path.join(HERE, 'panel_data', f'{script_record}.json')))['calls']
            saved = {c['figure'] for c in calls if c['call'] == 'save' and c['args']['name'] == record}
            roots = sorted({c['call'] for c in calls if c.get('figure') in saved and not c.get('nested')
                            and c['call'] != 'figure'} | {'save'})
            imps, body, missing = extract(path, roots)
            imps = sorted(set(imps) | {'import numpy as np'})
            tail = MAIN.format(script_record=script_record, record=record, folder=folder)
        if missing:
            print(f'  {folder}: names not defined after extraction: {missing}')
        code = head + '\n'.join(imps) + '\n\n' + '\n\n\n'.join(body) + tail
        compile(code, folder, 'exec')
        open(os.path.join(out_dir, 'make_figure.py'), 'w').write(code)
        print(f'{folder}: {len(body)} definitions from {script}')
    shutil.copyfile(os.path.join(ROOT, 'manuscript_material', 'scripts', 'style.py'),
                    os.path.join(target, 'figures', 'figure_style.py'))
    shutil.copyfile(os.path.join(HERE, 'panel_io.py'), os.path.join(target, 'figures', 'panel_io.py'))


if __name__ == '__main__':
    port(sys.argv[1], sys.argv[2], set(sys.argv[3:]) or None)
