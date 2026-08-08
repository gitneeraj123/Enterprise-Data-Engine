"""PGVector retrieval and ingestion access using the write-capable app database URL."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector
from sqlalchemy.engine import URL

load_dotenv()


def _fallback_url() -> str:
    return URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
    ).render_as_string(hide_password=False)


def get_vector_db_url() -> str:
    return os.getenv("APP_DB_URL") or os.getenv("NEON_DB_URL") or _fallback_url()


@lru_cache
def get_vector_store() -> PGVector:
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return PGVector(
        embeddings=embeddings,
        collection_name="enterprise_policies",
        connection=get_vector_db_url(),
        use_jsonb=True,
    )


def retrieve_documents(query: str) -> str:
    """Perform semantic search over the policy collection."""
    try:
        results = get_vector_store().similarity_search_with_score(query, k=2)
        if not results:
            return "No relevant documents found."
        formatted_output = "Retrieved Context:\n"
        for doc, score in results:
            formatted_output += f"--- Chunk (Distance Score: {score:.4f}) ---\n{doc.page_content}\n"
        return formatted_output
    except Exception as exc:
        return f"Vector Retrieval Error: {str(exc)}"
