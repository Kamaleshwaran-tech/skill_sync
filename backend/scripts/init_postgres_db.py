"""
PostgreSQL Database Initialization Script for SkillSync AI.
Creates the database if missing, enables pgvector if available, and creates all SQLAlchemy tables.
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
logger = logging.getLogger("init_postgres_db")


def init_database() -> bool:
    settings = get_settings()
    db_url = get_database_url()
    logger.info("Initializing database with URL: %s", db_url.split("@")[-1] if "@" in db_url else db_url)

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
