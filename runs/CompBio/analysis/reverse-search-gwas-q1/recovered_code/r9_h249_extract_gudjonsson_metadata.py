import csv
import sys

source_path, out_path = sys.argv[1:3]
keywords = ("immunoglobulin", "igg", "iga", "igm", "globulin", "fcgr", "tnfrsf13b", "fcgrt")

with open(source_path, "r", errors="replace") as fh, open(out_path, "w") as out:
    reader = csv.reader(fh, delimiter="\t")
    for line_number, row in enumerate(reader, start=1):
        text = "\t".join(row)
        lowered = text.lower()
        if line_number <= 4 or any(keyword in lowered for keyword in keywords):
            out.write(f"{line_number}\t{text}\n")
