#!/bin/bash

. ../secret.envsh

echo "Building embeddings with local model..."

time ( find ../Task2/knowledge_base/ -type f -exec cat {} \; | ( env -u OPENAI_API_KEY python index_or_query.py ) )

echo

echo "Building embeddings with OpenAI..."

time ( find ../Task2/knowledge_base/ -type f -exec cat {} \; | python index_or_query.py )
