import gzip
import sys


input_path, output_path = sys.argv[1:3]
with open(input_path, "rb") as raw:
    magic = raw.read(2)
opener = gzip.open if magic == b"\x1f\x8b" else open

bin_size = 5_000_000
best = {}
sig_by_chrom = {}

with opener(input_path, "rt", encoding="utf-8", errors="replace") as handle:
    header = handle.readline().rstrip("\n\r").split("\t")
    if len(header) < 8 or header[7] != "P":
        raise ValueError(f"Unexpected header: {header!r}")
    for line in handle:
        fields = line.rstrip("\n\r").split("\t")
        if len(fields) < 8:
            continue
        try:
            chrom = fields[0]
            pos = int(fields[1])
            p = float(fields[7])
        except ValueError:
            continue
        if p < 5e-8:
            sig_by_chrom[chrom] = sig_by_chrom.get(chrom, 0) + 1
        key = (chrom, pos // bin_size)
        if key not in best or p < best[key][0]:
            best[key] = (p, fields[:8])

with open(output_path, "w", encoding="utf-8") as out:
    out.write("section\tchrom\tvalue\n")
    for chrom in sorted(sig_by_chrom, key=lambda x: (not x.isdigit(), int(x) if x.isdigit() else x)):
        out.write(f"significant_count\t{chrom}\t{sig_by_chrom[chrom]}\n")
    out.write("rank\tbin_start\tCHROM\tPOS\tID\tREF\tALT\tA1\tTEST\tP\n")
    ranked = sorted(best.values(), key=lambda x: x[0])[:300]
    for rank, (p, fields) in enumerate(ranked, 1):
        bin_start = (int(fields[1]) // bin_size) * bin_size
        out.write(f"{rank}\t{bin_start}\t" + "\t".join(fields) + "\n")
