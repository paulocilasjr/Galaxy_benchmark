// Build a manuscript .docx from a paper directory's manuscript.md.
//
// Usage (from the repository root):
//   node manuscript_narrative/build_docx.js manuscript_narrative/user-oriented <output.docx> [markdown file in the paper dir]
// Requires the `docx` npm package (see manuscript_narrative/package.json; or set NODE_PATH to a node_modules that has it).
//
// Markdown subset: '# ' title, '## ' and '### ' headings, paragraphs, '- ' bullets, pipe tables, '\newpage',
// inline **bold**, *italic*, ^superscript^, `code`, citations [@key;@key2], '[Authors: ...]' placeholders (highlighted),
// '## [Name]' hidden section headings (e.g. the unheaded introduction), <!-- comments --> (dropped), {{key}} numbers (filled from the paper's numbers.json; an unknown key is an error), and the
// markers [[REFERENCES]], [[METHODS_REFERENCES]], [[FIGURES]] and [[ED_FIGURES]].
//
// Reference numbering follows Nature Methods: main text, then figure legends, then Methods (with the data and code
// availability statements), then Extended Data legends. [[REFERENCES]] lists the references first cited in the main text
// or main figure legends; [[METHODS_REFERENCES]] lists the rest, continuing the numbering.
const fs = require('fs');
const path = require('path');
const {
  AlignmentType, BorderStyle, Document, Footer, HeadingLevel, ImageRun, LevelFormat, LineNumberRestartFormat, PageBreak,
  PageNumber, Packer, Paragraph, ShadingType, Table, TableCell, TableRow, TextRun, WidthType,
} = require('docx');

const paperDir = path.resolve(process.argv[2]);
const outPath = path.resolve(process.argv[3]);
const mdFile = process.argv[4] || 'manuscript.md'; // relative to the paper directory, e.g. supplementary/Supplementary_Note_1.md
const numbers = JSON.parse(fs.readFileSync(path.join(paperDir, 'numbers.json'), 'utf8'));
let md = fs.readFileSync(path.join(paperDir, mdFile), 'utf8').replace(/<!--[\s\S]*?-->/g, '');
md = md.replace(/\\newpage\s*\n\s*## Figures\s*\n/g, '\n');
const authorFile = path.join(__dirname, 'author_metadata.json');
const authorFields = fs.existsSync(authorFile) ? JSON.parse(fs.readFileSync(authorFile, 'utf8')).fields || {} : {};
md = md.replace(/\[Authors:\s*([^\]]+)\]/g, (placeholder, field) => {
  const value = authorFields[field.trim()];
  return typeof value === 'string' && value.trim() ? value.trim() : placeholder;
});
md = md.replace(/\{\{([A-Za-z0-9_.-]+)\}\}/g, (_, k) => {
  if (!(k in numbers)) throw new Error(`Unknown number key: {{${k}}}`);
  return String(numbers[k]);
});
if (/\{\{|\}\}/.test(md)) throw new Error('Unfilled {{ }} placeholder');
const refs = JSON.parse(fs.readFileSync(path.join(__dirname, 'references.json'), 'utf8'));

const FONT = 'Arial';
const PAGE_W = 11906; // A4, twentieths of a point
const MARGIN = 1440;
const CONTENT_W = PAGE_W - 2 * MARGIN;

// ------------------------------------------------------------------ sections and citation numbering
function sectionClass(heading) {
  if (/^Figure legends/i.test(heading)) return 'legends';
  if (/^Extended Data/i.test(heading)) return 'ed';
  if (/^(Methods|Online Methods|Data availability|Code availability)/i.test(heading)) return 'methods';
  if (/^(References|Methods references|Acknowledgements|Author contributions|Competing interests|Additional information|Supplementary)/i.test(heading)) return 'other';
  return 'main';
}
const sections = { main: [], legends: [], methods: [], ed: [], other: [] };
const wordCounts = { abstract: 0, main: 0, legends: [] };
{
  let cls = 'main';
  let heading = '';
  for (const line of md.split('\n')) {
    if (line.startsWith('## ')) { heading = line.slice(3).trim().replace(/^\[(.*)\]$/, '$1'); cls = sectionClass(heading); continue; }
    if (line.startsWith('# ')) continue;
    if (/^\[\[(REFERENCES|METHODS_REFERENCES|FIGURES|ED_FIGURES)\]\]$/.test(line.trim()) || line.trim() === '\\newpage') continue;
    sections[cls].push(line);
    const words = line.replace(/\[@[^\]]+\]/g, '').split(/\s+/).filter((w) => /[A-Za-z0-9]/.test(w)).length;
    if (heading === 'Abstract') wordCounts.abstract += words;
    else if (cls === 'main' && heading && !line.startsWith('###') && !line.startsWith('|')) wordCounts.main += words;
    if (cls === 'legends' && /^\*\*Fig\. \d/.test(line)) wordCounts.legends.push(words);
  }
}
const order = [];
const firstClass = {};
for (const cls of ['main', 'legends', 'methods', 'ed', 'other']) {
  for (const m of sections[cls].join('\n').matchAll(/\[@([^\]]+)\]/g)) {
    for (const k of m[1].split(';').map((x) => x.trim().replace(/^@/, ''))) {
      if (!refs[k]) throw new Error(`Unknown reference key: ${k}`);
      if (!order.includes(k)) { order.push(k); firstClass[k] = cls; }
    }
  }
}
const num = Object.fromEntries(order.map((k, i) => [k, i + 1]));
const mainRefs = order.filter((k) => ['main', 'legends'].includes(firstClass[k]));
const methodsRefs = order.filter((k) => !['main', 'legends'].includes(firstClass[k]));

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

