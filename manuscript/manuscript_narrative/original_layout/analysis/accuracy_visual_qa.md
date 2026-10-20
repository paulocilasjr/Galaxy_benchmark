> **Superseded record (2 October 2026 revision).** This visual QA applies to the earlier build. Figures 1 and 4–6, the Source Data workbook and the DOCX were regenerated; current render hashes and the visual check are in `../visual_validation.json`.

# Visual QA: original-layout Figures 1–3

Final rebuild follow-up: Fig. 2's sensitivity labels now wrap across two lines and are fully visible. The clipping identified below has been corrected and visually verified.

Inspected the full-resolution PNG previews after the initial figure build. No figure edits were made by this reviewer.

| Figure | Layout assessment | Population and interpretation assessment |
|---|---|---|
| Fig. 1 | All boxes, arrows, headings and table rows readable; no clipping or overlaps. | Correctly states four configurations, three independent replicate runs and two assigned arms. Counts 4,240 total → 3,840 primary → 3,816 endpoint runs agree with the archive. IWC primary performance uses nine of ten tasks and 108 runs per arm. Interface audit uses all 160 tasks; performance and primary matched-token analyses use 159. |
| Fig. 2 | Panel d's second y-axis label clips at the left image boundary: the beginning of “Exclude benchmark side C1 C2 C3 C6” is absent. Other panels are readable without overlap. | Binary score axes and IWC continuous agreement remain separate. Arm-specific intervals and sensitivity difference intervals are visually distinguishable. The zero-score exclusion interval includes zero at full precision. All abbreviated model names should be defined in the caption. |
| Fig. 3 | All five panels, intervals, tick labels and legend are readable without clipping or overlaps. | Panels a–b show differences in all-three-correct rates, not per-run accuracy. Panel c has a ratio equality reference at one and preserves benchmark-specific discordance definitions. UDT blue bars explicitly indicate a recorded ok job, correctly separate from returned-ok interface status; CompBio job completion count is 572 rather than 569 returned-ok runs. |

Required correction: shorten/wrap Fig. 2d's sensitivity label to “Exclude 15 audited\ntasks (C1/C2/C3/C6)” or “Exclude 15 audited tasks”, with category definitions in the caption. Retain the existing axis positions if the short label fits; otherwise enlarge the left margin without squeezing panel e.

Optional clarity: title Fig. 3a–b “all-three-correct rate” so the named outcome and percentage-point difference axis are explicit. Define “5.5”, “Sol”, “Luna” and “DeepSeek” in the captions as GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna and DeepSeek V4 Pro.

Fig. 1's matched-token population label was verified against the figure builder's selection of `task_scope == 'primary_endpoint'`; the token analysis also retains a separate all-ten-task IWC sensitivity, which is not this label's population.
