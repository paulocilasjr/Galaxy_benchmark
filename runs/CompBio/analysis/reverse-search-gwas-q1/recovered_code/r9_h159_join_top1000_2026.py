import re
import sys


def target_key(chrom, pos):
    chrom = chrom.lower()
    if chrom.startswith("chr"):
        chrom = chrom[3:]
    return chrom, pos


def source_keys(fields):
    keys = set()
    for i, field in enumerate(fields):
        value = field.strip()
        m = re.fullmatch(r"(?:chr)?([0-9]+|x|y|mt)[:](\d+)", value, re.I)
        if m:
            keys.add(target_key(m.group(1), m.group(2)))
        if i + 1 < len(fields) and re.fullmatch(r"(?:chr)?[0-9]+|x|y|mt", value, re.I):
            if re.fullmatch(r"\d+", fields[i + 1].strip()):
                keys.add(target_key(value, fields[i + 1].strip()))
    return keys


def main():
    if len(sys.argv) < 3:
        raise SystemExit("usage: join_top1000_2026.py target table=path ... output")
    target_path = sys.argv[1]
    output = sys.argv[-1]
    sources = sys.argv[2:-1]
    targets = {}
    with open(target_path, "r", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line.strip() or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) >= 2 and re.fullmatch(r"\d+", fields[1].strip()):
                targets[target_key(fields[0], fields[1])] = line.rstrip("\n")

    with open(output, "w", encoding="utf-8") as out:
        out.write("target_variants\t%d\n" % len(targets))
        for source in sources:
            label, path = source.split("=", 1)
            out.write("TABLE\t%s\n" % label)
            with open(path, "r", encoding="utf-8", errors="replace") as handle:
                for line in handle:
                    fields = line.rstrip("\n").split("\t")
                    matched = source_keys(fields) & targets.keys()
                    for key in sorted(matched):
                        out.write("MATCH\t%s:%s\tTARGET\t%s\tSOURCE\t%s\n" % (
                            key[0], key[1], targets[key], line.rstrip("\n")))


if __name__ == "__main__":
    main()
