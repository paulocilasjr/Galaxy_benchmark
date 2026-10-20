import csv
import math
import sys

iron_in, innate_in = sys.argv[1], sys.argv[2]

def parse_float(value):
    if value is None or value == '' or value.upper() == 'NA':
        return math.nan
    return float(value)

def write_lists(infile, fg_out, bg_out):
    with open(infile, newline='') as handle, \
         open(fg_out, 'w', newline='') as fg, \
         open(bg_out, 'w', newline='') as bg:
        reader = csv.DictReader(handle, delimiter='\t')
        if reader.fieldnames is None:
            raise SystemExit(f'{infile}: no header')
        required = {'rowname', 'log2FoldChange', 'padj'}
        missing = required.difference(reader.fieldnames)
        if missing:
            raise SystemExit(f'{infile}: missing columns {sorted(missing)}')
        fg.write('gene_id\n')
        bg.write('gene_id\n')
        for row in reader:
            gene = row['rowname'].strip()
            if not gene:
                continue
            bg.write(gene + '\n')
            lfc = parse_float(row['log2FoldChange'])
            padj = parse_float(row['padj'])
            if math.isfinite(lfc) and math.isfinite(padj) and abs(lfc) > 1.5 and padj < 0.05:
                fg.write(gene + '\n')

write_lists(iron_in, 'iron_foreground.tsv', 'iron_background.tsv')
write_lists(innate_in, 'innate_foreground.tsv', 'innate_background.tsv')
