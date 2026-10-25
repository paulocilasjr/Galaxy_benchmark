#!/usr/bin/env python3
"""Build the 10-slide talk for the Nature Methods Brief Communication (terms and results of its outline).

Text, boxes and diagrams are native PowerPoint shapes (editable); the four result figures come from
make_deck_figures.py. Every slide carries speaker notes with the numbers and caveats behind it.
Usage: python build_deck.py   (writes galaxy_agents_brief_communication.pptx next to this script)
"""
import os

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'galaxy_agents_brief_communication.pptx')
INK, INK2, MUTED = RGBColor(0x1A, 0x1A, 0x1A), RGBColor(0x55, 0x55, 0x55), RGBColor(0x8A, 0x8A, 0x8A)
GAL, CODE = RGBColor(0x00, 0x72, 0xB2), RGBColor(0xD5, 0x5E, 0x00)
GAL_T, CODE_T = RGBColor(0xE5, 0xF1, 0xF8), RGBColor(0xFB, 0xEC, 0xE0)       # light tints for box fills
PANEL, LINE, WHITE = RGBColor(0xF4, 0xF5, 0xF6), RGBColor(0xD9, 0xDD, 0xE0), RGBColor(0xFF, 0xFF, 0xFF)
FONT = 'Arial'
W, H = 13.333, 7.5

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(W), Inches(H)
BLANK = prs.slide_layouts[6]


# ---------------------------------------------------------------- helpers
def text(slide, x, y, w, h, paras, size=16, color=INK, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP,
         spacing=1.1, after=6):
    """A text box. paras: list of paragraphs; each a string or a list of (text, {bold, color, size, italic}) runs."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_after = Pt(after)
        runs = [(para, {})] if isinstance(para, str) else para
        for t, f in runs:
            r = p.add_run()
            r.text = t
            r.font.name = FONT
            r.font.size = Pt(f.get('size', size))
            r.font.bold = f.get('bold', bold)
            r.font.italic = f.get('italic', False)
            r.font.color.rgb = f.get('color', color)
    return tb


def bullets(slide, x, y, w, h, items, size=16, color=INK, gap=9, marker='•', marker_color=None):
    """Bulleted paragraphs with a hanging indent; items are strings or run lists as in text()."""
    tb = text(slide, x, y, w, h, [[(f'{marker}  ', {'color': marker_color or MUTED, 'bold': True})] +
                                  ([(it, {})] if isinstance(it, str) else it) for it in items],
              size=size, color=color, after=gap)
    for p in tb.text_frame.paragraphs:
        pPr = p._p.get_or_add_pPr()
        pPr.set('marL', str(Inches(0.24)))
        pPr.set('indent', str(-Inches(0.24)))
    return tb


def nostyle(shape):
    """Drop the theme style reference, so no renderer adds the theme's shadow or outline."""
    st = shape._element.find(qn('p:style'))
    if st is not None:
        shape._element.remove(st)


def box(slide, x, y, w, h, fill=PANEL, line=None, radius=0.08, shape=MSO_SHAPE.ROUNDED_RECTANGLE, lw=1.0):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(lw)
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        s.adjustments[0] = radius
    s.shadow.inherit = False
    nostyle(s)
    s.text_frame.text = ''
    return s


def arrow(slide, x1, y1, x2, y2, color=MUTED, width=2.0):
    c = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    c.line.color.rgb = color
    c.line.width = Pt(width)
    ln = c.line._get_or_add_ln()
    tail = ln.makeelement(qn('a:tailEnd'), {'type': 'triangle', 'w': 'med', 'len': 'med'})
    ln.append(tail)
    return c


def dot(slide, x, y, d, color, shape=MSO_SHAPE.OVAL):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(d), Inches(d))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.shadow.inherit = False
    nostyle(s)
    return s


