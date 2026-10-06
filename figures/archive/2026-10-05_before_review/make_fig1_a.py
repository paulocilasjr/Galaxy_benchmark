"""Fig. 1a,b schematic: study design overview (a) and per-run execution pipeline (b).

Pictogram version: text is reduced to names, counts and short labels; definitions live in the legend
(figures/fig1_a_legend.md). Writes figures/fig1_a.svg (editable text, for Inkscape), fig1_a.pdf (vector,
TrueType) and fig1_a.png (600 dpi, RGB) at 180 mm width with the shared Nature Portfolio style in
manuscript_material/scripts/style.py. Task counts are read from the repository.
"""
import csv
import glob
import io
import os
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(ROOT, 'manuscript_material', 'scripts'))
import style  # noqa: E402  (sets rcParams on import)
style.ENV_LABEL = {'open_ended_code': 'Custom code', 'galaxy': 'Galaxy'}   # the paper's name for the condition
from style import plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import (Circle, Ellipse, FancyArrow, FancyArrowPatch, FancyBboxPatch, Polygon,  # noqa: E402
                                Rectangle)
from PIL import Image  # noqa: E402

OUT = os.path.join(ROOT, 'figures')
W = 180.0                 # mm; Nature Methods double-column width
PT = 25.4 / 72            # mm per point
INK, INK2 = style.INK, style.INK2
FILL, EDGE = style.LIGHT, '#c9c8c3'
G, C = style.GALAXY, style.CODE
G_TINT = style.ENV_TINT['galaxy']
G_LIGHT = '#e6f0f8'
IC, LW = '#4a4a4a', 0.6   # pictogram stroke colour and width (pt)
CHEVRON = '#c4c4c4'
LAB = 5.0                 # pictogram labels
NAME = 6.0

CONFIGS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro']
N_COND, N_REP = 2, 3


def facts():
    cb = list(csv.DictReader(open(os.path.join(ROOT, 'experiments/CompBioBench/source_compbiobench.v1.tsv')),
                             delimiter='\t'))
    bix = glob.glob(os.path.join(ROOT, 'experiments/BixBench/task_*.json'))
    iwc = glob.glob(os.path.join(ROOT, 'IWC/analysis/wf_*'))
    return dict(bix=len(bix), cb=len(cb), iwc=len(iwc))


# ---------------------------------------------------------------- canvas and primitives (mm, y downwards)
class Canvas:
    def __init__(self):
        # measure on a 1200-dpi canvas: at low dpi, hinted glyph advances round to whole pixels
        self.fig = plt.figure(figsize=(W / 25.4, 200 / 25.4), dpi=1200)
        self.ax = self.fig.add_axes([0, 0, 1, 1])
        self.ax.set_xlim(0, W)
        self.ax.set_ylim(200, 0)
        self.ax.axis('off')
        self.r = self.fig.canvas.get_renderer()

    def width(self, s, size, weight='normal'):
        prop = FontProperties(family='Arial', size=size, weight=weight)
        return self.r.get_text_width_height_descent(s, prop, ismath=False)[0] / self.fig.dpi * 25.4

    def text(self, x, y, s, size=LAB, weight='normal', color=INK, ha='left'):
        """y is the top of the line box."""
        self.ax.text(x, y + 0.80 * size * PT, s, fontsize=size, fontweight=weight, color=color, ha=ha,
                     va='baseline', zorder=6)

    def ctext(self, x, y, s, size=LAB, weight='normal', color=INK):
        """Centred on (x, y)."""
        self.ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha='center', va='center_baseline',
                     zorder=6)

    def poly(self, pts, fc='none', ec=IC, lw=LW, closed=True, z=3, ls='-'):
        self.ax.add_patch(Polygon(pts, closed=closed, fc=fc, ec=ec, lw=lw, zorder=z, joinstyle='round',
                                  capstyle='round', ls=ls))

    def line(self, pts, color=IC, lw=LW, z=4, ls='-'):
        xs, ys = zip(*pts)
        self.ax.plot(xs, ys, color=color, lw=lw, zorder=z, solid_capstyle='round', ls=ls,
                     dash_capstyle='round')

    def rrect(self, x, y, w, h, r=0.5, fc='white', ec=IC, lw=LW, z=3, ls='-'):
        self.ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}', fc=fc, ec=ec,
                                         lw=lw, zorder=z, ls=ls))

    def rect(self, x, y, w, h, fc='white', ec='none', lw=LW, z=3):
        self.ax.add_patch(Rectangle((x, y), w, h, fc=fc, ec=ec, lw=lw, zorder=z))

    def circ(self, cx, cy, r, fc='white', ec=IC, lw=LW, z=3):
        self.ax.add_patch(Circle((cx, cy), r, fc=fc, ec=ec, lw=lw, zorder=z))

    def ell(self, cx, cy, w, h, fc='white', ec=IC, lw=LW, z=3):
        self.ax.add_patch(Ellipse((cx, cy), w, h, fc=fc, ec=ec, lw=lw, zorder=z))

    def arrow(self, p0, p1, color=IC, lw=0.7, rad=0.0, ms=5, z=4, ls='-'):
        self.ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle='-|>', mutation_scale=ms, lw=lw, color=color,
                                          connectionstyle=f'arc3,rad={rad}', shrinkA=0, shrinkB=0, zorder=z,
                                          linestyle=ls))

    def arc_arrow(self, cx, cy, r, th0, th1, color=IC, lw=0.7, ms=4.5, z=4):
        th = np.radians(np.linspace(th0, th1, 60))
        pts = list(zip(cx + r * np.cos(th), cy - r * np.sin(th)))
        self.line(pts[:-3], color=color, lw=lw, z=z)
        self.arrow(pts[-4], pts[-1], color=color, lw=lw, ms=ms, z=z)

    def chevron(self, x0, x1, y):
        self.ax.add_patch(FancyArrow(x0, y, x1 - x0, 0, width=1.5, head_width=3.6, head_length=2.2,
                                     length_includes_head=True, fc=CHEVRON, ec='none', zorder=2))

    def marker(self, x, y, env, ms=3.7):
        self.ax.plot([x], [y], marker=style.ENV_MARKER[env], ms=ms, mfc=style.ENV_COLOR[env], mec='white',
                     mew=0.4, ls='', zorder=5)

    def save(self, h):
        self.fig.set_size_inches(W / 25.4, h / 25.4)
        self.ax.set_ylim(h, 0)
        style.enforce_min_font(self.fig)
        title = 'Fig. 1a,b | Study design and isolated execution pipeline'
        self.fig.savefig(os.path.join(OUT, 'fig1_a.svg'), metadata={'Title': title})
        self.fig.savefig(os.path.join(OUT, 'fig1_a.pdf'), metadata={'Title': title})
        buf = io.BytesIO()  # Nature artwork: RGB without alpha
        self.fig.savefig(buf, format='png', dpi=600, facecolor='white')
        Image.open(buf).convert('RGB').save(os.path.join(OUT, 'fig1_a.png'), dpi=(600, 600))


