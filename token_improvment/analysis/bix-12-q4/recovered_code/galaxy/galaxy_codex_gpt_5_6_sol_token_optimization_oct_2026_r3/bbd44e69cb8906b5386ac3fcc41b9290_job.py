import csv
import pathlib
import subprocess
import sys
import tempfile
import zipfile

def parse_pis(stdout, member):
    lines = [line.strip() for line in stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("PhyKit returned no output for " + member)
    fields = lines[-1].split()
    if len(fields) != 3:
        raise RuntimeError("Unexpected PhyKit output for %s: %r" % (member, stdout))
    informative = int(fields[0])
    total = int(fields[1])
    percentage = float(fields[2].rstrip("%"))
    return informative, total, percentage

def process_archive(zip_path, group, expected_count, writer, work):
    with zipfile.ZipFile(zip_path) as archive:
        members = sorted(
            name for name in archive.namelist()
            if not name.endswith("/") and name.endswith(".faa.mafft")
        )
        if len(members) != expected_count:
            raise RuntimeError(
                "%s archive has %d aligned members; expected %d"
                % (group, len(members), expected_count)
            )
        for index, member in enumerate(members):
            alignment_path = work / ("%s_%04d.fasta" % (group, index))
            alignment_path.write_bytes(archive.read(member))
            result = subprocess.run(
                ["phykit", "pis", "-a", str(alignment_path)],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            informative, total, percentage = parse_pis(result.stdout, member)
            writer.writerow([group, format(percentage, ".15g"), member, informative, total])
            alignment_path.unlink()

def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: job.py ANIMALS_ZIP FUNGI_ZIP OUTPUT")
    with tempfile.TemporaryDirectory() as tmp, open(sys.argv[3], "w", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow(["group", "percentage", "alignment", "informative_sites", "total_sites"])
        work = pathlib.Path(tmp)
        process_archive(sys.argv[1], "animals", 241, writer, work)
        process_archive(sys.argv[2], "fungi", 255, writer, work)

if __name__ == "__main__":
    main()
