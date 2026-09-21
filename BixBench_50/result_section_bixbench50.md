# RESULTS

## Agents maintain bioinformatics accuracy when operating through Galaxy

We retrospectively examined 1,500 archived agent runs from the BixBench-50 benchmark. The design crosses three controlled variables, and every result below is reported at the level of one of them. **Tasks** are the 50 verified BixBench questions, drawn from 33 source capsules; they differ in length, analytical complexity and biological domain, but no independent difficulty grading was available, so task difficulty is never used here as an explanatory variable. **Model configurations** are the five agent set-ups evaluated on every task: GPT-5.5, GPT-5.6 Sol and GPT-5.6 Luna through the Codex harness, and DeepSeek V4 Pro through the Codex harness and through a superseded Claude Code harness. Because four of the five share the Codex harness while the superseded set-up does not, the model and its harness are confounded for that one set-up; we therefore write model configuration rather than model throughout. **Execution environments** are the two settings in which the agent produced and ran code: Galaxy, in which the agent was required to perform the analysis through the Galaxy workbench API, and open-ended code, in which it executed code directly in its own runtime. Both environments were supplied with skills, and both are recorded as conditions in the archived evidence.

**Replicates** are three repeat executions of each task by each model configuration in each environment. They were not a designed factor and are not documented as seed-matched, so they are used to quantify run-to-run variation within a fixed combination of the other variables, never as paired observations across environments. One **run** is accordingly a single execution of one task, by one model configuration, in one environment, for one replicate, and 50 × 5 × 2 × 3 yields the 1,500 runs audited here. Where an analysis summarizes the three replicates of a fixed task and model configuration within one environment, we call that group an **analysis cell**; there are 500 cells. The **solution path** - the tools, commands and parameters through which an agent reached its answer - is an outcome of a run rather than a controlled variable, and is analysed separately in the third section below. Three outcome quantities are kept distinct throughout and are never merged: the **submitted answer** returned by the agent; whether the original benchmark evaluator **accepted** that answer, which is the accuracy endpoint used in every accuracy statement; and the **execution state** of the underlying Galaxy jobs or shell commands, which records operational completion and carries no claim about scientific correctness.

Across this BixBench-50 subset, Galaxy runs achieved 85.2% accuracy (639/750), compared with 82.0% (615/750) for open-ended code (Table 1). All original scores were retained, including zero scores for five Galaxy runs and one open-ended-code run that the original evaluator recorded as missing an answer.

Holding the task set fixed and varying model configuration and environment, high accuracy was observed throughout (Table 1). GPT-5.5 achieved 89.3% accuracy through Galaxy and 87.3% through open-ended code; the corresponding values were 88.7% and 86.7% for GPT-5.6 Sol, and 86.0% in both environments for GPT-5.6 Luna. DeepSeek V4 Pro achieved 82.0% and 80.7% through the Codex harness, and 80.0% and 69.3% through the superseded Claude Code harness, respectively (150 runs per environment and configuration). Galaxy had higher accuracy on 14 tasks, open-ended code on 10, and the environments were tied on 26 (Table 2). Thus, the pooled difference of 3.2 percentage points reflected heterogeneous task and configuration outcomes rather than a uniform advantage.

Shifting the unit of analysis from the run to the analysis cell resolves accuracy into replicate outcomes, which separates whether a model configuration could reach an accepted answer at all from whether it did so on every replicate (Table 3). Outcomes were overwhelmingly all-or-nothing: of the 250 analysis cells in each environment, 88.8% in Galaxy and 86.8% in open-ended code had either all three or none of their replicates accepted, leaving 11.2% and 13.2% with one or two. The configurations differed much less in whether they could answer a task at all than in whether they answered it every time. Every Galaxy configuration obtained at least one accepted answer for 45 of 50 tasks (90.0%), and open-ended-code configurations for 42 to 46 (84.0-92.0%), a spread of 8 percentage points; acceptance of all three replicates ranged from 64.0% to 88.0% of tasks in Galaxy and from 56.0% to 86.0% in open-ended code, a spread of about 30 points. Expressed as a consistency index - tasks answered in all three replicates as a proportion of those answered at least once - the configurations ranged from 97.8% for GPT-5.5 in Galaxy to 66.7% for the superseded DeepSeek configuration in open-ended code. The accuracy ordering in Table 1 is therefore largely an ordering of replicate consistency rather than of the ability to reach an accepted answer.

Complete failures were more concentrated in Galaxy. Each Galaxy configuration failed all three replicates on exactly five tasks, although not the same five: three tasks were failed by every configuration and seven by at least one. The corresponding open-ended-code counts were more dispersed, at four to eight tasks per configuration, with two tasks failed by every configuration and twelve by at least one. Pairing the environments within task and configuration, 198 of 250 pairs (79.2%) recorded the same number of accepted replicates, with Galaxy higher in 33 pairs and open-ended code in 19. Replication also changes the apparent success rate materially: single-run accuracy of 85.2% in Galaxy corresponds to 90.0% of tasks answered at least once in three replicates, and 82.0% corresponds to 88.0% in open-ended code. A single run therefore understates task coverage, whereas a best-of-three summary overstates the reliability a user would experience from one execution.

Read alongside the solution-path analysis below, these distributions indicate that agents varied more in how they reached an answer than in whether that answer was accepted: replicate outcomes were all-or-nothing in 88.8% of Galaxy cells, whereas all three replicates recorded an identical toolset in only 18.0% of evaluable Galaxy cells. Consistent acceptance therefore did not require a consistent computational solution path.

The superseded DeepSeek/Claude Code configuration accounted for 16 of the 24 additional accepted Galaxy answers. Excluding this configuration reduced the descriptive difference to 1.3 percentage points, with accuracy of 86.5% (519/600) for Galaxy and 85.2% (511/600) for open-ended code (Table 1). An exploratory bootstrap of the full comparison, resampling the 33 source capsules as blocks while retaining their tasks and runs, yielded a 95% interval of -1.4 to +7.9 percentage points for the pooled difference (100,000 resamples). This post hoc interval assumes independence between capsules, which may share biological inputs. Together with differences in instructions, tools and execution software, and the absence of documented matched seeds, these results preclude a claim of superiority, statistical equivalence or non-inferiority.

The execution records provide a practical context for the high observed accuracy: agents had access to both data-manipulation operations and established bioinformatics tools, and could request custom tools within Galaxy when composing task-specific calculations. This combination supported analyses that required connecting heterogeneous inputs to specialist computations, rather than answering tasks from text alone. Installed tools supplied identifiable computational implementations, while filtering, conversion and aggregation operations supported the preparation of their inputs. These solution paths accompanied successful answers, although their causal contribution was not isolated experimentally. The finding is therefore that high benchmark accuracy was compatible with a workbench that retained inspectable execution records, not that the workbench itself explained the accuracy difference. For agent-assisted bioinformatics, this establishes the feasibility of obtaining accepted analytical answers alongside explicit computational provenance, while leaving scientific validation of individual workflows distinct from answer acceptance. The performance estimates here apply to BixBench-50 and do not extend to GalaxyBench or BioAgent.