# ---------------------------------------------------------------- pictograms (centred on cx, cy)
def doc(cv, cx, cy, w=4.0, h=5.2, ec=IC, fc='white', mark=None, lines=3, z=3):
    x0, y0, f = cx - w / 2, cy - h / 2, min(w, h) * 0.32
    cv.poly([(x0, y0), (x0 + w - f, y0), (x0 + w, y0 + f), (x0 + w, y0 + h), (x0, y0 + h)], fc=fc, ec=ec, z=z)
    cv.poly([(x0 + w - f, y0), (x0 + w - f, y0 + f), (x0 + w, y0 + f)], ec=ec, closed=False, z=z)
    if mark:
        cv.ctext(cx, cy + 0.45, mark, 6.5, 'bold', ec)
    else:
        for i in range(lines):
            yy = y0 + h * (0.38 + 0.19 * i)
            cv.line([(x0 + w * 0.2, yy), (x0 + w * (0.8 if i < lines - 1 else 0.55), yy)], color=ec, lw=0.45, z=z + 1)


def files(cv, cx, cy, w=3.4, h=4.4, ec=IC, n=3):
    for k in reversed(range(n)):
        doc(cv, cx - 0.9 + k * 0.9, cy - 0.5 + k * 0.5, w, h, ec=ec, lines=2, z=3 + (n - k))


def table(cv, cx, cy, w=4.6, h=3.6, ec=IC):
    x0, y0 = cx - w / 2, cy - h / 2
    cv.rrect(x0, y0, w, h, r=0.3, ec=ec, z=5)
    cv.rect(x0, y0, w, h / 3.5, fc=ec, z=5)
    for i in (1, 2):
        cv.line([(x0, y0 + h * (0.29 + 0.24 * i)), (x0 + w, y0 + h * (0.29 + 0.24 * i))], color=ec, lw=0.4, z=6)
    cv.line([(x0 + w * 0.4, y0), (x0 + w * 0.4, y0 + h)], color=ec, lw=0.4, z=6)


def dna(cv, cx, cy, w=4.6, h=9.0):
    t = np.linspace(0, 2.4 * np.pi, 90)
    y = cy - h / 2 + t / t[-1] * h
    for k in np.linspace(0.35, t[-1] - 0.35, 8):
        yy = cy - h / 2 + k / t[-1] * h
        cv.line([(cx + w / 2 * np.sin(k), yy), (cx - w / 2 * np.sin(k), yy)], color=EDGE, lw=0.7, z=3)
    cv.line(list(zip(cx + w / 2 * np.sin(t), y)), color=IC, lw=0.9)
    cv.line(list(zip(cx - w / 2 * np.sin(t), y)), color=IC, lw=0.9)


def workflow(cv, cx, cy, s=8.5, ec=IC, fc='white'):
    nodes = [(-0.3, -0.36), (0.3, -0.36), (0.0, 0.0), (-0.3, 0.36), (0.3, 0.36)]
    for a, b in [(0, 2), (1, 2), (2, 3), (2, 4)]:
        cv.line([(cx + nodes[a][0] * s, cy + nodes[a][1] * s), (cx + nodes[b][0] * s, cy + nodes[b][1] * s)],
                color=ec, lw=0.6, z=3)
    for i, (nx, ny) in enumerate(nodes):
        cv.rrect(cx + nx * s - 1.25, cy + ny * s - 0.8, 2.5, 1.6, r=0.35, fc=ec if i == 2 else fc, ec=ec, z=4)