def header(slide, kicker, title, accent=GAL, title_size=27):
    box(slide, 0.6, 0.42, 0.08, 0.30, fill=accent, shape=MSO_SHAPE.RECTANGLE)
    text(slide, 0.8, 0.40, 11.5, 0.35, [kicker.upper()], size=12.5, color=INK2, bold=True)
    text(slide, 0.6, 0.82, 12.1, 1.15, [title], size=title_size, color=INK, bold=True, spacing=1.0)


def footer(slide, note, number):
    text(slide, 0.6, 7.03, 11.2, 0.35, [note], size=10, color=INK2, spacing=1.0)
    text(slide, 12.1, 7.03, 0.65, 0.3, [str(number)], size=10, color=INK2, align=PP_ALIGN.RIGHT)


def notes(slide, body):
    slide.notes_slide.notes_text_frame.text = body


def image(slide, name, x, y, w=None, h=None):
    path = os.path.join(HERE, f'{name}.png')
    return slide.shapes.add_picture(path, Inches(x), Inches(y), Inches(w) if w else None, Inches(h) if h else None)


def key(slide, x, y, color, label, shape=MSO_SHAPE.RECTANGLE, size=14):
    dot(slide, x, y + 0.06, 0.17, color, shape)
    text(slide, x + 0.27, y, 3, 0.3, [label], size=size, color=INK)


# ---------------------------------------------------------------- 1. title
s = prs.slides.add_slide(BLANK)
box(s, 0, 0, 0.32, H, fill=GAL, shape=MSO_SHAPE.RECTANGLE)
box(s, 0.32, 0, 0.10, H, fill=CODE, shape=MSO_SHAPE.RECTANGLE)
text(s, 1.1, 1.35, 11.0, 2.3, ['AI agents can perform accurate bioinformatics analyses through a computational workbench'],
     size=40, bold=True, spacing=1.0)
text(s, 1.1, 3.75, 11.0, 0.9, ['Agents working in Galaxy compared with agents writing custom code: '
                              '160 tasks, three benchmarks, four models'], size=20, color=INK2, spacing=1.1)
box(s, 1.1, 4.95, 1.2, 0.05, fill=LINE, shape=MSO_SHAPE.RECTANGLE)
text(s, 1.1, 5.2, 9, 0.45, ['Paulo Cilas Morais Lyra'], size=22, bold=True)
text(s, 1.1, 5.7, 9, 0.4, ['Goecks Lab · Moffitt Cancer Center'], size=16, color=INK2)
text(s, 1.1, 6.1, 9, 0.4, ['October 2026'], size=16, color=INK2)
key(s, 9.9, 6.55, GAL, 'Galaxy', MSO_SHAPE.OVAL, size=13)
key(s, 11.05, 6.55, CODE, 'custom code', size=13)
notes(s, 'Title adapted from Jeremy Goecks\'s title comment. The claim: AI agents can perform bioinformatics analyses '
         'through Galaxy as accurately as with custom code, and the analyses they produce are recorded, inspectable and '
         'rerunnable. Not the claim: a new benchmark, or that Galaxy beats custom code.\n\nColours throughout: blue = '
         'Galaxy, vermillion = custom code.')

# ---------------------------------------------------------------- 2. agents
s = prs.slides.add_slide(BLANK)
header(s, 'Introduction · agents', 'Agent benchmarks evaluate agents as programmers: each agent writes and runs its own code')
bullets(s, 0.6, 2.25, 5.6, 3.6, [
    'Agents are being used for biomedical data analysis.',
    'Benchmarks now test whether they can complete whole bioinformatics analyses, for example BixBench-Verified-50 and '
    'CompBioBench.',
    [('These benchmarks evaluate agents as ', {}), ('programmers', {'bold': True}),
     (': each agent writes and runs its own code.', {})]], size=19, gap=16)
# diagram: task -> agent writes code -> runs it -> answer
ys = 2.2
for i, (t1, t2) in enumerate([('Task and data', 'a biomedical question'),
                              ('Agent writes code', 'installs software, writes scripts'),
                              ('Agent runs it', 'in its own workspace'),
                              ('Answer', 'scored against the benchmark')]):
    y = ys + i * 0.92
    box(s, 7.3, y, 4.9, 0.72, fill=CODE_T if i in (1, 2) else PANEL)
    text(s, 7.55, y + 0.08, 4.5, 0.3, [t1], size=16.5, bold=True)
    text(s, 7.55, y + 0.40, 4.5, 0.3, [t2], size=13, color=INK2)
    if i < 3:
        arrow(s, 9.75, y + 0.74, 9.75, y + 0.9)
