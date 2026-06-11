# Enterprise Intelligent Data Engine 🤖

An autonomous, multi-agent Retrieval-Augmented Generation (RAG) system designed to route enterprise queries seamlessly between unstructured text documents (Vector Search) and structured relational databases (Text-to-SQL).

## 🏗️ Architecture Pillars
- **Dynamic Intent Routing:** Utilizes LangGraph and Llama 3 to classify user queries and route them to the appropriate data tool.
- **Autonomous Text-to-SQL:** Dynamically generates and executes relational database queries via SQLAlchemy.
- **Corrective RAG (CRAG):** Features an Evaluator Guardrail that grades retrieved context and falls back to a Tavily web search to prevent LLM hallucinations.
- **Hybrid Storage Pipeline:** Embeds and stores text documents persistently using `pgvector` inside PostgreSQL.
- **Automated Data Ingestion:** Uses Apache Airflow DAGs to continuously monitor and ingest new PDF policies into the vector database.
- **Interactive UI:** A fully functional Streamlit frontend for chatting and drag-and-drop document ingestion.

## 🚀 Quick Start Guide

### 1. Clone the Repository
```bash
git clone [https://github.com/yourusername/Enterprise-Data-Engine.git](https://github.com/yourusername/Enterprise-Data-Engine.git)
cd Enterprise-Data-Engine


2. Environment Setup
Create a virtual environment and install the dependencies:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

Create a .env file in the root directory and add your API keys:


3. Database Setup (pgvector)
Ensure PostgreSQL is running locally and the pgvector extension is enabled. Update your database connection strings inside the codebase to match your local credentials.

4. Run the Application
Start the Streamlit interface:
python3 -m streamlit run app.py

5. Start the Automated Airflow Pipeline (Optional)
To enable automated PDF ingestion:
export AIRFLOW_HOME=$(pwd)/airflow
airflow standalone

🛠️ Tech Stack
AI/Frameworks: LangGraph, LangChain, Groq (Llama 3), HuggingFace Embeddings

Data Engineering: PostgreSQL (pgvector), SQLAlchemy, Apache Airflow

Frontend: Streamlit