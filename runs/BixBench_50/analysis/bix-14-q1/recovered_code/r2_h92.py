import sys, zipfile, xml.etree.ElementTree as ET, re, os, io, math
NS = {'main':'http://schemas.openxmlformats.org/spreadsheetml/2006/main', 'rel':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
CODING_TERMS = {
    'synonymous_variant','missense_variant','stop_gained','stop_lost','start_lost',
    'frameshift_variant','inframe_insertion','inframe_deletion','protein_altering_variant',
    'coding_sequence_variant','stop_retained_variant','incomplete_terminal_codon_variant',
    'start_retained_variant','initiator_codon_variant'
}

def col_to_idx(cell_ref):
    m = re.match(r'([A-Z]+)', cell_ref or '')
    if not m:
        return None
    idx = 0
    for ch in m.group(1):
        idx = idx * 26 + (ord(ch) - 64)
    return idx - 1

def text_of(elem):
    if elem is None:
        return ''
    return ''.join(t.text or '' for t in elem.iter() if t.tag.endswith('}t') or t.tag == 't')

def read_shared(zf):
    try:
        root = ET.fromstring(zf.read('xl/sharedStrings.xml'))
    except KeyError:
        return []
    return [text_of(si) for si in root.findall('{%s}si' % NS['main'])]

def first_sheet_path(zf):
    wb = ET.fromstring(zf.read('xl/workbook.xml'))
    rels = ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
    rid_to_target = {rel.attrib['Id']: rel.attrib['Target'] for rel in rels}
    sheet = wb.find('{%s}sheets/{%s}sheet' % (NS['main'], NS['main']))
    rid = sheet.attrib.get('{%s}id' % NS['rel'])
    target = rid_to_target[rid]
    if target.startswith('/'):
        return target.lstrip('/')
    if target.startswith('xl/'):
        return target
    return 'xl/' + target

def cell_value(cell, shared):
    typ = cell.attrib.get('t')
    if typ == 's':
        v = cell.find('{%s}v' % NS['main'])
        if v is None or v.text is None:
            return ''
        return shared[int(v.text)]
    if typ == 'inlineStr':
        return text_of(cell)
    v = cell.find('{%s}v' % NS['main'])
    return '' if v is None or v.text is None else str(v.text)

def read_xlsx_rows(blob):
    rows = []
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        shared = read_shared(zf)
        sheet_path = first_sheet_path(zf)
        root = ET.fromstring(zf.read(sheet_path))
        for row in root.findall('.//{%s}row' % NS['main']):
            vals = {}
            max_idx = -1
            for cell in row.findall('{%s}c' % NS['main']):
                idx = col_to_idx(cell.attrib.get('r'))
                if idx is None:
                    continue
                vals[idx] = cell_value(cell, shared)
                max_idx = max(max_idx, idx)
            if max_idx >= 0:
                rows.append([vals.get(i, '') for i in range(max_idx + 1)])
    return rows

def norm(s):
    return str(s or '').strip()

def norm_id(s):
    s = norm(s)
    if re.fullmatch(r'\d+(?:\.0+)?', s):
        return str(int(float(s)))
    return s

def sample_from_name(name):
    base = os.path.basename(name)
    base = re.sub(r'\.xlsx$', '', base)
    sample = base.split('230209_Exome_GRCh38_CHIP_')[-1]
    if sample.startswith('SRR'):
        return sample
    return sample.split('-')[0]

def parse_float(s):
    try:
        return float(norm(s))
    except ValueError:
        return None

def split_terms(s):
    return {x.strip() for x in re.split(r'[,;|]', norm(s)) if x.strip()}

def nonempty_protein(s):
    s = norm(s)
    return bool(s and s not in {'.', '-', ','} and s.replace(',', '').strip())

def gene_overlap(gene_text, gene_set):
    genes = {g.strip() for g in re.split(r'[,;|]', norm(gene_text)) if g.strip()}
    return bool(genes & gene_set)

def table_dicts(rows, required_headers):
    for i, row in enumerate(rows[:10]):
        headers = [norm(x) for x in row]
        if all(h in headers for h in required_headers):
            return [
                {headers[j]: data[j] if j < len(data) else '' for j in range(len(headers)) if headers[j]}
                for data in rows[i+1:] if any(norm(x) for x in data)
            ]
    raise RuntimeError('Required headers not found: ' + ','.join(required_headers))

def main(archive_path):
    with zipfile.ZipFile(archive_path) as outer:
        names = outer.namelist()
        trio_name = 'inputs/230215_Trio_Status.xlsx'
        genes_name = 'inputs/230214_Schenz_et_al_2022_CHIP_Genes.xlsx'
        variant_names = sorted(n for n in names if n.startswith('inputs/CHIP_DP10_GQ20_PASS/') and n.endswith('.xlsx'))
        trio_recs = table_dicts(read_xlsx_rows(outer.read(trio_name)), ['Sample ID', 'BLM Mutation Status'])
        carrier_ids = {norm_id(r.get('Sample ID')) for r in trio_recs if norm(r.get('BLM Mutation Status')).lower() == 'carrier'}
        gene_rows = read_xlsx_rows(outer.read(genes_name))
        gene_set = {norm(r[0]) for r in gene_rows if r and norm(r[0])}

        selected_samples = []
        carrier_files = 0
        total_rows = chip_rows = vaf_rows = coding_below = synonymous_below = 0
        for name in variant_names:
            sample_id = sample_from_name(name)
            if norm_id(sample_id) not in carrier_ids:
                continue
            carrier_files += 1
            selected_samples.append(sample_id)
            recs = table_dicts(read_xlsx_rows(outer.read(name)), ['Chr:Pos', 'Variant Allele Freq', 'Sequence Ontology (Combined)', 'Gene Names'])
            for rec in recs:
                total_rows += 1
                in_chip = norm(rec.get('In_CHIP')).lower() == 'true' or gene_overlap(rec.get('Gene Names'), gene_set)
                if not in_chip:
                    continue
                chip_rows += 1
                vaf = parse_float(rec.get('Variant Allele Freq'))
                if vaf is None or not (vaf < 0.3):
                    continue
                vaf_rows += 1
                terms = split_terms(rec.get('Sequence Ontology (Combined)'))
                coding = bool(terms & CODING_TERMS) or nonempty_protein(rec.get('HGVS p. (Clinically Relevant)', ''))
                if not coding:
                    continue
                coding_below += 1
                if 'synonymous_variant' in terms:
                    synonymous_below += 1

    fraction = synonymous_below / coding_below if coding_below else float('nan')
    with open('answer.txt', 'w') as out:
        out.write(format(fraction, '.12g') + '\n')
    with open('audit.tsv', 'w') as out:
        out.write('metric\tvalue\n')
        rows = [
            ('carrier_sample_count_in_trio', len(carrier_ids)),
            ('carrier_variant_file_count', carrier_files),
            ('selected_samples', ','.join(selected_samples)),
            ('gene_count', len(gene_set)),
            ('carrier_variant_rows_total', total_rows),
            ('carrier_chip_rows', chip_rows),
            ('carrier_chip_rows_vaf_below_0_3', vaf_rows),
            ('coding_rows_vaf_below_0_3', coding_below),
            ('synonymous_coding_rows_vaf_below_0_3', synonymous_below),
            ('fraction', format(fraction, '.12g')),
        ]
        for k, v in rows:
            out.write(f'{k}\t{v}\n')

if __name__ == '__main__':
    main(sys.argv[1])