## Galaxy workbench enables agents to structure and run analyses

Agents in the Galaxy environment produced at least one accepted answer for 47 of the 50 tasks, and all 15 runs were accepted for 25 tasks. Open-ended code produced at least one accepted answer for 48 tasks and acceptance in every run for 25 tasks (Table 2). Tasks with unanimous acceptance in Galaxy spanned phylogenetic treeness comparisons, filtered somatic-variant counts, colony morphology summaries, differential-expression counts and logistic-regression model assessment. These coverage measures describe performance across configurations and replicates, rather than the probability that a single agent run will succeed.

The observed tool records show how agents structured work across these domains. Spreadsheet conversion, column selection and filtering accompanied specialist operations including PhyKIT metrics, DESeq2 differential expression, pathway over-representation analysis, feature-wise correlation and regression. Among the retained creating jobs, the recorded spreadsheet-to-tabular converter accounted for 644 jobs, column selection for 557 and filtering for 397; the recorded KEGG over-representation and PhyKIT metrics tool versions accounted for 269 and 202 jobs, respectively (Table 4). These counts describe observed operations rather than independent analyses, but highlight the combination of data preparation and domain-specific computation in the recorded workflows.

Concrete task outcomes illustrate the breadth of this composition (Table 5). All 15 Galaxy runs returned accepted answers for a somatic-variant filtering and counting task and for a colony-morphology task requiring circularity to be summarized for the genotype with the largest mean colony area. Both tasks also yielded 15 accepted open-ended-code answers. Histories associated with the latter contained grouping and Datamash operations. A differential-expression task involving DESeq2, shrinkage and adjustment for sex yielded 15 accepted Galaxy answers, compared with 13 in open-ended code, while a logistic-regression AIC task yielded 15 accepted answers in each environment. For whole-genome coverage, histories contained BWA-MEM and samtools depth operations, with accepted answers in 14 of 15 Galaxy runs and all 15 open-ended-code runs. These examples connect the aggregate accuracy to recognizable bioinformatics and statistical tasks. Explicit tool identifiers, parameters and dataset associations made the recorded computational sequences available for retrospective inspection, including assessment of which inputs and settings were used.

Execution evidence was available at different levels of detail (Table 6). Dataset-bearing snapshots represented 711 distinct public histories linked to 714 Galaxy run records. Another 32 runs had history metadata only because their histories exceeded the collector's 300-item limit, and four histories were unavailable. The capped histories contained 41,304 elements: state summaries reported 40,722 as `ok`, 202 as `new` and nine as `failed_metadata`, with 371 elements not accounted for by those summaries. Detailed contents were intentionally left unretrieved. Thirty-one of the 32 capped-history runs had accepted answers, showing that a collection limit should not be interpreted as analytical failure. These element states describe dataset availability or processing status, not independent jobs or scientific correctness.

The detailed snapshots contained 5,042 distinct creating jobs, of which 4,454 were `ok`, 552 were `error` (10.9%), 25 were `deleted` and 11 were `paused` (Table 6). These records include preparation and conversion steps, have incomplete coverage, and may contain inherited or later history state; they do not represent a complete inventory of benchmark-specific scientific attempts. Within the available records, 93 candidate failure-to-success sequences were identified across 49 Galaxy runs, based on a later successful job using the same tool and input dataset identifiers. The preserved parameters and error records make such sequences inspectable, but the candidates were not independently adjudicated as successful scientific corrections. Accordingly, the data demonstrate evidence for investigating recovery, rather than an improvement in recovery or parameter selection relative to open-ended code.

Successful answers in the Galaxy environment also cannot yet be equated with verified Galaxy-only completion. The original evaluator's fresh-history recording check was false for all 750 Galaxy runs despite the retrieved history evidence. Reconciliation of this discrepancy and attribution of substantive calculations to their execution location remain necessary before assigning a count of exclusively Galaxy-derived solutions. The demonstrated workbench contribution is the combination of diverse analytical operations with identifiable inputs, parameters, outputs and execution states, providing material that users can inspect when evaluating an agent's result.

The environment is the focus of the next analysis, with task and model configuration held fixed within each comparison. Whether the workbench changed which tasks could be answered, rather than how the work was recorded, can be examined by pairing the two environments within each task and model configuration (Table 7). No task was answered acceptably in Galaxy alone: every task with at least one accepted Galaxy answer also produced at least one accepted open-ended-code answer. The converse occurred once, for the RCV Mann-Whitney task, with 8 of 15 accepted open-ended-code answers against none in Galaxy, and two tasks produced no accepted answer in either environment. Task-level pairing alone would overstate environment effects, however, because each task contributes 15 runs per environment across five configurations. Among the 250 task-by-configuration pairs, strict discordance - all three replicates accepted in one environment and none in the other - occurred in four pairs favouring Galaxy, spread across three tasks, and two pairs favouring open-ended code, both on the same task.

Requiring a difference to reproduce across configurations separates environment effects from configuration-specific ones. Two tasks had at least four of five configurations favouring Galaxy with none favouring open-ended code: the miRNA multiple-testing ratio task (15 of 15 accepted Galaxy answers against 6 of 15) and the gseapy odds-ratio task (11 of 15 against 2 of 15). No task showed the mirror pattern for open-ended code. Six tasks had configurations pointing in both directions, so their apparent environment differences are configuration-specific rather than attributable to the execution environment, and 22 tasks were tied across all five configurations. The workbench therefore altered the recorded outcome for a small, identifiable minority of tasks rather than shifting performance broadly.

The recorded solution paths and submitted answers indicate what separated these cases (Table 7). For the miRNA task, all 15 Galaxy runs submitted the ratio 0:0 using an installed univariate testing tool together with task-specific correction tools, whereas open-ended-code runs split between 0:0, accepted in all six cases, and 1:0, rejected in all nine; the outcome turned on whether a single miRNA passed the corrected threshold. For the gseapy task, Galaxy runs using the installed gseapy and DESeq2 wrappers concentrated on the accepted odds ratio 5.8124, submitted in 9 of 15 runs, while open-ended-code runs concentrated instead on 5.8310, submitted in 5 of 15, with the remaining values spread between 5.62 and 6.16 - differences consistent with variation in the upstream differentially expressed gene set rather than in the enrichment test itself. The single open-ended-code advantage arises the same way in reverse: all 15 Galaxy runs, using installed PhyKIT and nonparametric rank-test tools, submitted the identical p-value 1.5198 x 10^-56, which the evaluator did not accept, whereas open-ended-code runs split, 8 submitting 7.6968 x 10^-54 and being accepted. Both environments invoked the same statistical function with equivalent options, and five open-ended-code runs also submitted the unaccepted value, so the divergence arose upstream in how the RCV inputs were assembled; the archived packages do not retain the intermediate outputs needed to establish which construction the reference used.

