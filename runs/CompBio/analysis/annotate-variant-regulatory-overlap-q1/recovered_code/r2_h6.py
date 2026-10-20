import json
import sys
import urllib.request


GENOME = "hg38"
TRACK = "cCREregistry"
EXPECTED_REF = "G"


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Galaxy-cCRE-query/1.0"})
    with urllib.request.urlopen(req, timeout=60) as handle:
        payload = handle.read().decode("utf-8")
    return json.loads(payload), payload


def first_track_list(obj):
    if TRACK in obj and isinstance(obj[TRACK], list):
        return obj[TRACK]
    for key, value in obj.items():
        if isinstance(value, list) and key not in {"chroms", "trackDb"}:
            return value
    return []


def value(record, *names):
    if isinstance(record, dict):
        for name in names:
            if name in record:
                return record[name]
        return None
    return None


def main():
    variant_bed, hits_path, diagnostics_path, answer_path = sys.argv[1:5]
    with open(variant_bed, "r", encoding="utf-8") as handle:
        rows = [line.rstrip("\n").split("\t") for line in handle if line.strip() and not line.startswith("#")]
    if len(rows) != 1:
        raise SystemExit(f"expected one variant BED row, found {len(rows)}")

    chrom = rows[0][0]
    start0 = int(rows[0][1])
    end0 = int(rows[0][2])
    if end0 <= start0:
        raise SystemExit("variant interval is empty or invalid")

    seq_url = (
        "https://api.genome.ucsc.edu/getData/sequence?"
        f"genome={GENOME};chrom={chrom};start={start0};end={end0}"
    )
    seq_json, seq_payload = fetch_json(seq_url)
    observed_ref = seq_json.get("dna", "").upper()
    ref_status = "match" if observed_ref == EXPECTED_REF else "mismatch"

    track_url = (
        "https://api.genome.ucsc.edu/getData/track?"
        f"genome={GENOME};track={TRACK};chrom={chrom};start={start0};end={end0}"
    )
    track_json, track_payload = fetch_json(track_url)
    records = first_track_list(track_json)

    hits = []
    for record in records:
        rec_chrom = value(record, "chrom", "genoName", "tName")
        rec_start = value(record, "chromStart", "start", "tStart")
        rec_end = value(record, "chromEnd", "end", "tEnd")
        rec_name = value(record, "name")
        rec_class = value(record, "cCRE_class", "ccreClass", "class")
        if rec_chrom is None or rec_start is None or rec_end is None:
            continue
        rec_start = int(rec_start)
        rec_end = int(rec_end)
        if rec_chrom == chrom and rec_start < end0 and rec_end > start0:
            if rec_name is None or rec_class is None:
                raise SystemExit(f"overlapping record missing name/class: {record!r}")
            hits.append((rec_chrom, rec_start, rec_end, str(rec_name), str(rec_class), record))

    with open(hits_path, "w", encoding="utf-8") as out:
        for rec_chrom, rec_start, rec_end, rec_name, rec_class, record in hits:
            out.write(f"{rec_chrom}\t{rec_start}\t{rec_end}\t{rec_name}\t{rec_class}\t{json.dumps(record, sort_keys=True)}\n")

    with open(diagnostics_path, "w", encoding="utf-8") as out:
        out.write("key\tvalue\n")
        out.write(f"variant_bed\t{chrom}:{start0}-{end0}\n")
        out.write(f"variant_1based_inclusive\t{chrom}:{start0 + 1}-{end0}\n")
        out.write(f"sequence_url\t{seq_url}\n")
        out.write(f"observed_reference\t{observed_ref}\n")
        out.write(f"expected_reference\t{EXPECTED_REF}\n")
        out.write(f"reference_check\t{ref_status}\n")
        out.write(f"track_url\t{track_url}\n")
        out.write(f"items_returned\t{track_json.get('itemsReturned', 'NA')}\n")
        out.write(f"overlap_count\t{len(hits)}\n")
        if not observed_ref:
            out.write(f"sequence_payload\t{seq_payload[:500]}\n")
        if not records:
            out.write(f"track_payload\t{track_payload[:1000]}\n")

    if ref_status != "match":
        raise SystemExit(f"reference allele check failed: expected {EXPECTED_REF}, observed {observed_ref!r}")
    if not hits:
        raise SystemExit("no overlapping cCRE records found")

    answers = []
    for _, _, _, rec_name, rec_class, _ in hits:
        answers.append(f"{rec_class},{rec_name}")
    with open(answer_path, "w", encoding="utf-8") as out:
        out.write("\n".join(answers) + "\n")


if __name__ == "__main__":
    main()
