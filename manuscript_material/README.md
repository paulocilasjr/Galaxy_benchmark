# Manuscript material for Nature Methods submission

This folder holds every display item, supplementary file, Source Data workbook and statement that the Results text (`Results_section_final`) calls for. Every figure number, Extended Data number, Supplementary Table number and Supplementary Note number matches a call-out in that text. Each file is generated from the archived evidence by the scripts in `scripts/`, so every number traces back to a run, trace line or archive table.

## 1. Design rules applied to every figure and table

1. **The open-ended code condition is the reference condition and always comes first.** This holds for panel order (Fig. 1a before 1b), row order, legends, table columns and Source Data columns. Every condition difference is Galaxy − open-ended code.
2. **Colour has one meaning.** Vermillion (#D55E00) is the open-ended code condition and blue (#0072B2) the Galaxy condition, everywhere. Panels that show only Galaxy-condition runs use Galaxy blue. Benchmarks are never colour-coded; panels and labels separate them.
3. **Colour-vision safety.** The colours come from the Okabe–Ito palette, which Nature Methods itself recommended (Wong, *Nat. Methods* **8**, 441; 2011). Execution condition is also encoded by shape (squares for open-ended code, circles for Galaxy), so it survives greyscale printing. Every category palette carries direct counts or labels as a second cue.
4. **No abbreviations.** Terms such as G/C, pp, CI, MCP, UDT, CC*, MAE, DE, QC, AMR and r1 are spelled out or replaced by plain descriptions in all figure text.
5. **Related results share one plot type.** Fig. 2a, c and d use the same layout: replicate runs and mean on the left, condition difference with its interval on the right, with identical rows. Fig. 3a repeats one small-multiple layout for the three benchmarks.
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
| Fig. 3a | `Fig3.pdf` a | Galaxy-condition performance by model configuration: IWC 0.999/0.991/0.954/0.937; BixBench-Verified-50 89.3/88.7/86.0/82.0 (Claude Code 80.0); CompBioBench 86.7/91.7/85.0/84.3 | Supp. Tables 55, 58, 61 |
| Fig. 3b | `Fig3.pdf` b | User-defined-tool requests: BixBench-Verified-50 67/35/39/9%; CompBioBench 88/80/61/43% | Supp. Table 24 |
| Extended Data Fig. 4 | `ED_Fig4.tif` a, b | Domain-skill uptake; DeepSeek V4 Pro (Codex) imported the interface library in 31 of 150 runs | Supp. Table 20 |
| Fig. 3c | `Fig3.pdf` c | Median input-token usage per run, IWC 2.35/4.23/6.34/10.2 million; BixBench-Verified-50 1.19/1.56/3.52/5.03; CompBioBench 1.73/3.75/8.48/10.2 | Supp. Table 49 |
| Extended Data Fig. 6 | `ED_Fig6.tif` a, b | Input-token usage versus performance; ratios 1.33/4.08/3.44 and model differences −0.7/−3.3/−7.3 versus GPT-5.5 | Supp. Tables 49, 54 |
| Fig. 4a | `Fig4.pdf` a | BixBench-Verified-50: 197 versus 187 sets at 3/3, 28 versus 33 split, 25 versus 30 at 0/3 | Supp. Table 56 |
| Fig. 4b | `Fig4.pdf` b | CompBioBench: one distinct answer in 333 versus 321 of 400 sets | Supp. Tables 44d, 60 |
| Section 3, IWC within-set ranges | — | Median within-set ranges 0.0000/0.0011/0.0022/0.0047 (all ten tasks); 5 versus 11 split sets | Supp. Table 8a |
| Fig. 4c | `Fig4.pdf` c | Divergence mechanisms: Galaxy 13, 6 and 6 of 36; open-ended code 30 of 45 hand-written method or software version | Supp. Table 48 |
| Extended Data Fig. 5 | `ED_Fig5.tif` a, b | Divergence mechanisms by model configuration; the five split IWC Galaxy-condition sets | Supp. Tables 8, 48 |
| Fig. 4d | `Fig4.pdf` d | Run-level versus unanimous accuracy; −1.3 (GPT-5.5), −6.0 (DeepSeek V4 Pro), −16.0 (Claude Code); range 9.3 → 24.0 points | Supp. Table 56a,b |
| Section 3, tool-set fingerprints | — | Identical Galaxy tool-set fingerprints in 43.5% of 0/3 and 15.3% of 3/3 sets | Supp. Table 47 |
| Fig. 5a | `Fig5.pdf` a | 93 task cases: 30 reference or evaluator (6, 4, 20), 52 agent analysis, 8 Galaxy, 3 other; Galaxy contributed in 14 | Supp. Table 14a–c |
| Extended Data Fig. 8 | `ED_Fig8.tif` a–c | Answer retrieval (26 task cases), local computation (15 correct CompBioBench answers), cross-run copying (2 runs) | Supp. Table 14b,d |
| Fig. 5b | `Fig5.pdf` b | bix-35-q1: 15/15 versus 14/15; 7 of 15 Galaxy histories with a substituted job; six recovered | — |
| Extended Data Fig. 7 | `ED_Fig7.tif` a, b | bix-35-q1: the metric each PhyKIT job executed; request shapes | — |
| Fig. 5c | `Fig5.pdf` c | contaminated-rna-q1: 12/13 versus 9/12; core_nt did not complete in three runs; 8,793 Hydra reads; 195 Epstein–Barr virus reads | — |

## 4. Where the Results text and the archive disagree

Every number in the Results text was checked against the archive. The items below need an edit or a decision. Everything else matched, including 519/511, +2.0/+2.0/0.0/+1.3, 197/187, 28/33, 25/30, 333/321, 62/58, 43.5%/15.3%, the input-token medians and ratios, and the task-audit counts (93; 30 = 6 + 4 + 20; 52; 8; 14; 26; 15; 2).

| # | Where | Text says | Archive shows | Suggested change |
|---|---|---|---|---|
| 1 | Introduction, endpoints | "the returned benchmark score from the official leaderboard" | The figures and tables use the archived scores. The archive labels 10 of the 24 paired scores as predicted. Two differ from the leaderboard: GPT-5.6 Sol Galaxy replicate run 3 (archive 91, leaderboard 92) and DeepSeek V4 Pro Galaxy replicate run 1 (83 versus 84). | Either say "reported benchmark scores as archived", or switch to leaderboard values. The leaderboard values change the text: Galaxy mean 87.1 (not 86.9); differences +0.3, +1.0, 0.0, +0.3; Sol 92.0 and DeepSeek V4 Pro 84.7 in Section 2. Tell me which and I will regenerate. |
| 2 | Section 1, IWC | "Median Galaxy-condition output agreement was 1.000 for every model configuration" | 1.000 for three model configurations; GPT-5.6 Luna 0.998 (nine tasks) | "…1.000 for three of four model configurations and 0.998 for GPT-5.6 Luna" (Supp. Table 7a) |
| 3 | Section 1, BixBench-Verified-50 | "nine of 250 task–configuration pairs were solved only in Galaxy and four only in open-ended code" | The 250 pairs include the superseded Claude Code harness, but the paragraph is about the four Codex model configurations. For those four the counts are 5 and 3 of 200. | Say which population is meant (Supp. Table 3a lists both) |
| 4 | Section 1, closing paragraph | "the only condition difference whose interval excluded zero occurred on the benchmark derived from Galaxy workflows" | The superseded Claude Code harness on BixBench-Verified-50, +10.7 (1.4 to 21.2), also excludes zero | Add "among the Codex model configurations" |
| 5 | Section 1, BixBench-Verified-50 | "every interval included zero" | GPT-5.5's interval is 0.00 to 5.30, so zero is its lower bound | Optional: "no interval excluded zero" |
| 6 | Section 2, IWC | "installed Galaxy tools, which supplied 69% of recorded analysis jobs" | 69.2% (935 of 1,352) is the share of Galaxy analysis jobs run with domain tools. IWC had no user-defined tools, so installed tools ran essentially every job. | "…in which domain tools accounted for 69% of Galaxy analysis jobs (Supplementary Table 11)" |
| 7 | Section 2, user-defined tools | "on CompBioBench the same ordering held" | Sol and Luna swap places: BixBench-Verified-50 Luna 39% > Sol 35%; CompBioBench Sol 80% > Luna 61% | "GPT-5.5 was again the highest and DeepSeek V4 Pro the lowest" |
| 8 | Section 2, domain skill | "in 44% to 55% of Galaxy-condition runs compared with 74% to 79%" | 55% is the Codex harness and 44% the superseded Claude Code harness. Denominator: 114 runs on the 38 BixBench-Verified-50 tasks with a relevant skill. In the open-ended code condition GPT-5.6 Luna (27%) was lower than DeepSeek V4 Pro (Codex, 41%). | "…55% (Codex harness) and 44% (Claude Code harness) of Galaxy-condition runs on the 38 BixBench-Verified-50 tasks with a relevant skill" (Supp. Table 20a) |
| 9 | Section 2, interface library | "In 51 of its 150 … runs" | 31 runs imported or called the interface library in shell code; 16 more only read its source. The 51 could not be reproduced. | "31" (Supp. Table 20b; Extended Data Fig. 4b) |
| 10 | Section 2 | "achieved an 80.0% score" | — | "80.0% accuracy" (glossary) |
| 11 | Section 3, definitions | Success on CompBioBench is "a match to the strong-consensus answer", but the result reported is one distinct answer (333/321), a consistency measure | By the consensus definition, 22 Galaxy-condition versus 35 open-ended code sets are split | Add the consensus-based split counts (Supp. Table 44b), or define answer consistency where it is used |
| 12 | Section 3 | "more unanimous sets and fewer split sets … in all three benchmarks" | Unanimous categories are not defined for IWC (continuous endpoint). Fewer split sets holds in all three. | "fewer split sets" |
| 13 | Section 3, IWC | Median within-set ranges 0.0000/0.0011/0.0022/0.0047 "(Supplementary Table 8)" | These are all-ten-task values; the archived Table 8 uses nine tasks (0.0000/0.0022/0.0044/0.0035). Table 8a now also holds the ten-task values. | Add "across all ten tasks" |
| 14 | Section 3, the five split IWC sets | "Amplicon denoising split on truncation lengths not stated in the task" | Amplicon denoising split only in the open-ended code condition. The five Galaxy sets are: peptide verification (three), mitochondrial genome assembly and host-read removal (a score conflict). | Replace amplicon denoising with host-read removal, or state that it split in the open-ended code condition (Extended Data Fig. 5b) |
| 15 | Section 3, PepQuery | "runs using only PepQuery2 2.0.2 reached 0.982 to 1.000" | GPT-5.6 Luna replicate run 3 used PepQuery2 and scored 0.900, because its unrestricted-modification search returned no sequences | Add the exception |
| 16 | Section 3, divergence | "scored-incorrect replicates on the platform-neutral benchmarks" | Divergence mechanisms were assigned on BixBench-Verified-50 only | "on BixBench-Verified-50" |
| 17 | Section 3, unanimous accuracy | "78.8% … 74.8%, a condition difference of 4.0 percentage points, compared with 1.3 points at the run level" | 78.8/74.8 pool all five model configurations; 1.3 pools four. Same five: run level +3.2 → unanimous +4.0. Four Codex: +1.3 → +3.0. | Compare like with like (Fig. 4d note; Supp. Table 56b) |
| 18 | Section 3, closing | "25 Galaxy-condition replicate sets never produced a correct answer … These tasks were therefore not resolved by changing model configuration" | The 25 sets span 7 distinct tasks. Only 3 (bix-45-q1, bix-53-q2, bix-61-q5) are 0/3 for all five model configurations. | "…including three tasks that no model configuration solved" |
| 19 | Section 4, integrity | "integrity problems affecting both conditions" | Local computation and cross-run copying are Galaxy-condition problems by definition. The execution condition of each retrieval run was not tabulated. | Drop "affecting both conditions", or I tabulate retrieval by condition |
| 20 | Section 4, contaminated-rna-q1 | "Each run then fell back to a narrower installed database … Epstein–Barr virus at 195 reads" | Two runs used standard-16 and answered Epstein–Barr virus. GPT-5.6 Luna replicate run 1 used a mitochondrion-only BLAST search and answered *Artemia franciscana*. | "Two runs fell back to … ; the third searched mitochondrial sequences only" |
| 21 | Section 4, contaminated-rna-q1 | "Agents in open-ended code … did not encounter this constraint" | The one failing open-ended code run (DeepSeek V4 Pro, replicate run 1) built its own database of human, mouse, rat and Epstein–Barr virus only, and answered rat | "…the one failing open-ended code run built a database that also lacked cnidarians" |
| 22 | Extended Data order | First citations run ED 1, 3, 2, 4, 6, 5, 8, 7 | Nature requires Extended Data to be cited in numerical order | Swap the numbers of ED 2/3, 5/6 and 7/8 in the text and I will rename the files, or reorder the call-outs |
| 23 | Supplementary Table order | First citations run 1, 7, 9, 12, 18, 2, 3, 4, 5, 6, 60, 55, … | 24 of 67 tables are cited, not in numerical order; 43 are uncited | Renumber using the last column of `Supplementary_Table_crosswalk.csv`, and cite or drop the uncited tables (§6) |
| 24 | Supplementary Notes | Notes 1, 2, 8 and 9 are cited | Notes 3–7 are not cited | Cite Note 7 at the consensus-proxy sentence and Note 6 at the audit paragraph; cite Notes 3–5 in Methods or drop them |

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
| 8 | Within-set output-agreement ranges on all ten tasks; split sets | Section 3 |
| 14 | Rebuilt as the task-level audit: primary cause by benchmark, flags, all 93 task cases, integrity problems; the run-level failure ledger kept as block e | Section 4, Fig. 5a |
| 20 | Domain-skill uptake; interface-library scripting | Section 2, Extended Data Fig. 4 |
| 44 | Distinct answers per CompBioBench replicate set, with totals (333/321) | Section 3, Fig. 4b |
| 49 | Median input-token usage by benchmark, model configuration and condition | Section 2, Fig. 3c |
| 56 | Run-level and unanimous accuracy, per model configuration and pooled | Section 3, Fig. 4a,d |
| 60 | Tasks with one distinct answer across all 12 runs (62/58) | Section 1 |
| 61 | Reported benchmark scores by model configuration, with archive labels | Sections 1 and 2 |

**Cited:** 1–9, 12, 14, 18, 20, 24, 44, 47–49, 54–56, 58, 60, 61 (24 tables). **Not cited in the Results** (43): 10, 11, 13, 15–17, 19, 21–23, 25–43, 45, 46, 50–53, 57, 59, 62–67. The index sheet marks them. Cite them in Methods or delete them before submission.

**Citation-order renumbering**, if required (current → proposed): 1→1 · 7→2 · 9→3 · 12→4 · 18→5 · 2→6 · 3→7 · 4→8 · 5→9 · 6→10 · 60→11 · 55→12 · 58→13 · 61→14 · 24→15 · 20→16 · 49→17 · 54→18 · 56→19 · 44→20 · 8→21 · 48→22 · 47→23 · 14→24; uncited tables follow as 25–67. To apply it, edit `ORDER`/`UNCITED` in `scripts/make_supplement.py`, rerun it and update the text citations.

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