Two checks limit how far these cases generalize. First, the apparent convergence of Galaxy answers within the discordant tasks is not a corpus-wide property: the median number of distinct submitted answers per task was 2.0 in both environments, with a single distinct answer in 18 of 50 tasks in each. Unanimity is also not correctness, since among the 18 tasks on which all 15 Galaxy runs submitted one answer, 15 were accepted throughout and two were rejected throughout. Second, evaluator behaviour contributes directly to these counts: byte-identical submitted answers received different scores under different recorded verifier modes, and the rarely applied rounded-numeric mode accepted 2 of 11 runs against 81.8-87.4% for the other modes. That mode was applied only to the two DeepSeek configurations, making it a configuration-level rather than a environment-level confounder; verifier modes were otherwise distributed almost identically across the two environments, which supports the environment comparison itself.

For a prospective user, the practical implication is that in this corpus the workbench did not determine which analyses could be completed; it determined what could be examined afterwards. Where a environment difference did appear, it originated in a specific analytical choice - a threshold boundary, an upstream gene set, an input assembly - that the Galaxy records exposed as tool identifiers, parameters and dataset associations, and that the open-ended-code archives expressed as command text. The case in which every Galaxy replicate reproduced an unaccepted p-value illustrates the corresponding risk: a standardized solution path reproduces an unaccepted result as reliably as an accepted one, so recorded provenance supports verification but does not replace it.

## Solution-path variability across tasks, model configurations and execution environments

Recorded tool use differed among model configurations (Table 8), although the available classification describes tool and command indicators rather than fully adjudicated scientific methods. In Galaxy, GPT-5.5 and GPT-5.6 Sol had PhyKIT indicators in 23 and 25 of their 150 runs, respectively, and Datamash indicators in three and eight. GPT-5.6 Luna had 20 PhyKIT-labelled runs and the largest number of Datamash-labelled runs (22). DeepSeek through Codex had 25 PhyKIT, 14 Datamash and seven Summary Statistics indicators; the superseded Claude Code configuration had 23, eight and one, respectively. Summary Statistics indicators were also recorded for the GPT configurations, in one GPT-5.5 run and in four runs each for GPT-5.6 Sol and GPT-5.6 Luna. Labels were non-exclusive. In open-ended code, the identified solution paths included local scripts, PhyKIT and Newick or branch parsing across all five configurations. PhyKIT indicators were most frequent for DeepSeek through Codex (30 runs), while Newick or branch parsing was most frequent for GPT-5.6 Sol (23 runs). IQ-TREE report parsing and Biopython appeared less frequently across the corpus, in 15 and three open-ended-code runs, respectively, and in no Galaxy run.

The remaining analyses take the solution path as the outcome and treat task, model configuration and environment as the explanatory variables. Because solution-path labels were recorded for only a minority of runs, we assessed replicate-level consistency directly from the archived execution records. For each of the 500 analysis cells - one task, environment and configuration with its three replicate-labelled runs - we derived a solution-path fingerprint per run and compared the three fingerprints within the cell (Table 9). The fingerprint is the set of version-stripped Galaxy tool identifiers recorded on job events, excluding data-fetch jobs, or, in open-ended code, the set of analytical tool and library tokens matched by a fixed vocabulary against the recorded command text. Identical fingerprints across all three replicates were the exception in both environments: 44 of 244 evaluable Galaxy cells (18.0%) and 16 of 250 open-ended-code cells (6.4%). Repeating a task with the same configuration therefore rarely reproduced the same recorded toolset.

Within Galaxy, agreement differed across configurations: DeepSeek V4 Pro through Codex had the highest identical-fingerprint rate (25.0%; mean pairwise Jaccard similarity 0.541) and GPT-5.5 the lowest (12.0%; 0.260). This ordering did not carry over to open-ended code, where DeepSeek through Codex was the least consistent configuration (2.0%; one of 50 cells) and the three GPT configurations were tied at 8.0%. The configuration that repeated itself most closely in one environment was therefore not the one that repeated itself most closely in the other, which does not support an account in which solution-path stability is a fixed property of a model. Agreement magnitudes should not be compared between environments: the two fingerprints are extracted by different instruments - structured tool identifiers in Galaxy against closed-vocabulary parsing of command text in open-ended code - and the two summary measures disagree in direction, with Galaxy showing the higher identical-path rate and open-ended code the higher mean Jaccard similarity. Comparisons between configurations within a environment use a single instrument and are the interpretable contrast.

Which task was being solved accounted for more of the observed spread than which configuration solved it (Table 10). In Galaxy, mean agreement per task ranged from 0.00 to 0.93 with a standard deviation of 0.274 across the 50 tasks, whereas mean agreement per configuration spanned 0.26 to 0.54 with a standard deviation of 0.092; the corresponding standard deviations in open-ended code were 0.088 across tasks and 0.038 across configurations. Task identity did not transfer between environments, however: the rank correlation between a task's Galaxy agreement and its open-ended-code agreement was weak (Spearman rho = 0.135, n = 50 tasks). Variability was thus concentrated in particular task-and-environment combinations rather than in tasks that are intrinsically variable or configurations that are intrinsically unstable.

Two intuitive explanations were not supported by these records. Recorded workload showed essentially no association with agreement, whether measured as median events per run (Spearman rho = +0.012 in Galaxy and -0.075 in open-ended code) or median analytical Galaxy jobs per run (+0.110), so longer or more operation-heavy executions were not systematically more variable. Nor did the configuration performing the fewest operations repeat itself most closely: in Galaxy, DeepSeek V4 Pro through Codex recorded both the highest median events per run (81.0) and the highest agreement, while GPT-5.5 recorded the fewest (39.0) and the lowest. These observations do not support an account in which a less elaborate or less capable model is more stable, and no independent capability or difficulty measure was available with which to test either construct. Two associations were observed instead. Galaxy cells containing at least one failed job had lower agreement than cells with no recorded failure (mean Jaccard 0.281 across 135 cells against 0.585 across 109), a difference that persisted within each tertile of fingerprint size and is therefore not a by-product of larger toolsets. Second, and contrary to a reading in which consistency indicates reliability, Galaxy agreement was highest where no answer was accepted: cells with no accepted answer had mean Jaccard 0.638 and 41.7% identical solution paths, against 0.385 and 14.1% for cells in which all three replicates were accepted. Those 24 cells derive from only six distinct tasks, so this is a clustered case-level observation rather than a population estimate, and no comparable gradient appeared in open-ended code (0.651 against 0.654). It is consistent with the RCV Mann-Whitney case below, in which all 15 Galaxy runs shared a PhyKIT indicator and none was accepted: replicates can converge on the same unaccepted solution path.

