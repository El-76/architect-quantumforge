#!/bin/bash

cd "$(dirname "$0")"

. ../secret.envsh

echo "Building embeddings with local model..."

time ( env -u OPENAI_API_KEY python index_or_query.py --wiki ../Task2/knowledge_base --hashes ./hashes-local.txt )

echo

echo "Building embeddings with OpenAI..."

time python index_or_query.py --wiki ../Task2/knowledge_base --hashes ./hashes-openai.txt
