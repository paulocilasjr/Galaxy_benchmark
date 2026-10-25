import gzip
import io
import sys
import urllib.request


TARGET_POSITIONS = {
    ("1", 161473296),
    ("1", 161475575),
    ("1", 161481328),
    ("1", 161498503),
    ("1", 161506415),
    ("1", 161507159),
    ("1", 161507228),
    ("1", 161507276),
    ("1", 161507414),
    ("1", 161508918),
    ("1", 161509003),
    ("1", 161509341),
    ("1", 161509562),
    ("1", 161509648),
    ("1", 161509809),
    ("1", 161510859),
    ("1", 161513694),
    ("1", 161515469),
    ("1", 161517662),
    ("1", 161522385),
    ("1", 161522877),
    ("1", 161523491),
    ("1", 161530615),
    ("1", 161530617),
    ("1", 161530922),
    ("1", 161531006),
    ("1", 161533223),
    ("1", 161537658),
    ("1", 161540644),
    ("1", 161540726),
    ("1", 161545536),
    ("1", 161558222),
    ("1", 161595363),
    ("1", 161612233),
    ("1", 161642443),
    ("6", 31614248),
    ("6", 31973120),
    ("6", 32047051),
    ("6", 32061428),
    ("6", 32067917),
    ("6", 32092090),
    ("6", 32096949),
    ("6", 32112414),
    ("6", 32128224),
    ("6", 32164195),
    ("6", 32438927),
    ("6", 32667724),
    ("6", 32668787),
    ("6", 32668221),
    ("6", 32662128),
}


def open_text(path):
    raw = open(path, "rb")
    prefix = raw.peek(2)[:2] if hasattr(raw, "peek") else raw.read(2)
    if prefix == b"\x1f\x8b":
        raw.close()
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8", errors="replace")
    raw.seek(0)
    return io.TextIOWrapper(raw, encoding="utf-8", errors="replace")


def load_input(path):
    values = {}
    with open_text(path) as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                continue
            chrom = fields[0].removeprefix("chr")
            try:
                key = (chrom, int(fields[1]))
            except ValueError:
                continue
            if key in TARGET_POSITIONS:
                values[key] = (fields[2], fields[7])
    return values


def source_rows(url, input_values, out):
    request = urllib.request.Request(url, headers={"Accept-Encoding": "identity"})
    scanned = 0
    hits = 0
    found = set()
    with urllib.request.urlopen(request, timeout=120) as response:
        with gzip.GzipFile(fileobj=response) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", errors="replace") as handle:
                header = next(handle).rstrip("\n")
                for line in handle:
                    scanned += 1
                    fields = line.rstrip("\n").split("\t")
                    if not fields:
                        continue
                    token = fields[0]
                    try:
                        chrom, rest = token.split(":", 1)
                        position = int(rest.split("_", 1)[0])
                    except (ValueError, IndexError):
                        continue
                    key = (chrom.removeprefix("chr"), position)
                    if key not in TARGET_POSITIONS:
                        continue
                    found.add(key)
                    hits += 1
                    source_p = fields[9] if len(fields) > 9 else ""
                    input_id, input_p = input_values.get(key, ("", ""))
                    out.write(
                        "ROW\t%s\t%s\t%s\t%s\t%s\t%s\n"
                        % (url, key[0], key[1], token, source_p, input_id + ":" + input_p)
                    )
                    if found == TARGET_POSITIONS:
                        break
    out.write("SUMMARY\t%s\t%d\t%d\t%d\n" % (url, scanned, hits, len(found)))


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: query_bcx2_sources.py INPUT OUTPUT [URL ...]")
    input_path, output_path = sys.argv[1], sys.argv[2]
    urls = sys.argv[3:]
    input_values = load_input(input_path)
    with open(output_path, "w", encoding="utf-8") as out:
        out.write("record\tsource_url\tchrom\tposition\tsource_variant\tsource_p\tinput_id_and_p\n")
        out.write("INPUT_TARGETS\t%d\n" % len(input_values))
        for url in urls:
            source_rows(url, input_values, out)


if __name__ == "__main__":
    main()