Additional examination of the saved traces identified structured execution requests in 30 of the 32 runs whose histories exceeded the collection limit. These requests included archive extraction, collection filtering and aggregation, PhyKIT alignment and tree wrappers, Datamash and nonparametric rank tests. Seventeen of the 32 runs requested custom Galaxy tools, including tools for treeness and parsimony-site calculations (Table 6). For example, a Luna run for the treeness-comparison task requested a custom summary tool alongside archive extraction and collection filtering, whereas a Sol run for the fungal parsimony-informative-site task requested installed PhyKIT and Datamash tools. This evidence identifies both installed-tool and custom-tool solution paths within Galaxy, but execution requests alone do not establish successful completion, and the selected large-history subset cannot estimate their prevalence across all runs.

Different solution-path indicators could accompany the same accepted endpoint (Table 5). All 30 runs for the treeness-comparison task were accepted despite differences in recorded solution paths. Conversely, all 15 Galaxy answers to the RCV Mann-Whitney task were rejected, compared with eight accepted open-ended-code answers, although the Galaxy runs shared a PhyKIT indicator and all 45 retrieved creating jobs were `ok`. For the transition-to-transversion-ratio task, neither environment produced an accepted answer even though all 19 retrieved Galaxy creating jobs were `ok`. These examples distinguish operational completion and tool-family agreement from answer correctness; they do not resolve whether discrepancies arose from inputs, parameters, interpretation or evaluator behavior.

The extent of scientific solution variability remains less certain than these observed tool-use differences. The original classification left 572 of 750 Galaxy runs (76.3%) unclassified and labelled 610 of 750 open-ended-code runs (81.3%) as local shell or script with method unclassified. The targeted recovery improved descriptions for selected runs but did not uniformly reclassify the corpus. The replicate-level fingerprint comparison reported above uses recorded tool identifiers and command text rather than these labels and therefore covers the corpus more completely, but it measures agreement between recorded operations rather than adjudicated scientific method: identical toolsets can implement different analyses, and different toolsets can implement the same one. No independent task-difficulty strata were available, preventing comparisons of solution consistency across difficulty levels; low observed acceptance alone would not provide an independent difficulty measure. Consequently, the evidence supports configuration-dependent tool-use patterns and ranks configurations by replicate-level agreement of recorded operations within each environment, but that ranking does not transfer between environments, and the evidence does not identify a configuration with greater scientific method diversity or more consistent solutions after accounting for task difficulty. For users, the demonstrated implication is that different recorded solution paths can yield accepted answers, while a shared tool or successful execution state does not establish scientific equivalence. The contrasting treeness and RCV outcomes make this distinction particularly clear: agreement at the endpoint can coexist with implementation differences, and agreement at the tool-family level can coexist with rejected answers. Interpretation of agent-generated results therefore requires examination of input selection and analytical settings alongside the final answer.

## Input-token cost and recorded provenance across execution environments

The structured execution evidence in the Galaxy environment accompanied substantially greater reported input-token use. Across 250 task-by-configuration comparisons, the median Galaxy-to-open-ended-code input-token ratio was 4.74, corresponding to a 374% increase (interquartile range, 2.45-9.62; range, 0.265-56.94; Table 11). For each task and configuration, the ratio compared the median input-token total of three Galaxy runs with the median of three open-ended-code runs. Thus, this estimate describes a typical within-task, within-configuration relative increase, rather than the ratio of pooled token totals or a comparison of seed-matched replicates. The wide range also indicates that higher consumption was not universal: some comparisons required fewer input tokens in Galaxy, whereas others showed much larger increases.

Relative token use varied across configurations without tracking answer acceptance monotonically (Table 11). Median ratios were 3.86 for GPT-5.5, 5.03 for GPT-5.6 Sol, 7.63 for GPT-5.6 Luna, 4.50 for DeepSeek through Codex and 2.97 for the superseded DeepSeek/Claude Code configuration. Luna had the greatest median relative input-token use but not the highest Galaxy accuracy: its acceptance rate was 86.0%, compared with 89.3% for GPT-5.5. Conversely, the superseded DeepSeek configuration had the lowest median ratio and the largest environment-associated accuracy difference, but the lowest absolute accuracy in both environments. These observations do not support a simple interpretation in which more tokens identify a more capable model or fewer mistakes. Relative consumption depends on the open-ended-code denominator as well as on model, harness and provider accounting, and no independent model-capability ranking was evaluated.

The traces identify several operations that could contribute to the additional input footprint, including tool discovery, parameter specification, history inspection, execution requests, waiting and output retrieval. Such interactions expose the computational state to the agent, but their contribution to total token use was not separately quantified. Failure-related overhead likewise remains unresolved. Although the Galaxy snapshots contained failed jobs and candidate failure-to-success sequences, failed Galaxy jobs and nonzero shell exits are not interchangeable measures of scientific attempts. The available records therefore do not establish that open-ended code consumed fewer tokens because it failed less frequently, nor do they quantify how much of the Galaxy increase arose from retries rather than routine coordination of the analysis. Assigning the difference to either mechanism would require stage-resolved token accounting and comparable definitions of attempts in both environments.

Input-token consumption is also distinct from financial or total computational cost. The provider-reported input totals include cached input, which was not counted a second time, and exclude output tokens from this endpoint. Differences in cache use, output generation, pricing and execution infrastructure would therefore need to be incorporated before translating the observed ratios into monetary costs. The present comparison quantifies a larger input-token footprint, not a corresponding fold increase in expenditure.

The evidence for human interpretability is more specific than a demonstrated improvement in readability. Galaxy histories linked identifiable tools and parameters to input datasets, outputs and execution states, providing structured material for checking how an answer was produced and where an operation failed. Even for collection-limited histories, metadata distinguished the size and recorded states of the history from final-answer acceptance without requiring retrieval of every element. Open-code archives also retained commands and outputs, however, and no blinded readability assessment, review-time comparison or independent replay study was performed. Improved human readability should therefore be regarded as a proposed benefit of the structured records, rather than a measured outcome of this benchmark.

Together, the accuracy, execution and usage results define a practical trade-off: high answer acceptance was achievable alongside inspectable workbench records, at a substantially higher median input-token footprint. This combination is relevant to bioinformatics settings in which a plausible answer alone is insufficient and the computational steps must remain available for scrutiny. The records establish the availability of that evidence, but not whether it reduces human verification effort enough to offset the additional resource use. The supported conclusion is that accuracy and structured provenance can coexist in agent-driven analysis; the economic and human-review value of that provenance remains to be measured.

