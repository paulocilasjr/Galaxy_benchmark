import csv, math, sys

def kegg_id(gene):
    gene = gene.strip()
    if not gene:
        return ''
    return gene if ':' in gene else 'pau:' + gene

def parse_float(value):
    if value is None:
        return None
    v = value.strip()
    if not v or v.upper() == 'NA' or v.lower() == 'nan':
        return None
    try:
        x = float(v)
    except ValueError:
        return None
    if math.isnan(x):
        return None
    return x

def write_lists(in_path, fg_path, bg_path, summary_path):
    total = 0
    fg_count = 0
    bg_seen = set()
    fg_seen = set()
    with open(in_path, newline='') as handle:
        reader = csv.DictReader(handle, delimiter='\t')
        needed = {'rowname', 'log2FoldChange', 'padj'}
        missing = needed.difference(reader.fieldnames or [])
        if missing:
            raise SystemExit('Missing columns in %s: %s' % (in_path, ','.join(sorted(missing))))
        for row in reader:
            total += 1
            gid = kegg_id(row.get('rowname', ''))
            if gid:
                bg_seen.add(gid)
            lfc = parse_float(row.get('log2FoldChange'))
            padj = parse_float(row.get('padj'))
            if gid and lfc is not None and padj is not None and abs(lfc) > 1.5 and padj < 0.05:
                fg_seen.add(gid)
    with open(fg_path, 'w') as out:
        for gid in sorted(fg_seen):
            out.write(gid + '\n')
    with open(bg_path, 'w') as out:
        for gid in sorted(bg_seen):
            out.write(gid + '\n')
    with open(summary_path, 'w') as out:
        out.write('input\trows\tbackground_genes\tforeground_genes\n')
        out.write('%s\t%d\t%d\t%d\n' % (in_path, total, len(bg_seen), len(fg_seen)))

write_lists(sys.argv[1], 'glu_fe_fg.txt', 'glu_fe_bg.txt', 'glu_fe_summary.tsv')
write_lists(sys.argv[2], 'succ_fg.txt', 'succ_bg.txt', 'succ_summary.tsv')
