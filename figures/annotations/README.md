# AI-assisted annotations (2026-10-06)

Three coding tasks run by independent AI coders (Claude, one coder per batch of 9–75 items). Each coder saw only its codebook and its assigned items, and never saw any earlier label, grade or key. `build_samples.py` draws the stratified samples (seed 20261002) and regenerates the condensed transcripts into `./transcripts/`. The transcripts are not kept here because they contain the agents' full outputs, including CompBioBench answers.

| Task | Codebook | Sample (`*_key.csv`) | Blinding | Coded output (`coded/`) |
|---|---|---|---|---|
| D: verification steps | `CODEBOOK_D_verification.md` | 80 runs: 10 per benchmark (BixBench-Verified-50, CompBioBench) × condition × outcome, at most one run per task per stratum | Coder blind to the grade; the condition is visible in the transcript | `D_batch1–8.json` |
| A2: second rater for the BixBench-Verified-50 failure-cause audit | `CODEBOOK_A2_causes.md` | 45 incorrect runs, stratified by the original audit's cause group and condition | Coder blind to the original audit; sees the reference answer | `A2_batch1–5.json` |
| A1: second rater for the failure-class rules | `CODEBOOK_A1_requests.md` | 150 failed Galaxy requests, 10 per class (`A1_items.json`) | Coder blind to the rule-based class | `A1_part1–2.json` |

Notes:
- These are AI-assisted second ratings, not human validation. Human blinded validation of a sample remains to be done.
- In the first A2 attempt, 24 of 45 transcripts lacked the reference answer, because the run summaries store none for those tasks. Those codes were discarded, the references were added from `ground_truth/BixBench`, and all 45 items were coded again.
- One verification coder recorded an agent's download of the public BixBench answer file as a plausibility check (D043). `make_ed_validation.py` drops that check. Benchmark-answer access is analysed separately (`make_answer_exposure.py`).
