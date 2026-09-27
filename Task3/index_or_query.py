import argparse
import hashlib
import numpy
import os
import sys
import tiktoken
import torch

from fastembed import SparseTextEmbedding
from loguru import logger
from openai import OpenAI
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchAny,
    Modifier,
    PointStruct,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

from sentence_transformers import SentenceTransformer

OPENAI_DENSE_MODEL_NAME = "text-embedding-3-large"
LOCAL_DENSE_MODEL_NAME = "codefuse-ai/F2LLM-v2-330M"
LOCAL_DENSE_MODEL_BATCH_SIZE = 16

DENSE_MODEL_CHUNK_SIZE = 512
DENSE_MODEL_OVERLAP_TOKENS = 64

SPARSE_MODEL_NAME = "Qdrant/bm25"

QDRANT_URL = "http://localhost:6333"
QDRANT_COLLECTION_NAME_PREFIX = "wiki"
QDRANT_UPLOAD_BATCH_SIZE = 128

def load_hashes(hash_file: Path) -> dict[int, str]:
    hashes = {}

    if not hash_file.exists():
        return hashes

    with hash_file.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            file_id_str, md5_hash = line.split(maxsplit=1)
            hashes[int(file_id_str)] = md5_hash

    return hashes

def save_hashes(hash_file: Path, hashes: dict[int, str]) -> None:
    with hash_file.open("w", encoding="utf-8") as f:
        for file_id in sorted(hashes):
            f.write(f"{file_id} {hashes[file_id]}\n")

def calculate_md5(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()

def process_directory(
    directory: Path,
    hashes: dict[int, str],
) -> dict[int, str]:
    changed_files = {}

    for txt_file in directory.glob("*.txt"):
        with txt_file.open("r", encoding="utf-8") as f:
            file_id = int(f.readline().strip())
            content = f.read()

        md5_hash = calculate_md5(content)

        if hashes.get(file_id) != md5_hash:
            changed_files[file_id] = content
            hashes[file_id] = md5_hash

    return changed_files

logger.remove()

logger.add(sys.stdout, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}")

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

    qdrant_collection_name = f'{QDRANT_COLLECTION_NAME_PREFIX}-openai'
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

    qdrant_collection_name = f'{QDRANT_COLLECTION_NAME_PREFIX}-local'

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
        collection_name=qdrant_collection_name,
        query=dense_embeddings[0].tolist(),
        using="dense",
        limit=limit * 2,
        with_payload=True,
    ).points

    sparse_result = qdrant.query_points(
        collection_name=qdrant_collection_name,
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
    parser.add_argument(
        "--query",
        help="query mode"
    )
    parser.add_argument(
        "--wiki",
        help="path to wiki files directory",
    )
    parser.add_argument(
        "--hashes",
        help="path to MD5 hashes file",
    )

    args = parser.parse_args()

    if args.query is not None:
        query(args.query, 5)

        sys.exit()

    wiki_directory = Path(args.wiki)
    hashes_file = Path(args.hashes)

    hashes = load_hashes(hashes_file)

    changed_pages = process_directory(
        directory=wiki_directory,
        hashes=hashes,
    )

    save_hashes(hashes_file, hashes)

    documents = []
    metadata = []

    if len(changed_pages) == 0:
        logger.info(f"nothing to upload")

        exit(0)

    logger.info(f"started processing {len(changed_pages)} new or changed wiki pages")

    for (page_id, page) in changed_pages.items():
        lines = page.splitlines()

        title = lines[0].strip()
        content = "\n".join(lines[1:]).strip()

        chunk_id = 1

        while True:
            text = f'Title: {title}\n{content}'

            tokens = encode(text)

            chunk = tokens[0:DENSE_MODEL_CHUNK_SIZE]

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

            if len(chunk) < DENSE_MODEL_CHUNK_SIZE:
                break

            content = decode(tokens[DENSE_MODEL_CHUNK_SIZE - DENSE_MODEL_OVERLAP_TOKENS:])

    if not use_openai and local_dense_model.max_seq_length > DENSE_MODEL_CHUNK_SIZE:
        local_dense_model.max_seq_length = DENSE_MODEL_CHUNK_SIZE

    dense_embeddings = embed(
        documents,
    )

    sparse_embeddings = list(
        sparse_model.embed(
            documents
        )
    )

    if not qdrant.collection_exists(
        collection_name=qdrant_collection_name
    ):
        qdrant.create_collection(
            collection_name=qdrant_collection_name,

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

    page_ids = list(changed_pages.keys())

    if page_ids:
        qdrant.delete(
            collection_name=qdrant_collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="page_id",
                        match=MatchAny(any=page_ids),
                    )
                ]
            ),
            wait=True,
        )

    points = []

    for (dense, sparse, meta) in zip(
        dense_embeddings,
        sparse_embeddings,
        metadata,
    ):
        point = PointStruct(
            id=meta["page_id"] * 1000 + meta["chunk_id"],

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
            collection_name=qdrant_collection_name,
            points=batch,
            wait=True,
        )

        start += QDRANT_UPLOAD_BATCH_SIZE

        if len(batch) < QDRANT_UPLOAD_BATCH_SIZE:
            break

    count = qdrant.count(
        collection_name=qdrant_collection_name,
        exact=True,
    ).count

    logger.info(f"successfully uploaded {len(points)} chunks from {len(changed_pages)} new or changed wiki pages, total collection size is {count}")

if __name__ == "__main__":
    main()
