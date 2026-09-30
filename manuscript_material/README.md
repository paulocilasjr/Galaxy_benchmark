# Manuscript material for Nature Methods submission

This folder holds every display item, supplementary file, Source Data workbook and statement that the Results text (`Results_section_final`) calls for. Every figure number, Extended Data number, Supplementary Table number and Supplementary Note number matches a call-out in that text. Each file is generated from the archived evidence by the scripts in `scripts/`, so every number traces back to a run, trace line or archive table.

## 1. Design rules applied to every figure and table

1. **The open-ended code condition is the reference condition and always comes first.** This holds for panel order (Fig. 1a before 1b), row order, legends, table columns and Source Data columns. Every condition difference is Galaxy − open-ended code.
2. **Colour has one meaning.** Vermillion (#D55E00) is the open-ended code condition and blue (#0072B2) the Galaxy condition, everywhere. Panels that show only Galaxy-condition runs use Galaxy blue. Benchmarks are never colour-coded; panels and labels separate them.
3. **Colour-vision safety.** The colours come from the Okabe–Ito palette, which Nature Methods itself recommended (Wong, *Nat. Methods* **8**, 441; 2011). Execution condition is also encoded by shape (squares for open-ended code, circles for Galaxy), so it survives greyscale printing. Every category palette carries direct counts or labels as a second cue.
4. **No abbreviations.** Terms such as G/C, pp, CI, MCP, UDT, CC*, MAE, DE, QC, AMR and r1 are spelled out or replaced by plain descriptions in all figure text.
5. **Related results share one plot type.** Fig. 2a, c and d use the same layout: replicate runs and mean on the left, condition difference with its interval on the right, with identical rows. Fig. 3a repeats one small-multiple layout for the three benchmarks, and Fig. 4a–c repeat one stacked-bar layout on shared rows. Every multi-benchmark panel orders the benchmarks IWC, BixBench-Verified-50, CompBioBench.
6. **One vocabulary everywhere.** Every figure, legend, table, data file and statement uses the official terms in `glossary/` (see §5).
7. **Every panel title states its finding** (for example "BixBench-Verified-50: the Galaxy condition had more unanimous and fewer split replicate sets"). Axis labels say what is measured and in which unit; interval types and reference lines are named on the panel. Text is black or grey, never coloured.

## 2. What is here

| Folder | Contents | Submit? |
|---|---|---|
| `figures/` | `Fig1.pdf` … `Fig5.pdf`: vector PDFs with editable, embedded TrueType text; 183 mm wide and 112–170 mm tall. `previews/` holds 300-dpi PNGs. | PDFs: yes |
| `extended_data/` | `ED_Fig1.tif` … `ED_Fig8.tif` (300 dpi, RGB, LZW, under 350 kB each) plus the same figures as `.eps`; 179 mm wide and 72–120 mm tall. `previews/` holds PNGs. | TIFF (or EPS): yes |
| `legends/` | `Figure_legends.md` / `.docx`: legends for all 13 figures. In the .docx each legend is one paragraph, in journal style. | Paste into the manuscript |
| `supplementary/` | `Supplementary_Information.pdf`: glossary, Supplementary Notes 1–9 and legends for all tables and data files. | Yes |
| | `Supplementary_Tables.xlsx`: Supplementary Tables 1–67, plus index and glossary sheets. | Yes |
| | `Supplementary_Data_1_run_summaries.xlsx`: 4,240 runs. | Yes |
| | `Supplementary_Data_2_failed_Galaxy_interface_calls.xlsx`: 7,389 calls. | Yes |
| | `Supplementary_Data_3_parameter_substitutions.xlsx`: 2,085 calls. | Yes |
| | `Supplementary_Table_crosswalk.csv`: each Supplementary Table number with its archive ID, where the Results cite it, and a proposed number in citation order. | Authors only |
| `source_data/` | `Source_Data_Fig1–5.xlsx` and `Source_Data_ED_Fig1–8.xlsx`, one sheet per panel. | Yes |
| | `figure_data.json` and `derived/` are build intermediates; `derived/` contains local file paths. | No |
| `glossary/` | `Glossary.md` / `.xlsx` / `.docx`: the 68 official terms, with status (original, sharpened or new), definition, example and retired wording. Also embedded in the Supplementary Information and the Supplementary Tables workbook. | Yes, via the Supplementary Information |
| `qa/cvd/` | Every figure simulated under protanopia, deuteranopia, tritanopia and greyscale, for checking. | No |
| `statements/` | Data availability, Code availability and Reporting Summary notes (.md and .docx). Placeholders are marked `[Authors: …]`. | Paste into the manuscript and forms |
| `scripts/` | Generators and `requirements.txt` (see §8). | Via the code repository |

The per-case evidence behind Fig. 5 and Supplementary Table 14 is `individual_error_analysis.md` at the repository root.

## 3. Call-out map: the Results text to figures and tables

**Main-figure titles.** Each title opens that figure's legend, as Nature Methods requires, and is also stored as the PDF's title metadata. The image itself carries no title. Titles for Figs. 2–5 are the Results section headings, with "configurations" written as "model configurations" in Fig. 4 to follow the glossary. Edit the titles in `scripts/figure_titles.json` and in the legends.

- **Fig. 1** | Study design: the same model configurations perform each task in the open-ended code condition and in the Galaxy condition.
- **Fig. 2** | Galaxy-mediated execution preserves benchmark performance.
- **Fig. 3** | Model configurations achieve similar performance through different Galaxy strategies.
- **Fig. 4** | Replicate agreement separates model configurations that run-level accuracy conflates.
- **Fig. 5** | Trace-level analysis distinguishes benchmark artifacts from platform and agent failures.

| Call-out in the Results | File, panel | Finding shown | Supporting tables |
|---|---|---|---|
| Fig. 1a | `Fig1.pdf` a | Open-ended code condition: model configuration and agent harness in an unrestricted shell | — |
| Fig. 1b | `Fig1.pdf` b | Galaxy condition: the Galaxy interface (tool search, parameter descriptions, history inspection, job submission and monitoring, user-defined tools) | — |
| Fig. 1c | `Fig1.pdf` c | Three benchmarks, five model configurations, three replicate runs; endpoint of each benchmark | Supp. Table 1 |
| Extended Data Fig. 1 | `ED_Fig1.tif` a, b | Archive (4,240 runs, 4,228 traces, 23,080 Galaxy analysis jobs, 69,812 Galaxy interface calls) and audit pipeline | Supp. Notes 1, 2; Supp. Data 1 |
| Fig. 2a | `Fig2.pdf` a | IWC mean output agreement 0.940 → 0.980, +0.040 (0.010 to 0.078); medians per model configuration | Supp. Table 7 |
| Fig. 2b | `Fig2.pdf` b | IWC per task; six tasks at ≥0.998; notes 1–4 give every run below 0.5 | Supp. Tables 9, 18 |
| Extended Data Fig. 3 | `ED_Fig3.tif` a, b | IWC sensitivity: 0.040 → 0.004 without zero-scored tasks; Sol and Luna change sign when leaving one task out; every run below 0.5 | Supp. Tables 12, 18 |
| Fig. 2c | `Fig2.pdf` c | BixBench-Verified-50: 519/600 versus 511/600, +1.3 (−3.5 to 6.3); per model configuration +2.0, +2.0, 0.0, +1.3; Claude Code +10.7 | Supp. Tables 2–4 |
| Fig. 2d | `Fig2.pdf` d | CompBioBench: 86.9 versus 86.7; +0.3, +0.7, 0.0, 0.0 (archived reported benchmark scores) | Supp. Tables 5, 61 |
| Extended Data Fig. 2 | `ED_Fig2.tif` a, b | Consensus proxy: mean absolute error 2.6; 82 strong-consensus tasks; 33 versus 40 deviations | Supp. Table 6 |
| Section 1, answer consistency | — | 62 versus 58 of 100 tasks with one distinct answer across all 12 runs | Supp. Table 60a |
| Fig. 3a | `Fig3.pdf` a | Galaxy-condition performance by model configuration, one 70–100% axis: IWC 99.9/99.1/95.4/93.7% (output agreement 0.999/0.991/0.954/0.937); BixBench-Verified-50 89.3/88.7/86.0/82.0 (Claude Code 80.0); CompBioBench 86.7/91.7/85.0/84.3 | Supp. Tables 55, 58, 61 |
| Fig. 3b | `Fig3.pdf` b | User-defined-tool requests: IWC 0% (not offered; 0 of 120 runs); BixBench-Verified-50 67/35/39/9%; CompBioBench 88/80/61/43% | Supp. Table 24 |
| Extended Data Fig. 4 | `ED_Fig4.tif` a, b | Domain-skill uptake; DeepSeek V4 Pro (Codex) imported the interface library in 31 of 150 runs | Supp. Table 20 |
| Fig. 3c | `Fig3.pdf` c | Median input-token usage per run, IWC 2.35/4.23/6.34/10.2 million; BixBench-Verified-50 1.19/1.56/3.52/5.03; CompBioBench 1.73/3.75/8.48/10.2 | Supp. Table 49 |
| Extended Data Fig. 6 | `ED_Fig6.tif` a, b | Input-token usage versus performance; ratios 1.33/4.08/3.44 and model differences −0.7/−3.3/−7.3 versus GPT-5.5 | Supp. Tables 49, 54 |
| Fig. 4a | `Fig4.pdf` a | IWC: 5 of 40 Galaxy-condition versus 11 of 39 open-ended code sets split (within-set range above 0.05) | Supp. Tables 8a, 44 |
| Fig. 4b | `Fig4.pdf` b | BixBench-Verified-50: 197 versus 187 sets at 3/3, 28 versus 33 split, 25 versus 30 at 0/3 | Supp. Table 56 |
| Fig. 4c | `Fig4.pdf` c | CompBioBench, 82 strong-consensus tasks: 305 versus 293 sets at 3/3, 22 versus 35 split, 1 versus 0 at 0/3 (Galaxy versus open-ended code) | Supp. Table 44b,c |
| Section 3, CompBioBench distinct answers | — | One distinct answer in 333 versus 321 of 400 sets | Supp. Tables 44d, 60 |
| Section 3, IWC within-set ranges | — | Median within-set ranges 0.0000/0.0011/0.0022/0.0047 (all ten tasks); 5 versus 11 split sets | Supp. Table 8a |
| Fig. 4d | `Fig4.pdf` d | Divergence mechanisms: Galaxy 13, 6 and 6 of 36; open-ended code 30 of 45 hand-written method or software version | Supp. Table 48 |
| Extended Data Fig. 5 | `ED_Fig5.tif` a, b | Divergence mechanisms by model configuration; the five split IWC Galaxy-condition sets | Supp. Tables 8, 48 |
| Fig. 4e | `Fig4.pdf` e | Run-level versus unanimous accuracy; −1.3 (GPT-5.5), −6.0 (DeepSeek V4 Pro), −16.0 (Claude Code); range 9.3 → 24.0 points | Supp. Table 56a,b |
| Section 3, tool-set fingerprints | — | Identical Galaxy tool-set fingerprints in 43.5% of 0/3 and 15.3% of 3/3 sets | Supp. Table 47 |
| Fig. 5a | `Fig5.pdf` a | 93 task cases: 30 reference or evaluator (6, 4, 20), 52 agent analysis, 8 Galaxy, 3 other; Galaxy contributed in 14 | Supp. Table 14a–c |
| Extended Data Fig. 8 | `ED_Fig8.tif` a–c | Answer retrieval (26 task cases), local computation (15 correct CompBioBench answers), cross-run copying (2 runs) | Supp. Table 14b,d |
| Fig. 5b | `Fig5.pdf` b | bix-35-q1: 15/15 versus 14/15; 7 of 15 Galaxy histories with a substituted job; six recovered | — |
| Extended Data Fig. 7 | `ED_Fig7.tif` a, b | bix-35-q1: the metric each PhyKIT job executed; request shapes | — |
| Fig. 5c | `Fig5.pdf` c | contaminated-rna-q1: 12/13 versus 9/12; core_nt did not complete in three runs; 8,793 Hydra reads; 195 Epstein–Barr virus reads | — |

## 4. Where the Results text and the archive disagree

Where the text and the archived data disagree, the data are kept. `Results_text_edits.md` lists every edit the text needs, with the current wording, the replacement wording and the table or figure that supports it:
- A, 21 edits where the text contradicts the data;
- B, 7 consistency edits (terminology and missing call-outs);
- C, the numbering changes needed for submission.

Numbers not listed there were checked and match, including 519/511, +2.0/+2.0/0.0/+1.3, 197/187, 28/33, 25/30, 333/321, 62/58, 43.5%/15.3%, the input-token medians and ratios, and the task-audit counts (93; 30 = 6 + 4 + 20; 52; 8; 14; 26; 15; 2).

## 5. Glossary

The authoritative glossary is `glossary/Glossary.md` (also `.xlsx` and `.docx`), generated from `scripts/glossary.py`. It holds 68 terms: 36 adopted as supplied, 6 sharpened and 26 new.

Terms added for the new Results text:
- *Replicate agreement* (the Section 3 umbrella: outcome repeatability or answer consistency);
- *Run-level accuracy; unanimous accuracy*;
- *Task case* and *primary cause category* (C1–C8) for the task-level audit;
- *Integrity flag*, *benchmark-answer retrieval*, *local computation (Galaxy condition)* and *cross-run output reuse*;
- *Interface-binding failure* (bix-35-q1).

The run-level *primary cause; secondary cause* now says it applies to the failure ledger. Earlier additions (benchmark, platform-neutral and workflow-derived benchmark, agent harness, split replicate set, scored-correct and scored-incorrect run, consensus proxy, Galaxy interface call, direct Galaxy API call, analysis history, Galaxy analysis job, probe tool, parameter substitution, adjudication confidence, divergence mechanism, verifier mode) are unchanged.

Wording in the Results that differs from the glossary: "configuration" or "configurations" → "model configuration(s)"; "replicates" → "replicate runs"; "rejected run" → "scored-incorrect run" (keep "rejected" for the evaluator's action); "returned benchmark score" → "reported benchmark score"; "UDTs" and "MCP" are defined at first use and should not reappear as abbreviations in figures.

## 6. Supplementary Table numbering

The Results text already cites Supplementary Table numbers, so the numbering was kept and each cited table was given the content the text quotes. Blocks were added (marked a, b, … in each sheet, with the archived table kept as the last block):

| Table | Added | Text it supports |
|---|---|---|
| 3 | Task–model-configuration pairs scored correct in one condition only (9/4 of 250; 5/3 of 200) | Section 1 |
| 7 | Median and mean output agreement per model configuration, nine and ten tasks | Section 1, Fig. 2a |
| 8 | Within-set output-agreement ranges on all ten tasks; split sets | Section 3, Fig. 4a |
| 14 | Rebuilt as the task-level audit: primary cause by benchmark, flags, all 93 task cases, integrity problems; the run-level failure ledger kept as block e | Section 4, Fig. 5a |
| 20 | Domain-skill uptake; interface-library scripting | Section 2, Extended Data Fig. 4 |
| 44 | Split replicate sets by benchmark (CompBioBench 22/35 of 328, with 3/3 and 0/3); distinct answers per CompBioBench replicate set (333/321) | Section 3, Fig. 4a,c |
| 49 | Median input-token usage by benchmark, model configuration and condition | Section 2, Fig. 3c |
| 56 | Run-level and unanimous accuracy, per model configuration and pooled | Section 3, Fig. 4b,e |
| 60 | Tasks with one distinct answer across all 12 runs (62/58) | Section 1 |
| 61 | Reported benchmark scores by model configuration, with archive labels | Sections 1 and 2 |

**Cited:** 1–9, 12, 14, 18, 20, 24, 44, 47–49, 54–56, 58, 60, 61 (24 tables), plus 11 once edit 5 of `Results_text_edits.md` is made. **Not cited in the Results** (42): 10, 13, 15–17, 19, 21–23, 25–43, 45, 46, 50–53, 57, 59, 62–67. The index sheet marks them. Cite them in Methods or delete them before submission.

**Citation-order renumbering**, if required (current → proposed): 1→1 · 7→2 · 9→3 · 12→4 · 18→5 · 2→6 · 3→7 · 4→8 · 5→9 · 6→10 · 60→11 · 55→12 · 58→13 · 61→14 · 11→15 · 24→16 · 20→17 · 49→18 · 54→19 · 56→20 · 44→21 · 8→22 · 48→23 · 47→24 · 14→25; uncited tables follow as 26–67. To apply it, edit `ORDER`/`UNCITED` in `scripts/make_supplement.py`, rerun it and update the text citations.

**How the archive tables were adapted.** Execution-condition columns and rows are reordered so that the open-ended code condition comes first. Titles, headers and legends use the official terms, and benchmark short names are spelled out. Cell values are otherwise as archived.

## 7. Nature Methods and accessibility compliance

**Checked against the Nature Portfolio figure guide (research-figure-guide.nature.com, checked 25 September 2026):**
- **Main figures.** 183 mm wide, 112–170 mm tall; vector PDF with editable, embedded TrueType text; RGB.
- **Extended Data.** 179 mm wide, 72–120 mm tall (limit 180 × 170 mm); TIFF at 300 dpi, RGB with no alpha, each under 350 kB; EPS also supplied. Eight items, against a limit of 10.
- **Text.** Arial at 5–7 pt, with 8 pt bold lowercase panel labels; a script raises any smaller text to 5 pt. No figure text is coloured; condition is carried by the adjacent marker.
- **Source Data.** One workbook per figure, one sheet per panel, with open-ended code columns first.

**Colour-vision accessibility.** Palettes come from the Okabe–Ito set. The execution-condition pair stays separable under protanopia (ΔE 21.9). Every figure is simulated under protanopia, deuteranopia, tritanopia and greyscale in `qa/cvd/` (Machado 2009 matrices); execution conditions stay separable through colour and shape, and categories through colour plus printed counts. The one weak pair (bluish green versus reddish purple) is never placed side by side.

**To confirm on the current Nature Methods author pages:** the display-item limit, the legend word limit, the Supplementary Table format, the Reporting Summary template and the data and code citation style.

## 8. Reproducing everything

From the repository root, with Python 3.12 and `pip install -r manuscript_material/scripts/requirements.txt`:

```bash
python manuscript_material/scripts/build_data.py       # assembles every panel's data from the archive and individual_error_analysis.md
python manuscript_material/scripts/fig_main.py         # Figs. 1-5 + Source Data
python manuscript_material/scripts/fig_ed.py           # Extended Data Figs. 1-8 + Source Data
python manuscript_material/scripts/make_supplement.py  # Supplementary Tables, Data 1-3, Supplementary Information PDF
python manuscript_material/scripts/glossary.py         # glossary/ (.md, .xlsx, .docx)
python manuscript_material/scripts/md_to_docx.py       # legends and statements as .docx
python manuscript_material/scripts/cvd_check.py        # colour-vision simulations for checking (qa/cvd/)
```

No agent code is executed, no Galaxy server is contacted, no score is regraded and no file under `ground_truth/` is read.