box(s, 0.6, 6.0, 12.1, 0.78, fill=PANEL)
text(s, 0.85, 6.1, 11.6, 0.6, [[('The gap: ', {'bold': True}),
                                ('whether agents can work through a scientific workbench, instead of writing their own '
                                 'code, has not been tested.', {})]], size=17, anchor=MSO_ANCHOR.MIDDLE)
footer(s, 'Outline P1 and abstract.', 2)
notes(s, 'P1. Agents are being used for biomedical data analysis, and benchmarks now test whether they can complete whole '
         'bioinformatics analyses. These benchmarks evaluate agents as programmers: each agent writes and runs its own '
         'code. Whether agents can work through a workbench to complete bioinformatics tasks as accurately as they can '
         'write code has not been tested.')

# ---------------------------------------------------------------- 3. Galaxy
s = prs.slides.add_slide(BLANK)
header(s, 'Introduction · Galaxy', 'Galaxy is a widely used scientific workbench, and a Model Context Protocol server '
                                   'opens it to agents')
text(s, 0.6, 2.2, 5.8, 0.4, ['For people'], size=18, bold=True, color=GAL)
people = [('Versioned tools', 'every tool and version is defined'),
          ('Managed compute', 'jobs run on the server, not on a laptop'),
          ('Histories', 'record parameters, inputs and outputs'),
          ('Shared, turned into workflows, rerun', 'a history is a reusable analysis')]
for i, (t1, t2) in enumerate(people):
    y = 2.72 + i * 0.95
    box(s, 0.6, y, 5.8, 0.8, fill=GAL_T)
    text(s, 0.85, y + 0.1, 5.4, 0.3, [t1], size=16, bold=True)
    text(s, 0.85, y + 0.44, 5.4, 0.3, [t2], size=13, color=INK2)
text(s, 7.05, 2.2, 5.7, 0.4, ['For agents: the Galaxy MCP server'], size=18, bold=True, color=GAL)
ops = ['Tool search', 'Parameter descriptions', 'History inspection', 'Job submission and monitoring',
       'User-defined tools (UDTs) for operations no installed tool covers']
box(s, 7.05, 2.72, 5.7, 3.65, fill=WHITE, line=GAL, lw=1.5)
bullets(s, 7.35, 2.95, 5.2, 3.3, ops, size=16.5, gap=13, marker='▸', marker_color=GAL)
arrow(s, 6.55, 4.5, 6.95, 4.5, color=GAL)
footer(s, 'Outline P1 and P2. MCP, Model Context Protocol; analyses run on usegalaxy.org.', 3)
notes(s, 'P1: scientific workbenches such as Galaxy are a widely used alternative for people: versioned tools, managed '
         'compute, and histories that record parameters, inputs and outputs and can be shared, turned into workflows '
         'and rerun.\nP2: Galaxy provides a Model Context Protocol server that gives agents tool search, parameter '
         'descriptions, history inspection, job submission and monitoring, and user-defined tools (UDTs) for operations '
         'no installed tool covers.')

# ---------------------------------------------------------------- 4. hypothesis
s = prs.slides.add_slide(BLANK)
header(s, 'Hypothesis', 'Can agents work through a workbench as accurately as they write code?')
box(s, 0.6, 2.1, 12.1, 1.35, fill=GAL_T)
text(s, 0.95, 2.22, 11.5, 1.15, [[('Hypothesis. ', {'bold': True, 'color': GAL}),
                                  ('AI agents can perform bioinformatics analyses through Galaxy as accurately as with '
                                   'custom code, and the analyses they produce are recorded, inspectable and rerunnable.',
                                   {})]], size=20, anchor=MSO_ANCHOR.MIDDLE, spacing=1.05)