## TABLES

**Table 1 | Answer acceptance by model configuration and execution environment in the BixBench-50 subset.**

| Model configuration | Galaxy, accepted/n (%)ᵃ | Open-ended code, accepted/n (%)ᵃ | Difference (pp)ᵇ |
|---|---|---|---|
| GPT-5.5 | 134/150 (89.3) | 131/150 (87.3) | +2.0 |
| GPT-5.6 Sol | 133/150 (88.7) | 130/150 (86.7) | +2.0 |
| GPT-5.6 Luna | 129/150 (86.0) | 129/150 (86.0) | 0.0 |
| DeepSeek V4 Pro (Codex) | 123/150 (82.0) | 121/150 (80.7) | +1.3 |
| DeepSeek V4 Pro (Claude Code, superseded) | 120/150 (80.0) | 104/150 (69.3) | +10.7 |
| **All configurations**ᶜ | **639/750 (85.2)** | **615/750 (82.0)** | **+3.2** |
| All configurations excluding the superseded configurationᵈ | 519/600 (86.5) | 511/600 (85.2) | +1.3 |

Accuracy is defined as acceptance of the submitted answer by the original benchmark evaluator. The retrospective corpus comprises 1,500 archived runs covering 50 BixBench tasks from 33 source capsules, with three replicate-labelled runs per task, configuration and environment (150 runs per configuration per environment). Replicate labels do not document matched seeds. pp, percentage points.
ᵃPer-configuration counts were derived from the reported percentages and the fixed denominator of 150 runs; derived counts sum to the independently reported environment totals of 639 and 615.
ᵇDifference = Galaxy − open-ended code; positive values favour Galaxy. An exploratory post hoc block bootstrap resampling the 33 source capsules (100,000 resamples) gave a 95% interval of −1.4 to +7.9 pp for the pooled difference. The interval assumes independence between capsules that may share biological inputs and, together with differences in instructions, tools and execution software, precludes claims of superiority, statistical equivalence or non-inferiority.
ᶜAll original evaluator scores were retained, including zero scores for five Galaxy runs and one open-ended-code run that the original evaluator recorded as missing an answer.
ᵈThe superseded DeepSeek V4 Pro/Claude Code configuration accounted for 16 of the 24 additional accepted Galaxy answers; this row excludes that configuration.

**Table 2 | Task-level acceptance patterns and coverage across the 50 BixBench-50 tasks.**

| Task-level measure | Galaxy | Open-ended code |
|---|---|---|
| Tasks with at least one accepted answer | 47/50 | 48/50 |
| Tasks with all 15 runs accepted | 25/50 | 25/50 |
| Tasks with higher accuracy than the comparator environmentᵃ | 14/50 | 10/50 |
| Tasks tied between environmentsᵃ | 26/50 | 26/50 |

Each task contributed 15 runs per environment (five model configurations × three replicate-labelled runs). Coverage measures describe performance across configurations and replicates and do not estimate the probability that a single agent run will succeed. Tasks with unanimous Galaxy acceptance spanned phylogenetic treeness comparisons, filtered somatic-variant counts, colony morphology summaries, differential-expression counts and logistic-regression model assessment.
ᵃThe higher, lower and tied categories are mutually exclusive and sum to 50 tasks; the tied set (26 tasks) is shared by both environments.

**Table 3 | Replicate-level success distribution by execution environment and model configuration.**

| Environment | Model configuration | 3 of 3ᶜ | 2 of 3 | 1 of 3 | 0 of 3ᶜ | Accepted runs | ≥1 accepted (%)ᵃ | All three accepted (%) | Consistency index (%)ᵇ |
|---|---|---|---|---|---|---|---|---|---|
| Galaxy | GPT-5.5 | 44 | 1 | 0 | 5 | 134/150 | 90.0 | 88.0 | 97.8 |
| Galaxy | GPT-5.6 Sol | 43 | 2 | 0 | 5 | 133/150 | 90.0 | 86.0 | 95.6 |
| Galaxy | GPT-5.6 Luna | 40 | 4 | 1 | 5 | 129/150 | 90.0 | 80.0 | 88.9 |
| Galaxy | DeepSeek V4 Pro (Codex) | 38 | 2 | 5 | 5 | 123/150 | 90.0 | 76.0 | 84.4 |
| Galaxy | DeepSeek V4 Pro (Claude Code, superseded) | 32 | 11 | 2 | 5 | 120/150 | 90.0 | 64.0 | 71.1 |
| Galaxy | **All configurations** | **197** | **20** | **8** | **25** | **639/750** | **90.0** | **78.8** | **87.6** |
| Open-ended code | GPT-5.5 | 43 | 1 | 0 | 6 | 131/150 | 88.0 | 86.0 | 97.7 |
| Open-ended code | GPT-5.6 Sol | 41 | 3 | 1 | 5 | 130/150 | 90.0 | 82.0 | 91.1 |
| Open-ended code | GPT-5.6 Luna | 38 | 7 | 1 | 4 | 129/150 | 92.0 | 76.0 | 82.6 |
| Open-ended code | DeepSeek V4 Pro (Codex) | 37 | 4 | 2 | 7 | 121/150 | 86.0 | 74.0 | 86.0 |
| Open-ended code | DeepSeek V4 Pro (Claude Code, superseded) | 28 | 6 | 8 | 8 | 104/150 | 84.0 | 56.0 | 66.7 |
| Open-ended code | **All configurations** | **187** | **21** | **12** | **30** | **615/750** | **88.0** | **74.8** | **85.0** |

Counts are tasks classified by the number of accepted replicates (n = 50 tasks per configuration per environment; 250 analysis cells per environment). Accepted-run totals reconcile with Table 1 (3 × the 3-of-3 count, plus 2 × the 2-of-3 count, plus the 1-of-3 count). Percentages in the three right-hand columns are of 50 tasks except where stated.
ᵃEquivalently, 50 minus the 0-of-3 count. Every Galaxy configuration reached this figure on 45 of 50 tasks, but not on the same 45: three tasks were failed in all three replicates by every configuration and seven by at least one. In open-ended code, two tasks were failed by every configuration and twelve by at least one.
ᵇTasks with all three replicates accepted, as a percentage of tasks with at least one accepted replicate. The index separates reaching an accepted answer at all from reaching it in every replicate; it is undefined for a configuration with no accepted answers, which did not occur.
ᶜOutcomes were largely all-or-nothing: 222 of 250 Galaxy cells (88.8%) and 217 of 250 open-ended-code cells (86.8%) were either 3 of 3 or 0 of 3. Pairing environments within task and configuration, 198 of 250 pairs (79.2%) recorded the same number of accepted replicates, Galaxy was higher in 33 and open-ended code in 19, and 171 pairs were unanimous in both environments. These counts are descriptive; replicates are not documented as seed-matched, so a pair difference is not an estimate of a per-run treatment effect.

