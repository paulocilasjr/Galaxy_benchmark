#!/usr/bin/env python3
"""Split every figure in result_evaluation/figures/ into one image per panel, for the result-evaluation document.

No figure is cropped from pixels and no estimate is recomputed. Each composite figure is redrawn from the panel data
its script recorded (figures/panel_data/*.json, written by figures/panel_io.py) with the script's own drawing
functions, while the artists each panel adds to the figure are tracked:
- Figs 2-5 and Extended Data Figs 2-5: one panel per drawing call (draw_a, draw_b, ..., ed_census, ...);
- Extended Data Figs 6-7: one function draws all four panels, so a panel starts at each label() call;
- Fig. 1: one canvas laid out in millimetres; a panel runs from its panel_head() to the next one.
Each panel is then saved alone (the other panels hidden) with a tight bounding box. With --check, each redrawn
composite is also compared pixel for pixel with its PNG in result_evaluation/figures/, to show the redraw is that figure.

The scripts' save() functions are replaced while redrawing, so no figure file is rewritten.

Writes result_evaluation/panels/<id>.png (300 dpi) and <id>.pdf (vector), and panels/manifest.csv.
Run from the repository root with the figure environment (manuscript_material/scripts/requirements.txt):
    python result_evaluation/split_panels.py [--check]
"""
import csv
import io
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIG = os.path.join(HERE, 'figures')       # the regenerated figures (site-matched scores; see figures/README.md)
OUT = os.path.join(HERE, 'panels')
sys.path.insert(0, FIG)
sys.dont_write_bytecode = True   # importing the figure scripts must not write into figures/__pycache__

import numpy as np  # noqa: E402
import panel_io  # noqa: E402
from matplotlib.transforms import Bbox  # noqa: E402
from PIL import Image, ImageChops  # noqa: E402

DPI = 300
PAD_IN = 0.04
MM = 1 / 25.4

# script, recorded panel data, recorded figure name, panel id prefix, how panels are delimited
FIGURES = [
    ('make_fig2', 'fig2', 'fig2', 'fig2', 'draw'),
    ('make_fig2', 'fig2', 'ed_fig2', 'ed2', 'draw'),
    ('make_fig3', 'fig3', 'fig3', 'fig3', 'draw'),
    ('make_fig3', 'fig3', 'ed_fig3', 'ed3', 'draw'),
    ('make_fig4', 'fig4', 'fig4', 'fig4', 'draw'),
    ('make_fig4', 'fig4', 'ed_fig4', 'ed4', 'draw'),
    ('make_fig5', 'fig5', 'fig5', 'fig5', 'draw'),
    ('make_fig5', 'fig5', 'ed_fig5', 'ed5', 'draw'),
    ('make_ed_validation', 'ed_validation', 'ed_fig6', 'ed6', 'label'),
    ('make_ed_validation', 'ed_validation', 'ed_fig7', 'ed7', 'label'),
]


def children(fig):
    return [c for c in fig.get_children() if c is not fig.patch]


class Panels:
    """Artists added to a figure between successive panel marks."""

    def __init__(self):
        self.marks = []   # [figure, letter, ids of the figure's artists when the panel started]

    def mark(self, fig, letter):
        self.marks.append((fig, letter, {id(c) for c in children(fig)}))

    def groups(self, fig):
        marks = [(letter, before) for f, letter, before in self.marks if f is fig]
        now = children(fig)
        out = []
        for i, (letter, before) in enumerate(marks):
            after = marks[i + 1][1] if i + 1 < len(marks) else {id(c) for c in now}
            out.append((letter, [c for c in now if id(c) in after and id(c) not in before]))
        return out


def trim(png_bytes):
    """Drop any white margin left around a panel, keeping PAD_IN of white."""
    im = Image.open(io.BytesIO(png_bytes)).convert('RGB')
    box = ImageChops.difference(im, Image.new('RGB', im.size, 'white')).getbbox()
    pad = round(PAD_IN * DPI)
    if box:
        box = (max(box[0] - pad, 0), max(box[1] - pad, 0), min(box[2] + pad, im.width), min(box[3] + pad, im.height))
        im = im.crop(box)
    return im


def write_panel(fig, pid, manifest, figure_name, bbox_inches='tight'):
    fig.savefig(os.path.join(OUT, f'{pid}.pdf'), bbox_inches=bbox_inches, pad_inches=PAD_IN)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=DPI, facecolor='white', bbox_inches=bbox_inches, pad_inches=PAD_IN)
    im = trim(buf.getvalue())
    im.save(os.path.join(OUT, f'{pid}.png'), dpi=(DPI, DPI))
    manifest.append({'panel': pid, 'figure': figure_name, 'png': f'panels/{pid}.png', 'pdf': f'panels/{pid}.pdf',
                     'width_mm': round(im.width / DPI * 25.4, 1), 'height_mm': round(im.height / DPI * 25.4, 1)})
    print(f'  {pid}: {im.width / DPI * 25.4:.0f} x {im.height / DPI * 25.4:.0f} mm')


