> **Superseded record (2 October 2026 revision).** This visual QA applies to the earlier build. Figures 1 and 4–6, the Source Data workbook and the DOCX were regenerated; current render hashes and the visual check are in `../visual_validation.json`.

# DOCX visual QA: pages 1–7

Inspected full-resolution images `page-1.png` through `page-7.png` in `/private/tmp/galaxy-original-layout-render` from the twenty-page manuscript render.

All seven pages pass visual layout review: no blank pages, isolated headings, clipping, overlapping line numbers, broken glyphs or duplicate footer numbering. Body paragraphs continue normally across page breaks. Page 2's second Results heading retains three lines of its following paragraph. Page 1's yellow author placeholder is complete and readable. The title, abstracts, section headings and page 7 figure legends remain clearly differentiated.

One editorial correction was reported from page 3 lines 99–100: the comma in “Sol on CompBioBench, Higher all-three-correct rates...” should be a period. This is a punctuation repair rather than a layout issue; the affected page should be re-rendered after the correction.

Also rechecked the final Fig. 2 preview and `F2_sensitivity` workbook preview: both previous clipping problems are resolved. The figure's sensitivity labels wrap naturally; the workbook population identifiers retain every character across wrapped lines.

Final follow-up: the punctuation repair is complete. The root reviewer inspected updated pages1,3and11; other17page PNGs are byte-identical to the reviewed render. Exact page/source hashes appear in visual_validation.json.