**Table 4 | Most frequently recorded Galaxy tools among retained creating jobs.**

| Recorded tool or operation | Jobs (n)ᵃ |
|---|---|
| Spreadsheet-to-tabular conversion | 644 |
| Column selection | 557 |
| Filtering | 397 |
| KEGG over-representation analysis | 269 |
| PhyKIT metrics | 202 |

Counts are of recorded creating jobs in the retrieved Galaxy history snapshots (Table 6) and refer to the specific recorded tool versions. They include data-preparation and conversion steps, have incomplete coverage and may reflect inherited or later history state. KEGG, Kyoto Encyclopedia of Genes and Genomes.
ᵃCounts describe observed operations, not independent analyses or benchmark-specific scientific attempts. No denominator for the tool-specific counts was specified in the source analysis; the retrieved corpus contained 5,042 distinct creating jobs (Table 6).

**Table 5 | Task-level case examples: accepted answers by environment and recorded Galaxy operations.**

| Task (analysis type) | Galaxy, accepted (n/15) | Open-ended code, accepted (n/15) | Recorded Galaxy operations or solution-path indicatorsᵃ |
|---|---|---|---|
| Treeness comparison (phylogenetics) | 15 | 15 | Differing recorded solution paths across runs |
| Somatic-variant filtering and counting | 15 | 15ᵇ | Variant filtering and counting |
| Colony morphology (circularity for the genotype with the largest mean colony area) | 15 | 15 | Grouping; Datamash |
| Differential expression (DESeq2, shrinkage, adjustment for sex) | 15 | 13 | DESeq2 |
| Logistic-regression model assessment (AIC) | 15 | 15 | Regression |
| Whole-genome coverage | 14 | 15 | BWA-MEM; samtools depth |
| RCV Mann–Whitney test | 0 | 8 | PhyKIT indicator shared by all runs; all 45 retrieved creating jobs in the `ok` state |
| Transition-to-transversion ratio | 0 | 0 | All 19 retrieved Galaxy creating jobs in the `ok` state |

Denominator is 15 runs per environment per task (five configurations × three replicate-labelled runs). Acceptance counts were taken from the `outcome.original_evaluator_score` field of the corresponding per-task evidence files. AIC, Akaike information criterion; RCV, relative composition variability.
ᵃOperational completion (`ok` job states) and tool-family agreement are distinct from answer acceptance. These examples do not resolve whether discrepancies arose from input selection, parameters, interpretation or evaluator behaviour.
ᵇTwo archived tasks match this description (median somatic CHIP variant count under a variant-allele-frequency filter, and the ClinVar-classified proportion of such variants); both recorded 15 accepted answers in each environment, so the value is unaffected by which task the case example refers to.

**Table 6 | Availability and recorded states of Galaxy execution records.**

| Evidence category | Measure | Value |
|---|---|---|
| Record availability | Galaxy runs linked to dataset-bearing history snapshots | 714/750 runs |
| | Distinct public histories represented | 711 |
| | Runs with history metadata only (collection limit exceeded)ᵃ | 32/750 runs |
| | Histories unavailable | 4 |
| Element states in collection-limited histories (n = 41,304 elements)ᵃ | `ok` | 40,722 |
| | `new` | 202 |
| | `failed_metadata` | 9 |
| | Not accounted for by state summaries | 371 |
| Creating-job states in detailed snapshots (n = 5,042 jobs)ᵇ | `ok` | 4,454 (88.3%) |
| | `error` | 552 (10.9%) |
| | `deleted` | 25 (0.5%) |
| | `paused` | 11 (0.2%) |
| Recovery and outcome indicators | Candidate failure-to-success sequencesᶜ | 93 across 49 Galaxy runs |
| | Collection-limited runs with accepted answers | 31/32 runs |
| | Collection-limited runs with structured execution requests | 30/32 runs |
| | Collection-limited runs requesting custom Galaxy tools | 17/32 runs |
| | Runs passing the evaluator's fresh-history recording checkᵈ | 0/750 runs |

ᵃHistories exceeding the collector's 300-item limit were retained as metadata only; their detailed contents were intentionally not retrieved. Element states describe dataset availability or processing status, not independent jobs or scientific correctness. A collection limit is not an indicator of analytical failure: 31 of these 32 runs had accepted answers.
ᵇPercentages are of the 5,042 distinct creating jobs; only the `error` percentage was reported in the source analysis and the remainder were derived. These records include preparation and conversion steps, have incomplete coverage and may contain inherited or later history state; they are not a complete inventory of benchmark-specific scientific attempts.
ᶜIdentified where a later successful job used the same tool and input dataset identifiers. Candidates were not independently adjudicated as successful scientific corrections and therefore constitute evidence for investigating recovery, not a demonstrated improvement in recovery relative to open-ended code.
ᵈThe original evaluator's fresh-history recording check was recorded as false for all 750 Galaxy runs despite the retrieved history evidence. This discrepancy is unreconciled and precludes assigning a count of exclusively Galaxy-derived solutions.

**Table 7 | Environment discordance in accepted answers, paired within task and model configuration.**

| Pairing level | Measure | Value |
|---|---|---|
| Task level (50 tasks; 15 runs per environment) | Tasks with accepted answers in Galaxy only (open-ended code 0/15) | 0 |
| | Tasks with accepted answers in open-ended code only (Galaxy 0/15) | 1ᵃ |
| | Tasks with no accepted answer in either environment | 2 |
| | Tasks differing by ≥5 of 15 runs between environments | 3 (2 favouring Galaxy, 1 favouring open-ended code) |
| Task × configuration level (250 pairs; 3 replicates per environment) | Pairs with all three accepted in Galaxy and none in open-ended code | 4 pairs, across 3 tasks |
| | Pairs with all three accepted in open-ended code and none in Galaxy | 2 pairs, both on 1 task |
| Reproducibility across the five configurations (50 tasks) | Tasks where ≥4 of 5 configurations favour Galaxy and none favour open-ended code | 2ᵇ |
| | Tasks where ≥4 of 5 configurations favour open-ended code and none favour Galaxy | 0 |
| | Tasks with configurations favouring both directionsᶜ | 6 |
| | Tasks tied across all five configurations | 22 |
| Answer convergence (50 tasks)ᵈ | Median distinct submitted answers per task, Galaxy / open-ended code | 2.0 / 2.0 |
| | Tasks with one distinct answer across all 15 runs, Galaxy / open-ended code | 18 / 18 |
| | Of the 18 unanimous Galaxy tasks: accepted throughout / rejected throughout / mixed | 15 / 2 / 1 |
| Evaluator behaviour (1,500 runs)ᵉ | Runs scored under the rounded-numeric verifier mode (accepted) | 11 (2 accepted) |
| | Acceptance under the four other recorded verifier modes | 81.8–87.4% |