def compare(fig, name, check):
    """Redraw the whole composite at the published resolution and compare it with figures/<name>.png."""
    if not check:
        return
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=600, facecolor='white')
    new = np.asarray(Image.open(buf).convert('RGB'), dtype=np.int16)
    old = np.asarray(Image.open(os.path.join(FIG, f'{name}.png')).convert('RGB'), dtype=np.int16)
    if new.shape != old.shape:
        print(f'  CHECK {name}: size differs {new.shape} vs {old.shape}')
        return
    diff = np.abs(new - old).max(axis=2)
    print(f'  CHECK {name}: {100 * (diff > 0).mean():.4f}% of pixels differ (max channel difference {diff.max()})')


def split_composite(script, record, name, prefix, mode, manifest, check):
    import importlib
    mod = importlib.import_module(script)
    ns = mod.__dict__
    panels = Panels()
    calls = json.load(open(os.path.join(FIG, 'panel_data', f'{record}.json')))['calls']
    saved = {c['figure'] for c in calls if c['call'] == 'save' and c['args']['name'] == name}
    seen = {}

    if mode == 'draw':   # wrap the top-level drawing calls of this figure: each starts a panel
        for call in {c['call'] for c in calls if c.get('figure') in saved and not c.get('nested')} - {'figure', 'save'}:
            def wrapped(*args, __fn=ns[call], **kwargs):
                fig = kwargs.get('fig', args[0] if args else None)
                seen[fig] = seen.get(fig, 0) + 1
                panels.mark(fig, 'abcdefgh'[seen[fig] - 1])
                return __fn(*args, **kwargs)
            ns[call] = wrapped
    label = ns['label']

    def label_hook(fig, x, y, letter, title, H, note=None):
        if mode == 'label':
            panels.mark(fig, letter)
        else:   # the panel letter the script draws must match the drawing-call order
            assert panels.marks[-1][1] == letter or letter not in 'abcdefgh', (name, letter, panels.marks[-1][1])
        return label(fig, x, y, letter, title, H, note)
    ns['label'] = label_hook

    def capture(fig, name, title, __target=name):   # replaces the script's save(): nothing is written to figures/
        if name != __target:
            return
        mod.style.enforce_min_font(fig)
        compare(fig, name, check)
        groups = panels.groups(fig)
        everything = children(fig)
        shown = {id(a): a.get_visible() for a in everything}
        for letter, artists in groups:
            keep = {id(a) for a in artists}
            for a in everything:
                a.set_visible(shown[id(a)] and id(a) in keep)
            write_panel(fig, f'{prefix}{letter}', manifest, name)
        for a in everything:
            a.set_visible(shown[id(a)])
        mod.plt.close(fig)
    ns['save'] = capture
    panel_io.replay(os.path.join(FIG, 'panel_data', f'{record}.json'), ns, names=[name])
    ns['label'] = label


def split_fig1(manifest, check):
    """Fig. 1 is one canvas in mm (y down); each panel runs from its panel_head() to the next one."""
    import make_fig1_a as mod
    heads = []
    head = mod.panel_head

    def head_hook(cv, y, letter, title):
        heads.append((letter, y))
        return head(cv, y, letter, title)
    mod.panel_head = head_hook
    recorded = json.load(open(os.path.join(FIG, 'panel_data', 'fig1_a.json')))['facts']
    mod.facts = lambda: dict(recorded)   # the counts the published figure was drawn with

    def capture(cv, h):
        cv.fig.set_size_inches(mod.W * MM, h * MM)
        cv.ax.set_ylim(h, 0)
        mod.style.enforce_min_font(cv.fig)
        compare(cv.fig, 'fig1_a', check)
        for i, (letter, y0) in enumerate(heads):
            y1 = heads[i + 1][1] - 0.5 if i + 1 < len(heads) else h
            box = Bbox.from_extents(0, (h - y1) * MM, mod.W * MM, (h - y0) * MM)
            write_panel(cv.fig, f'fig1{letter}', manifest, 'fig1_a', bbox_inches=box)
        mod.plt.close(cv.fig)
    mod.Canvas.save = capture
    mod.main()


def main():
    check = '--check' in sys.argv
    os.makedirs(OUT, exist_ok=True)
    manifest = []
    print('fig1_a')
    split_fig1(manifest, check)
    for script, record, name, prefix, mode in FIGURES:
        print(name)
        split_composite(script, record, name, prefix, mode, manifest, check)
    with open(os.path.join(OUT, 'manifest.csv'), 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(manifest[0]))
        w.writeheader()
        w.writerows(manifest)
    print(f'{len(manifest)} panels written to {OUT}')


if __name__ == '__main__':
    main()