// ------------------------------------------------------------------ inline formatting
function runs(text, base = {}) {
  const out = [];
  const re = /(\[@[^\]]+\]|\*\*[^*]+\*\*|\*[^*\s][^*]*\*|\^[^^]+\^|`[^`]+`|\[Authors:[^\]]*\])/g;
  let last = 0;
  for (const m of text.matchAll(re)) {
    if (m.index > last) out.push(new TextRun({ text: text.slice(last, m.index), font: FONT, ...base }));
    const t = m[0];
    if (t.startsWith('[@')) {
      const ns = t.slice(2, -1).split(';').map((s) => num[s.trim().replace(/^@/, '')]);
      out.push(new TextRun({ text: compress(ns), superScript: true, font: FONT, ...base }));
    } else if (t.startsWith('**')) {
      out.push(...runs(t.slice(2, -2), { ...base, bold: true }));
    } else if (t.startsWith('[Authors:')) {
      out.push(new TextRun({ text: t, highlight: 'yellow', font: FONT, ...base }));
    } else if (t.startsWith('*')) {
      out.push(...runs(t.slice(1, -1), { ...base, italics: true }));
    } else if (t.startsWith('^')) {
      out.push(new TextRun({ text: t.slice(1, -1), superScript: true, font: FONT, ...base }));
    } else if (t.startsWith('`')) {
      out.push(new TextRun({ text: t.slice(1, -1), font: 'Courier New', ...base, size: (base.size || 22) - 2 }));
    }
    last = m.index + t.length;
  }
  if (last < text.length) out.push(new TextRun({ text: text.slice(last), font: FONT, ...base }));
  return out;
}

// ------------------------------------------------------------------ blocks
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function tableBlock(lines) {
  const rows = lines.filter((l) => !/^\|\s*-/.test(l)).map((l) => l.trim().replace(/^\||\|$/g, '').split('|').map((c) => c.trim()));
  const n = rows[0].length;
  const widths = n === 4 ? [0.22, 0.34, 0.22, 0.22] : Array(n).fill(1 / n);
  const colW = widths.map((f) => Math.floor(f * CONTENT_W));
  const border = { style: BorderStyle.SINGLE, size: 4, color: '999999' };
  return new Table({
    width: { size: colW.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: colW,
    rows: rows.map((r, ri) => new TableRow({
      tableHeader: ri === 0,
      children: r.map((c, ci) => new TableCell({
        width: { size: colW[ci], type: WidthType.DXA },
        shading: ri === 0 ? { type: ShadingType.CLEAR, fill: 'E8EEF4', color: 'auto' } : undefined,
        borders: { top: border, bottom: border, left: border, right: border },
        margins: { top: 60, bottom: 60, left: 80, right: 80 },
        children: [new Paragraph({ spacing: { line: 240 }, children: runs(c, { size: 16, bold: ri === 0 }) })],
      })),
    })),
  });
}

function figurePages(prefix) {
  // prefix 'Fig' for main figures, 'ED_Fig' for Extended Data figures
  const dir = path.join(paperDir, 'figures', 'previews');
  const re = new RegExp(`^${prefix}(\\d+)\\.png$`);
  const files = fs.readdirSync(dir).filter((f) => re.test(f)).sort((a, b) => parseInt(a.match(re)[1]) - parseInt(b.match(re)[1]));
  const out = [];
  files.forEach((f) => {
    const n = f.match(re)[1];
    const label = prefix === 'Fig' ? `Fig. ${n}` : `Extended Data Fig. ${n}`;
    const { w, h } = pngSize(path.join(dir, f));
    let width = Math.floor(CONTENT_W * 96 / 1440); // fit the actual A4 text block at 96 dpi
    let height = Math.round((width * h) / w);
    if (height > 860) { width = Math.round((width * 860) / height); height = 860; }
    out.push(new Paragraph({ children: [new PageBreak()] }));
    out.push(new Paragraph({ children: runs(`**${label}**`) }));
    out.push(new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new ImageRun({ type: 'png', data: fs.readFileSync(path.join(dir, f)), transformation: { width, height },
        altText: { title: label, description: label, name: f } })],
    }));
  });
  return out;
}

