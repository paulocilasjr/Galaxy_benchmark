import sys
import json
import urllib.request
import urllib.error

url = "https://www.ebi.ac.uk/gwas/summary-statistics/api/chromosomes/1/associations?start=161530617&end=161530617&size=50"
out_path = sys.argv[2] if len(sys.argv) > 2 else "result.txt"

req = urllib.request.Request(url, headers={"Accept": "application/json", "User-Agent": "galaxy-udt-probe/0.1"})
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        status = resp.status
        headers = dict(resp.headers)
        body = resp.read().decode("utf-8", errors="replace")
except urllib.error.HTTPError as e:
    status = e.code
    headers = dict(e.headers) if e.headers else {}
    body = e.read().decode("utf-8", errors="replace")
except Exception as e:
    status = "ERR"
    headers = {}
    body = f"{type(e).__name__}: {e}"

with open(out_path, "w") as f:
    f.write(f"status\t{status}\n")
    f.write(f"content_type\t{headers.get('Content-Type', headers.get('content-type', ''))}\n")
    f.write("body_length\t" + str(len(body)) + "\n")
    f.write("body\t" + body + "\n")
