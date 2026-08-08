"""Least-privilege SQL execution used by the LangGraph SQL route."""

import os
import re
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine
from sqlalchemy.exc import SQLAlchemyError

load_dotenv()
FORBIDDEN_SQL = re.compile(r"\b(DROP|DELETE|ALTER|TRUNCATE|INSERT|UPDATE|GRANT|REVOKE)\b", re.IGNORECASE)


def _fallback_url() -> str:
    return URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
    ).render_as_string(hide_password=False)


def get_sql_agent_db_url() -> str:
    """Use the dedicated Neon read-only role whenever it is configured."""
    return os.getenv("SQL_AGENT_DB_URL") or os.getenv("NEON_DB_URL") or _fallback_url()


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_sql_agent_db_url(), pool_pre_ping=True)


def execute_sql(query: str) -> str:
    """Execute an agent query only if it contains no write/DDL operations."""
    if FORBIDDEN_SQL.search(query):
        return "SQL Safety Error: only read-only SELECT queries are allowed."
    try:
        with get_engine().connect() as connection:
            result = connection.execute(text(query))
            if not result.returns_rows:
                return "SQL Safety Error: only queries that return rows are allowed."
            rows = result.fetchall()
            columns = result.keys()
            if not rows:
                return "Query executed successfully, but returned no results."
            output = f"Columns: {', '.join(columns)}\n"
            for row in rows:
                output += f"{row}\n"
            return output
    except SQLAlchemyError as exc:
        return f"SQL Execution Error: {str(exc)}. Please correct your SQL syntax and try again."
