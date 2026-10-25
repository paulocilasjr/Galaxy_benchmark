# Figure 5 | Galaxy records analyses as structured provenance and uses more input tokens on question-answering tasks

This figure asks what running analyses through Galaxy costs in model tokens relative to custom code, where the extra input comes from, whether interface changes reduce it, and what Galaxy's retained record gives a reviewer in return. The answer matters because the case for Galaxy rests on auditability, and that benefit has to be weighed against the extra context the interface consumes.

## Fig. 5a | Does Galaxy use more tokens than custom code on each benchmark, and do incorrect runs use more input than correct ones?
panel: fig5a

### Rationale
- **Data.** Scored primary runs of four model configurations (three per task and condition), with per-run token counts from the agent traces, paired into task–model cells: 200 on BixBench-Verified-50, 400 on CompBioBench and 40 on IWC (10 tasks, including host-read removal). Below, replicate sets (three runs of one task, model and condition) with both outcomes under the results-site grades: 94 custom-code and 77 Galaxy sets, models and benchmarks pooled.
- **Variables.** Galaxy / custom-code ratios of input tokens (including cached context), uncached input (input minus cached) and output tokens. Below, input tokens of incorrect relative to correct runs; a run is correct when accepted or, for IWC, at ≥ 0.99 output agreement.
- **Analysis.** Primary: geometric mean over cells of the ratio of median tokens per run; aggregate: ratio of total tokens over the same cells; below, geometric mean over sets of median incorrect / median correct input. Intervals: 95% percentile cluster-bootstrap (20,000 resamples; clusters are BixBench source capsules, otherwise tasks). Holm-adjusted *P* values from paired cluster sign-flip tests (200,000 draws; exact for IWC) are in Source Data.
- **Reading the plot.** Log x-axis; 1 means equal use. Filled diamonds, primary estimates (printed at right, input in bold); open circles, aggregate; below, colour marks the condition.

### Conclusion
On the question-answering benchmarks, Galaxy used clearly more tokens. Input was 5.2× (95% interval 3.9–6.8) on BixBench-Verified-50 and 4.2× (3.5–5.1) on CompBioBench, with uncached input at 2.9× and 3.0× and output at 2.3× and 2.1× (all *P* < 0.001). Aggregate input ratios were lower (4.3× and 2.6×). On IWC, Galaxy did not use clearly more input (1.8×, 0.9–3.4; aggregate 0.89×); uncached input was higher (1.7×, 1.2–2.4), although its Holm-adjusted *P* was 0.08. Incorrect runs used about as much input as correct runs of the same task and model (1.12× in custom code, 0.89–1.39; 1.10× in Galaxy, 0.80–1.54). Token ratios are not monetary costs.

## Fig. 5b | Does Galaxy's extra input come from more actions or from more input per action, and what does Galaxy return to the agent?
panel: fig5b

### Rationale
- **Data.** Left, the task–model cells of panel a (200, 400 and 40), with each run's action count from the archive's per-run action table. Right, characters returned by Galaxy interface calls in 1,908 traced Galaxy runs. The notes use the inspected-tool records (1,942, 6,357 and 788 inspected tools by benchmark) and per-run cached-token counts.
- **Variables.** Actions are the agent's tool calls: shell commands, Galaxy interface calls, web searches or fetches, and file reads, writes and edits. Tokens per action is input tokens (including cached context) divided by actions. Bars give each request type's share of all characters Galaxy returned in a benchmark.
- **Analysis.** Left, the primary estimator of panel a, with 95% cluster-bootstrap intervals; sign-flip *P* values and a correct-runs-only sensitivity analysis are in Source Data. Right and notes, descriptive only.
- **Reading the plot.** Left, diamonds on a log axis, where 1 means equal. Right, stacked bars sum to 100% per benchmark; blue marks finding tools, and segments under 9% are unlabelled.

### Conclusion
On the question-answering benchmarks, Galaxy's extra input reflects both more actions (2.8×, 95% interval 2.4–3.4, on BixBench-Verified-50; 2.3×, 2.1–2.6, on CompBioBench) and more input per action (1.9×, 1.6–2.1; 1.8×, 1.7–2.0). On IWC neither ratio is clearly above 1 (1.4×, 0.96–2.05; 1.2×, 0.86–1.68). Finding tools produced the largest share of returned characters in every benchmark (42–69%), and 45–53% of inspected tools were not executed in the same run. The median cached share was 96% in Galaxy and 93–96% in custom code, so most input is earlier context reread. The split is not causal: because context accumulates, more actions also raise input per action.

## Fig. 5c | Can changes to the Galaxy interface reduce Galaxy's token use relative to custom code?
panel: fig5c