text(s, 0.6, 3.75, 12, 0.4, ['Why both together, and why this matters'], size=18, bold=True)
cards = [('Recorded and inspectable', 'Every Galaxy run leaves a structured record of every tool, parameter and dataset. '
          'People can review the analysis in Galaxy and rerun or continue it without using model tokens.'),
         ('Rigor becomes cheap', 'Galaxy makes rigor-improving approaches cheap: running several methods for the same step '
          'and comparing them, or validating results before reporting.'),
         ('Agents as virtual users', 'Agent traces show where scientific software is hard to use, and give a quantitative '
          'cost for each problem.')]
for i, (t1, t2) in enumerate(cards):
    x = 0.6 + i * 4.1
    box(s, x, 4.25, 3.9, 2.15, fill=PANEL)
    text(s, x + 0.25, 4.42, 3.45, 0.4, [t1], size=17, bold=True)
    text(s, x + 0.25, 4.88, 3.45, 1.45, [t2], size=14, color=INK2, spacing=1.1)
text(s, 0.6, 6.55, 12.1, 0.4, [[('Not the claim: ', {'bold': True}),
                                ('a new benchmark, or that Galaxy beats custom code.', {})]], size=14, color=INK2)
footer(s, 'Outline framing, abstract and P6. The rigor approaches are hypotheses this study did not test.', 4)
notes(s, 'Main claim (outline framing). Why it matters: the payoff in the abstract (structured record of every tool, '
         'parameter and dataset), P5 (agents as virtual users) and P6 (Galaxy makes rigor-improving approaches cheap; '
         'present as hypotheses this study did not test). Not the claim: a new benchmark ("Galaxy-Bench"), or that Galaxy '
         'beats custom code (Jeremy Goecks\'s review comments, 2026-09-07).')

# ---------------------------------------------------------------- 5. design
s = prs.slides.add_slide(BLANK)
header(s, 'Experimental design and setup', 'Same model, two conditions: 160 tasks × 4 models × 3 replicates = 3,840 runs')
# models
box(s, 0.6, 2.2, 2.9, 3.6, fill=PANEL)
text(s, 0.8, 2.35, 2.6, 0.6, ['Four model configurations'], size=16, bold=True, spacing=1.0)
text(s, 0.8, 2.95, 2.6, 0.3, ['in the Codex harness'], size=13, color=INK2)
bullets(s, 0.8, 3.45, 2.6, 2.3, ['GPT-5.5', 'GPT-5.6 Sol', 'GPT-5.6 Luna', 'DeepSeek V4 Pro'], size=15, gap=8)
arrow(s, 3.55, 3.4, 4.05, 2.95)
arrow(s, 3.55, 4.6, 4.05, 5.05)
# conditions
box(s, 4.1, 2.2, 4.0, 1.65, fill=GAL_T, line=GAL, lw=1.5)
text(s, 4.35, 2.33, 3.6, 0.35, ['Galaxy'], size=18, bold=True, color=GAL)
text(s, 4.35, 2.75, 3.6, 1.0, ['All analysis runs as Galaxy jobs, including UDTs, through the Galaxy MCP server'],
     size=13.5, spacing=1.05)
box(s, 4.1, 4.15, 4.0, 1.65, fill=CODE_T, line=CODE, lw=1.5)
text(s, 4.35, 4.28, 3.6, 0.35, ['Custom code (baseline)'], size=18, bold=True, color=CODE)
text(s, 4.35, 4.7, 3.6, 1.0, ['The agent installs software and writes its own code'], size=13.5, spacing=1.05)
arrow(s, 8.15, 3.02, 8.65, 3.6)
arrow(s, 8.15, 4.97, 8.65, 4.4)
# benchmarks
box(s, 8.7, 2.2, 4.0, 3.6, fill=PANEL)
text(s, 8.95, 2.35, 3.6, 0.35, ['Three benchmarks, 160 tasks'], size=16, bold=True)
bench = [('BixBench-Verified-50', '50 tasks · accepted answer'), ('CompBioBench', '100 tasks · agreement with the key'),
         ('IWC-derived tasks', '10 tasks · output agreement, correct at ≥ 0.99')]
