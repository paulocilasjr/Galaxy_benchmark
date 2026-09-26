"""Shared figure style meeting Nature Portfolio specifications.

Verified against research-figure-guide.nature.com (accessed 2026-09-25):
main figures 89 mm or 183 mm wide, max 170 mm tall; Extended Data max 180 x 170 mm;
sans-serif (Arial) 5-7 pt; panel labels 8 pt bold lowercase; strokes 0.25-1 pt; RGB;
editable vector text with TrueType (Type 42) fonts; avoid coloured text.

Colour rules (safe for colour-vision deficiency):
- Colours come from the Okabe-Ito palette recommended in Nature Methods (Wong, B. Points of view: Color blindness.
  Nat. Methods 8, 441; 2011). Every palette below passed a simulation-based validator (OKLab Delta E >= 8 between
  neighbouring colours under simulated protanopia and deuteranopia).
- Colour has one meaning across the paper: vermillion = open-ended code, blue = Galaxy. Environment is also encoded
  by marker shape (square = open-ended code, circle = Galaxy) so that it survives greyscale printing.
- Benchmarks are never colour-coded; panels and labels separate them.
- Open-ended code is the reference condition and is always shown first.
"""
import io
import json
import os

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
from PIL import Image  # noqa: E402

MM = 1 / 25.4
W_DOUBLE, W_SINGLE, H_MAX = 183 * MM, 89 * MM, 170 * MM
W_ED = 179 * MM  # 180 mm limit; EPS bounding boxes round up to whole points

# Okabe-Ito palette
OI_ORANGE, OI_SKY, OI_GREEN, OI_YELLOW = '#E69F00', '#56B4E9', '#009E73', '#F0E442'
OI_BLUE, OI_VERMILLION, OI_PURPLE, OI_BLACK = '#0072B2', '#D55E00', '#CC79A7', '#000000'

CODE, GALAXY = OI_VERMILLION, OI_BLUE
ENVS = ['open_ended_code', 'galaxy']  # reference condition first, everywhere
ENV_COLOR = {'open_ended_code': CODE, 'galaxy': GALAXY}
ENV_TINT = {'open_ended_code': '#F6DCCB', 'galaxy': '#CFE3F1'}
ENV_MARKER = {'open_ended_code': 's', 'galaxy': 'o'}
ENV_LABEL = {'open_ended_code': 'Open-ended code', 'galaxy': 'Galaxy'}

BENCH = ['BixBench50', 'CompBio', 'IWC']
BENCH_LABEL = {'BixBench50': 'BixBench-Verified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}
BENCH_2L = {'BixBench50': 'BixBench-\nVerified-50', 'CompBio': 'CompBioBench', 'IWC': 'IWC'}

CONFIGS = ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro']
SUPERSEDED = 'DeepSeek V4 Pro (Claude Code, superseded)'
CFG_LABEL = {c: c for c in CONFIGS}
CFG_LABEL.update({SUPERSEDED: 'DeepSeek V4 Pro,\nClaude Code harness\n(superseded)', 'DeepSeek V4 Pro (Codex)': 'DeepSeek V4 Pro',
                  'GPT-6 Astra': 'GPT-6 Astra'})

INK, INK2 = '#1a1a1a', '#555555'
GRID, LIGHT = '#e4e3df', '#f2f1ee'
NEUTRAL_LIGHT, NEUTRAL_MID, NEUTRAL_DARK = '#DDDDDD', '#999999', '#555555'

plt.rcParams.update({
    'font.family': 'Arial', 'font.size': 6, 'axes.titlesize': 6, 'axes.labelsize': 6,
    'xtick.labelsize': 5.5, 'ytick.labelsize': 5.5, 'legend.fontsize': 5.5, 'legend.title_fontsize': 5.5,
    'axes.linewidth': 0.5, 'xtick.major.width': 0.5, 'ytick.major.width': 0.5,
    'xtick.major.size': 2, 'ytick.major.size': 2, 'xtick.major.pad': 1.5, 'ytick.major.pad': 1.5,
    'lines.linewidth': 0.75, 'patch.linewidth': 0.5, 'axes.edgecolor': INK2, 'axes.labelcolor': INK,
    'xtick.color': INK2, 'ytick.color': INK, 'text.color': INK, 'axes.spines.top': False,
    'axes.spines.right': False, 'legend.frameon': False, 'legend.handlelength': 1.0,
    'legend.handletextpad': 0.4, 'legend.columnspacing': 0.8, 'legend.borderaxespad': 0.2,
    'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none', 'savefig.dpi': 300,
    'axes.titleweight': 'bold', 'axes.titlepad': 3, 'axes.labelpad': 2, 'hatch.linewidth': 0.5,
    'mathtext.default': 'regular',  # superscripts and subscripts set in Arial
})


def panel_label(fig, x, y, letter):
    fig.text(x, y, letter, fontsize=8, fontweight='bold', va='top', ha='left', color=INK)


def panel_title(fig, x, y, text):
    """Panel headline: states the finding, not only the content."""
    fig.text(x + 0.018, y - 0.001, text, fontsize=6.5, fontweight='bold', va='top', ha='left', color=INK, linespacing=1.15)


def grid_x(ax):
    ax.xaxis.grid(True, color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)


def grid_y(ax):
    ax.yaxis.grid(True, color=GRID, lw=0.4, zorder=0)
    ax.set_axisbelow(True)


def env_handles(ms=3.8, which=ENVS):
    """Legend handles for the two environments, open-ended code first."""
    from matplotlib.lines import Line2D
    return [Line2D([], [], marker=ENV_MARKER[e], ls='', mfc=ENV_COLOR[e], mec='white', mew=0.4, ms=ms, label=ENV_LABEL[e])
            for e in which]


def env_patches(which=ENVS):
    from matplotlib.patches import Patch
    return [Patch(fc=ENV_COLOR[e], label=ENV_LABEL[e]) for e in which]


def enforce_min_font(fig, minimum=5.0):
    """Nature requires 5-7 pt text at final size; raise any smaller text to the floor."""
    from matplotlib.text import Text
    for t in fig.findobj(Text):
        if t.get_text() and t.get_fontsize() < minimum:
            t.set_fontsize(minimum)


def save_main(fig, name, outdir):
    enforce_min_font(fig)
    pdf = os.path.join(outdir, 'figures', f'{name}.pdf')
    tf = os.path.join(os.path.dirname(__file__), 'figure_titles.json')  # title lives in the legend; also stored as PDF metadata
    title = json.load(open(tf)).get(name) if os.path.exists(tf) else None
    fig.savefig(pdf, metadata={'Title': f"{name.replace('Fig', 'Fig. ')} | {title}"} if title else None)
    fig.savefig(os.path.join(outdir, 'figures', 'previews', f'{name}.png'), dpi=300)
    plt.close(fig)
    return pdf


def save_ed(fig, name, outdir):
    enforce_min_font(fig)
    base = os.path.join(outdir, 'extended_data', name)
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=300, facecolor='white')
    Image.open(buf).convert('RGB').save(base + '.tif', compression='tiff_lzw', dpi=(300, 300))  # RGB, no alpha
    fig.savefig(base + '.eps')
    fig.savefig(os.path.join(outdir, 'extended_data', 'previews', f'{name}.png'), dpi=200)
    plt.close(fig)
    return base + '.tif'
