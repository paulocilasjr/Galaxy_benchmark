# RESULTS

We synthesized the 50 retrospective `history_analysis.md` reports under `BixBench_50/analysis/<task_name>/`. The corpus contains 1,500 scored agent runs: 50 BixBench tasks, 5 model configurations, 3 replicates per model, and 2 execution conditions (Galaxy and open-ended code). Original traces were available for all workbook rows, and public Galaxy records represented 711 distinct histories. The analyses were retrospective: no agent code was rerun, hidden references were not opened, and the original evaluator scores were preserved rather than replaced with a new scoring rule.

## Agents maintain bioinformatics accuracy when operating through Galaxy

Across the BixBench-50 subset, agents retained high answer accuracy when routed through Galaxy. Galaxy runs produced 639 correct original evaluator scores among 750 scored runs (85.2%), compared with 615 of 750 open-ended code runs (82.0%). Thus, Galaxy was 3.2 percentage points higher overall in this retrospective set. The effect was modest rather than universal: at the task level, Galaxy had a higher mean score for 14 tasks, open-ended code had a higher mean score for 10 tasks, and 26 tasks were tied. At the model-by-task level, Galaxy exceeded code in 33 comparisons, code exceeded Galaxy in 19, and 198 were tied.

| Evaluation slice | Galaxy accuracy | Open-code accuracy | Difference |
|---|---:|---:|---:|
| All BixBench-50 runs | 85.2% | 82.0% | +3.2 pp |
| `llm_verifier` tasks | 82.3% | 81.0% | +1.3 pp |
| `range_verifier` tasks | 88.2% | 86.2% | +2.1 pp |
| `str_verifier` tasks | 86.3% | 80.0% | +6.3 pp |

The model-level results show the same pattern: Galaxy generally preserved, and in several cases improved, the probability of submitting the fixed answer accepted by the original BixBench evaluator. The largest Galaxy-code gap was observed for `deepseek_v4_pro_via_claude_code_superseded`, for which Galaxy accuracy was 80.0% compared with 69.3% in open-ended code. `codex_gpt_5_6_luna` was balanced across conditions, and no model showed a large systematic loss from using Galaxy.

| Model slug | Galaxy accuracy | Open-code accuracy | Difference |
|---|---:|---:|---:|
| `codex_gpt_5_5` | 89.3% | 87.3% | +2.0 pp |
| `codex_gpt_5_6_sol` | 88.7% | 86.7% | +2.0 pp |
| `codex_gpt_5_6_luna` | 86.0% | 86.0% | 0.0 pp |
| `deepseek_v4_pro_via_codex` | 82.0% | 80.7% | +1.3 pp |
| `deepseek_v4_pro_via_claude_code_superseded` | 80.0% | 69.3% | +10.7 pp |

This high accuracy is best interpreted as evidence that a structured workbench can carry agent reasoning into executable, auditable bioinformatics practice without erasing the agent's ability to reach correct answers. In these tasks, Galaxy did not simply provide a place to store files. It exposed typed tools, explicit parameters, datasets, histories, job states, and reusable outputs. These platform properties are especially relevant for biomedical analysis, where the route to an answer often matters as much as the answer itself. The result therefore supports a field-level conclusion: agentic bioinformatics can be made more reviewable and reproducible without an obvious accuracy penalty, and in this corpus Galaxy slightly improved accuracy relative to unconstrained code.

## Galaxy workbench enhances agents to structure and run analyses

The Galaxy condition supported successful work across the full biological range represented in BixBench-50. At least one Galaxy run was correct for 47 of 50 tasks, and all 15 Galaxy runs were correct for 25 tasks. These solved tasks included phylogenetic and alignment-derived calculations, variant and methylation summaries, transcriptomic differential expression and enrichment questions, statistical modeling, correlation analyses, protein abundance questions, and imaging-derived phenotypic measurements. The three tasks with no correct Galaxy runs were `bix-45-q1`, `bix-53-q2`, and `bix-61-q5`; two of these were also never solved by open-ended code, indicating task-level difficulty or scoring sensitivity rather than a Galaxy-specific failure alone.

The Galaxy histories exposed 5,042 distinct analytical creating jobs after deduplication, including 552 failed jobs (10.9%). These job ledgers are scientifically important because they convert agent behavior into inspectable execution evidence. They retain tool identifiers, dataset associations, parameter records, job states, and, where available, error text. This structure explains why agents could accomplish diverse tasks in Galaxy: instead of holding the whole analysis in an ephemeral shell session, agents could decompose work into data upload, filtering, statistical summarization, tool execution, and result extraction steps whose intermediate products remained addressable.

Galaxy also creates a practical recovery surface. Failed jobs are not silent: they return state, parameters, inputs, and errors that can be inspected before retrying. Several reports flag later successful jobs with the same tool and input dataset identifiers as operational recovery candidates. The audit did not manually adjudicate every candidate as a scientific recovery, so the safe conclusion is not that Galaxy automatically fixes mistakes. Rather, Galaxy makes failed execution legible. That legibility can help agents revise parameters, rerun tools, or verify that a later successful job used the intended inputs.

The most visible Galaxy tool families were PhyKIT, Datamash, and Summary Statistics, alongside many unclassified Galaxy routes whose job records were still retained. This matters for users because a correct answer from Galaxy arrives with a review trail: histories, datasets, job states, and parameterized tool calls can be audited after the run. For regulated, collaborative, or publication-facing computational biology, that evidence is a central benefit over a transient notebook or shell transcript.

