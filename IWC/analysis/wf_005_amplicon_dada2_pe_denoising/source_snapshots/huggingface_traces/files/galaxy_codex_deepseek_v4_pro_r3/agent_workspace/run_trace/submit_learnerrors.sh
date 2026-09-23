#!/usr/bin/env bash
set -euo pipefail

API="$GALAXY_URL/api/tools"
HIST="bbd44e69cb8906b5fb29461679e42397"
TOOL="toolshed.g2.bx.psu.edu/repos/iuc/dada2_learnerrors/dada2_learnErrors/1.38.0+galaxy1"

MAP="$1"
DIRECTION="$2"
COL="$3"

if [[ "$DIRECTION" == "forward" ]]; then
  ids=$(awk -F'\t' -v c="$COL" '{print $c}' "$MAP")
else
  ids=$(awk -F'\t' -v c="$COL" '{print $c}' "$MAP")
fi

values=$(printf '%s\n' "$ids" | jq -R -s -c 'split("\n") | map(select(length>0) | {src:"hda", id:.})')

payload=$(jq -nc --arg hist "$HIST" --arg tool "$TOOL" --argjson values "$values" '{
  history_id: $hist,
  tool_id: $tool,
  inputs: {
    "fls": {"values": $values},
    "nbases": "8",
    "advanced|errfoo": "loessErrfun",
    "advanced|maxconsist": "10",
    "advanced|omegac": "0.0",
    "advanced|quality_bins": "",
    "advanced|randomize": false,
    "plotopt|obs": true,
    "plotopt|err_out": true,
    "plotopt|err_in": false,
    "plotopt|nominalQ": true
  }
}')

curl -sS -X POST -H "x-api-key: $GALAXY_API_KEY" -H "Content-Type: application/json" "$API" --data-binary "$payload"
