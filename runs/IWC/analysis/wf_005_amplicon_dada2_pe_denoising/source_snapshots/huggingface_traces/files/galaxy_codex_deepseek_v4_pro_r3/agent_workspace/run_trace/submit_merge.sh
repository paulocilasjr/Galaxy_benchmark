#!/usr/bin/env bash
set -euo pipefail

API="$GALAXY_URL/api/tools"
HIST="bbd44e69cb8906b5fb29461679e42397"
TOOL="toolshed.g2.bx.psu.edu/repos/iuc/dada2_mergepairs/dada2_mergePairs/1.38.0+galaxy1"

FILTER_MAP="$1"
DADA_JOBS="$2"
OUT="$3"

JOBS_TSV=$(mktemp)

while IFS=$'\t' read -r sample derep_f derep_r; do
  dada_f=$(awk -F'\t' -v s="$sample" -v d="forward" '$1==s && $2==d {print $4}' "$DADA_JOBS")
  dada_r=$(awk -F'\t' -v s="$sample" -v d="reverse" '$1==s && $2==d {print $4}' "$DADA_JOBS")
  payload=$(jq -nc --arg hist "$HIST" --arg tool "$TOOL" \
    --arg dadaF "$dada_f" --arg derepF "$derep_f" --arg dadaR "$dada_r" --arg derepR "$derep_r" '{
    history_id: $hist,
    tool_id: $tool,
    inputs: {
      "dadaF": {"src": "hda", "id": $dadaF},
      "derepF": {"src": "hda", "id": $derepF},
      "dadaR": {"src": "hda", "id": $dadaR},
      "derepR": {"src": "hda", "id": $derepR},
      "minOverlap": "12",
      "maxMismatch": "0",
      "justConcatenate": false,
      "trimOverhang": false,
      "output_details": false
    }
  }')
  resp=$(curl -sS -X POST -H "x-api-key: $GALAXY_API_KEY" -H "Content-Type: application/json" "$API" --data-binary "$payload")
  jobid=$(printf '%s' "$resp" | jq -r '.jobs[0].id')
  merged=$(printf '%s' "$resp" | jq -r '.outputs[] | select(.output_name=="merged") | .id')
  printf '%s\t%s\t%s\n' "$sample" "$jobid" "$merged" >> "$JOBS_TSV"
done < "$FILTER_MAP"

cat "$JOBS_TSV"
cp "$JOBS_TSV" "$OUT"
