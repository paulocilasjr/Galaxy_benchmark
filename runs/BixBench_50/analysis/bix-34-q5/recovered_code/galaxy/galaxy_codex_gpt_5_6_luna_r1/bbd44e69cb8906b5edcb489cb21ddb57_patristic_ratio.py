import math
import re
import statistics
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

mean_pattern = re.compile(r"^\s*mean:\s*([-+0-9.eE]+)\s*$", re.MULTILINE)

def process_group(group, archive_path):
    with zipfile.ZipFile(archive_path) as archive:
        members = sorted(
            name for name in archive.namelist()
            if name.endswith(".treefile") and not name.endswith("/")
        )
        if not members:
            raise RuntimeError(f"{group}: no .treefile members found")
        values = []
        failures = []
        with tempfile.TemporaryDirectory(prefix=f"{group}_") as work:
            work_path = Path(work)
            for index, member in enumerate(members):
                tree_path = work_path / f"{index}.treefile"
                tree_path.write_bytes(archive.read(member))
                completed = subprocess.run(
                    ["phykit", "patristic_distances", "-t", str(tree_path)],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                if completed.returncode != 0:
                    failures.append((member, completed.stderr.strip() or completed.stdout.strip()))
                    continue
                match = mean_pattern.search(completed.stdout)
                if match is None:
                    failures.append((member, "PhyKit output did not contain a mean line"))
                    continue
                value = float(match.group(1))
                if not math.isfinite(value):
                    failures.append((member, "PhyKit returned a non-finite mean"))
                    continue
                values.append((member, value))
        if failures:
            details = "; ".join(f"{name}: {message}" for name, message in failures[:5])
            raise RuntimeError(
                f"{group}: {len(failures)} of {len(members)} selected treefiles failed; {details}"
            )
        if len(values) != len(members):
            raise RuntimeError(f"{group}: processed {len(values)} of {len(members)} selected treefiles")
        return members, values

def main():
    animals_members, animals_values = process_group("Animals", sys.argv[1])
    fungi_members, fungi_values = process_group("Fungi", sys.argv[2])
    animal_median = statistics.median(value for _, value in animals_values)
    fungi_median = statistics.median(value for _, value in fungi_values)
    ratio = fungi_median / animal_median

    with open("per_tree_means.tsv", "w", encoding="utf-8") as output:
        output.write("group\tmember\tmean_patristic_distance\n")
        for member, value in animals_values:
            output.write(f"Animals\t{member}\t{value:.17g}\n")
        for member, value in fungi_values:
            output.write(f"Fungi\t{member}\t{value:.17g}\n")

    with open("patristic_summary.tsv", "w", encoding="utf-8") as output:
        output.write(
            "group\tselected_treefiles\tprocessed_treefiles\tfailed_treefiles\tmedian_mean_patristic_distance\n"
        )
        output.write(
            f"Animals\t{len(animals_members)}\t{len(animals_values)}\t0\t{animal_median:.17g}\n"
        )
        output.write(
            f"Fungi\t{len(fungi_members)}\t{len(fungi_values)}\t0\t{fungi_median:.17g}\n"
        )
        output.write(f"Fungi_over_Animals\t2\t2\t0\t{ratio:.17g}\n")

    with open("ratio.txt", "w", encoding="utf-8") as output:
        output.write(f"{ratio:.17g}\n")

if __name__ == "__main__":
    main()