Acceptance is the original evaluator's score, as in Table 1. Pairing is within task and configuration; "favouring" a environment means more of its three replicates were accepted. Counts were computed from the `outcome.original_evaluator_score` and `outcome.original_evaluator_mode` fields of all 1,500 run records in the 50 per-task evidence files.
ᵃThe RCV Mann–Whitney task (8 of 15 accepted open-ended-code answers against 0 of 15 in Galaxy; Table 5). All 15 Galaxy runs submitted the identical unaccepted p-value, as did five open-ended-code runs.
ᵇThe miRNA multiple-testing ratio task (15 of 15 against 6 of 15) and the gseapy odds-ratio task (11 of 15 against 2 of 15).
ᶜConfigurations disagreeing in direction within the same task indicate configuration-specific rather than environment-level differences.
ᵈSubmitted answers normalised to six significant figures before counting distinct values. Convergence of Galaxy answers is therefore not a general property of the environment, although it characterises the discordant tasks described in the text.
ᵉByte-identical submitted answers, verified by matching SHA-256 values, received different scores under different recorded verifier modes. The rounded-numeric mode was applied only to the two DeepSeek V4 Pro configurations, so it is a configuration-level confounder; the four other modes were distributed almost identically across environments (llm_verifier_auto_code 40%, range_verifier 26%, str_verifier_auto_numeric 19% and str_verifier 14% in each), which supports the environment comparison.

**Table 8 | Recorded solution-path indicators by model configuration and execution environment.**

| Environment | Model configuration | PhyKIT | Datamash | Summary Statistics | Newick or branch parsing | IQ-TREE report | Biopython | Unclassified solution pathᵃ |
|---|---|---|---|---|---|---|---|---|
| Galaxy | GPT-5.5 | 23 | 3 | 1 | 0 | 0 | 0 | 123 |
| Galaxy | GPT-5.6 Sol | 25 | 8 | 4 | 0 | 0 | 0 | 115 |
| Galaxy | GPT-5.6 Luna | 20 | 22 | 4 | 0 | 0 | 0 | 110 |
| Galaxy | DeepSeek V4 Pro (Codex) | 25 | 14 | 7 | 0 | 0 | 0 | 106 |
| Galaxy | DeepSeek V4 Pro (Claude Code, superseded) | 23 | 8 | 1 | 0 | 0 | 0 | 118 |
| Galaxy | **All configurations** | **116** | **55** | **17** | **0** | **0** | **0** | **572** |
| Open-ended code | GPT-5.5 | 16 | 0 | 0 | 13 | 1 | 1 | 125 |
| Open-ended code | GPT-5.6 Sol | 20 | 0 | 0 | 23 | 1 | 0 | 121 |
| Open-ended code | GPT-5.6 Luna | 18 | 0 | 0 | 18 | 6 | 0 | 122 |
| Open-ended code | DeepSeek V4 Pro (Codex) | 30 | 0 | 0 | 13 | 0 | 0 | 118 |
| Open-ended code | DeepSeek V4 Pro (Claude Code, superseded) | 16 | 0 | 0 | 13 | 7 | 2 | 124 |
| Open-ended code | **All configurations** | **100** | **0** | **0** | **80** | **15** | **3** | **610** |

Values are numbers of runs carrying each indicator, out of 150 runs per configuration per environment (750 runs per environment). Indicator labels are non-exclusive: of the 318 runs with a classified solution path, 253 carried one indicator, 62 carried two and three carried three. Labels describe recorded tool and command indicators rather than fully adjudicated scientific methods, and zeros are measured absences of the indicator in the retrieved records rather than missing data. Counts were aggregated from the `solution_solution path.classification` field of all 1,500 run records in the 50 per-task evidence files (`analysis/<task>/history_analysis_evidence.json`); the aggregation reproduces every previously reported value, including Galaxy PhyKIT (23, 25, 20, 25, 23), Galaxy Datamash (3, 8, 22, 14, 8), Galaxy Summary Statistics for the two DeepSeek configurations (7 and 1), the open-ended-code PhyKIT maximum (30 runs, DeepSeek V4 Pro/Codex), the open-ended-code Newick or branch parsing maximum (23 runs, GPT-5.6 Sol) and the unclassified totals in both environments.
ᵃSolution-path classification coverage was incomplete and the underlying labels differ by environment: in Galaxy, 572 of 750 runs (76.3%) carried no solution-path classification; in open-ended code, 610 of 750 runs (81.3%) were labelled 'local shell or script; method unclassified'. Open-ended-code records contained no null classifications, and Galaxy records contained no 'local shell or script' labels. In every cell, classified plus unclassified runs sum to 150. No independent task-difficulty strata were available, so solution consistency could not be compared across difficulty levels.

**Table 9 | Replicate-level agreement of recorded solution paths, by execution environment and model configuration.**

| Environment | Model configuration | Cells with identical solution paths | Two of three identical | All three distinct | Not evaluableᵃ | Identical (%)ᵇ | Mean pairwise Jaccardᵇ |
|---|---|---|---|---|---|---|---|
| Galaxy | GPT-5.5 | 6 | 6 | 38 | 0 | 12.0 | 0.260 |
| Galaxy | GPT-5.6 Sol | 12 | 10 | 28 | 0 | 24.0 | 0.453 |
| Galaxy | GPT-5.6 Luna | 6 | 8 | 32 | 4 | 13.0 | 0.402 |
| Galaxy | DeepSeek V4 Pro (Codex) | 12 | 11 | 25 | 2 | 25.0 | 0.541 |
| Galaxy | DeepSeek V4 Pro (Claude Code, superseded) | 8 | 14 | 28 | 0 | 16.0 | 0.432 |
| Galaxy | **All configurations** | **44** | **49** | **151** | **6** | **18.0** | **0.417** |
| Open-ended code | GPT-5.5 | 4 | 7 | 39 | 0 | 8.0 | 0.669 |
| Open-ended code | GPT-5.6 Sol | 4 | 13 | 33 | 0 | 8.0 | 0.695 |
| Open-ended code | GPT-5.6 Luna | 4 | 12 | 34 | 0 | 8.0 | 0.663 |
| Open-ended code | DeepSeek V4 Pro (Codex) | 1 | 8 | 41 | 0 | 2.0 | 0.581 |
| Open-ended code | DeepSeek V4 Pro (Claude Code, superseded) | 3 | 11 | 36 | 0 | 6.0 | 0.642 |
| Open-ended code | **All configurations** | **16** | **51** | **183** | **0** | **6.4** | **0.650** |

