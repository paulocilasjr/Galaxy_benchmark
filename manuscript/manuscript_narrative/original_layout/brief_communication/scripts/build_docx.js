// Build the Brief Communication and its Supplementary Information as Word files.
//
// Usage (from this folder's parent, after scripts/compute_numbers.py, make_figures.py and make_supplement.py):
//   NODE_PATH=<node_modules with docx> node scripts/build_docx.js <manuscript.docx> <Supplementary_Information.docx>
//
// Text: scripts/content.js (manuscript) and scripts/si_notes.js (Supplementary Notes); figures and tables:
// figures/ and supplementary/si_content.json; references: ../../references.json (Nature style, verified).
// Citations {cite:key} are numbered in Nature Methods order: main text, figure legends, then Methods with the data and
// code availability statements. The main reference list holds those first cited in the main text or legends; the
// Methods list continues the numbering. [[...]] marks an item the authors must supply (highlighted yellow).
const fs = require('fs');
const path = require('path');
const {
  AlignmentType, BorderStyle, Document, Footer, HeadingLevel, ImageRun, LineNumberRestartFormat, PageBreak,
  PageNumber, PageOrientation, Packer, Paragraph, ShadingType, Table, TableCell, TableRow, TextRun, WidthType,
} = require('docx');

const BC = path.dirname(__dirname);
const C = require('./content.js');
const { notes } = require('./si_notes.js');
const refs = JSON.parse(fs.readFileSync(path.join(BC, '..', '..', 'references.json'), 'utf8'));
const SI = JSON.parse(fs.readFileSync(path.join(BC, 'supplementary', 'si_content.json'), 'utf8'));
const [mainOut, siOut] = process.argv.slice(2).map((p) => path.resolve(p));

const FONT = 'Arial';
const SIZE = 24; // 12 pt
const DOUBLE = 480;
const PAGE = { width: 11906, height: 16838 }; // A4
const MARGIN = 1440;
const TEXT_W = PAGE.width - 2 * MARGIN;
const TEXT_W_LAND = PAGE.height - 2 * MARGIN;

// ------------------------------------------------------------------ citation numbering
const methodsText = C.methods.flatMap(([, ps]) => ps).concat([C.dataAvailability, C.codeAvailability]);
const order = [];
const firstIn = {};
for (const [where, texts] of [['main', C.main], ['legends', C.legends.map((l) => l.body)], ['methods', methodsText]]) {
  for (const t of texts) {
    for (const m of t.matchAll(/\{cite:([^}]+)\}/g)) {
      for (const k of m[1].split(',').map((s) => s.trim())) {
        if (!refs[k]) throw new Error(`Unknown reference key: ${k}`);
        if (!order.includes(k)) { order.push(k); firstIn[k] = where; }
      }
    }
  }
}
if (/\{cite:/.test(C.abstract)) throw new Error('The abstract must be unreferenced');
const num = Object.fromEntries(order.map((k, i) => [k, i + 1]));
const mainRefs = order.filter((k) => firstIn[k] !== 'methods');
const methodsRefs = order.filter((k) => firstIn[k] === 'methods');

function compress(ns) {
  ns = [...new Set(ns)].sort((a, b) => a - b);
  const out = [];
  for (let i = 0; i < ns.length; i++) {
    let j = i;
    while (j + 1 < ns.length && ns[j + 1] === ns[j] + 1) j++;
    out.push(j - i >= 2 ? `${ns[i]}–${ns[j]}` : j > i ? `${ns[i]},${ns[j]}` : `${ns[i]}`);
    i = j;
  }
  return out.join(',');
}

// ------------------------------------------------------------------ inline formatting and word counts
function runs(text, base = {}) {
  const out = [];
  const re = /(\{cite:[^}]+\}|\[\[[^\]]+\]\]|\*\*[^*]+\*\*|\*[^*\s][^*]*\*)/g;
  let last = 0;
  const plain = (t, b) => new TextRun({ text: t, font: FONT, ...b });
  for (const m of text.matchAll(re)) {
    if (m.index > last) out.push(plain(text.slice(last, m.index), base));
    const t = m[0];
    if (t.startsWith('{cite:')) {
      out.push(plain(compress(t.slice(6, -1).split(',').map((k) => num[k.trim()])), { ...base, superScript: true }));
    } else if (t.startsWith('[[')) {
      out.push(plain(`[${t.slice(2, -2)}]`, { ...base, highlight: 'yellow' }));
    } else if (t.startsWith('**')) {
      out.push(...runs(t.slice(2, -2), { ...base, bold: true }));
    } else {
      out.push(...runs(t.slice(1, -1), { ...base, italics: true }));
    }
    last = m.index + t.length;
  }
  if (last < text.length) out.push(plain(text.slice(last), base));
  return out;
}

