import csv
import sys

source_path, out_path = sys.argv[1:3]
needles = {
    "rs143596860", "rs7554873", "rs2647032", "rs3763321",
    "rs34562254", "rs4273077", "rs4561508", "rs4985726",
}

with open(source_path, "r", errors="replace") as fh, open(out_path, "w") as out:
    reader = csv.reader(fh, delimiter="\t")
    for row in reader:
        text = "\t".join(row)
        if any(x in text for x in needles):
            out.write(text + "\n")