### Rationale
- **Data.** Complete 50-task BixBench-Verified-50 runs from the token_improvment records. July (GPT-5.5): the July 6 batch with round 1 in place against the archived runs made after round 2, 150 runs per condition in each, both conditions rerun. October (GPT-5.6 Sol): the archived Galaxy runs, one intermediate replicate after round 3 (batch summary totals only), and 150 new Galaxy runs after round 3 plus longer waits, all against the same archived custom-code runs. Correctness follows the results site (for the July 6 batch, its July page).
- **Variables.** Tokens are input (including cached context) plus output, summed over the 50 tasks and averaged over replicates. The columns give Galaxy and custom-code millions of tokens per 50-task run, the Galaxy change from the first to the last stage, and the share of Galaxy runs correct.
- **Analysis.** Ratio of tokens per 50-task run, with 95% cluster-bootstrap intervals over source capsules (20,000 resamples); the Galaxy change is paired by task and uses the same bootstrap. The one-replicate stage has no interval, and no tests were run.
- **Reading the plot.** Log x-axis. Filled diamonds, three replicates with intervals; open diamond, one replicate. Grey lines join the stages of each comparison; bold values mark each comparison's last stage.

### Conclusion
In both comparisons, Galaxy token use fell by more than half. In July, the ratio fell from 5.48× (95% interval 4.17–7.26) to 2.81× (2.11–3.80), and Galaxy tokens fell 55% (95% interval 45–63%). In October, it fell from 3.45× (1.65–7.15) through 2.42× (one replicate) to 1.53× (0.77–3.01), and Galaxy tokens fell 56% (46–63%). Galaxy correctness stayed at 91–93% (custom code, 89–90%). These are batch comparisons: several changes were bundled, the October agent CLI version also changed (0.146.0 to 0.156.0) and its custom-code baseline was not rerun. The panel does not estimate the effect of any single change.

## Fig. 5d | What does the retained record hold for each analysis step in each condition?
panel: fig5d

### Rationale
- **Data.** Per-task evidence files for all primary runs: 21,918 Galaxy jobs and 56,404 custom-code shell commands labelled as analysis. The whole-analysis row covers 1,920 runs per condition. Nothing was rerun.
- **Variables.** Each step's record of six elements (software and version, parameters, input data, output data, execution status, command or code) is classed as structured record, free text in the retained trace, partial (environment image or history metadata only), or not retained (unknown, not absent). A run's whole analysis counts as structured when its Galaxy history was retrieved.
- **Analysis.** Descriptive only: percentages of steps (or runs) per class, assigned by fixed rules. Galaxy elements are structured when the job record holds the field, and UDT software only with a versioned container. Custom-code parameters, inputs and commands count as free text, exit codes as structured, versions as free text when any command in the run printed one, and output files as not retained.
- **Reading the plot.** Each bar sums to 100%. Dark, structured; mid-grey, free text; light grey, partial; hatched, not retained. Segments under 12% are unlabelled.

### Conclusion
Galaxy kept a structured record of each element for 94–100% of jobs (software and version 96%, input data 95%, command 94%), and 98% of Galaxy runs had a retrieved history. Custom-code steps kept parameters, inputs and code as free text in the trace (100%) and software versions as free text in 71%. Exit codes were structured, but output files and the whole analysis were not retained. The panel compares what the benchmark retained, not what custom code could record, and it does not test reproducibility.

## Fig. 5e | How does the same analysis step appear in the custom-code trace and in the Galaxy job record?
panel: fig5e

### Rationale
- **Data.** One BixBench-Verified-50 task, bix-45-q1 (PhyKIT relative composition variability), with GPT-5.6 Sol replicate 1 in each condition; this is the case in Fig. 2d. Entries come from the task's retained evidence file: the PhyKIT Galaxy job, and the custom-code run's shell commands labelled as analysis. Outcomes come from the graded runs.
- **Variables.** Five rows: software and version, parameters, inputs and outputs, status, and the graded answer. Galaxy entries are job-record fields (tool ID, parameter fields, dataset IDs, job state, exit code). Custom-code entries are what the command text and exit codes show.
- **Analysis.** Descriptive single case; no statistics. The script reads each entry from the evidence and stops if key facts change (the pinned PhyKIT version, its loading through PYTHONPATH, no retained custom-code outputs).
- **Reading the plot.** Read across a row to compare the two records. The orange column is the custom-code trace; the blue column is the Galaxy job record.

### Conclusion
The Galaxy job record held the wrapper and its version (phykit_metrics 0.2.0+galaxy0), three parameter fields, links to 1 input and 3 output datasets, and the job state as queryable fields. The custom-code trace held the same facts only inside command text, and its output files were not retained. Only the custom-code trace recorded the PhyKIT library version (2.0.3, loaded through PYTHONPATH); the Galaxy job record does not hold it. The Galaxy answer was rejected because the reference encodes the older PhyKIT value. This is one illustrative case, and neither record was rerun.