## Task solution variability is model-dependent

The analyses show that correct answers can arise through different computational routes. In the Galaxy condition, 572 of 750 run-level route indicators were unclassified at the high-level route-label layer, but explicit tool families still recurred: PhyKIT appeared in 116 Galaxy routes, Datamash in 55, and Summary Statistics in 17. In open-ended code, 610 of 750 runs were described as local shell or script with method unclassified; explicit open-code indicators included PhyKIT (100), Newick or branch parsers (80), IQ-TREE report parsing (15), and Biopython (3).

Model behavior was not identical. `codex_gpt_5_6_luna` used Datamash most often among Galaxy runs (22 route-family counts), whereas `deepseek_v4_pro_via_codex` used Summary Statistics most often (7) and showed the highest explicit PhyKIT count in open code (30). `codex_gpt_5_6_sol` and `codex_gpt_5_5` showed similar accuracy and similar Galaxy route profiles, with PhyKIT appearing frequently in phylogenetic tasks and unclassified routes dominating more general tabular, statistical, and transcriptomic tasks.

| Model slug | Characteristic Galaxy route families | Characteristic open-code route families |
|---|---|---|
| `codex_gpt_5_5` | Unclassified routes dominated; PhyKIT recurrent; rare Datamash and Summary Statistics | Mostly local scripts; PhyKIT and Newick parsing for phylogenetic tasks |
| `codex_gpt_5_6_sol` | Unclassified routes plus PhyKIT, Datamash, and Summary Statistics | Mostly local scripts; PhyKIT and Newick parsing |
| `codex_gpt_5_6_luna` | Highest Datamash use among models; PhyKIT also common | Local scripts plus Newick parsing, PhyKIT, and occasional IQ-TREE report parsing |
| `deepseek_v4_pro_via_codex` | Broadest explicit mix of PhyKIT, Datamash, and Summary Statistics | Local scripts with the highest explicit PhyKIT count |
| `deepseek_v4_pro_via_claude_code_superseded` | Unclassified routes plus PhyKIT and Datamash | Local scripts with PhyKIT, Newick parsing, IQ-TREE report parsing, and rare Biopython |

The available analyses do not define formal task difficulty levels, and `task_list.json` also does not provide difficulty strata. Therefore, solution consistency cannot be attributed to easy, medium, or hard bins. Instead, the stronger pattern is domain- and model-dependent. Phylogenetic tasks tended to converge on established primitives such as PhyKIT, Newick parsing, branch statistics, tree length, treeness, patristic distance, or evolutionary-rate calculations. Transcriptomic and enrichment tasks were more sensitive to filtering thresholds, covariates, shrinkage choices, pathway libraries, and rounding. Statistical modeling tasks required correct formula specification and coefficient extraction. Users should therefore expect multiple valid-looking routes to sometimes produce the same accepted answer, but should not assume that route equivalence guarantees scientific equivalence. Parameter inspection remains essential.

## Galaxy usage improves human readability but at a higher token cost

Galaxy imposed a substantial input-token overhead. Across 250 model-task comparisons with reported usage in both conditions, the median Galaxy/open-code input-token ratio was 4.74x, with an interquartile range of 2.45x to 9.62x and a maximum of 56.9x. This ratio reflects provider-reported input-token totals from the original traces; it is not a full cost model, does not sum cached input or reasoning output, and does not include dated API pricing.

| Model slug | Median Galaxy/code input-token ratio | Mean ratio | Galaxy accuracy | Open-code accuracy |
|---|---:|---:|---:|---:|
| `codex_gpt_5_5` | 3.86x | 4.96x | 89.3% | 87.3% |
| `codex_gpt_5_6_sol` | 5.03x | 6.86x | 88.7% | 86.7% |
| `codex_gpt_5_6_luna` | 7.64x | 14.63x | 86.0% | 86.0% |
| `deepseek_v4_pro_via_codex` | 4.50x | 7.93x | 82.0% | 80.7% |
| `deepseek_v4_pro_via_claude_code_superseded` | 2.97x | 4.74x | 80.0% | 69.3% |

The token increase was not explained simply by more failed attempts. The task-level median token ratio had only a weak positive association with the number of Galaxy analytical jobs (Pearson r = 0.15) and a weak negative association with failed jobs (r = -0.10). Several high-token tasks had few failures, whereas some low-ratio tasks had many failed jobs. This suggests that the cost arises from the structure of Galaxy operation itself: tool discovery, dataset upload and selection, history management, parameter serialization, polling, output retrieval, and provenance inspection all require conversational and API scaffolding beyond the core scientific computation.

The readability gain is therefore best described as auditability rather than a directly measured human-review outcome. The histories make the analysis more readable to a reviewer because they expose what tool ran, on which dataset, with what parameters, and with what job state. The source analyses did not include blinded reviewer scoring or time-to-review measurements, so they do not prove that humans read Galaxy outputs faster. They do show that Galaxy produces a richer evidence layer for evaluating agent behavior.

For benchmarked biomedical analysis, the benefits generally justify the higher token cost. Galaxy preserved or slightly improved answer accuracy, supported successful execution across most task classes, and generated provenance that open-ended code often lacks unless the agent constructs it deliberately. The trade-off is most favorable when the goal is reproducible, reviewable analysis rather than the cheapest possible calculation. For quick exploratory computation, the token cost may be excessive; for scientific workflows that must be audited, rerun, or defended, the Galaxy workbench converts agent work into a more durable and interpretable record.
