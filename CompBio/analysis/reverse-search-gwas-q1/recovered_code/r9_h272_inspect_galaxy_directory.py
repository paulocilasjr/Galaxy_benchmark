import os
import sys


root = sys.argv[1]
print("root=%s" % root)
print("is_dir=%s is_file=%s" % (os.path.isdir(root), os.path.isfile(root)))
if os.path.isdir(root):
    for current, dirs, files in os.walk(root):
        rel = os.path.relpath(current, root)
        print("DIR\t%s\t%d files" % (rel, len(files)))
        for name in sorted(files)[:20]:
            print("FILE\t%s" % os.path.join(rel, name))
        if rel != ".":
            dirs[:] = []
elif os.path.isfile(root):
    print("size=%d" % os.path.getsize(root))