def terminal(cv, cx, cy, w=11.0, h=7.6, ec=IC, prompt_color=INK):
    x0, y0 = cx - w / 2, cy - h / 2
    cv.rrect(x0, y0, w, h, r=0.6, fc='white', ec=ec)
    cv.rrect(x0, y0, w, 1.6, r=0.6, fc=ec, ec=ec, z=3)
    cv.rect(x0, y0 + 0.9, w, 0.75, fc=ec, z=3)
    for k in range(3):
        cv.circ(x0 + 0.9 + k * 0.85, y0 + 0.8, 0.22, fc='white', ec='none', z=4)
    cv.text(x0 + 0.9, y0 + 2.3, '>_', 6.5, 'bold', prompt_color)
    for i, frac in enumerate((0.55, 0.75, 0.4)):
        yy = y0 + 5.1 + i * 0.95
        if yy < y0 + h - 0.6:
            cv.line([(x0 + 1.0, yy), (x0 + 1.0 + (w - 2.0) * frac, yy)], color=EDGE, lw=0.55)


def galaxy_window(cv, cx, cy, w=14.0, h=8.6, title='usegalaxy.org', udt=True, tiles=(3, 2)):
    x0, y0 = cx - w / 2, cy - h / 2
    cv.rrect(x0, y0, w, h, r=0.6, fc='white', ec=G, lw=0.75)
    cv.rrect(x0, y0, w, 1.9, r=0.6, fc=G, ec=G, z=3)
    cv.rect(x0, y0 + 1.1, w, 0.8, fc=G, z=3)
    if title:
        cv.ctext(cx, y0 + 1.05, title, LAB, 'bold', 'white')
    nx, ny = tiles
    gx = 0.6
    tw, th = (w - 1.4 - (nx - 1) * gx) / nx, (h - 2.9 - (ny - 1) * gx) / ny
    for j in range(ny):
        for i in range(nx):
            tx, ty = x0 + 0.7 + i * (tw + gx), y0 + 2.5 + j * (th + gx)
            if udt and i == nx - 1 and j == ny - 1:
                cv.rrect(tx, ty, tw, th, r=0.3, fc='white', ec=G, lw=0.6, ls=(0, (1.6, 0.9)), z=4)
                cv.ctext(tx + tw / 2, ty + th / 2, 'UDT', LAB, 'bold', INK)
            else:
                cv.rrect(tx, ty, tw, th, r=0.3, fc=G_TINT, ec='none', z=4)
                cv.line([(tx + tw * 0.25, ty + th / 2), (tx + tw * 0.75, ty + th / 2)], color=G, lw=0.6, z=5)


def agent(cv, cx, cy, s=6.0, ec=IC):
    hw, hh = s / 2, s * 0.36
    cv.line([(cx, cy - hh), (cx, cy - hh - s * 0.18)], color=ec, lw=0.6)
    cv.circ(cx, cy - hh - s * 0.22, s * 0.065, fc=ec, ec=ec, z=4)
    cv.rect(cx - hw - s * 0.08, cy - s * 0.12, s * 0.08, s * 0.24, fc=ec, z=3)
    cv.rect(cx + hw, cy - s * 0.12, s * 0.08, s * 0.24, fc=ec, z=3)
    cv.rrect(cx - hw, cy - hh, 2 * hw, 2 * hh, r=s * 0.12, fc='white', ec=ec, lw=0.7, z=4)
    for sx in (-1, 1):
        cv.circ(cx + sx * s * 0.19, cy - s * 0.05, s * 0.075, fc=ec, ec=ec, z=5)
    cv.line([(cx - s * 0.14, cy + s * 0.17), (cx + s * 0.14, cy + s * 0.17)], color=ec, lw=0.6, z=5)


def container(cv, x, y, w, h, d=2.6, ec=IC):
    cv.poly([(x, y + d), (x + d, y), (x + w, y), (x + w - d, y + d)], fc='#e9e8e4', ec=ec, z=2)
    cv.poly([(x + w - d, y + d), (x + w, y), (x + w, y + h - d), (x + w - d, y + h)], fc='#dcdbd6', ec=ec, z=2)
    cv.poly([(x, y + d), (x + w - d, y + d), (x + w - d, y + h), (x, y + h)], fc='#f7f7f5', ec=ec, z=2)


def lock(cv, cx, cy, s=3.0, opened=False, ec=IC):
    bw, bh, r = s, s * 0.78, s * 0.3
    ay = cy - bh * 0.1
    dx, lift = (s * 0.5, s * 0.3) if opened else (0.0, 0.0)
    th = np.radians(np.linspace(0, 180, 40))
    arc = list(zip(cx + dx + r * np.cos(th), ay - s * 0.3 - lift - r * np.sin(th)))
    pts = [(cx + dx + r, ay - lift)] + arc + [(cx + dx - r, ay - lift)]
    cv.line(pts, color=ec, lw=0.8, z=6)
    cv.rrect(cx - bw / 2, ay, bw, bh, r=0.35, fc=ec, ec=ec, z=7)
    cv.circ(cx, ay + bh * 0.45, s * 0.09, fc='white', ec='none', z=8)


def clock(cv, cx, cy, r=2.2, ec=IC):
    cv.circ(cx, cy, r, fc='white', ec=ec, lw=0.7)
    for k in range(12):
        a = np.radians(k * 30)
        cv.line([(cx + 0.78 * r * np.cos(a), cy - 0.78 * r * np.sin(a)),
                 (cx + 0.92 * r * np.cos(a), cy - 0.92 * r * np.sin(a))], color=ec, lw=0.4)
    cv.line([(cx, cy), (cx, cy - 0.62 * r)], color=ec, lw=0.7)
    cv.line([(cx, cy), (cx + 0.48 * r, cy + 0.15 * r)], color=ec, lw=0.7)


