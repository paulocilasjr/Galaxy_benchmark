#!/usr/bin/env bash
set -euo pipefail

HISTORY_ID=$(jq -r '.history_id' run_trace/assigned_history.json)
GALAXY_URL="${GALAXY_URL%/}"
API_KEY="${GALAXY_API_KEY}"
TOOL_ID='toolshed.g2.bx.psu.edu/repos/iuc/dada2_filterandtrim/dada2_filterAndTrim/1.38.0+galaxy1'
COLLECTION_ID='bc691189a1eab94e'

mkdir -p /tmp/dada2/filter_responses
rm -f /tmp/dada2/filter_map.tsv /tmp/dada2/filter_jobs.tsv

curl -sS -H "x-api-key: ${API_KEY}" \
  "${GALAXY_URL}/api/dataset_collections/${COLLECTION_ID}" \
  > /tmp/dada2/input_collection.json

jq -r '.elements[] |
  .element_identifier as $sample |
  (.object.elements[] | select(.element_identifier == "forward") | .object.id) as $fwd |
  (.object.elements[] | select(.element_identifier == "reverse") | .object.id) as $rev |
  [$sample, $fwd, $rev] | @tsv' \
  /tmp/dada2/input_collection.json > /tmp/dada2/sample_map.tsv

while IFS=$'\t' read -r sample fwd rev; do
  for direction in forward reverse; do
    if [ "$direction" = forward ]; then
      input_id="$fwd"
      trunc_len=240
    else
      input_id="$rev"
      trunc_len=160
    fi
    payload="/tmp/dada2/filter_payload_${sample}_${direction}.json"
    jq -n \
      --arg history_id "$HISTORY_ID" \
      --arg tool_id "$TOOL_ID" \
      --arg input_id "$input_id" \
      --argjson trunc_len "$trunc_len" \
      '{
        history_id: $history_id,
        tool_id: $tool_id,
        inputs: {
          "paired_cond|paired_select": "single",
          "paired_cond|reads": {src: "hda", id: $input_id},
          "trim|truncQ": 2,
          "trim|trimLeft": 0,
          "trim|trimRight": 0,
          "trim|truncLen": $trunc_len,
          "filter|maxLen": "",
          "filter|minLen": 20,
          "filter|maxN": 0,
          "filter|minQ": 0,
          "filter|maxEE": 2,
          "seprev_cond|seprev_select": "no",
          "rmPhiX": true,
          "rmlowcomplex": 0,
          "orientFwd": "",
          "output_statistics": true
        }
      }' > "$payload"

    response="/tmp/dada2/filter_responses/${sample}_${direction}.json"
    curl -sS -X POST \
      -H "x-api-key: ${API_KEY}" \
      -H 'Content-Type: application/json' \
      --data-binary @"$payload" \
      "${GALAXY_URL}/api/tools" > "$response"

    if ! jq -e '.outputs and .jobs' "$response" >/dev/null; then
      echo "SUBMISSION ERROR for ${sample} ${direction}:" >&2
      jq . "$response" >&2
      exit 1
    fi

    output_id=$(jq -r '.outputs[] | select(.output_name == "output_single") | .id' "$response")
    job_id=$(jq -r '.jobs[0].id' "$response")
    if [ -z "$output_id" ] || [ "$output_id" = null ] || [ -z "$job_id" ] || [ "$job_id" = null ]; then
      echo "Missing output/job in ${sample} ${direction}:" >&2
      jq . "$response" >&2
      exit 1
    fi
    printf '%s\t%s\t%s\t%s\n' "$sample" "$direction" "$output_id" "$job_id" >> /tmp/dada2/filter_map.tsv
    printf '%s\n' "$job_id" >> /tmp/dada2/filter_jobs.tsv
  done
done < /tmp/dada2/sample_map.tsv

echo "Submitted $(wc -l < /tmp/dada2/filter_map.tsv) filter jobs"
echo "Map: /tmp/dada2/filter_map.tsv"
echo "Jobs: /tmp/dada2/filter_jobs.tsv"
