import csv
import gzip
import heapq
import sys


def open_text(path):
    with open(path, "rb") as fh:
        magic = fh.read(2)
    return gzip.open(path, "rt", encoding="utf-8", errors="replace") if magic == b"\x1f\x8b" else open(path, "rt", encoding="utf-8", errors="replace")


def pval(value):
    try:
        return float(value)
    except Exception:
        return None


def region(chrom, pos):
    windows = {
        "FCGR": ("1", 161480000, 161680000),
        "HLA": ("6", 32000000, 33000000),
        "TACI": ("17", 16900000, 17100000),
        "FCGRT": ("19", 49300000, 49800000),
    }
    for label, (want_chrom, start, end) in windows.items():
        if chrom == want_chrom and start <= pos <= end:
            return label
    return None


def add_top(heaps, label, value, row, limit=20):
    if value is None:
        return
    heap = heaps.setdefault(label, [])
    item = (value, row)
    if len(heap) < limit:
        heapq.heappush(heap, item)
    elif value > heap[0][0]:
        heapq.heapreplace(heap, item)


target_path, loci_path, out_path = sys.argv[1:4]
target_heaps = {}
target_exact = []
with open_text(target_path) as inp:
    header = inp.readline().rstrip("\n\r").split("\t")
    for line in inp:
        fields = line.rstrip("\n\r").split("\t")
        if len(fields) < 8:
            continue
        chrom, pos_s = fields[0], fields[1]
        try:
            pos = int(pos_s)
        except Exception:
            continue
        label = region(chrom, pos)
        if label is not None:
            p = pval(fields[7])
            add_top(target_heaps, label, -p if p is not None and p > 0 else None, fields)
        if (chrom, pos) in {
            ("1", 161625940), ("1", 161642443), ("6", 32438927), ("6", 32662128),
            ("17", 16939677), ("17", 16945436), ("17", 16945825), ("17", 16960324),
            ("19", 49525049),
        }:
            target_exact.append(fields)

ztt_rows = []
regional_rows = []
with open_text(loci_path) as inp:
    reader = csv.reader(inp, delimiter="\t")
    rows = list(reader)

# The first four rows are title/blank/header/blank; data begins after them.
for fields in rows[4:]:
    if not fields or len(fields) < 13:
        continue
    try:
        locus_chrom = fields[1]
        locus_pos = int(fields[2])
    except Exception:
        continue
    if region(locus_chrom, locus_pos) is not None:
        regional_rows.append(fields)
    if fields[0] == "ZTT":
        ztt_rows.append(fields)

with open(out_path, "w", encoding="utf-8") as out:
    out.write("TARGET_REGIONAL_TOPS\n")
    for label in ("FCGR", "HLA", "TACI", "FCGRT"):
        out.write("REGION\t%s\n" % label)
        for value, fields in sorted(target_heaps.get(label, []), reverse=True):
            out.write("\t".join(fields) + "\n")
    out.write("TARGET_EXACT_COORDINATES\n")
    out.write("\t".join(header) + "\n")
    for fields in target_exact:
        out.write("\t".join(fields) + "\n")
    out.write("KOYAMA_ZTT_LEAD_ROWS\n")
    out.write("\t".join([
        "Phenotype", "CHR", "POS", "REF", "ALT", "LocusStart", "LocusEnd",
        "N", "AAF", "BETA", "SE", "P", "LOGP", "rsID", "Consequence",
        "GeneSymbol"
    ]) + "\n")
    for fields in ztt_rows:
        out.write("\t".join(fields) + "\n")
    out.write("KOYAMA_ALL_REGIONAL_LEAD_ROWS\n")
    for fields in regional_rows:
        out.write("\t".join(fields) + "\n")