def target(cv, cx, cy, r=3.0, ec=IC):
    for k, f in enumerate((1.0, 0.66, 0.33)):
        cv.circ(cx, cy, r * f, fc='white' if k % 2 == 0 else '#dcdbd6', ec=ec, lw=0.6, z=3 + k)
    cv.circ(cx, cy, r * 0.1, fc=ec, ec=ec, z=6)


def verdict(cv, cx, cy, ok=True, r=1.15):
    if ok:
        cv.circ(cx, cy, r, fc=INK, ec=INK, z=4)
        cv.line([(cx - r * 0.45, cy + r * 0.02), (cx - r * 0.1, cy + r * 0.38), (cx + r * 0.5, cy - r * 0.38)],
                color='white', lw=0.75, z=5)
    else:
        cv.circ(cx, cy, r, fc='white', ec=INK2, lw=0.6, z=4)
        k = r * 0.38
        cv.line([(cx - k, cy - k), (cx + k, cy + k)], color=INK2, lw=0.7, z=5)
        cv.line([(cx - k, cy + k), (cx + k, cy - k)], color=INK2, lw=0.7, z=5)


def coins(cv, cx, cy, w=4.6, n=3, ec=IC):
    eh, step = w * 0.36, w * 0.24
    for i in range(n):
        yy = cy + (n - 1) / 2 * step - i * step
        cv.rect(cx - w / 2, yy, w, step, fc='white', z=3 + 2 * i)
        cv.line([(cx - w / 2, yy), (cx - w / 2, yy + step)], color=ec, lw=0.6, z=3 + 2 * i)
        cv.line([(cx + w / 2, yy), (cx + w / 2, yy + step)], color=ec, lw=0.6, z=3 + 2 * i)
        cv.ell(cx, yy + step, w, eh, fc='white', ec=ec, z=2 + 2 * i)
        cv.ell(cx, yy, w, eh, fc='white', ec=ec, z=4 + 2 * i)


def bars(cv, x, y, w=5.4, h=4.4, color=G, fail=INK):
    vals, fails = (1.0, 0.72, 0.5, 0.3), (0.12, 0.22, 0.08, 0.1)
    bh = h / len(vals) * 0.7
    for i, (v, f) in enumerate(zip(vals, fails)):
        yy = y + i * h / len(vals)
        cv.rect(x, yy, w * v, bh, fc=color, z=3)
        cv.rect(x + w * (v - f), yy, w * f, bh, fc=fail, z=4)


def magnifier(cv, cx, cy, r=2.0, ec=IC):
    cv.line([(cx + r * 0.7, cy + r * 0.7), (cx + r * 1.55, cy + r * 1.55)], color=ec, lw=1.4)
    cv.circ(cx, cy, r, fc='white', ec=ec, lw=0.8, z=4)


def stacked(cv, x, y, w=10.0, h=1.6):
    """Failure-cause glyph: one bar split into cause groups (proportions illustrative)."""
    parts = ((0.55, style.NEUTRAL_DARK), (0.3, style.OI_GREEN), (0.1, style.OI_PURPLE), (0.05, style.NEUTRAL_LIGHT))
    xx = x
    for f, col in parts:
        cv.rect(xx, y, w * f, h, fc=col, z=4)
        xx += w * f


def history(cv, cx, cy, w=5.4, h=7.2, color=G):
    x0, y0 = cx - w / 2, cy - h / 2
    cv.rrect(x0, y0, w, h, r=0.5, fc='white', ec=color, lw=0.7)
    cv.rrect(x0, y0, w, 1.5, r=0.5, fc=color, ec=color, z=3)
    cv.rect(x0, y0 + 0.8, w, 0.7, fc=color, z=3)
    for i in range(3):
        ty = y0 + 2.1 + i * 1.55
        if ty + 1.2 > y0 + h - 0.3:
            break
        cv.rrect(x0 + 0.55, ty, w - 1.1, 1.2, r=0.25, fc=G_TINT, ec='none', z=4)
        cv.circ(x0 + 1.25, ty + 0.6, 0.3, fc=color, ec='none', z=5)


def provenance(cv, x, y, w=24.0, color=G):
    """dataset -> tool -> dataset -> tool -> dataset."""
    n = 5
    xs = [x + w * i / (n - 1) for i in range(n)]
    for a, b in zip(xs[:-1], xs[1:]):
        cv.arrow((a + 1.1, y), (b - 1.2, y), color=color, lw=0.6, ms=3.5)
    for i, xx in enumerate(xs):
        if i % 2 == 0:
            cv.circ(xx, y, 1.0, fc=G_TINT, ec=color, lw=0.7, z=5)
        else:
            cv.rrect(xx - 1.05, y - 1.05, 2.1, 2.1, r=0.3, fc=color, ec=color, z=5)


def bubble(cv, cx, cy, w=5.4, h=3.8, ec=IC, mark='A'):
    x0, y0 = cx - w / 2, cy - h / 2
    cv.poly([(x0 + w * 0.22, y0 + h - 0.2), (x0 + w * 0.18, y0 + h + 1.2), (x0 + w * 0.45, y0 + h - 0.2)],
            fc='white', ec=ec, z=3)
    cv.rrect(x0, y0, w, h, r=0.9, fc='white', ec=ec, z=4)
    cv.rect(x0 + w * 0.25, y0 + h - 0.45, w * 0.17, 0.5, fc='white', z=5)
    cv.ctext(cx, cy + 0.1, mark, 6.0, 'bold', INK)


