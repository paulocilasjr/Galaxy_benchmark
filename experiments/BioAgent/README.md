# BioAgent Experiments

This directory contains a faithful import of the BioAgent Bench task set into this repository as a separate group.

Design rules used for this import:

- prompts are copied from the BioAgent Bench task metadata
- the only prompt change is an added sentence requiring execution in the Galaxy environment
- task comparison rules are taken from the BioAgent evaluator implementation and paper-aligned task descriptions
- raw inputs are downloaded into `dataset/bioagent_inputs/` using the published BioAgent metadata URLs

This group is kept separate from the native Galaxy Benchmark experiments because the source tasks were not originally authored in this repository's prompt-tier contract.
