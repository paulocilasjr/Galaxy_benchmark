# Recovered custom Galaxy code

See [manifest.json](manifest.json) for each file’s model/replicate, tool ID, job ID, state, extraction method, and hash.

- `r0`: ChatGPT5.5 replicate 1; `r1`: ChatGPT5.5 replicate 2; `r2`: ChatGPT5.5 replicate 3; `r3`: ChatGPT5.6 sol replicate 1.
- `hNN` is the first output dataset HID associated with the job.
- `.sh` preserves the recorded command with one trailing newline added; `.py` contains decoded Base64 or the Python body extracted from a heredoc.
- Failed versions are preserved without repair. The collection-preflight job has no available command and therefore no fabricated code file.
- No recovered code was executed during this audit. The original installable Galaxy tool definitions were not retrieved.
