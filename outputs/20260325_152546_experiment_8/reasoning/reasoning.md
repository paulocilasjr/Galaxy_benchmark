## 2026-03-25T15:27:12Z | failure_signature
- Decision made: Treat the previous BUSCO failure as a server-side auto-lineage dataset mismatch rather than a local input-mapping error.
- Why this decision was made: Attempt 1 failed at BUSCO job bbd44e69cb8906b54787b4fe4bf5e36e because usegalaxy.org tried to run offline against `eukaryota_odb10`, but the live lineage selector now advertises `_odb12` bundles. That makes the failure signature specific to auto-lineage on this server version, not to the genome FASTA or BUSCO tool submission itself.
- Next action: Probe the live BUSCO lineage selector and switch to an explicit lineage for the retry attempt.

## 2026-03-25T15:27:12Z | discovery_strategy
- Decision made: Use direct BioBlend tool execution on usegalaxy.org rather than a published workflow.
- Why this decision was made: The input filenames exactly match the GTN Maker short tutorial dataset bundle. A published Helix workflow is available on usegalaxy.org, but it would ignore the provided transcript, protein, SNAP, and Augustus inputs, so the direct Maker-centered execution is the narrower fit to the benchmark prompt.
- Next action: Recreate the tutorial/tool discovery evidence and then run the tutorial-aligned tool chain.

## 2026-03-25T15:27:12Z | tool_selection
- Decision made: Adopt the GTN short tutorial tool sequence: Fasta Statistics, BUSCO, Maker, Genome annotation statistics, GFFRead, BUSCO, Map annotation ids, and JBrowse.
- Why this decision was made: The GTN tutorial content explicitly states the objectives 'Annotate genome with Maker', 'Evaluate annotation quality with BUSCO', and 'View annotations in JBrowse'. The current usegalaxy.org tool inventory still exposes the same tool family with updated versions.
- Next action: Validate credentials, create a new history, and upload all five experiment inputs.

## 2026-03-25T15:27:16Z | version_mapping
- Decision made: Use current installed tool versions while preserving the tutorial's functional mapping.
- Why this decision was made: The tutorial references older tool versions, but usegalaxy.org currently exposes Maker 2.31.11+galaxy2, BUSCO 5.8.0+galaxy2, GFFRead 2.2.1.4+galaxy0, JBrowse 1.16.11+galaxy1, Genome annotation statistics 0.8.4, Map annotation ids 2.31.11, and Fasta Statistics 2.0. Those are the exact runnable versions on the credentialed server.
- Next action: Create a fresh history and upload the local datasets.

## 2026-03-25T15:36:04Z | busco_lineage_mapping
- Decision made: Use explicit BUSCO lineage `ascomycota_odb12` for both the genome and transcript BUSCO runs.
- Why this decision was made: The live BUSCO build payload for this history exposes 495 lineage options, including ['ascomycota_odb12', 'fungi_odb12', 'eukaryota_odb12']. No Schizosaccharomyces-specific lineage was exposed, so `ascomycota_odb12` is the most specific lineage available on the server that still fits Schizosaccharomyces pombe as an ascomycete.
- Next action: Run the pre-annotation QC steps before Maker with the explicit lineage fix in place.