for i, (t1, t2) in enumerate(bench):
    y = 2.9 + i * 0.92
    text(s, 8.95, y, 3.6, 0.3, [t1], size=15, bold=True)
    text(s, 8.95, y + 0.33, 3.6, 0.5, [t2], size=12.5, color=INK2)
box(s, 0.6, 6.05, 12.1, 0.8, fill=WHITE, line=LINE)
text(s, 0.85, 6.1, 11.6, 0.7, [[('3 replicates per task and condition → 3,840 runs.  ', {'bold': True}),
                                ('Why IWC: its tasks come from Galaxy workflows, so they test whether workbench-native '
                                 'tasks behave differently from platform-neutral ones.', {})]],
     size=15, anchor=MSO_ANCHOR.MIDDLE, spacing=1.05)
footer(s, 'Outline P2. IWC, Intergalactic Workflow Commission.', 5)
notes(s, 'P2. Two conditions defined once: Galaxy (all analysis runs as Galaxy jobs, including UDTs) and custom code (the '
         'agent installs software and writes its own code), with custom code as the baseline. Four model configurations '
         'in the Codex harness, 160 tasks (BixBench-Verified-50, CompBioBench, IWC-derived tasks), three replicates per '
         'task and condition, 3,840 runs. A run is correct when accepted (BixBench-Verified-50, CompBioBench) or at IWC '
         'output agreement >= 0.99.')

# ---------------------------------------------------------------- 6. result 1
s = prs.slides.add_slide(BLANK)
header(s, 'Result 1 · accuracy', 'Agents can use Galaxy to accurately complete bioinformatics tasks at the same level of '
                                 'accuracy as custom code', title_size=25)
image(s, 'deck_result1_accuracy', 1.05, 1.92, w=11.2)
box(s, 0.6, 6.42, 12.1, 0.5, fill=PANEL)
text(s, 0.85, 6.45, 11.6, 0.45, [[('Robust: ', {'bold': True}),
                                  ('differences stay within about one point of zero after removing tasks with audited '
                                   'benchmark-side problems.', {})]], size=14.5, anchor=MSO_ANCHOR.MIDDLE)
footer(s, 'Galaxy − custom code with 95% cluster-bootstrap intervals, by model and for all four models pooled. '
          'IWC wf_007 runs as the results site published them on 12 Oct 2026.', 6)
notes(s, 'P3 (numbers from PR #12, site-matched scores).\nBixBench-Verified-50: 87.2% custom code, 87.7% Galaxy, +0.5 '
         '(-3.9 to 4.8) points.\nCompBioBench: 86.7% and 87.0%, +0.3 (-1.8 to 2.5) points.\nIWC: output agreement 0.95 '
         'and 0.99, +0.036 (0.006 to 0.073); three tasks containing a zero-scored run account for most of the difference.'
         '\nRobustness: removing 15 BixBench tasks with audited benchmark-side problems or 66 CompBioBench task-'
         'configuration cells keeps both differences within about one point of zero.\nNo per-model difference is '
         'significant after Holm adjustment. This does not establish equivalence.')

# ---------------------------------------------------------------- 7. result 2
s = prs.slides.add_slide(BLANK)
header(s, 'Result 2 · errors', 'Errors come in two kinds: systematic errors come mostly from the benchmark, random '
                               'errors mostly from missing validation', title_size=25)
image(s, 'deck_result2_errors', 0.45, 1.95, w=7.65)
x0 = 8.35
box(s, x0, 2.0, 4.35, 2.05, fill=PANEL)
text(s, x0 + 0.25, 2.12, 3.9, 0.35, ['Systematic'], size=16.5, bold=True, color=INK)
text(s, x0 + 0.25, 2.48, 3.9, 1.55, ['Repeat in every replicate. 85 of the 94 benchmark-specification errors sit in '
                                    'replicate groups where all three runs were wrong, which usually give the same wrong '
                                    'answer: the task or the answer key, not chance.'], size=13, color=INK2, spacing=1.05)
