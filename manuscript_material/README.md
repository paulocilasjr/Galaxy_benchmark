# Manuscript material for Nature Methods submission

This folder holds every display item, supplementary file, Source Data workbook and statement that the draft Results call for. Each file is generated from the archived evidence by the scripts in `scripts/`, so every number traces back to a run, trace line or archive table.

## 1. Design rules applied to every figure and table

1. **Open-ended code is the reference condition and always comes first.** This holds for panel order (Fig. 1a before 1b), row order, legends, table columns and Source Data columns. Differences are always reported as Galaxy minus open-ended code.
2. **Colour has one meaning.** Vermillion (#D55E00) is open-ended code and blue (#0072B2) is Galaxy, everywhere. Panels that show only Galaxy runs use Galaxy blue. Benchmarks are never colour-coded; panels and labels separate them.
3. **Colour-vision safety.** The colours come from the Okabe–Ito palette, which Nature Methods itself recommended (Wong, *Nat. Methods* **8**, 441; 2011). Environment is also encoded by shape (squares for open-ended code, circles for Galaxy), so it survives greyscale printing. Every category palette carries direct counts or labels as a second cue.
4. **No abbreviations.** Terms such as G/C, pp, CI, MCP, UDT, CC*, MAE, DE, QC, AMR and r1 are spelled out or replaced by plain descriptions. An automated audit of all figure text found none remaining.
5. **Related results share one plot type.** Fig. 2a–c show only the Galaxy-minus-open-ended-code difference for each benchmark, with identical layout and rows; pooled score levels are given under each panel title.
6. **Every panel title states its finding** (for example "Galaxy produced fewer non-unanimous triplicates than open-ended code in every benchmark"). Axis labels say what is measured and in which unit; interval types and reference lines are named on the panel.

## 2. What is here

| Folder | Contents | Submit? |
|---|---|---|
| `figures/` | `Fig1.pdf` … `Fig5.pdf`: vector PDFs with editable, embedded TrueType text; 183 mm wide and 112–170 mm tall. `previews/` holds 300-dpi PNGs. | PDFs: yes |
| `extended_data/` | `ED_Fig1.tif` … `ED_Fig5.tif` (300 dpi, RGB, LZW) plus the same figures as `.eps`; 179 mm wide and ≤165 mm tall. `previews/` holds PNGs. | TIFF (or EPS): yes |
| `legends/` | `Figure_legends.md` / `.docx`: legends for all ten figures. In the .docx each legend is one paragraph, in journal style. | Paste into the manuscript |
| `supplementary/` | `Supplementary_Information.pdf`: Supplementary Notes 1–9 and legends for all tables and data files. | Yes |
| | `Supplementary_Tables.xlsx`: Supplementary Tables 1–67, plus index and glossary sheets. | Yes |
| | `Supplementary_Data_1_run_summaries.xlsx`: 4,240 runs. | Yes |
| | `Supplementary_Data_2_failed_MCP_calls.xlsx`: 7,389 calls. | Yes |
| | `Supplementary_Data_3_parameter_substitutions.xlsx`: 2,085 calls. | Yes |
| | `Supplementary_Table_crosswalk.csv`: maps each Supplementary Table number to its archive ID. | Authors only |
| `source_data/` | `Source_Data_Fig1–5.xlsx` and `Source_Data_ED_Fig1–5.xlsx`, one sheet per panel. | Yes |
| | `figure_data.json` and `derived/` are build intermediates; `derived/` contains local file paths. | No |
| `qa/cvd/` | Every figure simulated under protanopia, deuteranopia, tritanopia and greyscale, for checking. | No |
| `statements/` | Data availability, Code availability and Reporting Summary notes (.md and .docx). Placeholders are marked `[Authors: …]`. | Paste into the manuscript and forms |
| `scripts/` | Generators and `requirements.txt` (see §8). | Via the code repository |

## 3. Call-out map: the draft's text to figures and tables

**Main-figure titles.** Each title opens that figure's legend, as Nature Methods requires, and is also stored as the PDF's title metadata. The image itself carries no title. Edit the titles in `scripts/figure_titles.json` and in the legends.

- **Fig. 1** | Study design: the same AI agents analyse biological data in open-ended code or through the Galaxy workbench.
- **Fig. 2** | Agents reach similar accuracy in Galaxy and in open-ended code, and most of their failures are not caused by Galaxy.
- **Fig. 3** | Agents use Galaxy as a structured analysis environment whose records reveal input, parameter and silent-substitution errors.
- **Fig. 4** | Solution paths vary by model and benchmark, and Galaxy replicates agree more often and diverge for different reasons.
- **Fig. 5** | Galaxy raises input-token use, mostly for finding and inspecting tools, in exchange for an inspectable analysis record.


| Call-out | File, panel | Finding shown | Data source |
|---|---|---|---|
| Fig. 1a | `Fig1.pdf` a | Open-ended code, the reference condition | — |
| Fig. 1b | `Fig1.pdf` b | Galaxy-mediated condition and what Galaxy records | — |
| Fig. 1c | `Fig1.pdf` c | Three benchmarks, five configurations, runs per cell; endpoint of each benchmark | Supp. Table 1 |
| Fig. 2a | `Fig2.pdf` a | BixBench acceptance is similar: Galaxy minus open-ended code with 95% interval, per configuration | Supp. Table 2 |
| Fig. 2b | `Fig2.pdf` b | CompBioBench aggregate scores are similar: difference of means (no interval available) | Supp. Tables 5–6 |
| Fig. 2c | `Fig2.pdf` c | IWC agreement is equal or higher with Galaxy: difference with 95% interval | Supp. Table 7 |
| Fig. 2d | `Fig2.pdf` d | Near-perfect agreement on most IWC tasks; cause of every score below 0.5 | Supp. Tables 9, 18 |
| Fig. 2e | `Fig2.pdf` e | Most rejections are not caused by Galaxy (22 of 111 implicate it) | Supp. Table 14 |
| Fig. 3a | `Fig3.pdf` a | Every core workbench operation was used, per benchmark | Supp. Table 20 |
| Fig. 3b | `Fig3.pdf` b | Workflow-derived tasks relied more on domain-analysis tools (28%, 40%, 69% of jobs) | Supp. Tables 11, 21–23 |
| Fig. 3c | `Fig3.pdf` c | User-defined-tool use depends on the model | Supp. Tables 24, 27 |
| Fig. 3d | `Fig3.pdf` d | Recorded errors point to inputs and parameters | Supp. Table 32 |
| Fig. 3e | `Fig3.pdf` e | Galaxy silently changed requested values in 16–30% of tool runs | Supp. Table 37; Supp. Data 3 |
| Fig. 4a | `Fig4.pdf` a | Open-ended-code runs spread across more command-line software | Supp. Table 39 |
| Fig. 4b | `Fig4.pdf` b | Replicate tool sets agree most on workflow-derived tasks | Supp. Tables 41–43 |
| Fig. 4c | `Fig4.pdf` c | Fewer non-unanimous triplicates in Galaxy in every benchmark (33/28, 35/22, 11/5) | Supp. Table 44 |
| Fig. 4d | `Fig4.pdf` d | Different divergence mechanisms: hand-written methods and version differences 67% vs 14%; interface traps 0% vs 17% | Supp. Table 48 |
| Fig. 5a | `Fig5.pdf` a | 4–5× input tokens on platform-neutral tasks, 1.9× on IWC | Supp. Tables 49–51 |
| Fig. 5b | `Fig5.pdf` b | About half of interface activity is tool search and inspection | Supp. Table 53 |
| Fig. 5c | `Fig5.pdf` c | More tokens did not mean more accuracy (paired forest plots) | Supp. Table 54 |
| Fig. 5d | `Fig5.pdf` d | Six findings recoverable from the Galaxy record; 67% → 14% | Supp. Tables 16, 18, 37, 48 |
| Extended Data Fig. 1a–d (new) | `ED_Fig1.tif` | Archive; audit pipeline; consensus-proxy validation (mean absolute error 2.6); consensus support per task | Supp. Table 6 |
| Extended Data Fig. 2a | `ED_Fig2.tif` a | Replicate tool sets agree most on IWC, in both environments | Supp. Table 10 |
| Extended Data Fig. 2b | `ED_Fig2.tif` b | bix-45-q1: every Galaxy run returned the current-PhyKIT value | Supp. Tables 15–16 |
| Extended Data Fig. 2c | `ED_Fig2.tif` c | bix-43-q2: the same value was accepted or rejected depending on the verifier | Supp. Table 17 |
| Extended Data Fig. 2d | `ED_Fig2.tif` d | Low IWC scores re-examined against independent references | Supp. Tables 13, 18 |
| Extended Data Fig. 3a | `ED_Fig3.tif` a | User-defined tools often failed without an error message; 784 identical retries | Supp. Table 28 |
| Extended Data Fig. 3b | `ED_Fig3.tif` b | Failed interface calls by cause, per 1,000 calls | Supp. Table 34 |
| Extended Data Fig. 3c | `ED_Fig3.tif` c | Tools whose requested values were most often changed | Supp. Table 37 |
| Extended Data Fig. 3d | `ED_Fig3.tif` d | Engineering targets with evidence and measures | Supp. Table 38 |
| Extended Data Fig. 4a | `ED_Fig4.tif` a | Triplicate outcomes by configuration | Supp. Table 44 |
| Extended Data Fig. 4b | `ED_Fig4.tif` b | Prompt length and workload did not consistently predict failures | Supp. Table 45 |
| Extended Data Fig. 5a | `ED_Fig5.tif` a | Token overhead smallest on IWC for every configuration | Supp. Table 52 |
| Extended Data Fig. 5b | `ED_Fig5.tif` b | Direct calls to Galaxy's programming interface, by operation | Supp. Table 53 |

## 4. Edits the draft text needs

Items 1–17 are factual or call-out corrections checked against the archive. Items 18–20 keep the text consistent with the redesigned figures.

| # | Location in the draft | Current text | Change to | Evidence |
|---|---|---|---|---|
| 1 | Design paragraph; editorial note 1 | "21,880 recorded Galaxy jobs" | "23,080 recorded Galaxy analysis jobs" (5,042 + 16,686 + 1,352, excluding data uploads) | Extended Data Fig. 1a |
| 2 | Design paragraph, after "69,812 recorded MCP calls" | — | add "(Extended Data Fig. 1a,b)" | Extended Data Fig. 1 is new; without it the Extended Data numbering starts at 2 |
| 3 | Section 1, first paragraph | "a median Galaxy score of 1.000 for every configuration" | "a median Galaxy score of 1.000 for three of four configurations (0.998 for Luna)" | Supp. Table 7 |
| 4 | Section 1, consensus-proxy sentence | — | add "(Extended Data Fig. 1c,d and Supplementary Table 6)" | New validation panel and table |
| 5 | Section 1, third paragraph | "(Fig. 2e and Supplementary failure ledger)" | "(Fig. 2e and Supplementary Table 14)" | Ledger is Supp. Table 14 |
| 6 | Section 1, bix-45-q1 sentence | "(Extended Data Fig. 2b,c and Supplementary Tables B12 and B13)" | "(Extended Data Fig. 2b and Supplementary Tables 15 and 16)" | Panel c is bix-43-q2 |
| 7 | Section 1, bix-43-q2 clause | "(Supplementary Table B8)" | "(Extended Data Fig. 2c and Supplementary Table 17)" | Panel c shows this case |
| 8 | Section 2, failure-count sentence | "3,454 before any job existed and 3,677 afterwards" | add "; 258 matched no cause" | The three groups sum to 7,389 (Supp. Table 34) |
| 9 | Section 2, taxonomy sentence | "(Extended Data Fig. 3b and Supplementary Table X5)" | "(Extended Data Fig. 3b and Supplementary Table 34)" | X5 (now Supp. Table 33) lists error-message indicators, not the causes |
| 10 | Section 2 | "Installed-wrapper errors usually retained stderr (85.5% in BixBench)" | "BixBench error jobs usually retained an error message (85.5%; Supplementary Table 33)" | Supp. Table 33 covers all BixBench error jobs, not installed wrappers only |
| 11 | Section 2, Section 4, editorial note 8 | "769 blind identical resubmissions" | "784" (615 of which failed again) | 769 was a partial count; Supp. Table 28 |
| 12 | Section 3, first paragraph | "GPT-5.5 doing so six to seven times more often than DeepSeek (Fig. 4a)" | "about seven times more often than DeepSeek in BixBench (66.7% versus 9.3%) and twice as often in CompBioBench (88.3% versus 43.3%) (Fig. 3c)" | Supp. Table 24. Cite Fig. 4a on the preceding BWA/minimap2 sentence instead: "(Fig. 4a and Supplementary Table 39)" |
| 13 | Section 3, identical-answers sentence | "(Fig. 4d and Supplementary Table X16)" | "(Supplementary Table 46)"; add "(Fig. 4d and Supplementary Table 48)" to the sentence beginning "Quantitatively, self-implementation…" | Fig. 4d shows divergence mechanisms |
| 14 | Section 4, discovery sentence | "(Fig. 5b and Extended Data Fig. 5b)" | "(Fig. 5b and Supplementary Table 53)"; add "(Extended Data Fig. 5b)" after "580 of 600" | Extended Data Fig. 5b shows direct calls to Galaxy's programming interface |
| 15 | Section 4, third paragraph | "median input was 2.2 million tokens in accepted Galaxy runs and 2.8 million in rejected ones" | add "after excluding the four tasks that failed in nearly every run (2.20 versus 1.95 million across all runs)" | Recomputed from per-run usage |
| 16 | Call-out plan, Fig. 5d | "five reconstructed findings" | "six" | Text and figure list six |
| 17 | Every "Supplementary Table B…/C…/I…/X…" | archive IDs | sequential numbers (see §5) | Nature numbers supplementary items in citation order |
| 18 | Design paragraph | "(Fig. 1a)" after the Galaxy interface; "(Fig. 1b)" after open-ended code | swap to "(Fig. 1b)" and "(Fig. 1a)"; better still, introduce the reference condition first | Fig. 1 now shows open-ended code in panel a |
| 19 | Throughout | "mixed cells"; "MCP calls"; "non-utility Tool Shed jobs" | use the figure terms "non-unanimous triplicates", "calls to the Galaxy interface" and "jobs run with domain-analysis tools", or define each at first use, e.g. "mixed cells (non-unanimous triplicates)" | The figures avoid unexplained terms; the text and figures should use the same words |
| 20 | Wherever paired values are reported | e.g. "86.5% … against 85.2% under open-ended code" | optionally report open-ended code first ("85.2% with open-ended code and 86.5% with Galaxy") | Matches the figure order and the reference role of open-ended code |

**Not re-derived by these scripts.** These draft numbers come from the prior audit and are consistent with the report:
- the benchmark-integrity counts (38 runs, 29 accepted, 37 from one configuration);
- 12 versus 8 tasks for failed-call differences;
- 93/213/41 candidate recovery episodes.

## 5. Supplementary Table numbering

Tables are numbered in order of first citation. Archive IDs map to numbers as follows (NEW = introduced by this audit):

X1 → 1 · B1 → 2 · B10 → 3 · B11 → 4 · C1 → 5 · NEW consensus proxy → 6 · I1 → 7 · I2 → 8 · I3 → 9 · X3 → 10 · X19 → 11 · I4 → 12 · I6 → 13 · NEW failure ledger → 14 · B12 → 15 · B13 → 16 · B8 → 17 · I5 → 18 · C4 → 19 · X14 → 20 · B9 → 21 · C8 → 22 · I10 → 23 · X12 → 24 · X13 → 25 · X15 → 26 · I11 → 27 · NEW user-defined-tool reliability → 28 · B4 → 29 · C3 → 30 · I7 → 31 · X18 → 32 · X5 → 33 · NEW failed-call causes → 34 · X10 → 35 · C7 → 36 · NEW parameter changes → 37 · X7 → 38 · X9 → 39 · I12 → 40 · B5 → 41 · C5 → 42 · I8 → 43 · NEW non-unanimous triplicates → 44 · X11 → 45 · X16 → 46 · B6 → 47 · NEW divergence mechanisms → 48 · B7 → 49 · C6 → 50 · I9 → 51 · X2 → 52 · NEW discovery and direct interface use → 53 · B15 → 54 · I13 → 55.

**Twelve archive tables are not cited by the draft.** They are appended as 56–67: B2, B3, B14, B16, C2, C9, C10, X4, X6, X8, X17 and X20. Cite them at the location suggested in the index sheet or delete them.

**How the archive tables were adapted.**
- Environment columns and rows are reordered so that open-ended code comes first.
- Benchmark short names are spelled out.
- A glossary sheet defines remaining technical terms.
- Cell values are otherwise as archived.

To renumber after editing the text, change `ORDER` and `UNCITED` in `scripts/make_supplement.py` and rerun it.

## 6. Nature Methods and accessibility compliance

**Verified against the Nature Portfolio figure guide (research-figure-guide.nature.com, checked 25 September 2026):**
- **Main figures.** 183 mm wide, ≤170 mm tall; vector PDF with editable, embedded TrueType text; RGB.
- **Extended Data.** 179 mm × ≤165 mm (limit 180 × 170 mm); TIFF at 300 dpi, RGB with no alpha, under 1 MB each; EPS also supplied. Five items, against a limit of 10.
- **Text.** Arial at 5–7 pt, with 8 pt bold lowercase panel labels; a script audit found no text outside these sizes. Text is black or grey, never coloured.
- **Source Data.** One workbook per figure, one sheet per panel, with open-ended-code columns first.

**Colour-vision accessibility:**
- **Palette check.** Palettes were checked with a simulation-based validator:
  - environment pair: ΔE 21.9 under protanopia and 31.2 under normal vision;
  - cause and mechanism palettes: neighbouring colours all ΔE ≥ 9.6 under deuteranopia.
- **Colour pairs kept apart.** The one weak pair (bluish green versus reddish purple, ΔE 7.6) is never placed side by side.
- **Visual simulation.** Every figure was simulated under protanopia, deuteranopia, tritanopia and greyscale (`qa/cvd/`, Machado 2009 matrices). Environments stay separable in all four through colour and shape; categories through colour plus printed counts.

**To confirm on the current Nature Methods author pages** (behind a login when checked):
- the display-item limit;
- the legend word limit (legends here run 75–209 words);
- the Supplementary Table format;
- the Reporting Summary template;
- the data and code citation style.

## 7. The two open choices in the draft

- **Heading of Section 3.** Recommendation: "Galaxy changes the sources of agent variability". Fig. 4c,d state this directly.
- **The superseded Claude Code harness.** Recommendation: keep it as the scaffold-dependence contrast. It is visually separated in every figure; justify it in one Methods sentence (same model, different harness, BixBench only, excluded from pooled estimates).

## 8. Reproducing everything

From the repository root, with Python 3.12 and `pip install -r manuscript_material/scripts/requirements.txt`:

```bash
python manuscript_material/scripts/build_data.py       # ~10 s: assembles every panel's data from the archive
python manuscript_material/scripts/fig_main.py         # Figs. 1-5 + Source Data
python manuscript_material/scripts/fig_ed.py           # Extended Data Figs. 1-5 + Source Data
python manuscript_material/scripts/make_supplement.py  # Supplementary Tables, Data 1-3, Supplementary Information PDF
python manuscript_material/scripts/md_to_docx.py       # legends and statements as .docx
python manuscript_material/scripts/cvd_check.py        # colour-vision simulations for checking (qa/cvd/)
```

No agent code is executed, no Galaxy server is contacted and no score is regraded.