def trace(cv, cx, cy, w=4.4, h=5.6, ec=IC):
    x0, y0 = cx - w / 2, cy - h / 2
    cv.rrect(x0, y0, w, h, r=0.4, fc='white', ec=ec)
    for i, (ind, frac) in enumerate(((0, 0.7), (0.15, 0.5), (0, 0.8), (0.15, 0.45), (0, 0.6))):
        yy = y0 + 0.95 + i * 0.95
        cv.line([(x0 + 0.6 + w * ind, yy), (x0 + 0.6 + w * ind + (w - 1.2) * frac, yy)],
                color=IC if ind == 0 else style.NEUTRAL_MID, lw=0.5)


def tag(cv, cx, cy, s, color=G, size=LAB):
    w = cv.width(s, size, 'bold') + 1.4
    cv.rrect(cx - w / 2, cy - 1.15, w, 2.3, r=0.5, fc='white', ec=color, lw=0.7, z=6)
    cv.ctext(cx, cy + 0.05, s, size, 'bold', INK)
    return w


def waffle(cv, x, y, n, cols, cell=1.0, gap=0.28, open_last=0, fc=style.NEUTRAL_MID):
    for i in range(n):
        r, c = divmod(i, cols)
        xx, yy = x + c * (cell + gap), y + r * (cell + gap)
        if i >= n - open_last:
            cv.rect(xx + 0.08, yy + 0.08, cell - 0.16, cell - 0.16, fc='white', ec=fc, lw=0.5, z=4)
        else:
            cv.rect(xx, yy, cell, cell, fc=fc, z=4)
    return x + cols * (cell + gap) - gap


# ---------------------------------------------------------------- layout helpers
def panel_head(cv, y, letter, title):
    cv.ax.text(0.6, y + 0.80 * 8 * PT, letter, fontsize=8, fontweight='bold', va='baseline', color=INK, zorder=6)
    cv.text(5.0, y + 0.55, title, 6.5, 'bold')


def column_head(cv, x, w, y, title, sub=None):
    cv.text(x, y, title, 6.5, 'bold')
    if sub:
        cv.text(x + cv.width(title, 6.5, 'bold') + 1.4, y + 0.3, sub, 5.5, color=INK2)
    cv.ax.plot([x, x + w], [y + 3.5, y + 3.5], color=INK2, lw=0.5, zorder=2)


def step_head(cv, x, y, i, name):
    cv.circ(x + 3.0, y + 3.0, 1.55, fc=INK, ec='none', z=4)
    cv.ctext(x + 3.0, y + 3.05, str(i), 5.5, 'bold', 'white')
    cv.text(x + 5.6, y + 1.55, name, 6.5, 'bold')