const words = (t) => t.replace(/\{cite:[^}]+\}/g, '').replace(/[*]/g, '').split(/\s+/)
  .filter((w) => /[A-Za-z0-9]/.test(w)).length;

// ------------------------------------------------------------------ blocks
const P = (text, opt = {}) => new Paragraph({ spacing: { after: 0, line: opt.line || DOUBLE }, ...opt.para,
  children: runs(text, opt.run || {}) });
const H1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120, line: DOUBLE },
  children: runs(text, { bold: true }) });
const H2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 120, after: 0, line: DOUBLE },
  children: runs(text, { bold: true }) });
const pageBreak = () => new Paragraph({ children: [new PageBreak()] });
const indented = (text, opt = {}) => P(text, { ...opt, para: { indent: { firstLine: 360 } } });

function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function image(file, maxW, maxH, alt) {
  const { w, h } = pngSize(file);
  let width = Math.floor((maxW / 1440) * 96);
  let height = Math.round((width * h) / w);
  const cap = Math.floor((maxH / 1440) * 96);
  if (height > cap) { width = Math.round((width * cap) / height); height = cap; }
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(file), transformation: { width, height },
      altText: { title: alt, description: alt, name: path.basename(file) } })] });
}

function refList(keys) {
  return keys.map((k) => new Paragraph({ spacing: { after: 0, line: DOUBLE }, indent: { left: 432, hanging: 432 },
    children: [new TextRun({ text: `${num[k]}.\t`, font: FONT }), ...runs(refs[k])],
    tabStops: [{ type: 'left', position: 432 }] }));
}

function table(t, width, size = 15) {
  const n = t.header.length;
  // column weight: longest cell (capped) or longest header word, whichever is larger
  const weight = t.header.map((h, i) => Math.max(8, ...h.split(/\s+/).map((w) => w.length + 2),
    ...t.rows.map((r) => Math.min(String(r[i]).length, i === 0 && t.transposed ? 18 : 48))));
  const total = weight.reduce((a, b) => a + b, 0);
  const colW = weight.map((x) => Math.floor((x / total) * width));
  const border = { style: BorderStyle.SINGLE, size: 4, color: '9a9a9a' };
  const cell = (text, ci, head) => new TableCell({
    width: { size: colW[ci], type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: 'E9EEF3', color: 'auto' } : undefined,
    borders: { top: border, bottom: border, left: border, right: border },
    margins: { top: 40, bottom: 40, left: 70, right: 70 },
    children: [new Paragraph({ spacing: { line: 240 }, children: runs(String(text), { size, bold: head || (ci === 0
      && t.transposed) }) })],
  });
  return new Table({
    width: { size: colW.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: colW,
    rows: [new TableRow({ tableHeader: true, children: t.header.map((h, i) => cell(h, i, true)) }),
      ...t.rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, i, false)) }))],
  });
}

const styles = {
  default: { document: { run: { font: FONT, size: SIZE, color: '000000' } } },
  paragraphStyles: [
    { id: 'Title', name: 'Title', basedOn: 'Normal', run: { font: FONT, size: 32, bold: true, color: '000000' } },
    { id: 'Heading1', name: 'heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run: { font: FONT, size: 26, bold: true, color: '000000' }, paragraph: { keepNext: true, outlineLevel: 0 } },
    { id: 'Heading2', name: 'heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
      run: { font: FONT, size: SIZE, bold: true, color: '000000' }, paragraph: { keepNext: true, outlineLevel: 1 } },
  ],
};
const footer = () => ({ default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
  suppressLineNumbers: true, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })] })] }) });
