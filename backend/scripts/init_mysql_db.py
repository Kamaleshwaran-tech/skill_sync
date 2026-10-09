"""
MySQL Database Initialization Script for SkillSync AI.
Creates all SQLAlchemy tables in MySQL and verifies connectivity.
"""

from __future__ import annotations

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import sys
import logging
from sqlalchemy import text

from app.config.settings import get_settings
from app.database.session import Base, engine, get_database_url
# Import all models so Base.metadata has full registry
import app.models.models
import app.models.auth_models

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("init_mysql_db")


def init_database() -> bool:
    settings = get_settings()
    db_url = get_database_url()
    logger.info("Initializing database with URL: %s", db_url.split("@")[-1] if "@" in db_url else db_url)

    if "mysql" in db_url:
        try:
            import pymysql
            from urllib.parse import urlparse
            parsed = urlparse(db_url.replace("mysql+pymysql://", "http://"))
            db_name = parsed.path.lstrip("/") or "skillsync_ai"
            user = parsed.username or "root"
            password = parsed.password or ""
            host = parsed.hostname or "localhost"
            port = parsed.port or 3306

            logger.info("Connecting to MySQL server at %s:%d as '%s'...", host, port, user)
            conn = pymysql.connect(host=host, port=port, user=user, password=password, connect_timeout=5)
            with conn.cursor() as cur:
                cur.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
                logger.info("✓ Verified/Created database '%s' in MySQL!", db_name)
            conn.close()
        except Exception as my_err:
            logger.error("❌ Failed to connect to MySQL server: %s", my_err)
            logger.error("Please ensure MySQL is running on port %d and verify your password in backend/.env!", port if 'port' in locals() else 3306)
            return False

    try:
        # Step 1: Connect and test connectivity
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            logger.info("Connected to database successfully (SELECT 1 -> %s)", result)

            # Step 2: Enable pgvector extension if PostgreSQL
            if "postgresql" in db_url:
                try:
                    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                    conn.commit()
                    logger.info("pgvector extension enabled / verified.")
                except Exception as ext_err:
                    logger.warning("pgvector extension not enabled (optional): %s", ext_err)

        # Step 3: Create all tables defined in models
        logger.info("Creating all SQLAlchemy tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Created %d tables registered in Base.metadata:", len(Base.metadata.tables))
        for table_name in sorted(Base.metadata.tables.keys()):
            logger.info("  - %s", table_name)

        logger.info("Database initialization completed successfully!")
        return True

    except Exception as exc:
        logger.error("Database initialization failed: %s", exc)
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
