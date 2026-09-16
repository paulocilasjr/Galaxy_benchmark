import gzip
import heapq
import sys


def open_text(path):
    with open(path, "rb") as probe:
        magic = probe.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", errors="replace")
    return open(path, "rt", errors="replace")


def add_top(heap, key, value, row, limit=25):
    item = (value, row)
    if len(heap) < limit:
        heapq.heappush(heap, item)
    elif value > heap[0][0]:
        heapq.heapreplace(heap, item)


def target_regions():
    return {
        "FCGR_hg38": ("1", 161480000, 161680000),
        "HLA_hg38": ("6", 32000000, 33000000),
        "TACI_hg38": ("17", 16900000, 17100000),
        "FCGRT_hg38": ("19", 49300000, 49800000),
    }


def source_regions():
    return {
        "FCGR_hg19": ("1", 161450000, 161650000),
        "HLA_hg19": ("6", 32000000, 33000000),
        "TACI_hg19": ("17", 16800000, 16900000),
        "FCGRT_hg19": ("19", 49300000, 49800000),
    }


def scan_target(path):
    regions = target_regions()
    heaps = {name: [] for name in regions}
    with open_text(path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        idx = {name: i for i, name in enumerate(header)}
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if len(fields) <= max(idx.get("P", 0), idx.get("#CHROM", 0), idx.get("POS", 0)):
                continue
            chrom = fields[idx.get("#CHROM", 0)]
            try:
                pos = int(fields[idx.get("POS", 1)])
                p = float(fields[idx.get("P", 7)])
            except (ValueError, IndexError):
                continue
            if p <= 0:
                continue
            for name, (want_chrom, lo, hi) in regions.items():
                if chrom == want_chrom and lo <= pos <= hi:
                    add_top(heaps[name], -__import__("math").log10(p),
                            "\t".join([name, chrom, str(pos), fields[idx.get("ID", 2)], fields[idx.get("P", 7)]]))
    return heaps


def scan_source(path):
    regions = source_regions()
    heaps = {name: [] for name in regions}
    with open_text(path) as handle:
        header = handle.readline().rstrip("\n").split("\t")
        idx = {name: i for i, name in enumerate(header)}
        pcol = "neglog10_pval_meta_hq" if "neglog10_pval_meta_hq" in idx else "neglog10_pval_meta"
        for line in handle:
            fields = line.rstrip("\n").split("\t")
            if len(fields) <= max(idx.get("chr", 0), idx.get("pos", 1), idx.get(pcol, 0)):
                continue
            chrom = fields[idx.get("chr", 0)]
            try:
                pos = int(fields[idx.get("pos", 1)])
                score = float(fields[idx[pcol]])
            except (ValueError, IndexError):
                continue
            for name, (want_chrom, lo, hi) in regions.items():
                if chrom == want_chrom and lo <= pos <= hi:
                    row = "\t".join([
                        name, chrom, str(pos), fields[idx.get("ref", 2)],
                        fields[idx.get("alt", 3)], fields[idx[pcol]],
                        fields[idx.get("neglog10_pval_meta", idx[pcol])],
                        fields[idx.get("neglog10_pval_EUR", idx[pcol])],
                    ])
                    add_top(heaps[name], score, row)
    return heaps


def main():
    target_heaps = scan_target(sys.argv[1])
    source_heaps = scan_source(sys.argv[2])
    with open(sys.argv[3], "w") as out:
        out.write("dataset\tregion\tchrom\tpos\tref_or_id\talt_or_p\tprimary_score\tmeta_score\teur_score\n")
        for name, heap in target_heaps.items():
            for score, row in sorted(heap, reverse=True):
                parts = row.split("\t")
                out.write("target\t" + "\t".join([parts[0], parts[1], parts[2], parts[3], parts[4], f"{score:.6f}", "NA"]) + "\n")
        for name, heap in source_heaps.items():
            for score, row in sorted(heap, reverse=True):
                parts = row.split("\t")
                out.write("source\t" + "\t".join([parts[0], parts[1], parts[2], parts[3], parts[4], parts[5], parts[6], parts[7]]) + "\n")


if __name__ == "__main__":
    main()
