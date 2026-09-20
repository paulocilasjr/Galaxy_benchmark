import urllib.request

rows = []
for scheme in ("https", "http"):
    for endpoint in ("list/organism", "link/pathway/paz", "link/pathway/pae"):
        url = scheme + "://rest.kegg.jp/" + endpoint
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "GalaxyUserTool-pa14-kegg-ora/0.1"})
            with urllib.request.urlopen(request, timeout=60) as response:
                body = response.read().decode("utf-8", "replace")
                rows.append("%s\t%s\t%s\t%s" % (scheme, endpoint, response.status, len(body)))
                for sample in body.splitlines()[:3]:
                    rows.append("sample\t" + sample.replace("\t", "\\t"))
        except Exception as exc:
            rows.append("%s\t%s\tERROR\t%s" % (scheme, endpoint, str(exc)))
with open("diagnostic.txt", "w", encoding="utf-8") as output:
    output.write("\n".join(rows) + "\n")