box(s, x0, 4.2, 4.35, 2.05, fill=PANEL)
text(s, x0 + 0.25, 4.32, 3.9, 0.35, ['Random'], size=16.5, bold=True, color=INK)
text(s, x0 + 0.25, 4.68, 3.9, 1.55, ['Differ between replicates. Missing validation is spread out: 16 of its 32 errors '
                                    'are in groups where the other two were correct. bix-30-q3: failed custom-code runs '
                                    'added exclusions, normalization and a test the task did not ask for.'], size=13,
     color=INK2, spacing=1.05)
text(s, 0.6, 6.42, 12.1, 0.55, [[('Most wrong answers are not runs that broke: ', {'bold': True}),
                                 ('69–94% of correct runs also hit an execution error and recovered; wrong runs finished '
                                  'and reported the wrong thing.', {})]], size=14)
footer(s, 'BixBench-Verified-50: 151 incorrect runs, causes from execution traces; 71% from the benchmark, 25% agent '
          'errors, 3 from Galaxy, 4 without an answer.', 7)
notes(s, 'P4. BixBench (151 incorrect runs, causes from execution traces): 71% came from the benchmark, an under-specified '
         'task or reference answer (94) or a scorer rejecting a valid answer (13); 25% were agent errors, no validation of '
         'the answer (32) or wrong biological or statistical knowledge (5); Galaxy itself caused 3, and 4 runs submitted '
         'no answer.\nMissing validation is a primary or secondary cause in 116 of the 151 incorrect runs; it often turns '
         'an ambiguous task into a confidently wrong answer. Example: bix-30-q3, failed custom-code runs added exclusions, '
         'normalization and a statistical test the task did not ask for (Galaxy 12/12 correct, custom code 4/12). '
         'Counter-example: CompBioBench variant-status-q1, Galaxy runs that added a read-position check were right.\n'
         'Incorrect runs in all-wrong replicate groups: 105 of 151 (BixBench), 144 of 316 (CompBioBench), 36 of 55 (IWC). '
         'When all three are wrong they usually give the same wrong answer (77-83% of such groups in BixBench, 61-64% in '
         'CompBioBench): the task or the answer key, not chance.\nCompBioBench and IWC have no failure-cause audit yet.')

# ---------------------------------------------------------------- 8. result 3
s = prs.slides.add_slide(BLANK)
header(s, 'Result 3 · consensus', 'Consensus helps a little; a validation step that picks the correct replicate would '
                                  'help more', title_size=26)
image(s, 'deck_result3_consensus', 0.45, 1.92, w=7.5)
x0 = 8.45
items = [[('A majority vote ', {'bold': True}), ('over three replicates adds 0.3 to 2.3 points '
                                                 '(BixBench-Verified-50, CompBioBench).', {})],
         [('At least one replicate was correct ', {'bold': True}), ('in 85–94% of replicate groups: most of the room '
                                                                    'left is a correct answer produced but not chosen.', {})],
         [('Disagreement flags answers to check ', {'bold': True}), ('without the true answer: replicates split on 8–10% '
                                                                     '(BixBench), 15–17% (CompBioBench) and 10–20% (IWC) '
                                                                     'of groups.', {})],
         [('Galaxy runs are more consistent, ', {'bold': True}), ('which cuts both ways: voting gains 0.3 points in Galaxy '
                                                                  'against 2.3 with custom code.', {})]]
bullets(s, x0, 2.05, 4.3, 4.3, items, size=14, gap=12)
box(s, 0.6, 6.42, 12.1, 0.5, fill=PANEL)
text(s, 0.85, 6.45, 11.6, 0.45, [[('Consistent wrong answers need fixes in the tools, not votes: ', {'bold': True}),
                                  ('bix-45-q1 failed in all 12 Galaxy runs because of the PhyKIT version (custom code 8/12).',
                                   {})]], size=14, anchor=MSO_ANCHOR.MIDDLE)
