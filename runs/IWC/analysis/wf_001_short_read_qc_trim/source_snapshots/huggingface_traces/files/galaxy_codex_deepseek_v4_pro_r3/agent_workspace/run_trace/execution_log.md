# Execution log

## Task
Paired-end quality control and trimming of `Raw reads` (list:paired).

## Galaxy history
- Assigned history: `bbd44e69cb8906b5a89756046ae6b99f`
- Input collection: `Raw reads` (`f521464397c694a8`, list:paired)
- The fastp wrapper requires a direct `paired` collection, so a paired
  collection named `Raw reads paired` (`09375be7e727c039`) was created from
  the same forward/reverse datasets in the assigned history.

## Tool and parameters
- Tool: fastp `1.3.6+galaxy0`
- Adapter trimming: enabled; no adapter sequence supplied;
  `--detect_adapter_for_pe` enabled (mate-overlap analysis only)
- Quality filter:
  - qualified quality phred: 20
  - unqualified percent limit: 40
  - N base limit: 5
  - length required: 15
- Disabled unrelated processing: polyG tail trimming, polyX tail trimming,
  cut-by-quality front/tail/right, base correction, low-complexity filter,
  duplicate analysis, overrepresentation analysis

## Result
- Forward output dataset: `f9cad7b01a472135fd9925511efc06c6`
- Reverse output dataset: `f9cad7b01a472135007c3b16acc7079b`
- Exported:
  - `final_answer/trimmed_forward.fastqsanger.gz`
  - `final_answer/trimmed_reverse.fastqsanger.gz`

## Validation
- gzip integrity: OK
- Retained read pairs: 276,615 in each mate
- Read ID order synchronized between mates: OK
- Minimum retained read length: 31 bp forward, 21 bp reverse
- Maximum ambiguous N bases per retained read: 5
- Maximum low-quality base fraction per retained read: 0.40
