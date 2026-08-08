import os
from dotenv import load_dotenv
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_postgres.vectorstores import PGVector

# Load environment variables
load_dotenv()

# Build the connection string using your existing .env variables
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "agent_db")

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# 1. Initialize Embeddings
print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# 2. Mock Documents (Same as Week 1)
sample_documents = [
    "Company Remote Work Policy: Employees can work remotely up to 3 days per week. Core hours are 10 AM to 4 PM EST. All remote employees must use the company VPN for security.",
    "Expense Reimbursement Guidelines: Travel expenses must be submitted within 30 days. Meals are covered up to $50 per day. Receipts are strictly mandatory for any expense over $25.",
    "IT Support and Password Reset: Passwords must be changed every 90 days. Passwords must contain at least 12 characters, 1 number, and 1 special character. Contact IT at ext 4444 for locked accounts."
]

# 3. Chunking Strategy
text_splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
docs = text_splitter.create_documents(sample_documents)

# 4. Initialize PGVector & Upsert
print("Connecting to PostgreSQL and creating vector tables...")
# The collection_name acts like a specific table namespace for these embeddings
vector_store = PGVector(
    embeddings=embeddings,
    collection_name="enterprise_policies",
    connection=connection_string,
    use_jsonb=True, # Highly recommended for storing metadata alongside vectors
)

print("Inserting document chunks into the database...")
vector_store.add_documents(docs)
print("Migration complete! Vectors are now permanently stored in PostgreSQL.")