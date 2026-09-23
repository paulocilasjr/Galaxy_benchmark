#!/usr/bin/env bash
set -euo pipefail

API="$GALAXY_URL/api/tools"
HIST="bbd44e69cb8906b5fb29461679e42397"
TOOL="toolshed.g2.bx.psu.edu/repos/iuc/dada2_dada/dada2_dada/1.38.0+galaxy1"

MAP="$1"
ERR_FWD="$2"
ERR_REV="$3"
OUT="$4"

JOBS_TSV=$(mktemp)

while IFS=$'\t' read -r sample fwd rev; do
  for direction in forward reverse; do
    if [[ "$direction" == "forward" ]]; then
      reads="$fwd"
      err="$ERR_FWD"
    else
      reads="$rev"
      err="$ERR_REV"
    fi
    payload=$(jq -nc --arg hist "$HIST" --arg tool "$TOOL" --arg reads "$reads" --arg err "$err" '{
      history_id: $hist,
      tool_id: $tool,
      inputs: {
        "batch_cond|batch_select": "yes",
        "batch_cond|derep": {"src": "hda", "id": $reads},
        "err": {"src": "hda", "id": $err},
        "advanced|enable": "no"
      }
    }')
    resp=$(curl -sS -X POST -H "x-api-key: $GALAXY_API_KEY" -H "Content-Type: application/json" "$API" --data-binary "$payload")
    jobid=$(printf '%s' "$resp" | jq -r '.jobs[0].id')
    outid=$(printf '%s' "$resp" | jq -r '.outputs[0].id')
    printf '%s\t%s\t%s\t%s\n' "$sample" "$direction" "$jobid" "$outid" >> "$JOBS_TSV"
  done
done < "$MAP"

cat "$JOBS_TSV"
cp "$JOBS_TSV" "$OUT"
