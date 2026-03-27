## 2026-03-25T18:24:04Z | failure_signature
- Decision made: Treat the latest failure as a local network interruption during polling rather than a Galaxy tool failure.
- Why this decision was made: Attempt 2 had already completed uploads, Fasta Statistics, explicit-lineage BUSCO, and Maker in history `experiment_8_20260325_152546`, but the local runner terminated with a `bioblend.ConnectionError` caused by DNS resolution failure against `usegalaxy.org` while polling the Maker job. A direct recovery query showed that the Maker job and its outputs were already `ok` remotely.
- Next action: Resume from the completed remote history instead of re-running the upstream steps.

## 2026-03-25T18:24:04Z | resume_strategy
- Decision made: Resume from the successful attempt-2 Galaxy history rather than starting a new history.
- Why this decision was made: The recovery query confirmed that the remote history already contains successful upstream outputs through Maker, so repeating those long-running steps would add latency without improving correctness. Resuming from the same history preserves the exact successful upstream state that the downstream tools should consume.
- Next action: Verify the resumed datasets and then continue with the downstream annotation-analysis steps.

## 2026-03-25T18:24:04Z | tool_selection
- Decision made: Adopt the GTN short tutorial tool sequence: Fasta Statistics, BUSCO, Maker, Genome annotation statistics, GFFRead, BUSCO, Map annotation ids, and JBrowse.
- Why this decision was made: The GTN tutorial content explicitly states the objectives 'Annotate genome with Maker', 'Evaluate annotation quality with BUSCO', and 'View annotations in JBrowse'. The current usegalaxy.org tool inventory still exposes the same tool family with updated versions.
- Next action: Validate credentials, create a new history, and upload all five experiment inputs.

## 2026-03-25T18:24:06Z | version_mapping
- Decision made: Use current installed tool versions while preserving the tutorial's functional mapping.
- Why this decision was made: The tutorial references older tool versions, but usegalaxy.org currently exposes Maker 2.31.11+galaxy2, BUSCO 5.8.0+galaxy2, GFFRead 2.2.1.4+galaxy0, JBrowse 1.16.11+galaxy1, Genome annotation statistics 0.8.4, Map annotation ids 2.31.11, and Fasta Statistics 2.0. Those are the exact runnable versions on the credentialed server.
- Next action: Create a fresh history and upload the local datasets.

## 2026-03-25T18:24:07Z | busco_lineage_mapping
- Decision made: Use explicit BUSCO lineage `ascomycota_odb12` for both the genome and transcript BUSCO runs.
- Why this decision was made: Attempt 2 already probed the live BUSCO selector and recorded the available lineage candidates in `/Users/4475918/Projects/Galaxy_benchmark/outputs/20260325_152546_experiment_8/results/busco_lineage_probe.json`. That probe chose `ascomycota_odb12`, which was then validated by a successful genome BUSCO execution in the resumed history, so the transcript BUSCO run should reuse the same lineage for consistency.
- Next action: Continue from the resumed Maker output into the downstream analysis steps.

## 2026-03-25T18:24:07Z | maker_parameters
- Decision made: Reuse the existing Maker output instead of resubmitting Maker.
- Why this decision was made: Attempt 2 already submitted Maker with the correct GTN-aligned transcript, protein, Augustus, SNAP, and repeat-masking parameters, and the recovered remote history shows the final annotation dataset in `ok` state. Reusing that exact successful GFF avoids another long-running Maker submission while preserving the validated parameterization.
- Next action: Evaluate the resumed annotation before extracting transcript sequences.

