"""Driver interface for running the conformance fixtures against a deployment.

A driver turns one fixture request into one observation (see observation.schema.json). Only the interface and a
recorded-observation driver are provided here: the archived Galaxy interface adapter's source is not in this repository,
and this package contacts no server. A live driver for a frozen deployment implements `run` by calling that
deployment's agent interface and translating its reply into the observation fields.

Abstract operations and the archived Galaxy adapter operations they correspond to:

| fixture operation    | archived adapter operation                     |
|----------------------|------------------------------------------------|
| search_tools         | search_galaxy_tools                            |
| inspect_tool         | inspect_galaxy_tool                            |
| run_tool             | run_galaxy_tool_and_wait                       |
| run_custom_tool      | run_galaxy_udt_and_wait                        |
| wait_jobs            | wait_for_galaxy_jobs                           |
| inspect_history      | inspect_galaxy_history                         |
| stage_file           | stage_workspace_file                           |
| copy_history         | none (agents used the Galaxy API from the shell) |
| download_dataset     | none (peek_galaxy_dataset returns a preview)   |
| record_local_step    | none (no execution-location receipt existed)   |
| raw_api_submission   | not an interface call; direct POST to the Galaxy API |

Fixture inputs are given as {"src": "fixture_input", "name": ...}; a driver stages inputs/<name> first and reports the
SHA-256 of what it staged in receipt.input_hashes.
"""
import json
from abc import ABC, abstractmethod
from pathlib import Path


class Driver(ABC):
    deployment: str = 'unspecified'
    adapter_version: str = 'unspecified'

    @abstractmethod
    def run(self, fixture: dict) -> dict:
        """Execute fixture['request'] and return the observation's `response` object."""

    def run_all(self, fixtures_doc: dict, out_path: Path):
        with open(out_path, 'w') as fh:
            for f in fixtures_doc['fixtures']:
                obs = {'fixture_id': f['id'], 'deployment': self.deployment, 'adapter_version': self.adapter_version,
                       'response': self.run(f)}
                fh.write(json.dumps(obs) + '\n')


class RecordedDriver(Driver):
    """Replays observations recorded elsewhere (for example by hand, or by another tool) for scoring."""

    def __init__(self, path):
        self.obs = {json.loads(line)['fixture_id']: json.loads(line) for line in open(path) if line.strip()}

    def run(self, fixture):
        return self.obs[fixture['id']]['response']
