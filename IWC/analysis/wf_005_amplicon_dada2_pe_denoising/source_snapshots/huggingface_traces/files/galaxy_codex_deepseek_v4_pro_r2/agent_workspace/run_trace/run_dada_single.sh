#!/usr/bin/env bash
set -euo pipefail

HISTORY_ID=$(jq -r '.history_id' run_trace/assigned_history.json)
GALAXY_URL="${GALAXY_URL%/}"
API_KEY="${GALAXY_API_KEY}"
TOOL_ID='toolshed.g2.bx.psu.edu/repos/iuc/dada2_dada/dada2_dada/1.38.0+galaxy1'
ERR_F='f9cad7b01a472135e2d0e0baaedecde0'
ERR_R='f9cad7b01a4721351174ff21d2d106f5'

mkdir -p /tmp/dada2/dada_single_responses
: > /tmp/dada2/dada_single_map.tsv
: > /tmp/dada2/dada_single_jobs.tsv

while IFS=$'\t' read -r sample direction filtered_id job_id; do
  if [ "$direction" = forward ]; then
    err="$ERR_F"
  else
    err="$ERR_R"
  fi

  payload="/tmp/dada2/dada_single_payload_${sample}_${direction}.json"
  jq -n \
    --arg history_id "$HISTORY_ID" \
    --arg tool_id "$TOOL_ID" \
    --arg input_id "$filtered_id" \
    --arg err "$err" \
    '{
      history_id: $history_id,
      tool_id: $tool_id,
      inputs: {
        "batch_cond|batch_select": "yes",
        "batch_cond|derep": {src: "hda", id: $input_id},
        "err": {src: "hda", id: $err},
        "advanced|enable": "no"
      }
    }' > "$payload"

  response="/tmp/dada2/dada_single_responses/${sample}_${direction}.json"
  curl -sS -X POST \
    -H "x-api-key: ${API_KEY}" \
    -H 'Content-Type: application/json' \
    --data-binary @"$payload" \
    "${GALAXY_URL}/api/tools" > "$response"

  if ! jq -e '.outputs and .jobs' "$response" >/dev/null; then
    echo "Submission error for ${sample} ${direction}" >&2
    jq . "$response" >&2
    exit 1
  fi

  outid=$(jq -r '.outputs[] | select(.output_name == "dada") | .id' "$response")
  newjob=$(jq -r '.jobs[0].id' "$response")
  if [ -z "$outid" ] || [ "$outid" = null ] || \
     [ -z "$newjob" ] || [ "$newjob" = null ]; then
    echo "Missing output/job for ${sample} ${direction}" >&2
    jq . "$response" >&2
    exit 1
  fi

  printf '%s\t%s\t%s\t%s\n' "$sample" "$direction" "$outid" "$newjob" \
    >> /tmp/dada2/dada_single_map.tsv
  printf '%s\n' "$newjob" >> /tmp/dada2/dada_single_jobs.tsv
done < /tmp/dada2/filter_map.tsv

echo "Submitted $(wc -l < /tmp/dada2/dada_single_map.tsv) single-sample dada jobs"
echo "Map: /tmp/dada2/dada_single_map.tsv"
echo "Jobs: /tmp/dada2/dada_single_jobs.tsv"
