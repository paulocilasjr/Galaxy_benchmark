# Galaxy execution log

- Assigned history: `bbd44e69cb8906b5ea728ff9921b6a5b` (`run-a8083b20ce9d4271ab6bb3968f13f51c`). No other history was accessed.
- Input: the `forward` and `reverse` members of the provided `Raw reads` `list:paired` collection. A standalone `paired` collection view (`96aa6d015c6aa270`) was created in the same history because the installed fastp wrapper could not render a command directly from the nested collection.
- Accepted Galaxy job: `bbd44e69cb8906b593cf74a91cd13f4b`, fastp `1.3.6`; state `ok` and all 22 checked parameters matched.
- Adapter handling: enabled with no supplied adapter sequences and paired-end adapter-sequence autodetection disabled. The rendered command has no adapter-sequence or autodetection flag, so paired adapter clipping used mate-overlap analysis.
- Filters: low-quality base threshold Phred 20; reject when low-quality bases exceed 40%; reject when N bases exceed 5; reject when either post-adapter mate is shorter than 15 bases.
- Other modification options: read merging, fixed front/tail trimming, quality-window cutting, PolyX trimming, base correction, UMI processing, duplicate removal, low-complexity filtering, and overrepresentation analysis were disabled. No PolyG or PolyX operation appears in the report.
- Galaxy report: 755,922 input reads (377,961 pairs); 554,226 retained reads (277,113 pairs); 89,226 reads adapter-trimmed; Q20 rate improved from 0.819271 to 0.987745. Adapter sequences are reported as `unspecified` for both mates.
- Exported Galaxy datasets: forward `f9cad7b01a472135ba6f4c0da876d14a`; reverse `f9cad7b01a4721359b325bd44a779faa`.
- Validation: both gzip streams pass integrity checks; both contain 277,113 records; normalized mate-ID hashes match; every retained mate has length >=15, <=5 N bases, and <=40% bases below Phred 20. Observed minimum mate length was 31 and maximum low-quality fraction was 0.400000.
- Deliverable SHA-256: forward `a06695255f49997b5d87b3aa3fd688f86ed4b4c7fa1aa1285741e545ae7bf8ee`; reverse `09de0702762a598372117cd5457901f043b7b6a2e085b6fc00b6838afa19ec97`.
- Earlier setup attempts are retained only as diagnostic provenance in `run_trace/`; their outputs were rejected and not exported.
