# Execution log

## Inputs
- Assigned Galaxy history: `bbd44e69cb8906b59e58e5c004a6d3b9`
- Raw input collection: `f92754240e629818` (`list:paired`, element `pair`)
- Forward dataset: `f9cad7b01a4721359e5bcb65ec705d2b`
- Reverse dataset: `f9cad7b01a4721356179c236b338b16c`

## Preparation
- The assigned input is a `list:paired` collection. The fastp wrapper expects a
  single `paired` collection, so the existing forward/reverse datasets were
  zipped with the Galaxy `__ZIP_COLLECTION__` tool.
- Zipped paired collection: `ea93b086e6bae684`

## fastp run
- Tool: `toolshed.g2.bx.psu.edu/repos/iuc/fastp/fastp/1.3.6+galaxy0`
- History: `bbd44e69cb8906b59e58e5c004a6d3b9`
- Input collection: `ea93b086e6bae684`
- Output paired collection: `758c0f91f85d07fa`
- Generated command:

  `fastp --thread ${GALAXY_SLOTS:-1} --report_title ... -i ... -I ... -o first.fastqsanger.gz -O second.fastqsanger.gz -q 20 -u 40 -n 5 -l 15 --dont_eval_duplication`

### Parameters
- Adapter trimming: enabled, no adapter sequence supplied, PE auto-detection
  flag disabled. This uses mate-overlap analysis only.
- `qualified_quality_phred`: 20
- `unqualified_percent_limit`: 40
- `n_base_limit`: 5
- `length_required`: 15
- Quality trimming/cutting, polyX trimming, and base correction: disabled
- PolyG trimming: no polyG flag was emitted by the wrapper command; the
  generated command contains no other trimming flags.

## Outputs
- Forward Galaxy dataset: `f9cad7b01a472135662bd94e9e889b8f`
- Reverse Galaxy dataset: `f9cad7b01a4721354a13cfd5ae070819`
- Forward local file: `final_answer/trimmed_forward.fastqsanger.gz`
- Reverse local file: `final_answer/trimmed_reverse.fastqsanger.gz`

## Verification
- Forward records: 277,113
- Reverse records: 277,113
- Read identifiers match one-to-one in the same order after stripping `/1` and
  `/2` mate suffixes.
- Both files are valid gzip FASTQ (`fastqsanger.gz`).
- Retained mate lengths: 31 to 101 bp.
- No retained read has more than 5 `N` bases.
- No retained read has more than 40% bases below Phred 20.
