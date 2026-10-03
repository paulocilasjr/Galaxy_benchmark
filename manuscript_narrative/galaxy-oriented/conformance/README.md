# Conformance fixtures for agent-facing workbench interfaces

This folder implements the conformance suite of Supplementary Note 1, section 3, for the Galaxy-oriented manuscript. It tests an interface and server, not a model: each fixture is a fixed request with known inputs and machine-checkable expectations. **Status: specified and self-tested; not yet run against any deployment.** No result here is evidence that Galaxy, or the archived adapter, meets or fails a requirement.

## Contents

| File | Role |
|---|---|
| `build_fixtures.py` | Writes `inputs/`, `fixtures.json` and `archive_basis_check.json`. |
| `fixtures.json` | 33 fixtures across requirements R1–R6 (binding 12, failure payloads 6, metadata 3, discovery 3, life cycle 4, attestation and isolation 5). |
| `inputs/` | Small synthetic input files with fixed bytes; their SHA-256 values are recorded in each fixture. `table.xlsx.txt` is a placeholder to be replaced by a real one-sheet workbook at registration. |
| `observation.schema.json` | What a driver must record for each fixture. |
| `score.py` | Scores `observations.jsonl` against the fixtures. |
| `selftest.py` | Checks the suite itself: reference responses must pass, and ten injected defects must be detected. Writes `selftest_report.json`. |
| `driver.py` | Driver interface, a recorded-observation driver, and the mapping from fixture operations to the archived adapter's operations. |

## Fixture design

Each fixture records:

- the requirement and category;
- its control type:
  - `positive`: must succeed;
  - `negative`: must be rejected, or echoed exactly as resolved where the protocol allows that;
  - `dataset_only` and `unsupported_comparison`: legitimate zero-comparison calls that must be declared as such;
  - `known_location`: execution-location ground truth for receipts;
- the request, the input hashes, the checks and one reference response that satisfies them.

Five binding fixtures reproduce request shapes from bix-35-q1 job ledgers, and `build_fixtures.py` confirms each shape in the cited ledger event (`archive_basis_check.json`). Among them:

- R1-04 is the bare-identifier request after which Galaxy ran the default metric;
- R1-05 is the case-index-only resubmission that was checked against zero parameters and returned `ok`.

Their `archive_basis.archived_outcome` fields record what the archived adapter did; both outcomes fail these fixtures.

Values written `<freeze:NAME>` (tool versions, container images, option lists, output descriptions) must be fixed when the study's catalogue is frozen. `score.py` reports such fixtures as `unfrozen` unless the values are supplied with `--freeze freeze_values.json`.

## Running

```sh
python build_fixtures.py          # regenerate fixtures and inputs
python selftest.py                # must report every mutation as detected
python score.py observations.jsonl --freeze freeze_values.json --out report.json
```

The report gives pass and fail counts per requirement, with the reason for each failure. It shows the completion rate on positive controls and the refusal-or-exact-echo rate on negative controls side by side. This means an adapter that refuses everything, or accepts everything, cannot score well. It also reports the accuracy of execution-location receipts.

## Self-test (mutation controls)

`selftest.py` applies ten defects to the reference responses:

- removing parameter checks;
- truncating receipts;
- permitting cross-account reads;
- stripping failure diagnostics;
- hiding versions and output semantics;
- unbounded discovery responses;
- refusing every request;
- accepting every request;
- mislabelling the execution location;
- requiring a history for tool schemas.

Each defect must make at least one fixture of each targeted requirement fail. The current report (`selftest_report.json`) shows all 33 reference responses passing and all ten defects detected. This validates the fixtures and scorer only.

## Not yet done

- A live driver. The archived adapter's source is not in this repository, and this package contacts no server.
- Freeze values, a frozen catalogue and the second deployment.
- Equivalent fixtures for another workbench. Supplementary Note 1 requires all three before results are interpreted.
