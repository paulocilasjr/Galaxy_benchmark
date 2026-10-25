import os
import sys
import zipfile


root = sys.argv[1]
out_path = sys.argv[2]

with open(out_path, "w", encoding="utf-8") as out:
    out.write("path=" + root + "\n")
    out.write("isdir=" + str(os.path.isdir(root)) + "\n")
    out.write("isfile=" + str(os.path.isfile(root)) + "\n")
    out.write("exists=" + str(os.path.exists(root)) + "\n")
    if os.path.exists(root):
        out.write("size=" + str(os.path.getsize(root)) + "\n")
    if os.path.isfile(root):
        try:
            with zipfile.ZipFile(root) as archive:
                names = archive.namelist()
                out.write("zip_entries=" + str(len(names)) + "\n")
                for name in names[:5]:
                    out.write("entry=" + name + "\n")
        except Exception as exc:
            out.write("zip_error=" + type(exc).__name__ + ":" + str(exc) + "\n")