# Extended Data Fig. 5 | Token use by model, outcome and action count

This figure breaks the pooled token comparisons of Fig. 5a down by model configuration and outcome, and shows how input tokens grow with the number of actions. It asks whether the token gap holds for each model, and whether token use tracks score or correctness.

## Extended Data Fig. 5a | Does higher input-token use go with higher scores across model configurations and conditions?
panel: ed5a

### Rationale
- **Data.** Scored primary runs with a token count, grouped by benchmark, model configuration and condition. The 24 groups hold 150 runs each on BixBench-Verified-50, 290–300 on CompBioBench and 30 on IWC (10 tasks, including host-read removal). BixBench-Verified-50 scores use the results-site grades, including the regrades of bix-53-q2 and bix-43-q2.
- **Variables.** x, median input tokens per run, including cached context (millions). y, mean score in percent; for IWC, mean output agreement × 100. Colour marks the model; squares are custom code, circles Galaxy.
- **Analysis.** 95% cluster-bootstrap intervals (2,000 resamples; clusters are BixBench source capsules, otherwise tasks) for both the mean score and the median tokens. Descriptive only; no tests.
- **Reading the plot.** Log x-axis. Horizontal bars are token intervals and vertical bars score intervals. Compare a model's square and circle for the condition gap, and compare colours for model differences.

### Conclusion
In all 12 model–benchmark pairs, Galaxy's median input exceeded custom code's; for example, 1.19M against 0.32M for GPT-5.5 on BixBench-Verified-50, and 3.75M against 0.53M for GPT-5.6 Sol on CompBioBench. On those two benchmarks, each model's scores in the two conditions differed by at most 2 points. Higher token use did not go with higher scores across models: GPT-5.6 Luna in Galaxy used the most input on both (5.0M and 10.1M) and scored 87% and 85%. Scores here include only runs with a token count.

## Extended Data Fig. 5b | Do incorrect runs use more input tokens than correct runs, model by model?
panel: ed5b

### Rationale
- **Data.** The 3,826 scored primary runs with a token count, split by condition, model configuration and outcome, and pooled over benchmarks. The ratios use replicate sets with both outcomes: 13–32 per model and condition. Outcomes use the results-site grades; the bix-43-q2 regrade adds two sets and changes which runs are correct in two others.
- **Variables.** Input tokens per run, including cached context (millions). Light boxes are correct runs and solid boxes incorrect runs; a run is correct when accepted or, for IWC, at ≥ 0.99 output agreement. The number above each pair is the incorrect / correct ratio.
- **Analysis.** Ratios are geometric means over sets of median incorrect / median correct input, the lower plot of Fig. 5a split by model. Intervals are 95% cluster-bootstrap intervals; sign-flip *P* values, Holm-adjusted over the eight tests, are in Source Data. Boxes are descriptive.
- **Reading the plot.** Log y-axis. Boxes show the middle 50% and the median, whiskers reach 1.5 times the interquartile range, and grey dots are runs. Orange is custom code; blue is Galaxy.

### Conclusion
No model shows a clear difference. Within replicate sets, incorrect / correct ratios ranged from 0.98× to 1.35× in custom code and from 0.84× to 1.31× in Galaxy. Every 95% interval includes 1, though only just for GPT-5.6 Luna in custom code (1.35×, 0.998–1.85), and every Holm-adjusted *P* is at least 0.61. The pooled boxes place incorrect runs higher in all eight groups, but they mix tasks; the within-set ratios hold task and model fixed and are the fairer comparison.

## Extended Data Fig. 5c | How does a run's input-token use scale with its number of actions?
panel: ed5c

### Rationale
- **Data.** The 3,825 scored primary runs of panel b that have at least one recorded action, one point per run, with benchmarks and models pooled. Token counts come from the agent traces and action counts from the archive's per-run action table, as in Fig. 5b.
- **Variables.** x, actions per run: the agent's tool calls (shell commands, Galaxy interface calls, web searches or fetches, file operations). y, input tokens per run, including cached context (millions). Orange squares are custom code; blue circles are Galaxy.
- **Analysis.** Descriptive only; no fitted line, correlation or test. The panel shows the shape of the association, not a model of it.
- **Reading the plot.** Both axes are log scale, so equal distances are equal fold changes. Points are semi-transparent, so dense regions look darker.

### Conclusion
Input tokens rise steeply with actions in both conditions, and the two conditions fall along one shared band. Custom-code runs dominate the low-action end, and Galaxy runs extend further towards high action counts. This matches Fig. 5b, where more actions account for much of Galaxy's extra input. Each later call carries the retained context, so cumulative input grows with actions by construction. The association is therefore not a decomposition of cost.
