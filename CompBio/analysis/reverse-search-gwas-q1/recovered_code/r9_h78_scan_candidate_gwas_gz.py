import gzip
import sys

source = sys.argv[1]
targets = {
    ("1", "161612233"),
    ("1", "161595730"),
    ("17", "16842991"),
    ("17", "16849139"),
    ("17", "16848750"),
    ("6", "32629905"),
    ("6", "32406704"),
    ("17", "16863638"),
}

print("line_type\tcontent")
with gzip.open(source, "rt", encoding="utf-8", errors="replace") as handle:
    for line_number, raw in enumerate(handle, 1):
        line = raw.rstrip("\n\r")
        if line_number <= 3:
            print("header\t" + line)
            continue
        if not line or line.startswith("#"):
            continue
        fields = line.split("\t")
        if len(fields) < 2:
            fields = line.split()
        if len(fields) >= 2 and (fields[0], fields[1]) in targets:
            print("target\t" + line)