const portrait = { page: { size: PAGE, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } };
const landscape = { page: { size: { ...PAGE, orientation: PageOrientation.LANDSCAPE },
  margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } } };

// ------------------------------------------------------------------ manuscript
function manuscript() {
  const count = {
    abstract: words(C.abstract),
    main: C.main.reduce((a, p) => a + words(p), 0),
    legends: C.legends.reduce((a, l) => a + words(l.title) + words(l.body), 0),
    references: mainRefs.reduce((a, k) => a + words(refs[k]), 0),
    methods: methodsText.reduce((a, p) => a + words(p), 0) + C.methods.reduce((a, [h]) => a + words(h), 0),
  };
  count.total = count.abstract + count.main + count.legends + count.references;
  const ch = [];
  ch.push(P('Brief Communication', { run: { color: '555555' } }));
  ch.push(new Paragraph({ heading: HeadingLevel.TITLE, spacing: { before: 240, after: 240, line: 360 },
    children: runs(C.title, { size: 32, bold: true }) }));
  for (const k of ['authors', 'affiliations', 'correspondence']) ch.push(P(C.front[k]));
  ch.push(P(''));
  ch.push(P(`Word counts: abstract ${count.abstract}; main text ${count.main}; figure legends ${count.legends}; ` +
    `main-text references ${count.references} (${mainRefs.length} references); total ${count.total}. ` +
    `Methods ${count.methods} (${methodsRefs.length} further references). Display items: 2 figures. Supplementary ` +
    `Information: 11 Supplementary Figures, 6 Supplementary Tables and 3 Supplementary Notes; Supplementary Data 1 and 2; ` +
    `Source Data for Figs. 1 and 2.`, { run: { size: 20, color: '444444' } }));
  ch.push(pageBreak());

  ch.push(H1('Abstract'));
  ch.push(P(C.abstract));
  ch.push(P('')); // Brief Communications have no headings in the main text
  C.main.forEach((p, i) => ch.push(i === 0 ? P(p) : indented(p)));

  ch.push(H1('References'));
  ch.push(...refList(mainRefs));

  ch.push(pageBreak());
  ch.push(H1('Methods'));
  for (const [h, ps] of C.methods) {
    ch.push(H2(h));
    ps.forEach((p, i) => ch.push(i === 0 ? P(p) : indented(p)));
  }
  ch.push(H2('Reporting summary'));
  ch.push(P(C.reporting));
  ch.push(H1('Data availability'));
  ch.push(P(C.dataAvailability));
  ch.push(H1('Code availability'));
  ch.push(P(C.codeAvailability));
  ch.push(H1('Methods references'));
  ch.push(...refList(methodsRefs));
  for (const [h, text] of C.endMatter) {
    ch.push(H1(h));
    ch.push(P(text));
  }

  for (const l of C.legends) {
    ch.push(pageBreak());
    ch.push(image(path.join(BC, 'figures', l.file), TEXT_W, 7600, l.title));
    ch.push(P(`**${l.title}** ${l.body}`, { line: 360 }));
  }

  const doc = new Document({
    creator: '[Authors]', title: C.title, styles,
    sections: [{ properties: { ...portrait, lineNumbers: { countBy: 1, restart: LineNumberRestartFormat.CONTINUOUS } },
      footers: footer(), children: ch }],
  });
  return Packer.toBuffer(doc).then((buf) => {
    fs.writeFileSync(mainOut, buf);
    console.log(`wrote ${mainOut}`);
    console.log(`  ${JSON.stringify(count)}`);
    console.log(`  references: ${mainRefs.length} main text and legends, ${methodsRefs.length} Methods only`);
  });
}

