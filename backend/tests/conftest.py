import os
from pathlib import Path
import tempfile

# Independent temporary database and uploads. Never use a user's configured data.
_test_directory = tempfile.TemporaryDirectory(prefix="skillsync-core-tests-")
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_test_directory.name) / "test.db")
os.environ["RESUME_STORAGE_DIR"] = str(Path(_test_directory.name) / "resumes")
os.environ["JWT_SECRET_KEY"] = (
    "test-only-random-looking-secret-not-for-deployment-123456789"
)
os.environ["ADZUNA_APP_ID"] = ""
os.environ["ADZUNA_API_KEY"] = ""
import pytest
from fastapi.testclient import TestClient
from app.config.settings import get_settings

get_settings.cache_clear()
from app.main import app
from app.database.session import Base, engine
from app.middleware.logging import rate_limit_store


@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    rate_limit_store.clear()
    with TestClient(app) as client:
        yield client
    rate_limit_store.clear()
