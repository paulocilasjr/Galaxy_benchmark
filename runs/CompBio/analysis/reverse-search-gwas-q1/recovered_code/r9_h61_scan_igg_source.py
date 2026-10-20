import gzip
import io
import sys
import tarfile


TARGETS = {
    "rs7554873",
    "rs143596860",
    "rs34562254",
    "rs4273077",
    "rs4561508",
    "rs2647032",
    "rs3763321",
}

archive_path = sys.argv[1]
out_path = sys.argv[2]
member_filter = sys.argv[3] if len(sys.argv) > 3 else ""

with tarfile.open(archive_path, mode="r:gz") as archive, open(out_path, "w", encoding="utf-8") as out:
    out.write("source_member\tsnp\trow\n")
    for member in archive:
        if not member.isfile() or not member.name.endswith(".gz"):
            continue
        if member_filter and member_filter not in member.name:
            continue
        member_file = archive.extractfile(member)
        if member_file is None:
            continue
        with member_file:
            gz = gzip.GzipFile(fileobj=member_file)
            with io.TextIOWrapper(gz, encoding="utf-8", errors="replace") as text:
                next(text, None)
                for line in text:
                    fields = line.rstrip("\n").split("\t")
                    if fields and fields[0] in TARGETS:
                        out.write(member.name + "\t" + fields[0] + "\t" + line)
