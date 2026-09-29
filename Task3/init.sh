#!/bin/bash

cd "$(dirname "$0")"

docker stop qdrant_wiki

docker rm qdrant_wiki

rm -rf qdrant_storage qdrant_storage_wiki/ hashes-local.txt hashes-openai.txt

mkdir -p qdrant_storage

docker run -d --name qdrant_wiki -p 6333:6333 -p 6334:6334 -v $(pwd)/qdrant_storage:/qdrant/storage:z -u $(id -u):$(id -g) qdrant/qdrant:latest-unprivileged

./index.sh

docker stop qdrant_wiki

cp -r qdrant_storage/ qdrant_storage_wiki

docker start qdrant_wiki
