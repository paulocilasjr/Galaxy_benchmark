## 2026-03-25T18:49:32Z | failure_signature
- Decision made: Treat the latest blocker as scheduler delay on transcript BUSCO rather than as a failure of the core annotation pipeline.
- Why this decision was made: Attempt 3 had already completed annotation statistics and GFFRead in history `experiment_8_20260325_152546`, but transcript BUSCO job `bbd44e69cb8906b5566147c35dd8dedf` remained queued through repeated polls and direct job inspection showed no runner assignment or error details. Genome BUSCO, annotation statistics, Maker, and GFFRead had all completed successfully.
- Next action: Resume from the completed history and finish the result-producing steps that do not depend on the queued transcript BUSCO job.

## 2026-03-25T18:49:32Z | resume_strategy
- Decision made: Resume from the successful attempt-3 Galaxy history state rather than starting a new history.
- Why this decision was made: The resumed history already contains successful upstream outputs through GFFRead, so repeating those long-running steps would add latency without changing the answer. The remaining benchmark outputs depend on the Maker annotation, genome BUSCO, and JBrowse rather than on a second BUSCO run that has not been scheduled yet.
- Next action: Verify the resumed datasets and then continue with Map annotation ids and JBrowse.

## 2026-03-25T18:49:32Z | tool_selection
- Decision made: Adopt the GTN short tutorial tool sequence: Fasta Statistics, BUSCO, Maker, Genome annotation statistics, GFFRead, BUSCO, Map annotation ids, and JBrowse.
- Why this decision was made: The GTN tutorial content explicitly states the objectives 'Annotate genome with Maker', 'Evaluate annotation quality with BUSCO', and 'View annotations in JBrowse'. The current usegalaxy.org tool inventory still exposes the same tool family with updated versions.
- Next action: Validate credentials, create a new history, and upload all five experiment inputs.

## 2026-03-25T18:49:34Z | version_mapping
- Decision made: Use current installed tool versions while preserving the tutorial's functional mapping.
- Why this decision was made: The tutorial references older tool versions, but usegalaxy.org currently exposes Maker 2.31.11+galaxy2, BUSCO 5.8.0+galaxy2, GFFRead 2.2.1.4+galaxy0, JBrowse 1.16.11+galaxy1, Genome annotation statistics 0.8.4, Map annotation ids 2.31.11, and Fasta Statistics 2.0. Those are the exact runnable versions on the credentialed server.
- Next action: Create a fresh history and upload the local datasets.

## 2026-03-25T18:49:36Z | busco_lineage_mapping
- Decision made: Use explicit BUSCO lineage `ascomycota_odb12` for both the genome and transcript BUSCO runs.
- Why this decision was made: Attempt 2 already probed the live BUSCO selector and recorded the available lineage candidates in `/Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_152546_experiment_8/results/busco_lineage_probe.json`. That probe chose `ascomycota_odb12`, which was then validated by a successful genome BUSCO execution in the resumed history, so the transcript BUSCO run should reuse the same lineage for consistency.
- Next action: Continue from the resumed Maker output into the downstream analysis steps.

## 2026-03-25T18:49:36Z | maker_parameters
- Decision made: Reuse the existing Maker output instead of resubmitting Maker.
- Why this decision was made: The resumed history still contains the successful Maker final annotation dataset in `ok` state, and attempt 3 already showed that annotation statistics and GFFRead also complete correctly from that GFF. Reusing those outputs avoids another long-running Maker submission while preserving the validated parameterization.
- Next action: Inspect transcript BUSCO status and then continue with ID mapping plus JBrowse.

## 2026-03-25T18:49:36Z | transcript_busco_status
- Decision made: Treat transcript BUSCO state `queued` as non-blocking for experiment completion.
- Why this decision was made: The experiment outputs only require the evaluation tool name and the visualization tool name. BUSCO already completed successfully on the genome, genome annotation statistics completed successfully, and the remaining visualization steps depend only on the Maker annotation. Waiting indefinitely for the second BUSCO scheduler slot would not change those answers.
- Next action: Finish the remaining Map annotation ids and JBrowse steps and then write the benchmark result.

## 2026-03-25T18:52:55Z | result_interpretation
- Decision made: Represent `total_tools` using the completed executions and explicitly note the queued transcript BUSCO job.
- Why this decision was made: The core benchmark outputs were completed with genome BUSCO, Genome annotation statistics, Maker, Map annotation ids, and JBrowse, but the transcript BUSCO job never left Galaxy's scheduler queue during the final recovery window. The result therefore counts completed tool executions and documents the queued extra BUSCO attempt explicitly.
- Next action: Write result.json and only then read the ground truth file.

