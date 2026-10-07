from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from app.config.settings import get_settings
from app.database.base import Base

settings = get_settings()


def get_database_url() -> str:
    url = settings.database_url
    if url.startswith("mysql://"):
        url = url.replace("mysql://", "mysql+pymysql://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg2://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+"):
        url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url


def _ensure_mysql_db(db_url: str) -> None:
    if "mysql" not in db_url:
        return
    try:
        import pymysql
        from urllib.parse import urlparse
        parsed = urlparse(db_url.replace("mysql+pymysql://", "http://"))
        db_name = parsed.path.lstrip("/") or "skillsync_ai"
        user = parsed.username or "root"
        password = parsed.password or ""
        host = parsed.hostname or "localhost"
        port = parsed.port or 3306
        conn = pymysql.connect(host=host, port=port, user=user, password=password, connect_timeout=3)
        with conn.cursor() as cur:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        conn.close()
    except Exception as exc:
        import logging
        logging.getLogger("session").warning("MySQL auto-database check: %s", exc)


def create_db_engine():
    db_url = get_database_url()
    if db_url.startswith("sqlite"):
        return create_engine(
            db_url,
            echo=settings.db_echo,
            future=True,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
    _ensure_mysql_db(db_url)
    try:
        pg_engine = create_engine(
            db_url,
            echo=settings.db_echo,
            future=True,
            pool_size=10,
            max_overflow=20,
            pool_recycle=3600,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3},
        )
        with pg_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return pg_engine
    except Exception as exc:
        import logging
        if settings.environment.lower() == "production":
            raise RuntimeError("Unable to connect to the configured production database.") from exc
        logging.getLogger("session").warning("Could not connect to external DB (%s). Using development SQLite fallback.", exc)
        return create_engine(
            "sqlite:///./skillsync_ai.db",
            echo=settings.db_echo,
            future=True,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )


engine = create_db_engine()
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> tuple[bool, str]:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True, "Database connection successful."
    except Exception as exc:  # pragma: no cover - defensive fallback
        return False, f"Database connection failed: {exc}"


__all__ = ["Base", "SessionLocal", "engine", "get_db_session", "check_database_connection"]
