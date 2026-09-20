import csv
import math
import os
import re
import statistics
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

zip_path = sys.argv[1]
per_path = sys.argv[2]
answer_path = sys.argv[3]
failed_path = sys.argv[4]

num_re = re.compile(r'[-+]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][-+]?\d+)?')


def read_fasta_lengths(path):
    seqs = []
    current = []
    with open(path, 'r', encoding='utf-8', errors='replace') as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith('>'):
                if current:
                    seqs.append(''.join(current))
                    current = []
            else:
                current.append(line)
        if current:
            seqs.append(''.join(current))
    if not seqs:
        raise ValueError('no FASTA sequences')
    lengths = {len(s) for s in seqs}
    if len(lengths) != 1:
        raise ValueError('sequences have unequal aligned lengths: ' + ','.join(map(str, sorted(lengths))))
    return len(seqs), lengths.pop()


def parse_phykit(raw, aln_len):
    vals = [float(m.group(0)) for m in num_re.finditer(raw)]
    if not vals:
        raise ValueError('no numeric values in PhyKit output: ' + raw.strip())
    expected = []
    for i, val in enumerate(vals):
        rounded = round(val)
        if abs(val - rounded) < 1e-9 and 0 <= rounded <= aln_len:
            pct = rounded / aln_len * 100.0 if aln_len else 0.0
            score = 10.0
            source = 'derived_from_count'
            if i + 1 < len(vals):
                cand = vals[i + 1]
                cand_pct = cand * 100.0 if 0 <= cand <= 1 and pct > 1 else cand
                if 0 <= cand_pct <= 100 and abs(cand_pct - pct) <= 0.25:
                    pct = cand_pct
                    score = 0.0
                    source = 'phykit_count_and_percent'
            expected.append((score, i, rounded, pct, source))
    if not expected:
        raise ValueError('no plausible PI count in PhyKit output for length %d: %s' % (aln_len, raw.strip()))
    expected.sort(key=lambda x: (x[0], x[1]))
    _, _, count, pct, source = expected[0]
    return count, pct, source

rows = []
failures = []
with tempfile.TemporaryDirectory() as tmp:
    tmpdir = Path(tmp)
    with zipfile.ZipFile(zip_path) as zf:
        members = sorted([m for m in zf.namelist() if not m.endswith('/') and m.endswith('.faa.mafft')])
        if not members:
            raise SystemExit('no .faa.mafft members found in archive')
        for idx, member in enumerate(members, 1):
            safe = re.sub(r'[^A-Za-z0-9_.-]+', '_', os.path.basename(member))
            work = tmpdir / ('%04d_%s' % (idx, safe))
            try:
                data = zf.read(member)
                work.write_bytes(data)
                seq_count, aln_len = read_fasta_lengths(work)
                proc = subprocess.run(['phykit', 'parsimony_informative_sites', str(work)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if proc.returncode != 0:
                    raise RuntimeError('phykit failed: ' + proc.stderr.strip())
                count, pct, source = parse_phykit(proc.stdout, aln_len)
                if count < 0 or count > aln_len or pct < 0 or pct > 100:
                    raise ValueError('out-of-range parsed values')
                rows.append({
                    'alignment': member,
                    'sequence_count': seq_count,
                    'alignment_length': aln_len,
                    'pi_sites': count,
                    'pi_percent': pct,
                    'parse_source': source,
                    'phykit_stdout': proc.stdout.strip().replace('\t', ' '),
                })
            except Exception as exc:
                failures.append({'alignment': member, 'error': str(exc)})

with open(per_path, 'w', newline='') as handle:
    fieldnames = ['alignment', 'sequence_count', 'alignment_length', 'pi_sites', 'pi_percent', 'parse_source', 'phykit_stdout']
    writer = csv.DictWriter(handle, fieldnames=fieldnames, delimiter='\t')
    writer.writeheader()
    writer.writerows(rows)

with open(failed_path, 'w', newline='') as handle:
    writer = csv.DictWriter(handle, fieldnames=['alignment', 'error'], delimiter='\t')
    writer.writeheader()
    writer.writerows(failures)

if failures:
    raise SystemExit('failed alignments: %d' % len(failures))
if not rows:
    raise SystemExit('no successful alignments')
median_pct = statistics.median([r['pi_percent'] for r in rows])
with open(answer_path, 'w') as handle:
    handle.write('metric\tvalue\talignments\n')
    handle.write('median_pi_percent\t%.12g\t%d\n' % (median_pct, len(rows)))
