# Moving to another computer

The repository was checked against `origin` on 2026-10-25. All local branch
commits were already reachable from remote branches, and there were no stashes
or tracked working-tree changes before the migration additions. The latest
working tree is on `refactor/repository-layout`; the remote default is `main`.

Clone the branch containing this preservation work:

```sh
git clone --branch refactor/repository-layout git@github.com:paulocilasjr/Galaxy_benchmark.git
cd Galaxy_benchmark
python3 docs/migration/restore.py
```

The restore command verifies 2,168 formerly ignored archive files (2,164 logs,
one run manifest, and three manuscript evaluation metadata JSON files). It
also reassembles the 151,441,444-byte dataset at
`runs/CompBio/analysis/reverse-search-gwas-q1/reverse.search.gwas.q1.tsv.gz`
from five committed binary pieces, checking SHA-256 hashes and sizes.
The original dataset remains ignored to avoid storing it twice in Git.
The pieces preserve its exact bytes without an external download or Git LFS.

To check the preservation records without creating the dataset:

```sh
python3 docs/migration/restore.py --verify-only
```

`preserved_files.json` records paths, sizes and SHA-256 hashes of the newly
preserved files. `large_dataset.json` records the dataset and its pieces.
The archive logs were checked for common secret patterns and the current
local Galaxy API key. No complete credential was identified by those checks;
historical logs include truncated key prefixes and dated signed download URLs.
The original evidence files were preserved without modification.

## Files needing separate handling

- `.env`: contains `GALAXY_API_KEY` and `URL`. Transfer this file through a
  secure channel or recreate it from `.env.example` and your credentials.
  Credential values are deliberately absent from this backup.
- `.venv/`: recreate the Python environment. `local-python-packages.txt`
  records installed package names and versions for reference; use the
  relevant analysis/manuscript requirements files for installation. This
  inventory alone does not preserve interpreter binaries or native libraries.
- `.claude/settings.local.json`: a copy is preserved as
  `claude-settings.local.snapshot.json`. It includes permissions and paths
  specific to the original computer. Review it before applying it elsewhere.
- macOS metadata, Python bytecode, pytest caches and Office lock files are
  temporary files and remain ignored.
- No `outputs/` run directories existed during this check. New runs written
  there remain ignored under the benchmark execution contract and must be
  archived separately when they are created.

Git configuration, authentication, hooks and reflogs inside `.git/` are local
machine state and are not recreated by cloning. Remote branches retain the
existing committed project history. You can inspect them with `git branch -r`.
