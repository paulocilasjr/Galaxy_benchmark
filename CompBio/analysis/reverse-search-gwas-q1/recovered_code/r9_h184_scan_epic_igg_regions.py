import gzip
import heapq
import math
import sys


def open_text(path):
    with open(path, "rb") as probe:
        magic = probe.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", errors="replace")
    return open(path, "rt", errors="replace")


def add_top(heap, score, row, limit=10):
    if not math.isfinite(score):
        return
    item = (score, row)
    if len(heap) < limit:
        heapq.heappush(heap, item)
    elif item > heap[0]:
        heapq.heapreplace(heap, item)


def top_rows(heap):
    return sorted(heap, reverse=True)


regions = {
    "FCGR": ("1", 161480000, 161680000),
    "HLA": ("6", 32000000, 33000000),
    "TACI": ("17", 16900000, 17100000),
    "FCGRT": ("19", 49300000, 49800000),
}

target_path, source_path, out_path = sys.argv[1:4]
target_heaps = {name: [] for name in regions}
source_heaps = {name: [] for name in regions}

with open_text(target_path) as fh:
    header = None
    pidx = None
    for line in fh:
        if not line.strip():
            continue
        if line.startswith("#"):
            header = line.rstrip("\n").split("\t")
            pidx = header.index("P")
            continue
        fields = line.rstrip("\n").split("\t")
        if pidx is None or len(fields) <= pidx:
            fields = line.rstrip("\n").split()
        try:
            chrom = fields[0].removeprefix("chr")
            pos = int(fields[1])
            p = float(fields[pidx])
        except (ValueError, IndexError):
            continue
        for name, (rchrom, start, end) in regions.items():
            if chrom == rchrom and start <= pos <= end:
                add_top(target_heaps[name], -math.log10(p), "\t".join(fields))

with open_text(source_path) as fh:
    source_header = None
    cidx = posidx = pidx = None
    for line in fh:
        if not line.strip():
            continue
        if source_header is None:
            source_header = line.rstrip("\n").split("\t")
            lower = [x.lower() for x in source_header]
            cidx = lower.index("chromosome")
            posidx = lower.index("base_pair_location")
            pidx = lower.index("p_value")
            continue
        fields = line.rstrip("\n").split("\t")
        if len(fields) <= max(cidx, posidx, pidx):
            continue
        try:
            chrom = fields[cidx].removeprefix("chr")
            pos = int(fields[posidx])
            p = float(fields[pidx])
        except (ValueError, IndexError):
            continue
        for name, (rchrom, start, end) in regions.items():
            if chrom == rchrom and start <= pos <= end:
                add_top(source_heaps[name], -math.log10(p), "\t".join(fields))

with open(out_path, "w") as out:
    out.write("target_header\t" + "\t".join(header or []) + "\n")
    out.write("source_header\t" + "\t".join(source_header or []) + "\n")
    for name in regions:
        out.write("TARGET_REGION\t" + name + "\n")
        for score, row in top_rows(target_heaps[name]):
            out.write("TARGET\t" + name + "\t-log10P=" + format(score, ".8g") + "\t" + row + "\n")
        out.write("SOURCE_REGION\t" + name + "\n")
        for score, row in top_rows(source_heaps[name]):
            out.write("SOURCE\t" + name + "\t-log10P=" + format(score, ".8g") + "\t" + row + "\n")