function refList(keys) {
  return keys.map((k) => new Paragraph({ spacing: { after: 80, line: 276 },
    children: [new TextRun({ text: `${num[k]}. `, font: FONT }), ...runs(refs[k])] }));
}

const children = [];
const lines = md.split('\n');
let para = [];
function flush() {
  if (!para.length) return;
  children.push(new Paragraph({ spacing: { after: 160, line: 360 }, children: runs(para.join(' ')) }));
  para = [];
}
for (let i = 0; i < lines.length; i++) {
  const line = lines[i];
  if (line.startsWith('|')) {
    flush();
    const tl = [];
    while (i < lines.length && lines[i].startsWith('|')) tl.push(lines[i++]);
    i--;
    children.push(tableBlock(tl));
    children.push(new Paragraph({ spacing: { after: 160 }, children: [] }));
  } else if (line.startsWith('# ')) {
    flush();
    children.push(new Paragraph({ heading: HeadingLevel.TITLE, spacing: { after: 240 }, children: runs(line.slice(2), { size: 32, bold: true }) }));
  } else if (/^## \[.*\]\s*$/.test(line)) {
    flush(); // hidden heading: marks a section (e.g. the unheaded introduction) without printing it
  } else if (/^## (Figures|Extended Data figures)\s*$/.test(line)) {
    flush(); // Figure pages have their own labels; avoid a heading-only page before the page break.
  } else if (line.startsWith('## ')) {
    flush();
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_1, spacing: { before: 240, after: 120 }, children: runs(line.slice(3), { size: 26, bold: true }) }));
  } else if (line.startsWith('### ')) {
    flush();
    children.push(new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 200, after: 100 }, children: runs(line.slice(4), { size: 23, bold: true }) }));
  } else if (line.startsWith('- ')) {
    flush();
    children.push(new Paragraph({ numbering: { reference: 'bullets', level: 0 }, spacing: { line: 360 }, children: runs(line.slice(2)) }));
  } else if (line.trim() === '\\newpage') {
    flush();
    children.push(new Paragraph({ children: [new PageBreak()] }));
  } else if (line.trim() === '[[REFERENCES]]') {
    flush();
    children.push(...refList(mainRefs));
  } else if (line.trim() === '[[METHODS_REFERENCES]]') {
    flush();
    children.push(...refList(methodsRefs));
  } else if (line.trim() === '[[FIGURES]]') {
    flush();
    children.push(...figurePages('Fig'));
  } else if (line.trim() === '[[ED_FIGURES]]') {
    flush();
    children.push(...figurePages('ED_Fig'));
  } else if (!line.trim()) {
    flush();
  } else {
    para.push(line.trim());
  }
}
flush();

const doc = new Document({
  creator: 'Galaxy benchmark project',
  title: md.split('\n')[0].replace(/^# /, ''),
  styles: {
    default: { document: { run: { font: FONT, size: 22, color: '000000' } } },
    paragraphStyles: [
      { id: 'Title', name: 'Title', basedOn: 'Normal', run: { font: FONT, color: '000000', size: 32, bold: true } },
      { id: 'Heading1', name: 'heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, color: '000000', size: 26, bold: true }, paragraph: { keepNext: true } },
      { id: 'Heading2', name: 'heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, color: '000000', size: 23, bold: true }, paragraph: { keepNext: true } },
    ],
  },
  numbering: { config: [{ reference: 'bullets', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] }] },
  sections: [{
    properties: {
      page: { size: { width: PAGE_W, height: 16838 }, margin: { top: MARGIN, bottom: MARGIN, left: MARGIN, right: MARGIN } },
      lineNumbers: { countBy: 1, restart: LineNumberRestartFormat.CONTINUOUS },
    },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, suppressLineNumbers: true,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })] })] }) },
    children,
  }],
});
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(outPath, buf);
  console.log(`wrote ${outPath}`);
  console.log(`  abstract ${wordCounts.abstract} words; main text ${wordCounts.main} words (introduction, Results, Discussion)`);
  console.log(`  ${wordCounts.legends.length} main figure legends (${wordCounts.legends.join(', ')} words)`);
  console.log(`  references: ${mainRefs.length} main text and legends, ${methodsRefs.length} Methods and Extended Data only`);
});
