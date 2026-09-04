# Enterprise Intelligent Data Engine

An authenticated RAG application that routes enterprise questions to either a
read-only SQL tool or a pgvector policy search. The AI/LangGraph flow remains
the core engine; FastAPI provides its secure API and React provides the UI.

## Tech stack

- FastAPI, JWT authentication, and role-based access control
- React + Vite
- Neon Postgres with pgvector
- LangGraph, LangChain, Groq, HuggingFace embeddings, and Tavily

## Prerequisites

Create a Neon project, enable pgvector, and create two database roles:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE ROLE app_readonly WITH LOGIN PASSWORD '<strong-password>';
GRANT CONNECT ON DATABASE neondb TO app_readonly;
GRANT USAGE ON SCHEMA public TO app_readonly;
GRANT SELECT ON employees TO app_readonly;
```

Use a separate write-capable Neon role for the application tables and vector
store. Never use the read-only role for application writes.

## Local development

```bash
git clone <repository-url>
cd Enterprise-Data-Engine

cd backend
cp .env.example .env
pip install -r requirements.txt
uvicorn main:app --reload
```

In another terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Set `APP_DB_URL` in `backend/.env` to the write-capable Neon connection URL
and `SQL_AGENT_DB_URL` to the restricted role connection URL. Add your Groq,
Tavily, JWT, and initial-admin values there. Set `VITE_API_URL` in
`frontend/.env` to the backend URL (normally `http://localhost:8000`).

Authentication uses a JWT in an HttpOnly cookie; it is never returned to or
stored by the frontend. In production, serve the API over HTTPS and leave
`COOKIE_SECURE=true` (the default). For local HTTP development only, add
`COOKIE_SECURE=false` to `backend/.env`. `COOKIE_SAMESITE` defaults to `lax`;
set it to `none` only for a cross-site frontend and HTTPS deployment.

On first backend startup, `app_users` and `documents` are created and exactly
one administrator is seeded from `INITIAL_ADMIN_USERNAME` and
`INITIAL_ADMIN_PASSWORD` when the user table is empty.

## Docker

Create `backend/.env` from `backend/.env.example`, then run:

```bash
docker-compose up --build
```

This starts only the backend on port 8000 and the frontend on port 80. Neon is
external; no database or scheduler container is included.

## Roles

- **Admin:** chat, upload and delete PDF documents, and create user accounts.
- **Employee:** chat only.

Document ingestion is admin-triggered: PDFs are chunked and embedded
synchronously during upload, with processing failures shown in the dashboard.

## EC2 deployment

On a `t3.micro` Ubuntu instance, install Docker and Docker Compose, clone this
repository, create `backend/.env`, then run `docker-compose up --build -d`.
Open port 80; port 8000 is optional for direct API access. For a public setup,
place the containers behind one reverse proxy and add HTTPS. A 2 GB swap file
helps avoid build-time memory pressure on small instances.