# ---------------------------------------------------------------- panel a
def benchmarks(cv, x, y, w, f):
    rows = [('BixBench-Verified-50', f['bix'], 10, 0, True, 13.6),
            ('CompBioBench', f['cb'], 20, 0, True, 13.6),
            ('IWC', f['iwc'], 10, 1, False, 13.6)]
    gap = 1.6
    yy = y
    for k, (name, n, cols, open_last, answer, h) in enumerate(rows):
        cv.rrect(x, yy, w, h, r=0.9, fc=FILL, ec=EDGE, lw=0.5, z=1)
        icx, icy = x + 5.2, yy + h / 2
        if k == 0:
            doc(cv, icx - 0.9, icy - 0.6, 4.4, 5.6, mark='?')
            table(cv, icx + 1.6, icy + 2.2, 4.2, 3.2)
        elif k == 1:
            dna(cv, icx, icy, 4.6, h - 3.4)
        else:
            workflow(cv, icx, icy, 8.0)
        tx = x + 11.2
        cv.text(tx, yy + 1.3, name, NAME, 'bold')
        cv.text(x + w - 1.4, yy + 1.5, f'{n} tasks', 5.5, color=INK2, ha='right')
        rows_n = -(-n // cols)
        oy = yy + 8.4
        wy = oy - (rows_n * 1.28 - 0.28) / 2
        xe = waffle(cv, tx, wy, n, cols, open_last=open_last)
        ox = x + w - 4.6
        cv.arrow((xe + 0.8, oy), (ox - 3.3, oy), color=IC, lw=0.6, ms=4)
        if answer:
            bubble(cv, ox, oy - 0.5, 5.0, 3.6)
            cv.ctext(ox, oy + 3.6, 'answer', LAB, color=INK2)
        else:
            files(cv, ox + 0.3, oy - 0.3, 3.2, 4.0)
            cv.ctext(ox, oy + 3.6, 'files', LAB, color=INK2)
        yy += h + gap
    ky = yy + 0.2   # waffle key
    cv.rect(x + 0.4, ky + 0.35, 1.0, 1.0, fc=style.NEUTRAL_MID, z=4)
    cv.text(x + 2.0, ky, 'task', LAB, color=INK2)
    kx = x + 2.0 + cv.width('task', LAB) + 2.4
    cv.rect(kx + 0.08, ky + 0.43, 0.84, 0.84, fc='white', ec=style.NEUTRAL_MID, lw=0.5, z=4)
    cv.text(kx + 1.6, ky, 'not scored', LAB, color=INK2)
    return yy + 2.4


def design(cv, x, y, w, n_tasks, bottom):
    wl, gap = 18.0, 1.0
    wc = (w - wl - gap) / 2
    xs = {'open_ended_code': x + wl, 'galaxy': x + wl + wc + gap}
    hh = 17.6
    for env in style.ENVS:
        cv.rrect(xs[env], y, wc, hh, r=0.9, fc=style.ENV_TINT[env], ec=style.ENV_COLOR[env], lw=0.75, z=1)
        cv.ctext(xs[env] + wc / 2, y + 2.4, style.ENV_LABEL[env], NAME, 'bold')
    cc = xs['open_ended_code'] + wc / 2
    terminal(cv, cc, y + 10.3, 15.0, 9.0, prompt_color=C)
    gc = xs['galaxy'] + wc / 2
    gw = wc - 9.4
    tag(cv, xs['galaxy'] + 4.1, y + 10.3, 'MCP')
    galaxy_window(cv, gc + 3.4, y + 10.3, gw, 10.0)
    cv.line([(xs['galaxy'] + 6.4, y + 10.3), (gc + 3.4 - gw / 2, y + 10.3)], color=G, lw=0.7, z=5)
    # rows: model configurations, each running the Codex agent
    cv.text(x, y + hh - 4.5, 'Model', 5.5, 'bold')
    cv.text(x, y + hh - 2.3, '(Codex agent)', LAB, color=INK2)
    f_h = 8.6
    rows_top = y + hh + 0.4
    rh = (bottom - f_h - 3.6 - rows_top) / len(CONFIGS)
    for i, name in enumerate(CONFIGS):
        ry = rows_top + i * rh
        agent(cv, x + 2.0, ry + rh / 2 + 0.35, 3.2)
        cv.text(x + 4.6, ry + rh / 2 - 1.0, name, 5.5, 'bold')
        for env in style.ENVS:
            cx = xs[env] + wc / 2
            for k in (-1, 0, 1):
                cv.marker(cx + 3.0 * k, ry + rh / 2, env)
        cv.ax.plot([x, x + w], [ry + rh, ry + rh], color=style.GRID, lw=0.5, zorder=2)
    ly = rows_top + len(CONFIGS) * rh + 0.6
    cv.marker(x + 1.0, ly + 1.15, 'open_ended_code', ms=3.2)
    cv.marker(x + 3.3, ly + 1.15, 'galaxy', ms=3.2)
    cv.text(x + 5.0, ly, 'replicate run (×3)', LAB, color=INK2)
    # design equation: numbers large, factor names small
    fy = bottom - f_h
    cv.rrect(x, fy, w, f_h, r=0.9, fc=FILL, ec=EDGE, lw=0.5, z=1)
    n_runs = n_tasks * len(CONFIGS) * N_COND * N_REP
    terms = [(str(n_tasks), 'tasks'), ('×', None), (str(len(CONFIGS)), 'models'), ('×', None),
             (str(N_COND), 'conditions'), ('×', None), (str(N_REP), 'replicates'), ('=', None),
             (f'{n_runs:,}', 'runs')]
    widths = [max(cv.width(t, 7, 'bold'), cv.width(s or '', LAB)) for t, s in terms]
    sep = 1.8
    xx = x + (w - sum(widths) - sep * (len(terms) - 1)) / 2
    for (t, s), ww in zip(terms, widths):
        cv.ctext(xx + ww / 2, fy + 3.3, t, 7, 'bold', INK)  # Nature text maximum; 8 pt is for panel letters
        if s:
            cv.ctext(xx + ww / 2, fy + 6.6, s, LAB, color=INK2)
        xx += ww + sep
    return n_runs


def evaluation(cv, x, y, w, bottom):
    rows = ['Accuracy', 'Repeatability', 'Input tokens', 'Galaxy interface', 'Failure causes']
    gap = 1.4
    h = (bottom - y - gap * (len(rows) - 1)) / len(rows)
    for k, name in enumerate(rows):
        yy = y + k * (h + gap)
        g = name.startswith('Galaxy')
        cv.rrect(x, yy, w, h, r=0.9, fc=G_TINT if g else FILL, ec=G if g else EDGE, lw=0.75 if g else 0.5, z=1)
        icx, icy = x + 5.0, yy + h / 2
        tx = x + 10.4
        cv.text(tx, yy + 1.2, name, NAME, 'bold')
        gy = yy + h - 3.0   # glyph row centre
        if k == 0:
            target(cv, icx, icy, 3.1)
            verdict(cv, tx + 1.2, gy, True)
            verdict(cv, tx + 4.0, gy, False)
            cv.text(tx + 5.8, gy - 1.05, '0/1', LAB, color=INK2)
            bx = tx + 12.0
            cv.rect(bx, gy - 0.55, 9.0, 1.1, fc='#e3e2de', ec=IC, lw=0.4, z=4)
            cv.rect(bx, gy - 0.55, 9.0 * 0.72, 1.1, fc=style.NEUTRAL_MID, z=5)
            cv.text(bx + 10.0, gy - 1.05, '0–1', LAB, color=INK2)
        elif k == 1:
            cv.arc_arrow(icx, icy, 2.6, 110, 420, lw=0.8)
            cv.ctext(icx, icy + 0.05, '×3', 5.5, 'bold', INK)
            for j in range(3):
                verdict(cv, tx + 1.2 + j * 2.6, gy, True, r=1.0)
            cv.text(tx + 1.2 + 2 * 2.6 + 1.6, gy - 1.05, 'or', LAB, color=INK2)
            ox = tx + 1.2 + 2 * 2.6 + 1.6 + cv.width('or', LAB) + 1.8
            for j, ok in enumerate((True, False, True)):
                verdict(cv, ox + j * 2.6, gy, ok, r=1.0)
        elif k == 2:
            coins(cv, icx, icy + 0.2, 4.8)
            cv.text(tx, gy - 1.05, 'per run, incl. cached', LAB, color=INK2)
        elif k == 3:
            bars(cv, icx - 2.9, icy - 2.4, 5.8, 4.8)
            cv.text(tx, gy - 1.05, 'calls · failures · UDTs', LAB, color=INK2)
        else:
            magnifier(cv, icx - 0.5, icy - 0.5, 2.0)
            stacked(cv, tx, gy - 0.8, 14.0, 1.6)
            cv.text(tx + 15.2, gy - 1.05, 'failing tasks', LAB, color=INK2)


# ---------------------------------------------------------------- panel b
def step_prepare(cv, x, y, w, h):
    step_head(cv, x, y, 1, 'Prepare')
    container(cv, x + 2.0, y + 7.6, 24.0, 21.0)
    doc(cv, x + 8.4, y + 17.8, 5.0, 6.4)
    cv.ctext(x + 8.4, y + 23.9, 'prompt', LAB, color=INK2)
    files(cv, x + 17.0, y + 17.8, 3.8, 5.0)
    cv.ctext(x + 16.7, y + 23.9, 'inputs', LAB, color=INK2)
    cv.ctext(x + 12.7, y + 30.6, 'container', LAB, color=INK2)
    rx = x + w - 6.6
    doc(cv, rx, y + 13.6, 4.8, 6.0, lines=3)
    lock(cv, rx + 1.6, y + 15.2, 2.6)
    cv.ctext(rx, y + 19.8, 'reference', LAB, color=INK2)
    history(cv, rx, y + 26.6, 5.2, 6.4)
    cv.ctext(rx, y + 31.6, 'history', LAB, color=INK2)


def step_execute(cv, x, y, w, h):
    step_head(cv, x, y, 2, 'Execute')
    ax_, ay = x + w / 2, y + 13.2
    agent(cv, ax_, ay, 6.4)
    cv.arc_arrow(ax_, ay - 0.3, 5.2, 200, 340, lw=0.7, ms=4)
    cv.arc_arrow(ax_, ay - 0.3, 5.2, 20, 160, lw=0.7, ms=4)
    clock(cv, x + w - 5.4, y + 4.4, 2.1)
    cv.ctext(x + w - 5.4, y + 8.3, 'time limit', LAB, color=INK2)
    tl, gl = (x + 8.4, y + 27.0), (x + w - 9.8, y + 27.0)
    cv.arrow((ax_ - 3.0, ay + 3.6), (tl[0] + 1.5, tl[1] - 4.6), color=IC, lw=0.7)
    cv.arrow((ax_ + 3.0, ay + 3.6), (gl[0] - 1.5, gl[1] - 4.8), color=G, lw=0.7)
    tag(cv, (ax_ + gl[0]) / 2 + 1.4, (ay + 3.6 + gl[1] - 4.8) / 2, 'MCP')
    terminal(cv, *tl, 12.0, 8.0)
    cv.ctext(tl[0], tl[1] + 5.6, 'shell', LAB, color=INK2)
    galaxy_window(cv, *gl, 16.4, 8.0, title=None, udt=True)
    cv.ctext(gl[0], gl[1] + 5.6, 'Galaxy jobs', LAB, color=INK2)


def step_capture(cv, x, y, w, h):
    step_head(cv, x, y, 3, 'Capture')
    cy = y + 13.8
    items = [('answer', lambda cx: bubble(cv, cx, cy - 0.6, 5.0, 3.6)),
             ('outputs', lambda cx: files(cv, cx + 0.4, cy - 0.3, 3.2, 4.2)),
             ('trace', lambda cx: trace(cv, cx, cy, 4.4, 5.6)),
             ('tokens', lambda cx: coins(cv, cx, cy, 4.6))]
    for i, (lab, fn) in enumerate(items):
        cx = x + 5.6 + i * (w - 11.2) / 3
        fn(cx)
        cv.ctext(cx, cy + 5.0, lab, LAB, color=INK2)
    cv.rrect(x + 1.6, y + 21.6, w - 3.2, 10.8, r=0.7, fc=G_LIGHT, ec='none', z=1)
    provenance(cv, x + 6.0, y + 25.8, w - 12.0)
    cv.ctext(x + w / 2, y + 29.8, 'history provenance', LAB, color=INK2)


def step_evaluate(cv, x, y, w, h):
    step_head(cv, x, y, 4, 'Evaluate')
    cy = y + 12.6
    ax_, rx, mx = x + 6.2, x + w - 6.4, x + w / 2
    bubble(cv, ax_, cy - 0.5, 5.0, 3.6)
    cv.ctext(ax_, cy + 4.6, 'answer', LAB, color=INK2)
    doc(cv, rx, cy, 4.6, 5.8)
    lock(cv, rx + 1.6, cy + 1.5, 2.4, opened=True)
    cv.ctext(rx, cy + 4.6, 'reference', LAB, color=INK2)
    cv.circ(mx, cy, 2.0, fc='white', ec=IC, lw=0.7)
    cv.ctext(mx, cy + 0.05, '=?', 5.5, 'bold', INK)
    cv.arrow((ax_ + 3.0, cy), (mx - 2.2, cy), color=IC, lw=0.6, ms=4)
    cv.arrow((rx - 2.8, cy), (mx + 2.2, cy), color=IC, lw=0.6, ms=4)
    cv.arrow((mx, cy + 2.2), (mx, cy + 4.8), color=IC, lw=0.6, ms=4)
    verdict(cv, mx - 1.5, cy + 6.4, True)
    verdict(cv, mx + 1.5, cy + 6.4, False)
    # aggregation: each task is run three times; accuracy pools the scored runs, and its 95% CI resamples tasks
    cv.line([(x + 2.4, y + 21.4), (x + w - 2.4, y + 21.4)], color=EDGE, lw=0.5, z=2)
    gx = [x + 6.4 + 2.4 * j for j in range(3)]           # columns: replicate runs 1-3
    gy = [y + 24.2 + 2.3 * i for i in range(3)]          # rows: tasks
    for yy, row in zip(gy, ((1, 1, 1), (1, 0, 1), (0, 0, 0))):
        for xx, ok in zip(gx, row):
            verdict(cv, xx, yy, bool(ok), 0.82)
    cv.ctext(gx[1], y + 31.9, '3 runs per task', LAB, color=INK2)
    mid = gy[1]
    cv.arrow((gx[-1] + 1.8, mid), (x + 17.2, mid), color=IC, lw=0.6, ms=3.5)
    bx, bw, base, top = x + 19.4, 4.4, gy[-1] + 0.9, gy[0] + 0.6
    cv.rect(bx, top, bw, base - top, fc=style.NEUTRAL_MID, z=4)
    cv.line([(bx - 0.9, base), (bx + bw + 0.9, base)], color=IC, lw=0.5, z=5)
    cx = bx + bw / 2
    cv.line([(cx, top - 1.6), (cx, top + 1.6)], color=INK, lw=0.7, z=6)
    for yy in (top - 1.6, top + 1.6):
        cv.line([(cx - 0.6, yy), (cx + 0.6, yy)], color=INK, lw=0.7, z=6)
    cv.ctext(cx, y + 31.9, 'accuracy', LAB, color=INK2)
    cv.text(bx + bw + 1.4, top - 2.2, '95% CI from', LAB, color=INK2)
    cv.text(bx + bw + 1.4, top, 'resampled tasks', LAB, color=INK2)


# ---------------------------------------------------------------- assemble
def main():
    f = facts()
    n_tasks = f['bix'] + f['cb'] + f['iwc']
    cv = Canvas()

    panel_head(cv, 0.0, 'a', 'GalaxyBench workflow overview')
    w1, w3, gap = 46.0, 44.0, 6.0
    x1, x3 = 0.6, W - 0.6 - w3
    x2 = x1 + w1 + gap
    w2 = x3 - gap - x2
    top = 6.6
    column_head(cv, x1, w1, top, 'Benchmarks', f'{n_tasks} tasks')
    column_head(cv, x2, w2, top, 'Experimental design')
    column_head(cv, x3, w3, top, 'Evaluation')
    y1 = top + 5.4
    bottom = benchmarks(cv, x1, y1, w1, f)
    n_runs = design(cv, x2, y1, w2, n_tasks, bottom)
    evaluation(cv, x3, y1, w3, bottom)
    mid = (y1 + bottom) / 2
    cv.chevron(x1 + w1 + 0.9, x2 - 0.9, mid)
    cv.chevron(x2 + w2 + 0.9, x3 - 0.9, mid)

    yb = bottom + 5.0
    panel_head(cv, yb, 'b', 'Isolated execution pipeline')
    cv.text(5.0 + cv.width('Isolated execution pipeline', 6.5, 'bold') + 1.6, yb + 0.75,
            f'one of {n_runs:,} runs', 5.5, color=INK2)
    lab = 'Galaxy condition only'
    lx = W - 0.6 - cv.width(lab, LAB)
    cv.text(lx, yb + 0.85, lab, LAB, color=INK2)
    cv.rrect(lx - 4.0, yb + 0.85, 3.0, 2.0, r=0.4, fc=G, ec='none', z=2)
    gap_b = 5.0
    ws = (W - 1.2 - 3 * gap_b) / 4
    ys, hs = yb + 5.6, 34.6
    for i, fn in enumerate((step_prepare, step_execute, step_capture, step_evaluate)):
        x = 0.6 + i * (ws + gap_b)
        cv.rrect(x, ys, ws, hs, r=0.9, fc='white', ec=EDGE, lw=0.6, z=0)
        fn(cv, x, ys, ws, hs)
        if i < 3:
            cv.chevron(x + ws + 0.8, x + ws + gap_b - 0.8, ys + hs / 2)
    h = ys + hs + 0.6
    cv.save(h)
    print(f'fig1_a: {W:.0f} x {h:.1f} mm; {n_tasks} tasks, {n_runs:,} runs')


if __name__ == '__main__':
    main()
