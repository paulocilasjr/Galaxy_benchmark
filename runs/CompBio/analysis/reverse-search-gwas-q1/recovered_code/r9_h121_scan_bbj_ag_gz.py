import re
import sys
import gzip

TARGET_IDS = {
    "rs7554873",
    "rs143596860",
    "rs34562254",
    "rs4273077",
    "rs4561508",
    "rs4985726",
    "rs2647032",
    "rs3763321",
    "rs150420714",
    "rs2926468",
}
TARGET_COORDS = {
    "1:161612233",
    "1:161595730",
    "6:32629905",
    "6:32406704",
    "17:16842991",
    "17:16849139",
    "17:16848750",
    "17:16863638",
    "19:50014739",
}

def is_target(line):
    fields = re.split(r"\s+", line.strip())
    for field in fields:
        if field in TARGET_IDS or field in TARGET_COORDS:
            return True
        if any(field.startswith(coord + ":") or field.startswith(coord + "_") for coord in TARGET_COORDS):
            return True
    return False

input_path = sys.argv[1]
output_path = sys.argv[2]
with open(input_path, "rb") as probe:
    compressed = probe.read(2) == b"\x1f\x8b"
opener = gzip.open if compressed else open
with opener(input_path, "rt", encoding="utf-8", errors="replace") as text, open(output_path, "wt", encoding="utf-8") as output:
    for index, line in enumerate(text):
        if index < 4:
            output.write("header\t%s\n" % line.rstrip("\n"))
        if is_target(line):
            output.write("target\t%s\n" % line.rstrip("\n"))
