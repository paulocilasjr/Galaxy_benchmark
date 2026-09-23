# Run trace

## Inputs

- Forward: `data/inputs/raw_reads/pair/forward/forward.fastqsanger.gz`
- Reverse: `data/inputs/raw_reads/pair/reverse/reverse.fastqsanger.gz`
- Paired records before processing: 377,961

## Method

- Tool: fastp 1.3.6
- Adapter removal: paired-end mate-overlap analysis only. No adapter sequence was
  supplied and paired-end adapter-sequence auto-detection was not enabled.
- Quality threshold: Phred 20
- Unqualified-base limit: 40%
- N-base limit: 5
- Minimum retained length: 15 bp after adapter trimming
- Other trimming/base correction disabled, including polyG/polyX trimming.

## Results

- Retained pairs: 277,113
- Forward retained reads: 277,113
- Reverse retained reads: 277,113
- Verified mate IDs are synchronized in order.
- Verified no retained read exceeds the quality, N, or minimum-length limits.

## Outputs

- `final_answer/trimmed_forward.fastqsanger.gz`
- `final_answer/trimmed_reverse.fastqsanger.gz`
