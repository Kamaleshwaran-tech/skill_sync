import os
from pathlib import Path

# ensure a fresh sqlite test DB for every run
TEST_DB = Path("./test_skillsync_ai.db")
if TEST_DB.exists():
    try:
        TEST_DB.unlink()
    except Exception:
        pass

os.environ["DATABASE_URL"] = "sqlite:///./test_skillsync_ai.db"

import pytest
from fastapi.testclient import TestClient

from app.config.settings import get_settings
get_settings.cache_clear()

from app.main import app
from app.database.session import Base, engine


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
