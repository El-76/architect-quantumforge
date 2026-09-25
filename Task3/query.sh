#!/bin/bash

. ../secret.envsh

echo "Querying with local model..."

echo

( env -u OPENAI_API_KEY python index_or_query.py --query $1 )

echo

echo "Querying with OpenAI..."

echo

python index_or_query.py --query $1