footer(s, 'Estimates from the existing runs; no consensus strategy was run. Votes from correctness; IWC correct at '
          'agreement ≥ 0.99.', 8)
notes(s, 'P4, consensus table (data/replicate_consensus.csv, rerun on PR #12 data).\nSingle run / majority of 3 / at '
         'least 1 of 3 / majority of 12:\nBixBench Galaxy 87.7 / 88.0 / 91.5 / 92.0; custom code 87.2 / 89.5 / 91.0 / '
         '90.0.\nCompBioBench Galaxy 87.0 / 87.3 / 94.3 / 91.0; custom code 86.7 / 89.0 / 93.8 / 89.0.\nIWC Galaxy 80.0 / '
         '80.0 / 85.0 / 80.0; custom code 74.2 / 72.5 / 85.0 / 70.0 (updated for the wf_007 runs the site replaced on 12 '
         'Oct; the outline table predates that update).\nA majority over all 12 runs of a task reaches 89-92% on '
         'BixBench and CompBioBench. A text vote on BixBench scores below a single run, because 10% of groups with three '
         'correct runs gave differently worded correct answers. On IWC\'s continuous score the median of three raises '
         'mean agreement from 0.990 to 0.991 (Galaxy) and from 0.954 to 0.964 (custom code); the best of three reaches '
         '0.995 and 0.994.\nCaveats: votes from correctness assume correct answers agree; ties count as incorrect; none of '
         'these strategies were run.')

# ---------------------------------------------------------------- 9. result 4
s = prs.slides.add_slide(BLANK)
header(s, 'Result 4 · what Galaxy adds and what it costs', 'Agent traces showed where Galaxy\'s tokens went; interface '
                                                            'fixes cut its cost from about 20× to 1.53× custom code',
       title_size=25)
# record card
box(s, 0.6, 2.0, 4.6, 3.05, fill=WHITE, line=GAL, lw=1.5)
text(s, 0.82, 2.1, 4.2, 0.35, ['What Galaxy adds: a structured record'], size=15, bold=True, color=GAL)
text(s, 0.82, 2.45, 4.2, 0.3, ['One Galaxy run (bix-45-q1, GPT-5.6 Sol, replicate 1)'], size=11.5, color=INK2)
jobs = [('PhyKIT metrics 0.2.0+galaxy0', 'relative composition variability · animals → 3 datasets'),
        ('PhyKIT metrics 0.2.0+galaxy0', 'relative composition variability · fungi → 3 datasets'),
        ('Nonparametric rank tests 0.1.0+galaxy2', 'Mann–Whitney U, animal vs fungal → 1 dataset')]
for i, (t1, t2) in enumerate(jobs):
    y = 2.85 + i * 0.68
    box(s, 0.82, y, 4.18, 0.6, fill=GAL_T)
    text(s, 0.98, y + 0.05, 3.3, 0.28, [t1], size=12, bold=True)
    text(s, 0.98, y + 0.3, 3.9, 0.28, [t2], size=10.5, color=INK2)
    text(s, 4.45, y + 0.05, 0.5, 0.28, ['ok'], size=11, bold=True, color=GAL, align=PP_ALIGN.RIGHT)
text(s, 0.6, 5.15, 4.6, 0.9, ['Tool versions, parameters, datasets and job states: reviewable in Galaxy and rerunnable '
                              'without model tokens.'], size=12.5, color=INK2, spacing=1.05)
box(s, 0.6, 5.95, 4.6, 0.95, fill=PANEL)
text(s, 0.8, 6.0, 4.25, 0.85, [[('Where the tokens went: ', {'bold': True}),
                                ('95% of Galaxy tokens were cached input; 2.66× as many agent steps, each with 2.2× as '
                                 'much context. Cost = round trips × context size.', {})]], size=11.5, spacing=1.05,
     anchor=MSO_ANCHOR.MIDDLE)
