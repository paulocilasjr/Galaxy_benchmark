"""Replace unnecessary local account paths and credential-looking strings.

The download manifests retain the original SHA-256; this records the SHA-256
of the retained derivative. Secret-bearing original bytes are not retained.
"""
import hashlib
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent / "source_snapshots/huggingface_traces"
PATTERNS = [
    (re.compile(rb"/Users/[0-9]+/"), b"/Users/[redacted]/", "local_account_path"),
    (re.compile(rb"hf_[A-Za-z0-9]{20,}"), b"[redacted_hf_token]", "hf_token"),
    (re.compile(rb"sk-[A-Za-z0-9_-]{20,}"), b"[redacted_api_token]", "api_token"),
    (re.compile(rb"(GALAXY_API_KEY\s*[=:]\s*)[A-Za-z0-9]{20,}"), rb"\1[redacted]", "galaxy_api_key_assignment"),
    (re.compile(rb"(Bearer\s+)[A-Za-z0-9._-]{20,}"), rb"\1[redacted]", "bearer_token"),
]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    for manifest_name in ("manifest.json", "manifest_galaxy.json"):
        path = ROOT / manifest_name
        if not path.exists():
            continue
        manifest = json.loads(path.read_text())
        for run in manifest["runs"].values():
            for item in run.get("files", []):
                if not item.get("downloaded"):
                    continue
                local = ROOT.parent.parent / item["local_path"]
                original = local.read_bytes()
                # A rerun after redaction must not overwrite the original hash.
                if "retained_sha256" in item:
                    assert sha(original) == item["retained_sha256"]
                    continue
                assert sha(original) == item["sha256"]
                derivative = original
                scope = []
                for pattern, replacement, name in PATTERNS:
                    derivative, count = pattern.subn(replacement, derivative)
                    if count:
                        scope.append({"kind": name, "replacements": count})
                if derivative != original:
                    local.write_bytes(derivative)
                item["retained_sha256"] = sha(derivative)
                item["retained_bytes"] = len(derivative)
                item["redactions"] = scope
        path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
