import csv
import sys

source_path, out_path = sys.argv[1:3]
needles = {"rs7554873", "rs34562254"}

with open(source_path, "r", errors="replace") as fh, open(out_path, "w") as out:
    reader = csv.reader(fh, delimiter="\t")
    for line_number, row in enumerate(reader, start=1):
        text = "\t".join(row)
        if line_number <= 10 or any(x in text for x in needles):
            out.write(f"{line_number}\t{text}\n")
