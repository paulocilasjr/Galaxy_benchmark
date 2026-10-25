# Brief Communication build (Nature Methods)

This folder rebuilds `../Galaxy_agents_original_layout_manuscript.docx` as a Nature Methods Brief Communication, with its figures, Source Data and Supplementary Information. Built on 2026-10-20.

## Outputs

| File | Contents |
|---|---|
| `../Galaxy_agents_original_layout_manuscript.docx` | Manuscript: title page, abstract, main text (no headings), references, Methods, end statements, Figs. 1 and 2 with legends |
| `Supplementary_Information.docx` / `.pdf` | Supplementary Figs. 1–11, Supplementary Tables 1–6, Supplementary Notes 1–3 |
| `supplementary/Supplementary_Tables.xlsx` | Supplementary Tables 1–6, one sheet each |
| `supplementary/Supplementary_Data_1.xlsx` | Source data of Supplementary Figs. 1–11, one sheet each |
| `supplementary/Supplementary_Data_2.xlsx` | Run index: every run with its agent trace, results-site page and Galaxy history, and the history access check (sheets: Primary runs 3,840; Replaced runs 77; Interface rounds 450). The primary sheet is also `Supplementary_Data_2_primary_runs.csv` |
| `figures/Fig1.*`, `figures/Fig2.*` | Main figures: 180 mm wide, Arial 5–7 pt, PDF, SVG and 600-dpi PNG (300-dpi copies embedded in the .docx). Fig. 1: a, design; b–d, Galaxy − custom code by model and pooled. Fig. 2: a, failure causes by sibling replicates correct; b, single run, majority of 3, majority of 12 and at least 1 of 3 correct; c, one analysis step as each condition records it (bix-16-q1, GPT-5.6 Luna r1; every field checked against the run evidence); d, Galaxy ÷ custom-code tokens by interface round |
| `figures/Source_Data_Fig1.xlsx`, `figures/Source_Data_Fig2.xlsx` | Source Data for the main figures |

## Build

From this folder, with the figure environment (`manuscript/manuscript_material/scripts/requirements.txt`, Python 3.12) and the `docx` npm package on `NODE_PATH`:

```sh
python scripts/compute_numbers.py    # numbers.json: every cited number and its source
python scripts/make_figures.py       # Figs. 1 and 2, Source Data, Supplementary Fig. 4
python scripts/make_supplement.py    # supplementary/: legends, tables and workbooks
python scripts/fetch_site_links.py   # links the archive lacks: wf_007 reruns and the 6 July round-1 runs (results site)
python scripts/make_run_index.py     # Supplementary Data 2
python scripts/check_galaxy_histories.py && python scripts/make_run_index.py   # access check of every history link
node scripts/build_docx.js ../Galaxy_agents_original_layout_manuscript.docx Supplementary_Information.docx
```

The text is in `scripts/content.js` (manuscript) and `scripts/si_notes.js` (Supplementary Notes). References come from `../../references.json` and are numbered in Nature order (main text, legends, then Methods). `data/` holds tables copied from goeckslab/agent-galaxy-benchmark-manuscript (`data/SOURCES.json`). Scores are the site-matched `figures/scored_runs.csv`.

## Format checks (2026-10-20)

- Abstract: 69 words, no references (limit 70).
- Counted text: abstract, main text (1,007), figure legends (271) and main-text references (224), 1,571 words in total. The limit is 1,200 words, extendable to 1,600 at the editors' discretion.
- Voice: the text follows the PI's style (GLEAM, mlsurv and ITCR samples): gap, "To address this gap, we…", results with intervals, grouped limitations "First… Second… Third…", "Future work will…".
- Two display items; 11 main-text references and 5 Methods-only references.
- Methods: about 2,400 words with subheadings, a Statistics and reproducibility section and a Reporting summary statement.

## Run links (2026-10-20)

- Every run in Supplementary Data 2 has a Hugging Face trace link, in both conditions. The dataset `goeckslab/galaxy-agent-benchmark-run-traces` returns HTTP 401 without credentials, so readers cannot open the traces until it is made public or access is arranged.
- Galaxy histories: 2,281 of the 2,285 Galaxy runs' histories open without an account (importable, not published). Four DeepSeek V4 Pro BixBench-Verified-50 histories return HTTP 403: bix-32-q2 replicates 1–3 and bix-55-q1 replicate 3.
- The links of the 53 reviewed CompBioBench reruns in the archive workbook resolve to the same histories as those in the rerun manifest.
- bix-11-q1, GPT-5.6 Sol, Galaxy replicates 2 and 3: the site links one history to both runs, and both traces work in it.

## Items the authors must supply

They are highlighted in yellow in the documents:
- authors, affiliations and the corresponding author;
- the Galaxy MCP servers and agent skills: repository URL, version and licence;
- the Codex CLI version of the BixBench-Verified-50 GPT-5.5 runs (the other main runs used 0.146.0), and why GPT-5.6 Luna ran at maximum effort;
- the language-model verifier of BixBench-Verified-50;
- the human review of the failure-cause audit;
- the use of AI tools;
- access to the trace dataset (now private) and a DOI, the four unshared Galaxy histories, release DOIs and licences;
- acknowledgements and funding, author contributions and competing interests.

The Nature Portfolio Reporting Summary and editorial policy checklist are separate forms and are not generated here.
