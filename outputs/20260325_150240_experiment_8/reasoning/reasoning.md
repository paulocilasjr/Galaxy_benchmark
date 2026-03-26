## 2026-03-25T15:07:55Z | discovery_strategy
- Decision made: Use direct BioBlend tool execution on usegalaxy.org rather than a published workflow.
- Why this decision was made: The input filenames exactly match the GTN Maker short tutorial dataset bundle. A published Helix workflow is available on usegalaxy.org, but it would ignore the provided transcript, protein, SNAP, and Augustus inputs, so the direct Maker-centered execution is the narrower fit to the benchmark prompt.
- Next action: Recreate the tutorial/tool discovery evidence and then run the tutorial-aligned tool chain.

## 2026-03-25T15:07:55Z | tool_selection
- Decision made: Adopt the GTN short tutorial tool sequence: Fasta Statistics, BUSCO, Maker, Genome annotation statistics, GFFRead, BUSCO, Map annotation ids, and JBrowse.
- Why this decision was made: The GTN tutorial content explicitly states the objectives 'Annotate genome with Maker', 'Evaluate annotation quality with BUSCO', and 'View annotations in JBrowse'. The current usegalaxy.org tool inventory still exposes the same tool family with updated versions.
- Next action: Validate credentials, create a new history, and upload all five experiment inputs.

## 2026-03-25T15:08:07Z | version_mapping
- Decision made: Use current installed tool versions while preserving the tutorial's functional mapping.
- Why this decision was made: The tutorial references older tool versions, but usegalaxy.org currently exposes Maker 2.31.11+galaxy2, BUSCO 5.8.0+galaxy2, GFFRead 2.2.1.4+galaxy0, JBrowse 1.16.11+galaxy1, Genome annotation statistics 0.8.4, Map annotation ids 2.31.11, and Fasta Statistics 2.0. Those are the exact runnable versions on the credentialed server.
- Next action: Create a fresh history and upload the local datasets.

## 2026-03-25T15:08:07Z | busco_lineage_mapping
- Decision made: Use BUSCO auto-lineage restricted to eukaryotes instead of the tutorial's older static Fungi selector.
- Why this decision was made: The current BUSCO 5.8.0 tool on usegalaxy.org exposes stable auto-lineage options directly and the lineage selector is dynamic. Auto-detecting within eukaryotes preserves the tutorial intent for Schizosaccharomyces while avoiding brittle server-specific lineage dataset tokens.
- Next action: Run the pre-annotation QC steps before Maker.

## 2026-03-25T15:21:43Z | run_failure
- Decision made: Stop the run after a terminal failure: Run BUSCO on genome failed with terminal job state error.
- Why this decision was made: Benchmark policy requires concrete failure evidence to be captured before any retry. The current attempt remains immutable; any retry must happen in a new run directory with a signature-specific fix strategy.
- Next action: Inspect the recorded error context and decide whether a new attempt is justified.

