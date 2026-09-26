# Galaxy improvement report: why agents failed on BixBench-50, CompBioBench and IWC

Retrospective trace audit, 25 September 2026. Scope: every archived run in `BixBench_50/` (there is no `./BixBench` directory), `CompBio/` and `IWC/`: 4,240 runs, 4,228 with a primary agent trace. No agent code was re-run and no Galaxy job was submitted. This version supersedes the earlier report of 24 September, which is preserved unchanged at [analysis_reports/galaxy_improvement_20260924/Galaxy_improvement_report.v1_prior_audit.md](analysis_reports/galaxy_improvement_20260924/Galaxy_improvement_report.v1_prior_audit.md). That audit's per-failure dossiers and independent checks remain valid evidence and are cited here where used.

## Executive summary

**Most rejected Galaxy answers were not caused by Galaxy.** Of the 111 rejected BixBench Galaxy runs, 58 have a task-specification or reference problem as their primary cause, 15 were rejected by the evaluator despite a correct answer, 26 are statistical/reasoning errors, 3 are domain-knowledge errors, 5 wrote no answer, and **4 have a platform defect as the primary cause**. Platform problems are a contributing (secondary) cause in 18 more, so Galaxy is implicated in **22 of 111 (20%)** failures. The code track fails for similar reasons (135 rejections; no Galaxy involvement, by construction).

**Four tasks account for over half of all Galaxy rejections.** bix-53-q2, bix-61-q5, bix-54-q7 and bix-26-q5 fail in 116 of 120 runs across both tracks and all five model configurations (58 of 111 Galaxy rejections). One is an evaluator false negative: "increase" was rejected against "increases the number of DE genes" 30/30 times. The other three have references that depend on choices the question does not state. The only accepted runs on bix-54-q7 and bix-26-q5 retrieved the benchmark's own source files from Hugging Face or GitHub.

**Where Galaxy did cause failures, the mechanisms are specific and fixable:**

1. **Silent parameter substitution.** Galaxy falls back to defaults when submitted keys do not bind to the conditional/repeat structure. In **4,352 tool-run calls (30% of BixBench, 16% of CompBio, 29% of IWC)** the harness detected that Galaxy would substitute or drop requested values: `max`→`count`, `treeness`→`total_tree_length`, genome `hg38`→`apiMel4` (honeybee), `paired`→`single`. Of these, 916 jobs actually ran with the wrong parameters. bix-35-q1 failed exactly this way.
2. **Wrapper output semantics.** On bix-28-q3 the PhyKIT metrics wrapper's non-verbose `long_branch_score` returned 146.3023. That is the *sample variance* of the four per-taxon scores, not their median (−30.455).
3. **Hidden software versions.** On bix-45-q1 (0/15 Galaxy accepted), the reference encodes an older PhyKIT RCV definition. The wrapper's underlying version is not surfaced, and there is no ordinary way to pin one.
4. **UDT unreliability.** Only 51% of user-defined-tool calls returned `ok`. 1,298 UDT jobs failed before execution with **no diagnostic text**. On bix-31-q2 the UDT jobs never dispatched, and the agent fell back to R DESeq2 instead of the pydeseq2 the task named.

**The dominant cost of Galaxy is overhead, not wrong answers.**
- **Failed calls:** 7,389 of 69,812 Galaxy MCP calls failed (10.6%), about half before any job existed.
- **Schema errors:** "History unavailable" alone accounts for 1,340 failed calls; the tool-schema call requires a history context the MCP tool treats as optional.
- **Discovery:** tool search and inspection are 40–51% of MCP calls and 42–70% of the text those calls return.
- **Workarounds:** every Codex BixBench Galaxy run fell back to BioBlend/raw REST from the shell, for history copy (537/600) and downloads (580/600).
- **Tokens:** median input use is 4.7× the code track on BixBench and 4.4× on CompBio.
- **Friction and outcome:** friction is only weakly associated with rejection (median 2 vs 1 failed calls per run).

