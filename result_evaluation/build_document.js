#!/usr/bin/env node
/*
 * Build the result-evaluation document (DOCX) from the panel images and the per-figure text.
 *
 * Inputs (all in result_evaluation/):
 *   text/*.md            one section per figure: "# Figure N | title", an intro paragraph, then one "## Fig. Na | question?"
 *                        block per panel with a "panel: <id>" line, "### Rationale" bullets and "### Conclusion" text
 *   panels/manifest.csv  panel images written by split_panels.py, with their size in mm
 *   build/pages.json     optional: page number of each figure and panel, read from a first render (build.py)
 *   build/meta.json      optional: commit and date stamped on the title page
 * Output: Galaxy_benchmark_figure_evaluation.docx
 *
 * Usage: node result_evaluation/build_document.js   (needs the npm package docx; build.py sets NODE_PATH)
 */
const fs = require('fs');
const path = require('path');
const {
  AlignmentType, Bookmark, BorderStyle, Document, Footer, HeadingLevel, ImageRun, InternalHyperlink, LevelFormat,
  Packer, PageNumber, Paragraph, ShadingType, Table, TableCell, TableRow, TabStopType, TextRun, WidthType,
} = require('docx');

const HERE = __dirname;
const OUT = process.env.OUT_DOCX || path.join(HERE, 'Galaxy_benchmark_figure_evaluation.docx');
const TEXT = process.env.TEXT_DIR || path.join(HERE, 'text');
const ORDER = ['Figure 1', 'Figure 2', 'Figure 3', 'Figure 4', 'Figure 5', 'Extended Data Fig. 2',
  'Extended Data Fig. 3', 'Extended Data Fig. 4', 'Extended Data Fig. 5', 'Extended Data Fig. 6',
  'Extended Data Fig. 7'];
const SOURCE = { fig1: 'fig1_a', fig2: 'fig2', fig3: 'fig3', fig4: 'fig4', fig5: 'fig5', ed2: 'ed_fig2', ed3: 'ed_fig3',
  ed4: 'ed_fig4', ed5: 'ed_fig5', ed6: 'ed_fig6', ed7: 'ed_fig7' };

// page: US Letter, 0.7 in margins
const IN = 1440;
const PAGE = { width: 12240, height: 15840, margin: 0.7 * IN };
const TEXT_W = PAGE.width - 2 * PAGE.margin;                 // DXA
const TEXT_MM = TEXT_W / IN * 25.4;
const IMG = { maxScale: 1.6, maxHeightMm: 105 };             // enlarge small panels; leave room for the text
const FONT = 'Arial';
const INK = '1A1A1A', INK2 = '555555', BLUE = '0072B2', TINT = 'EAF2F8', RULE = 'C9C8C3';

