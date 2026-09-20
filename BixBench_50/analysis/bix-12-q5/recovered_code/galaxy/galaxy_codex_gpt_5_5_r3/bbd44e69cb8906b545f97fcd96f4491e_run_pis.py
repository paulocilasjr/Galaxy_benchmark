import pathlib
import subprocess
import sys
import tempfile
import zipfile

archive_path = sys.argv[1]
suffix = '.faa.mafft'

with zipfile.ZipFile(archive_path) as zf:
    members = sorted(name for name in zf.namelist() if (not name.endswith('/')) and name.endswith(suffix))
    if not members:
        raise SystemExit(f'No archive members ending with {suffix!r} were found')

    best = None
    processed = 0
    with tempfile.TemporaryDirectory() as tmpdir, open('pis_counts.tsv', 'w', encoding='utf-8') as counts:
        counts.write('member\tparsimony_informative_sites\ttotal_sites\tpercent_parsimony_informative\n')
        tmp = pathlib.Path(tmpdir)
        for idx, member in enumerate(members, start=1):
            aln_path = tmp / f'alignment_{idx}.fa'
            aln_path.write_bytes(zf.read(member))
            proc = subprocess.run(
                ['phykit', 'pis', str(aln_path)],
                check=False,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if proc.returncode != 0:
                raise SystemExit(f'PhyKIT failed for {member}: {proc.stderr.strip()}')
            parts = proc.stdout.strip().split()
            if len(parts) < 3:
                raise SystemExit(f'Unexpected PhyKIT output for {member}: {proc.stdout!r}')
            try:
                pis = int(float(parts[0]))
                total = int(float(parts[1]))
                pct = float(parts[2])
            except ValueError as exc:
                raise SystemExit(f'Non-numeric PhyKIT output for {member}: {proc.stdout!r}') from exc
            counts.write(f'{member}\t{pis}\t{total}\t{pct}\n')
            processed += 1
            if best is None or pis > best[0]:
                best = (pis, member, total, pct)

    pathlib.Path('answer.txt').write_text(f'{best[0]}\n', encoding='utf-8')
    pathlib.Path('summary.tsv').write_text(
        'selected_suffix\tselected_members\tprocessed_members\tmax_member\tmax_parsimony_informative_sites\ttotal_sites\tpercent_parsimony_informative\n'
        f'{suffix}\t{len(members)}\t{processed}\t{best[1]}\t{best[0]}\t{best[2]}\t{best[3]}\n',
        encoding='utf-8',
    )
