# Design differences between the two arms

Machine-readable tables of how the open-ended code and Galaxy arms differed (harness and container, runtime model and
reasoning, prompts, time budgets, dates, tools offered, campaign selection, other differences, and fields never recorded).
Read-only extraction from the archive; `ground_truth/`, evaluator answer files and credentials are not read.

| File | Content |
|---|---|
| `design_metadata.json` / `.md` | Tables for each question, each with the exact source fields |
| `per_run_design_metadata.csv` | One row per run (4,240), redacted (public Galaxy usernames and account-like campaign tokens) |

Regenerate from the repository root (Python 3.12 + pandas):

```bash
W=$(mktemp -d)
python manuscript_narrative/derived/design/extract_design.py $W
python manuscript_narrative/derived/design/prompt_phrases.py $W
python manuscript_narrative/derived/design/build_design_metadata.py $W manuscript_narrative/derived/design
python manuscript_narrative/derived/design/build_md.py manuscript_narrative/derived/design
```
