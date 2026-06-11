import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Connect to the existing collection you just created in Postgres
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="enterprise_policies",
    connection=connection_string,
)

def retrieve_documents(query: str) -> str:
    """
    Performs a semantic search over the pgvector store in PostgreSQL.
    """
    try:
        results = vector_store.similarity_search_with_score(query, k=2)
        
        if not results:
            return "No relevant documents found."
            
        formatted_output = "Retrieved Context:\n"
        for doc, score in results:
            formatted_output += f"--- Chunk (Distance Score: {score:.4f}) ---\n"
            formatted_output += f"{doc.page_content}\n"
            
        return formatted_output
        
    except Exception as e:
        return f"Vector Retrieval Error: {str(e)}"