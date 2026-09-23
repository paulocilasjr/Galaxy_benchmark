#!/usr/bin/env bash
set -euo pipefail

HISTORY_ID=$(jq -r '.history_id' run_trace/assigned_history.json)
GALAXY_URL="${GALAXY_URL%/}"
API_KEY="${GALAXY_API_KEY}"
TOOL_ID='toolshed.g2.bx.psu.edu/repos/iuc/dada2_dada/dada2_dada/1.38.0+galaxy1'
ERR_F='f9cad7b01a4721353a0d7ac35c6952f3'
ERR_R='f9cad7b01a472135ac202684ed46382c'

mkdir -p /tmp/dada2/dada_paired_responses
: > /tmp/dada2/dada_paired_map.tsv
: > /tmp/dada2/dada_paired_jobs.tsv

# paired_filter_map.tsv columns:
# sample  filtered_forward  filtered_reverse  outtab  filter_job  output_collection
while IFS=$'\t' read -r sample fwd rev outtab filter_job out_coll; do
  for direction in forward reverse; do
    if [ "$direction" = forward ]; then
      filtered_id="$fwd"
      err="$ERR_F"
    else
      filtered_id="$rev"
      err="$ERR_R"
    fi

    payload="/tmp/dada2/dada_paired_payload_${sample}_${direction}.json"
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

    response="/tmp/dada2/dada_paired_responses/${sample}_${direction}.json"
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
      >> /tmp/dada2/dada_paired_map.tsv
    printf '%s\n' "$newjob" >> /tmp/dada2/dada_paired_jobs.tsv
  done
done < /tmp/dada2/paired_filter_map.tsv

echo "Submitted $(wc -l < /tmp/dada2/dada_paired_map.tsv) paired-filtered single-sample DADA jobs"
echo "Map: /tmp/dada2/dada_paired_map.tsv"
echo "Jobs: /tmp/dada2/dada_paired_jobs.tsv"
