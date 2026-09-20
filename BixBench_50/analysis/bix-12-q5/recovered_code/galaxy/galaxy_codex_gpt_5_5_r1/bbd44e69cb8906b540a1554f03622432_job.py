import os
import re
import shutil
import subprocess
import sys
import zipfile


def parse_fasta_raw_seqs(path):
    seqs = []
    name = None
    chunks = []
    with open(path) as handle:
        for raw in handle:
            line = raw.strip()
            if not line:
                continue
            if line.startswith(">"):
                if name is not None:
                    seqs.append((name, "".join(chunks)))
                parts = line[1:].split()
                name = parts[0] if parts else "seq"
                chunks = []
            else:
                chunks.append(line)
    if name is not None:
        seqs.append((name, "".join(chunks)))
    return seqs


def alignment_length_if_valid(path):
    seqs = parse_fasta_raw_seqs(path)
    if not seqs:
        raise RuntimeError(f"No sequences in {path}")
    lengths = {len(seq) for _, seq in seqs}
    if len(lengths) != 1:
        raise RuntimeError(f"Unequal sequence lengths in {path}: {sorted(lengths)}")
    return lengths.pop()


def run_phykit_pis(path):
    last_err = ""
    for cmd in (["phykit", "pis", path], ["pk_pis", path]):
        proc = subprocess.run(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if proc.returncode == 0:
            out = proc.stdout.strip()
            for token in out.split():
                clean = token.strip("[]():,;%")
                if re.fullmatch(r"\d+", clean):
                    return int(clean), out
            raise RuntimeError(f"Could not parse PhyKIT pis output for {path}: {out!r}")
        last_err = proc.stderr.strip() or proc.stdout.strip()
    raise RuntimeError(f"PhyKIT pis failed for {path}: {last_err}")


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: job.py scogs_animals.zip")
    zip_path = sys.argv[1]
    work = "alignments"
    os.makedirs(work, exist_ok=True)
    rows = []
    with zipfile.ZipFile(zip_path) as zf:
        names = sorted(n for n in zf.namelist() if n.endswith(".faa.mafft") and not n.endswith("/"))
        if not names:
            raise RuntimeError("No .faa.mafft alignments found in input zip")
        for i, member in enumerate(names, 1):
            base = os.path.basename(member)
            safe = re.sub(r"[^0-9A-Za-z._=-]", "_", f"{i:04d}_{base}")
            out_path = os.path.join(work, safe)
            with zf.open(member) as src, open(out_path, "wb") as dst:
                shutil.copyfileobj(src, dst)
            aln_len = alignment_length_if_valid(out_path)
            count, raw_out = run_phykit_pis(out_path)
            rows.append((base, count, aln_len, raw_out.replace("\t", " ")))
    max_row = max(rows, key=lambda row: row[1])
    with open("summary.tsv", "w") as handle:
        handle.write("alignment\tparsimony_informative_sites\talignment_length\tphykit_pis_output\n")
        for base, count, aln_len, raw_out in rows:
            handle.write(f"{base}\t{count}\t{aln_len}\t{raw_out}\n")
    with open("answer.txt", "w") as handle:
        handle.write(f"{max_row[1]}\n")
    with open("metrics.txt", "w") as handle:
        handle.write(f"processed_alignments\t{len(rows)}\n")
        handle.write(f"max_alignment\t{max_row[0]}\n")
        handle.write(f"max_pis\t{max_row[1]}\n")


if __name__ == "__main__":
    main()
