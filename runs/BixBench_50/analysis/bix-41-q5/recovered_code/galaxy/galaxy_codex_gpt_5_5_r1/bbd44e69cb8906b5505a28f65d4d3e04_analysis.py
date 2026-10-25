import csv
import math
import sys
from collections import defaultdict

input_path = sys.argv[1]
output_path = 'swarm_similarity.tsv'

rows = []
with open(input_path, newline='') as handle:
    reader = csv.DictReader(handle)
    required = {'StrainNumber', 'Ratio', 'Area', 'Circularity'}
    missing = required.difference(reader.fieldnames or [])
    if missing:
        raise SystemExit('Missing required columns: ' + ','.join(sorted(missing)))
    for row in reader:
        rows.append(row)

if not rows:
    raise SystemExit('Input has no data rows')

groups = defaultdict(list)
for row in rows:
    key = (row['StrainNumber'], row['Ratio'])
    groups[key].append((float(row['Area']), float(row['Circularity'])))

def means(values):
    n = len(values)
    return (sum(v[0] for v in values) / n, sum(v[1] for v in values) / n, n)

summary = {key: means(values) for key, values in groups.items()}
strain1_keys = [key for key in summary if key[0] == '1']
if len(strain1_keys) != 1:
    raise SystemExit('Expected exactly one Strain 1 group, found %d' % len(strain1_keys))
target_key = strain1_keys[0]
target_area, target_circ, target_n = summary[target_key]

candidates = []
for (strain, ratio), (area, circ, n) in summary.items():
    if strain == '287_98':
        candidates.append({'ratio': ratio, 'mean_area': area, 'mean_circularity': circ, 'n': n})
if not candidates:
    raise SystemExit('No 287_98 mixed-culture ratio groups found')

areas = [target_area] + [c['mean_area'] for c in candidates]
circs = [target_circ] + [c['mean_circularity'] for c in candidates]
area_range = max(areas) - min(areas)
circ_range = max(circs) - min(circs)
if area_range == 0 or circ_range == 0:
    raise SystemExit('Cannot normalize a zero-range measurement')

for candidate in candidates:
    da = (candidate['mean_area'] - target_area) / area_range
    dc = (candidate['mean_circularity'] - target_circ) / circ_range
    candidate['normalized_distance'] = math.sqrt(da * da + dc * dc)

candidates.sort(key=lambda c: (c['normalized_distance'], c['ratio']))
answer = candidates[0]['ratio']

with open(output_path, 'w', newline='') as handle:
    writer = csv.writer(handle, delimiter='\t')
    writer.writerow(['answer_ratio', 'target_strain', 'target_ratio', 'target_n', 'target_mean_area', 'target_mean_circularity', 'candidate_ratio', 'candidate_n', 'candidate_mean_area', 'candidate_mean_circularity', 'normalized_distance'])
    for candidate in candidates:
        writer.writerow([
            answer,
            target_key[0],
            target_key[1],
            target_n,
            format(target_area, '.12g'),
            format(target_circ, '.12g'),
            candidate['ratio'],
            candidate['n'],
            format(candidate['mean_area'], '.12g'),
            format(candidate['mean_circularity'], '.12g'),
            format(candidate['normalized_distance'], '.12g'),
        ])
