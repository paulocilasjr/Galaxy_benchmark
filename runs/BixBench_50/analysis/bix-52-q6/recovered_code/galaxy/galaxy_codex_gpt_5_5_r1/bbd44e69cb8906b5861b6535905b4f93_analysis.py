import csv
import sys

age_path, length_path, result_path, answer_path = sys.argv[1:5]

sites_by_chrom = {}
with open(age_path, encoding='utf-8-sig', newline='') as handle:
    reader = csv.DictReader(handle)
    required = {'Pos', 'Chromosome', 'StartPosition', 'EndPosition'}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise SystemExit('Missing required CpG columns: ' + ','.join(sorted(missing)))
    for row in reader:
        chrom = row['Chromosome'].strip()
        if not chrom or chrom.upper() == 'MT':
            continue
        pos = row['Pos'].strip()
        if pos:
            key = pos
        else:
            key = chrom + ':' + row['StartPosition'].strip() + '-' + row['EndPosition'].strip()
        sites_by_chrom.setdefault(chrom, set()).add(key)

rows = []
with open(length_path, encoding='utf-8-sig', newline='') as handle:
    reader = csv.DictReader(handle)
    required = {'Chromosome', 'Length'}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise SystemExit('Missing required length columns: ' + ','.join(sorted(missing)))
    for row in reader:
        chrom = row['Chromosome'].strip()
        if not chrom or chrom.upper() == 'MT':
            continue
        length = int(row['Length'])
        count = len(sites_by_chrom.get(chrom, set()))
        density = count / length if length else 0.0
        rows.append((chrom, count, length, density))

if not rows:
    raise SystemExit('No chromosome rows were available after filtering')

rows.sort(key=lambda item: (-item[3], item[0]))
with open(result_path, 'w', encoding='utf-8', newline='') as handle:
    writer = csv.writer(handle, delimiter='\t', lineterminator='\n')
    writer.writerow(['Chromosome', 'UniqueAgeRelatedCpGSites', 'Length', 'Density'])
    for chrom, count, length, density in rows:
        writer.writerow([chrom, count, length, format(density, '.12g')])

with open(answer_path, 'w', encoding='utf-8', newline='') as handle:
    handle.write(rows[0][0] + '\n')
