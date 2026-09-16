import gzip
import sys
import tarfile


archive_path = sys.argv[1]
out_path = sys.argv[2]

with tarfile.open(archive_path, mode="r:gz") as archive, open(out_path, "w", encoding="utf-8") as out:
    out.write("member\tsize_bytes\tfirst_lines\n")
    for member in archive:
        if not member.isfile():
            continue
        member_file = archive.extractfile(member)
        if member_file is None:
            continue
        with member_file:
            if member.name.endswith(".gz"):
                raw = gzip.GzipFile(fileobj=member_file).read(65536)
            else:
                raw = member_file.read(65536)
        lines = raw.decode("utf-8", errors="replace").splitlines()[:3]
        out.write(member.name + "\t" + str(member.size) + "\t" + "\\n".join(lines).replace("\t", "<TAB>") + "\n")
