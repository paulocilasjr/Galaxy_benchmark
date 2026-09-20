import sys, zipfile, re, statistics
from pathlib import PurePosixPath
from xml.etree import ElementTree as ET

NS = {'a': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}


def col_index(cell_ref):
    letters = ''.join(ch for ch in cell_ref if ch.isalpha())
    n = 0
    for ch in letters:
        n = n * 26 + ord(ch.upper()) - 64
    return n


def shared_strings(xlsx):
    try:
        data = xlsx.read('xl/sharedStrings.xml')
    except KeyError:
        return []
    root = ET.fromstring(data)
    out = []
    for si in root.findall('a:si', NS):
        out.append(''.join(t.text or '' for t in si.findall('.//a:t', NS)))
    return out


def sheet_rows(xlsx, sheet_name='xl/worksheets/sheet1.xml'):
    ss = shared_strings(xlsx)
    root = ET.fromstring(xlsx.read(sheet_name))
    rows = []
    for row in root.findall('.//a:sheetData/a:row', NS):
        vals = {}
        for c in row.findall('a:c', NS):
            idx = col_index(c.attrib['r'])
            typ = c.attrib.get('t')
            if typ == 'inlineStr':
                val = ''.join(t.text or '' for t in c.findall('.//a:t', NS))
            else:
                v = c.findtext('a:v', default='', namespaces=NS)
                if typ == 's' and v != '':
                    val = ss[int(v)]
                else:
                    val = v
            vals[idx] = val
        rows.append(vals)
    return rows


def first_sheet_rows(xlsx_bytes):
    with zipfile.ZipFile(xlsx_bytes) as xlsx:
        return sheet_rows(xlsx)


def norm(s):
    return str(s).strip() if s is not None else ''


def parse_float(s):
    s = norm(s)
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def parse_header(rows, header_row_index):
    header = rows[header_row_index]
    return {norm(v): k for k, v in header.items() if norm(v)}


def split_genes(text):
    return {tok.upper() for tok in re.split(r'[^A-Za-z0-9-]+', norm(text)) if tok}


def sample_id_from_name(name):
    base = PurePosixPath(name).name
    m = re.search(r'CHIP_(\d+)-', base)
    if not m:
        return None
    return m.group(1)


def median_value(values):
    vals = sorted(values)
    n = len(vals)
    if n == 0:
        raise ValueError('No carrier variant files were matched')
    mid = n // 2
    if n % 2:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2

archive_path = sys.argv[1]
with zipfile.ZipFile(archive_path) as archive:
    names = archive.namelist()

    status_name = next(n for n in names if n.endswith('230215_Trio_Status.xlsx'))
    genes_name = next(n for n in names if n.endswith('230214_Schenz_et_al_2022_CHIP_Genes.xlsx'))

    with archive.open(status_name) as fh:
        status_rows = first_sheet_rows(fh)
    status_header = parse_header(status_rows, 0)
    carriers = set()
    for row in status_rows[1:]:
        sid = norm(row.get(status_header['Sample ID']))
        if sid.endswith('.0'):
            sid = sid[:-2]
        if norm(row.get(status_header['BLM Mutation Status'])).lower() == 'carrier':
            carriers.add(sid)

    with archive.open(genes_name) as fh:
        gene_rows = first_sheet_rows(fh)
    chip_genes = {norm(row.get(1)).upper() for row in gene_rows if norm(row.get(1))}

    records = []
    matched_carriers = set()
    missing_files = sorted(carriers)
    for name in sorted(n for n in names if n.startswith('inputs/CHIP_DP10_GQ20_PASS/') and n.endswith('.xlsx')):
        sid = sample_id_from_name(name)
        if sid is None or sid not in carriers:
            continue
        matched_carriers.add(sid)
        with archive.open(name) as fh:
            rows = first_sheet_rows(fh)
        header = parse_header(rows, 1)
        required = ['Zygosity', 'Variant Allele Freq', 'Gene Names', 'Sequence Ontology (Combined)', 'Effect (Combined)']
        for req in required:
            if req not in header:
                raise ValueError(f'Missing required column {req} in {name}')
        count = 0
        seen_rows = 0
        for row in rows[2:]:
            seen_rows += 1
            zyg = norm(row.get(header['Zygosity']))
            if zyg.lower() == 'reference':
                continue
            location_text = (norm(row.get(header['Sequence Ontology (Combined)'])) + ' ' + norm(row.get(header['Effect (Combined)']))).lower()
            if 'intron' in location_text or 'intergenic' in location_text or 'utr' in location_text:
                continue
            vaf = parse_float(row.get(header['Variant Allele Freq']))
            if vaf is None or not (vaf < 0.3):
                continue
            gene_match = bool(split_genes(row.get(header['Gene Names'])) & chip_genes)
            in_chip = False
            if 'In_CHIP' in header:
                in_chip = norm(row.get(header['In_CHIP'])).lower() == 'true'
            if not (gene_match or in_chip):
                continue
            count += 1
        records.append((int(sid), count, seen_rows, PurePosixPath(name).name))

    counts = [r[1] for r in records]
    med = median_value(counts)

    with open('per_sample_counts.tsv', 'w') as out:
        out.write('sample_id\tchip_somatic_variant_count\tinput_variant_rows\tfile\n')
        for sid, count, seen_rows, base in sorted(records):
            out.write(f'{sid}\t{count}\t{seen_rows}\t{base}\n')

    if med == int(med):
        answer = str(int(med))
    else:
        answer = str(med)
    with open('answer.txt', 'w') as out:
        out.write(answer + '\n')

    with open('diagnostics.tsv', 'w') as out:
        out.write('metric\tvalue\n')
        out.write(f'carrier_ids_in_status\t{len(carriers)}\n')
        out.write(f'carrier_variant_files_matched\t{len(records)}\n')
        out.write(f'carrier_ids_without_variant_file\t{",".join(sorted(carriers - matched_carriers, key=lambda x:int(x) if x.isdigit() else x))}\n')
        out.write(f'chip_gene_count\t{len(chip_genes)}\n')
        out.write('filters\tBLM Mutation Status Carrier; CHIP gene or In_CHIP True; zygosity not Reference; sequence/effect not intron/intergenic/UTR; VAF < 0.3\n')
