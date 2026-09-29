#!/bin/bash

cd "$(dirname "$0")"

rm -f answers-local.jsonl answers-openai.jsonl

( cat golden-set.txt | while read LINE; do
     ../Task4/rag_query.sh --json "${LINE}" 2>/dev/null | jq -c .
done ) | tee answers-local.jsonl

( cat golden-set.txt | while read LINE; do
    ../Task4/rag_query.sh --openai-embeddings --openai-llm --json "${LINE}" 2>/dev/null | jq -c .
done ) | tee answers-openai.jsonl
