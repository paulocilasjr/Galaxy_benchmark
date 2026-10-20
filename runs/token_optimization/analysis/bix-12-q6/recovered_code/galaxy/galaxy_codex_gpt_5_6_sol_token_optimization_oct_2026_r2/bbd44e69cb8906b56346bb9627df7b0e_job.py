import csv
import pathlib
import subprocess
import sys
import zipfile

import scipy
from scipy.stats import mannwhitneyu

animals_zip = pathlib.Path(sys.argv[1])
fungi_zip = pathlib.Path(sys.argv[2])
work = pathlib.Path("alignments")
work.mkdir(exist_ok=True)

def counts_for(archive_path, group):
    group_dir = work / group.lower()
    group_dir.mkdir(exist_ok=True)
    rows = []
    with zipfile.ZipFile(archive_path) as zf:
        members = sorted(
            n for n in zf.namelist()
            if not n.endswith("/") and pathlib.PurePosixPath(n).name.endswith(".mafft")
        )
        if not members:
            raise RuntimeError(f"No .mafft alignments found in {archive_path}")
        for idx, member in enumerate(members):
            target = group_dir / f"{idx:04d}.faa"
            target.write_bytes(zf.read(member))
            proc = subprocess.run(
                ["phykit", "pis", str(target)],
                check=True,
                text=True,
                capture_output=True,
            )
            fields = proc.stdout.strip().split("\t")
            if len(fields) != 3:
                raise RuntimeError(f"Unexpected PhyKIT output for {member}: {proc.stdout!r}")
            pi_count = int(fields[0])
            aln_len = int(fields[1])
            percent = float(fields[2])
            rows.append((group, member, pi_count, aln_len, percent))
    return rows

animal_rows = counts_for(animals_zip, "Animals")
fungi_rows = counts_for(fungi_zip, "Fungi")

with open("counts.tsv", "w", newline="") as out:
    writer = csv.writer(out, delimiter="\t", lineterminator="\n")
    writer.writerow(["group", "alignment", "parsimony_informative_sites", "alignment_length", "percent_parsimony_informative_sites"])
    writer.writerows(animal_rows + fungi_rows)

animal_counts = [row[2] for row in animal_rows]
fungi_counts = [row[2] for row in fungi_rows]
test = mannwhitneyu(
    animal_counts,
    fungi_counts,
    use_continuity=True,
    alternative="two-sided",
    method="auto",
)

with open("result.tsv", "w", newline="") as out:
    writer = csv.writer(out, delimiter="\t", lineterminator="\n")
    writer.writerow(["test", "sample1", "sample2", "n1", "n2", "U_statistic", "p_value", "alternative", "method", "scipy_version"])
    writer.writerow([
        "Mann-Whitney U",
        "Animals",
        "Fungi",
        len(animal_counts),
        len(fungi_counts),
        format(float(test.statistic), ".17g"),
        format(float(test.pvalue), ".17g"),
        "two-sided",
        "auto",
        scipy.__version__,
    ])
