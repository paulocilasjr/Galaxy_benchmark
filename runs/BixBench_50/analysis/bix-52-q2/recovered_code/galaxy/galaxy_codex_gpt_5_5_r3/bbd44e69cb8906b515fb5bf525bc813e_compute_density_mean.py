import csv
import sys
from collections import defaultdict

jd_cpg_path = sys.argv[1]
jd_lengths_path = sys.argv[2]
out_path = sys.argv[3]

filtered = defaultdict(set)
with open(jd_cpg_path, newline='', encoding='utf-8-sig') as handle:
    reader = csv.DictReader(handle)
    required = {'Pos', 'MethylationPercentage', 'Chromosome'}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise SystemExit('missing CpG columns: ' + ','.join(sorted(missing)))
    for row in reader:
        methylation = float(row['MethylationPercentage'])
        if methylation > 90.0 or methylation < 10.0:
            chrom = row['Chromosome'].strip()
            pos = row['Pos'].strip()
            if chrom and pos:
                filtered[chrom].add(pos)

lengths = {}
with open(jd_lengths_path, newline='', encoding='utf-8-sig') as handle:
    reader = csv.DictReader(handle)
    required = {'Chromosome', 'Length'}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise SystemExit('missing length columns: ' + ','.join(sorted(missing)))
    for row in reader:
        chrom = row['Chromosome'].strip()
        if chrom:
            lengths[chrom] = int(row['Length'])

densities = []
for chrom, positions in filtered.items():
    if not positions:
        continue
    if chrom not in lengths:
        raise SystemExit('missing chromosome length for ' + chrom)
    densities.append(len(positions) / lengths[chrom])

if not densities:
    raise SystemExit('no filtered CpGs found')
answer = sum(densities) / len(densities)
with open(out_path, 'w', encoding='utf-8') as out:
    out.write(format(answer, '.17g') + '\n')
