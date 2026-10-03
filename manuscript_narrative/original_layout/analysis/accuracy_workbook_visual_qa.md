> **Superseded record (2 October 2026 revision).** This visual QA applies to the earlier build. Figures 1 and 4–6, the Source Data workbook and the DOCX were regenerated; current render hashes and the visual check are in `../visual_validation.json`.

# Source Data visual QA: first twelve alphabetical sheet previews

Final rebuild follow-up: `F2_sensitivity.population` now wraps, including the full BixBench C1/C2/C3/C6 suffix and ATAC identifier. The required clipping correction identified below has been implemented and visually verified. Midword wrapping remains a minor stylistic matter, not lost content.

Inspected each named PNG at native resolution. Previews wider than 2,048 pixels were also inspected through overlapping 1,900-pixel crops saved temporarily under `/private/tmp/original-workbook-qa-accuracy`; crop boundaries are not workbook clipping. These previews show each sheet's header and initial data rows, not every record in the workbook.

| Preview | Finding |
|---|---|
| `Audit_tasks.png` | Header and displayed values complete. Long semicolon-delimited tags wrap within words; awkward but readable. Widening the tag column or inserting display breaks after semicolons would improve scanning. |
| `Column_dictionary.png` | Displayed definitions and headers readable, no clipping. |
| `F1_design.png` | Headers/numbers complete. Runs-per-arm values closely abut endpoint text; a small left indent in endpoint cells would improve separation. |
| `F2_scores.png` | Headers and displayed numerical values complete. Scale values closely abut endpoint text but remain distinguishable. |
| `F2_sensitivity.png` | **Required fix:** `population` strings truncate at the column A/B boundary. The BixBench identifier does not show its C3/C6 suffix, and the ATAC identifier abuts the following IWC benchmark value. Enable wrap for population, size row height for complete text, or widen column A to fit the longest value. All displayed numbers and headers complete. |
| `F3_UDT_association.png` | No clipping. `correct_runs` values closely abut the interpretation sentence; indent that text slightly for separation. |
| `F3_UDT_usage.png` | All header text/numbers present. Long identifiers wrap inside words such as `runs` (`ru` / `ns`); widening those columns or wrapping at underscores would be more comfortable. |
| `F3_repeatability.png` | All displayed numerical values and headers present. No undersized font at native resolution. |
| `F4_cases.png` | All displayed prose, headers and numerical fields present across four overlapping crops. Large horizontal width supports lengthy evidence/caveat cells without truncation. The task identifier in `audit_task` wraps inside an underscore-delimited name but remains complete. |
| `F4_categories.png` | All values and headers present. Percent values closely abut the unit text; add a small indent in unit cells. |
| `F4_error_counts.png` | All headers and numerical values complete and readable. |
| `F4_tags.png` | All headers and numerical values complete. Renderer displays Boolean tags as checkboxes; true/false states are visually distinguishable. |

No displayed number was clipped and no native-resolution font was undersized. Full-width PNGs may appear small when scaled into a chat window; that is a viewer effect. The identified population truncation is actual column-boundary clipping and requires a workbook-layout correction.
