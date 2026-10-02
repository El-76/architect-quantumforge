#!/usr/bin/env bash

set -euo pipefail

INPUT_FILE="${1:-dataset.jsonl}"

while IFS= read -r line
do
    [ -z "$line" ] && continue

    candidate=$(jq -r '.candidate_answer' <<< "$line")
    reference=$(jq -r '.reference_answer' <<< "$line")

    cosine=$(
        python ../Task3/index_or_query.py \
            --candidate "$candidate" \
            --reference "$reference"
    )

    jq -c \
        --argjson cosine "$cosine" \
        '. + {cosine: $cosine}' \
        <<< "$line"

done < "$INPUT_FILE"
