import argparse
import numpy
import os
import sys
import tiktoken
import torch

from fastembed import SparseTextEmbedding
from openai import OpenAI

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    SparseVectorParams,
    SparseVector,
    PointStruct,
    Modifier,
)

from sentence_transformers import SentenceTransformer

OPENAI_DENSE_MODEL_NAME = "text-embedding-3-large"
LOCAL_DENSE_MODEL_NAME = "codefuse-ai/F2LLM-v2-330M"
LOCAL_DENSE_MODEL_BATCH_SIZE = 16

SPARSE_MODEL_NAME = "Qdrant/bm25"

QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME = "wiki"
QDRANT_UPLOAD_BATCH_SIZE = 128

use_openai = 'OPENAI_API_KEY' in os.environ

if use_openai:
    openai_ = OpenAI()

    tokenizer = tiktoken.encoding_for_model(
        OPENAI_DENSE_MODEL_NAME
    )

    encode = lambda text: tokenizer.encode_ordinary(text)

    decode = lambda token_ids: tokenizer.decode(token_ids)

    embed = lambda documents: numpy.asarray([
        item.embedding for item in openai_.embeddings.create(
            model=OPENAI_DENSE_MODEL_NAME,
            input=documents,
        ).data
    ])
else:
    device = "cuda" if torch.cuda.is_available() else "cpu"

    local_dense_model = SentenceTransformer(
        LOCAL_DENSE_MODEL_NAME,
        device=device,
    )

    tokenizer = local_dense_model.tokenizer

    encode = lambda text: tokenizer.encode(
        text,
        add_special_tokens=False
    )

    decode = lambda token_ids: tokenizer.decode(
        token_ids,
        skip_special_tokens=False,
        clean_up_tokenization_spaces=False,
    )

    embed = lambda documents: local_dense_model.encode(
        documents,
        batch_size=LOCAL_DENSE_MODEL_BATCH_SIZE,
        normalize_embeddings=True,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

sparse_model = SparseTextEmbedding(
    model_name=SPARSE_MODEL_NAME,
)

qdrant = QdrantClient(
    url=QDRANT_URL,
)

def query(query: str, limit: int):
    dense_embeddings = embed(
        [query],
    )

    sparse_embeddings = list(
        sparse_model.embed(
            [query]
        )
    )

    dense_result = qdrant.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=dense_embeddings[0].tolist(),
        using="dense",
        limit=limit * 2,
        with_payload=True,
    ).points

    sparse_result = qdrant.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=SparseVector(
            indices=sparse_embeddings[0].indices.tolist(),
            values=sparse_embeddings[0].values.tolist(),
        ),
        using="sparse",
        limit=limit * 2,
        with_payload=True,
    ).points

    # ------------------------------------------------------------
    # Reciprocal Rank Fusion
    # ------------------------------------------------------------

    RRF_K = 60

    rrf_scores = {}
    points = {}

    for rank, point in enumerate(dense_result, start=1):
        point_id = point.id

        rrf_scores[point_id] = (
            rrf_scores.get(point_id, 0.0)
            + 1.0 / (RRF_K + rank)
        )

        points[point_id] = point


    for rank, point in enumerate(sparse_result, start=1):
        point_id = point.id

        rrf_scores[point_id] = (
            rrf_scores.get(point_id, 0.0)
            + 1.0 / (RRF_K + rank)
        )

        points[point_id] = point

    # ------------------------------------------------------------
    # Sort
    # ------------------------------------------------------------

    ranked = sorted(
        rrf_scores.items(),
        key=lambda x: x[1],
        reverse=True,
    )

    # ------------------------------------------------------------
    # Display
    # ------------------------------------------------------------

    print(f"\nQuery: {query}\n")

    for rank, (point_id, score) in enumerate(
        ranked[:limit],
        start=1,
    ):
        point = points[point_id]
        payload = point.payload

        print("=" * 80)
        print(f"#{rank}  RRF={score:.6f}")
        print(f"Title: {payload.get('title')}")
        print(f"Page ID: {payload.get('page_id')}")
        print(f"Chunk: {payload.get('chunk_id')}")
        print()
        print(payload.get("page_content", ""))
        print()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--query")

    args = parser.parse_args()

    if args.query is not None:
        query(args.query, 5)

        sys.exit()

    chunk_size = 512
    overlap_tokens = 64

    wiki = sys.stdin.read()

    pages = wiki.split("\n\n")

    documents = []
    metadata = []

    for page_id, page in enumerate(pages, start=1):
        lines = page.splitlines()

        title = lines[0].strip()
        content = "\n".join(lines[1:]).strip()

        chunk_id = 1

        while True:
            text = f'Title: {title}\n{content}'

            tokens = encode(text)

            chunk = tokens[0:chunk_size]

            document = decode(chunk)

            metadata += [
                {
                    "page_id": page_id,
                    "title": title,
                    "chunk_id": chunk_id,
                    "page_content": document,
                }
            ]

            documents += [ document ]

            chunk_id += 1

            if len(chunk) < chunk_size:
                break

            content = decode(tokens[chunk_size - overlap_tokens:])

    dense_embeddings = embed(
        documents,
    )

    sparse_embeddings = list(
        sparse_model.embed(
            documents
        )
    )

    if qdrant.collection_exists(
        collection_name=QDRANT_COLLECTION_NAME
    ):
        qdrant.delete_collection(
            collection_name=QDRANT_COLLECTION_NAME
        )


    qdrant.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,

        vectors_config={
            "dense": VectorParams(
                size=dense_embeddings.shape[1],
                distance=Distance.COSINE,
            )
        },

        sparse_vectors_config={
            "sparse": SparseVectorParams(
                modifier=Modifier.IDF,
            )
        },
    )

    points = []

    for idx, (dense, sparse, meta) in enumerate(
        zip(
            dense_embeddings,
            sparse_embeddings,
            metadata,
        )
    ):
        point = PointStruct(
            id=idx,

            vector={
                "dense": dense.tolist(),

                "sparse": SparseVector(
                    indices=sparse.indices.tolist(),
                    values=sparse.values.tolist(),
                ),
            },

            payload=meta,
        )

        points += [ point ]


    start = 0

    while True:
        batch = points[start:start + QDRANT_UPLOAD_BATCH_SIZE]

        qdrant.upsert(
            collection_name=QDRANT_COLLECTION_NAME,
            points=batch,
            wait=True,
        )

        start += QDRANT_UPLOAD_BATCH_SIZE

        if len(batch) < QDRANT_UPLOAD_BATCH_SIZE:
            break

if __name__ == "__main__":
    main()