// ------------------------------------------------------------------ Supplementary Information
function supplement() {
  const sec1 = [];
  sec1.push(P('Supplementary Information', { run: { color: '555555' } }));
  sec1.push(new Paragraph({ heading: HeadingLevel.TITLE, spacing: { before: 240, after: 240, line: 360 },
    children: runs(C.title, { size: 32, bold: true }) }));
  sec1.push(P(C.front.authors, { line: 360 }));
  sec1.push(P(''));
  sec1.push(H1('Contents'));
  const line = (t) => P(t, { line: 300, run: { size: 20 } });
  for (const f of SI.figures) sec1.push(line(`Supplementary Fig. ${f.n} | ${f.title}`));
  for (const t of SI.tables) sec1.push(line(`Supplementary Table ${t.n} | ${t.title}`));
  for (const n of notes) sec1.push(line(`Supplementary Note ${n.n} | ${n.title}`));
  sec1.push(line('Supplementary Data 1 | Source data of Supplementary Figs. 1–11 (Excel workbook, one sheet per figure; ' +
    'provided separately).'));
  sec1.push(line('Supplementary Data 2 | Run index: every run with links to its agent trace, its results-site page and, ' +
    'for Galaxy runs, its Galaxy history, with the result of an access check (Excel workbook; provided separately).'));
  sec1.push(P(''));
  sec1.push(P('In the Supplementary Figures, IWC denotes the IWC-derived tasks and custom code the condition in which ' +
    'the agent installed software and wrote its own code. A run is correct when accepted (BixBench-Verified-50), when ' +
    'it agrees with the answer key (CompBioBench) or at output agreement ≥ 0.99 (IWC-derived tasks). Supplementary ' +
    'Tables 1–6 are also provided as an Excel workbook.', { line: 300, run: { size: 20 } }));

  for (const f of SI.figures) {
    sec1.push(pageBreak());
    // leave room for the legend on the same page (9-pt text: about 112 characters per 13-pt line)
    const legendLines = f.body.reduce((acc, l) => acc + Math.ceil(l.length / 112), 2);
    const room = PAGE.height - 2 * MARGIN - 400 - legendLines * 262;
    sec1.push(image(path.join(BC, f.file), TEXT_W, Math.max(room, 4200), `Supplementary Fig. ${f.n}`));
    const body = [];
    for (const l of f.body) {
      if (l.startsWith('- ')) body.push(new Paragraph({ spacing: { line: 260 }, indent: { left: 360, hanging: 200 },
        children: runs(`– ${l.slice(2)}`, { size: 18 }) }));
      else body.push(new Paragraph({ spacing: { line: 260 }, children: runs(l, { size: 18 }) }));
    }
    sec1.push(new Paragraph({ spacing: { line: 260, before: 60 }, keepNext: true,
      children: runs(`**Supplementary Fig. ${f.n} | ${f.title}**`, { size: 18 }) }));
    sec1.push(...body);
  }

  const sec2 = [];
  SI.tables.forEach((t, i) => {
    if (i) sec2.push(pageBreak());
    sec2.push(new Paragraph({ spacing: { after: 80, line: 276 },
      children: runs(`**Supplementary Table ${t.n} | ${t.title}**`, { size: 20 }) }));
    sec2.push(new Paragraph({ spacing: { after: 160, line: 260 }, children: runs(t.legend, { size: 18 }) }));
    sec2.push(table(t, TEXT_W_LAND, [3, 6].includes(t.n) ? 14 : 15));
  });

  const sec3 = [];
  for (const n of notes) {
    if (n.n > 1) sec3.push(pageBreak());
    sec3.push(H1(`Supplementary Note ${n.n} | ${n.title}`));
    n.paragraphs.forEach((p) => sec3.push(new Paragraph({ spacing: { after: 160, line: 360 }, children: runs(p) })));
  }

  const doc = new Document({
    creator: '[Authors]', title: `Supplementary Information: ${C.title}`, styles,
    sections: [
      { properties: portrait, footers: footer(), children: sec1 },
      { properties: landscape, footers: footer(), children: sec2 },
      { properties: portrait, footers: footer(), children: sec3 },
    ],
  });
  return Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(siOut, buf); console.log(`wrote ${siOut}`); });
}

manuscript().then(supplement);