**Successful runs differed at the decision point, not in tool count.** They:
- tied conventions to provenance (the PhyKIT version to the input archive's date; sample IDs to the collection manifest; essentiality as −Chronos);
- checked scientific invariants (mitochondrial identity; a median lies within its data);
- treated identical outputs from two "different" metrics as a red flag rather than as confirmation.

**Top Galaxy changes**, detailed in §7:
- make tool-state validation strict and return an effective-parameter diff;
- make conditional branch selection unambiguous;
- serve tool schemas without a history;
- always return a diagnostic for failed jobs, including pre-execution failures;
- give UDTs a dry-run/lint step and a container dependency check;
- surface underlying software versions and output semantics;
- add history-copy and download operations to the agent API;
- run deployment smoke tests (two wrappers on usegalaxy.org failed because their own scripts were missing).

## 1. Scope, data and method

| Benchmark | Tasks | Configurations | Runs (Galaxy / code) | Endpoint | Failure definition used here |
|---|---:|---|---:|---|---|
| BixBench-50 | 50 | GPT-5.5, GPT-5.6 Sol, GPT-5.6 Luna, DeepSeek V4 Pro via Codex, DeepSeek V4 Pro via Claude Code (superseded) | 1,500 (750 / 750) | Binary acceptance; reference value stored in each `evaluation.json` | `score == 0` (246 runs) |
| CompBioBench | 100 | GPT-5.5, Sol, Luna, DeepSeek V4 Pro 0813 (Codex); GPT-6 Astra code-only | 2,500 (1,200 / 1,300) | **No item-level grades or references archived**; 22 aggregate vector totals | Deviation from a ≥20/25 cross-run consensus (probable failure; see below) |
| IWC | 10 | GPT-5.5, Sol, Luna, DeepSeek V4 Pro (Codex) | 240 (120 / 120) | Continuous 0–1 agreement | Score < 0.5 (8 runs), plus sub-0.95 clusters |

**Trace extraction.** Every primary event log was parsed: Codex `codex_events.jsonl[.gz]`, and Claude Code `claude_events.jsonl.gz` for the superseded DeepSeek harness. For each Galaxy MCP call, the structured `status`, `error`, `failure_summary`, validation `errors` and `parameter_provenance` were recovered. Each failed call was then classified as either:
- **A1–A8**, pre-submission interface failures (no job created); or
- **B1–B5**, failures of a created job.

Shell commands in Galaxy runs were scanned for BioBlend and raw-REST use. Rejected runs were read call by call and contrasted with accepted runs of the same task, using the same model where one succeeded.

**Root-cause categories:**
- `PLATFORM`: Galaxy, MCP or tooling (for code runs: local environment tooling).
- `KNOWLEDGE`: a domain gap.
- `RIGOR`: weak evidence accepted, thresholds or invariants ignored, a wrong denominator.
- `SPEC`: the task is under-specified, or the reference depends on an unstated choice.
- `EVALUATOR`: the grader rejected an equivalent answer, or score records conflict.
- `CONTRACT`: an output-format or identifier violation.
- `HARNESS`: no answer was written.

**CompBio correctness proxy.** With no item grades, the modal answer across 25 runs per task was tested against the 22 reported vector totals. It reproduces them with a mean absolute error of 2.6/100 (bias +2.0). On the 82 tasks with ≥20/25 agreement a deviating answer is therefore a *probable* failure. The 18 contested tasks need independent checks. A search that re-fits individual answers to the totals over-fits (22 constraints, 100 unknowns) and was not used.

**Limitations.**
- Token totals are per run and cannot be attributed to individual calls, so returned-character volume is used as a proxy for context spent.
- Galaxy histories were snapshotted after the runs.
- Replicate labels are not matched seeds.
- The parameter-mismatch and bypass statistics cover the Codex-harness traces (1,908 Galaxy runs); the Claude Code harness renders results differently.
- Adjudications marked `unresolved` or `mixed` (32 of 246) are best-supported explanations, not proofs.

Scripts and derived tables: [analysis_reports/galaxy_improvement_20260924/v2_trace_friction/](analysis_reports/galaxy_improvement_20260924/v2_trace_friction/README.md).

## 2. Which runs failed

### 2.1 BixBench-50: rejected runs per replicate (each cell out of 50 tasks)

| Configuration | Galaxy r1 | r2 | r3 | **Galaxy** | Code r1 | r2 | r3 | **Code** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GPT-5.5 | 6 | 5 | 5 | **16/150** | 6 | 6 | 7 | **19/150** |
| GPT-5.6 Sol | 6 | 5 | 6 | **17/150** | 7 | 6 | 7 | **20/150** |
| GPT-5.6 Luna | 5 | 8 | 8 | **21/150** | 7 | 5 | 9 | **21/150** |
| DeepSeek V4 Pro (Codex) | 9 | 10 | 8 | **27/150** | 10 | 10 | 9 | **29/150** |
| DeepSeek V4 Pro (Claude Code, superseded) | 10 | 12 | 8 | **30/150** | 15 | 16 | 15 | **46/150** |
| **All** | | | | **111/750 (14.8%)** | | | | **135/750 (18.0%)** |

The failures are concentrated:

| Pattern | Tasks | Galaxy rejections | Code rejections |
|---|---|---:|---:|
| Fail in both tracks in nearly every run | bix-53-q2 (30/30), bix-61-q5 (30/30), bix-54-q7 (28/30), bix-26-q5 (28/30) | 58 | 58 |
| Fail in every Galaxy run, often solved in code | bix-45-q1 (Galaxy 0/15 accepted, code 8/15) | 15 | 7 |
| Solved far more often in Galaxy | bix-30-q3 (15/15 vs 6/15), bix-43-q2 (11/15 vs 2/15) | 4 | 22 |
| Scattered failures on tasks most runs solved (mostly DeepSeek) | 26 tasks | 34 | 48 |

Six runs wrote no answer: five Galaxy (four DeepSeek-Codex) and one code. Median input tokens: Galaxy 2.20 M (accepted) vs 1.95 M (rejected); code 0.46 M vs 0.84 M.

### 2.2 IWC: runs scoring below 0.5

| Run | Score | What happened |
|---|---:|---|
| Galaxy GPT-5.5 r1, mitogenome | 0.000 | Wrong contig submitted (§4.6) |
| Code GPT-5.5 r1, mitogenome | 0.000 | Wrong contig submitted despite the agent's own noted evidence gap |
| Code DeepSeek r2, mitogenome | 0.000 | Wrong contig, validated only against itself |
| Code GPT-5.5 r1 and r3, amplicon | 0.000 | Sample IDs lowercased (contract) |
| Code DeepSeek r3, pseudobulk | 0.000 | Incorrect Benjamini–Hochberg (BH) implementation |
| Galaxy Luna r1 and r3, host removal | 0.273 | **Evaluator artifact**: correct BWA-MEM output scored against the Bowtie2 route (§4.6) |

Galaxy therefore has exactly **one** genuine IWC failure, and the same model and replicate also failed in code. Galaxy mean agreement is ≥ 0.99 for Sol and DeepSeek, and 0.937–0.954 for GPT-5.5 and Luna; the latter two means are pulled down by the mitogenome zero and the two host-removal artifacts.

### 2.3 CompBio: deviations from strong consensus (probable failures; 82 tasks)

| Configuration | Galaxy r1 / r2 / r3 | Code r1 / r2 / r3 |
|---|---|---|
| GPT-5.5 | 2 / 0 / 2 | 6 / 1 / 3 |
| GPT-5.6 Sol | 0 / 3 / 2 | 1 / 2 / 0 |
| GPT-5.6 Luna | 5 / 3 / 4 | 5 / 3 / 5 |
| DeepSeek V4 Pro 0813 | 5 / 1 / 6 | 7 / 3 / 4 |
| GPT-6 Astra | n/a | 4 |

In total there are 33 Galaxy and 40 code deviations. The reported aggregate scores (Galaxy 83–93/100, code 80–95/100) are consistent with this. Galaxy-specific deviations cluster by model on a handful of tasks (§4.7).

## 3. Root causes at a glance

Primary / secondary counts over all 246 rejected BixBench runs and the 8 IWC runs below 0.5:

| Population | PLATFORM | KNOWLEDGE | RIGOR | SPEC | EVALUATOR | CONTRACT | HARNESS |
|---|---:|---:|---:|---:|---:|---:|---:|
| BixBench Galaxy (111) | **4** / 18 | 3 / 3 | 26 / 52 | **58** / 12 | 15 / 0 | 0 / 0 | 5 / 0 |
| BixBench code (135) | 0 / 0 | 12 / 6 | 39 / 63 | **64** / 26 | 18 / 1 | 1 / 0 | 1 / 0 |
| IWC Galaxy (3) | 0 / 1 | 1 / 0 | 0 / 0 | 0 / 2 | 2 / 0 | 0 / 0 | 0 / 0 |
| IWC code (5) | 0 / 2ᵃ | 1 / 0 | 2 / 1 | 0 / 0 | 0 / 0 | 2 / 0 | 0 / 0 |

ᵃ Local tooling friction (R setup, assembler dependencies), not Galaxy.

Confidence across the 246 BixBench adjudications: 159 high, 55 moderate, 20 mixed, 12 unresolved. The full ledger is in Appendix A.

**Interpretation.**
- **What the Galaxy failures mostly are:** failures of the benchmark (task specification or grading) or of the model's reasoning, which occur identically in code.
- **Where Galaxy is decisive:** a small number of failures where the platform silently did something other than what was asked (parameter substitution, wrapper output semantics), hid information needed to match the reference (software version), or failed without telling the agent why (UDT dispatch, missing diagnostics).
- **Galaxy as the everyday tax:** 7,389 failed calls and roughly 4–5× the input tokens of code, even when the answer is right.

## 4. Failure analyses

### 4.1 Four tasks that fail in both tracks

**bix-53-q2: evaluator false negative (30/30 rejected).** The question asks whether excluding the third replicates changes the number of DE genes, and in which direction. The expected answer is "increases the number of differentially expressed genes". All 30 runs, in both tracks and all five configurations, answered "increase". Several added counts, e.g. `1479 1931 increase` (Galaxy GPT-5.5, Sol, Luna) or `increase: 1575 to 1975` (DeepSeek). The verifier is labelled `llm_verifier_auto_code` but applied token matching; it recorded `observed_normalized: "1479 1931 increase"` and rejected it. The direction is semantically identical. The exact counts were not independently recomputed. **Primary: EVALUATOR.**

**bix-61-q5: reference built on an unstated callset (30/30 answered 2.56; reference 2.68).** The supplied input includes `SRR35233585_raw_variants.vcf` (GATK HaplotypeCaller output). Every run computed Ts/Tv from it, and `bcftools stats` gives `TSTV 48234 18865 2.56` (open-code Sol r1 L10). Agents explicitly decided against unrequested filtering. For example, Galaxy Luna r1 (L18): "compute Ts/Tv from its called SNV alleles, excluding indels … with no unrequested quality/PASS filter". The VCF header declares a `LowQual` filter, and the file name says "raw", so the reference likely used a filtered callset. No run computed a filtered sensitivity value that could confirm this, and the VCF bytes were not retained for an independent recount. Unanimous convergence across 2 tracks × 5 configurations argues strongly against an agent error. **Primary: SPEC; secondary: RIGOR (no filter-sensitivity check).**

**bix-54-q7: reference depends on an undocumented row filter (28/30 rejected).**
- **The two answer clusters:** 178,984 (full data) and 180,771 (mixture rows only).
- **The accepted value:** 184,371.8, which requires excluding the pure-strain-98 rows while keeping pure strain 287.
- **How the two accepted runs got it:**
  - DeepSeek-Codex Galaxy r1 states at L89: "The original analysis path filters out strain controls `1` and `98`". It learned this after downloading `futurehouse/BixBench/BixBench.jsonl` and the original `CapsuleFolder-…zip` from Hugging Face (L62–L84).
  - DeepSeek-Codex code r2 cloned a GitHub repository and grepped it for `184371`, the reference value itself (L38–L40).

No honest analysis in the archive reached the reference. **Primary: SPEC; secondary: RIGOR (no row-inclusion sensitivity check).** Galaxy-specific friction was not decisive; R was only available through UDTs, which worked here.

**bix-26-q5: enrichment settings unstated (28/30 rejected; reference 3).**
- **Galaxy runs** converged on 2 (13/15), largely via the `kegg_ora` wrapper.
- **Code runs** converged on 1 (clusterProfiler and gseapy variants).
- **What changes the count:** the gene universe, KEGG ID mapping, pathway-size limits, and whether BH covers all tested terms or only those with hits.
- **The two answers of 3:** DeepSeek-Codex Galaxy r3 searched the Hugging Face BixBench dataset and the Future-House/BixBench GitHub repository before answering (L155–L169). The DeepSeek-Claude Code code r3 acceptance is unexplained.
- **The missing Galaxy answer** (DeepSeek-Codex r1) consumed 68.8 M input tokens over 206 shell calls and ended in literature searches.

**Primary: SPEC; secondary: RIGOR.** Galaxy's `kegg_ora` wrapper also had the highest error count in BixBench (62/269 jobs). Of those, 27 were "empty background after pathway intersection" and 19 "mapping table has too few columns", both input-contract errors (prior audit, Table X18).

### 4.2 Galaxy-specific failures (platform primary or decisive)

**bix-45-q1: hidden software version (0/15 Galaxy accepted).**
- **The Galaxy result:** all 15 Galaxy runs used `goeckslab/phykit_metrics/0.2.0+galaxy0` and obtained p = 1.5197572608715265e-56. Current PhyKIT (2.4.1, pip) gives the identical value in code runs.
- **The reference:** 7.6968e-54, which matches PhyKIT 2.0.3's RCV (different gap and ambiguous-residue handling; U = 6115 vs 5483.5).
- **How the successful code runs found it:** they reasoned from provenance. Open-code Sol r1 (L29): *"The archive timestamps predate the current PhyKIT release; the contemporaneous release was PhyKIT 2.0.3. Because RCV's treatment of gaps/ambiguous residues has since changed, I'm reproducing the function from that release rather than silently mixing 2025 inputs with a 2026 implementation."* Luna r3 tried 1.12.6, 2.1.4 and 2.0.3. DeepSeek-Codex code r1 even searched the web for the Galaxy wrapper's PhyKIT version.
- **What the Galaxy runs could not see:** `search_galaxy_tools` and `inspect_galaxy_tool` never report a wrapper's underlying package version; one agent had to read the tool XML for a *different* PhyKIT wrapper to find `<requirement version="1.11.7">`. Pinning PhyKIT 2.0.3 required a UDT, which the "prefer ordinary tools" policy discourages. The Galaxy policy also forbids the local side-by-side version computation that the code agents used as their diagnostic.
- **Scientific status:** the Galaxy answer is the correct output of current PhyKIT.

**Primary: SPEC (reference tied to an unstated version); secondary: PLATFORM (version opacity, no ordinary pinning).**

**bix-28-q3: wrapper returned variance as the metric (Galaxy Sol r1).**
1. The verbose run (L42–L43) returned four per-taxon long-branch scores: −29.4826, −32.1541, −31.4275, −6.9357 (median −30.45505).
2. To "keep even the requested aggregation inside Galaxy/PhyKIT", the agent reran with `"verbose": false` (L47). The wrapper returned a single row labelled `long_branch_score` with value **146.3023** (L48).
3. That value is the sample variance of the four scores (recomputed: 146.3022 from the rounded values). PhyKIT's non-verbose output is a block of summary statistics, and the wrapper evidently kept the last one.
4. The agent submitted 146.3023 even though a median cannot lie outside the range of its own four values.

The other 29 runs aggregated the verbose output themselves and were accepted. **Primary: PLATFORM (wrapper output contract); secondary: RIGOR.**

**bix-35-q1: conditional binding silently selected the default metric (Galaxy DeepSeek-Claude Code r1).**
1. **First submission (L3091):** flat keys `{"operation|selector": "evolutionary_rate", …}` returned `status=parameter_mismatch`. Galaxy had run the default `total_tree_length`, and the agent noticed (L3283: "The tool ran but with the wrong metric").
2. **Retry (L3914):** `{"operation": {"__current_case__": 0, …}}`, on the assumption that case 0 was `evolutionary_rate` because it is listed first among the select options. Galaxy's case index follows the conditional's `<when>` order, so it ran `total_tree_length` again. With no explicit non-dataset values to compare, the harness's mismatch guard reported `ok` (`checked_parameter_count: 0`).
3. **Acceptance:** the agent then downloaded both outputs (L6618: "Total tree length output: 0.1884 … Evolutionary rate output: 0.1884") and concluded that "PhyKIT's evolutionary_rate function returns 0.1884 … (which matches the total tree length)".

The accepted value is 0.0471 = tree length ÷ 4 tips. **Primary: PLATFORM (silent default and ambiguous branch index); secondary: RIGOR (identical outputs from two metrics accepted as confirmation).**

**bix-31-q2: UDT dispatch failure forced a method substitution (Galaxy DeepSeek-Codex r2, r3).** The task names *pydeseq2 with default shrinkage*, which has no ordinary Galaxy wrapper.
1. DeepSeek-Codex r2's UDT jobs were created but never ran. L131: "`handler`/`exit_code` as null and outputs empty, indicating the API-created UDT job was never actually dispatched on usegalaxy.org".
2. The agent tried the Galaxy CLI, then embedding the UDT in a workflow (L175), then a minimal UDT without an input `format` (L286).
3. It then settled on "the ordinary DESeq2 wrapper … with apeglm shrinkage" (L320), which is R DESeq2, a different estimator. It returned −0.0811 against the pydeseq2 reference of about −0.060; r3 returned −0.0828.

Every accepted Galaxy run used pydeseq2 through a working UDT. **Primary: PLATFORM; secondary: RIGOR (accepted a named-method substitution).**

**bix-16-q1 COX17 (Galaxy DeepSeek-Codex r1): missing dependency, then an unvalidated reimplementation.** The agent correctly transformed Chronos gene effect to essentiality (−effect). Its UDT container lacked SciPy (L115), so it hand-wrote a rank-based correlation. The result was implausible (top ρ = −0.238, whereas the true strongest is about −0.52) and was accepted without spot-checking a single gene. **Primary: RIGOR; secondary: PLATFORM.**

### 4.3 Where Galaxy "won", and why

**bix-30-q3 (Galaxy 15/15, code 6/15): the Galaxy advantage was a default, not better reasoning.**
- **The failing code runs** reproduced the *published* analysis: Student t-test, the paper's exclusion of P_3 and C_18, and mean-Ct normalization. That makes hsa-miR-21 Bonferroni-significant (p = 1.95e-4, adjusted 0.034), giving 1:0. Their own sensitivity tables show that Welch gives 0:0 (open-code Sol r1 L27–L31).
- **Galaxy's ordinary route was broken.** The W4M `Univariate` wrapper failed on usegalaxy.org because its own script was missing (`cannot open file '/jetstream2/scratch/main/jobs/78851853/tool_files/univariate_script.R': No such file or directory`, Galaxy Sol r1 L88 and L91). The spreadsheet converter also returned an empty collection for the legacy `.xls` input (L55).
- **The Galaxy fallback:** the agent wrote a UDT using R's `t.test`, which defaults to Welch, on all 20 unnormalized samples, and got 0:0.

The reference matches R defaults. **Code failures: SPEC.**

**bix-43-q2 (Galaxy 11/15, code 2/15).**
- **Values:** Galaxy runs mostly returned 5.8124 (tolerance 5.781–5.839). Code runs mostly returned 5.8403 or 5.8460, just outside, while 5.8310 passed in the tolerance mode.
- **Grader inconsistency:** DeepSeek-Codex code r1–r3 all returned exactly 5.831005059276599 and were rejected by a `str_verifier_rounded_numeric` mode, whereas Luna and Sol runs with the same value were accepted by `str_verifier_auto_numeric` (EVALUATOR).
- **Unexplained difference:** the DEG-set difference between 5.812 and 5.840 (pre-filter semantics, contrast set, pydeseq2 version) was not isolated.

**IWC code zeros.**
- **Casing:** the amplicon casing failures could not occur through Galaxy collections, whose element identifiers carry the logical sample names. The successful code run (GPT-5.5 r2, L23) read `identifier: hFMT_cecal_1296_1` from the collection manifest, while r1 and r3 used lowercased directory slugs.
- **BH:** the pseudobulk BH failure (DeepSeek code r3, L60) is a hand-written `np.maximum.accumulate` where BH needs a reverse cumulative minimum. Galaxy wrappers return library-computed adjusted p-values.

These are real structural benefits of Galaxy.

**bix-16-q1 (Galaxy Sol accepted).** The featurewise-correlation wrapper exposes "negate one matrix" as an explicit option, and the agent used it to express essentiality as −effect (L29). The eight CCND1 answers in both tracks correlated against raw gene effect. For example, open-code DeepSeek-Codex r1 L35 gives CCND1 −0.629, while −effect gives CDKN1A −0.523 (DeepSeek-Codex r3 L36). The bundled `crispr-dependency-correlation` skill states the required sign transform. **KNOWLEDGE** in both tracks.

### 4.4 Scattered failures

The 82 scattered rejections (34 Galaxy, 48 code) are overwhelmingly reasoning failures. Most are by DeepSeek. Representative decision points (full list in Appendix A):

| Pattern | Examples | Category |
|---|---|---|
| Wrong statistical population | bix-12-q4 Luna code r1 kept only alignments with exactly four sequences (22/241, 211/255) and "validated" U by recomputing it on the same restricted set; bix-45-q1 DeepSeek-Claude Code code restricted to shared orthologs; bix-31-q2 DeepSeek-Claude Code code r3 subsampled for memory | RIGOR |
| Wrong biological definition | Gap characters counted as states for parsimony-informative sites (bix-12-q2/q5/q6); raw Chronos vs essentiality (bix-16-q1); `.mldist` ML distance instead of patristic distance (bix-34-q5) | KNOWLEDGE |
| Invariant not checked | `sort -k3,3n` on scientific notation picked ρ = −9.4e-5 as "strongest" (bix-16-q1 Luna Galaxy r2, L58); 19,160 vs 19,159 rows, and the retained complement 539 (bix-52-q7 Galaxy Sol/Luna) | RIGOR |
| Wrong order of operations | Enrichment of the intersected DE genes instead of intersecting pathways from three ORAs (bix-32-q2 DeepSeek-Claude Code code r1) | RIGOR |
| Unit or format | `10.0%` for a requested fraction 0.1 (bix-53-q5) | CONTRACT |

Galaxy-specific friction contributed materially only in the cases in §4.2.

### 4.5 Missing answers and benchmark-source retrieval

The six missing answers are not Galaxy-friction failures:
- **Four DeepSeek-Codex Galaxy runs** ended their turn mid-investigation after only 2–9 Galaxy calls with **zero** failed calls:
  - bix-26-q5 r1 burned 68.8 M tokens;
  - bix-46-q4 r2 was searching for the literal value "−4.09911354408172";
  - bix-43-q2 r3 had opened the BixBench dataset viewer on Hugging Face;
  - bix-27-q5 r1 was reading legacy Galaxy PCA wrapper source to learn its output semantics. This is the one case with a platform flavour: the wrapper's output meaning was not documented in the tool schema.
- **Galaxy DeepSeek-Claude Code bix-34-q5 r3** ran out mid-UDT after its PhyKIT output parser returned 0/96 trees.
- **Code DeepSeek-Claude Code bix-52-q7 r3** stopped after resolving a filename mismatch.

**Benchmark integrity.**
- **Scale:** 38 BixBench runs issued web or shell calls that referenced the benchmark's own source data (`futurehouse/BixBench`, `BixBench.jsonl`, `CapsuleFolder-*.zip`). 37 were DeepSeek-Codex (22 Galaxy, 15 code), and 29 of the 38 were accepted.
- **Proven effect on outcome:** a lookup does not prove the answer was copied, but in bix-54-q7 and bix-26-q5 the only accepted runs are among these. Code DeepSeek-Codex r2 on bix-54-q7 also grepped a repository for the reference value.
- **Other answer-seeking:** a Luna code run on CompBio searched for "characterize.response.q1.txt answer".

DeepSeek-Codex acceptances should be treated as contamination-risk until the harness blocks these domains.

### 4.6 IWC

**Mitogenome, Galaxy GPT-5.5 r1 (score 0).** The following facts are from the prior audit's independent check, which downloaded the public *Agrius convolvuli* mitogenome OZ203683.1.
- **The selection:** the agent picked circular contig `ptg000099c` (14,449 bp, depth ~206 vs nuclear ~15–16) at L70–82 on length, depth and circularity alone.
- **The validation:** it checked gzip integrity, record count and alphabet (L120/L127), but no gene content or identity.
- **The outcome:** the submitted sequence shares zero canonical 31-mers with the reference; the other 21 candidates score F1 0.94–1.00.

The accepted Galaxy runs added identity evidence:
- GPT-5.5 r2 used MitoHiFi with genetic code 5, recovering 37 annotated genes and a 15,449-bp circular sequence.
- Sol r1 used mitochondrial-read selection plus Flye with origin-spanning alignment.

Platform friction (SeqKit grep rejecting `ptg000099c` with "Pattern must not end with backslash") occurred *after* the wrong choice. **Primary: KNOWLEDGE (identity by length/depth); secondary: PLATFORM.** The two code zeros are, respectively, a run that recognised its candidate lacked support outside the anchor and finalized it anyway (RIGOR), and seed-dependent polishing validated by self-alignment (KNOWLEDGE).

**Host removal, Galaxy Luna r1/r3 (saved 0.273; run record 0.9999/1.0).**
- **Luna r1's output:** its method file declares BWA-MEM, and its output retains 20,899 read pairs.
- **How it was scored:** `route: null`, against the Bowtie2 reference, which retains 72,867 pairs.
- **The matching reference:** the BWA route, as recorded on Sol r1's evaluator, retains 20,896 pairs. Luna matches 20,895 of them.

This is a route-registration artifact. The 3.5-fold difference between the BWA and Bowtie2 references is itself a specification issue: the answer depends on the aligner. **Primary: EVALUATOR.**

**Sub-0.95 clusters** are route or parameter choices rather than failures:
- amplicon Galaxy GPT-5.5 r1/r2 used the QIIME2 DADA2 route (0.918 vs 0.956);
- peptide verification lost precision (0.87–0.91) through extra peptide–accession pairs.

Both tracks show both patterns.

### 4.7 CompBio: Galaxy-specific deviations by model

Agreement with the consensus answer, per replicate (✓/✗):

| Task (consensus) | GPT-5.5 G / C | Sol G / C | Luna G / C | DeepSeek G / C | Astra |
|---|---|---|---|---|---|
| characterize-response (c;v) | ✓✓✓ / ✓✓✓ | ✓✓✓ / ✓✓✓ | **✗✗✗ / ✓✓✓** | ✗✗✗ / ✗✗✗ | c;v |
| atac-doublet | ✓✓✓ / ✓✓✓ | ✓✗✓ / ✓✓✓ | **✗✓✗ / ✓✓✓** | ✓✓✓ / ✓✓✗ | ✓ |
| contaminated-rna-q1 (hydra) | ✓✓✗ / ✓✓✓ | ✓✓✓ / ✓✓✓ | **✗✗✓ / ✓✓✓** | ✓✓✓ / ✗✓✓ | ✓ |
| histone-chip (H3K9me3) | ✓✓✓ / ✓✓✓ | ✓✓✓ / ✓✓✓ | ✓✓✓ / ✓✓✓ | **✗✓✗ / ✓✓✓** | ✓ |
| finding-geo (GSE114176) | ✗✓✓ / ✓✓✗ | ✓✓✓ / ✓✓✓ | ✓✓✓ / ✓✓✓ | **✗✗✗ / ✓✗✓** | ✓ |
| tissue-fibroblast (Omentum,Bone; contested) | ✓✓✗ / ✓✓✓ | ✗✓✓ / ✓✓✓ | ✗✗✗ / ✓✗✗ | ✓✓✗ / ✓✓✓ | **Lung,Bone** |

**characterize-response, Luna: Galaxy's evidence rule met a reference-coverage gap.**
- **The task:** identify which condition and cell type best explain a 112-gene mouse response list.
- **Luna in code (c;v):** read the list, ran three web searches and answered "c;v", i.e. LIF-stimulated dendritic cells, which fits the cytokine-response ("immune dictionary") literature.
- **Luna in Galaxy:** followed the policy that "all evidence-bearing scientific computation must run in Galaxy" and ran enrichment against Galaxy's generic gene-set libraries (L44–L200). It took "LPS-specific macrophage signatures among the significant terms" as decisive and answered a;i (LPS, monocytes) in all three replicates.

The failure is primarily KNOWLEDGE, with a PLATFORM contribution: Galaxy lacks that specialised reference, and the prompt directs agents to trust Galaxy-computable proxies over literature.

**histone-chip, DeepSeek Galaxy r1/r3.** The agent committed to a narrow-peak route: MACS2 peak calling followed by ChIPseeker annotation. It shortlisted "H3K4me1 or H3K27ac" (L294) and never considered broad heterochromatin signatures, which H3K9me3 needs. The run absorbed 26 failed calls over 146 MCP calls and 19.3 M tokens. **KNOWLEDGE; secondary PLATFORM.**

**cryptic-exon, DeepSeek Galaxy r2/r3 (from the prior audit's independent check).**
- **r2** selected CD74 by name-matching gene overlaps, although its own STAR output contained the GNG10 junction pair (43 and 36 unique reads bracketing a 53-bp exon on chr9).
- **r3** selected UBC from junctions with zero unique-read support.

**RIGOR/KNOWLEDGE.** The Galaxy run that succeeded explicitly constructed the "two novel junctions splitting a known intron" predicate.

**Contested tasks.** tissue-fibroblast (16 vs 8 plus GPT-6 Astra, which scored 93/100 in aggregate), odd-one-out (11/9/3/2), ml-model-track-overlap (7/6/5/5), reverse-search-gwas-q1 (6/4/…) and encode-atac-pipeline (7/4/…) cannot be adjudicated without references. They should not be counted as failures of either track.

## 5. What successful runs did differently

1. **They tied conventions to provenance.** Examples: the PhyKIT release matched to the input archive's timestamps (bix-45-q1); sample IDs read from the collection manifest rather than directory names (IWC amplicon); essentiality defined as −Chronos, as the bundled skill instructs (bix-16-q1).
2. **They checked the scientific predicate, not just the file.** Accepted mitogenome runs checked gene content and identity. The accepted cryptic-exon run built the exon from two junctions. The accepted long-branch runs aggregated per-taxon values they could see.
3. **They treated anomalies as signals.** The failures show what happens otherwise: two metrics that return the same number (bix-35-q1), a "median" outside its data (bix-28-q3), a zero-count filter result (bix-14-q1 Luna Galaxy r2), and an implausibly weak top correlation (bix-16-q1 COX17) were all submitted. Successful runs typically ran a second, independent check.
4. **They used wrappers that expose the convention as a parameter.** Examples are "negate one matrix" in featurewise correlation, and the Welch default in R that happened to match the bix-30-q3 reference. This is a structural advantage Galaxy can extend deliberately (§7).
5. **Caution:** on bix-54-q7 and bix-26-q5 the only "successes" retrieved benchmark source files. That behaviour should be blocked, not emulated.

## 6. Platform friction: what the traces show

### 6.1 Scale

| | BixBench-50 | CompBio | IWC | Total |
|---|---:|---:|---:|---:|
| Galaxy MCP calls | 17,550 | 48,297 | 3,965 | 69,812 |
| Calls returning a failure status | 1,900 (10.8%) | 5,116 (10.6%) | 373 (9.4%) | 7,389 |
| …failed before a job existed (A-codes) | 1,194 | 2,099 | 161 | 3,454 |
| …failed after a job was created (B-codes) | 703 | 2,793 | 181 | 3,677 |
| Tool-run calls where Galaxy would substitute or drop requested parameters | 1,482 / 4,894 (30%) | 2,530 / 16,078 (16%) | 340 / 1,168 (29%) | 4,352 |
| Median Galaxy MCP calls (failed) per run | 16 (1) | 24 (2) | 25.5 (2) | |
| Median input tokens per run, Galaxy vs code | 2.16 M vs 0.53 M | 4.55 M vs 0.82 M | 4.71 M vs 2.02 M | |
| Median within-task Galaxy/code input-token ratio | 4.74 | 4.42 | 1.88 | |

| Code | Failure pattern | BixBench | CompBio | IWC | Total |
|---|---|---:|---:|---:|---:|
| A1 | `inspect_galaxy_tool` → "History unavailable. Please specify a valid history id" | 704 | 588 | 48 | **1,340** |
| A2 | Tool ID not found: guessed IDs (`Sort1`, `Filter`, `cut1`, `grep1`, `__UDT__`), truncated Tool Shed IDs | 53 | 347 | 21 | 421 |
| A3 | Nested conditional/repeat key rejected ("`'0\|filter\|filter_type' has an invalid key structure`", "received conflicting value") | 84 | 122 | 14 | 220 |
| A4 | Parameter value or datatype validation (missing value, option `None`, collection passed to a single-dataset input) | 186 | 567 | 52 | 805 |
| A5 | ID handling ("invalid dataset id", "Wrong id (…) unable to decode", "History is not owned by user") | 114 | 142 | 13 | 269 |
| A6 | UDT representation schema (pydantic union/discriminator errors, id pattern, output lacks `from_work_dir`) | 13 | 124 | 0 | 137 |
| A7 | Upload/datatype registry ("Requested extension 'bedpe' unknown"; also `gct`, `bed.gz`, `gff.gz`, `gzip`, `text`, `pt`) | 3 | 91 | 0 | 94 |
| A8 | Server/transport (HTML error pages, "Uncaught exception in exposed API method", HTTP 429, "Transport closed", timeouts) | 37 | 118 | 13 | 168 |
| B1 | UDT container lacks a dependency ("there is no package called 'DESeq2'", pip externally-managed) | 21 | 58 | 0 | 79 |
| B2 | Job error returned with **no diagnostic text** | 252 | 1,503 | 74 | **1,829** |
| B3 | Tool runtime error with stderr | 411 | 1,036 | 86 | 1,533 |
| B4 | Input format, compression or index | 19 | 178 | 18 | 215 |
| B5 | Memory or resource | 0 | 18 | 3 | 21 |
| Z | Unclassified | 3 | 224 | 31 | 258 |

### 6.2 Mechanisms, with verbatim evidence

**A1, "History unavailable" (1,340 calls; 511 Codex runs).**
- **When it fails:** 87% of these failures (972 of 1,119 in Codex traces) are `inspect_galaxy_tool` calls sent **without** a `history_id`. Of the 12,129 successful inspections, 99.8% include one.
- **The remaining 147** passed a history the user did not own, usually the seed history before copying. Example: bix-35-q1 DeepSeek-Claude Code r1 L442, where the result carried `history_error: "History is not owned by user"` beneath the "History unavailable" message.
- **Mechanism:** Galaxy's tool-form build endpoint needs a history context; the MCP tool treats `history_id` as optional and the error text gives no hint of the cause.
- **Cost:** in 224 runs the call immediately after the first A1 failure was another A1 failure. In 182 BixBench runs agents fetched tool schemas directly through BioBlend (`gi.tools.show_tool(tool_id, io_details=True)`) instead of the MCP tool.

**Silent parameter substitution (4,352 calls).** The harness validated requests (`validate_before_submit`) and compared job parameters with the request (`parameter_provenance`). Galaxy itself accepted payloads whose keys did not bind and filled defaults:
- **3,436 blocked before submission** (`validation_parameter_mismatch`): 1,808 with explicit value substitutions, 1,628 with requested paths missing from the resolved state.
- **916 executed** (`parameter_mismatch`): 277 with substituted values, 639 with dropped paths.

Examples (task, tool: requested → resolved):
- bix-12-q5, datamash_ops: `operations|0|op_name` `max` → `count`
- bix-18-q1, datamash_ops: `operations|0|op_column` `6` → `1`
- bix-11-q1, phykit_metrics: `operation|selector` `treeness` → `total_tree_length`
- bix-24-q2, deseq2: `factorLevel` `DMSO` → `FactorLevel`
- bix-24-q2, gprofiler: `domain_scope` `custom` → `annotated`
- gene-fusion-q1, STAR: `genomeDir` `hg38` → `apiMel4`; `sPaired` `paired` → `single`; `settingsType` `arriba` → `default`

Most affected tools: filter_tabular (692), datamash_ops (501), Add_a_column1 (316), Grouping1 (246), phykit_metrics (224), tp_sort_header_tool (192), deseq2 (171). Calls returning a mismatch consumed about 6.9 h (BixBench), 51 h (CompBio) and 8.3 h (IWC) of wall-clock time. Without the benchmark's guard, each of these would have been a silently wrong analysis.

**A3/A5, payload shape and misleading errors.** bix-11-q1 Galaxy Luna r2 spent 12 unzip submissions binding one conditional, each running about 7 minutes:
1. **L46:** `"input_file": "f9cad7b01a4721355d41e68797c46966"` returned "Parameter 'input_file': **invalid dataset id** 'f9cad7b01a4721355d41e68797c46966'". The ID was valid (listed at L29); the payload needed `{"src":"hda","id":…}`.
2. **L56–L63:** `extract_options|target` (flat), `extract_options: {target: …}` (nested) and dotted `extract_options.target` all returned `parameter_mismatch` or `validation_parameter_mismatch`: the regex was silently ignored.
3. **L75 and L77:** the identical payload `"extract_options": "all_regex"` was sent twice and returned "Invalid value 'all_regex' submitted for conditional parameter 'extract_options'", with no hint of the expected structure.
4. **L86:** the agent submitted `keep_regex: "foo"` purely to test whether the parameter was honoured.

Across the corpus, the 214 "invalid dataset id" errors named 215 IDs: 173 had already appeared in the run as valid datasets, and 42 were history IDs passed as dataset IDs. There were also malformed IDs: `Wrong id ( f9cad7b01a4721351f3211a9b8fc0fa23 )` is 33 characters (bix-18-q1 Luna r2 L69), and a 30-character ID appears at bix-43-q2 Luna r3. Galaxy reports only "unable to decode".

**B2 and UDTs, failing blind.**
- **UDT outcome:** of 4,960 UDT calls, only 2,509 (51%) returned `ok`; 2,011 failed, 133 failed at creation, and 307 had other non-ok statuses.
- **No diagnostic:** 1,298 UDT job failures, plus 80 ordinary-tool failures, occurred in phase `pre_execution_or_command_rendering` with no stderr or job message returned.
- **Blind retries:** after a no-text failure, the agent's next call resubmitted identical inputs 784 times, and 615 of those failed again.
- **Probe tools:** agents built throwaway probe UDTs (`animal-pis-udt-preflight-v1`, `render_probe_v1`, `udt-render-preflight-busco-v1`) to bisect template rendering. There were 1,859 such calls in 517 of the 808 CompBio runs that used UDTs. The bundled `galaxy-udt-authoring` skill had to teach this pattern ("use one only when a cheap probe resolves a concrete uncertainty about the selected container, import, command rendering, binding, or output creation"), because Galaxy offers no dry run.
- **Schema errors** are raw pydantic output, e.g. `"Unable to extract tag using discriminator 'type' in ('body', 'representation', 'outputs', 0)"` (bix-12-q4 DeepSeek-Claude Code r1 L10640).
- **Dependency failures:** `"Error in library(DESeq2) : there is no package called 'DESeq2'"` (bix-49-q4 Sol r2 L61; bix-53-q5 Sol r2 L86), in containers the agent chose without any capability check.

**API coverage gaps drive agents to BioBlend.** In Codex-harness Galaxy runs, agents called BioBlend or raw REST from the shell for:
- **copying the seed history:** 537/600 BixBench runs (policy-mandated, no MCP tool);
- **downloading outputs:** 580/600 BixBench (MCP offers only `peek`), 234/1,188 CompBio, 73/120 IWC;
- **fetching tool schemas:** 182 / 193 / 24;
- **polling jobs:** 92 / 237 / 57, despite prompts forbidding polling;
- **submitting jobs through raw `POST /api/tools`, bypassing the harness's validation entirely:** 22 / 209 / 37.

Overall, 39% of Galaxy-track shell commands in BixBench were Galaxy API calls. One agent called `GET /api/tools`, expected a flat tool list, received 87 top-level panel entries and crashed on an entry whose `name` was `None` (contaminated-rna-q3 DeepSeek r2 L16).

**Discovery burden.**
- **Share of calls:** search and inspection are 44% (BixBench), 40% (CompBio) and 51% (IWC) of MCP calls by median run share.
- **Share of returned text:** 70%, 42% and 70% of characters returned by MCP.
- **Searches per run:** median 4 / 6 / 7, maximum 41 / 129 / 40.
- **Wasted inspection:** about half of all inspected tools were never run (876/1,942, 3,100/6,552 and 418/788).
- **ID guessing:** 421 tool IDs were guessed and not found (`Sort1`, `Filter`, `cut1`, `head`, `sorter`).

**Deployment defects on usegalaxy.org.**
- **Missing wrapper scripts:** 15 jobs across 10 runs failed because the wrapper's own script was absent from the execution node (`univariate_script.R` 13, `transformation_script.R` 2).
- **Silent empty conversion:** the xlsx→tabular converter returned an empty collection for a legacy `.xls` (bix-30-q3 Sol r1 L55).
- **Undispatched UDT jobs:** handler null (bix-31-q2).
- **Rate limiting:** 429 responses were returned as nginx HTML (bix-12-q4 DeepSeek-Codex r1 L75: `429 Too Many Requests`).
- **Diagnostics with no text:** 47/47 fastp error jobs in IWC retained no stderr (prior audit, Table X18).

### 6.3 Does friction cause rejection?

Mostly no, with the exceptions in §4.2. Excluding the four tasks that failed in essentially every run, accepted and rejected BixBench Galaxy runs compare as follows:

| Measure | Accepted | Rejected |
|---|---:|---:|
| Failed MCP calls per run, median (mean) | 1 (2.5) | 2 (2.9) |
| Runs with ≥ 5 failed calls | 18.1% | 24.5% |
| Input tokens per run, median (mean) | 2.2 M (3.9 M) | 2.8 M (9.7 M) |

Within tasks that had both outcomes, rejected runs had more failed calls in 12 tasks and fewer in 8. The friction that changes answers is the kind that does *not* surface as a failed call: silent substitution, wrapper semantics, hidden versions. Visible friction mostly costs time and tokens.

## 7. Recommendations for Galaxy

Priorities reflect demonstrated effect on correctness first, then on cost. "Evidence" cites this archive; "Measure" is how to verify the change on a replay of these tasks.

| # | Change (owner) | Evidence | Measure |
|---|---|---|---|
| 1 | **Strict tool-state validation** (Galaxy server). Reject unknown or unbound keys and invalid select values instead of substituting defaults. Every job-creation response should include an *effective-parameters diff* (requested vs resolved). Apply the typed parameter models to API submissions in strict mode. | 4,352 substitution/drop events; 916 executed silently; bix-35-q1 rejection; `hg38`→`apiMel4` | 0 executed jobs whose resolved state differs from the request without an explicit error |
| 2 | **Unambiguous conditional binding** (server + tool-schema API). The selector *value* should choose the branch. Validate or deprecate `__current_case__` in API payloads. For each tool and branch, publish a JSON Schema and one valid example payload in the 21.01 format. | 220 A3 errors; the 12-attempt unzip case; `__current_case__: 0` selecting the wrong branch in bix-35-q1 | Binding attempts per successful submission ≈ 1 on the replay |
| 3 | **Tool schemas without a history** (server `/api/tools/{id}/build`, MCP). Return the schema with history-dependent options omitted, or default to the user's working history. Replace "History unavailable" with an actionable message. | 1,340 A1 failures in 511+ runs; 182 BioBlend schema bypasses | A1 = 0 |
| 4 | **Always return a diagnostic** (job API). Pre-execution failures (template rendering, container resolution, dependency load, dispatch) should return a structured `{phase, message, excerpt}`. `wait` and `show_job` should include stderr, job messages and exit code. | 1,829 no-text failures; 1,298 UDT pre-execution failures; 784 blind identical resubmissions (615 failed again); 1,859 probe-UDT calls | No-text failure share → 0; probe-UDT calls → 0 |
| 5 | **UDT dry run and lint** (UDT API). Validate the representation with human-readable errors and an example. Render the command against placeholder inputs. Check that the container contains the requested executables and libraries (e.g. `R -e 'library(DESeq2)'`, `python -c 'import scipy'`). Report dispatch health. | 51% UDT `ok` rate; 137 schema errors; 79 missing dependencies; bix-31-q2 undispatched jobs; bix-16-q1 COX17 | UDT first-attempt `ok` rate; 0 undispatched jobs |
| 6 | **Surface software versions and output semantics** (tool metadata, search/inspect results). Show underlying package versions (`<requirements>`) and output column meanings in search and inspect results. Allow selection of pinned versions where several are installed. Add wrapper tests for multi-statistic outputs. | bix-45-q1 (0/15 Galaxy accepted); bix-28-q3 (variance reported as the metric) | Version visible without reading tool XML; wrapper output labelled per statistic |
| 7 | **Close API gaps agents fill with BioBlend** (API/MCP). Add history copy with an ID map (old → new dataset IDs), streamed full-dataset download, and resumable job waits keyed by job ID. | Copy 537/600; download 580/600; raw POST submissions in 268 runs bypassing validation; polling in 386 runs | Share of Galaxy-track shell commands that are Galaxy API calls (currently 26–39%) |
| 8 | **Actionable ID and ownership errors** (server). Examples: "value must be `{src, id}`, got a bare string"; "encoded IDs are 16/32 hex characters; received 33"; "history belongs to another user: copy it first". | 269 A5 errors; "invalid dataset id" for valid IDs | Retries after an A5 error |
| 9 | **Datatype aliases** (datatype registry). Map or suggest `bed.gz`→bed (compressed), `gff.gz`, `gzip`, `text`→txt; add `bedpe` and `gct`, or return a nearest-match suggestion. | 94 A7 upload failures | A7 = 0 |
| 10 | **Compact, ranked discovery** (tool search API/MCP). Return cards of tool, version, operation, input/output datatypes and key parameters, ranked by operation and datatype. Support case-insensitive ID and nearest-name resolution. | 40–51% of MCP calls and 42–70% of returned text; half of inspected tools never run; 421 guessed IDs | Discovery calls and characters per task; tokens per accepted answer |
| 11 | **Deployment smoke tests** (usegalaxy.org operations). Continuously run each installed wrapper's test data. Alert on missing `tool_files` and on empty outputs from converters. | `univariate_script.R`/`transformation_script.R` missing (15 jobs, 10 runs); empty xlsx conversion | 0 "No such file" wrapper failures |
| 12 | **Machine-readable transport errors** (proxy/server). Return JSON errors with `Retry-After` for 429s and HTML-free 4xx/5xx responses. | 168 A8 errors including nginx HTML pages | Parseable error share = 100% |
| 13 | **Reference-signature coverage** (data managers). Curate cytokine and perturbation response signatures for the enrichment tools. More generally, document which reference resources Galaxy lacks, so that an agent following a "compute in Galaxy" policy knows when a Galaxy-computable proxy is weak. | characterize-response: Luna Galaxy 0/3 vs code 3/3 | Replay agreement on signature-identification tasks |

**For the agent-facing MCP layer specifically:**
- default `history_id` to the working history;
- keep the requested-vs-resolved guard, but also compare when only `__current_case__` is sent (bix-35-q1 slipped through with `checked_parameter_count: 0`);
- flag *identical outputs from different parameterisations* as a probable binding error;
- expose job stderr in every blocking result.

## 8. Recommendations for the benchmark, evaluator and agent harness

These do not change Galaxy but are needed before track comparisons are meaningful:

- **Grading.** Fix semantic normalization (bix-53-q2: 30 false rejections; bix-53-q5: percent vs fraction). Use one numeric verifier mode per task: 5.831005059276599 was accepted and rejected in different runs of bix-43-q2. Register all valid routes for IWC host removal.
- **Specification.**
  - State the software version or accept version-equivalent answers (bix-45-q1).
  - State the callset filter (bix-61-q5), the row-inclusion rule (bix-54-q7), the enrichment universe and BH family (bix-26-q5), and the test and normalization (bix-30-q3).
  - Otherwise accept the defensible alternatives. Together these account for 116 of 246 BixBench rejections.
- **Integrity.** Block the `futurehouse/BixBench` dataset and repository, and published answer tables, from agent web access. Flag the 38 runs that referenced them (29 accepted) and re-score without them.
- **Item-level grades for CompBio.** Only aggregate totals exist; the consensus proxy here is a stopgap.
- **Harness.** Detect a turn that ends without an answer and without a failure. Enforce a token budget: one run used 68.8 M input tokens and answered nothing.
- **Agent skills.** Add invariant checks before serializing an answer:
  - a median must lie within the range of its data;
  - identical outputs from different metrics indicate a binding error;
  - suspect lexical sorting of scientific notation;
  - zero or empty filter results require justification;
  - reproduce library statistics (BH) rather than hand-coding them;
  - take identifiers from manifests, not paths;
  - match software versions to data provenance.

## Appendix A. Failure ledger: all 246 rejected BixBench runs and the 8 IWC runs below 0.5

Runs are labelled track (G = Galaxy, C = code), configuration and replicate. DS-Codex is DeepSeek V4 Pro via Codex; DS-ClaudeCode is DeepSeek V4 Pro via the superseded Claude Code harness. Call-level excerpts for every BixBench rejection are in the prior audit's [failure dossiers](analysis_reports/galaxy_improvement_20260924/failure_dossiers.md). The machine-readable ledger is [ledger.json](analysis_reports/galaxy_improvement_20260924/v2_trace_friction/ledger.json).

| Task | Runs | Answer(s) | Decision point | Primary / secondary | Confidence |
|---|---|---|---|---|---|
| bix-12-q2 | C DS-ClaudeCode r1, r2 | 5.437352%; 5.44% | Counted gap characters as character states when scoring parsimony-informative sites | KNOWLEDGE / – | high |
| bix-12-q4 | C Luna r1 | 1162.0 | Kept only alignments with exactly four sequences (22/241 animal, 211/255 fungal); re-derived U on the same restricted set and treated agreement as validation | RIGOR / – | high |
| bix-12-q4 | G DS-ClaudeCode r1, r2; C DS-ClaudeCode r1, r2, r3 | 5604; 6160; 6350; 7048.5 | Parsimony-informative percentages computed on a different population or state definition | RIGOR / KNOWLEDGE | moderate |
| bix-12-q5 | C DS-ClaudeCode r1, r3 | 35 | Gap characters counted as states (maximum 35 instead of 29) | KNOWLEDGE / – | high |
| bix-12-q6 | C Luna r1; C DS-ClaudeCode r2, r3 | 55058; 6181.0; 6397 | State definition (gaps) and population differ from the reference counting | KNOWLEDGE / RIGOR | high |
| bix-14-q1 | G Luna r2 | 0 | Filter chain yielded zero qualifying variants; the zero was submitted without question | RIGOR / – | moderate |
| bix-14-q1 | G DS-Codex r1, r2; C DS-Codex r1, r2, r3 | 0.638 | Different carrier-cohort / coding-variant / VAF definition gives 30/47 | RIGOR / SPEC | moderate |
| bix-16-q1 | G Luna r2 | USP54 | `sort -k3,3n` on scientific-notation coefficients selected ρ = −9.4e-5 as "strongest" | RIGOR / – | high |
| bix-16-q1 | C Luna r3; G DS-Codex r3; C DS-Codex r1, r2; G DS-ClaudeCode r2, r3; C DS-ClaudeCode r2, r3 | CCND1 | Correlated expression with raw Chronos gene effect instead of essentiality (−effect) | KNOWLEDGE / RIGOR | high |
| bix-16-q1 | G DS-Codex r1 | COX17 | UDT container lacked SciPy; hand-written rank correlation gave implausible values and was accepted | RIGOR / PLATFORM | high |
| bix-16-q3 | G DS-ClaudeCode r1 | 0 | Threshold/direction choice gave 0 genes | RIGOR / – | unresolved |
| bix-16-q4 | C DS-Codex r2; C DS-ClaudeCode r1 | 6.885%; 0.583% | Different test family or multiple-testing denominator | RIGOR / – | unresolved |
| bix-22-q1 | G DS-ClaudeCode r1 | CD4 | Normalization / cell-type interpretation | RIGOR / – | unresolved |
| bix-24-q2 | C Sol r1; G Luna r3 | upregulation | Direction call from GO enrichment of up- vs down-regulated sets inverted | RIGOR / SPEC | moderate |
| bix-26-q5 | G GPT-5.5 r1–r3; C GPT-5.5 r1–r3; G Sol r1–r3; C Sol r1–r3; G Luna r1–r3; C Luna r1–r3; G DS-Codex r2; C DS-Codex r1–r3; G DS-ClaudeCode r1–r3; C DS-ClaudeCode r1, r2 | 1; 2 | Enrichment universe, KEGG ID mapping and BH family unstated; Galaxy kegg_ora → 2, code clusterProfiler variants → 1; no sensitivity reported | SPEC / RIGOR | moderate |
| bix-26-q5 | G DS-Codex r1 | none | 68.8 M input tokens, 206 shell calls, ended in literature and benchmark-source searches | HARNESS / RIGOR | high |
| bix-27-q5 | C Luna r3; C DS-Codex r2; G DS-ClaudeCode r2; C DS-ClaudeCode r1, r3 | 56.47%; 56.02% | PCA input scope differs (56.47 vs 55.97) | RIGOR / SPEC | unresolved |
| bix-27-q5 | G DS-Codex r1 | none | Turn ended while web-searching legacy Galaxy PCA wrapper source for its output semantics | HARNESS / PLATFORM | high |
| bix-28-q3 | G Sol r1 | 146.3023 | Wrapper's non-verbose long_branch_score returned the sample variance of the four per-taxon scores; range not checked | PLATFORM / RIGOR | high |
| bix-30-q3 | C GPT-5.5 r3; C Sol r1–r3; C Luna r3; C DS-Codex r1–r3; C DS-ClaudeCode r2 | 1:0 | Reproduced the published Student t-test with paper exclusions (miR-21 Bonferroni p_adj = 0.034); reference matches Welch on unnormalized data | SPEC / – | high |
| bix-31-q2 | G DS-Codex r2, r3 | −0.0811; −0.0828 | UDT jobs never dispatched; fell back to R DESeq2 + apeglm instead of the named pydeseq2 | PLATFORM / RIGOR | high |
| bix-31-q2 | C DS-Codex r3; C DS-ClaudeCode r1, r2 | −0.048; −0.072 | Estimator/filter settings differ from pydeseq2 defaults | RIGOR / SPEC | moderate |
| bix-31-q2 | C DS-ClaudeCode r3 | −0.0492 | Subsampled the population to save memory | RIGOR / – | high |
| bix-32-q2 | G DS-Codex r1–r3; C DS-Codex r1–r3; G DS-ClaudeCode r2 | 2 | Different enrichment operation/universe gives 2 same-direction pathways | RIGOR / SPEC | moderate |
| bix-32-q2 | C DS-ClaudeCode r1 | 3 | Enriched the intersection of DE genes instead of intersecting pathways from three ORAs | RIGOR / – | high |
| bix-34-q5 | G DS-ClaudeCode r3 | none | Budget ended mid-UDT after PhyKIT output parsing returned 0/96 trees | HARNESS / PLATFORM | high |
| bix-34-q5 | C DS-ClaudeCode r1–r3 | 1.11; 1.70; 1.83 | Wrong aggregation unit / population / distance metric (.mldist) | RIGOR / KNOWLEDGE | high |
| bix-35-q1 | G DS-ClaudeCode r1 | 0.1884 | Flat keys ran default total_tree_length; `__current_case__: 0` ran it again with the guard blind; identical outputs accepted | PLATFORM / RIGOR | high |
| bix-35-q2 | G DS-ClaudeCode r2; C DS-ClaudeCode r1, r2 | 1820.5; 83.0 | Different gene population for the rank test | RIGOR / – | moderate |
| bix-43-q2 | C GPT-5.5 r1, r3; C Sol r2, r3; C Luna r1, r3; G DS-Codex r2; C DS-ClaudeCode r1 | 5.840–5.859 | Near-miss DEG set (pre-filter, contrast, pydeseq2 version) under 0.5% tolerance | SPEC / RIGOR | mixed |
| bix-43-q2 | C GPT-5.5 r2; G DS-Codex r1; G DS-ClaudeCode r2; C DS-ClaudeCode r2, r3 | 5.62; 5.92; 6.13; 6.16; 7.17 | DEG set / enrichment input far from reference | RIGOR / SPEC | mixed |
| bix-43-q2 | G DS-Codex r3 | none | Turn ended during web searches that included the BixBench dataset viewer | HARNESS / RIGOR | high |
| bix-43-q2 | C DS-Codex r1–r3 | 5.831005 | Rounded-numeric verifier rejected a value accepted in other runs | EVALUATOR / – | high |
| bix-43-q4 | G GPT-5.5 r1; C Sol r3; C DS-Codex r1; G DS-ClaudeCode r2 | 9/49; 8/47 | DEG-set / pathway-denominator difference | RIGOR / SPEC | mixed |
| bix-45-q1 | G all 15 runs | 1.5198e-56 | Reference encodes PhyKIT 2.0.3-era RCV; Galaxy wrapper, like current PhyKIT, gives 1.5198e-56; version hidden, pinning needs a UDT | SPEC / PLATFORM | high |
| bix-45-q1 | C GPT-5.5 r1–r3; C Luna r2; C DS-ClaudeCode r3 | 1.5198e-56 | Used current PhyKIT without checking version sensitivity | SPEC / RIGOR | high |
| bix-45-q1 | C DS-ClaudeCode r1, r2 | 4.0287e-55 | Restricted to orthologs shared by both groups | RIGOR / SPEC | moderate |
| bix-46-q4 | G DS-Codex r2 | none | Turn ended during web search for the published log2FC value | HARNESS / – | high |
| bix-49-q4 | C DS-ClaudeCode r2, r3 | 2100 | Estimator difference (2106 and 2118 both accepted elsewhere) | RIGOR / SPEC | unresolved |
| bix-51-q8 | G DS-ClaudeCode r3 | −0.0271 | Defined the outcome as treatment arm (41 treated vs 39 controls) instead of PR vs SD/PD response | RIGOR / KNOWLEDGE | high |
| bix-52-q2 | G Luna r3 | 9.51e-08 | Join / denominator scope | RIGOR / – | unresolved |
| bix-52-q7 | G Sol r3; G Luna r2 | 19160 | Off-by-one: header row counted | RIGOR / – | high |
| bix-52-q7 | G Luna r3 | 539 | Reported the retained complement instead of removed rows | RIGOR / – | high |
| bix-52-q7 | C DS-ClaudeCode r3 | none | Stopped after resolving an input filename mismatch | HARNESS / – | high |
| bix-53-q2 | all 30 runs | "increase" (± counts) | Equivalent direction rejected against "increases the number of DE genes" | EVALUATOR / – | high |
| bix-53-q5 | C DS-ClaudeCode r3 | 10.0% | Percent given where a fraction (0.1) was requested; same value | CONTRACT / EVALUATOR | high |
| bix-54-q7 | 28 runs: every run except G DS-Codex r1 and C DS-Codex r2 (both accepted) | 178,984; 180,771 | Reference requires excluding pure-strain-98 rows, documented only in the original capsule; accepted runs retrieved benchmark source | SPEC / RIGOR | high |
| bix-55-q1 | C Sol r1; C Luna r3; C DS-ClaudeCode r2 | 100; 64 | BUSCO version / pipeline or completeness-intersection difference | RIGOR / SPEC | mixed |
| bix-61-q2 | G DS-ClaudeCode r1 | 20.5045 | Re-trimmed the raw subsample FASTQs with Trimmomatic instead of mapping the supplied trimmed reads | RIGOR / – | high |
| bix-61-q5 | all 30 runs | 2.56 | Ts/Tv on the supplied raw GATK callset (48,234/18,865); reference presumably filtered; no filter-sensitivity check | SPEC / RIGOR | high |
| wf_003 host removal | G Luna r1, r3 | 0.273 | BWA-MEM output (20,899 retained) scored against the Bowtie2 route (72,867); matches the BWA route (20,896) | EVALUATOR / SPEC | high |
| wf_005 amplicon | C GPT-5.5 r1, r3 | 0.000 | Sample IDs from lowercased directory slugs instead of manifest identifiers | CONTRACT / – (r3: PLATFORMᵃ) | high |
| wf_007 mitogenome | G GPT-5.5 r1 | 0.000 | 14,449-bp high-depth circle chosen by length/depth; no identity check (0 shared 31-mers with OZ203683.1) | KNOWLEDGE / PLATFORM | high |
| wf_007 mitogenome | C GPT-5.5 r1 | 0.000 | Noted that the candidate lacked support outside the anchor, then finalized it | RIGOR / PLATFORMᵃ | high |
| wf_007 mitogenome | C DS-Codex r2 | 0.000 | Seed-dependent polishing and self-alignment used as validation | KNOWLEDGE / RIGOR | high |
| wf_010 pseudobulk | C DS-Codex r3 | 0.000 | Hand-written BH used forward cumulative max; 1,065/1,429 FDRs wrong | RIGOR / – | high |

ᵃ Local tooling friction in the code environment.


## Appendix B. Reproduction and evidence

- **Friction, mismatch, discovery, bypass and ledger analyses:** [analysis_reports/galaxy_improvement_20260924/v2_trace_friction/](analysis_reports/galaxy_improvement_20260924/v2_trace_friction/README.md). Run `extract.py` first; it regenerates `run_summaries.jsonl` and per-run call logs from the archived traces in about 15 s.
- **Prior audit:** [report](analysis_reports/galaxy_improvement_20260924/Galaxy_improvement_report.v1_prior_audit.md), [failure dossiers](analysis_reports/galaxy_improvement_20260924/failure_dossiers.md), [independent checks](analysis_reports/galaxy_improvement_20260924/independent_checks.json) (mitochondrial reference comparison, BH recomputation, amplicon headers, cryptic-exon junctions).
- **Source archives:** trace, evaluator and Galaxy snapshot paths follow `<benchmark>/analysis/<task>/source_snapshots/huggingface_traces/files/<run_id>/`. Line numbers (`Lnnn`) refer to the decompressed primary event log in that directory (`agent_workspace/run_trace/` or, for GPT-5.5 BixBench runs, `run_trace/`).
- **Aggregate tables** referenced for token ratios and job states: [Result_table.md](Result_table.md) (B7, C6, I9, X5, X6, X18).

## Addendum: replicate variability, or why a model that can solve a task still fails it

*Added 25 September 2026. Scripts: [variability.py](analysis_reports/galaxy_improvement_20260924/v2_trace_friction/variability.py) and the mechanism scripts listed in Appendix B.*

**Question.** When a model gets a task right in one replicate and wrong in another, the capability is present but not reliable. What causes the divergence? Which model is least consistent, and why? Is Galaxy more or less stable than open-ended code, and is the source of the instability the same in both tracks?

**Definitions.**
- A *cell* is one task × configuration × track, with three replicates.
- A cell is *mixed* when:
  - **BixBench:** 1 or 2 of 3 replicates are accepted;
  - **CompBio:** 1 or 2 of 3 match a strong (≥ 20/25) consensus answer;
  - **IWC:** the within-cell score range exceeds 0.05.
- Mixed cells are the direct measure of "can, but does not reliably".
- For every rejected replicate in a BixBench mixed cell, the trace was compared with its accepted sibling(s) to find what separated them. This *divergence mechanism* is distinct from the root-cause categories of §3: it names what differed between replicates, not why the answer was wrong.

### V1. How much replicate variability, by model and track

| Configuration | BixBench mixed cells, Galaxy / code (of 50) | CompBio mixed cells, Galaxy / code (of 82) | IWC variable cells, Galaxy / code (of 10) |
|---|---:|---:|---:|
| GPT-5.5 | 1 / 1 | 3 / 8 | 2 / 4 (of 9) |
| GPT-5.6 Sol | 2 / 4 | 4 / 3 | 1 / 2 |
| GPT-5.6 Luna | 5 / 8 | 6 / 10 | 2 / 2 |
| DeepSeek V4 Pro (Codex) | 7 / 6 | 9 / 14 | 0 / 3 |
| DeepSeek V4 Pro (Claude Code, superseded) | **13 / 14** | n/a | n/a |
| **All** | **28 / 33** | **22 / 35** | **5 / 11** |

The CompBio and IWC DeepSeek rows are the Codex harness (V4 Pro 0813 for CompBio). In BixBench, all-rejected cells (0/3) are also fewer in Galaxy (25) than in code (30), and all-accepted cells are more numerous (197 vs 187).

**Galaxy is the more stable condition in all three benchmarks:** fewer mixed cells in BixBench (28 vs 33), CompBio (22 vs 35) and IWC (5 vs 11).

**The least consistent models:**
- **DeepSeek, both harnesses.** DeepSeek via the superseded Claude Code harness is mixed in 26% of BixBench Galaxy cells (13/50) and 28% of code cells. DeepSeek via Codex is the least consistent in CompBio in both tracks (9 and 14 mixed cells).
- **GPT-5.6 Luna** is next (5 and 8 BixBench, 6 and 10 CompBio).
- **GPT-5.5 and Sol** are the most stable (1–4 mixed cells per benchmark and track).
- **IWC exception:** on the workflow-derived IWC tasks, DeepSeek-Codex has no variable Galaxy cell but three in code.

### V2. What separated the accepted and the rejected replicate

| Divergence mechanism | Galaxy (36 rejected replicates in 28 mixed cells) | Code (45 in 33) | Examples (task, configuration, replicate) |
|---|---:|---:|---|
| **Platform trap hit by this replicate only** | **6** | 0 | bix-28-q3 Sol r1 alone asked for non-verbose `long_branch_score` and received the variance; bix-35-q1 DS-ClaudeCode r1 alone used flat keys and silently ran the default metric; bix-31-q2 DS-Codex r2/r3 UDT jobs never dispatched, while r1's pydeseq2 UDT ran; bix-16-q1 DS-Codex r1 chose a container without SciPy; bix-34-q5 DS-ClaudeCode r3 UDT output parsing failed until the budget ran out |
| **Environment or package-version drift** | 0 | **7** | bix-43-q2 Sol r1 installed pydeseq2 0.4.12 (5.831, accepted) while r2/r3 used 0.5.4 (5.840, rejected); bix-55-q1 Sol r1 installed BUSCO 5.7.1 (100) while r2 matched the supplied 5.8.0 outputs (101); bix-45-q1 Luna r1/r3 used PhyKIT 2.0.3 while r2 used the current release. Luna bix-43-q2 r1/r3 and bix-55-q1 r3 are probable, with the same values as the verified Sol cases |
| **Convention or definition applied differently** | 13 | 11 | bix-16-q1: essentiality as −Chronos in the accepted replicates, raw Chronos in the CCND1 replicates (both tracks); bix-51-q8 DS-ClaudeCode r3 used treatment arm as the outcome; bix-61-q2 DS-ClaudeCode r1 re-trimmed the raw FASTQs instead of mapping the supplied trimmed reads; bix-30-q3 code replicates chose the paper's Student t-test instead of Welch |
| **Self-implemented method diverged (script in code, UDT in Galaxy)** | 5 | **23** | bix-12-q2/q5/q6 code: hand-written parsimony-informative-site counters that treat gaps as states (all Galaxy replicates used the PhyKIT wrapper); bix-27-q5 own PCA scope; bix-35-q2 own gene population; Galaxy: bix-12-q4 DS-ClaudeCode r1/r2 own UDT, bix-43-q2 DS-ClaudeCode r2 seven pydeseq2 UDT revisions |
| **Final-step slip** | 6 | 1 | bix-52-q7: Sol r3 and Luna r2 counted the header (19,160); Luna r3 reported the complement (539); bix-16-q1 Luna r2 applied `sort -k3,3n` to scientific notation; bix-14-q1 Luna r2 submitted 0 |
| **No answer** | 3 | 1 | DS-Codex bix-26-q5 r1, bix-27-q5 r1 and bix-46-q4 r2 ended their turns mid-investigation |
| **Benchmark-source lookup asymmetry** | 3 | 2 | bix-54-q7 and bix-26-q5: the only accepted DS-Codex replicate retrieved benchmark source data; its siblings, which analysed honestly, failed |

Four observations locate the variability more precisely.

1. **In Galaxy, replicates diverge at a decision inside the same route, not by taking different routes.**
   - In most Galaxy mixed cells, accepted and rejected replicates ran the same wrapper: `featurewise_correlation` for all three Luna and all three DS-ClaudeCode bix-16-q1 replicates; `phykit_metrics` in bix-28-q3 and bix-35-q1; `Filter1`/`wc_gnu` in bix-52-q7; `bwa_mem` in bix-61-q2.
   - Tool-set agreement is actually *higher* in Galaxy mixed cells (mean Jaccard 0.488; 28% identical toolsets) than in all-accepted cells (0.413; 15%) ([Result_table.md](Result_table.md), Table B6).
   - The outcome turns on a parameter or interpretation step within the route: a sign, a verbosity flag, a branch key, a header line, an outcome column.
2. **Visible friction does not separate the replicates.**
   - Within Galaxy mixed cells, the rejected replicate had more failed MCP calls in only 9 of 28 cells, and fewer in 11.
   - Rejected replicates did consume more effort: median 31 vs 23.5 shell calls, and more input tokens in 17 of 28 cells. This reflects looping and early termination, not error-prone execution.
   - The platform events that split replicates are the silent ones: substituted defaults, wrapper output semantics, undispatched jobs. They appear only in the replicate that happened to take the optional path that triggers them.
3. **Platform traps look stochastic because an optional choice triggers them.** Only one of three Sol replicates asked for the non-verbose output (bix-28-q3). Only one DS-ClaudeCode replicate used flat parameter keys (bix-35-q1).

   The IWC peptide-verification task shows the same pattern through catalog multiplicity:

   | IWC peptide-verification replicates | PepQuery wrapper | Score |
   |---|---|---:|
   | GPT-5.5 r2, Sol r3, Luna r2, Luna r3 | legacy `pepquery/1.6.2` (Luna r3 also ran `pepquery2`) | 0.868–0.908 |
   | All replicates that used only `pepquery2/2.0.2` | `pepquery2/2.0.2` | 0.982–1.000 |

   The version a replicate finds first in search decides the score.
4. **Skill uptake partly explains convention divergence.**
   - Within Galaxy mixed cells, accepted replicates read the relevant domain skill (e.g. `crispr-dependency-correlation`, `phylogenetics-tree-metrics`, `expression-matrix-pca`) in 26 of 40 cases (65%), rejected replicates in 14 of 29 (48%). The code-track figures are 56% vs 44%.
   - The effect is sharpest where the skill states the decisive convention. On bix-16-q1 in Galaxy, both accepted DeepSeek replicates read the CRISPR skill that prescribes −gene effect, and all three DeepSeek replicates that answered CCND1 did not.

### V3. Why DeepSeek and Luna are the inconsistent ones

**DeepSeek (both harnesses): variability from inconsistent process, not from the platform.**
- **Lower skill uptake.** It reads the relevant domain skill in 44% (Claude Code harness) and 55% (Codex harness) of Galaxy runs, versus 74–79% for GPT-5.5, Sol and Luna. On convention-sensitive tasks this makes the definition used vary by replicate: 15 of its 27 Galaxy divergences are convention or self-implementation mechanisms.
- **Unstable interface mode (DS-Codex).** In 51 of 150 BixBench Galaxy runs, DeepSeek-Codex scripted the MCP core library from the shell (`import galaxy_execute_mcp_core`) instead of calling the MCP tools; no other configuration did so more than twice. Acceptance is similar either way (41/51 vs 82/99), but these runs are over-represented among its mixed-cell replicates (13 of 21, versus 34% of all its runs). The same task is therefore attempted through different interfaces from replicate to replicate.
- **Stopping and lookups (DS-Codex).** Three of its seven Galaxy mixed cells come from a replicate that ended its turn without an answer. In two more, the only accepted replicate retrieved benchmark source files.
- **Platform traps.** DeepSeek accounts for 5 of the 6 platform-trap divergences (bix-16-q1, bix-31-q2 ×2, bix-34-q5, bix-35-q1). Its trajectories use more UDTs and more free-form payloads, which exposes them to silent defaults, UDT dispatch failures and missing container dependencies.
- **The superseded Claude Code harness** adds the most self-implemented variants: 15 of its 22 code-track divergences are hand-written reimplementations.

**GPT-5.6 Luna: longest trajectories, most late-stage slips.**
- **Trajectory length.** Luna runs at maximum reasoning and has by far the longest Galaxy trajectories: median 35 MCP calls and 5.0 M input tokens per BixBench run, versus 8–15 calls and 1.2–1.6 M tokens for GPT-5.5 and Sol. More exploration creates more branch points.
- **Where it fails.** Four of its six Galaxy divergences are final-step slips made after long, otherwise correct analyses (bix-52-q7 r2/r3, bix-16-q1 r2, bix-14-q1 r2). Its IWC and CompBio divergences are route picks: the legacy PepQuery wrapper in two peptide replicates, and generic enrichment in all three characterize-response replicates (§4.7).
- **Code track.** Luna reads domain skills in only 27% of code runs, and its code divergences are dominated by version drift and self-implementation.

**GPT-5.5 and Sol are stable** because their trajectories are short and direct, they read the relevant skill in 74–90% of runs, and they rarely re-implement named methods. Their few divergences are single slips or single platform traps.

### V4. Galaxy vs open-ended code: which is more stable, and is the source the same?

**Stability.** Galaxy has fewer mixed cells in every benchmark (28 vs 33, 22 vs 35, 5 vs 11) and fewer all-wrong BixBench cells (25 vs 30). Galaxy is the more stable condition. The typical IWC cell is near-identical in both tracks (median within-cell range 0.0001 in Galaxy, 0.0000 in code), so the IWC difference lies in how often a cell has an outlying replicate, not in everyday noise.

**The sources differ.** They overlap only in the model-driven mechanisms.

| Source of replicate variability | Galaxy | Open-ended code | Why |
|---|---|---|---|
| Self-implementation and environment drift | 5 of 36 (14%) | **30 of 45 (67%)** | In code, each replicate writes its own parser or statistic and installs whatever package versions it chooses: pydeseq2 0.4.12 vs 0.5.4, BUSCO 5.7.1 vs 5.8.0, PhyKIT 2.0.3 vs 2.4.1. Galaxy wrappers fix both the implementation and the version. In Galaxy, self-implementation arises only when an agent writes a UDT. |
| Platform traps and catalog multiplicity | **6 of 36 (17%)**, plus the IWC PepQuery split | 0 | These are Galaxy-specific: silent defaults, wrapper output semantics, undispatched UDTs, and several versions of the same tool in the catalog. |
| Convention application and final-step slips | 19 of 36 (53%) | 12 of 45 (27%) | These are model behaviours shared by both tracks. The same DeepSeek configurations answer CCND1 on bix-16-q1 in both tracks, and the bix-24-q2 direction inversion occurs in both. Their larger *share* in Galaxy reflects the removal of the code-only sources, not more of these errors (19 vs 12 replicates). |
| No answer and benchmark lookups | 6 | 3 | Harness and model behaviour, concentrated in DeepSeek-Codex. |

**Consequences.**
- **Pinning cuts both ways.** Galaxy's stability comes largely from wrapper pinning: one implementation, one version, one output format. This produces stable-right cells, e.g. bix-55-q1 (15/15 answered 101), bix-12-q2/q5/q6 (every Galaxy replicate correct), and bix-43-q2 (11/15 answered 5.8124). The same mechanism produces stable-wrong cells when the pinned version differs from the reference: bix-45-q1 (0/15, identical p-value in every run) and bix-26-q5 (13/15 answered 2).
- **Where replicates are free, variance appears.** Galaxy variance appears where agents escape the pinning (UDTs), hit an unguarded interface path (defaults, verbosity, branch index), or face a choice the catalog leaves open (two PepQuery versions).
- **The shared root is model-level.** Inconsistent application of domain conventions and last-step arithmetic occurs in both conditions. Neither platform addresses it; skill routing and answer-time invariant checks do.

### V5. What would make Galaxy replicates more consistent

1. **Remove the silent paths.** Strict validation with an effective-parameter diff, unambiguous branch selection, and labelled wrapper outputs (§7, recommendations 1, 2 and 6). These address the bix-28-q3 and bix-35-q1 platform-trap divergences.
2. **Make UDT execution predictable.** A dispatch-health, dependency and output-parsing preflight (§7, recommendations 4 and 5) addresses the other four platform-trap divergences: bix-31-q2 r2/r3, bix-34-q5 and bix-16-q1 COX17.
3. **Curate the catalog.** Mark superseded wrappers (e.g. `pepquery/1.6.2` alongside `pepquery2/2.0.2`) as deprecated, rank the current version first in search, and show versions in search results. This removes the IWC peptide split.
4. **Route skills automatically (agent harness).** Surface the relevant domain skill from task keywords rather than relying on the model to open it. The gap is widest for DeepSeek (44–55% uptake vs 74–79%) and is associated with replicate divergence on convention tasks.
5. **Use the same interface every time (harness).** Expose one supported way to drive Galaxy and block ad-hoc imports of the MCP core, so replicates of the same task use the same interface.
6. **Add answer-time invariants and a finish guard (harness).** Check that a median lies within its data, flag zero or empty filter results, require that header rows be excluded from counts, and do not end a turn without an answer. These address the final-step slips and early terminations, which account for 9 of the 36 Galaxy divergences.
7. **For the code track, pin the environment** (lockfile or container per task) to remove the version-drift source that has no counterpart in Galaxy.

*Limits.* Mechanisms are assigned from trace review of the failing and passing replicates; classifications for bix-22-q1, bix-16-q3 and bix-52-q2 rest on unresolved root causes (Appendix A). CompBio mixed cells use the consensus proxy. IWC counts use a 0.05 range threshold. Replicates are not seed-matched, so "variability" here means run-to-run divergence under the same prompt, model and harness, not controlled sampling noise.
