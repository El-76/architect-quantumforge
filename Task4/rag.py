import argparse
import os
import torch

from sentence_transformers import SentenceTransformer

from langchain_core.embeddings import Embeddings
from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import (
    ChatOpenAI,
    OpenAIEmbeddings
)

from langchain_qdrant import (
    FastEmbedSparse,
    QdrantVectorStore,
    RetrievalMode,
)

from qdrant_client import QdrantClient

from operator import itemgetter

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough

# ============================================================
# Configuration
# ============================================================

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME_PREFIX = "wiki"

DENSE_MODEL_NAME = "codefuse-ai/F2LLM-v2-330M"
SPARSE_MODEL_NAME = "Qdrant/bm25"


# ============================================================
# Dense embedding adapter
# ============================================================

class SentenceTransformerEmbeddings(Embeddings):

    def __init__(self, model_name: str):
        device = "cuda" if torch.cuda.is_available() else "cpu"

        self.model = SentenceTransformer(
            model_name,
            device=device,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()

    def embed_query(self, text: str) -> list[float]:
        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embedding.tolist()


# ============================================================
# Embedding models
# ============================================================

dense_embeddings_openai = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

dense_embeddings_local = SentenceTransformerEmbeddings(
    DENSE_MODEL_NAME,
)

sparse_embeddings = FastEmbedSparse(
    model_name=SPARSE_MODEL_NAME,
)


# ============================================================
# Qdrant
# ============================================================

client = QdrantClient(
    url=QDRANT_URL,
)


vector_store_openai = QdrantVectorStore(
    client=client,
    collection_name=f"{COLLECTION_NAME_PREFIX}-openai",

    # Dense model
    embedding=dense_embeddings_openai,

    # BM25
    sparse_embedding=sparse_embeddings,

    # Use both
    retrieval_mode=RetrievalMode.HYBRID,

    # These MUST match the names used during indexing
    vector_name="dense",
    sparse_vector_name="sparse",
)


vector_store_local = QdrantVectorStore(
    client=client,
    collection_name=f"{COLLECTION_NAME_PREFIX}-local",

    # Dense model
    embedding=dense_embeddings_local,

    # BM25
    sparse_embedding=sparse_embeddings,

    # Use both
    retrieval_mode=RetrievalMode.HYBRID,

    # These MUST match the names used during indexing
    vector_name="dense",
    sparse_vector_name="sparse",
)



# ============================================================
# Retriever
# ============================================================

retriever_openai_for_openai = vector_store_openai.as_retriever(
    search_kwargs={
        "k": 5,
    }
)

retriever_local_for_openai = vector_store_local.as_retriever(
    search_kwargs={
        "k": 5,
    }
)

retriever_openai_for_local = vector_store_openai.as_retriever(
    search_kwargs={
        "k": 3,
    }
)

retriever_local_for_local = vector_store_local.as_retriever(
    search_kwargs={
        "k": 3,
    }
)

# ============================================================
# LLM
# ============================================================

llm_openai = ChatOpenAI(
    model="gpt-5.6-luna",
    temperature=0,
)

llm_local = ChatOpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy",
    max_tokens=512,
    temperature=0,
    model="Qwen/Qwen2.5-1.5B-Instruct",
)


# ============================================================
# Prompt
# ============================================================

system_prompt = """
Ты отвечаешь на вопросы по базе знаний.

"""

system_prompt_suffix = """
Используй только информацию из Context.

Если Context не содержит достаточной информации для ответа,
скажи, что в базе знаний недостаточно информации.

Не придумывай факты.

Context:
{context}

Следующие сообщения являются примерами ответов.
Они не относятся к текущему диалогу.
Не ссылайся на них как на историю разговора.

Вопрос: Кто из героев книг Демченко является однофамильцем знаменитого российского фигуриста?
Ответ: Захар Алексеевич Авербух.

Вопрос: Какой цвет глаз у Сёку?
Ответ: Я не знаю ответ на этот вопрос.

Примеры закончились.

Начиная со следующего сообщения пользователя,
считай, что начинается новый независимый диалог.
"""

system_prompt_openai = system_prompt + """
Ты помощник, который сначала размышляет, а потом отвечает. Всегда пиши свои шаги.

""" + system_prompt_suffix

system_prompt_local = system_prompt + system_prompt_suffix

prompt_openai = ChatPromptTemplate.from_messages([
    ("system", system_prompt_openai),
    ("human", "{input}"),
])

prompt_local = ChatPromptTemplate.from_messages([
    ("system", system_prompt_local),
    ("human", "{input}"),
])

def format_docs(docs):
    return "\n\n---\n\n".join(
        f"[{doc.metadata.get('title')}]\n{doc.page_content}"
        for doc in docs
    )

# ============================================================
# Query
# ============================================================

def query(query: str, use_openai_embeddings: bool, use_openai_llm: bool) -> str:
    if use_openai_llm:
        prompt = prompt_openai
        llm = llm_openai

        if use_openai_embeddings:
            retriever = retriever_openai_for_openai
        else:
            retriever = retriever_local_for_openai
    else:
        prompt = prompt_local
        llm = llm_local

        if use_openai_embeddings:
            retriever = retriever_openai_for_local
        else:
            retriever = retriever_local_for_local

    rag_chain = (
        {
            "context": itemgetter("input") | retriever | format_docs,
            "input": itemgetter("input"),
        }
        | prompt
        | llm
    )

    response = rag_chain.invoke({
        "input": query,
    })

    # print(response)

    return response.content

if __name__ == "__main__":
    parser = argparse.ArgumentParser(usage="python rag.py [--openai-embeddings] [--openai-llm] --model <query string>")
    parser.add_argument("--openai-embeddings", action="store_true", help="use OpenAI embeddings")
    parser.add_argument("--openai-llm", action="store_true", help="use OpenAI LLM")

    args, unknown_args = parser.parse_known_args()

    answer = query(unknown_args[0], getattr(args, "openai_embeddings", False), getattr(args, "openai_llm", False))

    print("Answer:")
    print(answer)

