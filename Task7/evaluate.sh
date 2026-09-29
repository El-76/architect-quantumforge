#!/usr/bin/env bash

cd "$(dirname "$0")"

. ../secret.envsh

set -euo pipefail

INPUT_FILE="${1:-dataset.json}"
MODEL="${MODEL:-gpt-5}"

while IFS= read -r item
do
    question=$(jq -r '.question' <<< "$item")
    reference=$(jq -r '.reference_answer' <<< "$item")
    candidate=$(jq -r '.candidate_answer' <<< "$item")

    prompt=$(cat <<EOF
Вопрос:
$question

Эталонный ответ:
$reference

Ответ кандидата:
$candidate

Оцени ответ кандидата в сравнении с эталонным ответом.

Верни только JSON с полями score и reason.

Значения score:
1.0 = ответы эквивалентны
0.8 = по большей части ответ кандидата верный
0.5 = ответ кандидата частично верный
0.0 = ответ кандидата неверный

EOF
)

    response=$(
    curl -s https://api.openai.com/v1/responses \
      -H "Authorization: Bearer $OPENAI_API_KEY" \
      -H "Content-Type: application/json" \
      -d @- <<EOF
{
  "model": "$MODEL",
  "input": [
    {
      "role": "system",
      "content": "You are an objective QA evaluator."
    },
    {
      "role": "user",
      "content": $(jq -Rs . <<< "$prompt")
    }
  ],
  "text": {
    "format": {
      "type": "json_schema",
      "name": "evaluation",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "score": {
            "type": "number"
          },
          "reason": {
            "type": "string"
          }
        },
        "required": ["score", "reason"],
        "additionalProperties": false
      }
    }
  }
}
EOF
)

echo "$response" | jq -c --arg question "$question" '
  .output[]
  | select(.type=="message")
  | .content[0].text
  | fromjson
  | . + {question: $question}
'

done < "$INPUT_FILE"
