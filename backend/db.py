"""Database helpers for the application-owned Neon tables."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL

load_dotenv()


def _fallback_url() -> str:
    """Build a PostgreSQL URL from the legacy DB_* variables when provided."""
    return URL.create(
        "postgresql+psycopg2",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME"),
    ).render_as_string(hide_password=False)


def get_app_db_url() -> str:
    """Return the write-capable application URL without embedding credentials in code."""
    return os.getenv("APP_DB_URL") or os.getenv("NEON_DB_URL") or _fallback_url()


@lru_cache
def get_engine() -> Engine:
    return create_engine(get_app_db_url(), pool_pre_ping=True)


def init_db() -> None:
    """Create application tables and seed the one administrator on a new database."""
    from auth import hash_password

    initial_username = os.getenv("INITIAL_ADMIN_USERNAME")
    initial_password = os.getenv("INITIAL_ADMIN_PASSWORD")
    with get_engine().begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS app_users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'employee'
                    CHECK (role IN ('admin', 'employee')),
                created_at TIMESTAMP DEFAULT NOW()
            )
        """))
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                uploaded_by TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT NOW(),
                status TEXT NOT NULL DEFAULT 'processing'
                    CHECK (status IN ('processing', 'processed', 'failed'))
            )
        """))
        user_count = connection.execute(text("SELECT COUNT(*) FROM app_users")).scalar_one()
        if user_count == 0:
            if not initial_username or not initial_password:
                raise RuntimeError(
                    "INITIAL_ADMIN_USERNAME and INITIAL_ADMIN_PASSWORD are required for a new database."
                )
            connection.execute(
                text("""
                    INSERT INTO app_users (username, password_hash, role)
                    VALUES (:username, :password_hash, 'admin')
                """),
                {"username": initial_username, "password_hash": hash_password(initial_password)},
            )


def get_user(username: str):
    with get_engine().connect() as connection:
        return connection.execute(
            text("SELECT username, password_hash, role FROM app_users WHERE username = :username"),
            {"username": username},
        ).mappings().first()