// ------------------------------------------------------------------ parsing
function parseText() {
  const figures = {};
  for (const f of fs.readdirSync(TEXT).filter((f) => f.endsWith('.md')).sort()) {
    let fig = null, panel = null, part = null, para = [];
    const flush = () => {
      if (!para.length) return;
      const text = para.join(' ').trim();
      para = [];
      if (panel && part) panel[part].push({ kind: 'p', text });
      else if (fig && !panel) fig.intro.push(text);
    };
    for (const raw of fs.readFileSync(path.join(TEXT, f), 'utf8').split('\n')) {
      const line = raw.trimEnd();
      let m;
      if ((m = line.match(/^# (.+)$/))) {
        flush();
        const [label, ...rest] = m[1].split(' | ');
        const key = ORDER.find((k) => label.trim() === k);
        if (!key) throw new Error(`${f}: unknown figure heading "${m[1]}"`);
        fig = figures[key] = { key, label: label.trim(), title: rest.join(' | ').trim(), intro: [], panels: [] };
        panel = null;
      } else if ((m = line.match(/^## (.+)$/))) {
        flush();
        const [label, ...rest] = m[1].split(' | ');
        panel = { label: label.trim(), question: rest.join(' | ').trim(), id: null, rationale: [], conclusion: [] };
        fig.panels.push(panel);
        part = null;
      } else if ((m = line.match(/^panel:\s*(\S+)/)) && panel) {
        panel.id = m[1];
      } else if ((m = line.match(/^### (.+)$/))) {
        flush();
        part = /rationale/i.test(m[1]) ? 'rationale' : 'conclusion';
      } else if ((m = line.match(/^\s*[-*] (.+)$/)) && panel && part) {
        flush();
        panel[part].push({ kind: 'li', text: m[1] });
      } else if (!line.trim()) {
        flush();
      } else if (/^\s+\S/.test(raw) && panel && part && panel[part].length && panel[part].at(-1).kind === 'li' && !para.length) {
        panel[part].at(-1).text += ' ' + line.trim();   // continuation of a bullet
      } else {
        para.push(line.trim());
      }
    }
    flush();
  }
  const missing = ORDER.filter((k) => !figures[k]);
  if (missing.length) throw new Error(`no text for: ${missing.join(', ')}`);
  return ORDER.map((k) => figures[k]);
}

function readManifest() {
  const [head, ...rows] = fs.readFileSync(path.join(HERE, 'panels', 'manifest.csv'), 'utf8').trim().split(/\r?\n/);
  const cols = head.split(',');
  return Object.fromEntries(rows.map((r) => {
    const v = Object.fromEntries(r.split(',').map((x, i) => [cols[i], x]));
    return [v.panel, v];
  }));
}

function readJson(name, fallback) {
  const p = path.join(HERE, 'build', name);
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, 'utf8')) : fallback;
}

// ------------------------------------------------------------------ inline Markdown: **bold**, *italic*, `code`
function runs(text, base = {}) {
  const out = [];
  const re = /\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`/g;
  let last = 0, m;
  while ((m = re.exec(text))) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), ...base }));
    if (m[1] !== undefined) out.push(...runs(m[1], { ...base, bold: true }));
    else if (m[2] !== undefined) out.push(new TextRun({ text: m[2], ...base, italics: true }));
    else out.push(new TextRun({ text: m[3], ...base, font: 'Courier New', size: 17 }));
    last = re.lastIndex;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), ...base }));
  return out;
}

// ------------------------------------------------------------------ building blocks
const anchorOf = (id) => `p_${id}`;
const figAnchor = (fig) => `f_${fig.key.replace(/\W+/g, '_')}`;
const mmToPx = (mm) => Math.round(mm / 25.4 * 96);

function body(text, opts = {}) {
  return new Paragraph({ children: runs(text), spacing: { after: 120, line: 276 }, ...opts });
}

function label(text) {
  return new Paragraph({
    children: [new TextRun({ text: text.toUpperCase(), bold: true, size: 17, color: BLUE, characterSpacing: 20 })],
    spacing: { before: 200, after: 80 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: RULE, space: 2 } },
  });
}

function panelImage(entry) {
  const w = +entry.width_mm, h = +entry.height_mm;
  const s = Math.min(IMG.maxScale, TEXT_MM / w, IMG.maxHeightMm / h);
  return new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 160, after: 60 },
    keepNext: true,
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(path.join(HERE, entry.png)),
      transformation: { width: mmToPx(w * s), height: mmToPx(h * s) },
      altText: { title: entry.panel, description: `Panel ${entry.panel}`, name: entry.panel } })],
  });
}

function contentsLine(text, anchor, page, level) {
  const children = [new InternalHyperlink({ anchor, children: runs(text, level === 0 ? { bold: true } : {}) }),
    new TextRun({ text: `\t${page ?? '–'}`, bold: level === 0 })];
  return new Paragraph({
    children,
    indent: level ? { left: 360, hanging: 0 } : undefined,
    tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W, leader: 'dot' }],
    spacing: { before: level ? 0 : 140, after: level ? 30 : 50 },
  });
}

function definitions() {
  const rows = [
    ['Conditions', 'Custom code: the agent installs software and writes and runs its own code in an isolated workspace. Galaxy: the agent runs installed Galaxy tools and agent-written user-defined tools (UDTs) as jobs on usegalaxy.org through a Model Context Protocol (MCP) interface. Prompts, containers and time limits differ, so the conditions are compared as deployed.'],
    ['Benchmarks and scores', 'BixBench-Verified-50: 50 questions graded as on the results site, the original evaluator\'s acceptance with documented regrades of bix-53-q2 (directional answer accepted) and bix-43-q2 (platform-specific rounding). CompBioBench: 100 questions scored against a reconstructed answer key that reproduces the official leaderboard. IWC: 10 workflow tasks scored by agreement of output files with curated workflow outputs (0–1), against the reference of the declared route where the method is open. Scores are benchmark-specific and never pooled.'],
    ['Correct run', 'Accepted (BixBench-Verified-50, CompBioBench) or, for IWC, output agreement ≥ 0.99.'],
    ['Models and replicates', 'Four model configurations (GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, DeepSeek V4 Pro) on the Codex agent harness. Each ran every task three times per condition: independent repeats, not successive attempts. A replicate set is the three runs of one task by one model in one condition; a task–model pair is the two replicate sets of one task and model.'],
    ['Intervals', '95% percentile cluster-bootstrap intervals (20,000 resamples unless stated); clusters are BixBench source capsules, otherwise tasks. Wilson intervals for small coded samples.'],
    ['P values', 'Paired cluster sign-flip or randomization tests (200,000 draws; exact enumeration for IWC), Holm-adjusted within each family. A non-significant test does not establish equivalence; no equivalence margin was prespecified.'],
  ];
  const w0 = 2100, w1 = TEXT_W - w0;
  const cell = (children, width, fill) => new TableCell({
    children, width: { size: width, type: WidthType.DXA },
    shading: fill ? { type: ShadingType.CLEAR, fill, color: 'auto' } : undefined,
    margins: { top: 70, bottom: 70, left: 110, right: 110 },
  });
  const border = { style: BorderStyle.SINGLE, size: 4, color: RULE };
  return new Table({
    width: { size: TEXT_W, type: WidthType.DXA },
    columnWidths: [w0, w1],
    borders: { top: border, bottom: border, left: border, right: border, insideHorizontal: border, insideVertical: border },
    rows: rows.map(([k, v]) => new TableRow({ children: [
      cell([new Paragraph({ children: [new TextRun({ text: k, bold: true, size: 18 })] })], w0, 'F2F1EE'),
      cell([new Paragraph({ children: runs(v, { size: 18 }), spacing: { line: 252 } })], w1),
    ] })),
  });
}

// docx 9.6.1 writes every bookmark with w:id="1"; OOXML requires unique ids, so renumber them (each end closes the
// most recent open start)
async function uniqueBookmarkIds(buf) {
  const JSZip = require('jszip');
  const zip = await JSZip.loadAsync(buf);
  let xml = await zip.file('word/document.xml').async('string');
  let n = 0;
  const open = [];
  xml = xml.replace(/<w:bookmark(Start|End)\b[^>]*>/g, (tag, kind) => {
    const id = kind === 'Start' ? (open.push(++n), n) : open.pop();
    return tag.replace(/w:id="[^"]*"/, `w:id="${id}"`);
  });
  if (open.length) throw new Error('unbalanced bookmarks');
  zip.file('word/document.xml', xml);
  return zip.generateAsync({ type: 'nodebuffer', compression: 'DEFLATE' });
}

// ------------------------------------------------------------------ document
function build() {
  const figures = parseText();
  const manifest = readManifest();
  const pages = readJson('pages.json', {});
  const meta = readJson('meta.json', {});
  const nPanels = figures.reduce((n, f) => n + f.panels.length, 0);
  for (const f of figures) for (const p of f.panels) {
    if (!p.id || !manifest[p.id]) throw new Error(`${p.label}: no panel image for id "${p.id}"`);
  }
  const unused = Object.keys(manifest).filter((id) => !figures.some((f) => f.panels.some((p) => p.id === id)));
  if (unused.length) throw new Error(`panels without text: ${unused.join(', ')}`);

  const c = [];
  // title page
  c.push(new Paragraph({ spacing: { before: 2600 }, children: [new TextRun({ text: 'Galaxy Benchmark', size: 26, color: BLUE, bold: true })] }));
  c.push(new Paragraph({ heading: HeadingLevel.TITLE, children: [new TextRun('Figure-by-figure evaluation of the evidence')] }));
  c.push(new Paragraph({ spacing: { before: 240, after: 600 }, children: runs(
    `Every panel of the ${figures.filter((f) => f.label.startsWith('Figure')).length} main and ` +
    `${figures.filter((f) => !f.label.startsWith('Figure')).length} Extended Data figures, regenerated with every run scored as the ` +
    `public results site shows it, one panel at a time (${nPanels} panels): the question each panel answers, how it was ` +
    `generated, and what its evidence shows.`,
    { size: 24, color: INK2 }) }));
  const stamp = [meta.date && `Prepared ${meta.date}`,
    meta.site && `Scores as shown on goeckslab.github.io/galaxy-agent-benchmark on ${meta.site}`,
    meta.commit && `Run archive at commit ${meta.commit}${meta.branch ? ` (${meta.branch})` : ''}; figures in result_evaluation/figures/`].filter(Boolean);
  for (const s of stamp) c.push(new Paragraph({ children: [new TextRun({ text: s, size: 19, color: INK2 })], spacing: { after: 60 } }));

  // how to read
  c.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun('How to read this document')] }));
  c.push(body('Each panel has its own page with four parts:'));
  for (const [k, v] of [
    ['Title.', 'the question the panel answers.'],
    ['Panel.', 'the panel image, redrawn alone from the data its figure script recorded.'],
    ['Rationale.', 'how the panel was generated: the data and their source (**Data**), what is plotted (**Variables**), the estimators, intervals and tests (**Analysis**), and how to read the encodings (**Reading the plot**).'],
    ['Conclusion.', 'what the evidence shows in answer to the title, and where its inference stops.'],
  ]) c.push(new Paragraph({ numbering: { reference: 'bullets', level: 0 }, children: [new TextRun({ text: `${k} `, bold: true }), ...runs(v)], spacing: { after: 60, line: 276 } }));
  c.push(body('The figures were regenerated for this document in result_evaluation/figures/, with the manuscript figures\' own drawing and statistics code. Every run carries the score the public results site displays: BixBench-Verified-50 as graded on the site (two items, bix-53-q2 and bix-43-q2, regraded after the original evaluation; 27 runs), CompBioBench as on its official leaderboard, and IWC as shown per run, now including the host-read removal task. The 3,840 primary runs on 160 tasks are all scored. Run results were checked against the traces, submitted files and Galaxy histories. The repository\'s figures/ holds the same set; result_evaluation/figures/README.md lists every difference from the earlier set (figures/archive/2026-10-07_before_site_scores/).', { spacing: { before: 120, after: 120, line: 276 } }));
  c.push(body('The panels were not cropped from the figure images. split_panels.py redraws each composite figure from the panel data its script recorded and saves each panel alone; each redrawn composite matches its PNG pixel for pixel. Every number in the text comes from the figure\'s Source Data file (result_evaluation/figures/*_source_data.csv), its legend or the panel itself.', { spacing: { before: 0, after: 200, line: 276 } }));
  c.push(label('Shared definitions'));
  c.push(definitions());

  // contents
  c.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [new TextRun('Contents')] }));
  for (const f of figures) {
    c.push(contentsLine(`${f.label} | ${f.title}`, figAnchor(f), pages[figAnchor(f)], 0));
    for (const p of f.panels) c.push(contentsLine(`${p.label.replace(/^(Extended Data )?Fig\. /, (m, ed) => (ed ? 'ED ' : ''))}  ${p.question}`, anchorOf(p.id), pages[anchorOf(p.id)], 1));
  }

  // figures and panels
  for (const f of figures) {
    c.push(new Paragraph({ heading: HeadingLevel.HEADING_1, pageBreakBefore: true, children: [
      new Bookmark({ id: figAnchor(f), children: [new TextRun({ text: `${f.label} | `, color: BLUE }), new TextRun(f.title)] })] }));
    for (const t of f.intro) c.push(body(t));
    c.push(label('Panels in this figure'));
    for (const p of f.panels) c.push(new Paragraph({ numbering: { reference: 'bullets', level: 0 }, spacing: { after: 50 },
      children: [new InternalHyperlink({ anchor: anchorOf(p.id), children: [new TextRun({ text: `${p.label}  `, bold: true, color: BLUE }), ...runs(p.question)] })] }));

    for (const p of f.panels) {
      const entry = manifest[p.id];
      c.push(new Paragraph({ heading: HeadingLevel.HEADING_2, pageBreakBefore: true, keepNext: true, children: [
        new Bookmark({ id: anchorOf(p.id), children: [new TextRun({ text: `${p.label} | `, color: BLUE }), ...runs(p.question)] })] }));
      c.push(panelImage(entry));
      const letter = p.id.slice(-1);
      c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({
        text: `Panel ${letter} of result_evaluation/figures/${SOURCE[p.id.slice(0, -1)]}.pdf · image: result_evaluation/${entry.png}`, size: 15, color: INK2 })] }));
      c.push(label('Rationale'));
      for (const item of p.rationale) {
        c.push(item.kind === 'li'
          ? new Paragraph({ numbering: { reference: 'bullets', level: 0 }, children: runs(item.text), spacing: { after: 60, line: 264 } })
          : body(item.text));
      }
      c.push(label('Conclusion'));
      p.conclusion.forEach((item, i) => c.push(new Paragraph({
        children: runs(item.text),
        shading: { type: ShadingType.CLEAR, fill: TINT, color: 'auto' },
        border: { left: { style: BorderStyle.SINGLE, size: 18, color: BLUE, space: 8 } },
        indent: { left: 160, right: 80 },
        spacing: { before: i ? 0 : 60, after: 0, line: 276 },
      })));
    }
  }

  const doc = new Document({
    title: 'Galaxy Benchmark: figure-by-figure evaluation of the evidence',
    creator: 'Galaxy Benchmark',
    styles: {
      default: { document: { run: { font: FONT, size: 19, color: INK } } },
      paragraphStyles: [
        { id: 'Title', name: 'Title', basedOn: 'Normal', next: 'Normal', run: { font: FONT, size: 52, bold: true, color: INK }, paragraph: { spacing: { after: 120 } } },
        { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 30, bold: true, color: INK }, paragraph: { spacing: { after: 240 }, outlineLevel: 0 } },
        { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: FONT, size: 25, bold: true, color: INK }, paragraph: { spacing: { after: 60 }, outlineLevel: 1 } },
      ],
    },
    numbering: { config: [{ reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 300, hanging: 220 } } } }] }] },
    sections: [{
      properties: { page: { size: { width: PAGE.width, height: PAGE.height }, margin: { top: PAGE.margin, bottom: PAGE.margin, left: PAGE.margin, right: PAGE.margin } } },
      footers: { default: new Footer({ children: [new Paragraph({
        tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W }],
        children: [new TextRun({ text: 'Galaxy Benchmark · figure-by-figure evaluation', size: 15, color: INK2 }),
          new TextRun({ children: ['\t', PageNumber.CURRENT], size: 15, color: INK2 })] })] }) },
      children: c,
    }],
  });
  // heading text -> bookmark, so build.py can read each heading's page from the rendered PDF's outline
  const anchors = {};
  for (const f of figures) {
    anchors[`${f.label} | `] = figAnchor(f);
    for (const p of f.panels) anchors[`${p.label} | `] = anchorOf(p.id);
  }
  fs.mkdirSync(path.join(HERE, 'build'), { recursive: true });
  fs.writeFileSync(path.join(HERE, 'build', 'anchors.json'), JSON.stringify(anchors, null, 1));
  return Packer.toBuffer(doc).then(uniqueBookmarkIds).then((buf) => {
    fs.writeFileSync(OUT, buf);
    console.log(`wrote ${OUT}: ${figures.length} figures, ${nPanels} panels${Object.keys(pages).length ? ', with page numbers' : ''}`);
  });
}

build().catch((e) => { console.error(e.message); process.exit(1); });