A analysis cell is one task, environment and model configuration together with its three replicate-labelled runs (50 tasks × 2 environments × 5 configurations = 500 cells, covering all 1,500 archived runs; 50 cells per configuration per environment). Solution-path fingerprints are auditor-derived: in Galaxy, the set of version-stripped Galaxy tool identifiers recorded on job events, excluding data-fetch jobs; in open-ended code, the set of analytical tool and library tokens matched by a fixed vocabulary against recorded command text. Counts and statistics are reproducible from the archived evidence with `solution_path_consistency_analysis.py`, which writes `solution_path_consistency_results.json`.
ᵃCells in which no run carried any fingerprint signal. These are reported separately rather than counted as agreement, and are excluded from the two right-hand columns.
ᵇAmong evaluable cells; Jaccard is the mean of the three pairwise replicate similarities, where 1 denotes identical fingerprints and 0 no shared element. Agreement magnitudes are not comparable between environments, because the fingerprints are extracted by different instruments and the two measures disagree in direction: Galaxy has the higher identical-path rate and open-ended code the higher mean Jaccard similarity. Comparisons between configurations within a environment use a single instrument.

**Table 10 | Factors examined as sources of replicate-level solution-path variability.**

| Factor examined | Measure | Galaxy | Open-ended code |
|---|---|---|---|
| Task identityᵃ | s.d. of per-task mean agreement (n = 50 tasks); range | 0.274; 0.00–0.93 | 0.088; 0.45–0.91 |
| Configuration identity | s.d. of per-configuration mean agreement (n = 5); range | 0.092; 0.26–0.54 | 0.038; 0.58–0.69 |
| Recorded workload | Spearman ρ with median events per run | +0.012 (244 cells) | −0.075 (250 cells) |
| Recorded analytical jobs | Spearman ρ with median Galaxy jobs per run | +0.110 (244 cells) | Not applicable |
| Fingerprint size | Spearman ρ with mean fingerprint size | −0.041 (244 cells) | +0.056 (250 cells) |
| Recorded job failureᵇ | Mean agreement, cells with ≥1 failed job | 0.281 (135 cells) | Not recorded |
| Recorded job failureᵇ | Mean agreement, cells with no failed job | 0.585 (109 cells) | Not recorded |
| Answer acceptanceᶜ | Mean agreement, all three replicates accepted | 0.385 (192 cells, 45 tasks) | 0.654 (187 cells, 44 tasks) |
| Answer acceptanceᶜ | Mean agreement, one or two accepted | 0.443 (28 cells, 22 tasks) | 0.625 (33 cells, 21 tasks) |
| Answer acceptanceᶜ | Mean agreement, none accepted | 0.638 (24 cells, 6 tasks) | 0.651 (30 cells, 12 tasks) |
| Answer acceptanceᶜ | Identical solution paths, none accepted (%) | 41.7 | 6.7 |
| Answer acceptanceᶜ | Identical solution paths, all three accepted (%) | 14.1 | 7.5 |

Agreement is the mean pairwise Jaccard similarity of the three replicate solution-path fingerprints within a cell, as defined in Table 9; higher values denote more similar recorded solution paths. All entries are auditor-derived and descriptive. Cells are not independent units: each task contributes up to five cells per environment, so cell counts overstate the number of independent observations. s.d., standard deviation.
ᵃTask-level variability did not transfer between environments: the rank correlation between a task's Galaxy agreement and its open-ended-code agreement was weak (Spearman ρ = 0.135, n = 50 tasks).
ᵇJob failure states are a Galaxy-specific measure; non-zero shell exits in open-ended code are not an equivalent quantity and were not counted here. The failure difference persists within each tertile of mean fingerprint size, comparing cells with and without a failed job: 0.171 against 0.649 for small, 0.321 against 0.570 for mid and 0.323 against 0.425 for large fingerprints.
ᶜThe Galaxy acceptance gradient likewise persists within each tertile of mean fingerprint size, comparing cells with all three replicates accepted against cells with none accepted: 0.400 against 0.667 for small, 0.402 against 0.691 for mid and 0.351 against 0.487 for large fingerprints. It is therefore not explained by toolset size; the 24 Galaxy cells with no accepted answer nevertheless derive from only six distinct tasks. No independent task-difficulty stratification was available, so difficulty cannot be separated from any of these associations, and none of them establishes a causal mechanism.

**Table 11 | Input-token ratios between environments and answer acceptance, by model configuration.**

| Model configuration | Comparisons (n)ᵃ | Median input-token ratio (Galaxy:open-ended code)ᵇ | Galaxy accuracy (%)ᶜ | Open-ended code accuracy (%)ᶜ |
|---|---|---|---|---|
| GPT-5.5 | 50 | 3.86 | 89.3 | 87.3 |
| GPT-5.6 Sol | 50 | 5.03 | 88.7 | 86.7 |
| GPT-5.6 Luna | 50 | 7.63 | 86.0 | 86.0 |
| DeepSeek V4 Pro (Codex) | 50 | 4.50 | 82.0 | 80.7 |
| DeepSeek V4 Pro (Claude Code, superseded) | 50 | 2.97 | 80.0 | 69.3 |
| **All configurations** | **250** | **4.74 (IQR 2.45–9.62; range 0.265–56.94)** | **85.2** | **82.0** |

Provider-reported input totals include cached input, which was not counted a second time, and exclude output tokens. Differences in cache use, output generation, pricing and execution infrastructure would need to be incorporated before translating these ratios into monetary or total computational cost. IQR, interquartile range.
ᵃEach comparison is one task × one configuration: the median input-token total of three Galaxy runs divided by the median of three open-ended-code runs (50 tasks × 5 configurations = 250 comparisons). Per-configuration counts were derived as 250/5.
ᵇThe pooled median ratio of 4.74 corresponds to a 374% increase. It describes a typical within-task, within-configuration relative increase and is neither the ratio of pooled token totals nor a comparison of seed-matched replicates. The range indicates that higher Galaxy consumption was not universal.
ᶜAccuracy values are reproduced from Table 1 to permit comparison; relative token use did not track answer acceptance monotonically, and no independent model-capability ranking was evaluated.

<!-- Evidence provenance for manuscript preparation: BixBench_50/bixBench50_overview_audit.json; BixBench_50/bixBench50_recovery_summary.json; the 50 analysis/<task>/history_analysis.md reports and their archived evidence. Tables 7-10 were recomputed from the 1,500 run records in the 50 analysis/<task>/history_analysis_evidence.json files; the replicate-level solution-path analysis in Tables 9 and 10 is reproducible with BixBench_50/solution_path_consistency_analysis.py, which writes BixBench_50/solution_path_consistency_results.json. No new agent runs, detailed history retrievals or answer regrading were performed for this section. -->
