#!/usr/bin/env bash
set -euo pipefail

API="$GALAXY_URL/api/tools"
HIST="bbd44e69cb8906b5fb29461679e42397"
TOOL="toolshed.g2.bx.psu.edu/repos/iuc/dada2_filterandtrim/dada2_filterAndTrim/1.38.0+galaxy1"

PAIRS_TSV=$(mktemp)
JOBS_TSV=$(mktemp)

curl -sS -H "x-api-key: $GALAXY_API_KEY" "$GALAXY_URL/api/dataset_collections/80c8a6983b17ea0b" \
  | jq -r '.elements[] | [.element_identifier, .id] | @tsv' > "$PAIRS_TSV"

while IFS=$'\t' read -r sample collid; do
  payload=$(jq -nc --arg hist "$HIST" --arg tool "$TOOL" --arg coll "$collid" '{
    history_id: $hist,
    tool_id: $tool,
    inputs: {
      "paired_cond|paired_select": "paired",
      "paired_cond|reads": {"src": "dce", "id": $coll},
      "trim|truncQ": "2",
      "trim|trimLeft": "0",
      "trim|trimRight": "0",
      "trim|truncLen": "240",
      "filter|maxLen": "",
      "filter|minLen": "20",
      "filter|maxN": "0",
      "filter|minQ": "0",
      "filter|maxEE": "2",
      "seprev_cond|seprev_select": "yes",
      "seprev_cond|trim|truncQ": "2",
      "seprev_cond|trim|trimLeft": "0",
      "seprev_cond|trim|trimRight": "0",
      "seprev_cond|trim|truncLen": "160",
      "seprev_cond|filter|maxLen": "",
      "seprev_cond|filter|minLen": "20",
      "seprev_cond|filter|maxN": "0",
      "seprev_cond|filter|minQ": "0",
      "seprev_cond|filter|maxEE": "2",
      "rmPhiX": "true",
      "rmlowcomplex": "0",
      "orientFwd": "",
      "output_statistics": "true"
    }
  }')
  resp=$(curl -sS -X POST -H "x-api-key: $GALAXY_API_KEY" -H "Content-Type: application/json" "$API" --data-binary "$payload")
  jobid=$(printf '%s' "$resp" | jq -r '.jobs[0].id')
  outcoll=$(printf '%s' "$resp" | jq -r '.output_collections[] | select(.name=="dada2: filterAndTrim on collection 69: Paired reads") | .id' | head -n 1)
  printf '%s\t%s\t%s\n' "$sample" "$jobid" "$outcoll" >> "$JOBS_TSV"
done < "$PAIRS_TSV"

cat "$JOBS_TSV"
cp "$JOBS_TSV" run_trace/filter_jobs.tsv