image(s, 'deck_result4_tokens', 5.4, 1.95, w=7.4)
footer(s, 'BixBench-Verified-50. Not a controlled ablation; ~20× and ~8× are one run per task, not yet on the results '
          'site. Main runs: 4.2× BixBench, 2.7× CompBioBench, 0.92× IWC.', 9)
notes(s, 'P5. What Galaxy adds: every Galaxy run leaves a structured record of tool identities and versions, requested and '
         'resolved parameters, datasets and job states; people can review it in Galaxy and rerun or continue it without '
         'model tokens. The example record also shows the PhyKIT version behind the bix-45-q1 systematic error.\n'
         'Where the tokens went (6 July experiment, GPT-5.5, 150 runs per condition): cached input was 95% of Galaxy '
         'tokens and output under 1%; Galaxy runs took 2.66x as many agent steps, each carrying 2.2x as much context.\n'
         'Stages: baseline about 20x; round 1 (prompt and skills) about 8x; round 1 rerun with replicates 5.48x; round 2 '
         '(MCP and execution) 2.81x, Galaxy tokens down 55.2%; round 2 with GPT-5.6 Sol 3.45x; round 3a (interface) '
         '2.42x; round 3b (longer waits) 1.53x, 137/150 correct.\nAgents as virtual users: each overhead was found in '
         'agent traces, fixed in the interface, and the benchmark rerun to measure the effect.\nCaveats: not a controlled '
         'ablation (the model alone moves the ratio, 2.81x vs 3.45x); baseline and round 1 used one run per task and need '
         'run records before they can be cited; round 3 is one benchmark and one model; the main Galaxy results use the '
         'round-2 interface.')

# ---------------------------------------------------------------- 10. conclusions
s = prs.slides.add_slide(BLANK)
header(s, 'Conclusions', 'AI agents can perform bioinformatics analyses through Galaxy as accurately as with custom code, '
                         'and the analyses are recorded, inspectable and rerunnable', title_size=22)
take = [('Accuracy', 'Similar in the two conditions on every benchmark: +0.5 and +0.3 points; IWC +0.036 agreement.'),
        ('Errors', 'Systematic errors come mostly from the benchmark; random errors mostly from missing validation.'),
        ('Consensus', 'A vote helps a little; a validation step that picks the correct replicate would help more.'),
        ('Cost', 'Agents as virtual users found the interface overheads; fixes cut Galaxy from about 20× to 1.53× '
                 'custom code.')]
for i, (t1, t2) in enumerate(take):
    x = 0.6 + (i % 2) * 6.1
    y = 2.15 + (i // 2) * 1.55
    box(s, x, y, 5.95, 1.38, fill=PANEL)
    box(s, x, y, 0.09, 1.38, fill=GAL, shape=MSO_SHAPE.RECTANGLE)
    text(s, x + 0.3, y + 0.14, 5.45, 0.35, [t1], size=17, bold=True)
    text(s, x + 0.3, y + 0.52, 5.45, 0.85, [t2], size=14, color=INK2, spacing=1.05)
text(s, 0.6, 5.35, 12.1, 0.35, ['Implications to test next'], size=15.5, bold=True)
bullets(s, 0.6, 5.72, 12.1, 0.9, [
    'Galaxy makes rigor-improving approaches cheap: running several methods for the same step and comparing them, or '
    'validating results before reporting.',
    'Agent traces could become a routine source of usability evidence for scientific software.'], size=14, gap=4)
footer(s, 'Limitations: a fixed set of models and benchmarks, prompts that differ between conditions, and models that '
          'change quickly.', 10)
notes(s, 'Main claim and the four results. P6: Galaxy makes rigor-improving approaches cheap, such as running several '
         'methods for the same step and comparing them, or validating results before reporting; these are hypotheses '
         'this study did not test. Agents as virtual users: run agents on representative tasks, attribute cost and '
         'failure to specific interface features, fix them, and re-measure. Limitations: a fixed set of models and '
         'benchmarks, prompts that differ between conditions, and models that change quickly.')

prs.save(OUT)
print('wrote', OUT)
